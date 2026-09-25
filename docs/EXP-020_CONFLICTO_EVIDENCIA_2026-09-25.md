# EXP-020 — Conflicto de evidencia

**Estado:** cerrado; ejecución aislada PASS, batería completa PASS, núcleo sin modificaciones.

## Hipótesis

Un conjunto de evidencias conflictivas puede representarse dentro de O/M/A/δ sin introducir una primitiva específica de conflicto o resolución. El núcleo debe conservar la distinción entre:

- conflicto entre evidencias distintas;
- contradicción del mismo hecho;
- procedimiento externo de resolución.

## Protocolo

Se verificó:

- representación de evidencia a favor y en contra;
- coexistencia de múltiples fuentes;
- rechazo de contradicción positiva/negativa del mismo hecho por I3;
- atomicidad del rechazo;
- ausencia de resolución automática;
- resolución externa con procedencia;
- conservación de las evidencias originales;
- ausencia de inferencia por ausencia de evidencia;
- restricciones sobre resolución;
- ausencia de quinta primitiva.

## Resultado

La ejecución aislada produjo:

`18 passed in 0.14s`

El conflicto entre relaciones distintas, por ejemplo `supports` y `refutes`, puede almacenarse como estructura ordinaria de M. No existe una operación especial de resolución en el núcleo.

En cambio, cuando se intenta registrar el mismo hecho con polaridad positiva y negativa, I3 lo rechaza y la transición es atómica: el estado previo permanece intacto.

Esto es una distinción fundamental. **Conflicto epistemológico entre fuentes no equivale a contradicción estructural del estado.**

## Resolución externa

Un procedimiento externo puede producir una relación derivada que represente una resolución y conservar sus premisas:

`origin="derived"`

`rule_id="resolve_v1"`

`premises=("s","r")`

La resolución, sin embargo, depende de criterios externos: confiabilidad de fuentes, pesos, reglas de agregación, contexto, evidencia adicional u otro método explícito.

## Clasificación

**CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO.**

No se encontró evidencia que justifique una quinta primitiva.

## Límite

MF_MIN puede representar el conflicto y registrar una resolución calculada externamente, pero no decide por sí mismo cuál evidencia debe prevalecer.

Tampoco se interpreta la ausencia de evidencia como evidencia contraria.

## Integridad

No se modificaron `mf_min_definitivo.py` ni los invariantes I1–I6.

EXP-020 cierra la batería experimental de la Fase 3.
