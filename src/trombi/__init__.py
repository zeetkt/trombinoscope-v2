"""Trombinoscope package initialization."""

from src.trombi.face_detector import FaceDetection, FaceDetector
from src.trombi.image_processor import crop_face_square, process_images_parallel
from src.trombi.layout import Layout, compose_trombinoscope, calculate_a4_layout

__all__ = [
    "FaceDetection",
    "FaceDetector",
    "crop_face_square",
    "process_images_parallel",
    "Layout",
    "compose_trombinoscope",
    "calculate_a4_layout",
]

__version__ = "2.0.0"
