"""Configuration settings for the trombinoscope application."""

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Face detection settings
    face_detection_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for face detection",
    )
    face_detection_model: str = Field(
        default="short_range",
        description="MediaPipe face detection model selection",
    )

    # Image processing settings
    default_output_size: int = Field(
        default=520,
        ge=128,
        le=2048,
        description="Default output size for cropped faces in pixels",
    )
    default_margin: float = Field(
        default=0.75,
        ge=0.0,
        le=2.0,
        description="Default margin around detected faces (ratio)",
    )
    default_upward_bias: float = Field(
        default=0.10,
        ge=0.0,
        le=0.5,
        description="Default upward bias for face centering (ratio)",
    )

    # Grid layout settings
    default_columns: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Default number of columns in the grid",
    )
    default_padding: int = Field(
        default=40,
        ge=10,
        le=100,
        description="Default padding between grid cells in pixels",
    )
    default_label_height: int = Field(
        default=80,
        ge=40,
        le=150,
        description="Default height reserved for labels in pixels",
    )
    default_font_size: int = Field(
        default=46,
        ge=20,
        le=80,
        description="Default font size for labels",
    )

    # Color settings
    default_background_color: str = Field(
        default="#ffffff",
        description="Default background color for the canvas",
    )

    # Font settings
    font_candidates: List[str] = Field(
        default=[
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
            "/usr/share/fonts/opentype/noto/NotoSans-Bold.otf",
            "/usr/share/fonts/opentype/noto/NotoSans-Regular.otf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttc",
            "arial.ttf",
            "DejaVuSans-Bold.ttf",
            "DejaVuSans.ttf",
        ],
        description="List of font paths to try when loading fonts",
    )

    # Processing settings
    max_workers: int = Field(
        default=4,
        ge=1,
        le=16,
        description="Maximum number of parallel workers for image processing",
    )
    max_file_size_mb: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum file size in MB for uploaded images",
    )


# Global settings instance
settings = Settings()
