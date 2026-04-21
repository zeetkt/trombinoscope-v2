"""PDF generation for trombinoscope output."""

import io
import logging
import math
from typing import List, Optional

from PIL import Image
from fpdf import FPDF

from src.trombi.layout import Layout, A4_LANDSCAPE_WIDTH, A4_LANDSCAPE_HEIGHT

logger = logging.getLogger(__name__)

# A4 Landscape at 300 DPI in mm
A4_WIDTH_MM = 297  # mm
A4_HEIGHT_MM = 210  # mm


def generate_pdf(
    images: List[Image.Image],
    labels: Optional[List[str]],
    title: str = "",
    layout: Optional[Layout] = None,
) -> bytes:
    """Generate a PDF from the trombinoscope images.

    Creates an A4 landscape PDF at print quality (300 DPI equivalent).

    Args:
        images: List of images to include in the PDF.
        labels: Optional list of labels for each image.
        title: Optional title to display on the PDF.
        layout: Layout configuration. If None, auto-calculates A4 layout.

    Returns:
        The PDF file content as bytes.
    """
    if not images:
        raise ValueError("No images provided for PDF generation")

    # Create PDF in landscape A4
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()

    # Calculate layout if not provided
    if layout is None:
        from src.trombi.layout import calculate_a4_layout
        layout = calculate_a4_layout(
            num_images=len(images),
            label_h=80,
            bg="#ffffff",
            font_size=46,
        )

    n = len(images)
    cols = max(1, layout.cols)
    rows = math.ceil(n / cols)

    label_h = layout.label_h
    h_margin = 10  # mm
    v_margin = 8   # mm
    v_spacing = 3  # mm

    # Calculate cell size to fill width
    available_width = A4_WIDTH_MM - 2 * h_margin
    available_height = A4_HEIGHT_MM - 2 * v_margin

    # Calculate max cell size from height constraint
    max_cell_from_height = (
        available_height - (rows + 1) * v_spacing
    ) / rows - (label_h / 10)  # Convert label_h from px to mm roughly

    # Calculate horizontal spacing
    h_spacing = (available_width - cols * max_cell_from_height) / (cols + 1)

    if h_spacing >= 3:  # Minimum 3mm between images
        cell_size_mm = max_cell_from_height
    else:
        h_spacing = 3
        cell_size_mm = (available_width - (cols + 1) * h_spacing) / cols

    cell_size_mm = max(cell_size_mm, 20)  # Minimum 20mm
    h_pad = h_spacing

    # Calculate actual grid dimensions
    grid_w = cols * cell_size_mm + (cols + 1) * h_pad
    grid_h = rows * (cell_size_mm + label_h / 10 + v_spacing)

    # Center the grid on A4 page
    offset_x = (A4_WIDTH_MM - grid_w) / 2
    offset_y = (A4_HEIGHT_MM - grid_h) / 2

    # Add images to PDF
    for i, img in enumerate(images):
        r, c = divmod(i, cols)
        x = offset_x + h_pad + c * (cell_size_mm + h_pad)
        y = offset_y + v_spacing + r * (cell_size_mm + label_h / 10 + v_spacing)

        # Convert PIL image to bytes
        img_bytes = io.BytesIO()
        # Resize to appropriate size for PDF (150 DPI is usually enough for PDF)
        pdf_size = int(cell_size_mm * 5.9)  # ~150 DPI
        img_resized = img.resize((pdf_size, pdf_size), Image.Resampling.LANCZOS)
        img_resized.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Add image to PDF
        pdf.image(img_bytes, x=x, y=y, w=cell_size_mm, h=cell_size_mm)

        # Add label if provided
        if labels and i < len(labels) and labels[i].strip():
            text = labels[i].strip()
            pdf.set_xy(x, y + cell_size_mm + 1)
            pdf.set_font("Arial", "B", 8)
            pdf.cell(cell_size_mm, 5, text, align="C")

    # Add title if provided
    if title.strip():
        pdf.set_xy(A4_WIDTH_MM - 60, A4_HEIGHT_MM - 15)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, title, align="R")

    # Return PDF as bytes
    return pdf.output()
