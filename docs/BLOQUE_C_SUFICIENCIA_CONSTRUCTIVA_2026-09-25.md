# MF_MIN — BLOQUE C: SUFICIENCIA CONSTRUCTIVA

**Fecha de emisión:** 2026-09-25 02:46:00 UTC  
**Fecha local:** 2026-09-24 20:46:00 UTC−06:00  
**Baseline:** V7.1 — `283f0d9`  
**Núcleo evaluado:** `MF_MIN = <O,M,A,δ>`

---

## 1. Propósito

El Bloque C determina qué capacidades pueden construirse sobre el núcleo MF_MIN sin introducir un quinto primitivo.

La pregunta no es:

> “¿El sistema V7.1 ya tiene una implementación para esta capacidad?”

La pregunta es:

> “¿Puede expresarse la semántica necesaria utilizando únicamente objetos, relaciones, restricciones y transiciones?”

Se separan tres niveles:

1. **Representación:** el fenómeno puede expresarse mediante `O,M,A,δ`.
2. **Algoritmo:** hace falta un procedimiento externo para calcular, buscar u operar sobre esa representación.
3. **Primitiva:** el fenómeno requiere semántica fundamental adicional que no puede reducirse al núcleo sin simplemente cambiar de ubicación el mismo concepto.

Por tanto, que una capacidad requiera un algoritmo no implica que requiera un nuevo componente fundamental.

---

## 2. Método

Para cada capacidad se aplicó el siguiente esquema conceptual:

```
fenómeno
   ↓
representación mínima con O, M, A
   ↓
transformaciones mediante δ
   ↓
comprobación de invariantes I1–I6
   ↓
separación representación / algoritmo / semántica adicional
   ↓
clasificación
```

La evidencia se tomó de la especificación canónica del núcleo y de la implementación V7.1 publicada en el repositorio.

No se modificó el núcleo para obtener los resultados.

---

## 3. Categorías de resultado

### CORE-EXPRESSIBLE

La capacidad puede expresarse directamente mediante las estructuras del núcleo y sus transiciones.

### CORE + ALGORITMO

La semántica puede permanecer dentro de `O,M,A,δ`, pero se necesita un procedimiento externo para calcularla o explotarla.

### EXTENSIÓN JUSTIFICADA

Aparece una semántica adicional que no está definida por el núcleo actual. Esto no autoriza automáticamente a introducir un nuevo primitivo: primero debe convertirse en un experimento controlado de los Bloques D/E.

### INDETERMINADA

La representación disponible permite hipótesis plausibles, pero no existe evidencia suficiente para decidir de forma rigurosa.

---

# 4. Matriz de suficiencia

| Capacidad | Representación con O/M/A/δ | Algoritmo adicional | Resultado |
|---|---|---|---|
| Identidad | Objeto con identidad distinguible | No | **CORE-EXPRESSIBLE** |
| Relación | Relación entre objetos | No | **CORE-EXPRESSIBLE** |
| Estado | S = <O,M,A> | No | **CORE-EXPRESSIBLE** |
| Cambio | δ(S,T)=S' | No | **CORE-EXPRESSIBLE** |
| Memoria | Estado persistido/histórico como objetos y relaciones | Persistencia/retrieval | **CORE + ALGORITMO** |
| Secuencia / tiempo | Estados y relaciones ordenadas + δ | Reloj/ordenador temporal | **CORE + ALGORITMO / INDETERMINADA** |
| Causalidad | Relaciones, restricciones y transiciones | Análisis causal/procedencia | **INDETERMINADA** |
| Regla | Estructura relacional/objetos + restricciones | Motor de inferencia | **CORE + ALGORITMO** |
| Incertidumbre | Puede codificarse como información sobre objetos/relaciones | Semántica cuantitativa/calibración | **INDETERMINADA** |
| Planificación | Espacio de estados generado por δ | Búsqueda | **CORE + ALGORITMO** |
| Aprendizaje | Cambios sobre estados/reglas | Algoritmo de actualización | **CORE + ALGORITMO / INDETERMINADA** |

---

# 5. Experimento C1 — Identidad

## Hipótesis

MF_MIN debe poder distinguir dos entidades aunque posean valores iguales.

## Representación

Sean:

```
o1 = Object(id="a", type="item", value=10)
o2 = Object(id="b", type="item", value=10)
```

La identidad pertenece al objeto y no se reduce a igualdad de valor.

## Evidencia en V7.1

La implementación de `Object` exige un identificador no vacío y conserva separadamente `id`, `type`, `value` y `properties`.

La existencia de `I1` garantiza unicidad de identidad.

## Resultado

**CORE-EXPRESSIBLE.**

No se necesita un quinto componente.

---

# 6. Experimento C2 — Relación

## Hipótesis

MF_MIN debe poder representar información estructural entre entidades.

## Representación

```
m = (source, predicate, target, polarity)
```

con referencias a objetos de `O`.

Ejemplo:

```
pieza_A --pertenece_a--> lote_1
```

## Restricciones

`I2` garantiza integridad referencial y `I4` evita duplicación semántica del mismo hecho.

## Resultado

**CORE-EXPRESSIBLE.**

La relación es precisamente el papel asignado a `M`.

---

# 7. Experimento C3 — Estado

## Hipótesis

El núcleo debe poder representar una configuración completa del sistema.

## Representación

```
S = <O,M,A>
```

donde:

- `O` contiene las entidades;
- `M` contiene las relaciones;
- `A` contiene las restricciones activas.

## Resultado

**CORE-EXPRESSIBLE.**

El estado no requiere un nuevo primitivo porque ya es la estructura formal del núcleo.

---

# 8. Experimento C4 — Cambio

## Hipótesis

El sistema debe poder transformar un estado válido en otro.

## Representación

```
δ(S,T) = S'
```

donde `T` especifica una transición.

Una operación puede agregar, eliminar o modificar elementos siempre que el estado resultante conserve las condiciones del núcleo.

## Resultado

**CORE-EXPRESSIBLE.**

La transformación no necesita un componente separado de cambio: está definida por `δ`.

---

# 9. Experimento C5 — Memoria

## Hipótesis

Un sistema debe poder conservar información acerca de estados o acontecimientos anteriores.

## Reducción

Un acontecimiento puede convertirse en una entidad:

```
evento_17 ∈ O
```

y sus características pueden expresarse mediante relaciones:

```
evento_17 --ocurrio_en--> estado_5
evento_17 --afecta_a--> objeto_A
```

Una colección persistente de tales estructuras puede conservar información histórica.

## Distinción fundamental

El núcleo puede **representar** memoria.

La persistencia física en disco, una base de datos, índices de recuperación o una política de olvido son mecanismos de implementación.

Por tanto:

**Representación:** posible con el núcleo.

**Persistencia/retrieval:** algoritmo o infraestructura externa.

## Resultado

**CORE + ALGORITMO.**

No existe evidencia suficiente para declarar `Memory` como quinto primitivo.

---

# 10. Experimento C6 — Secuencia y tiempo

## Hipótesis

Debe poder representarse que un estado ocurrió antes o después de otro.

## Representación posible

Los estados o acontecimientos pueden convertirse en objetos y relacionarse:

```
evento_1 --precede--> evento_2
```

También puede representarse un valor temporal:

```
instante_1.value = 100
instante_2.value = 101
```

y una transición:

```
δ(S_1,T_1)=S_2
δ(S_2,T_2)=S_3
```

## Límite

Esto demuestra representabilidad de orden temporal, no que MF_MIN contenga una teoría fundamental del tiempo.

Un reloj físico, sincronización, duración continua o semántica temporal avanzada pertenecen a capas adicionales.

## Resultado

**CORE + ALGORITMO / INDETERMINADA.**

No se justifica introducir `Time` como quinto primitivo en esta etapa.

---

# 11. Experimento C7 — Causalidad

## Hipótesis

Puede existir una relación entre condiciones y cambios de estado.

## Representación mínima

Una transición puede depender de relaciones presentes en un estado:

```
condición(S) → δ(S,T)=S'
```

Las condiciones pueden expresarse mediante `M` y `A`.

La implementación V7.1 también conserva información de procedencia en relaciones derivadas, pero dicha procedencia está explícitamente clasificada como metadata y no como quinto primitivo.

## Límite

Representar:

> “X fue una condición de la transición Y”

no equivale automáticamente a demostrar causalidad en sentido filosófico, científico o contrafactual.

La causalidad requiere una semántica adicional que permita distinguir dependencia causal de mera correlación o precedencia.

## Resultado

**INDETERMINADA.**

La representación estructural es posible, pero no se ha demostrado que la semántica causal completa sea reducible al núcleo.

Esto queda como candidato para un experimento posterior, no como nuevo primitivo.

---

# 12. Experimento C8 — Regla

## Hipótesis

Una regla puede describirse como una estructura que relaciona condiciones con una conclusión.

## Representación

Conceptualmente:

```
condiciones → conclusión
```

Las condiciones pueden corresponder a relaciones de `M`, y su admisibilidad puede expresarse mediante `A`.

El procesamiento de reglas puede realizarse mediante un algoritmo externo.

## Evidencia V7.1

`EngineD` está deliberadamente fuera del núcleo y depende de él:

```
EngineD → MF_MIN
```

Esto constituye una separación arquitectónica clara entre representación formal e inferencia.

## Resultado

**CORE + ALGORITMO.**

La existencia de `EngineD` no demuestra que inferencia sea un quinto primitivo.

---

# 13. Experimento C9 — Incertidumbre

## Hipótesis

Puede ser necesario representar información cuyo grado de confianza no sea binario.

## Representación candidata

Puede construirse un objeto que contenga un valor cuantitativo:

```
belief_1.value = 0.72
```

y relacionarlo con una proposición:

```
belief_1 --about--> fact_1
```

Por tanto, existe una codificación estructural posible.

## Límite

Codificar el número `0.72` no define por sí mismo qué significa:

- probabilidad;
- confianza subjetiva;
- frecuencia;
- posibilidad;
- credibilidad;
- error de medición.

La semántica cuantitativa de incertidumbre no está definida por `O,M,A,δ`.

## Resultado

**INDETERMINADA.**

Se necesita un experimento formal específico antes de decidir si la incertidumbre es una extensión semántica necesaria o simplemente una estructura representable más un algoritmo.

---

# 14. Experimento C10 — Planificación

## Hipótesis

Planificar significa encontrar una secuencia de transiciones que conduzca de un estado inicial a un estado objetivo.

## Reducción

Si:

```
δ(S_0,T_1)=S_1
δ(S_1,T_2)=S_2
...
δ(S_n,T_n)=S_goal
```

entonces una secuencia de transiciones constituye un plan candidato.

La búsqueda de esa secuencia puede realizarse mediante BFS, DFS, A*, programación dinámica u otros algoritmos.

## Resultado

**CORE + ALGORITMO.**

La planificación no necesita convertirse en una quinta primitiva porque su espacio semántico está determinado por estados y transiciones.

---

# 15. Experimento C11 — Aprendizaje

## Hipótesis

Aprender puede entenderse como modificación del estado interno a partir de experiencia.

## Reducción

Una experiencia puede representarse como objetos y relaciones:

```
experiencia → O,M
```

Una transición puede producir un nuevo estado:

```
δ(S, experiencia) = S'
```

Si las reglas o parámetros forman parte del estado representado, pueden existir transiciones que los modifiquen bajo restricciones.

## Límite

Esto establece representabilidad de cambios derivados de experiencia.

No demuestra que cualquier algoritmo de aprendizaje, aprendizaje estadístico, generalización o descubrimiento autónomo pueda expresarse eficientemente mediante el núcleo.

## Resultado

**CORE + ALGORITMO / INDETERMINADA.**

No se introduce `Learning` como primitivo.

---

# 16. Resultado global

Los experimentos producen tres observaciones importantes.

## 16.1 El núcleo tiene una expresividad considerable

Las capacidades básicas:

```
identidad
relación
estado
cambio
```

son directamente expresables.

Varias capacidades de nivel superior pueden construirse como algoritmos sobre esas estructuras:

```
memoria
reglas
planificación
aprendizaje
```

Esto es importante porque evita confundir una capacidad operacional con una primitiva ontológica.

## 16.2 Hay fronteras reales de semántica

Dos áreas no deben darse por resueltas:

```
causalidad
incertidumbre
```

En ambas puede existir una codificación estructural dentro de `O,M,A`, pero todavía no está demostrado que la semántica específica quede completamente definida por el núcleo.

Por ello se clasifican como **INDETERMINADAS**, no como fracasos ni como nuevos componentes.

## 16.3 No aparece evidencia para ampliar el núcleo

Durante este bloque no se encontró una capacidad que obligue a establecer formalmente:

```
MF_MIN = <O,M,A,δ,X>
```

con un quinto primitivo `X`.

Por tanto, la hipótesis de trabajo permanece:

```
MF_MIN = <O,M,A,δ>
```

como **mínimo operativo bajo la semántica actual**.

---

# 17. Límites de la conclusión

Este bloque NO demuestra:

- que `O,M,A,δ` sea universalmente suficiente para toda inteligencia;
- que cualquier algoritmo pueda implementarse eficientemente sobre el núcleo;
- que causalidad sea reducible al núcleo;
- que incertidumbre sea reducible al núcleo;
- que MF_MIN sea computacionalmente óptimo;
- que no exista otra ontología mínima equivalente;
- que el núcleo constituya una teoría de conciencia, inteligencia general o autonomía.

La conclusión es deliberadamente más estrecha:

> Dentro del modelo formal actualmente definido, las capacidades estudiadas pueden representarse o abordarse sin haber demostrado la necesidad de un quinto primitivo.

---

# 18. Criterio de cierre del Bloque C

El Bloque C se considera cerrado cuando:

1. Las capacidades principales tienen una clasificación explícita.
2. Se separó representación de algoritmo.
3. Se registraron límites y casos indeterminados.
4. No se introdujeron primitivas nuevas únicamente para aumentar funcionalidades.
5. Las conclusiones no exceden la evidencia disponible.

Los casos **INDETERMINADOS** pasan a experimentos específicos de los Bloques D/E solamente si existe una pregunta concreta que pueda falsar o fortalecer la hipótesis.

No se realizarán nuevas pruebas genéricas de suficiencia sin nueva evidencia o una objeción formal.

---

# 19. Decisión

**BLOQUE C — CERRADO PARA ESTA ETAPA.**

Estado del núcleo:

```
MF_MIN = <O,M,A,δ>
```

Clasificación global:

```
CORE-EXPRESSIBLE
    identidad
    relación
    estado
    cambio

CORE + ALGORITMO
    memoria
    reglas
    planificación
    aprendizaje

INDETERMINADA
    causalidad
    incertidumbre
    semántica temporal fuerte
```

No se justifica agregar un quinto primitivo en este momento.

**Siguiente bloque:** D — Reclasificación de V7.1.

El objetivo de D será separar formalmente lo que pertenece al núcleo de todo aquello que V7.1 construyó encima de él, sin borrar ni invalidar ese trabajo.
