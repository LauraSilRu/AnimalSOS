import unicodedata
from enum import Enum


class DecisionFiltro(str, Enum):
    SIN_LLM = "sin_llm"
    REQUIERE_LLM = "requiere_llm"


REGLAS_SIMPLES = {
    "informacion": [
        "horario",
        "horarios",
        "hora de apertura",
        "horas de apertura",
        "cuando abre",
        "cuando cierra",
        "a que hora abre",
        "a que hora cierra",
    ],
    "donacion": [
        "quiero donar",
        "me gustaria donar",
        "hacer una donacion",
        "quiero hacer una donacion",
        "me gustaria hacer una donacion",
        "donar dinero",
        "donar dinero",
        "aportar dinero",
        "ayudar economicamente",
        "ayuda economica",
    ],
    "voluntariado": [
        "quiero ser voluntario",
        "quiero hacer voluntariado",
        "hacer voluntariado",
        "quiero ayudar como voluntario",
        "me gustaria hacer voluntariado",
        "me gustaria ser voluntario",
    ],
}


def normalizar_texto(texto: str) -> str:
    """Convierte el texto a minúsculas y elimina las tildes."""

    texto = texto.lower().strip()

    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )


def analizar_filtro(mensaje: str) -> tuple[DecisionFiltro, str | None]:
    """Determina si una incidencia puede resolverse mediante reglas simples."""

    mensaje_normalizado = normalizar_texto(mensaje)

    for categoria, palabras_clave in REGLAS_SIMPLES.items():
        for palabra in palabras_clave:
            if palabra in mensaje_normalizado:
                return DecisionFiltro.SIN_LLM, categoria

    return DecisionFiltro.REQUIERE_LLM, None