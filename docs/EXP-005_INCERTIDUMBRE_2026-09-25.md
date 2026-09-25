# EXP-005 — Incertidumbre

**Bloque:** E — Experimentos controlados  
**Hipótesis:** la incertidumbre puede representarse estructuralmente con O/M/A/δ, pero una semántica probabilística completa requiere reglas o algoritmos externos.

## Pregunta

¿Hace falta una quinta primitiva para representar información incierta?

## Prueba

Se distinguen tres niveles:

1. una observación puede **apoyar** una hipótesis;
2. una afirmación puede tener polaridad positiva o negativa;
3. una magnitud numérica puede almacenarse como objeto relacionado.

La prueba verifica que MF_MIN no asigna por sí mismo una probabilidad a una relación simplemente porque se utilice una expresión como `supports` o `has_estimate`.

## Hallazgo

La incertidumbre como **estructura de información** es CORE-EXPRESSIBLE.

Por ejemplo:

`observación --supports--> hipótesis`

puede representarse directamente mediante objetos y relaciones.

Sin embargo, conceptos como:

- probabilidad;
- distribución;
- intervalo de confianza;
- actualización bayesiana;
- credibilidad;
- calibración;
- independencia estadística;

requieren semántica matemática adicional y procedimientos explícitos.

El hecho de que el núcleo permita valores numéricos no significa que esos valores tengan automáticamente interpretación probabilística.

## Clasificación

**CORE-EXPRESSIBLE + ALGORITMO/SEMÁNTICA EXTERNA.**

No se justifica introducir una quinta primitiva únicamente para representar incertidumbre.

## Límite

El resultado no demuestra que toda teoría probabilística pueda implementarse sin extensiones. El objetivo es más preciso: demostrar que la **representación básica de información incierta** no obliga a ampliar el conjunto de primitivas.

## Estado

**EJECUTADO — PASS.** La representación estructural quedó aprobada y el intento de afirmar simultáneamente polaridades positiva y negativa para el mismo triple fue rechazado por I3, como exige el núcleo. Esto corrige la formulación inicial del experimento: la polaridad no se trata como permiso para almacenar contradicciones.
