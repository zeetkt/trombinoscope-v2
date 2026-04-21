"""Shape masks for photo cropping (circle, rounded, hexagon)."""

import logging
import math
from typing import Literal

from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

ShapeType = Literal["square", "circle", "rounded", "hexagon"]


def create_circle_mask(size: int) -> Image.Image:
    """Create a circular mask for the given size.

    Args:
        size: The width and height of the mask in pixels.

    Returns:
        A grayscale mask image where white is opaque and black is transparent.
    """
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    return mask


def create_rounded_mask(size: int, radius_percent: float = 0.15) -> Image.Image:
    """Create a rounded rectangle mask for the given size.

    Args:
        size: The width and height of the mask in pixels.
        radius_percent: Corner radius as a percentage of the size (default 15%).

    Returns:
        A grayscale mask image where white is opaque and black is transparent.
    """
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    radius = int(size * radius_percent)
    draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
    return mask


def create_hexagon_mask(size: int) -> Image.Image:
    """Create a hexagonal mask for the given size.

    The hexagon is oriented with flat top and bottom.

    Args:
        size: The width and height of the mask in pixels.

    Returns:
        A grayscale mask image where white is opaque and black is transparent.
    """
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)

    # Calculate hexagon points
    # Hexagon with flat top and bottom
    center_x = size // 2
    center_y = size // 2
    radius = size // 2 - 2  # Small padding to avoid edge artifacts

    points = []
    for i in range(6):
        angle_deg = 60 * i  # Start from top (0 degrees)
        angle_rad = math.radians(angle_deg)
        x = center_x + radius * math.sin(angle_rad)
        y = center_y - radius * math.cos(angle_rad)
        points.append((x, y))

    draw.polygon(points, fill=255)
    return mask


def apply_shape_mask(
    image: Image.Image,
    shape: ShapeType,
    radius_percent: float = 0.15,
) -> Image.Image:
    """Apply a shape mask to an image.

    Args:
        image: The input image to mask.
        shape: The shape type to apply.
        radius_percent: Corner radius for rounded shape (default 15%).

    Returns:
        The image with the shape mask applied (RGBA mode).
    """
    if shape == "square":
        return image.convert("RGBA")

    size = min(image.size)

    # Create the appropriate mask
    if shape == "circle":
        mask = create_circle_mask(size)
    elif shape == "rounded":
        mask = create_rounded_mask(size, radius_percent)
    elif shape == "hexagon":
        mask = create_hexagon_mask(size)
    else:
        return image.convert("RGBA")

    # Resize image to square if needed
    if image.size != (size, size):
        image = image.resize((size, size), Image.Resampling.LANCZOS)

    # Apply mask
    rgba_image = image.convert("RGBA")
    rgba_image.putalpha(mask)

    return rgba_image


def get_shape_names() -> dict[str, str]:
    """Get a mapping of shape types to display names.

    Returns:
        Dictionary mapping shape types to human-readable names.
    """
    return {
        "square": "Carré",
        "circle": "Cercle",
        "rounded": "Arrondi",
        "hexagon": "Hexagone",
    }
