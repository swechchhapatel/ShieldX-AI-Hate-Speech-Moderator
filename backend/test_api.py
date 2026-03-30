import requests

API_URL = "http://127.0.0.1:5000/predict"

samples = [
    "I hate these people, they should leave!",
    "You are the best!",
    "I love programming.",
    "asian people are smart",
    "What a stupid comment you made"
]

for text in samples:
    res = requests.post(API_URL, json={"text": text})
    print(f"Text: {text}")
    #print("Prediction:", res.json(), "\n")
    print("Status code:", res.status_code)
    print("Raw response text:", res.text)
