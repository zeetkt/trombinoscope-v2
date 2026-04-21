"""Utility functions for the trombinoscope application."""

import logging
from typing import Tuple

from PIL import Image

logger = logging.getLogger(__name__)


def validate_image_file(file_path: str) -> Tuple[bool, str]:
    """Validate an image file. Returns (is_valid, error_message)."""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True, ""
    except Exception as e:
        return False, f"Invalid image file: {e}"


def get_image_dimensions(image: Image.Image) -> Tuple[int, int]:
    """Get image dimensions as (width, height)."""
    return image.size
