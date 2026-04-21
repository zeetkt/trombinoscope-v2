"""Tests for the image processor module."""

from PIL import Image

from src.trombi.face_detector import FaceDetection
from src.trombi.image_processor import crop_face_square


class TestCropFaceSquare:
    """Tests for crop_face_square function."""

    def test_crop_without_face(self):
        """Test cropping without face (fallback mode)."""
        img = Image.new("RGB", (500, 600), color="green")
        result = crop_face_square(img, face=None, out_size=256)
        assert result.size == (256, 256)

    def test_crop_with_face(self):
        """Test cropping with a face detection."""
        img = Image.new("RGB", (500, 600), color="green")
        face = FaceDetection(x=200, y=200, width=100, height=100, confidence=0.9)
        result = crop_face_square(img, face=face, out_size=256)
        assert result.size == (256, 256)

    def test_crop_converts_rgba(self):
        """Test RGBA images are converted to RGB."""
        img = Image.new("RGBA", (500, 600), color=(0, 255, 0, 128))
        result = crop_face_square(img, face=None, out_size=256)
        assert result.mode == "RGB"
