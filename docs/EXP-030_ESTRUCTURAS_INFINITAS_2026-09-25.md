# EXP-030 — Estructuras infinitas y no finitas
Fecha: 2026-09-25

## 1. Hipótesis

La estructura O/M/A/delta puede representar descripciones de dominios, procesos o familias no finitas sin materializar todos sus elementos. La prueba separa representación simbólica, materialización finita y semántica de infinitud.

## 2. Frontera evaluada

Se evaluaron:
- prefijos finitos de estructuras infinitas;
- generadores y esquemas;
- dominios no finitos;
- cardinalidad simbólica;
- sucesiones y familias indexadas;
- procesos potencialmente infinitos;
- materialización limitada;
- cierre externo;
- snapshots finitos;
- límites de representación.

La pregunta no es si el núcleo puede almacenar literalmente un conjunto infinito en memoria. La pregunta es si la infinitud obliga a una quinta primitiva ontológica.

## 3. Resultados

### 3.1 Prefijos finitos

Un dominio infinito puede representarse mediante un objeto que lo describe y mediante miembros finitos materializados como objetos ordinarios.

El núcleo no genera automáticamente los miembros no observados.

### 3.2 Generadores y esquemas

Un generador o esquema puede almacenarse como Object. Su texto o valor descriptivo no activa por sí mismo ninguna expansión.

Una rutina externa puede materializar un prefijo finito y registrar las relaciones de generación.

### 3.3 Cardinalidad

La cardinalidad infinita puede almacenarse como dato asociado a un objeto. Por ejemplo, aleph_0 puede ser el valor de otro Object.

Esto representa información sobre cardinalidad; no introduce una semántica cardinal intrínseca.
### 3.4 Sucesiones y familias

Una sucesión no finita puede describirse mediante un esquema, mientras que términos concretos se materializan como objetos independientes.

El núcleo puede conservar la correspondencia mediante relaciones y procedencia derivada.

### 3.5 Cierre

El núcleo no aplica cierre infinito de forma implícita. Un algoritmo externo puede calcular nuevos elementos o relaciones y aplicarlos mediante delta.

La expansión queda limitada por el algoritmo, el presupuesto de cálculo o el criterio de materialización.

### 3.6 Procesos potencialmente infinitos

Un proceso descrito como “repetir indefinidamente” puede representarse como Object. El texto no hace que delta ejecute un ciclo infinito.

La ejecución pertenece a un algoritmo externo.

### 3.7 Atomicidad

La validación de referencias continúa vigente. Una relación que apunta a un objeto inexistente se rechaza y el estado previo permanece intacto.

La existencia de una estructura no finita no elimina las invariantes I1-I6.

## 4. Distinciones críticas

### Descripción infinita ≠ almacenamiento infinito

El núcleo puede almacenar una descripción finita de una estructura no finita.

### Prefijo finito ≠ totalidad

Materializar diez elementos no convierte esos diez elementos en una enumeración completa del dominio.

### Generador ≠ cierre automático

Un generador almacenado no produce consecuencias hasta que un algoritmo externo lo interpreta.

### Cardinalidad ≠ semántica cardinal

Almacenar aleph_0 no hace que el núcleo realice teoría de conjuntos.

### Proceso infinito ≠ ejecución infinita

Una descripción de proceso puede permanecer como dato sin bloquear delta.

### Límite computacional ≠ nueva ontología

Un parámetro que limita materialización puede representarse como objeto o restricción. No aparece evidencia de una quinta primitiva.
## 5. Evidencia reproducible

Prueba aislada: **33 passed**.

Batería completa: **455 passed**.

git diff --check: limpio.

mf_min_definitivo.py: sin modificaciones.

## 6. Clasificación

**CORE-EXPRESSIBLE + ALGORITMO/SEMÁNTICA EXTERNA**

Los casos examinados pueden representarse con O/M/A/delta mediante:
- objetos descriptivos;
- relaciones;
- snapshots;
- axiomas y restricciones;
- materialización finita;
- algoritmos externos de generación o cierre.

No se identificó una dependencia ontológica que obligue a introducir una quinta primitiva.

## 7. Límite demostrado

EXP-030 no demuestra que toda matemática de estructuras infinitas pueda implementarse eficientemente sobre el núcleo.

Tampoco demuestra que cualquier semántica de infinitud pueda reducirse a una representación finita sin estructuras auxiliares.

Demuestra algo más acotado: los fenómenos estructurales probados —dominios no finitos, generadores, esquemas, cardinalidad simbólica, sucesiones, procesos potencialmente infinitos y materialización limitada— pueden describirse y extenderse mediante O/M/A/delta sin introducir una nueva categoría ontológica.

La capacidad de razonar sobre infinitud, convergencia, cardinalidad, inducción, continuidad o límites permanece en algoritmos y semánticas externas.

## 8. Estado de Fase 5

Con EXP-025 a EXP-030 quedan atacadas seis fronteras de Fase 5:
- cuantificación y variables;
- conocimiento no monotónico;
- modalidad y contrafactualidad;
- sistemas abiertos y observación parcial;
- identidad dinámica y referencia;
- estructuras infinitas/no finitas.

El patrón continúa siendo estable:

**el núcleo representa; los algoritmos externos calculan; las semánticas fuertes interpretan; delta aplica cambios.**

La siguiente frontera pendiente de la lista original es la **equivalencia compleja de estados/estructuras**, que debe probar si comparar estados completos, isomorfismos o equivalencias estructurales exige una nueva primitiva o solamente algoritmos externos.

## 9. Conclusión

EXP-030 no aporta evidencia reproducible para ampliar <O,M,A,delta>.

La frontera de infinitud queda clasificada como un problema de representación simbólica, generación, cierre y semántica externa, no como una nueva categoría ontológica demostrada.
