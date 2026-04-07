import streamlit as st
import google.generativeai as genai
import random
import os
import time
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from PyPDF2 import PdfReader

# Nuevas librerías para RAG
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tutor de Análisis Crítico", layout="wide")

# 2. CONEXIÓN API GEMINI
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # LangChain requiere que la llave esté en las variables de entorno del sistema operativo
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

# 3. RUTAS DE DOCUMENTOS 
CONFIG = {
    "Urb-Historia 1": {
        "Actividad_1": {
            "Opción 1": ["documentos/Urb-Historia 1/Actividad_1/Archivo_1.pdf"],
            "Opción 2": ["documentos/Urb-Historia 1/Actividad_1/Archivo_2.pdf"],
            "Opción 3": ["documentos/Urb-Historia 1/Actividad_1/Archivo_3.pdf"]
        },
        "Actividad_2": {
            "Opción 1": ["documentos/Urb-Historia 1/Actividad_2/Archivo_4.pdf"],
            "Opción 2": ["documentos/Urb-Historia 1/Actividad_2/Archivo_5.pdf"]
        },
        "Actividad_3": {
            "Opción Única": ["documentos/Urb-Historia 1/Actividad_3/Archivo_6.pdf"]
        }
    },
    "Urb-Historia 2": {
        "Actividad_1": {
            "Sesion_1": {
                "Opción 1": ["documentos/Urb-Historia 2/Actividad_1/Sesion_1/Archivo_1.pdf"],
                "Opción 2": ["documentos/Urb-Historia 2/Actividad_1/Sesion_1/Archivo_2.pdf"]
            },
            "Sesion_2": {
                "Opción 1": ["documentos/Urb-Historia 2/Actividad_1/Sesion_2/Archivo_3.pdf"],
                "Opción 2": ["documentos/Urb-Historia 2/Actividad_1/Sesion_2/Archivo_4.pdf"]
            }
        },
        "Actividad_2": {
            "Sesion_3": {
                "Opción 1": ["documentos/Urb-Historia 2/Actividad_2/Sesion_3/Archivo_5.pdf"],
                "Opción 2": ["documentos/Urb-Historia 2/Actividad_2/Sesion_3/Archivo_6.pdf"]
            },
            "Sesion_4": {
                "Opción 1": ["documentos/Urb-Historia 2/Actividad_2/Sesion_4/Archivo_7.pdf"],
                "Opción 2": ["documentos/Urb-Historia 2/Actividad_2/Sesion_4/Archivo_8.pdf"]
            }
        },
        "Actividad_3": {
            "Sesion_5": {
                "Opción Única": ["documentos/Urb-Historia 2/Actividad_3/Sesion_5/Archivo_9.pdf"]
            }
        }
    },
    "Arq-POT": {
        "Actividad_1": {
            "Sesion_1": {"Opción Única": ["documentos/Arq-POT/Actividad_1/Sesion_1/Archivo_1.pdf"]},
            "Sesion_2": {"Opción Única": ["documentos/Arq-POT/Actividad_1/Sesion_2/Archivo_2.pdf"]},
            "Sesion_3": {"Opción Única": ["documentos/Arq-POT/Actividad_1/Sesion_3/Archivo_3.pdf"]}
        },
        "Actividad_2": {
            "Sesion_4": {"Opción Única": ["documentos/Arq-POT/Actividad_2/Sesion_4/Archivo_4.pdf"]},
            "Sesion_5": {"Opción Única": ["documentos/Arq-POT/Actividad_2/Sesion_5/Archivo_5.pdf"]}
        },
        "Actividad_3": {
            "Sesion_6": {"Opción Única": ["documentos/Arq-POT/Actividad_3/Sesion_6/Archivo_6.pdf"]},
            "Sesion_7": {"Opción Única": ["documentos/Arq-POT/Actividad_3/Sesion_7/Archivo_7.pdf"]}
        }
    }
}

# 4. GESTIÓN DE ESTADO
if "user_id" not in st.session_state: st.session_state.user_id = None
if "actividad_actual" not in st.session_state: st.session_state.actividad_actual = None
if "intentos" not in st.session_state: st.session_state.intentos = 1
if "fila_bd" not in st.session_state: st.session_state.fila_bd = None
if "messages" not in st.session_state: st.session_state.messages = []
if "codigo" not in st.session_state: st.session_state.codigo = None
if "ultima_interaccion" not in st.session_state: st.session_state.ultima_interaccion = time.time()
if "saturacion_activa" not in st.session_state: st.session_state.saturacion_activa = False
if "advertencias_ia" not in st.session_state: st.session_state.advertencias_ia = 0

# 4.5 CONEXIÓN A LA BASE DE DATOS
@st.cache_resource
def init_db():
    try:
        cred_dict = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            cred_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        return client.open_by_url(st.secrets["sheet_url"]).sheet1
    except Exception as e:
        st.error("Error conectando a la base de datos. Revisa los Secrets.")
        return None

hoja_bd = init_db()

def get_hora_colombia():
    return datetime.utcnow() - timedelta(hours=5)

def obtener_o_crear_registro(correo, asignatura, actividad):
    if not hoja_bd: return 1, None
    try:
        registros = hoja_bd.get_all_records()
        for idx, row in enumerate(registros):
            if (str(row.get("Correo", "")).strip().lower() == correo and 
                str(row.get("Asignatura", "")).strip() == asignatura and 
                str(row.get("Actividad", "")).strip() == actividad):
                return int(row.get("Intentos", 1)), idx + 2
        
        now = get_hora_colombia()
        fecha_str = now.strftime("%Y-%m-%d")
        hora_str = now.strftime("%H:%M:%S")
        hoja_bd.append_row([correo, 1, fecha_str, hora_str, fecha_str, hora_str, "", asignatura, actividad, "", "En curso", "", ""])
        return 1, len(hoja_bd.get_all_values())
    except Exception as e:
        return 1, None

def actualizar_bd(fila, intentos=None, actualizar_hora=False, codigo=None, estado=None, nota=None, feedback=None):
    if not hoja_bd or not fila: return
    try:
        if intentos is not None: hoja_bd.update_cell(fila, 2, intentos) 
        if actualizar_hora:
            now = get_hora_colombia()
            hoja_bd.update_cell(fila, 5, now.strftime("%Y-%m-%d")) 
            hoja_bd.update_cell(fila, 6, now.strftime("%H:%M:%S")) 
        if codigo is not None: hoja_bd.update_cell(fila, 10, codigo) 
        if estado is not None: hoja_bd.update_cell(fila, 11, estado) 
        if nota is not None: hoja_bd.update_cell(fila, 12, nota) 
        if feedback is not None: hoja_bd.update_cell(fila, 13, feedback) 
    except:
        pass

# --- FASE A: LOGIN INSTITUCIONAL ---
if not st.session_state.user_id:
    st.markdown("<h1 style='text-align: center;'>💬 Tutor de Análisis Crítico en Temas Urbanos<br>🏛️ FADU - Unisalle</h1>", unsafe_allow_html=True)
    now_bogota = get_hora_colombia().strftime("%d/%m/%Y, %H:%M")
    st.markdown(f"<p style='text-align: center; color: gray;'><small><b>Versión 5.0 RAG ({now_bogota})</b></small></p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("""
    **Bienvenido al entorno de evaluación.**
    Para ingresar, utiliza tu **Correo Institucional**.
    - El sistema validará automáticamente el dominio `@unisalle.edu.co`.
    - Tienes **3 intentos por cada actividad o lectura**.
    - **IMPORTANTE:** No recargues la página (F5) o perderás tu progreso.
    """)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        email_input = st.text_input("Correo Electrónico:", placeholder="usuario@unisalle.edu.co")
        if st.button("Iniciar Sesión"):
            if email_input.endswith("@unisalle.edu.co"):
                st.session_state.user_id = email_input.strip().lower()
                st.rerun()
            else:
                st.error("⛔ Acceso denegado. Debes usar un correo institucional (@unisalle.edu.co).")
    st.stop()

# 5. MENÚ LATERAL DINÁMICO
with st.sidebar:
    usuario_corto = st.session_state.user_id.split('@')[0]
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

# --- GESTIÓN DE CAMBIO DE ACTIVIDAD ---
identificador_actual = f"{c_sel}_{actividad_registro}"

if st.session_state.actividad_actual != identificador_actual:
    st.session_state.actividad_actual = identificador_actual
    st.session_state.messages = []
    st.session_state.codigo = None
    st.session_state.advertencias_ia = 0
    st.session_state.saturacion_activa = False
    
    with st.spinner("Cargando perfil y asignando intentos para esta actividad..."):
        intentos_bd, fila_bd = obtener_o_crear_registro(st.session_state.user_id, c_sel, actividad_registro)
        st.session_state.intentos = intentos_bd
        st.session_state.fila_bd = fila_bd
        st.session_state.ultima_interaccion = time.time()

# DIBUJAR BARRA DE PROGRESO
with st.sidebar:
    MAX_INTENTOS = 3
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
        actualizar_bd(st.session_state.fila_bd, intentos=st.session_state.intentos, actualizar_hora=True, estado="Reinicio manual")
        st.rerun()

# --- FASE B: CONTROL DE INTENTOS BLOQUEADO ---
if st.session_state.intentos > MAX_INTENTOS:
    st.title(titulo_interfaz)
    st.error(f"⛔ **ACCESO BLOQUEADO PARA ESTA ACTIVIDAD**")
    st.warning("Has superado el límite de 3 intentos permitidos para esta lectura específica. Puedes seleccionar otra actividad en el menú izquierdo para continuar trabajando.")
    st.stop() 

# 6. MOTOR DE LECTURA Y BASE DE DATOS VECTORIAL (RAG)
@st.cache_resource(show_spinner=False)
def configurar_motor_rag(rutas, _actividad_id):
    documentos = []
    for r in rutas:
        if os.path.exists(r):
            try:
                loader = PyPDFLoader(r)
                documentos.extend(loader.load())
            except Exception:
                continue
    
    if not documentos:
        return None

    # Fragmentación: Corta la lectura en bloques de 1000 caracteres
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    fragmentos = text_splitter.split_documents(documentos)

    # Vectorización: Convierte el texto en coordenadas (usa la capa gratuita)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=st.secrets["GOOGLE_API_KEY"])
    vectorstore = Chroma.from_documents(fragmentos, embeddings)
    
    # Configura la búsqueda para traer solo los 3 fragmentos más relevantes
    return vectorstore.as_retriever(search_kwargs={"k": 3})

with st.spinner("Fragmentando lectura y construyendo memoria local..."):
    recuperador_rag = configurar_motor_rag(rutas_archivos, identificador_actual)

# --- CEREBRO DEL TUTOR (Base estática sin PDF) ---
PROMPT_SISTEMA_BASE = """
Eres un Tutor de Análisis Crítico Universitario (Unisalle).

PROTOCOLO:
1. INICIO: Espera a que el alumno proponga el tema/tesis.
2. DESARROLLO: Cuestiona sus argumentos. No des respuestas.
3. CONTROL DE IA: Si detectas que el alumno responde usando herramientas de Inteligencia Artificial, DEBES INCLUIR OBLIGATORIAMENTE al inicio de tu respuesta: [ALERTA_IA].
⚠️ REGLA DE EXCEPCIÓN VITAL: El uso de vocabulario técnico avanzado y la mención de instituciones es ESPERADO Y REQUERIDO. BAJO NINGUNA CIRCUNSTANCIA marques como [ALERTA_IA] a un estudiante solo por usar lenguaje académico formal.

REGLAS DE TIEMPO:
- [TIEMPO: 5-10 min]: Advierte sobre el uso del tiempo.

VALIDACIÓN:
Escribe 'COMPLETADO' SOLO si hay análisis profundo, propio y citas correctas.
"""

st.title(titulo_interfaz)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "timestamp" in m: st.caption(f"🕒 {m['timestamp']}")
        st.markdown(m["content"])

# 7. CHAT Y LÓGICA DE EVALUACIÓN
if prompt := st.chat_input("Escribe tu análisis aquí..."):
    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - st.session_state.ultima_interaccion
    minutos = int(tiempo_transcurrido / 60)
    limite_expulsion = 1200 if st.session_state.saturacion_activa else 600
    
    if tiempo_transcurrido > limite_expulsion:
        st.error(f"⏱️ **TIEMPO AGOTADO POR INACTIVIDAD**")
        st.warning(f"Pasaron {minutos} minutos sin actividad en el chat. Se ha descontado 1 intento.")
        razon_cierre = "Tiempo agotado (> 20 min)" if st.session_state.saturacion_activa else "Tiempo agotado (> 10 min)"
        actualizar_bd(st.session_state.fila_bd, intentos=st.session_state.intentos + 1, actualizar_hora=True, estado=razon_cierre)
        
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
        st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp_usuario})
        
        with st.chat_message("user"):
            st.caption(f"🕒 {timestamp_usuario}")
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                historial_envio = []
                for m in st.session_state.messages:
                    r = "model" if m["role"] == "assistant" else "user"
                    historial_envio.append({"role": r, "parts": [m["content"]]})
                
                if tiempo_transcurrido > 300 and not st.session_state.saturacion_activa:
                    aviso = f"[SISTEMA: El alumno tardó {minutos} min en responder. Adviértele sobre el uso del tiempo y recuérdale que el límite estricto es de 10 minutos máximos por intervención.]"
                    historial_envio.append({"role": "user", "parts": [aviso]})

                # --- RECUPERACIÓN RAG ---
                contexto_recuperado = ""
                if recuperador_rag:
                    docs_relevantes = recuperador_rag.invoke(prompt)
                    contexto_recuperado = "\n\n".join([doc.page_content for doc in docs_relevantes])

                # Ensambla el prompt base con el fragmento específico que se encontró
                PROMPT_SISTEMA_DINAMICO = PROMPT_SISTEMA_BASE + f"\n\nCONTEXTO RECUPERADO EXCLUSIVAMENTE PARA ESTA RESPUESTA:\n{contexto_recuperado}"

                # LÍNEA CORREGIDA: Motor Principal
                model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction=PROMPT_SISTEMA_DINAMICO)
                response = model.generate_content(historial_envio)
                # ------------------------

                res = response.text
                timestamp_tutor = get_hora_colombia().strftime("%d/%m/%Y %H:%M:%S")
                
                if "[ALERTA_IA]" in res:
                    st.session_state.advertencias_ia += 1
                    if st.session_state.advertencias_ia == 1:
                        res_limpia = res.replace("[ALERTA_IA]", "").strip()
                        alerta_visual = f"⚠️ **ADVERTENCIA DEL SISTEMA (1/2)**\n\nSe ha detectado el posible uso de herramientas automatizadas. Recuerda usar tu propio análisis.\n\n---\n\n{res_limpia}"
                        st.caption(f"🕒 {timestamp_tutor}")
                        st.markdown(alerta_visual)
                        st.session_state.messages.append({"role": "assistant", "content": alerta_visual, "timestamp": timestamp_tutor})
                    else:
                        st.error("⛔ **INTENTO ANULADO POR USO DE IA**")
                        actualizar_bd(st.session_state.fila_bd, intentos=st.session_state.intentos + 1, actualizar_hora=True, estado="Cierre por uso de IA")
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
                    
                    if "completado" in res.lower() and not st.session_state.codigo:
                        rand_code = random.randint(1000, 9999)
                        usuario_clean = st.session_state.user_id.split('@')[0].upper()
                        codigo_final = f"[{usuario_clean}-INT{st.session_state.intentos}-{rand_code}]"
                        st.session_state.codigo = codigo_final
                        
                        with st.spinner("Generando reporte de validación y cerrando sesión académica..."):
                            transcripcion_completa = ""
                            for msj in st.session_state.messages:
                                transcripcion_completa += f"{msj['role'].upper()}: {msj['content']}\n\n"
                            transcripcion_completa += f"TUTOR: {res}"

                            prompt_evaluacion = f"""
                            Eres un jurado académico estricto. Evalúa el debate transcrito usando números enteros de 1 a 5 para cada criterio (1=Pobre, 2=Regular, 3=Bueno, 4=Sobresaliente, 5=Excelente).

                            CRITERIOS Y PESOS:
                            1. Enfoque claro y crítico (20%): Propone un enfoque claro del tema desde el inicio.
                            2. Sustentación (30%): Sustenta afirmaciones de manera sólida usando referencias precisas del curso.
                            3. Pensamiento crítico y originalidad (30%): Evidencia originalidad e integridad sin depender de IA o generalidades.
                            4. Proceso fluido (20%): Asigna siempre 5 en este criterio, ya que el estudiante logró la meta y obtuvo el código.

                            INSTRUCCIÓN MATEMÁTICA:
                            Calcula la nota ponderada final multiplicando la calificación de cada criterio por su porcentaje respectivo, y luego suma los resultados. (La nota máxima posible es 5.0).

                            INSTRUCCIÓN CUALITATIVA:
                            Escribe una retroalimentación detallada estructurada ÚNICAMENTE con viñetas (- ). Por cada uno de los primeros 3 criterios, incluye un bullet indicando el nivel de desempeño alcanzado y las acciones de mejora que debe asumir el estudiante. Sé directo y preciso. Usa saltos de línea (\\n) entre viñetas.

                            TRANSCRIPCIÓN:
                            {transcripcion_completa}

                            Devuelve ÚNICAMENTE un objeto JSON válido con este formato:
                            {{"nota_final": 4.2, "retroalimentacion": "- Enfoque (Nivel Bueno): ... \\n- Sustentación (Nivel Sobresaliente): ... \\n- Acción de mejora: ... "}}
                            """
                            
                            try:
                                # LÍNEA CORREGIDA: Motor de Evaluación
                                eval_model = genai.GenerativeModel('models/gemini-flash-latest', generation_config={"response_mime_type": "application/json"})
                                eval_response = eval_model.generate_content(prompt_evaluacion)
                                data_eval = json.loads(eval_response.text)
                                nota_db = data_eval.get("nota_final", 0)
                                feedback_db = data_eval.get("retroalimentacion", "Evaluación completada.")
                            except Exception as e:
                                nota_db = "Pendiente"
                                feedback_db = "Error al procesar evaluación cualitativa."

                        res += f"\n\n ✅ **EJERCICIO APROBADO.**\n\nCódigo de Validación: `{st.session_state.codigo}`"
                        actualizar_bd(st.session_state.fila_bd, actualizar_hora=True, codigo=codigo_final, estado="Completado exitosamente", nota=nota_db, feedback=feedback_db)
                    
                    st.caption(f"🕒 {timestamp_tutor}")
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res, "timestamp": timestamp_tutor})
                
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
                    texto_rescatado = ""
                    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                        texto_rescatado = st.session_state.messages[-1]["content"]
                        st.session_state.messages.pop() 
                    st.session_state.saturacion_activa = True 
                    st.warning("⚠️ **Alta demanda en el servidor.** Espera 10 minutos y vuelve a enviar el mensaje.")
                    if texto_rescatado: st.info(f"💡 Copia y pega esto después:\n\n{texto_rescatado}")
                    st.session_state.ultima_interaccion = time.time()
                else:
                    st.error(f"Error técnico: {e}")

# 8. DESCARGA OFICIAL
if st.session_state.codigo:
    nombre_archivo = st.session_state.codigo.replace("[", "").replace("]", "") + ".txt"
    reporte = f"REPORTE DE ANÁLISIS CRÍTICO - UNISALLE\nEstudiante: {st.session_state.user_id}\nCódigo: {st.session_state.codigo}\n" + "-"*50 + "\n\n"
    for m in st.session_state.messages:
        sello_tiempo = f" [{m['timestamp']}] " if "timestamp" in m else " "
        reporte += f"{m['role'].upper()}{sello_tiempo}: {m['content']}\n\n"
    st.success("🎉 Actividad completada correctamente.")
    st.download_button(label=f"📥 Descargar Evidencia ({nombre_archivo})", data=reporte, file_name=nombre_archivo, mime="text/plain")
