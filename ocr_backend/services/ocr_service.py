import easyocr
import pytesseract
from PIL import Image
import cv2
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        try:
            self.reader = easyocr.Reader(['en'])
            logger.info("EasyOCR initialized successfully")
            
            # Configure Tesseract parameters
            custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
            self.tesseract_config = custom_config
            
        except Exception as e:
            logger.error(f"Failed to initialize OCR service: {str(e)}")
            raise

    def preprocess_image(self, image):
        """
        Enhanced image preprocessing for better OCR results
        """
        try:
            # Convert to grayscale if image is in color
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Get image dimensions
            height, width = gray.shape
            
            # Resize if image is too large (helps with OCR accuracy)
            max_dimension = 2000
            if height > max_dimension or width > max_dimension:
                scale = max_dimension / max(height, width)
                gray = cv2.resize(gray, None, fx=scale, fy=scale)
            
            # Denoise
            gray = cv2.fastNlMeansDenoising(gray)
            
            # Increase contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # Binarization
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Remove small noise
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
            gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            
            return gray
            
        except Exception as e:
            logger.error(f"Error in image preprocessing: {str(e)}")
            raise

    def process_image(self, image_path):
        """
        Process image using both EasyOCR and Tesseract with enhanced preprocessing
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to read image: {image_path}")

            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Save processed image for debugging
            debug_path = image_path + '_processed.png'
            cv2.imwrite(debug_path, processed_image)
            logger.info(f"Saved processed image for debugging: {debug_path}")
            
            # EasyOCR processing
            try:
                easyocr_result = self.reader.readtext(processed_image)
                easyocr_text = ' '.join([text[1] for text in easyocr_result])
                logger.info("EasyOCR processing completed successfully")
            except Exception as e:
                logger.error(f"EasyOCR processing failed: {str(e)}")
                easyocr_text = ""

            # Tesseract processing
            try:
                tesseract_text = pytesseract.image_to_string(
                    Image.fromarray(processed_image),
                    config=self.tesseract_config
                )
                logger.info("Tesseract processing completed successfully")
            except Exception as e:
                logger.error(f"Tesseract processing failed: {str(e)}")
                tesseract_text = ""

            # Select the better result or combine them
            if len(easyocr_text) > len(tesseract_text):
                final_text = easyocr_text
            else:
                final_text = tesseract_text

            # Log results for debugging
            logger.info(f"EasyOCR result length: {len(easyocr_text)}")
            logger.info(f"Tesseract result length: {len(tesseract_text)}")
            logger.info(f"Selected text length: {len(final_text)}")

            return {
                'success': True,
                'text': final_text.strip(),
                'easyocr_text': easyocr_text.strip(),
                'tesseract_text': tesseract_text.strip()
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 