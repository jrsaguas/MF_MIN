# MF_MIN V7 — Arquitectura Cognitiva Neuro-Simbólica Integrada

**MF_MIN** (Núcleo Formal Mínimo $\langle O, M, A, \delta \rangle$) es una arquitectura cognitiva neuro-simbólica que unifica formalismo deductivo estricto, planificación determinista en espacios de estados, atención por producto punto escalado ($Q, K, V$), memoria episódica consolidada, aprendizaje por refuerzo de operadores $Q(a)$ y meta-inducción autónoma de reglas y conceptos ontológicos.

---

## 1. Puesta en Marcha Rápida (Interfaz Web Interactiva)

Para ejecutar y utilizar tu proyecto de inmediato, solo necesitas Python 3 y `numpy`:

```bash
# 1. Iniciar el servidor web cognitivo
python main.py
# (O alternativamente: python server.py)
```

Abre tu navegador en:
👉 **[http://localhost:8000](http://localhost:8000)**

### Funcionalidades de la Interfaz Web (`visualizer.html`)
- **Simulador 2D en Vivo (`VirtualFacilityEnvironment`):** Visualiza en un canvas interactivo las salas (`pasillo`, `deposito`, `sala_servidores`), el estado de las puertas (cerradas, abiertas, bloqueadas con cerradura electrónica), la posición del agente y la recolección de llaves/tarjetas.
- **Canal de Comandos Deliberativos:** Envía instrucciones en lenguaje natural como `"entra a la sala de servidores"`, `"ir al deposito"`, `"recoger tarjeta azul"` o usa los botones de acción rápida.
- **Canal de Aserciones Epistémicas:** Enseña hechos al agente en tiempo real (ej. `"A pertenece a B."`, `"B pertenece a C."`). Observa cómo el Kernel los valida, `EngineD` deduce nuevos hechos y `RuleCandidateBuilder` auto-promueve reglas sin recargar la página.
- **Grafo Formal del Kernel:** Tabla en tiempo real de relaciones activas $\langle s, p, o, \text{pol} \rangle$ con distintivos de procedencia (`asserted`, `derived`, `proposed`).
- **Priors de Acción $Q(a)$:** Barras visuales de preferencias aprendidas mediante asignación de crédito por refuerzo.
- **Memoria Episódica:** Historial de trayectorias planificadas, costos de energía y recompensas acumuladas.

---

## 2. Modos de Ejecución Alternativos

El lanzador unificado `main.py` permite operar todos los módulos del sistema:

| Comando | Descripción |
| :--- | :--- |
| `python main.py` | Inicia el servidor web interactivo en `http://localhost:8000` |
| `python main.py --demo` | Ejecuta la demostración end-to-end de Capa 2 (`demo.py`) |
| `python main.py --sim` | Ejecuta el bucle cognitivo cerrado Capa 3 con detección de discrepancias (`simulation_loop.py`) |
| `python main.py --cli` | Abre una consola interactiva conversacional con el agente |
| `python main.py --test` | Ejecuta la suite completa de 54 pruebas de integración |
| `python mf_min_definitivo.py` | Ejecuta la batería de 88 pruebas formales de invariantes $I_1-I_6$ del Kernel |

---

## 3. Estructura de Capas del Sistema

1. **Capa 0 y 1 — Núcleo Formal y Deducción (`mf_min_definitivo.py`, `engine_d.py`):**
   - Estado formal $S = \langle O, M, A \rangle$.
   - Seis invariantes formales: $I_1$ (unicidad de ID), $I_2$ (integridad referencial), $I_3$ (no contradicción), $I_4$ (unicidad de hechos), $I_5$ (consistencia axiomática con `__distinct__`), $I_6$ (finitud numérica).
   - Motor deductivo forward-chaining con procedencia verificable (`verify_derivation`).
2. **Capa 2 — Deliberación, Memoria y Aprendizaje (`motor_c.py`, `context.py`, `attention.py`, `learning.py`):**
   - Planificador BFS determinista sobre estados simulados con transiciones atómicas.
   - Atención Scaled Dot-Product $(Q, K, V)$ y firmas canónicas de estado `ContextSignature`.
   - Adaptación de pesos de acción $Q(a)$ por recompensas ambientales.
3. **Capa 3 — Epistemología e Inducción (`agent.py`, `rule_candidate_builder.py`, `concept_induction.py`):**
   - Despachador de entradas universales `InputEnvelope` (`COMMAND`, `ASSERTION`, `PERCEPTION`).
   - Inducción de reglas de transitividad y simetría con recuento de soporte y discriminación ante contraejemplos.
   - Reificación conceptual de clases abstractas en el Kernel.


---

## 4. Continuidad del proyecto: Bloques A–F

A partir de la auditoría de V7.1 se establece una línea de continuidad que separa el **núcleo formal** de las capacidades construidas sobre él.

### Núcleo de trabajo

```
MF_MIN = <O, M, A, δ>
```

El núcleo queda tratado como **mínimo operativo de trabajo** bajo la semántica actual. La investigación de eliminación de sus cuatro componentes queda cerrada salvo nueva evidencia concreta.

### Bloques

| Bloque | Propósito | Resultado esperado |
|---|---|---|
| **A** | Especificación formal | Definición canónica del núcleo |
| **B** | Irreducibilidad | Cierre acotado de O, M, A y δ |
| **C** | Suficiencia constructiva | Mapa de expresividad y límites |
| **D** | Reclasificación V7.1 | Separación núcleo/extensiones |
| **E** | Experimentos controlados | Evidencia reproducible sobre capacidades |
| **F** | Gobernanza científica | Criterios para evolucionar el núcleo |

### Documentación

- [Plan completo de Bloques A–F](docs/PLAN_BLOQUES_A_F_2026-09-24.md)
- [Cierre de irreducibilidad](docs/PRUEBA_IRREDUCIBILIDAD_MF_MIN_2026-09-24.md)
- [Registro de decisiones](docs/REGISTRO_DECISION_MF_MIN_2026-09-24.md)

**Registro inicial:** 2026-09-25 02:22:46 UTC / 2026-09-24 20:22:46 UTC-06:00.

El objetivo de esta etapa no es aumentar indefinidamente la cantidad de funcionalidades, sino determinar qué puede emerger del núcleo, dónde están sus límites y qué extensiones están realmente justificadas.
