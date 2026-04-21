"""Modern face detection using OpenCV DNN."""

import logging
from dataclasses import dataclass
from typing import List, Optional

import cv2
import numpy as np
from PIL import Image

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class FaceDetection:
    """Represents a detected face with bounding box and confidence."""

    x: int
    y: int
    width: int
    height: int
    confidence: float


class FaceDetector:
    """OpenCV DNN-based face detector."""

    def __init__(
        self,
        min_detection_confidence: float = settings.face_detection_confidence,
        model_selection: int = 0,
    ) -> None:
        """Initialize the face detector."""
        self.min_detection_confidence = min_detection_confidence
        self.model_selection = model_selection
        self._detector: Optional[cv2.dnn.Net] = None
        self._initialize_detector()

    def _initialize_detector(self) -> None:
        """Initialize the OpenCV DNN face detector."""
        if self._detector is None:
            try:
                # Use OpenCV's DNN face detector with pre-trained model
                model_file = (
                    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                )
                self._detector = cv2.CascadeClassifier(model_file)
                if self._detector.empty():
                    raise RuntimeError("Failed to load cascade classifier")
                logger.info("Initialized face detector (Haar Cascade)")
            except Exception as e:
                logger.error(f"Failed to initialize face detector: {e}")
                raise RuntimeError(f"Face detector initialization failed: {e}") from e

    def detect_faces(self, image: Image.Image) -> List[FaceDetection]:
        """Detect all faces in an image."""
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Convert PIL to numpy array (RGB to BGR for OpenCV)
        np_image = np.array(image)
        gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)

        # Detect faces with multiple scales
        faces = self._detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(70, 70),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        # If no faces found, try with more lenient parameters
        if len(faces) == 0:
            faces = self._detector.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(60, 60),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )

        detections = []
        for x, y, w, h in faces:
            # Haar cascades don't give confidence, use a default
            confidence = 0.8
            detections.append(
                FaceDetection(
                    x=int(x),
                    y=int(y),
                    width=int(w),
                    height=int(h),
                    confidence=confidence,
                )
            )

        # Sort by area (largest first) - proxy for confidence
        detections.sort(key=lambda d: d.width * d.height, reverse=True)
        return detections

    def detect_largest_face(self, image: Image.Image) -> Optional[FaceDetection]:
        """Detect the largest face in an image."""
        faces = self.detect_faces(image)
        if not faces:
            return None
        return max(faces, key=lambda f: f.width * f.height)

    def close(self) -> None:
        """Release detector resources."""
        self._detector = None
        logger.info("Face detector resources released")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
