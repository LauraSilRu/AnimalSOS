import json
import os
import time

from dotenv import load_dotenv
from groq import Groq, RateLimitError

from backend.schemas import MetricasLLM, ResultadoTriaje


load_dotenv()


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

EJEMPLO DE CLASIFICACIÓN (FEW-SHOT):

Entrada:
"Gato perdido desde hace dos días. Su familia no consigue localizarlo."

Salida esperada:
{
  "categoria": "animal_perdido",
  "urgencia": "media",
  "departamento": "rescate",
  "resumen": "Gato perdido desde hace dos días necesita ayuda para localizarlo",
  "accion_recomendada": "Recopilar información y coordinar acciones para localizar al animal.",
  "justificacion": "La incidencia describe un gato perdido que necesita ayuda para ser localizado."
}

Utiliza este ejemplo como referencia para relacionar los hechos de la incidencia
con la categoría, urgencia y departamento correspondientes. No copies el ejemplo
literalmente si la nueva incidencia describe una situación diferente.

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


class GroqService:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("No se ha encontrado GROQ_API_KEY.")

        self.client = Groq(api_key=api_key)

    def analizar(self, mensaje: str):

        max_reintentos = 3

        schema = ResultadoTriaje.model_json_schema()
        schema["additionalProperties"] = False

        for intento in range(max_reintentos):

            inicio = time.perf_counter()

            try:

                respuesta = self.client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": PROMPT_SISTEMA,
                        },
                        {
                            "role": "user",
                            "content": mensaje,
                        },
                    ],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "resultado_triaje",
                            "strict": True,
                            "schema": schema,
                        },
                    },
                    temperature=0.2,
                    top_p=0.9,
                )

                latencia = time.perf_counter() - inicio

                contenido = respuesta.choices[0].message.content

                datos = json.loads(contenido)

                resultado = ResultadoTriaje(**datos)

                tokens_entrada = respuesta.usage.prompt_tokens
                tokens_salida = respuesta.usage.completion_tokens
                tokens_totales = respuesta.usage.total_tokens

                coste_entrada = (
                    tokens_entrada / 1_000_000
                ) * 0.075

                coste_salida = (
                    tokens_salida / 1_000_000
                ) * 0.30

                coste_estimado = coste_entrada + coste_salida

                metricas = MetricasLLM(
                    proveedor="groq",
                    modelo="openai/gpt-oss-20b",
                    tokens_entrada=tokens_entrada,
                    tokens_salida=tokens_salida,
                    tokens_totales=tokens_totales,
                    latencia_segundos=round(latencia, 3),
                    coste_estimado=round(coste_estimado, 8),
                )

                return resultado, metricas

            except RateLimitError:

                if intento == max_reintentos - 1:
                    raise

                espera = 2 ** intento

                print(
                    f"Rate limit de Groq. "
                    f"Reintento {intento + 1}/{max_reintentos} "
                    f"en {espera} segundos..."
                )

                time.sleep(espera)