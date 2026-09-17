import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/incidencias"


st.set_page_config(
    page_title="AnimalSOS",
    page_icon="🐾",
    layout="wide",
)


# ==================================================
# CONFIGURACIÓN
# ==================================================

st.title("🐾 AnimalSOS")
st.subheader(
    "Sistema inteligente de triaje para protectoras y rescate animal"
)

st.write(
    "AnimalSOS analiza incidencias mediante reglas y modelos de lenguaje. "
    "La decisión generada por IA debe ser revisada y validada por una "
    "persona antes de considerarse definitiva."
)


# ==================================================
# ENTRADA DE LA INCIDENCIA
# ==================================================

st.markdown("### 📝 Nueva incidencia")

mensaje = st.text_area(
    "Describe la incidencia",
    placeholder=(
        "Ejemplo: He encontrado un perro herido junto a una carretera."
    ),
    height=120,
)


proveedor = st.selectbox(
    "Proveedor de IA",
    options=[
        "ollama",
        "groq",
        "comparar",
    ],
    format_func=lambda x: {
        "ollama": "🖥️ Ollama (local)",
        "groq": "☁️ Groq (externo)",
        "comparar": "⚖️ Comparar ambos",
    }[x],
)


analizar = st.button(
    "🔍 Analizar incidencia",
    type="primary",
)


# ==================================================
# FUNCIÓN PARA LLAMAR A LA API
# ==================================================

def analizar_incidencia(mensaje, proveedor):

    respuesta = requests.post(
        API_URL,
        json={
            "mensaje": mensaje,
            "proveedor": proveedor,
        },
        timeout=120,
    )

    respuesta.raise_for_status()

    return respuesta.json()


# ==================================================
# ANÁLISIS
# ==================================================

if analizar:

    if not mensaje.strip():

        st.warning(
            "Escribe una incidencia antes de analizarla."
        )

    else:

        with st.spinner("Analizando incidencia..."):

            try:

                resultado = analizar_incidencia(
                    mensaje,
                    proveedor,
                )

                st.session_state["resultado"] = resultado

            except requests.exceptions.ConnectionError:

                st.error(
                    "No se ha podido conectar con la API. "
                    "Comprueba que FastAPI está ejecutándose."
                )

            except requests.exceptions.HTTPError as error:

                st.error(
                    f"La API ha devuelto un error: {error}"
                )

            except Exception as error:

                st.error(
                    f"Se ha producido un error: {error}"
                )


# ==================================================
# MOSTRAR RESULTADO
# ==================================================

if "resultado" in st.session_state:

    resultado = st.session_state["resultado"]

    st.divider()

    st.markdown("## 📊 Resultado del análisis")

    st.markdown(
        f"**Incidencia:** {resultado['mensaje_recibido']}"
    )

    st.markdown(
        f"**Filtro:** `{resultado['decision_filtro']}`"
    )


    # ==================================================
    # CASO SIN LLM
    # ==================================================

    if resultado["proveedor"] == "ninguno":

        st.success(
            "Esta incidencia ha sido resuelta mediante reglas "
            "sin necesidad de utilizar un modelo de lenguaje."
        )

        st.info(
            f"Categoría detectada: **{resultado['categoria']}**"
        )


    # ==================================================
    # UN SOLO PROVEEDOR
    # ==================================================

    elif resultado["proveedor"] in ["ollama", "groq"]:

        datos = resultado["resultado"]
        metricas = resultado["metricas"]


        col1, col2 = st.columns(2)


        # ----------------------------------------------
        # CLASIFICACIÓN
        # ----------------------------------------------

        with col1:

            st.markdown("### 🏷️ Clasificación")

            st.write(
                f"**Categoría:** {datos['categoria']}"
            )

            st.write(
                f"**Urgencia:** {datos['urgencia']}"
            )

            st.write(
                f"**Departamento:** {datos['departamento']}"
            )


        # ----------------------------------------------
        # MÉTRICAS
        # ----------------------------------------------

        with col2:

            st.markdown("### 📈 Métricas")

            st.write(
                f"**Modelo:** {metricas['modelo']}"
            )

            st.write(
                f"**Tokens totales:** "
                f"{metricas['tokens_totales']}"
            )

            st.write(
                f"**Latencia:** "
                f"{metricas['latencia_segundos']} s"
            )

            st.write(
                f"**Coste estimado:** "
                f"${metricas['coste_estimado']:.8f}"
            )


        # ----------------------------------------------
        # INFORMACIÓN DEL RESULTADO
        # ----------------------------------------------

        st.markdown("### 📝 Resumen")

        st.info(datos["resumen"])


        st.markdown("### 💡 Acción recomendada")

        st.write(datos["accion_recomendada"])


        st.markdown("### 🔎 Justificación")

        st.write(datos["justificacion"])


        # ----------------------------------------------
        # VALIDACIÓN HUMANA
        # ----------------------------------------------

        st.divider()

        st.markdown("## 👩‍💼 Validación humana")

        st.write(
            "La IA propone una clasificación, pero el operador "
            "puede revisarla y modificarla antes de validarla."
        )


        categoria_editada = st.selectbox(
            "Categoría",
            [
                "animal_herido",
                "animal_perdido",
                "animal_abandonado",
                "posible_maltrato",
                "rescate",
                "adopcion",
                "acogida",
                "otro",
            ],
            index=[
                "animal_herido",
                "animal_perdido",
                "animal_abandonado",
                "posible_maltrato",
                "rescate",
                "adopcion",
                "acogida",
                "otro",
            ].index(datos["categoria"]),
        )


        urgencia_editada = st.selectbox(
            "Urgencia",
            [
                "baja",
                "media",
                "alta",
                "critica",
            ],
            index=[
                "baja",
                "media",
                "alta",
                "critica",
            ].index(datos["urgencia"]),
        )


        departamento_editado = st.selectbox(
            "Departamento",
            [
                "rescate",
                "acogida",
                "adopciones",
                "voluntariado",
                "administracion",
            ],
            index=[
                "rescate",
                "acogida",
                "adopciones",
                "voluntariado",
                "administracion",
            ].index(datos["departamento"]),
        )


        if st.button(
            "✅ Validar resultado",
            key="validar_resultado",
        ):

            st.success(
                "Resultado revisado y validado por una persona."
            )

            st.markdown("### 📋 Decisión final")

            st.write(
                f"**Categoría:** {categoria_editada}"
            )

            st.write(
                f"**Urgencia:** {urgencia_editada}"
            )

            st.write(
                f"**Departamento:** {departamento_editado}"
            )


    # ==================================================
    # COMPARACIÓN
    # ==================================================

    elif resultado["proveedor"] == "comparar":

        resultados = resultado["resultados"]
        metricas = resultado["metricas"]


        st.markdown("## ⚖️ Comparación de modelos")


        col_ollama, col_groq = st.columns(2)


        # ==================================================
        # OLLAMA
        # ==================================================

        with col_ollama:

            st.markdown("### 🖥️ Ollama")

            datos_ollama = resultados["ollama"]
            metricas_ollama = metricas["ollama"]


            st.write(
                f"**Categoría:** "
                f"{datos_ollama['categoria']}"
            )

            st.write(
                f"**Urgencia:** "
                f"{datos_ollama['urgencia']}"
            )

            st.write(
                f"**Departamento:** "
                f"{datos_ollama['departamento']}"
            )


            st.markdown("**Resumen**")

            st.info(
                datos_ollama["resumen"]
            )


            st.markdown("**Acción recomendada**")

            st.write(
                datos_ollama["accion_recomendada"]
            )


            st.markdown("**Justificación**")

            st.write(
                datos_ollama["justificacion"]
            )


            st.markdown("#### 📈 Métricas")

            st.write(
                f"Tokens: "
                f"{metricas_ollama['tokens_totales']}"
            )

            st.write(
                f"Latencia: "
                f"{metricas_ollama['latencia_segundos']} s"
            )

            st.write(
                f"Coste: "
                f"${metricas_ollama['coste_estimado']:.8f}"
            )


        # ==================================================
        # GROQ
        # ==================================================

        with col_groq:

            st.markdown("### ☁️ Groq")

            datos_groq = resultados["groq"]
            metricas_groq = metricas["groq"]


            st.write(
                f"**Categoría:** "
                f"{datos_groq['categoria']}"
            )

            st.write(
                f"**Urgencia:** "
                f"{datos_groq['urgencia']}"
            )

            st.write(
                f"**Departamento:** "
                f"{datos_groq['departamento']}"
            )


            st.markdown("**Resumen**")

            st.info(
                datos_groq["resumen"]
            )


            st.markdown("**Acción recomendada**")

            st.write(
                datos_groq["accion_recomendada"]
            )


            st.markdown("**Justificación**")

            st.write(
                datos_groq["justificacion"]
            )


            st.markdown("#### 📈 Métricas")

            st.write(
                f"Tokens: "
                f"{metricas_groq['tokens_totales']}"
            )

            st.write(
                f"Latencia: "
                f"{metricas_groq['latencia_segundos']} s"
            )

            st.write(
                f"Coste: "
                f"${metricas_groq['coste_estimado']:.8f}"
            )


        # ==================================================
        # TABLA COMPARATIVA
        # ==================================================

        st.divider()

        st.markdown("### 📊 Comparativa de rendimiento")


        st.dataframe(
            {
                "Proveedor": [
                    "Ollama",
                    "Groq",
                ],
                "Modelo": [
                    metricas_ollama["modelo"],
                    metricas_groq["modelo"],
                ],
                "Tokens": [
                    metricas_ollama["tokens_totales"],
                    metricas_groq["tokens_totales"],
                ],
                "Latencia (s)": [
                    metricas_ollama["latencia_segundos"],
                    metricas_groq["latencia_segundos"],
                ],
                "Coste ($)": [
                    f"{metricas_ollama['coste_estimado']:.8f}",
                    f"{metricas_groq['coste_estimado']:.8f}",
                ],
            },
            use_container_width=True,
            hide_index=True,
        )


        # ==================================================
        # GRÁFICOS
        # ==================================================

        st.markdown("### ⚡ Comparación de latencia")

        st.bar_chart(
            {
                "Ollama": metricas_ollama["latencia_segundos"],
                "Groq": metricas_groq["latencia_segundos"],
            }
        )


        st.markdown("### 🔢 Comparación de tokens")

        st.bar_chart(
            {
                "Ollama": metricas_ollama["tokens_totales"],
                "Groq": metricas_groq["tokens_totales"],
            }
        )


        # ==================================================
        # VALIDACIÓN HUMANA EN COMPARACIÓN
        # ==================================================

        st.divider()

        st.markdown("## 👩‍💼 Validación humana")

        st.write(
            "La comparación permite al operador revisar las propuestas "
            "de ambos modelos y seleccionar una como punto de partida "
            "para la decisión final."
        )


        modelo_a_validar = st.radio(
            "Resultado que quieres revisar",
            [
                "ollama",
                "groq",
            ],
            format_func=lambda x: {
                "ollama": "🖥️ Propuesta de Ollama",
                "groq": "☁️ Propuesta de Groq",
            }[x],
        )


        if modelo_a_validar == "ollama":
            datos_validacion = datos_ollama
        else:
            datos_validacion = datos_groq


        categorias = [
            "animal_herido",
            "animal_perdido",
            "animal_abandonado",
            "posible_maltrato",
            "rescate",
            "adopcion",
            "acogida",
            "otro",
        ]


        urgencias = [
            "baja",
            "media",
            "alta",
            "critica",
        ]


        departamentos = [
            "rescate",
            "acogida",
            "adopciones",
            "voluntariado",
            "administracion",
        ]


        categoria_final = st.selectbox(
            "Categoría final",
            categorias,
            index=categorias.index(
                datos_validacion["categoria"]
            ),
            key="categoria_final",
        )


        urgencia_final = st.selectbox(
            "Urgencia final",
            urgencias,
            index=urgencias.index(
                datos_validacion["urgencia"]
            ),
            key="urgencia_final",
        )


        departamento_final = st.selectbox(
            "Departamento final",
            departamentos,
            index=departamentos.index(
                datos_validacion["departamento"]
            ),
            key="departamento_final",
        )


        if st.button(
            "✅ Validar decisión final",
            key="validar_comparacion",
        ):

            st.success(
                "Decisión revisada y validada por una persona."
            )

            st.markdown("### 📋 Decisión final")

            st.write(
                f"**Categoría:** {categoria_final}"
            )

            st.write(
                f"**Urgencia:** {urgencia_final}"
            )

            st.write(
                f"**Departamento:** {departamento_final}"
            )