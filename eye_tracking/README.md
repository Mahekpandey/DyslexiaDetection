# Eye Tracking for Dyslexia Detection

This project implements an advanced eye tracking system for detecting potential indicators of dyslexia through real-time analysis of reading patterns. The system uses computer vision and machine learning techniques to analyze various aspects of eye movement during reading.

## Features

### 1. Core Eye Tracking Metrics

- **Gaze Position Tracking**
  - Tracks both left and right eye positions
  - Calculates average gaze position
  - Monitors horizontal and vertical eye movements

- **Fixation Analysis**
  - Detects stable gaze points (fixations)
  - Measures fixation duration
  - Uses percentile-based thresholds for individual adaptation
  - Minimum fixation duration: 200ms

- **Saccade Detection**
  - Identifies rapid eye movements between fixations
  - Analyzes saccade velocity and direction
  - Normalizes saccade measurements based on individual baseline
  - Detects backward saccades (regressions)

### 2. Advanced Metrics

- **Reading Speed**
  - Words per minute (WPM) calculation
  - Adjusts for text complexity using Flesch-Kincaid readability scores
  - Considers individual reading patterns

- **Blink Analysis**
  - Monitors blink frequency
  - Calculates blink rate per minute
  - Considers blink duration patterns

- **Gaze Stability**
  - Measures steadiness of gaze during reading
  - Analyzes fixation stability
  - Tracks vertical drift

### 3. Dyslexia Indicators

The system analyzes several key indicators associated with dyslexia:

1. **Backward Saccades (Weight: 25%)**
   - Frequent backward eye movements
   - Indicates re-reading behavior

2. **Long Fixations (Weight: 20%)**
   - Extended gaze duration on words
   - Compared against individual baseline

3. **Irregular Saccades (Weight: 20%)**
   - Unusual eye movement patterns
   - Normalized against baseline behavior

4. **Gaze Stability (Weight: 15%)**
   - Stability of eye position during reading
   - Measures focus maintenance

5. **Blink Rate (Weight: 10%)**
   - Frequency of blinking
   - Potential indicator of reading difficulty

6. **Pupil Variability (Weight: 10%)**
   - Changes in pupil size
   - May indicate cognitive load

### 4. Real-time Analysis

- Continuous monitoring of eye movements
- Dynamic threshold adjustments
- Baseline metric updates
- Rolling window of 1000 samples for baseline calculations

## Technical Implementation

### Data Collection
```python
def _update_reading_metrics(self, eye_data):
    # Collects:
    - Gaze positions (left and right eyes)
    - Pupil measurements
    - Blink data
    - Temporal information
```

### Metric Calculation
```python
def _analyze_reading_patterns(self):
    # Processes:
    - Reading speed with complexity adjustment
    - Fixation patterns
    - Saccade characteristics
    - Dyslexia probability calculation
```

### Baseline Normalization
```python
def _normalize_saccade_velocity(self, velocity):
    # Normalizes measurements using:
    - Individual baseline data
    - Z-score normalization
    - Rolling window of measurements
```

## Severity Classification

The system classifies dyslexia probability into three levels:

- **Mild**: Probability < 40%
- **Moderate**: Probability 40-70%
- **Severe**: Probability > 70%

## Usage

1. **Start the Analysis**
   ```python
   analyzer = ReadingAnalyzer()
   analyzer.start_reading_test(text)
   ```

2. **Process Frames**
   ```python
   processed_frame, metrics = analyzer.process_frame(frame)
   ```

3. **View Results**
   - Real-time metrics display
   - Visual indicators for detected patterns
   - Probability and severity assessment

## Dependencies

- OpenCV (cv2)
- NumPy
- Mediapipe (for facial landmark detection)

## References

1. Rayner, K. (1998). Eye movements in reading and information processing: 20 years of research. Psychological Bulletin.
2. Pennington, B. F. (2009). Diagnosing learning disorders: A neuropsychological framework.
3. Stein, J. (2014). Dyslexia: the Role of Vision and Visual Attention.

## Note

This system is intended as a screening tool and should not be used as the sole basis for dyslexia diagnosis. Professional assessment is recommended for accurate diagnosis. 