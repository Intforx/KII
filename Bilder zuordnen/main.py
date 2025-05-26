from flask import Flask, request, jsonify, render_template
import os
import shutil
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import requests
from dotenv import load_dotenv

# 🔐 Umgebungsvariablen laden
load_dotenv()
OPENAI_API_KEY = os.getenv("OpenAi-API-Key")

# 🧠 Modelle laden
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 🎨 Epochen-Datenbank
epochen = {
    "Impressionismus": "keine harten Konturen, verschwimmen der Umrisse, Helle Farbpalette, flüchtige und kurze Pinselstriche, nebeneinanderliegende Farbpunkte, Natur, Licht, Atmosphäre",
    "Barock": "detaillierte und exakte Formensprache, Gegenstandsfarbe, farbe pastos aufgetragen, scheinwerferartiges licht, hintergrund oft sehr dunkel, Verdeckung klarer raumgrenzen, asymmetrie im bildaufbau, Dramatische Lichtführung, religiöse Themen, starker Kontrast, Bewegung",
    "Renaissance": "Menschen naturgetreu dargestellt, idealisierte Welt mit perfektionierten Menschen und Landschaften, Perspektive, Symmetrie, klassische Architektur, menschliche Anatomie",
    "Expressionismuss": "Figuren stark verzerrt, verzicht auf details, sichtbarer pinselduktus, gegenteil vom Impressionismus, Reduzierung der form, Form teils grob, starke Kontraste, keine naturgetreue wiedergabe, Verzerrte Formen, starke Farben, emotionale Ausdrücke",
    "Klassizismus": "antike statuen und wahrgenommenes Schönheitsbild, Tempelmotiv, Säulenreihe, ideal proportionierte, makellose Körper der Götter, religiöse und mythologische Motive, Harmonie, Strenge formale Kompositon, harte Umrisse, wenig Farben, verzicht auf Raumwirkung",
    "Kubismus": "in prismatische flächen zergliedert, raum wird in facetten zergliedert, grau- und blautöne, keine bunten farben, häufung von Licht- und Schattenpartien, Überlagerung einzelner Flächen, Vorder- und Hintegrund sind ineinander verschränkt, Geometrische Formen, mehrere Perspektiven, Abstraktion",
    "Realismus": "erdfarben, wirklichkeitsgetreue farbwahl, malweise ist exakt und lasierend oder pastos und ungenau, szenen aus alltäglichen leben, alltägliche und hässliche ist bildmotiv, betonung der Objektivität und wirklichkeit",
    "Surrealismus": "traumhafte und unwirkliche Situationen, gegenständliche orientierende Darstellung, Figuren/Räume/Gegenstände exakt und naturgetreu dargestellt",
    "Wegbereiter der Moderne": "starke Konturen, keine reale Farbgebung, reine Farben, Formen stark vereinfacht, Räumlichkeit durch Farbe erzeugt, Formen auf geometrische Grunkörper reduziert",
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

# 🔍 Epoche finden
def finde_epoche(caption):
    caption_vec = embedding_model.encode([caption])
    D, I = index.search(np.array(caption_vec).astype("float32"), 1)
    return epoche_names[I[0][0]]

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
    img_path = f"temp_{file.filename}"
    file.save(img_path)

    caption = generate_caption(img_path)
    epoche = finde_epoche(caption)
    os.remove(img_path)

    return render_template("index.html", caption=caption, epoche=epoche)

@app.route("/generate-image", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt")

    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "prompt": prompt,
            "n": 1,
            "size": "512x512"
        }
    )

    if response.status_code == 200:
        image_url = response.json()["data"][0]["url"]
        return jsonify({"imageUrl": image_url})
    else:
        return jsonify({"error": response.text}), 500

if __name__ == "__main__":
    app.run(port=3000, debug=True)
