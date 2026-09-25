# MF_MIN — CIERRE DE IRREDUCIBILIDAD OPERATIVA

**Fecha/hora:** 2026-09-25 02:22:46 UTC / 2026-09-24 20:22:46 UTC-06:00  
**Baseline:** V7.1 — commit `283f0d9`  
**Publicación:** merge commit `0f536cd`

## 1. Alcance

Esta no es una afirmación de minimalidad universal sobre todos los sistemas formales posibles.

La afirmación que se cierra es más precisa:

> Bajo la semántica operacional adoptada por MF_MIN, ninguno de los cuatro componentes (O,M,A,delta) puede eliminarse sin reintroducir una estructura semánticamente equivalente.

Por tanto:

[
MF_{MIN}=langle O,M,A,deltaangle
]

queda establecido como **núcleo mínimo operativo de trabajo**.

## 2. Qué significa «eliminar»

Una reducción solo cuenta como eliminación si:

1. el componente desaparece;
2. su función semántica permanece disponible;
3. no se introduce otro mecanismo equivalente que simplemente cambie su nombre o ubicación;
4. no se degrada la capacidad formal que el componente proporcionaba.

Mover una relación a una propiedad no elimina la relación.  
Codificar un axioma como una condición de una transición no elimina la restricción.  
Codificar una transición como una relación especial no elimina la semántica de transición.

## 3. Caso O — Objetos

(O) proporciona el dominio de entidades distinguibles sobre el cual pueden definirse identidad, referencia y participación en relaciones.

Sin un dominio distinguible no existe:

- identidad;
- referencia;
- fuente/objetivo de una relación;
- estado estructurado de entidades.

Una representación alternativa puede utilizar otra ontología de datos, pero mientras conserve entidades distinguibles estará proporcionando funcionalmente (O).

**Resultado: NECESARIO BAJO EL MODELO ACTUAL.**

## 4. Caso M — Relaciones

(M) proporciona la estructura que conecta entidades.

Supóngase que se intenta eliminar (M) almacenando toda relación como una propiedad de un objeto.

La información relacional sigue existiendo:

[
(o_i,p,o_j)
]

aunque se codifique físicamente como:

[
o_i.	ext{p}=o_j
]

Por tanto, se ha cambiado la representación, no eliminado la estructura relacional.

**Resultado: NECESARIO BAJO EL MODELO ACTUAL.**

## 5. Caso A — Restricciones/Axiomas

(A) representa condiciones que no son simplemente nuevos hechos sino restricciones sobre estados o transformaciones.

Podemos intentar absorber (A) en (delta):

[
delta_A(S,T)
]

Pero entonces las condiciones que determinan qué transición es válida siguen existiendo dentro de la semántica de (delta).

Se ha realizado una fusión de mecanismos, no una eliminación de la función.

**Resultado: NECESARIO BAJO EL MODELO ACTUAL.**

## 6. Caso δ — Transición

El núcleo representa estados:

[
S=langle O,M,Aangle
]

Pero un sistema que únicamente representa estados no representa transformación.

La capacidad adicional:

[
Sightarrow S'
]

requiere una semántica de transición.

Puede codificarse una transición como una relación, evento u objeto, pero para que tenga efecto debe existir una regla operacional que interprete dicha estructura.

Esa regla es funcionalmente equivalente a (delta).

**Resultado: NECESARIO BAJO EL MODELO ACTUAL.**

## 7. Matriz de cierre

| Componente | Intento de eliminación | Resultado |
|---|---|---|
| (O) | eliminar dominio de entidades | reaparece como entidades distinguibles |
| (M) | convertir relaciones en propiedades | reubicación de estructura relacional |
| (A) | absorber restricciones en (delta) | fusión, no eliminación |
| (delta) | codificar transiciones como relaciones | requiere semántica operacional equivalente |

## 8. Resultado final

[
oxed{langle O,M,A,deltaangle}
]

queda aceptado como el núcleo mínimo operativo de MF_MIN.

Esto **no** afirma:

[
orall F,quad Fsupseteq{O,M,A,delta}
]

ni que ninguna teoría alternativa pueda utilizar otra base primitiva.

La afirmación es relativa al modelo semántico definido por MF_MIN.

## 9. Criterio para reabrir

La cuestión de irreducibilidad solo se reabrirá ante evidencia nueva de uno de estos tipos:

- contraejemplo concreto;
- reducción formal completa;
- formalización alternativa con menor número de primitivas y capacidad equivalente;
- demostración de derivabilidad de un componente sin reintroducir su semántica;
- contradicción interna en la especificación.

La mera intuición de que «quizá pueda eliminarse» no dispara otra ronda.

## 10. Decisión

**CERRADO PARA DESARROLLO.**

La investigación continúa ahora con la pregunta constructiva:

> ¿Qué puede emerger de (O,M,A,delta) antes de introducir extensiones?

