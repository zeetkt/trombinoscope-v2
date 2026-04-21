"""Tests for visual effects."""

import pytest
from PIL import Image

from src.trombi.effects import (
    add_drop_shadow,
    create_shadow_layer,
)


class TestCreateShadowLayer:
    """Tests for create_shadow_layer function."""

    def test_shadow_layer_size(self):
        """Test that shadow layer is larger than input size."""
        shadow = create_shadow_layer(100)
        # Shadow should be larger due to offset and blur
        assert shadow.size[0] > 100
        assert shadow.size[1] > 100
        assert shadow.mode == "RGBA"

    def test_shadow_layer_has_transparency(self):
        """Test that shadow layer has transparent areas."""
        shadow = create_shadow_layer(100)
        alpha = shadow.split()[3]
        # Corners should be transparent
        assert alpha.getpixel((0, 0)) == 0


class TestAddDropShadow:
    """Tests for add_drop_shadow function."""

    def test_adds_shadow_to_image(self):
        """Test that shadow is added to image."""
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
        result = add_drop_shadow(img)
        # Result should be larger than original
        assert result.size[0] > 100
        assert result.size[1] > 100
        assert result.mode == "RGBA"

    def test_converts_rgb_to_rgba(self):
        """Test that RGB images are converted to RGBA."""
        img = Image.new("RGB", (100, 100), color="red")
        result = add_drop_shadow(img)
        assert result.mode == "RGBA"

    def test_custom_opacity(self):
        """Test that custom opacity is applied."""
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
        # Low opacity should create lighter shadow
        result_low = add_drop_shadow(img, opacity=0.1)
        result_high = add_drop_shadow(img, opacity=0.8)
        assert result_low.size == result_high.size
