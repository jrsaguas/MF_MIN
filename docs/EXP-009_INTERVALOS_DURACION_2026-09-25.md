# EXP-009 — Intervalos y duración

**Fecha:** 2026-09-25  
**Bloque:** Fase 1 — Temporalidad fuerte  
**Estado:** cerrado; ejecución aislada y batería completa PASS, núcleo sin modificaciones.

## 1. Hipótesis

Un intervalo temporal puede representarse usando únicamente objetos y relaciones del núcleo O/M/A/δ: el intervalo, sus extremos y un dato de duración pueden ser objetos; las conexiones entre ellos pueden ser relaciones. Debe distinguirse entre **representar datos temporales** y **atribuirles semántica temporal fuerte**. Calcular duración a partir de extremos, imponer unidades, positividad, aditividad o reglas de composición puede requerir algoritmos o restricciones externas.

## 2. Pregunta

¿La representación de intervalos y duración exige un nuevo primitivo del núcleo, o puede mantenerse dentro de O/M/A/δ con algoritmos y restricciones adicionales?

## 3. Diseño

Se prueban cinco niveles:

1. intervalo como objeto;
2. inicio y fin como objetos relacionados con el intervalo;
3. duración como objeto con valor numérico;
4. operaciones externas sobre valores, como diferencia y suma;
5. composición de intervalos y propiedades semánticas, evitando asumir que el nombre de un predicado crea significado.

El experimento no modifica mf_min_definitivo.py, los invariantes I1–I6 ni la especificación del núcleo.

## 4. Representación

- O: objetos interval, event, time_point y duration;
- M: relaciones starts_at, ends_at y has_duration;
- A: no se introduce una nueva clase de axioma;
- δ: se usa para incorporar objetos y relaciones.

## 5. Resultados esperados

### 5.1 Representación

Debe ser posible almacenar un intervalo con inicio, fin y duración sin introducir un quinto componente.

### 5.2 Duración

Un número puede almacenarse como valor de un objeto. Esto no demuestra que el núcleo conozca por sí mismo unidades, resta temporal, positividad o aditividad.

### 5.3 Cálculo

Operaciones como 15 - 10 = 5 y 5 + 7 = 12 pueden ejecutarse externamente sobre valores ya representados. El resultado no aparece espontáneamente en M.

### 5.4 Composición

Dos intervalos pueden compartir un extremo mediante relaciones. La adyacencia o composición de intervalos no debe aparecer automáticamente solo porque dos relaciones compartan un objeto.

## 6. Contraejemplo buscado

Una estructura con starts_at(i1,s1) y ends_at(i1,e1) no determina por sí sola:

- que s1 ocurra antes que e1;
- que exista una unidad temporal;
- que la duración sea positiva;
- que la duración sea t(e1)-t(s1);
- que dos intervalos consecutivos formen un intervalo compuesto.

Si estas propiedades son necesarias, deben expresarse mediante relaciones, restricciones o algoritmos explícitos.

## 7. Clasificación provisional

**CORE-EXPRESSIBLE + ALGORITMO/RESTRICCIÓN.**

La representación estructural de intervalos y valores de duración no justifica un nuevo primitivo. La semántica temporal fuerte de duración queda abierta a una caracterización algorítmica/restrictiva.

Esto no permite concluir todavía que toda teoría de intervalos sea reducible a O/M/A/δ. Quedan por investigar persistencia, cambio, concurrencia, unidades, intervalos abiertos/cerrados, duración indeterminada y composición temporal más rica.

## 8. Criterio de cierre

El experimento solo se considera cerrado después de:

- ejecución aislada reproducible;
- batería completa pytest experiments;
- git diff --check;
- revisión de que el núcleo no cambió;
- registro del resultado y limitaciones.

## 9. Fuera de alcance

No se modifican:

- mf_min_definitivo.py;
- invariantes I1–I6;
- MF_MIN_CORE_SPEC;
- APIs del núcleo;
- módulos cognitivos o de agentes;
- interfaz web.
