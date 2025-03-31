import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, List

class EyeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[dict]]:
        """
        Process a single frame for eye tracking
        Args:
            frame: Input frame (BGR format)
        Returns:
            Tuple of (processed frame, eye tracking data)
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        eye_data = []
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Extract eye landmarks and calculate metrics
                eye_metrics = self._extract_eye_metrics(face_landmarks)
                eye_data.append(eye_metrics)
                
                # Draw face mesh
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(
                        thickness=1, circle_radius=1
                    )
                )
                
                # Draw eye landmarks with different colors
                self._draw_eye_landmarks(frame, face_landmarks)
                
                # Add text with eye tracking status
                cv2.putText(frame, "Eye Tracking Active", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame, eye_data

    def _draw_eye_landmarks(self, frame: np.ndarray, landmarks):
        """Draw eye landmarks with different colors for better visualization"""
        # Left eye landmarks (green)
        left_eye_indices = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
        for idx in left_eye_indices:
            point = landmarks.landmark[idx]
            h, w, _ = frame.shape
            x, y = int(point.x * w), int(point.y * h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # Right eye landmarks (blue)
        right_eye_indices = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
        for idx in right_eye_indices:
            point = landmarks.landmark[idx]
            h, w, _ = frame.shape
            x, y = int(point.x * w), int(point.y * h)
            cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)

    def _extract_eye_metrics(self, landmarks) -> dict:
        """
        Extract eye tracking metrics from face landmarks
        Args:
            landmarks: Face mesh landmarks
        Returns:
            Dictionary containing eye tracking metrics
        """
        # Get eye landmarks
        left_eye = self._get_eye_landmarks(landmarks, "left")
        right_eye = self._get_eye_landmarks(landmarks, "right")
        
        # Calculate basic metrics
        left_center = self._calculate_eye_center(left_eye)
        right_center = self._calculate_eye_center(right_eye)
        
        return {
            "left_eye_center": left_center,
            "right_eye_center": right_center,
            "pupil_position": None,  # To be implemented
            "gaze_direction": None,  # To be implemented
            "fixation_points": [],   # To be implemented
            "saccades": [],          # To be implemented
            "blinks": []             # To be implemented
        }

    def _get_eye_landmarks(self, landmarks, eye: str) -> List[Tuple[float, float]]:
        """Get landmarks for a specific eye"""
        if eye == "left":
            indices = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
        else:
            indices = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
        
        return [(landmarks.landmark[idx].x, landmarks.landmark[idx].y) for idx in indices]

    def _calculate_eye_center(self, eye_landmarks: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate the center point of an eye"""
        x_coords = [x for x, _ in eye_landmarks]
        y_coords = [y for _, y in eye_landmarks]
        return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))

    def release(self):
        """Release resources"""
        self.face_mesh.close() 