from backend.services.json_format import normalize, extract_json_block, repair_json
import base64
import requests
import os
import time
import psutil
from pathlib import Path
from PIL import Image

from .image_processing import preprocess_image

BASE_DIR = Path(__file__).parent.parent.parent

# ---------------------------------------------------------------------------
# ⬇️  CHANGE THIS to the name you gave your model when running:
#     ollama create <MODEL_NAME> -f ollama/receipt_model/Modelfile
# ---------------------------------------------------------------------------
LLAMA_SERVER_URL = "http://receipt-llama-server:8080/v1/chat/completions"
# ⚠️  Must match the system message used during fine-tuning (confirmed from Colab inference log)
SYSTEM_MSG = "You are a helpful assistant."

PROMPT = (
    "<|vision_start|><|image_pad|><|vision_end|>"
    "Extract company, date, address and total from this receipt.\n"
    "If missing return null.\n"
    "Do NOT guess.\n"
    "Return ONLY valid JSON."
)


def _image_to_base64(image_bytes: bytes) -> str:
    """Encode raw image bytes to a base64 string for the Ollama API."""
    return base64.b64encode(image_bytes).decode("utf-8")


def get_ram_usage(pid):
    """Returns RAM usage of a process in MB."""
    try:
        process = psutil.Process(pid)
        return process.memory_info().rss / (1024 * 1024)
    except:
        return 0

def get_llama_server_ram():
    """Finds the llama-server process and returns its RAM usage in MB."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'llama-server' in proc.info['name'].lower():
                return proc.memory_info().rss / (1024 * 1024)
        except:
            continue
    return 0

def ocr_receipt(image_path: str):
    img_path = Path(image_path)
    if not img_path.is_absolute():
        img_path = BASE_DIR / img_path

    # ── 1. OpenCV preprocessing ──────────────────────────────────────────────
    image_bytes = preprocess_image(str(img_path))
    img_b64 = _image_to_base64(image_bytes)
    
    # ── 2. chat completions ───────────────────────────────────────────────────────
    payload = {
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
             "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": PROMPT
                    }
                ]
        }
    ],
    "temperature": 0.0,  # Strictement déterministe
    "top_p": 1.0,
    "max_tokens": 512,
    "stream": False
    }
    max_retries = 6 
    attempt = 0
    
    while attempt < max_retries:
        try:
            response = requests.post(LLAMA_SERVER_URL, json=payload, timeout=400)
            
            # Handle the "Loading model" case (llama.cpp server specific)
            if response.status_code == 503:
                error_data = response.json().get("error", {})
                if "Loading model" in error_data.get("message", ""):
                    attempt += 1
                    print(f"⏳ Server is still loading the model (attempt {attempt}/{max_retries}). Waiting 10s...")
                    time.sleep(10)
                    continue
            
            response.raise_for_status()
            raw_json = response.json()
            print("[Llama response]:", raw_json)

            # RAM Monitoring as requested
            backend_ram = get_ram_usage(os.getpid())
            server_ram = get_llama_server_ram()
            print("-" * 30)
            print(f"📊 RAM usage (Backend): {backend_ram:.2f} MB")
            if server_ram > 0:
                print(f"📊 RAM usage (Llama Server): {server_ram:.2f} MB")
            print("-" * 30)

            break
            
        except requests.exceptions.ConnectionError:
            print("❌ Server is not running at http://localhost:8080")
            return None
        except Exception as e:
            print(f"❌ Server error: {e}")
            if 'response' in locals():
                 print(f"Response content: {response.text}")
            return None
    else:
        print("❌ Server timed out while loading the model.")
        return None
    try:
        decoded = raw_json["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as e:
        print(f"❌ Erreur format OpenAI: {e}")
        return None

    if not decoded:
        print("⚠️ Ollama returned an empty response.")
        return None

    # ── 4. Parse JSON from the response ─────────────────────────────────────
    raw_content = extract_json_block(decoded) or decoded
    data = repair_json(raw_content)
    
    if not data:
        print(f"Failed to parse JSON from: {raw_content}")
        return None

    # ── 5. Normalize (dates, address, total) ────────────────────────────────
    data = normalize(data)

    if data.get("total"):
        try:
            data["total"] = float(
                str(data["total"])
                .replace(",", ".")
                .replace("$", "")
                .replace("€", "")
                .strip()
            )
        except Exception:
            data["total"] = None

    print("✅ Final Normalized Result:", data)

    filled_fields = sum(1 for v in data.values() if v)
    confidence = filled_fields / 4

    return {**data, "confidence": confidence}