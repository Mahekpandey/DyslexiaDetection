import cv2
import numpy as np
from reading_analyzer import ReadingAnalyzer
import time
import json
from datetime import datetime

class ReadingTest:
    def __init__(self):
        self.analyzer = ReadingAnalyzer()
        # More structured test with different types of text
        self.test_sections = {
            'simple': [
                "The quick brown fox jumps over the lazy dog.",
                "She sells seashells by the seashore.",
                "The rain in Spain stays mainly in the plain."
            ],
            'complex': [
                "The intricate mechanisms of cognitive processing",
                "Scientists hypothesize various theoretical frameworks",
                "Understanding multifaceted learning methodologies"
            ],
            'numbers': [
                "Please read these numbers: 123 456 789",
                "Calculate: 15 + 27 = 42, 89 - 34 = 55",
                "Phone: (555) 123-4567, Date: 03/31/2024"
            ]
        }
        self.current_section = 'simple'
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 1.0
        self.line_spacing = 60
        self.start_y = 100
        self.left_margin = 20
        self.section_data = {}

    def draw_text(self, frame):
        """Draw reading text on frame with background"""
        overlay = frame.copy()
        
        # Draw section title
        title_y = self.start_y - 40
        title = f"Section: {self.current_section.title()}"
        cv2.putText(overlay, title, 
                   (self.left_margin, title_y),
                   self.font, self.font_scale,
                   (255, 255, 0), 2)

        # Draw text lines
        for i, line in enumerate(self.test_sections[self.current_section]):
            y = self.start_y + i * self.line_spacing
            
            # Get text size
            (text_width, text_height), _ = cv2.getTextSize(line, self.font, self.font_scale, 2)
            
            # Draw background rectangle
            cv2.rectangle(overlay, 
                         (self.left_margin - 10, y - text_height - 5),
                         (self.left_margin + text_width + 10, y + 5),
                         (0, 0, 0),
                         -1)
            
            # Draw text
            cv2.putText(overlay, line,
                       (self.left_margin, y),
                       self.font,
                       self.font_scale,
                       (255, 255, 255),
                       2)
        
        # Draw instructions
        instructions = "Press SPACE for next section, 'q' to finish"
        cv2.putText(overlay, instructions,
                   (self.left_margin, frame.shape[0] - 30),
                   self.font, 0.7,
                   (0, 255, 255), 2)

        # Blend the overlay with the original frame
        alpha = 0.7
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    def run_test(self):
        """Run the reading test"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return

        print("\nReading Test Instructions:")
        print("1. Position your head to face the camera directly")
        print("2. Read each section naturally, left to right")
        print("3. Press SPACE to move to the next section")
        print("4. Press 'q' when finished with all sections\n")
        time.sleep(3)

        sections = list(self.test_sections.keys())
        section_idx = 0
        self.current_section = sections[section_idx]
        
        reading_data = []
        section_start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            processed_frame, eye_data = self.analyzer.analyze_frame(frame)
            self.draw_text(processed_frame)

            if eye_data:
                eye_data['timestamp'] = time.time() - section_start_time
                eye_data['section'] = self.current_section
                reading_data.append(eye_data)

            cv2.imshow('Reading Test', processed_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                # Save current section data
                self.section_data[self.current_section] = {
                    'duration': time.time() - section_start_time,
                    'data': [d for d in reading_data if d['section'] == self.current_section]
                }
                
                # Move to next section
                section_idx += 1
                if section_idx < len(sections):
                    self.current_section = sections[section_idx]
                    section_start_time = time.time()
                    print(f"\nMoving to {self.current_section} section...")
                else:
                    break

        # Calculate and display final metrics
        self.display_final_metrics()
        self.save_results()

        cap.release()
        cv2.destroyAllWindows()
        self.analyzer.release()

    def calculate_section_metrics(self, section_name):
        """Calculate metrics for a specific section"""
        if section_name not in self.section_data:
            return None

        section = self.section_data[section_name]
        text = self.test_sections[section_name]
        
        # Calculate basic metrics
        total_chars = sum(len(line) for line in text)
        words = total_chars / 5  # Approximate words
        duration = section['duration']
        wpm = (words / duration) * 60

        # Get dyslexia indicators from the last frame
        metrics = self.analyzer._analyze_reading_patterns()
        
        return {
            'duration_seconds': duration,
            'words_per_minute': wpm,
            'dyslexia_indicators': metrics.get('dyslexia_indicators', {}),
            'total_words': words
        }

    def display_final_metrics(self):
        """Display final reading metrics"""
        print("\n=== Reading Test Results ===\n")
        
        for section in self.test_sections.keys():
            metrics = self.calculate_section_metrics(section)
            if metrics:
                print(f"\nSection: {section.title()}")
                print(f"Duration: {metrics['duration_seconds']:.2f} seconds")
                print(f"Reading Speed: {metrics['words_per_minute']:.1f} WPM")
                
                if 'dyslexia_indicators' in metrics:
                    indicators = metrics['dyslexia_indicators']
                    print(f"Dyslexia Indicators: {indicators['probability']*100:.1f}%")
                    print("\nDetailed Indicators:")
                    for name, value in indicators.get('indicators', {}).items():
                        print(f"- {name}: {'Yes' if value else 'No'}")

    def save_results(self):
        """Save test results to a file"""
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
            'sections': {}
        }
        
        for section in self.test_sections.keys():
            results['sections'][section] = self.calculate_section_metrics(section)

        filename = f"reading_test_results_{results['timestamp']}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {filename}")

def main():
    # Initialize the reading analyzer
    analyzer = ReadingAnalyzer()
    
    # Start video capture
    cap = cv2.VideoCapture(0)
    
    print("Starting reading test...")
    print("Press 'q' to quit")
    print("Press 's' to start/restart the reading test")
    print("Press 'p' to pause/resume")
    
    paused = True
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Flip frame horizontally for more intuitive interaction
            frame = cv2.flip(frame, 1)
            
            if not paused:
                # Process frame with reading analysis
                processed_frame, metrics = analyzer.process_frame(frame)
                
                # Display metrics
                if metrics:
                    print(f"\rDyslexia Probability: {metrics['dyslexia_probability']:.2%} | "
                          f"Reading Speed: {metrics['reading_speed']:.1f} WPM | "
                          f"Fixations: {metrics['fixation_count']} | "
                          f"Regressions: {metrics['regression_count']}", end='')
            else:
                # Just show the frame with text when paused
                processed_frame = frame.copy()
                analyzer._draw_text(processed_frame)
                cv2.putText(processed_frame, "PAUSED - Press 's' to start", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display the frame
            cv2.imshow('Reading Test', processed_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Reset analyzer and start new test
                analyzer = ReadingAnalyzer()
                paused = False
                print("\nStarting new reading test...")
            elif key == ord('p'):
                paused = not paused
                if paused:
                    print("\nTest paused")
                else:
                    print("\nTest resumed")
                
    except Exception as e:
        print(f"\nError during reading test: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        analyzer.release()

if __name__ == "__main__":
    main() 