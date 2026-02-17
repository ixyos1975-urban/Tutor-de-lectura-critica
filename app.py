import streamlit as st
import google.generativeai as genai
import random
import os
from PyPDF2 import PdfReader

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tutor - Diagnóstico", layout="wide")

# 2. CONEXIÓN Y DIAGNÓSTICO (Esto es nuevo)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

# --- BARRA LATERAL CON PRUEBA DE CONEXIÓN ---
with st.sidebar:
    st.header("🔧 Diagnóstico de Conexión")
    if st.button("Verificar Modelos Disponibles"):
        try:
            st.info("Consultando a Google...")
            # Preguntamos a la API qué modelos ve esta llave
            modelos = genai.list_models()
            nombres = [m.name for m in modelos if 'generateContent' in m.supported_generation_methods]
            
            if nombres:
                st.success(f"¡Conexión Exitosa! Se encontraron {len(nombres)} modelos.")
                st.code("\n".join(nombres), language="text")
            else:
                st.warning("La llave funciona, pero no tiene acceso a modelos de chat.")
        except Exception as e:
            st.error(f"❌ Error grave con la llave: {e}")
            st.markdown("**Solución:** Tu API Key podría estar bloqueada o mal copiada. Crea una nueva en Google AI Studio.")

    st.divider()
    
    # MENÚ DE NAVEGACIÓN NORMAL
    st.title("📂 Navegación")
    # Configuración básica de carpetas (Solo como ejemplo para que no falle)
    CONFIG = {"Historia 1": {"Actividad 1": {"Sesión 1": ["documentos/Historia_1/Act_1/Sesion_1/f1.pdf"]}}}
    
    c_sel = st.selectbox("Curso", list(CONFIG.keys()))
    a_sel = st.selectbox("Actividad", list(CONFIG[c_sel].keys()))
    s_sel = st.selectbox("Sesión", list(CONFIG[c_sel][a_sel].keys()))

# 3. LECTURA DE PDF
def leer_pdf(rutas):
    texto = ""
    for r in rutas:
        if os.path.exists(r):
            try:
                lector = PdfReader(r)
                for p in lector.pages: texto += p.extract_text() + "\n"
            except: continue
    return texto

texto_referencia = leer_pdf(CONFIG[c_sel][a_sel][s_sel])

# 4. CHAT (Usando el nombre más específico posible)
st.title(f"💬 Sesión: {s_sel}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Escribe algo para probar..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # INTENTO 1: Usamos la versión específica '001' que suele ser más estable
            nombre_modelo = 'gemini-1.5-flash-001'
            
            model = genai.GenerativeModel(nombre_modelo)
            
            # Historial simple
            chat = model.start_chat(history=[])
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Falló con '{nombre_modelo}'. Error: {e}")
            st.info("👆 Usa el botón de Diagnóstico en la izquierda para ver qué nombre de modelo debemos poner aquí.")
