# EXP-029 — Identidad dinámica y referencia bajo transformación
Fecha: 2026-09-25

## 1. Hipótesis

MF_MIN separa la identidad de un objeto de su valor y de las relaciones que lo describen. Esta prueba evalúa si esa separación continúa siendo suficiente cuando existen transformaciones, nuevas representaciones, composición cambiante y referencias que pueden retargetearse.

## 2. Estructuras evaluadas

Se representaron:
- identidad persistente mediante Object.id;
- valores y representaciones;
- transformación entre objetos;
- referencias;
- alias;
- composición de sistemas;
- relaciones same_as y represents;
- retargeting de referencias mediante delta;
- procedencia de equivalencias derivadas;
- snapshots de estado.

## 3. Resultados

### 3.1 Identidad frente a valor

El identificador permanece separado del valor almacenado. Los snapshots conservan el estado anterior, mientras que un estado posterior puede contener nuevas representaciones.

No se requiere mutación in-place para modelar cambio.

### 3.2 Transformación

Una transformación puede representarse como relación entre estados u objetos.

La existencia de transformed_to no implica automáticamente same_as. La equivalencia de identidad requiere una política externa.

### 3.3 Referencias

Una referencia puede apuntar a un objeto y posteriormente retargetearse mediante remove_relation + add_relation.

El retargeting utiliza delta existente.

### 3.4 Composición

La composición de un sistema puede cambiar agregando o retirando relaciones de composición sin sustituir el objeto que representa al sistema.

### 3.5 Identidad derivada

Una política externa puede derivar same_as con rule_id y premises. El núcleo almacena la conclusión y su procedencia, pero no decide qué criterio establece identidad.

## 4. Distinciones críticas

### Identidad ≠ valor

Cambiar una representación o valor no obliga a crear una nueva identidad.

### Identidad ≠ referencia

Una referencia puede cambiar de objetivo sin que desaparezca la identidad del objeto referido.

### Transformación ≠ equivalencia

Dos objetos relacionados por una transformación no son automáticamente el mismo objeto.

### Equivalencia ≠ ontología intrínseca

El predicado same_as no activa por sí mismo una política de identidad.

### Composición ≠ identidad

Cambiar las partes de un sistema no obliga al núcleo a redefinir automáticamente su identidad.

## 5. Evidencia reproducible

Prueba aislada: 24 passed.

Batería completa: 364 passed.

git diff --check: limpio.

mf_min_definitivo.py: sin modificaciones.

## 6. Clasificación

**CORE-EXPRESSIBLE + ALGORITMO/SEMÁNTICA EXTERNA**

La separación identidad/valor/referencia se mantiene sin introducir una quinta primitiva.

Las políticas fuertes de identidad dinámica —criterios de continuidad, identidad a través del tiempo, identidad de objetos compuestos, equivalencia entre representaciones y resolución de referencias rotas— permanecen externas.

## 7. Límite demostrado

EXP-029 no demuestra que toda teoría de identidad o persistencia pueda reducirse eficientemente a O/M/A/delta.

Demuestra que los casos estructurales examinados pueden representarse preservando la identidad mediante IDs, relaciones y snapshots, mientras que los criterios semánticos de identidad permanecen externos.

## 8. Estado de Fase 5

EXP-025 a EXP-029 han cubierto, respectivamente:
- cuantificación y variables;
- conocimiento no monotónico;
- modalidad y contrafactualidad;
- sistemas abiertos y observación parcial;
- identidad dinámica y referencia.

En los cinco casos no apareció evidencia reproducible que obligue a introducir una quinta primitiva.

La siguiente frontera relevante puede ser la representación de estructuras infinitas/no finitas y, posteriormente, una síntesis formal de los límites de Fase 5.
