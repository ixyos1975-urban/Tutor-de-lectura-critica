# WORKFLOWS.md

## Propósito

Este documento define los procedimientos operativos mínimos que deben seguirse para intervenir el **Tutor de Lectura Crítica**.

Los workflows no reemplazan el criterio humano ni las reglas del proyecto. Sirven para que tareas recurrentes sigan una secuencia consistente y verificable.

---

# 1. Protocolo de entrada de tareas

## WF-01 — Task Intake / Nueva necesidad

### Entrada mínima del profesor

Toda nueva tarea debe partir, cuando sea posible, de estos cinco campos:

1. **Problema observado:** qué está ocurriendo.
2. **Resultado esperado:** qué debería ocurrir.
3. **Ejemplo o evidencia:** dónde se observa.
4. **Qué debe preservarse:** qué comportamiento no debe perderse.
5. **Prioridad:** baja, media o alta.

### Transformación a Task Specification

ChatGPT debe convertir esa entrada en una especificación breve:

- `TASK-ID`
- `TYPE`
- `RISK`
- `PROBLEM`
- `EXPECTED_RESULT`
- `PRESERVE`
- `ACCEPTANCE_CRITERIA`
- `TECHNICAL_HYPOTHESIS`
- `HUMAN_REVIEW_REQUIRED`

La hipótesis técnica es provisional hasta contrastarla con el repositorio.

### Tipos de tarea

- `BUG`
- `FEATURE`
- `PEDAGOGY`
- `REFACTOR`
- `INTEGRATION`
- `LLM`
- `DOCUMENTATION`
- `CONFIG`

### Niveles de riesgo

#### LOW
Documentación, erratas, etiquetas, textos menores o cambios visuales localizados.

#### MEDIUM
Funcionalidades, RAG, persistencia, estado de sesión o integraciones de alcance controlado.

#### HIGH
Pedagogía, evaluación, aprobación, arquitectura, seguridad, datos sensibles o cambio de proveedor LLM.

Las tareas `HIGH` requieren revisión humana antes de `DONE`.

---

# 2. Selección del workflow

ChatGPT propone el workflow inicial según el tipo de tarea.

Codex debe confirmarlo o corregirlo después de inspeccionar el repositorio.

## Mapeo inicial

| TYPE | Workflow |
|---|---|
| BUG | `WF-02` |
| FEATURE | `WF-03` |
| PEDAGOGY | `WF-03` + validación pedagógica |
| REFACTOR | `WF-05` |
| INTEGRATION | `WF-02` o `WF-03` |
| LLM | `WF-04` |
| DOCUMENTATION | workflow ligero |
| CONFIG | workflow ligero + validación técnica |

Antes de implementar debe existir un Execution Contract con:

- workflow seleccionado;
- nivel de riesgo;
- rules aplicables;
- decisions relevantes;
- guardrails aplicables;
- criterios de aceptación;
- tests requeridos;
- nivel de revisión humana.

---

# 3. WF-02 — Corrección de bug

## Objetivo

Corregir un comportamiento que debería funcionar y no funciona como se espera.

## Procedimiento

1. Registrar comportamiento esperado.
2. Registrar comportamiento observado.
3. Reunir evidencia disponible: mensaje, captura, pasos o logs.
4. Intentar reproducir el problema cuando sea posible.
5. Inspeccionar el componente afectado y sus dependencias.
6. Revisar Rules y Decisions relevantes.
7. Formular o confirmar la causa técnica.
8. Aplicar la corrección mínima necesaria.
9. Ejecutar validaciones técnicas y funcionales aplicables.
10. Comprobar regresiones relacionadas.
11. Ejecutar Pre/Post Harness Impact Check.
12. Actualizar el Harness si corresponde.
13. Generar Completion Report.
14. Registrar resultado en `LOG.md`.

## Salida posible

- `DONE`
- `DONE_WITH_NOTES`
- `READY_FOR_REVIEW`
- `BLOCKED`
- `FAILED`

---

# 4. WF-03 — Nueva funcionalidad o cambio pedagógico

## Objetivo

Introducir una nueva capacidad o modificar un comportamiento existente.

## Procedimiento

1. Formalizar necesidad y resultado esperado.
2. Identificar impacto funcional y, si aplica, pedagógico.
3. Revisar Rules, Decisions y Guardrails relevantes.
4. Definir criterios de aceptación.
5. Ejecutar Pre-Harness Impact Check.
6. Inspeccionar repositorio y confirmar o corregir la hipótesis técnica.
7. Identificar componentes afectados.
8. Implementar el cambio mínimo necesario.
9. Ejecutar tests técnicos.
10. Ejecutar tests funcionales.
11. Si afecta pedagogía, ejecutar smoke tests pedagógicos aplicables.
12. Ejecutar Post-Harness Impact Check.
13. Actualizar Harness cuando corresponda.
14. Ejecutar Definition of Done.
15. Si el riesgo es HIGH, devolver `READY_FOR_REVIEW`.
16. Registrar resultado en `LOG.md`.

## Regla adicional para pedagogía

Un cambio pedagógico no puede cerrarse como `DONE` únicamente porque los tests técnicos pasen.

---

# 5. WF-04 — Cambio de proveedor o modelo LLM

## Objetivo

Cambiar proveedor, modelo o integración principal del LLM sin perder funcionalidad ni intención pedagógica.

## Procedimiento

1. Registrar motivo del cambio.
2. Revisar `DECISIONS.md` y decisiones históricas relacionadas.
3. Clasificar la tarea como `HIGH`.
4. Revisar compatibilidad de API:
   - endpoint;
   - autenticación;
   - formato de mensajes;
   - respuesta;
   - errores;
   - límites;
   - costos.
5. Revisar configuración y secretos.
6. Buscar referencias específicas al proveedor anterior.
7. Identificar acoplamientos innecesarios.
8. Implementar la migración con cambio mínimo razonable.
9. Ejecutar tests técnicos.
10. Ejecutar prueba de integración real solo cuando sea necesaria.
11. Ejecutar smoke tests pedagógicos.
12. Revisar política de manejo de errores.
13. Ejecutar Harness Impact Check.
14. Actualizar Context, Decisions y Validation cuando corresponda.
15. Devolver `READY_FOR_REVIEW`.
16. Requerir validación humana antes de `DONE`.

## Costo operativo

No realizar llamadas reales al LLM cuando la tarea pueda validarse sin consumir API.

---

# 6. WF-05 — Refactorización controlada

## Objetivo

Cambiar estructura interna manteniendo el comportamiento esperado.

## Procedimiento

1. Definir problema estructural.
2. Identificar qué comportamiento debe permanecer idéntico.
3. Clasificar riesgo.
4. Revisar arquitectura y decisiones previas.
5. Ejecutar tests disponibles antes de modificar.
6. Ejecutar Pre-Harness Impact Check.
7. Aplicar refactorización en pasos pequeños.
8. Ejecutar los mismos tests después.
9. Comparar comportamiento antes/después.
10. Revisar regresiones.
11. Ejecutar Post-Harness Impact Check.
12. Crear Decision Record si cambia arquitectura relevante.
13. Requerir revisión humana para cambios arquitectónicos `HIGH`.
14. Registrar resultado.

## Guardrail

No iniciar una refactorización estructural dentro de un bugfix puntual salvo autorización explícita.

---

# 7. WF-06 — Validación y cierre de tarea

## Objetivo

Determinar si una intervención puede cerrarse.

## Procedimiento

1. Confirmar objetivo original.
2. Confirmar archivos modificados.
3. Ejecutar validaciones automáticas aplicables.
4. Ejecutar validaciones asistidas.
5. Revisar Guardrails.
6. Ejecutar Definition of Done.
7. Ejecutar Post-Harness Impact Check.
8. Actualizar Harness si corresponde.
9. Clasificar estado final.
10. Generar Completion Report.
11. Registrar en `LOG.md`.

## Regla de cierre por riesgo

### LOW
Puede llegar a `DONE` con validación automática suficiente.

### MEDIUM
Requiere validación automática + asistida; revisión humana cuando el caso lo justifique.

### HIGH
No puede alcanzar `DONE` sin revisión humana explícita.

---

# 8. WF-07 — Mantenimiento del Harness

## Objetivo

Mantener sincronizado el Harness con el estado real del Tutor.

## Procedimiento

1. Ejecutar Harness Impact Check.
2. Identificar qué documentos pueden estar afectados:
   - Context;
   - Rules;
   - Decisions;
   - Workflows;
   - Validation;
   - Log.
3. Clasificar el cambio:
   - técnico;
   - pedagógico;
   - estratégico.
4. Actualizar documentación técnica permitida.
5. Proponer cambios normativos si corresponde.
6. Requerir revisión humana cuando afecta:
   - reglas pedagógicas;
   - guardrails;
   - decisiones estratégicas;
   - arquitectura de alto impacto.
7. Comprobar consistencia entre código, contexto, decisiones, reglas y tests.
8. Registrar actualización.

## Harness Impact Check

### PRE-IMPACT
Antes de implementar:

- ¿puede cambiar Context?
- ¿puede cambiar Rules?
- ¿puede requerir Decision Record?
- ¿puede cambiar Workflow?
- ¿puede requerir nuevos tests?

### POST-IMPACT
Después de implementar:

- ¿qué cambió realmente?
- ¿qué documentación quedó obsoleta?
- ¿qué nueva decisión apareció?
- ¿qué comportamiento merece un test permanente?

---

# 9. WF-CTX-01 — Inconsistencia de contexto

## Objetivo

Resolver contradicciones entre documentación, decisiones, reglas, configuración y repositorio.

## Procedimiento

1. Detectar la contradicción.
2. Identificar las fuentes involucradas.
3. Clasificarla como:
   - `STALE_DOCUMENTATION`;
   - `TECHNICAL_INCONSISTENCY`;
   - `RULE_VIOLATION`.
4. Consultar Decision Records relevantes.
5. Inspeccionar repositorio y configuración real.
6. Determinar la fuente de autoridad según el dominio.
7. Resolver automáticamente solo si la contradicción es inequívoca y de bajo riesgo.
8. Bloquear o escalar si afecta una decisión estratégica o pedagógica.
9. Actualizar documentación si corresponde.
10. Registrar la resolución.

---

# 10. Workflow ligero — Documentation / Config

Para tareas `LOW` de documentación o configuración menor:

1. Confirmar alcance.
2. Verificar fuente de autoridad.
3. Aplicar cambio mínimo.
4. Revisar diff.
5. Ejecutar validación pertinente.
6. Ejecutar Harness Impact Check.
7. Registrar solo si la tarea es significativa.

---

# 11. Completion Report estándar

Toda tarea significativa debe terminar con:

## TASK
- ID
- tipo
- riesgo
- objetivo

## IMPLEMENTATION
Resumen breve de lo realizado.

## FILES_CHANGED
Archivos modificados y motivo.

## VALIDATION
Tests o checks ejecutados con:
- `PASS`
- `FAIL`
- `REVIEW`
- `NOT_APPLICABLE`

## GUARDRAIL_CHECK
Guardrails relevantes y estado.

## HARNESS_IMPACT
- `NONE`
- `CONTEXT`
- `RULE`
- `DECISION`
- `WORKFLOW`
- `VALIDATION`
- `MULTIPLE`

## KNOWN_LIMITATIONS
Limitaciones o incertidumbres relevantes.

## STATUS
- `DONE`
- `DONE_WITH_NOTES`
- `READY_FOR_REVIEW`
- `BLOCKED`
- `FAILED`

## HUMAN_REVIEW
Indicar:
- `YES/NO`
- razón;
- qué debe revisar específicamente el profesor.

---

# 12. Principios de operación

- El Harness es infraestructura, no un agente autónomo.
- ChatGPT propone clasificación y workflow.
- Codex confirma o corrige después de inspeccionar el repositorio.
- El repositorio confirma la realidad técnica.
- Las Rules definen el comportamiento esperado.
- Las tareas HIGH permanecen bajo control humano.
- La complejidad del workflow debe ser proporcional al riesgo.
