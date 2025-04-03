import asyncio
import json
import base64
from typing import Dict, Any
from flask import Flask
from flask_socketio import SocketIO, emit
from .webcam_handler import WebcamHandler

class WebSocketHandler:
    def __init__(self, app: Flask):
        """
        Initialize WebSocket handler
        Args:
            app: Flask application instance
        """
        self.socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
        self.webcam_handler = WebcamHandler()
        self.frame_rate = 30  # Target FPS
        self.frame_interval = 1.0 / self.frame_rate
        self.setup_routes()

    def setup_routes(self):
        """Setup WebSocket routes"""
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')
            emit('connection_response', {'status': 'connected'})

        @self.socketio.on('start_eye_tracking')
        def handle_start_tracking():
            if self.webcam_handler.start():
                emit('tracking_started', {'status': 'success'})
                self.start_frame_stream()
            else:
                emit('tracking_started', {'status': 'error', 'message': 'Failed to start webcam'})

        @self.socketio.on('stop_eye_tracking')
        def handle_stop_tracking():
            self.webcam_handler.stop()
            emit('tracking_stopped', {'status': 'success'})

    def start_frame_stream(self):
        """Start streaming frames to the client"""
        async def stream_frames():
            last_frame_time = 0
            while True:
                current_time = asyncio.get_event_loop().time()
                elapsed = current_time - last_frame_time
                
                if elapsed >= self.frame_interval:
                    result = self.webcam_handler.get_frame()
                    if result is None:
                        break
                    
                    frame_bytes, eye_data = result
                    frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
                    
                    emit('frame', {
                        'frame': frame_base64,
                        'eye_data': eye_data
                    })
                    
                    last_frame_time = current_time
                else:
                    await asyncio.sleep(self.frame_interval - elapsed)

        asyncio.create_task(stream_frames())

    def run(self, host: str = '0.0.0.0', port: int = 5000):
        """Run the WebSocket server"""
        self.socketio.run(host=host, port=port) 