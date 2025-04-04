import cv2
import numpy as np
import time
from .eye_tracker import EyeTracker
from typing import Dict, List, Tuple, Optional
import math
import re
from collections import defaultdict
from .cognitive_load_analyzer import CognitiveLoadAnalyzer

class ReadingAnalyzer:
    def __init__(self):
        """Initialize reading analyzer"""
        # Initialize eye tracker
        self.eye_tracker = EyeTracker()
        
        # Initialize test state
        self.test_start_time = None
        self.is_paused = False
        self.pause_start_time = None
        self.total_pause_time = 0
        
        # Initialize metrics
        self.fixation_count = 0
        self.regression_count = 0
        self.words_read = 0
        self.reading_speed = 0
        
        # Initialize eye metrics
        self.eye_metrics = {
            'fixations': [],
            'saccades': [],
            'blinks': [],
            'gaze_positions': [],
            'pupil_sizes': []
        }
        
        # Add smoothing parameters
        self.metric_history = {
            'dyslexia_probability': [],
            'cognitive_load': [],
            'fixation_stability': [],
            'reading_linearity': []
        }
        self.smoothing_window = 30  # 1 second at 30fps
        self.min_active_reading_time = 2.0  # Require 2 seconds of active reading
        self.active_reading_start = None
        self.movement_threshold = 0.05  # Minimum movement to consider as intentional
        self.last_probability = 0.0
        self.probability_change_rate = 0.1  # Maximum change per frame
        
        # Add cognitive load display colors
        self.load_colors = {
            'Low': (0, 255, 0),     # Green
            'Medium': (0, 255, 255), # Yellow
            'High': (0, 0, 255)      # Red
        }
        
        # Initialize test parameters
        self.fixation_threshold = 0.1
        self.saccade_threshold = 0.2
        self.last_gaze_x = None
        self.last_gaze_y = None
        self.reading_data = []
        
        # Initialize other attributes
        self.calibration_data = []
        self.is_calibrated = False
        self.test_text = None
        self.test_duration = 0
        self.current_line = 0
        self.text_position = (50, 150)
        self.line_spacing = 40
        self.text_scale = 0.8
        self.text_thickness = 2
        self.background_alpha = 0.7
        self.baseline_metrics = {
            'fixation_durations': [],
            'saccade_velocities': [],
            'gaze_stabilities': []
        }
        
        # Initialize thresholds
        self.min_fixation_duration = 0.2
        self.backward_saccade_threshold = 0.4
        self.fixation_duration_threshold = 0.3
        self.saccade_length_threshold = 0.15
        self.blink_rate_threshold = 30
        self.gaze_stability_threshold = 0.2
        self.vertical_gaze_threshold = 0.3
        self.regression_threshold = 0.35
        self.word_span_threshold = 0.25
        
        # Initialize display settings
        self.font = cv2.FONT_HERSHEY_DUPLEX
        self.text_color = (255, 255, 255)
        self.warning_color = (0, 0, 255)
        self.success_color = (0, 255, 0)
        self.info_color = (255, 165, 0)
        
        # Initialize text content
        self.text_to_read = [
            "Please read this text carefully and naturally.",
            "The quick brown fox jumps over the lazy dog.",
            "Reading is a complex cognitive process that requires",
            "coordination between visual processing and comprehension.",
            "Take your time and try to understand each word."
        ]
        
        # Initialize regression analysis parameters
        self.regression_thresholds = {
            'short': 0.15,   # 15% of screen width
            'medium': 0.3,   # 30% of screen width
            'long': 0.45     # 45% of screen width
        }
        self.regression_patterns = {
            'short': 0,  # Within-word regressions
            'medium': 0,  # Previous word regressions
            'long': 0,   # Multiple word regressions
            'vertical': 0 # Line change regressions
        }
        self.last_regression_time = None
        self.regression_frequency = []
        
        # Initialize enhanced detection metrics
        self.fixation_stability_history = []
        self.saccade_times = []
        self.reading_linearity_scores = []
        self.reread_positions = defaultdict(int)
        
        # Initialize stability thresholds
        self.fixation_stability_threshold = 0.15
        self.linearity_threshold = 0.25
        self.saccade_time_threshold = 0.1
        
        # Initialize regression timing
        self.min_regression_duration = 0.1
        self.regression_start_time = None
        self.potential_regression = None

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
        """Draw analysis results with enhanced metrics"""
        # Set up display parameters
        x, y = 10, 30
        metrics_color = (255, 255, 255)
        
        # Draw main metrics
        self._draw_text_with_outline(frame, f"Reading Speed: {metrics['reading_speed']} WPM", 
                                   (x, y), metrics_color)
        y += 30
        
        # Draw dyslexia probability with color based on severity
        prob = metrics['dyslexia_indicators']['probability'] * 100
        severity = metrics['dyslexia_indicators']['severity']
        severity_color = self._get_severity_color(severity)
        
        self._draw_text_with_outline(frame, f"Dyslexia Probability: {prob:.1f}%", 
                                   (x, y), severity_color)
        y += 30
        self._draw_text_with_outline(frame, f"Severity: {severity}", 
                                   (x, y), severity_color)
        y += 40
        
        # Draw enhanced metrics section
        enhanced = metrics.get('enhanced_metrics', {})
        self._draw_text_with_outline(frame, "Enhanced Metrics:", (x, y), metrics_color)
        y += 25
        
        # Draw stability metrics with color coding
        stability_color = self._get_metric_color(enhanced.get('fixation_stability', 0))
        self._draw_text_with_outline(frame, 
            f"Fixation Stability: {enhanced.get('fixation_stability', 0):.2f}", 
            (x, y), stability_color)
        y += 25
        
        linearity_color = self._get_metric_color(enhanced.get('reading_linearity', 0))
        self._draw_text_with_outline(frame, 
            f"Reading Linearity: {enhanced.get('reading_linearity', 0):.2f}", 
            (x, y), linearity_color)
        y += 25
        
        saccade_color = self._get_metric_color(1.0 - enhanced.get('avg_saccade_time', 0) / 0.1)
        self._draw_text_with_outline(frame, 
            f"Avg Saccade Time: {enhanced.get('avg_saccade_time', 0)*1000:.0f}ms", 
            (x, y), saccade_color)
        y += 25
        
        reread_color = self._get_metric_color(1.0 - enhanced.get('reread_score', 0))
        self._draw_text_with_outline(frame, 
            f"Reread Score: {enhanced.get('reread_score', 0):.2f}", 
            (x, y), reread_color)
        y += 40
        
        # Draw regression analysis
        if 'regression_analysis' in metrics and metrics['regression_analysis']:
            reg_analysis = metrics['regression_analysis']
            patterns = reg_analysis.get('regression_patterns', {})
            
            regression_color = self._get_regression_color(reg_analysis.get('regression_severity', 0))
            self._draw_text_with_outline(frame, "Regression Analysis:", (x, y), regression_color)
            y += 25
            
            # Draw regression counts with severity-based colors
            counts = [
                ("Short", patterns.get('short', 0)),
                ("Medium", patterns.get('medium', 0)),
                ("Long", patterns.get('long', 0)),
                ("Line Changes", patterns.get('vertical', 0))
            ]
            
            for label, count in counts:
                color = self._get_count_color(count, label)
                self._draw_text_with_outline(frame, f"  {label}: {count}", (x, y), color)
                y += 25
            
            # Draw regression frequency
            freq = reg_analysis.get('avg_regression_frequency', 0)
            if freq != float('inf'):
                self._draw_text_with_outline(frame, 
                    f"Avg Time Between Regressions: {freq:.1f}s", 
                    (x, y), regression_color)
            y += 40
        
        # Draw cognitive load section
        cognitive = metrics['cognitive_metrics']
        load_level = (
            'High' if cognitive['load_score'] > 0.7 else
            'Medium' if cognitive['load_score'] > 0.3 else
            'Low'
        )
        load_color = self.load_colors[load_level]
        
        self._draw_text_with_outline(frame, "Cognitive Metrics:", (x, y), metrics_color)
        y += 25
        self._draw_text_with_outline(frame, 
            f"Cognitive Load: {cognitive['load_score']:.2f}", 
            (x, y), load_color)
        y += 25
        self._draw_text_with_outline(frame, 
            f"Pupil Load: {cognitive['pupil_load']:.2f}", 
            (x, y), load_color)
        y += 25
        self._draw_text_with_outline(frame, 
            f"Blink Load: {cognitive['blink_load']:.2f}", 
            (x, y), load_color)
        
        # Draw cognitive load bar
        self._draw_load_bar(frame, x, y + 20, cognitive['load_score'], load_color)

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
        """Get color based on enhanced severity levels"""
        colors = {
            'Mild': (0, 255, 0),            # Green
            'Borderline': (0, 255, 128),    # Light Green
            'Borderline-to-Moderate': (0, 255, 255),  # Cyan
            'Moderate': (0, 128, 255),      # Light Blue
            'Moderate-to-Severe': (0, 0, 255),  # Blue
            'Severe': (0, 0, 128)           # Dark Blue
        }
        return colors.get(severity, (255, 255, 255))

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

    def _smooth_metric(self, metric_name: str, new_value: float) -> float:
        """Apply temporal smoothing to metrics"""
        history = self.metric_history[metric_name]
        history.append(new_value)
        
        # Keep only recent history
        if len(history) > self.smoothing_window:
            history.pop(0)
            
        # Apply exponential moving average
        alpha = 0.1  # Smoothing factor
        smoothed = history[0]
        for value in history[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed
            
        return smoothed

    def _is_active_reading(self, current_time: float) -> bool:
        """Determine if user is actively reading based on gaze patterns"""
        if len(self.eye_metrics['gaze_positions']) < 2:
            return False
            
        # Check for consistent horizontal movement
        positions = np.array(self.eye_metrics['gaze_positions'][-10:])
        if len(positions) < 2:
            return False
            
        # Calculate average horizontal movement
        x_positions = positions[:, 0]
        avg_movement = np.mean(np.abs(np.diff(x_positions)))
        
        # If movement is too small, not considered active reading
        if avg_movement < self.movement_threshold:
            self.active_reading_start = None
            return False
            
        # Start or continue active reading timer
        if self.active_reading_start is None:
            self.active_reading_start = current_time
            
        # Check if we've been actively reading long enough
        return (current_time - self.active_reading_start) >= self.min_active_reading_time

    def _analyze_reading_patterns(self) -> Dict:
        """Analyze reading patterns with enhanced regression analysis"""
        current_time = time.time()
        
        # Only analyze if actively reading
        is_active = self._is_active_reading(current_time)
        
        # Get ML features and cognitive metrics
        ml_features = self.eye_tracker.get_ml_features()
        cognitive_metrics = self.eye_tracker.get_cognitive_metrics()
        
        # Calculate reading speed
        if self.test_start_time:
            elapsed_time = current_time - self.test_start_time
            reading_speed = int((self.words_read / elapsed_time) * 60) if elapsed_time > 0 else 0
        else:
            reading_speed = 0
            
        # Calculate enhanced metrics with smoothing
        fixation_stability = self._smooth_metric('fixation_stability', 
                                               self._calculate_fixation_stability())
        reading_linearity = self._smooth_metric('reading_linearity', 
                                              self._calculate_reading_linearity())
        avg_saccade_time = np.mean(self.saccade_times) if self.saccade_times else 0
        reread_score = self._calculate_reread_score()
        
        # Get cognitive load components with smoothing
        cognitive_load = self._smooth_metric('cognitive_load', 
                                           min(0.8, cognitive_metrics.get('cognitive_load_score', 0.0)))
        pupil_load = min(0.7, cognitive_metrics.get('pupil_load', 0.0))
        blink_load = min(0.6, cognitive_metrics.get('blink_load', 0.0))
        
        # Get regression analysis only if actively reading
        regression_analysis = {}
        if is_active and len(self.eye_metrics['gaze_positions']) >= 2:
            current_gaze = self.eye_metrics['gaze_positions'][-1]
            previous_gaze = self.eye_metrics['gaze_positions'][-2]
            regression_analysis = self._analyze_regression_patterns(
                current_gaze, previous_gaze, current_time
            )
        
        # Calculate probability only if actively reading
        if is_active:
            # Enhanced indicators with smoothed metrics
            indicators = {
                'backward_saccades': regression_analysis.get('total_regressions', 0) > 0,
                'long_fixations': len([f for f in self.eye_metrics.get('fixations', [])
                                     if f.get('duration', 0) > self.fixation_duration_threshold]) > 3,
                'irregular_saccades': len([s for s in self.eye_metrics.get('saccades', [])
                                         if s.get('length', 0) > self.saccade_length_threshold]) > 2,
                'high_cognitive_load': cognitive_load > 0.5,
                'high_pupil_load': pupil_load > 0.4,
                'high_blink_load': blink_load > 0.4,
                'frequent_regressions': regression_analysis.get('avg_regression_frequency', float('inf')) < 2.0,
                'long_regressions': regression_analysis.get('regression_patterns', {}).get('long', 0) > 2,
                'poor_fixation_stability': fixation_stability < self.fixation_stability_threshold,
                'poor_reading_linearity': reading_linearity < self.linearity_threshold,
                'slow_saccades': avg_saccade_time > self.saccade_time_threshold,
                'high_reread_rate': reread_score > 0.3
            }
            
            # Calculate new probability
            new_probability = sum(
                weights[k] * float(v) 
                for k, v in indicators.items()
            )
            
            if regression_analysis.get('regression_severity'):
                new_probability = (new_probability + regression_analysis['regression_severity']) / 2
                
            # Apply sigmoid and smooth the probability
            new_probability = 1 / (1 + math.exp(-10 * (new_probability - 0.5)))
            
            # Limit rate of change
            probability_diff = new_probability - self.last_probability
            if abs(probability_diff) > self.probability_change_rate:
                new_probability = self.last_probability + (
                    self.probability_change_rate if probability_diff > 0 
                    else -self.probability_change_rate
                )
            
            self.last_probability = new_probability
            dyslexia_probability = self._smooth_metric('dyslexia_probability', new_probability)
        else:
            # If not actively reading, maintain last probability or decrease slowly
            dyslexia_probability = max(0, self.last_probability - 0.01)
            self.last_probability = dyslexia_probability
        
        # Enhanced severity classification with smoother transitions
        dyslexia_probability_pct = 100 * dyslexia_probability
        if dyslexia_probability_pct > 80:
            severity = "Severe"
        elif dyslexia_probability_pct > 65:
            severity = "Moderate-to-Severe"
        elif dyslexia_probability_pct > 50:
            severity = "Moderate"
        elif dyslexia_probability_pct > 35:
            severity = "Borderline-to-Moderate"
        elif dyslexia_probability_pct > 20:
            severity = "Borderline"
        else:
            severity = "Mild"
            
        return {
            'fixation_count': self.fixation_count,
            'regression_count': self.regression_count,
            'reading_speed': reading_speed,
            'cognitive_metrics': {
                'load_score': cognitive_load,
                'pupil_load': pupil_load,
                'blink_load': blink_load
            },
            'enhanced_metrics': {
                'fixation_stability': fixation_stability,
                'reading_linearity': reading_linearity,
                'avg_saccade_time': avg_saccade_time,
                'reread_score': reread_score
            },
            'regression_analysis': regression_analysis,
            'dyslexia_indicators': {
                'probability': dyslexia_probability,
                'severity': severity,
                'indicators': indicators if is_active else {}
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

    def _calculate_fixation_stability(self) -> float:
        """Calculate how stable fixations are based on gaze position variance"""
        try:
            if len(self.fixation_stability_history) < 2:
                return 0.5  # Default middle value
            
            # Calculate movement between consecutive positions
            movements = []
            positions = np.array(self.fixation_stability_history)
            for i in range(1, len(positions)):
                movement = np.linalg.norm(positions[i] - positions[i-1])
                movements.append(movement)
            
            # Calculate stability score based on average movement
            avg_movement = np.mean(movements)
            stability_score = 1.0 / (1.0 + avg_movement * 20)  # Adjusted sensitivity
            
            # Map to more realistic range (0.3-0.95)
            return 0.3 + (stability_score * 0.65)
        except Exception as e:
            print(f"Error calculating fixation stability: {str(e)}")
            return 0.5

    def _calculate_reading_linearity(self) -> float:
        """Calculate how linear the reading pattern is"""
        try:
            if len(self.eye_metrics['gaze_positions']) < 3:
                return 0.5
            
            # Get recent positions
            positions = np.array(self.eye_metrics['gaze_positions'][-10:])  # Last 10 positions
            
            if len(positions) < 3:
                return 0.5
                
            # Calculate vertical deviation
            y_positions = positions[:, 1]  # Get y coordinates
            vertical_deviation = np.std(y_positions)
            
            # Calculate horizontal progression
            x_positions = positions[:, 0]  # Get x coordinates
            x_diffs = np.diff(x_positions)
            forward_ratio = np.sum(x_diffs > 0) / len(x_diffs)  # Ratio of forward movements
            
            # Combine metrics
            linearity_score = (
                (1.0 / (1.0 + vertical_deviation * 10)) * 0.6 +  # Vertical stability
                forward_ratio * 0.4  # Forward progression
            )
            
            # Map to more realistic range (0.3-0.95)
            return 0.3 + (linearity_score * 0.65)
        except Exception as e:
            print(f"Error calculating reading linearity: {str(e)}")
            return 0.5

    def _calculate_reread_score(self) -> float:
        """Calculate score based on how often words are reread"""
        try:
            if not self.reread_positions:
                return 0.0
            
            # Get reread counts
            reread_counts = list(self.reread_positions.values())
            
            if not reread_counts:
                return 0.0
            
            # Calculate metrics
            max_rereads = max(reread_counts)
            avg_rereads = np.mean(reread_counts)
            
            # Normalize score (0-1)
            reread_score = min(1.0, (avg_rereads / 3.0) * (max_rereads / 5.0))
            
            return reread_score
        except Exception as e:
            print(f"Error calculating reread score: {str(e)}")

    def _get_metric_color(self, value: float) -> Tuple[int, int, int]:
        """Get color based on metric value (0-1 range)"""
        if value > 0.7:
            return (0, 255, 0)  # Green
        elif value > 0.4:
            return (0, 255, 255)  # Yellow
        else:
            return (0, 0, 255)  # Red

    def _get_regression_color(self, severity: float) -> Tuple[int, int, int]:
        """Get color based on regression severity"""
        if severity < 0.3:
            return (0, 255, 0)  # Green
        elif severity < 0.6:
            return (0, 255, 255)  # Yellow
        else:
            return (0, 0, 255)  # Red

    def _get_count_color(self, count: int, category: str) -> Tuple[int, int, int]:
        """Get color based on regression count and category"""
        thresholds = {
            'Short': (3, 6),
            'Medium': (2, 4),
            'Long': (1, 3),
            'Line Changes': (2, 4)
        }
        low, high = thresholds.get(category, (3, 6))
        
        if count <= low:
            return (0, 255, 0)  # Green
        elif count <= high:
            return (0, 255, 255)  # Yellow
        else:
            return (0, 0, 255)  # Red

    def _draw_load_bar(self, frame: np.ndarray, x: int, y: int, 
                      load_score: float, color: Tuple[int, int, int]):
        """Draw a load bar with the given score"""
        bar_length = 200
        bar_height = 20
        
        # Draw background bar
        cv2.rectangle(frame, (x, y), (x + bar_length, y + bar_height),
                     (128, 128, 128), -1)
        
        # Draw filled portion based on load
        filled_length = int(bar_length * load_score)
        cv2.rectangle(frame, (x, y), (x + filled_length, y + bar_height),
                     color, -1)
        
        # Draw border
        cv2.rectangle(frame, (x, y), (x + bar_length, y + bar_height),
                     (255, 255, 255), 1)