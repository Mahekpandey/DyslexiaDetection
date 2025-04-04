import requests
import json
import time
from datetime import datetime

BASE_URL = 'http://localhost:5001'

def test_speech_recognition():
    """Test the speech recognition functionality"""
    print("\nTesting Speech Recognition System...")
    
    # 1. Start a reading assessment to get a passage
    print("\n1. Getting a reading passage...")
    response = requests.post(f'{BASE_URL}/api/reading/start', 
                           json={'difficulty': 'easy'})
    
    if response.status_code == 200:
        data = response.json()
        passage = data['passage']
        print(f"Passage to read: {passage}")
    else:
        print("Error getting passage")
        return
    
    # 2. Record speech
    print("\n2. Recording speech (5 seconds)...")
    print("Please read the following passage:")
    print(passage)
    print("\nRecording will start in 3 seconds...")
    time.sleep(3)
    
    response = requests.post(f'{BASE_URL}/api/speech/record', 
                           json={'duration': 5})
    
    if response.status_code == 200:
        data = response.json()
        audio_path = data['audio_path']
        print(f"Recording saved to: {audio_path}")
    else:
        print("Error recording speech")
        return
    
    # 3. Transcribe speech
    print("\n3. Transcribing speech...")
    response = requests.post(f'{BASE_URL}/api/speech/transcribe', 
                           json={'audio_path': audio_path})
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            transcribed_text = data['text']
            print(f"Transcribed text: {transcribed_text}")
        else:
            print(f"Transcription error: {data['error']}")
            return
    else:
        print("Error transcribing speech")
        return
    
    # 4. Analyze speech
    print("\n4. Analyzing speech...")
    response = requests.post(f'{BASE_URL}/api/speech/analyze', 
                           json={
                               'recognized_text': transcribed_text,
                               'original_text': passage
                           })
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            analysis = data['analysis']
            print("\nAnalysis Results:")
            print(f"Accuracy: {analysis['accuracy']}%")
            print(f"Words Recognized: {analysis['words_recognized']}/{analysis['total_words']}")
            print(f"Dyslexia Probability: {analysis.get('dyslexia_probability', 'N/A')}")
            
            if analysis.get('errors'):
                print("\nErrors found:")
                for error in analysis['errors']:
                    print(f"Position {error['position']}: Said '{error['spoken']}' instead of '{error['expected']}'")
        else:
            print("Analysis failed")
    else:
        print("Error analyzing speech")

if __name__ == '__main__':
    # Wait for the server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    try:
        test_speech_recognition()
        print("\nTest completed!")
    except Exception as e:
        print(f"\nError during testing: {str(e)}") 