# MF_MIN — PLAN DE RECUPERACIÓN Y CONTINUIDAD — BLOQUES A–F

**Proyecto:** MF_MIN  
**Repositorio:** `jrsaguas/MF_MIN`  
**Versión de referencia:** V7.1  
**Snapshot preservado:** `283f0d9`  
**Merge de publicación:** `0f536cd`  
**Fecha/hora de registro:** 2026-09-25 02:22:46 UTC / 2026-09-24 20:22:46 UTC-06:00  
**Estado:** plan aprobado para ejecución  
**Regla principal:** MF_MIN se mantiene como proyecto independiente.

---

## 0. PROPÓSITO

Este documento fija la continuación de MF_MIN después de la auditoría de V7.1.

La pregunta fundacional del proyecto es:

> ¿Cuál es el núcleo mínimo necesario para que un sistema pueda distinguir, conservar y transformar información de manera formalmente verificable?

La hipótesis de trabajo queda expresada como:

[
MF_{MIN}=langle O,M,A,deltaangle
]

donde:

- (O): objetos/entidades distinguibles;
- (M): relaciones o estructura semántica entre objetos;
- (A): restricciones/axiomas que determinan condiciones de consistencia;
- (delta): transición que transforma un estado formal en otro.

La auditoría determinó que V7.1 contiene una operacionalización robusta de este núcleo, pero también una expansión considerable hacia memoria, planificación, aprendizaje, percepción, epistemología, lenguaje y agentes.

**Decisión:** no borrar esa expansión. Se reclasificará como trabajo derivado y extensiones del núcleo.

---

# 1. REGLAS DE GOBERNANZA DEL PLAN

1. **V7.1 es baseline congelada.**
2. Ninguna extensión se convierte automáticamente en parte del núcleo.
3. Una prueba de reducción no se repite indefinidamente.
4. Cada pregunta de investigación tiene un criterio de cierre.
5. Un resultado puede ser:
   - REDUCIBLE;
   - NECESARIO BAJO EL MODELO ACTUAL;
   - INDETERMINADO.
6. «Indeterminado» no obliga a repetir experimentos indefinidamente.
7. Para reabrir una conclusión debe aparecer nueva evidencia: contraejemplo, formalización alternativa concreta, reducción explícita o contradicción.
8. «Mover» una función de un componente a otro no cuenta como eliminación si conserva la misma semántica.
9. El código experimental no modifica el núcleo por conveniencia de implementación.
10. Cada incorporación al núcleo debe justificar semántica independiente y preservar los invariantes existentes.

---

# 2. BLOQUE A — CIERRE FORMAL DEL NÚCLEO

## Objetivo

Separar definitivamente la definición matemática/conceptual de MF_MIN de la implementación histórica de V7.1.

## Trabajo

Crear una especificación canónica del núcleo:

[
S=langle O,M,Aangle
]

[
delta(S,T)=S'
]

y documentar:

- definición de (O);
- definición de (M);
- definición de (A);
- contrato de (delta);
- representación de estados;
- transiciones atómicas;
- invariantes (I_1-I_6);
- límites explícitos del modelo.

## Invariantes de referencia

- (I_1): unicidad de identificadores;
- (I_2): integridad referencial;
- (I_3): no contradicción;
- (I_4): unicidad semántica de hechos;
- (I_5): consistencia axiomática;
- (I_6): validez/finitud numérica.

## Entregables

- `docs/MF_MIN_CORE_SPEC_2026-09-24.md`
- tabla formal ↔ implementación;
- definición de qué pertenece al núcleo y qué no.

## Criterio de cierre

El núcleo queda definido de forma suficientemente precisa para que dos implementaciones independientes puedan intentar reproducirlo sin depender de V7.1.

---

# 3. BLOQUE B — CIERRE DE LA IRREDUCIBILIDAD

## Objetivo

Cerrar formalmente la investigación de eliminación de (O,M,A,delta) sin entrar en ciclos infinitos.

## Método

Para cada componente (Xin{O,M,A,delta}):

1. Definir qué función semántica cumple.
2. Intentar una reducción concreta.
3. Determinar si la función desaparece o simplemente se reubica.
4. Identificar si existe una representación equivalente.
5. Registrar el resultado.
6. Cerrar el caso.

## Resultado de referencia de la auditoría

### (O)

Sin objetos distinguibles no existe un dominio sobre el cual conservar identidad o estructura.

**Resultado:** NECESARIO BAJO EL MODELO ACTUAL.

Existe además un argumento acotado de irreductibilidad para la identidad/dominio de objetos, pero no se afirma una irreductibilidad universal respecto de cualquier formalismo imaginable.

### (M)

Eliminar relaciones exige representar la misma estructura relacional dentro de propiedades, axiomas u otro mecanismo.

Eso constituye una reubicación semántica, no una eliminación.

**Resultado:** NECESARIO BAJO EL MODELO ACTUAL.

### (A)

Las restricciones pueden codificarse dentro de (delta), pero entonces la semántica de (A) reaparece como reglas de aceptación/rechazo de transiciones.

**Resultado:** NECESARIO BAJO EL MODELO ACTUAL.

### (delta)

Sin transición no existe transformación formal:

[
Sightarrow S'
]

Codificar cada transición como una relación especial exige todavía una semántica operacional equivalente a (delta).

**Resultado:** NECESARIO BAJO EL MODELO ACTUAL.

## Conclusión de cierre

[
oxed{MF_{MIN}=langle O,M,A,deltaangle}
]

se acepta como **núcleo mínimo operativo de trabajo**, no como teorema universal que demuestre que ninguna formalización alternativa puede utilizar otra ontología primitiva.

## Criterio de reapertura

La cuestión solo se reabre ante:

- contraejemplo explícito;
- reducción semántica real;
- formalización alternativa completa;
- demostración de que uno de los cuatro componentes es derivable sin pérdida funcional.

No se repetirán pruebas por mera duda o por aumentar el número de casos.

---

# 4. BLOQUE C — SUFICIENCIA CONSTRUCTIVA Y LÍMITE EXPRESIVO

## Objetivo

Cambiar la pregunta:

> «¿Podemos eliminar otro componente?»

por:

> «¿Qué podemos construir usando solamente (O,M,A,delta)?»

## Capacidades a investigar

Se construirán casos mínimos de:

1. identidad;
2. relación;
3. estado;
4. cambio;
5. memoria;
6. secuencia temporal;
7. causalidad;
8. reglas;
9. incertidumbre;
10. planificación;
11. aprendizaje.

Cada caso deberá responder:

- ¿puede representarse?
- ¿puede transformarse?
- ¿qué invariantes se preservan?
- ¿qué información adicional requiere?
- ¿la capacidad emerge del núcleo o necesita una extensión?

## Resultado esperado

Un mapa de expresividad:

[
	ext{Núcleo} ightarrow 	ext{Capacidad representable}
]

y otro de límites:

[
	ext{Fenómeno} ightarrow 	ext{Extensión necesaria}
]

## Criterio de cierre

No se busca demostrar que todo puede reducirse al núcleo. Se busca conocer exactamente qué puede expresar y dónde empiezan sus límites.

---

# 5. BLOQUE D — RECLASIFICACIÓN DE V7.1

## Objetivo

Recuperar el núcleo conceptual sin destruir el trabajo realizado.

## Clasificación

### Núcleo

- `mf_min_definitivo.py`
- objetos;
- relaciones;
- axiomas/restricciones;
- transición;
- invariantes;
- validación formal.

### Inferencia/derivación

- `engine_d.py`
- mecanismos de derivación y procedencia.

### Memoria

- `knowledge_store.py`
- `memory.py`
- `retrieval.py`
- `retrieval_indexed.py`

### Aprendizaje/inducción

- `learning.py`
- `rule_induction.py`
- `rule_candidate_builder.py`
- `concept_induction.py`

### Acción/planificación

- `motor_c.py`
- `simulation.py`
- `simulation_loop.py`

### Percepción/epistemología

- `perception.py`
- `epistemic.py`
- `semantic_bridge.py`

### Interfaz cognitiva

- `natural_language.py`
- `llm_adapter.py`
- `agent.py`

### Visualización y experimentación

- `visualizer.html`
- demos y herramientas auxiliares.

## Principio

La existencia de una capacidad en V7.1 **no prueba** que esa capacidad pertenezca al núcleo.

La arquitectura se reorganiza conceptualmente:

[
	ext{MF_MIN}
ightarrow
	ext{Extensiones}
ightarrow
	ext{Capacidades}
ightarrow
	ext{Agente}
]

## Criterio de cierre

Toda pieza importante de V7.1 tendrá una clasificación documentada y una relación explícita con el núcleo.

---

# 6. BLOQUE E — EXPERIMENTOS CONTROLADOS

## Objetivo

Investigar capacidades emergentes sin convertir el proyecto en una colección indefinida de funcionalidades.

## Experimentos iniciales

### EXP-001 — Memoria

Hipótesis: la memoria puede construirse como estados/relaciones persistentes y mecanismos externos de recuperación.

### EXP-002 — Tiempo

Hipótesis: secuencias temporales pueden representarse mediante objetos, relaciones y transiciones.

### EXP-003 — Causalidad

Hipótesis: ciertas relaciones de dependencia pueden representarse como estructura relacional + historial de transiciones.

### EXP-004 — Reglas

Hipótesis: una regla puede tratarse como estructura semántica que restringe o genera transiciones.

### EXP-005 — Incertidumbre

Determinar qué parte puede expresarse con el núcleo y qué requiere semántica adicional.

### EXP-006 — Planificación

Determinar si planificación es una propiedad emergente de búsqueda sobre (delta) o una extensión con semántica adicional.

### EXP-007 — Aprendizaje

Separar representación formal de mecanismos que modifican parámetros, reglas o estrategias.

## Plantilla obligatoria

Cada experimento tendrá:

1. hipótesis;
2. definición formal;
3. caso mínimo;
4. implementación;
5. pruebas;
6. resultado;
7. contraejemplos;
8. límites;
9. clasificación núcleo/extensión;
10. decisión de cierre.

## Criterio de cierre

Un experimento termina cuando:

- la hipótesis queda apoyada bajo las condiciones declaradas;
- es refutada;
- o queda indeterminada con evidencia suficiente.

No se repetirán pruebas sin una razón nueva.

---

# 7. BLOQUE F — GOBERNANZA CIENTÍFICA Y CONTINUIDAD

## Objetivo

Evitar que MF_MIN vuelva a desviarse de su pregunta fundacional por acumulación de funcionalidades.

## Puertas de decisión

### Gate F1 — Núcleo

¿La nueva propuesta requiere un primitivo que no puede expresarse mediante (O,M,A,delta)?

Si no, permanece como extensión.

### Gate F2 — Semántica

¿El nuevo componente posee una semántica independiente?

Si solo reubica una función existente, no entra al núcleo.

### Gate F3 — Verificación

¿Se preservan los invariantes?

Si no, la propuesta no se integra al núcleo.

### Gate F4 — Evidencia

¿Existe evidencia formal o experimental reproducible?

Si no, permanece como hipótesis.

### Gate F5 — Reproducibilidad

¿Otra implementación podría verificar el mismo comportamiento a partir de la especificación?

Si no, la especificación está incompleta.

## Regla de evolución

Una extensión podrá proponerse para el núcleo únicamente si satisface simultáneamente:

1. necesidad demostrada;
2. irreductibilidad respecto del núcleo vigente;
3. semántica independiente;
4. evidencia reproducible;
5. compatibilidad con los invariantes;
6. beneficio formal claro.

## Resultado

El proyecto queda dividido en dos velocidades:

**Investigación fundamental**
[
	ext{O,M,A,}delta
ightarrow
	ext{expresividad}
ightarrow
	ext{límites}
]

**Ingeniería/aplicación**
[
	ext{núcleo}
ightarrow
	ext{memoria}
ightarrow
	ext{inferencia}
ightarrow
	ext{aprendizaje}
ightarrow
	ext{planificación}
ightarrow
	ext{agente}
]

Ambas pueden avanzar sin confundirse.

---

# 8. ORDEN DE EJECUCIÓN

1. **A — Especificación formal**
2. **B — Cierre de irreducibilidad**
3. **C — Suficiencia constructiva**
4. **D — Reclasificación de V7.1**
5. **E — Experimentos**
6. **F — Gobernanza y criterios de evolución**

Los bloques A y B establecen el fundamento. C determina el poder expresivo. D recupera el trabajo histórico. E explora capacidades. F evita que el proyecto vuelva a perder su centro.

---

# 9. DEFINICIÓN DE «TERMINADO»

El trabajo A–F no se considera terminado por cantidad de código.

Se considera terminado cuando:

- existe una especificación formal estable;
- la irreducibilidad está cerrada bajo el criterio declarado;
- existe un mapa de expresividad;
- V7.1 está clasificada;
- los primeros experimentos tienen resultados reproducibles;
- existen reglas explícitas para decidir qué pertenece al núcleo;
- el repositorio permite reconstruir por qué se tomaron las decisiones.

---

# 10. ESTADO INICIAL DEL PLAN

**Baseline:** V7.1 preservada.  
**Estado conceptual:** núcleo (langle O,M,A,deltaangle) aceptado como mínimo operativo de trabajo.  
**Estado de irreducibilidad:** cerrado bajo el criterio acotado descrito en el Bloque B.  
**Siguiente trabajo:** Bloque A, especificación canónica del núcleo.  
**Restricción:** no iniciar una nueva ronda indefinida de eliminación de componentes.

---

## HISTORIAL DE DECISIONES

### 2026-09-24 / 2026-09-25 UTC

La auditoría de V7.1 identificó un desplazamiento del centro de gravedad del proyecto: de la investigación del núcleo mínimo hacia una arquitectura cognitiva amplia.

Se decidió conservar el código existente y recuperar la separación entre:

- núcleo formal;
- extensiones;
- experimentos;
- aplicaciones.

Se establece formalmente el cierre de la investigación de eliminación de (O,M,A,delta) para fines de desarrollo, manteniendo abierta únicamente la posibilidad de reapertura ante nueva evidencia concreta.

**Decisión:** continuar con Bloques A–F.

