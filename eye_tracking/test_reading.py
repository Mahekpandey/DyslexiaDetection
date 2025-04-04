import cv2
import time
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eye_tracking.reading_analyzer import ReadingAnalyzer

def test_reading():
    """Test reading analysis with webcam input"""
    # Initialize analyzer
    analyzer = ReadingAnalyzer()
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print("Reading Test Started")
    print("Press 's' to start/restart the test")
    print("Press 'p' to pause/resume")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process frame
        processed_frame, metrics = analyzer.process_frame(frame)
        
        # Display frame
        cv2.imshow('Reading Test', processed_frame)
        
        # Handle key events
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            analyzer.start_test()
            print("Test started")
        elif key == ord('p'):
            analyzer.toggle_pause()
            print("Test paused" if analyzer.is_paused else "Test resumed")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_reading() 