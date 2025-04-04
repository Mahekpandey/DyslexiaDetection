from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from services.ocr_service import OCRService
from services.text_transform_service import TextTransformService
from services.tts_service import TTSService
import logging
import time
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
MAX_AGE_HOURS = 24  # Files older than 24 hours will be deleted

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OCR service
ocr_service = OCRService()
text_transform_service = TextTransformService()
tts_service = TTSService()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """
    Remove files older than MAX_AGE_HOURS
    """
    try:
        current_time = time.time()
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.getmtime(filepath) < current_time - (MAX_AGE_HOURS * 3600):
                os.remove(filepath)
                logger.info(f"Cleaned up old file: {filename}")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def get_unique_filename(filename):
    """
    Generate a unique filename to prevent overwrites
    """
    name, ext = os.path.splitext(filename)
    timestamp = int(time.time())
    return f"{name}_{timestamp}{ext}"

@app.route('/api/ocr/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/ocr/upload', methods=['POST'])
def upload_file():
    try:
        # Clean up old files before processing new upload
        cleanup_old_files()

        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file part in the request'
            }), 400

        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No selected file'
            }), 400

        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # Generate unique filename and save the file
        filename = secure_filename(file.filename)
        unique_filename = get_unique_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            file.save(file_path)
            logger.info(f"File saved successfully: {unique_filename}")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to save file'
            }), 500

        # Process the image with OCR
        result = ocr_service.process_image(file_path)

        # Clean up the uploaded file
        try:
            os.remove(file_path)
            logger.info(f"Temporary file removed: {unique_filename}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {str(e)}")

        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500

        return jsonify({
            'success': True,
            'text': result['text'],
            'easyocr_text': result['easyocr_text'],
            'tesseract_text': result['tesseract_text']
        })

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing the file'
        }), 500

@app.route('/api/ocr/transform', methods=['POST'])
def transform_text():
    """Transform text into OpenDyslexic font image"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        text = data['text']
        font_size = data.get('font_size', 36)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'transformed_{timestamp}.png'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Transform text
        success, message = text_transform_service.transform_text(
            text=text,
            output_path=output_path,
            font_size=font_size
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 500
        
        return jsonify({
            'success': True,
            'message': message,
            'image_path': filename
        })
        
    except Exception as e:
        logger.error(f"Error in transform_text: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ocr/speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        text = data['text']
        engine = data.get('engine', 'pyttsx3')  # Default to pyttsx3
        
        # Generate speech
        success, message, audio_file = tts_service.text_to_speech(text, engine)
        
        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 500
        
        # Return the audio file
        return send_file(
            audio_file,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        )
        
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ocr/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up old files"""
    try:
        # Clean up OCR files
        cleanup_old_files()  # Using the global cleanup function
        
        # Clean up TTS cache
        tts_cleanup_success, tts_message = tts_service.cleanup_cache()
        
        return jsonify({
            'success': True,
            'message': 'Cleanup completed successfully',
            'tts_message': tts_message
        })
        
    except Exception as e:
        logger.error(f"Error in cleanup_files: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 