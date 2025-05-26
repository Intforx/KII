import os
import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

# 🔑 Deine API-Zugangsdaten
API_KEY = "bs-943429ledjpeg-gruppe2"
API_URL = "https://lm3.hs-ansbach.de/worker2/v1/chat/completions"

# 🖼️ Bildbeschreibung mit BLIP
def generate_caption(image_path):
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    raw_image = Image.open(image_path).convert("RGB")
    inputs = processor(raw_image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

# 🧠 Kunstepochen als Wissensbasis (RAG-Kontext)
def prepare_retriever():
    beschreibungen = [
        Document(page_content="Impressionismus: keine harten Konturen, verschwimmen der Umrisse, Helle Farbpalette, flüchtige und kurze Pinselstriche, nebeneinanderliegende Farbpunkte, Natur, Licht, Atmosphäre."),
        Document(page_content="Barock: detaillierte und exakte Formensprache, Gegenstandsfarbe, farbe pastos aufgetragen, scheinwerferartiges licht, hintergrund oft sehr dunkel, Verdeckung klarer raumgrenzen, asymmetrie im bildaufbau, Dramatische Lichtführung, religiöse Themen, starker Kontrast, Bewegung."),
        Document(page_content="Renaissance: Menschen naturgetreu dargestellt, idealisierte Welt mit perfektionierten Menschen und Landschaften, Perspektive, Symmetrie, klassische Architektur, menschliche Anatomie."),
        Document(page_content="Expressionismus: Figuren stark verzerrt, verzicht auf details, sichtbarer pinselduktus, gegenteil vom Impressionismus, Reduzierung der form, Form teils grob, starke Kontraste, keine naturgetreue wiedergabe, Verzerrte Formen, starke Farben, emotionale Ausdrücke."),
        Document(page_content="Klassizismus: orientierung an antiken statuen und wahrgenommenen Schönheitsbild, Tempelmotiv, Säulenreihe, ideal proportionierte, makellose Körper der Götter, religiöse und mythologische Motive, Harmonie, Strenge formale Kompositon, harte Umrisse, zurückgesetzte Farbigkeit, verzicht auf Raumwirkung."),
        Document(page_content="Kubismus: in prismatische flächen zergliedert, raum wird in facetten zergliedert, grau- und blautöne, keine bunten farben, häufung von Licht- und Schattenpartien, Überlagerung einzelner Flächen, Vorder- und Hintegrund sind ineinander verschränkt, Geometrische Formen, mehrere Perspektiven, Abstraktion."),
        Document(page_content="Realismus: erdfarben, wirklichkeitsgetreue farbwahl, malweise ist exakt und lasierend oder pastos und ungenau, szenen aus alltäglichen leben, alltägliche und hässliche ist bildmotiv, betonung der Objektivität und wirklichkeit."),
        Document(page_content="Surrealismus: traumhafte und unwirkliche Situationen, gegenständliche orientierende Darstellung, Figuren/Räume/Gegenstände exakt und naturgetreu dargestellt."),
        Document(page_content="Wegbereiter der Moderne: starke Konturen, keine reale Farbgebung, reine Farben, Formen stark vereinfacht, Räumlichkeit durch Farbe erzeugt, Formen auf geometrische Grunkörper reduziert."),
    ]
 
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(beschreibungen, embeddings).as_retriever()

retriever = prepare_retriever()

# 📋 Prompt erstellen
def baue_prompt(caption, kontext):
    return f"""
Du bist ein erfahrener Kunsthistoriker. Analysiere das folgende Bild auf Basis der Beschreibung und weise es einer der passenden Kunstepoche (Impressionismus, Barock, Renaissance, Expressionismus, Klassizismus, Kubismus, Realismus, Surrealismus und Wegbereiter der Moderne) zu.

Bildbeschreibung:
{caption}

Hilfskontext (Epoche-Merkmale):
{kontext}

Welche Kunstepoche passt am besten zu diesem Bild? Begründe deine Einschätzung in ein bis zwei Sätzen.
"""

# 🤖 Anfrage an LLM stellen
def frage_llm(prompt):
    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Du bist der Kunstexperte Palette, ein Spezialist für Kunstepochen."},
                {"role": "user", "content": prompt}
            ]
        }
    )
    if response.status_code != 200:
        raise Exception(f"Fehler vom Modellserver: {response.text}")
    return response.json()["choices"][0]["message"]["content"]

# ▶️ Hauptfunktion
def analysiere_bild(image_path):
    print("🔍 Erzeuge Bildbeschreibung...")
    caption = generate_caption(image_path)
    print("📄 Beschreibung:", caption)

    print("📚 Suche relevante Kunstepochen...")
    docs = retriever.get_relevant_documents(caption)
    kontext = "\n".join([doc.page_content for doc in docs])

    prompt = baue_prompt(caption, kontext)
    print("✉️ Sende an LLM...")
    antwort = frage_llm(prompt)
    return antwort

# ✅ Test-Aufruf
if __name__ == "__main__":
    bildpfad = "Impressionismus.jpg"  # ← ersetze durch dein eigenes Bild
    ergebnis = analysiere_bild(bildpfad)
    print("\n🎨 Ergebnis:\n", ergebnis)