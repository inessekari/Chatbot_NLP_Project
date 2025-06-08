import csv
import os
from models import PatientHistory, Base, engine, SessionLocal  # Tout importer ici !

# Pour affichage du chemin absolu vers la base
abspath = os.path.abspath(engine.url.database)
print("Chemin ABSOLU :", abspath)

# Crée les tables si pas encore existantes
Base.metadata.create_all(bind=engine)

def import_patient_history_csv(csv_path):
    session = SessionLocal()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Si un patient_id existe déjà, on saute (évite doublons)
            exists = session.query(PatientHistory).filter_by(patient_id=int(row['patient_id'])).first()
            if not exists:
                patient = PatientHistory(
                    patient_id=int(row['patient_id']),
                    age=int(row['age']),
                    sex=row['sex'],
                    medical_history=row['medical_history'] if row['medical_history'] else None,
                    recent_history=row['recent_history'] if row['recent_history'] else None,
                )
                session.add(patient)
        session.commit()
    session.close()
    print("✅ Import terminé !")

# Appel :
import_patient_history_csv("/Users/ines/NLP/emergency_chatbot/data/patient_history.csv")
