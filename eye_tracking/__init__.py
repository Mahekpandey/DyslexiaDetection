"""
Eye tracking module for dyslexia detection.
This module provides functionality for tracking eye movements and analyzing
reading patterns to assist in dyslexia detection.
"""

from .eye_tracker import EyeTracker
from .reading_analyzer import ReadingAnalyzer

__all__ = ['EyeTracker', 'ReadingAnalyzer'] 