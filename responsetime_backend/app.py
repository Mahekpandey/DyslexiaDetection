from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from utils.response_calculator import ResponseTimeCalculator

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# Initialize response time calculator
response_calculator = ResponseTimeCalculator()

@app.route('/api/whackamole/start', methods=['POST'])
def start_game():
    # Clear any previous attempts
    response_calculator.clear_attempts()
    return jsonify({
        'status': 'success',
        'message': 'Game started',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/whackamole/record-attempt', methods=['POST'])
def record_attempt():
    try:
        # Start timing for new attempt
        response_calculator.start_attempt()
        
        # Wait for the hit (this would be handled by the frontend)
        # For testing, we'll just return a success message
        return jsonify({
            'status': 'success',
            'message': 'Attempt started',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/whackamole/end-attempt', methods=['POST'])
def end_attempt():
    try:
        response_time = response_calculator.end_attempt()
        return jsonify({
            'status': 'success',
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/whackamole/results', methods=['GET'])
def get_results():
    try:
        attempts = response_calculator.get_attempts()
        if not attempts:
            return jsonify({
                'status': 'error',
                'message': 'No attempts recorded'
            }), 404

        response_times = [attempt['response_time'] for attempt in attempts]
        result = response_calculator.calculate_score(response_times)

        # Convert milliseconds to seconds for display
        attempts_data = [
            {
                'response_time': rt / 1000,  # Convert ms to seconds
                'score': score
            } for rt, score in zip(result['response_times'], result['individual_scores'])
        ]

        # Analysis based on score
        score = result['score']
        avg_time_seconds = result['average_time'] / 1000  # Convert ms to seconds
        
        if score >= 90:
            analysis = {
                'message': "🌟 AMAZING REFLEXES! You're a Whack-A-Mole Champion! 🏆",
                'detail': "Your lightning-fast reactions are incredible! You have the reflexes of a superhero!",
                'motivation': "Keep up the fantastic work - you're absolutely crushing it! 🚀"
            }
        elif score >= 75:
            analysis = {
                'message': "⭐ GREAT JOB! You're Getting Really Good! 🎯",
                'detail': "Your response times are above average - that's awesome!",
                'motivation': "You're so close to becoming a champion! A little more practice and you'll be unstoppable! 💪"
            }
        elif score >= 60:
            analysis = {
                'message': "🌈 Good Effort! You're Making Progress! 🎮",
                'detail': "Your response times are getting better with each try.",
                'motivation': "Keep practicing and you'll be a Whack-A-Mole master in no time! You can do it! 🌟"
            }
        else:
            analysis = {
                'message': "🌱 You're Learning and Growing! 🎯",
                'detail': "Everyone starts somewhere - and you're on your way up!",
                'motivation': "With a bit more practice, you'll be catching those moles faster than ever! Let's try again! 🎮"
            }

        return jsonify({
            'status': 'success',
            'attempts': attempts_data,
            'average_response_time': avg_time_seconds,
            'score': result['score'],
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/whackamole/calculate-score', methods=['POST'])
def calculate_score():
    try:
        # Get all recorded response times
        attempts = response_calculator.get_attempts()
        response_times = [attempt['response_time'] for attempt in attempts]
        
        if len(response_times) != 3:
            return jsonify({
                'status': 'error',
                'message': f'Need exactly 3 attempts, got {len(response_times)}'
            }), 400
        
        # Calculate final score
        result = response_calculator.calculate_score(response_times)
        
        return jsonify({
            'status': 'success',
            'average_response_time': result['average_time'],
            'score': result['score'],
            'individual_scores': result['individual_scores'],
            'response_times': result['response_times'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000) 