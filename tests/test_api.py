from fastapi.testclient import TestClient

from backend.main import app
from backend.mock_llm_service import MockLLMService

client = TestClient(app)


def test_crear_incidencia_valida(monkeypatch):
    monkeypatch.setattr(
        "backend.main.llm_service",
        MockLLMService(),
    )

    response = client.post(
        "/incidencias",
        json={
            "mensaje": "He encontrado un perro herido junto a una carretera."
        },
    )

    assert response.status_code == 200
    assert response.json()["mensaje_recibido"] == (
        "He encontrado un perro herido junto a una carretera."
    )
    assert response.json()["decision_filtro"] == "requiere_llm"
    assert response.json()["resultado"]["categoria"] == "animal_herido"
    assert response.json()["resultado"]["urgencia"] == "alta"
    assert response.json()["resultado"]["departamento"] == "rescate"


def test_rechazar_incidencia_vacia():
    response = client.post(
        "/incidencias",
        json={
            "mensaje": ""
        },
    )

    assert response.status_code == 422

def test_rechazar_sin_mensaje():
    response = client.post(
        "/incidencias",
        json={},
    )

    assert response.status_code == 422

def test_api_controla_error_de_ollama(monkeypatch):
    def fake_analizar(mensaje):
        raise Exception("Ollama no está disponible")

    monkeypatch.setattr(
        "backend.main.llm_service.analizar",
        fake_analizar,
    )

    response = client.post(
        "/incidencias",
        json={
            "mensaje": "He encontrado un perro herido",
            "proveedor": "ollama",
        },
    )

    assert response.status_code == 503

    data = response.json()

    assert data["detail"]["error"] == "El proveedor Ollama no está disponible."