import requests
import os
import time
import json

def test_new_features():
    """Test the new text transformation and TTS features"""
    base_url = 'http://localhost:5001/api/ocr'
    
    # Test Case 1: Text Transformation
    print("\nTest Case 1: Text Transformation")
    transform_data = {
        'text': 'Hello World! This is a test for OpenDyslexic font.',
        'font_size': 36
    }
    response = requests.post(
        f"{base_url}/transform",
        json=transform_data
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test Case 2: Text to Speech (pyttsx3)
    print("\nTest Case 2: Text to Speech (pyttsx3)")
    tts_data = {
        'text': 'Hello World! This is a test for text to speech.',
        'engine': 'pyttsx3'
    }
    response = requests.post(
        f"{base_url}/speech",
        json=tts_data
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        # Save the audio file
        with open('test_speech_pyttsx3.mp3', 'wb') as f:
            f.write(response.content)
        print("Audio file saved as test_speech_pyttsx3.mp3")
    
    # Test Case 3: Text to Speech (gTTS)
    print("\nTest Case 3: Text to Speech (gTTS)")
    tts_data['engine'] = 'gtts'
    response = requests.post(
        f"{base_url}/speech",
        json=tts_data
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        # Save the audio file
        with open('test_speech_gtts.mp3', 'wb') as f:
            f.write(response.content)
        print("Audio file saved as test_speech_gtts.mp3")
    
    # Test Case 4: Cache Test (should use cached file)
    print("\nTest Case 4: Cache Test")
    response = requests.post(
        f"{base_url}/speech",
        json=tts_data
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Cached audio file retrieved successfully")
    
    # Test Case 5: Cleanup
    print("\nTest Case 5: Cleanup")
    response = requests.post(f"{base_url}/cleanup")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Clean up test files
    for file in ['test_speech_pyttsx3.mp3', 'test_speech_gtts.mp3']:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed test file: {file}")

if __name__ == "__main__":
    test_new_features() 