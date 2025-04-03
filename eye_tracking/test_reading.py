import cv2
import numpy as np
from reading_analyzer import ReadingAnalyzer

def main():
    # Initialize the reading analyzer
    analyzer = ReadingAnalyzer()
    
    # Start video capture
    cap = cv2.VideoCapture(0)
    
    # Set video capture properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print("Starting reading analysis...")
    print("Press 's' to start/restart the reading test")
    print("Press 'p' to pause/resume")
    print("Press 'q' to quit")
    
    is_running = False
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            # Flip frame horizontally for more intuitive interaction
            frame = cv2.flip(frame, 1)
            
            if is_running:
                # Process frame with reading analysis
                processed_frame, metrics = analyzer.process_frame(frame)
                
                # Display metrics in console
                if metrics and 'dyslexia_indicators' in metrics:
                    indicators = metrics['dyslexia_indicators']
                    print(f"\rDyslexia Probability: {indicators['probability']*100:.1f}% | "
                          f"Reading Speed: {metrics['reading_speed']} WPM | "
                          f"Fixations: {metrics['fixation_count']} | "
                          f"Regressions: {metrics.get('regression_count', 0)}", end='')
            else:
                # Just show the frame with instructions when not running
                processed_frame = frame.copy()
                cv2.putText(processed_frame, "Press 's' to start reading test",
                           (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow('Reading Analysis', processed_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Reset analyzer and start new test
                analyzer = ReadingAnalyzer()
                is_running = True
                print("\nStarting new reading test...")
            elif key == ord('p'):
                is_running = not is_running
                print("\nTest paused" if not is_running else "\nTest resumed")
                
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        analyzer.release()

if __name__ == "__main__":
    main() 