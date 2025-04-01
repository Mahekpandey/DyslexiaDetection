from typing import Dict, List, Tuple
import json
import os
from datetime import datetime
import numpy as np
import logging
import cv2
import mediapipe as mp
import time

logger = logging.getLogger(__name__)

class EyeTrackingService:
    def __init__(self):
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Calibration settings
        self.calibration_points = []
        self.is_calibrated = False
        self.calibration_matrix = None
        
        # Thresholds for detection
        self.thresholds = {
            'fixation_duration_min': 0.1,  # seconds
            'saccade_velocity_min': 30,    # pixels per second
            'blink_duration_max': 0.4,     # seconds
            'gaze_deviation_max': 0.2,     # normalized
            'backward_saccade_threshold': 0.3,  # proportion
            'reading_line_deviation': 0.15  # normalized
        }
        
        # Reading metrics
        self.reading_metrics = {
            'line_position': 0,
            'current_word': 0,
            'reading_speed': 0,
            'regression_count': 0
        }

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmarks indices
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        # Reading metrics
        self.last_gaze_point = None
        self.fixation_start_time = None
        self.fixation_threshold = 0.1  # 100ms
        self.saccade_threshold = 0.05  # Distance threshold for saccade detection
        self.regression_threshold = -0.1  # Negative x-movement threshold
        
        # Counters
        self.fixation_count = 0
        self.regression_count = 0
        self.words_read = 0
        self.reading_start_time = None

    def calibrate(self, points: List[Tuple[float, float]], gaze_data: List[Tuple[float, float]]) -> bool:
        """Calibrate eye tracking using reference points"""
        try:
            if len(points) != len(gaze_data) or len(points) < 5:
                return False
                
            # Convert to numpy arrays
            points = np.array(points)
            gaze_data = np.array(gaze_data)
            
            # Calculate transformation matrix
            self.calibration_matrix = np.linalg.lstsq(gaze_data, points, rcond=None)[0]
            self.is_calibrated = True
            
            logger.info("Calibration completed successfully")
            return True
        except Exception as e:
            logger.error(f"Calibration failed: {str(e)}")
            return False

    def process_frame_data(self, frame_data: Dict) -> Dict:
        """Process a single frame of eye tracking data"""
        try:
            # Extract raw gaze data
            left_eye = np.array(frame_data.get('left_eye', [0, 0]))
            right_eye = np.array(frame_data.get('right_eye', [0, 0]))
            timestamp = frame_data.get('timestamp', datetime.now().timestamp())
            
            # Apply calibration if available
            if self.is_calibrated:
                left_eye = self._apply_calibration(left_eye)
                right_eye = self._apply_calibration(right_eye)
            
            # Calculate basic metrics
            gaze_point = self._calculate_gaze_point(left_eye, right_eye)
            velocity = self._calculate_velocity(gaze_point, timestamp)
            acceleration = self._calculate_acceleration(velocity, timestamp)
            
            # Detect eye movements
            fixation = self._detect_fixation(velocity)
            saccade = self._detect_saccade(velocity, acceleration)
            blink = self._detect_blink(frame_data.get('blink_data', {}))
            
            # Update reading metrics
            self._update_reading_metrics(gaze_point, fixation, saccade)
            
            return {
                'timestamp': timestamp,
                'gaze_point': gaze_point.tolist(),
                'metrics': {
                    'velocity': float(velocity),
                    'acceleration': float(acceleration),
                    'fixation': fixation,
                    'saccade': saccade,
                    'blink': blink,
                    'reading_metrics': self.reading_metrics.copy()
                },
                'analysis': self._analyze_reading_pattern()
            }
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return {}

    def _apply_calibration(self, point: np.ndarray) -> np.ndarray:
        """Apply calibration transformation to gaze point"""
        if self.calibration_matrix is not None:
            return np.dot(point, self.calibration_matrix)
        return point

    def _calculate_gaze_point(self, left_eye: np.ndarray, right_eye: np.ndarray) -> np.ndarray:
        """Calculate combined gaze point from both eyes"""
        return (left_eye + right_eye) / 2

    def _calculate_velocity(self, current_point: np.ndarray, timestamp: float) -> float:
        """Calculate gaze velocity"""
        if not hasattr(self, '_last_point'):
            self._last_point = current_point
            self._last_timestamp = timestamp
            return 0.0
            
        dt = timestamp - self._last_timestamp
        if dt == 0:
            return 0.0
            
        velocity = np.linalg.norm(current_point - self._last_point) / dt
        
        self._last_point = current_point
        self._last_timestamp = timestamp
        
        return velocity

    def _calculate_acceleration(self, current_velocity: float, timestamp: float) -> float:
        """Calculate gaze acceleration"""
        if not hasattr(self, '_last_velocity'):
            self._last_velocity = current_velocity
            self._last_acc_timestamp = timestamp
            return 0.0
            
        dt = timestamp - self._last_acc_timestamp
        if dt == 0:
            return 0.0
            
        acceleration = (current_velocity - self._last_velocity) / dt
        
        self._last_velocity = current_velocity
        self._last_acc_timestamp = timestamp
        
        return acceleration

    def _detect_fixation(self, velocity: float) -> Dict:
        """Detect and analyze fixation"""
        is_fixation = velocity < self.thresholds['saccade_velocity_min']
        
        if is_fixation:
            if not hasattr(self, '_fixation_start'):
                self._fixation_start = datetime.now().timestamp()
            duration = datetime.now().timestamp() - self._fixation_start
        else:
            duration = 0
            self._fixation_start = None
            
        return {
            'is_fixation': is_fixation,
            'duration': duration
        }

    def _detect_saccade(self, velocity: float, acceleration: float) -> Dict:
        """Detect and analyze saccade"""
        is_saccade = velocity >= self.thresholds['saccade_velocity_min']
        
        return {
            'is_saccade': is_saccade,
            'velocity': velocity,
            'acceleration': acceleration
        }

    def _detect_blink(self, blink_data: Dict) -> Dict:
        """Analyze blink data"""
        return {
            'is_blinking': blink_data.get('is_blinking', False),
            'duration': blink_data.get('duration', 0),
            'frequency': blink_data.get('frequency', 0)
        }

    def _update_reading_metrics(self, gaze_point: np.ndarray, fixation: Dict, saccade: Dict):
        """Update reading-specific metrics"""
        if fixation['is_fixation']:
            # Update current line position
            self.reading_metrics['line_position'] = gaze_point[1]
            
            # Estimate word position based on x-coordinate
            self.reading_metrics['current_word'] = int(gaze_point[0] / 50)  # assuming average word width
            
            # Update reading speed (words per minute)
            if fixation['duration'] > 0:
                self.reading_metrics['reading_speed'] = 60 / fixation['duration']
        
        if saccade['is_saccade']:
            # Detect backward saccades (regressions)
            if hasattr(self, '_last_gaze_x') and gaze_point[0] < self._last_gaze_x:
                self.reading_metrics['regression_count'] += 1
                
        self._last_gaze_x = gaze_point[0]

    def _analyze_reading_pattern(self) -> Dict:
        """Analyze reading pattern for dyslexia indicators"""
        metrics = self.reading_metrics
        
        # Calculate indicators
        indicators = {
            'high_regression_rate': (metrics['regression_count'] / max(metrics['current_word'], 1)
                                   > self.thresholds['backward_saccade_threshold']),
            'irregular_line_tracking': abs(metrics['line_position'] - getattr(self, '_last_line_position', 0))
                                     > self.thresholds['reading_line_deviation']
                                     if hasattr(self, '_last_line_position') else False,
            'slow_reading_speed': metrics['reading_speed'] < 150  # typical reading speed threshold
        }
        
        # Calculate probability
        indicator_weights = {
            'high_regression_rate': 0.4,
            'irregular_line_tracking': 0.3,
            'slow_reading_speed': 0.3
        }
        
        probability = sum(indicator_weights[k] * float(v) for k, v in indicators.items())
        
        self._last_line_position = metrics['line_position']
        
        return {
            'indicators': indicators,
            'probability': probability,
            'confidence': self._calculate_confidence(metrics)
        }

    def _calculate_confidence(self, metrics: Dict) -> float:
        """Calculate confidence level of the analysis"""
        # Factors affecting confidence:
        # 1. Number of data points
        # 2. Consistency of measurements
        # 3. Quality of calibration
        
        data_points_weight = min(1.0, metrics.get('current_word', 0) / 100)
        calibration_weight = 1.0 if self.is_calibrated else 0.5
        
        return data_points_weight * calibration_weight

    def save_session_data(self, session_id: str, data: Dict):
        """Save session data to file"""
        filename = os.path.join(self.data_dir, f"session_{session_id}.json")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def get_session_data(self, session_id: str) -> Dict:
        """Retrieve session data"""
        filename = os.path.join(self.data_dir, f"session_{session_id}.json")
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def analyze_session(self, session_id: str) -> Dict:
        """Analyze a complete session and generate report"""
        data = self.get_session_data(session_id)
        if not data:
            return None

        metrics_list = [entry.get('metrics', {}) for entry in data.get('data', [])]
        if not metrics_list:
            return {'error': 'No metrics data found'}

        # Calculate aggregate metrics
        avg_gaze_stability = np.mean([m.get('gaze_stability', 0) for m in metrics_list])
        avg_blink_rate = np.mean([m.get('blink_rate', 0) for m in metrics_list])
        
        # Get dyslexia probabilities over time
        probabilities = [m.get('dyslexia_indicators', {}).get('probability', 0) 
                        for m in metrics_list]
        
        return {
            'session_id': session_id,
            'duration': len(metrics_list),  # number of data points
            'average_metrics': {
                'gaze_stability': float(avg_gaze_stability),
                'blink_rate': float(avg_blink_rate),
                'dyslexia_probability': float(np.mean(probabilities))
            },
            'trend': {
                'improving': bool(len(probabilities) > 1 and 
                                probabilities[-1] < np.mean(probabilities)),
                'confidence': self._calculate_confidence({'data': metrics_list})
            }
        }

    def process_frame(self, frame):
        if frame is None:
            return None

        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        
        if not results.multi_face_landmarks:
            return {
                "reading_speed": 0,
                "fixations": self.fixation_count,
                "regressions": self.regression_count,
                "dyslexia_probability": 0
            }

        face_landmarks = results.multi_face_landmarks[0]
        
        # Get eye landmarks
        left_eye = np.array([[face_landmarks.landmark[i].x * frame.shape[1],
                            face_landmarks.landmark[i].y * frame.shape[0]] for i in self.LEFT_EYE])
        right_eye = np.array([[face_landmarks.landmark[i].x * frame.shape[1],
                             face_landmarks.landmark[i].y * frame.shape[0]] for i in self.RIGHT_EYE])

        # Calculate gaze point (average of both eyes)
        current_gaze = np.mean([np.mean(left_eye, axis=0), np.mean(right_eye, axis=0)], axis=0)

        # Initialize reading start time if not set
        if self.reading_start_time is None:
            self.reading_start_time = time.time()

        # Process eye movements
        metrics = self._process_eye_movements(current_gaze)
        
        # Update last gaze point
        self.last_gaze_point = current_gaze

        return metrics

    def _process_eye_movements(self, current_gaze):
        if self.last_gaze_point is None:
            return {
                "reading_speed": 0,
                "fixations": self.fixation_count,
                "regressions": self.regression_count,
                "dyslexia_probability": 0
            }

        # Calculate movement
        movement = np.linalg.norm(current_gaze - self.last_gaze_point)

        # Detect fixation
        if movement < self.saccade_threshold:
            if self.fixation_start_time is None:
                self.fixation_start_time = time.time()
            elif time.time() - self.fixation_start_time > self.fixation_threshold:
                self.fixation_count += 1
                self.fixation_start_time = None
        else:
            self.fixation_start_time = None
            # Detect regression (backward movement)
            if current_gaze[0] - self.last_gaze_point[0] < self.regression_threshold:
                self.regression_count += 1

        # Calculate reading speed (rough estimate)
        reading_time = time.time() - self.reading_start_time
        # Assume average word length of 5 characters and typical reading distance
        estimated_words = max(1, self.fixation_count // 2)  # Rough estimate: 2 fixations per word
        reading_speed = int((estimated_words / reading_time) * 60) if reading_time > 0 else 0

        # Calculate dyslexia probability based on metrics
        regression_rate = self.regression_count / max(1, self.fixation_count)
        dyslexia_probability = int(min(100, max(0, 
            regression_rate * 100 +  # High regression rate indicates potential dyslexia
            (self.fixation_count / max(1, estimated_words) - 1) * 50  # More fixations than typical
        )))

        return {
            "reading_speed": reading_speed,
            "fixations": self.fixation_count,
            "regressions": self.regression_count,
            "dyslexia_probability": dyslexia_probability
        }

    def reset_metrics(self):
        self.fixation_count = 0
        self.regression_count = 0
        self.words_read = 0
        self.reading_start_time = None
        self.last_gaze_point = None
        self.fixation_start_time = None 