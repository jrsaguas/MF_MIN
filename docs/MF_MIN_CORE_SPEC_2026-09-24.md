# MF_MIN — ESPECIFICACIÓN CANÓNICA DEL NÚCLEO
## Bloque A — Especificación formal

**Fecha de emisión:** 2026-09-25 02:36:33 UTC  
**Fecha local:** 2026-09-24 20:36:33 UTC−06:00  
**Baseline:** V7.1 — `283f0d9`  
**Publicación:** `0f536cd`

## 1. Propósito
Definir el núcleo conceptual de MF_MIN independientemente de sus capas de aplicación.

[
MF_{MIN}=langle O,M,A,deltaangle
]

Esta especificación no afirma que dicha ontología sea la única posible; establece el modelo formal de trabajo que deberá poder reproducirse independientemente de V7.1.

## 2. Estado y transición
Un estado es:
[
S=langle O,M,Aangle
]
donde (O) son objetos distinguibles, (M) relaciones semánticas y (A) restricciones/axiomas activos.

(delta) transforma estados:
[
delta(S,T)=S'
]

## 3. O — Objetos
(O) proporciona entidades distinguibles sobre las que pueden establecerse identidad, referencia y participación en relaciones:
[
o_iin O
]
La identidad y el valor son conceptualmente distintos:
[
id(o_i)
eq value(o_i)
]
Tipos, propiedades y congelamiento de valores presentes en V7.1 son decisiones operativas, no primitivas adicionales.

## 4. M — Relaciones
(M) expresa estructura entre objetos. Una relación elemental puede representarse como:
[
m=(s,p,o,pi)
]
con (s,oin O), predicado (p) y polaridad (pi).

Toda referencia debe ser válida. El mismo hecho no puede duplicarse bajo identificadores diferentes con la misma semántica.

## 5. A — Axiomas/restricciones
(A) contiene condiciones que restringen los estados admisibles o las transformaciones aceptables.

Conceptualmente:
[
A:mathcal Sightarrow{valid,invalid}
]

Una relación describe información del estado; una restricción determina condiciones de validez. Por ello (M
eq A), aunque ambos participen en la evaluación.

## 6. δ — Transición
(delta) proporciona transformación de estados:
[
delta:S	imes Tightarrow S
]
Una transición aceptada debe mantener referencias válidas, respetar restricciones y preservar invariantes. Las operaciones complejas pueden componerse de transiciones atómicas.

## 7. Invariantes I1–I6
- **I1 — Unicidad de identidad:** no existen dos objetos válidos con el mismo identificador.
- **I2 — Integridad referencial:** toda referencia formal apunta a una entidad existente.
- **I3 — No contradicción:** no coexisten afirmaciones incompatibles bajo la semántica de polaridad adoptada.
- **I4 — Unicidad semántica:** el mismo hecho no se duplica bajo identificadores diferentes.
- **I5 — Consistencia axiomática:** ningún estado aceptado viola una restricción activa.
- **I6 — Validez numérica:** los valores sometidos al dominio numérico permanecen en el dominio finito admitido.

Contrato global:
[
Sinmathcal S_{valid}land T validRightarrowdelta(S,T)inmathcal S_{valid}
]

## 8. Procedencia e inferencia
`origin`, `rule_id` y `premises` son metadatos de procedencia, no una quinta primitiva.

`EngineD` es una extensión de inferencia. Sus resultados pueden representarse en (M), pero el motor deductivo no modifica la ontología del núcleo.

## 9. Correspondencia con V7.1

| Formal | V7.1 |
|---|---|
| (O) | objetos del Kernel |
| (M) | `Relation` / estructura relacional |
| (A) | `AxiomConstraint` / validadores |
| (delta) | operaciones de transición del Kernel |
| I1–I6 | validaciones y pruebas |
| procedencia | `origin`, `rule_id`, `premises` |
| inferencia | `EngineD` |

Memoria, planificación, aprendizaje, percepción, epistemología, lenguaje, LLM, agentes, interfaz web y visualización son **extensiones**, no primitivas del núcleo.

## 10. No-afirmaciones
Esta especificación no afirma conciencia, inteligencia general, autonomía fuerte, aprendizaje universal, lenguaje fundamental, optimalidad matemática ni unicidad universal de esta ontología.

## 11. Criterio de conformidad
Una implementación conforme debe poder:
1. representar entidades distinguibles;
2. representar relaciones;
3. representar restricciones;
4. transformar estados;
5. preservar I1–I6;
6. verificar que las transiciones aceptadas producen estados válidos;
7. interpretar el núcleo sin depender de capas superiores de V7.1.

## 12. Estado del Bloque A
**ESPECIFICACIÓN CANÓNICA INICIAL — CERRADA PARA ESTA ETAPA.**

Toda modificación futura requiere revisión explícita de esta especificación.

**Siguiente:** Bloque B — cierre de irreducibilidad.
