# EXP-028 — Sistemas abiertos y observación parcial
Fecha: 2026-09-25

## 1. Hipótesis

Un sistema puede tener una frontera con un entorno externo y ser observado sólo parcialmente. La pregunta de frontera es si esta apertura y esta incompletitud observacional exigen una nueva primitiva ontológica en MF_MIN.

## 2. Estructuras evaluadas

Se representaron:
- sistema;
- entorno;
- frontera e interacción;
- entradas y salidas;
- eventos externos;
- observaciones parciales;
- propiedades observadas;
- procedencia de resultados derivados;
- tiempo de una observación como estructura explícita.

Todo ello se expresó mediante objetos y relaciones ordinarias.

## 3. Resultados

### 3.1 Observación parcial

Una observación puede registrarse como objeto y relacionarse con el sistema observado.

La ausencia de una observación no se convierte en falsedad. El núcleo no adopta por sí mismo una hipótesis de mundo cerrado.

### 3.2 Sistemas abiertos

La relación entre sistema y entorno puede representarse mediante relaciones de interacción, entrada y salida.

La existencia de una frontera no activa automáticamente una dinámica de intercambio.

### 3.3 Eventos externos

Un evento puede entrar en la representación del sistema mediante una relación.

El evento no provoca automáticamente una transición adicional: un algoritmo externo debe determinar si existe una consecuencia y cómo representarla.

### 3.4 Inferencia a partir de observaciones

Una observación puede actuar como premisa de una relación derivada. La procedencia conserva las observaciones utilizadas.

La transformación de observaciones en estado estimado pertenece a un procesamiento externo.

### 3.5 Vistas parciales múltiples

Varias observaciones o sensores pueden coexistir. El núcleo no decide automáticamente cuál es correcta, cuál es más fiable o cómo fusionarlas.

Esas decisiones pertenecen a semánticas o algoritmos externos.

## 4. Distinciones críticas

### Observabilidad ≠ estado completo

Representar una observación no implica representar todo el estado real del sistema.

### Ausencia ≠ negación

No observar una propiedad no equivale a registrar explícitamente su negación.

### Entrada ≠ transición automática

Un evento externo puede estar representado sin que el núcleo invente una transición física o causal.

### Procedencia ≠ estimación

Las premises registran qué información sustentó una conclusión, pero no constituyen por sí mismas un algoritmo de estimación.

## 5. Evidencia reproducible

Prueba aislada: 26 passed.

Batería completa: 340 passed.

git diff --check: limpio.

mf_min_definitivo.py: sin modificaciones.

## 6. Clasificación

**CORE-EXPRESSIBLE + ALGORITMO/SEMÁNTICA EXTERNA**

La apertura del sistema y la observación parcial no proporcionaron evidencia de una quinta primitiva.

El núcleo representa estructura, mientras que:
- fusión de observaciones;
- estimación de estado;
- filtrado;
- fiabilidad;
- actualización por eventos;
- semántica del entorno

permanecen externos.

## 7. Límite demostrado

EXP-028 no demuestra que cualquier teoría de sistemas abiertos o cualquier algoritmo de observación pueda implementarse eficientemente sobre MF_MIN.

Demuestra que la estructura básica de un sistema abierto con información parcial puede representarse con O/M/A/delta sin ampliar el núcleo.

## 8. Siguiente frontera

La siguiente frontera fuerte es la **identidad dinámica y referencia bajo transformación**, donde debe comprobarse si un objeto puede conservar identidad mientras cambian sus representaciones, referencias o composición.
