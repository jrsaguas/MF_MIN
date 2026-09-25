# EXP-026 — Conocimiento no monotónico y retractación
Fecha: 2026-09-25

## 1. Hipótesis

Un sistema de conocimiento no monotónico permite que una conclusión aceptada provisionalmente sea retirada cuando aparece nueva información, sin requerir una nueva primitiva ontológica en MF_MIN.

La pregunta de frontera es:
- ¿pueden representarse defaults y excepciones?
- ¿puede aparecer nueva información después de una conclusión derivada?
- ¿puede una conclusión ser retractada mediante delta?
- ¿puede una conclusión ser reinstalada?
- ¿la prioridad entre reglas pertenece al núcleo?

## 2. Representación evaluada

Se utilizaron únicamente:
- Object
- Relation
- AxiomConstraint
- Transition
- operaciones ordinarias de delta
- metadatos de procedencia de relaciones derivadas.

Los vocabularios normally_implies, exception_to y overrides_exception se trataron como predicados ordinarios. El nombre del predicado no activa razonamiento.
## 3. Resultados experimentales

### 3.1 Defaults

Una regla por defecto puede representarse como objetos y relaciones. La estructura de una regla no constituye por sí misma una inferencia.

### 3.2 Excepciones

Una excepción puede almacenarse como relación explícita. La ausencia de una excepción no se interpreta como prueba de que el default sea aplicable.

### 3.3 Inferencia externa

Una conclusión obtenida por una política no monotónica puede almacenarse como relación derivada con rule_id y premises.

La procedencia permite distinguir hecho original, conclusión derivada, regla productora y premisas utilizadas.

### 3.4 Retractación

Cuando aparece una excepción, un algoritmo externo puede eliminar una relación derivada mediante remove_relation.

La retractación no exige una nueva operación especial del núcleo: utiliza delta ya existente.
### 3.5 Reinstalación

Una conclusión retirada puede volver a representarse mediante una nueva relación derivada si una política externa determina que las condiciones cambiaron.

Esto permite modelar:

hecho → default → conclusión → excepción → retractación → nueva condición → reinstalación

sin introducir una quinta primitiva.

### 3.6 Conflictos y prioridad

Dos defaults o una regla y una excepción pueden coexistir.

MF_MIN no decide automáticamente:
- qué regla tiene prioridad;
- si una excepción derrota a un default;
- si una conclusión derrotada debe retirarse;
- qué lógica de prioridad utilizar;
- si la retractación debe propagarse a conclusiones dependientes.

Estas decisiones pertenecen a un algoritmo o semántica externa.
## 4. Distinciones críticas

### 4.1 Ausencia no es negación

Que no exista una relación positiva no crea automáticamente una relación negativa.

El supuesto de mundo cerrado, negación por defecto o razonamiento por falta de prueba requiere semántica externa.

### 4.2 Negación explícita no es ausencia

Una relación con polarity=False es evidencia negativa explícita. Continúa sometida al invariante I3: el mismo hecho positivo y negativo no pueden coexistir.

### 4.3 Retractación no es contradicción estructural

Eliminar una conclusión derivada porque dejó de ser defendible no equivale a insertar simultáneamente su versión positiva y negativa.

La retractación es un cambio de estado mediante delta.

### 4.4 Procedencia no es semántica no monotónica

rule_id y premises permiten registrar cómo se obtuvo una conclusión, pero no especifican por sí mismos cuándo debe retractarse.
## 5. Evidencia reproducible

Prueba aislada:
23 passed in 0.10s

Batería completa:
292 passed in 0.37s

git diff --check no reportó incidencias.

mf_min_definitivo.py no presentó cambios.

## 6. Clasificación

CORE-EXPRESSIBLE + ALGORITMO/SEMÁNTICA EXTERNA

El fenómeno no exige una nueva primitiva bajo el modelo actual.

La parte representacional pertenece a O/M/A/delta. La parte específicamente no monotónica —defaults, prioridades, negación por defecto, selección de extensiones, retractación propagada y reinstalación— queda fuera de la semántica intrínseca del núcleo.
## 7. Límite demostrado

EXP-026 no demuestra que toda lógica no monotónica pueda implementarse eficientemente sobre MF_MIN.

Demuestra una frontera más precisa:

> La estructura necesaria para representar defaults, excepciones, conclusiones provisionales y cambios de estado puede expresarse mediante O/M/A/delta; la semántica fuerte de razonamiento no monotónico permanece externa.

Por tanto, no hay evidencia para promover una quinta primitiva.

## 8. Implicación para Fase 5

EXP-026 refuerza el patrón observado en las fases anteriores:

representación en el núcleo → procesamiento mediante algoritmos externos → interpretación mediante semánticas externas → restricciones mediante axiomas → aplicación mediante delta.

La siguiente frontera relevante puede continuar con semántica modal/contrafactual, sistemas abiertos o identidad dinámica, manteniendo el mismo criterio de falsificación.
