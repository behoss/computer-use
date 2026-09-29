"""
Computer Use Agent - macOS Desktop Automation

A production-ready autonomous agent using Gemini Computer Use API
for macOS desktop automation with safety-first design.
"""

from .agent import ComputerUseAgent
from .config.settings import AgentConfig

__version__ = "1.0.0"
__all__ = ["ComputerUseAgent", "AgentConfig"]
