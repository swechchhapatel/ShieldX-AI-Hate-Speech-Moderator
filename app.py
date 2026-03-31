# ======================================================
# AI Hate Speech & Cyberbullying Moderator (Flask API)
# ======================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import re
import nltk
import traceback
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ---------------------------------------
# NLTK Data Setup
# ---------------------------------------
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# ---------------------------------------
# Model and Vectorizer Loading
# ---------------------------------------
try:
    model = joblib.load('hate_speech_model.pkl')
    tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')
    print("✅ Model and vectorizer loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load model/vectorizer: {e}")
    raise e

# ---------------------------------------
# Preprocessing Setup
# ---------------------------------------
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text: str) -> str:
    """Clean, tokenize, and lemmatize text"""
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]
    return " ".join(tokens)

# ---------------------------------------
# Flask App Configuration
# ---------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
  # Enable CORS for all routes

# ---------------------------------------
# /predict Route (for manual text testing)
# ---------------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(force=True)
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Empty text', 'confidence': 0.0, 'label': 'Unknown'}), 400

        cleaned = preprocess_text(text)
        if not cleaned:
            return jsonify({'error': 'No meaningful content after cleaning', 'confidence': 0.0, 'label': 'Unknown'}), 400

        vector = tfidf_vectorizer.transform([cleaned])
        prediction = model.predict(vector)[0]

        # Confidence Handling
        try:
            proba = model.predict_proba(vector)[0]
            confidence = float(max(proba))
        except Exception:
            confidence = 0.5

        label = "Hate Speech/Bullying" if int(prediction) == 1 else "Safe"
        return jsonify({
            'label': label,
            'confidence': round(confidence, 3),
            'original_text': text
        })

    except Exception as e:
        print("❌ Error in /predict:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ---------------------------------------
# /moderate Route (for Chrome Extension)
# ---------------------------------------
@app.route('/moderate', methods=['POST'])
def moderate():
    """
    Handles multiple comments at once for moderation.
    Input:
        {
          "comments": [
             {"id": "1", "text": "you are an idiot"},
             {"id": "2", "text": "have a great day"}
          ]
        }
    Output:
        {
          "results": [
             {"id": "1", "is_hate": true, "confidence": 0.98, "text": "you are an idiot"},
             {"id": "2", "is_hate": false, "confidence": 0.15, "text": "have a great day"}
          ]
        }
    """
    try:
        data = request.get_json(force=True)
        comments = data.get('comments', [])
        if not comments:
            return jsonify({'error': 'No comments received'}), 400

        results = []
        texts = [preprocess_text(c.get('text', '')) for c in comments]
        valid_indices = [i for i, t in enumerate(texts) if t.strip()]

        if not valid_indices:
            return jsonify({'results': []})

        # Vectorize all valid texts in one go for performance
        vectors = tfidf_vectorizer.transform([texts[i] for i in valid_indices])
        preds = model.predict(vectors)

        try:
            probas = model.predict_proba(vectors)
        except Exception:
            probas = [[0.5, 0.5] for _ in preds]

        for i, idx in enumerate(valid_indices):
            text = comments[idx].get('text', '')
            comment_id = comments[idx].get('id', '')
            prediction = preds[i]
            confidence = float(max(probas[i]))

            results.append({
                'id': comment_id,
                'text': text,
                'is_hate': bool(prediction == 1),
                'confidence': round(confidence, 3)
            })

        return jsonify({'results': results})

    except Exception as e:
        print("❌ Error in /moderate:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ---------------------------------------
# Server Entry Point
# ---------------------------------------
if __name__ == '__main__':
    print("🚀 AI Hate Speech Moderator running at: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
