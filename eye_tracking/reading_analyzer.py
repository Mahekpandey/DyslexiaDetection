import cv2
import numpy as np
from eye_tracker import EyeTracker
import time
from typing import Dict, List, Tuple, Optional
import math
import re
from collections import defaultdict

class ReadingAnalyzer:
    def __init__(self):
        self.eye_tracker = EyeTracker()
        self.reading_data = []
        self.calibration_data = []
        self.is_calibrated = False
        self.test_start_time = None
        self.test_text = None
        self.test_duration = 0
        self.words_read = 0
        self.regression_count = 0
        self.last_gaze_x = None
        self.baseline_metrics = {
            'fixation_durations': [],
            'saccade_velocities': [],
            'gaze_stabilities': []
        }
        
        # Thresholds
        self.fixation_threshold = 0.1
        self.saccade_threshold = 0.3
        self.min_fixation_duration = 0.2
        
        # Enhanced dyslexia indicator thresholds
        self.backward_saccade_threshold = 0.4
        self.fixation_duration_threshold = 0.3
        self.saccade_length_threshold = 0.15
        self.blink_rate_threshold = 30
        self.gaze_stability_threshold = 0.2
        self.vertical_gaze_threshold = 0.3
        self.regression_threshold = 0.35
        self.word_span_threshold = 0.25
        
        # UI Parameters
        self.font = cv2.FONT_HERSHEY_DUPLEX
        self.text_color = (255, 255, 255)
        self.warning_color = (0, 0, 255)
        self.success_color = (0, 255, 0)
        self.info_color = (255, 165, 0)
        
        # Reading text parameters
        self.text_to_read = [
            "Please read this text carefully and naturally.",
            "The quick brown fox jumps over the lazy dog.",
            "Reading is a complex cognitive process that requires",
            "coordination between visual processing and comprehension.",
            "Take your time and try to understand each word."
        ]
        self.current_line = 0
        self.text_position = (50, 150)
        self.line_spacing = 40
        self.text_scale = 0.8
        self.text_thickness = 2
        self.background_alpha = 0.7
        
        # Initialize metrics
        self.words_read = 0
        self.fixation_count = 0
        self.reading_speed = 0
        
        # Initialize test state
        self.test_text = " ".join(self.text_to_read)  # For word counting

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Process a frame and update reading metrics"""
        if self.test_start_time is None:
            self.test_start_time = time.time()
        
        # Process frame with eye tracker
        processed_frame, eye_data = self.eye_tracker.process_frame(frame)
        
        # Draw text overlay
        self._draw_text_overlay(processed_frame)
        
        # Update metrics if we have valid gaze data
        if eye_data and 'left_gaze' in eye_data:
            self._update_reading_metrics(eye_data)
        
        # Calculate and draw metrics
        metrics = self._analyze_reading_patterns()
        self._draw_analysis(processed_frame, metrics)
        
        return processed_frame, metrics

    def _draw_text_overlay(self, frame: np.ndarray):
        """Draw reading text with improved visibility"""
        h, w = frame.shape[:2]
        
        # Create semi-transparent overlay for better text visibility
        overlay = frame.copy()
        
        # Draw dark background for text area
        text_area_height = len(self.text_to_read) * self.line_spacing + 50
        cv2.rectangle(overlay, 
                     (0, self.text_position[1] - 40),
                     (w, self.text_position[1] + text_area_height),
                     (0, 0, 0), -1)  # Black background
        
        # Add overlay to frame with lower opacity
        cv2.addWeighted(frame, 0.3, overlay, 0.7, 0, frame)
        
        # Draw text lines with better visibility
        y = self.text_position[1]
        for i, line in enumerate(self.text_to_read):
            # Get text size for centering
            (text_width, text_height), _ = cv2.getTextSize(
                line, self.font, self.text_scale, self.text_thickness)
            
            # Center text horizontally
            x = (w - text_width) // 2
            
            # Draw text with white color and black outline
            cv2.putText(frame, line, (x, y), self.font, self.text_scale,
                       (0, 0, 0), self.text_thickness + 2, cv2.LINE_AA)  # Black outline
            cv2.putText(frame, line, (x, y), self.font, self.text_scale,
                       (255, 255, 255), self.text_thickness, cv2.LINE_AA)  # White text
            
            y += self.line_spacing

    def _draw_analysis(self, frame: np.ndarray, metrics: Dict):
        """Draw analysis results with improved UI"""
        if not metrics or 'dyslexia_indicators' not in metrics:
            return

        h, w = frame.shape[:2]
        indicators = metrics['dyslexia_indicators']
        
        # Draw metrics on the right side with dark background
        metrics_width = 400
        x = w - metrics_width
        y = 40
        
        # Draw probability with color gradient
        prob = indicators['probability']
        prob_color = self._get_probability_color(prob)
        text = f"Dyslexia Probability: {prob*100:.1f}%"
        self._draw_text_with_outline(frame, text, (x, y), prob_color)
        
        # Draw severity
        y += 40
        severity_color = self._get_severity_color(indicators['severity'])
        text = f"Severity: {indicators['severity'].upper()}"
        self._draw_text_with_outline(frame, text, (x, y), severity_color)
        
        # Draw indicators with icons and clear true/false values
        y += 40
        for name, value in indicators['indicators'].items():
            color = (0, 0, 255) if value else (0, 255, 0)  # Red for issues, green for normal
            display_name = name.replace('_', ' ').title()
            status = "Detected" if value else "Normal"  # More descriptive status
            text = f"{display_name}: {status}"
            self._draw_text_with_outline(frame, text, (x, y), color)
            y += 30
        
        # Draw metrics with units
        y += 10
        metrics_color = (255, 255, 0)  # Yellow color for metrics
        self._draw_text_with_outline(frame, f"Reading Speed: {metrics['reading_speed']} WPM", 
                                   (x, y), metrics_color)
        y += 30
        self._draw_text_with_outline(frame, f"Fixations: {metrics['fixation_count']}/min", 
                                   (x, y), metrics_color)
        y += 30
        self._draw_text_with_outline(frame, f"Regressions: {metrics['regression_count']}", 
                                   (x, y), metrics_color)
        y += 30
        self._draw_text_with_outline(frame, f"Blink Rate: {metrics['blink_rate']:.1f}/min", 
                                   (x, y), metrics_color)

    def _draw_text_with_outline(self, frame: np.ndarray, text: str, position: Tuple[int, int], 
                              color: Tuple[int, int, int]):
        """Draw text with black outline for better visibility"""
        x, y = position
        # Draw black outline
        cv2.putText(frame, text, (x, y), self.font, 0.7, (0, 0, 0), 4, cv2.LINE_AA)
        # Draw colored text
        cv2.putText(frame, text, (x, y), self.font, 0.7, color, 2, cv2.LINE_AA)

    def _get_probability_color(self, probability: float) -> Tuple[int, int, int]:
        """Get color based on probability (green to red gradient)"""
        if probability < 0.3:
            return (0, 255, 0)  # Green
        elif probability < 0.6:
            return (0, 255, 255)  # Yellow
        else:
            return (0, 0, 255)  # Red

    def _get_severity_color(self, severity: str) -> Tuple[int, int, int]:
        """Get color based on severity level"""
        if severity.lower() == 'mild':
            return (0, 255, 0)  # Green
        elif severity.lower() == 'moderate':
            return (0, 255, 255)  # Yellow
        else:
            return (0, 0, 255)  # Red

    def _calculate_vertical_movement(self, eye_data: Dict) -> float:
        """Calculate vertical movement of gaze"""
        if len(self.reading_data) < 2:
            return 0
            
        prev_data = self.reading_data[-2]
        curr_data = self.reading_data[-1]
        
        # Extract numeric values from tuples and handle potential None values
        try:
            prev_left_y = float(prev_data['left_eye'][1]) if prev_data['left_eye'] is not None else 0.0
            curr_left_y = float(curr_data['left_eye'][1]) if curr_data['left_eye'] is not None else 0.0
            prev_right_y = float(prev_data['right_eye'][1]) if prev_data['right_eye'] is not None else 0.0
            curr_right_y = float(curr_data['right_eye'][1]) if curr_data['right_eye'] is not None else 0.0
            
            # Calculate vertical movement for both eyes
            left_vertical = abs(curr_left_y - prev_left_y)
            right_vertical = abs(curr_right_y - prev_right_y)
            
            return (left_vertical + right_vertical) / 2
        except (TypeError, IndexError, ValueError):
            return 0.0

    def _detect_fixations(self) -> List[Dict]:
        """Enhanced fixation detection with stability analysis"""
        fixations = []
        current_fixation = None
        
        for i in range(1, len(self.reading_data)):
            prev = self.reading_data[i-1]
            curr = self.reading_data[i]
            
            # Extract numeric values from tuples and handle potential None values
            prev_gaze = prev.get('left_gaze', (0.0, 0.0))
            curr_gaze = curr.get('left_gaze', (0.0, 0.0))
            
            # Calculate movement using both horizontal and vertical components
            try:
                prev_x = float(prev_gaze[0]) if prev_gaze else 0.0
                prev_y = float(prev_gaze[1]) if prev_gaze else 0.0
                curr_x = float(curr_gaze[0]) if curr_gaze else 0.0
                curr_y = float(curr_gaze[1]) if curr_gaze else 0.0
                
                horizontal_movement = abs(curr_x - prev_x)
                vertical_movement = abs(curr_y - prev_y)
                total_movement = math.sqrt(horizontal_movement**2 + vertical_movement**2)
            except (TypeError, IndexError, ValueError):
                total_movement = 0.0
            
            if total_movement < self.fixation_threshold:
                if current_fixation is None:
                    current_fixation = {
                        'start_time': prev['timestamp'],
                        'position': prev_gaze,
                        'start_index': i-1,
                        'stability': 1.0
                    }
                else:
                    # Update stability based on movement
                    current_fixation['stability'] *= max(0.0, 1.0 - float(total_movement))
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
            
            # Extract numeric values from tuples safely
            prev_gaze = prev.get('left_gaze', (0.0, 0.0))
            curr_gaze = curr.get('left_gaze', (0.0, 0.0))
            
            try:
                # Calculate movement components with proper float conversion
                prev_x = float(prev_gaze[0]) if prev_gaze else 0.0
                prev_y = float(prev_gaze[1]) if prev_gaze else 0.0
                curr_x = float(curr_gaze[0]) if curr_gaze else 0.0
                curr_y = float(curr_gaze[1]) if curr_gaze else 0.0
                
                horizontal_movement = curr_x - prev_x
                vertical_movement = curr_y - prev_y
                total_movement = math.sqrt(horizontal_movement**2 + vertical_movement**2)
            except (TypeError, IndexError, ValueError):
                continue
            
            if total_movement > self.saccade_threshold:
                # Determine saccade direction and type
                direction = 'backward' if horizontal_movement < 0 else 'forward'
                saccade_type = 'regression' if direction == 'backward' and abs(float(horizontal_movement)) > self.regression_threshold else 'normal'
                
                saccades.append({
                    'start_position': prev_gaze,
                    'end_position': curr_gaze,
                    'length': float(total_movement),
                    'direction': direction,
                    'type': saccade_type,
                    'horizontal_movement': float(horizontal_movement),
                    'vertical_movement': float(vertical_movement),
                    'timestamp': curr['timestamp']
                })
        
        return saccades

    def _update_reading_metrics(self, eye_data: Dict):
        """Update reading metrics based on eye tracking data"""
        # Store current timestamp
        current_time = time.time()
        
        # Get gaze data and ensure they are tuples of floats
        left_gaze = tuple(map(float, eye_data.get('left_gaze', (0.0, 0.0))))
        right_gaze = tuple(map(float, eye_data.get('right_gaze', (0.0, 0.0))))
        
        # Calculate average gaze position
        avg_gaze_x = (left_gaze[0] + right_gaze[0]) / 2.0
        avg_gaze_y = (left_gaze[1] + right_gaze[1]) / 2.0
        
        # Calculate vertical movement safely
        vertical_movement = 0.0
        if self.last_gaze_x is not None:
            vertical_movement = abs(float(avg_gaze_y))
        
        # Safely handle pupil relative positions
        left_pupil_relative = eye_data.get('left_pupil_relative', (0.0, 0.0))
        right_pupil_relative = eye_data.get('right_pupil_relative', (0.0, 0.0))
        
        # Convert to tuples of floats if they aren't already
        try:
            if isinstance(left_pupil_relative, tuple):
                left_pupil_relative = tuple(map(float, left_pupil_relative))
            else:
                left_pupil_relative = (float(left_pupil_relative), 0.0)
        except (TypeError, ValueError):
            left_pupil_relative = (0.0, 0.0)
            
        try:
            if isinstance(right_pupil_relative, tuple):
                right_pupil_relative = tuple(map(float, right_pupil_relative))
            else:
                right_pupil_relative = (float(right_pupil_relative), 0.0)
        except (TypeError, ValueError):
            right_pupil_relative = (0.0, 0.0)
        
        # Store reading data with proper numeric types
        self.reading_data.append({
            'timestamp': current_time,
            'left_eye': left_pupil_relative,
            'right_eye': right_pupil_relative,
            'left_gaze': left_gaze,
            'right_gaze': right_gaze,
            'blink_data': eye_data.get('blink_data', {'is_blinking': False}),
            'vertical_movement': float(vertical_movement)
        })
        
        # Update last gaze position
        self.last_gaze_x = float(avg_gaze_x)
        
        # Limit data storage to prevent memory issues
        if len(self.reading_data) > 300:  # Store last 10 seconds at 30fps
            self.reading_data.pop(0)
        
        # Update fixation count if gaze is stable
        if self.last_gaze_x is not None:
            try:
                gaze_movement = abs(float(avg_gaze_x - self.last_gaze_x))
                if gaze_movement < self.fixation_threshold:
                    self.fixation_count += 1
                
                # Update regression count
                if gaze_movement > self.saccade_threshold and avg_gaze_x < self.last_gaze_x:
                    self.regression_count += 1
            except (TypeError, ValueError):
                pass

    def _calculate_readability_score(self, text: str) -> float:
        """Calculate Flesch-Kincaid readability score"""
        try:
            # Count sentences (approximate)
            sentences = len(re.split(r'[.!?]+', text))
            if sentences == 0:
                return 0.0
                
            # Count words
            words = len(text.split())
            if words == 0:
                return 0.0
                
            # Count syllables (approximate)
            syllables = 0
            for word in text.split():
                # Simple syllable counting rule
                word = word.lower()
                count = 0
                vowels = "aeiouy"
                if word[0] in vowels:
                    count += 1
                for index in range(1, len(word)):
                    if word[index] in vowels and word[index-1] not in vowels:
                        count += 1
                if word.endswith('e'):
                    count -= 1
                if count == 0:
                    count = 1
                syllables += count
            
            # Calculate Flesch-Kincaid score
            # 0.39 * (total words / total sentences) + 11.8 * (total syllables / total words) - 15.59
            score = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
            
            # Normalize score to 0-1 range (higher is easier to read)
            normalized_score = min(max((score + 100) / 200, 0), 1)
            return normalized_score
            
        except Exception as e:
            print(f"Error calculating readability: {str(e)}")
            return 0.5  # Return middle score on error
            
    def _get_text_complexity_factor(self, text: str) -> float:
        """Get complexity factor based on readability score"""
        readability = self._calculate_readability_score(text)
        # Convert readability to complexity (1 - readability)
        # Higher complexity factor means text is harder to read
        return 1.0 - readability

    def _update_baseline_metrics(self, metrics: Dict):
        """Update baseline metrics with current measurements"""
        try:
            if 'fixation_duration' in metrics:
                self.baseline_metrics['fixation_durations'].append(metrics['fixation_duration'])
            if 'saccade_velocity' in metrics:
                self.baseline_metrics['saccade_velocities'].append(metrics['saccade_velocity'])
            if 'gaze_stability' in metrics:
                self.baseline_metrics['gaze_stabilities'].append(metrics['gaze_stability'])
                
            # Keep only last 1000 measurements to maintain recent baseline
            max_samples = 1000
            for key in self.baseline_metrics:
                if len(self.baseline_metrics[key]) > max_samples:
                    self.baseline_metrics[key] = self.baseline_metrics[key][-max_samples:]
        except Exception as e:
            print(f"Error updating baseline metrics: {str(e)}")

    def _get_percentile_threshold(self, metric_name: str, percentile: float = 90) -> float:
        """Calculate threshold based on baseline percentile"""
        try:
            if metric_name not in self.baseline_metrics or not self.baseline_metrics[metric_name]:
                return self._get_default_threshold(metric_name)
                
            values = sorted(self.baseline_metrics[metric_name])
            index = int(len(values) * percentile / 100)
            return values[min(index, len(values) - 1)]
        except Exception as e:
            print(f"Error calculating percentile threshold: {str(e)}")
            return self._get_default_threshold(metric_name)

    def _get_default_threshold(self, metric_name: str) -> float:
        """Get default threshold for a metric"""
        thresholds = {
            'fixation_durations': 0.3,  # 300ms
            'saccade_velocities': 100,  # pixels/second
            'gaze_stabilities': 0.7     # 0-1 scale
        }
        return thresholds.get(metric_name, 0.0)

    def _normalize_saccade_velocity(self, velocity: float) -> float:
        """Normalize saccade velocity based on individual baseline"""
        try:
            if not self.baseline_metrics['saccade_velocities']:
                return velocity
                
            # Calculate mean and std of baseline velocities
            baseline_velocities = np.array(self.baseline_metrics['saccade_velocities'])
            mean_vel = np.mean(baseline_velocities)
            std_vel = np.std(baseline_velocities)
            
            if std_vel == 0:
                return velocity
                
            # Normalize using z-score
            normalized_vel = (velocity - mean_vel) / std_vel
            return normalized_vel
            
        except Exception as e:
            print(f"Error normalizing saccade velocity: {str(e)}")
            return velocity

    def _analyze_reading_patterns(self) -> Dict:
        """Enhanced reading pattern analysis with ML-ready features"""
        if len(self.reading_data) < 2:
            return self._get_default_metrics()

        # Get ML features from eye tracker
        ml_features = self.eye_tracker.get_ml_features()
        
        # Calculate reading speed (words per minute) with complexity adjustment
        if self.test_start_time and self.test_text:
            elapsed_time = max(time.time() - self.test_start_time, 1)
            self.test_duration = elapsed_time
            self.words_read = len(self.test_text.split())
            
            # Adjust reading speed based on text complexity
            complexity_factor = self._get_text_complexity_factor(self.test_text)
            raw_reading_speed = (self.words_read / elapsed_time) * 60
            reading_speed = int(raw_reading_speed * (1.0 - complexity_factor * 0.5))
        else:
            reading_speed = 0

        # Calculate fixation metrics using percentile-based thresholds
        fixation_duration = ml_features.get('avg_fixation_duration', 0)
        fixation_threshold = self._get_percentile_threshold('fixation_durations')
        long_fixations = 1 if fixation_duration > fixation_threshold else 0
        
        # Update baseline metrics
        self._update_baseline_metrics({
            'fixation_duration': fixation_duration,
            'saccade_velocity': ml_features.get('saccade_velocity', 0),
            'gaze_stability': ml_features.get('gaze_stability', 0)
        })

        # Calculate saccade metrics with normalization
        saccade_velocity = ml_features.get('saccade_velocity', 0)
        normalized_velocity = self._normalize_saccade_velocity(saccade_velocity)
        irregular_saccades = 1 if abs(normalized_velocity) > 2.0 else 0  # More than 2 standard deviations

        # Calculate other metrics
        blink_rate = ml_features.get('blink_rate', 0)
        gaze_stability = ml_features.get('gaze_stability', 0)
        pupil_variability = ml_features.get('pupil_variability', 0)

        # Calculate dyslexia probability with adjusted weights
        indicators = {
            'backward_saccades': self.regression_count > 0,
            'long_fixations': long_fixations > 0,
            'irregular_saccades': irregular_saccades > 0,
            'high_blink_rate': blink_rate > 0.3,
            'low_gaze_stability': gaze_stability < 0.7,
            'high_pupil_variability': pupil_variability > 0.3
        }

        # Weight the indicators
        weights = {
            'backward_saccades': 0.25,
            'long_fixations': 0.2,
            'irregular_saccades': 0.2,
            'high_blink_rate': 0.1,
            'low_gaze_stability': 0.15,
            'high_pupil_variability': 0.1
        }

        # Calculate probability score
        probability_score = sum(weights[k] * float(v) for k, v in indicators.items())
        dyslexia_probability = min(probability_score * 100, 100)

        # Determine severity
        severity = "Mild"
        if dyslexia_probability > 70:
            severity = "Severe"
        elif dyslexia_probability > 40:
            severity = "Moderate"

        return {
            'fixation_count': self.fixation_count,
            'regression_count': self.regression_count,
            'reading_speed': reading_speed,
            'blink_rate': blink_rate,
            'dyslexia_indicators': {
                'probability': dyslexia_probability / 100.0,  # Convert to 0-1 range
                'severity': severity,
                'indicators': indicators
            },
            'ml_features': {
                'fixation_duration': fixation_duration,
                'saccade_velocity': normalized_velocity,
                'gaze_stability': gaze_stability,
                'pupil_variability': pupil_variability,
                'text_complexity': complexity_factor if self.test_text else 0.0
            }
        }

    def _get_default_metrics(self) -> Dict:
        """Return default metrics structure"""
        return {
            'fixation_count': 0,
            'regression_count': 0,
            'reading_speed': 0,
            'blink_rate': 0.0,
            'dyslexia_indicators': {
                'probability': 0.0,
                'severity': 'mild',
                'indicators': {
                    'backward_saccades': False,
                    'long_fixations': False,
                    'irregular_saccades': False,
                    'high_blink_rate': False,
                    'low_gaze_stability': False,
                    'high_pupil_variability': False
                }
            },
            'ml_features': {
                'fixation_duration': 0.0,
                'saccade_velocity': 0.0,
                'gaze_stability': 1.0,
                'pupil_variability': 0.0,
                'text_complexity': 0.0
            }
        }

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