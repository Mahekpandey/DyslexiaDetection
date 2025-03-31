import cv2
import numpy as np
from eye_tracker import EyeTracker
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
        
        # Dyslexia indicator thresholds
        self.backward_saccade_threshold = 0.4  # Proportion of backward movements
        self.fixation_duration_threshold = 0.3  # Average fixation duration (seconds)
        self.saccade_length_threshold = 0.15   # Average saccade length
        self.blink_rate_threshold = 30         # Blinks per minute
        self.gaze_stability_threshold = 0.2    # Maximum gaze variation for stability

    def analyze_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Analyze a single frame and return processed frame with metrics"""
        processed_frame, eye_data = self.eye_tracker.process_frame(frame)
        
        if 'left_pupil_relative' in eye_data:
            # Store reading data
            self.reading_data.append({
                'timestamp': time.time(),
                'left_eye': eye_data['left_pupil_relative'],
                'right_eye': eye_data['right_pupil_relative'],
                'left_gaze': eye_data['left_gaze'],
                'right_gaze': eye_data['right_gaze'],
                'blink_data': eye_data['blink_data']
            })
            
            # Analyze reading patterns
            metrics = self._analyze_reading_patterns()
            
            # Draw analysis results
            self._draw_analysis(processed_frame, metrics)
            
        return processed_frame, eye_data

    def _detect_fixations(self) -> List[Dict]:
        """Detect fixations in reading data"""
        fixations = []
        current_fixation = None
        
        for i in range(1, len(self.reading_data)):
            prev = self.reading_data[i-1]
            curr = self.reading_data[i]
            
            # Calculate movement using gaze direction
            movement = math.sqrt(
                (curr['left_gaze'][0] - prev['left_gaze'][0])**2 +
                (curr['left_gaze'][1] - prev['left_gaze'][1])**2
            )
            
            if movement < self.fixation_threshold:
                if current_fixation is None:
                    current_fixation = {
                        'start_time': prev['timestamp'],
                        'position': prev['left_gaze'],
                        'start_index': i-1
                    }
            elif current_fixation is not None:
                duration = curr['timestamp'] - current_fixation['start_time']
                if duration >= self.min_fixation_duration:
                    current_fixation['duration'] = duration
                    current_fixation['end_index'] = i
                    fixations.append(current_fixation)
                current_fixation = None
        
        return fixations

    def _detect_saccades(self) -> List[Dict]:
        """Detect saccades in reading data"""
        saccades = []
        
        for i in range(1, len(self.reading_data)):
            prev = self.reading_data[i-1]
            curr = self.reading_data[i]
            
            # Calculate movement using gaze direction
            movement = math.sqrt(
                (curr['left_gaze'][0] - prev['left_gaze'][0])**2 +
                (curr['left_gaze'][1] - prev['left_gaze'][1])**2
            )
            
            if movement > self.saccade_threshold:
                saccades.append({
                    'start_position': prev['left_gaze'],
                    'end_position': curr['left_gaze'],
                    'length': movement,
                    'direction': 'backward' if curr['left_gaze'][0] < prev['left_gaze'][0] else 'forward',
                    'timestamp': curr['timestamp']
                })
        
        return saccades

    def _calculate_backward_saccade_ratio(self, saccades: List[Dict]) -> float:
        """Calculate the ratio of backward saccades"""
        if not saccades:
            return 0
        backward_count = sum(1 for s in saccades if s['direction'] == 'backward')
        return backward_count / len(saccades)

    def _analyze_reading_patterns(self) -> Dict:
        """Analyze reading patterns for dyslexia indicators"""
        if len(self.reading_data) < 2:
            return {}

        # Calculate basic metrics
        fixations = self._detect_fixations()
        saccades = self._detect_saccades()
        
        # Calculate blink rate (blinks per minute)
        blink_count = sum(1 for d in self.reading_data[-60:] if d['blink_data']['is_blinking'])
        blink_rate = blink_count * (60 / len(self.reading_data[-60:]))
        
        # Calculate gaze stability
        gaze_stability = self._calculate_gaze_stability()
        
        # Calculate dyslexia indicators
        metrics = {
            'fixation_count': len(fixations),
            'average_fixation_duration': np.mean([f['duration'] for f in fixations]) if fixations else 0,
            'saccade_count': len(saccades),
            'backward_saccade_ratio': self._calculate_backward_saccade_ratio(saccades),
            'average_saccade_length': np.mean([s['length'] for s in saccades]) if saccades else 0,
            'blink_rate': blink_rate,
            'gaze_stability': gaze_stability
        }
        
        # Calculate dyslexia probability
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
        """Calculate dyslexia probability based on reading metrics"""
        indicators = {
            'high_backward_saccades': metrics['backward_saccade_ratio'] > self.backward_saccade_threshold,
            'long_fixations': metrics['average_fixation_duration'] > self.fixation_duration_threshold,
            'irregular_saccades': metrics['average_saccade_length'] > self.saccade_length_threshold,
            'high_blink_rate': metrics['blink_rate'] > self.blink_rate_threshold,
            'poor_gaze_stability': metrics['gaze_stability'] > self.gaze_stability_threshold
        }
        
        # Calculate overall probability
        indicator_count = sum(1 for v in indicators.values() if v)
        probability = indicator_count / len(indicators)
        
        return {
            'indicators': indicators,
            'probability': probability
        }

    def _draw_analysis(self, frame: np.ndarray, metrics: Dict):
        """Draw analysis results on frame"""
        if not metrics or 'dyslexia_indicators' not in metrics:
            return

        h = frame.shape[0]
        indicators = metrics['dyslexia_indicators']
        
        # Draw overall probability
        prob = indicators['probability']
        color = (0, 255, 0) if prob < 0.3 else (0, 165, 255) if prob < 0.7 else (0, 0, 255)
        cv2.putText(frame, f"Dyslexia Indicators: {prob*100:.1f}%", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw specific indicators
        y_pos = 60
        for name, value in indicators['indicators'].items():
            color = (0, 0, 255) if value else (0, 255, 0)
            cv2.putText(frame, f"{name}: {'Yes' if value else 'No'}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_pos += 30
        
        # Draw additional metrics
        cv2.putText(frame, f"Blink Rate: {metrics['blink_rate']:.1f}/min", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_pos += 30
        cv2.putText(frame, f"Gaze Stability: {metrics['gaze_stability']:.3f}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def release(self):
        """Release resources"""
        self.eye_tracker.release()
        self.reading_data = [] 