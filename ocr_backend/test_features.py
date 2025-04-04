import requests
import os
import time
import shutil
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_test_image(filename, text="Test OCR Text"):
    """Create a test image with text"""
    # Create a white background image
    img = Image.new('RGB', (800, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    # Add text to the image
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Center the text
    x = (800 - text_width) / 2
    y = (200 - text_height) / 2
    
    # Draw the text
    draw.text((x, y), text, font=font, fill='black')
    
    # Save the image
    img.save(filename)

def test_ocr_features():
    # Base URL
    base_url = 'http://localhost:5001/api/ocr'
    
    # Test Case 1: Health Check
    print("\nTest Case 1: Health Check")
    response = requests.get(f"{base_url}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test Case 2: No file upload
    print("\nTest Case 2: No file upload")
    response = requests.post(f"{base_url}/upload", files={})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test Case 3: Empty file
    print("\nTest Case 3: Empty file")
    response = requests.post(f"{base_url}/upload", files={'file': ('', '')})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test Case 4: Invalid file type
    print("\nTest Case 4: Invalid file type")
    with open('test.txt', 'w') as f:
        f.write('test')
    response = requests.post(f"{base_url}/upload", files={'file': open('test.txt', 'rb')})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    os.remove('test.txt')
    
    # Test Case 5: Valid image upload with text
    print("\nTest Case 5: Valid image upload with text")
    create_test_image('test.png', "Hello World! This is a test for OCR.")
    with open('test.png', 'rb') as f:
        response = requests.post(f"{base_url}/upload", files={'file': f})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    os.remove('test.png')
    
    # Test Case 6: File size limit
    print("\nTest Case 6: File size limit")
    # Create a large image (11MB)
    large_img = Image.new('RGB', (3000, 3000), color='white')
    draw = ImageDraw.Draw(large_img)
    draw.text((1500, 1500), "Large Image Test", fill='black')
    large_img.save('large.png', quality=100)
    with open('large.png', 'rb') as f:
        response = requests.post(f"{base_url}/upload", files={'file': f})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    os.remove('large.png')
    
    # Test Case 7: Manual cleanup
    print("\nTest Case 7: Manual cleanup")
    response = requests.post(f"{base_url}/cleanup")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test Case 8: Multiple file uploads
    print("\nTest Case 8: Multiple file uploads")
    for i in range(3):
        create_test_image(f'test_{i}.png', f"Test Text {i} for OCR")
        with open(f'test_{i}.png', 'rb') as f:
            response = requests.post(f"{base_url}/upload", files={'file': f})
        print(f"Upload {i+1} Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        os.remove(f'test_{i}.png')
        time.sleep(2)  # Increased wait time between uploads
    
    # Test Case 9: File cleanup after 24 hours
    print("\nTest Case 9: File cleanup simulation")
    # Create a test file with old timestamp
    create_test_image('old_file.png', "Old file test")
    old_time = time.time() - (25 * 3600)  # 25 hours old
    os.utime('old_file.png', (old_time, old_time))
    
    # Try to upload a new file (should trigger cleanup)
    create_test_image('new_file.png', "New file test")
    with open('new_file.png', 'rb') as f:
        response = requests.post(f"{base_url}/upload", files={'file': f})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Clean up test files
    os.remove('old_file.png')
    os.remove('new_file.png')

if __name__ == "__main__":
    test_ocr_features() 