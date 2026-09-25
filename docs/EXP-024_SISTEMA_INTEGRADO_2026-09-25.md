# EXP-024 — Sistema integrado

**Estado:** cerrado.

## Hipótesis

Un escenario integrado que combine intervención, temporalidad, causalidad, evidencia, incertidumbre y conflicto puede representarse mediante O/M/A/δ sin introducir una quinta primitiva.

## Resultado

Ejecución aislada: **15 passed**.

Batería completa: **255 passed**.

El escenario integrado representa conjuntamente:

- evento de intervención y objetivo;
- estado baseline y estado posterior;
- localización temporal;
- orden temporal;
- resultado producido;
- afirmación causal explícita;
- evidencia de múltiples fuentes;
- incertidumbre numérica asociada a evidencia;
- conflicto entre fuentes;
- derivación externa con procedencia y premisas.

## Evidencia negativa importante

El núcleo no infiere automáticamente:

- causalidad a partir de orden temporal;
- orden temporal a partir de causalidad;
- efecto a partir de una intervención;
- resolución de conflicto entre evidencias;
- actualización por incertidumbre;
- significado especial a partir del nombre de un predicado.

Cuando se necesita una conclusión integrada, puede almacenarse como relación derivada con `origin="derived"`, `rule_id` y `premises`. La semántica de la regla permanece externa.

## Incidente de prueba

La primera versión del experimento reutilizó accidentalmente el ID `u` para el objeto de incertidumbre y para una relación. I1 rechazó correctamente la transición mediante `DuplicateIDError`. El test fue corregido usando un ID distinto para la relación. Esto confirma que la unicidad global de IDs se mantiene incluso en el escenario integrado.

## Clasificación

**CORE-EXPRESSIBLE + ALGORITMO/SEMÁNTICA EXTERNA.**

No apareció evidencia de una quinta primitiva.

## Cierre de Fase 4

EXP-021, EXP-022, EXP-023 y EXP-024 cubren interacciones entre temporalidad, causalidad, evidencia, incertidumbre e intervención. En conjunto, la batería no obliga a modificar O/M/A/δ.

La siguiente etapa es cerrar documentalmente la Fase 4 y construir el **mapa de límites de MF_MIN**.

