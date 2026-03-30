# backend/app.py
from flask import Flask, request, jsonify
import joblib
from flask_cors import CORS
import re
import os

# --- PATH SETUP ---
base_dir = os.path.dirname(__file__)
model_path = os.path.join(base_dir, "model", "hate_model.pkl")
vectorizer_path = os.path.join(base_dir, "model", "vectorizer.pkl")

# --- FLASK APP ---
app = Flask(__name__)
CORS(app)  # allow Chrome extension access

# --- MODEL LOADING ---
model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

# --- TEXT CLEANING ---
def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^A-Za-z\s]", "", text)
    return text.lower().strip()

# --- ROUTES ---
@app.route("/")
def home():
    return jsonify({"message": "AI Hate Speech Moderator API is live!"})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "")
        if not text.strip():
            return jsonify({"error": "Empty text input"}), 400

        cleaned = clean_text(text)
        vec = vectorizer.transform([cleaned])
        prediction = int(model.predict(vec)[0])

        return jsonify({
            "text": text,
            "prediction": prediction
        })

    except Exception as e:
        import traceback
        print("Error during prediction:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
