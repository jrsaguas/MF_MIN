# EXP-008 — Orden temporal

**Fecha:** 2026-09-25
**Bloque:** Post-fundacional / Fase 1 — Temporalidad fuerte
**Estado:** PASS
**Objetivo:** determinar qué aspectos de un orden temporal pueden expresarse
con O/M/A/δ sin introducir un nuevo primitivo.

## 1. Hipótesis

Una colección de eventos puede representarse mediante O y relaciones
temporales explícitas mediante M. Las propiedades del orden pueden
comprobarse mediante A y/o algoritmos que operen sobre M. El predicado
"before" no recibe semántica universal por su nombre.

La pregunta no es si puede escribirse una palabra como "before", sino si
las propiedades estructurales relevantes pueden representarse, validarse
y derivarse sin añadir una quinta categoría ontológica.

## 2. Protocolo aplicado

El experimento usa exclusivamente la API pública del núcleo:
- Kernel
- Transition
- add_object
- add_relation
- add_axiom

No modifica mf_min_definitivo.py, invariantes I1-I6 ni ninguna otra pieza
del núcleo.

Se prueban: representación explícita, irreflexividad, asimetría,
transitividad, cierre transitivo algorítmico, restricción mediante A,
atomicidad de δ y ausencia de semántica automática por el nombre del
predicado.
## 3. Resultados observables

### 3.1 Representación

Los eventos e1, e2, e3 y e4 se representan como O.
Las relaciones e1 before e2 y e2 before e3 se representan como M.
No fue necesario ningún objeto o tipo primitivo temporal adicional.

**Resultado:** CORE-EXPRESSIBLE.

### 3.2 Propiedades estructurales

Irreflexividad y asimetría pueden evaluarse sobre el conjunto de relaciones.
No requieren una nueva categoría ontológica.

Sin embargo, evaluar una propiedad no significa que el núcleo la imponga
automáticamente. La distinción entre representación y semántica es central.

**Resultado:** CORE + ALGORITMO/RESTRICCIÓN.

### 3.3 Transitividad

Con e1 before e2 y e2 before e3, el almacenamiento de M no introduce
automáticamente e1 before e3.

Un algoritmo externo de cierre transitivo puede calcular esa consecuencia
usando únicamente las relaciones existentes. El estado del núcleo permanece
sin cambios hasta que una transición δ incorpore explícitamente el resultado.

**Resultado:** CORE + ALGORITMO.

### 3.4 Restricción por A

Un axioma con cláusula before(?x, ?x) permite rechazar una relación
reflexiva. El rechazo conserva el estado anterior, verificando además la
atomicidad de δ.

**Resultado:** CORE + RESTRICCIÓN.
## 4. Contraejemplo relevante

Se almacenaron simultáneamente e1 before e2 y e2 before e1 sin añadir
un axioma de asimetría. Esto fue aceptado estructuralmente.

Esto demuestra que el nombre "before" no constituye por sí mismo una
semántica universal de orden. La semántica fuerte debe estar expresada
mediante A, mediante un algoritmo o mediante reglas explícitas de uso.

## 5. Invariantes

El experimento conserva las invariantes I1-I6 del núcleo. En particular:
- no se crean IDs duplicados;
- las relaciones apuntan a objetos existentes;
- no se introducen contradicciones de polaridad;
- el rechazo de una transición no modifica el estado previo;
- no se altera el núcleo para hacer pasar el experimento.

## 6. Clasificación

**Conclusión provisional: CORE-EXPRESSIBLE + ALGORITMO/RESTRICCIÓN.**

La evidencia de EXP-008 no justifica un nuevo primitivo temporal.
El núcleo puede representar los elementos de un orden y, mediante A/δ y
algoritmos externos, comprobar o derivar propiedades del orden.

Esto no demuestra todavía que toda semántica temporal fuerte sea reducible
a O/M/A/δ. Quedan fuera de este experimento intervalos, duración,
simultaneidad, densidad temporal, relojes, persistencia y restricciones
temporales más ricas. Esos casos corresponden a los experimentos siguientes.
## 7. Evidencia reproducible

Prueba específica:

python -m pytest -q experiments/exp-008-orden-temporal

Resultado:

8 passed in 0.19s

El experimento se diseñó como prueba aislada y después debe ejecutarse
contra la batería completa de experiments.

## 8. Decisión

No modificar el núcleo MF_MIN.

EXP-008 aporta evidencia positiva de expresividad del núcleo para orden
temporal explícito, pero mantiene abierta la investigación de temporalidad
fuerte. El siguiente paso es EXP-009, intervalos y duración, sin alterar
la conclusión de este experimento.
