from pathlib import Path
import ollama
import json
import re

# Obtenir le chemin absolu du dossier contenant ce script
BASE_DIR = Path(__file__).parent

client = ollama.Client(host='http://localhost:11434')

# 1. Charger l'image en binaire
with open(BASE_DIR / '001.jpg', 'rb') as file:
    image_data = file.read()

# Prompt plus strict
prompt = """Extraire ces 4 champs du ticket :
- company (nom de l'entreprise)
- date (JJ/MM/AAAA)
- total (nombre décimal sans devise)
- address (adresse courte)

Répondre uniquement par un objet JSON standard."""

# 2. Envoyer la requête
try:
    response = client.chat(
        model='qwen2.5vl:3b',
        format='json',
        messages=[
            {
                'role': 'user',
                'content': prompt,
                'images': [image_data]
            }
        ],
        options={
            "temperature": 0.0,
            "num_predict": 256 
        }
    )

    raw_content = response['message']['content'].strip()
    
    # Nettoyage rudimentaire si le JSON est entouré de texte ou de markdown
    if "```json" in raw_content:
        raw_content = raw_content.split("```json")[-1].split("```")[0].strip()
    elif "```" in raw_content:
        raw_content = raw_content.split("```")[-1].split("```")[0].strip()

    try:
        data = json.loads(raw_content)
        print(f"Entreprise : {data.get('company', 'N/A')}")
        print(f"Date       : {data.get('date', 'N/A')}")
        print(f"Total      : {data.get('total', 'N/A')}")
        print(f"Adresse    : {data.get('address', 'N/A')}")
    except json.JSONDecodeError as e:
        # Tentative de nettoyage des virgules traînantes courantes (trailing commas)
        try:
            cleaned_content = re.sub(r',\s*([\]}])', r'\1', raw_content)
            data = json.loads(cleaned_content)
            print(f"Entreprise : {data.get('company', 'N/A')}")
            print(f"Date       : {data.get('date', 'N/A')}")
            print(f"Total      : {data.get('total', 'N/A')}")
            print(f"Adresse    : {data.get('address', 'N/A')}")
        except:
            print(f"Erreur de décodage JSON : {e}")
            print(f"Contenu brut reçu : '{raw_content}'")

except Exception as e:
    print(f"Une erreur est survenue : {e}")