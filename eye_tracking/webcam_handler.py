import cv2
import numpy as np
from typing import Optional, Tuple, Dict
import threading
import time

class WebcamHandler:
    def __init__(self):
        self.cap = None
        self.is_running = False
        self.frame_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.frame_rate = 30
        self.frame_interval = 1.0 / self.frame_rate
        self.last_frame_time = 0

    def start(self) -> bool:
        """Start webcam capture"""
        if self.is_running:
            return True
            
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            return False
            
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, self.frame_rate)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer size
        
        self.is_running = True
        self.frame_thread = threading.Thread(target=self._capture_frames)
        self.frame_thread.daemon = True
        self.frame_thread.start()
        return True

    def stop(self):
        """Stop webcam capture"""
        self.is_running = False
        if self.frame_thread:
            self.frame_thread.join()
        if self.cap:
            self.cap.release()
        self.cap = None
        self.current_frame = None

    def _capture_frames(self):
        """Capture frames in a separate thread"""
        while self.is_running:
            current_time = time.time()
            elapsed = current_time - self.last_frame_time
            
            if elapsed >= self.frame_interval:
                ret, frame = self.cap.read()
                if ret:
                    with self.frame_lock:
                        self.current_frame = frame
                    self.last_frame_time = current_time
                else:
                    time.sleep(0.001)  # Small sleep if frame capture failed
            else:
                time.sleep(max(0, self.frame_interval - elapsed))

    def get_frame(self) -> Optional[Tuple[bytes, Dict]]:
        """Get the current frame and eye tracking data"""
        if not self.is_running or self.current_frame is None:
            return None
            
        with self.frame_lock:
            frame = self.current_frame.copy()
            
        # Convert frame to JPEG format
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_bytes = buffer.tobytes()
        
        return frame_bytes, {}  # Eye tracking data will be added by the analyzer 