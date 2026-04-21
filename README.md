# Trombinoscope Generator v2

A modern, high-performance trombinoscope (photo grid) generator with advanced face detection.

## Features

- **Modern Face Detection**: Uses MediaPipe instead of Haar Cascades for better accuracy
- **Parallel Processing**: Multi-threaded image processing for faster batch operations
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Configuration Management**: Environment-based configuration with Pydantic Settings
- **Type Safety**: Full type hints throughout the codebase
- **Comprehensive Testing**: Unit tests with pytest
- **Docker Support**: Multi-stage builds for optimized container images
- **Security**: Non-root user in Docker containers

## Architecture

```
trombinoscope-v2/
├── config/
│   └── settings.py          # Configuration management
├── src/
│   └── trombi/
│       ├── __init__.py      # Package initialization
│       ├── app.py           # Streamlit application
│       ├── face_detector.py # MediaPipe face detection
│       ├── image_processor.py # Image cropping & processing
│       ├── layout.py        # Grid composition
│       └── utils.py         # Utility functions
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── test_face_detector.py
│   ├── test_image_processor.py
│   └── test_layout.py
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Docker Compose configuration
├── pyproject.toml           # Project metadata & tool config
├── requirements.txt         # Python dependencies
└── README.md

```

## Quick Start

### Local Installation

```bash
# Clone or navigate to the project
cd trombinoscope-v2

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run src/trombi/app.py
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t trombinoscope:v2 .
docker run -p 8501:8501 trombinoscope:v2
```

## Configuration

Configuration is managed through environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `FACE_DETECTION_CONFIDENCE` | 0.5 | Minimum confidence for face detection |
| `FACE_DETECTION_MODEL` | short_range | Model selection (short_range/full_range) |
| `DEFAULT_OUTPUT_SIZE` | 520 | Default thumbnail size in pixels |
| `DEFAULT_MARGIN` | 0.75 | Margin ratio around detected faces |
| `DEFAULT_UPWARD_BIAS` | 0.10 | Upward bias for face centering |
| `DEFAULT_COLUMNS` | 4 | Default number of columns |
| `DEFAULT_PADDING` | 40 | Default padding between cells |
| `MAX_WORKERS` | 4 | Maximum parallel workers |
| `MAX_FILE_SIZE_MB` | 50 | Maximum upload file size |

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black src tests

# Lint
ruff check src tests

# Type check
mypy src
```

## Key Improvements Over v1

1. **Face Detection**: MediaPipe provides more accurate and reliable face detection than Haar Cascades
2. **Performance**: Parallel processing with ThreadPoolExecutor for batch operations
3. **Type Safety**: Full type annotations with mypy checking
4. **Configuration**: Centralized configuration with validation
5. **Testing**: Comprehensive unit test suite
6. **Docker**: Multi-stage builds for smaller images
7. **Security**: Non-root user in containers
8. **Error Handling**: Better exception handling throughout

## License

MIT
