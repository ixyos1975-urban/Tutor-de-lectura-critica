# config.py

APP_TITLE = "Tutor de Análisis Crítico"
APP_LAYOUT = "wide"

# Control académico
MAX_INTENTOS = 3

# Tiempos de inactividad (en segundos)
TIMEOUT_NORMAL = 600       # 10 minutos
TIMEOUT_SATURACION = 1200  # 20 minutos
AVISO_TIEMPO = 300         # 5 minutos

# Modelos Gemini
MODEL_MAIN = "models/gemini-flash-latest"
MODEL_EVAL = "models/gemini-flash-latest"
EMBEDDING_MODEL = "models/embedding-001"

# Parámetros RAG
# Ajuste intermedio: reduce consumo sin fragmentar demasiado el sentido del texto.
CHUNK_SIZE = 750
CHUNK_OVERLAP = 150
TOP_K = 3

# Dominio institucional permitido
DOMINIO_PERMITIDO = "@unisalle.edu.co"

# Optimización de consumo de tokens
# Solo se enviarán a la API los últimos N mensajes del historial.
# El historial completo sigue guardado en session_state para pantalla y reporte.
MAX_HISTORIAL = 8

# Límite de salida del tutor.
# Un tutor socrático debe responder con preguntas y observaciones breves.
MAX_OUTPUT_TOKENS = 350
