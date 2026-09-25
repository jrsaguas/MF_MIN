# EXP-007 — Aprendizaje

**Bloque:** E — Experimentos controlados  
**Hipótesis:** experiencia, resultados y conocimiento aprendido pueden representarse en O/M/A/δ; el algoritmo de generalización y actualización permanece fuera del núcleo.

## Pregunta

¿El aprendizaje obliga a introducir una nueva primitiva fundamental?

## Prueba

Se representan:

1. una experiencia;
2. una acción realizada;
3. un resultado;
4. una regla/generalización;
5. una relación derivada cuya procedencia conserva sus premisas.

El núcleo puede conservar la experiencia y efectuar cambios mediante δ.

## Resultado conceptual

La representación de una experiencia aprendida no exige una quinta primitiva.

Una forma abstracta es:

`experiencia → evidencia → generalización → estado actualizado`

Los elementos anteriores pueden ser objetos y relaciones; la actualización es una transición.

Lo que **no** está contenido automáticamente en el núcleo es el algoritmo que decide qué generalización aprender, cómo ponderar experiencias, cómo olvidar, cómo explorar o cómo optimizar una política.

## Clasificación

**CORE + ALGORITMO.**

Esto es consistente con la arquitectura de V7.1: componentes como `learning.py`, memoria y mecanismos de inducción son extensiones algorítmicas sobre el núcleo, no primitivas adicionales.

## Límite

Este experimento no demuestra que todo paradigma de aprendizaje pueda reducirse a la misma implementación. Aprendizaje estadístico, refuerzo, meta-aprendizaje o aprendizaje continuo requieren semánticas y algoritmos específicos.

## Estado

**IMPLEMENTADO — pendiente de ejecución runtime.**
