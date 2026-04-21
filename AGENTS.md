# AGENTS.md - Developer Guidelines for Trombinoscope v2

## Project Overview

Upgraded Python/Streamlit application for generating trombinoscopes with MediaPipe face detection.

## Architecture

- `config/settings.py` - Pydantic-based configuration
- `src/trombi/face_detector.py` - MediaPipe face detection
- `src/trombi/image_processor.py` - Image processing with parallel execution
- `src/trombi/layout.py` - Grid composition
- `src/trombi/app.py` - Streamlit UI

## Commands

```bash
# Run app
streamlit run src/trombi/app.py

# Run tests
pytest

# Code quality
black src tests
ruff check src tests
mypy src

# Docker
docker-compose up --build
```

## Code Style

- Type hints for all functions
- Google-style docstrings
- Explicit returns
- Context managers for resources

### Imports Order

```python
import logging
from typing import List, Optional

import mediapipe as mp
from PIL import Image

from config.settings import settings
```

## Dependencies

Core: streamlit, mediapipe, pillow, numpy, pydantic
Dev: pytest, black, ruff, mypy
