from pathlib import Path
import ollama
import json
from ..core.config import OLLAMA_HOST, OLLAMA_MODEL

BASE_DIR = Path(__file__).parent.parent.parent

client = ollama.Client(host=OLLAMA_HOST)


# Prompt plus strict
prompt = """Extraire ces 4 champs du ticket :
- company (nom de l'entreprise)
- date (JJ/MM/AAAA)
- total (nombre décimal sans devise)
- address (adresse courte)
Répondre uniquement par un objet JSON standard."""


def ocr_receipt(image_path: str):
    # 1. Charger l'image en binaire
    # Si le chemin est relatif, on le joint à BASE_DIR.
    # Si c'est déjà un chemin absolu, Path le gèrera correctement.
    img_path = Path(image_path)
    if not img_path.is_absolute():
        img_path = BASE_DIR / img_path

    with open(img_path, "rb") as file:
        image_data = file.read()
    # 2. Envoyer la requête
    try:
        response = client.chat(
            model=OLLAMA_MODEL,
            format="json",
            messages=[{"role": "user", "content": prompt, "images": [image_data]}],
            options={"temperature": 0.0, "num_predict": 256},
        )
        raw_content = response["message"]["content"].strip()

        # Nettoyage rudimentaire si le JSON est entouré de texte ou de markdown
        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[-1].split("```")[0].strip()
        elif "```" in raw_content:
            raw_content = raw_content.split("```")[-1].split("```")[0].strip()

        data = json.loads(raw_content)

        # Calculate confidence based on field completeness
        filled_fields = sum(1 for v in data.values() if v)
        confidence = filled_fields / 4

        return {**data, "confidence": confidence}
    except Exception as e:
        print(f"Erreur OCR: {e}")
        return None
