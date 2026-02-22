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

# 3. RUTAS DE DOCUMENTOS (ESTRUCTURA DEFINITIVA SIN TILDES)
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
if "messages" not in st.session_state:
    st.session_state.messages = []
if "codigo" not in st.session_state:
    st.session_state.codigo = None
if "ultima_interaccion" not in st.session_state:
    st.session_state.ultima_interaccion = time.time()

# --- FASE A: LOGIN INSTITUCIONAL (@unisalle.edu.co) ---
if not st.session_state.user_id:
    # Nuevo título centrado con salto de línea
    st.markdown("<h1 style='text-align: center;'>💬 Tutor de Análisis Crítico en Temas Urbanos<br>🏛️ FADU - Unisalle</h1>", unsafe_allow_html=True)
    
    # Fecha de creación y versión unificada con formato numérico
    st.markdown("<p style='text-align: center; color: gray;'><small><b>Versión 1.31</b> (22/02/2026)</small></p>", unsafe_allow_html=True)
    
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

# 5. MENÚ LATERAL DINÁMICO
with st.sidebar:
    usuario_corto = st.session_state.user_id.split('@')[0]
    st.title(f"👤 {usuario_corto}")
    
    progreso = st.session_state.intentos / MAX_INTENTOS
    st.progress(progreso, text=f"Intento {st.session_state.intentos} de {MAX_INTENTOS}")
    
    st.divider()
    
    # Selectores dinámicos
    c_sel = st.selectbox("Asignatura", list(CONFIG.keys()))
    a_sel = st.selectbox("Actividad", list(CONFIG[c_sel].keys()))
    
    # Lógica inteligente: ¿Hay sesiones o son archivos directos?
    if isinstance(CONFIG[c_sel][a_sel], dict):
        s_sel = st.selectbox("Sesión", list(CONFIG[c_sel][a_sel].keys()))
        rutas_archivos = CONFIG[c_sel][a_sel][s_sel]
        titulo_interfaz = f"💬 {c_sel} | {a_sel} | {s_sel}"
    else:
        s_sel = None
        rutas_archivos = CONFIG[c_sel][a_sel]
        titulo_interfaz = f"💬 {c_sel} | {a_sel}"
    
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

texto_referencia = leer_pdf(rutas_archivos)

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

st.title(titulo_interfaz)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 7. CHAT CON LÓGICA DE TIEMPO Y MANEJO DE ERRORES
if prompt := st.chat_input("Escribe tu análisis aquí..."):
    
    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - st.session_state.ultima_interaccion
    minutos = int(tiempo_transcurrido / 60)
    
    if tiempo_transcurrido > 600:
        st.error(f"⏱️ **TIEMPO AGOTADO POR INACTIVIDAD**")
        st.warning(f"Pasaron {minutos} minutos sin actividad. Se ha descontado 1 intento.")
        st.session_state.intentos += 1
        st.session_state.messages = []
        st.session_state.codigo = None
        st.session_state.ultima_interaccion = time.time()
        time.sleep(3)
        st.rerun()

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
                
                if tiempo_transcurrido > 300:
                    aviso = f"[SISTEMA: El alumno tardó {minutos} min. Adviértele sobre inactividad.]"
                    historial_envio.append({"role": "user", "parts": [aviso]})

                model = genai.GenerativeModel('models/gemini-flash-latest', system_instruction=PROMPT_SISTEMA)
                response = model.generate_content(historial_envio)
                res = response.text
                
                if "completado" in res.lower() and not st.session_state.codigo:
                    rand_code = random.randint(1000, 9999)
                    usuario_clean = st.session_state.user_id.split('@')[0].upper()
                    codigo_final = f"[{usuario_clean}-INT{st.session_state.intentos}-{rand_code}]"
                    
                    st.session_state.codigo = codigo_final
                    res += f"\n\n ✅ **EJERCICIO APROBADO.**\n\nCódigo de Validación: `{st.session_state.codigo}`"
                
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
                
            except Exception as e:
                error_msg = str(e).lower()
                # Detectamos si es el error 429 de cuota superada
                if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
                    st.warning("⚠️ **Alta demanda en el servidor.** El Tutor Virtual está procesando las solicitudes de muchos estudiantes al mismo tiempo. Por favor, espera aproximadamente un minuto y vuelve a intentar enviar tu mensaje.")
                    # Eliminamos el último mensaje del usuario para que pueda volver a enviarlo sin que se duplique
                    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                        st.session_state.messages.pop() 
                else:
                    # Si es otro tipo de error, lo mostramos normalmente
                    st.error(f"Se ha producido un error técnico: {e}")

# 8. DESCARGA OFICIAL
if st.session_state.codigo:
    nombre_archivo_limpio = st.session_state.codigo.replace("[", "").replace("]", "") + ".txt"
    
    reporte = f"REPORTE DE ANÁLISIS CRÍTICO - UNISALLE\n"
    reporte += f"Estudiante: {st.session_state.user_id}\n"
    reporte += f"Código de Validación: {st.session_state.codigo}\n"
    reporte += "-"*50 + "\n\n"
    for m in st.session_state.messages:
        reporte += f"{m['role'].upper()}: {m['content']}\n\n"
        
    st.success("🎉 Actividad completada correctamente.")
    
    st.download_button(
        label=f"📥 Descargar Evidencia ({nombre_archivo_limpio})", 
        data=reporte, 
        file_name=nombre_archivo_limpio,
        mime="text/plain"
    )
