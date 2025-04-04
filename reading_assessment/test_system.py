import requests
import json
import os
import time

BASE_URL = 'http://localhost:5001'

def test_reading_assessment():
    print("Testing Reading Assessment System...")
    
    # 1. Start a reading assessment
    print("\n1. Starting reading assessment...")
    response = requests.post(f'{BASE_URL}/api/reading/start', 
                           json={'difficulty': 'medium'})
    print(f"Response: {response.json()}")
    
    # Get the passage and audio URL
    passage = response.json()['passage']
    audio_url = response.json()['audio_url']
    
    # 2. Analyze reading (simulating user reading)
    print("\n2. Analyzing reading...")
    analysis_data = {
        'user_reading': passage,  # Perfect reading for testing
        'original_text': passage,
        'reading_time': 30  # 30 seconds reading time
    }
    
    response = requests.post(f'{BASE_URL}/api/reading/analyze', 
                           json=analysis_data)
    print(f"Analysis Results: {response.json()}")
    
    # 3. Save results
    print("\n3. Saving results...")
    response = requests.post(f'{BASE_URL}/api/reading/save-result', 
                           json=response.json())
    print(f"Save Response: {response.json()}")
    
    # 4. Train the model
    print("\n4. Training the model...")
    response = requests.post(f'{BASE_URL}/api/model/train')
    print(f"Training Results: {response.json()}")

if __name__ == '__main__':
    # Wait for the server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    try:
        test_reading_assessment()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nError during testing: {str(e)}") 