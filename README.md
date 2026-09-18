# 🐾 AnimalSOS

Motor inteligente de triaje para protectoras y asociaciones de rescate animal.

AnimalSOS es una aplicación que utiliza modelos de lenguaje (LLM) para analizar incidencias relacionadas con animales, clasificarlas y priorizarlas según su urgencia.

El sistema combina un filtro previo de reglas simples con modelos LLM locales y externos, validación estructurada mediante Pydantic, métricas de rendimiento y una fase final de revisión humana.

---

## 🎯 Objetivo del proyecto

Las protectoras y asociaciones de rescate reciben incidencias muy diferentes: animales heridos, animales perdidos, posibles casos de maltrato, adopciones, acogidas o solicitudes de ayuda.

El objetivo de AnimalSOS es proporcionar una primera clasificación automática que ayude a organizar estas incidencias y facilite su derivación al departamento correspondiente.

La IA funciona como **sistema de apoyo**, no como sustituto de la decisión de una persona responsable.

---

## 🧩 Funcionamiento general

El flujo de una incidencia es:

```text
Usuario
   │
   ▼
FastAPI
   │
   ▼
Filtro de reglas simples
   │
   ├── Caso sencillo ──► Respuesta directa
   │
   └── Caso complejo
            │
            ▼
       Selección de proveedor
            │
       ┌────┴────────────┐
       ▼                 ▼
    Ollama              Groq
       │                 │
       └───────┬─────────┘
               ▼
       Respuesta JSON
               │
               ▼
       Validación Pydantic
               │
               ▼
       Resultado + métricas
               │
               ▼
        Revisión humana
               │
               ▼
        Decisión final
               │
               ▼
        Registro histórico
```

El usuario puede seleccionar:

- **Ollama**: ejecución local mediante `llama3.2`.
- **Groq**: proveedor externo mediante `openai/gpt-oss-20b`.
- **Comparar ambos**: ejecuta los dos modelos sobre la misma incidencia.

---

## 🏗️ Arquitectura

El proyecto está organizado en varias capas:

```text
AnimalSOS/
│
├── backend/
│   ├── main.py
│   ├── schemas.py
│   ├── filter.py
│   ├── llm_service.py
│   ├── groq_service.py
│   ├── mock_llm_service.py
│   └── incident_log.py
│
├── data/
│   └── .gitkeep
│
├── frontend/
│   └── app.py
│
├── tests/
│   ├── test_api.py
│   ├── test_filter.py
│   └── test_llm_service.py
│
├── docs/
│   └── benchmark.md
│
├── benchmark.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Backend

El backend está desarrollado con **FastAPI**.

`main.py` gestiona el endpoint `/incidencias`, aplica el filtro inicial y selecciona el proveedor LLM.

### Schemas

`schemas.py` contiene los modelos Pydantic utilizados para validar las entradas y salidas.

### Filtro previo

`filter.py` identifica algunas consultas sencillas que no necesitan utilizar un LLM.

Actualmente contempla:

- información sobre horarios;
- donaciones;
- voluntariado.

De esta forma, estos casos pueden resolverse directamente sin realizar una llamada al modelo.

### Servicios LLM

`llm_service.py` implementa la comunicación con Ollama.

`groq_service.py` implementa la comunicación con Groq.

`mock_llm_service.py` permite utilizar una respuesta simulada durante las pruebas sin depender de un modelo real.

### Registro de incidencias

`incident_log.py` gestiona el historial local de incidencias.

Permite:

- guardar cada incidencia procesada;
- registrar el método utilizado;
- conservar el resultado propuesto por la IA cuando corresponde;
- guardar la decisión final;
- actualizar una incidencia cuando existe validación humana.

El historial se almacena localmente en `data/incidencias.json`. Este archivo no se sube al repositorio porque está incluido en `.gitignore`. Se mantiene `data/.gitkeep` para conservar la estructura de la carpeta en Git.

---

# 🤖 Modelos utilizados

## Ollama

AnimalSOS utiliza Ollama para ejecutar localmente el modelo:

```text
llama3.2
```

Ventajas de esta opción:

- ejecución local;
- no requiere enviar la incidencia a un proveedor externo;
- coste estimado por petición: `0 €`;
- permite trabajar con un modelo de código abierto/local.

La aplicación utiliza salida estructurada mediante el esquema generado por Pydantic.

---

## Groq

Como proveedor externo se utiliza:

```text
openai/gpt-oss-20b
```

La respuesta se solicita mediante un esquema JSON estructurado y posteriormente se valida con Pydantic.

El sistema registra:

- tokens de entrada;
- tokens de salida;
- tokens totales;
- latencia;
- coste estimado.

Además, se ha implementado un sistema de reintentos ante errores de límite de peticiones (`RateLimitError`) utilizando backoff exponencial.

---

# 🧠 Prompt Engineering

El prompt utilizado por AnimalSOS está diseñado para obtener respuestas consistentes y estructuradas.

Incluye:

### Razonamiento estructurado

El modelo recibe un proceso de análisis dividido conceptualmente en:

```text
THOUGHT → ACTION → OBSERVATION
```

El razonamiento interno no se muestra como una cadena de pensamiento extensa. La aplicación únicamente recibe la respuesta estructurada y una justificación breve y comprensible.

### Few-shot prompting

El modelo recibe ejemplos de referencia de incidencias y respuestas esperadas para orientar el formato y la clasificación.

### Restricción de categorías

Las categorías posibles están definidas explícitamente:

- `animal_herido`
- `animal_perdido`
- `animal_abandonado`
- `posible_maltrato`
- `rescate`
- `adopcion`
- `acogida`
- `otro`

### Niveles de urgencia

La urgencia puede ser:

- `baja`
- `media`
- `alta`
- `critica`

### Departamentos

Los resultados se asignan a:

- `rescate`
- `acogida`
- `adopciones`
- `voluntariado`
- `administracion`

### Parámetros del modelo

Se utilizan:

```text
temperature = 0.2
top_p = 0.9
```

El objetivo es favorecer respuestas relativamente consistentes.

---

# 🛡️ Prevención de sesgos

El prompt incluye instrucciones explícitas para que la clasificación de una incidencia no dependa de características personales irrelevantes.

El modelo debe ignorar como criterio para determinar la urgencia:

- género;
- origen;
- raza;
- nacionalidad;
- etnia;
- barrio;
- nivel socioeconómico.

También se indica que no debe inferir características personales que no aparezcan explícitamente en la incidencia.

La urgencia debe depender de la situación descrita y de los hechos relevantes para el triaje.

---

# 🔒 Validación con Pydantic

La respuesta generada por el modelo no se acepta directamente.

Primero se convierte a un objeto `ResultadoTriaje` mediante Pydantic.

Esto permite controlar estructuralmente:

- categorías válidas;
- niveles de urgencia válidos;
- departamentos válidos;
- campos obligatorios;
- longitud del resumen.

El resumen debe contener entre **8 y 12 palabras**.

Si el modelo devuelve una categoría que no pertenece al conjunto permitido, Pydantic rechaza la respuesta.

Por ejemplo:

```text
emergencia_veterinaria
```

no es una categoría válida de AnimalSOS y provoca un error de validación.

En Ollama, cuando la respuesta no cumple el esquema, se realiza un segundo intento solicitando al modelo que corrija el resultado.

---

# 🚨 Gestión de errores

La API diferencia entre diferentes tipos de problemas.

### Error de validación

Si la respuesta del modelo no cumple el esquema esperado:

```text
HTTP 422
```

### Proveedor no disponible

Si Ollama o Groq no están disponibles:

```text
HTTP 503
```

### Entrada inválida

Si falta el mensaje o está vacío:

```text
HTTP 422
```

Esto evita que las respuestas incorrectas del modelo lleguen directamente a la interfaz de usuario.

---

# 📊 Métricas

AnimalSOS registra métricas para poder comparar los modelos.

Para cada ejecución se registran:

| Métrica | Descripción |
|---|---|
| Proveedor | Ollama o Groq |
| Modelo | Modelo utilizado |
| Tokens de entrada | Tokens utilizados en el prompt |
| Tokens de salida | Tokens generados |
| Tokens totales | Entrada + salida |
| Latencia | Tiempo de respuesta |
| Coste estimado | Coste calculado de la petición |

---

# ⚖️ Comparación de modelos

La aplicación permite ejecutar una misma incidencia utilizando los dos proveedores.

Esto permite comparar:

- clasificación;
- urgencia;
- departamento;
- latencia;
- número de tokens;
- coste estimado.

Los resultados del benchmark se encuentran en:

```text
docs/benchmark.md
```

El benchmark utiliza cinco incidencias representativas y ejecuta cada una con Ollama y Groq.

### Resultados de la ejecución final

| Métrica | Ollama | Groq |
|---|---:|---:|
| Respuestas válidas | 5/5 | 5/5 |
| Latencia media | 3.498 s | 0.961 s |
| Tokens medios | 1416 | 1665 |
| Coste total estimado | 0 € | 0.00105022 € |

Estos resultados corresponden a una única ejecución de cinco incidencias y no representan por sí mismos el comportamiento general de los modelos.

---

# 👩‍💼 Human-in-the-loop

La decisión generada por la IA no se considera automáticamente definitiva.

El dashboard incorpora una fase de **revisión humana**.

La persona responsable puede revisar y modificar:

- categoría;
- urgencia;
- departamento.

Después puede validar la decisión final.

Este enfoque permite utilizar la IA como herramienta de apoyo manteniendo la supervisión humana sobre las decisiones de triaje.

## 📋 Registro de incidencias

AnimalSOS mantiene un historial local de las incidencias procesadas para
poder consultar posteriormente cómo se resolvió cada caso.

Cada incidencia registrada incluye:

- Identificador de la incidencia.
- Fecha y hora.
- Mensaje original.
- Método utilizado: sin LLM, Ollama, Groq o comparación.
- Resultado propuesto por el modelo, cuando corresponde.
- Decisión final.
- Indicación de si hubo validación humana.

El registro permite diferenciar entre:

- ⚙️ **Decisión automática**: casos resueltos mediante reglas sin utilizar un LLM.
- 🤖 **Decisión de IA**: resultado generado por Ollama o Groq.
- 👩‍💼 **Validada por persona**: resultado revisado y confirmado o modificado por una persona.

En los casos en los que existe revisión humana se conservan tanto la
propuesta inicial de la IA como la decisión final, permitiendo comprobar
qué cambios se realizaron.

El historial se almacena localmente en:

`data/incidencias.json`

Este archivo está incluido en `.gitignore` para evitar subir al repositorio
los datos generados durante las pruebas. Se mantiene un `.gitkeep` para
conservar la estructura de la carpeta `data/` en Git.

---

# 🖥️ Dashboard

La interfaz está desarrollada con **Streamlit**.

Permite:

1. Introducir una incidencia.
2. Seleccionar el proveedor.
3. Ejecutar el análisis.
4. Visualizar la clasificación.
5. Consultar la justificación.
6. Consultar la acción recomendada.
7. Consultar las métricas.
8. Comparar Ollama y Groq.
9. Revisar y modificar la decisión.
10. Validar el resultado final.
11. Consultar el historial de incidencias registradas.

La interfaz también muestra gráficamente información relacionada con el rendimiento de los modelos durante la comparación.

---

# 🌐 API

## Endpoint principal

```http
POST /incidencias
```

### Ejemplo de petición

```json
{
  "mensaje": "He encontrado un perro herido junto a una carretera.",
  "proveedor": "ollama"
}
```

Los valores disponibles para `proveedor` son:

```text
ollama
groq
comparar
```

### Ejemplo de respuesta

```json
{
  "id": 1,
  "mensaje_recibido": "He encontrado un perro herido junto a una carretera.",
  "decision_filtro": "requiere_llm",
  "proveedor": "ollama",
  "resultado": {
    "categoria": "animal_herido",
    "urgencia": "alta",
    "departamento": "rescate",
    "resumen": "Perro herido junto a carretera necesita atención y rescate",
    "accion_recomendada": "Contactar con el equipo de rescate",
    "justificacion": "La incidencia describe un animal herido que necesita asistencia."
  }
}
```

---

# 🧪 Tests

El proyecto utiliza **Pytest**.

Se han implementado pruebas para diferentes partes de la aplicación.

### Filtro

Se comprueba que:

- las consultas de información no utilicen el LLM;
- las donaciones no utilicen el LLM;
- las incidencias complejas requieran un LLM.

### API

Se comprueba:

- funcionamiento del endpoint;
- respuesta de una incidencia;
- rechazo de mensajes vacíos;
- rechazo de peticiones sin mensaje;
- gestión de errores del proveedor Ollama.

### Validación LLM

Se comprueba que Pydantic rechace una categoría que no pertenece al esquema permitido.

Para las pruebas del endpoint se utiliza un servicio mock cuando no es necesario realizar una llamada real a un modelo.

---

# ▶️ Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/LauraSiluRu/AnimalSOS.git
cd AnimalSOS
```

## 2. Crear entorno virtual

En Windows:

```bash
python -m venv .venv
```

Activar:

```bash
.venv\Scripts\activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# 🦙 Configuración de Ollama

Instalar Ollama y descargar el modelo:

```bash
ollama pull llama3.2
```

Comprobar que funciona:

```bash
ollama run llama3.2
```

---

# 🔑 Configuración de Groq

Crear un archivo `.env` en la raíz del proyecto:

```text
GROQ_API_KEY=tu_clave_de_groq
```

El archivo `.env` está incluido en `.gitignore` y no debe subirse al repositorio.

---

# 🚀 Ejecución

## Iniciar el backend

Desde la raíz del proyecto:

```bash
uvicorn backend.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

La documentación interactiva de FastAPI está disponible en:

```text
http://127.0.0.1:8000/docs
```

## Iniciar el dashboard

En otra terminal:

```bash
streamlit run frontend/app.py
```

---

# 📈 Ejecutar el benchmark

Desde la raíz del proyecto:

```bash
python benchmark.py
```

El benchmark ejecuta las mismas cinco incidencias utilizando Ollama y Groq y muestra:

- resultados;
- latencia;
- tokens;
- coste estimado;
- clasificación;
- urgencia;
- departamento;
- resumen comparativo.

La documentación de los resultados se encuentra en:

```text
docs/benchmark.md
```

---

# 🧪 Ejecutar los tests

Desde la raíz:

```bash
pytest
```

Los tests se encuentran en:

```text
tests/
```

---

# 🔐 Consideraciones de seguridad

AnimalSOS está diseñado como un sistema de apoyo al triaje.

La clasificación generada por un LLM no sustituye la valoración profesional de una persona responsable.

El sistema incorpora:

- validación estructurada;
- categorías controladas;
- gestión de errores;
- revisión humana;
- registro de incidencias y decisiones finales;
- instrucciones contra sesgos;
- separación entre proveedores.

Las claves API se gestionan mediante variables de entorno y no deben almacenarse directamente en el código.

---

# ⚠️ Limitaciones

Actualmente el sistema presenta algunas limitaciones:

- El benchmark utiliza únicamente cinco incidencias.
- Los resultados corresponden a una única ejecución.
- La latencia de Ollama depende del hardware local.
- El coste de Groq es una estimación basada en los tokens utilizados.
- La evaluación de calidad es principalmente funcional.
- No se ha realizado una evaluación estadística sobre un conjunto amplio de incidencias etiquetadas manualmente.
- Las decisiones generadas por los modelos pueden diferir ante una misma incidencia.

Por este motivo, AnimalSOS mantiene una fase de revisión humana antes de considerar definitiva una decisión.

---

# 🔮 Posibles mejoras futuras

Entre las posibles líneas de evolución del proyecto:

- ampliar el conjunto de incidencias para evaluar los modelos;
- crear un dataset etiquetado manualmente;
- incorporar métricas de calidad más completas;
- incorporar autenticación de usuarios;
- desplegar la API y el dashboard;
- añadir más proveedores y modelos;
- mejorar el sistema de evaluación automática;
- incorporar monitorización de errores y rendimiento.

---

# 🛠️ Tecnologías utilizadas

- Python
- FastAPI
- Pydantic
- Ollama
- llama3.2
- Groq
- openai/gpt-oss-20b
- Streamlit
- Pytest
- Requests
- python-dotenv

---

# 📁 Estructura resumida

```text
AnimalSOS/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── filter.py
│   ├── llm_service.py
│   ├── groq_service.py
│   ├── mock_llm_service.py
│   └── incident_log.py
│
├── data/
│   └── .gitkeep
│
├── frontend/
│   └── app.py
│
├── tests/
│   ├── test_api.py
│   ├── test_filter.py
│   └── test_llm_service.py
│
├── docs/
│   └── benchmark.md
│
├── benchmark.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 👩‍💻 Proyecto

**AnimalSOS**

Proyecto desarrollado como parte de un proyecto formativo de AI Engineering.