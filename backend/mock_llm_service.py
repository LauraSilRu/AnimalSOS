from backend.schemas import (
    Categoria,
    Departamento,
    MetricasLLM,
    ResultadoTriaje,
    Urgencia,
)


class MockLLMService:

    def analizar(self, mensaje: str):

        resultado = ResultadoTriaje(
            categoria=Categoria.ANIMAL_HERIDO,
            urgencia=Urgencia.ALTA,
            departamento=Departamento.RESCATE,
            resumen="Animal herido requiere atención y posible rescate inmediato",
            accion_recomendada="Contactar al equipo de rescate",
            justificacion="La incidencia describe un animal que podría necesitar asistencia.",
        )

        metricas = MetricasLLM(
            proveedor="mock",
            modelo="mock-llm",
            tokens_entrada=0,
            tokens_salida=0,
            tokens_totales=0,
            latencia_segundos=0.0,
            coste_estimado=0.0,
        )

        return resultado, metricas