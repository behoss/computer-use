"""LLM request/response logging for debugging and observability."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class LLMLogger:
    """Logs all LLM interactions to file for debugging."""

    def __init__(self, log_dir: str = "logs"):
        """Initialize LLM logger.

        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"llm_log_{timestamp}.jsonl"
        self.step_counter = 0

    def log_request(self, step: int, prompt: str, image_data: Any = None) -> None:
        """Log LLM request.

        Args:
            step: Current step number
            prompt: Text prompt sent to LLM
            image_data: Screenshot data (not logged, just noted)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "request",
            "step": step,
            "prompt": prompt,
            "has_image": image_data is not None,
        }
        self._write_log(log_entry)

    def log_response(
        self,
        step: int,
        response_text: str,
        function_calls: list | None = None,
        thinking: str | None = None,
    ) -> None:
        """Log LLM response.

        Args:
            step: Current step number
            response_text: Text response from LLM
            function_calls: List of function calls made
            thinking: Model's thinking process if available
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "response",
            "step": step,
            "response_text": response_text,
            "function_calls": function_calls or [],
            "thinking": thinking,
        }
        self._write_log(log_entry)

    def log_error(self, step: int, error: str) -> None:
        """Log an error.

        Args:
            step: Current step number
            error: Error message
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "step": step,
            "error": error,
        }
        self._write_log(log_entry)

    def log_goal_rewrite(self, original_goal: str, rewritten_goal: str) -> None:
        """Log goal rewriting information.

        Args:
            original_goal: Original user goal
            rewritten_goal: Rewritten goal
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "goal_rewrite",
            "original_goal": original_goal,
            "rewritten_goal": rewritten_goal,
        }
        self._write_log(log_entry)

    def _write_log(self, entry: Dict[str, Any]) -> None:
        """Write log entry to file.

        Args:
            entry: Log entry dictionary
        """
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry, indent=None) + "\n")

    def get_log_path(self) -> str:
        """Get the path to the current log file.

        Returns:
            Path to log file
        """
        return str(self.log_file)
