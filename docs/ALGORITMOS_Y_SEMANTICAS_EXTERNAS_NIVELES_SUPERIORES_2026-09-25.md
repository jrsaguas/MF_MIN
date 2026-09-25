# ALGORITMOS Y SEMANTICAS EXTERNAS PARA LOS NIVELES SUPERIORES

**Fecha:** 2026-09-25

## 1. Principio

MF_MIN separa: **estructura != procedimiento != semantica**.

El nucleo es MF_MIN = <O,M,A,delta>. O/M/A/delta proporcionan representacion, restricciones y transicion. Los niveles superiores pueden consultar, derivar, buscar, calcular, actualizar, comparar, resolver conflictos, interpretar y aprender sin convertirse automaticamente en primitivas.

## 2. Representacion

El Nivel 1 registra objetos, relaciones, restricciones y cambios. Validadores y serializadores pueden operar sobre el estado.

## 3. Consulta y navegacion

Algoritmos: Query(S,predicado), Neighbors(M,x), Filter(R,C), e indices por ID, tipo, predicado y referencias. La consulta selecciona informacion; no redefine O/M.

## 4. Reglas y derivacion

Un motor externo puede hacer matching de premisas, seleccionar reglas, construir resultados, validar con A, aplicar atomicamente con delta y registrar procedencia. Las derivaciones pueden conservar origin=derived, rule_id y premises.

## 5. Cierre y composicion

Pueden usarse cierre transitivo, forward chaining, backward chaining, resolucion, matching, composicion de relaciones y propagacion de restricciones. Una propiedad como transitividad no existe por el nombre del predicado: debe venir de una regla o semantica externa.

## 6. Temporalidad

before(t1,t2) puede almacenarse en M. Un algoritmo externo puede calcular cierre transitivo, comprobar irreflexividad, asimetria, transitividad y restricciones de intervalos. Los intervalos pueden representar inicio, fin y duracion. La aritmetica de duracion es externa. La semantica temporal fuerte requiere una teoria externa.

## 7. Causalidad

causes(A,B) puede almacenarse como M. El nivel superior puede implementar identificacion causal, modelos estructurales, comparacion de intervenciones, ajuste por confusores, contrafactuales y composicion causal. No se acepta automaticamente before(A,B) => causes(A,B), ni causes(A,B) => before(A,B).

## 8. Intervencion

Una intervencion puede representarse con relaciones hacia su objetivo y estados antes/despues. Algoritmos externos pueden construir baseline, rama intervenida, comparaciones, estimaciones de efecto y analisis de sensibilidad. Intervencion no implica causalidad sin un procedimiento que lo justifique.

## 9. Evidencia

supports(E,H) y refutes(E,H) pueden conservarse en M. Algoritmos externos pueden hacer agregacion, ponderacion, evaluacion de calidad, comparacion de fuentes, deteccion de conflicto y actualizacion. El nucleo no selecciona automaticamente una fuente ganadora.

## 10. Probabilidad e incertidumbre

Un valor como u=0.25 puede ser un objeto y A puede imponer 0 <= u <= 1. Pero valor numerico != semantica probabilistica, e incertidumbre != probabilidad, hasta que una semantica externa las conecte. Algoritmos posibles: Bayes, probabilidad condicional, propagacion de incertidumbre, inferencia probabilistica y Monte Carlo.

## 11. Actualizacion de creencias

Si B_t(H) es un objeto, un algoritmo externo puede calcular B_(t+1)(H) = Update(B_t(H),E). Bayes, filtros y reglas heuristicas son ejemplos. delta registra el cambio; no determina Update.

## 12. Resolucion de conflictos

Dos fuentes pueden sostener afirmaciones incompatibles. El nucleo puede conservar ambas. Un resolutor externo puede aplicar prioridad de fuente, pesos, mayoria, confiabilidad, consistencia global, agregacion probabilistica o argumentacion formal.

## 13. Planificacion

Un planificador externo puede calcular Plan(S,G) -> [a1,...,an] mediante BFS, DFS, A*, STRIPS, planificacion heuristica u optimizacion. delta aplica las transiciones seleccionadas; no decide cual plan es mejor.

## 14. Aprendizaje

Un algoritmo externo puede calcular Learn(D) -> Model y despues Model(S) -> T. Puede utilizar induccion de reglas, regresion, clustering, aprendizaje bayesiano o aprendizaje por refuerzo. El resultado aprendido puede regresar a O/M.

## 15. Memoria

La memoria puede construirse sobre M mediante almacenamiento, recuperacion, indexacion, ranking, compresion, consolidacion y olvido. Una arquitectura de memoria compleja no implica una quinta primitiva.

## 16. Integracion

Los niveles pueden componerse: Estado -> Consulta -> Inferencia -> Validacion -> delta -> Estado nuevo. Un ciclo completo puede ser: observar -> representar -> inferir -> validar -> actuar -> observar.

## 17. Contrato de un algoritmo externo

| Campo | Requisito |
|---|---|
| Entrada | Estado y/o subconjunto |
| Precondiciones | Condiciones requeridas |
| Procedimiento | Algoritmo definido |
| Salida | Objetos, relaciones o transiciones |
| Procedencia | Regla, modelo o metodo |
| Validacion | Restricciones verificadas |
| Determinismo | Determinista o estocastico |
| Incertidumbre | Representacion utilizada |
| Fallos | Condiciones de rechazo |
| Semantica | Interpretacion introducida |
| Dependencias | Modelos/conocimiento externo |
| Reproducibilidad | Prueba o experimento |

## 18. Frontera arquitectonica

Core -> representa.

Algoritmos -> transforman o infieren.

Semanticas -> interpretan.

Axiomas -> restringen.

delta -> aplica cambios.

La existencia de un algoritmo potente sobre el nucleo no demuestra que ese algoritmo sea una primitiva fundamental.

## 19. Criterio para una nueva primitiva

Una extension solo puede convertirse en candidata si demuestra: representacion insuficiente con O/M/A/delta; insuficiencia del procesamiento externo permitido; ausencia de reubicacion semantica; contraejemplo reproducible; preservacion de invariantes; independencia de una implementacion concreta; y necesidad para una clase de fenomenos.

Hasta entonces permanece como algoritmo o semantica externa.

## 20. Conclusion

MF_MIN no afirma ser una teoria completa de inteligencia, tiempo, causalidad o incertidumbre. La afirmacion precisa es que el nucleo proporciona una estructura minima sobre la cual pueden construirse multiples niveles de procesamiento y semantica sin aumentar necesariamente las primitivas fundamentales. La investigacion debe intentar romper esta separacion mediante contraejemplos reproducibles.
