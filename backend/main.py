from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from backend.filter import analizar_filtro
from backend.groq_service import GroqService
from backend.llm_service import OllamaService
from backend.schemas import IncidenciaEntrada, Proveedor, Departamento
from backend.incident_log import guardar_incidencia


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

        departamentos_sin_llm = {
            "informacion": Departamento.ADMINISTRACION.value,
            "donacion": Departamento.ADMINISTRACION.value,
            "voluntariado": Departamento.VOLUNTARIADO.value,
        }

        departamento = departamentos_sin_llm.get(
            categoria,
            Departamento.ADMINISTRACION.value,
        )

        decision_final = {
            "categoria": categoria,
            "departamento": departamento,
        }

        guardar_incidencia(
            mensaje=incidencia.mensaje,
            proveedor="ninguno",
            resultado_ia=None,
            decision_final=decision_final,
            validacion_humana=False,
        )

        return {
            "mensaje_recibido": incidencia.mensaje,
            "decision_filtro": decision,
            "categoria": categoria,
            "departamento": departamento,
            "proveedor": "ninguno",
        }

    # -------- OLLAMA --------
    if incidencia.proveedor == Proveedor.OLLAMA:

        try:
            resultado, metricas = llm_service.analizar(
                incidencia.mensaje
            )
        except ValidationError as error:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "La respuesta de Ollama no cumple el esquema esperado.",
                    "detalle": str(error),
                },
            )
        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "El proveedor Ollama no está disponible.",
                    "detalle": str(error),
                },
            )

        registro = guardar_incidencia(
            mensaje=incidencia.mensaje,
            proveedor="ollama",
            resultado_ia=resultado.model_dump(),
            decision_final=resultado.model_dump(),
            validacion_humana=False,
        )

        return {
            "id": registro["id"],
            "mensaje_recibido": incidencia.mensaje,
            "decision_filtro": decision,
            "proveedor": "ollama",
            "resultado": resultado,
            "metricas": metricas,
        }

    # -------- GROQ --------
    if incidencia.proveedor == Proveedor.GROQ:

        try:
            resultado, metricas = groq_service.analizar(
                incidencia.mensaje
            )
        except ValidationError as error:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "La respuesta de Groq no cumple el esquema esperado.",
                    "detalle": str(error),
                },
            )
        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "El proveedor Groq no está disponible.",
                    "detalle": str(error),
                },
            )

        registro = guardar_incidencia(
            mensaje=incidencia.mensaje,
            proveedor="groq",
            resultado_ia=resultado.model_dump(),
            decision_final=resultado.model_dump(),
            validacion_humana=False,
        )

        return {
            "id": registro["id"],
            "mensaje_recibido": incidencia.mensaje,
            "decision_filtro": decision,
            "proveedor": "groq",
            "resultado": resultado,
            "metricas": metricas,
        }

    # -------- COMPARAR --------
    if incidencia.proveedor == Proveedor.COMPARAR:

        try:
            resultado_ollama, metricas_ollama = llm_service.analizar(
                incidencia.mensaje
            )

            resultado_groq, metricas_groq = groq_service.analizar(
                incidencia.mensaje
            )

        except ValidationError as error:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Uno de los modelos no cumple el esquema esperado.",
                    "detalle": str(error),
                },
            )

        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Uno de los proveedores no está disponible.",
                    "detalle": str(error),
                },
            )

        registro = guardar_incidencia(
            mensaje=incidencia.mensaje,
            proveedor="comparar",
            resultado_ia={
                "ollama": resultado_ollama.model_dump(),
                "groq": resultado_groq.model_dump(),
            },
            decision_final=None,
            validacion_humana=False,
        )

        return {
            "id": registro["id"],
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