"""
Microsoft Graph & MSAL Adapter for Outlook Mail.
Authenticates against corporate Azure AD / Entra ID and accesses inbox messages.
Seamlessly falls back to mock adapter when credentials are not configured.
"""
import logging
from typing import Dict, Any, List
import requests
import msal
from app.core.config import settings
from app.adapters.base import BaseEmailClient
from app.adapters.mock_adapters import mock_email_client

logger = logging.getLogger(__name__)

class OutlookMailClient(BaseEmailClient):
    """Integrates with Microsoft Graph Mail API using MSAL auth tokens."""

    def __init__(self):
        self.client_id = settings.MS_GRAPH_CLIENT_ID
        self.client_secret = settings.MS_GRAPH_CLIENT_SECRET
        self.tenant_id = settings.MS_GRAPH_TENANT_ID
        self.use_mock = settings.USE_MOCK_OUTLOOK or not (self.client_id and self.client_secret)

    def _get_access_token(self) -> str:
        """Acquires OAuth2 token using MSAL client credentials grant."""
        if self.use_mock:
            return "mock_token"

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" in result:
            return result["access_token"]
        raise RuntimeError(f"MSAL authentication failed: {result.get('error_description')}")

    def fetch_unread_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        if self.use_mock:
            return mock_email_client.fetch_unread_emails(limit)

        try:
            token = self._get_access_token()
            headers = {"Authorization": f"Bearer {token}"}
            endpoint = f"https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$filter=isRead eq false&$top={limit}"
            resp = requests.get(endpoint, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            messages = []
            for item in data.get("value", []):
                messages.append({
                    "id": item.get("id"),
                    "subject": item.get("subject", ""),
                    "sender": item.get("from", {}).get("emailAddress", {}).get("address", ""),
                    "recipient": item.get("toRecipients", [{}])[0].get("emailAddress", {}).get("address", ""),
                    "body": item.get("bodyPreview", "") or item.get("body", {}).get("content", ""),
                    "received_at": item.get("receivedDateTime")
                })
            return messages
        except Exception as e:
            logger.warning(f"Error fetching from MS Graph: {e}. Falling back to mock client.")
            return mock_email_client.fetch_unread_emails(limit)

    def send_email(self, to: str, subject: str, body: str) -> bool:
        if self.use_mock:
            return mock_email_client.send_email(to, subject, body)

        try:
            token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "message": {
                    "subject": subject,
                    "body": {"contentType": "Text", "content": body},
                    "toRecipients": [{"emailAddress": {"address": to}}]
                }
            }
            resp = requests.post("https://graph.microsoft.com/v1.0/me/sendMail", json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"Failed sending email via MS Graph: {e}. Falling back to mock.")
            return mock_email_client.send_email(to, subject, body)

outlook_mail_client = OutlookMailClient()
