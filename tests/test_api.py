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
    assert response.json() == {
        "mensaje_recibido": "He encontrado un perro herido junto a una carretera."
    }


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