import asyncio
import json
import logging
import numpy as np
import base64
import cv2
from typing import Dict, Set
from websockets.server import WebSocketServerProtocol
from eye_tracking_service import EyeTrackingService

logger = logging.getLogger(__name__)

class WebSocketHandler:
    def __init__(self):
        self.clients: Set[WebSocketServerProtocol] = set()
        self.eye_tracking_service = EyeTrackingService()
        self.active_sessions: Dict[str, Dict] = {}
        logger.info("WebSocket handler initialized")

    async def register(self, websocket: WebSocketServerProtocol):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"New client connected. Total clients: {len(self.clients)}")

    async def unregister(self, websocket: WebSocketServerProtocol):
        """Unregister a WebSocket client"""
        self.clients.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get('type')

            if message_type == 'frame':
                # Decode base64 image
                frame_data = base64.b64decode(data['frame'])
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Process frame using your existing implementation
                metrics = self.eye_tracking_service.process_frame(frame)
                
                if metrics:
                    # Add additional analysis from your implementation
                    analysis = self.eye_tracking_service._analyze_reading_pattern()
                    metrics.update(analysis)
                    await websocket.send(json.dumps(metrics))

            elif message_type == 'calibration_start':
                # Use your existing calibration logic
                points = data.get('points', [])
                gaze_data = data.get('gaze_data', [])
                
                if points and gaze_data:
                    success = self.eye_tracking_service.calibrate(points, gaze_data)
                    await websocket.send(json.dumps({
                        "type": "calibration_status",
                        "status": "completed" if success else "failed"
                    }))
                else:
                    self.eye_tracking_service.reset_metrics()
                    await websocket.send(json.dumps({
                        "type": "calibration_status",
                        "status": "started"
                    }))

            elif message_type == 'reading_test_start':
                # Reset metrics and start reading test
                self.eye_tracking_service.reset_metrics()
                await websocket.send(json.dumps({
                    "type": "reading_test_status",
                    "status": "started"
                }))

            elif message_type == 'end_session':
                session_id = data.get('session_id')
                if session_id:
                    # Save session data using your existing implementation
                    session_data = {
                        'metrics': self.eye_tracking_service.reading_metrics,
                        'analysis': self.eye_tracking_service._analyze_reading_pattern()
                    }
                    self.eye_tracking_service.save_session_data(session_id, session_data)
                    await websocket.send(json.dumps({
                        "type": "session_ended",
                        "status": "success"
                    }))

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def _handle_start_session(self, websocket: WebSocketServerProtocol, payload: Dict):
        """Handle session start request"""
        session_id = payload.get('session_id')
        if not session_id:
            await self._send_error(websocket, "Session ID is required")
            return

        self.active_sessions[session_id] = {
            'websocket': websocket,
            'start_time': asyncio.get_event_loop().time(),
            'frame_count': 0,
            'calibrated': False
        }

        await self._send_response(websocket, {
            'type': 'session_started',
            'payload': {'session_id': session_id}
        })

    async def _handle_frame_data(self, websocket: WebSocketServerProtocol, payload: Dict):
        """Process frame data and send analysis results"""
        session_id = payload.get('session_id')
        if not session_id or session_id not in self.active_sessions:
            await self._send_error(websocket, "Invalid session ID")
            return

        frame_data = payload.get('frame_data', {})
        session = self.active_sessions[session_id]
        session['frame_count'] += 1

        # Process frame data
        processed_data = self.eye_tracking_service.process_frame_data(frame_data)
        
        # Send processed data back to client
        await self._send_response(websocket, {
            'type': 'frame_processed',
            'payload': {
                'session_id': session_id,
                'frame_number': session['frame_count'],
                'data': processed_data
            }
        })

    async def _handle_calibration(self, websocket: WebSocketServerProtocol, payload: Dict):
        """Handle calibration data"""
        session_id = payload.get('session_id')
        if not session_id or session_id not in self.active_sessions:
            await self._send_error(websocket, "Invalid session ID")
            return

        points = payload.get('points', [])
        gaze_data = payload.get('gaze_data', [])

        success = self.eye_tracking_service.calibrate(points, gaze_data)
        session = self.active_sessions[session_id]
        session['calibrated'] = success

        await self._send_response(websocket, {
            'type': 'calibration_result',
            'payload': {
                'session_id': session_id,
                'success': success
            }
        })

    async def _handle_end_session(self, websocket: WebSocketServerProtocol, payload: Dict):
        """Handle session end request"""
        session_id = payload.get('session_id')
        if not session_id or session_id not in self.active_sessions:
            await self._send_error(websocket, "Invalid session ID")
            return

        session = self.active_sessions.pop(session_id)
        duration = asyncio.get_event_loop().time() - session['start_time']

        # Save session data
        session_data = {
            'duration': duration,
            'frame_count': session['frame_count'],
            'calibrated': session['calibrated']
        }
        self.eye_tracking_service.save_session_data(session_id, session_data)

        await self._send_response(websocket, {
            'type': 'session_ended',
            'payload': {
                'session_id': session_id,
                'duration': duration,
                'frame_count': session['frame_count']
            }
        })

    async def _send_error(self, websocket: WebSocketServerProtocol, message: str):
        """Send error message to client"""
        await self._send_response(websocket, {
            'type': 'error',
            'payload': {'message': message}
        })

    async def _send_response(self, websocket: WebSocketServerProtocol, data: Dict):
        """Send response to client"""
        try:
            await websocket.send(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")

    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return

        for client in self.clients.copy():
            try:
                await client.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to client: {str(e)}")
                await self.unregister(client) 