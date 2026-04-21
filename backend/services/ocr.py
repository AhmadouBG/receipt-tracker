import json
import base64
import io
import torch
import re
from pathlib import Path
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText

from .image_processing import preprocess_image

BASE_DIR = Path(__file__).parent.parent.parent

#Load the local tiny multimodal model (SmolVLM-256M-Instruct)
processor = AutoProcessor.from_pretrained("gueye07/qwen2_model_finetune")
model = AutoModelForImageTextToText.from_pretrained(
    "gueye07/qwen2_model_finetune",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
).to("cuda" if torch.cuda.is_available() else "cpu")
#Initialize Ollama client
#client = ollama.Client(host=OLLAMA_HOST)
prompt = """Extract company, date, address and total from this image as JSON"""
def ocr_receipt(image_path: str):
    img_path = Path(image_path)
    if not img_path.is_absolute():
        img_path = BASE_DIR / img_path

    # Apply intelligent OpenCV preprocessing before OCR
    image_bytes = preprocess_image(str(img_path))
    
    # Load the processed bytes into a PIL Image for Transformers
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt}
            ]
        },
    ]

    try:
        # We append "{" to the prompt to force the model to start the JSON immediately
        text_prompt = processor.apply_chat_template(messages, add_generation_prompt=True) + "{"
        
        # Prepare inputs for generation
        inputs = processor(text=text_prompt, images=[image], return_tensors="pt")
        inputs = inputs.to(model.device)

        # Generate output locally with repetition_penalty to avoid infinite loops
        generated_ids = model.generate(
            **inputs, 
            max_new_tokens=512,
            repetition_penalty=1.2  # Critical to stop "_tax_tax_tax" loops
        )
        generated_texts = processor.batch_decode(
            generated_ids, 
            skip_special_tokens=True
        )
        print("generated_texts: ", generated_texts)
        decoded = generated_texts[0]

        # Extract assistant content starting from our forced "{"
        if "Assistant:" in decoded:
            raw_content = "{" + decoded.split("Assistant:")[-1].split("{", 1)[-1]
        else:
            raw_content = "{" + decoded.split("{", 1)[-1] if "{" in decoded else decoded

        if not data:
            print(f"Raw content returned by model (Failed to parse):\n{raw_content}")
            raise ValueError("No valid JSON found after extraction or repair")

        # Normalize data (summing prices, formatting dates, etc.)
        data = normalize(data)

        # Ensure total is a float if possible for the database
        if data.get("total"):
            try:
                data["total"] = float(data["total"].replace(",", ".").replace("$", "").replace("€", "").strip())
            except:
                data["total"] = None

        print("✅ Final Normalized Result:", data)

        filled_fields = sum(1 for v in data.values() if v)
        confidence = filled_fields / 4

        return {**data, "confidence": confidence}
        
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError OCR: {e}")
        try:
            print(f"Raw content returned by model:\n{raw_content}")
        except:
            pass
        return None
    except Exception as e:
        print(f"Erreur OCR: {e}")
        import traceback
        traceback.print_exc()
        return None
