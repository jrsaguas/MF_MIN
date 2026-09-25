# EXP-012 — Dependencia

**Fecha:** 2026-09-25  
**Fase:** 2 — Causalidad fuerte  
**Estado:** experimento construido; pendiente de cierre formal tras batería completa.

## 1. Hipótesis

Una afirmación de dependencia puede representarse como una relación de M entre objetos O. Sin embargo, una relación `depends_on` no constituye por sí misma una teoría causal fuerte ni autoriza inferencias de necesidad, intervención o contrafactualidad.

## 2. Pregunta

¿La dependencia requiere un nuevo primitivo del núcleo, o puede representarse mediante O/M/A/δ dejando su semántica fuerte a reglas y algoritmos explícitos?

## 3. Diseño

Se prueban:

1. representación de una dependencia;
2. composición estructural de dependencias;
3. ausencia de inferencia automática de causalidad;
4. ausencia de transitividad implícita;
5. separación respecto del orden temporal;
6. evidencia explícita sobre objetos relacionados;
7. ausencia de semántica creada por el nombre del predicado;
8. cierre algorítmico externo;
9. aplicación de la dependencia como transición ordinaria de δ.

No se modifica el núcleo, la especificación ni I1–I6.
## 4. Resultado experimental

La ejecución aislada produjo:

`12 passed in 0.05s`

Una dependencia `y depends_on x` se almacena como relación M. Una cadena `z depends_on y` y `y depends_on x` puede analizarse externamente para obtener una dependencia indirecta, pero `z depends_on x` no aparece automáticamente en M.

La existencia de `depends_on` tampoco genera una relación `causes`, ni una relación `before`. El núcleo conserva las afirmaciones sin atribuirles semántica causal adicional.

También puede representarse evidencia como otra relación entre una observación y el objeto cuya dependencia se estudia.
## 5. Contraejemplo y límite

Sin una restricción explícita, el sistema puede almacenar tanto `x depends_on y` como `y depends_on x`. Por tanto, el nombre `depends_on` no impone por sí mismo irreflexividad, asimetría, aciclicidad, necesidad o causalidad.

La dependencia fuerte queda abierta. Según la teoría elegida podría significar dependencia funcional, necesidad lógica, dependencia contrafactual, dependencia causal o una relación distinta. Este experimento no decide entre esas semánticas.

## 6. Clasificación

**CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO.**

La representación básica no justifica un quinto primitivo. La frontera relevante está en la semántica fuerte de dependencia, que debe someterse a experimentos posteriores antes de considerar cualquier modificación del núcleo.

## 7. Criterio de cierre

El cierre formal requiere batería completa, `git diff --check`, verificación de núcleo intacto y registro de los límites.

## 8. Conclusión

EXP-012 confirma una primera reducción constructiva: una afirmación de dependencia puede vivir dentro de O/M/A/δ como estructura relacional, mientras que sus propiedades fuertes deben ser explicitadas y comprobadas. El siguiente experimento, EXP-013, estudiará **intervención**, donde se podrá separar con mayor precisión una dependencia observacional de una modificación deliberada del sistema.
