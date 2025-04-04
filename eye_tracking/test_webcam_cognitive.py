import cv2
import numpy as np
from eye_tracking.eye_tracker import EyeTracker
from eye_tracking.cognitive_load_analyzer import CognitiveLoadAnalyzer
import time

def test_webcam_cognitive_load():
    print("Starting Webcam Cognitive Load Test...")
    print("Press 'q' to quit, 's' to start/restart test")
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Initialize eye tracker
    tracker = EyeTracker()
    test_start_time = None
    test_running = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
            
        # Process frame
        metrics = tracker.process_frame(frame)
        
        # Get cognitive load metrics
        cognitive_metrics = tracker.get_cognitive_metrics()
        
        # Draw metrics on frame
        cv2.putText(frame, f"Cognitive Load: {cognitive_metrics['cognitive_load_score']:.2f}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Load Level: {cognitive_metrics['load_level']}", 
                    (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Pupil Load: {cognitive_metrics['pupil_load']:.2f}", 
                    (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Blink Load: {cognitive_metrics['blink_load']:.2f}", 
                    (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw cognitive load bar
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 180
        score = cognitive_metrics['cognitive_load_score']
        
        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + bar_height), 
                     (128, 128, 128), -1)
        
        # Filled portion based on score
        fill_width = int(bar_width * score)
        if score > 0.7:
            color = (0, 0, 255)  # Red for high load
        elif score > 0.3:
            color = (0, 255, 255)  # Yellow for medium load
        else:
            color = (0, 255, 0)  # Green for low load
            
        cv2.rectangle(frame, (bar_x, bar_y), 
                     (bar_x + fill_width, bar_y + bar_height), 
                     color, -1)
        
        # Border
        cv2.rectangle(frame, (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + bar_height), 
                     (255, 255, 255), 1)
        
        # Show frame
        cv2.imshow('Cognitive Load Test', frame)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            test_running = not test_running
            test_start_time = time.time() if test_running else None
            print("Test", "started" if test_running else "stopped")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_webcam_cognitive_load() 