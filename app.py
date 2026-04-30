import streamlit as st
import google.generativeai as genai
import random
import os
import time
import json
import gspread
import re
from pathlib import Path
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

from config import (
    APP_TITLE,
    APP_LAYOUT,
    MAX_INTENTOS,
    TIMEOUT_NORMAL,
    TIMEOUT_SATURACION,
    AVISO_TIEMPO,
    MODEL_MAIN,
    MODEL_EVAL,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
    DOMINIO_PERMITIDO,
)

from catalogo import CONFIG

from prompts import (
    construir_prompt_sistema_dinamico,
    construir_prompt_evaluacion,
)

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title=APP_TITLE, layout=APP_LAYOUT)

# 2. CONEXIÓN API GEMINI
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

# 3. GESTIÓN DE ESTADO
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "actividad_actual" not in st.session_state:
    st.session_state.actividad_actual = None
if "intentos" not in st.session_state:
    st.session_state.intentos = 1
if "fila_bd" not in st.session_state:
    st.session_state.fila_bd = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "codigo" not in st.session_state:
    st.session_state.codigo = None
if "ultima_interaccion" not in st.session_state:
    st.session_state.ultima_interaccion = time.time()
if "saturacion_activa" not in st.session_state:
    st.session_state.saturacion_activa = False
if "advertencias_ia" not in st.session_state:
    st.session_state.advertencias_ia = 0

# 4. CONEXIÓN A GOOGLE SHEETS
@st.cache_resource
def init_db():
    try:
        cred_dict = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            cred_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        client = gspread.authorize(creds)
        return client.open_by_url(st.secrets["sheet_url"]).sheet1
    except Exception:
        st.error("Error conectando a la base de datos. Revisa los Secrets.")
        return None

hoja_bd = init_db()

def get_hora_colombia():
    return datetime.utcnow() - timedelta(hours=5)

def obtener_o_crear_registro(correo, asignatura, actividad):
    if not hoja_bd:
        return 1, None
    try:
        registros = hoja_bd.get_all_records()
        for idx, row in enumerate(registros):
            if (
                str(row.get("Correo", "")).strip().lower() == correo
                and str(row.get("Asignatura", "")).strip() == asignatura
                and str(row.get("Actividad", "")).strip() == actividad
            ):
                return int(row.get("Intentos", 1)), idx + 2

        now = get_hora_colombia()
        fecha_str = now.strftime("%Y-%m-%d")
        hora_str = now.strftime("%H:%M:%S")
        hoja_bd.append_row([
            correo, 1, fecha_str, hora_str, fecha_str, hora_str, "",
            asignatura, actividad, "", "En curso", "", ""
        ])
        return 1, len(hoja_bd.get_all_values())
    except Exception:
        return 1, None

def actualizar_bd(fila, intentos=None, actualizar_hora=False, codigo=None, estado=None, nota=None, feedback=None):
    if not hoja_bd or not fila:
        return
    try:
        if intentos is not None:
            hoja_bd.update_cell(fila, 2, intentos)
        if actualizar_hora:
            now = get_hora_colombia()
            hoja_bd.update_cell(fila, 5, now.strftime("%Y-%m-%d"))
            hoja_bd.update_cell(fila, 6, now.strftime("%H:%M:%S"))
        if codigo is not None:
            hoja_bd.update_cell(fila, 10, codigo)
        if estado is not None:
            hoja_bd.update_cell(fila, 11, estado)
        if nota is not None:
            hoja_bd.update_cell(fila, 12, nota)
        if feedback is not None:
            hoja_bd.update_cell(fila, 13, feedback)
    except Exception:
        pass

def es_error_saturacion(error):
    error_msg = str(error).lower()
    patrones = [
        "429",
        "quota",
        "exhausted",
        "resource has been exhausted",
        "rate limit",
    ]
    return any(p in error_msg for p in patrones)

def generar_con_reintentos(model, historial_envio, max_reintentos=3, esperas=(4, 8, 15)):
    ultimo_error = None
    for intento in range(max_reintentos):
        try:
            return model.generate_content(historial_envio)
        except Exception as e:
            ultimo_error = e
            if not es_error_saturacion(e):
                raise
            if intento < max_reintentos - 1:
                espera = esperas[intento] if intento < len(esperas) else esperas[-1]
                st.warning(
                    f"⚠️ Servidor temporalmente ocupado. Reintentando en {espera} segundos... "
                    f"(intento {intento + 1} de {max_reintentos})"
                )
                time.sleep(espera)
            else:
                raise ultimo_error

def normalizar_nombre_indice(texto):
    texto = texto.strip().replace(" ", "_")
    texto = re.sub(r"[^A-Za-z0-9_\-]", "", texto)
    return texto

def obtener_ruta_indice(actividad_id):
    nombre_indice = normalizar_nombre_indice(actividad_id)
    ruta_base = Path(__file__).resolve().parent / "rag_store"
    return ruta_base / nombre_indice

def existe_indice_rag(actividad_id):
    ruta_indice = obtener_ruta_indice(actividad_id)
    return ruta_indice.exists() and any(ruta_indice.iterdir())

# 5. LOGIN INSTITUCIONAL
if not st.session_state.user_id:
    st.markdown(
        "<h1 style='text-align: center;'>💬 Tutor de Análisis Crítico en Temas Urbanos<br>🏛️ FADU - Unisalle</h1>",
        unsafe_allow_html=True,
    )
    now_bogota = get_hora_colombia().strftime("%d/%m/%Y, %H:%M")
    st.markdown(
        f"<p style='text-align: center; color: gray;'><small><b>Versión 5.0 RAG ({now_bogota})</b></small></p>",
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown(f"""
    **Bienvenido al entorno de evaluación.**
    Para ingresar, utiliza tu **Correo Institucional**.
    - El sistema validará automáticamente el dominio `{DOMINIO_PERMITIDO}`.
    - Tienes **{MAX_INTENTOS} intentos por cada actividad o lectura**.
    - **IMPORTANTE:** No recargues la página (F5) o perderás tu progreso.
    """)

    col1, col2 = st.columns([1, 2])
    with col1:
        email_input = st.text_input("Correo Electrónico:", placeholder=f"usuario{DOMINIO_PERMITIDO}")
        if st.button("Iniciar Sesión"):
            if email_input.strip().lower().endswith(DOMINIO_PERMITIDO):
                st.session_state.user_id = email_input.strip().lower()
                st.rerun()
            else:
                st.error(f"⛔ Acceso denegado. Debes usar un correo institucional ({DOMINIO_PERMITIDO}).")
    st.stop()

# 6. MENÚ LATERAL DINÁMICO
with st.sidebar:
    usuario_corto = st.session_state.user_id.split("@")[0]
    st.title(f"👤 {usuario_corto}")

    st.divider()
    c_sel = st.selectbox("Asignatura", list(CONFIG.keys()))
    a_sel = st.selectbox("Actividad", list(CONFIG[c_sel].keys()))
    nivel_3 = CONFIG[c_sel][a_sel]
    primer_key = list(nivel_3.keys())[0]

    if isinstance(nivel_3[primer_key], dict):
        s_sel = st.selectbox("Sesión", list(nivel_3.keys()))
        opciones = nivel_3[s_sel]
        o_sel = st.selectbox("Opción de Lectura", list(opciones.keys()))
        rutas_archivos = opciones[o_sel]
        titulo_interfaz = f"💬 {c_sel} | {a_sel} | {s_sel} | {o_sel}"
        actividad_registro = f"{a_sel} | {s_sel} | {o_sel}"
    else:
        s_sel = None
        o_sel = st.selectbox("Opción de Lectura", list(nivel_3.keys()))
        rutas_archivos = nivel_3[o_sel]
        titulo_interfaz = f"💬 {c_sel} | {a_sel} | {o_sel}"
        actividad_registro = f"{a_sel} | {o_sel}"

# 7. CAMBIO DE ACTIVIDAD
identificador_actual = f"{c_sel}_{actividad_registro}"

if st.session_state.actividad_actual != identificador_actual:
    st.session_state.actividad_actual = identificador_actual
    st.session_state.messages = []
    st.session_state.codigo = None
    st.session_state.advertencias_ia = 0
    st.session_state.saturacion_activa = False

    with st.spinner("Cargando perfil y asignando intentos para esta actividad..."):
        intentos_bd, fila_bd = obtener_o_crear_registro(
            st.session_state.user_id, c_sel, actividad_registro
        )
        st.session_state.intentos = intentos_bd
        st.session_state.fila_bd = fila_bd
        st.session_state.ultima_interaccion = time.time()

# 8. BARRA DE PROGRESO
with st.sidebar:
    progreso = min(st.session_state.intentos / MAX_INTENTOS, 1.0)
    st.progress(progreso, text=f"Intento {st.session_state.intentos} de {MAX_INTENTOS} (Esta actividad)")

    st.divider()
    if st.button("🗑️ Reiniciar (Gasta 1 Intento)"):
        st.session_state.intentos += 1
        st.session_state.messages = []
        st.session_state.codigo = None
        st.session_state.advertencias_ia = 0
        st.session_state.saturacion_activa = False
        st.session_state.ultima_interaccion = time.time()
        actualizar_bd(
            st.session_state.fila_bd,
            intentos=st.session_state.intentos,
            actualizar_hora=True,
            estado="Reinicio manual",
        )
        st.rerun()

# 9. CONTROL DE INTENTOS
if st.session_state.intentos > MAX_INTENTOS:
    st.title(titulo_interfaz)
    st.error("⛔ **ACCESO BLOQUEADO PARA ESTA ACTIVIDAD**")
    st.warning(
        f"Has superado el límite de {MAX_INTENTOS} intentos permitidos para esta lectura específica. "
        "Puedes seleccionar otra actividad en el menú izquierdo para continuar trabajando."
    )
    st.stop()

# 10. MOTOR RAG
@st.cache_resource(show_spinner=False)
def configurar_motor_rag(rutas, actividad_id):
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=st.secrets["GOOGLE_API_KEY"],
    )

    ruta_indice = obtener_ruta_indice(actividad_id)
    ruta_indice.parent.mkdir(parents=True, exist_ok=True)

    # 1. Intentar cargar un índice ya existente
    if ruta_indice.exists() and any(ruta_indice.iterdir()):
        try:
            vectorstore = Chroma(
                persist_directory=str(ruta_indice),
                embedding_function=embeddings,
            )
            return vectorstore.as_retriever(search_kwargs={"k": TOP_K})
        except Exception as e:
            st.warning(
                f"⚠️ El índice RAG existente no pudo cargarse. "
                f"Se intentará reconstruirlo. Detalle: {e}"
            )

    # 2. Si no existe o falló, reconstruir desde los PDFs
    documentos = []
    ruta_proyecto = Path(__file__).resolve().parent

    rutas_no_encontradas = []
    errores_carga = []

    for r in rutas:
        ruta_pdf = (ruta_proyecto / r).resolve()

        if ruta_pdf.exists():
            try:
                loader = PyPDFLoader(str(ruta_pdf))
                documentos.extend(loader.load())
            except Exception as e:
                errores_carga.append(f"{ruta_pdf.name}: {e}")
        else:
            rutas_no_encontradas.append(str(ruta_pdf))

    if rutas_no_encontradas:
        st.warning("⚠️ No se encontraron algunos archivos PDF requeridos para esta lectura.")
        for ruta in rutas_no_encontradas:
            st.caption(f"Ruta no encontrada: {ruta}")

    if errores_carga:
        st.warning("⚠️ Algunos PDF existen, pero no pudieron leerse correctamente.")
        for err in errores_carga[:5]:
            st.caption(err)

    if not documentos:
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    fragmentos = text_splitter.split_documents(documentos)

    vectorstore = Chroma.from_documents(
        fragmentos,
        embeddings,
        persist_directory=str(ruta_indice),
    )

    try:
        if hasattr(vectorstore, "persist"):
            vectorstore.persist()
    except Exception:
        pass

    return vectorstore.as_retriever(search_kwargs={"k": TOP_K})


indice_existia_antes = existe_indice_rag(identificador_actual)

with st.spinner("Preparando índice RAG de la lectura..."):
    recuperador_rag = configurar_motor_rag(rutas_archivos, identificador_actual)

if recuperador_rag:
    if indice_existia_antes:
        st.caption("📚 Índice RAG cargado desde almacenamiento local de la app.")
    else:
        st.caption("🛠️ Índice RAG construido por primera vez y almacenado localmente en la app.")
else:
    st.caption("⚠️ No fue posible construir o cargar el índice RAG para esta lectura.")

# 11. INTERFAZ DE CHAT
st.title(titulo_interfaz)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "timestamp" in m:
            st.caption(f"🕒 {m['timestamp']}")
        st.markdown(m["content"])

# 12. CHAT Y EVALUACIÓN
if prompt := st.chat_input("Escribe tu análisis aquí..."):
    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - st.session_state.ultima_interaccion
    minutos = int(tiempo_transcurrido / 60)
    limite_expulsion = TIMEOUT_SATURACION if st.session_state.saturacion_activa else TIMEOUT_NORMAL

    if tiempo_transcurrido > limite_expulsion:
        st.error("⏱️ **TIEMPO AGOTADO POR INACTIVIDAD**")
        st.warning(f"Pasaron {minutos} minutos sin actividad en el chat. Se ha descontado 1 intento.")
        razon_cierre = "Tiempo agotado (> 20 min)" if st.session_state.saturacion_activa else "Tiempo agotado (> 10 min)"
        actualizar_bd(
            st.session_state.fila_bd,
            intentos=st.session_state.intentos + 1,
            actualizar_hora=True,
            estado=razon_cierre,
        )

        st.session_state.intentos += 1
        st.session_state.messages = []
        st.session_state.codigo = None
        st.session_state.advertencias_ia = 0
        st.session_state.saturacion_activa = False
        st.session_state.ultima_interaccion = time.time()
        time.sleep(3)
        st.rerun()

    else:
        st.session_state.ultima_interaccion = time.time()
        actualizar_bd(st.session_state.fila_bd, actualizar_hora=True, estado="En curso")

        if len(prompt) > 800:
            st.toast("⚠️ Respuesta muy larga. Resume con tus palabras.", icon="🚫")

        timestamp_usuario = get_hora_colombia().strftime("%d/%m/%Y %H:%M:%S")
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "timestamp": timestamp_usuario}
        )

        with st.chat_message("user"):
            st.caption(f"🕒 {timestamp_usuario}")
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                historial_envio = []
                for m in st.session_state.messages:
                    r = "model" if m["role"] == "assistant" else "user"
                    historial_envio.append({"role": r, "parts": [m["content"]]})

                if tiempo_transcurrido > AVISO_TIEMPO and not st.session_state.saturacion_activa:
                    aviso = (
                        f"[SISTEMA: El alumno tardó {minutos} min en responder. "
                        "Adviértele sobre el uso del tiempo y recuérdale que el límite estricto es de 10 minutos máximos por intervención.]"
                    )
                    historial_envio.append({"role": "user", "parts": [aviso]})

                contexto_recuperado = ""
                if recuperador_rag:
                    docs_relevantes = recuperador_rag.invoke(prompt)
                    contexto_recuperado = "\n\n".join([doc.page_content for doc in docs_relevantes])

                prompt_sistema_dinamico = construir_prompt_sistema_dinamico(contexto_recuperado)

                model = genai.GenerativeModel(
                    MODEL_MAIN,
                    system_instruction=prompt_sistema_dinamico,
                )
                response = generar_con_reintentos(model, historial_envio)
                res = response.text
                timestamp_tutor = get_hora_colombia().strftime("%d/%m/%Y %H:%M:%S")

                if "[ALERTA_IA]" in res:
                    st.session_state.advertencias_ia += 1
                    if st.session_state.advertencias_ia == 1:
                        res_limpia = res.replace("[ALERTA_IA]", "").strip()
                        alerta_visual = (
                            "⚠️ **ADVERTENCIA DEL SISTEMA (1/2)**\n\n"
                            "Se ha detectado el posible uso de herramientas automatizadas. "
                            "Recuerda usar tu propio análisis.\n\n---\n\n"
                            f"{res_limpia}"
                        )
                        st.caption(f"🕒 {timestamp_tutor}")
                        st.markdown(alerta_visual)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": alerta_visual, "timestamp": timestamp_tutor}
                        )
                    else:
                        st.error("⛔ **INTENTO ANULADO POR USO DE IA**")
                        actualizar_bd(
                            st.session_state.fila_bd,
                            intentos=st.session_state.intentos + 1,
                            actualizar_hora=True,
                            estado="Cierre por uso de IA",
                        )
                        st.session_state.intentos += 1
                        st.session_state.messages = []
                        st.session_state.codigo = None
                        st.session_state.advertencias_ia = 0
                        st.session_state.saturacion_activa = False
                        st.session_state.ultima_interaccion = time.time()
                        time.sleep(5)
                        st.rerun()
                else:
                    st.session_state.saturacion_activa = False

                    if "[dictamen_aprobado]" in res.lower() and not st.session_state.codigo:
                        rand_code = random.randint(1000, 9999)
                        usuario_clean = st.session_state.user_id.split("@")[0].upper()
                        codigo_final = f"[{usuario_clean}-INT{st.session_state.intentos}-{rand_code}]"
                        st.session_state.codigo = codigo_final

                        with st.spinner("Generando reporte de validación y cerrando sesión académica..."):
                            transcripcion_completa = ""
                            for msj in st.session_state.messages:
                                transcripcion_completa += f"{msj['role'].upper()}: {msj['content']}\n\n"
                            transcripcion_completa += f"TUTOR: {res}"

                            prompt_evaluacion = construir_prompt_evaluacion(transcripcion_completa)

                            try:
                                eval_model = genai.GenerativeModel(
                                    MODEL_EVAL,
                                    generation_config={"response_mime_type": "application/json"},
                                )
                                eval_response = eval_model.generate_content(prompt_evaluacion)
                                data_eval = json.loads(eval_response.text)
                                nota_db = data_eval.get("nota_final", 0)
                                feedback_db = data_eval.get("retroalimentacion", "Evaluación completada.")
                            except Exception:
                                nota_db = "Pendiente"
                                feedback_db = "Error al procesar evaluación cualitativa."

                        res += f"\n\n ✅ **EJERCICIO APROBADO.**\n\nCódigo de Validación: `{st.session_state.codigo}`"
                        actualizar_bd(
                            st.session_state.fila_bd,
                            actualizar_hora=True,
                            codigo=codigo_final,
                            estado="Completado exitosamente",
                            nota=nota_db,
                            feedback=feedback_db,
                        )

                    st.caption(f"🕒 {timestamp_tutor}")
                    st.markdown(res)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": res, "timestamp": timestamp_tutor}
                    )

            except Exception as e:
                if es_error_saturacion(e):
                    texto_rescatado = ""

                    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                        texto_rescatado = st.session_state.messages[-1]["content"]
                        st.session_state.messages.pop()

                    st.session_state.saturacion_activa = False
                    st.session_state.ultima_interaccion = time.time()

                    st.warning(
                        "⚠️ El servidor sigue ocupado en este momento. "
                        "Por favor intenta nuevamente en 30 a 60 segundos."
                    )

                    if texto_rescatado:
                        st.info(f"💡 Tu texto quedó preservado. Cópialo y vuelve a enviarlo:\n\n{texto_rescatado}")
                else:
                    st.error(f"Error técnico: {e}")

# 13. DESCARGA OFICIAL
if st.session_state.codigo:
    nombre_archivo = st.session_state.codigo.replace("[", "").replace("]", "") + ".txt"
    reporte = (
        f"REPORTE DE ANÁLISIS CRÍTICO - UNISALLE\n"
        f"Estudiante: {st.session_state.user_id}\n"
        f"Código: {st.session_state.codigo}\n"
        + "-" * 50 + "\n\n"
    )
    for m in st.session_state.messages:
        sello_tiempo = f" [{m['timestamp']}] " if "timestamp" in m else " "
        reporte += f"{m['role'].upper()}{sello_tiempo}: {m['content']}\n\n"

    st.success("🎉 Actividad completada correctamente.")
    st.download_button(
        label=f"📥 Descargar Evidencia ({nombre_archivo})",
        data=reporte,
        file_name=nombre_archivo,
        mime="text/plain",
    )
