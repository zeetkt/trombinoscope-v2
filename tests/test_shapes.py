"""Tests for shape masks."""

import pytest
from PIL import Image

from src.trombi.shapes import (
    apply_shape_mask,
    create_circle_mask,
    create_hexagon_mask,
    create_rounded_mask,
    get_shape_names,
)


class TestCreateCircleMask:
    """Tests for create_circle_mask function."""

    def test_circle_mask_size(self):
        """Test that circle mask has correct size."""
        mask = create_circle_mask(100)
        assert mask.size == (100, 100)
        assert mask.mode == "L"

    def test_circle_mask_is_opaque_in_center(self):
        """Test that center of circle is opaque."""
        mask = create_circle_mask(100)
        assert mask.getpixel((50, 50)) == 255


class TestCreateRoundedMask:
    """Tests for create_rounded_mask function."""

    def test_rounded_mask_size(self):
        """Test that rounded mask has correct size."""
        mask = create_rounded_mask(100, radius_percent=0.15)
        assert mask.size == (100, 100)
        assert mask.mode == "L"

    def test_rounded_mask_center_opaque(self):
        """Test that center of rounded mask is opaque."""
        mask = create_rounded_mask(100)
        assert mask.getpixel((50, 50)) == 255


class TestCreateHexagonMask:
    """Tests for create_hexagon_mask function."""

    def test_hexagon_mask_size(self):
        """Test that hexagon mask has correct size."""
        mask = create_hexagon_mask(100)
        assert mask.size == (100, 100)
        assert mask.mode == "L"

    def test_hexagon_mask_center_opaque(self):
        """Test that center of hexagon mask is opaque."""
        mask = create_hexagon_mask(100)
        assert mask.getpixel((50, 50)) == 255


class TestApplyShapeMask:
    """Tests for apply_shape_mask function."""

    def test_square_shape_returns_rgba(self):
        """Test that square shape returns RGBA image."""
        img = Image.new("RGB", (100, 100), color="red")
        result = apply_shape_mask(img, "square")
        assert result.mode == "RGBA"

    def test_circle_shape_returns_rgba_with_alpha(self):
        """Test that circle shape returns RGBA with transparency."""
        img = Image.new("RGB", (100, 100), color="red")
        result = apply_shape_mask(img, "circle")
        assert result.mode == "RGBA"
        # Corners should be transparent
        alpha = result.split()[3]
        assert alpha.getpixel((0, 0)) == 0
        assert alpha.getpixel((99, 99)) == 0

    def test_invalid_shape_returns_rgba(self):
        """Test that invalid shape defaults to RGBA."""
        img = Image.new("RGB", (100, 100), color="red")
        result = apply_shape_mask(img, "invalid")  # type: ignore
        assert result.mode == "RGBA"


class TestGetShapeNames:
    """Tests for get_shape_names function."""

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        names = get_shape_names()
        assert isinstance(names, dict)
        assert len(names) > 0

    def test_contains_expected_shapes(self):
        """Test that expected shapes are present."""
        names = get_shape_names()
        assert "square" in names
        assert "circle" in names
        assert "rounded" in names
        assert "hexagon" in names
