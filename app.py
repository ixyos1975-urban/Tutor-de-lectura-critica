import streamlit as st
import google.generativeai as genai
import random
import os
from PyPDF2 import PdfReader

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tutor de Análisis Crítico", layout="wide")

# 2. CONEXIÓN API (Sin 'transport=rest' para probar el protocolo estándar)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ No se encontró la API Key en Streamlit Secrets.")
    st.stop()

# 3. CONFIGURACIÓN DE RUTAS (Asegúrate de que coincidan con tus carpetas en GitHub)
CONFIG = {
    "Historia 1": {
        "Actividad 1": {
            "Sesión 1": ["documentos/Historia_1/Act_1/Sesion_1/f1.pdf"]
        }
    }
}

# 4. MOTOR DE LECTURA DE PDF
def leer_contenido_pdf(rutas):
    texto = ""
    for r in rutas:
        if os.path.exists(r):
            try:
                lector = PdfReader(r)
                for pagina in lector.pages:
                    texto += pagina.extract_text() + "\n"
            except:
                continue
    return texto

# 5. MENÚ LATERAL
with st.sidebar:
    st.title("📂 Navegación")
    curso = st.selectbox("Curso", list(CONFIG.keys()))
    actividad = st.selectbox("Actividad", list(CONFIG[curso].keys()))
    sesion = st.selectbox("Sesión", list(CONFIG[curso][actividad].keys()))
    
    st.divider()
    if st.button("🗑️ Reiniciar Chat"):
        st.session_state.messages = []
        st.session_state.codigo = None
        st.rerun()

# 6. CARGA DE CONTEXTO
material = leer_contenido_pdf(CONFIG[curso][actividad][sesion])

# Instrucciones para la IA
PROMPT_SISTEMA = f"""Eres un Tutor Socrático. 
Tu material de referencia es: {material}
REGLAS:
- Nunca des respuestas directas.
- Haz preguntas que inviten a la reflexión.
- Usa la palabra 'COMPLETADO' solo si el análisis es profundo."""

st.title(f"💬 Sesión: {sesion}")

# Inicialización de memoria
if "messages" not in st.session_state:
    st.session_state.messages = []
if "codigo" not in st.session_state:
    st.session_state.codigo = None

# Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. FLUJO DE CHAT (Entrada y Respuesta)
if prompt_usuario := st.chat_input("Escribe tu análisis aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)

    with st.chat_message("assistant"):
        try:
            # AJUSTE CRÍTICO: Usamos el nombre completo del modelo 'models/gemini-1.5-flash'
            model = genai.GenerativeModel(
                model_name='models/gemini-1.5-flash', 
                system_instruction=PROMPT_SISTEMA
            )
            
            # Traducimos roles para Google (assistant -> model)
            history = []
            for m in st.session_state.messages:
                role = "model" if m["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [m["content"]]})
            
            # Llamada a la API
            respuesta = model.generate_content(history)
            texto_ia = respuesta.text
            
            # Lógica de validación
            if "completado" in texto_ia.lower() and not st.session_state.codigo:
                st.session_state.codigo = f"[EXITO-{random.randint(100, 999)}]"
                texto_ia += f"\n\n✅ **SESIÓN FINALIZADA.** Código: {st.session_state.codigo}"
            
            st.markdown(texto_ia)
            st.session_state.messages.append({"role": "assistant", "content": texto_ia})
            
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            st.info("Sugerencia: Si el error 404 persiste, intenta generar una nueva API Key en Google AI Studio.")

# 8. BOTÓN DE DESCARGA
if st.session_state.codigo:
    reporte = f"Evidencia de Tutoría\nSesión: {sesion}\nCódigo: {st.session_state.codigo}\n\n"
    for m in st.session_state.messages:
        reporte += f"{m['role'].upper()}: {m['content']}\n\n"
    st.download_button("📥 Descargar Reporte", reporte, file_name=f"Resultado_{sesion}.txt")
