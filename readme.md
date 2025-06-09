# 🩺 Chatbot NLP d’Urgence pour le Triage Médical

Ce projet est un chatbot médical multilingue et modulaire, conçu pour aider les patients à évaluer le niveau d’urgence de leurs symptômes. Il combine un module FAQ médical et un classifieur machine learning de triage, le tout orchestré via une architecture robuste en FastAPI.

Développé dans le cadre du Mastère Data Engineering & IA à l’EFREI (2024–2025)  
Auteures : Inès Sekari & Malaïka Nkuida  
Encadrant : Steve Elanga

---

## Objectifs du projet

- Réduire la saturation des urgences hospitalières en filtrant les cas non urgents.
- Offrir un chatbot multilingue fiable (FR/EN) pour l’analyse des symptômes.
- Proposer une architecture scalable pour une exploitation médicale en temps réel.

---

## Architecture du projet

/emergency_chatbot/
│
├── api_chatbot/       	        # Contient toute la logique du chatbot
│   ├── main.py			        # Le script principal de lancement du chatbot
│   ├── __init__.py		        # Repère module Python
│   ├── test_chat_api.py	    # Tests unitaires pour l'API du chatbot
│   ├── test_faq.py		        # Tests unitaires sur la base FAQ
│   ├── app.py			        # API frontend du chatbot pour l'UI
│   ├── preprocessing.py	    # Fonctions de nettoyage et préparation du texte/questions
│   └── faq.py 			        # Gestion et interrogation de la base de connaissances FAQ
│
├── api_ml/            	        # Toute la partie apprentissage, entraînement et API modèle pour triage (urgent/non-urgent)
│   ├── model.py		        # Définition/chargement/sauvegarde du modèle ML
│   ├── triage_pipeline.pkl	    # Pipeline entraîné (pickle) réutilisable
│   ├── serve.py		        # API de déploiement FastAPI
│   └── train_classifier.py	    # Script de training du modèle et sauvegarde pipeline
│
├── api_db/            	        # La gestion base de données
│   ├── import_patient.py	    # Script d'import de données patients
│   ├── main.py			        # Script principal DB
│   └── models.py		        # Définition des modèles de données DB (Patient, Question, etc.)
│
├── data/              	        # Datasets CSV(triage_dataset, medical_faq…)
│            
├── notebooks/              	# Notebooks d'exploration, d'EDA, ou scripts ad-hoc de test ML/NLP
├── readme.md              	    #Documentation du projet
├── interactions.db           	# Fichier base de données SQLite pour stocker un historique des chats/interactions  
└── requirements.txt 		    # Dépendances globales du projet




## Lancer le projet

### 1. Lancer l’API du modèle ML
```bash
cd emergency_chatbot
uvicorn api_ml.serve:app --reload --port 8001

### 2. Lancer l'API Chatbot
    cd emergency_chatbot
    uvicorn api_db.main:app --host 0.0.0.0 --port 8002 --reload

### 3. Lancer l'API de base de données
    cd emergency_chatbot
    uvicorn api_chatbot.main:app --reload 

### 4. Lancer l'interface Streamlit
    cd api_chatbot
    streamlit run app.py

URLs utiles

API Chatbot → http://localhost:8000/docs
API ML (Modèle) → http://localhost:8001/docs
API Base de données → http://localhost:8002/docs
Interface Streamlit → http://localhost:8501/


Fonctionnalités principales

Mode double : Chat FAQ ou analyse des symptômes (ML).
Multilingue : détection et traduction automatique (FR/EN).
Pipeline NLP personnalisé : synonymes médicaux, négations, correction orthographique.
Modèle ML : régression logistique, intégration âge/sexe, score de sentiment.
Architecture modulaire : testable, scalable, facile à maintenir.


Dataset & Modèle

Dataset : ~1 000 descriptions de symptômes annotées urgent / non-urgent.
Prétraitement : expansion de synonymes, détection de négation, polarité émotionnelle.
Pipeline ML : TF-IDF + régression logistique avec variables démographiques.
Performances : Accuracy ~74 %, F1 Macro : 0.72, ROC AUC : ~0.81

Tests & Validation

Interfaces Swagger UI pour tester les APIs.
Cas tests réalistes simulant des patients (FAQ ou symptômes).
Logging persistant via interactions.db (API DB).

Aspects éthiques & techniques

Traduction automatique FR → EN (modèle entraîné en anglais).
Aucune donnée médicale sensible stockée.
Design modulaire prêt pour intégration de modèles NLP avancés (BERT, etc.).


Installation

git clone https://github.com/inessekari/Chatbot_NLP_Project.git
cd emergency-chatbot
pip install -r requirements.txt

Dépendances

Voir requirements.txt pour la liste complète.

Améliorations futures

Entraînement sur des datasets multilingues (FR + EN).
Migration vers des modèles type BERT (CamemBERT, FlauBERT…).
Ajout d’une mémoire conversationnelle persistante.
Déploiement complet via Docker + CI/CD.
Intégration d’une base patient ou historique médical.


Crédits

Conçu avec Python, FastAPI, scikit-learn, spaCy, TextBlob, Streamlit.
Ce projet a été développé à des fins académiques et n’est pas destiné à un usage médical réel sans validation clinique.