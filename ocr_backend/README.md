# OCR Backend Service

This is a separate backend service for the OCR (Optical Character Recognition) and Text-to-Speech features of the Dyslexia Detection project.

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR:
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

4. Run the service:
```bash
python app.py
```

The service will run on port 5001 (separate from the main backend).

## API Endpoints

- `GET /api/ocr/health`: Health check endpoint
- `POST /api/ocr/upload`: Upload image for OCR processing
- `POST /api/ocr/transform`: Transform text to OpenDyslexic font
- `POST /api/ocr/speech`: Generate speech from text

## Directory Structure

```
ocr_backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── services/          # Service modules
│   ├── ocr_service.py    # OCR processing
│   └── tts_service.py    # Text-to-speech
└── uploads/           # Temporary file storage
```

## Note
This is a separate service from the main Dyslexia Detection backend and runs on a different port to avoid conflicts. 