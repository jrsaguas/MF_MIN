# BLOQUE E — Experimentos controlados sobre MF_MIN
## Diseño experimental y criterios de falsación
**Fecha:** 2026-09-25  
**Baseline:** MF_MIN V7.1

## 1. Objetivo

El Bloque E transforma las capacidades superiores de V7.1 en hipótesis experimentales. No se agregan primitivas al núcleo por conveniencia.

Núcleo de referencia: MF_MIN = ⟨O,M,A,δ⟩

Cada experimento debe determinar si una capacidad puede representarse con el núcleo, requiere algoritmos externos, tiene límites bajo la semántica actual, o proporciona evidencia concreta de que la semántica necesita ampliación.

## 2. Protocolo común

Cada experimento registra: hipótesis, estado inicial S=⟨O,M,A⟩, representación mediante O/M/A/δ, operaciones δ, resultado observable, invariantes I1–I6, pruebas o contraejemplos, separación entre núcleo y algoritmo externo, limitaciones y conclusión.

Una implementación que simplemente introduzca una nueva clase no constituye evidencia de necesidad.

## 3. Matriz inicial

| ID | Capacidad | Hipótesis inicial | Criterio principal |
|---|---|---|---|
| EXP-001 | Memoria | Un estado histórico puede representarse con O/M/δ | Recuperar información sin nuevo primitivo |
| EXP-002 | Temporalidad | El orden temporal puede codificarse con O/M/δ | Distinguir orden de semántica temporal fuerte |
| EXP-003 | Causalidad | La estructura causal puede almacenarse en M, pero causalidad fuerte requiere análisis adicional | Separar correlación, precedencia y contrafactual |
| EXP-004 | Reglas | Las reglas pueden representarse como estructuras y ejecutarse como algoritmo | No convertir reglas en quinto primitivo |
| EXP-005 | Incertidumbre | Puede existir representación estructural, pero falta probar una semántica completa | Distinguir confianza, probabilidad, posibilidad y desconocimiento |
| EXP-006 | Planificación | Planificar es buscar una secuencia de transiciones | Resolver planificación sin nuevo primitivo |
| EXP-007 | Aprendizaje | Aprender puede modelarse como transición guiada por experiencia | Distinguir proceso de nueva ontología |

## 4. EXP-001 — Memoria

### Hipótesis
La memoria episódica no requiere un nuevo primitivo formal.

### Diseño
Representar eventos como objetos, contenido como relaciones, orden como relaciones entre eventos, incorporación como transiciones δ y persistencia física como infraestructura externa.

### Falsación
Buscar un caso donde recuperar un episodio exija una entidad formal que no pueda expresarse como O/M/A ni obtenerse mediante δ.

### Resultado esperado
La representación formal es posible; índices, embeddings y recuperación eficiente permanecen fuera del núcleo.

**Estado: EJECUTADO — PASS.**

## 5. EXP-002 — Temporalidad

### Hipótesis
El orden de eventos puede representarse mediante O/M/δ, pero esto no demuestra una teoría temporal completa.

### Diseño
Construir eventos e1,e2,e3 y relaciones antes_de(e1,e2). Cambiar el estado mediante δ y conservar el historial como estructuras del estado o registro externo.

### Falsación
Encontrar una propiedad temporal necesaria que no pueda representarse sin introducir semántica adicional.

**Estado: EJECUTADO — PASS.**

## 6. EXP-003 — Causalidad

### Hipótesis
Una relación causa(a,b) puede almacenarse como M, pero almacenar una etiqueta causal no demuestra causalidad.

### Diseño
Comparar precedencia, correlación, dependencia, intervención y contrafactual.

### Falsación
Demostrar que una propiedad causal necesaria requiere una operación o semántica que no pueda reducirse a O/M/A/δ.

**Estado: EJECUTADO — PASS.**

## 7. EXP-004 — Reglas

### Hipótesis
Una regla puede tratarse como estructura sobre el núcleo y ejecutarse mediante un algoritmo de inferencia.

### Diseño
Usar P(x) ∧ Q(x) → R(x), verificar premisas y producir una transición derivada.

### Falsación
Requerir una semántica de reglas que no pueda expresarse como datos + evaluación + δ.

**Estado: EJECUTADO — PASS.**

## 8. EXP-005 — Incertidumbre

### Hipótesis
Es posible representar estructuralmente una afirmación junto con un valor asociado, pero aún debe probarse si una semántica completa de incertidumbre puede derivarse del núcleo.

### Diseño
Comparar representaciones de confianza, probabilidad, posibilidad, evidencia y desconocimiento. No deben tratarse como equivalentes.

### Falsación
Demostrar que la semántica requerida no puede expresarse mediante estructuras existentes y algoritmos externos sin pérdida conceptual esencial.

**Estado: EJECUTADO — PASS.**

## 9. EXP-006 — Planificación

### Hipótesis
Planificar es buscar una secuencia de transiciones que lleve de un estado inicial a un estado objetivo.

### Diseño
Definir S0 →δ S1 →δ ... →δ Sn y comprobar el objetivo sobre Sn. La búsqueda, heurística y función de coste pertenecen al algoritmo externo.

### Falsación
Demostrar que planificación necesita una primitiva ontológica adicional y no solamente búsqueda sobre δ.

**Estado: EJECUTADO — PASS.**

## 10. EXP-007 — Aprendizaje

### Hipótesis
Un cambio aprendido puede representarse como una transición de estado causada por experiencia y evaluación.

### Diseño
Separar experiencia observada, modificación de estado, modificación de reglas/parámetros y criterio de actualización. El algoritmo de aprendizaje queda fuera del núcleo.

### Falsación
Encontrar una forma de aprendizaje cuya semántica fundamental no pueda expresarse como transformación de estructuras existentes.

**Estado: EJECUTADO — PASS.**

## 11. Ejecución runtime y resultado consolidado

La batería se ejecutó localmente sobre la copia sincronizada con `origin/main`.

**Resultado final:** 19 pruebas aprobadas, 0 fallos.

La primera ejecución produjo 5 fallos en EXP-004, EXP-005 y EXP-007. La revisión mostró que no eran contraejemplos contra MF_MIN, sino discrepancias entre los tests experimentales y los contratos ya definidos por el núcleo:

- EXP-004 y EXP-007 intentaban crear relaciones `derived` sin `rule_id`, aunque el contrato de `Relation` exige procedencia de regla para una derivación.
- EXP-005 intentaba conservar simultáneamente polaridades positiva y negativa del mismo triple, lo que viola deliberadamente I3 (no contradicción).

Los tests fueron corregidos para respetar esos contratos sin modificar el núcleo. La segunda ejecución produjo **19 passed in 0.06s**.

Este resultado no prueba una expresividad universal de MF_MIN. Sí confirma que las siete representaciones experimentales implementadas son compatibles con el núcleo V7.1 bajo la semántica e invariantes actuales, y que sus algoritmos/semánticas adicionales pueden mantenerse como extensiones.

## 12. Criterio de cierre

Un experimento se cierra cuando la representación funciona y sus límites están documentados; aparece un contraejemplo reproducible; o queda demostrado que la pregunta es indeterminada bajo la semántica actual.

No se repiten indefinidamente experimentos equivalentes.

Un resultado negativo válido es: “No demostrado bajo el formalismo actual”; no significa automáticamente “imposible en toda formalización”.

## 13. Gobernanza de resultados

Ningún experimento puede modificar el núcleo automáticamente.

Si aparece evidencia de insuficiencia:

contraejemplo → análisis → intento de reducción → nueva semántica propuesta → pruebas → decisión

Solo entonces puede abrirse una revisión del núcleo.

## 14. Estado del Bloque E

**BLOQUE E: CERRADO FORMALMENTE.**

Los siete experimentos fueron ejecutados sobre la copia local sincronizada con `origin/main` y finalizaron con **19 pruebas aprobadas y 0 fallos**. Las correcciones realizadas afectaron únicamente a los tests experimentales para alinearlos con contratos ya existentes del núcleo; no fue necesario modificar `mf_min_definitivo.py`.

Conclusión del bloque: no aparece evidencia experimental de que memoria, temporalidad básica, causalidad representacional, reglas, incertidumbre estructural, planificación o aprendizaje representacional requieran una quinta primitiva. Las limitaciones de semántica fuerte y los algoritmos de alto nivel permanecen explícitamente fuera del núcleo.
