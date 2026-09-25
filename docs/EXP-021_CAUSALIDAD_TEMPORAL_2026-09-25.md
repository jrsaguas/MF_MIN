# EXP-021 — Causalidad temporal

**Estado:** cerrado; ejecución aislada PASS, batería completa pendiente de cierre, núcleo sin modificaciones.

## Hipótesis

La combinación de orden temporal y relaciones causales puede representarse mediante O/M/A/δ, pero la mera coexistencia de orden temporal y causalidad no debe producir automáticamente una inferencia causal-temporal.

## Protocolo

Se verificó:

- separación entre `before` y `causes`;
- ausencia de inferencia causal a partir de precedencia temporal;
- ausencia de inferencia temporal a partir de causalidad;
- representación explícita de eventos y tiempos;
- coexistencia de relaciones temporales y causales;
- registro de una derivación temporal-causal externa con procedencia;
- ausencia de resolución por nombre de predicado;
- rechazo de una derivación sin `rule_id`;
- ausencia de quinta primitiva.

## Resultado

Ejecución aislada:

`12 passed`

La estructura temporal puede almacenarse en M mediante objetos de tiempo y relaciones como `before`/ `occurs_at`. La estructura causal puede almacenarse independientemente mediante `causes`.

La combinación de ambas estructuras sigue siendo una composición de O y M. El núcleo no convierte automáticamente:

`before(a,b) + occurs_at(a,t1) + occurs_at(b,t2) -> causes(a,b)`

ni realiza el razonamiento inverso.

## Clasificación

**CORE-EXPRESSIBLE + ALGORITMO/SEMÁNTICA EXTERNA.**

La interacción temporal-causal no justificó una quinta primitiva.

## Límite

El experimento no pretende demostrar que toda teoría de causalidad temporal sea reducible a O/M/A/δ. Demuestra que su estructura explícita puede representarse y que las inferencias fuertes requieren reglas/procedimientos externos.

## Integridad

`mf_min_definitivo.py` no fue modificado y los invariantes I1–I6 permanecen intactos.

Siguiente experimento: **EXP-022 — evidencia temporal incierta**.
