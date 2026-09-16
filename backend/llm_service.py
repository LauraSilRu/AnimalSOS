import json

import ollama

from backend.schemas import ResultadoTriaje


PROMPT_SISTEMA = """
Eres el motor de triaje de AnimalSOS, una herramienta de apoyo
para protectoras y asociaciones de rescate animal.

Tu tarea es analizar una incidencia y clasificarla.

CATEGORÍAS PERMITIDAS:
- animal_herido: animal con lesiones, dolor o síntomas físicos evidentes.
- animal_perdido: animal que parece perdido o separado de su responsable.
- animal_abandonado: animal dejado sin responsable o cuidado.
- posible_maltrato: existen indicios de maltrato, abuso o violencia.
- rescate: situación que requiere localizar, recuperar o poner a salvo
  a un animal en peligro.
- adopcion: consultas relacionadas con adoptar un animal.
- acogida: consultas relacionadas con acoger temporalmente un animal.
- otro: casos que no encajan claramente en las categorías anteriores.

URGENCIAS PERMITIDAS:
- baja
- media
- alta
- critica

DEPARTAMENTOS PERMITIDOS:
- rescate
- acogida
- adopciones
- voluntariado
- administracion

REGLAS DE CLASIFICACIÓN:
- Un animal herido o en peligro debe dirigirse normalmente a rescate.
- Una situación con peligro inmediato para la vida del animal debe tener
  urgencia critica.
- Una lesión que requiere atención rápida pero sin peligro inmediato
  puede tener urgencia alta.
- Las consultas generales, administrativas o de voluntariado no deben
  clasificarse como rescate si no existe una emergencia.
- No inventes información que no aparezca en la incidencia.
- Utiliza exclusivamente los valores permitidos anteriormente.

RESUMEN:
- Debe resumir la incidencia en entre 8 y 12 palabras.
- Debe ser claro y conciso.

JUSTIFICACIÓN:
- Explica brevemente por qué has elegido la categoría, urgencia y
  departamento.
- No muestres razonamientos internos ni procesos de pensamiento.
- Devuelve únicamente el resultado estructurado solicitado.
"""


class OllamaService:
    def analizar(self, mensaje: str) -> ResultadoTriaje:
        mensajes = [
            {
                "role": "system",
                "content": PROMPT_SISTEMA,
            },
            {
                "role": "user",
                "content": (
                    "Ejemplo de referencia:\n"
                    "Incidencia: Un perro ha sido atropellado y está herido "
                    "en una carretera.\n"
                    "Categoría: animal_herido\n"
                    "Urgencia: critica\n"
                    "Departamento: rescate"
                ),
            },
            {
                "role": "assistant",
                "content": (
                    '{"categoria":"animal_herido",'
                    '"urgencia":"critica",'
                    '"departamento":"rescate",'
                    '"resumen":"Perro atropellado y herido necesita rescate '
                    'y atención urgente inmediata",'
                    '"accion_recomendada":"Contactar con el equipo de rescate '
                    'y trasladar al animal a atención veterinaria",'
                    '"justificacion":"El animal presenta una lesión causada '
                    'por un atropello y se encuentra en una situación de '
                    'peligro."}'
                ),
            },
            {
                "role": "user",
                "content": mensaje,
            },
        ]

        for intento in range(2):
            respuesta = ollama.chat(
                model="llama3.2",
                messages=mensajes,
                format=ResultadoTriaje.model_json_schema(),
                options={
                    "temperature": 0.2,
                    "top_p": 0.9,
                },
            )

            contenido = respuesta["message"]["content"]
            datos = json.loads(contenido)

            try:
                return ResultadoTriaje(**datos)

            except Exception as error:
                if intento == 0:
                    mensajes.append(
                        {
                            "role": "user",
                            "content": (
                                "La respuesta anterior no cumple el esquema. "
                                "Corrige el resultado y devuelve un nuevo JSON. "
                                f"Error de validación: {error}"
                            ),
                        }
                    )
                else:
                    raise