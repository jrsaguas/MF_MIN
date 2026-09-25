# EXP-006 — Planificación

**Bloque:** E — Experimentos controlados  
**Hipótesis:** un problema de planificación puede representarse sobre O/M/A/δ; la búsqueda y selección de planes es un algoritmo externo.

## Prueba

Se representan:

- estados;
- objetivo;
- acciones;
- precondiciones;
- efectos;
- relaciones de alcanzabilidad.

La ejecución de una acción se modela como un cambio de estado mediante δ.

## Resultado conceptual

La estructura necesaria para describir un problema de planificación cabe en el núcleo. No obstante, el núcleo no determina por sí mismo qué plan elegir, cuál es óptimo ni cómo explorar el espacio de estados.

Por ello se separan:

`representación del problema → O/M/A`

`ejecución del plan → δ`

`búsqueda/selección → algoritmo externo`

## Clasificación

**CORE + ALGORITMO.**

No se justifica una quinta primitiva.

## Límite

Planificación óptima, heurísticas, costos, incertidumbre, restricciones temporales y planificación bajo observación parcial son problemas adicionales. Su presencia no se debe asumir como propiedad automática de MF_MIN.

## Estado

**IMPLEMENTADO — pendiente de ejecución runtime.**
