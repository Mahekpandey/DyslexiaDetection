import cv2
import numpy as np
from typing import Optional, Tuple
from .eye_tracker import EyeTracker

class WebcamHandler:
    def __init__(self, camera_id: int = 0):
        """
        Initialize webcam handler
        Args:
            camera_id: ID of the camera to use (default: 0 for primary camera)
        """
        self.camera_id = camera_id
        self.cap = None
        self.eye_tracker = EyeTracker()
        self.is_running = False

    def start(self) -> bool:
        """
        Start webcam capture
        Returns:
            bool: True if successful, False otherwise
        """
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.is_running = True
        return True

    def get_frame(self) -> Optional[Tuple[np.ndarray, dict]]:
        """
        Get a single frame from the webcam
        Returns:
            Tuple of (frame, eye tracking data) if successful, None otherwise
        """
        if not self.is_running or self.cap is None:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        # Process frame with eye tracker
        processed_frame, eye_data = self.eye_tracker.process_frame(frame)
        
        # Encode frame for web transmission
        _, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        
        return frame_bytes, eye_data[0] if eye_data else {}

    def stop(self):
        """Stop webcam capture and release resources"""
        self.is_running = False
        if self.cap is not None:
            self.cap.release()
        self.eye_tracker.release() 