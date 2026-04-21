"""Tests for the face detector module."""

from PIL import Image

from src.trombi.face_detector import FaceDetection, FaceDetector


class TestFaceDetection:
    """Tests for FaceDetection dataclass."""

    def test_face_detection_creation(self):
        """Test creating a FaceDetection object."""
        face = FaceDetection(x=10, y=20, width=100, height=150, confidence=0.95)
        assert face.x == 10
        assert face.y == 20
        assert face.width == 100
        assert face.height == 150
        assert face.confidence == 0.95

    def test_face_detection_area(self):
        """Test that face area is calculated correctly."""
        face = FaceDetection(x=0, y=0, width=100, height=100, confidence=0.9)
        assert face.width * face.height == 10000


class TestFaceDetector:
    """Tests for FaceDetector class."""

    def test_detector_initialization(self):
        """Test that detector initializes correctly."""
        detector = FaceDetector(min_detection_confidence=0.5, model_selection=0)
        assert detector.min_detection_confidence == 0.5
        assert detector.model_selection == 0
        detector.close()

    def test_detector_context_manager(self):
        """Test that detector works as context manager."""
        with FaceDetector() as detector:
            assert detector._detector is not None

    def test_detect_faces_empty_image(self):
        """Test detection on empty/solid color image."""
        with FaceDetector() as detector:
            # Create a solid color image
            img = Image.new("RGB", (100, 100), color="red")
            faces = detector.detect_faces(img)
            assert isinstance(faces, list)

    def test_detect_largest_face_no_faces(self):
        """Test that None is returned when no faces detected."""
        with FaceDetector() as detector:
            img = Image.new("RGB", (100, 100), color="blue")
            result = detector.detect_largest_face(img)
            assert result is None
