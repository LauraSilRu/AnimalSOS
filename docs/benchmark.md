# Benchmark de proveedores LLM

## Objetivo

Comparar el comportamiento de los dos proveedores utilizados en AnimalSOS:

- Ollama con el modelo local `llama3.2`
- Groq con el modelo `openai/gpt-oss-20b`

La comparación se realiza utilizando las mismas incidencias y midiendo latencia, tokens utilizados, coste estimado y validez de las respuestas.

## Metodología

Se ejecutaron cinco incidencias representativas de diferentes situaciones de triaje.

Ambos proveedores recibieron las mismas incidencias y utilizaron el mismo esquema de salida mediante Pydantic.

Los parámetros utilizados fueron:

- `temperature`: 0.2
- `top_p`: 0.9

Se registraron:

- número de respuestas válidas;
- latencia;
- tokens utilizados;
- coste estimado;
- categoría asignada;
- nivel de urgencia;
- departamento asignado.

El benchmark se ejecutó localmente desde `benchmark.py`.

## Incidencias utilizadas

1. Perro atropellado que no puede levantarse.
2. Gato perdido desde hace dos días.
3. Persona golpeando repetidamente a un perro.
4. Consulta sobre adopción de un perro.
5. Animal solo en la calle cuya situación no está clara.

## Resultados

| Incidencia | Ollama | Groq |
|---|---|---|
| 1 | animal_herido / critica / rescate | animal_herido / critica / rescate |
| 2 | animal_perdido / baja / rescate | animal_perdido / media / rescate |
| 3 | posible_maltrato / alta / rescate | posible_maltrato / critica / rescate |
| 4 | adopcion / baja / adopciones | adopcion / baja / adopciones |
| 5 | animal_perdido / baja / rescate | animal_abandonado / baja / rescate |

### Métricas

| Métrica | Ollama | Groq |
|---|---:|---:|
| Respuestas válidas | 5/5 | 5/5 |
| Latencia media | 3.498 s | 0.961 s |
| Tokens medios | 1416 | 1665 |
| Coste total estimado | 0 € | 0.00105022 € |

## Interpretación

En esta prueba, ambos proveedores generaron respuestas que cumplieron el esquema de salida definido por Pydantic.

Groq presentó una menor latencia media en las cinco incidencias evaluadas, mientras que Ollama presentó un coste estimado de cero al ejecutarse localmente.

Ollama utilizó menos tokens de media en esta ejecución.

Los modelos coincidieron completamente en las incidencias 1 y 4.

En la incidencia 2 coincidieron en la categoría y el departamento, pero asignaron diferentes niveles de urgencia.

En la incidencia 3 coincidieron en la categoría y el departamento, pero también difirieron en la urgencia.

En la incidencia 5 asignaron categorías diferentes.

Estas diferencias muestran que la salida de un LLM puede variar ante una misma incidencia y justifican la incorporación de una fase de revisión humana antes de tomar una decisión definitiva.

## Validación mediante Pydantic

Durante una ejecución anterior del benchmark se detectaron respuestas cuyo campo `resumen` no cumplía la restricción de entre 8 y 12 palabras.

La validación Pydantic rechazó estas respuestas.

Posteriormente se reforzó el prompt indicando explícitamente al modelo que debía comprobar la longitud del resumen antes de devolver el JSON.

Tras este ajuste, ambos proveedores obtuvieron 5/5 respuestas válidas en la ejecución final.

Este comportamiento demuestra el papel de Pydantic como capa de validación entre la respuesta del modelo y la aplicación.

## Limitaciones

Los resultados corresponden a una única ejecución de cinco incidencias y no representan el comportamiento general de los modelos.

La latencia de Ollama puede depender del hardware local utilizado para ejecutar el modelo.

El coste de Groq es una estimación basada en los tokens utilizados durante la ejecución.

La evaluación de calidad realizada es principalmente funcional: se comprueba la validez de la estructura y se comparan las clasificaciones obtenidas. No se ha realizado una evaluación estadística sobre un conjunto grande de incidencias etiquetadas manualmente.

## Conclusión técnica

El benchmark permite observar las diferencias prácticas entre utilizar un modelo local y un proveedor externo.

Ollama proporciona ejecución local sin coste por petición, mientras que Groq presentó una menor latencia en las pruebas realizadas.

Las diferencias de clasificación observadas entre proveedores refuerzan la decisión de utilizar los LLM como sistema de apoyo al triaje y mantener una revisión humana para validar las decisiones antes de actuar sobre una incidencia.