# EXP-022 — Evidencia temporal incierta

**Estado:** cerrado; ejecución aislada PASS, batería completa PASS, núcleo sin modificaciones.

## Hipótesis

La combinación de evidencia, ubicación temporal e incertidumbre puede representarse con O/M/A/δ. La incertidumbre temporal no debe crear por sí misma una nueva semántica temporal ni una inferencia causal o probabilística automática.

## Resultado

Ejecución aislada:

`15 passed in 0.12s`

Se representaron:

- evidencias observadas en tiempos;
- orden temporal entre observaciones;
- valores de incertidumbre como datos;
- evidencia a favor y en contra desde fuentes distintas;
- restricciones temporales;
- derivaciones con procedencia;
- ausencia de evidencia como estado distinto de refutación.

La coexistencia de `supports`, `refutes`, `observed_at`, `before` y `has_uncertainty` no activa por sí sola ningún procedimiento de actualización, resolución o causalidad.

## Contradicción y conflicto

La invariancia I3 continúa aplicándose al mismo hecho positivo/negativo. El conflicto entre fuentes diferentes puede coexistir porque no es automáticamente el mismo hecho estructural.

## Clasificación

**CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO.**

No apareció evidencia que justifique una quinta primitiva.

## Límite

El experimento no establece una teoría completa de incertidumbre temporal. Establece que su estructura representacional puede construirse con O/M/A/δ, mientras que la interpretación de intervalos inciertos, distribución temporal, probabilidad condicionada y resolución epistemológica permanece externa.

## Integridad

Núcleo e invariantes I1–I6 sin modificaciones.

Siguiente: **EXP-023 — intervención con incertidumbre**.
