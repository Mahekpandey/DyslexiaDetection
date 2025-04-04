# Reading Assessment Module

## Overview
The Reading Assessment module is a comprehensive system for evaluating reading capabilities and potential dyslexia indicators through speech recognition and analysis. It provides real-time feedback on reading performance with features like word-by-word pronunciation assistance and speed control.

## Technical Architecture

### Frontend (React.js)
- **Core Libraries**:
  - `React`: UI component management and state handling
  - `@mui/material`: Material UI components for modern interface design
  - `@mui/icons-material`: Icon components for visual feedback
  - `Web Speech API`: Browser's built-in text-to-speech for pronunciation assistance

- **Key Components**:
  1. Reading Interface
     - Displays reading passages
     - Shows recording status with visual feedback
     - Real-time speech recognition status updates
  
  2. Results Display
     - Accuracy percentage
     - Words per minute calculation
     - Dyslexia prediction indicators
     - Word-by-word error analysis
     - Interactive pronunciation practice with speed control

### Backend (Python/Flask)
- **Core Libraries**:
  - `Flask`: Web server framework
  - `speech_recognition`: Audio capture and speech-to-text conversion
  - `pyttsx3`: Text-to-speech engine for server-side audio processing
  - `numpy`: Numerical computations for analysis
  - `scikit-learn`: ML model for dyslexia prediction

- **Key Components**:
  1. Speech Handler (`speech_handler.py`)
     - Manages audio recording
     - Handles speech recognition
     - Processes text analysis
     - Calculates reading metrics

  2. ML Model (`ml_model.py`)
     - Analyzes reading patterns
     - Predicts dyslexia indicators
     - Processes reading metrics

## Data Flow
1. **Assessment Initialization**
   ```
   Frontend → /api/reading/start → Backend generates passage → Frontend displays
   ```

2. **Recording Process**
   ```
   Start Recording → Backend initializes → Ambient noise adjustment → 
   Active listening → Speech processing → Text recognition
   ```

3. **Analysis Pipeline**
   ```
   Recognized Text → Text cleaning → Compare with original → 
   Calculate metrics → ML analysis → Results generation
   ```

## API Endpoints

### Reading Assessment
- `POST /api/reading/start`: Initiates assessment, returns reading passage
- `POST /api/reading/analyze`: Analyzes reading performance
- `POST /api/reading/save-result`: Stores assessment results

### Speech Processing
- `POST /api/speech/init`: Initializes recording session
- `POST /api/speech/record`: Handles speech recording
- `GET /api/speech/status`: Returns current recording state
- `POST /api/speech/transcribe`: Converts speech to text

## Metrics Calculation

### Accuracy
- Word-by-word comparison between original and spoken text
- Calculated as: (correct_words / total_words) × 100%

### Reading Speed
- Words per minute calculation based on recording duration
- Formula: (word_count / duration_in_seconds) × 60

### Error Analysis
- Types of errors tracked:
  - Mispronunciations
  - Omissions (missing words)
  - Substitutions
  - Hesitations

## ML Model Features
- Reading speed analysis
- Error pattern recognition
- Pronunciation consistency
- Word recognition accuracy
- Reading fluency assessment

## State Management
- Recording states:
  - `idle`: Initial/ready state
  - `ADJUSTING`: Calibrating for ambient noise
  - `LISTENING`: Active recording
  - `PROCESSING`: Speech recognition in progress

## Security and Performance
- Audio data processed in real-time
- No permanent storage of audio recordings
- Results anonymized and stored securely
- Optimized for low latency response

## Error Handling
- Ambient noise detection
- Network connectivity issues
- Speech recognition failures
- Invalid input protection

## Future Enhancements
- Multiple language support
- Custom passage creation
- Progress tracking over time
- Detailed error pattern analysis
- Enhanced ML model training

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