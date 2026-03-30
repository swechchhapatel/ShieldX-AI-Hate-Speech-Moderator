import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import re
import nltk
nltk.download('wordnet')

# Load dataset
df = pd.read_csv("C:\\Users\\palak\\Documents\\AI-POWERED-HATE-SPEECH-AND-CYBERBULLYING-MODERATOR\\backend\\model\\labeled_data.csv")  # rename your file accordingly
print("Dataset loaded:", df.shape)
df = df[['tweet', 'class']]

#Text Cleaning
def clean_text(text):
    text = text.lower()

    # remove urls
    text = re.sub(r'http\S+', '', text)

    # remove mentions
    text = re.sub(r'@\w+', '', text)

    # remove "rt"
    text = re.sub(r'\brt\b', '', text)

    # remove html entities (&amp;, &#...)
    text = re.sub(r'&\w+;', '', text)

    # remove special characters (keep words)
    text = re.sub(r'[^a-z\s]', '', text)

    # remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

df['clean_text'] = df['tweet'].apply(clean_text)

#TF-IDF Vectorization
vectorizer = TfidfVectorizer(
    max_features=10000,
    ngram_range=(3,5),      # unigrams + bigrams
    analyzer='char'
)

X = vectorizer.fit_transform(df['clean_text'])
y = df['class']

#train model
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LogisticRegression(max_iter=1000, class_weight={0:5, 1:1, 2:1})  # Adjust weights based on class imbalance
model.fit(X_train, y_train)

#evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model + vectorizer
joblib.dump(model, "hate_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("Model and vectorizer saved successfully!")
