import streamlit as st
import google.generativeai as genai
import random
import os
from PyPDF2 import PdfReader

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tutor de Análisis Crítico", layout="wide")

# 2. CONEXIÓN API
if "GOOGLE_API_KEY" in st.secrets:
    # Usamos transport='rest' para forzar una conexión más estable en la nube
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

# 3. RUTAS DE DOCUMENTOS (Verifica que estos nombres existan en tus carpetas de GitHub)
CONFIG = {
    "Historia 1": {
        "Actividad 1": {
            "Sesión 1": ["documentos/Historia_1/Act_1/Sesion_1/f1.pdf"]
        }
    }
}

# 4. MOTOR DE LECTURA DE PDF
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

# 5. MENÚ LATERAL (SIDEBAR)
with st.sidebar:
    st.title("📂 Menú de Tutoría")
    c_sel = st.selectbox("Curso", list(CONFIG.keys()))
    a_sel = st.selectbox("Actividad", list(CONFIG[c_sel].keys()))
    s_sel = st.selectbox("Sesión", list(CONFIG[c_sel][a_sel].keys()))
    
    st.divider()
    if st.button("🔄 Reiniciar Chat"):
        st.session_state.messages = []
        st.session_state.codigo = None
        st.rerun()
    
    # AYUDA PARA APRENDER: Esto muestra qué versión está usando el servidor
    import google.generativeai as _genai
    st.caption(f"Versión de librería instalada: {_genai.__version__}")

# 6. CONFIGURACIÓN DEL TUTOR
texto_referencia = leer_pdf(CONFIG[c_sel][a_sel][s_sel])

PROMPT_SISTEMA = f"""Eres un Tutor Socrático experto. No des respuestas, haz preguntas.
Texto de referencia: {texto_referencia}
Si el alumno demuestra un análisis excelente, usa la palabra 'COMPLETADO'."""

st.title(f"💬 Sesión: {s_sel}")

# Memoria del chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "codigo" not in st.session_state:
    st.session_state.codigo = None

# Mostrar historial
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 7. INTERACCIÓN (Entrada y respuesta)
if prompt := st.chat_input("Escribe tu análisis aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Usamos el nombre de modelo más estándar
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=PROMPT_SISTEMA)
            
            # Traducción de roles: assistant -> model
            historial = []
            for m in st.session_state.messages:
                r = "model" if m["role"] == "assistant" else "user"
                historial.append({"role": r, "parts": [m["content"]]})
            
            # Llamada a la IA
            response = model.generate_content(historial)
            res = response.text
            
            if "completado" in res.lower() and not st.session_state.codigo:
                st.session_state.codigo = f"[AC-{random.randint(1000, 9999)}]"
                res += f"\n\n ✅ **VALIDADO.** Código: {st.session_state.codigo}"
            
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            
        except Exception as e:
            st.error(f"Error de conexión con la IA: {e}")

# 8. BOTÓN DE DESCARGA
if st.session_state.codigo:
    reporte = f"Sesión: {s_sel}\nCódigo: {st.session_state.codigo}\n\n"
    for m in st.session_state.messages:
        reporte += f"{m['role'].upper()}: {m['content']}\n\n"
    st.download_button("📥 Descargar Reporte", reporte, file_name=f"Resultado.txt")
