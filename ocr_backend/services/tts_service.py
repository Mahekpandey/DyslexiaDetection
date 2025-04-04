import os
import pyttsx3
from gtts import gTTS
import hashlib
import logging
from typing import Tuple, Optional
import time

class TTSService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache', 'tts')
        self._ensure_cache_dir()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Slower speech rate for better clarity
    
    def _ensure_cache_dir(self):
        """Ensure the cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_key(self, text: str, engine: str) -> str:
        """Generate a cache key for the text"""
        return hashlib.md5(f"{text}_{engine}".encode()).hexdigest()
    
    def _get_cached_file(self, text: str, engine: str) -> Optional[str]:
        """Check if a cached audio file exists"""
        cache_key = self._get_cache_key(text, engine)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.mp3")
        
        if os.path.exists(cache_file):
            # Check if file is less than 24 hours old
            if time.time() - os.path.getmtime(cache_file) < 24 * 3600:
                return cache_file
            else:
                # Remove old cache file
                os.remove(cache_file)
        return None
    
    def text_to_speech(self, text: str, engine: str = 'pyttsx3') -> Tuple[bool, str, Optional[str]]:
        """
        Convert text to speech using specified engine
        
        Args:
            text: Text to convert to speech
            engine: Engine to use ('pyttsx3' or 'gtts')
            
        Returns:
            Tuple of (success, message, audio_file_path)
        """
        try:
            # Check cache first
            cached_file = self._get_cached_file(text, engine)
            if cached_file:
                return True, "Using cached audio file", cached_file
            
            # Generate cache key
            cache_key = self._get_cache_key(text, engine)
            output_file = os.path.join(self.cache_dir, f"{cache_key}.mp3")
            
            if engine == 'pyttsx3':
                # Use pyttsx3 for offline TTS
                self.engine.save_to_file(text, output_file)
                self.engine.runAndWait()
                
            elif engine == 'gtts':
                # Use gTTS for online TTS
                tts = gTTS(text=text, lang='en', slow=True)
                tts.save(output_file)
                
            else:
                return False, f"Unsupported engine: {engine}", None
            
            return True, "Audio generated successfully", output_file
            
        except Exception as e:
            error_msg = f"Error generating speech: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def cleanup_cache(self, max_age_hours: int = 24) -> Tuple[bool, str]:
        """
        Clean up old cache files
        
        Args:
            max_age_hours: Maximum age of cache files in hours
            
        Returns:
            Tuple of (success, message)
        """
        try:
            current_time = time.time()
            removed_count = 0
            
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    if current_time - os.path.getmtime(filepath) > max_age_hours * 3600:
                        os.remove(filepath)
                        removed_count += 1
            
            return True, f"Cleaned up {removed_count} old cache files"
            
        except Exception as e:
            error_msg = f"Error cleaning up cache: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg 