import requests
import os

def test_ocr_endpoint():
    # URL of the OCR endpoint
    url = 'http://localhost:5001/api/ocr/upload'
    
    # Test case 1: No file
    print("\nTest Case 1: No file")
    response = requests.post(url, files={})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test case 2: Empty file
    print("\nTest Case 2: Empty file")
    response = requests.post(url, files={'file': ('', '')})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test case 3: Invalid file type
    print("\nTest Case 3: Invalid file type")
    with open('test.txt', 'w') as f:
        f.write('test')
    response = requests.post(url, files={'file': open('test.txt', 'rb')})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    os.remove('test.txt')

if __name__ == "__main__":
    test_ocr_endpoint() 