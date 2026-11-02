"""
Abstract base classes defining strict interfaces for external system tools and adapters.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseLLMClient(ABC):
    """Interface for generative engine communications."""

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """Generates a text or JSON completion from the LLM."""
        pass

    @abstractmethod
    def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """Generates vector embeddings for a given text snippet."""
        pass


class BaseEmailClient(ABC):
    """Interface for interacting with enterprise mailboxes."""

    @abstractmethod
    def fetch_unread_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves unread emails from the corporate inbox."""
        pass

    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Sends an email through the corporate mail service."""
        pass


class BaseCalendarClient(ABC):
    """Interface for querying availability and scheduling meetings."""

    @abstractmethod
    def get_free_busy_slots(
        self,
        start_date: str,
        end_date: str,
        duration_minutes: int = 30
    ) -> List[Dict[str, str]]:
        """Returns 2-3 optimal open meeting slots matching schedule."""
        pass

    @abstractmethod
    def schedule_event(
        self,
        subject: str,
        start_time: str,
        end_time: str,
        attendees: List[str]
    ) -> Dict[str, Any]:
        """Books a calendar appointment."""
        pass
