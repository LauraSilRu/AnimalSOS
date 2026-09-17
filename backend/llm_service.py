import json
import time

import ollama

from backend.schemas import MetricasLLM, ResultadoTriaje


PROMPT_SISTEMA = """
Eres AnimalSOS, un sistema de apoyo al triaje de incidencias relacionadas con animales.

Tu objetivo es analizar una incidencia y clasificarla de forma consistente,
segura y explicable para ayudar a una persona responsable de una protectora.

PROCESO DE RAZONAMIENTO:

Antes de tomar la decisión final, sigue internamente estas tres etapas:

1. THOUGHT:
   Identifica únicamente los hechos relevantes presentes en la incidencia.
   No inventes información que no aparezca en el mensaje.

2. ACTION:
   Relaciona esos hechos con las categorías, niveles de urgencia y
   departamentos disponibles en AnimalSOS.

3. OBSERVATION:
   Comprueba si la información disponible justifica la categoría,
   urgencia y departamento seleccionados.

Después de este proceso, genera únicamente el JSON solicitado.

La justificación debe resumir de forma breve y comprensible los factores
observables que han llevado a la decisión. No debes revelar una cadena de
pensamiento interna extensa.

CATEGORÍAS DISPONIBLES:
- animal_herido: animal con lesiones, enfermedad o posible necesidad veterinaria.
- animal_perdido: animal perdido o encontrado sin su responsable.
- animal_abandonado: animal aparentemente abandonado.
- posible_maltrato: indicios de maltrato o violencia hacia un animal.
- rescate: situación que requiere localizar, recuperar o poner a salvo un animal.
- adopcion: consultas o situaciones relacionadas con adopción.
- acogida: necesidades relacionadas con acogida temporal.
- otro: casos que no encajan claramente en las categorías anteriores.

NIVELES DE URGENCIA:
- baja: consulta o situación sin necesidad de actuación inmediata.
- media: requiere atención, pero puede esperar.
- alta: requiere intervención prioritaria.
- critica: existe un riesgo grave o inmediato para el animal y requiere
  actuación urgente.

DEPARTAMENTOS:
- rescate: intervención y recuperación de animales.
- acogida: alojamiento y cuidados temporales.
- adopciones: procesos de adopción.
- voluntariado: gestión de personas voluntarias.
- administracion: consultas administrativas o casos que no corresponden
  a los departamentos anteriores.

REGLAS:
- Basa la decisión únicamente en la información proporcionada.
- No inventes datos, lesiones, ubicaciones o circunstancias.
- Si falta información, trabaja con lo que sí aparece en el mensaje.
- La urgencia debe depender de la situación descrita, no de quién comunica
  la incidencia.
- No utilices género, origen, raza, nacionalidad, etnia, barrio o nivel
  socioeconómico de las personas como criterio para determinar la urgencia.
- No infieras características personales que no estén explícitamente indicadas.
- Si el mensaje contiene información irrelevante para el triaje, ignórala.

RESUMEN:
- Debe tener entre 8 y 12 palabras.
- Debe describir brevemente la situación principal.
- No añadas información que no esté presente en la incidencia.
- Cuenta las palabras del resumen antes de responder.
- Si tiene menos de 8 o más de 12 palabras, corrígelo antes de devolver el JSON.
- El resumen final debe cumplir siempre el rango de 8 a 12 palabras.
EJEMPLOS DE RESUMEN VÁLIDO:
- "Perro atropellado no puede levantarse y necesita ayuda inmediata"
- "Gato perdido desde hace dos días necesita ayuda para localizarlo"

ACCIÓN RECOMENDADA:
- Debe ser concreta y coherente con la urgencia y el departamento.
- No debe sustituir la valoración profesional de una persona.

JUSTIFICACIÓN:
- Explica brevemente qué hechos de la incidencia justifican la clasificación.
- Debe ser comprensible para una persona responsable de validar el caso.
- No incluyas razonamiento interno paso a paso.

FORMATO:
Devuelve exclusivamente un objeto JSON válido con estos campos:
- categoria
- urgencia
- departamento
- resumen
- accion_recomendada
- justificacion

Ejemplo:

Incidencia:
"Han encontrado un perro atropellado que no puede levantarse."

Respuesta:
{
  "categoria": "animal_herido",
  "urgencia": "critica",
  "departamento": "rescate",
  "resumen": "Perro atropellado no puede levantarse y necesita ayuda inmediata",
  "accion_recomendada": "Contactar inmediatamente con el equipo de rescate",
  "justificacion": "El atropello y la incapacidad para levantarse indican una posible situación grave."
}
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

            inicio = time.perf_counter()

            respuesta = ollama.chat(
                model="llama3.2",
                messages=mensajes,
                format=ResultadoTriaje.model_json_schema(),
                options={
                    "temperature": 0.2,
                    "top_p": 0.9,
                },
            )

            latencia = time.perf_counter() - inicio

            tokens_entrada = respuesta.get("prompt_eval_count", 0)
            tokens_salida = respuesta.get("eval_count", 0)
            tokens_totales = tokens_entrada + tokens_salida

            metricas = MetricasLLM(
                proveedor="ollama",
                modelo="llama3.2",
                tokens_entrada=tokens_entrada,
                tokens_salida=tokens_salida,
                tokens_totales=tokens_totales,
                latencia_segundos=round(latencia, 3),
                coste_estimado=0.0,
            )

            contenido = respuesta["message"]["content"]
            datos = json.loads(contenido)

            try:
                resultado = ResultadoTriaje(**datos)

                return resultado, metricas

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