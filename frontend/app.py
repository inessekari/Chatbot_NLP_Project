import streamlit as st
import requests

st.set_page_config(page_title="Chatbot Médical", page_icon="🩺")

st.title("🩺 Chatbot Médical")

# Tabs: "Question" (FAQ) and "Urgence" (ML)
tab1, tab2 = st.tabs(["💬 Questions médicales", "🚨 Évaluer une urgence"])

# === Onglet FAQ / Chatbot ===
with tab1:
    st.subheader("💬 Posez une question médicale")
    faq_message = st.text_input("Votre question", placeholder="Ex: C'est quoi l'endométriose ?", key="faq_msg")
    if st.button("Envoyer la question", key="faq_btn"):
        if not faq_message.strip():
            st.warning("Veuillez entrer une question.")
        else:
            try:
                res = requests.post("http://localhost:8000/chat", json={"message": faq_message})
                data = res.json()

                if data.get("type") == "faq":
                    st.success(data["response"])
                else:
                    st.info("Cette question n'est pas encore couverte par la FAQ.")
            except Exception as e:
                st.error(f"Erreur lors de la requête : {e}")

# === Onglet ML Urgence ===
with tab2:
    st.subheader("🚨 Symptômes à analyser")
    ml_message = st.text_input("Décrivez vos symptômes", placeholder="Ex: Je ne peux pas respirer", key="ml_msg")
    age = st.number_input("Âge", min_value=0, max_value=120, step=1)
    sexe = st.selectbox("Sexe", ["", "F", "M"], index=0)

    if st.button("Analyser l'urgence", key="ml_btn"):
        if not ml_message.strip() or not sexe:
            st.warning("Veuillez remplir tous les champs.")
        else:
            payload = {
                "message": ml_message,
                "age": age,
                "sexe": sexe
            }

            try:
                res = requests.post("http://localhost:8000/chat", json=payload)
                data = res.json()
                response = data.get("response", {})

                if isinstance(response, dict) and "label" in response:
                    if response["label"] == 1:
                        st.error("⚠️ Urgence médicale détectée. Rendez-vous immédiatement à l'hôpital.")
                    elif response["label"] == 0:
                        st.info("ℹ️ Il ne semble pas s'agir d'une urgence. Consultez votre médecin.")
                    else:
                        st.warning("Résultat non interprétable.")
                    
                    if "proba_urgent" in response:
                        st.write(f"Confiance : **{response['proba_urgent'] * 100:.1f}%**")
                else:
                    st.warning("La réponse n'a pas pu être interprétée.")

            except Exception as e:
                st.error(f"Erreur : {e}")
