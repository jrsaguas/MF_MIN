# BLOQUE F — Gobernanza científica y control de evolución del núcleo MF_MIN

**Fecha:** 2026-09-25  
**Baseline:** MF_MIN V7.1  
**Núcleo de referencia:** MF_MIN = ⟨O,M,A,δ⟩

## 1. Propósito

El Bloque F establece las reglas de decisión para evitar que la expansión de V7.1 vuelva a confundirse con una modificación del núcleo formal.

La gobernanza no decide de antemano que ⟨O,M,A,δ⟩ sea el núcleo definitivo en sentido universal. Define un procedimiento reproducible para conservarlo, ampliarlo o abrir una revisión cuando aparezca evidencia suficiente.

Principio rector:

> Una capacidad nueva no entra al núcleo porque sea útil, elegante, intuitiva o difícil de implementar. Entra únicamente si existe evidencia de insuficiencia semántica del núcleo actual.

## 2. Tres estados permitidos

Toda capacidad investigada debe terminar en uno de estos estados:

1. **CORE-EXPRESSIBLE** — puede representarse con O/M/A/δ.
2. **EXTENSION** — requiere algoritmos, índices, heurísticas, modelos, infraestructura o semántica especializada, pero no demuestra un nuevo primitivo.
3. **INDETERMINATE** — la semántica actual no permite concluir todavía si existe una insuficiencia fundamental.

No se utilizará NEW-PRIMITIVE como resultado automático de un experimento. La aparición de evidencia candidata abre una **revisión del núcleo**.

## 3. Criterios de admisión al núcleo

Una propuesta solo puede solicitar revisión como nuevo componente del núcleo cuando satisface conjuntamente:

### F1 — Fenómeno no reducible

Debe existir una capacidad o propiedad necesaria que no pueda expresarse mediante las estructuras existentes O, M, A y las transformaciones δ.

### F2 — Intento explícito de reducción

Debe documentarse al menos un intento serio de representar el fenómeno usando exclusivamente el núcleo, incluyendo dónde falla.

No basta afirmar que una nueva abstracción es más conveniente.

### F3 — Contraejemplo reproducible

Debe existir un caso concreto, ejecutable o formalmente verificable, donde la representación del núcleo pierda una propiedad semántica esencial.

### F4 — Eliminación de reubicación

Debe demostrarse que la propiedad no puede conservarse simplemente trasladando la semántica a:

- una relación;
- un objeto;
- una restricción;
- una secuencia de transiciones;
- metadatos;
- un algoritmo externo;
- o una composición de elementos ya existentes.

**Relocalizar una capacidad no equivale a demostrar un nuevo primitivo.**

### F5 — Semántica independiente

El candidato debe tener significado propio y no ser un alias conveniente de O, M, A o δ.

### F6 — Preservación

La ampliación propuesta debe conservar, o reemplazar explícitamente con justificación formal, las propiedades e invariantes que ya hacen válido al núcleo.

## 4. Evidencia mínima para abrir una revisión

Una revisión del núcleo requiere un expediente que contenga:

- definición precisa del fenómeno;
- representación intentada con O/M/A/δ;
- estado inicial y estado final;
- operaciones δ involucradas;
- invariantes afectados;
- contraejemplo reproducible;
- intento de reducción;
- explicación de por qué la reducción falla;
- candidato semántico;
- comparación con alternativas de extensión;
- pruebas positivas y negativas;
- límites conocidos;
- conclusión provisional.

La revisión no implica aceptación. Solo habilita la decisión.

## 5. Puerta de decisión

El flujo obligatorio es:

~~~text
fenómeno
   ↓
formalización
   ↓
representación O/M/A/δ
   ↓
¿funciona?
 ├─ sí → CORE-EXPRESSIBLE o EXTENSION
 └─ no
      ↓
intento de reducción
      ↓
¿fallo reproducible?
 ├─ no → INDETERMINATE
 └─ sí
      ↓
¿la semántica puede mantenerse como extensión?
 ├─ sí → EXTENSION
 └─ no
      ↓
revisión del núcleo
      ↓
nueva semántica candidata
      ↓
pruebas + contraejemplos + preservación
      ↓
decisión documentada
~~~

No existe promoción automática de código a núcleo.

## 6. Presupuesto finito de investigación

Cada cuestión debe tener un presupuesto explícito de investigación.

El objetivo es evitar dos fallos opuestos:

- cerrar prematuramente una cuestión importante;
- repetir indefinidamente experimentos equivalentes sin nueva evidencia.

Un experimento puede cerrarse cuando:

1. la representación funciona y sus límites están documentados;
2. aparece un contraejemplo reproducible;
3. la cuestión queda indeterminada bajo la semántica disponible;
4. nuevas repeticiones no añaden información relevante.

Un resultado indeterminado permanece registrado como abierto, no se convierte artificialmente en imposibilidad.

## 7. Separación entre investigación y construcción

MF_MIN mantiene dos líneas relacionadas pero no intercambiables.

### Línea de investigación

~~~text
O, M, A, δ
      ↓
expresividad
      ↓
límites
      ↓
contraejemplos
      ↓
revisión formal
~~~

### Línea de ingeniería

~~~text
núcleo
  ↓
algoritmos
  ↓
memoria / inferencia / planificación / aprendizaje
  ↓
agentes
  ↓
interfaces e infraestructura
~~~

Una mejora de ingeniería puede ser importante sin modificar el núcleo.

Una capacidad útil no constituye por sí misma evidencia de una nueva primitiva.

## 8. Regla para LLM y componentes externos

Los modelos de lenguaje, embeddings, índices, heurísticas y demás componentes externos se consideran **proponentes o mecanismos de cálculo**, no fundamentos ontológicos del núcleo.

Flujo permitido:

~~~text
componente externo
      ↓
propuesta / hipótesis / transición
      ↓
MF_MIN
      ↓
validación
      ├─ rechazo
      ├─ incorporación como dato
      └─ derivación / transición válida
~~~

La salida de un componente externo no se convierte en verdad del núcleo por el hecho de haber sido generada.

## 9. Regla de autonomía

Se mantiene la distinción:

**autoconfigurar ≠ rediseñarse**

La adaptación permitida puede progresar de forma controlada:

1. observar;
2. proponer;
3. evaluar;
4. incorporar aprendizaje;
5. adaptar parámetros o reglas dentro de límites;
6. proponer cambios estructurales únicamente como hipótesis;
7. someter cualquier cambio del núcleo al proceso de gobernanza F.

El sistema no puede modificar su propia definición fundamental simplemente porque una ejecución produzca una propuesta.

## 10. Control de cambios del núcleo

Cualquier modificación de O, M, A, δ o de sus invariantes debe:

- estar asociada a un expediente de revisión;
- identificar el motivo y la evidencia;
- mantener trazabilidad de la versión anterior;
- actualizar la especificación formal;
- actualizar las pruebas afectadas;
- ejecutar la batería de regresión;
- documentar qué afirmaciones anteriores siguen siendo válidas y cuáles cambian;
- registrar explícitamente cualquier nueva limitación.

Las extensiones no deben editar el núcleo solo para simplificar su propia implementación.

## 11. Clasificación obligatoria de nuevas funcionalidades

Antes de incorporar una funcionalidad, debe responderse:

| Pregunta | Resultado |
|---|---|
| ¿Puede representarse con O/M/A/δ? | CORE-EXPRESSIBLE |
| ¿Necesita un algoritmo o infraestructura adicional? | EXTENSION |
| ¿Tiene semántica fuerte no resuelta? | INDETERMINATE |
| ¿Existe contraejemplo reproducible contra el núcleo? | Abrir revisión |
| ¿Solo mejora conveniencia o eficiencia? | EXTENSION |
| ¿Solo reubica una semántica existente? | EXTENSION |
| ¿Propone un nuevo primitivo? | Revisión, nunca promoción automática |

## 12. Regla de falsación

Las afirmaciones fuertes deben formularse de manera que puedan fallar.

No se debe escribir:

> “MF_MIN puede representar todo.”

Debe escribirse una afirmación acotada, por ejemplo:

> “Bajo la semántica X y las operaciones Y, la capacidad Z puede representarse sin introducir un nuevo primitivo.”

Esto mantiene separadas las conclusiones demostradas de las hipótesis abiertas.

## 13. Registro de decisiones

Cada decisión relevante debe conservar:

- fecha;
- versión del núcleo;
- pregunta;
- evidencia;
- experimentos utilizados;
- decisión;
- justificación;
- limitaciones;
- estado posterior.

Las decisiones históricas no se borran cuando cambia una conclusión. Se registra una nueva decisión que referencia la anterior.

## 14. Estado actual de MF_MIN

Con los Bloques A–E cerrados:

- **A:** especificación formal establecida.
- **B:** irreducibilidad cerrada de forma acotada bajo el modelo actual.
- **C:** suficiencia constructiva evaluada.
- **D:** V7.1 reclasificado entre núcleo y extensiones.
- **E:** siete experimentos controlados ejecutados; 19 pruebas aprobadas y 0 fallos.
- **F:** gobernanza establecida para impedir ampliaciones no justificadas.

El estado del núcleo continúa siendo:

~~~text
MF_MIN = ⟨O,M,A,δ⟩
mínimo operativo de trabajo bajo la semántica actual
~~~

Esto no constituye una afirmación de minimalidad universal.

## 15. Cierre del Bloque F

El Bloque F queda cerrado como **protocolo de gobernanza**.

A partir de este punto, una nueva capacidad no debe incorporarse al núcleo por expansión acumulativa. Debe pasar primero por la clasificación CORE-EXPRESSIBLE / EXTENSION / INDETERMINATE y, solo ante evidencia suficiente de insuficiencia semántica, por una revisión formal del núcleo.

El siguiente trabajo de investigación puede centrarse en los límites que permanecen abiertos —especialmente causalidad fuerte, incertidumbre formal y temporalidad fuerte— sin alterar el núcleo por anticipación.

**BLOQUE F: CERRADO FORMALMENTE.**
