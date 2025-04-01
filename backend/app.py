from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import logging
import os
import sys
import cv2
import numpy as np
import base64
import asyncio
import websockets
import json
import threading
from werkzeug.serving import is_running_from_reloader

# Add parent directory to path to find eye_tracking package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eye_tracking.reading_analyzer import ReadingAnalyzer

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store active sessions
active_sessions = {}

# Track WebSocket connections per session
websocket_connections = {}

@app.route('/')
def index():
    return send_from_directory('static', 'test.html')

@app.route('/test')
def test_page():
    return send_from_directory('static', 'test.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/start-session', methods=['POST'])
def start_session():
    session_id = str(len(active_sessions) + 1)
    active_sessions[session_id] = {
        "status": "active",
        "analyzer": ReadingAnalyzer(),
        "metrics": {
            "reading_speed": 0,
            "fixations": 0,
            "regressions": 0,
            "dyslexia_probability": 0
        }
    }
    return jsonify({"session_id": session_id})

@app.route('/api/end-session/<session_id>', methods=['POST'])
def end_session(session_id):
    if session_id in active_sessions:
        # Clean up resources
        if 'analyzer' in active_sessions[session_id]:
            active_sessions[session_id]['analyzer'].release()
        active_sessions[session_id]["status"] = "completed"
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Session not found"}), 404

@app.route('/api/sessions')
def get_sessions():
    # Return only the metrics, not the analyzer objects
    session_data = {
        sid: {k: v for k, v in data.items() if k != 'analyzer'}
        for sid, data in active_sessions.items()
    }
    return jsonify(session_data)

@app.route('/api/sessions/<session_id>')
def get_session(session_id):
    if session_id in active_sessions:
        # Return only the metrics, not the analyzer object
        session_data = {k: v for k, v in active_sessions[session_id].items() if k != 'analyzer'}
        return jsonify(session_data)
    return jsonify({"status": "error", "message": "Session not found"}), 404

@app.route('/api/calibrate/<session_id>', methods=['POST'])
def calibrate(session_id):
    if session_id not in active_sessions:
        return jsonify({"status": "error", "message": "Session not found"}), 404
        
    try:
        active_sessions[session_id]['analyzer'].start_calibration()
        return jsonify({"status": "success", "message": "Calibration started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/start-reading-test/<session_id>', methods=['POST'])
def start_reading_test(session_id):
    if session_id not in active_sessions:
        return jsonify({"status": "error", "message": "Session not found"}), 404
        
    try:
        text = request.json.get('text', '')
        if not text:
            return jsonify({"status": "error", "message": "No text provided"}), 400
            
        active_sessions[session_id]['analyzer'].start_reading_test(text)
        return jsonify({"status": "success", "message": "Reading test started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

async def handle_websocket(websocket):
    try:
        session_id = None
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'init':
                # Handle session initialization
                session_id = data.get('session_id')
                if not session_id or session_id not in active_sessions:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid or expired session"
                    }))
                    await websocket.close()
                    return
                
                # Store WebSocket connection for this session
                if session_id in websocket_connections:
                    try:
                        old_ws = websocket_connections[session_id]
                        await old_ws.send(json.dumps({
                            "type": "error",
                            "message": "Session taken over by another connection"
                        }))
                        await old_ws.close()
                    except:
                        pass
                websocket_connections[session_id] = websocket
                logger.info(f"Session {session_id} initialized with WebSocket connection")
                
                # Send initial metrics
                await websocket.send(json.dumps(active_sessions[session_id]['metrics']))
                
            elif data['type'] == 'frame':
                # Validate session
                frame_session_id = data.get('session_id')
                if not frame_session_id or frame_session_id != session_id:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid or expired session"
                    }))
                    continue
                
                if frame_session_id not in active_sessions:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Session not found"
                    }))
                    await websocket.close()
                    return
                    
                # Process frame
                try:
                    # Decode frame
                    frame_data = base64.b64decode(data['frame'])
                    nparr = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    # Process frame using ReadingAnalyzer
                    analyzer = active_sessions[frame_session_id]['analyzer']
                    processed_frame, eye_data = analyzer.analyze_frame(frame)
                    
                    # Encode processed frame
                    _, buffer = cv2.imencode('.jpg', processed_frame)
                    processed_frame_data = base64.b64encode(buffer).decode('utf-8')
                    
                    # Get reading metrics
                    metrics = analyzer._analyze_reading_patterns()
                    if metrics and 'dyslexia_indicators' in metrics:
                        response = {
                            'reading_speed': int(metrics.get('reading_speed', 0)),
                            'fixations': metrics.get('fixation_count', 0),
                            'regressions': int(metrics.get('regression_count', 0)),
                            'dyslexia_probability': int(metrics['dyslexia_indicators']['probability'] * 100),
                            'indicators': metrics['dyslexia_indicators']['indicators'],
                            'severity': metrics['dyslexia_indicators']['severity'],
                            'processed_frame': processed_frame_data
                        }
                        
                        # Update session metrics
                        active_sessions[frame_session_id]['metrics'] = response
                        
                        # Send metrics to client
                        await websocket.send(json.dumps(response))
                except Exception as e:
                    logger.error(f"Error processing frame: {str(e)}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Error processing frame: {str(e)}"
                    }))
            
            elif data['type'] == 'calibration_start':
                if not session_id or session_id != data.get('session_id'):
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid session for calibration"
                    }))
                    continue
                    
                if session_id in active_sessions:
                    try:
                        active_sessions[session_id]['analyzer'].start_calibration()
                        await websocket.send(json.dumps({
                            "type": "calibration_status",
                            "status": "started",
                            "points": active_sessions[session_id]['analyzer'].calibration_points
                        }))
                    except Exception as e:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": f"Error starting calibration: {str(e)}"
                        }))
            
            elif data['type'] == 'reading_test_start':
                if not session_id or session_id != data.get('session_id'):
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid session for reading test"
                    }))
                    continue
                    
                if session_id in active_sessions:
                    try:
                        text = data.get('text', '')
                        if not text:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": "No text provided for reading test"
                            }))
                            continue
                            
                        active_sessions[session_id]['analyzer'].start_reading_test(text)
                        await websocket.send(json.dumps({
                            "type": "reading_test_status",
                            "status": "started"
                        }))
                    except Exception as e:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": f"Error starting reading test: {str(e)}"
                        }))

            elif data['type'] == 'end_session':
                end_session_id = data.get('session_id')
                if end_session_id and end_session_id == session_id and end_session_id in active_sessions:
                    try:
                        active_sessions[end_session_id]['analyzer'].release()
                    except:
                        pass
                    active_sessions[end_session_id]["status"] = "completed"
                    if end_session_id in websocket_connections:
                        del websocket_connections[end_session_id]
                    await websocket.close()
                    return

    except Exception as e:
        logger.error(f"Error in websocket handler: {str(e)}")
        try:
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))
        except:
            pass
    finally:
        # Clean up if needed
        if session_id:
            if session_id in active_sessions:
                try:
                    active_sessions[session_id]['analyzer'].release()
                except:
                    pass
            if session_id in websocket_connections and websocket_connections[session_id] == websocket:
                del websocket_connections[session_id]
        try:
            await websocket.close()
        except:
            pass

async def start_websocket_server():
    async with websockets.serve(handle_websocket, "0.0.0.0", 8765):
        logger.info("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

def run_websocket_server():
    asyncio.run(start_websocket_server())

if __name__ == '__main__':
    # Start WebSocket server in a separate thread
    websocket_thread = threading.Thread(target=run_websocket_server, daemon=True)
    websocket_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', debug=True, use_reloader=False) 