# EXP-025 — Cuantificacion y variables

**Estado:** cerrado.

## Hipotesis

Variables, dominios, alcance de variables y afirmaciones cuantificadas pueden representarse como objetos y relaciones. La semantica de satisfaccion, instanciacion y prueba puede permanecer en un algoritmo externo.

## Resultado

Ejecucion aislada: **14 passed**.

Bateria completa: **269 passed**.

Se representaron variables, dominios, predicados, formulas, alcance, vinculacion, testigos, contraejemplos y derivaciones con procedencia.

El nombre de una relacion como for_all o exists no activa inferencia por si mismo. La instanciacion puede registrarse como una relacion derivada con rule_id y premises.

Un primer intento fallo porque se uso una relacion hacia un ID que no era un objeto y porque el contrato real de A exige name. Esos fallos fueron del experimento, no del nucleo, y se corrigieron respetando los contratos existentes.

## Limite

El experimento demuestra representabilidad estructural y deja la semantica cuantificacional en el nivel externo. No demuestra que toda logica cuantificacional, semantica de primer orden o razonamiento de segundo orden pueda implementarse eficientemente sobre el nucleo.

## Clasificacion

**CORE-EXPRESSIBLE + ALGORITMO/SEMANTICA EXTERNA.**

No aparece evidencia de una quinta primitiva.

## Integridad

`mf_min_definitivo.py` no fue modificado. I1–I6 permanecen vigentes.
