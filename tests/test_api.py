from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_crear_incidencia_valida():
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