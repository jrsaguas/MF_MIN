# FASE 5 — MAPA DE LÍMITES DE MF_MIN

**Fecha:** 2026-09-25  
**Estado:** mapa inicial consolidado a partir de EXP-001..024.

## 1. Objetivo

Esta fase no agrega primitivas. Su objetivo es separar tres preguntas que durante la evolución de V7.1 tendían a mezclarse:

1. ¿Puede un fenómeno representarse estructuralmente con O/M/A/δ?
2. ¿Puede obtenerse una consecuencia mediante un algoritmo construido sobre el núcleo?
3. ¿La semántica fuerte del fenómeno está definida intrínsecamente por el núcleo?

Estas preguntas no son equivalentes.

## 2. Resultado global

La evidencia experimental disponible no ha producido un contraejemplo que obligue a introducir una quinta primitiva.

El patrón dominante es:

**O/M/A/δ representa la estructura; algoritmos externos producen composición, inferencia, actualización o resolución; las semánticas fuertes siguen siendo contratos externos.**

Esto no demuestra que todo fenómeno imaginable sea expresable por MF_MIN. Demuestra solamente que los dominios investigados hasta EXP-024 no han exigido una ampliación del núcleo.

## 3. Mapa de dominios

| Dominio | Representación con O/M/A/δ | Procesamiento adicional | Semántica intrínseca demostrada |
|---|---|---|---|
| Identidad | Sí | No necesariamente | Sí, dentro del modelo actual |
| Relaciones | Sí | Opcional | Sí, como estructura relacional |
| Restricciones | Sí | Validación | Sí, como restricciones explícitas |
| Transición/cambio | Sí | δ | Sí, como cambio de estado |
| Memoria | Sí | Consulta/agregación | No como módulo especial |
| Reglas | Sí | Motor externo | No |
| Planificación | Sí | Búsqueda/selección externa | No |
| Aprendizaje | Sí | Generalización/actualización externa | No |
| Orden temporal | Sí | Cierre/restricciones externas | No como inferencia automática |
| Intervalos/duración | Sí | Aritmética/composición externa | No |
| Persistencia/historia | Parcialmente sí | Snapshots/historial externo | No como tiempo intrínseco |
| Concurrencia | Sí | Validación externa | No inferida por coexistencia |
| Dependencia | Sí | Composición externa | No como causalidad |
| Intervención | Sí | Evaluación/comparación externa | No como causalidad automática |
| Causalidad | Sí como afirmación | Inferencia/identificación externa | No demostrada |
| Confusión/contrafactuales | Sí como estructura | Análisis externo | No |
| Evidencia | Sí | Evaluación externa | No |
| Probabilidad | Sí como datos/valores | Cálculo externo | No |
| Actualización de creencias | Sí | Regla de actualización externa | No |
| Incertidumbre | Sí como estructura/dato | Interpretación/cálculo externo | No |
| Conflicto de evidencia | Sí | Resolución externa | No |
| Interacción integrada | Sí | Algoritmo/semántica externa | No |

## 4. Fronteras principales

### L1 — Representación vs interpretación

Un predicado puede almacenarse en M sin que su nombre otorgue significado operacional.

Ejemplo:

`causes(a,b)`

puede ser representado; el núcleo no demuestra que `a` cause `b`.

### L2 — Restricción vs semántica

A puede prohibir un estado determinado, pero una restricción no constituye por sí misma una teoría semántica completa.

Por ejemplo, una cota numérica puede exigir:

`0 <= u <= 1`

sin convertir automáticamente `u` en una probabilidad con reglas de inferencia.

### L3 — Evidencia vs verdad

M puede registrar soporte, refutación, procedencia y conflicto. El núcleo no selecciona automáticamente cuál fuente es correcta.

### L4 — Temporalidad vs orden de ejecución

δ define transiciones del sistema, pero el orden de ejecución de esas transiciones no equivale automáticamente al tiempo del dominio representado.

### L5 — Correlación/orden vs causalidad

EXP-003, EXP-014, EXP-015 y EXP-021 muestran que relaciones temporales, dependencia e intervención pueden coexistir con afirmaciones causales sin que una implique automáticamente a las otras.

### L6 — Incertidumbre vs actualización

Un valor de incertidumbre puede almacenarse y restringirse. Su interpretación y su transformación ante nueva evidencia requieren una política externa.

### L7 — Conflicto estructural vs conflicto epistémico

I3 protege contra una contradicción exacta entre polaridades del mismo hecho. Dos fuentes diferentes pueden sostener afirmaciones incompatibles sin que esto constituya automáticamente el mismo tipo de contradicción estructural.

### L8 — Estructura integrada vs inteligencia integrada

El caso EXP-024 demuestra que muchas dimensiones pueden coexistir en el mismo estado. Eso no implica que el núcleo deba incorporar un agente de razonamiento, planificador, aprendiz o resolvedor de conflictos.

## 5. Lo que todavía NO está demostrado

El mapa no debe convertir los resultados actuales en una afirmación universal.

Continúan abiertas, entre otras, estas cuestiones:

- semántica temporal fuerte: intervalos complejos, eventos durativos y calendarios con semántica completa;
- causalidad formal fuerte: identificación causal, contrafactuales formales y modelos estructurales completos;
- incertidumbre formal fuerte: distribuciones, medidas, dependencia probabilística y semánticas alternativas;
- conocimiento negativo y no monotónico a escala general;
- cuantificación y variables de primer orden;
- identidad dinámica y referencia bajo transformación compleja;
- composición de múltiples estados con equivalencia formal;
- sistemas abiertos donde aparecen entidades externas y observaciones parciales;
- semánticas modales o contrafactuales que no sean simples relaciones almacenadas;
- límites de representación cuando el dominio exige infinitud o estructuras no finitas.

Estas preguntas no deben convertirse automáticamente en nuevas primitivas. Primero requieren contraejemplos reproducibles bajo el protocolo de gobernanza.

## 6. Criterio de falsificación

Una futura reclamación de insuficiencia del núcleo debe mostrar:

1. un fenómeno formalmente definido;
2. una representación explícita con O/M/A/δ intentada de buena fe;
3. un resultado requerido por la definición del fenómeno;
4. demostración de que el resultado no puede obtenerse sin introducir una estructura semánticamente equivalente a una de las primitivas existentes;
5. reproducibilidad mediante pruebas;
6. ausencia de simple reubicación de la semántica en un algoritmo externo.

Sin estos elementos, el resultado se clasifica como **INDETERMINADO**, no como nueva primitiva.

## 7. Decisión de Fase 5

La evidencia acumulada hasta EXP-024 mantiene la hipótesis de trabajo:

[
MF_{MIN} = langle O,M,A,deltaangle
]

como **núcleo operativo mínimo bajo el modelo formal actual**, sin justificar todavía una afirmación universal de minimalidad para toda formalización posible.

La siguiente tarea es realizar una revisión dirigida de los límites que quedaron realmente abiertos y seleccionar solamente aquellos capaces de producir un contraejemplo fuerte.

No se autoriza ampliar el núcleo por conveniencia arquitectónica.
