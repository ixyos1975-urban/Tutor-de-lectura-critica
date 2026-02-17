import streamlit as st
import google.generativeai as genai
import random
from PyPDF2 import PdfReader

st.set_page_config(page_title="Tutor de análisis crítico de lectura", layout="wide")

# CONFIGURACIÓN API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
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

if prompt := st.chat_input("Escribe tu análisis..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        model = genai.GenerativeModel('models/gemini-1.5-flash', system_instruction=PROMPT)
        historial = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]} for m in st.session_state.messages]
res = model.generate_content(historial).text
        if "completado" in res.lower() and not st.session_state.codigo:
            st.session_state.codigo = f"[AC-{random.randint(1000, 9999)}]"
            res += f"\n\n✅ **VALIDADO. Código:** {st.session_state.codigo}"
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})

if st.session_state.codigo:
    rep = f"Reporte: {c_sel} - {a_sel} - {s_sel}\nCódigo: {st.session_state.codigo}\n\n"
    for m in st.session_state.messages: rep += f"{m['role'].upper()}: {m['content']}\n\n"
    st.download_button("📥 Descargar Evidencia", rep, file_name=f"Analisis_{s_sel}.txt")
