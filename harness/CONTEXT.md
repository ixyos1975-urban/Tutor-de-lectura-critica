# CONTEXT.md

## 1. Propósito del proyecto

El **Tutor de Lectura Crítica** es una aplicación académica orientada a acompañar a estudiantes universitarios en procesos de lectura, interpretación, argumentación y pensamiento crítico.

La función del Tutor no es producir la respuesta académica en lugar del estudiante. Debe favorecer la construcción autónoma del razonamiento mediante preguntas, contraste, sustentación y uso pertinente de evidencia textual.

## 2. Usuarios y roles

### Estudiante
Interactúa con el Tutor a partir de lecturas académicas y desarrolla su propio análisis.

### Profesor
Define el propósito pedagógico, prioriza necesidades, valida cambios de alto impacto y conserva la decisión final sobre criterios pedagógicos y evaluativos.

### ChatGPT
Apoya la formalización de necesidades, la traducción entre intención pedagógica y requisito funcional, y la estructuración del trabajo de desarrollo.

### Codex
Inspecciona el repositorio, confirma o corrige hipótesis técnicas, implementa cambios, ejecuta verificaciones y reporta resultados dentro de los límites definidos por el Harness.

## 3. Arquitectura técnica observada en el repositorio público

La rama pública `main` consultada contiene actualmente:

- `app.py`: orquestación principal de la aplicación Streamlit, sesión, persistencia, RAG, interacción con el LLM y evaluación.
- `config.py`: parámetros generales de la aplicación, control académico, tiempos, modelos y parámetros RAG.
- `catalogo.py`: estructura académica de asignaturas, actividades, sesiones y lecturas.
- `prompts.py`: construcción de instrucciones pedagógicas y de evaluación.
- `documentos/`: corpus académico en PDF.
- `rag_store/`: almacenamiento de índices RAG persistidos.
- `requirements.txt`: dependencias Python.
- `README.md`: documentación general del proyecto.

La aplicación utiliza Streamlit y Python. La persistencia académica observada se apoya en Google Sheets mediante `gspread`. El estado temporal se maneja mediante `st.session_state`.

## 4. Arquitectura pedagógica

El Tutor debe conservar como principios centrales:

- promover razonamiento autónomo;
- evitar respuestas sustitutivas;
- pedir sustentación cuando una afirmación sea insuficiente;
- mantener relación con evidencia textual cuando sea pertinente;
- no confundir extensión o lenguaje sofisticado con comprensión;
- evitar aprobación prematura;
- mantener el juicio pedagógico final bajo responsabilidad docente.

Las reglas operativas detalladas se mantienen en `RULES.md`.

## 5. RAG

El sistema utiliza recuperación aumentada por generación (RAG) para conectar la interacción con documentos académicos.

Conceptualmente:

`PDF → fragmentación → embeddings → Chroma → recuperación → contexto para el Tutor`

La recuperación documental cumple una función pedagógica además de técnica: mantener la argumentación vinculada con las lecturas de referencia.

Las decisiones históricas sobre persistencia y conservación del RAG deben consultarse en `DECISIONS.md`.

## 6. Proveedor LLM: estado y discrepancia actual

### Decisión vigente del proyecto
El proveedor LLM vigente definido por el proyecto es **DeepSeek**, adoptado por razones de reducción de costos operativos.

### Estado observado en la rama pública consultada
La rama pública `main` consultada todavía contiene referencias operativas a **Google Gemini**, incluyendo:

- importación y configuración de `google.generativeai` en `app.py`;
- uso de `GoogleGenerativeAIEmbeddings`;
- constantes de modelos Gemini en `config.py`;
- referencias a Gemini en el `README.md`.

Por tanto, existe una discrepancia entre la **decisión vigente del proyecto** y el **estado técnico observado en el repositorio público**.

### Clasificación provisional
`TECHNICAL_INCONSISTENCY / STALE_DOCUMENTATION`

Antes de cualquier intervención relacionada con el LLM debe verificarse cuál es el repositorio o rama realmente desplegada y sincronizar este contexto con la implementación efectiva.

No asumir que Gemini sigue siendo el proveedor vigente solo porque aparece en la rama pública, ni asumir que DeepSeek ya está implementado en esa rama sin verificar el código real.

## 7. Configuración operativa

Los valores técnicos concretos deben obtenerse del código y del entorno vigente, no duplicarse en este archivo.

Fuentes técnicas:

- `config.py`;
- variables de entorno;
- secretos de Streamlit;
- configuración efectiva del despliegue.

Este archivo describe la arquitectura y el estado conceptual; no reemplaza la configuración ejecutable.

## 8. Modelo de desarrollo actual

El proceso de desarrollo se estructura conceptualmente así:

`Profesor → ChatGPT → Task Specification → Codex → repositorio → validación → revisión humana cuando aplica`

El Harness funciona como infraestructura de conocimiento y control; no es un agente autónomo.

## 9. Fuentes de autoridad

La autoridad depende del dominio:

- propósito y comportamiento pedagógico: `RULES.md`;
- implementación técnica efectiva: repositorio;
- configuración real: código + entorno + secrets;
- motivos y elecciones históricas: `DECISIONS.md`;
- procedimiento: `AGENTS.md` + `WORKFLOWS.md`;
- pruebas y Definition of Done: `VALIDATION.md`;
- historia técnica: Git;
- historia operativa: `LOG.md`.

## 10. Regla de contraste

`CONTEXT.md` orienta; el repositorio muestra la realidad técnica.

Antes de cualquier modificación, Codex debe inspeccionar el estado real del código y reportar contradicciones relevantes entre este contexto, las decisiones, las reglas y la implementación.

## 11. Limitaciones conocidas del estado actual

- Parte importante de la orquestación sigue concentrada en `app.py`.
- La validación funcional y pedagógica todavía depende en buena medida de pruebas humanas.
- El repositorio público consultado presenta una discrepancia respecto del proveedor LLM vigente reportado para el proyecto.
- El Harness v0.1 está en construcción; algunos documentos referenciados por `AGENTS.md` aún pueden no existir hasta completar el Hito 5.

## 12. Estado del Harness

**Versión:** 0.1 — construcción inicial.

**Fase actual:** materialización de la arquitectura TO-BE definida y auditada previamente.

**Última revisión conceptual:** 2026-08-16.
