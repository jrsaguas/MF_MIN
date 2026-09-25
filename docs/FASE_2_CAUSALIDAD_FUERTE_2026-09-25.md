# FASE 2 — Causalidad fuerte

**Fecha:** 2026-09-25  
**Estado:** cerrada; EXP-012–EXP-015 ejecutados con núcleo intacto.

## Objetivo

Determinar hasta dónde pueden representarse dependencia, intervención, confusión y composición causal condicionada usando O/M/A/δ, sin convertir relaciones con nombres causales en semántica automática.

## Resultados

| Experimento | Fenómeno | Resultado |
|---|---|---|
| EXP-012 | Dependencia | CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO |
| EXP-013 | Intervención | CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO |
| EXP-014 | Confusión y contraejemplos | CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO |
| EXP-015 | Composición condicionada | CORE-EXPRESSIBLE + ALGORITMO/SEMÁNTICA EXTERNA |

## Hallazgos consolidados

1. Una dependencia puede almacenarse como M sin que implique causalidad fuerte.
2. Una intervención puede representarse como evento y cambio de estado sin introducir una operación especial.
3. Asociación, intervención y causalidad deben mantenerse diferenciadas.
4. Un confusor puede representarse explícitamente, pero su tratamiento requiere procedimientos externos.
5. Una cadena causal no autoriza por sí sola una composición transitiva.
6. Una composición condicionada puede derivarse explícitamente mediante una regla externa, conservando premisas y condición como procedencia.
7. La existencia de una relación o el nombre de un predicado no crea por sí mismo semántica causal.
8. Ningún experimento de la fase justificó una quinta primitiva.

## Límite encontrado

O/M/A/δ proporcionan estructura para representar escenarios causales y registrar transiciones y derivaciones. No contienen por sí mismos una teoría completa de identificación causal, intervención contrafactual, condiciones de validez, confusión o composición causal.

Por tanto, la fase no demuestra una reducción universal de la causalidad a O/M/A/δ. Establece un límite metodológico: las afirmaciones causales fuertes deben venir acompañadas de reglas, evidencia, algoritmos o semántica explícita fuera del núcleo.

## Verificación

La batería acumulada después de EXP-015 debe ejecutar todos los experimentos de `experiments/`. El núcleo `mf_min_definitivo.py` no se modifica y las invariantes I1–I6 permanecen vigentes.

## Decisión de fase

**Fase 2 cerrada. No se modifica el núcleo.**

La siguiente línea de investigación es **Fase 3 — Incertidumbre formal**, con EXP-016–EXP-020:

- soporte y evidencia;
- probabilidad;
- actualización de creencias;
- incertidumbre bajo restricciones;
- conflicto entre evidencias.

El mismo protocolo experimental y el presupuesto finito de investigación se conservan.
