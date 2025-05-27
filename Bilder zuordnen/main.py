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
    "Expressionismus": "Verzerrte Formen, starke Farben, emotionale Ausdrücke",
    "Klassizismus": "...",
    "Kubismus": "Geometrische Formen, mehrere Perspektiven, Abstraktion",
    "Realismus": "...",
    "Surrealismus": "...",
    "Wegbereiter der Moderne": "..."
}
epoche_vectors = embedding_model.encode(list(epochen.values()))
index = faiss.IndexFlatL2(epoche_vectors.shape[1])
index.add(np.array(epoche_vectors).astype("float32"))

# 🖼️ Bildbeschreibung mit BLIP + GPT
def generate_verbesserte_bildbeschreibung(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(image, return_tensors="pt")
        out = model.generate(**inputs)
        raw_caption = processor.decode(out[0], skip_special_tokens=True)

        prompt = (
            f"Das folgende ist eine automatisch generierte Bildbeschreibung: \"{raw_caption}\"\n\n"
            f"Formuliere daraus eine kunsthistorisch fundierte, prägnante und stilistisch saubere Beschreibung des Bildes in einem Satz."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Du kannst hier auch gpt-4 verwenden, wenn verfügbar
            messages=[
                {"role": "system", "content": "Du bist ein Kunsthistoriker."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=100
        )
        return response.choices[0].message["content"].strip()

    except Exception as e:
        print("Fehler bei der Caption-Erstellung:", e)
        return "Fehler bei der Beschreibungserstellung."

# 🔍 Epoche zuordnen via GPT
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
            model="gpt-3.5-turbo",
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

# 🚀 Flask App
app = Flask(__name__, template_folder="templates")

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
        beschreibung = generate_verbesserte_bildbeschreibung(img_path)
        epoche_caption, antwort_caption = finde_epoche_mit_gpt(beschreibung)
    finally:
        os.remove(img_path)

    return render_template(
        "index.html",
        caption=beschreibung,
        epoche_caption=epoche_caption,
        gpt_antwort_caption=antwort_caption
    )

if __name__ == "__main__":
    app.run(debug=True)
