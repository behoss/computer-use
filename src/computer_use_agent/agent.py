"""Core agent orchestrator for Computer Use Agent."""

import os
import time
import logging
import subprocess
from pathlib import Path
from typing import Optional
from google import genai
from google.genai import types

from .config import (
    AgentConfig,
    SAFETY_SYSTEM_INSTRUCTIONS,
    SLACK_INSTRUCTIONS,
    GENERIC_MACOS_INSTRUCTIONS,
)
from .actions import ActionExecutor, ScreenManager
from .actions.executor import get_safety_confirmation
from .utils import ResponseHandler, RetryableAPICall
from .utils.llm_logger import LLMLogger

logger = logging.getLogger(__name__)


class ComputerUseAgent:
    """Main orchestrator for Computer Use automation."""

    def __init__(self, config: AgentConfig):
        """Initialize the agent.

        Args:
            config: Agent configuration
        """
        self.config = config

        # Initialize API client
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=api_key)

        # Get screen dimensions
        import pyautogui

        width = config.screen_width or pyautogui.size()[0]
        height = config.screen_height or pyautogui.size()[1]

        # Initialize components
        self.screen = ScreenManager(width, height)
        self.executor = ActionExecutor(self.screen, verbose=config.verbose)
        self.response_handler = ResponseHandler(self.screen)
        self.llm_logger = LLMLogger()

    def _play_sound(self, sound_name: str) -> None:
        """Play a system sound on macOS.

        Args:
            sound_name: Name of the sound file (e.g., 'Ping', 'Glass')
        """
        try:
            # macOS system sounds are in /System/Library/Sounds/
            sound_path = f"/System/Library/Sounds/{sound_name}.aiff"
            # Play sound in background without blocking
            subprocess.Popen(
                ["afplay", sound_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            # Silently fail if sound can't be played
            pass

    def run(self) -> bool:
        """Run the agent to accomplish the goal.

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'=' * 60}")
        if self.config.original_goal:
            print(f"📝 ORIGINAL GOAL: {self.config.original_goal}")
            print(f"🎯 REWRITTEN GOAL: {self.config.goal}")
            # Log goal rewrite to file
            self.llm_logger.log_goal_rewrite(
                self.config.original_goal, self.config.goal
            )
        else:
            print(f"🎯 GOAL: {self.config.goal}")
        print(f"📱 APP: {self.config.app_name}")
        print(f"📋 LLM LOG: {self.llm_logger.get_log_path()}")
        print(f"{'=' * 60}\n")

        # Build configuration
        system_instruction = self._build_system_instruction()
        model_config = self._create_model_config(system_instruction)

        # Initial screenshot and setup
        print("📸 Taking initial screenshot...")
        initial_screenshot = self.screen.capture_screenshot()

        # Initialize conversation
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part(text=self.config.goal),
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/png", data=initial_screenshot
                        )
                    ),
                ],
            )
        ]

        print(
            f"⏱️  Starting in 3 seconds... Please make sure {self.config.app_name} is open!"
        )
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)

        # Determine app URL
        app_url = f"{self.config.app_name.lower().replace(' ', '-')}://app"

        # Agent loop
        for iteration in range(self.config.max_iterations):
            # Play step sound notification (quick "Tink" sound)
            self._play_sound("Tink")

            print(f"\n{'=' * 40}")
            print(f"📍 STEP {iteration + 1}/{self.config.max_iterations}")
            print(f"{'=' * 40}")

            # Get model response with retry logic
            print("🤔 Analyzing screen and planning next action...")
            response = self._call_model_with_retry(contents, model_config, iteration)

            if not response:
                print("❌ Model returned no response object")
                self.llm_logger.log_error(
                    iteration + 1, "No response object from model"
                )
                return False

            if not response.candidates:
                print("❌ Model returned no candidates")
                print(f"   Response object: {response}")
                if hasattr(response, "prompt_feedback"):
                    print(f"   Prompt feedback: {response.prompt_feedback}")
                self.llm_logger.log_error(
                    iteration + 1,
                    f"No candidates in response. Prompt feedback: {getattr(response, 'prompt_feedback', 'N/A')}",
                )
                return False

            candidate = response.candidates[0]

            # Add model response to history
            if candidate.content:
                contents.append(candidate.content)

            # Check if task is complete
            if not self.response_handler.has_function_calls(candidate):
                text_response = self.response_handler.extract_text_response(candidate)
                if text_response:
                    print(f"✅ Agent finished: {text_response}")
                else:
                    print("✅ Task completed")
                break

            # Execute function calls
            print("⚙️  Executing actions...")
            results, should_terminate = self.executor.execute_function_calls(
                candidate, lambda sd: get_safety_confirmation(sd, self.config.yolo_mode)
            )

            if should_terminate:
                print("❌ Agent terminated due to safety decision")
                break

            # ALWAYS TAKE SCREENSHOTS: Critical for accuracy
            # Previously we skipped screenshots during scrolls to save tokens,
            # but this caused the LLM to hallucinate message content it couldn't see.
            # Accuracy is more important than token optimization.
            include_screenshot = True
            print("📸 Capturing new state...")

            function_responses = self.response_handler.create_function_responses(
                results, iteration, include_screenshot, app_url
            )

            # Add function responses to conversation
            if function_responses:
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(function_response=fr)
                            for fr in function_responses
                        ],
                    )
                )

            time.sleep(0.5)

        print(f"\n{'=' * 60}")
        print("✅ AGENT TASK COMPLETED")
        print(f"{'=' * 60}")

        # Play completion sound (distinct "Glass" sound)
        self._play_sound("Glass")

        # Clean up progress file on success
        if self.config.save_progress and self.config.progress_file.exists():
            self.config.progress_file.unlink()

        return True

    def _build_system_instruction(self) -> str:
        """Build complete system instruction.

        Returns:
            Complete system instruction string
        """
        instruction = GENERIC_MACOS_INSTRUCTIONS

        if self.config.include_safety_instructions:
            instruction = SAFETY_SYSTEM_INSTRUCTIONS + "\n\n" + instruction

        if self.config.app_instructions:
            instruction += "\n\n" + self.config.app_instructions

        instruction += f"\n\nThe user's goal is: {self.config.goal}"

        return instruction

    def _create_model_config(
        self, system_instruction: str
    ) -> types.GenerateContentConfig:
        """Create model configuration.

        Args:
            system_instruction: System instruction to use

        Returns:
            GenerateContentConfig for the model
        """
        config_params = {
            "tools": [
                types.Tool(
                    computer_use=types.ComputerUse(
                        environment=types.Environment.ENVIRONMENT_BROWSER,
                        excluded_predefined_functions=self.config.excluded_functions,
                    )
                )
            ],
            "temperature": self.config.temperature,
            "system_instruction": system_instruction,
        }

        # Add thinking config if enabled
        if self.config.enable_thinking:
            config_params["thinking_config"] = types.ThinkingConfig(
                include_thoughts=True
            )

        return types.GenerateContentConfig(**config_params)

    def _call_model_with_retry(
        self, contents, config, iteration: int
    ) -> Optional[types.GenerateContentResponse]:
        """Call model with retry logic.

        Args:
            contents: Conversation contents
            config: Model configuration
            iteration: Current iteration number

        Returns:
            Model response or None if failed
        """
        retry_helper = RetryableAPICall(
            max_retries=3,
            initial_delay=2.0,
            on_503_callback=lambda retry, delay: print(
                f"⚠️  API temporarily unavailable (attempt {retry + 1}/3)\n"
                f"   Waiting {delay} seconds before retry..."
            ),
            on_429_callback=lambda: print(
                "⚠️  Rate limit reached. Waiting 30 seconds..."
            ),
        )

        for retry in range(retry_helper.max_retries):
            try:
                # Log request
                prompt_text = (
                    f"System: {config.system_instruction}\n\nStep {iteration + 1}"
                )
                self.llm_logger.log_request(iteration + 1, prompt_text, image_data=True)

                # Call API
                response = self.client.models.generate_content(
                    model=self.config.model_name,
                    contents=contents,
                    config=config,
                )

                # Log response
                if response and response.candidates:
                    candidate = response.candidates[0]
                    response_text = (
                        self.response_handler.extract_text_response(candidate) or ""
                    )
                    function_calls = []
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, "function_call") and part.function_call:
                                function_calls.append(
                                    {
                                        "name": part.function_call.name,
                                        "args": (
                                            dict(part.function_call.args)
                                            if part.function_call.args
                                            else {}
                                        ),
                                    }
                                )
                    self.llm_logger.log_response(
                        iteration + 1, response_text, function_calls
                    )

                return response

            except Exception as e:
                self.llm_logger.log_error(iteration + 1, str(e))
                if retry < retry_helper.max_retries - 1 and retry_helper.should_retry(
                    e
                ):
                    retry_helper.retry_count = retry
                    retry_helper.wait_and_retry()
                    continue
                else:
                    # Final failure
                    print(f"❌ API Error: {e}")
                    self._save_progress(iteration)
                    return None

        return None

    def _save_progress(self, iteration: int):
        """Save progress for recovery.

        Args:
            iteration: Current iteration number
        """
        if not self.config.save_progress:
            return

        try:
            with open(self.config.progress_file, "w") as f:
                f.write(f"Step: {iteration + 1}/{self.config.max_iterations}\n")
                f.write(f"Original Goal: {self.config.goal}\n")
                f.write(f"App: {self.config.app_name}\n")
                f.write(f"Last Action: Step {iteration + 1}\n")
                f.write("Status: Interrupted\n")

            print(f"\n📝 Progress saved to {self.config.progress_file}")
        except Exception as e:
            logger.error(f"Could not save progress: {e}")
