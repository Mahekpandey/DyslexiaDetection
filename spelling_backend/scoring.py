from typing import Tuple
import difflib

def calculate_accuracy(expected: str, actual: str) -> float:
    """Calculate spelling accuracy between expected and actual spelling."""
    return difflib.SequenceMatcher(None, expected.lower(), actual.lower()).ratio()

def calculate_dyslexia_indicator(accuracy: float, time_taken: float, age_group: str) -> float:
    """Calculate dyslexia indicator based on accuracy and time taken."""
    # Base thresholds for different age groups
    age_thresholds = {
        "5-7": {"accuracy": 0.7, "time": 30.0},
        "8-10": {"accuracy": 0.8, "time": 25.0},
        "11-13": {"accuracy": 0.85, "time": 20.0},
        "14+": {"accuracy": 0.9, "time": 15.0}
    }
    
    threshold = age_thresholds.get(age_group, {"accuracy": 0.8, "time": 25.0})
    
    # Calculate indicators
    accuracy_indicator = max(0, (threshold["accuracy"] - accuracy) / threshold["accuracy"])
    time_indicator = max(0, (time_taken - threshold["time"]) / threshold["time"])
    
    # Weighted average of indicators
    dyslexia_indicator = (accuracy_indicator * 0.7) + (time_indicator * 0.3)
    
    return min(1.0, dyslexia_indicator)

def calculate_score(accuracy: float, time_taken: float, difficulty: int) -> float:
    """Calculate overall score based on accuracy, time, and difficulty."""
    time_factor = max(0, 1 - (time_taken / 60))  # Normalize time to 60 seconds
    difficulty_factor = 1 + (difficulty * 0.1)  # Increase score with difficulty
    
    return (accuracy * 0.7 + time_factor * 0.3) * difficulty_factor * 100

def analyze_response(expected: str, actual: str, time_taken: float, age_group: str, difficulty: int) -> Tuple[float, float, float]:
    """Analyze user response and return score, accuracy, and dyslexia indicator."""
    accuracy = calculate_accuracy(expected, actual)
    dyslexia_indicator = calculate_dyslexia_indicator(accuracy, time_taken, age_group)
    score = calculate_score(accuracy, time_taken, difficulty)
    
    return score, accuracy, dyslexia_indicator 