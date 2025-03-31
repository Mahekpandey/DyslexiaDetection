import cv2
import numpy as np
from reading_analyzer import ReadingAnalyzer

def main():
    # Initialize reading analyzer
    analyzer = ReadingAnalyzer()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    print("Starting reading analysis...")
    print("Please read the text from left to right")
    print("Press 'q' to quit")

    try:
        while True:
            # Read frame from webcam
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Analyze frame
            processed_frame, _ = analyzer.analyze_frame(frame)

            # Display the frame
            cv2.imshow('Reading Analysis', processed_frame)

            # Break loop on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error during analysis: {str(e)}")
    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        analyzer.release()

if __name__ == "__main__":
    main() 