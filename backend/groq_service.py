import json
import os
import time

from dotenv import load_dotenv
from groq import Groq, RateLimitError

from backend.schemas import MetricasLLM, ResultadoTriaje


load_dotenv()


PROMPT_SISTEMA = """
Eres el motor de triaje de AnimalSOS, una herramienta de apoyo
para protectoras y asociaciones de rescate animal.

Tu tarea es analizar una incidencia y clasificarla.

CATEGORÍAS PERMITIDAS:
- animal_herido
- animal_perdido
- animal_abandonado
- posible_maltrato
- rescate
- adopcion
- acogida
- otro

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

REGLAS:
- Un animal herido o en peligro debe dirigirse normalmente a rescate.
- Una situación con peligro inmediato para la vida del animal debe tener
  urgencia critica.
- Una lesión que requiere atención rápida pero sin peligro inmediato
  puede tener urgencia alta.
- Las consultas generales, administrativas o de voluntariado no deben
  clasificarse como rescate si no existe una emergencia.
- No inventes información que no aparezca en la incidencia.
- Utiliza exclusivamente los valores permitidos.

RESUMEN:
- Debe tener entre 8 y 12 palabras.
- Debe ser claro y conciso.

JUSTIFICACIÓN:
- Explica brevemente la decisión.
- No muestres razonamientos internos ni procesos de pensamiento.

CONTROL DE SESGOS:
- No utilices género, origen, raza, nacionalidad, etnia o barrio
  para determinar la urgencia.
- La urgencia debe basarse exclusivamente en las características
  objetivas de la situación y el posible riesgo para el animal.

Devuelve únicamente el resultado estructurado solicitado.
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