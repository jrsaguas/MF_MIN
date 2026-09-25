# EXP-013 — Intervención

**Fecha:** 2026-09-25  
**Fase:** 2 — Causalidad fuerte  
**Estado:** cerrado; ejecución aislada y batería completa PASS, núcleo sin modificaciones.

## 1. Hipótesis

Una intervención deliberada puede representarse mediante O/M/A/δ como un evento o acción explícita, relaciones que describen su objetivo y un estado posterior obtenido mediante transiciones. La semántica fuerte de “intervenir” y la interpretación causal del cambio no se siguen automáticamente de esas estructuras.

## 2. Pregunta

¿La intervención requiere un nuevo primitivo del núcleo, o puede representarse mediante objetos, relaciones, restricciones y transiciones, dejando la semántica causal fuerte a reglas y algoritmos explícitos?

## 3. Diseño experimental

Se prueban:

1. representación de una intervención como objeto/evento;
2. relación explícita entre intervención y objetivo;
3. representación de estados antes/después sin mutación de objetos existentes;
4. aplicación mediante operaciones ordinarias de δ;
5. separación entre observación, dependencia e intervención;
6. comparación explícita de estados para identificar un cambio;
7. posibilidad de mantener una rama intervenida separada de una línea base;
8. ausencia de inferencia automática de causalidad;
9. ausencia de semántica creada por el nombre intervenes_on;
10. ausencia de justificación para un quinto primitivo.

No se modifica mf_min_definitivo.py, la especificación ni I1–I6.

## 4. Resultado esperado y representación

Una intervención puede descomponerse estructuralmente como:

i1 ∈ O, targets(i1, y0) ∈ M, starts_from(i1, s0) ∈ M, produces(i1, s1) ∈ M.

El estado posterior puede contener un nuevo objeto de valor y1 y una relación has_value(s1, y1). Esto respeta la implementación actual del núcleo: los objetos existentes no se actualizan in-place; el cambio se expresa mediante nuevos objetos/relaciones y una nueva instantánea estructural.

La transición δ puede incorporar cada elemento como operaciones ordinarias. No se introduce una operación primitiva intervene.

## 5. Observación, dependencia e intervención

observes(obs1, y0) no implica intervención. Del mismo modo, depends_on(z0, y0) no implica que alguien haya modificado y0. Una relación intervenes_on(i1, y0) tampoco cambia el estado únicamente por su nombre: el efecto debe estar representado explícitamente mediante una transición y estados comparables.

Esto permite separar tres niveles:

- **observación:** registro de información sobre un objeto;
- **dependencia:** afirmación estructural entre objetos;
- **intervención:** evento/acción con objetivo y transición entre estados.

La representación de estos niveles cabe en O/M/A/δ, aunque sus semánticas no sean equivalentes.

## 6. Contraejemplos y límites

El experimento construye un caso donde intervenes_on existe como relación pero no produce ningún cambio por sí misma. También mantiene una rama intervenida separada de una línea base, mostrando que la comparación de estados requiere una construcción explícita.

El hecho de que después de una intervención aparezca y1 en s1 no demuestra por sí solo causalidad fuerte. Para una afirmación causal sería necesario especificar, según la teoría adoptada, condiciones de intervención, variables afectadas, mecanismo o modelo, posibles factores de confusión y el criterio mediante el cual el cambio se atribuye a la intervención.

Esos problemas quedan deliberadamente fuera de EXP-013 y serán tratados en los experimentos siguientes de la Fase 2.

## 7. Clasificación

**CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO.**

La estructura básica de una intervención no exige un quinto primitivo. La frontera aparece en la semántica que permite interpretar una transición como una intervención causal y atribuirle un efecto.

## 8. Criterio de cierre

El cierre formal requiere ejecución aislada, batería completa de experiments, git diff --check, verificación de que el núcleo no fue modificado y registro reproducible de los límites.

## 9. Conclusión

EXP-013 muestra que una intervención puede representarse constructivamente dentro de O/M/A/δ mediante un evento explícito, relaciones de objetivo y estados antes/después. La representación no convierte automáticamente el cambio en causalidad: la semántica fuerte de la intervención permanece como problema externo y verificable. No se justifica modificar el núcleo en esta etapa.

El siguiente paso es EXP-014 — confusión y contraejemplos, donde se someterá esta representación a casos en los que una asociación aparente puede persistir sin que exista el efecto causal que se pretende atribuir a la intervención.
