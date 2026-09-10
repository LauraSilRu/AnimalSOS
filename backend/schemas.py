from enum import Enum

from pydantic import BaseModel, Field


class Urgencia(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class Categoria(str, Enum):
    ANIMAL_HERIDO = "animal_herido"
    ANIMAL_EN_PELIGRO = "animal_en_peligro"
    ANIMAL_PERDIDO = "animal_perdido"
    ANIMAL_ENCONTRADO = "animal_encontrado"
    ABANDONO_O_MALTRATO = "abandono_o_maltrato"
    ADOPCION = "adopcion"
    ACOGIDA = "acogida"
    VOLUNTARIADO = "voluntariado"
    DONACION = "donacion"
    INFORMACION = "informacion"


class Departamento(str, Enum):
    RESCATE = "rescate"
    REENCUENTROS = "reencuentros"
    ADOPCIONES = "adopciones"
    ACOGIDAS = "acogidas"
    VOLUNTARIADO = "voluntariado"
    DONACIONES = "donaciones"
    ATENCION_GENERAL = "atencion_general"


class IncidenciaEntrada(BaseModel):
    mensaje: str = Field(
        ...,
        min_length=1,
        description="Descripción de la incidencia comunicada por el usuario",
    )


class ResultadoTriaje(BaseModel):
    categoria: Categoria
    urgencia: Urgencia
    departamento: Departamento
    resumen: str
    accion_recomendada: str
    razonamiento: str