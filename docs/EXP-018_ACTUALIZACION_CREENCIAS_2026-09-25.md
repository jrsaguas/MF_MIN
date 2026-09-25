# EXP-018 — Actualización de creencias

**Estado:** cerrado; ejecución aislada PASS, batería completa pendiente, núcleo sin modificaciones.

## 1. Hipótesis

Una actualización de creencia provocada por evidencia puede representarse mediante objetos, relaciones, restricciones y transiciones de MF_MIN. La operación que calcula el nuevo valor —por ejemplo una actualización bayesiana— no forma parte de la semántica primitiva de O/M/A/δ.

La prueba busca distinguir tres niveles:

1. representar una creencia inicial;
2. representar evidencia y un estado posterior;
3. calcular y justificar externamente el cambio de valor.

## 2. Protocolo

Se conserva el protocolo experimental de la Fase 3:

- hipótesis explícita;
- representación mediante O/M/A/δ;
- transiciones δ observables;
- invariantes I1–I6;
- contraejemplos;
- procedencia de resultados derivados;
- clasificación final;
- no modificación del núcleo.

El experimento no añade primitivas ni modifica `mf_min_definitivo.py`.

## 3. Representación

Una creencia se modela como un objeto numérico:

`Belief(b_0)=0.4`

y se vincula con una hipótesis mediante una relación `belief_of`.

La evidencia se representa mediante relaciones ordinarias, por ejemplo:

`Evidence(e) --supports--> Hypothesis(h)`

Una actualización se representa creando un nuevo objeto de creencia y una relación:

`b_0 --updated_to--> b_1`

Esto evita mutación in-place y permite conservar los estados anteriores.

## 4. Resultados experimentales

La prueba aislada produjo:

`23 passed in 0.05s`

Se verificó que:

- la creencia inicial es representable como dato de O;
- la evidencia es representable en M;
- añadir evidencia no cambia automáticamente el valor de la creencia;
- una actualización puede representarse como un nuevo objeto;
- δ puede almacenar la transición sin una operación especial de creencia;
- una regla externa puede producir una relación derivada con `rule_id` y `premises`;
- un cálculo de estilo bayesiano permanece externo;
- evidencia conflictiva puede representarse sin resolución automática;
- evidencia insuficiente no fuerza un valor posterior;
- el nombre de un predicado no ejecuta semántica de actualización;
- las restricciones numéricas pueden rechazarse atómicamente mediante A;
- la identidad de la hipótesis permanece constante entre estados de creencia;
- no se requiere una quinta primitiva.

## 5. Contraejemplos y límites

La existencia de `supports` no determina cuánto debe cambiar una creencia.

Tampoco existe, por el solo hecho de almacenar un valor en [0,1]:

- espacio muestral;
- distribución completa;
- regla de actualización;
- independencia;
- verosimilitud;
- prior/posterior con semántica probabilística completa;
- normalización;
- elección de evidencia relevante.

Por tanto, el paso

`evidencia → nuevo valor de creencia`

requiere un procedimiento externo explícito.

## 6. Procedencia

Cuando la actualización se representa como derivada, MF_MIN puede conservar:

- relación de actualización;
- `origin="derived"`;
- `rule_id`;
- relaciones premisa mediante `premises`.

Esto permite distinguir una actualización propuesta o calculada externamente de una relación simplemente afirmada.

## 7. Clasificación

**Resultado: CORE-EXPRESSIBLE + SEMÁNTICA/ALGORITMO EXTERNO.**

Los elementos estructurales de una actualización de creencias caben en O/M/A/δ:

- O representa hipótesis, evidencia y valores de creencia;
- M representa soporte, refutación, pertenencia y transición entre estados;
- A puede imponer restricciones numéricas;
- δ aplica las transiciones y conserva atomicidad.

La semántica fuerte de actualización no está contenida en esas estructuras. El algoritmo externo decide cómo transformar evidencia y estado previo en un nuevo valor.

## 8. Consecuencia para MF_MIN

EXP-018 no proporciona evidencia para introducir una quinta primitiva.

Sí proporciona una frontera más precisa: **representar una actualización no equivale a incorporar al núcleo una teoría de actualización de creencias**.

Esto mantiene la separación establecida en EXP-016 y EXP-017:

`O/M/A/δ → representación`

`algoritmo externo → cálculo de actualización`

`proveniencia → justificación trazable del resultado`

## 9. Estado de la Fase 3

EXP-018 queda cerrado.

La Fase 3 continúa con:

- EXP-019 — incertidumbre con restricciones;
- EXP-020 — conflicto de evidencia.

La revisión de una posible nueva primitiva queda condicionada a la evidencia acumulada de toda la fase, no a un único experimento.

## 10. Integridad

El experimento no modifica:

- `mf_min_definitivo.py`;
- invariantes I1–I6;
- la especificación del núcleo.

El resultado es una extensión experimental externa al núcleo.
