import streamlit as st
import google.generativeai as genai
import random
import os
from PyPDF2 import PdfReader

# 1. CONFIGURACIÓN DE LA PÁGINA (Título en la pestaña del navegador)
st.set_page_config(page_title="Tutor de Análisis Crítico", layout="wide")

# 2. CONEXIÓN CON LA API DE GOOGLE
# Verificamos que la llave esté en los 'Secrets' de Streamlit
if "GOOGLE_API_KEY" in st.secrets:
    # Usamos transport='rest' para evitar errores de conexión 404 en la nube
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("⚠️ No se encontró la llave API. Configúrala en los Secrets de Streamlit.")
    st.stop()

# 3. ESTRUCTURA DE ARCHIVOS (Asegúrate de que estas carpetas existan en GitHub)
CONFIG = {
    "Historia 1": {
        "Actividad 1": {
            "Sesión 1": ["documentos/Historia_1/Act_1/Sesion_1/f1.pdf"]
        }
    }
}

# 4. FUNCIÓN PARA LEER EL CONTENIDO DE LOS PDFS
def extraer_texto_pdf(rutas):
    texto_total = ""
    for ruta in rutas:
        if os.path.exists(ruta):
            try:
                reader = PdfReader(ruta)
                for page in reader.pages:
                    texto_total += page.extract_text() + "\n"
            except Exception:
                continue
    return texto_total

# 5. BARRA LATERAL DE NAVEGACIÓN
with st.sidebar:
    st.title("📂 Menú de Tutoría")
    curso = st.selectbox("Curso", list(CONFIG.keys()))
    actividad = st.selectbox("Actividad", list(CONFIG[curso].keys()))
    sesion = st.selectbox("Sesión", list(CONFIG[curso][actividad].keys()))
    
    if st.button("🔄 Reiniciar Sesión"):
        st.session_state.messages = []
        st.session_state.codigo = None
        st.rerun()

# 6. CARGA DEL MATERIAL DE LECTURA
material = extraer_texto_pdf(CONFIG[curso][actividad][sesion])

# Instrucciones para que la IA se comporte como un tutor
PROMPT_SISTEMA = f"""Eres un Tutor Socrático experto en lectura crítica. 
Material de lectura: {material}
REGLAS:
1. No resuelvas las dudas directamente; haz preguntas que guíen al alumno.
2. Solo cuando el alumno haga un análisis profundo, escribe la palabra 'COMPLETADO'."""

st.title(f"💬 Sesión: {sesion}")

# Inicialización de la memoria del chat (State)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "codigo" not in st.session_state:
    st.session_state.codigo = None

# Dibujar los mensajes previos de la conversación
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 7. INTERACCIÓN (Entrada de texto del usuario)
if prompt := st.chat_input("Escribe tu reflexión aquí..."):
    # Guardar y mostrar lo que escribe el alumno
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del asistente (Solo ocurre si el usuario escribió algo)
    with st.chat_message("assistant"):
        try:
            # Usamos 'gemini-1.5-flash-latest' para evitar errores de versión
            model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=PROMPT_SISTEMA)
            
            # Traducimos los nombres de los roles (Streamlit: assistant -> Google: model)
            historial_api = []
            for m in st.session_state.messages:
                rol_google = "model" if m["role"] == "assistant" else "user"
                historial_api.append({"role": rol_google, "parts": [m["content"]]})
            
            # Pedimos la respuesta a Google
            respuesta_ia = model.generate_content(historial_api)
            texto_final = respuesta_ia.text
            
            # Si el tutor valida el análisis, generamos el código de éxito
            if "completado" in texto_final.lower() and not st.session_state.codigo:
                st.session_state.codigo = f"[AC-{random.randint(1000, 9999)}]"
                texto_final += f"\n\n ✅ **ANÁLISIS VALIDADO.** Código: {st.session_state.codigo}"
            
            st.markdown(texto_final)
            st.session_state.messages.append({"role": "assistant", "content": texto_final})
            
        except Exception as e:
            st.error(f"Error de conexión con la IA: {e}")

# 8. EXPORTACIÓN DE RESULTADOS (Se activa al finalizar)
if st.session_state.codigo:
    reporte = f"REPORTE DE EVIDENCIA\nSesión: {sesion}\nCódigo: {st.session_state.codigo}\n\n"
    for m in st.session_state.messages:
        reporte += f"{m['role'].upper()}: {m['content']}\n\n"
    
    st.download_button("📥 Descargar reporte de sesión", reporte, file_name=f"Evidencia_{sesion}.txt")
