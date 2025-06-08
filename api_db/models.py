import os
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# ## 1. On définit le chemin de la DB de façon absolue
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "interactions.db")
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

# ## 2. Session locale
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# ## 3. Base class
Base = declarative_base()

# ## 4. Modèles
class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    response_type = Column(String, nullable=False)  # 'faq' ou 'ml'
    response = Column(String, nullable=False)
    proba_urgent = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class PatientHistory(Base):
    __tablename__ = "patient_history"

    patient_id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    sex = Column(String, nullable=False)
    medical_history = Column(String, nullable=True)
    recent_history = Column(String, nullable=True)
