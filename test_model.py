import pandas as pd
import joblib
import random
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Load the trained model and vectorizer
print("Loading model and vectorizer...")
model = joblib.load('hate_speech_model.pkl')
tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Load your dataset
print("Loading dataset...")
df = pd.read_csv('train.csv')

# Create the target variable (same as in training)
df['toxic'] = (df[['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']].max(axis=1) > 0.5).astype(int)

print(f"Dataset loaded: {len(df)} comments")
print(f"Toxic comments: {df['toxic'].sum()} ({df['toxic'].mean()*100:.2f}%)")

def test_random_samples(num_samples=20):
    """Test random samples from the dataset"""
    print(f"\n{'='*50}")
    print(f"TESTING {num_samples} RANDOM SAMPLES")
    print(f"{'='*50}")
    
    samples = df.sample(n=num_samples)
    
    for idx, row in samples.iterrows():
        text = row['comment_text']
        actual_label = "Toxic" if row['toxic'] == 1 else "Safe"
        
        # Preprocess and predict
        processed_text = preprocess_text(text)
        text_vector = tfidf_vectorizer.transform([processed_text])
        prediction = model.predict(text_vector)[0]
        confidence = model.predict_proba(text_vector)[0]
        
        predicted_label = "Toxic" if prediction == 1 else "Safe"
        confidence_score = max(confidence)
        
        print(f"\nSample {idx}:")
        print(f"Text: {text[:100]}...")
        print(f"Actual: {actual_label} | Predicted: {predicted_label}")
        print(f"Confidence: {confidence_score:.4f}")
        print(f"Match: {'✅' if actual_label == predicted_label else '❌'}")

def test_specific_cases():
    """Test specific edge cases"""
    print(f"\n{'='*50}")
    print("TESTING SPECIFIC EDGE CASES")
    print(f"{'='*50}")
    
    test_cases = [
        # Clear toxic examples
        "You are stupid and should leave forever!",
        "I hate you and everyone like you!",
        "This is disgusting and you are terrible!",
        "People like you should not exist!",
        
        # Clear safe examples
        "This is a wonderful and friendly conversation!",
        "I appreciate your help and support!",
        "Let's work together to solve this problem!",
        "Have a great day everyone!",
        
        # Edge cases (might be tricky)
        "This movie is so bad it should be banned!",
        "I strongly dislike your opinion!",
        "That was a terrible decision!",
        "This food tastes horrible!"
    ]
    
    for i, text in enumerate(test_cases):
        processed_text = preprocess_text(text)
        text_vector = tfidf_vectorizer.transform([processed_text])
        prediction = model.predict(text_vector)[0]
        confidence = model.predict_proba(text_vector)[0]
        
        predicted_label = "Toxic" if prediction == 1 else "Safe"
        confidence_score = confidence[1] if prediction == 1 else confidence[0]
        
        print(f"\nTest {i+1}:")
        print(f"Text: {text}")
        print(f"Predicted: {predicted_label}")
        print(f"Confidence: {confidence_score:.4f}")

def evaluate_model_performance():
    """Comprehensive model evaluation"""
    print(f"\n{'='*50}")
    print("COMPREHENSIVE MODEL EVALUATION")
    print(f"{'='*50}")
    
    # Use a subset for faster evaluation
    test_df = df.sample(n=1000, random_state=42)
    
    # Preprocess
    test_df['cleaned_text'] = test_df['comment_text'].apply(preprocess_text)
    X_test = tfidf_vectorizer.transform(test_df['cleaned_text'])
    y_true = test_df['toxic']
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Print metrics
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=['Safe', 'Toxic']))
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    print("\nConfusion Matrix:")
    print(cm)
    
    # Calculate accuracy
    accuracy = (y_true == y_pred).mean()
    print(f"\nOverall Accuracy: {accuracy:.4f}")

# You need to include the same preprocessing function from your training
def preprocess_text(text):
    """Same preprocessing as in train_model.py"""
    import re
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    if not isinstance(text, str):
        return ""
    
    try:
        text = text.lower()
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = word_tokenize(text)
        tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
        return ' '.join(tokens)
    except Exception as e:
        return ""

if __name__ == "__main__":
    print("🤖 AI HATE SPEECH DETECTOR - MODEL TESTING")
    print("Model: Logistic Regression with TF-IDF")
    
    # Run different tests
    test_random_samples(10)
    test_specific_cases()
    evaluate_model_performance()
    
    print(f"\n{'='*50}")
    print("TESTING COMPLETED!")
    print(f"{'='*50}")

    y_pred = model.predict(tfidf_vectorizer.transform(df['comment_text'].apply(preprocess_text)))
    print("\nOverall Classification Report:")
    print(classification_report(df['toxic'], y_pred, target_names=['Safe', '    Toxic']))   