import os
import requests
import logging

def setup_assets():
    """Set up required assets for the OCR backend"""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create necessary directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, 'assets')
    fonts_dir = os.path.join(assets_dir, 'fonts')
    cache_dir = os.path.join(base_dir, 'cache')
    tts_cache_dir = os.path.join(cache_dir, 'tts')
    
    # Create directories if they don't exist
    for directory in [assets_dir, fonts_dir, cache_dir, tts_cache_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
    
    # Download OpenDyslexic font
    font_url = "https://github.com/antijingoist/opendyslexic/raw/master/compiled/OpenDyslexic-Regular.otf"
    font_path = os.path.join(fonts_dir, 'OpenDyslexic-Regular.otf')
    
    if not os.path.exists(font_path):
        try:
            logger.info("Downloading OpenDyslexic font...")
            response = requests.get(font_url)
            response.raise_for_status()
            
            with open(font_path, 'wb') as f:
                f.write(response.content)
            
            logger.info("Successfully downloaded OpenDyslexic font")
        except Exception as e:
            logger.error(f"Error downloading OpenDyslexic font: {str(e)}")
            raise
    else:
        logger.info("OpenDyslexic font already exists")
    
    logger.info("Asset setup completed successfully")

if __name__ == "__main__":
    setup_assets() 