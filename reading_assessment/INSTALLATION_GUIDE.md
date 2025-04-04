# Installation Guide for Dyslexia Assessment System

## Prerequisites
1. Python 3.8 or higher
2. Node.js 14.x or higher
3. PostgreSQL 12.x or higher
4. Git
5. Virtual Environment (recommended)

## Step 1: Environment Setup

### 1.1 Create and Activate Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Windows
venv\Scripts\activate
# For Linux/Mac
source venv/bin/activate
```

### 1.2 Install Python Dependencies
```bash
# Install required Python packages
pip install django==4.2.0
pip install djangorestframework==3.14.0
pip install psycopg2-binary==2.9.6
pip install tensorflow==2.12.0
pip install numpy==1.24.3
pip install pandas==2.0.2
pip install scikit-learn==1.2.2
pip install python-dotenv==1.0.0
```

## Step 2: Speech Recognition Setup

### 2.1 Install DeepSpeech
```bash
# Clone DeepSpeech repository
git clone https://github.com/mozilla/DeepSpeech.git
cd DeepSpeech

# Install DeepSpeech
pip install deepspeech

# Download pre-trained model
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer
```

### 2.2 Install Audio Dependencies
```bash
# For Windows
pip install pyaudio
# For Linux
sudo apt-get install python3-pyaudio
# For Mac
brew install portaudio
pip install pyaudio
```

## Step 3: Text-to-Speech Setup

### 3.1 Install MARY TTS
```bash
# Clone MARY TTS repository
git clone https://github.com/marytts/marytts.git
cd marytts

# Build MARY TTS
./gradlew build

# Start MARY TTS server
./gradlew run
```

### 3.2 Install Additional TTS Dependencies
```bash
pip install pyttsx3==2.90
pip install gTTS==2.3.2
```

## Step 4: Frontend Setup

### 4.1 Install Node.js Dependencies
```bash
# Create React app
npx create-react-app frontend
cd frontend

# Install required packages
npm install @material-ui/core @material-ui/icons
npm install axios
npm install react-router-dom
npm install @testing-library/react @testing-library/jest-dom
```

## Step 5: Database Setup

### 5.1 PostgreSQL Configuration
```bash
# Create database
createdb dyslexia_assessment

# Create user and grant privileges
psql -U postgres
CREATE USER dyslexia_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE dyslexia_assessment TO dyslexia_user;
```

### 5.2 Django Database Configuration
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate
```

## Step 6: Environment Variables Setup

Create a `.env` file in the root directory:
```env
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://dyslexia_user:your_password@localhost:5432/dyslexia_assessment
DEEPSPEECH_MODEL_PATH=path/to/deepspeech-0.9.3-models.pbmm
DEEPSPEECH_SCORER_PATH=path/to/deepspeech-0.9.3-models.scorer
MARY_TTS_SERVER_URL=http://localhost:59125
```

## Step 7: Verify Installation

### 7.1 Test Speech Recognition
```python
import deepspeech
import wave
import numpy as np

# Load model
model = deepspeech.Model('deepspeech-0.9.3-models.pbmm', 'deepspeech-0.9.3-models.scorer')
```

### 7.2 Test Text-to-Speech
```python
import pyttsx3

engine = pyttsx3.init()
engine.say("Test speech synthesis")
engine.runAndWait()
```

### 7.3 Test Database Connection
```python
python manage.py check
```

## Common Issues and Solutions

1. **DeepSpeech Installation Issues**
   - Solution: Ensure you have the correct Python version and all system dependencies installed
   - For Windows: Install Visual C++ Build Tools
   - For Linux: Install build-essential and python3-dev

2. **PyAudio Installation Issues**
   - Windows: Download and install PyAudio wheel file
   - Linux: Install portaudio19-dev
   - Mac: Install portaudio via Homebrew

3. **Database Connection Issues**
   - Check PostgreSQL service is running
   - Verify database credentials in .env file
   - Ensure database user has proper permissions

4. **MARY TTS Server Issues**
   - Check if port 59125 is available
   - Verify Java installation
   - Check server logs for specific errors

## Next Steps
After completing the installation:
1. Start the development server
2. Run the frontend development server
3. Test the complete system
4. Begin development following the development process document 