# EXP-011 — Concurrencia y restricciones temporales

**Fecha:** 2026-09-25  
**Fase:** 1 — Temporalidad fuerte  
**Estado:** cerrado; ejecución aislada y batería completa PASS, núcleo sin modificaciones.

## 1. Hipótesis

La concurrencia, la simultaneidad y las restricciones temporales entre múltiples eventos pueden representarse mediante O/M/A/δ. Sus criterios semánticos no aparecen por el nombre de una relación ni por el orden de ejecución de δ: requieren relaciones explícitas, algoritmos o restricciones.

## 2. Pregunta

¿La concurrencia y las restricciones temporales exigen un nuevo primitivo del núcleo, o pueden expresarse como objetos, relaciones, axiomas y transiciones sobre estados existentes?

## 3. Diseño

Se prueban, de forma aislada:

1. ausencia de inferencia automática de concurrencia;
2. representación explícita de concurrencia;
3. representación explícita de simultaneidad;
4. separación entre tiempo del dominio y orden de ejecución de δ;
5. almacenamiento de múltiples restricciones en M;
6. validación algorítmica de restricciones;
7. rechazo de una restricción reflexiva mediante A;
8. atomicidad de δ ante rechazo;
9. ausencia de semántica creada solo por el nombre del predicado.

No se modifica `mf_min_definitivo.py`, la especificación del núcleo ni I1–I6.
## 4. Resultado experimental

La ejecución aislada produjo:

`11 passed in 0.06s`

La evidencia muestra que dos eventos sin una relación temporal explícita no pueden clasificarse automáticamente como concurrentes. Del mismo modo, `simultaneous` y `concurrent_with` pueden representarse como relaciones M ordinarias sin introducir una estructura ontológica adicional.

El orden de ejecución de δ tampoco aporta por sí mismo una semántica temporal al dominio. Dos eventos pueden declararse simultáneos o independientes sin que exista una relación `before` entre ellos.

Las restricciones pueden expresarse como propiedades verificables sobre M o como axiomas A. El axioma de irreflexividad utilizado en el experimento rechaza `before(e1,e1)` y la transición rechazada no altera el estado previo.
## 5. Contraejemplos y límites

La representación estructural no equivale a una teoría temporal completa. En particular, almacenar `concurrent_with(e1,e2)` no demuestra una definición universal de concurrencia.

Tampoco se debe confundir la secuencialidad de la implementación de δ con la temporalidad de los eventos modelados.

Una relación `before(e1,e2)` seguida de `before(e2,e1)` puede almacenarse si no existe una restricción de aciclicidad/asimetría. Esto demuestra que el nombre del predicado no impone semántica por sí solo.

El experimento no resuelve aún:
- concurrencia física;
- simultaneidad relativista;
- relojes y sincronización;
- tiempo continuo/discreto;
- consistencia global de calendarios;
- semánticas temporales modales.
## 6. Clasificación

**CORE-EXPRESSIBLE + ALGORITMO/RESTRICCIÓN.**

La evidencia obtenida no justifica un quinto primitivo. Los eventos son O; las relaciones de orden, concurrencia y simultaneidad son M; las condiciones de consistencia pueden formularse en A; y δ aplica/rechaza cambios de estado de manera atómica.

Las propiedades más fuertes de concurrencia quedan deliberadamente como semántica o algoritmos externos hasta que una prueba de límite reproducible demuestre lo contrario.

## 7. Criterio de cierre

Para el cierre formal de EXP-011 se requiere:

- ejecución aislada reproducible;
- batería completa `pytest experiments`;
- `git diff --check`;
- verificación de que el núcleo no cambió;
- registro final del resultado y limitaciones.

## 8. Conclusión

EXP-011 no encuentra evidencia de una necesidad de ampliar `<O,M,A,δ>`. La frontera observada sigue siendo entre representación estructural, por un lado, y semántica temporal fuerte/algoritmos de restricción, por otro.

Con EXP-008, EXP-009, EXP-010 y EXP-011 queda cubierta la primera fase experimental prevista. La revisión conjunta de Fase 1 debe evitar convertir estos resultados locales en una afirmación universal sobre toda teoría del tiempo.
