"""Tests for reorder helpers."""

import pytest
from PIL import Image

from src.trombi.reorder import (
    create_sortable_items,
    create_thumbnail,
    get_reordered_indices,
    image_to_base64,
    prepare_sortable_data,
    reorder_list,
)


class TestCreateThumbnail:
    """Tests for create_thumbnail function."""

    def test_thumbnail_size(self):
        """Test that thumbnail respects max size."""
        img = Image.new("RGB", (500, 500), color="red")
        thumb = create_thumbnail(img, size=100)
        assert thumb.size[0] <= 100
        assert thumb.size[1] <= 100


class TestImageToBase64:
    """Tests for image_to_base64 function."""

    def test_returns_string(self):
        """Test that function returns a string."""
        img = Image.new("RGB", (10, 10), color="red")
        b64 = image_to_base64(img)
        assert isinstance(b64, str)
        assert len(b64) > 0


class TestReorderList:
    """Tests for reorder_list function."""

    def test_reorder_list(self):
        """Test that list is reordered correctly."""
        original = ["a", "b", "c", "d"]
        new_order = [2, 0, 3, 1]
        result = reorder_list(original, new_order)
        assert result == ["c", "a", "d", "b"]


class TestGetReorderedIndices:
    """Tests for get_reordered_indices function."""

    def test_extracts_indices(self):
        """Test that indices are extracted correctly."""
        sortable_result = [
            {"id": "img_2", "label": "Item 2"},
            {"id": "img_0", "label": "Item 0"},
            {"id": "img_1", "label": "Item 1"},
        ]
        indices = get_reordered_indices(sortable_result)
        assert indices == [2, 0, 1]


class TestPrepareSortableData:
    """Tests for prepare_sortable_data function."""

    def test_returns_list_of_dicts(self):
        """Test that function returns list of dictionaries."""
        imgs = [Image.new("RGB", (50, 50)) for _ in range(3)]
        names = ["A", "B", "C"]
        data = prepare_sortable_data(imgs, names)
        assert isinstance(data, list)
        assert len(data) == 3
        for item in data:
            assert "id" in item
            assert "label" in item
            assert "image" in item
