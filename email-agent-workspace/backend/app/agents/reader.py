"""
Reader Agent: Ingests, normalizes, and contextualizes incoming email payloads.
Strips noise, disclaimers, and formats context for downstream agents.
"""
import re
from typing import Dict, Any

class ReaderAgent:
    """Parses raw email data and extracts clean textual context."""

    def clean_email_body(self, raw_body: str) -> str:
        """Removes trailing email disclaimers, excessive whitespace, and signatures."""
        if not raw_body:
            return ""

        # Normalize line endings
        text = raw_body.replace("\r\n", "\n").replace("\r", "\n")

        # Strip standard corporate confidentiality disclaimers
        disclaimer_markers = [
            r"(?i)this\s+message\s+contains\s+confidential\s+information",
            r"(?i)if\s+you\s+are\s+not\s+the\s+intended\s+recipient",
            r"(?i)this\s+e-mail\s+and\s+any\s+attachments\s+are\s+confidential",
            r"(?i)--\s*\n",
            r"(?i)sent\s+from\s+my\s+iphone",
            r"(?i)get\s+outlook\s+for\s+"
        ]
        for marker in disclaimer_markers:
            parts = re.split(marker, text)
            if len(parts) > 1 and len(parts[0].strip()) > 20:
                text = parts[0]

        # Collapse excess whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def process(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepares a clean context payload from raw email data."""
        raw_body = email_data.get("body", "")
        cleaned_body = self.clean_email_body(raw_body)

        sender = email_data.get("sender", "")
        sender_name = sender.split("@")[0].replace(".", " ").title() if "@" in sender else sender

        thread_history = email_data.get("thread_history", [])

        return {
            "cleaned_body": cleaned_body,
            "subject": email_data.get("subject", ""),
            "sender": sender,
            "sender_name": sender_name,
            "recipient": email_data.get("recipient", ""),
            "received_at": email_data.get("received_at", ""),
            "word_count": len(cleaned_body.split()),
            "thread_history": thread_history
        }

reader_agent = ReaderAgent()
