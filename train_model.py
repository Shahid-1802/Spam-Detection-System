import pandas as pd
import joblib
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

data = pd.read_csv("spam.csv")

data['label'] = data['label'].map({'ham':0,'spam':1})

X = data['message']
y = data['label']

vectorizer = TfidfVectorizer(stop_words='english')
X_vec = vectorizer.fit_transform(X)

model = MultinomialNB()
model.fit(X_vec,y)

os.makedirs("model",exist_ok=True)

joblib.dump(model,"model/spam_model.pkl")
joblib.dump(vectorizer,"model/vectorizer.pkl")

print("Model trained successfully")