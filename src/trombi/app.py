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
from src.trombi.layout import Layout, compose_trombinoscope, compose_trombinoscope_a4, calculate_a4_layout
from src.trombi.pdf_generator import generate_pdf
from src.trombi.shapes import get_shape_names, ShapeType
from src.trombi.reorder import prepare_sortable_data, reorder_list, get_reordered_indices

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Générateur de trombinoscope",
        layout="wide",
    )

    st.title("Générateur de trombinoscope v2")
    st.markdown("1) Upload photos 2) Réorganisez 3) Personnalisez 4) Générez")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Photos")
        files = st.file_uploader(
            "Upload photos",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )

        # Initialize session state for reordered data
        if "reordered_images" not in st.session_state:
            st.session_state.reordered_images = None
            st.session_state.reordered_names = None
            st.session_state.reordered_files = None

        names: List[str] = []
        pil_imgs: List[Image.Image] = []

        if files:
            # Load images
            if st.session_state.reordered_images is None:
                pil_imgs = [Image.open(f).convert("RGB") for f in files]
                names = [f.name for f in files]
                st.session_state.reordered_images = pil_imgs
                st.session_state.reordered_names = names
                st.session_state.reordered_files = files
            else:
                pil_imgs = st.session_state.reordered_images
                names = st.session_state.reordered_names
                files = st.session_state.reordered_files

            # Drag and drop reordering
            st.subheader("Réorganiser (glisser-déposer)")

            try:
                from streamlit_sortables import sort_items

                # Create unique IDs for each image to track them across reordering
                if "image_ids" not in st.session_state or len(st.session_state.image_ids) != len(pil_imgs):
                    st.session_state.image_ids = [f"img_{i}" for i in range(len(pil_imgs))]

                # Create labels showing thumbnail + name
                # streamlit-sortables v0.3.1 supports direction='vertical' for better display
                sortable_labels = [f"📷 {name}" for name in names]
                sorted_labels = sort_items(
                    sortable_labels,
                    key="sortable_photos",
                    direction="vertical"
                )

                # Reorder if changed
                if sorted_labels and sorted_labels != sortable_labels:
                    # Find new order by matching labels
                    new_indices = []
                    for sorted_label in sorted_labels:
                        # Find which original index corresponds to this label
                        for i, name in enumerate(names):
                            if sorted_label == f"📷 {name}":
                                new_indices.append(i)
                                break

                    if len(new_indices) == len(pil_imgs):
                        st.session_state.reordered_images = reorder_list(pil_imgs, new_indices)
                        st.session_state.reordered_names = reorder_list(names, new_indices)
                        st.session_state.reordered_files = reorder_list(files, new_indices)
                        # Update IDs to match new order
                        st.session_state.image_ids = [st.session_state.image_ids[i] for i in new_indices]
                        st.rerun()
            except ImportError:
                st.info("streamlit-sortables non installé. Utilisez les numéros ci-dessous pour réorganiser.")

                # Fallback: manual reordering with numbers
                st.subheader("Réorganiser")
                new_order = []
                for i in range(len(pil_imgs)):
                    new_pos = st.number_input(
                        f"Position de '{names[i]}'",
                        min_value=1,
                        max_value=len(pil_imgs),
                        value=i + 1,
                        key=f"pos_{i}",
                    )
                    new_order.append((new_pos - 1, i))

                if st.button("Appliquer l'ordre"):
                    new_order.sort(key=lambda x: x[0])
                    new_indices = [x[1] for x in new_order]
                    st.session_state.reordered_images = reorder_list(pil_imgs, new_indices)
                    st.session_state.reordered_names = reorder_list(names, new_indices)
                    st.session_state.reordered_files = reorder_list(files, new_indices)
                    st.rerun()

            # Names input
            st.subheader("Noms")
            final_names: List[str] = []
            for i, name in enumerate(st.session_state.reordered_names):
                final_name = st.text_input(
                    f"Photo {i+1}",
                    value=name if not name.endswith(('.jpg', '.jpeg', '.png')) else "",
                    key=f"final_name_{i}",
                )
                final_names.append(final_name)

            pil_imgs = st.session_state.reordered_images
            files = st.session_state.reordered_files

    with col2:
        st.subheader("Paramètres")

        format_option = st.selectbox(
            "Format",
            ["Standard", "A4 Paysage (300 DPI)"],
            help="A4 Paysage optimise automatiquement la taille pour une page A4 en mode paysage"
        )

        use_a4 = format_option == "A4 Paysage (300 DPI)"

        if use_a4:
            st.info("ℹ️ Mode A4 Paysage : les dimensions sont calculées automatiquement pour optimiser l'impression sur une page A4 à 300 DPI (3508×2480 px).")

        # Shape selection
        shape_options = get_shape_names()
        shape = st.selectbox(
            "Forme des vignettes",
            options=list(shape_options.keys()),
            format_func=lambda x: shape_options[x],
            index=0,  # Default to square
        )

        # Shadow toggle (enabled by default)
        use_shadow = st.toggle("Ombre portée", value=True, help="Ajoute une ombre subtile sous chaque vignette")

        c1, c2, c3 = st.columns(3)
        with c1:
            if use_a4:
                st.metric("Colonnes", "Auto")
                cols = 4  # Valeur par défaut, sera recalculée
            else:
                cols = st.slider("Colonnes", 1, 8, settings.default_columns)
        with c2:
            if use_a4:
                st.metric("Taille vignettes", "Auto")
                out_size = 300  # Valeur par défaut, sera recalculée
            else:
                out_size = st.slider(
                    "Taille vignettes (px)", 256, 900, settings.default_output_size
                )
        with c3:
            if use_a4:
                st.metric("Marge", "Auto")
                padding = 20  # Valeur par défaut, sera recalculée
            else:
                padding = st.slider("Espacement (px)", 10, 80, settings.default_padding)

        c4, c5, c6 = st.columns(3)
        with c4:
            margin = st.slider("Marge visage", 0.2, 1.6, settings.default_margin)
        with c5:
            upward_bias = st.slider(
                "Décalage vers le haut", 0.0, 0.35, settings.default_upward_bias
            )
        with c6:
            bg = st.selectbox("Arrière-plan", ["#ffffff", "#f5f5f5", "#eeeeee"])

        font_size = st.slider("Taille police", 20, 80, settings.default_font_size)
        title_br = st.text_input("Titre (bas droite, optionnel)", "")

        if st.button("Générer", type="primary"):
            if not files:
                st.error("Aucune image fournie.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    # Use final names if available
                    labels_list = final_names if 'final_names' in locals() else names
                    labels = labels_list if any(labels_list) else None

                    # Progress callback for image processing
                    def update_progress(current: int, total: int) -> None:
                        progress = current / total
                        progress_bar.progress(min(progress, 0.5))
                        status_text.text(f"Traitement des images... {current}/{total}")

                    status_text.text("Détection et recadrage des visages...")
                    headshots = process_images_parallel(
                        pil_imgs,
                        out_size=out_size,
                        margin=margin,
                        upward_bias=upward_bias,
                        progress_callback=update_progress,
                    )

                    status_text.text("Composition de la grille...")
                    progress_bar.progress(0.7)

                    if use_a4:
                        layout = calculate_a4_layout(
                            num_images=len(headshots),
                            label_h=80,
                            bg=bg,
                            font_size=int(font_size),
                            shape=shape,
                            shadow=use_shadow,
                        )
                        st.info(f"Format A4: {layout.cols} colonnes, vignettes de {layout.out_size}px")
                        canvas = compose_trombinoscope_a4(
                            images=headshots,
                            labels=labels,
                            title_br=title_br,
                            layout=layout,
                        )
                    else:
                        layout = Layout(
                            cols=cols,
                            out_size=out_size,
                            padding=padding,
                            label_h=80,
                            bg=bg,
                            font_size=int(font_size),
                            shape=shape,
                            shadow=use_shadow,
                        )
                        canvas = compose_trombinoscope(
                            images=headshots,
                            labels=labels,
                            title_br=title_br,
                            layout=layout,
                        )

                    progress_bar.progress(0.9)
                    status_text.text("Finalisation...")

                    # Convert to RGB if necessary for display
                    if canvas.mode == "RGBA":
                        # Create white background for display
                        background = Image.new("RGB", canvas.size, bg)
                        background.paste(canvas, mask=canvas.split()[3])
                        canvas_rgb = background
                    else:
                        canvas_rgb = canvas

                    st.image(canvas_rgb, caption="Aperçu")

                    progress_bar.progress(1.0)
                    status_text.text("✅ Terminé !")

                    col_png, col_pdf = st.columns(2)

                    with col_png:
                        import io
                        buf = io.BytesIO()
                        canvas_rgb.save(buf, format="PNG")
                        buf.seek(0)
                        st.download_button(
                            label="📥 Télécharger PNG",
                            data=buf,
                            file_name="trombinoscope.png",
                            mime="image/png",
                        )

                    with col_pdf:
                        status_text.text("Génération du PDF...")
                        try:
                            pdf_bytes = generate_pdf(
                                images=headshots,
                                labels=labels,
                                title=title_br,
                                layout=layout,
                            )
                            st.download_button(
                                label="📄 Télécharger PDF (A4)",
                                data=pdf_bytes,
                                file_name="trombinoscope.pdf",
                                mime="application/pdf",
                            )
                        except Exception as pdf_error:
                            st.error(f"Erreur PDF: {pdf_error}")
                            logger.exception("PDF generation failed")

                    # Clear progress after a moment
                    import time
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()

                except Exception as e:
                    st.error(f"Erreur: {e}")
                    logger.exception("Processing failed")

    # Footer with author and license
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em; padding: 20px;'>
            © 2026 <strong>Bastien ERRICO</strong> | 
            <a href="https://github.com/zeetkt/trombinoscope-v2" target="_blank">GitHub</a> | 
            License MIT
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
