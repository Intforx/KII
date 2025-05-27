from flask import Flask, request, render_template
import os
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import openai
import uuid
from dotenv import load_dotenv

# 🔐 Umgebungsvariablen laden
load_dotenv()
OPENAI_API_KEY = os.getenv("OpenAi-API-Key")
openai.api_key = OPENAI_API_KEY

# 🧠 Modelle laden
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 🎨 Epochen-Datenbank
epochen = {
    "Impressionismus": "Helle Farben, flüchtige Pinselstriche, Natur, Licht und Atmosphäre",
    "Barock": "Dramatische Lichtführung, religiöse Themen, starker Kontrast und Bewegung",
    "Renaissance": "Perspektive, Symmetrie, klassische Architektur, menschliche Anatomie",
    "Expressionismuss": " Verzerrte Formen, starke Farben, emotionale Ausdrücke",
    "Klassizismus": "...",
    "Kubismus": "Geometrische Formen, mehrere Perspektiven, Abstraktion",
    "Realismus": "...",
    "Surrealismus": "...",
    "Wegbereiter der Moderne": "..."
}
epoche_names = list(epochen.keys())
epoche_vectors = embedding_model.encode(list(epochen.values()))
index = faiss.IndexFlatL2(epoche_vectors.shape[1])
index.add(np.array(epoche_vectors).astype("float32"))

# 📸 Bildbeschreibung generieren
def generate_caption(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

# 🔍 GPT zur Epochenzuordnung
def finde_epoche_mit_gpt(caption):
    epochen_prompt = "\n\n".join([f"{name}: {beschreibung}" for name, beschreibung in epochen.items()])
    prompt = (
        f"Du bist ein Kunsthistoriker. "
        f"Basierend auf der folgenden Bildbeschreibung:\n\n"
        f"\"{caption}\"\n\n"
        f"Ordne das Bild der am besten passenden Kunstepoche zu.\n"
        f"Hier sind die Beschreibungen der Epochen:\n\n"
        f"{epochen_prompt}\n\n"
        f"Gib mir den Namen der am besten passenden Epoche und eine kurze Begründung."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein Experte für Kunstgeschichte."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        antwort = response.choices[0].message["content"].strip()

        for name in epochen.keys():
            if name.lower() in antwort.lower():
                return name, antwort
        return "Unbekannt", antwort

    except Exception as e:
        print("OpenAI-Fehler:", e)
        return "Fehler", "Es gab ein Problem bei der Abfrage an GPT."

def gpt_kurzbeschreibung(caption):
    prompt = (
        f"Fasse die folgende Bildbeschreibung in einem Satz kurz zusammen:\n\n\"{caption}\""
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein Kunstexperte."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=60
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("OpenAI-Fehler:", e)
        return caption

# 🚀 Flask App
app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def analyse_bild():
    if "file" not in request.files:
        return "Kein Bild hochgeladen", 400

    file = request.files["file"]
    if file.filename == "":
        return "Dateiname leer", 400

    img_path = f"temp_{uuid.uuid4().hex}.jpg"
    file.save(img_path)

    try:
        caption = generate_caption(img_path)
        kurzbeschreibung = gpt_kurzbeschreibung(caption)
        epoche, gpt_antwort = finde_epoche_mit_gpt(caption)
    finally:
        os.remove(img_path)

    return render_template(
        "index.html",
        caption=caption,
        kurzbeschreibung=kurzbeschreibung,
        epoche=epoche,
        gpt_antwort=gpt_antwort
    )

if __name__ == "__main__":
    app.run(debug=True)
