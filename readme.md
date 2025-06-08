# Emergency Chatbot Architecture

## Arborescence
├── api_chatbot/       # API d'entrée utilisateur (FAQ + ML)
├── api_ml/            # Modèle ML "urgence" (FastAPI)
├── api_db/            # Base de données SQLite et scripts, modèles
├── data/              # Datasets
└── requirements.txt   # Dépendances Python

## Lancer le projet

### 1. Lancer l'API ML
    cd api_ml
    uvicorn serve:app --reload --port 8001

### 2. Lancer l'API Chatbot
    cd ../api_chatbot
    uvicorn main:app --reload --port 8000

### 3. Tester le chatbot
    http POST http://localhost:8000/chat/ message="Votre question ici"
    # ou python script de test manuel

## Fonctionnement
- User → Chatbot (FAQ / fallback ML) → log interaction en DB.
- FAQ : réponses codées, ML : modèle `triage_pipeline.pkl` (aléatoir, logistic, etc).
- Historique et logs stockés dans `interactions.db`.

## Dépendances
Installer avec :
    pip install -r requirements.txt

## URLs utiles
- http://localhost:8000/docs (API chatbot)
- http://localhost:8001/docs (API ML)
- http://localhost:8002/docs (API DB)