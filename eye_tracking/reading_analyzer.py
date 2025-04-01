import cv2
import numpy as np
from .eye_tracker import EyeTracker
import time
from typing import Dict, List, Tuple
import math

class ReadingAnalyzer:
    def __init__(self):
        self.eye_tracker = EyeTracker()
        self.reading_data = []
        self.fixation_threshold = 0.1  # Maximum movement to be considered a fixation
        self.saccade_threshold = 0.3   # Minimum movement to be considered a saccade
        self.min_fixation_duration = 0.2  # Minimum time for a fixation
        
        # Enhanced dyslexia indicator thresholds
        self.backward_saccade_threshold = 0.4  # Proportion of backward movements
        self.fixation_duration_threshold = 0.3  # Average fixation duration (seconds)
        self.saccade_length_threshold = 0.15   # Average saccade length
        self.blink_rate_threshold = 30         # Blinks per minute
        self.gaze_stability_threshold = 0.2    # Maximum gaze variation for stability
        self.vertical_gaze_threshold = 0.3     # Maximum vertical gaze movement
        self.regression_threshold = 0.35       # Threshold for regression detection
        self.word_span_threshold = 0.25        # Maximum word span for normal reading
        
        # Calibration data
        self.calibration_data = []
        self.is_calibrated = False
        self.calibration_points = []
        
        # Reading test data
        self.test_start_time = None
        self.test_duration = 0
        self.words_read = 0
        self.test_text = None

    def analyze_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Analyze a single frame and return processed frame with metrics"""
        processed_frame, eye_data = self.eye_tracker.process_frame(frame)
        
        if 'left_pupil_relative' in eye_data:
            # Store reading data with enhanced metrics
            self.reading_data.append({
                'timestamp': time.time(),
                'left_eye': eye_data['left_pupil_relative'],
                'right_eye': eye_data['right_pupil_relative'],
                'left_gaze': eye_data['left_gaze'],
                'right_gaze': eye_data['right_gaze'],
                'blink_data': eye_data['blink_data'],
                'gaze_stability': self._calculate_gaze_stability(),
                'vertical_movement': self._calculate_vertical_movement(eye_data)
            })
            
            # Analyze reading patterns with enhanced metrics
            metrics = self._analyze_reading_patterns()
            
            # Draw analysis results
            self._draw_analysis(processed_frame, metrics)
            
        return processed_frame, eye_data

    def _calculate_vertical_movement(self, eye_data: Dict) -> float:
        """Calculate vertical movement of gaze"""
        if len(self.reading_data) < 2:
            return 0
            
        prev_data = self.reading_data[-2]
        curr_data = self.reading_data[-1]
        
        # Calculate vertical movement for both eyes
        left_vertical = abs(curr_data['left_eye'][1] - prev_data['left_eye'][1])
        right_vertical = abs(curr_data['right_eye'][1] - prev_data['right_eye'][1])
        
        return (left_vertical + right_vertical) / 2

    def _detect_fixations(self) -> List[Dict]:
        """Enhanced fixation detection with stability analysis"""
        fixations = []
        current_fixation = None
        
        for i in range(1, len(self.reading_data)):
            prev = self.reading_data[i-1]
            curr = self.reading_data[i]
            
            # Calculate movement using both horizontal and vertical components
            horizontal_movement = abs(curr['left_gaze'][0] - prev['left_gaze'][0])
            vertical_movement = abs(curr['left_gaze'][1] - prev['left_gaze'][1])
            total_movement = math.sqrt(horizontal_movement**2 + vertical_movement**2)
            
            if total_movement < self.fixation_threshold:
                if current_fixation is None:
                    current_fixation = {
                        'start_time': prev['timestamp'],
                        'position': prev['left_gaze'],
                        'start_index': i-1,
                        'stability': 1.0
                    }
                else:
                    # Update stability based on movement
                    current_fixation['stability'] *= (1 - total_movement)
            elif current_fixation is not None:
                duration = curr['timestamp'] - current_fixation['start_time']
                if duration >= self.min_fixation_duration:
                    current_fixation['duration'] = duration
                    current_fixation['end_index'] = i
                    current_fixation['average_stability'] = current_fixation['stability'] / (i - current_fixation['start_index'])
                    fixations.append(current_fixation)
                current_fixation = None
        
        return fixations

    def _detect_saccades(self) -> List[Dict]:
        """Enhanced saccade detection with direction analysis"""
        saccades = []
        
        for i in range(1, len(self.reading_data)):
            prev = self.reading_data[i-1]
            curr = self.reading_data[i]
            
            # Calculate movement components
            horizontal_movement = curr['left_gaze'][0] - prev['left_gaze'][0]
            vertical_movement = curr['left_gaze'][1] - prev['left_gaze'][1]
            total_movement = math.sqrt(horizontal_movement**2 + vertical_movement**2)
            
            if total_movement > self.saccade_threshold:
                # Determine saccade direction and type
                direction = 'backward' if horizontal_movement < 0 else 'forward'
                saccade_type = 'regression' if direction == 'backward' and abs(horizontal_movement) > self.regression_threshold else 'normal'
                
                saccades.append({
                    'start_position': prev['left_gaze'],
                    'end_position': curr['left_gaze'],
                    'length': total_movement,
                    'direction': direction,
                    'type': saccade_type,
                    'horizontal_movement': horizontal_movement,
                    'vertical_movement': vertical_movement,
                    'timestamp': curr['timestamp']
                })
        
        return saccades

    def _analyze_reading_patterns(self) -> Dict:
        """Enhanced reading pattern analysis with more metrics"""
        if len(self.reading_data) < 2:
            return {}

        # Calculate basic metrics
        fixations = self._detect_fixations()
        saccades = self._detect_saccades()
        
        # Calculate advanced metrics
        blink_count = sum(1 for d in self.reading_data[-60:] if d['blink_data']['is_blinking'])
        blink_rate = blink_count * (60 / len(self.reading_data[-60:]))
        
        # Calculate reading speed (words per minute)
        if self.test_start_time and self.test_text:
            elapsed_time = time.time() - self.test_start_time
            self.test_duration = elapsed_time
            self.words_read = len(self.test_text.split())
            reading_speed = (self.words_read / elapsed_time) * 60
        else:
            reading_speed = 0
        
        # Calculate gaze stability and vertical movement
        gaze_stability = self._calculate_gaze_stability()
        vertical_movement = np.mean([d['vertical_movement'] for d in self.reading_data[-30:]])
        
        # Calculate saccade metrics
        backward_saccades = [s for s in saccades if s['direction'] == 'backward']
        regressions = [s for s in saccades if s['type'] == 'regression']
        
        metrics = {
            'fixation_count': len(fixations),
            'average_fixation_duration': np.mean([f['duration'] for f in fixations]) if fixations else 0,
            'average_fixation_stability': np.mean([f['average_stability'] for f in fixations]) if fixations else 0,
            'saccade_count': len(saccades),
            'backward_saccade_ratio': len(backward_saccades) / len(saccades) if saccades else 0,
            'regression_count': len(regressions),
            'average_saccade_length': np.mean([s['length'] for s in saccades]) if saccades else 0,
            'blink_rate': blink_rate,
            'gaze_stability': gaze_stability,
            'vertical_movement': vertical_movement,
            'reading_speed': int(reading_speed)
        }
        
        # Calculate dyslexia indicators with enhanced analysis
        metrics['dyslexia_indicators'] = self._calculate_dyslexia_indicators(metrics)
        
        return metrics

    def _calculate_gaze_stability(self) -> float:
        """Calculate gaze stability from recent gaze directions"""
        if len(self.reading_data) < 2:
            return 1.0
            
        recent_data = self.reading_data[-30:]  # Look at last 30 frames
        left_gaze_var = np.var([d['left_gaze'][0] for d in recent_data])
        right_gaze_var = np.var([d['right_gaze'][0] for d in recent_data])
        
        # Return average variance (lower is more stable)
        return (left_gaze_var + right_gaze_var) / 2

    def _calculate_dyslexia_indicators(self, metrics: Dict) -> Dict:
        """Enhanced dyslexia indicator calculation"""
        indicators = {
            'high_backward_saccades': bool(metrics['backward_saccade_ratio'] > self.backward_saccade_threshold),
            'long_fixations': bool(metrics['average_fixation_duration'] > self.fixation_duration_threshold),
            'irregular_saccades': bool(metrics['average_saccade_length'] > self.saccade_length_threshold),
            'high_blink_rate': bool(metrics['blink_rate'] > self.blink_rate_threshold),
            'poor_gaze_stability': bool(metrics['gaze_stability'] > self.gaze_stability_threshold),
            'excessive_vertical_movement': bool(metrics['vertical_movement'] > self.vertical_gaze_threshold),
            'frequent_regressions': bool(metrics['regression_count'] > 5),  # More than 5 regressions per minute
            'slow_reading_speed': bool(metrics['reading_speed'] < 100)  # Less than 100 words per minute
        }
        
        # Calculate weighted probability based on indicator importance
        weights = {
            'high_backward_saccades': 0.2,
            'long_fixations': 0.15,
            'irregular_saccades': 0.15,
            'high_blink_rate': 0.1,
            'poor_gaze_stability': 0.1,
            'excessive_vertical_movement': 0.1,
            'frequent_regressions': 0.1,
            'slow_reading_speed': 0.1
        }
        
        weighted_sum = sum(weights[ind] for ind, val in indicators.items() if val)
        probability = weighted_sum / sum(weights.values())
        
        return {
            'indicators': indicators,
            'probability': probability,
            'severity': 'mild' if probability < 0.4 else 'moderate' if probability < 0.7 else 'severe'
        }

    def _draw_analysis(self, frame: np.ndarray, metrics: Dict):
        """Enhanced visualization of analysis results"""
        if not metrics or 'dyslexia_indicators' not in metrics:
            return

        h = frame.shape[0]
        indicators = metrics['dyslexia_indicators']
        
        # Draw overall probability with color coding
        prob = indicators['probability']
        color = (0, 255, 0) if prob < 0.3 else (0, 165, 255) if prob < 0.7 else (0, 0, 255)
        cv2.putText(frame, f"Dyslexia Probability: {prob*100:.1f}%", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw severity level
        severity_color = (0, 255, 0) if indicators['severity'] == 'mild' else (0, 165, 255) if indicators['severity'] == 'moderate' else (0, 0, 255)
        cv2.putText(frame, f"Severity: {indicators['severity'].upper()}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, severity_color, 2)
        
        # Draw specific indicators
        y_pos = 90
        for name, value in indicators['indicators'].items():
            color = (0, 0, 255) if value else (0, 255, 0)
            display_name = name.replace('_', ' ').title()
            cv2.putText(frame, f"{display_name}: {'Yes' if value else 'No'}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_pos += 30
        
        # Draw additional metrics
        cv2.putText(frame, f"Reading Speed: {metrics['reading_speed']} wpm", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_pos += 30
        cv2.putText(frame, f"Fixations: {metrics['fixation_count']}/min", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_pos += 30
        cv2.putText(frame, f"Regressions: {metrics['regression_count']}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def start_calibration(self):
        """Start calibration process"""
        self.calibration_data = []
        self.is_calibrated = False
        self.calibration_points = [
            (0.2, 0.2), (0.5, 0.2), (0.8, 0.2),
            (0.2, 0.5), (0.5, 0.5), (0.8, 0.5),
            (0.2, 0.8), (0.5, 0.8), (0.8, 0.8)
        ]

    def start_reading_test(self, text: str):
        """Start a reading test with given text"""
        self.test_start_time = time.time()
        self.test_text = text
        self.reading_data = []  # Clear previous data
        self.words_read = 0

    def release(self):
        """Release resources"""
        self.eye_tracker.release()
        self.reading_data = []
        self.calibration_data = []
        self.test_text = None 