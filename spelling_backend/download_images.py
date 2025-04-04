import requests
import os
from pathlib import Path

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}")

def main():
    # Create images directory if it doesn't exist
    images_dir = Path(__file__).parent / "static" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Sample images from reliable sources
    images = {
        "cat.jpg": "https://cdn.pixabay.com/photo/2014/11/30/14/11/cat-551554_640.jpg",
        "dog.jpg": "https://cdn.pixabay.com/photo/2016/12/13/05/15/puppy-1903313_640.jpg",
        "elephant.jpg": "https://cdn.pixabay.com/photo/2016/11/14/04/45/elephant-1822636_640.jpg",
        "giraffe.jpg": "https://cdn.pixabay.com/photo/2019/07/27/06/21/giraffe-4366005_640.jpg",
        "beautiful.jpg": "https://cdn.pixabay.com/photo/2014/09/14/18/04/dandelion-445228_640.jpg",
        "knowledge.jpg": "https://cdn.pixabay.com/photo/2015/11/19/21/10/knowledge-1052010_640.jpg",
        "psychology.jpg": "https://cdn.pixabay.com/photo/2019/09/29/21/24/brain-4514014_640.jpg",
        "phenomenon.jpg": "https://cdn.pixabay.com/photo/2011/12/14/12/21/orion-nebula-11107_640.jpg"
    }

    for filename, url in images.items():
        filepath = images_dir / filename
        if not filepath.exists():
            download_image(url, str(filepath))
        else:
            print(f"Image {filename} already exists")

if __name__ == "__main__":
    main() 