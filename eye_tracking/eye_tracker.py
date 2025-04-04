import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, List, Dict, Optional
import math
from collections import deque
import time
from .cognitive_load_analyzer import CognitiveLoadAnalyzer

class EyeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,  # Increased confidence threshold
            min_tracking_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Enhanced eye landmark indices for better accuracy
        self.LEFT_EYE_INDICES = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
        self.RIGHT_EYE_INDICES = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
        
        # Refined upper and lower eyelid indices
        self.LEFT_EYE_UPPER = [159, 160, 161, 246]
        self.LEFT_EYE_LOWER = [145, 144, 163, 33]
        self.RIGHT_EYE_UPPER = [386, 385, 384, 398]
        self.RIGHT_EYE_LOWER = [374, 373, 390, 362]
        
        # Iris landmarks for precise gaze tracking
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        
        # Enhanced blink detection parameters
        self.blink_threshold = 0.23  # Adjusted threshold
        self.blink_frames = deque(maxlen=15)  # Increased buffer
        self.min_blink_frames = 3
        self.blink_history = deque(maxlen=300)  # 10 seconds at 30fps
        
        # Enhanced gaze tracking parameters
        self.gaze_history = deque(maxlen=10)
        self.smoothing_factor = 0.4
        self.gaze_stability_threshold = 0.1
        
        # Data collection for ML
        self.frame_timestamps = []
        self.eye_metrics = {
            'fixations': [],
            'saccades': [],
            'blinks': [],
            'gaze_positions': [],
            'pupil_sizes': []
        }
        
        # Frame processing
        self.frame_count = 0
        self.last_landmarks = None
        self.last_eye_data = None
        self.frame_shape = None
        self.fps = 30.0  # Assumed fps
        
        # Initialize feature extraction parameters
        self.min_fixation_duration = 0.1  # 100ms
        self.max_saccade_velocity = 500  # degrees/second
        self.saccade_threshold = 0.1  # normalized units
        
        # Add cognitive load analyzer
        self.cognitive_analyzer = CognitiveLoadAnalyzer()
        self.cognitive_metrics = {
            'cognitive_load_score': 0.0,
            'load_level': 'Low',
            'pupil_load': 0.0,
            'blink_load': 0.0
        }

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Process frame with enhanced metrics collection"""
        if frame is None:
            return None, {}

        self.frame_count += 1
        timestamp = time.time()
        self.frame_timestamps.append(timestamp)
        
        # Store frame shape for coordinate conversion
        if self.frame_shape is None:
            self.frame_shape = frame.shape[:2]

        # Process frame with MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        if not results.multi_face_landmarks:
            return frame, self._get_empty_metrics()
        
        face_landmarks = results.multi_face_landmarks[0]
        
        # Extract eye landmarks and metrics
        left_eye = self._extract_eye_landmarks(face_landmarks, self.LEFT_EYE_INDICES)
        right_eye = self._extract_eye_landmarks(face_landmarks, self.RIGHT_EYE_INDICES)
        
        # Calculate core metrics
        left_ear = self._calculate_ear(left_eye)
        right_ear = self._calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Enhanced blink detection
        is_blink = self._detect_blink(avg_ear)
        if is_blink:
            self.blink_history.append(timestamp)
        
        # Calculate gaze metrics
        left_gaze = self._calculate_gaze_direction(left_eye)
        right_gaze = self._calculate_gaze_direction(right_eye)
        
        # Calculate pupil size
        left_pupil_size = self._calculate_pupil_size(left_eye)
        right_pupil_size = self._calculate_pupil_size(right_eye)
        
        # Store metrics for ML
        metrics = {
            'timestamp': timestamp,
            'left_eye': left_eye,
            'right_eye': right_eye,
            'left_ear': left_ear,
            'right_ear': right_ear,
            'avg_ear': avg_ear,
            'is_blink': is_blink,
            'left_gaze': left_gaze,
            'right_gaze': right_gaze,
            'left_pupil_size': left_pupil_size,
            'right_pupil_size': right_pupil_size,
            'gaze_stability': self._calculate_gaze_stability(),
            'blink_rate': self._calculate_blink_rate(timestamp)
        }
        
        self._update_ml_features(metrics)
        
        # Draw visualizations
        self._draw_face_mesh(frame, face_landmarks)
        self._draw_eye_landmarks(frame, left_eye, right_eye)
        self._draw_blink_status(frame, is_blink)
        self._draw_gaze_direction(frame, left_eye, right_eye, left_gaze, right_gaze)
        
        return frame, metrics

    def _draw_face_mesh(self, frame: np.ndarray, face_landmarks) -> None:
        """Draw face mesh with improved visibility"""
        h, w = frame.shape[:2]
        for connection in self.mp_face_mesh.FACEMESH_TESSELATION:
            start_idx = connection[0]
            end_idx = connection[1]
            
            start_point = face_landmarks.landmark[start_idx]
            end_point = face_landmarks.landmark[end_idx]
            
            start_x = int(start_point.x * w)
            start_y = int(start_point.y * h)
            end_x = int(end_point.x * w)
            end_y = int(end_point.y * h)
            
            # Draw thicker lines with white color for better visibility
            cv2.line(frame, (start_x, start_y), (end_x, end_y), 
                    (255, 255, 255), 1, cv2.LINE_AA)

    def _draw_eye_landmarks(self, frame: np.ndarray, left_eye: np.ndarray, right_eye: np.ndarray) -> None:
        """Draw eye landmarks with improved visibility"""
        def draw_eye(eye_points):
            if len(eye_points) < 4:
                return
                
            # Draw iris center
            center = eye_points[0].astype(int)
            cv2.circle(frame, tuple(center), 3, (0, 255, 0), -1, cv2.LINE_AA)
            
            # Draw iris points
            for point in eye_points[1:4]:
                pt = point.astype(int)
                cv2.circle(frame, tuple(pt), 2, (255, 0, 0), -1, cv2.LINE_AA)
            
            # Draw eye contour
            for point in eye_points[4:]:
                pt = point.astype(int)
                cv2.circle(frame, tuple(pt), 2, (0, 255, 255), -1, cv2.LINE_AA)
                
            # Draw eye contour lines
            contour = eye_points[4:].astype(np.int32)
            cv2.polylines(frame, [contour], True, (0, 255, 255), 1, cv2.LINE_AA)
        
        if left_eye.size > 0:
            draw_eye(left_eye)
        if right_eye.size > 0:
            draw_eye(right_eye)

    def _draw_blink_status(self, frame: np.ndarray, is_blink: bool) -> None:
        """Draw blink status with improved visibility"""
        text = "BLINK" if is_blink else "OPEN"
        color = (0, 0, 255) if is_blink else (0, 255, 0)
        
        # Position at top-left with outline for better visibility
        pos = (10, 30)
        # Draw black outline
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                    (0, 0, 0), 4, cv2.LINE_AA)
        # Draw colored text
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                    color, 2, cv2.LINE_AA)

    def _calculate_ear(self, eye_landmarks) -> float:
        """Calculate Eye Aspect Ratio (EAR) for blink detection"""
        if len(eye_landmarks) < 6:  # Need at least 6 points for EAR
            return 0.0
            
        # Convert landmarks to numpy array if not already
        landmarks = np.array(eye_landmarks)
        
        # Get vertical distances
        # Use the middle points of upper and lower eyelid
        upper_mid_idx = len(landmarks) // 3
        lower_mid_idx = -len(landmarks) // 3
        
        upper_point = landmarks[upper_mid_idx]
        lower_point = landmarks[lower_mid_idx]
        
        # Calculate vertical distance
        vertical_dist = abs(upper_point[1] - lower_point[1])
        
        # Get horizontal distance (eye width)
        left_point = landmarks[0]
        right_point = landmarks[len(landmarks)//2]
        horizontal_dist = abs(left_point[0] - right_point[0])
        
        # Avoid division by zero
        if horizontal_dist == 0:
            return 0.0
            
        # Calculate EAR
        ear = vertical_dist / horizontal_dist
        
        # Apply thresholding to make it more stable
        return ear if ear < 0.5 else 0.5  # Cap the maximum EAR value

    def _detect_blink(self, avg_ear: float) -> bool:
        """Detect blink using EAR value with smoothing"""
        if avg_ear == 0.0:
            return False
            
        self.blink_frames.append(avg_ear)
        
        # Apply smoothing to EAR values
        smoothed_ear = np.mean(list(self.blink_frames))
        is_blinking = smoothed_ear < self.blink_threshold
        
        return is_blinking

    def _calculate_gaze_direction(self, eye_landmarks) -> Tuple[float, float]:
        """Calculate gaze direction with improved accuracy"""
        if eye_landmarks is None or len(eye_landmarks) < 4:
            return (0.0, 0.0)
            
        try:
            # Calculate eye center using iris landmarks
            eye_center = self._calculate_eye_center(eye_landmarks)
            if eye_center is None:
                return (0.0, 0.0)
                
            # Calculate iris center (first point is iris center)
            iris_center = eye_landmarks[0].astype(float)
            
            # Calculate gaze vector
            gaze_x = float(iris_center[0] - eye_center[0])
            gaze_y = float(iris_center[1] - eye_center[1])
            
            # Normalize gaze vector
            magnitude = math.sqrt(gaze_x * gaze_x + gaze_y * gaze_y)
            if magnitude > 0:
                gaze_x /= magnitude
                gaze_y /= magnitude
                
            return (float(gaze_x), float(gaze_y))
        except (IndexError, TypeError, ValueError):
            return (0.0, 0.0)

    def _calculate_eye_center(self, eye_landmarks: np.ndarray) -> Tuple[float, float]:
        """Calculate eye center from landmarks"""
        if eye_landmarks is None or len(eye_landmarks) < 4:
            return None
            
        try:
            # Use contour points (indices 4 onwards are contour points)
            contour_points = eye_landmarks[4:].astype(float)
            if len(contour_points) == 0:
                return None
                
            # Calculate center as mean of contour points
            center_x = float(np.mean(contour_points[:, 0]))
            center_y = float(np.mean(contour_points[:, 1]))
            
            return (center_x, center_y)
        except (IndexError, TypeError, ValueError):
            # Fallback to iris center if contour calculation fails
            try:
                iris_center = eye_landmarks[0].astype(float)
                return (float(iris_center[0]), float(iris_center[1]))
            except (IndexError, TypeError, ValueError):
                return None

    def _extract_eye_landmarks(self, face_landmarks, indices) -> np.ndarray:
        """Get eye landmarks in image coordinates"""
        if self.frame_shape is None:
            return np.zeros((1, 2))
            
        h, w = self.frame_shape
        landmarks = []
        
        try:
            # Extract iris landmarks first (first 4 points)
            for idx in indices[:4]:
                point = face_landmarks.landmark[idx]
                landmarks.append([int(point.x * w), int(point.y * h)])
                
            # Then extract eye contour landmarks
            for idx in indices[4:]:
                point = face_landmarks.landmark[idx]
                landmarks.append([int(point.x * w), int(point.y * h)])
        except (IndexError, AttributeError):
            return np.zeros((1, 2))
            
        return np.array(landmarks)

    def _draw_gaze_direction(self, frame: np.ndarray, left_eye: np.ndarray, right_eye: np.ndarray, 
                           left_gaze: Tuple[float, float], right_gaze: Tuple[float, float]) -> None:
        """Draw gaze direction with improved visibility"""
        def draw_eye_gaze(eye_center, gaze, color):
            if eye_center is None or gaze is None:
                return
                
            try:
                # Convert eye center to integer coordinates
                center_x = int(eye_center[0])
                center_y = int(eye_center[1])
                
                # Calculate end point of gaze line
                scale = 50.0  # Length of the gaze line
                end_x = int(center_x + gaze[0] * scale)
                end_y = int(center_y + gaze[1] * scale)
                
                # Draw gaze line with improved visibility
                cv2.arrowedLine(frame, (center_x, center_y), (end_x, end_y), 
                              color, 2, cv2.LINE_AA, tipLength=0.2)
            except (TypeError, ValueError):
                pass

        # Draw left eye gaze
        if left_eye.size > 0:
            left_center = self._calculate_eye_center(left_eye)
            if left_center:
                draw_eye_gaze(left_center, left_gaze, (0, 255, 0))

        # Draw right eye gaze
        if right_eye.size > 0:
            right_center = self._calculate_eye_center(right_eye)
            if right_center:
                draw_eye_gaze(right_center, right_gaze, (0, 255, 0))

    def release(self):
        """Release resources"""
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
        cv2.destroyAllWindows()

    def _calculate_pupil_size(self, eye_landmarks: np.ndarray) -> float:
        """Calculate normalized pupil size"""
        if len(eye_landmarks) < 4:
            return 0.0
            
        # Use iris landmarks to calculate pupil area
        iris_points = eye_landmarks[:4]
        hull = cv2.convexHull(iris_points.astype(np.float32))
        area = cv2.contourArea(hull)
        
        # Normalize by eye width
        eye_width = np.max(eye_landmarks[:, 0]) - np.min(eye_landmarks[:, 0])
        if eye_width == 0:
            return 0.0
            
        return area / (eye_width * eye_width)

    def _calculate_blink_rate(self, current_time: float) -> float:
        """Calculate blinks per minute"""
        if len(self.blink_history) < 2:
            return 0.0
            
        # Count blinks in the last minute
        one_minute_ago = current_time - 60
        recent_blinks = sum(1 for t in self.blink_history if t > one_minute_ago)
        
        # Calculate rate based on available time window
        time_window = min(60.0, current_time - self.blink_history[0])
        if time_window <= 0:
            return 0.0
            
        return (recent_blinks / time_window) * 60

    def _calculate_gaze_stability(self) -> float:
        """Calculate gaze stability score"""
        try:
            if len(self.gaze_history) < 2:
                return 1.0
                
            # Ensure all values in gaze_history are numeric
            valid_gaze_points = []
            for point in self.gaze_history:
                try:
                    # Convert to float if it's a tuple
                    if isinstance(point, tuple):
                        x = float(point[0])
                        y = float(point[1])
                        valid_gaze_points.append([x, y])
                    else:
                        # If it's already a numeric value
                        valid_gaze_points.append([float(point), 0.0])
                except (TypeError, IndexError, ValueError):
                    # Skip invalid points
                    continue
            
            if len(valid_gaze_points) < 2:
                return 1.0
                
            # Calculate variance of gaze positions
            gaze_points = np.array(valid_gaze_points)
            variance = np.var(gaze_points, axis=0)
            stability = 1.0 / (1.0 + float(np.mean(variance)))
            
            return min(1.0, float(stability))
        except Exception:
            # Return default value if any error occurs
            return 1.0

    def _update_ml_features(self, metrics: Dict) -> None:
        """Update feature collection for machine learning"""
        try:
            # Ensure gaze positions are stored as tuples of floats
            left_gaze = metrics.get('left_gaze', (0.0, 0.0))
            right_gaze = metrics.get('right_gaze', (0.0, 0.0))
            
            # Convert to float tuples if they aren't already
            try:
                left_gaze = (float(left_gaze[0]), float(left_gaze[1]))
                right_gaze = (float(right_gaze[0]), float(right_gaze[1]))
            except (TypeError, IndexError, ValueError):
                left_gaze = (0.0, 0.0)
                right_gaze = (0.0, 0.0)
            
            # Store average gaze position instead of tuple of tuples
            avg_gaze = (
                (left_gaze[0] + right_gaze[0]) / 2.0,
                (left_gaze[1] + right_gaze[1]) / 2.0
            )
            self.eye_metrics['gaze_positions'].append(avg_gaze)
            
            # Ensure pupil sizes are stored as floats
            left_pupil = float(metrics.get('left_pupil_size', 0.0))
            right_pupil = float(metrics.get('right_pupil_size', 0.0))
            
            self.eye_metrics['pupil_sizes'].append((
                left_pupil,
                right_pupil
            ))
            
            # Update fixations and saccades
            if len(self.eye_metrics['gaze_positions']) >= 2:
                try:
                    prev_gaze = np.array(self.eye_metrics['gaze_positions'][-2])
                    curr_gaze = np.array(self.eye_metrics['gaze_positions'][-1])
                    
                    # Detect saccade
                    velocity = np.linalg.norm(curr_gaze - prev_gaze) * self.fps
                    if velocity > self.saccade_threshold:
                        self.eye_metrics['saccades'].append({
                            'timestamp': metrics['timestamp'],
                            'velocity': float(velocity),
                            'amplitude': float(np.linalg.norm(curr_gaze - prev_gaze))
                        })
                    # Detect fixation
                    elif len(self.eye_metrics['fixations']) == 0 or \
                         metrics['timestamp'] - self.eye_metrics['fixations'][-1]['end_time'] > self.min_fixation_duration:
                        self.eye_metrics['fixations'].append({
                            'start_time': metrics['timestamp'],
                            'end_time': metrics['timestamp'],
                            'position': curr_gaze
                        })
                    else:
                        self.eye_metrics['fixations'][-1]['end_time'] = metrics['timestamp']
                except (TypeError, ValueError, IndexError):
                    # Skip this update if there's an error
                    pass
            
            # Update cognitive load metrics
            timestamp = time.time()
            
            # Calculate average pupil size from the tuple
            pupil_size_tuple = self.eye_metrics['pupil_sizes'][-1] if self.eye_metrics['pupil_sizes'] else (0.0, 0.0)
            avg_pupil_size = (float(pupil_size_tuple[0]) + float(pupil_size_tuple[1])) / 2.0
            
            # Update pupil metrics
            pupil_metrics = self.cognitive_analyzer.update_pupil_size(
                pupil_size=avg_pupil_size,
                timestamp=timestamp
            )
            
            # Update blink metrics
            is_eye_closed = self._detect_blink(metrics['avg_ear'])
            blink_metrics = self.cognitive_analyzer.update_blink(
                is_eye_closed=is_eye_closed,
                timestamp=timestamp
            )
            
            # Calculate cognitive load
            if pupil_metrics and blink_metrics:
                cognitive_load = self.cognitive_analyzer.calculate_cognitive_load(
                    pupil_metrics=pupil_metrics,
                    blink_metrics=blink_metrics
                )
                
                if cognitive_load:
                    self.cognitive_metrics = {
                        'cognitive_load_score': cognitive_load['cognitive_load_score'],
                        'load_level': cognitive_load['load_level'],
                        'pupil_load': cognitive_load['pupil_load_component'],
                        'blink_load': cognitive_load['blink_load_component']
                    }
            
            # Add cognitive metrics to ML features
            self.eye_metrics['cognitive_load_score'] = self.cognitive_metrics['cognitive_load_score']
            self.eye_metrics['pupil_load'] = self.cognitive_metrics['pupil_load']
            self.eye_metrics['blink_load'] = self.cognitive_metrics['blink_load']
        except Exception as e:
            # Log error and continue
            print(f"Error in _update_ml_features: {str(e)}")
            pass

    def _get_empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'timestamp': time.time(),
            'left_eye': np.zeros((1, 2)),
            'right_eye': np.zeros((1, 2)),
            'left_ear': 0.0,
            'right_ear': 0.0,
            'avg_ear': 0.0,
            'is_blink': False,
            'left_gaze': (0, 0),
            'right_gaze': (0, 0),
            'left_pupil_size': 0.0,
            'right_pupil_size': 0.0,
            'gaze_stability': 1.0,
            'blink_rate': 0.0,
            'cognitive_load_score': 0.0,
            'pupil_load': 0.0,
            'blink_load': 0.0
        }

    def get_ml_features(self) -> Dict:
        """Get collected features for machine learning"""
        try:
            # Calculate fixation metrics
            fixation_count = len(self.eye_metrics['fixations'])
            avg_fixation_duration = 0.0
            if self.eye_metrics['fixations']:
                durations = [f['end_time'] - f['start_time'] for f in self.eye_metrics['fixations']]
                avg_fixation_duration = float(np.mean(durations)) if durations else 0.0
            
            # Calculate saccade metrics
            saccade_count = len(self.eye_metrics['saccades'])
            avg_saccade_velocity = 0.0
            if self.eye_metrics['saccades']:
                velocities = [float(s['velocity']) for s in self.eye_metrics['saccades']]
                avg_saccade_velocity = float(np.mean(velocities)) if velocities else 0.0
            
            # Calculate blink rate
            blink_rate = 0.0
            if self.frame_timestamps and len(self.frame_timestamps) > 1:
                time_span = time.time() - self.frame_timestamps[0]
                if time_span > 0:
                    blink_rate = float(len(self.blink_history) / time_span * 60)
            
            # Calculate gaze stability
            gaze_stability = self._calculate_gaze_stability()
            
            # Calculate pupil size variability
            pupil_size_variability = 0.0
            if self.eye_metrics['pupil_sizes']:
                try:
                    # Extract left pupil sizes (first element of each tuple)
                    left_pupil_sizes = [float(p[0]) for p in self.eye_metrics['pupil_sizes']]
                    pupil_size_variability = float(np.std(left_pupil_sizes)) if left_pupil_sizes else 0.0
                except (TypeError, IndexError, ValueError):
                    pupil_size_variability = 0.0
            
            return {
                'fixation_count': int(fixation_count),
                'avg_fixation_duration': float(avg_fixation_duration),
                'saccade_count': int(saccade_count),
                'avg_saccade_velocity': float(avg_saccade_velocity),
                'blink_rate': float(blink_rate),
                'gaze_stability': float(gaze_stability),
                'pupil_size_variability': float(pupil_size_variability),
                'cognitive_load_score': float(self.eye_metrics['cognitive_load_score']),
                'pupil_load': float(self.eye_metrics['pupil_load']),
                'blink_load': float(self.eye_metrics['blink_load'])
            }
        except Exception as e:
            # Return default values if any error occurs
            return {
                'fixation_count': 0,
                'avg_fixation_duration': 0.0,
                'saccade_count': 0,
                'avg_saccade_velocity': 0.0,
                'blink_rate': 0.0,
                'gaze_stability': 1.0,
                'pupil_size_variability': 0.0,
                'cognitive_load_score': 0.0,
                'pupil_load': 0.0,
                'blink_load': 0.0
            }

    def get_cognitive_metrics(self):
        """Return current cognitive load metrics."""
        return self.cognitive_metrics 