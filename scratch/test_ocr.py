import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.services.ocr import ocr_receipt

if __name__ == "__main__":
    # Test with one of the existing images
    image_path = "data/receipts/02173f69-5bd7-49fb-8295-b3e9e2bc11a2.jpg"
    print(f"Testing OCR with {image_path}...")
    result = ocr_receipt(image_path)
    print("\nOCR Result:")
    print(result)
