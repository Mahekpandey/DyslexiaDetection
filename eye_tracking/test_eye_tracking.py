import cv2
import numpy as np
from eye_tracker import EyeTracker
import time

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    # Initialize eye tracker
    eye_tracker = EyeTracker()

    print("Starting eye tracking test...")
    print("Press 'q' to quit")

    try:
        while True:
            # Read frame from webcam
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break

            # Process frame with eye tracker
            processed_frame, eye_data = eye_tracker.process_frame(frame)

            # Display the frame
            cv2.imshow('Eye Tracking Test', processed_frame)

            # Break loop on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error during eye tracking: {str(e)}")
    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 