import re
import string
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import pandas as pd

# ====== CONFIGURATION GLOBALE ======
nlp = spacy.load("en_core_web_sm")

# Synonyms mapping
SYNONYMS = {
    "bp": "blood pressure",
    "hr": "heart rate",
    "temp": "temperature",
    "fever": "pyrexia",
    "high-temp": "pyrexia",
    "hightemp": "pyrexia",
    "sob": "shortness of breath",
    "n/v": "nausea vomiting",
    "nv": "nausea vomiting",
    "abd": "abdominal",
    "cp": "chest pain",
}

AUTO_CORRECT = False 

# === Stopwords custom : conserve certains mots médicaux/diagnostiques
MEDICAL_KEEP = {
    "need", "worried", "see", "doctor", "pain", "son", "daughter", "child", "blood", "pressure"
}


MY_EXTRA_STOPWORDS = {'would', 'like', 'get', 'take', 'go', 'yes', 'no', 'thanks', 'please', "okay", "hi", "hello", 'thank'}

# Point clé : On retire aussi 'no', 'not', 'without' des stopwords pour la négation médicale
COMBINED_STOPWORDS = (STOP_WORDS | MY_EXTRA_STOPWORDS) - MEDICAL_KEEP - {"no", "not", "without"}

# ====== FONCTION NÉGATION ======

NEGATION_PATTERNS = [
    (r"\bno ([a-z0-9_\-]+)", r"no_\1"),  # ex: "no fever" -> "no_fever"
    (r"\bnot ([a-z0-9_\-]+)", r"no_\1"),
    (r"\bwithout ([a-z0-9_\-]+)", r"no_\1"),
    (r"\bnegative for ([a-z0-9_\-]+)", r"no_\1"),
]
def apply_negation_patterns(text):
    # On applique chaque pattern, une seule "poste-négation" à la fois
    for pat, rep in NEGATION_PATTERNS:
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)
    return text

# ====== CORE FUNCTIONS ======

def expand_synonyms(text):
    """
    Remplace tous les synonymes/mapping dans le texte, insensible à la casse,
    sur mots/expressions entières (évite doc.splitting prématuré).
    """
    sorted_synonyms = sorted(SYNONYMS.items(), key=lambda x: len(x[0]), reverse=True)
    for k, v in sorted_synonyms:
        text = re.sub(rf'\b{re.escape(k)}\b', v, text, flags=re.IGNORECASE)
    return text

def basic_cleanup(text):
    text = text.lower().strip()
    text = re.sub(r"[’']", " ", text)  # apostrophes → espace
    text = re.sub(r"\.\.+", " ", text)  # points multiples → espace
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
    return text

def correct_typos(text):
    try:
        from textblob import TextBlob
        return str(TextBlob(text).correct())
    except ImportError:
        return text

def add_english_contractions(stopword_set):
    """Ajoute les contractions anglaises courantes à un ensemble de stopwords."""
    EN_CONTRACTIONS = {"m", "s", "re", "ve", "ll", "d"}
    return stopword_set.union(EN_CONTRACTIONS)

def preprocess(
        text,
        typo_correct=AUTO_CORRECT,
        synonym_replace=True,
        remove_stopwords=True,
        custom_stopwords=COMBINED_STOPWORDS
    ):
    # AJOUT : élargir les stopwords pour inclure les contractions
    custom_stopwords = add_english_contractions(custom_stopwords)
    
    # 1. Synonymes AVANT nettoyage
    if synonym_replace:
        text = expand_synonyms(text)
    # 2. Gestion négation
    text = apply_negation_patterns(text)
    # 3. Nettoyage basique
    text = basic_cleanup(text)
    # 4. Correction
    if typo_correct:
        text = correct_typos(text)
    # 5. Lemmatization + stopwords
    doc = nlp(text)
    lemmas = []
    for token in doc:
        if token.is_punct or token.is_space:
            continue
        if token.lemma_ == "-PRON-":
            _lemma = token.text.lower()
        else:
            _lemma = token.lemma_
        #print(token.text, _lemma, _lemma.lower() in custom_stopwords)
        if remove_stopwords and _lemma.lower() in custom_stopwords:
            continue
        lemmas.append(_lemma)
    return " ".join(lemmas)

# ==== USAGE EXEMPLE ====
if __name__ == "__main__":
    tests = [
        "Patient has a fever, HR 130, complaints of severe abdominal Pain!",
        "BP is low, High-temp and som abd pain detected.",
        "Shortness of breath (SOB) & N/V, severe chest pain.",
        "feveer and temp up, HR high",  # typo 'feveer', 'temp'
        "The patient has no pain, but high blood pressure."
    ]
    for idx, sentence in enumerate(tests, 1):
        print(f"\nExample {idx} — Original: {sentence}")
        print("Processed: ", preprocess(sentence, typo_correct=True))

