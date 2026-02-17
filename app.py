import streamlit as st
import google.generativeai as genai
import random
import os
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
    if st.button("🗑️ Reiniciar Conversación"):
        st.session_state.messages = []
        st.session_state.codigo = None
        st.rerun()

# 6. CARGAR CONTEXTO
texto_referencia = leer_pdf(CONFIG[c_sel][a_sel][s_sel])

# --- CEREBRO DEL TUTOR (Instrucciones Pedagógicas) ---
PROMPT_SISTEMA = f"""
Eres un Tutor Socrático de la Universidad.
Texto de referencia: {texto_referencia}

ESTRUCTURA DE LA SESIÓN (Sigue este orden estrictamente):

FASE 1: INICIO Y RESPONSABILIDAD
- Tu primera tarea es NO iniciar el análisis ni hacer preguntas del contenido todavía.
- Si el estudiante saluda ("Hola", "Buenas") o dice "Estoy listo", TÚ DEBES RESPONDER: "Bienvenido. Para comenzar, por favor propón el tema específico o la tesis del texto que deseas analizar hoy."
- Si el estudiante no propone un tema claro, insiste amablemente: "Necesito que tú definas el enfoque. ¿Qué aspecto del texto te llamó la atención?"

FASE 2: DESARROLLO (Solo cuando ya haya un tema propuesto)
- Usa el Método Socrático: haz preguntas que cuestionen lo que el alumno dice sobre SU tema elegido.
- Anti-Plagio: Si la respuesta parece de IA (listas, definiciones de diccionario), di: "Eso suena genérico. Dímelo con tus palabras y basándote en el texto".
- Evidencia: Exige citas. Pregunta: "¿En qué página o párrafo el autor menciona eso?".

FASE 3: CIERRE
- Solo escribe 'COMPLETADO' si el alumno demostró análisis profundo, citó el texto y defendió su punto.
"""

st.title(f"💬 {s_sel}")

if "messages" not in st.session_state:
    # Mensaje inicial del sistema para invitar a la acción (Opcional, pero ayuda)
    st.session_state.messages = []

if "codigo" not in st.session_state:
    st.session_state.codigo = None

# Mostrar historial
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 7. CHAT
if prompt := st.chat_input("Escribe aquí..."):
    # Filtro de longitud (Anti-Copiar/Pegar masivo)
    if len(prompt) > 800:
        st.toast("⚠️ Respuesta muy larga. Por favor, resume con tus propias palabras.", icon="🚫")
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(
                model_name='models/gemini-flash-latest', 
                system_instruction=PROMPT_SISTEMA
            )
            
            historial = []
            for m in st.session_state.messages:
                r = "model" if m["role"] == "assistant" else "user"
                historial.append({"role": r, "parts": [m["content"]]})
            
            response = model.generate_content(historial)
            res = response.text
            
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
    st.download_button("📥 Descargar", reporte, file_name="Evidencia.txt")
