"""Grid layout composition for the trombinoscope."""

import math
from dataclasses import dataclass
from typing import List, Optional, Union

from PIL import Image, ImageDraw, ImageFont

from config.settings import settings


@dataclass
class Layout:
    """Configuration for the grid layout."""

    cols: int
    out_size: int
    padding: int
    label_h: int
    bg: str
    font_size: int = 46


def load_font(
    size: int, bold: bool = True
) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
    """Load a font from the configured candidates."""
    candidates = settings.font_candidates
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            pass
    return ImageFont.load_default()


def compose_trombinoscope(
    images: List[Image.Image],
    labels: Optional[List[str]],
    title_br: str,
    layout: Layout,
) -> Image.Image:
    """Compose images into a trombinoscope grid."""
    n = len(images)
    cols = max(1, layout.cols)
    rows = math.ceil(n / cols)

    cell = layout.out_size
    pad = layout.padding
    label_h = layout.label_h

    canvas_w = cols * cell + (cols + 1) * pad
    canvas_h = rows * (cell + label_h) + (rows + 1) * pad

    canvas = Image.new("RGB", (canvas_w, canvas_h), layout.bg)
    draw = ImageDraw.Draw(canvas)

    font_label = load_font(layout.font_size, bold=True)
    font_title = load_font(layout.font_size + 8, bold=True)

    for i, img in enumerate(images):
        r, c = divmod(i, cols)
        x = pad + c * (cell + pad)
        y = pad + r * (cell + label_h + pad)

        canvas.paste(img, (x, y))

        if labels and i < len(labels) and labels[i].strip():
            text = labels[i].strip()
            bbox = draw.textbbox((0, 0), text, font=font_label)
            tw = bbox[2] - bbox[0]
            tx = x + (cell - tw) // 2
            ty = y + cell + 10
            draw.text((tx, ty), text, fill="black", font=font_label)

    if title_br.strip():
        bbox = draw.textbbox((0, 0), title_br, font=font_title)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            (canvas_w - tw - 30, canvas_h - th - 20),
            title_br,
            fill="black",
            font=font_title,
        )

    return canvas
