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

---

## EXP-MED-001

**Fecha:** 2026-08-17
**Tipo:** `BUG`
**Riesgo:** `MEDIUM`

### Objetivo
Corregir las rutas inválidas del catálogo `PRUEBA` para que resuelvan los PDF existentes sin afectar otros catálogos ni el motor RAG.

### Archivos modificados
- `catalogo.py` → alinear únicamente las rutas de `Demo_1.pdf` y `Demo_2.pdf` con la estructura real.
- `harness/CONTEXT.md` → retirar la limitación del catálogo `PRUEBA` después de resolverla.
- `harness/LOG.md` → registrar la tarea experimental.

### Rules / Guardrails aplicados
- `RULE-TEC-01`, `RULE-TEC-02`, `RULE-TEC-03`, `RULE-TEC-04`
- `RULE-PRO-04`, `RULE-PRO-07`, `RULE-PRO-08`, `RULE-PRO-10`
- `GRD-02`, `GRD-03`

### Decisions consultadas o creadas
- `DEC-001` y `DEC-002` consultadas.
- Ninguna decisión creada.

### Workflow
- `WF-02`

### Validación
- Reproducción previa → `PASS`; 2 de 24 rutas no resolvían, ambas en `PRUEBA`.
- `AUTO-01` → `PASS`; importación de `catalogo.py` válida.
- `AUTO-02` → `PASS`; estructura `CONFIG` accesible.
- `AUTO-03` → `PASS`; las 24 rutas catalogadas resuelven archivos existentes.
- `AUTO-04` → `PASS`; cambio funcional limitado al catálogo `PRUEBA`.
- `ASSIST-01` → `PASS`.
- `ASSIST-02` → `PASS`.
- `ASSIST-03` → `PASS`; los otros 22 documentos y catálogos conservan sus rutas válidas.
- `ASSIST-04` → `PASS`; se retiró del Context la limitación ya resuelta.
- `TEST-INT-RAG-01` → `NOT_APPLICABLE`; no cambió el motor RAG y la precondición de acceso documental quedó verificada por `AUTO-03`.
- Diff check → `PASS`.
- Llamadas API → ninguna.

### Harness Impact
`CONTEXT`

### Actualización del Harness
- `harness/CONTEXT.md` actualizado para no conservar como limitación un bug ya resuelto.
- `harness/LOG.md` actualizado como registro operativo.

### Limitaciones / incidencias
- No se ejecutó recuperación RAG end-to-end porque la tarea no modificó esa integración y prohíbe llamadas API.
- El repositorio no contiene una suite automatizada de tests.

### Revisión humana
- Requerida: `NO`
- Resultado: `NOT_APPLICABLE`.
- Observación: tarea `MEDIUM` localizada, con validación automática y asistida sin resultados `REVIEW` ni impacto pedagógico.

### Estado final
`DONE`

---

## HARNESS-CAL-002

**Fecha:** 2026-08-17
**Tipo:** `PEDAGOGY / GOVERNANCE`
**Riesgo:** `HIGH`

### Objetivo
Recalibrar la gobernanza de `[ALERTA_IA]` a partir de `EXP-HIGH-001` y de la decisión humana sobre escalabilidad, autonomía operativa y revisión por excepción.

### Archivos modificados
- `harness/RULES.md` → recalibrar `GRD-07`.
- `harness/DECISIONS.md` → crear `DEC-007`.
- `harness/VALIDATION.md` → recalibrar `TEST-GOV-ADV-01`.
- `harness/LOG.md` → registrar la calibración.

### Rules / Guardrails aplicados
- `RULE-TEC-03`, `RULE-TEC-04`, `RULE-PRO-06`, `RULE-PRO-08`, `RULE-PRO-09`
- `GRD-02`, `GRD-03`, `GRD-04`, `GRD-06`, `GRD-07`

### Decisions consultadas o creadas
- `DEC-007` creada con estado `VIGENTE`.
- Estado de implementación: `PENDIENTE DE ADECUACIÓN DEL FLUJO ACTUAL`.

### Workflow
- `WF-03`
- `WF-07`

### Validación
- `AUTO-04` → `PASS`; cambios limitados a los cuatro archivos autorizados.
- `AUTO-05` → `PASS`; referencias internas verificadas.
- Coherencia `GRD-07` / `DEC-007` / `TEST-GOV-ADV-01` → `PASS`.
- Preservación de `GRD-04` → `PASS`.
- Ausencia de revisión humana previa obligatoria por evento → `PASS`.
- Inferencia LLM no presentada como prueba infalible ni libre de sesgos → `PASS`.
- Código funcional sin modificaciones → `PASS`.
- `ASSIST-01` → `REVIEW`; cambio normativo pendiente de aprobación humana.
- `ASSIST-02` → `REVIEW`; guardrail pendiente de aprobación humana.
- `ASSIST-04` → `PASS`.
- Llamadas API → ninguna.

### Harness Impact
`MULTIPLE`

### Actualización del Harness
- Rules, Decisions, Validation y Log.

### Limitaciones / incidencias
- El flujo funcional actual de `[ALERTA_IA]` no fue modificado y permanece pendiente de adecuación y validación frente a la política recalibrada.
- `EXP-HIGH-001` se conserva como evidencia histórica de origen.

### Revisión humana
- Requerida: `YES`
- Resultado: `APPROVED`.
- Observación: el profesor aprobó `GRD-07`, `DEC-007` y `TEST-GOV-ADV-01` con una precisión de redacción. Las tareas o modificaciones `HIGH` del sistema requieren revisión humana antes de su cierre; los eventos operativos individuales se someten a revisión humana por excepción conforme a `GRD-07` y `DEC-007`.

### Estado final
`DONE`
