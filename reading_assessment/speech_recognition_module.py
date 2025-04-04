import speech_recognition as sr
import numpy as np
from difflib import SequenceMatcher
import wave
import pyaudio
import os
import time
import json

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_dir = 'static/recordings'
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # Adjust recognition settings
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 3000
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
    def record_audio(self, duration=None):
        """Record audio from microphone"""
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Recording...")
            
            if duration:
                audio = self.recognizer.record(source, duration=duration)
            else:
                audio = self.recognizer.listen(source)
                
            return audio
            
    def transcribe_audio(self, audio_data):
        """Transcribe audio using Google Speech Recognition"""
        try:
            text = self.recognizer.recognize_google(audio_data)
            return text.lower()
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Speech Recognition service; {e}")
            return None
            
    def analyze_word(self, spoken_word, expected_word):
        """Analyze a single word for accuracy and error patterns"""
        spoken = spoken_word.lower().strip('.,!?')
        expected = expected_word.lower().strip('.,!?')
        
        # Quick exact match check
        if spoken == expected:
            return {
                'correct': True,
                'similarity': 1.0,
                'patterns': {'letter_reversal': False, 'phonetic_similarity': False, 'letter_sequence': False},
                'is_homophone': False
            }
        
        # Calculate similarity
        similarity = SequenceMatcher(None, spoken, expected).ratio()
        
        # Quick homophone check
        homophones = {
            'wood': ['would'], 'would': ['wood'],
            'chuck': ['check', 'chock'],
            'there': ['their', "they're"],
            'to': ['too', 'two'],
            'for': ['four', 'fore'],
            'sea': ['see'],
            'by': ['buy', 'bye']
        }
        
        # Check homophones
        is_homophone = False
        if expected in homophones and spoken in homophones[expected]:
            is_homophone = True
        elif spoken in homophones and expected in homophones[spoken]:
            is_homophone = True
            
        # Only check patterns if similarity is in a reasonable range
        patterns = {
            'letter_reversal': False,
            'phonetic_similarity': False,
            'letter_sequence': False
        }
        
        if 0.6 <= similarity <= 0.85:
            patterns.update({
                'letter_reversal': self._check_letter_reversal(spoken, expected),
                'phonetic_similarity': self._check_phonetic_similarity(spoken, expected),
                'letter_sequence': self._check_letter_sequence(spoken, expected)
            })
        
        # Determine if word is correct
        is_correct = (similarity > 0.85 or 
                     is_homophone or 
                     patterns['phonetic_similarity'])
        
        return {
            'correct': is_correct,
            'similarity': similarity,
            'patterns': patterns,
            'is_homophone': is_homophone
        }
    
    def _check_letter_reversal(self, spoken, expected):
        """Check for reversed letter patterns"""
        reversals = [('b', 'd'), ('p', 'q'), ('m', 'w'), ('n', 'u')]
        for a, b in reversals:
            if ((a in expected and b in spoken) or 
                (b in expected and a in spoken)):
                return True
        return False
    
    def _check_phonetic_similarity(self, spoken, expected):
        """Check for phonetically similar sounds - optimized version"""
        # Quick length check
        if abs(len(spoken) - len(expected)) > 2:
            return False
            
        # Common phonetic patterns - ordered by frequency
        phonetic_map = {
            's': set(['c', 'z']),
            't': set(['d', 'ed']),
            'f': set(['ph', 'gh']),
            'k': set(['c', 'ch', 'ck']),
            'i': set(['y', 'ee']),
            'er': set(['ur', 'ir']),
            'oo': set(['u', 'ew']),
            'ai': set(['ay', 'a']),
            'sh': set(['ch']),
            'w': set(['wh']),
            'n': set(['kn', 'gn'])
        }
        
        # Check each character position
        for i in range(len(expected)):
            if i >= len(spoken):
                break
                
            # Check single character mappings
            if expected[i] in phonetic_map and spoken[i] in phonetic_map[expected[i]]:
                return True
                
            # Check two-character mappings
            if i < len(expected) - 1:
                expected_pair = expected[i:i+2]
                if i < len(spoken) - 1:
                    spoken_pair = spoken[i:i+2]
                    if expected_pair in phonetic_map and spoken_pair in phonetic_map[expected_pair]:
                        return True
        
        # Check endings
        endings = [('ing', 'in'), ('ed', 't'), ('s', 'z'), ('ly', 'li')]
        for end1, end2 in endings:
            if (expected.endswith(end1) and spoken.endswith(end2)) or \
               (expected.endswith(end2) and spoken.endswith(end1)):
                return True
        
        return False
    
    def _check_letter_sequence(self, spoken, expected):
        """Check for letter sequence errors"""
        if len(spoken) != len(expected):
            return False
            
        differences = sum(1 for a, b in zip(spoken, expected) if a != b)
        return differences == 2 and sorted(spoken) == sorted(expected)
    
    def analyze_speech(self, recognized_text, original_text):
        """Analyze full speech recognition results"""
        if not recognized_text or not original_text:
            return {
                "accuracy": 0,
                "words_recognized": 0,
                "total_words": len(original_text.split()),
                "errors": [],
                "word_analysis": []
            }
        
        recognized_words = recognized_text.lower().split()
        original_words = original_text.lower().split()
        
        word_analysis = []
        errors = []
        correct_words = 0
        
        for i, (spoken, expected) in enumerate(zip(recognized_words, original_words)):
            analysis = self.analyze_word(spoken, expected)
            
            if analysis['correct']:
                correct_words += 1
            else:
                errors.append({
                    "position": i,
                    "spoken": spoken,
                    "expected": expected,
                    "patterns": analysis['patterns']
                })
            
            word_analysis.append({
                "word": expected,
                "spoken": spoken,
                "correct": analysis['correct'],
                "similarity": analysis['similarity'],
                "patterns": analysis['patterns']
            })
        
        total_words = len(original_words)
        accuracy = (correct_words / total_words * 100) if total_words > 0 else 0
        
        return {
            "accuracy": round(accuracy, 2),
            "words_recognized": correct_words,
            "total_words": total_words,
            "errors": errors,
            "word_analysis": word_analysis
        }
    
    def real_time_recognition(self, callback=None, stop_after=None):
        """Perform real-time speech recognition with word-level analysis"""
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            start_time = time.time()
            while True:
                if stop_after and (time.time() - start_time) > stop_after:
                    break
                    
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio)
                    
                    if callback:
                        callback(text.lower())
                        
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    continue
                except sr.RequestError as e:
                    print(f"Recognition error: {e}")
                    break
                except KeyboardInterrupt:
                    break 