import speech_recognition as sr
import pyttsx3
import time

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        # Optimize recognition settings
        self.recognizer.energy_threshold = 3000  # Adjusted for better balance
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8  # Reduced to be more responsive
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5

    def text_to_speech(self, text):
        """Convert text to speech and read it aloud"""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_and_recognize(self, duration=None):
        """Record audio and convert to text"""
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                
                audio = self.recognizer.listen(
                    source,
                    timeout=10 if duration is None else duration,
                    phrase_time_limit=10 if duration is None else duration
                )
                
                print("Recognition in progress...")
                text = self.recognizer.recognize_google(
                    audio,
                    language='en-US',
                    show_all=False
                )
                print(f"Recognized text: {text}")
                
                if text and len(text.strip()) > 0:
                    return text.strip().lower()
                    
        except sr.WaitTimeoutError:
            print("No speech detected. Please try again.")
        except sr.UnknownValueError:
            print("Could not understand the audio. Please speak clearly.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Error: {e}")
                
        return ""

    def analyze_reading(self, original_text, spoken_text):
        """Compare original text with spoken text and return analysis"""
        try:
            # Clean up the input texts
            original_text = str(original_text).lower().strip()
            
            # Extract text from JSON if needed
            if isinstance(spoken_text, str):
                if spoken_text.startswith('{'):
                    try:
                        import json
                        spoken_dict = json.loads(spoken_text.replace("'", '"'))
                        spoken_text = spoken_dict.get('recognized_text', '')
                    except:
                        # If JSON parsing fails, remove the JSON-like structure manually
                        if "recognized_text" in spoken_text:
                            spoken_text = spoken_text.split("recognized_text': '")[1].split("'")[0]
            
            spoken_text = str(spoken_text).lower().strip()
            
            # Clean and split texts into words
            original_words = [word.strip('.,!?') for word in original_text.split()]
            spoken_words = [word.strip('.,!?') for word in spoken_text.split()]
            
            # Calculate accuracy
            correct_words = 0
            errors = []
            
            # Compare words and track errors
            for i, orig_word in enumerate(original_words):
                if i < len(spoken_words):
                    spoken_word = spoken_words[i]
                    if orig_word == spoken_word:
                        correct_words += 1
                    else:
                        errors.append({
                            "expected": orig_word,
                            "spoken": spoken_word,
                            "index": i
                        })
                else:
                    errors.append({
                        "expected": orig_word,
                        "spoken": "(missing)",
                        "index": i
                    })
            
            # Calculate accuracy percentage
            total_words = len(original_words)
            accuracy = (correct_words / total_words * 100) if total_words > 0 else 0
            
            # Calculate reading speed (words per minute)
            reading_time = 30  # seconds
            words_per_minute = (len(spoken_words) / reading_time) * 60 if spoken_words else 0
            
            return {
                "accuracy": round(accuracy, 2),
                "total_words": total_words,
                "correct_words": correct_words,
                "words_per_minute": round(words_per_minute, 2),
                "errors": errors,
                "recognized_text": spoken_text,
                "original_text": original_text
            }
        except Exception as e:
            print(f"Error in analyze_reading: {str(e)}")
            return {
                "accuracy": 0,
                "total_words": 0,
                "correct_words": 0,
                "words_per_minute": 0,
                "errors": [],
                "recognized_text": spoken_text,
                "original_text": original_text
            }

    def words_are_similar(self, word1, word2):
        """Check if two words are similar enough to be considered the same"""
        # If words are short, they need to be more similar
        if len(word1) <= 3 or len(word2) <= 3:
            return word1 == word2
        
        # For longer words, allow some variation
        if len(word1) != len(word2):
            return False
        
        differences = sum(1 for a, b in zip(word1, word2) if a != b)
        max_differences = len(word1) // 3  # Allow up to 1/3 of characters to be different
        
        return differences <= max_differences 