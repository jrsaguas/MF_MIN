# PLAN DE INVESTIGACIÓN POST-FUNDACIONAL MF_MIN — 2026-09-25

**Baseline:** commit 350dcad  
**Núcleo:** MF_MIN = ⟨O,M,A,δ⟩  
**Estado:** A–F cerrados  
**Objetivo:** determinar los límites semánticos del núcleo sin ampliarlo por anticipación.

## 1. Punto de partida

La etapa A–F ya estableció el núcleo operativo de trabajo, las capacidades construidas sobre él y el procedimiento para justificar una eventual modificación.

La siguiente etapa será de **investigación de fronteras**, no de expansión funcional.

Pregunta central:

> ¿Qué fenómenos aparentemente requieren semántica adicional y cuáles pueden seguir expresándose mediante O, M, A y δ sin perder la propiedad que queremos representar?

La gobernanza F permanece activa durante todo el ciclo.

## 2. Orden de investigación

FASE 1 — Temporalidad fuerte  
↓  
FASE 2 — Causalidad fuerte  
↓  
FASE 3 — Incertidumbre formal  
↓  
FASE 4 — Interacción entre las tres  
↓  
FASE 5 — Mapa de límites del núcleo  
↓  
FASE 6 — Revisión formal únicamente si la evidencia lo exige

El orden es deliberado: primero se fortalece la representación temporal; después se estudia causalidad sobre estados/eventos temporalmente estructurados; finalmente se estudia incertidumbre y su interacción con ambas.

## 3. FASE 1 — Temporalidad fuerte

### Pregunta

¿Puede O/M/A/δ representar semántica temporal fuerte y no solamente relaciones ordinales como before?

### Propiedades a distinguir

- orden parcial;
- simultaneidad;
- duración;
- intervalos;
- inicio y final;
- persistencia;
- cambio de estado;
- precedencia;
- concurrencia;
- restricciones temporales.

### Método

1. Definir formalmente cada propiedad.
2. Intentar representarla con O/M/A/δ.
3. Construir contraejemplos cuando la representación pierda semántica.
4. Separar representación de algoritmo de consulta.
5. Determinar qué parte es expresable y qué parte necesita una extensión.
6. Solo abrir revisión del núcleo ante insuficiencia semántica irreducible.

### Experimentos

- EXP-008: orden temporal.
- EXP-009: intervalos y duración.
- EXP-010: persistencia y cambio.
- EXP-011: concurrencia y restricciones temporales.

Salida: docs/FASE_1_TEMPORALIDAD_FUERTE_2026-09-25.md

## 4. FASE 2 — Causalidad fuerte

### Pregunta

¿Puede el núcleo representar causalidad con propiedades que distingan una mera correlación o relación de una dependencia causal?

El experimento anterior demostró que una relación causal explícita puede representarse y que la transitividad causal no debe inferirse automáticamente. Ahora se estudiará qué significa causalidad fuerte.

### Propiedades candidatas

- dirección causal;
- dependencia;
- intervención;
- condiciones;
- mecanismos;
- ausencia de causalidad;
- confusores;
- contraejemplos;
- composición causal bajo condiciones explícitas.

### Regla crítica

No se introducirá una entidad llamada causa solo para hacer conveniente la representación. Primero se intentará construir la semántica con objetos, relaciones, restricciones y transiciones.

### Experimentos

- EXP-012: dependencia causal.
- EXP-013: intervención.
- EXP-014: confusión y contraejemplos.
- EXP-015: composición causal condicionada.

Salida: docs/FASE_2_CAUSALIDAD_FUERTE_2026-09-25.md

## 5. FASE 3 — Incertidumbre formal

### Pregunta

¿Puede O/M/A/δ representar incertidumbre con semántica formal y no solamente almacenar valores o relaciones de soporte?

El experimento anterior mostró que una observación puede relacionarse con una hipótesis, puede existir polaridad y el núcleo no permite contradicciones arbitrarias; almacenar un número no crea por sí mismo semántica probabilística.

Ahora se distinguirán:

- valor numérico;
- confianza;
- soporte;
- probabilidad;
- posibilidad;
- evidencia;
- distribución;
- actualización de creencias.

### Experimentos

- EXP-016: soporte y evidencia.
- EXP-017: probabilidad.
- EXP-018: actualización de creencias.
- EXP-019: incertidumbre con restricciones.
- EXP-020: conflicto de evidencia.

Si la semántica probabilística puede implementarse como objetos, relaciones, restricciones y algoritmos externos, seguirá siendo una EXTENSION. Solo una pérdida semántica irreducible abrirá revisión del núcleo.

Salida: docs/FASE_3_INCERTIDUMBRE_FORMAL_2026-09-25.md

## 6. FASE 4 — Interacción

Se probarán combinaciones:

- tiempo + causalidad;
- tiempo + incertidumbre;
- causalidad + incertidumbre;
- tiempo + causalidad + incertidumbre.

Pregunta:

> ¿Una combinación produce una propiedad que no aparece en ninguno de los tres dominios individualmente?

Experimentos:

- EXP-021: causalidad temporal.
- EXP-022: evidencia temporal incierta.
- EXP-023: intervención con incertidumbre.
- EXP-024: sistema integrado.

La finalidad será buscar emergencia semántica, no acumular funcionalidades.

## 7. FASE 5 — Mapa de límites

Después de los experimentos se construirá una matriz de evidencia:

| Fenómeno | O/M/A/δ | Algoritmo externo | Extensión | Indeterminado | Evidencia |
|---|---|---|---|---|---|
| Identidad | ✓ | — | — | — | C |
| Relaciones | ✓ | — | — | — | C |
| Cambio | ✓ | — | — | — | C |
| Memoria | ✓ | ✓ | — | — | EXP-001 |
| Temporalidad fuerte | ? | ? | ? | ? | EXP-008…011 |
| Causalidad fuerte | ? | ? | ? | ? | EXP-012…015 |
| Incertidumbre formal | ? | ? | ? | ? | EXP-016…020 |
| Interacciones | ? | ? | ? | ? | EXP-021…024 |

La matriz registrará qué semántica fue demostrada y bajo qué condiciones.

## 8. FASE 6 — Revisión del núcleo

Esta fase solo se activa si la evidencia satisface F1–F6 del Bloque F.

### Resultado A — El núcleo permanece

Las capacidades son expresables mediante O/M/A/δ, posiblemente con algoritmos y extensiones.

### Resultado B — Se documenta un límite

Una propiedad no queda demostrada, pero tampoco existe evidencia suficiente para introducir una nueva primitiva.

Estado: INDETERMINATE.

### Resultado C — Insuficiencia semántica reproducible

Existe un contraejemplo reproducible, la reducción falla y ninguna extensión conserva la semántica requerida.

Entonces se abre una REVISIÓN FORMAL DEL NÚCLEO.

No se modifica el núcleo antes de completar esa revisión.

## 9. Infraestructura experimental

Cada experimento debe conservar:

1. hipótesis;
2. definición formal;
3. estado inicial;
4. representación O/M/A/δ;
5. operaciones δ;
6. resultado observable;
7. invariantes I1–I6;
8. prueba positiva;
9. contraejemplo o prueba negativa;
10. clasificación;
11. limitaciones;
12. conclusión.

Cada experimento será reproducible mediante pytest.

Ningún experimento podrá modificar automáticamente el núcleo, sus invariantes o su especificación.

## 10. Regla de parada

Una línea de investigación se cierra cuando:

- existe una demostración suficiente bajo el modelo actual;
- existe un contraejemplo reproducible;
- queda formalmente indeterminada;
- o nuevas pruebas no aportan evidencia nueva.

Una cuestión abierta puede permanecer abierta.

Abrir una cuestión no obliga a resolverla mediante código.

## 11. Control de regresión

Después de cada bloque experimental:

pytest experiments  
↓  
pytest suite completa  
↓  
git diff  
↓  
revisión de cambios  
↓  
commit  
↓  
push

Regla principal:

> Los experimentos investigan el núcleo; no lo modifican.

Si una modificación del núcleo resulta necesaria, primero se detiene la implementación y se abre el expediente de revisión F.

## 12. Qué NO haremos todavía

Para evitar volver a la deriva que motivó la auditoría, quedan fuera del siguiente ciclo:

- añadir más agentes por defecto;
- ampliar la interfaz web por acumulación;
- añadir nuevos módulos cognitivos sin hipótesis;
- integrar más LLM como finalidad en sí misma;
- crear nuevos primitivos por conveniencia;
- optimizar extensiones antes de conocer sus límites;
- rediseñar V7.1 completo.

La arquitectura existente permanece como baseline experimental.

## 13. Qué sí haremos

1. investigar temporalidad fuerte;
2. producir experimentos reproducibles;
3. determinar qué es semántica y qué es algoritmo;
4. investigar causalidad fuerte;
5. investigar incertidumbre formal;
6. estudiar las interacciones;
7. construir el mapa de límites;
8. decidir, con evidencia, si el núcleo permanece o necesita revisión.

## 14. Criterio de éxito

La etapa será exitosa incluso si ningún nuevo primitivo resulta necesario.

El resultado útil puede ser:

MF_MIN = ⟨O,M,A,δ⟩  
↓  
límites conocidos  
↓  
extensiones justificadas  
↓  
casos indeterminados claramente delimitados

El objetivo no es hacer el núcleo más grande.

El objetivo es saber **hasta dónde llega realmente**.

## 15. Primer objetivo operativo

El siguiente trabajo concreto será FASE 1 — Temporalidad fuerte.

Primero se construirá EXP-008, centrado exclusivamente en **orden temporal y sus propiedades formales**.

No se implementarán todavía intervalos, causalidad ni incertidumbre en ese experimento.

Secuencia:

EXP-008  
↓  
ejecución  
↓  
análisis  
↓  
clasificación  
↓  
EXP-009

Así evitamos mezclar variables y podremos identificar exactamente qué propiedad exige qué mecanismo.

**Estado: PLAN APROBADO PARA EJECUCIÓN.**
