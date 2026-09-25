# EXP-023 — Intervención con incertidumbre

**Estado:** cerrado; ejecución aislada PASS, batería completa PASS, núcleo sin modificaciones.

## Hipótesis

La intervención experimental, su resultado, evidencia y un valor de incertidumbre pueden coexistir dentro de O/M/A/δ. La incertidumbre no debe convertirse automáticamente en intervención, causalidad, resolución o actualización.

## Resultado

Ejecución aislada:

`14 passed in 0.04s`

Se representaron:

- objetivo de la intervención;
- estado previo y estado producido;
- incertidumbre asociada;
- evidencia del resultado;
- orden temporal entre intervención y observación;
- ramas baseline/intervención;
- conflictos de evidencia;
- derivaciones con procedencia.

La intervención permanece como estructura explícita. El núcleo no ejecuta una operación especial llamada intervención: la información se almacena mediante objetos, relaciones y transiciones ordinarias.

## Límites demostrados

La presencia de una incertidumbre no produce automáticamente un efecto.

La intervención no produce automáticamente una relación `causes`.

Una relación con nombre causal no ejecuta semántica causal.

La resolución de evidencia y la estimación del efecto requieren procedimientos externos.

I3 continúa rechazando la polaridad positiva y negativa del mismo hecho, mientras que fuentes diferentes pueden mantener evidencia conflictiva.

## Clasificación

**CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO.**

No apareció evidencia suficiente para una quinta primitiva.

## Integridad

Núcleo e invariantes I1–I6 sin modificaciones.

Siguiente: **EXP-024 — sistema integrado**.
