# EXP-015 — Composición causal condicionada

**Fecha:** 2026-09-25  
**Estado:** cerrado; ejecución aislada PASS, batería completa PASS, núcleo sin modificaciones.

## 1. Hipótesis

Una composición causal condicionada puede representarse con O/M/A/δ, pero no debe inferirse automáticamente. La composición requiere una condición explícita y un procedimiento externo que aplique la regla.

## 2. Definición operacional

Se estudia una cadena `a causes b` y `b causes c`, junto con una condición `k required_for rule1`. La conclusión candidata es `a causes c`.

El experimento distingue tres cosas: representación de la cadena, disponibilidad de la condición y ejecución de la composición. La mera presencia de las primeras dos no hace que δ invente la conclusión.

## 3. Representación O/M/A/δ

- **O:** eventos `a`, `b`, `c`, condición `k` y regla `rule1`.
- **M:** relaciones `causes`, `required_for` y metadatos de procedencia.
- **A:** queda disponible para restringir estados válidos; no se añade semántica causal especial.
- **δ:** agrega premisas, condición y, cuando un procedimiento externo decide derivarla, la relación resultante.

Una relación derivada usa `origin=derived`, `rule_id` y `premises`; estos campos ya pertenecen al contrato operacional de M y no constituyen una quinta primitiva.

## 4. Pruebas

Se ejecutaron 16 pruebas aisladas.

Casos positivos:
- cadena causal explícita;
- condición explícita;
- representación de la regla;
- derivación condicionada explícita con procedencia completa;
- almacenamiento mediante una transición ordinaria.

Casos negativos/contraejemplos:
- la transitividad causal no aparece automáticamente;
- una condición ausente bloquea la composición;
- una condición de otro contexto no sustituye la requerida;
- el nombre de un predicado no crea semántica causal;
- incluso con condición presente, δ no inventa la conclusión.

## 5. Resultado

**Clasificación: CORE-EXPRESSIBLE + ALGORITMO/SEMÁNTICA EXTERNA.**

O/M/A/δ son suficientes para representar los elementos estructurales de la composición condicionada. La regla de composición, sus condiciones de aplicación y la validez causal fuerte pertenecen a una capa algorítmica/semántica externa.

El experimento no demuestra que toda teoría causal pueda reducirse a O/M/A/δ. Demuestra únicamente que este patrón de composición no exige una nueva primitiva en el modelo estudiado.

## 6. Conclusión de Fase 2

EXP-012–EXP-015 no justifican modificar `<O,M,A,δ>`. La fase cierra con una separación clara entre dependencia, intervención, confusión y composición condicionada.

**Decisión:** conservar el núcleo intacto y avanzar a Fase 3 — incertidumbre formal.

## 7. Reproducibilidad

Prueba aislada:

`python -m pytest -q experiments/exp-015-composicion-causal-condicionada/test_exp_015_composicion_causal_condicionada.py`

Resultado: `16 passed`.

Se verificará además la batería completa, `git diff --check` y la ausencia de cambios en `mf_min_definitivo.py` antes del commit.