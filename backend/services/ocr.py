from backend.services.json_format import normalize
import json
import io
import torch
from pathlib import Path
from PIL import Image
from transformers import pipeline, GenerationConfig
import gc

from .image_processing import preprocess_image

BASE_DIR = Path(__file__).parent.parent.parent


# Load the local tiny multimodal model using the pipeline for easier management
device = -1
generator = pipeline(
    "image-text-to-text",
    model="gueye07/SmolVLM-256M-Instruct-FineTuned-Merged-NoTrainer",
    dtype=torch.bfloat16,
    device=device,
    trust_remote_code=True
)

prompt = (
    "Look at this receipt image. "
    "Return ONLY a single JSON object with exactly these four keys and nothing else:\n"
    '{"company": "<store name>", "date": "<YYYY-MM-DD>", '
    '"address": "<store address>", "total": "<amount as number>"}'
)


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
                {"type": "image", "image": image},
                {"type": "text", "text": prompt}
            ]
        },
    ]

    try:
        # Per the HF docs, GenerationConfig is the correct way to override the model's
        # saved generation_config.json (which has max_length=20 causing the conflict).
        # Passing it as `generation_config=` routes it to model.generate(), not the processor.
        # The processor emits a non-fatal warning about it but correctly ignores it.
        config = GenerationConfig(
            do_sample=False,         # greedy decoding — deterministic, best for structured JSON
            repetition_penalty=1.3,
            max_new_tokens=128,
            max_length=512,          # explicitly override the model's saved max_length=20
        )
        outputs = generator(
            messages,
            generation_config=config,
        )
        
        # Extract assistant content from the conversation history
        decoded = outputs[0]["generated_text"][-1]["content"]
        print("generated_content: ", decoded)
        
        # Extract assistant content and ensure it starts with our expected JSON brace
        raw_content = decoded
        if "{" in raw_content:
            raw_content = "{" + raw_content.split("{", 1)[-1]
        
        # Robustly parse JSON using the helper from json_format
        from .json_format import repair_json
        data = repair_json(raw_content)
        
        if not data:
            print(f"Failed to parse JSON from: {raw_content}")
            return None

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
    finally:
        # On aide le Garbage Collector
        gc.collect()