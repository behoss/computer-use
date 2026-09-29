"""Screen management for Computer Use Agent."""

import io
import pyautogui
from typing import Tuple


class ScreenManager:
    """Manages screen operations and screenshot capture."""

    def __init__(self, width: int, height: int):
        """Initialize screen manager.

        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        self.width = width
        self.height = height

    def denormalize_x(self, x: int) -> int:
        """Convert normalized x coordinate (0-999) to actual pixel coordinate.

        Args:
            x: Normalized x coordinate (0-999)

        Returns:
            Actual pixel x coordinate
        """
        return int(x / 1000 * self.width)

    def denormalize_y(self, y: int) -> int:
        """Convert normalized y coordinate (0-999) to actual pixel coordinate.

        Args:
            y: Normalized y coordinate (0-999)

        Returns:
            Actual pixel y coordinate
        """
        return int(y / 1000 * self.height)

    def denormalize_coords(self, x: int, y: int) -> Tuple[int, int]:
        """Convert normalized coordinates to actual pixel coordinates.

        Args:
            x: Normalized x coordinate (0-999)
            y: Normalized y coordinate (0-999)

        Returns:
            Tuple of (actual_x, actual_y) pixel coordinates
        """
        return self.denormalize_x(x), self.denormalize_y(y)

    def capture_screenshot(self) -> bytes:
        """Capture current screen state as PNG bytes.

        Returns:
            Screenshot as PNG bytes
        """
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    def get_center(self) -> Tuple[int, int]:
        """Get center coordinates of screen.

        Returns:
            Tuple of (center_x, center_y)
        """
        return self.width // 2, self.height // 2
