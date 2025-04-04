# OCR and Font Conversion Module

## Overview
The OCR (Optical Character Recognition) module is designed to convert physical book pages into dyslexia-friendly digital text. It captures images of book pages, extracts the text using OCR, and converts it into a dyslexic-friendly font format for easier reading.

## Technical Architecture

### Frontend (React.js)
- **Core Libraries**:
  - `React`: UI component management
  - `@mui/material`: Material UI components for interface design
  - `react-webcam`: Camera integration for page capture
  - `axios`: HTTP client for API communication
  - `react-to-print`: PDF generation and printing support

- **Key Components**:
  1. Image Capture Interface
     - Camera preview and capture
     - Image quality verification
     - Upload functionality for existing images
  
  2. Text Display
     - Converted text preview
     - Font customization options
     - Download and print capabilities

### Backend (Python/Flask)
- **Core Libraries**:
  - `Flask`: Web server framework
  - `pytesseract`: OCR engine for text extraction
  - `opencv-python`: Image processing and enhancement
  - `Pillow`: Image handling and manipulation
  - `pdf2image`: PDF to image conversion
  - `numpy`: Image array operations
  - `werkzeug`: File handling and security

- **Key Components**:
  1. Image Processing (`image_processor.py`)
     - Image preprocessing and enhancement
     - Noise reduction
     - Contrast adjustment
     - Rotation correction

  2. OCR Engine (`ocr_engine.py`)
     - Text extraction from images
     - Layout analysis
     - Character recognition
     - Text formatting preservation

  3. Font Converter (`font_converter.py`)
     - Text to dyslexic font conversion
     - Font styling and spacing
     - Page layout preservation

## Data Flow
1. **Image Upload Process**
   ```
   Frontend camera/upload → Image preprocessing → OCR processing → 
   Text extraction → Font conversion → Frontend display
   ```

2. **Text Processing Pipeline**
   ```
   Raw image → Enhancement → OCR → Text cleaning → 
   Font conversion → Format preservation → Final output
   ```

## API Endpoints

### OCR Processing
- `POST /api/ocr/upload`: Upload image for processing
- `POST /api/ocr/process`: Process uploaded image
- `GET /api/ocr/result`: Retrieve processed text
- `POST /api/ocr/convert`: Convert text to dyslexic font

### File Management
- `GET /api/ocr/files`: List processed files
- `DELETE /api/ocr/files/<id>`: Delete processed file
- `GET /api/ocr/download/<id>`: Download converted file

## Image Processing Features
- Automatic skew correction
- Noise reduction
- Contrast enhancement
- Resolution optimization
- Page boundary detection

## OCR Capabilities
- Multi-language text recognition
- Layout preservation
- Table and diagram detection
- Special character handling
- Font style recognition

## Font Conversion Features
- OpenDyslexic font integration
- Customizable font size
- Adjustable line spacing
- Character spacing optimization
- Paragraph formatting

## Setup

1. Create and activate virtual environment:
```bash
# Create virtual environment
python -m venv venv_ocr

# Activate virtual environment
# For Windows
.\venv_ocr\Scripts\activate
# For Linux/Mac
source venv_ocr/bin/activate
```

2. Install Tesseract OCR:
```bash
# Windows (using chocolatey)
choco install tesseract

# Linux
sudo apt-get install tesseract-ocr

# Mac
brew install tesseract
```

3. Set up environment variables:
Create a `.env` file in the root directory:
```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5002
TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe  # Windows
UPLOAD_FOLDER=static/uploads
OUTPUT_FOLDER=static/output
ALLOWED_EXTENSIONS=png,jpg,jpeg,pdf
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Create necessary directories:
```bash
mkdir static uploads output
mkdir static\uploads static\output  # Windows
# OR
mkdir -p static/uploads static/output  # Linux/Mac
```

6. Run the application:
```bash
python app.py
```

## Directory Structure
```
ocr_backend/
├── app.py                # Main application file
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
├── static/              # Static files
│   ├── uploads/         # Uploaded images
│   └── output/          # Processed files
├── modules/
│   ├── image_processor.py  # Image processing functions
│   ├── ocr_engine.py      # OCR functionality
│   └── font_converter.py  # Font conversion logic
└── README.md            # This file
```

## Performance Optimization
- Image caching for faster processing
- Batch processing capability
- Parallel processing for multiple pages
- Memory-efficient large file handling
- Response compression

## Error Handling
- Invalid image detection
- OCR confidence scoring
- Processing status tracking
- Error recovery mechanisms
- Input validation

## Security Features
- File type validation
- Size limit enforcement
- Secure file storage
- Access control
- Rate limiting

## Notes
- Supports multiple image formats (PNG, JPG, PDF)
- Processes multiple pages from PDF files
- Maintains original document formatting
- Provides progress tracking for long operations
- Includes error recovery mechanisms 