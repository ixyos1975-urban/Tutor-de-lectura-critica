# LOG.md

## Propósito

Este documento registra la historia operativa de tareas significativas realizadas sobre el **Tutor de Lectura Crítica**.

No reemplaza Git ni duplica diffs. Su función es conservar, de manera breve y trazable:

- qué tarea se realizó;
- con qué nivel de riesgo;
- qué archivos fueron afectados;
- qué validaciones se ejecutaron;
- qué impacto tuvo sobre el Harness;
- qué decisiones se crearon o actualizaron;
- cuál fue el estado final;
- si existió revisión humana.

---

# 1. Formato estándar de registro

## TASK-ID

**Fecha:**  
**Tipo:**  
**Riesgo:** `LOW / MEDIUM / HIGH`

### Objetivo
Descripción breve de la necesidad y resultado esperado.

### Archivos modificados
- archivo → motivo
- archivo → motivo

### Rules / Guardrails aplicados
- `RULE-*`
- `GRD-*`

### Decisions consultadas o creadas
- `DEC-*`

### Workflow
- `WF-*`

### Validación
- `TEST-*` → `PASS / FAIL / REVIEW / NOT_APPLICABLE`
- `AUTO-*` → resultado
- `ASSIST-*` → resultado

### Harness Impact
- `NONE`
- `CONTEXT`
- `RULE`
- `DECISION`
- `WORKFLOW`
- `VALIDATION`
- `MULTIPLE`

### Actualización del Harness
Indicar archivos actualizados, si aplica.

### Limitaciones / incidencias
Registrar únicamente información útil para trabajo futuro.

### Revisión humana
- Requerida: `YES / NO`
- Resultado:
- Observación:

### Estado final
- `DONE`
- `DONE_WITH_NOTES`
- `READY_FOR_REVIEW`
- `BLOCKED`
- `FAILED`

---

# 2. Principios de uso

1. No copiar diffs completos.
2. No reproducir logs técnicos extensos si Git o la herramienta ya los conserva.
3. No almacenar secretos, claves API ni datos sensibles.
4. Registrar tareas significativas y decisiones reutilizables.
5. Una tarea `HIGH` debe registrar la revisión humana antes de quedar `DONE`.
6. Si una tarea genera una nueva decisión, registrar también su `DEC-*`.
7. Si una tarea detecta una inconsistencia relevante, registrar su clasificación:
   - `STALE_DOCUMENTATION`
   - `TECHNICAL_INCONSISTENCY`
   - `RULE_VIOLATION`
8. Mantener cada entrada breve y orientada a trazabilidad.

---

# 3. Registro inicial del Harness

## TASK-HARNESS-001

**Fecha:** 2026-08-16  
**Tipo:** `DOCUMENTATION / ARCHITECTURE`  
**Riesgo:** `HIGH`

### Objetivo
Materializar la versión inicial del Harness v0.1 para el Tutor de Lectura Crítica a partir de la arquitectura TO-BE definida y auditada previamente.

### Archivos creados
- `AGENTS.md` → puerta de entrada persistente para Codex.
- `harness/CONTEXT.md` → contexto canónico y fuentes de autoridad.
- `harness/RULES.md` → reglas pedagógicas, técnicas, de proceso y guardrails.
- `harness/DECISIONS.md` → decisiones relevantes y su justificación.
- `harness/WORKFLOWS.md` → protocolos operativos y selección de workflows.
- `harness/VALIDATION.md` → validaciones, tests, DoD y criterios de cierre.
- `harness/LOG.md` → trazabilidad operativa.

### Decisions consultadas o creadas
- `DEC-001` a `DEC-006`.

### Hallazgo relevante
Existe una discrepancia entre la decisión vigente de utilizar DeepSeek y las referencias todavía visibles a Gemini en la rama pública consultada.

### Clasificación
`TECHNICAL_INCONSISTENCY / STALE_DOCUMENTATION`

### Harness Impact
`MULTIPLE`

### Revisión humana
- Requerida: `YES`
- Resultado: pendiente de revisión final del paquete v0.1.

### Estado final
`READY_FOR_REVIEW`

---

## BOOTSTRAP-001

**Fecha:** 2026-08-17
**Tipo:** `DOCUMENTATION / VALIDATION`
**Riesgo:** `HIGH`

### Objetivo
Comprobar que el Harness v0.1 puede leerse, aplicarse y contrastarse con el estado real del repositorio sin modificar el proyecto.

### Archivos modificados
- Ninguno.

### Rules / Guardrails aplicados
- `RULE-TEC-01`, `RULE-TEC-02`, `RULE-PRO-07`, `RULE-PRO-10`
- `GRD-02`, `GRD-03`

### Decisions consultadas o creadas
- `DEC-001` a `DEC-006` consultadas.
- Ninguna decisión creada.

### Workflow
- `WF-CTX-01`

### Validación
- Harness readability → `PASS`
- Repository inspection → `PASS`
- Rule traceability → `PASS`
- Decision traceability → `PASS`
- Drift detection → `PASS`
- Non-modification control → `PASS`
- Harness calibration needed → `YES`

### Harness Impact
`NONE`

### Limitaciones / incidencias
- Se detectaron desalineaciones documentales, normativas y técnicas que requieren calibración y revisión humana.

### Revisión humana
- Requerida: `YES`
- Resultado: pendiente.
- Observación: revisar la calibración normativa derivada de los hallazgos.

### Estado final
`REVIEW_REQUIRED`

---

## HARNESS-CAL-001

**Fecha:** 2026-08-17
**Tipo:** `DOCUMENTATION / HARNESS CALIBRATION`
**Riesgo:** `HIGH`

### Objetivo
Calibrar el Harness v0.1 a partir de la evidencia de `BOOTSTRAP-001`, sin modificar el código ni la configuración funcional del Tutor.

### Archivos modificados
- `harness/CONTEXT.md` → actualizar el mapa canónico y registrar el estado observado.
- `harness/RULES.md` → delimitar la automatización académica y proteger frente a acciones adversas automatizadas.
- `harness/DECISIONS.md` → registrar el estado de implementación pendiente de `DEC-006`.
- `harness/VALIDATION.md` → añadir validaciones de decisiones automatizadas de alto impacto y acciones adversas.
- `harness/LOG.md` → registrar `BOOTSTRAP-001` y esta calibración.

### Rules / Guardrails aplicados
- `RULE-TEC-02`, `RULE-TEC-03`, `RULE-TEC-04`, `RULE-PRO-06`, `RULE-PRO-07`, `RULE-PRO-08`, `RULE-PRO-09`
- `GRD-02`, `GRD-03`, `GRD-04`, `GRD-06`, `GRD-07`

### Decisions consultadas o creadas
- `DEC-001` a `DEC-006` consultadas.
- `DEC-006` complementada sin cambiar su estado `VIGENTE`.

### Workflow
- `WF-07`
- `WF-CTX-01`

### Validación
- `AUTO-04` → `PASS`; el diff contiene únicamente los cinco archivos autorizados dentro de `harness/`.
- `AUTO-05` → `PASS`; referencias internas de identificadores y rutas comprobadas.
- `ASSIST-01` → `REVIEW`
- `ASSIST-02` → `REVIEW`
- `ASSIST-04` → `PASS`

### Harness Impact
`MULTIPLE`

### Actualización del Harness
- Context, Rules, Decisions, Validation y Log.

### Limitaciones / incidencias
- No se corrigió la discrepancia de rutas del catálogo `PRUEBA`.
- No se implementó DeepSeek.
- No se modificaron `[DICTAMEN_APROBADO]`, `[ALERTA_IA]` ni el código del Tutor.

### Revisión humana
- Requerida: `YES`
- Resultado: `APPROVED`.
- Observación: el profesor aprobó `GRD-04`, `GRD-07`, `TEST-GOV-AUTO-01`, `TEST-GOV-ADV-01` y la actualización de `DEC-006`. La revisión humana no implica aprobación docente previa de toda automatización académica ordinaria; es obligatoria cuando la decisión sea crítica, sancionatoria, excepcional, controvertida o produzca una consecuencia académica adversa relevante.

### Estado final
`DONE`

---

## EXP-LOW-001

**Fecha:** 2026-08-17
**Tipo:** `DOCUMENTATION`
**Riesgo:** `LOW`

### Objetivo
Sincronizar la referencia del modelo LLM en `README.md` con la configuración ejecutable vigente del checkout.

### Archivos modificados
- `README.md` → actualizar exclusivamente la versión documentada del modelo Gemini.
- `harness/LOG.md` → registrar la tarea experimental.

### Rules / Guardrails aplicados
- `RULE-TEC-01`, `RULE-TEC-02`, `RULE-TEC-03`, `RULE-TEC-04`, `RULE-TEC-05`
- `RULE-PRO-04`, `RULE-PRO-07`, `RULE-PRO-08`, `RULE-PRO-10`
- `GRD-02`, `GRD-03`

### Decisions consultadas o creadas
- `DEC-006` consultada; no modificada.
- Ninguna decisión creada.

### Workflow
- Workflow ligero — Documentation / Config.

### Validación
- Fuente técnica de autoridad (`config.py`) → `PASS`; `MODEL_MAIN` y `MODEL_EVAL` usan `gemini-2.5-flash`.
- Consistencia `README.md` / configuración → `PASS`.
- `AUTO-04` → `PASS`.
- `AUTO-05` → `PASS`.
- Diff check → `PASS`.
- Tests funcionales y llamadas API → `NOT_APPLICABLE`.

### Harness Impact
`NONE`

### Actualización del Harness
- Solo `harness/LOG.md` como registro operativo; sin cambios en Context, Rules, Decisions, Workflows o Validation.

### Limitaciones / incidencias
- `DEC-006` continúa vigente y pendiente de implementación; esta tarea documenta exclusivamente el modelo implementado en el checkout actual.

### Revisión humana
- Requerida: `NO`
- Resultado: `NOT_APPLICABLE`.
- Observación: tarea documental `LOW` sin impacto funcional, pedagógico o estratégico.

### Estado final
`DONE`
