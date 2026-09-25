# BLOQUE D — Reclasificación de V7.1
## Auditoría arquitectónica de MF_MIN
**Fecha:** 2026-09-25  
**Baseline:** V7.1, commit `283f0d9`

## 1. Propósito
Este bloque separa el núcleo formal `MF_MIN = ⟨O,M,A,δ⟩` de las extensiones existentes. No modifica ni elimina código. La clasificación se basa en función y dependencias observadas, no en nombres.

**Regla:** un componente pertenece al núcleo solo si define directamente O, M, A, δ o una invariante constitutiva.

## 2. Clasificación

| Archivo | Clase | Motivo |
|---|---|---|
| `mf_min_definitivo.py` | CORE | Define Object/O, Relation/M, AxiomConstraint/A, Transition/δ, State e invariantes. |
| `engine_d.py` | EXTENSIÓN FORMAL | Inferencia por reglas sobre estados válidos; depende del núcleo. |
| `motor_c.py` | EXTENSIÓN ALGORÍTMICA | Planificación, acciones y búsqueda sobre estados/transiciones. |
| `reconcile.py` | EXTENSIÓN FORMAL | Reconciliación de propuestas contra el Kernel. |
| `evaluation.py` | EXTENSIÓN | Evaluación y puntuación de planes. |
| `rule_candidate_builder.py` | EXTENSIÓN | Generación y validación de hipótesis de reglas. |
| `rule_induction.py` | EXTENSIÓN | Inducción estructural de reglas. |
| `concept_induction.py` | EXTENSIÓN | Inducción conceptual mediante objetos/relaciones ordinarios. |
| `agent.py` | EXTENSIÓN / ORQUESTACIÓN | Integra percepción, conocimiento, planificación, memoria, aprendizaje y lenguaje. |
| `memory.py` | EXTENSIÓN | Memoria de trabajo y episódica. |
| `attention.py` | EXTENSIÓN | Q/K/V y atención. |
| `embeddings.py` | EXTENSIÓN | Representación vectorial y similitud. |
| `context.py` | EXTENSIÓN | Contexto cognitivo compuesto. |
| `learning.py` | EXTENSIÓN | Aprendizaje y consolidación episódica. |
| `perception.py` | EXTENSIÓN | Convierte lecturas en propuestas. |
| `epistemic.py` | EXTENSIÓN | Evaluación epistemológica de claims. |
| `knowledge.py` | EXTENSIÓN | Entidades, claims, evidencia, procedencia y estados epistémicos. |
| `knowledge_store.py` | EXTENSIÓN / INFRAESTRUCTURA | Almacenamiento e índices de conocimiento. |
| `knowledge_codec.py` | EXTENSIÓN | Conversión entre artefactos y representaciones semánticas. |
| `semantic_bridge.py` | EXTENSIÓN | Proyección desde representación semántica hacia MF_MIN. |
| `natural_language.py` | EXTENSIÓN | Lenguaje natural ↔ objetivos formales. |
| `universal_extractor.py` | EXTENSIÓN | Extracción de hechos relacionales desde texto. |
| `universal_io.py` | INFRAESTRUCTURA | Transporte de artefactos externos. |
| `llm_adapter.py` | EXTENSIÓN / ADAPTER | Interfaz con LLM; el LLM permanece fuera del núcleo. |
| `retrieval.py` | EXTENSIÓN | Recuperación semántica/episódica. |
| `retrieval_indexed.py` | EXTENSIÓN | Recuperación indexada y vectorial. |
| `storage.py` | INFRAESTRUCTURA | Persistencia y serialización. |
| `audit_log.py` | INFRAESTRUCTURA | Trazabilidad operacional. |
| `environment.py` | SIMULACIÓN | Mundo externo simulado, separado del estado del Kernel. |
| `simulation.py` | SIMULACIÓN / DEMO | Integración extremo a extremo. |
| `simulation_loop.py` | SIMULACIÓN / INTEGRACIÓN | Ciclo entorno → percepción → Kernel → acción → aprendizaje. |
| `main.py` | INFRAESTRUCTURA | Lanzador CLI, pruebas y modos de ejecución. |
| `demo.py` | DEMO | Demostración integrada. |
| `visualizer.html` | UI / DEMO | Visualización interactiva. |
| `mf_min_facade.py` | API / FACHADA | Delegación ergonómica sobre Kernel + EngineD; no define nueva semántica. |
| `tests/test_architecture.py` | TEST | Evidencia sobre arquitectura. |
| `tests/test_consolidation.py` | TEST | Evidencia sobre consolidación. |
| `tests/test_context_representation.py` | TEST | Evidencia sobre contexto. |
| `tests/test_dominio_cero.py` | TEST | Evidencia sobre dominio mínimo. |
| `tests/test_knowledge_layer_v2.py` | TEST | Evidencia sobre conocimiento. |
| `tests/test_rule_candidate_builder.py` | TEST | Evidencia sobre candidatos de reglas. |
| `tests/test_rule_induction.py` | TEST | Evidencia sobre inducción. |
| `tests/test_concept_induction.py` | TEST | Evidencia sobre inducción conceptual. |
| `tests/test_agent_reorganization.py` | TEST | Evidencia sobre integración del agente. |
| `domains/*.json` | CONFIGURACIÓN | Escenarios/datos de dominio; no alteran la definición formal. |
| `README.md` | DOCUMENTACIÓN | Describe el sistema completo y su arquitectura. |
| `CONSOLIDACION_V6_DEFINITIVA.md` | DOCUMENTACIÓN HISTÓRICA | Registro de consolidación anterior. |

## 3. Hallazgos

### H1 — El núcleo existe
`mf_min_definitivo.py` contiene la semántica primaria de O, M, A y δ y las invariantes I1–I6.

### H2 — V7.1 es más grande que el núcleo
Memoria, atención, embeddings, aprendizaje, percepción, conocimiento, lenguaje, LLM, planificación e inducción forman una arquitectura construida sobre MF_MIN.

### H3 — Las extensiones no prueban nuevos primitivos
Que una capacidad sea compleja o útil no demuestra que sea irreducible. El Bloque C ya mostró que las capacidades estudiadas no justifican un quinto primitivo.

### H4 — El núcleo está físicamente concentrado
`mf_min_definitivo.py` es un archivo grande. Esto sugiere un posible refactor futuro, pero no se hará durante este bloque.

### H5 — La fachada permanece fuera del núcleo
`mf_min_facade.py` delega en `Kernel` y `EngineD`; es una interfaz de conveniencia.

## 4. Reglas de gobierno

**D1. Dependencia:** las extensiones pueden depender del núcleo; el núcleo no debe depender de ellas.

**D2. Núcleo:** solo O/M/A/δ e invariantes constitutivas.

**D3. Algoritmos:** inferencia, planificación, recuperación, aprendizaje e inducción permanecen fuera.

**D4. Adaptadores:** LLM, lenguaje, sensores, UI y almacenamiento permanecen fuera.

**D5. Promoción:** una extensión solo puede proponerse como nuevo primitivo después de demostrar que no puede representarse mediante O/M/A/δ, que no se trata de una reubicación y que posee semántica independiente verificable.

## 5. Arquitectura resultante

```
ENTRADAS / LENGUAJE / SENSORES / LLM
                 ↓
       EXTENSIONES SEMÁNTICAS
                 ↓
        ┌───────────────────┐
        │    MF_MIN CORE    │
        │   S = ⟨O,M,A⟩     │
        │       δ           │
        │    I1 ... I6      │
        └─────────┬─────────┘
                  ↓
     INFERENCIA / PLANIFICACIÓN
                  ↓
      MEMORIA / ATENCIÓN / APRENDIZAJE
                  ↓
       AGENTE / SIMULACIÓN / UI
```

La dirección conceptual correcta queda establecida como:

`CORE → EXTENSIONES → SISTEMA`

## 6. Decisión

**BLOQUE D: CERRADO PARA ESTA ETAPA.**

V7.1 queda reclasificado como:

`Sistema V7.1 = Core + extensiones formales + arquitectura cognitiva + infraestructura + experimentos`

No se elimina el trabajo existente. Se separa su estatus epistemológico: el núcleo responde a la hipótesis mínima; las demás capacidades son extensiones que deben estudiarse experimentalmente.

El siguiente paso es el **Bloque E — Experimentos controlados**, donde cada capacidad será evaluada como hipótesis falsable y no como ampliación automática del núcleo.
