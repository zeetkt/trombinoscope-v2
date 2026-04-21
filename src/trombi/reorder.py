"""Helpers for drag-and-drop reordering functionality."""

import base64
import io
import logging
from dataclasses import dataclass
from typing import List, Tuple

from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class ImageItem:
    """Represents an image item for reordering."""

    id: str
    name: str
    thumbnail_base64: str


def create_thumbnail(image: Image.Image, size: int = 100) -> Image.Image:
    """Create a thumbnail of the image.

    Args:
        image: The input image.
        size: The maximum size of the thumbnail.

    Returns:
        A thumbnail image.
    """
    thumb = image.copy()
    thumb.thumbnail((size, size))
    return thumb


def image_to_base64(image: Image.Image) -> str:
    """Convert a PIL image to base64 string.

    Args:
        image: The PIL image to convert.

    Returns:
        Base64 encoded string of the image.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def create_sortable_items(
    images: List[Image.Image],
    filenames: List[str],
) -> List[ImageItem]:
    """Create sortable items from images and filenames.

    Args:
        images: List of PIL images.
        filenames: List of original filenames.

    Returns:
        List of ImageItem objects ready for sortables.
    """
    items = []
    for i, (img, filename) in enumerate(zip(images, filenames)):
        thumb = create_thumbnail(img, size=100)
        b64 = image_to_base64(thumb)
        item = ImageItem(
            id=f"img_{i}",
            name=filename,
            thumbnail_base64=b64,
        )
        items.append(item)
    return items


def reorder_list(
    original_list: List,
    new_order_indices: List[int],
) -> List:
    """Reorder a list based on new indices.

    Args:
        original_list: The original list to reorder.
        new_order_indices: List of indices in the new order.

    Returns:
        The reordered list.
    """
    return [original_list[i] for i in new_order_indices]


def get_reordered_indices(sortable_result: List[dict]) -> List[int]:
    """Extract the original indices from sortable result.

    Args:
        sortable_result: Result from streamlit-sortables.

    Returns:
        List of original indices in the new order.
    """
    indices = []
    for item in sortable_result:
        # Extract index from id (format: "img_N")
        idx_str = item["id"].split("_")[1]
        indices.append(int(idx_str))
    return indices


def prepare_sortable_data(
    images: List[Image.Image],
    names: List[str],
) -> List[dict]:
    """Prepare data for streamlit-sortables component.

    Args:
        images: List of PIL images.
        names: List of names/labels for each image.

    Returns:
        List of dictionaries for sortables component.
    """
    items = []
    for i, (img, name) in enumerate(zip(images, names)):
        thumb = create_thumbnail(img, size=80)
        b64 = image_to_base64(thumb)
        items.append({
            "id": f"img_{i}",
            "label": name if name else f"Photo {i+1}",
            "image": f"data:image/png;base64,{b64}",
        })
    return items
