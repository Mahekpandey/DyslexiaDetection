# DyslexiaDetection - Comprehensive Reading Assessment Platform

![Training History](./assets/training_history.png)

## Overview
DyslexiaDetection is an integrated platform designed to assist in the early detection and support of dyslexia through multiple assessment methods. The platform combines reading assessment, OCR-based text conversion, and handwriting analysis to provide a comprehensive evaluation system.

## Features

### 1. Reading Assessment Module
- Real-time speech recognition for reading evaluation
- Word-by-word accuracy tracking
- Reading speed calculation (WPM)
- Dyslexia prediction based on reading patterns
- Interactive pronunciation assistance
- Progress tracking across multiple attempts

### 2. OCR and Font Conversion
- Book page to dyslexia-friendly text conversion
- Support for multiple image formats (PNG, JPG, PDF)
- OpenDyslexic font integration
- Customizable text formatting
- Batch processing capability

### 3. Handwriting Analysis
- Real-time handwriting capture
- Pattern recognition for dyslexia indicators
- Detailed stroke analysis
- Pressure and spacing evaluation
- Historical data comparison

## Technical Architecture

### Frontend (React.js)
- **Core Technologies**:
  - React 18.x
  - Material-UI v5
  - Web Speech API
  - Canvas API
  - Axios for API communication

### Backend (Python)
- **Core Technologies**:
  - Flask for web services
  - TensorFlow/PyTorch for ML models
  - OpenCV for image processing
  - Tesseract for OCR
  - NumPy/Pandas for data processing

### Machine Learning Models
- **Reading Assessment Model**:
  - Features: Reading speed, accuracy, error patterns
  - Architecture: LSTM + Attention mechanism
  - Training Data: [Dataset details and size]
  - Accuracy: [Model performance metrics]

- **Handwriting Analysis Model**:
  - Features: Stroke patterns, pressure points, spacing
  - Architecture: CNN + RNN hybrid
  - Training Data: [Dataset details and size]
  - Accuracy: [Model performance metrics]

## Data Flow

### Reading Assessment Flow
```
User Reading → Speech Recognition → Text Analysis → 
Feature Extraction → ML Prediction → Results Display
```

### OCR Processing Flow
```
Image Upload → Preprocessing → OCR → Text Extraction → 
Font Conversion → Format Optimization → Display
```

### Handwriting Analysis Flow
```
Writing Input → Stroke Capture → Feature Extraction → 
Pattern Analysis → ML Processing → Results Generation
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- MongoDB 4.4+
- Tesseract OCR
- CUDA-capable GPU (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DyslexiaDetection.git
cd DyslexiaDetection
```

2. Set up virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

3. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Install OCR backend dependencies:
```bash
cd ../ocr_backend
pip install -r requirements.txt
```

5. Install frontend dependencies:
```bash
cd ../dyslexia-detection-frontend
npm install
```

6. Configure environment variables:
Create `.env` files in each directory (backend, ocr_backend, frontend) using the provided templates.

### Running the Application

1. Start the main backend:
```bash
cd backend
python app.py
```

2. Start the OCR backend:
```bash
cd ocr_backend
python app.py
```

3. Start the frontend:
```bash
cd dyslexia-detection-frontend
npm start
```

## Project Structure
```
DyslexiaDetection/
├── backend/                 # Main backend service
│   ├── models/             # ML models
│   ├── services/           # Business logic
│   └── api/                # API endpoints
├── ocr_backend/            # OCR service
│   ├── modules/            # OCR processing modules
│   └── static/             # Processed files
├── dyslexia-detection-frontend/  # React frontend
│   ├── src/               
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Main pages
│   │   └── services/      # API services
│   └── public/            # Static assets
└── datasets/              # Training datasets
    ├── reading/           # Reading assessment data
    └── handwriting/       # Handwriting samples
```

## Datasets
- **Reading Assessment Dataset**:
  - Size: [Number] samples
  - Source: [Source information]
  - Features: Reading speed, accuracy, error patterns
  - Format: JSON/CSV

- **Handwriting Dataset**:
  - Size: [Number] samples
  - Source: [Source information]
  - Features: Stroke data, pressure points
  - Format: Image/Vector data

## Model Training

### Reading Assessment Model
- Training script: `backend/models/train_reading_model.py`
- Configuration: `backend/config/model_config.json`
- Training history: See `assets/training_history.png`
- Validation accuracy: [Percentage]

### Handwriting Analysis Model
- Training script: `backend/models/train_handwriting_model.py`
- Configuration: `backend/config/handwriting_config.json`
- Training history: See `assets/handwriting_training.png`
- Validation accuracy: [Percentage]

## API Documentation

### Main Backend APIs
- `/api/reading/*`: Reading assessment endpoints
- `/api/handwriting/*`: Handwriting analysis endpoints
- `/api/users/*`: User management endpoints

### OCR Backend APIs
- `/api/ocr/*`: OCR processing endpoints
- `/api/font/*`: Font conversion endpoints

Detailed API documentation available in each module's README.

## Performance Optimization
- GPU acceleration for ML models
- Image processing optimization
- Response caching
- Lazy loading of components
- Efficient state management

## Security Features
- JWT authentication
- Input validation
- File type verification
- Rate limiting
- Secure data storage

## Future Enhancements
- Multi-language support
- Mobile application
- Real-time collaboration
- Advanced analytics dashboard
- Integration with educational platforms

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments
- [List of contributors]
- [Used datasets]
- [Research papers referenced]
- [Open source libraries used] 