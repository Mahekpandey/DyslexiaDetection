import cv2
import numpy as np
from eye_tracker import EyeTracker
import time
from typing import Tuple, Dict
import math

class AccuracyTester:
    def __init__(self):
        self.eye_tracker = EyeTracker()
        self.calibration_points = [
            (0.2, 0.2), (0.5, 0.2), (0.8, 0.2),  # Top row
            (0.2, 0.5), (0.5, 0.5), (0.8, 0.5),  # Middle row
            (0.2, 0.8), (0.5, 0.8), (0.8, 0.8)   # Bottom row
        ]
        self.current_point = 0
        self.samples = []
        self.recording = False
        self.point_duration = 3  # seconds
        self.point_start_time = 0
        self.last_accuracies = {"left": 0.0, "right": 0.0}

    def draw_calibration_point(self, frame: np.ndarray, point: Tuple[float, float], eye_data: Dict = None):
        """Draw current calibration point and gaze lines"""
        h, w = frame.shape[:2]
        x = int(point[0] * w)
        y = int(point[1] * h)
        
        # Draw outer circle
        cv2.circle(frame, (x, y), 20, (0, 255, 0), 2)
        # Draw inner circle
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        
        # Draw gaze lines if eye data is available
        if eye_data and 'left_pupil_relative' in eye_data:
            left_pos = eye_data['left_pupil_relative']
            right_pos = eye_data['right_pupil_relative']
            
            # Convert relative positions to pixel coordinates
            left_x = int(left_pos[0] * w)
            left_y = int(left_pos[1] * h)
            right_x = int(right_pos[0] * w)
            right_y = int(right_pos[1] * h)
            
            # Draw lines from eyes to target
            cv2.line(frame, (left_x, left_y), (x, y), (0, 255, 0), 1)
            cv2.line(frame, (right_x, right_y), (x, y), (0, 255, 0), 1)
        
        # Draw countdown
        if self.recording:
            time_left = self.point_duration - (time.time() - self.point_start_time)
            if time_left > 0:
                cv2.putText(frame, f"{time_left:.1f}s", (x + 25, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    def calculate_accuracy(self, target: Tuple[float, float], measured: Tuple[float, float]) -> float:
        """Calculate normalized accuracy score between target and measured positions"""
        # Calculate Euclidean distance
        distance = math.sqrt((target[0] - measured[0])**2 + (target[1] - measured[1])**2)
        # Convert distance to accuracy score (1 - normalized distance)
        # Max possible distance in normalized coordinates is sqrt(2)
        max_distance = math.sqrt(2)
        accuracy = 1.0 - min(distance / max_distance, 1.0)
        return accuracy

    def draw_accuracy_metrics(self, frame: np.ndarray, eye_data: Dict):
        """Draw accuracy metrics on frame"""
        if not 'left_pupil_relative' in eye_data:
            return

        current_target = self.calibration_points[self.current_point]
        left_pos = eye_data['left_pupil_relative']
        right_pos = eye_data['right_pupil_relative']
        
        left_accuracy = self.calculate_accuracy(current_target, left_pos)
        right_accuracy = self.calculate_accuracy(current_target, right_pos)
        
        # Update last accuracies
        self.last_accuracies = {"left": left_accuracy, "right": right_accuracy}
        
        # Draw accuracy information (as percentage)
        cv2.putText(frame, f"Left Eye Accuracy: {left_accuracy*100:.1f}%", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Right Eye Accuracy: {right_accuracy*100:.1f}%", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        if self.recording:
            # Store accuracy data
            self.samples.append({
                'target': current_target,
                'left_measured': left_pos,
                'right_measured': right_pos,
                'left_accuracy': left_accuracy,
                'right_accuracy': right_accuracy,
                'timestamp': time.time()
            })

    def run_test(self):
        """Run the accuracy test"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return

        print("Starting accuracy test...")
        print("Follow the green dots with your eyes")
        print("Press 'q' to quit, 'n' for next point, 'r' to restart")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame with eye tracker
            processed_frame, eye_data = self.eye_tracker.process_frame(frame)
            
            # Draw accuracy metrics first (so they appear under other elements)
            self.draw_accuracy_metrics(processed_frame, eye_data)
            
            # Draw current calibration point with gaze lines
            current_point = self.calibration_points[self.current_point]
            self.draw_calibration_point(processed_frame, current_point, eye_data)
            
            # Add test instructions
            cv2.putText(processed_frame, "Press 'n' for next point", (10, frame.shape[0] - 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(processed_frame, f"Point {self.current_point + 1}/9", (10, frame.shape[0] - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Display average accuracy if recording
            if self.recording:
                avg_accuracy = (self.last_accuracies["left"] + self.last_accuracies["right"]) / 2
                color = (0, 255, 0) if avg_accuracy > 0.7 else (0, 165, 255) if avg_accuracy > 0.4 else (0, 0, 255)
                cv2.putText(processed_frame, f"Average Accuracy: {avg_accuracy*100:.1f}%", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Display the frame
            cv2.imshow('Accuracy Test', processed_frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n'):
                # Move to next point
                self.current_point = (self.current_point + 1) % len(self.calibration_points)
                self.recording = True
                self.point_start_time = time.time()
            elif key == ord('r'):
                # Restart test
                self.current_point = 0
                self.samples = []
                self.recording = False

            # Check if current point duration is complete
            if self.recording and (time.time() - self.point_start_time) > self.point_duration:
                self.recording = False
                print(f"Point {self.current_point + 1} complete")
                # Automatically move to next point
                self.current_point = (self.current_point + 1) % len(self.calibration_points)
                if self.current_point == 0:
                    self.analyze_results()

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        self.eye_tracker.release()

    def analyze_results(self):
        """Analyze and display test results"""
        if not self.samples:
            print("No data collected")
            return

        # Calculate average accuracies
        left_accuracies = [s['left_accuracy'] for s in self.samples]
        right_accuracies = [s['right_accuracy'] for s in self.samples]
        
        print("\nTest Results:")
        print(f"Number of samples: {len(self.samples)}")
        print(f"Average left eye accuracy: {np.mean(left_accuracies)*100:.1f}%")
        print(f"Average right eye accuracy: {np.mean(right_accuracies)*100:.1f}%")
        print(f"Min left eye accuracy: {min(left_accuracies)*100:.1f}%")
        print(f"Min right eye accuracy: {min(right_accuracies)*100:.1f}%")
        
        # Reset samples for next round
        self.samples = []

if __name__ == "__main__":
    tester = AccuracyTester()
    tester.run_test() 