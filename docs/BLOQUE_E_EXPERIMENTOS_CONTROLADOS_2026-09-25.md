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

**Estado: pendiente de ejecución.**

## 5. EXP-002 — Temporalidad

### Hipótesis
El orden de eventos puede representarse mediante O/M/δ, pero esto no demuestra una teoría temporal completa.

### Diseño
Construir eventos e1,e2,e3 y relaciones antes_de(e1,e2). Cambiar el estado mediante δ y conservar el historial como estructuras del estado o registro externo.

### Falsación
Encontrar una propiedad temporal necesaria que no pueda representarse sin introducir semántica adicional.

**Estado: pendiente de ejecución.**

## 6. EXP-003 — Causalidad

### Hipótesis
Una relación causa(a,b) puede almacenarse como M, pero almacenar una etiqueta causal no demuestra causalidad.

### Diseño
Comparar precedencia, correlación, dependencia, intervención y contrafactual.

### Falsación
Demostrar que una propiedad causal necesaria requiere una operación o semántica que no pueda reducirse a O/M/A/δ.

**Estado: pendiente de ejecución.**

## 7. EXP-004 — Reglas

### Hipótesis
Una regla puede tratarse como estructura sobre el núcleo y ejecutarse mediante un algoritmo de inferencia.

### Diseño
Usar P(x) ∧ Q(x) → R(x), verificar premisas y producir una transición derivada.

### Falsación
Requerir una semántica de reglas que no pueda expresarse como datos + evaluación + δ.

**Estado: pendiente de ejecución.**

## 8. EXP-005 — Incertidumbre

### Hipótesis
Es posible representar estructuralmente una afirmación junto con un valor asociado, pero aún debe probarse si una semántica completa de incertidumbre puede derivarse del núcleo.

### Diseño
Comparar representaciones de confianza, probabilidad, posibilidad, evidencia y desconocimiento. No deben tratarse como equivalentes.

### Falsación
Demostrar que la semántica requerida no puede expresarse mediante estructuras existentes y algoritmos externos sin pérdida conceptual esencial.

**Estado: pendiente de ejecución.**

## 9. EXP-006 — Planificación

### Hipótesis
Planificar es buscar una secuencia de transiciones que lleve de un estado inicial a un estado objetivo.

### Diseño
Definir S0 →δ S1 →δ ... →δ Sn y comprobar el objetivo sobre Sn. La búsqueda, heurística y función de coste pertenecen al algoritmo externo.

### Falsación
Demostrar que planificación necesita una primitiva ontológica adicional y no solamente búsqueda sobre δ.

**Estado: pendiente de ejecución.**

## 10. EXP-007 — Aprendizaje

### Hipótesis
Un cambio aprendido puede representarse como una transición de estado causada por experiencia y evaluación.

### Diseño
Separar experiencia observada, modificación de estado, modificación de reglas/parámetros y criterio de actualización. El algoritmo de aprendizaje queda fuera del núcleo.

### Falsación
Encontrar una forma de aprendizaje cuya semántica fundamental no pueda expresarse como transformación de estructuras existentes.

**Estado: pendiente de ejecución.**

## 11. Criterio de cierre

Un experimento se cierra cuando la representación funciona y sus límites están documentados; aparece un contraejemplo reproducible; o queda demostrado que la pregunta es indeterminada bajo la semántica actual.

No se repiten indefinidamente experimentos equivalentes.

Un resultado negativo válido es: “No demostrado bajo el formalismo actual”; no significa automáticamente “imposible en toda formalización”.

## 12. Gobernanza de resultados

Ningún experimento puede modificar el núcleo automáticamente.

Si aparece evidencia de insuficiencia:

contraejemplo → análisis → intento de reducción → nueva semántica propuesta → pruebas → decisión

Solo entonces puede abrirse una revisión del núcleo.

## 13. Estado del Bloque E

**DISEÑO DEL BLOQUE E: CERRADO.**

Los siete experimentos quedan definidos y listos para ejecución.

La ejecución comenzará por EXP-001 (memoria), porque permite probar una capacidad ya implementada en V7.1 y establecer una metodología concreta antes de abordar temporalidad, causalidad, incertidumbre, planificación y aprendizaje.
