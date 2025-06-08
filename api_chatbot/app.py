import streamlit as st
import requests

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "chat"

# ➕ Historique de chat dans la session
if "history" not in st.session_state:
    st.session_state.history = []

st.set_page_config(page_title="Chatbot Médical", page_icon="🩺")
st.title("🩺 Chatbot Médical")

tab_labels = ["💬 Chatbot", "🚨 Évaluer une urgence"]
selected_tab = 0 if st.session_state.get("active_tab", "chat") == "chat" else 1
tab1, tab2 = st.tabs(tab_labels)

# --- Fonction d'envoi de message Chatbot ---
def send_faq_message():
    faq_message = st.session_state["faq_msg"]
    if faq_message.strip():
        try:
            payload = {"message": faq_message}
            res = requests.post("http://localhost:8000/chat", json=payload)
            data = res.json()
            answer = data.get("response", "Je n'ai pas la réponse à votre message")
            st.session_state.history.append(
                {"user": faq_message, "bot": answer}
            )
        except Exception as e:
            st.session_state.history.append(
                {"user": faq_message, "bot": f"[Erreur API] {e}"}
            )
    # Vide la boîte après envoi
    st.session_state["faq_msg"] = ""

# === Onglet FAQ / Chatbot (effet "chat") ===
with tab1:
    st.session_state.active_tab = "chat"
    st.subheader("💬 Démarrer une conversation médicale")

    # Historique façon messagerie (bulle)
    for chat in st.session_state.history:
        # Bulle utilisateur
        st.markdown(
            f'''<div style="background:#222;color:#fff;border:2px solid #b71c1c;padding:10px;
            border-radius:16px 2px 16px 16px;margin-bottom:2px;max-width: 60%;
            margin-left:auto;text-align:right;">
            <b>Vous :</b> {chat["user"]}</div>''',
            unsafe_allow_html=True)

        # Bulle bot
        st.markdown(
            f'''<div style="background:#000;color:#fff;border:2px solid #b71c1c;padding:10px;
            border-radius:2px 16px 16px 16px;margin-bottom:14px;max-width: 60%;
            margin-right:auto;text-align:left;">
            <b>Bot :</b> {chat["bot"]}</div>''',
            unsafe_allow_html=True)

    # Zone + boutons
    faq_message = st.text_input(
        "Votre message",
        placeholder="Ex: C'est quoi l'anxiété ?",
        key="faq_msg"
    )

    col1, col2 = st.columns([1, 1])
    send = col1.button("Envoyer le message", key="faq_btn", on_click=send_faq_message)
    clear = col2.button("🗑️ Effacer la conversation")

    if clear:
        st.session_state.history = []
        st.rerun()

# === Onglet ML Urgence ===
with tab2:
    st.session_state.active_tab = "urgence"
    st.subheader("🚨 Symptômes à analyser")

    ml_message = st.text_input(
        "Décrivez vos symptômes", 
        placeholder="Ex: J'ai une douleur à la poitrine", 
        key="ml_msg"
    )
    age = st.number_input("Âge", min_value=0, max_value=120, step=1)
    sexe = st.selectbox("Sexe", ["", "Femme", "Homme"], index=0)
    # Champs supplémentaires
    duree = st.selectbox(
        "Durée des symptômes",
        ["Quelques minutes", "Quelques heures", "Environ 24 h", "Plus de 24 h"],
        index=0,
        help="Depuis combien de temps ressentez-vous ces symptômes ?"
    )

    intensite = st.slider("Intensité des symptômes (1 = très léger, 10 = insupportable)", min_value=1, max_value=10, value=5)

    if st.button("Analyser l'urgence", key="ml_btn"):
        if not ml_message.strip() or not sexe:
            st.warning("Veuillez remplir tous les champs.")
        else:
            payload = {
                "message": ml_message,
                "age": age,
                "sexe": sexe,
                "duree_symptomes": duree,
                "intensite": intensite
            }
            try:
                res = requests.post("http://localhost:8000/evaluer-urgence", json=payload)
                data = res.json()
                response = data.get("response", {})

                if isinstance(response, dict) and "label" in response:
                    # -- Réponse médicale principale --
                    if response["label"] == 1:
                        st.error("⚠️ Urgence médicale détectée. Rendez-vous immédiatement à l'hôpital.")
                    elif response["label"] == 0:
                        st.info("ℹ️ Il ne semble pas s'agir d'une urgence. Consultez votre médecin généraliste.")
                    else:
                        st.warning("Résultat non interprétable.")
                    if "proba_urgent" in response:
                        st.write(f"Confiance : **{response['proba_urgent'] * 100:.1f}%**")
                        
                    # -- Analyse du sentiment (score numérique) --
                    if "sentiment" in response and isinstance(response["sentiment"], (int, float)):
                        score = response["sentiment"]
                        if score < 0.2:
                            st.warning("😟 Vous semblez très inquiet ou en détresse émotionnelle. Prenez soin de vous. Si besoin, contactez un proche ou une aide médicale.")
                            st.markdown("[Ressources d’aide psychologique : SOS Amitié](https://www.sos-amitie.com/)  &nbsp; [Numéro national de prévention du suicide : 3114](https://3114.fr/)")
                        elif score < 0.4:
                            st.info("🙏 Nous percevons un stress ou une inquiétude dans votre message. Restez calme, surveillez vos symptômes et n'hésitez pas à consulter si besoin.")

                else:
                    st.warning("La réponse n'a pas pu être interprétée. (Champ label absent)")
                    st.info(str(response))
            except Exception as e:
                st.error(f"Erreur : {e}")
