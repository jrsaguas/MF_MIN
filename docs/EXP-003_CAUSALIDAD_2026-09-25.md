# EXP-003 — Causalidad

**Bloque:** E — Experimentos controlados  
**Hipótesis:** una afirmación causal puede representarse como una relación de M, pero una teoría causal fuerte no debe confundirse con el almacenamiento de esa relación.

## Pregunta

¿Requiere la causalidad una quinta primitiva distinta de O, M, A y δ?

## Prueba

Se representan eventos como objetos y afirmaciones causales como relaciones:

`fire --causes--> heat`

`fire --causes--> smoke`

Después se construye una cadena:

`a --causes--> b --causes--> c`

La prueba verifica deliberadamente que MF_MIN **no inventa** `a causes c` solo porque exista la palabra `causes`.

También se representa evidencia de una afirmación causal mediante otra relación.

## Hallazgo

La **representación de una afirmación causal** es CORE-EXPRESSIBLE: fuente, relación y destino pertenecen a O/M.

Pero la **validez causal** es una cuestión diferente. Una teoría causal puede requerir temporalidad, intervención, contrafactuales, mecanismos, exclusión de confusores o criterios estadísticos. Ninguna de esas propiedades debe atribuirse automáticamente a M.

Esto evita dos errores opuestos:

1. declarar que causalidad exige una quinta primitiva sin intentar reducirla;
2. declarar que cualquier relación llamada `causes` ya constituye una teoría causal completa.

## Clasificación provisional

**CORE + SEMÁNTICA/ALGORITMO EXTERNO.**

La representación básica no exige nueva primitiva.

La semántica causal fuerte queda abierta para análisis posteriores: si alguna propiedad causal concreta no puede formalizarse mediante O/M/A/δ más reglas explícitas, deberá presentarse un contraejemplo reproducible.

## Estado

**IMPLEMENTADO — pendiente de ejecución runtime.**

No se modifica el núcleo `<O,M,A,δ>`.
