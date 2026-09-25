# EXP-016 — Soporte y evidencia

**Fecha:** 2026-09-25  
**Estado:** cerrado; ejecución aislada y batería completa PASS, núcleo sin modificaciones.

## Hipótesis

El soporte/evidencia puede representarse mediante O/M/A/δ sin introducir una quinta primitiva. El núcleo, sin embargo, no convierte por sí mismo `supports` en probabilidad, peso, confianza o creencia actualizada.

## Diseño

Se representan observaciones e hipótesis como O y relaciones `supports` como M. La polaridad permite evidencia positiva o negativa explícita, respetando I3. La procedencia de una afirmación derivada se conserva mediante `premises` y `rule_id`, sin convertir la procedencia en una nueva primitiva.

El experimento también verifica que ausencia de evidencia no equivale a evidencia negativa y que una restricción A puede limitar configuraciones sin añadir un componente ontológico nuevo.

## Resultado esperado

Si todas las capacidades estructurales pasan, la clasificación será **CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO**. Quedarán fuera del núcleo el peso cuantitativo de evidencia, probabilidad, confianza y actualización de creencias.

## Protocolo

Se ejecutará prueba aislada, batería completa, `git diff --check` y verificación explícita de que `mf_min_definitivo.py` permanezca sin cambios.
