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

# --- AQUÍ ESTÁ EL TRUCO ANTI-PLAGIO ---
PROMPT_SISTEMA = f"""
Eres un Tutor Socrático estricto pero amable.
Tu material de referencia es ÚNICAMENTE este texto: {texto_referencia}

TUS 3 REGLAS DE ORO:
1.  **DETECCIÓN DE IA:** Si el alumno responde con definiciones genéricas, listas perfectas, o texto que parece copiado de ChatGPT, dile: "Eso suena muy generico (o artificial). Por favor, dime con tus propias palabras qué entiendes, basándote en el texto que leímos".
2.  **EVIDENCIA:** Exige que el alumno cite o parafrasee partes específicas del PDF. Si no usa el texto, pregúntale: "¿En qué parte del documento se menciona eso?".
3.  **MÉTODO SOCRÁTICO:** Nunca des la respuesta. Solo haz preguntas que guíen.

Solo escribe 'COMPLETADO' si el alumno demostró análisis propio y citó el texto correctamente.
"""

st.title(f"💬 {s_sel}")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "codigo" not in st.session_state:
    st.session_state.codigo = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 7. CHAT
if prompt := st.chat_input("Escribe tu análisis aquí..."):
    # VALIDACIÓN SIMPLE: Si pegan un texto gigante (más de 800 caracteres) de golpe, avisamos.
    if len(prompt) > 800:
        st.toast("⚠️ ¡Ups! Esa respuesta es muy larga. Intenta ser más conciso y usar tus propias palabras.", icon="🚫")
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Usamos el modelo gratuito que funcionó
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
