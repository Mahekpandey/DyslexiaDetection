import os
from PIL import Image, ImageDraw, ImageFont
import logging
from typing import Tuple, Optional

class TextTransformService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.font_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'OpenDyslexic-Regular.otf')
        self._ensure_font_exists()
    
    def _ensure_font_exists(self):
        """Ensure the OpenDyslexic font exists"""
        if not os.path.exists(self.font_path):
            self.logger.error(f"OpenDyslexic font not found at {self.font_path}")
            raise FileNotFoundError(f"OpenDyslexic font not found at {self.font_path}")
    
    def transform_text(self, text: str, output_path: str, 
                      width: int = 800, height: int = 200,
                      font_size: int = 36) -> Tuple[bool, str]:
        """
        Transform text into an image using OpenDyslexic font
        
        Args:
            text: Text to transform
            output_path: Path to save the transformed image
            width: Width of the output image
            height: Height of the output image
            font_size: Size of the font to use
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create a white background image
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Load OpenDyslexic font
            font = ImageFont.truetype(self.font_path, font_size)
            
            # Calculate text dimensions
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Center the text
            x = (width - text_width) / 2
            y = (height - text_height) / 2
            
            # Draw the text
            draw.text((x, y), text, font=font, fill='black')
            
            # Save the image
            img.save(output_path)
            
            return True, "Text transformed successfully"
            
        except Exception as e:
            error_msg = f"Error transforming text: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_text_dimensions(self, text: str, font_size: int = 36) -> Tuple[int, int]:
        """
        Calculate the dimensions needed for the text
        
        Args:
            text: Text to measure
            font_size: Size of the font to use
            
        Returns:
            Tuple of (width, height)
        """
        try:
            # Create a temporary image to measure text
            img = Image.new('RGB', (1, 1))
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(self.font_path, font_size)
            
            # Get text dimensions
            text_bbox = draw.textbbox((0, 0), text, font=font)
            width = text_bbox[2] - text_bbox[0]
            height = text_bbox[3] - text_bbox[1]
            
            # Add padding
            width += 40
            height += 40
            
            return width, height
            
        except Exception as e:
            self.logger.error(f"Error calculating text dimensions: {str(e)}")
            return 800, 200  # Default dimensions 