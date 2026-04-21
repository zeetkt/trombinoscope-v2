"""Streamlit application for the trombinoscope generator."""

import logging
import sys
from pathlib import Path
from typing import List

import streamlit as st
from PIL import Image

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.trombi.image_processor import process_images_parallel
from src.trombi.layout import Layout, compose_trombinoscope, calculate_a4_layout

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Générateur de trombinoscope",
        layout="wide",
    )

    st.title("Générateur de trombinoscope v2")
    st.markdown("1) Upload photos 2) Enter names 3) Download PNG")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Photos")
        files = st.file_uploader(
            "Upload photos",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )

        names: List[str] = []
        if files:
            st.subheader("Names")
            for i, f in enumerate(files):
                name = st.text_input(f"Photo {i+1}: {f.name}", key=f"name_{i}")
                names.append(name)

    with col2:
        st.subheader("Settings")

        format_option = st.selectbox(
            "Format",
            ["Standard", "A4 Paysage (300 DPI)"],
            help="A4 Paysage optimise automatiquement la taille pour une page A4 en mode paysage"
        )
        
        use_a4 = format_option == "A4 Paysage (300 DPI)"

        if use_a4:
            st.info("ℹ️ Mode A4 Paysage : les dimensions sont calculées automatiquement pour optimiser l'impression sur une page A4 à 300 DPI (3508×2480 px).")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if use_a4:
                st.metric("Colonnes", "Auto")
                cols = 4  # Valeur par défaut, sera recalculée
            else:
                cols = st.slider("Columns", 1, 8, settings.default_columns)
        with c2:
            if use_a4:
                st.metric("Taille vignettes", "Auto")
                out_size = 300  # Valeur par défaut, sera recalculée
            else:
                out_size = st.slider(
                    "Thumbnail size (px)", 256, 900, settings.default_output_size
                )
        with c3:
            if use_a4:
                st.metric("Marge", "Auto")
                padding = 20  # Valeur par défaut, sera recalculée
            else:
                padding = st.slider("Padding (px)", 10, 80, settings.default_padding)

        c4, c5, c6 = st.columns(3)
        with c4:
            margin = st.slider("Face margin", 0.2, 1.6, settings.default_margin)
        with c5:
            upward_bias = st.slider(
                "Upward shift", 0.0, 0.35, settings.default_upward_bias
            )
        with c6:
            bg = st.selectbox("Background", ["#ffffff", "#f5f5f5", "#eeeeee"])

        font_size = st.slider("Font size", 20, 80, settings.default_font_size)
        title_br = st.text_input("Title (bottom right, optional)", "")

        if st.button("Generate", type="primary"):
            if not files:
                st.error("No images provided.")
            else:
                with st.spinner("Processing..."):
                    try:
                        pil_imgs = [Image.open(f).convert("RGB") for f in files]

                        headshots = process_images_parallel(
                            pil_imgs,
                            out_size=out_size,
                            margin=margin,
                            upward_bias=upward_bias,
                        )

                        labels = names if any(names) else None

                        if use_a4:
                            layout = calculate_a4_layout(
                                num_images=len(headshots),
                                label_h=80,
                                bg=bg,
                                font_size=int(font_size),
                            )
                            st.info(f"Format A4: {layout.cols} colonnes, vignettes de {layout.out_size}px")
                        else:
                            layout = Layout(
                                cols=cols,
                                out_size=out_size,
                                padding=padding,
                                label_h=80,
                                bg=bg,
                                font_size=int(font_size),
                            )

                        canvas = compose_trombinoscope(
                            images=headshots,
                            labels=labels,
                            title_br=title_br,
                            layout=layout,
                        )

                        st.image(canvas, caption="Preview")

                        import io
                        buf = io.BytesIO()
                        canvas.save(buf, format="PNG")
                        buf.seek(0)
                        st.download_button(
                            label="Download PNG",
                            data=buf,
                            file_name="trombinoscope.png",
                            mime="image/png",
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")
                        logger.exception("Processing failed")


if __name__ == "__main__":
    main()
