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

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tutor de Análisis Crítico", layout="wide")

# 2. CONEXIÓN API GEMINI
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

# 3. RUTAS DE DOCUMENTOS
CONFIG = {
    "Urb-Historia 1": {
        "Actividad_1": [
            "documentos/Urb-Historia 1/Actividad_1/Archivo_1.pdf",
            "documentos/Urb-Historia 1/Actividad_1/Archivo_2.pdf",
            "documentos/Urb-Historia 1/Actividad_1/Archivo_3.pdf"
        ],
        "Actividad_2": [
            "documentos/Urb-Historia 1/Actividad_2/Archivo_4.pdf",
            "documentos/Urb-Historia 1/Actividad_2/Archivo_5.pdf"
        ],
        "Actividad_3": [
            "documentos/Urb-Historia 1/Actividad_3/Archivo_6.pdf"
        ]
    },
    "Urb-Historia 2": {
        "Actividad_1": {
            "Sesion_1": [
                "documentos/Urb-Historia 2/Actividad_1/Sesion_1/Archivo_1.pdf",
                "documentos/Urb-Historia 2/Actividad_1/Sesion_1/Archivo_2.pdf"
            ],
            "Sesion_2": [
                "documentos/Urb-Historia 2/Actividad_1/Sesion_2/Archivo_3.pdf",
                "documentos/Urb-Historia 2/Actividad_1/Sesion_2/Archivo_4.pdf"
            ]
        },
        "Actividad_2": {
            "Sesion_3": [
                "documentos/Urb-Historia 2/Actividad_2/Sesion_3/Archivo_5.pdf",
                "documentos/Urb-Historia 2/Actividad_2/Sesion_3/Archivo_6.pdf"
            ],
            "Sesion_4": [
                "documentos/Urb-Historia 2/Actividad_2/Sesion_4/Archivo_7.pdf",
                "documentos/Urb-Historia 2/Actividad_2/Sesion_4/Archivo_8.pdf"
            ]
        },
        "Actividad_3": {
            "Sesion_5": [
                "documentos/Urb-Historia 2/Actividad_3/Sesion_5/Archivo_9.pdf"
            ]
        }
    },
    "Arq-POT": {
        "Actividad_1": {
            "Sesion_1": ["documentos/Arq-POT/Actividad_1/Sesion_1/Archivo_1.pdf"],
            "Sesion_2": ["documentos/Arq-POT/Actividad_1/Sesion_2/Archivo_2.pdf"],
            "Sesion_3": ["documentos/Arq-POT/Actividad_1/Sesion_3/Archivo_3.pdf"]
        },
        "Actividad_2": {
            "Sesion_4": ["documentos/Arq-POT/Actividad_2/Sesion_4/Archivo_4.pdf"],
            "Sesion_5": ["documentos/Arq-POT/Actividad_2/Sesion_5/Archivo_5.pdf"]
        },
        "Actividad_3": {
            "Sesion_6": ["documentos/Arq-POT/Actividad_3/Sesion_6/Archivo_6.pdf"],
            "Sesion_7": ["documentos/Arq-POT/Actividad_3/Sesion_7/Archivo_7.pdf"]
        }
    }
}

# 4. GESTIÓN DE ESTADO (MEMORIA DE LA APP)
if "user_id" not in st.session_state:
    st.session_state.user_id = None
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

# 4.5 CONEXIÓN A LA BASE DE DATOS (GOOGLE SHEETS)
@st.cache_resource
def init_db():
    try:
        cred_dict = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            cred_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(creds)
        return client.open_by_url(st.secrets["sheet_url"]).sheet1
    except Exception as e:
        st.error("Error conectando a la base de datos de auditoría. Revisa los Secrets.")
        return None

hoja_bd = init_db()

def get_hora_colombia():
    return datetime.utcnow() - timedelta(hours=5)

def registrar_ingreso(correo):
    if not hoja_bd: return 1, None
    try:
        registros = hoja_bd.get_all_records()
        fila = None
        intentos_actuales = 1
        
        for idx, row in enumerate(registros):
            if str(row.get("Correo", "")).strip().lower() == correo:
                fila = idx + 2 
                intentos_actuales = int(row.get("Intentos", 1))
                break
        
        now = get_hora_colombia()
        hora_str = now.strftime("%H:%M:%S")
        
        if fila:
            hoja_bd.update_cell(fila, 5, hora_str)
            hoja_bd.update_cell(fila, 9, "En curso")
            return intentos_actuales, fila
        else:
            fecha_str = now.strftime("%Y-%m-%d")
            hoja_bd.append_row([correo, 1, fecha_str, hora_str, hora_str, "", "", "", "En curso"])
            nueva_fila = len(hoja_bd.get_all_values())
            return 1, nueva_fila
    except Exception as e:
        return 1, None

def actualizar_bd(fila, intentos=None, actualizar_hora=False, asignatura=None, actividad=None, codigo=None, estado=None):
    if not hoja_bd or not fila: return
    try:
        if intentos is not None:
            hoja_bd.update_cell(fila, 2, intentos)
        if actualizar_hora:
            now = get_hora_colombia()
            hoja_bd.update_cell(fila, 5, now.strftime("%H:%M:%S"))
        if asignatura is not None:
            hoja_bd.update_cell(fila, 6, asignatura)
        if actividad is not None:
            hoja_bd.update_cell(fila, 7, actividad)
        if codigo is not None:
            hoja_bd.update_cell(fila, 8, codigo)
        if estado is not None:
            hoja_bd.update_cell(fila, 9, estado)
    except:
        pass

# --- FASE A: LOGIN INSTITUCIONAL (@unisalle.edu.co) ---
if not st.session_state.user_id:
    st.markdown("<h1 style='text-align: center;'>💬 Tutor de Análisis Crítico en Temas Urbanos<br>🏛️ FADU - Unisalle</h1>", unsafe_allow_html=True)
    
    now_bogota = get_hora_colombia().strftime("%d/%m/%Y, %H:%M")
    st.markdown(f"<p style='text-align: center; color: gray;'><small><b>Versión 2.8 ({now_bogota})</b></small></p>", unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    **Bienvenido al entorno de evaluación.**
    
    Para ingresar, utiliza tu **Correo Institucional**.
    - El sistema validará automáticamente el dominio `@unisalle.edu.co`.
    - Tienes **3 intentos** para lograr el objetivo de análisis.
    - **IMPORTANTE:** No recargues la página (F5) o perderás tu progreso.
    """)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        email_input = st.text_input("Correo Electrónico:", placeholder="usuario@unisalle.edu.co")
        
        if st.button("Iniciar Sesión"):
            if email_input.endswith("@unisalle.edu.co"):
                correo_limpio = email_input.strip().lower()
                
                with st.spinner("Sincronizando base de datos institucional..."):
                    intentos_bd, fila_bd = registrar_ingreso(correo_limpio)
                    
                    st.session_state.user_id = correo_limpio
                    st.session_state.intentos = intentos_bd
                    st.session_state.fila_bd = fila_bd
                    st.session_state.ultima_interaccion = time.time()
                
                st.rerun()
            else:
                st.error("⛔ Acceso denegado. Debes usar un correo institucional (@unisalle.edu.co).")
    st.stop()

# --- FASE B: CONTROL DE INTENTOS ---
MAX_INTENTOS = 3
if st.session_state.intentos > MAX_INTENTOS:
    st.error(f"⛔ **ACCESO BLOQUEADO PARA: {st.session_state.user_id}**")
    st.warning("Has superado el límite de 3 intentos permitidos. Por favor, contacta a tu docente para revisar tu caso.")
    if st.button("Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# 5. MENÚ LATERAL DINÁMICO
with st.sidebar:
    usuario_corto = st.session_state.user_id.split('@')[0]
    st.title(f"👤 {usuario_corto}")
    
    progreso = st.session_state.intentos / MAX_INTENTOS
    st.progress(progreso, text=f"Intento {st.session_state.intentos} de {MAX_INTENTOS}")
    
    st.divider()
    
    c_sel = st.selectbox("Asignatura", list(CONFIG.keys()))
    a_sel = st.selectbox("Actividad", list(CONFIG[c_sel].keys()))
    
    if isinstance(CONFIG[c_sel][a_sel], dict):
        s_sel = st.selectbox("Sesión", list(CONFIG[c_sel][a_sel].keys()))
        rutas_archivos = CONFIG[c_sel][a_sel][s_sel]
        titulo_interfaz = f"💬 {c_sel} | {a_sel} | {s_sel}"
        actividad_registro = f"{a_sel} | {s_sel}" 
    else:
        s_sel = None
        rutas_archivos = CONFIG[c_sel][a_sel]
        titulo_interfaz = f"💬 {c_sel} | {a_sel}"
        actividad_registro = a_sel 
    
    st.divider()
    if st.button("🗑️ Reiniciar (Gasta 1 Intento)"):
        st.session_state.intentos += 1
        st.session_state.messages = []
        st.session_state.codigo = None
        st.session_state.advertencias_ia = 0
        st.session_state.saturacion_activa = False
        st.session_state.ultima_interaccion = time.time()
        
        actualizar_bd(st.session_state.fila_bd, intentos=st.session_state.intentos, actualizar_hora=True, asignatura=c_sel, actividad=actividad_registro, estado="Reinicio manual")
        st.rerun()

# 6. CARGAR CONTEXTO
def leer_pdf(rutas):
    texto = ""
    for r in rutas:
        if os.path.exists(r):
            try:
                lector = PdfReader(r)
                for p in lector.pages: texto += p.extract_text() + "\n"
            except: continue
    return texto

texto_referencia = leer_pdf(rutas_archivos)

# --- CEREBRO DEL TUTOR ---
PROMPT_SISTEMA = f"""
Eres un Tutor de Análisis Crítico Universitario (Unisalle).
Texto de referencia: {texto_referencia}

PROTOCOLO:
1. INICIO: Espera a que el alumno proponga el tema/tesis.
2. DESARROLLO: Cuestiona sus argumentos. No des respuestas.
3. CONTROL DE IA (NUEVO): Si detectas que el alumno responde usando herramientas de Inteligencia Artificial (ChatGPT, Gemini, etc.), textos genéricos copiados y pegados, o falta de sustento personal, DEBES INCLUIR OBLIGATORIAMENTE al inicio de tu respuesta la etiqueta secreta: [ALERTA_IA]. Luego, indícale brevemente qué falló y recuérdale que debe usar sus propias ideas.

REGLAS DE TIEMPO (Invisible al alumno):
- [TIEMPO: 5-10 min]: Advierte sobre el uso del tiempo y recuérdale que el límite es 10 minutos.

VALIDACIÓN:
Escribe 'COMPLETADO' SOLO si hay análisis profundo, propio y citas correctas.
"""

st.title(titulo_interfaz)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "timestamp" in m:
            st.caption(f"🕒 {m['timestamp']}")
        st.markdown(m["content"])

# 7. CHAT CON LÓGICA DE TIEMPO Y MANEJO DE ERRORES
if prompt := st.chat_input("Escribe tu análisis aquí..."):
    
    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - st.session_state.ultima_interaccion
    minutos = int(tiempo_transcurrido / 60)
    
    # Lógica de tiempos dinámicos (10 min normal / 20 min en saturación)
    limite_expulsion = 1200 if st.session_state.saturacion_activa else 600
    
    if tiempo_transcurrido > limite_expulsion:
        st.error(f"⏱️ **TIEMPO AGOTADO POR INACTIVIDAD**")
        st.warning(f"Pasaron {minutos} minutos sin actividad en el chat. Se ha descontado 1 intento.")
        
        razon_cierre = "Tiempo agotado (> 20 min por saturación)" if st.session_state.saturacion_activa else "Tiempo agotado (> 10 min)"
        actualizar_bd(st.session_state.fila_bd, intentos=st.session_state.intentos + 1, actualizar_hora=True, asignatura=c_sel, actividad=actividad_registro, estado=razon_cierre)
        
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
        actualizar_bd(st.session_state.fila_bd, actualizar_hora=True, asignatura=c_sel, actividad=actividad_registro, estado="En curso")
        
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
                
                # Advertencia de los 5 a 10 minutos (Solo aplica si no hay saturación)
                if tiempo_transcurrido > 300 and not st.session_state.saturacion_activa:
                    aviso = f"[SISTEMA: El alumno tardó {minutos} min en responder. Adviértele sobre el uso del tiempo y recuérdale que el límite estricto es de 10 minutos máximos por intervención.]"
                    historial_envio.append({"role": "user", "parts": [aviso]})

                model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction=PROMPT_SISTEMA)
                response = model.generate_content(historial_envio)
                res = response.text
                timestamp_tutor = get_hora_colombia().strftime("%d/%m/%Y %H:%M:%S")
                
                # ----------------------------------------------------
                # SISTEMA DE DETECCIÓN DE IA (AMARILLA Y ROJA)
                # ----------------------------------------------------
                if "[ALERTA_IA]" in res:
                    st.session_state.advertencias_ia += 1
                    
                    if st.session_state.advertencias_ia == 1:
                        # Primera Advertencia (Tarjeta Amarilla)
                        res_limpia = res.replace("[ALERTA_IA]", "").strip()
                        alerta_visual = f"⚠️ **ADVERTENCIA DEL SISTEMA (1/2)**\n\nSe ha detectado el posible uso de herramientas de Inteligencia Artificial (LLMs) o textos generados automáticamente en tu respuesta. Recuerda que el objetivo de esta actividad es desarrollar tu propio pensamiento crítico. Si reincides en esta práctica, tu intento será anulado.\n\n---\n\n{res_limpia}"
                        
                        st.caption(f"🕒 {timestamp_tutor}")
                        st.markdown(alerta_visual)
                        st.session_state.messages.append({"role": "assistant", "content": alerta_visual, "timestamp": timestamp_tutor})
                        
                    else:
                        # Reincidencia: Expulsión (Tarjeta Roja)
                        st.error("⛔ **INTENTO ANULADO POR USO DE IA**")
                        st.warning("Persistente detección de uso de IA en el desarrollo del ejercicio por parte del usuario. Intento finalizado por infracción de normas.")
                        
                        actualizar_bd(st.session_state.fila_bd, intentos=st.session_state.intentos + 1, actualizar_hora=True, asignatura=c_sel, actividad=actividad_registro, estado="Cierre por uso de IA")
                        
                        st.session_state.intentos += 1
                        st.session_state.messages = []
                        st.session_state.codigo = None
                        st.session_state.advertencias_ia = 0
                        st.session_state.saturacion_activa = False
                        st.session_state.ultima_interaccion = time.time()
                        
                        time.sleep(5)
                        st.rerun()
                # ----------------------------------------------------
                else:
                    # Flujo Normal: Aprobación y Respuestas
                    st.session_state.saturacion_activa = False # Se resetea la saturación si hubo éxito
                    
                    if "completado" in res.lower() and not st.session_state.codigo:
                        rand_code = random.randint(1000, 9999)
                        usuario_clean = st.session_state.user_id.split('@')[0].upper()
                        codigo_final = f"[{usuario_clean}-INT{st.session_state.intentos}-{rand_code}]"
                        
                        st.session_state.codigo = codigo_final
                        res += f"\n\n ✅ **EJERCICIO APROBADO.**\n\nCódigo de Validación: `{st.session_state.codigo}`"
                        
                        actualizar_bd(st.session_state.fila_bd, actualizar_hora=True, asignatura=c_sel, actividad=actividad_registro, codigo=codigo_final, estado="Completado exitosamente")
                    
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
                        
                    st.session_state.saturacion_activa = True # Activa el reloj de 20 minutos
                    
                    st.warning("⚠️ **Alta demanda en el servidor.** Por favor, espera **aproximadamente 10 minutos** y vuelve a intentar enviar tu mensaje.\n\n🚨 **IMPORTANTE: NO RECARGUES NI ACTUALICES LA PÁGINA (F5)** o perderás tu intento.")
                    if texto_rescatado:
                        st.info(f"💡 **Copia tu mensaje aquí abajo, espera 10 minutos, pégalo en el chat y vuelve a enviarlo:**\n\n{texto_rescatado}")
                    st.session_state.ultima_interaccion = time.time()
                else:
                    st.error(f"Se ha producido un error técnico: {e}")

# 8. DESCARGA OFICIAL
if st.session_state.codigo:
    nombre_archivo_limpio = st.session_state.codigo.replace("[", "").replace("]", "") + ".txt"
    
    reporte = f"REPORTE DE ANÁLISIS CRÍTICO - UNISALLE\n"
    reporte += f"Estudiante: {st.session_state.user_id}\n"
    reporte += f"Código de Validación: {st.session_state.codigo}\n"
    reporte += "-"*50 + "\n\n"
    for m in st.session_state.messages:
        sello_tiempo = f" [{m['timestamp']}] " if "timestamp" in m else " "
        reporte += f"{m['role'].upper()}{sello_tiempo}: {m['content']}\n\n"
        
    st.success("🎉 Actividad completada correctamente.")
    
    st.download_button(
        label=f"📥 Descargar Evidencia ({nombre_archivo_limpio})", 
        data=reporte, 
        file_name=nombre_archivo_limpio,
        mime="text/plain"
    )
