# tests/test_chat.py
from fastapi.testclient import TestClient
from api_chatbot.main import app

client = TestClient(app)

def test_faq():
    response = client.post("/chat", json={"message": "What are the opening hours?"})
    assert response.status_code == 200
    assert response.json()["type"] == "faq"

def test_ml(monkeypatch):
    def dummy_ml_post(*args, **kwargs):
        class DummyResponse:
            def json(self):
                return {"response": "Non urgent", "proba_urgent": 0.1}
            @property
            def status_code(self):
                return 200
        return DummyResponse()

    import requests
    monkeypatch.setattr(requests, "post", dummy_ml_post)

    response = client.post("/chat", json={
        "message": "blabla",
        "age": 25,
        "sexe": "F"
    })

    assert response.status_code == 200
    assert response.json()["type"] == "ml"
