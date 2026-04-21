trombinoscope-v2/
├── config/
│   └── settings.py          # Pydantic-based configuration
├── src/
│   └── trombi/
│       ├── __init__.py      # Package initialization
│       ├── app.py           # Streamlit application
│       ├── face_detector.py # MediaPipe face detection
│       ├── image_processor.py # Image processing & parallel execution
│       ├── layout.py        # Grid composition
│       └── utils.py         # Utility functions
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── test_face_detector.py
│   ├── test_image_processor.py
│   └── test_layout.py
├── .dockerignore            # Docker ignore rules
├── .env.example             # Example environment configuration
├── .gitignore               # Git ignore rules
├── AGENTS.md                # Developer guidelines
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Docker Compose configuration
├── pyproject.toml           # Project metadata & tool config
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
