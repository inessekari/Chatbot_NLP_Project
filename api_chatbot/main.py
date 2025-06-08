from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api_chatbot.preprocessing import preprocess
from api_chatbot.faq import find_faq_answer
import requests
import math
from langdetect import detect
from googletrans import Translator
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from api_chatbot.faq import clean_text
 
app = FastAPI(title="Chatbot Medical Orchestrator", version="1.0")
 
 
@app.get("/")
def read_index():
    return FileResponse("frontend/index.html")
 
class ChatInput(BaseModel):
    message: str
    age: int = None
    sexe: str = None
 
API_ML_URL = "http://localhost:8001/predict"
API_DB_URL = "http://localhost:8002/interactions"
 
translator = Translator()
 
def is_valid_float(x):
    return isinstance(x, float) and not math.isnan(x) and not math.isinf(x)
 
def sanitize_payload(payload):
    if isinstance(payload, dict):
        for k, v in payload.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                payload[k] = None
            elif isinstance(v, dict):
                payload[k] = sanitize_payload(v)
            elif isinstance(v, list):
                payload[k] = [sanitize_payload(i) for i in v]
    elif isinstance(payload, float) and (math.isnan(payload) or math.isinf(payload)):
        payload = None
    return payload
 
def fix_payload_for_db(payload):
    payload.setdefault("response", "")
    payload.setdefault("message", "")
    payload.setdefault("response_type", "")
    return payload
 
def log_interaction_to_db(payload: dict):
    payload = sanitize_payload(payload)
    payload = fix_payload_for_db(payload)
    print("[DEBUG] Payload sent to DB:", payload)
    try:
        res = requests.post(API_DB_URL, json=payload, timeout=3)
        if res.status_code != 200:
            print(f"[Warning] Erreur API DB: {res.status_code} - {res.text}")
        else:
            print(f"[DEBUG] DB answered with {res.status_code}")
    except Exception as e:
        print(f"[Warning] Impossible de joindre l’API DB: {e}")


 # 1. Chatbot : FAQ ONLY
@app.post("/chat")

def chatbot_endpoint(chat: ChatInput):
    print("🔍 Message reçu:", chat.message)
    # 1. Détection de langue
    try:
        lang = detect(chat.message)
        print(f"Langue détectée: {lang}")
    except Exception as e:
        print(f"Erreur détection langue: {e}")
        lang = "en"
 
    # 2. Traduire la question si besoin
    query_for_faq = chat.message
    if lang != "en":
        try:
            query_for_faq = translator.translate(chat.message, src=lang, dest="en").text
            print(f"[TRADUCTION] Question en anglais : {query_for_faq}")
        except Exception as e:
            print(f"[TRADUCTION] Erreur traduction FR->EN : {e}")
    print("[DEBUG] Appel FAQ...")

    def detect_intent(user_input):
        cleaned = clean_text(user_input)
        greetings = ["bonjour", "salut", "hello", "bonsoir", "coucou", "hi", "hey"]
        thanks = ["merci", "thanks", "thank you"]
        goodbye = ["au revoir", "bye", "à bientôt"]
 
        if any(word in cleaned for word in greetings):
            return "greeting"
        elif any(word in cleaned for word in thanks):
            return "thanks"
        elif any(word in cleaned for word in goodbye):
            return "goodbye"
        return "unknown"

    intent = detect_intent(chat.message)

    if intent == "greeting":
        return {"response": "Bonjour ! Comment puis-je vous aider aujourd’hui ? 😊", "type": "intent", "lang": lang}
    elif intent == "thanks":
        return {"response": "Avec plaisir ! N’hésitez pas si vous avez d’autres questions. 🙏", "type": "intent", "lang": lang}
    elif intent == "goodbye":
        return {"response": "Au revoir ! Prenez soin de vous. 👋", "type": "intent", "lang": lang}

    faq_answer = find_faq_answer(query_for_faq, lang="en")  # NOTE : la FAQ attend de l'anglais !
 
    print(f"[DEBUG] Réponse FAQ: {faq_answer}")
 
    # 3. Si réponse trouvée, retraduit dans la langue
    if faq_answer:
        answer_for_user = faq_answer
        if lang != "en":
            try:
                answer_for_user = translator.translate(faq_answer, src="en", dest=lang).text
                print(f"[TRADUCTION] Réponse traduite EN->{lang} : {answer_for_user}")
            except Exception as e:
                print(f"[TRADUCTION] Erreur traduction EN->{lang} : {e}")
 
        payload = {
            "message": chat.message,
            "response_type": "faq",
            "response": answer_for_user,
            "proba_urgent": None
        }

        log_interaction_to_db(payload)

        return sanitize_payload({
            "response": answer_for_user,
            "type": "faq",
            "lang": lang
        })

    else:
        payload = {
            "message": chat.message,
            "response_type": "none",
            "response": "",
            "proba_urgent": None
        }

        log_interaction_to_db(payload)

        return {
            "response": (
                "Je suis désolé, je n’ai pas la réponse à cette question pour le moment. " 
                "Vous pouvez reformuler votre question ou utiliser l'onglet **🚨 Évaluer une urgence** "
                "si vous présentez des symptômes. 😊"
            ),
            "type": "none",
            "lang": lang,
        }

 
# 2. Evaluer une urgence : ML ONLY
@app.post("/evaluer-urgence")
def evaluer_urgence_endpoint(chat: ChatInput):
    print("🔍 Message reçu (urgence):", chat.message)
    print("🔍 Sexe:", chat.sexe, "| Age:", chat.age)
 
    if chat.age is None or chat.sexe is None:
        raise HTTPException(status_code=400, detail="Merci de renseigner l'âge et le sexe pour l'évaluation.")
 
    try:
        lang = detect(chat.message)
        print(f"Langue détectée: {lang}")
    except Exception as e:
        print(f"Erreur détection langue: {e}")
        lang = "en"
 
    sexe_cleaned = str(chat.sexe).strip().upper()
    if sexe_cleaned in ["FEMME", "F"]:
        sexe_cleaned = "F"
    elif sexe_cleaned in ["HOMME", "M"]:
        sexe_cleaned = "M"
    else:
        raise HTTPException(status_code=400, detail="Le champ 'sexe' doit être 'F' ou 'M'.")
 
    message_to_use = chat.message
    if lang != "en":
        try:
            translation = translator.translate(chat.message, src=lang, dest='en')
            message_to_use = translation.text
            print(f"Texte traduit en anglais: {message_to_use}")
        except Exception as e:
            print(f"Erreur traduction, utilisation du texte original : {e}")
 
    cleaned = preprocess(message_to_use)
 
    try:
        res = requests.post(
            API_ML_URL,
            json={"message": cleaned, "age": chat.age, "sexe": sexe_cleaned},
            timeout=5
        )
        if res.status_code == 200:
            ml_result = res.json()
            proba = ml_result.get("proba_urgent")
            proba_safe = proba if is_valid_float(proba) else None
 
            payload = {
                "message": chat.message,
                "response_type": "ml",
                "response": str(ml_result),
                "proba_urgent": proba_safe
            }
            log_interaction_to_db(payload)
            return sanitize_payload({
                "response": ml_result,
                "type": "ml",
                "lang": lang
            })
        else:
            raise Exception(f"Erreur API ML: {res.text}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur de communication avec API ML: {e}")
 
# page test
@app.get("/_ping")
def home():
    return {"msg": "API Chatbot orchestrateur en ligne."}