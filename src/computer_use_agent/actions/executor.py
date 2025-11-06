"""Action execution for Computer Use Agent."""

import time
import platform
import pyautogui
from typing import Dict, Any, List, Tuple
import termcolor

from .screen import ScreenManager


class ActionExecutor:
    """Executes Computer Use actions on the desktop."""

    def __init__(self, screen_manager: ScreenManager, verbose: bool = True):
        """Initialize action executor.

        Args:
            screen_manager: Screen manager instance
            verbose: Whether to print execution details
        """
        self.screen = screen_manager
        self.verbose = verbose

        # Configure pyautogui
        pyautogui.PAUSE = 0.5
        pyautogui.FAILSAFE = True

    def execute_function_calls(
        self, candidate, get_safety_confirmation_fn
    ) -> Tuple[List[Tuple[str, Dict[str, Any]]], bool]:
        """Execute function calls from the model response.

        Args:
            candidate: Model response candidate
            get_safety_confirmation_fn: Function to get safety confirmation

        Returns:
            Tuple of (results list, should_terminate boolean)
        """
        results = []
        function_calls = []
        should_terminate = False

        # Extract function calls from candidate
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    function_calls.append(part.function_call)

        for function_call in function_calls:
            action_result = {}
            fname = function_call.name
            args = function_call.args or {}

            # Check for safety decision
            extra_fields = {}
            if "safety_decision" in args:
                decision = get_safety_confirmation_fn(args["safety_decision"])
                if decision == "TERMINATE":
                    print(
                        "❌ User declined safety confirmation. Terminating agent loop."
                    )
                    should_terminate = True
                    results.append(
                        (fname, {"status": "cancelled", "safety_declined": True})
                    )
                    break
                extra_fields["safety_acknowledgement"] = True

            if self.verbose:
                print(f"  -> Executing: {fname}")
                print(f"     Args: {args}")

            try:
                action_result = self._execute_action(fname, args)
                # Merge extra fields (like safety_acknowledgement)
                action_result.update(extra_fields)
                # Wait for action to complete
                time.sleep(1)

            except Exception as e:
                print(f"     Error executing {fname}: {e}")
                action_result = {"status": "error", "error": str(e)}

            results.append((fname, action_result))

        return results, should_terminate

    def _execute_action(self, fname: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action.

        Args:
            fname: Function name
            args: Function arguments

        Returns:
            Action result dictionary
        """
        if fname == "open_web_browser":
            return {"status": "skipped", "message": "Desktop app, not browser"}

        elif fname == "click_at":
            return self._click_at(args)

        elif fname == "type_text_at":
            return self._type_text_at(args)

        elif fname == "key_combination":
            return self._key_combination(args)

        elif fname == "scroll_document":
            return self._scroll_document(args)

        elif fname == "scroll_at":
            return self._scroll_at(args)

        elif fname == "hover_at":
            return self._hover_at(args)

        elif fname == "drag_and_drop":
            return self._drag_and_drop(args)

        elif fname == "wait_5_seconds":
            return self._wait_5_seconds()

        elif fname == "go_back":
            return self._go_back()

        elif fname == "go_forward":
            return self._go_forward()

        elif fname == "search":
            return self._search()

        elif fname == "navigate":
            return self._navigate(args)

        else:
            print(f"     Warning: Unimplemented function {fname}")
            return {"status": "unimplemented"}

    def _click_at(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute click_at action."""
        actual_x, actual_y = self.screen.denormalize_coords(
            args.get("x", 0), args.get("y", 0)
        )
        print(f"     Clicking at ({actual_x}, {actual_y})")
        pyautogui.click(actual_x, actual_y)
        return {"status": "success"}

    def _type_text_at(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute type_text_at action."""
        actual_x, actual_y = self.screen.denormalize_coords(
            args.get("x", 0), args.get("y", 0)
        )
        text = args.get("text", "")
        press_enter = args.get("press_enter", False)
        clear_before = args.get("clear_before_typing", False)

        # Click to focus
        pyautogui.click(actual_x, actual_y)
        time.sleep(0.5)

        if clear_before:
            # Clear field on macOS
            pyautogui.hotkey("command", "a")
            time.sleep(0.1)
            pyautogui.press("backspace")
            time.sleep(0.1)

        # Type text
        pyautogui.write(text, interval=0.05)
        if press_enter:
            time.sleep(0.1)
            pyautogui.press("enter")

        return {"status": "success"}

    def _key_combination(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute key_combination action."""
        keys_str = args.get("keys", "")

        # Normalize to command for macOS
        keys_str = (
            keys_str.replace("Control+", "command+")
            .replace("control+", "command+")
            .replace("Ctrl+", "command+")
            .replace("ctrl+", "command+")
            .replace("Command+", "command+")
            .replace("Cmd+", "command+")
            .replace("cmd+", "command+")
        )

        # Split keys
        keys = [key.strip().lower() for key in keys_str.split("+")]

        print(f"     Pressing: {'+'.join(keys)}")

        # Use interval parameter for macOS to ensure modifier keys register
        if platform.system() == "Darwin":
            pyautogui.hotkey(*keys, interval=0.25)
        else:
            pyautogui.hotkey(*keys)

        return {"status": "success"}

    def _scroll_document(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scroll_document action."""
        direction = args.get("direction", "down")
        # macOS scroll direction - positive scrolls UP, negative scrolls DOWN
        scroll_amount = -300 if direction == "down" else 300

        # Ensure window has focus by clicking in the center first
        center_x, center_y = self.screen.get_center()
        pyautogui.click(center_x, center_y)
        time.sleep(0.3)

        # Perform the scroll
        pyautogui.scroll(scroll_amount)
        time.sleep(0.5)

        print(f"     Scrolled {direction} (amount: {scroll_amount})")
        return {"status": "success"}

    def _scroll_at(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scroll_at action."""
        actual_x = self.screen.denormalize_x(args.get("x", 500))
        actual_y = self.screen.denormalize_y(args.get("y", 500))
        direction = args.get("direction", "down")
        magnitude = args.get("magnitude", 800)

        # Calculate scroll amount based on direction and magnitude
        scroll_amount = (
            self.screen.denormalize_y(magnitude)
            if direction in ["up", "down"]
            else self.screen.denormalize_x(magnitude)
        )
        if direction in ["down", "right"]:
            scroll_amount = -scroll_amount

        # Click at position to focus
        pyautogui.click(actual_x, actual_y)
        time.sleep(0.3)

        pyautogui.scroll(scroll_amount)
        print(
            f"     Scrolled {direction} at ({actual_x}, {actual_y}), magnitude: {magnitude}"
        )
        return {"status": "success"}

    def _hover_at(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hover_at action."""
        actual_x, actual_y = self.screen.denormalize_coords(
            args.get("x", 0), args.get("y", 0)
        )
        pyautogui.moveTo(actual_x, actual_y)
        print(f"     Hovering at ({actual_x}, {actual_y})")
        return {"status": "success"}

    def _drag_and_drop(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute drag_and_drop action."""
        start_x = self.screen.denormalize_x(args.get("x", 0))
        start_y = self.screen.denormalize_y(args.get("y", 0))
        dest_x = self.screen.denormalize_x(args.get("destination_x", 0))
        dest_y = self.screen.denormalize_y(args.get("destination_y", 0))

        pyautogui.moveTo(start_x, start_y)
        time.sleep(0.2)
        pyautogui.drag(dest_x - start_x, dest_y - start_y, duration=0.5)
        print(f"     Dragged from ({start_x}, {start_y}) to ({dest_x}, {dest_y})")
        return {"status": "success"}

    def _wait_5_seconds(self) -> Dict[str, Any]:
        """Execute wait_5_seconds action."""
        print("     Waiting 5 seconds...")
        time.sleep(5)
        return {"status": "success"}

    def _go_back(self) -> Dict[str, Any]:
        """Execute go_back action."""
        pyautogui.hotkey("command", "[")
        return {"status": "success"}

    def _go_forward(self) -> Dict[str, Any]:
        """Execute go_forward action."""
        pyautogui.hotkey("command", "]")
        return {"status": "success"}

    def _search(self) -> Dict[str, Any]:
        """Execute search action (Spotlight on macOS)."""
        pyautogui.hotkey("command", "space")
        return {"status": "success"}

    def _navigate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute navigate action."""
        url = args.get("url", "")
        print(f"     Navigate requested to: {url}")
        return {"status": "not_applicable", "message": "Desktop app context"}


def get_safety_confirmation(safety_decision: Dict[str, Any]) -> str:
    """Prompt user for confirmation when safety check is triggered.

    Args:
        safety_decision: Safety decision dictionary from model

    Returns:
        "CONTINUE" or "TERMINATE"
    """
    termcolor.cprint("\n⚠️  Safety service requires explicit confirmation!", color="red")
    print(
        f"Explanation: {safety_decision.get('explanation', 'No explanation provided')}"
    )

    decision = ""
    while decision.lower() not in ("y", "n", "yes", "no"):
        decision = input("Do you wish to proceed? [Y]es/[N]o: ")

    if decision.lower() in ("n", "no"):
        return "TERMINATE"
    return "CONTINUE"
