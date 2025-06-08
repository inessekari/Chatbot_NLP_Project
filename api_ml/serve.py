from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import traceback
from textblob import TextBlob
import pandas as pd
import math

from api_ml.model import pipeline  # Pipeline ML

app = FastAPI(title="Emergency Triage API", version="1.0")

class Query(BaseModel):
    message: str = Field(..., example="J'ai des douleurs dans la poitrine.")
    age: int = Field(..., ge=0, le=120, example=42)
    sexe: str = Field(..., pattern="^(M|F|U)$", example="M")

def add_sentiment(message):
    if isinstance(message, str):
        pol = TextBlob(message).sentiment.polarity  # [-1, 1]
        return (pol + 1) / 2  # [0, 1]
    return 0.5

def clean_probability(prob):
    if prob is None:
        return None
    if isinstance(prob, float):
        if math.isnan(prob) or math.isinf(prob):
            return None
        return prob
    # Cast numpy.float64 or others to float
    try:
        fprob = float(prob)
        if math.isnan(fprob) or math.isinf(fprob):
            return None
        return fprob
    except:
        return None

@app.post("/predict/")
def predict(query: Query):
    if not query.message.strip():
        raise HTTPException(status_code=422, detail="Le texte ne doit pas être vide.")
    try:
        sentiment = add_sentiment(query.message)
        
        features = {
            "question_clean": query.message,
            "age": query.age,
            "sex": query.sexe,
            "sentiment": sentiment,
        }
        X = pd.DataFrame([features])

        proba_raw = pipeline.predict_proba(X)[0, 1]
        proba = clean_probability(proba_raw)

        label_raw = pipeline.predict(X)[0]
        label = int(label_raw) if label_raw in [0,1] else 0

        return {
            "label": label,
            "proba_urgent": proba,
            "sentiment": float(sentiment),
        }
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erreur interne sur la prédiction.")

@app.get("/")
def home():
    return {"message": "Bienvenue sur l'API de triage d'urgence."}
