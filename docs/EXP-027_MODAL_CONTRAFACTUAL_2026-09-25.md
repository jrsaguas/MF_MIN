# EXP-027 — Semántica modal y contrafactual
Fecha: 2026-09-25

## 1. Hipótesis

Las estructuras necesarias para representar mundos posibles, accesibilidad, proposiciones, antecedentes y resultados contrafactuales pueden expresarse mediante O/M/A/delta. La semántica fuerte de posibilidad, necesidad y contrafactualidad permanece externa.

## 2. Estructuras evaluadas

Se representaron:
- mundos posibles como objetos;
- proposiciones como objetos;
- accesibilidad entre mundos como relaciones;
- hechos que sostienen proposiciones en un mundo;
- antecedentes de escenarios alternativos;
- resultados contrafactuales;
- procedencia de resultados derivados.

Los predicados possibly, necessarily, counterfactual, accessible_to, assumes y would_hold no activan razonamiento por su nombre.

## 3. Resultados

### 3.1 Mundos y accesibilidad

Puede construirse una estructura de mundos y relaciones de accesibilidad sin una primitiva modal adicional.

La relación de accesibilidad no determina por sí sola qué proposiciones son verdaderas en los mundos accesibles.

### 3.2 Posibilidad y necesidad

Posibilidad y necesidad pueden almacenarse como relaciones distintas.

El núcleo no determina:
- qué mundos son relevantes;
- si una proposición es verdadera en todos los mundos accesibles;
- si es verdadera en alguno;
- qué marco modal utilizar.

Estas son decisiones semánticas externas.

### 3.3 Contrafactuales

Un escenario alternativo puede representarse mediante:
actual → mundo alternativo → antecedente → consecuente.

Un algoritmo externo puede producir una conclusión derivada con rule_id y premises.

Esto no convierte la relación counterfactual en una implicación material automática.

### 3.4 Selección de mundos

Cuando existen varios mundos alternativos, la selección del escenario relevante requiere una política externa.

También son externas las nociones de:
- cercanía entre mundos;
- semejanza;
- mínima revisión;
- condiciones de evaluación;
- preferencia entre escenarios.

## 4. Invariantes y límites

La estructura modal continúa sometida a los invariantes existentes, incluida la unicidad de identificadores y la prohibición de contradicción exacta.

La presencia de mundos alternativos permite representar divergencias sin introducir una contradicción estructural en un mismo hecho.

EXP-027 no demuestra que cualquier lógica modal o sistema contrafactual pueda implementarse eficientemente sobre el núcleo. Demuestra que su estructura representacional básica no obliga a introducir una quinta primitiva.

## 5. Evidencia reproducible

Prueba aislada: 22 passed.

Batería completa: 314 passed.

git diff --check: limpio.

mf_min_definitivo.py: sin modificaciones.

## 6. Clasificación

**CORE-EXPRESSIBLE + ALGORITMO/SEMÁNTICA EXTERNA**

El patrón vuelve a ser:

representación en O/M/A → procesamiento externo → interpretación semántica externa → restricciones mediante A → cambio de estado mediante delta.

No aparece evidencia de una nueva primitiva ontológica.

## 7. Frontera abierta

La siguiente dificultad relevante es distinguir la mera representación de escenarios abiertos de una semántica completa de sistemas abiertos y observación parcial. Esa frontera puede evaluarse en EXP-028.
