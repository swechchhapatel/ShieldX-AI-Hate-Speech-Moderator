import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib # To save the model

# Download necessary NLTK data (run this once)
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Load Dataset
print("Loading dataset...")
df = pd.read_csv('train.csv') # Make sure the file is in the same directory

# For simplicity, let's create a binary target: 'toxic' (if any toxicity > 0.5) or 'safe'
df['toxic'] = (df[['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']].max(axis=1) > 0.5).astype(int)

# We'll work with a smaller sample for faster training initially. Remove this for the full dataset.
df = df.sample(frac=0.3, random_state=42)
print("Dataset loaded and target created.")

# Text Preprocessing
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

df['comment_text'] = df['comment_text'].fillna('')

def preprocess_text(text):
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'\brt\b', '', text)
    text = re.sub(r'&\w+;', '', text)

    text = re.sub(r'\s+', ' ', text).strip()

    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]

    return ' '.join(tokens)



print("Preprocessing text... This may take a while.")
df['cleaned_comment_text'] = df['comment_text'].apply(preprocess_text)
print("Text preprocessing complete.")

# Prepare features and labels
X = df['cleaned_comment_text']
y = df['toxic']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)



# Feature Extraction with TF-IDF
print("Vectorizing text...")
tfidf_vectorizer = TfidfVectorizer(max_features=5000) # You can increase max_features
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

# Train a Logistic Regression Model
print("Training model...")
model = LogisticRegression(random_state=42, max_iter=1000, class_weight={0: 1, 1: 3}) 
model.fit(X_train_tfidf, y_train)

# Make predictions
y_probs = model.predict_proba(X_test_tfidf)[:,1]
y_pred = (y_probs > 0.3).astype(int)   

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save the model and the vectorizer for later use in the Flask API
joblib.dump(model, 'hate_speech_model.pkl')
joblib.dump(tfidf_vectorizer, 'tfidf_vectorizer.pkl')
print("Model and vectorizer saved!")