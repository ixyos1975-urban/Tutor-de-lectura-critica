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
# Se fijan modelos explícitos para evitar depender de alias "latest".
MODEL_MAIN = "gemini-2.5-flash"
MODEL_EVAL = "gemini-2.5-flash"

# Modelo de embeddings actualizado
EMBEDDING_MODEL = "models/gemini-embedding-001"

# Parámetros RAG
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 3

# Dominio institucional permitido
DOMINIO_PERMITIDO = "@unisalle.edu.co"
