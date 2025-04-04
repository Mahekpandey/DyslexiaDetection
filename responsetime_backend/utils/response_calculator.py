from typing import List
import time

class ResponseTimeCalculator:
    def __init__(self):
        self.attempts = []
        self.start_time = None
        self.current_attempt = None

    def start_attempt(self):
        """Start timing for a new attempt"""
        self.start_time = time.time() * 1000  # Convert to milliseconds
        self.current_attempt = {
            'start_time': self.start_time,
            'end_time': None,
            'response_time': None
        }

    def end_attempt(self):
        """End timing for current attempt and record it"""
        if not self.start_time:
            raise ValueError("No attempt in progress")
        
        end_time = time.time() * 1000
        response_time = end_time - self.start_time
        
        self.current_attempt['end_time'] = end_time
        self.current_attempt['response_time'] = response_time
        self.attempts.append(self.current_attempt)
        
        self.start_time = None
        self.current_attempt = None
        
        return response_time

    def calculate_score(self, response_times: List[float]) -> dict:
        """
        Calculate score based on response times
        Returns: {
            'average_time': float,
            'score': float (0-100),
            'individual_scores': List[float]
        }
        """
        if len(response_times) != 3:
            raise ValueError("Exactly 3 response times are required")

        # Perfect time threshold (500ms)
        perfect_time = 500
        
        # Calculate individual scores
        individual_scores = []
        for time_ms in response_times:
            if time_ms <= perfect_time:
                score = 100
            else:
                # More punitive scaling for slow responses
                # Lose 2 points for every 100ms above perfect time
                # This means response times above 5 seconds will get 0
                score = max(0, 100 - ((time_ms - perfect_time) / 50))
            individual_scores.append(round(score, 2))

        # Calculate average response time
        avg_time = sum(response_times) / len(response_times)
        
        # Calculate final score
        final_score = sum(individual_scores) / len(individual_scores)

        return {
            'average_time': round(avg_time, 2),
            'score': round(final_score, 2),
            'individual_scores': individual_scores,
            'response_times': response_times
        }

    def get_attempts(self):
        """Get all recorded attempts"""
        return self.attempts

    def clear_attempts(self):
        """Clear all recorded attempts"""
        self.attempts = []
        self.start_time = None
        self.current_attempt = None 