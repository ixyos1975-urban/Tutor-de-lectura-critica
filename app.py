import streamlit as st
import google.generativeai as genai
import random
import os
import time
from PyPDF2 import PdfReader

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tutor de Análisis Crítico", layout="wide")

# 2. CONEXIÓN API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

# 3. RUTAS DE DOCUMENTOS
CONFIG = {
    "Historia 1": {
        "Actividad 1": {
            "Sesión 1": ["documentos/Historia_1/Act_1/Sesion_1/f1.pdf"]
        }
    }
}

# 4. GESTIÓN DE ESTADO (MEMORIA DE LA APP)
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "intentos" not in st.session_state:
    st.session_state.intentos = 1
if "messages" not in st.session_state:
    st.session_state.messages = []
if "codigo" not in st.session_state:
    st.session_state.codigo = None
if "ultima_interaccion" not in st.session_state:
    st.session_state.ultima_interaccion = time.time()

# --- FASE A: LOGIN INSTITUCIONAL (@unisalle.edu.co) ---
if not st.session_state.user_id:
    st.title("🔐 Tutor de Análisis Crítico | Unisalle")
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
            # Validación estricta de dominio
            if email_input.endswith("@unisalle.edu.co"):
                st.session_state.user_id = email_input.strip().lower()
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

# 5. MENÚ LATERAL
with st.sidebar:
    # Mostramos el usuario limpio (sin el @unisalle...) para que se vea bien
    usuario_corto = st.session_state.user_id.split('@')[0]
    st.title(f"👤 {usuario_corto}")
    
    # Barra de progreso visual
    progreso = st.session_state.intentos / MAX_INTENTOS
    st.progress(progreso, text=f"Intento {st.session_state.intentos} de {MAX_INTENTOS}")
    
    st.divider()
    
    c_sel = st.selectbox("Curso", list(CONFIG.keys()))
    a_sel = st.selectbox("Actividad", list(CONFIG[c_sel].keys()))
    s_sel = st.selectbox("Sesión", list(CONFIG[c_sel][a_sel].keys()))
    
    st.divider()
    if st.button("🗑️ Reiniciar (Gasta 1 Intento)"):
        st.session_state.intentos += 1
        st.session_state.messages = []
        st.session_state.codigo = None
        st.session_state.ultima_interaccion = time.time()
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

texto_referencia = leer_pdf(CONFIG[c_sel][a_sel][s_sel])

# --- CEREBRO DEL TUTOR ---
PROMPT_SISTEMA = f"""
Eres un Tutor de Análisis Crítico Universitario (Unisalle).
Texto de referencia: {texto_referencia}

PROTOCOLO:
1. INICIO: Espera a que el alumno proponga el tema/tesis.
2. DESARROLLO: Cuestiona sus argumentos. No des respuestas.
3. INTEGRIDAD: Si detectas respuestas de IA o genéricas, exige citas del PDF.

REGLAS DE TIEMPO (Invisible al alumno):
- [TIEMPO: 5-10 min]: Advierte sobre la inactividad y el uso de fuentes externas.
- [TIEMPO: >10 min]: Cierre inminente.

VALIDACIÓN:
Escribe 'COMPLETADO' SOLO si hay análisis profundo, propio y citas correctas.
"""

st.title(f"💬 Sesión: {s_sel}")

# Historial de chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 7. CHAT CON LÓGICA DE TIEMPO
if prompt := st.chat_input("Escribe tu análisis aquí..."):
    
    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - st.session_state.ultima_interaccion
    minutos = int(tiempo_transcurrido / 60)
    
    # CASO 1: INACTIVIDAD (> 10 mins)
    if tiempo_transcurrido > 600:
        st.error(f"⏱️ **TIEMPO AGOTADO POR INACTIVIDAD**")
        st.warning(f"Pasaron {minutos} minutos sin actividad. Se ha descontado 1 intento.")
        st.session_state.intentos += 1
        st.session_state.messages = []
        st.session_state.codigo = None
        st.session_state.ultima_interaccion = time.time()
        time.sleep(3)
        st.rerun()

    # CASO 2: INTERACCIÓN VÁLIDA
    else:
        st.session_state.ultima_interaccion = time.time()
        
        if len(prompt) > 800:
            st.toast("⚠️ Respuesta muy larga. Resume con tus palabras.", icon="🚫")

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                historial_envio = []
                for m in st.session_state.messages:
                    r = "model" if m["role"] == "assistant" else "user"
                    historial_envio.append({"role": r, "parts": [m["content"]]})
                
                # Advertencia de tiempo (5-10 mins)
                if tiempo_transcurrido > 300:
                    aviso = f"[SISTEMA: El alumno tardó {minutos} min. Adviértele sobre inactividad.]"
                    historial_envio.append({"role": "user", "parts": [aviso]})

                model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction=PROMPT_SISTEMA)
                response = model.generate_content(historial_envio)
                res = response.text
                
                # GENERACIÓN DE CÓDIGO UNISALLE (ID + INTENTO + RANDOM)
                if "completado" in res.lower() and not st.session_state.codigo:
                    rand_code = random.randint(1000, 9999)
                    # Tomamos el usuario antes del @ y lo ponemos en mayúsculas
                    usuario_clean = st.session_state.user_id.split('@')[0].upper()
                    # Estructura del código: [JUAN.PEREZ-INT1-8492]
                    codigo_final = f"[{usuario_clean}-INT{st.session_state.intentos}-{rand_code}]"
                    
                    st.session_state.codigo = codigo_final
                    res += f"\n\n ✅ **EJERCICIO APROBADO.**\n\nCódigo de Validación: `{st.session_state.codigo}`"
                
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
                
            except Exception as e:
                st.error(f"Error: {e}")

# 8. DESCARGA OFICIAL (Nombre del archivo = Código)
if st.session_state.codigo:
    # 1. Quitamos los corchetes para el nombre del archivo
    nombre_archivo_limpio = st.session_state.codigo.replace("[", "").replace("]", "") + ".txt"
    
    # 2. Preparamos el contenido del archivo
    reporte = f"REPORTE DE ANÁLISIS CRÍTICO - UNISALLE\n"
    reporte += f"Estudiante: {st.session_state.user_id}\n"
    reporte += f"Código de Validación: {st.session_state.codigo}\n"
    reporte += "-"*50 + "\n\n"
    for m in st.session_state.messages:
        reporte += f"{m['role'].upper()}: {m['content']}\n\n"
        
    st.success("🎉 Actividad completada correctamente.")
    
    # 3. Botón de descarga con el nombre exacto
    st.download_button(
        label=f"📥 Descargar Evidencia ({nombre_archivo_limpio})", 
        data=reporte, 
        file_name=nombre_archivo_limpio,
        mime="text/plain"
    )
