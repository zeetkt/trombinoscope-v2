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


# A4 Landscape dimensions at 300 DPI (print quality)
A4_LANDSCAPE_WIDTH = 3508  # 297mm at 300 DPI
A4_LANDSCAPE_HEIGHT = 2480  # 210mm at 300 DPI
A4_MARGIN = 100  # Margin in pixels


def calculate_a4_layout(
    num_images: int,
    label_h: int = 80,
    bg: str = "#ffffff",
    font_size: int = 46,
) -> Layout:
    """Calculate optimal layout for A4 landscape format.

    Automatically determines the best number of columns and image size
    to fit all images on an A4 landscape page at 300 DPI.
    Maximizes image size to fill the page harmoniously.

    Args:
        num_images: Number of images to arrange
        label_h: Height reserved for labels
        bg: Background color
        font_size: Font size for labels

    Returns:
        Layout optimized for A4 landscape
    """
    # Usable area (with margins)
    usable_width = A4_LANDSCAPE_WIDTH - (2 * A4_MARGIN)
    usable_height = A4_LANDSCAPE_HEIGHT - (2 * A4_MARGIN)

    # Try different configurations to find optimal fit
    best_layout = None
    best_cell_size = 0

    # Test different column counts (1 to min(num_images, 6))
    # 6 columns max for A4 to keep images readable
    for cols in range(1, min(num_images + 1, 7)):
        rows = math.ceil(num_images / cols)

        # Try different padding values to find optimal balance
        for padding in [30, 40, 50, 60]:
            # Calculate max cell size from width constraint
            # cols * cell_size + (cols + 1) * padding <= usable_width
            max_cell_width = (usable_width - (cols + 1) * padding) // cols

            # Calculate max cell size from height constraint
            # rows * (cell_size + label_h) + (rows + 1) * padding <= usable_height
            max_cell_height = (usable_height - (rows + 1) * padding) // rows - label_h

            # Use the smaller dimension to ensure square cells
            cell_size = min(max_cell_width, max_cell_height)

            # Skip if too small
            if cell_size < 150:
                continue

            # Prefer larger cell sizes
            # With fewer images, we want to maximize cell size
            if cell_size > best_cell_size:
                best_cell_size = cell_size
                best_layout = Layout(
                    cols=cols,
                    out_size=cell_size,
                    padding=padding,
                    label_h=label_h,
                    bg=bg,
                    font_size=font_size,
                )

    # Fallback if no good layout found
    if best_layout is None:
        # For many images, use smaller cells
        cols = min(6, num_images)
        rows = math.ceil(num_images / cols)
        padding = 20
        
        # Calculate max possible size
        max_cell_width = (usable_width - (cols + 1) * padding) // cols
        max_cell_height = (usable_height - (rows + 1) * padding) // rows - label_h
        cell_size = min(max_cell_width, max_cell_height, 200)
        
        best_layout = Layout(
            cols=cols,
            out_size=max(cell_size, 100),
            padding=padding,
            label_h=label_h,
            bg=bg,
            font_size=font_size,
        )

    return best_layout


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


def compose_trombinoscope_a4(
    images: List[Image.Image],
    labels: Optional[List[str]],
    title_br: str,
    layout: Layout,
) -> Image.Image:
    """Compose images into an A4 landscape format (3508x2480px at 300 DPI).
    
    The grid fills the width with equal horizontal spacing.
    Vertical spacing is minimal to fit all rows.
    """
    n = len(images)
    cols = max(1, layout.cols)
    rows = math.ceil(n / cols)

    label_h = layout.label_h
    h_margin = 80  # Horizontal margin
    v_margin = 60  # Vertical margin
    v_spacing = 20  # Fixed vertical spacing between rows

    # Calculate cell size to fill width with equal horizontal spacing
    # Available width = A4 width - 2 * h_margin
    # Width = cols * cell_size + (cols + 1) * h_spacing
    available_width = A4_LANDSCAPE_WIDTH - 2 * h_margin
    
    # Calculate max cell size that fits in height with minimal vertical spacing
    # Height = rows * (cell_size + label_h) + (rows + 1) * v_spacing + 2 * v_margin <= A4 height
    available_height = A4_LANDSCAPE_HEIGHT - 2 * v_margin
    max_cell_from_height = (available_height - (rows + 1) * v_spacing) // rows - label_h
    
    # Calculate horizontal spacing to fill width with this cell size
    # available_width = cols * cell_size + (cols + 1) * h_spacing
    h_spacing = (available_width - cols * max_cell_from_height) / (cols + 1)
    
    if h_spacing >= 15:  # Minimum 15px between images horizontally
        cell_size = max_cell_from_height
    else:
        # Width is limiting, calculate cell size from width
        h_spacing = 15
        cell_size = (available_width - (cols + 1) * h_spacing) // cols

    # Ensure minimum cell size
    cell_size = max(cell_size, 100)
    h_pad = int(h_spacing)

    # Calculate actual grid dimensions
    grid_w = cols * cell_size + (cols + 1) * h_pad
    grid_h = rows * (cell_size + label_h) + (rows + 1) * v_spacing

    # Create A4 canvas with exact dimensions
    a4_canvas = Image.new("RGB", (A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT), layout.bg)
    draw = ImageDraw.Draw(a4_canvas)

    font_label = load_font(layout.font_size, bold=True)
    font_title = load_font(layout.font_size + 8, bold=True)

    # Center the grid on A4 page
    offset_x = (A4_LANDSCAPE_WIDTH - grid_w) // 2
    offset_y = (A4_LANDSCAPE_HEIGHT - grid_h) // 2

    for i, img in enumerate(images):
        r, c = divmod(i, cols)
        x = offset_x + h_pad + c * (cell_size + h_pad)
        y = offset_y + v_spacing + r * (cell_size + label_h + v_spacing)

        # Resize image to fit the cell size
        img_resized = img.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
        a4_canvas.paste(img_resized, (x, y))

        if labels and i < len(labels) and labels[i].strip():
            text = labels[i].strip()
            bbox = draw.textbbox((0, 0), text, font=font_label)
            tw = bbox[2] - bbox[0]
            tx = x + (cell_size - tw) // 2
            ty = y + cell_size + 10
            draw.text((tx, ty), text, fill="black", font=font_label)

    if title_br.strip():
        bbox = draw.textbbox((0, 0), title_br, font=font_title)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            (A4_LANDSCAPE_WIDTH - tw - 100, A4_LANDSCAPE_HEIGHT - th - 80),
            title_br,
            fill="black",
            font=font_title,
        )

    return a4_canvas
