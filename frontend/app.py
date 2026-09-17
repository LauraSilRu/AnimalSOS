import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/incidencias"


st.set_page_config(
    page_title="AnimalSOS",
    page_icon="🐾",
    layout="wide",
)



# ==================================================
# COMPONENTES VISUALES
# ==================================================

def tarjeta_clasificacion(datos):
    colores_urgencia = {
        "baja": ("#5d8a68", "🟢"),
        "media": ("#a8844f", "🟡"),
        "alta": ("#b86f3f", "🟠"),
        "critica": ("#a94f45", "🔴"),
    }

    color, icono = colores_urgencia.get(
        datos["urgencia"],
        ("#527a5a", "⚪"),
    )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="section-label">Propuesta de la IA</div>
            <div class="result-main">
                <div>
                    <div class="result-caption">CATEGORÍA</div>
                    <div class="result-value">🐾 {datos["categoria"].replace("_", " ").title()}</div>
                </div>
                <div class="urgency-pill" style="background:{color};">
                    {icono} {datos["urgencia"].upper()}
                </div>
            </div>
            <div class="department-row">
                <span>👥 Departamento</span>
                <strong>{datos["departamento"].replace("_", " ").title()}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tarjeta_metricas(metricas):
    st.markdown(
        f"""
        <div class="result-card">
            <div class="section-label">Rendimiento del modelo</div>
            <div class="model-name">🤖 {metricas["modelo"]}</div>
            <div class="metric-grid">
                <div class="mini-metric">
                    <span>⚡ Latencia</span>
                    <strong>{metricas["latencia_segundos"]} s</strong>
                </div>
                <div class="mini-metric">
                    <span>🔢 Tokens</span>
                    <strong>{metricas["tokens_totales"]}</strong>
                </div>
                <div class="mini-metric">
                    <span>💰 Coste estimado</span>
                    <strong>${metricas["coste_estimado"]:.8f}</strong>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tarjeta_info(titulo, icono, contenido, clase=""):
    st.markdown(
        f"""
        <div class="info-card {clase}">
            <div class="info-title">{icono} {titulo}</div>
            <div class="info-content">{contenido}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tarjeta_modelo(nombre, icono, datos, metricas):
    colores_urgencia = {
        "baja": "🟢",
        "media": "🟡",
        "alta": "🟠",
        "critica": "🔴",
    }

    icono_urgencia = colores_urgencia.get(datos["urgencia"], "⚪")

    with st.container(border=True):
        st.markdown(f"### {icono} {nombre}")
        st.caption(metricas["modelo"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**CATEGORÍA**")
            st.write(f"🐾 {datos['categoria'].replace('_', ' ').title()}")

        with col2:
            st.markdown("**URGENCIA**")
            st.write(
                f"{icono_urgencia} {datos['urgencia'].upper()}"
            )

        with col3:
            st.markdown("**DEPARTAMENTO**")
            st.write(
                f"👥 {datos['departamento'].replace('_', ' ').title()}"
            )


def tarjeta_decision_final(categoria, urgencia, departamento):
    colores_urgencia = {
        "baja": "#5d8a68",
        "media": "#a8844f",
        "alta": "#b86f3f",
        "critica": "#a94f45",
    }

    color = colores_urgencia.get(urgencia, "#527a5a")

    st.markdown(
        f"""
        <div class="final-card">
            <div class="final-icon">✓</div>
            <div>
                <div class="final-title">Decisión final validada</div>
                <div class="final-values">
                    🐾 {categoria.replace("_", " ").title()}
                    &nbsp; · &nbsp;
                    <span style="color:{color};">{urgencia.upper()}</span>
                    &nbsp; · &nbsp;
                    👥 {departamento.replace("_", " ").title()}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# CONFIGURACIÓN Y ESTILO VISUAL
# ==================================================

st.markdown(
    """
    <style>
    /* ---------- PALETA NATURAL ---------- */
    :root {
        --verde-oscuro: #315943;
        --verde: #527a5a;
        --verde-claro: #dfeadf;
        --verde-muy-claro: #f1f6f0;
        --tierra: #8a6748;
        --tierra-claro: #eee5da;
        --crema: #f7f4ec;
        --blanco: #ffffff;
        --texto: #29352d;
        --texto-suave: #667269;
    }

    /* Fondo general */
    .stApp {
        background: linear-gradient(180deg, #f1f6f0 0%, #f7f4ec 48%, #f4efe7 100%);
        color: var(--texto);
    }

    /* Contenedor principal */
    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Cabeceras */
    h1, h2, h3 {
        color: var(--verde-oscuro) !important;
        font-weight: 700 !important;
    }

    h1 {
        letter-spacing: -0.5px;
    }

    /* Hero */
    .animal-hero {
        background: linear-gradient(135deg, #315943 0%, #527a5a 100%);
        border-radius: 24px;
        padding: 2rem 2.3rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 30px rgba(49, 89, 67, 0.16);
    }

    .animal-hero h1 {
        color: white !important;
        margin: 0 0 0.35rem 0;
        font-size: 2.5rem;
    }

    .animal-hero p {
        color: #eef5ed;
        margin: 0;
        font-size: 1.05rem;
    }

    .hero-badge {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.16);
        color: white;
        font-size: 0.82rem;
    }

    /* Tarjetas */
    .section-card {
        background: rgba(255,255,255,0.88);
        border: 1px solid #dce5dc;
        border-radius: 18px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 5px 18px rgba(49, 89, 67, 0.07);
        margin-bottom: 1rem;
    }

    .section-label {
        color: var(--tierra);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }

    /* Campos */
    .stTextArea textarea {
        background-color: #fffdf9 !important;
        border: 1px solid #cbd8cc !important;
        border-radius: 14px !important;
        color: var(--texto) !important;
    }

    .stTextArea textarea:focus {
        border-color: var(--verde) !important;
        box-shadow: 0 0 0 2px rgba(82, 122, 90, 0.15) !important;
    }

    /* Botones */
    .stButton > button {
        border-radius: 12px !important;
        border: 1px solid #b7cbb9 !important;
        font-weight: 600 !important;
        min-height: 2.7rem;
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"] {
        background: var(--verde-oscuro) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 5px 14px rgba(49, 89, 67, 0.20);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: var(--verde) !important;
    }

    /* Selectores */
    [data-baseweb="select"] > div {
        border-radius: 12px !important;
        border-color: #cbd8cc !important;
        background: #fffdf9 !important;
    }

    /* Métricas */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.9);
        border: 1px solid #dce5dc;
        border-radius: 14px;
        padding: 0.9rem;
    }

    /* Alertas */
    [data-testid="stAlert"] {
        border-radius: 14px !important;
    }

    /* Tabla */
    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    /* Separadores */
    hr {
        border-color: #d8e2d8 !important;
    }

    /* ---------- RESULTADOS ---------- */
    .result-card {
        background: rgba(255,255,255,0.94);
        border: 1px solid #d8e3d9;
        border-radius: 18px;
        padding: 1.25rem 1.35rem;
        margin-bottom: 1rem;
        box-shadow: 0 6px 20px rgba(49, 89, 67, 0.08);
    }

    .result-main {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin: 0.7rem 0 1rem;
    }

    .result-caption {
        color: #7a847d;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
    }

    .result-value {
        color: #315943;
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }

    .urgency-pill {
        color: white;
        padding: 0.55rem 0.8rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.04em;
    }

    .department-row {
        border-top: 1px solid #e4ebe4;
        padding-top: 0.8rem;
        display: flex;
        justify-content: space-between;
        color: #667269;
    }

    .department-row strong {
        color: #315943;
    }

    .model-name {
        color: #315943;
        font-size: 1rem;
        font-weight: 700;
        margin: 0.65rem 0 0.8rem;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.6rem;
    }

    .mini-metric {
        background: #f1f6f0;
        border-radius: 12px;
        padding: 0.7rem;
    }

    .mini-metric span {
        display: block;
        color: #718078;
        font-size: 0.75rem;
        margin-bottom: 0.25rem;
    }

    .mini-metric strong {
        color: #315943;
        font-size: 0.95rem;
    }

    .info-card {
        background: #fffdf9;
        border-left: 4px solid #527a5a;
        border-radius: 14px;
        padding: 1rem 1.15rem;
        margin: 0.75rem 0;
        box-shadow: 0 3px 12px rgba(49, 89, 67, 0.05);
    }

    .info-title {
        color: #315943;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .info-content {
        color: #4e5c53;
        line-height: 1.55;
    }

    .model-card {
        background: rgba(255,255,255,0.94);
        border: 1px solid #d8e3d9;
        border-radius: 18px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 6px 20px rgba(49, 89, 67, 0.08);
    }

    .model-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .model-title {
        color: #315943;
        font-size: 1.15rem;
        font-weight: 700;
    }

    .model-tag {
        background: #eee5da;
        color: #76583d;
        border-radius: 999px;
        padding: 0.3rem 0.6rem;
        font-size: 0.7rem;
        max-width: 55%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .model-classification {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.7rem;
    }

    .model-classification div {
        background: #f1f6f0;
        border-radius: 12px;
        padding: 0.7rem;
    }

    .model-classification span {
        display: block;
        color: #718078;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }

    .model-classification strong {
        color: #315943;
        font-size: 0.9rem;
    }

    .final-card {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: #e5efe4;
        border: 1px solid #bfd1bf;
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
    }

    .final-icon {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        background: #527a5a;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        font-weight: 700;
        flex-shrink: 0;
    }

    .final-title {
        color: #315943;
        font-weight: 800;
        font-size: 1rem;
    }

    .final-values {
        color: #4e5c53;
        margin-top: 0.25rem;
        font-size: 0.9rem;
    }

    @media (max-width: 700px) {
        .metric-grid,
        .model-classification {
            grid-template-columns: 1fr;
        }

        .result-main {
            align-items: flex-start;
            flex-direction: column;
        }
    }

    /* Texto secundario */
    .help-text {
        color: var(--texto-suave);
        font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="animal-hero">
        <h1>🐾 AnimalSOS</h1>
        <p>Triaje inteligente para protectoras y equipos de rescate animal</p>
        <span class="hero-badge">🌿 IA como apoyo · revisión humana siempre</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
        <div class="section-label">Cómo funciona</div>
        <div class="help-text">
            Describe una incidencia, deja que AnimalSOS proponga una clasificación
            y revisa la decisión antes de validarla. La IA es una herramienta de
            apoyo, no sustituye el criterio profesional.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# ENTRADA DE LA INCIDENCIA
# ==================================================

st.markdown("## 📝 Nueva incidencia")

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
        # CLASIFICACIÓN Y MÉTRICAS
        # ----------------------------------------------

        col1, col2 = st.columns(2)

        with col1:
            tarjeta_clasificacion(datos)

        with col2:
            tarjeta_metricas(metricas)

        # ----------------------------------------------
        # INFORMACIÓN DEL RESULTADO
        # ----------------------------------------------

        st.markdown("### 📝 Resumen")
        tarjeta_info("Resumen de la incidencia", "📌", datos["resumen"])

        st.markdown("### 💡 Acción recomendada")
        tarjeta_info(
            "Siguiente paso sugerido",
            "🌱",
            datos["accion_recomendada"],
        )

        st.markdown("### 🔎 Justificación")
        tarjeta_info(
            "Por qué la IA propone esta clasificación",
            "🧭",
            datos["justificacion"],
        )

        # ----------------------------------------------
        # VALIDACIÓN HUMANA
        # ----------------------------------------------

        st.divider()

        st.markdown("## 👩‍💼 Revisión humana")

        st.markdown(
            """
            <div class="section-card">
                <div class="section-label">Human-in-the-Loop</div>
                <div class="help-text">
                    Revisa la propuesta de la IA y modifica cualquier campo
                    antes de convertirla en una decisión definitiva.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
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

            tarjeta_decision_final(
                categoria_editada,
                urgencia_editada,
                departamento_editado,
            )


    # ==================================================
    # COMPARACIÓN
    # ==================================================

    elif resultado["proveedor"] == "comparar":

        resultados = resultado["resultados"]
        metricas = resultado["metricas"]


        st.markdown("## ⚖️ Comparación de modelos")


        # ==================================================
        # PROPUESTAS DE LOS MODELOS
        # ==================================================

        col_ollama, col_groq = st.columns(2)

        datos_ollama = resultados["ollama"]
        metricas_ollama = metricas["ollama"]

        datos_groq = resultados["groq"]
        metricas_groq = metricas["groq"]

        with col_ollama:
            tarjeta_modelo(
                "Ollama",
                "🖥️",
                datos_ollama,
                metricas_ollama,
            )

            tarjeta_info("Resumen", "📌", datos_ollama["resumen"])
            tarjeta_info("Acción recomendada", "🌱", datos_ollama["accion_recomendada"])
            tarjeta_info("Justificación", "🧭", datos_ollama["justificacion"])

        with col_groq:
            tarjeta_modelo(
                "Groq",
                "☁️",
                datos_groq,
                metricas_groq,
            )

            tarjeta_info("Resumen", "📌", datos_groq["resumen"])
            tarjeta_info("Acción recomendada", "🌱", datos_groq["accion_recomendada"])
            tarjeta_info("Justificación", "🧭", datos_groq["justificacion"])

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

        st.markdown("## 👩‍💼 Revisión humana")

        st.markdown(
            """
            <div class="section-card">
                <div class="section-label">Human-in-the-Loop</div>
                <div class="help-text">
                    Compara las propuestas y selecciona un resultado como
                    punto de partida para la decisión final.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
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