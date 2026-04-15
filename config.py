# config.py

APP_TITLE = "Tutor de Análisis Crítico"
APP_LAYOUT = "wide"

# Control académico
MAX_INTENTOS = 3

# Tiempos de inactividad (en segundos)
TIMEOUT_NORMAL     = 600   # 10 minutos
TIMEOUT_SATURACION = 1200  # 20 minutos
AVISO_TIEMPO       = 300   # 5 minutos

# Modelos Gemini
MODEL_MAIN      = "models/gemini-flash-latest"
MODEL_EVAL      = "models/gemini-flash-latest"
EMBEDDING_MODEL = "models/embedding-001"

# Parámetros RAG
# CHUNK_SIZE reducido de 1000 → 500: cada fragmento recuperado pesa ~50% menos en tokens.
# CHUNK_OVERLAP reducido de 200 → 100: proporcional al nuevo tamaño de chunk.
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 100
TOP_K         = 3

# Dominio institucional permitido
DOMINIO_PERMITIDO = "@unisalle.edu.co"

# ── Optimización de consumo de tokens ────────────────────────────────────────
# MAX_HISTORIAL: número máximo de mensajes del historial que se envían a la API
# en cada turno. El historial completo se conserva en session_state para la
# pantalla y el reporte, pero la API solo recibe los últimos N mensajes.
# Valor 8 = 4 turnos completos (usuario + tutor), suficiente para coherencia socrática.
MAX_HISTORIAL = 8

# RAG_TURNO_LIMITE: el recuperador RAG se activa solo mientras el historial
# total tenga menos de N mensajes. Pasado ese punto el modelo ya tiene contexto
# suficiente del diálogo y el RAG solo añadiría tokens sin mejorar la calidad.
RAG_TURNO_LIMITE = 6

# MAX_OUTPUT_TOKENS: límite de tokens en la respuesta del tutor. Un tutor socrático
# debe hacer preguntas cortas, no redactar ensayos. 450 tokens ≈ 300 palabras,
# más que suficiente para una pregunta de cuestionamiento con contexto.
MAX_OUTPUT_TOKENS = 450
