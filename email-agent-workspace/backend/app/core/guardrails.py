"""
Enterprise Guardrails Module.
Provides prompt injection detection, PII masking, toxic content filtration,
and corporate compliance boundary checks.
"""
import re
from typing import Tuple, List

# Patterns frequently associated with prompt injection and privilege escalation attacks
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions",
    r"(?i)disregard\s+(?:all\s+)?(?:previous|prior)\s+rules",
    r"(?i)system\s+prompt\s+override",
    r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
    r"(?i)jailbreak",
    r"(?i)bypass\s+corporate\s+security",
    r"(?i)reveal\s+your\s+(?:internal\s+)?instructions",
    r"(?i)print\s+(?:all\s+)?api\s+keys",
    r"(?i)drop\s+table",
    r"(?i)delete\s+from\s+tasks",
    r"(?i)<script.*?>.*?</script>"
]

# Sensitive corporate / PII data patterns
CREDIT_CARD_PATTERN = r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
SSN_PATTERN = r"\b\d{3}-\d{2}-\d{4}\b"
PASSWORD_LEAK_PATTERN = r"(?i)(?:password|passwd|secret)\s*[:=]\s*\S+"

class GuardrailViolation(Exception):
    """Custom exception raised when guardrail policies are violated."""
    def __init__(self, message: str, violation_type: str):
        super().__init__(message)
        self.violation_type = violation_type


class EnterpriseGuardrails:
    """Enterprise safety and policy shield for corporate AI workflows."""

    @classmethod
    def inspect_input(cls, text: str) -> Tuple[bool, str, List[str]]:
        """
        Inspects text for prompt injections and unauthorized directives.
        Returns: (is_safe: bool, sanitized_text: str, violations: List[str])
        """
        if not text:
            return True, "", []

        violations = []

        # Check prompt injection patterns
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text):
                violations.append(f"Prompt injection attempt detected: '{pattern}'")

        # Sanitize PII
        sanitized = cls.mask_pii(text)

        is_safe = len(violations) == 0
        return is_safe, sanitized, violations

    @classmethod
    def mask_pii(cls, text: str) -> str:
        """Masks sensitive credit cards, SSNs, and exposed passwords."""
        masked = re.sub(CREDIT_CARD_PATTERN, "[REDACTED_CREDIT_CARD]", text)
        masked = re.sub(SSN_PATTERN, "[REDACTED_SSN]", masked)
        masked = re.sub(PASSWORD_LEAK_PATTERN, "password=[REDACTED_SECRET]", masked)
        return masked

    @classmethod
    def sanitize_output(cls, text: str) -> str:
        """Sanitizes outgoing generated model responses before sending or storing."""
        if not text:
            return ""
        # Remove accidental API key disclosures
        text = re.sub(r"sk-[a-zA-Z0-9_\-]{16,}", "[REDACTED_API_KEY]", text)
        return text
