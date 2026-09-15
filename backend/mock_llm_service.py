from backend.schemas import (
    Categoria,
    Departamento,
    ResultadoTriaje,
    Urgencia,
)


class MockLLMService:
    def analizar(self, mensaje: str) -> ResultadoTriaje:
        return ResultadoTriaje(
            categoria=Categoria.ANIMAL_HERIDO,
            urgencia=Urgencia.ALTA,
            departamento=Departamento.RESCATE,
            resumen="Animal herido requiere atención y posible rescate inmediato",
            accion_recomendada="Contactar al equipo de rescate",
            razonamiento="La incidencia describe un animal que podría necesitar asistencia.",
        )