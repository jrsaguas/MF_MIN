# EXP-010 — Persistencia y cambio

**Fecha:** 2026-09-25  
**Bloque:** Fase 1 — Temporalidad fuerte  
**Estado:** experimento construido; pendiente de cierre formal tras batería completa.

## 1. Hipótesis

La identidad de un objeto puede mantenerse entre estados sucesivos de S mediante el mismo identificador, mientras que el cambio puede representarse mediante nuevas relaciones u objetos en estados posteriores. Debe distinguirse entre persistencia representacional e historia temporal explícita. El núcleo ejecuta δ sobre estados, pero no mantiene automáticamente una línea temporal de todos los estados anteriores.

## 2. Pregunta

¿La persistencia de entidades y la representación del cambio exigen un nuevo primitivo temporal, o pueden expresarse con O/M/A/δ?

## 3. Diseño

Se prueban:
1. conservación del mismo identificador entre snapshots;
2. representación del cambio mediante nuevos valores relacionados con la misma entidad;
3. separación entre identidad y estado;
4. ausencia de mutación histórica implícita;
5. incorporación de orden temporal entre estados;
6. contraejemplo frente a la idea de que el nombre de un predicado crea semántica de persistencia.

No se modifica mf_min_definitivo.py, la especificación del núcleo ni los invariantes I1–I6.

## 4. Resultado

La identidad puede conservarse estructuralmente: el mismo objeto p1 aparece en estados sucesivos y las relaciones pueden asociarlo con diferentes objetos de estado.

El cambio puede representarse como una transición entre estados representados, por ejemplo has_state_at(p1,s1) y has_state_at(p1,s2), acompañada de before(s1,s2).

Sin embargo, el núcleo no posee por sí mismo un atributo history o timeline. Si se requiere conservar la secuencia completa de estados, esta historia debe almacenarse explícitamente mediante snapshots, relaciones u otra infraestructura externa.

## 5. Contraejemplo importante

El hecho de que dos estados estén relacionados con el mismo objeto no demuestra automáticamente:
- continuidad física o metafísica de la entidad;
- persistencia durante todo un intervalo;
- ausencia de estados intermedios;
- causalidad del cambio;
- una noción temporal intrínseca.

Estas propiedades requieren restricciones o semántica adicional.

## 6. Clasificación provisional

CORE-EXPRESSIBLE + INFRAESTRUCTURA/ALGORITMO.

La representación de identidad, estados, cambios y orden entre estados no justifica un quinto primitivo. La conservación de una historia completa es una capacidad de infraestructura construible sobre estados y transiciones, no una evidencia de un nuevo componente ontológico.

Esta conclusión está deliberadamente acotada: no afirma que toda teoría filosófica o física de persistencia sea reducible a O/M/A/δ.

## 7. Criterio de cierre

El experimento solo se considera cerrado después de:
- ejecución aislada reproducible;
- batería completa pytest experiments;
- git diff --check;
- revisión de que el núcleo no cambió;
- registro del resultado y limitaciones.

## 8. Preguntas abiertas

La Fase 1 todavía debe investigar:
- concurrencia;
- restricciones temporales entre múltiples eventos;
- persistencia con intervalos;
- simultaneidad;
- compatibilidad entre duración y cambio.

El siguiente experimento previsto es EXP-011 — concurrencia y restricciones temporales.

