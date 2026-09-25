# EXP-017 — Probabilidad

**Fase:** 3 — Incertidumbre formal  
**Hipótesis:** un valor probabilístico puede representarse como dato numérico en O y relacionarse mediante M, mientras que la interpretación como medida de probabilidad, normalización, cálculo condicional y actualización bayesiana requieren semántica o algoritmos externos.

## Protocolo

- Núcleo evaluado: O, M, A, δ.
- Invariantes preservadas: I1–I6.
- El núcleo no se modifica.
- Se distingue representación de un número de [0,1] de semántica probabilística.
- Las operaciones se realizan mediante transiciones δ ordinarias.

## Formalización

Sea h ∈ O una hipótesis y p ∈ O un objeto numérico con tipo Probability y valor p.value ∈ [0,1]. La asociación puede representarse mediante una relación M:

    has_probability(h,p)

A puede imponer localmente:

    0 ≤ p.value ≤ 1

Esto restringe valores numéricos, pero no define por sí solo un espacio muestral, exclusividad, normalización ni reglas de inferencia probabilística.

## Experimentos

EXP-017 verifica:
1. almacenamiento de valores 0 y 1;
2. asociación hipótesis–valor;
3. restricción [0,1] mediante A;
4. rechazo atómico de valores fuera del rango;
5. ausencia de semántica creada por el nombre del predicado;
6. ausencia de normalización automática;
7. ausencia de cálculo probabilístico implícito en δ;
8. representación estructural de probabilidad condicional;
9. ausencia de actualización bayesiana automática;
10. conservación de procedencia en afirmaciones derivadas;
11. distinción entre ausencia de probabilidad y probabilidad cero;
12. ausencia de quinto primitivo.

## Contraejemplo central

Dos hipótesis pueden recibir respectivamente 0.8 y 0.8 y el núcleo puede representar ambos valores sin contradicción. Su suma 1.6 demuestra que almacenar números en [0,1] no convierte automáticamente al conjunto en una distribución de probabilidad.

Por tanto, la normalización requiere información adicional sobre el conjunto de resultados, exclusividad, cobertura y la regla matemática que debe cumplirse.

Del mismo modo, una relación de soporte sobre una probabilidad previa no provoca por sí sola una actualización bayesiana.

## Resultado

**Estado:** cerrado tras ejecución aislada y batería completa PASS, núcleo sin modificaciones.

**Clasificación:** **CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO**.

La representación de valores probabilísticos, sus asociaciones y restricciones locales de rango utiliza O/M/A/δ. No se identificó un fenómeno que obligue a introducir una quinta primitiva.

La semántica probabilística fuerte permanece fuera del núcleo: distribución, normalización, probabilidad condicional, independencia, Bayes y actualización de creencias requieren procedimientos y/o axiomas externos.

## Limitaciones

Este experimento no demuestra que toda teoría de probabilidad sea reducible a O/M/A/δ. Establece únicamente el límite observado para representación numérica y operaciones probabilísticas básicas. La siguiente prueba debe estudiar actualización de creencias de forma explícita y reproducible.

## Conclusión

EXP-017 no proporciona evidencia para ampliar el núcleo. La frontera encontrada es semántica y algorítmica, no ontológica. El siguiente experimento es **EXP-018 — actualización de creencias**, donde se comprobará si modificar un valor de creencia a partir de evidencia puede representarse como transición sin introducir una nueva primitiva.
