import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import requests
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@app.route("/")
def index():
    return render_template("index.html")  # index.html aus templates/ laden

@app.route("/generate-image", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt")
    
    if not prompt or prompt.strip() == "":
        return jsonify({"error": "Prompt cannot be empty"}), 400

    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "response_format": "url"
            },
            timeout=30
        )
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        return jsonify({"imageUrl": image_url})
        
    except requests.exceptions.RequestException as e:
        print(f"OpenAI API Error: {str(e)}")
        return jsonify({"error": "Failed to generate image. Please try again."}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    

if __name__ == "__main__":
    app.run(port=3000)
