"""Tests for the layout module."""

from PIL import Image

from src.trombi.layout import Layout, compose_trombinoscope, load_font


class TestLayout:
    """Tests for Layout dataclass."""

    def test_layout_creation(self):
        """Test creating a Layout object."""
        layout = Layout(cols=4, out_size=256, padding=20, label_h=60, bg="#ffffff")
        assert layout.cols == 4
        assert layout.out_size == 256
        assert layout.padding == 20


class TestComposeTrombinoscope:
    """Tests for compose_trombinoscope function."""

    def test_compose_single_image(self):
        """Test composing with a single image."""
        img = Image.new("RGB", (256, 256), color="red")
        layout = Layout(cols=2, out_size=256, padding=20, label_h=60, bg="#ffffff")
        result = compose_trombinoscope([img], labels=None, title_br="", layout=layout)
        assert isinstance(result, Image.Image)

    def test_compose_multiple_images(self):
        """Test composing with multiple images."""
        images = [
            Image.new("RGB", (256, 256), color=c) for c in ["red", "green", "blue"]
        ]
        layout = Layout(cols=2, out_size=256, padding=20, label_h=60, bg="#ffffff")
        result = compose_trombinoscope(images, labels=None, title_br="", layout=layout)
        assert isinstance(result, Image.Image)


class TestLoadFont:
    """Tests for load_font function."""

    def test_load_font_returns_font(self):
        """Test that load_font returns a font object."""
        font = load_font(20)
        assert font is not None
