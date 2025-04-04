from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pyttsx3
from gtts import gTTS
import os
import json
import random
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from ml_model import DyslexiaPredictor, DyslexiaModel
from speech_handler import SpeechHandler
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes and allow file upload
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"]
    }
})

# Initialize components
engine = pyttsx3.init()
predictor = DyslexiaPredictor()
speech_handler = SpeechHandler()
dyslexia_model = DyslexiaModel()

# Get environment variables
AUDIO_STORAGE_PATH = os.getenv('AUDIO_STORAGE_PATH', 'static/audio')
RESULTS_FILE_PATH = os.getenv('RESULTS_FILE_PATH', 'data/reading_test_results.json')
PORT = int(os.getenv('PORT', 5001))

# Global state for recording process
recording_state = {
    'status': 'idle',
    'timestamp': None,
    'last_state_change': 0,
    'recognized_text': None
}

# State transition delays (in seconds)
STATE_DELAYS = {
    'ADJUSTING': 2,      # Show adjusting message for 2 seconds
    'LISTENING': 5,      # Minimum listening time
    'PROCESSING': 2      # Show processing for at least 2 seconds
}

def update_state(new_state, text=None):
    """Update the recording state with proper timing"""
    global recording_state
    current_time = time.time()
    
    # Only update if enough time has passed in current state
    if current_time - recording_state['last_state_change'] >= STATE_DELAYS.get(recording_state['status'], 0):
        recording_state['status'] = new_state
        recording_state['last_state_change'] = current_time
        if text is not None:
            recording_state['recognized_text'] = text
        print(f"State changed to: {new_state}")  # Debug log
        if new_state == 'ADJUSTING':
            print("Adjusting for ambient noise...")
        elif new_state == 'LISTENING':
            print("Listening...")
        elif new_state == 'PROCESSING':
            print("Recognition in progress...")

# Ensure directories exist
os.makedirs(AUDIO_STORAGE_PATH, exist_ok=True)
os.makedirs(os.path.dirname(RESULTS_FILE_PATH), exist_ok=True)

# Sample reading passages
READING_PASSAGES = [
    "The quick brown fox jumps over the lazy dog.",
    "Sally sells seashells by the seashore.",
    "Peter Piper picked a peck of pickled peppers.",
    "How much wood would a woodchuck chuck if a woodchuck could chuck wood?"
]

@app.route('/api/reading/start', methods=['POST'])
def get_reading_passage():
    """Get a random reading passage"""
    try:
        passage = random.choice(READING_PASSAGES)
        print(f"Sending passage: {passage}")  # Debug log
        return jsonify({
            'success': True,
            'passage': passage
        })
    except Exception as e:
        print(f"Error in get_reading_passage: {str(e)}")  # Debug log
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/speech/init', methods=['POST'])
def init_recording():
    """Initialize recording"""
    try:
        update_state('ADJUSTING')
        return jsonify({
            'success': True,
            'status': recording_state['status']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/speech/status', methods=['GET'])
def get_recording_status():
    """Get the current recording status"""
    # Check if we should transition to next state
    current_time = time.time()
    if recording_state['status'] != 'idle':
        time_in_state = current_time - recording_state['last_state_change']
        
        if recording_state['status'] == 'ADJUSTING' and time_in_state >= STATE_DELAYS['ADJUSTING']:
            update_state('LISTENING')
    
    return jsonify({
        'success': True,
        'status': recording_state['status'],
        'recognized_text': recording_state['recognized_text']
    })

@app.route('/api/speech/record', methods=['POST'])
def record_speech():
    """Record and recognize speech"""
    try:
        data = request.get_json()
        duration = data.get('duration', None)
        
        # Get the recognized text
        recognized_text = speech_handler.listen_and_recognize(duration)
        
        # Update state to processing
        update_state('PROCESSING')
        time.sleep(STATE_DELAYS['PROCESSING'])  # Ensure minimum processing time
        
        if not recognized_text:
            print("Could not understand the audio. Please speak clearly.")
            update_state('idle', text="Could not understand the audio. Please speak clearly.")
            return jsonify({
                'success': False,
                'error': 'No speech recognized'
            }), 400
        
        print(f"Recognized text: {recognized_text}")
        update_state('idle', text=recognized_text)
        
        return jsonify({
            'success': True,
            'recognized_text': recognized_text
        })
    except Exception as e:
        print(f"Error in record_speech: {str(e)}")
        update_state('idle')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/speech/analyze', methods=['POST'])
def analyze_speech():
    """Analyze the reading by comparing original text with recognized text"""
    try:
        data = request.get_json()
        original_text = data.get('original_text', '')
        recognized_text = data.get('recognized_text', '')
        
        # Ensure we have both texts
        if not original_text or not recognized_text:
            return jsonify({
                'success': False,
                'error': 'Missing original_text or recognized_text'
            }), 400
            
        analysis = speech_handler.analyze_reading(original_text, recognized_text)
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        print(f"Error in analyze_speech: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reading/analyze', methods=['POST'])
def analyze_reading():
    """Analyze the reading by comparing original text with recognized text"""
    try:
        data = request.get_json()
        original_text = data.get('original_text', '')
        recognized_text = data.get('recognized_text', '')
        
        # Ensure we have both texts
        if not original_text or not recognized_text:
            return jsonify({
                'success': False,
                'error': 'Missing original_text or recognized_text'
            }), 400
            
        # Analyze the reading using speech handler
        analysis = speech_handler.analyze_reading(original_text, recognized_text)
        
        # Prepare data for ML prediction
        reading_data = {
            'accuracy': analysis['accuracy'],
            'words_per_minute': analysis['words_per_minute'],
            'total_words': analysis['total_words'],
            'correct_words': analysis['correct_words'],
            'error_count': len(analysis['errors'])
        }
        
        # Get dyslexia prediction
        prediction = predictor.predict(reading_data)
        
        # Combine analysis and prediction
        result = {
            **analysis,
            'dyslexia_prediction': prediction['prediction'],
            'dyslexia_probability': prediction['probability']
        }
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    except Exception as e:
        print(f"Error in analyze_reading: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reading/save-result', methods=['POST'])
def save_reading_result():
    """Save the reading assessment results"""
    data = request.json
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save results to a JSON file
    result = {
        "timestamp": timestamp,
        "accuracy": data.get('accuracy'),
        "words_per_minute": data.get('words_per_minute'),
        "difficulty": data.get('difficulty'),
        "total_words": data.get('total_words'),
        "correct_words": data.get('correct_words'),
        "dyslexia_prediction": data.get('dyslexia_prediction'),
        "dyslexia_probability": data.get('dyslexia_probability')
    }
    
    os.makedirs(os.path.dirname(RESULTS_FILE_PATH), exist_ok=True)
    
    try:
        with open(RESULTS_FILE_PATH, 'r') as f:
            results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        results = []
    
    results.append(result)
    
    with open(RESULTS_FILE_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    
    return jsonify({"status": "success", "message": "Results saved successfully"})

@app.route('/api/model/train', methods=['POST'])
def train_model():
    """Train the dyslexia prediction model with historical data"""
    try:
        # Load historical data
        with open(RESULTS_FILE_PATH, 'r') as f:
            results = json.load(f)
        
        if not results:
            return jsonify({
                "status": "error",
                "message": "No historical data available for training"
            }), 400
        
        # Prepare features and labels
        X = predictor.prepare_features(results)
        y = np.array([1 if r.get('dyslexia_prediction', False) else 0 for r in results])
        
        # Train the model
        train_score, test_score = predictor.train(X, y)
        
        return jsonify({
            "status": "success",
            "message": "Model trained successfully",
            "training_accuracy": round(train_score * 100, 2),
            "testing_accuracy": round(test_score * 100, 2)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True) 