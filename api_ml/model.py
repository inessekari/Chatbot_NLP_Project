import joblib
import pandas as pd
from deep_translator import GoogleTranslator
from textblob import TextBlob
import os

# Chargement du pipeline une seule fois au premier import
pipeline = joblib.load(os.path.join(os.path.dirname(__file__), "triage_pipeline.pkl"))

def predict_urgency(text, age, sexe):
    # 1. Traduction (français -> anglais)
    text_en = GoogleTranslator(source='auto', target='en').translate(text)
    # 2. Analyse du sentiment sur le texte traduit
    sentiment = TextBlob(text_en).sentiment.polarity
    # 3. Formatage du sexe (si F/M → Female/Male ou garder F/M si ton dataset était comme ça)
    # Si tu avais F/M/U dans le dataset, ne change rien :
    sex = sexe
    # 4. Construction du DataFrame avec toutes les colonnes dans le BON ordre/nom
    X = pd.DataFrame({
        'question_clean': [text_en],
        'age': [age],
        'sex': [sex],
        'sentiment': [sentiment]
    })
    # 5. Prédiction
    proba = pipeline.predict_proba(X)[0, 1]
    prediction = int(proba >= 0.5)
    return {'prediction': prediction, 'proba_urgent': proba,
    'prediction': prediction,
    'proba_urgent': proba,
    'sentiment': sentiment,
    'translated_text': text_en  # Pratique pour logs/debug
}

