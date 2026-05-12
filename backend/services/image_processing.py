import cv2
import numpy as np
from PIL import Image, ImageOps, ImageStat
import io



def needs_contrast_adjustment(pil_img: Image.Image) -> bool:
    """Analyze image to see if it has low contrast or is too bright."""
    stat = ImageStat.Stat(pil_img.convert('L'))
    luminosity = stat.mean[0]
    contrast = stat.stddev[0]
    
    print(f"DEBUG - Image Analysis | Luminosity: {luminosity:.2f}, Contrast: {contrast:.2f}")
    
    # Thresholds provided by user
    if luminosity > 200 or contrast < 40:
        return True
    return False

def adjust_contrast(pil_img: Image.Image) -> Image.Image:
    """Apply aggressive autocontrast to the image."""
    gray_img = pil_img.convert('L')
    return ImageOps.autocontrast(gray_img, cutoff=5)

def preprocess_image(img_path: str) -> bytes:
    """Preprocess receipt image by warping perspective and adjusting contrast if needed."""
    image = cv2.imread(img_path)
    if image is None:
        with open(img_path, "rb") as file:
            return file.read()
    
    # Convert OpenCV image (BGR) to PIL Image (RGB)
    scanned_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(scanned_rgb)

    if needs_contrast_adjustment(pil_img):
        print("DEBUG - Contrast/Luminosity quality low. Applying autocontrast...")
        pil_img = adjust_contrast(pil_img)
    else:
        print("DEBUG - Image quality OK, skipping contrast adjustment.")

    # Save PIL image back to bytes
    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=95)
    
    # Save a debug copy for the user to see the result of preprocessing
    debug_path = img_path.replace(".jpg", "_debug_processed.jpg")
    pil_img.save(debug_path)
    
    return buffer.getvalue()
