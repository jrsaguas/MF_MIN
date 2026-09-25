# FASE 3 — INCERTIDUMBRE FORMAL

**Estado:** cerrada.

## Objetivo

Determinar hasta dónde pueden representarse incertidumbre, evidencia, probabilidad, actualización de creencias, restricciones y conflicto de evidencia utilizando únicamente O/M/A/δ, sin introducir una nueva primitiva ontológica.

## Resultados

| Experimento | Fenómeno | Clasificación |
|---|---|---|
| EXP-016 | soporte/evidencia | CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO |
| EXP-017 | probabilidad | CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO |
| EXP-018 | actualización de creencias | CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO |
| EXP-019 | incertidumbre con restricciones | CORE-EXPRESSIBLE + RESTRICCIÓN/SEMÁNTICA EXTERNA |
| EXP-020 | conflicto de evidencia | CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO |

## Síntesis

Los cinco experimentos convergen en una misma frontera.

O/M/A/δ permiten representar:

- observaciones y evidencias;
- hipótesis;
- valores numéricos;
- restricciones;
- soporte y refutación;
- estados sucesivos de creencia;
- procedencia de inferencias;
- conjuntos de evidencia conflictiva;
- transiciones derivadas.

Lo que no aparece como primitivo del núcleo es la semántica especializada que transforma esas estructuras:

`evidencia → probabilidad`

`evidencia → actualización`

`conflicto → resolución`

`datos → distribución`

`restricciones → interpretación epistemológica`

Esas operaciones requieren algoritmos, reglas o criterios externos.

## Distinción crítica: contradicción vs conflicto

La Fase 3 confirma una diferencia que debe permanecer explícita:

1. **Contradicción estructural:** mismo hecho positivo y negativo; I3 la rechaza.
2. **Conflicto de evidencia:** fuentes diferentes sostienen y refutan una hipótesis; puede coexistir.
3. **Resolución:** procedimiento externo que produce una conclusión derivada a partir del conflicto.

Colapsar estos tres niveles introduciría una semántica que el núcleo no necesita.

## Convergencia

Ninguno de EXP-016–020 produjo evidencia suficiente para introducir una quinta primitiva.

La conclusión de la Fase 3 es, por tanto:

**O/M/A/δ permanece como núcleo operativo suficiente para la representación estructural de los fenómenos estudiados.**

Esto no demuestra que toda teoría de incertidumbre sea reducible a MF_MIN. Establece únicamente el límite experimental observado bajo el formalismo y protocolo actuales.

## Integridad

- núcleo sin modificaciones;
- invariantes I1–I6 preservados;
- experimentos reproducibles con pytest;
- resultados documentados;
- no se promovió ninguna nueva primitiva.

## Siguiente fase

La Fase 4 estudiará la **interacción entre dimensiones**:

- EXP-021 — causalidad temporal;
- EXP-022 — evidencia temporal incierta;
- EXP-023 — intervención con incertidumbre;
- EXP-024 — sistema integrado.

El objetivo será comprobar si la combinación produce una necesidad ontológica que no apareció al estudiar cada dimensión por separado.
