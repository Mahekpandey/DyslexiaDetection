import pytesseract
from PIL import Image
import os

def test_tesseract():
    try:
        # Test if pytesseract can find tesseract executable
        print("Tesseract Version:", pytesseract.get_tesseract_version())
        print("Tesseract is working correctly!")
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    test_tesseract() 