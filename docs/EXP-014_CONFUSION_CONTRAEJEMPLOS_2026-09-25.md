# EXP-014 — Confusión y contraejemplos

**Fecha:** 2026-09-25  
**Fase:** 2 — Causalidad fuerte  
**Estado:** cerrado; ejecución aislada y batería completa PASS, núcleo sin modificaciones.

## 1. Hipótesis

Una intervención y un cambio posterior pueden representarse en O/M/A/δ, pero una asociación observacional o un cambio coincidente no basta para atribuir el efecto a la intervención. Los factores de confusión pueden representarse explícitamente, mientras que la identificación causal fuerte requiere semántica y procedimientos adicionales.

## 2. Pregunta

¿La presencia de una asociación, un cambio posterior a una intervención y una estructura de confusión exige un nuevo primitivo del núcleo, o puede representarse todo mediante O/M/A/δ sin convertir automáticamente asociación en causalidad?

## 3. Diseño

Se prueban:

1. representación de un factor de confusión como O;
2. asociaciones explícitas entre confusor, exposición y resultado;
3. ausencia de inferencia automática de asociación a causalidad;
4. estructura de causa común sin conclusión causal automática;
5. caso donde existe cambio posterior a intervención pero también un factor asociado al resultado;
6. contraejemplo donde el mismo resultado aparece sin intervención;
7. comparación entre rama base y rama intervenida;
8. ausencia de semántica creada por el nombre confounds;
9. condicionamiento como procedimiento externo;
10. ausencia de nuevo primitivo.

No se modifica el núcleo, la especificación ni I1–I6.

## 4. Resultado

La estructura de confusión puede almacenarse directamente:

c ∈ O, associated_with(c,x) ∈ M, associated_with(c,y) ∈ M.

Una asociación x associated_with y no genera x causes y. Tampoco una intervención seguida de un cambio genera automáticamente una relación causes.

El experimento representa además dos ramas: una línea base sin intervención y otra con una intervención que produce un estado posterior. El resultado observado puede aparecer en ambas ramas, por lo que la simple secuencia “intervención → cambio” no basta para identificar el efecto atribuible a la intervención.

## 5. Contraejemplo central

Se construye un escenario con:

- exposición x;
- resultado y;
- confusor c;
- intervención i;
- estado posterior s1.

La rama intervenida contiene i targets x, i produces s1 y s1 has_outcome y. Sin embargo, también se representa una asociación del confusor con y.

En una segunda rama, el mismo resultado y aparece sin que exista una intervención. Esto constituye un contraejemplo estructural contra la regla simplista:

intervención + cambio posterior => causalidad demostrada.

El núcleo puede representar ambos escenarios, pero no decide cuál explicación causal es correcta.

## 6. Condicionamiento

Puede definirse externamente un procedimiento que seleccione o compare asociaciones bajo una condición dada por c. Esa operación es algorítmica: las relaciones originales siguen almacenadas en M y el núcleo no introduce una operación primitiva de control o ajuste.

Esto preserva la separación entre representación y semántica inferencial.

## 7. Límite

EXP-014 no pretende resolver identificación causal completa. Un modelo causal fuerte requeriría especificar qué significa exactamente confusión, qué variables deben controlarse, qué intervenciones son válidas y bajo qué condiciones una comparación identifica un efecto.

La conclusión relevante para MF_MIN es más acotada: la representación de los contraejemplos y de la estructura de confusión no exige un quinto primitivo.

## 8. Clasificación

**CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO.**

O, M, A y δ son suficientes para representar los elementos estructurales examinados. La atribución causal fuerte permanece fuera de la semántica intrínseca del núcleo.

## 9. Criterio de cierre

El cierre formal requiere ejecución aislada, batería completa, git diff --check, verificación de núcleo intacto y commit/push reproducible.

## 10. Conclusión

EXP-014 aporta un contraejemplo importante: una intervención puede preceder a un cambio y, aun así, la estructura disponible puede contener explicaciones alternativas o un resultado que también aparece sin intervención. Por ello, representación, asociación, intervención y atribución causal no deben colapsarse en una sola relación.

No se justifica modificar O/M/A/δ. El siguiente experimento será EXP-015 — composición causal condicionada, para estudiar hasta dónde puede formalizarse una composición causal explícita sin introducir un nuevo primitivo.
