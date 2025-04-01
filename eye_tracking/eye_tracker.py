import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, List, Dict, Optional
import math

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
        
        # Define eye landmark indices
        self.LEFT_EYE_INDICES = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
        self.RIGHT_EYE_INDICES = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
        
        # Upper and lower eyelid indices for blink detection
        self.LEFT_EYE_UPPER = [159, 160, 161]
        self.LEFT_EYE_LOWER = [145, 144, 163]
        self.RIGHT_EYE_UPPER = [386, 385, 384]
        self.RIGHT_EYE_LOWER = [374, 373, 390]
        
        # Pupil indices (iris landmarks)
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        
        # Blink detection parameters
        self.blink_threshold = 0.2  # EAR threshold for blink detection
        self.blink_frames = []      # Store recent EAR values
        self.blink_window = 10      # Number of frames to store for blink detection
        self.min_blink_frames = 2   # Minimum frames for a blink
        
        # Gaze direction parameters
        self.gaze_history = []      # Store recent gaze directions
        self.gaze_window = 5        # Number of frames to average for gaze smoothing

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
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
        
        eye_data = {}
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Extract eye metrics
                eye_metrics = self._extract_eye_metrics(frame, face_landmarks)
                eye_data.update(eye_metrics)
                
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
                
                # Draw eye landmarks and gaze
                self._draw_eye_landmarks(frame, face_landmarks)
                self._draw_gaze_direction(frame, eye_data)
                self._draw_blink_status(frame, eye_data)
        
        return frame, eye_data

    def _calculate_ear(self, eye_upper: List[int], eye_lower: List[int], landmarks) -> float:
        """Calculate Eye Aspect Ratio (EAR) for blink detection"""
        upper_y = np.mean([landmarks.landmark[i].y for i in eye_upper])
        lower_y = np.mean([landmarks.landmark[i].y for i in eye_lower])
        return abs(upper_y - lower_y)

    def _detect_blinks(self, left_ear: float, right_ear: float) -> Dict:
        """Detect blinks using EAR values"""
        avg_ear = (left_ear + right_ear) / 2
        self.blink_frames.append(avg_ear)
        if len(self.blink_frames) > self.blink_window:
            self.blink_frames.pop(0)
        
        is_blinking = avg_ear < self.blink_threshold
        blink_duration = sum(1 for ear in self.blink_frames if ear < self.blink_threshold)
        
        return {
            'is_blinking': is_blinking,
            'blink_duration': blink_duration,
            'ear_value': avg_ear
        }

    def _calculate_gaze_direction(self, iris_center: Tuple[float, float], eye_corners: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate gaze direction vector"""
        eye_center = np.mean(eye_corners, axis=0)
        gaze_vector = np.array(iris_center) - np.array(eye_center)
        gaze_magnitude = np.linalg.norm(gaze_vector)
        if gaze_magnitude > 0:
            gaze_vector = gaze_vector / gaze_magnitude
        return tuple(gaze_vector)

    def _extract_eye_metrics(self, frame: np.ndarray, landmarks) -> Dict:
        """
        Extract eye tracking metrics from face landmarks
        Args:
            frame: Input frame
            landmarks: Face mesh landmarks
        Returns:
            Dictionary containing eye tracking metrics
        """
        h, w = frame.shape[:2]
        
        # Get eye landmarks
        left_eye = self._get_eye_landmarks(landmarks, "left")
        right_eye = self._get_eye_landmarks(landmarks, "right")
        
        # Calculate eye centers
        left_center = self._calculate_eye_center(left_eye)
        right_center = self._calculate_eye_center(right_eye)
        
        # Calculate pupil positions using iris landmarks
        left_pupil = self._calculate_pupil_position(landmarks, self.LEFT_IRIS, w, h)
        right_pupil = self._calculate_pupil_position(landmarks, self.RIGHT_IRIS, w, h)
        
        # Calculate relative pupil positions (normalized coordinates)
        left_pupil_rel = self._calculate_relative_pupil_position(left_pupil, left_eye)
        right_pupil_rel = self._calculate_relative_pupil_position(right_pupil, right_eye)
        
        # Calculate EAR for blink detection
        left_ear = self._calculate_ear(self.LEFT_EYE_UPPER, self.LEFT_EYE_LOWER, landmarks)
        right_ear = self._calculate_ear(self.RIGHT_EYE_UPPER, self.RIGHT_EYE_LOWER, landmarks)
        blink_data = self._detect_blinks(left_ear, right_ear)
        
        # Calculate gaze direction
        left_gaze = self._calculate_gaze_direction(left_pupil_rel, left_eye)
        right_gaze = self._calculate_gaze_direction(right_pupil_rel, right_eye)
        
        # Update gaze history for smoothing
        self.gaze_history.append((left_gaze, right_gaze))
        if len(self.gaze_history) > self.gaze_window:
            self.gaze_history.pop(0)
        
        # Calculate smoothed gaze direction
        avg_left_gaze = np.mean([g[0] for g in self.gaze_history], axis=0)
        avg_right_gaze = np.mean([g[1] for g in self.gaze_history], axis=0)
        
        return {
            "left_eye_center": left_center,
            "right_eye_center": right_center,
            "left_pupil": left_pupil,
            "right_pupil": right_pupil,
            "left_pupil_relative": left_pupil_rel,
            "right_pupil_relative": right_pupil_rel,
            "left_gaze": tuple(avg_left_gaze),
            "right_gaze": tuple(avg_right_gaze),
            "blink_data": blink_data
        }

    def _draw_gaze_direction(self, frame: np.ndarray, eye_data: Dict):
        """Visualize gaze direction"""
        if 'left_gaze' not in eye_data:
            return
            
        h, w = frame.shape[:2]
        scale = 50  # Scale factor for gaze vector visualization
        
        # Draw left eye gaze
        left_pupil = eye_data['left_pupil']
        left_gaze = eye_data['left_gaze']
        left_end = (
            int(left_pupil[0] + left_gaze[0] * scale),
            int(left_pupil[1] + left_gaze[1] * scale)
        )
        cv2.arrowedLine(frame, 
                       (int(left_pupil[0]), int(left_pupil[1])),
                       left_end,
                       (0, 255, 255), 2)
        
        # Draw right eye gaze
        right_pupil = eye_data['right_pupil']
        right_gaze = eye_data['right_gaze']
        right_end = (
            int(right_pupil[0] + right_gaze[0] * scale),
            int(right_pupil[1] + right_gaze[1] * scale)
        )
        cv2.arrowedLine(frame,
                       (int(right_pupil[0]), int(right_pupil[1])),
                       right_end,
                       (0, 255, 255), 2)

    def _draw_blink_status(self, frame: np.ndarray, eye_data: Dict):
        """Visualize blink status"""
        if 'blink_data' not in eye_data:
            return
            
        blink_data = eye_data['blink_data']
        color = (0, 0, 255) if blink_data['is_blinking'] else (0, 255, 0)
        status = "BLINK" if blink_data['is_blinking'] else "OPEN"
        cv2.putText(frame, f"Eyes: {status}", (10, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"EAR: {blink_data['ear_value']:.2f}", (10, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    def _draw_eye_landmarks(self, frame: np.ndarray, landmarks):
        """Draw eye landmarks and pupils with different colors"""
        h, w = frame.shape[:2]
        
        # Draw left eye landmarks (green)
        for idx in self.LEFT_EYE_INDICES:
            point = landmarks.landmark[idx]
            x, y = int(point.x * w), int(point.y * h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        
        # Draw right eye landmarks (blue)
        for idx in self.RIGHT_EYE_INDICES:
            point = landmarks.landmark[idx]
            x, y = int(point.x * w), int(point.y * h)
            cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)
        
        # Draw iris landmarks (red)
        for idx in self.LEFT_IRIS + self.RIGHT_IRIS:
            point = landmarks.landmark[idx]
            x, y = int(point.x * w), int(point.y * h)
            cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)

    def _calculate_pupil_position(self, landmarks, iris_indices: List[int], frame_width: int, frame_height: int) -> Tuple[float, float]:
        """Calculate pupil position using iris landmarks"""
        x_coords = []
        y_coords = []
        
        for idx in iris_indices:
            point = landmarks.landmark[idx]
            x_coords.append(point.x * frame_width)
            y_coords.append(point.y * frame_height)
        
        return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))

    def _calculate_relative_pupil_position(self, pupil_pos: Tuple[float, float], eye_landmarks: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate pupil position relative to eye corners"""
        # Get eye corner positions
        eye_left = min(eye_landmarks, key=lambda p: p[0])[0]
        eye_right = max(eye_landmarks, key=lambda p: p[0])[0]
        eye_top = min(eye_landmarks, key=lambda p: p[1])[1]
        eye_bottom = max(eye_landmarks, key=lambda p: p[1])[1]
        
        # Calculate relative position (0 to 1 for both x and y)
        rel_x = (pupil_pos[0] - eye_left) / (eye_right - eye_left)
        rel_y = (pupil_pos[1] - eye_top) / (eye_bottom - eye_top)
        
        return (rel_x, rel_y)

    def _get_eye_landmarks(self, landmarks, eye: str) -> List[Tuple[float, float]]:
        """Get landmarks for a specific eye"""
        indices = self.LEFT_EYE_INDICES if eye == "left" else self.RIGHT_EYE_INDICES
        return [(landmarks.landmark[idx].x, landmarks.landmark[idx].y) for idx in indices]

    def _calculate_eye_center(self, eye_landmarks: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate the center point of an eye"""
        x_coords = [x for x, _ in eye_landmarks]
        y_coords = [y for _, y in eye_landmarks]
        return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))

    def release(self):
        """Release resources"""
        if hasattr(self, 'face_mesh') and self.face_mesh:
            self.face_mesh.close() 