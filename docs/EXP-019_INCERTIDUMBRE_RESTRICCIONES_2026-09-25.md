# EXP-019 — Incertidumbre con restricciones

**Estado:** cerrado; ejecución aislada PASS, batería completa PASS, núcleo sin modificaciones.

## Hipótesis

La incertidumbre puede representarse como dato numérico y relaciones dentro de O/M/A/δ, mientras que las restricciones sobre esos valores pueden expresarse mediante A. Las restricciones no convierten automáticamente el núcleo en una teoría probabilística o de incertidumbre.

## Protocolo

Se verificó:

- representación de valores de incertidumbre;
- límites numéricos mediante axiomas;
- rechazo atómico de valores fuera de rango;
- coexistencia con evidencia;
- ausencia de normalización automática;
- ausencia de inferencia automática;
- conflictos entre restricciones;
- procedencia de resultados derivados;
- ausencia de necesidad de una quinta primitiva.

## Resultado

La ejecución aislada produjo:

`20 passed in 0.06s`

La incertidumbre queda representada mediante objetos ordinarios y relaciones. A puede restringir rangos y δ puede almacenar transiciones, pero ninguna de estas operaciones determina por sí misma una distribución, función de pérdida, medida de entropía, regla de actualización o interpretación epistemológica.

Un punto importante es que **restricción ≠ semántica**. Que un valor pertenezca a [0,1] no determina qué significa ese valor.

También se verificó que restricciones incompatibles producen rechazo de la transición y preservan el estado anterior.

## Clasificación

**CORE-EXPRESSIBLE + RESTRICCIÓN/SEMÁNTICA EXTERNA.**

No aparece evidencia para introducir una quinta primitiva.

## Límite

El experimento no pretende demostrar que toda teoría de incertidumbre sea reducible a O/M/A/δ. Demuestra algo más acotado: las estructuras necesarias para almacenar valores inciertos y restricciones sobre ellos pueden representarse sin ampliar la ontología del núcleo.

Las interpretaciones fuertes y los algoritmos de actualización permanecen fuera del núcleo.

## Integridad

No se modificaron `mf_min_definitivo.py` ni los invariantes I1–I6.

Siguiente experimento: **EXP-020 — conflicto de evidencia**.
