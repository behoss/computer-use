"""Configuration settings for Computer Use Agent."""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class AgentConfig:
    """Configuration for the Computer Use Agent.

    Attributes:
        goal: The task to accomplish
        app_name: Name of the application (e.g., "Slack", "Chrome")
        app_instructions: App-specific instructions
        max_iterations: Maximum number of agent steps
        verbose: Whether to print detailed output
        save_progress: Whether to save progress for recovery
        enable_thinking: Whether to include model's thinking process
        yolo_mode: Auto-approve all safety confirmations
        model_name: Gemini model to use
        temperature: Model temperature (0.0-1.0)
        excluded_functions: Functions to exclude from Computer Use
        screen_width: Screen width in pixels (recommended: 1440)
        screen_height: Screen height in pixels (recommended: 900)
        progress_file: Path to progress tracking file
    """

    goal: str
    original_goal: str = ""  # Set if goal was rewritten
    app_name: str = "Desktop Application"
    app_instructions: str = ""
    max_iterations: int = 40
    verbose: bool = True
    save_progress: bool = True
    enable_thinking: bool = False
    yolo_mode: bool = False  # Auto-approve all safety confirmations
    model_name: str = "gemini-2.5-computer-use-preview-10-2025"
    temperature: float = 0.1
    excluded_functions: List[str] = field(
        default_factory=lambda: ["open_web_browser", "navigate", "search"]
    )
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    progress_file: Path = field(default_factory=lambda: Path(".agent_progress.txt"))

    def __post_init__(self):
        """Post-initialization processing."""
        # Add browser-specific exclusions for non-browser apps
        if self.app_name.lower() not in ["chrome", "safari", "firefox", "browser"]:
            if "go_forward" not in self.excluded_functions:
                self.excluded_functions.append("go_forward")
