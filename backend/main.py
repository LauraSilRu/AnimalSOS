from fastapi import FastAPI

from backend.filter import analizar_filtro
from backend.groq_service import GroqService
from backend.llm_service import OllamaService
from backend.schemas import IncidenciaEntrada, Proveedor


app = FastAPI(
    title="AnimalSOS",
    description="Motor inteligente de triaje para protectoras y asociaciones de rescate animal",
    version="0.1.0",
)


llm_service = OllamaService()
groq_service = GroqService()


@app.get("/")
def root():
    return {
        "app": "AnimalSOS",
        "status": "ok",
    }


@app.post("/incidencias")
def crear_incidencia(incidencia: IncidenciaEntrada):

    # Primero aplicamos el filtro.
    decision, categoria = analizar_filtro(incidencia.mensaje)

    # Si es un caso sencillo, no necesitamos utilizar ningún LLM.
    if decision.value == "sin_llm":
        return {
            "mensaje_recibido": incidencia.mensaje,
            "decision_filtro": decision,
            "categoria": categoria,
            "proveedor": "ninguno",
        }

    # -------- OLLAMA --------
    if incidencia.proveedor == Proveedor.OLLAMA:

        resultado, metricas = llm_service.analizar(
            incidencia.mensaje
        )

        return {
            "mensaje_recibido": incidencia.mensaje,
            "decision_filtro": decision,
            "proveedor": "ollama",
            "resultado": resultado,
            "metricas": metricas,
        }

    # -------- GROQ --------
    if incidencia.proveedor == Proveedor.GROQ:

        resultado, metricas = groq_service.analizar(
            incidencia.mensaje
        )

        return {
            "mensaje_recibido": incidencia.mensaje,
            "decision_filtro": decision,
            "proveedor": "groq",
            "resultado": resultado,
            "metricas": metricas,
        }

    # -------- COMPARAR --------
    if incidencia.proveedor == Proveedor.COMPARAR:

        resultado_ollama, metricas_ollama = llm_service.analizar(
            incidencia.mensaje
        )

        resultado_groq, metricas_groq = groq_service.analizar(
            incidencia.mensaje
        )

        return {
            "mensaje_recibido": incidencia.mensaje,
            "decision_filtro": decision,
            "proveedor": "comparar",
            "resultados": {
                "ollama": resultado_ollama,
                "groq": resultado_groq,
            },
            "metricas": {
                "ollama": metricas_ollama,
                "groq": metricas_groq,
            },
        }