# FASE 1 — Temporalidad fuerte

**Fecha de cierre:** 2026-09-25  
**Experimentos:** EXP-008 a EXP-011  
**Estado:** cerrada experimentalmente; revisión de límites registrada.

## 1. Objetivo

Determinar hasta dónde O/M/A/δ pueden representar fenómenos temporales sin introducir un nuevo primitivo del núcleo. La fase separa capacidad representacional de semántica temporal fuerte.

## 2. Resultados

| Experimento | Fenómeno | Clasificación | Resultado |
|---|---|---|---|
| EXP-008 | orden temporal | CORE-EXPRESSIBLE + ALGORITMO/RESTRICCIÓN | PASS |
| EXP-009 | intervalos y duración | CORE-EXPRESSIBLE + ALGORITMO/RESTRICCIÓN | PASS |
| EXP-010 | persistencia y cambio | CORE-EXPRESSIBLE + INFRAESTRUCTURA/ALGORITMO | PASS |
| EXP-011 | concurrencia y restricciones | CORE-EXPRESSIBLE + ALGORITMO/RESTRICCIÓN | PASS |

## 3. Síntesis

Los cuatro experimentos muestran que eventos, estados, relaciones de orden,
intervalos, valores de duración, persistencia representacional, concurrencia
y restricciones temporales pueden construirse sobre O/M/A/δ.

Esto no demuestra que toda teoría del tiempo sea reducible al núcleo. Sí
establece una frontera experimental más precisa: la representación puede
permanecer en el núcleo mientras que algoritmos, restricciones e
infraestructura aportan semántica operacional adicional.
## 4. Límites identificados

Persisten como preguntas abiertas la semántica fuerte de duración, continuidad,
simultaneidad, concurrencia física, relojes, sincronización, tiempo
continuo/discreto y teorías temporales modales. También queda separada la
cuestión de causalidad: no debe introducirse en esta fase por contaminación
conceptual de los experimentos temporales.

Un mismo identificador entre snapshots no prueba por sí solo continuidad
metafísica; una relación `before` no adquiere semántica universal por su
nombre; y la ejecución secuencial de δ no define el tiempo del dominio.

## 5. Decisión de fase

No aparece evidencia reproducible que justifique un quinto primitivo.

La decisión es **continuar sin modificar `<O,M,A,δ>`** y avanzar a la fase de
causalidad fuerte. Esta decisión no convierte el resultado en una prueba
universal de minimalidad; mantiene abierta la falsificación mediante
contraejemplos reproducibles.

## 6. Trazabilidad

- EXP-008: orden temporal.
- EXP-009: intervalos y duración.
- EXP-010: persistencia y cambio.
- EXP-011: concurrencia y restricciones.
- Núcleo `mf_min_definitivo.py`: sin modificaciones durante la fase.
- Invariantes I1–I6: sin modificaciones.

## 7. Criterio para continuar

La fase se considera cerrada al cumplir batería reproducible, revisión de
integridad del repositorio y registro de límites. La siguiente frontera es
FASE 2 — Causalidad fuerte, empezando por EXP-012 — dependencia.
