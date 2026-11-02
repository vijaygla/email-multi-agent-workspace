"""
Legacy import bridge for Nexus Generative Engine Client.
Preserved for backwards compatibility with any external references.
"""
from app.adapters.nexus_client import (
    NexusGenerativeEngineClient,
    CapgeminiGenerativeEngineClient,
    nexus_client,
    capgemini_client,
)

__all__ = [
    "NexusGenerativeEngineClient",
    "CapgeminiGenerativeEngineClient",
    "nexus_client",
    "capgemini_client",
]
