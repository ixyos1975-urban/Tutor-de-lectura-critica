# AGENTS.md

## Propósito

Este repositorio corresponde al **Tutor de Lectura Crítica**, una aplicación académica orientada a acompañar procesos universitarios de lectura crítica mediante interacción guiada con IA.

Este archivo define el procedimiento mínimo que debe seguir cualquier agente de desarrollo antes de modificar el proyecto.

## Procedimiento obligatorio

Para toda tarea:

1. Leer `harness/CONTEXT.md`.
2. Leer `harness/RULES.md` cuando exista.
3. Identificar el tipo de tarea y su nivel de riesgo.
4. Consultar las decisiones relevantes en `harness/DECISIONS.md` cuando exista.
5. Seleccionar el workflow aplicable en `harness/WORKFLOWS.md` cuando exista.
6. Inspeccionar el repositorio real antes de modificar código.
7. Tratar cualquier hipótesis técnica previa como provisional hasta contrastarla con el código.
8. Aplicar el cambio mínimo necesario para resolver la necesidad.
9. No modificar componentes fuera del alcance salvo dependencia necesaria y explícitamente reportada.
10. Ejecutar las validaciones aplicables definidas en `harness/VALIDATION.md` cuando exista.
11. No declarar una tarea terminada si existe un criterio obligatorio de validación sin verificar.
12. Registrar el resultado en `harness/LOG.md` cuando exista.

## Autoridad por dominio

- **Comportamiento pedagógico esperado:** `harness/RULES.md`.
- **Implementación técnica vigente:** repositorio real.
- **Configuración operativa vigente:** código, variables de entorno y secretos configurados.
- **Motivo de decisiones relevantes:** `harness/DECISIONS.md`.
- **Procedimiento de trabajo:** este archivo y `harness/WORKFLOWS.md`.
- **Criterios de validación:** `harness/VALIDATION.md`.
- **Historia técnica:** Git.
- **Historia operativa de tareas:** `harness/LOG.md`.

Si dos fuentes se contradicen, no asumir silenciosamente cuál es correcta. Clasificar la discrepancia y reportarla antes de realizar una modificación que dependa de ella.

## Clasificación preliminar de riesgo

- **LOW:** documentación, etiquetas, erratas o cambios visuales menores.
- **MEDIUM:** funcionalidades, RAG, persistencia, estado de sesión o integraciones de alcance controlado.
- **HIGH:** pedagogía, evaluación, aprobación, arquitectura, seguridad, datos sensibles o cambio de proveedor LLM.

Las tareas `HIGH` no deben cerrarse como `DONE` sin revisión humana explícita.

## Límites

Un agente no puede:

- redefinir por su cuenta el propósito pedagógico del Tutor;
- cambiar reglas pedagógicas para justificar una implementación que las incumple;
- realizar refactorizaciones estructurales no solicitadas dentro de una corrección puntual;
- introducir secretos directamente en el código;
- asumir que una referencia histórica describe el estado técnico vigente.

## Cierre esperado

Toda intervención debe terminar con un reporte breve que incluya:

- tarea y objetivo;
- archivos modificados;
- implementación realizada;
- validaciones ejecutadas;
- comprobación de guardrails;
- limitaciones conocidas;
- impacto sobre el Harness;
- estado final (`DONE`, `DONE_WITH_NOTES`, `READY_FOR_REVIEW`, `BLOCKED` o `FAILED`).
