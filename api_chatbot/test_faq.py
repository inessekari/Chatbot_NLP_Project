from faq import find_faq_answer, FAQ_DB

test_question = "what are your opening hours?"
print("Question test :", test_question)
print("Clés FAQ :", list(FAQ_DB.keys()))
answer = find_faq_answer(test_question, threshold=50)  # seuil bas pour être sûr
print("Réponse trouvée :", answer)
