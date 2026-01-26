"""
Opik Integration Module
Exports all Opik-related functionality
"""

from src.opik_integration.client import opik_client, is_opik_enabled, get_opik_client
from src.opik_integration.tracing import opik_integration
from src.opik_integration.prompts import prompt_manager

__all__ = [
    "opik_client",
    "is_opik_enabled",
    "get_opik_client",
    "opik_integration",
    "prompt_manager",
]
