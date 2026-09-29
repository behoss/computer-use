"""Response handling utilities for Computer Use Agent."""

from typing import List, Tuple, Dict, Any
from google.genai import types


class ResponseHandler:
    """Handles model responses and creates function responses."""

    def __init__(self, screen_manager):
        """Initialize response handler.

        Args:
            screen_manager: ScreenManager instance
        """
        self.screen = screen_manager

    def create_function_responses(
        self,
        results: List[Tuple[str, Dict[str, Any]]],
        iteration: int = 0,
        include_screenshot: bool = True,
        app_url: str = "app://desktop",
    ) -> List[types.FunctionResponse]:
        """Create function responses from action results.

        Args:
            results: List of (function_name, result_dict) tuples
            iteration: Current iteration number
            include_screenshot: Whether to include screenshot
            app_url: Application URL for response

        Returns:
            List of FunctionResponse objects
        """
        function_responses = []

        for name, result in results:
            # Add URL to response (required by Computer Use API)
            response_data = dict(result)
            response_data["url"] = app_url

            # Skip screenshots for scroll operations after the first few to save context
            should_include_screenshot = include_screenshot and not (
                name in ["scroll_document", "scroll_at"] and iteration > 3
            )

            if should_include_screenshot:
                # Take screenshot
                screenshot_bytes = self.screen.capture_screenshot()

                # Create FunctionResponsePart with inline data
                function_response_part = types.FunctionResponsePart(
                    inline_data=types.FunctionResponseBlob(
                        mime_type="image/png", data=screenshot_bytes
                    )
                )

                function_responses.append(
                    types.FunctionResponse(
                        name=name,
                        response=response_data,
                        parts=[function_response_part],
                    )
                )
            else:
                # For scroll operations, provide text feedback without screenshot
                if name in ["scroll_document", "scroll_at"]:
                    response_data["description"] = (
                        "Scrolled successfully. Context preserved to prevent overflow."
                    )

                function_responses.append(
                    types.FunctionResponse(
                        name=name,
                        response=response_data,
                        parts=[],
                    )
                )

        return function_responses

    @staticmethod
    def extract_text_response(candidate) -> str:
        """Extract text from candidate response.

        Args:
            candidate: Model response candidate

        Returns:
            Extracted text or empty string
        """
        text_parts = []
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    text_parts.append(part.text)
        return " ".join(text_parts)

    @staticmethod
    def has_function_calls(candidate) -> bool:
        """Check if candidate contains function calls.

        Args:
            candidate: Model response candidate

        Returns:
            True if function calls present
        """
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    return True
        return False
