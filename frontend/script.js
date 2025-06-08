// Dictionnaire bilingue pour les réponses ML
const responseTemplates = {
  en: {
    emergency: "⚠️ Your condition appears to be an emergency, please go to the nearest hospital as soon as possible.",
    non_emergency: "ℹ️ Your condition does not appear to be an emergency, I advise you to make an appointment with your general practitioner.",
    unknown: "Unknown result",
    unrecognized: "Unrecognized response",
  },
  fr: {
    emergency: "⚠️ Votre état semble être une urgence, veuillez vous rendre à l'hôpital le plus proche le plus rapidement possible.",
    non_emergency: "ℹ️ Votre état ne semble pas être une urgence, je vous conseille de prendre rendez-vous avec votre médecin généraliste.",
    unknown: "Résultat inconnu",
    unrecognized: "Réponse non reconnue",
  },
};

// Fonction de détection de langue (simple heuristique)
function detectLanguage(text) {
  const frenchWords = ["bonjour", "je", "suis", "mal", "pas", "peux", "douleur", "tête", "urgence", "hôpital"];
  const lowerText = text.toLowerCase();
  const matches = frenchWords.filter(word => lowerText.includes(word));
  return matches.length >= 2 ? "fr" : "en";
}

async function sendMessage() {
  const message = document.getElementById("message").value.trim();
  const age = document.getElementById("age").value.trim();
  const sexe = document.getElementById("sexe").value.trim();

  if (!message) {
    alert("Merci d'entrer un message.");
    return;
  }

  const detectedLang = detectLanguage(message);
  console.log("Langue détectée :", detectedLang);

  const payload = { message };
  if (age && sexe) {
    payload.age = parseInt(age);
    payload.sexe = sexe.toUpperCase(); // pour être sûr du format
  }

  try {
    console.log("Envoi du payload:", payload);
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Erreur ${res.status}: ${err}`);
    }

    const data = await res.json();
    console.log("Réponse reçue:", data);

    const resData = data.response;
    let responseText = "";

    if (typeof resData === "string") {
      // Cas FAQ ou message simple
      responseText = resData;

    } else if (typeof resData === "object" && resData !== null) {
      // Cas réponse ML attendue
      const t = responseTemplates[detectedLang];
      if ("label" in resData && "proba_urgent" in resData) {
        if (resData.label === 1) {
          responseText = t.emergency;
        } else if (resData.label === 0) {
          responseText = t.non_emergency;
        } else {
          responseText = `${t.unknown} (label: ${resData.label})`;
        }
        responseText += `\nConfiance: ${(resData.proba_urgent * 100).toFixed(1)}%`;
      } else {
        // Si objet JSON inconnu
        responseText = JSON.stringify(resData, null, 2);
      }
    } else {
      responseText = responseTemplates[detectedLang].unrecognized;
    }

    document.getElementById("response").innerText = responseText;

  } catch (error) {
    console.error("Erreur lors de l'envoi du message:", error);
    document.getElementById("response").innerText = `Erreur: ${error.message}`;
  }
}

document.getElementById("send-btn").addEventListener("click", sendMessage);
