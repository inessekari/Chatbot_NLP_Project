import pandas as pd
from rapidfuzz import process, fuzz
import re
import unicodedata
from googletrans import Translator

##############################
# Nettoyage avancé pour FAQ  #
##############################
def clean_text(text):
    text = text.strip().lower()
    # Supprime accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])
    # Remplace tous caractères spéciaux et apostrophes
    text = re.sub(r"[’'`]", '', text)   # supprime apostrophes courantes FR/EN
    text = re.sub(r"[^\w\s]", '', text) # retire le reste (ponctuation, etc)
    text = re.sub(r"\s+", ' ', text)    # espaces multiples -> un seul espace
    return text.strip()

# Chargement CSV FAQ
try:
    faq_df = pd.read_excel("/Users/ines/NLP/emergency_chatbot/data/medical_faq.xlsx")
except Exception as e:
    print(f"Erreur chargement CSV FAQ: {e}")
    faq_df = pd.DataFrame(columns=["question", "answer"])

print("📄 Colonnes du fichier CSV :", faq_df.columns.tolist())
print("📄 Aperçu des premières lignes :")
print(faq_df.head())

faq_df = faq_df.drop_duplicates(subset=["question"])
faq_df = faq_df.dropna(subset=["question", "answer"])
faq_df['question'] = faq_df['question'].astype(str).apply(clean_text)

# Initialisation de la base FAQ
FAQ_DB = dict(zip(faq_df['question'], faq_df['answer']))


######################
# Traducteur Google  #
######################
translator = Translator()

def find_faq_answer(user_input, threshold=80, lang=None):
    cleaned_input = clean_text(user_input)
    print(f"[FAQ DEBUG] Entrée nettoyée: {cleaned_input}")
    
    # Astuce : si FR ou EN, ne traduis pas (la base est dans les deux langues)
    #   Tu ne devrais traduire que si la langue détectée est autre que fr/en
    do_translate = lang not in [None, "fr", "en"]
    if do_translate:
        try:
            translated = translator.translate(user_input, src=lang, dest='en')
            print(f"[FAQ] Traduction de '{user_input}' -> '{translated.text}'")
            cleaned_input = clean_text(translated.text)
        except Exception as e:
            print(f"[FAQ] Erreur traduction: {e} — on garde l'original")
    
    # Matching flou
    questions_list = list(FAQ_DB.keys())
    print(f"[FAQ DEBUG] Nombre de questions dans la base : {len(questions_list)}")
    print(f"[FAQ DEBUG] Entrée nettoyée : '{cleaned_input}'")
 
    if cleaned_input in questions_list:
        print("[FAQ DEBUG] Correspondance exacte trouvée.")
        return FAQ_DB[cleaned_input]
 
    result = process.extractOne(cleaned_input, questions_list, scorer=fuzz.token_sort_ratio)
    print(f"[FAQ DEBUG] Résultat brut : {result}")
 
    if result is None:
        print("[FAQ DEBUG] Aucun résultat trouvé.")
        return None
 
    match, score, _ = result
    print(f"[FAQ DEBUG] Matched '{match}' avec score={score}")
 
    if score >= threshold:
        answer = FAQ_DB.get(match)
        if answer and str(answer).lower() != "nan":
            return answer
 
    print("[FAQ DEBUG] => Aucun match suffisamment proche ou réponse invalide.")
    return None

#####################################
# Test rapide / debug à la main     #
#####################################
if __name__ == "__main__":
    test_questions = [
        "quels sont vos horaires d'ouverture",
        "quelle est l'adresse de l'hôpital",
        "avez-vous une pharmacie sur place?",
        "Le service urgence est-il ouvert 24/7 ?",
        "Do you accept walk-in patients?",
        "what is the emergency phone number?",
        "Y a-t-il un parking à l'hôpital",  # avec à et apostrophe
        "puis-je faire un test covid ici"    # test "puis-je"
    ]
    for q in test_questions:
        answer = find_faq_answer(q, lang=None)  # lang=None pour éviter la trad sur FR/EN
        print(f"\n🔍 Question: {q}\n📘 Réponse: {answer if answer else 'Aucune réponse trouvée'}")
