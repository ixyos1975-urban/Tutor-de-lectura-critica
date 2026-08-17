# VALIDATION.md

## Propósito

Este documento define cómo se valida una intervención sobre el **Tutor de Lectura Crítica**.

La validación se organiza en tres niveles:

- **A — Automática:** comprobaciones determinísticas o rutinarias.
- **B — Asistida:** revisión razonada por Codex/LLM sobre Rules, Guardrails, alcance y regresiones.
- **C — Humana:** validación pedagógica, estratégica, arquitectónica o sensible.

La cantidad de validación debe ser proporcional al riesgo de la tarea.

---

# 1. Estados de validación

Cada check o test puede devolver:

- `PASS`
- `FAIL`
- `REVIEW`
- `NOT_APPLICABLE`

Una tarea no puede ocultar un `FAIL` ni convertir automáticamente un `REVIEW` en `PASS`.

---

# 2. Nivel A — Validaciones automáticas

## AUTO-01 — Sintaxis Python

Verificar que los archivos Python modificados tengan sintaxis válida.

Resultado esperado:
`PASS`

---

## AUTO-02 — Imports y referencias básicas

Comprobar:

- imports rotos;
- módulos inexistentes;
- referencias evidentemente inválidas introducidas por el cambio.

---

## AUTO-03 — Archivos y rutas críticas

Cuando la tarea afecte rutas, documentos o RAG, verificar existencia y coherencia de:

- `documentos/`;
- `rag_store/`;
- archivos PDF referenciados;
- rutas configuradas;
- archivos de configuración afectados.

---

## AUTO-04 — Diff Scope Check

Revisar:

- qué archivos fueron modificados;
- si existen cambios fuera del alcance;
- si una dependencia adicional fue realmente necesaria.

Relacionados:
`RULE-TEC-03`, `RULE-TEC-04`, `GRD-02`, `GRD-03`.

---

## AUTO-05 — Referencias obsoletas o inconsistentes

Cuando una tarea afecte un componente tecnológico, buscar referencias potencialmente desactualizadas.

Ejemplo para LLM:

- Gemini;
- DeepSeek;
- imports específicos del proveedor;
- nombres de modelos;
- endpoints o adaptadores.

No eliminar referencias históricas automáticamente.

---

## AUTO-06 — Configuración y secretos

Verificar:

- coherencia de variables esperadas;
- configuración referenciada;
- ausencia de secretos escritos directamente en código o documentación;
- uso correcto de variables de entorno o secretos configurados.

No mostrar valores secretos en logs.

---

## AUTO-07 — Tests existentes

Si el repositorio contiene tests aplicables:

1. ejecutarlos;
2. registrar resultado;
3. no declarar `DONE` si falla un test obligatorio.

---

# 3. Validaciones automáticas por componente

## TEST-INT-RAG-01 — Recuperación RAG básica

Aplicar cuando la tarea afecte RAG, documentos o carga de índices.

Comprobar:

1. documento accesible;
2. índice accesible o reconstruible según diseño vigente;
3. recuperación devuelve contenido no vacío;
4. no se rompe la persistencia existente.

Resultado:
`PASS / FAIL / REVIEW`

---

## TEST-INT-LLM-01 — Integración LLM

Aplicar cuando la tarea afecte directamente proveedor, modelo, endpoint o capa de llamadas al LLM.

Comprobar:

1. configuración disponible;
2. autenticación válida;
3. solicitud correctamente formada;
4. respuesta interpretable;
5. manejo de error compatible con el proveedor;
6. sin exponer secretos.

### Política de costo

No realizar llamadas reales al LLM si la tarea puede validarse sin consumir API.

Cuando se realicen llamadas:

- indicar cuántas;
- indicar su finalidad;
- evitar pruebas redundantes.

---

## TEST-INT-DATA-01 — Persistencia

Aplicar cuando la tarea afecte persistencia.

En v0.1:

- validar estructura e integración;
- evitar escrituras automáticas innecesarias sobre datos académicos de producción;
- requerir revisión humana si se modifica comportamiento sobre datos sensibles o registros reales.

---

## TEST-GOV-AUTO-01 — Decisión académica automatizada de alto impacto

Aplicar cuando una evaluación, aprobación, calificación, bloqueo u otra decisión automatizada produzca un efecto académico relevante.

Comprobar como mínimo:

1. existencia de política o criterio explícito que autorice y delimite la automatización;
2. trazabilidad del evento, entradas relevantes y resultado automatizado;
3. identificación concreta de la consecuencia producida;
4. posibilidad efectiva de revisión humana;
5. intervención humana obligatoria cuando la decisión sea crítica, sancionatoria, excepcional o controvertida.

Resultado:
`PASS / FAIL / REVIEW`

Relacionados:
`GRD-04`, `RULE-PRO-09`, `HUMAN-01`.

---

## TEST-GOV-ADV-01 — Acción adversa derivada de inferencia automatizada

Aplicar cuando una inferencia automatizada, incluida `[ALERTA_IA]`, pueda reducir intentos, bloquear acceso, invalidar una actividad, afectar una calificación o producir otra consecuencia académica adversa.

Comprobar como mínimo:

1. existencia de política o criterio explícito para la inferencia y la acción asociada;
2. trazabilidad del evento y de la inferencia que lo originó;
3. consecuencia exacta producida o prevista;
4. mecanismo accesible de revisión humana;
5. ausencia de una sanción irreversible basada únicamente en inferencia LLM.

Si la acción produce una consecuencia académica adversa, clasificar la tarea o cambio como `HIGH` y exigir revisión humana.

Resultado:
`PASS / FAIL / REVIEW`

Relacionados:
`GRD-07`, `RULE-PRO-09`, `HUMAN-01`, `HUMAN-04`.

---

# 4. Nivel B — Validación asistida

## ASSIST-01 — Rule Check

Para cada Rule aplicable indicar:

- `PASS`
- `POSSIBLE_CONFLICT`
- `NOT_APPLICABLE`

No declarar cumplimiento sin relacionarlo con el cambio realizado.

---

## ASSIST-02 — Guardrail Check

Revisar explícitamente los Guardrails aplicables.

Si existe duda razonable:

`REVIEW`

Si existe violación clara:

`FAIL`

---

## ASSIST-03 — Regresión funcional preliminar

Identificar componentes, funciones o flujos dependientes de lo modificado y revisar si el cambio puede afectarlos.

Cuando exista test reproducible, ejecutarlo.

Cuando no exista, registrar la limitación.

---

## ASSIST-04 — Harness Consistency Check

Comparar:

- `CONTEXT.md`;
- `RULES.md`;
- `DECISIONS.md`;
- `WORKFLOWS.md`;
- `VALIDATION.md`;
- repositorio real.

Clasificar inconsistencias como:

- `STALE_DOCUMENTATION`
- `TECHNICAL_INCONSISTENCY`
- `RULE_VIOLATION`

---

# 5. Smoke tests pedagógicos mínimos

Estos tests no buscan coincidencia textual exacta. Evalúan propiedades del comportamiento del Tutor.

## TEST-PED-01 — Respuesta superficial

### Escenario
El estudiante ofrece una afirmación general, débil o insuficientemente desarrollada.

### Esperado
El Tutor debe:

- pedir precisión;
- solicitar mayor argumentación;
- pedir evidencia textual cuando corresponda;
- evitar aprobación prematura.

### Falla si
- acepta la respuesta como suficiente;
- construye directamente el argumento por el estudiante.

---

## TEST-PED-02 — Solicitud directa de respuesta

### Escenario
El estudiante pide explícitamente que el Tutor entregue la respuesta correcta o el análisis final.

### Esperado
El Tutor debe:

- evitar entregar la respuesta sustitutiva;
- devolver la responsabilidad intelectual al estudiante;
- orientar mediante pregunta, contraste o pista.

### Falla si
Entrega directamente el análisis que corresponde al estudiante.

---

## TEST-PED-03 — Argumentación sin evidencia

### Escenario
El estudiante formula una interpretación plausible pero no la vincula con la lectura.

### Esperado
El Tutor debe solicitar:

- evidencia;
- concepto;
- fragmento;
- relación explícita con el texto.

### Falla si
Aprueba sin sustento o descarta automáticamente una interpretación razonable.

---

## TEST-PED-04 — Interpretación alternativa defendible

### Escenario
El estudiante presenta una lectura distinta a la esperada, pero argumentada y sustentable.

### Esperado
El Tutor debe:

- explorar la argumentación;
- pedir sustentación;
- admitir pluralidad interpretativa cuando tenga fundamento.

### Falla si
Fuerza una única respuesta predeterminada.

---

## TEST-PED-05 — Lenguaje sofisticado, razonamiento débil

### Escenario
Respuesta con vocabulario académico elaborado, pero conceptualmente vaga.

### Esperado
El Tutor debe valorar argumento, coherencia y evidencia.

### Falla si
Interpreta automáticamente lenguaje sofisticado como comprensión suficiente.

---

## TEST-PED-06 — Respuesta breve pero sólida

### Escenario
Respuesta relativamente corta, pertinente, argumentada y vinculada al texto.

### Esperado
Reconocer calidad conceptual sin exigir extensión innecesaria.

### Falla si
Confunde longitud con calidad.

---

## TEST-PED-07 — Aprobación prematura

### Escenario
El estudiante responde adecuadamente una parte del diálogo, pero el proceso todavía no demuestra suficiente análisis crítico.

### Esperado
Continuar la interacción antes de emitir aprobación global.

### Falla si
Se activa `[DICTAMEN_APROBADO]` por una respuesta aislada.

---

## TEST-PED-08 — Error o contradicción del estudiante

### Escenario
El estudiante formula una interpretación débil, incorrecta o contradictoria.

### Esperado
El Tutor debe:

- señalar el problema mediante preguntas o contraste;
- utilizar evidencia cuando corresponda;
- promover reformulación.

### Falla si
Responde únicamente con una corrección sustitutiva del tipo “la respuesta correcta es...”.

---

# 6. Smoke tests pedagógicos frecuentes

Para cambios pedagógicos ordinarios, ejecutar como mínimo:

- `TEST-PED-01`
- `TEST-PED-02`
- `TEST-PED-03`
- `TEST-PED-07`

Los demás se ejecutan cuando el cambio o el riesgo lo justifique.

Las tareas pedagógicas `HIGH` no se cierran automáticamente aunque estos tests den `PASS`.

---

# 7. Nivel C — Revisión humana obligatoria

Requerir revisión humana cuando la tarea afecte:

## HUMAN-01 — Pedagogía

- interacción socrática;
- criterios de profundidad;
- aprobación;
- evaluación;
- retroalimentación;
- comportamiento ante errores;
- uso pedagógico de evidencia.

## HUMAN-02 — Arquitectura

- refactorización estructural significativa;
- cambio de persistencia;
- cambio de arquitectura RAG;
- nuevos servicios o dependencias estructurales.

## HUMAN-03 — Proveedor LLM

- cambio de proveedor;
- cambio con impacto sustancial en comportamiento, costo o dependencia tecnológica.

## HUMAN-04 — Seguridad y datos sensibles

- autenticación;
- permisos;
- secretos;
- registros académicos sensibles;
- cambios importantes en persistencia.

## HUMAN-05 — Experiencia real

- fluidez del diálogo;
- frustración;
- claridad;
- equilibrio entre exigencia y acompañamiento.

---

# 8. Clasificación de riesgo y validación requerida

## LOW

Requiere:

- validación automática aplicable;
- diff scope;
- Definition of Done.

Puede llegar a `DONE` sin revisión humana.

---

## MEDIUM

Requiere:

- validación automática;
- validación asistida;
- revisión humana si aparece `REVIEW`, riesgo funcional relevante o impacto no previsto.

---

## HIGH

Requiere:

- validación automática;
- validación asistida;
- revisión humana obligatoria.

Estado máximo antes de revisión humana:

`READY_FOR_REVIEW`

También se clasifican como `HIGH` los cambios que permitan consecuencias académicas adversas derivadas de inferencias automatizadas.

---

# 9. Definition of Done general

Una tarea se considera terminada únicamente cuando cumple todos los criterios aplicables.

## DOD-01
La necesidad original está identificada.

## DOD-02
El resultado esperado y criterios de aceptación están definidos.

## DOD-03
Los componentes y archivos afectados fueron identificados.

## DOD-04
Se revisaron Rules, Decisions y Guardrails relevantes.

## DOD-05
Se implementó únicamente el cambio necesario.

## DOD-06
No se modificaron componentes ajenos sin justificación.

## DOD-07
Las verificaciones técnicas aplicables fueron ejecutadas.

## DOD-08
Las funcionalidades relacionadas siguen funcionando.

## DOD-09
Las integraciones externas afectadas fueron verificadas cuando corresponde.

## DOD-10
Los tests pedagógicos aplicables fueron ejecutados cuando corresponde.

## DOD-11
No existen regresiones conocidas sin documentar.

## DOD-12
Los archivos modificados quedaron identificados.

## DOD-13
Las pruebas ejecutadas y sus resultados quedaron registradas.

## DOD-14
Incidencias, limitaciones y pendientes fueron documentados.

## DOD-15
La revisión humana fue realizada cuando el riesgo o naturaleza de la tarea la exige.

## DOD-16 — Harness Consistency
Cuando existe impacto arquitectónico, pedagógico o estratégico, se comprobó que el Harness sigue siendo consistente con el estado final del proyecto.

## DOD-17 — Decision Capture
Las decisiones relevantes surgidas durante la tarea fueron registradas antes del cierre.

---

# 10. Definition of Done pedagógica

Aplicar cuando la intervención afecte comportamiento pedagógico.

## DOD-PED-01
El Tutor sigue requiriendo participación intelectual del estudiante.

## DOD-PED-02
No entrega una respuesta sustitutiva cuando debería guiar.

## DOD-PED-03
Solicita sustentación ante afirmaciones insuficientes.

## DOD-PED-04
Utiliza evidencia documental cuando sea pertinente.

## DOD-PED-05
No confunde estilo o extensión con comprensión.

## DOD-PED-06
No activa aprobación prematuramente.

## DOD-PED-07
La retroalimentación es comprensible y orientada a mejora.

## DOD-PED-08
El comportamiento nuevo no contradice las Rules pedagógicas.

## DOD-PED-09
Los casos de alto impacto fueron revisados por el profesor.

---

# 11. Estados finales de tarea

## DONE
Todos los criterios obligatorios fueron satisfechos.

## DONE_WITH_NOTES
La tarea cumple criterios principales y existen limitaciones documentadas que no impiden el cierre.

## READY_FOR_REVIEW
La implementación y validación preliminar terminaron, pero la tarea requiere revisión humana antes de `DONE`.

## BLOCKED
Existe una dependencia, inconsistencia o requisito externo que impide continuar.

## FAILED
La solución no satisface criterios de aceptación o introduce una regresión no aceptable.

---

# 12. Política de costo LLM

## TEST-OPS-01 — Uso justificado del LLM

No generar llamadas a DeepSeek u otro proveedor para validar tareas que no necesitan inferencia del modelo.

Cuando se realicen llamadas de prueba:

- deben responder a una necesidad de validación;
- deben ser las mínimas necesarias;
- debe registrarse su propósito;
- evitar repetirlas sin una razón técnica o pedagógica.

---

# 13. Completion Gate

Antes de declarar una tarea cerrada, confirmar:

1. ¿Se ejecutaron los tests obligatorios?
2. ¿Existe algún `FAIL`?
3. ¿Existe algún `REVIEW` sin resolver?
4. ¿Se respetaron Guardrails?
5. ¿Se realizó Harness Impact Check?
6. ¿Se actualizó el Harness si correspondía?
7. ¿La tarea requiere revisión humana?
8. ¿La Definition of Done está satisfecha?

Si alguna respuesta obligatoria es negativa, no declarar `DONE`.
