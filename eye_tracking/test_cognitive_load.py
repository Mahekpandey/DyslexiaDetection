import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
from eye_tracking.cognitive_load_analyzer import CognitiveLoadAnalyzer
from eye_tracking.eye_tracker import EyeTracker

def test_cognitive_load_analyzer():
    print("Starting Cognitive Load Analysis Test...")
    analyzer = CognitiveLoadAnalyzer()
    
    # Test 1: Normal Reading Pattern
    print("\nTest 1: Normal Reading Pattern")
    timestamp = time.time()
    
    # Simulate normal pupil sizes (0.2-0.4 range)
    for i in range(30):  # 1 second of data at 30fps
        pupil_size = 0.3 + np.random.normal(0, 0.02)  # Small variations
        is_blinking = False
        
        pupil_metrics = analyzer.update_pupil_size(pupil_size, timestamp + i/30)
        blink_metrics = analyzer.update_blink(is_blinking, timestamp + i/30)
        
        if pupil_metrics and blink_metrics:
            load = analyzer.calculate_cognitive_load(pupil_metrics, blink_metrics)
            if load:
                print(f"Normal Load - Score: {load['cognitive_load_score']:.2f}, Level: {load['load_level']}")
    
    # Test 2: High Cognitive Load Pattern
    print("\nTest 2: High Cognitive Load Pattern")
    timestamp = time.time()
    
    # Simulate dilated pupils (0.4-0.6 range) and increased blink rate
    for i in range(30):
        pupil_size = 0.5 + np.random.normal(0, 0.03)  # Larger variations
        is_blinking = i % 10 == 0  # Blink every 10 frames
        
        pupil_metrics = analyzer.update_pupil_size(pupil_size, timestamp + i/30)
        blink_metrics = analyzer.update_blink(is_blinking, timestamp + i/30)
        
        if pupil_metrics and blink_metrics:
            load = analyzer.calculate_cognitive_load(pupil_metrics, blink_metrics)
            if load:
                print(f"High Load - Score: {load['cognitive_load_score']:.2f}, Level: {load['load_level']}")
    
    # Test 3: Low Cognitive Load Pattern
    print("\nTest 3: Low Cognitive Load Pattern")
    timestamp = time.time()
    
    # Simulate normal pupils (0.2-0.3 range) and normal blink rate
    for i in range(30):
        pupil_size = 0.25 + np.random.normal(0, 0.01)  # Small variations
        is_blinking = i % 20 == 0  # Blink every 20 frames
        
        pupil_metrics = analyzer.update_pupil_size(pupil_size, timestamp + i/30)
        blink_metrics = analyzer.update_blink(is_blinking, timestamp + i/30)
        
        if pupil_metrics and blink_metrics:
            load = analyzer.calculate_cognitive_load(pupil_metrics, blink_metrics)
            if load:
                print(f"Low Load - Score: {load['cognitive_load_score']:.2f}, Level: {load['load_level']}")

def test_eye_tracker_integration():
    print("\nTesting Eye Tracker Integration...")
    tracker = EyeTracker()
    
    # Simulate frame processing with different cognitive load patterns
    timestamp = time.time()
    
    # Test normal reading
    metrics = tracker.get_ml_features()
    cognitive_metrics = tracker.get_cognitive_metrics()
    print("\nNormal Reading Metrics:")
    print(f"Cognitive Load Score: {cognitive_metrics['cognitive_load_score']:.2f}")
    print(f"Load Level: {cognitive_metrics['load_level']}")
    print(f"Pupil Load: {cognitive_metrics['pupil_load']:.2f}")
    print(f"Blink Load: {cognitive_metrics['blink_load']:.2f}")

if __name__ == "__main__":
    test_cognitive_load_analyzer()
    test_eye_tracker_integration() 