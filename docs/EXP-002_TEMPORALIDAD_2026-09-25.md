# EXP-002 — Temporalidad

**Bloque:** E — Experimentos controlados  
**Hipótesis:** una temporalidad débil puede expresarse con O/M/A/δ, pero una semántica temporal fuerte no debe asumirse gratuitamente.

## Pregunta

¿Hace falta una quinta primitiva para representar tiempo?

## Prueba

Se construye una secuencia de tres eventos como objetos y relaciones explícitas:

- e1 before e2
- e2 before e3
- e1 before e3

La incorporación se realiza exclusivamente mediante `Transition` y `Kernel.transition()`.

## Resultado conceptual

La **relación temporal explícita** es CORE-EXPRESSIBLE: no requiere una primitiva temporal.

Sin embargo, la palabra `before` por sí sola no introduce una teoría temporal universal. Propiedades como transitividad, antisimetría, simultaneidad, intervalos, duración, métricas o tiempo continuo requieren semántica adicional, que puede expresarse mediante relaciones + axiomas + algoritmos en algunos casos.

Por tanto, esta prueba no autoriza a introducir `Time` como quinta primitiva.

## Estado

**IMPLEMENTADO — pendiente de ejecución runtime.**

El archivo de prueba es `experiments/exp-002-temporalidad/test_exp_002_temporalidad.py`.

Criterio de cierre posterior:

- si las pruebas pasan: cerrar como **CORE + ALGORITHM**, manteniendo abierta la cuestión de semántica temporal fuerte;
- si aparece una insuficiencia concreta: formular contraejemplo y analizar si la insuficiencia es representacional, axiomática o algorítmica antes de proponer cualquier nueva primitiva.

No se modifica el núcleo `<O,M,A,δ>`.
