"""Image processing utilities for face cropping and manipulation."""

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

from PIL import Image

from config.settings import settings
from src.trombi.face_detector import FaceDetection, FaceDetector

logger = logging.getLogger(__name__)


def crop_face_square(
    image: Image.Image,
    face: Optional[FaceDetection] = None,
    out_size: int = settings.default_output_size,
    margin: float = settings.default_margin,
    upward_bias: float = settings.default_upward_bias,
) -> Image.Image:
    """Crop and resize an image to focus on a face."""
    if image.mode != "RGB":
        image = image.convert("RGB")

    iw, ih = image.size

    if face is None:
        # Fallback: center crop
        top = int(ih * 0.05)
        bottom = int(ih * 0.75)
        tmp = image.crop((0, top, iw, bottom))
        tw, th = tmp.size
        size = min(tw, th)
        left = (tw - size) // 2
        top2 = (th - size) // 2
        crop = tmp.crop((left, top2, left + size, top2 + size))
        return crop.resize((out_size, out_size), Image.Resampling.LANCZOS)

    cx = face.x + face.width / 2
    cy = face.y + face.height / 2 - upward_bias * face.height
    side = max(face.width, face.height) * (1.0 + margin)

    left = int(round(cx - side / 2))
    top = int(round(cy - side / 2))
    right = int(round(cx + side / 2))
    bottom = int(round(cy + side / 2))

    if left < 0:
        right -= left
        left = 0
    if top < 0:
        bottom -= top
        top = 0
    if right > iw:
        left -= right - iw
        right = iw
    if bottom > ih:
        top -= bottom - ih
        bottom = ih

    left = max(0, left)
    top = max(0, top)
    right = min(iw, right)
    bottom = min(ih, bottom)

    crop = image.crop((left, top, right, bottom))
    cw, ch = crop.size
    size = min(cw, ch)
    cx2, cy2 = cw / 2, ch / 2
    left2 = int(round(cx2 - size / 2))
    top2 = int(round(cy2 - size / 2))
    crop = crop.crop((left2, top2, left2 + size, top2 + size))

    return crop.resize((out_size, out_size), Image.Resampling.LANCZOS)


def process_single_image(
    image: Image.Image,
    detector: FaceDetector,
    out_size: int = settings.default_output_size,
    margin: float = settings.default_margin,
    upward_bias: float = settings.default_upward_bias,
) -> Image.Image:
    """Process a single image: detect face and crop."""
    face = detector.detect_largest_face(image)
    return crop_face_square(image, face, out_size, margin, upward_bias)


def process_images_parallel(
    images: List[Image.Image],
    out_size: int = settings.default_output_size,
    margin: float = settings.default_margin,
    upward_bias: float = settings.default_upward_bias,
    max_workers: int = settings.max_workers,
) -> List[Image.Image]:
    """Process multiple images in parallel."""
    if not images:
        return []

    def process_with_detector(img: Image.Image) -> Image.Image:
        with FaceDetector() as detector:
            return process_single_image(img, detector, out_size, margin, upward_bias)

    if len(images) == 1:
        return [process_with_detector(images[0])]

    results = [None] * len(images)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_with_detector, img): idx
            for idx, img in enumerate(images)
        }
        for future in futures:
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                logger.error(f"Error processing image {idx}: {e}")
                raise

    return results
