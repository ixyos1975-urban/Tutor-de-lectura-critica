# RULES.md

## Propósito

Este documento reúne las reglas y guardrails que deben respetarse al modificar el **Tutor de Lectura Crítica**.

Las reglas describen comportamientos obligatorios. Los guardrails establecen límites que no deben cruzarse sin revisión o autorización humana.

---

# 1. Reglas pedagógicas

## RULE-PED-01 — Promover razonamiento autónomo

El Tutor debe favorecer que el estudiante construya su propio razonamiento, interpretación y argumentación.

## RULE-PED-02 — No sustituir al estudiante

El Tutor no debe producir de manera sustitutiva el análisis, respuesta final o argumento que corresponde desarrollar al estudiante.

## RULE-PED-03 — Exigir sustentación pertinente

Cuando una afirmación sea superficial, insuficiente o poco sustentada, el Tutor debe solicitar precisión, argumentación y/o evidencia textual antes de validar el avance.

## RULE-PED-04 — Preservar la intención pedagógica

Una optimización técnica, económica o de rendimiento no debe degradar la intención pedagógica del Tutor.

## RULE-PED-05 — No confundir forma con comprensión

La calidad de una respuesta no debe inferirse únicamente por su longitud, vocabulario sofisticado o estilo académico.

## RULE-PED-06 — Evitar aprobación prematura

La aprobación no debe activarse por una respuesta aislada si todavía no existe evidencia suficiente de análisis crítico, argumentación o comprensión.

---

# 2. Reglas técnicas

## RULE-TEC-01 — Inspeccionar antes de modificar

Codex debe inspeccionar el estado real del repositorio antes de realizar una modificación.

## RULE-TEC-02 — Verificar hipótesis técnicas

Toda hipótesis técnica formulada durante la conversación debe considerarse provisional hasta contrastarla con el código, la configuración o el entorno real.

## RULE-TEC-03 — Aplicar el cambio mínimo necesario

La intervención debe resolver la necesidad identificada con el menor alcance razonable.

## RULE-TEC-04 — Preservar funcionalidades no relacionadas

Los componentes y comportamientos fuera del alcance de la tarea deben mantenerse sin cambios, salvo dependencia necesaria y explícitamente reportada.

## RULE-TEC-05 — No duplicar configuración ejecutable

Los valores técnicos vigentes deben obtenerse de sus fuentes ejecutables (`config.py`, entorno y secretos) y no duplicarse innecesariamente en documentación.

## RULE-TEC-06 — No exponer secretos

Credenciales, claves API y otros secretos no deben escribirse directamente en el código, documentación o logs.

---

# 3. Reglas de proceso

## RULE-PRO-01 — Partir de una necesidad observable

Toda modificación debe poder vincularse con un problema, necesidad o resultado esperado identificable.

## RULE-PRO-02 — Separar necesidad, requisito y solución

Debe distinguirse explícitamente entre:

- necesidad observada;
- requisito funcional;
- hipótesis o solución técnica.

## RULE-PRO-03 — Definir criterios de aceptación

Toda tarea debe establecer qué condiciones deben cumplirse para considerarla satisfactoria.

## RULE-PRO-04 — Verificar antes de cerrar

Una tarea no debe declararse terminada únicamente porque el código compile o porque el cambio haya sido implementado.

## RULE-PRO-05 — Cumplir la Definition of Done

Una tarea no puede declararse `DONE` si existe un criterio obligatorio de la Definition of Done sin verificar.

## RULE-PRO-06 — Conservar decisiones históricas

Una decisión relevante que deje de aplicarse debe marcarse como reemplazada o revocada; no debe eliminarse del historial.

## RULE-PRO-07 — Contrastar contexto y repositorio

Antes de intervenir, el agente debe consultar el contexto canónico y contrastarlo con el estado real del repositorio.

## RULE-PRO-08 — Registrar evidencia de cierre

Todo workflow de modificación debe terminar con una verificación documentada y un registro operativo.

## RULE-PRO-09 — Risk-Gated Completion

Las tareas clasificadas como `HIGH` no pueden alcanzar el estado `DONE` sin validación humana explícita.

## RULE-PRO-10 — Context orienta; repositorio confirma

`CONTEXT.md` orienta al agente, pero la realidad técnica vigente debe confirmarse mediante inspección del repositorio y configuración efectiva.

---

# 4. Guardrails

## GRD-01 — No degradar pedagogía por optimización

No eliminar, simplificar o desactivar una función con impacto pedagógico únicamente para reducir costos, tokens, tiempo de ejecución o complejidad técnica sin revisión humana.

## GRD-02 — No modificar fuera del alcance

Codex no debe modificar componentes no relacionados con la tarea salvo que exista una dependencia necesaria y sea reportada explícitamente.

## GRD-03 — No realizar refactorizaciones no solicitadas

Una corrección puntual no debe utilizarse como oportunidad para realizar refactorizaciones estructurales no solicitadas.

## GRD-04 — Automatización académica y juicio humano

Las evaluaciones, retroalimentaciones y registros automatizados pueden operar cuando estén explícitamente previstos por el diseño pedagógico, tengan criterios identificables y conserven trazabilidad suficiente.

Las decisiones académicas críticas, sancionatorias, excepcionales o controvertidas no deben quedar resueltas únicamente por una inferencia automatizada. Estos casos requieren posibilidad efectiva de revisión humana y deben mantener bajo responsabilidad del profesor el juicio pedagógico final.

## GRD-05 — Evitar acoplamiento innecesario al proveedor LLM

La lógica pedagógica y de negocio del Tutor no debe quedar innecesariamente acoplada a un proveedor LLM concreto cuando sea posible mantener una separación razonable.

## GRD-06 — No autoautorizar cambios normativos

Un agente no puede modificar una Rule o Guardrail con el propósito de hacer aceptable una implementación que originalmente los incumplía.

Si una implementación entra en conflicto con una regla normativa:

1. marcar `FAIL` o `REVIEW`;
2. escalar a revisión humana;
3. solo modificar la regla si existe una decisión humana explícita que cambie el criterio.

## GRD-07 — Protección ante acciones adversas automatizadas

Una inferencia automatizada, incluida la detección de posible uso de IA, no debe producir por sí sola una consecuencia académica adversa irreversible sin política explícita, trazabilidad y posibilidad de revisión humana.

---

# 5. Autoridad normativa

Las reglas pedagógicas y guardrails tienen prioridad sobre una implementación que accidentalmente los contradiga.

Si el código vigente viola una regla:

- no reinterpretar la regla para justificar el código;
- clasificar la situación como `RULE_VIOLATION`;
- corregir la implementación o solicitar revisión humana.

---

# 6. Criterio de aplicación

No todas las reglas se aplican a todas las tareas.

Cada tarea debe identificar explícitamente:

- reglas aplicables;
- guardrails aplicables;
- reglas no aplicables cuando sea relevante.

El Completion Report debe registrar conflictos o revisiones pendientes.
