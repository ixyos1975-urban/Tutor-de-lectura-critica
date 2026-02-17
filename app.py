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

# 3. RUTAS DE TUS DOCUMENTOS
CONFIG = {
    "Historia 1": {
        "Actividad 1": {
            "Sesión 1": ["documentos/Historia_1/Act_1/Sesion_1/f1.pdf"]
        }
    }
}

# 4. LECTURA DE PDF
def leer_pdf(rutas):
    texto = ""
    for r in rutas:
        if os.path.exists(r):
            try:
                lector = PdfReader(r)
                for p in lector.pages: texto += p.extract_text() + "\n"
            except: continue
    return texto

# 5. MENÚ LATERAL
with st.sidebar:
    st.title("📂 Menú de Tutoría")
    c_sel = st.selectbox("Curso", list(CONFIG.keys()))
    a_sel = st.selectbox("Actividad", list(CONFIG[c_sel].keys()))
    s_sel = st.selectbox("Sesión", list(CONFIG[c_sel][a_sel].keys()))
    
    st.divider()
    
    # Botón de reinicio manual
    if st.button("🗑️ Reiniciar Conversación"):
        st.session_state.messages = []
        st.session_state.codigo = None
        st.session_state.ultima_interaccion = time.time() # Reiniciamos el reloj
        st.rerun()

# 6. CARGAR CONTEXTO
texto_referencia = leer_pdf(CONFIG[c_sel][a_sel][s_sel])

# --- INSTRUCCIONES DEL TUTOR (Modificadas: Sin mencionar "Socrático") ---
PROMPT_SISTEMA = f"""
Eres un Tutor de Análisis Crítico Universitario.
Texto de referencia: {texto_referencia}

ESTRUCTURA DE COMPORTAMIENTO:
1. FASE INICIAL: No inicies el tema. Saluda y espera a que el alumno proponga el tema/tesis.
2. FASE DESARROLLO: Tu método es el cuestionamiento profundo. NO des respuestas directas. Haz preguntas que desafíen los argumentos del alumno basándote estrictamente en el texto.
3. ANTI-PLAGIO: Si la respuesta es genérica o parece de IA, exige opinión propia y citas del PDF.

INSTRUCCIÓN ESPECIAL DE TIEMPO:
A veces recibirás una nota del sistema diciendo "[SISTEMA: El alumno tardó X minutos]".
- Si el alumno tardó entre 5 y 10 minutos: Tu respuesta DEBE empezar con una advertencia amable pero firme sobre el tiempo. Ejemplo: "Te tomaste un tiempo considerable. Recuerda que el límite es de 10 minutos por intervención. Sobre tu punto..."
- Si el alumno responde cosas vagas tras una demora: Sé severo. Dile: "Esa respuesta no aporta al análisis y el tiempo sigue corriendo. Necesito argumentos sobre el texto ahora mismo o la sesión se cerrará."

SOLO escribe 'COMPLETADO' si hay análisis profundo y citas correctas.
"""

st.title(f"💬 {s_sel}")

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "codigo" not in st.session_state:
    st.session_state.codigo = None

# Variable crítica para el temporizador
if "ultima_interaccion" not in st.session_state:
    st.session_state.ultima_interaccion = time.time()

# Mostrar historial
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 7. CHAT CON LÓGICA DE TIEMPO
if prompt := st.chat_input("Escribe tu análisis aquí..."):
    
    # --- PASO A: VERIFICACIÓN DEL RELOJ ---
    tiempo_actual = time.time()
    tiempo_transcurrido = tiempo_actual - st.session_state.ultima_interaccion
    minutos_transcurridos = int(tiempo_transcurrido / 60)
    
    # CASO 1: PENALIZACIÓN MÁXIMA (> 10 minutos)
    if tiempo_transcurrido > 600: # 600 segundos = 10 minutos
        st.error(f"⏱️ **SESIÓN CERRADA POR INACTIVIDAD**")
        st.warning(f"Han pasado {minutos_transcurridos} minutos desde tu última respuesta. El límite es de 10 minutos para evitar el uso de herramientas externas. Debes reiniciar.")
        st.session_state.messages = []
        st.session_state.codigo = None
        st.session_state.ultima_interaccion = time.time()
        if st.button("Empezar de nuevo"):
            st.rerun()
        st.stop()

    # CASO 2: MENSAJE VÁLIDO
    else:
        # Actualizamos el reloj
        st.session_state.ultima_interaccion = time.time()
        
        # Filtro de longitud
        if len(prompt) > 800:
            st.toast("⚠️ Respuesta muy larga. Resume con tus palabras.", icon="🚫")

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Preparamos el mensaje
                historial_envio = []
                for m in st.session_state.messages:
                    r = "model" if m["role"] == "assistant" else "user"
                    historial_envio.append({"role": r, "parts": [m["content"]]})
                
                # Chivatazo de tiempo (> 5 minutos)
                if tiempo_transcurrido > 300:
                    mensaje_sistema = f"""[SISTEMA: El alumno tardó {minutos_transcurridos} minutos en responder esto. 
                    ADVIÉRTELE que está cerca del límite de 10 minutos. Si su respuesta es corta o irrelevante, regáñalo.]"""
                    historial_envio.append({"role": "user", "parts": [mensaje_sistema]})

                # Llamada a la IA
                model = genai.GenerativeModel(
                    model_name='models/gemini-flash-latest', 
                    system_instruction=PROMPT_SISTEMA
                )
                
                response = model.generate_content(historial_envio)
                res = response.text
                
                # Validación
                if "completado" in res.lower() and not st.session_state.codigo:
                    st.session_state.codigo = f"[AC-{random.randint(1000, 9999)}]"
                    res += f"\n\n ✅ **VALIDADO.** Código: {st.session_state.codigo}"
                
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
                
            except Exception as e:
                st.error(f"Error: {e}")

# 8. DESCARGA
if st.session_state.codigo:
    reporte = f"Sesión: {s_sel}\nCódigo: {st.session_state.codigo}\n\n"
    for m in st.session_state.messages:
        reporte += f"{m['role'].upper()}: {m['content']}\n\n"
    st.download_button("📥 Descargar Evidencia", reporte, file_name="Evidencia.txt")
