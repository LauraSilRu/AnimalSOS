from enum import Enum


class DecisionFiltro(str, Enum):
    SIN_LLM = "sin_llm"
    REQUIERE_LLM = "requiere_llm"


REGLAS_SIMPLES = {
    "informacion": [
        "horario",
        "horarios",
        "horas de apertura",
        "cuando abre",
        "cuando cierra",
    ],
    "donacion": [
        "quiero donar",
        "quiero hacer una donación",
        "quiero donar dinero",
        "hacer una donación",
    ],
    "voluntariado": [
        "quiero ser voluntario",
        "quiero hacer voluntariado",
        "hacer voluntariado",
        "quiero ayudar como voluntario",
    ],
}


def analizar_filtro(mensaje: str) -> tuple[DecisionFiltro, str | None]:
    mensaje_normalizado = mensaje.lower().strip()

    for categoria, palabras_clave in REGLAS_SIMPLES.items():
        for palabra in palabras_clave:
            if palabra in mensaje_normalizado:
                return DecisionFiltro.SIN_LLM, categoria

    return DecisionFiltro.REQUIERE_LLM, None