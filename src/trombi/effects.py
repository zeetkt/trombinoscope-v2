"""Visual effects for images (drop shadows, etc.)."""

import logging
from typing import Tuple

from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)

# Default subtle shadow settings
DEFAULT_SHADOW_OFFSET = 4
DEFAULT_SHADOW_BLUR = 8
DEFAULT_SHADOW_OPACITY = 0.30
DEFAULT_SHADOW_COLOR = (0, 0, 0)


def create_shadow_layer(
    size: int,
    offset: int = DEFAULT_SHADOW_OFFSET,
    blur: int = DEFAULT_SHADOW_BLUR,
    opacity: float = DEFAULT_SHADOW_OPACITY,
    color: Tuple[int, int, int] = DEFAULT_SHADOW_COLOR,
) -> Image.Image:
    """Create a shadow layer for a square image.

    Args:
        size: The size of the image that will cast the shadow.
        offset: The offset of the shadow in pixels (default 4).
        blur: The blur radius for the shadow (default 8).
        opacity: The opacity of the shadow (0.0-1.0, default 0.30).
        color: The RGB color of the shadow (default black).

    Returns:
        An RGBA image containing only the shadow, sized to fit the shadow.
    """
    # Calculate canvas size to accommodate the shadow offset
    canvas_size = size + offset * 2 + blur * 2

    # Create a solid square for the shadow source
    shadow_size = size + blur * 2
    shadow = Image.new("RGBA", (shadow_size, shadow_size), (*color, 0))
    draw = Image.new("RGBA", (size, size), (*color, int(255 * opacity)))

    # Paste the solid shadow at the center
    shadow.paste(draw, (blur, blur))

    # Apply Gaussian blur
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))

    # Create the full canvas and paste the shadow with offset
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    shadow_x = offset + blur
    shadow_y = offset + blur
    canvas.paste(shadow, (shadow_x, shadow_y), shadow)

    return canvas


def add_drop_shadow(
    image: Image.Image,
    offset: int = DEFAULT_SHADOW_OFFSET,
    blur: int = DEFAULT_SHADOW_BLUR,
    opacity: float = DEFAULT_SHADOW_OPACITY,
    color: Tuple[int, int, int] = DEFAULT_SHADOW_COLOR,
) -> Image.Image:
    """Add a drop shadow to an image.

    The image is centered on a larger canvas with the shadow applied
    behind it.

    Args:
        image: The input image (RGBA for best results).
        offset: The offset of the shadow in pixels (default 4).
        blur: The blur radius for the shadow (default 8).
        opacity: The opacity of the shadow (0.0-1.0, default 0.30).
        color: The RGB color of the shadow (default black).

    Returns:
        A new RGBA image with the shadow applied.
    """
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    size = min(image.size)

    # Create shadow layer
    shadow_layer = create_shadow_layer(
        size=size,
        offset=offset,
        blur=blur,
        opacity=opacity,
        color=color,
    )

    # Calculate positions
    canvas_size = size + offset * 2 + blur * 2
    image_x = blur
    image_y = blur
    shadow_x = 0
    shadow_y = offset

    # Create final canvas
    result = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

    # Paste shadow first
    result.paste(shadow_layer, (shadow_x, shadow_y), shadow_layer)

    # Paste image on top
    result.paste(image, (image_x, image_y), image)

    return result


def add_drop_shadow_to_cell(
    image: Image.Image,
    cell_size: int,
    offset: int = DEFAULT_SHADOW_OFFSET,
    blur: int = DEFAULT_SHADOW_BLUR,
    opacity: float = DEFAULT_SHADOW_OPACITY,
) -> Image.Image:
    """Add a drop shadow and fit into a specific cell size.

    This is useful for grid layouts where all cells must be the same size.
    The shadow is applied, then the image is resized to fit the cell.

    Args:
        image: The input image.
        cell_size: The target cell size for the final image.
        offset: The offset of the shadow in pixels (default 4).
        blur: The blur radius for the shadow (default 8).
        opacity: The opacity of the shadow (0.0-1.0, default 0.30).

    Returns:
        A new RGBA image with shadow, fitted to the cell size.
    """
    # Add shadow first
    with_shadow = add_drop_shadow(
        image,
        offset=offset,
        blur=blur,
        opacity=opacity,
    )

    # Resize to fit cell with shadow included
    # The image with shadow is larger, so we need to account for that
    shadow_extra = offset * 2 + blur * 2
    target_size = cell_size + shadow_extra

    if with_shadow.size != (target_size, target_size):
        with_shadow = with_shadow.resize(
            (target_size, target_size),
            Image.Resampling.LANCZOS,
        )

    return with_shadow
