import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.services.ocr import ocr_receipt

if __name__ == "__main__":
    # Test with one of the existing images
    image_path = "data/receipts/7c9822e0-4168-4f09-a007-579034302e12.jpg"
    print(f"Testing OCR with {image_path}...")
    result = ocr_receipt(image_path)
    print("\nOCR Result:")
    print(result)
