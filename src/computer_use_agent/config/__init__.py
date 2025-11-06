"""Configuration package for Computer Use Agent."""

from .settings import AgentConfig
from .prompts import (
    SAFETY_SYSTEM_INSTRUCTIONS,
    SLACK_INSTRUCTIONS,
    GENERIC_MACOS_INSTRUCTIONS,
)

__all__ = [
    "AgentConfig",
    "SAFETY_SYSTEM_INSTRUCTIONS",
    "SLACK_INSTRUCTIONS",
    "GENERIC_MACOS_INSTRUCTIONS",
]
