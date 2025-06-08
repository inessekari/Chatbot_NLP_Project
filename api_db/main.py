from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from api_db.models import Base, Interaction, PatientHistory
from typing import Optional

# Configuration DB SQLite
DATABASE_URL = "sqlite:///./interactions.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Création des tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

# Création session DB
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

app = FastAPI(title="API DB - Interaction Logger")

# Schéma Pydantic pour les requêtes POST /interactions
class InteractionCreate(BaseModel):
    message: str
    response_type: str
    response: str
    proba_urgent: Optional[float] = None

class PatientHistoryCreate(BaseModel):
    patient_id: int
    age: int
    sex: str
    medical_history: Optional[str] = None
    recent_history: Optional[str] = None

# CRUD CREATE
@app.post("/patients/")
def create_patient_history(patient: PatientHistoryCreate):
    db = SessionLocal()
    try:
        patient_obj = PatientHistory(**patient.dict())
        db.add(patient_obj)
        db.commit()
        return {"status": "ok", "id": patient.patient_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.post("/interactions")
def create_interaction(data: InteractionCreate):
    db = SessionLocal()
    try:
        interaction = Interaction(
            message=data.message,
            response_type=data.response_type,
            response=data.response,
            proba_urgent=data.proba_urgent,
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return {"status": "ok", "id": interaction.id}
    finally:
        db.close()

# CRUD READ
@app.get("/patients/{patient_id}")
def get_patient_history(patient_id: int):
    db = SessionLocal()
    try:
        patient = db.query(PatientHistory).filter_by(patient_id=patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return {
            "patient_id": patient.patient_id,
            "age": patient.age,
            "sex": patient.sex,
            "medical_history": patient.medical_history,
            "recent_history": patient.recent_history,
        }
    finally:
        db.close()

@app.get("/interactions")
def get_all_interactions():
    db = SessionLocal()
    try:
        interactions = db.query(Interaction).all()
        return [
            {
                "id": i.id,
                "message": i.message,
                "response_type": i.response_type,
                "response": i.response,
                "proba_urgent": i.proba_urgent,
                "timestamp": i.timestamp.isoformat(),
            }
            for i in interactions
        ]
    finally:
        db.close()

# CRUD DELETE
@app.delete("/interactions/{interaction_id}")
def delete_interaction(interaction_id: int):
    db = SessionLocal()
    try:
        interaction = db.query(Interaction).filter_by(id=interaction_id).first()
        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")
        db.delete(interaction)
        db.commit()
        return {"status": "deleted"}
    finally:
        db.close()

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    db = SessionLocal()
    try:
        patient = db.query(PatientHistory).filter_by(patient_id=patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        db.delete(patient)
        db.commit()
        return {"status": "deleted"}
    finally:
        db.close()

@app.get("/")
def home():
    return {"msg": "API DB en ligne"}
