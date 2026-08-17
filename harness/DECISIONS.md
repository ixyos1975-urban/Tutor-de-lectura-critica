# DECISIONS.md

## Propósito

Este documento registra decisiones relevantes del **Tutor de Lectura Crítica**.

Cada Decision Record conserva:

- qué problema se estaba resolviendo;
- qué decisión se tomó;
- por qué se tomó;
- qué alternativas se consideraron;
- qué consecuencias tiene;
- qué reglas o componentes se relacionan con ella.

Estados posibles:

- `VIGENTE`
- `REEMPLAZADA`
- `REVOCADA`

No se registran aquí correcciones menores, erratas o ajustes triviales.

---

## DEC-001 — Modularización inicial de la aplicación

**Estado:** VIGENTE

**Título:** Separar configuración, catálogo académico y prompts de `app.py`.

**Problema:**  
La aplicación concentraba demasiadas responsabilidades en `app.py`, dificultando mantenimiento, lectura y evolución.

**Decisión:**  
Separar responsabilidades en módulos dedicados:

- `config.py`: configuración general;
- `catalogo.py`: estructura académica;
- `prompts.py`: comportamiento pedagógico y evaluativo basado en prompts;
- `app.py`: orquestación principal.

**Motivo:**  
Reducir concentración de responsabilidades y facilitar cambios localizados sin alterar todo el sistema.

**Alternativas consideradas:**  
Mantener toda la lógica dentro de `app.py`.

**Consecuencias:**  
Los cambios futuros deben respetar la separación existente y evitar volver a concentrar innecesariamente configuración, catálogo o prompts dentro de `app.py`.

**Componentes afectados:**  
`app.py`, `config.py`, `catalogo.py`, `prompts.py`.

**Reglas relacionadas:**  
`RULE-TEC-03`, `RULE-TEC-04`, `GRD-03`.

---

## DEC-002 — Persistencia de índices RAG

**Estado:** VIGENTE

**Título:** Persistir y reutilizar índices RAG en `rag_store/`.

**Problema:**  
La reconstrucción repetida de índices RAG generaba tiempos de carga y procesamiento innecesarios.

**Decisión:**  
Persistir los índices y reutilizarlos cuando estén disponibles.

**Motivo:**  
Mejorar rendimiento y reducir reconstrucciones repetitivas sin alterar la función pedagógica del RAG.

**Alternativas consideradas:**  
Reconstruir índices en cada ejecución.

**Consecuencias:**  
Las modificaciones relacionadas con RAG deben comprobar compatibilidad con la persistencia existente.

**Componentes afectados:**  
RAG, `rag_store/`, carga de documentos, flujo de recuperación.

**Reglas relacionadas:**  
`RULE-PED-04`, `RULE-TEC-04`.

---

## DEC-003 — Mantener RAG durante la interacción pedagógica

**Estado:** VIGENTE

**Título:** No desactivar el RAG únicamente para reducir consumo.

**Problema:**  
Se consideró reducir el uso del RAG como estrategia para disminuir consumo de tokens y costo operativo.

**Decisión:**  
Mantener la recuperación documental cuando sea pedagógicamente pertinente.

**Motivo:**  
La fundamentación textual y la relación con las lecturas de referencia son componentes esenciales del propósito pedagógico del Tutor.

**Alternativas consideradas:**  
Desactivar o limitar el RAG después de determinado número de turnos.

**Consecuencias:**  
Las optimizaciones de costo o rendimiento no deben eliminar automáticamente la conexión con la evidencia documental.

**Componentes afectados:**  
RAG, prompts, interacción pedagógica, validación.

**Reglas relacionadas:**  
`RULE-PED-03`, `RULE-PED-04`, `GRD-01`.

---

## DEC-004 — Manejo controlado de saturación y errores de API

**Estado:** VIGENTE

**Título:** Tratar fallos temporales de API mediante reintentos controlados y recuperación segura.

**Problema:**  
Errores de cuota, saturación o rate limit podían interrumpir la experiencia del estudiante.

**Decisión:**  
Incorporar manejo explícito de errores temporales y reintentos controlados cuando corresponda.

**Motivo:**  
Evitar que una falla transitoria del proveedor destruya la sesión o obligue al estudiante a reiniciar innecesariamente.

**Alternativas consideradas:**  
Propagar el error directamente al usuario sin recuperación.

**Consecuencias:**  
Los cambios de proveedor LLM deben revisar nuevamente esta política, ya que los códigos de error y comportamiento pueden variar.

**Componentes afectados:**  
Integración LLM, manejo de errores, experiencia de usuario.

**Reglas relacionadas:**  
`RULE-TEC-04`, `RULE-PRO-04`.

---

## DEC-005 — Desarrollo con Codex mediante bloques pequeños y verificables

**Estado:** VIGENTE

**Título:** Realizar intervenciones localizadas y verificables en lugar de cambios amplios no controlados.

**Problema:**  
Las modificaciones amplias incrementan el riesgo de regresiones y dificultan identificar la causa de los fallos.

**Decisión:**  
Trabajar con Codex mediante tareas delimitadas, con inspección previa, cambio mínimo y verificación posterior.

**Motivo:**  
Mejorar trazabilidad, reducir riesgo y facilitar depuración.

**Alternativas consideradas:**  
Solicitar refactorizaciones o mejoras generales de gran alcance en una única intervención.

**Consecuencias:**  
Las tareas deben tener alcance, criterios de aceptación y validación explícitos.

**Componentes afectados:**  
Proceso de desarrollo completo.

**Reglas relacionadas:**  
`RULE-TEC-01`, `RULE-TEC-03`, `RULE-PRO-03`, `RULE-PRO-04`, `GRD-02`, `GRD-03`.

---

## DEC-006 — Adopción de DeepSeek como proveedor LLM operativo

**Estado:** VIGENTE

**Estado de implementación:** PENDIENTE EN EL CHECKOUT INSPECCIONADO

**Título:** Sustituir Gemini por DeepSeek como proveedor LLM del proyecto.

**Problema:**  
El costo operativo asociado al uso de la API de Gemini resultaba elevado para la sostenibilidad del Tutor.

**Decisión:**  
Adoptar DeepSeek como proveedor LLM operativo del proyecto.

**Motivo:**  
Reducir significativamente los costos financieros de operación manteniendo la funcionalidad necesaria del Tutor.

**Alternativas consideradas:**  

- mantener Gemini;
- reducir el volumen de uso del modelo;
- evaluar otros proveedores.

**Consecuencias:**  

- DeepSeek debe tratarse como proveedor vigente del proyecto;
- deben revisarse configuración, endpoint, credenciales, formato de mensajes, manejo de errores y pruebas de integración;
- la lógica pedagógica no debe quedar acoplada innecesariamente a DeepSeek;
- futuras sustituciones del proveedor deben seguir el workflow correspondiente.

**Componentes afectados:**  
Integración LLM, configuración, secretos, manejo de errores, tests de integración y pruebas pedagógicas.

**Reglas relacionadas:**  
`RULE-PED-04`, `RULE-TEC-04`, `GRD-05`.

**Reemplaza a:**  
Uso operativo de Gemini.

**Observación de consistencia:**  
`BOOTSTRAP-001` verificó que la implementación del checkout inspeccionado continúa utilizando Gemini para generación, evaluación y embeddings, y que no existe una implementación ejecutable de DeepSeek. Antes de intervenir la integración LLM debe verificarse y sincronizarse el estado técnico real del checkout y del despliegue vigente.

---

## DEC-007 — Gobernanza de alertas automatizadas de posible uso de IA

**Estado:** VIGENTE

**Estado de implementación:** PENDIENTE DE ADECUACIÓN DEL FLUJO ACTUAL

**Problema:**
La revisión humana previa de cada alerta no es escalable para el volumen de estudiantes y debilitaría la autonomía operativa prevista para el Tutor.

**Decisión:**
Mantener la posibilidad de aplicar automáticamente consecuencias previamente definidas ante `[ALERTA_IA]`, con aplicación uniforme, trazabilidad suficiente, revisión humana por excepción y capacidad de corrección o restauración cuando corresponda.

La revisión humana por excepción puede activarse, entre otros casos, por solicitud del estudiante, controversia, inconsistencia detectada, incidencia técnica o muestreo de control. No se requiere autorización docente previa para cada evento automatizado.

**Razones:**

- escalabilidad;
- consistencia procedimental;
- reducción de variabilidad entre evaluadores;
- autonomía del ejercicio;
- necesidad de auditabilidad y corrección.

**Alcance y límites:**

- `[ALERTA_IA]` es un criterio operacional y no constituye prueba infalible de uso indebido de IA;
- la aplicación uniforme no debe presentarse como ausencia absoluta de errores o sesgos;
- cada consecuencia debe ser trazable hasta el evento que la originó;
- debe existir posibilidad efectiva de revisión humana por excepción;
- debe existir capacidad de corrección, reversión o restauración cuando una revisión determine que la consecuencia no correspondía;
- pueden emplearse auditorías muestrales para evaluar el comportamiento y la consistencia del sistema.

**Consecuencias:**

- el flujo funcional vigente debe evaluarse y adecuarse antes de considerar implementada esta decisión;
- la automatización puede mantenerse sin revisión docente previa de cada alerta;
- los futuros cambios sobre `[ALERTA_IA]` deben aplicar `TEST-GOV-ADV-01` y clasificarse como `HIGH` cuando produzcan consecuencias académicas adversas.

**Componentes afectados:**
Gobernanza pedagógica, alertas automatizadas, persistencia de trazas, revisión por excepción, corrección de consecuencias y validación.

**Reglas y validaciones relacionadas:**
`GRD-07`, `TEST-GOV-ADV-01`.

**Evidencia de origen:**
`EXP-HIGH-001`.

---

# Regla para nuevas decisiones

Debe crearse un nuevo Decision Record cuando un desarrollador futuro pueda preguntarse razonablemente:

> “¿Por qué se hizo esto de esta manera?”

Ejemplos típicos:

- cambio de proveedor LLM;
- cambio de arquitectura;
- cambio de persistencia;
- nueva política pedagógica;
- nueva estrategia RAG;
- modificación significativa de seguridad;
- cambio de criterio de evaluación;
- cambio permanente del workflow de desarrollo.

Cuando una decisión cambie:

- no eliminar la anterior;
- marcarla `REEMPLAZADA` o `REVOCADA`;
- indicar la nueva decisión que la sustituye cuando corresponda.
