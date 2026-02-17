import streamlit as st
import google.generativeai as genai
import random
from PyPDF2 import PdfReader

st.set_page_config(page_title="Tutor de análisis crítico de lectura", layout="wide")

# CONFIGURACIÓN API
if "GOOGLE_API_KEY" in st.secrets:
# LÍNEA 10 CORREGIDA:
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("Error: Configure la API Key en los Secrets.")
    st.stop()

# MATRIZ ACADÉMICA COMPLETA (Curso -> Actividad -> Sesión -> Lista de archivos)
CONFIG = {
    "Historia 1": {
        "Actividad 1": {"Sesión 1": ["documentos/Historia_1/Act_1/Sesion_1/f1.pdf", "documentos/Historia_1/Act_1/Sesion_1/f2.pdf", "documentos/Historia_1/Act_1/Sesion_1/f3.pdf"]},
        "Actividad 2": {"Sesión 2": ["documentos/Historia_1/Act_2/Sesion_2/f1.pdf", "documentos/Historia_1/Act_2/Sesion_2/f2.pdf"]},
        "Actividad 3": {"Sesión 3": ["documentos/Historia_1/Act_3/Sesion_3/f1.pdf"]},
    },
    "Historia 2": {
        "Actividad 1": {
            "Sesión 1": ["documentos/Historia_2/Act_1/Sesion_1/f1.pdf", "documentos/Historia_2/Act_1/Sesion_1/f2.pdf"],
            "Sesión 2": ["documentos/Historia_2/Act_1/Sesion_2/f1.pdf", "documentos/Historia_2/Act_1/Sesion_2/f2.pdf"]
        },
        "Actividad 2": {
            "Sesión 3": ["documentos/Historia_2/Act_2/Sesion_3/f1.pdf", "documentos/Historia_2/Act_2/Sesion_3/f2.pdf"],
            "Sesión 4": ["documentos/Historia_2/Act_2/Sesion_4/f1.pdf", "documentos/Historia_2/Act_2/Sesion_4/f2.pdf"]
        },
        "Actividad 3": {
            "Sesión 5": ["documentos/Historia_2/Act_3/Sesion_5/f1.pdf", "documentos/Historia_2/Act_3/Sesion_5/f2.pdf"]
        }
    },
    "POT": {
        "Actividad 1": {
            "Sesión 1": ["documentos/POT/Act_1/Sesion_1/f1.pdf"],
            "Sesión 2": ["documentos/POT/Act_1/Sesion_2/f1.pdf"],
            "Sesión 3": ["documentos/POT/Act_1/Sesion_3/f1.pdf"]
        },
        "Actividad 2": {
            "Sesión 4": ["documentos/POT/Act_2/Sesion_4/f1.pdf"],
            "Sesión 5": ["documentos/POT/Act_2/Sesion_5/f1.pdf"]
        },
        "Actividad 3": {
            "Sesión 6": ["documentos/POT/Act_3/Sesion_6/f1.pdf"],
            "Sesión 7": ["documentos/POT/Act_3/Sesion_7/f1.pdf"]
        }
    }
}

def extraer_texto_multiple(lista_rutas):
    texto_total = ""
    for ruta in lista_rutas:
        try:
            reader = PdfReader(ruta)
            for page in reader.pages:
                texto_total += page.extract_text()
        except: continue
    return texto_total if texto_total else None

# INTERFAZ DE SELECCIÓN
with st.sidebar:
    st.title("🎓 Control Académico")
    c_sel = st.selectbox("Curso:", list(CONFIG.keys()))
    a_sel = st.selectbox("Actividad:", list(CONFIG[c_sel].keys()))
    s_sel = st.selectbox("Sesión:", list(CONFIG[c_sel][a_sel].keys()))
    
    if st.button("🗑️ Reiniciar Sesión"):
        st.session_state.messages = []; st.session_state.codigo = None; st.rerun()

# LÓGICA DEL ASISTENTE
texto_contexto = extraer_texto_multiple(CONFIG[c_sel][a_sel][s_sel])

if not texto_contexto:
    st.error("⚠️ No se pudieron cargar los archivos de esta sesión.")
    st.stop()

PROMPT = f"Eres un 'Tutor de análisis crítico de lectura'. Curso: {c_sel}, {a_sel}, {s_sel}. Texto: {texto_contexto}. REGLA: No des respuestas, solo preguntas socráticas. Usa 'COMPLETADO' para cerrar."

st.title(f"💬 {c_sel} - {s_sel}")

if "messages" not in st.session_state: st.session_state.messages = []
if "codigo" not in st.session_state: st.session_state.codigo = None

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Escribe tu análisis aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): 
        st.markdown(prompt)

# LÍNEA 95 ACTUALIZADA:
model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=PROMPT)
        
        # LÍNEA 95: Traducción de roles (assistant -> model) para Google
        historial_google = []
        for m in st.session_state.messages:
            rol_corregido = "model" if m["role"] == "assistant" else "user"
            historial_google.append({"role": rol_corregido, "parts": [m["content"]]})
        
        try:
            # Generación de respuesta con el historial traducido
            response = model.generate_content(historial_google)
            res = response.text
            
            # Lógica para otorgar el código de validación final
            if "completado" in res.lower() and not st.session_state.codigo:
                st.session_state.codigo = f"[AC-{random.randint(1000, 9999)}]"
                res += f"\n\n ✅ **ANÁLISIS COMPLETADO. Código:** {st.session_state.codigo}"
            
            # Mostrar la respuesta en pantalla y guardarla
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            
        except Exception as e:
            st.error(f"Error de conexión con la IA: {e}")
            st.info("Si el error es 404, verifica tu API Key en los 'Secrets' de Streamlit.")

# --- ÚLTIMA PARTE: BOTÓN DE DESCARGA (SIN SANGRÍA) ---
if st.session_state.codigo:
    # Construcción del reporte de texto
    reporte = f"Tutor de Análisis Crítico\nCurso: {c_sel} | {s_sel}\nCódigo: {st.session_state.codigo}\n\n"
    for m in st.session_state.messages:
        reporte += f"{m['role'].upper()}: {m['content']}\n\n"
    
    st.download_button(
        label="📥 Descargar Evidencia de Aprendizaje",
        data=reporte,
        file_name=f"Analisis_{s_sel}.txt",
        mime="text/plain"
    )

