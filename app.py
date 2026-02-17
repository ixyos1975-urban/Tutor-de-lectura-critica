import streamlit as st
import google.generativeai as genai
import random
import os
from PyPDF2 import PdfReader

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tutor Socrático", layout="wide")

# 2. CONEXIÓN API (Usamos el canal estándar para evitar el error 404)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

# 3. RUTAS DE TUS DOCUMENTOS (Asegúrate que estas carpetas existan en GitHub)
CONFIG = {
    "Historia 1": {
        "Actividad 1": {
            "Sesión 1": ["documentos/Historia_1/Act_1/Sesion_1/f1.pdf"]
        }
    }
}

# 4. FUNCIÓN PARA LEER PDF
def leer_pdf(rutas):
    texto = ""
    for r in rutas:
        if os.path.exists(r):
            try:
                lector = PdfReader(r)
                for pagina in lector.pages:
                    texto += pagina.extract_text() + "\n"
            except: continue
    return texto

# 5. MENÚ LATERAL
with st.sidebar:
    st.title("📂 Menú")
    c_sel = st.selectbox("Curso", list(CONFIG.keys()))
    a_sel = st.selectbox("Actividad", list(CONFIG[c_sel].keys()))
    s_sel = st.selectbox("Sesión", list(CONFIG[c_sel][a_sel].keys()))
    if st.button("Reiniciar"):
        st.session_state.messages = []
        st.session_state.codigo = None
        st.rerun()

# 6. CARGAR CONTENIDO Y CONFIGURAR IA
texto_referencia = leer_pdf(CONFIG[c_sel][a_sel][s_sel])

PROMPT_SISTEMA = f"""Eres un Tutor Socrático. No des respuestas, haz preguntas.
Texto de referencia: {texto_referencia}
Si el alumno lo hace excelente, usa la palabra 'COMPLETADO'."""

st.title(f"💬 {s_sel}")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "codigo" not in st.session_state:
    st.session_state.codigo = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 7. EL CORAZÓN DEL CHAT
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Usamos el nombre de modelo más estable para evitar el error 'v1beta'
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=PROMPT_SISTEMA)
            
            # Traducimos roles: assistant -> model
            historial = []
            for m in st.session_state.messages:
                r = "model" if m["role"] == "assistant" else "user"
                historial.append({"role": r, "parts": [m["content"]]})
            
            response = model.generate_content(historial)
            res = response.text
            
            if "completado" in res.lower() and not st.session_state.codigo:
                st.session_state.codigo = f"[AC-{random.randint(1000, 9999)}]"
                res += f"\n\n ✅ **VALIDADO. Código:** {st.session_state.codigo}"
            
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            
        except Exception as e:
            st.error(f"Error de conexión: {e}")

# 8. DESCARGA
if st.session_state.codigo:
    reporte = f"Sesión: {s_sel}\nCódigo: {st.session_state.codigo}\n\n"
    for m in st.session_state.messages:
        reporte += f"{m['role'].upper()}: {m['content']}\n\n"
    st.download_button("📥 Descargar Reporte", reporte, file_name=f"Evidencia.txt")
