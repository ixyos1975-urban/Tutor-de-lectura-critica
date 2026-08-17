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
