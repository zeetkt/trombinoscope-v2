# AGENTS.md - Developer Guidelines for Trombinoscope v2

## Project Overview

Upgraded Python/Streamlit application for generating trombinoscopes with OpenCV face detection.

## Architecture

- `config/settings.py` - Pydantic-based configuration
- `config/__init__.py` - Makes config a Python package
- `src/trombi/face_detector.py` - OpenCV Haar Cascade face detection
- `src/trombi/image_processor.py` - Image processing with parallel execution
- `src/trombi/layout.py` - Grid composition
- `src/trombi/app.py` - Streamlit UI
- `src/trombi/utils.py` - Utility functions
- `src/trombi/shapes.py` - Shape masks (circle, rounded, hexagon)
- `src/trombi/effects.py` - Visual effects (drop shadows)
- `src/trombi/pdf_generator.py` - PDF export (A4 300 DPI)
- `src/trombi/reorder.py` - Drag-and-drop reordering helpers

## Commands

### Local Development

```bash
# Run app
streamlit run src/trombi/app.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Code quality
black src tests
ruff check src tests
mypy src
```

### Docker

```bash
# Build and run
docker-compose up --build

# Force rebuild (after code changes)
docker-compose up --build --force-recreate

# Stop containers
docker-compose down

# Build manually
docker build --no-cache -t trombinoscope:v2 .
docker run -p 8501:8501 trombinoscope:v2
```

## Docker Notes

### Key Docker Fixes Applied

1. **PYTHONPATH** - Set to `/app` for config module imports
2. **Non-root user** - `appuser` for security
3. **Dependencies** - Added `libglib2.0-0` for OpenCV
4. **Permissions** - Created `/home/appuser/.streamlit` and `/app/output` with correct ownership
5. **File output** - Uses `io.BytesIO` instead of file system writes (no permission issues)

### Docker Architecture

- **Multi-stage build** - Builder stage compiles deps, production stage is smaller
- **Health check** - Checks if Streamlit is responding
- **Fonts** - Includes DejaVu and Liberation fonts for image rendering

## Code Style

- Type hints for all functions
- Google-style docstrings
- Explicit returns
- Context managers for resources

### Imports Order

```python
import logging
from typing import List, Optional

import cv2
from PIL import Image

from config.settings import settings
```

## Dependencies

Core: streamlit, opencv-python-headless, pillow, numpy, pydantic, pydantic-settings, fpdf2, streamlit-sortables
Dev: pytest, pytest-cov, black, ruff, mypy

## Features

- **Face Detection**: OpenCV Haar Cascade for detecting faces in photos
- **Shape Masks**: Circle, rounded rectangle, and hexagon photo shapes
- **Drop Shadows**: Subtle shadow effects for photo depth (enabled by default)
- **PDF Export**: A4 landscape format at 300 DPI for print quality
- **Drag-and-Drop**: Reorder photos using streamlit-sortables
- **Progress Bar**: Real-time progress during image processing
- **A4 Layout**: Automatic optimal layout calculation for A4 pages
- **Parallel Processing**: Multi-threaded image processing for speed

## GitHub Repository

https://github.com/zeetkt/trombinoscope-v2
