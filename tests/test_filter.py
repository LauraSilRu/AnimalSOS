from backend.filter import DecisionFiltro, analizar_filtro


def test_informacion_no_necesita_llm():
    decision, categoria = analizar_filtro(
        "Quiero saber el horario de la protectora."
    )

    assert decision == DecisionFiltro.SIN_LLM
    assert categoria == "informacion"


def test_donacion_no_necesita_llm():
    decision, categoria = analizar_filtro(
        "Quiero hacer una donación."
    )

    assert decision == DecisionFiltro.SIN_LLM
    assert categoria == "donacion"


def test_caso_complejo_requiere_llm():
    decision, categoria = analizar_filtro(
        "He encontrado un perro herido junto a una carretera."
    )

    assert decision == DecisionFiltro.REQUIERE_LLM
    assert categoria is None