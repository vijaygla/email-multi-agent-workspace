"""
Secure Nexus Generative Engine Client.
Routes prompts and embedding requests to Nexus platform endpoint
with multi-model fallback orchestration and WebSocket streaming capabilities.
"""
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from openai import OpenAI
import httpx
from app.core.config import settings
from app.core.guardrails import EnterpriseGuardrails, GuardrailViolation
from app.adapters.base import BaseLLMClient

logger = logging.getLogger(__name__)

class NexusGenerativeEngineClient(BaseLLMClient):
    """
    Client for interacting with the Nexus Generative Engine Platform.
    Utilizes OpenAI-compatible REST endpoints and supports multi-model orchestration.
    """

    def __init__(self):
        self.api_key = settings.NEXUS_API_KEY
        self.base_url = settings.NEXUS_BASE_URL
        self.ws_url = settings.NEXUS_WS_URL

        # Initialize OpenAI compatible client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={"X-API-KEY": self.api_key}
        )

        # Fallback hierarchy
        self.fallback_chain = [
            settings.MODEL_ROUTER,
            settings.MODEL_REASONING,
            settings.MODEL_FALLBACK,
            "meta.llama3-8b-instruct-v1:0"
        ]

    def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Executes a chat completion with automated model fallback orchestration.
        """
        target_model = model or settings.MODEL_ROUTER
        models_to_try = [target_model] + [m for m in self.fallback_chain if m != target_model]

        last_error = None
        for current_model in models_to_try:
            try:
                # Corporate guardrail inspection
                if settings.ENABLE_GUARDRAILS:
                    for msg in messages:
                        is_safe, sanitized_content, violations = EnterpriseGuardrails.inspect_input(msg.get("content", ""))
                        if not is_safe:
                            raise GuardrailViolation(
                                f"Input blocked by guardrails: {', '.join(violations)}",
                                "INJECTION_ATTEMPT"
                            )
                        msg["content"] = sanitized_content

                logger.debug(f"Calling Nexus Generative Engine with model: {current_model}")

                params: Dict[str, Any] = {
                    "model": current_model,
                    "messages": messages,
                    "temperature": temperature,
                }
                if response_format:
                    params["response_format"] = response_format

                response = self.client.chat.completions.create(**params)
                raw_text = response.choices[0].message.content or ""

                if settings.ENABLE_GUARDRAILS:
                    raw_text = EnterpriseGuardrails.sanitize_output(raw_text)

                return raw_text.strip()

            except GuardrailViolation:
                raise
            except Exception as e:
                logger.warning(
                    f"Model '{current_model}' failed with error: {e}. Trying next model in fallback chain..."
                )
                last_error = e

        logger.error(f"All models failed in fallback chain. Last error: {last_error}")
        raise RuntimeError(f"Nexus Generative Engine request failed across all models: {last_error}")

    def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Calculates vector embeddings using Nexus internal embedding deployment.
        """
        embed_model = model or settings.MODEL_EMBEDDING
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=embed_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"Embedding generation with {embed_model} failed: {e}. Attempting fallback to text-embedding-3-small")
            try:
                fallback_resp = self.client.embeddings.create(
                    input=[text],
                    model="text-embedding-3-small"
                )
                return fallback_resp.data[0].embedding
            except Exception as e2:
                logger.error(f"Fallback embedding generation failed: {e2}")
                return []

    async def stream_query_ws(self, query: str, model: Optional[str] = None):
        """
        Connects to the Nexus WebSocket endpoint with X-API-KEY header for real-time socket communication.
        """
        import websockets
        headers = {"X-API-KEY": self.api_key}
        payload = {
            "action": "sendQuery",
            "model": model or settings.MODEL_ROUTER,
            "query": query
        }
        try:
            async with websockets.connect(self.ws_url, extra_headers=headers) as ws:
                await ws.send(json.dumps(payload))
                async for message in ws:
                    yield json.loads(message)
        except Exception as e:
            logger.warning(f"Nexus WebSocket streaming connection error: {e}")
            # Graceful fallback to REST completion
            reply = self.generate([{"role": "user", "content": query}], model=model)
            yield {"content": reply, "status": "completed"}

# Global singleton
nexus_client = NexusGenerativeEngineClient()
# Backward compatibility aliases
CapgeminiGenerativeEngineClient = NexusGenerativeEngineClient
capgemini_client = nexus_client
