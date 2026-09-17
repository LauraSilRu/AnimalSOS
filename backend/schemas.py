from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Categoria(str, Enum):
    ANIMAL_HERIDO = "animal_herido"
    ANIMAL_PERDIDO = "animal_perdido"
    ANIMAL_ABANDONADO = "animal_abandonado"
    POSIBLE_MALTRATO = "posible_maltrato"
    RESCATE = "rescate"
    ADOPCION = "adopcion"
    ACOGIDA = "acogida"
    OTRO = "otro"


class Urgencia(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class Departamento(str, Enum):
    RESCATE = "rescate"
    ACOGIDA = "acogida"
    ADOPCIONES = "adopciones"
    VOLUNTARIADO = "voluntariado"
    ADMINISTRACION = "administracion"

class Proveedor(str, Enum):
    OLLAMA = "ollama"
    GROQ = "groq"
    COMPARAR = "comparar"


class IncidenciaEntrada(BaseModel):
    mensaje: str = Field(
        ...,
        min_length=1,
        description="Descripción de la incidencia comunicada por el usuario",
    )
    proveedor: Proveedor = Field(
        default=Proveedor.OLLAMA,
        description="Proveedor LLM utilizado para analizar la incidencia",
    )


class ResultadoTriaje(BaseModel):
    categoria: Categoria
    urgencia: Urgencia
    departamento: Departamento
    resumen: str
    accion_recomendada: str
    justificacion: str

    @field_validator("resumen")
    @classmethod
    def validar_resumen(cls, value: str) -> str:
        word_count = len(value.split())

        if not 8 <= word_count <= 12:
            raise ValueError(
                "El resumen debe contener entre 8 y 12 palabras."
            )

        return value

class MetricasLLM(BaseModel):
    proveedor: str
    modelo: str
    tokens_entrada: int
    tokens_salida: int
    tokens_totales: int
    latencia_segundos: float
    coste_estimado: float