# Reading Assessment Feature

This module provides functionality for assessing reading speed and accuracy in children, with a focus on dyslexia detection.

## Features

- Text-to-speech synthesis for reading passages
- Real-time reading speed calculation
- Accuracy assessment
- Multiple difficulty levels
- Results tracking and analysis

## Setup

1. Create and activate virtual environment:
```bash
# Create virtual environment
python -m venv venv_reading

# Activate virtual environment
# For Windows
.\venv_reading\Scripts\activate
# For Linux/Mac
source venv_reading/bin/activate
```

2. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5001
AUDIO_STORAGE_PATH=static/audio
RESULTS_FILE_PATH=data/reading_test_results.json
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create necessary directories:
```bash
mkdir static data
mkdir static\audio  # On Windows
# OR
mkdir -p static/audio  # On Linux/Mac
```

5. Run the application:
```bash
python app.py
```

## API Endpoints

### 1. Start Reading Assessment
- **Endpoint**: `/api/reading/start`
- **Method**: POST
- **Body**: 
```json
{
    "difficulty": "easy|medium|hard"
}
```

### 2. Analyze Reading
- **Endpoint**: `/api/reading/analyze`
- **Method**: POST
- **Body**:
```json
{
    "user_reading": "text read by user",
    "original_text": "original passage",
    "reading_time": 60  // in seconds
}
```

### 3. Save Results
- **Endpoint**: `/api/reading/save-result`
- **Method**: POST
- **Body**:
```json
{
    "accuracy": 85.5,
    "words_per_minute": 120,
    "difficulty": "medium",
    "total_words": 20,
    "correct_words": 17
}
```

## Integration with Main Application

This feature is designed to be integrated with the main dyslexia detection application. It runs on port 5001 (configurable via .env) and can be accessed through the main application's frontend.

## Directory Structure

```
reading_assessment/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── static/            # Static files
│   └── audio/         # Generated audio files
├── data/              # Data storage
│   └── reading_test_results.json
└── README.md          # This file
```

## Notes

- The feature uses Google Text-to-Speech (gTTS) for generating audio
- Results are stored in JSON format for easy analysis
- The system supports multiple difficulty levels for progressive assessment
- All paths and ports are configurable via environment variables 