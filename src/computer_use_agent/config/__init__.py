"""Configuration package for Computer Use Agent."""

from .settings import AgentConfig
from .prompts import (
    SCROLLING_INSTRUCTIONS,
    SLACK_INSTRUCTIONS,
    GENERIC_MACOS_INSTRUCTIONS,
)

__all__ = [
    "AgentConfig",
    "SCROLLING_INSTRUCTIONS",
    "SLACK_INSTRUCTIONS",
    "GENERIC_MACOS_INSTRUCTIONS",
]
