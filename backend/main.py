from fastapi import FastAPI
from backend.filter import analizar_filtro
from backend.schemas import IncidenciaEntrada
from backend.llm_service import OllamaService


app = FastAPI(
    title="AnimalSOS",
    description="Motor inteligente de triaje para protectoras y asociaciones de rescate animal",
    version="0.1.0",
)

llm_service = OllamaService()

@app.get("/")
def root():
    return {
        "app": "AnimalSOS",
        "status": "ok",
    }


@app.post("/incidencias")
def crear_incidencia(incidencia: IncidenciaEntrada):
    decision, categoria = analizar_filtro(incidencia.mensaje)

    if decision.value == "sin_llm":
        return {
            "mensaje_recibido": incidencia.mensaje,
            "decision_filtro": decision,
            "categoria": categoria,
        }

    resultado = llm_service.analizar(incidencia.mensaje)

    return {
        "mensaje_recibido": incidencia.mensaje,
        "decision_filtro": decision,
        "resultado": resultado,
    }