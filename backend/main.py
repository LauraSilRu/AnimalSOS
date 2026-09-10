from fastapi import FastAPI

from backend.schemas import IncidenciaEntrada


app = FastAPI(
    title="AnimalSOS",
    description="Motor inteligente de triaje para protectoras y asociaciones de rescate animal",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "app": "AnimalSOS",
        "status": "ok",
    }


@app.post("/incidencias")
def crear_incidencia(incidencia: IncidenciaEntrada):
    return {
        "mensaje_recibido": incidencia.mensaje,
    }