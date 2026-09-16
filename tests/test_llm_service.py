import pytest
from pydantic import ValidationError

from backend.llm_service import OllamaService


def test_llm_rechaza_categoria_no_permitida(monkeypatch):
    respuesta_falsa = {
        "message": {
            "content": (
                '{"categoria":"emergencia_veterinaria",'
                '"urgencia":"alta",'
                '"departamento":"rescate",'
                '"resumen":"Perro herido necesita atención veterinaria '
                'urgente y rescate inmediato",'
                '"accion_recomendada":"Contactar con el equipo de rescate",'
                '"justificacion":"El animal presenta lesiones y necesita '
                'atención."}'
            )
        }
    }

    def fake_chat(*args, **kwargs):
        return respuesta_falsa

    monkeypatch.setattr(
        "backend.llm_service.ollama.chat",
        fake_chat,
    )

    with pytest.raises(ValidationError):
        OllamaService().analizar(
            "He encontrado un perro herido junto a una carretera."
        )