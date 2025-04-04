import numpy as np
from collections import deque
import logging

class CognitiveLoadAnalyzer:
    def __init__(self, window_size=60):  # 60 frames = 2 seconds at 30 fps
        """Initialize the cognitive load analyzer.
        
        Args:
            window_size (int): Number of frames to consider for rolling calculations
        """
        # Window size for rolling calculations
        self.window_size = window_size
        
        # Deques for storing historical data
        self.pupil_sizes = deque(maxlen=window_size)
        self.blink_durations = deque(maxlen=window_size)
        self.blink_intervals = deque(maxlen=window_size)
        
        # Timestamps for calculations
        self.last_blink_timestamp = None
        self.blink_start_time = None
        self.is_blinking = False
        
        # Baseline values
        self.baseline_pupil_size = None
        self.baseline_blink_rate = None
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def update_pupil_size(self, pupil_size, timestamp):
        """Update pupil size measurements and calculate dilation metrics.
        
        Args:
            pupil_size (float): Current pupil size
            timestamp (float): Current timestamp
        
        Returns:
            dict: Dictionary containing pupil metrics
        """
        try:
            # Add new pupil size to history
            self.pupil_sizes.append(pupil_size)
            
            # Calculate metrics only if we have enough data
            if len(self.pupil_sizes) < 3:
                return None
            
            # Calculate pupil metrics
            current_dilation = pupil_size
            mean_dilation = np.mean(self.pupil_sizes)
            dilation_variability = np.std(self.pupil_sizes)
            
            # Calculate dilation velocity (rate of change)
            dilation_velocity = (self.pupil_sizes[-1] - self.pupil_sizes[-2])
            
            # Update baseline if not set
            if self.baseline_pupil_size is None:
                self.baseline_pupil_size = mean_dilation
            
            # Calculate relative dilation (compared to baseline)
            relative_dilation = (current_dilation - self.baseline_pupil_size) / self.baseline_pupil_size
            
            return {
                'current_dilation': current_dilation,
                'mean_dilation': mean_dilation,
                'dilation_variability': dilation_variability,
                'dilation_velocity': dilation_velocity,
                'relative_dilation': relative_dilation
            }
            
        except Exception as e:
            self.logger.error(f"Error in update_pupil_size: {str(e)}")
            return None
    
    def update_blink(self, is_eye_closed, timestamp):
        """Update blink detection and calculate blink metrics.
        
        Args:
            is_eye_closed (bool): Whether the eye is currently closed
            timestamp (float): Current timestamp
        
        Returns:
            dict: Dictionary containing blink metrics
        """
        try:
            # Detect blink start
            if not self.is_blinking and is_eye_closed:
                self.is_blinking = True
                self.blink_start_time = timestamp
            
            # Detect blink end
            elif self.is_blinking and not is_eye_closed:
                self.is_blinking = False
                
                # Calculate blink duration
                if self.blink_start_time is not None:
                    blink_duration = timestamp - self.blink_start_time
                    self.blink_durations.append(blink_duration)
                    
                    # Calculate inter-blink interval
                    if self.last_blink_timestamp is not None:
                        interval = timestamp - self.last_blink_timestamp
                        self.blink_intervals.append(interval)
                    
                    self.last_blink_timestamp = timestamp
            
            # Calculate metrics only if we have enough data
            if len(self.blink_durations) < 2:
                return None
            
            # Calculate blink metrics
            mean_duration = np.mean(self.blink_durations)
            blink_variability = np.std(self.blink_durations)
            
            # Calculate blink rate (blinks per minute)
            if self.blink_intervals:
                mean_interval = np.mean(self.blink_intervals)
                blink_rate = 60.0 / mean_interval if mean_interval > 0 else 0
            else:
                blink_rate = 0
            
            return {
                'mean_blink_duration': mean_duration,
                'blink_variability': blink_variability,
                'blink_rate': blink_rate,
                'is_blinking': self.is_blinking
            }
            
        except Exception as e:
            self.logger.error(f"Error in update_blink: {str(e)}")
            return None
    
    def calculate_cognitive_load(self, pupil_metrics, blink_metrics):
        """Calculate overall cognitive load based on pupil and blink metrics.
        
        Args:
            pupil_metrics (dict): Dictionary of pupil-related metrics
            blink_metrics (dict): Dictionary of blink-related metrics
        
        Returns:
            dict: Dictionary containing cognitive load metrics
        """
        try:
            if not pupil_metrics or not blink_metrics:
                return None
            
            # Weights for different components (can be adjusted based on research)
            PUPIL_WEIGHT = 0.4
            BLINK_WEIGHT = 0.3
            VARIABILITY_WEIGHT = 0.3
            
            # Calculate pupil load component
            pupil_load = (
                pupil_metrics['relative_dilation'] * PUPIL_WEIGHT +
                pupil_metrics['dilation_variability'] * VARIABILITY_WEIGHT
            )
            
            # Calculate blink load component
            blink_load = (
                (blink_metrics['blink_variability'] / blink_metrics['mean_blink_duration'])
                * BLINK_WEIGHT if blink_metrics['mean_blink_duration'] > 0 else 0
            )
            
            # Combine into overall cognitive load score (0-1 range)
            cognitive_load = np.clip(pupil_load + blink_load, 0, 1)
            
            # Determine load level
            if cognitive_load < 0.3:
                load_level = "Low"
            elif cognitive_load < 0.7:
                load_level = "Medium"
            else:
                load_level = "High"
            
            return {
                'cognitive_load_score': cognitive_load,
                'load_level': load_level,
                'pupil_load_component': pupil_load,
                'blink_load_component': blink_load
            }
            
        except Exception as e:
            self.logger.error(f"Error in calculate_cognitive_load: {str(e)}")
            return None
    
    def reset(self):
        """Reset all stored data and baselines."""
        self.pupil_sizes.clear()
        self.blink_durations.clear()
        self.blink_intervals.clear()
        self.last_blink_timestamp = None
        self.blink_start_time = None
        self.is_blinking = False
        self.baseline_pupil_size = None
        self.baseline_blink_rate = None 