"""
agent.py — Agente Cognitivo Integrado Reorganizado (MF_MIN V7).

Arquitectura Unificada:
  - Contrato único de entrada mediante InputEnvelope y InputKind.
  - Despachador canónico Agent.receive(envelope).
  - Tres canales de entrada diferenciados semánticamente:
      * PERCEPTION: Telemetría / lecturas sensoriales externas (PerceptionModule / Claims).
      * COMMAND: Órdenes de acción / metas deliberativas (MotorC / PlanEvaluator).
      * ASSERTION: Hechos universales en lenguaje natural (UniversalFactExtractor / EpistemicEvaluator).
  - Ciclo de eventos cognitivos rastreables (CognitiveEvent).
  - Punto de observación desacoplado para aprendizaje inductivo (RuleCandidateBuilder).
  - Preservación estricta de retrocompatibilidad con toda la API de V6/V7.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any, Union
import time

from mf_min_definitivo import Kernel, State, Transition
from engine_d import EngineD, Rule
from motor_c import MotorC, Action, Goal, Plan
from memory import Memory, Episode, EpisodicMemory
from retrieval import Retriever
from retrieval_indexed import IndexedRetriever
from attention import AttentionEngine
from context import ContextBuilder, ActiveContext
from evaluation import PlanEvaluator, PlanScore
from learning import Learner
from embeddings import VectorEmbeddingEngine
from perception import PerceptionModule
from knowledge import Entity, Claim, Evidence, Provenance, EpistemicStatus
from knowledge_store import KnowledgeStore
from epistemic import EpistemicEvaluator
from semantic_bridge import SemanticBridge
from llm_adapter import OllamaAdapter
from universal_extractor import UniversalFactExtractor
from natural_language import NaturalLanguageInterface
from rule_candidate_builder import RuleCandidateBuilder, CandidateRule


class InputKind(str, Enum):
    PERCEPTION = "perception"
    COMMAND = "command"
    ASSERTION = "assertion"


@dataclass
class InputEnvelope:
    """
    Envoltorio tipado universal para toda entrada que ingresa al agente.
    Evita el error de 'todo es string', permitiendo payloads heterogéneos y estructurados.
    """
    kind: InputKind
    payload: Any
    source: str = "user"
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CognitiveEvent:
    """
    Evento cognitivo inmutable emitido durante las etapas del ciclo de vida.
    Permite la observación desacoplada por parte de módulos de aprendizaje.
    """
    event_type: str  # "fact_observed", "fact_asserted", "fact_committed", "fact_derived", "command_received", "action_executed", "action_failed", "goal_achieved", "episode_completed"
    payload: Dict[str, Any]
    source: str = "agent"
    timestamp: float = field(default_factory=time.time)
    cycle_id: Optional[str] = None


@dataclass
class AgentResponse:
    """Respuesta unificada y estructurada tras procesar un InputEnvelope."""
    success: bool
    kind: InputKind
    detail: str
    data: Optional[Dict[str, Any]] = None
    emitted_events: List[CognitiveEvent] = field(default_factory=list)


@dataclass
class AgentCycleResult:
    goal: Goal
    active_context: ActiveContext
    plan: Optional[Plan]
    plan_score: Optional[PlanScore]
    executed: bool
    goal_achieved: bool
    reward: float
    recorded_episode: Optional[Episode]
    new_state: State
    deductions_count: int = 0
    epistemic_claims_count: int = 0
    environment_feedback: str = ""


class Agent:
    """
    Agente Neuro-Simbólico Integrado con Despachador Canónico de Entradas.
    """
    def __init__(self, kernel: Optional[Kernel] = None, dim: int = 16):
        self.kernel = kernel or Kernel()
        self.embedder = VectorEmbeddingEngine(dim=dim)
        
        # 1. Memoria Unificada
        self.knowledge_store = KnowledgeStore()
        self.memory = Memory()
        self.episodic_memory: EpisodicMemory = self.memory.episodic

        # 2. Epistemología, Extracción y Proyección
        self.epistemic_evaluator = EpistemicEvaluator(self.kernel)
        self.bridge = SemanticBridge(self.epistemic_evaluator)
        self.perception = PerceptionModule(self.kernel)
        self.extractor = UniversalFactExtractor()
        
        # 3. Recuperación Jerárquica y Atención
        self.attention = AttentionEngine(dim=dim)
        self.retriever = Retriever(memory=self.memory, knowledge_store=self.knowledge_store, embedding_engine=self.embedder)
        self.indexed_retriever = IndexedRetriever(self.knowledge_store, embedder=self.embedder)
        self.context_builder = ContextBuilder(
            retriever=self.retriever,
            attention_engine=self.attention,
            embedder=self.embedder
        )
        
        # 4. Inferencia, Planificación y Aprendizaje
        self.engine_d = EngineD(self.kernel)
        self.inference_rules: List[Rule] = []
        self.learner = Learner(learning_rate=0.25, embedder=self.embedder)
        self.evaluator = PlanEvaluator(embedder=self.embedder)
        self.motor_c = MotorC(action_priors=self.learner.action_values)

        # 5. Adaptador de Lenguaje Local
        self.llm = OllamaAdapter(model="llama3.2:3b")

        # 6. Eventos y Hook de Aprendizaje Estructural
        self.event_log: List[CognitiveEvent] = []
        self.rule_candidate_builder = RuleCandidateBuilder()
        self.natural_language = NaturalLanguageInterface(embedder=self.embedder)
        self._cycle_counter: int = 0

    @property
    def state(self) -> State:
        return self.kernel.state

    def add_inference_rule(self, rule: Rule) -> None:
        """Registra una regla activa en la lista de inferencia de EngineD evitando duplicados."""
        if not any(r.id == rule.id or r.name == rule.name for r in self.inference_rules):
            self.inference_rules.append(rule)

    def emit_event(self, event: CognitiveEvent) -> None:
        """Registra un evento cognitivo en la memoria histórica del agente."""
        self.event_log.append(event)

    def _trigger_learning_hook(self, fact: Dict[str, Any], event: Optional[CognitiveEvent] = None) -> None:
        """
        PUNTO DE ANCLAJE DEL APRENDIZAJE:
        Notifica al RuleCandidateBuilder sobre hechos comprometidos en el Kernel.
        Nunca envía texto bruto ni derivaciones no comprobadas.
        Si una regla candidata alcanza los criterios de validación formal, se promueve
        automáticamente a EngineD cerrando el ciclo autónomo.
        """
        if self.rule_candidate_builder is not None:
            ev_id = (event.payload.get("id") if event else None) or fact.get("evidence_id")
            cands = self.rule_candidate_builder.observe(fact, evidence_id=ev_id)
            for cand in cands:
                promoted_rule = self.rule_candidate_builder.promote(cand.candidate_id)
                if promoted_rule is not None:
                    if not any(r.id == promoted_rule.id or r.name == promoted_rule.name for r in self.inference_rules):
                        self.add_inference_rule(promoted_rule)
                        ev_prom = CognitiveEvent(
                            event_type="rule_promoted",
                            payload={
                                "rule_id": promoted_rule.id,
                                "candidate_id": cand.candidate_id,
                                "pattern_type": cand.pattern_type,
                                "confidence": cand.confidence
                            },
                            source="rule_candidate_builder",
                            cycle_id=event.cycle_id if event else None
                        )
                        self.emit_event(ev_prom)

    # =========================================================================
    # DISPATCHER CANÓNICO UNIFICADO (Agent.receive)
    # =========================================================================
    def receive(self, envelope: Union[InputEnvelope, Dict[str, Any]]) -> AgentResponse:
        """
        Punto de entrada formal y único para interactuar con el agente.
        Orquesta el ciclo: RECEIVE -> NORMALIZE -> INTERPRET -> EPISTEMIC CHECK ->
        REPRESENT -> CONSOLIDATE -> INFER -> DECIDE/ACT -> EMIT EVENTS -> LEARN.
        """
        self._cycle_counter += 1
        cycle_id = f"cyc_{self._cycle_counter}_{int(time.time()*1000)}"

        # Normalización del envelope
        if isinstance(envelope, dict):
            kind_val = envelope.get("kind", "assertion")
            envelope = InputEnvelope(
                kind=InputKind(kind_val),
                payload=envelope.get("payload"),
                source=envelope.get("source", "user"),
                metadata=envelope.get("metadata", {})
            )
        elif not isinstance(envelope, InputEnvelope):
            raise TypeError(f"Entrada inválida a receive(): se esperaba InputEnvelope, recibido {type(envelope)}")

        handlers = {
            InputKind.PERCEPTION: self._handle_perception,
            InputKind.COMMAND: self._handle_command,
            InputKind.ASSERTION: self._handle_assertion,
        }

        handler = handlers.get(envelope.kind)
        if not handler:
            return AgentResponse(
                success=False,
                kind=envelope.kind,
                detail=f"Tipo de entrada no soportado: {envelope.kind}"
            )

        return handler(envelope, cycle_id)

    def _handle_perception(self, envelope: InputEnvelope, cycle_id: str) -> AgentResponse:
        """Procesa señales sensoriales / telemetría estructurada."""
        raw_readings = envelope.payload
        if isinstance(raw_readings, dict):
            readings = [raw_readings]
        elif isinstance(raw_readings, list):
            readings = raw_readings
        else:
            return AgentResponse(
                success=False,
                kind=InputKind.PERCEPTION,
                detail="Payload de percepción inválido: debe ser List[Dict] o Dict."
            )

        new_entities: List[Entity] = []
        new_claims: List[Claim] = []
        emitted: List[CognitiveEvent] = []

        for r in readings:
            s, p, o, pol = r["subject"], r["predicate"], r["object"], r.get("polarity", True)
            source = r.get("source", envelope.source)

            ent_s = Entity(id=s, type="Entity", label=s)
            ent_o = Entity(id=o, type="StateVal" if "estado" in p or "seguridad" in p else "Entity", label=o)
            self.knowledge_store.add_entity(ent_s)
            self.knowledge_store.add_entity(ent_o)
            new_entities.extend([ent_s, ent_o])

            ev = Evidence(id=f"ev_{source}_{s}_{p}", source=source, reliability=0.9, modality="sensor")
            prov = Provenance(origin="perceived", actor=source)
            cl = Claim(
                subject=s, predicate=p, object=o, polarity=pol,
                confidence_interpretation=1.0, confidence_evidence=0.9,
                provenance=prov, evidences=[ev]
            )
            self.knowledge_store.add_claim(cl)
            new_claims.append(cl)

            ev_obs = CognitiveEvent(
                event_type="fact_observed",
                payload={"subject": s, "predicate": p, "object": o, "polarity": pol, "source": source},
                source=source,
                cycle_id=cycle_id
            )
            self.emit_event(ev_obs)
            emitted.append(ev_obs)

        # Proyección atómica al Kernel
        transitions = self.bridge.project_to_kernel_transitions(
            entities=new_entities,
            claims=new_claims,
            store=self.knowledge_store,
            kernel=self.kernel
        )

        committed_count = 0
        if transitions:
            self.kernel.transition_batch(transitions)
            committed_count = len(transitions)
            for t in transitions:
                if t.operation == "add_relation":
                    payload = t.payload
                    fact_dict = {
                        "subject": payload["source"],
                        "predicate": payload["predicate"],
                        "object": payload["target"],
                        "polarity": payload.get("polarity", True),
                        "origin": payload.get("origin", "perceived"),
                        "id": payload.get("id")
                    }
                    ev_com = CognitiveEvent(
                        event_type="fact_committed",
                        payload=fact_dict,
                        source=envelope.source,
                        cycle_id=cycle_id
                    )
                    self.emit_event(ev_com)
                    emitted.append(ev_com)
                    self._trigger_learning_hook(fact_dict, ev_com)

        return AgentResponse(
            success=True,
            kind=InputKind.PERCEPTION,
            detail=f"Percepciones integradas con éxito ({committed_count} transiciones aplicadas).",
            data={"committed_transitions": committed_count, "readings_count": len(readings)},
            emitted_events=emitted
        )

    def _handle_assertion(self, envelope: InputEnvelope, cycle_id: str) -> AgentResponse:
        """Procesa hechos declarativos en lenguaje natural o estructurados."""
        payload = envelope.payload
        emitted: List[CognitiveEvent] = []

        if isinstance(payload, str):
            fact = self.extractor.extract_relation(payload)
            if not fact:
                return AgentResponse(
                    success=False,
                    kind=InputKind.ASSERTION,
                    detail="Rechazado: entrada no derivable o gramaticalmente ambigua.",
                    emitted_events=emitted
                )
        elif isinstance(payload, dict):
            fact = payload
        else:
            return AgentResponse(
                success=False,
                kind=InputKind.ASSERTION,
                detail=f"Tipo de payload no soportado para afirmación: {type(payload)}"
            )

        s, p, o, pol = fact["subject"], fact["predicate"], fact["object"], fact.get("polarity", True)
        source = envelope.source

        # 1. Registro en KnowledgeStore
        ent_s = Entity(id=s, type="Entity", label=s)
        ent_o = Entity(id=o, type="StateVal" if "estado" in p or "cerrada" in o or "abierta" in o else "Entity", label=o)
        self.knowledge_store.add_entity(ent_s)
        self.knowledge_store.add_entity(ent_o)

        ev = Evidence(id=f"ev_assert_{s}_{p}_{o}", source=source, reliability=0.95, modality="text")
        prov = Provenance(origin="asserted", actor=source)
        cl = Claim(
            subject=s, predicate=p, object=o, polarity=pol,
            confidence_interpretation=1.0, confidence_evidence=0.95,
            provenance=prov, evidences=[ev]
        )
        self.knowledge_store.add_claim(cl)

        ev_assert = CognitiveEvent(
            event_type="fact_asserted",
            payload={"subject": s, "predicate": p, "object": o, "polarity": pol, "source": source},
            source=source,
            cycle_id=cycle_id
        )
        self.emit_event(ev_assert)
        emitted.append(ev_assert)

        # 2. Validación Epistémica y Proyección al Kernel
        transitions = self.bridge.project_to_kernel_transitions(
            entities=[ent_s, ent_o],
            claims=[cl],
            store=self.knowledge_store,
            kernel=self.kernel
        )

        if not transitions:
            # Si el evaluador epistémico rechazó el claim
            return AgentResponse(
                success=False,
                kind=InputKind.ASSERTION,
                detail="Rechazado epistémicamente: el hecho genera contradicción o no supera el umbral formal.",
                emitted_events=emitted
            )

        self.kernel.transition_batch(transitions)

        fact_dict = {
            "subject": s,
            "predicate": p,
            "object": o,
            "polarity": pol,
            "origin": "asserted",
            "evidence_id": ev.id
        }
        ev_com = CognitiveEvent(
            event_type="fact_committed",
            payload=fact_dict,
            source=source,
            cycle_id=cycle_id
        )
        self.emit_event(ev_com)
        emitted.append(ev_com)

        # 3. Disparar hook de aprendizaje
        self._trigger_learning_hook(fact_dict, ev_com)

        return AgentResponse(
            success=True,
            kind=InputKind.ASSERTION,
            detail=f"Hecho integrado con éxito: {s} —{p}→ {o}",
            data={"fact": fact_dict, "transitions": len(transitions)},
            emitted_events=emitted
        )

    def _handle_command(self, envelope: InputEnvelope, cycle_id: str) -> AgentResponse:
        """Procesa instrucciones operativas y comandos orientados a metas."""
        payload = envelope.payload
        emitted: List[CognitiveEvent] = []

        available_actions = envelope.metadata.get("available_actions", [])

        if isinstance(payload, Goal):
            goal = payload
            goal_desc = str(getattr(goal, "conditions", ""))
        elif isinstance(payload, str):
            # Interpretar comando en lenguaje natural proyectándolo a un Goal formal
            goal, sim, desc = self.natural_language.parse_instruction_to_goal(payload)
            if goal is None:
                return AgentResponse(
                    success=False,
                    kind=InputKind.COMMAND,
                    detail=f"Rechazado epistémicamente: La instrucción no pudo ser proyectada a una meta formal válida (similitud insuficiente: {sim:.2f}).",
                    data={"similarity": sim, "raw_text": payload},
                    emitted_events=emitted
                )
            goal_desc = desc or payload
        else:
            return AgentResponse(
                success=False,
                kind=InputKind.COMMAND,
                detail=f"Payload de comando no soportado: {type(payload)}",
                emitted_events=emitted
            )

        ev_cmd = CognitiveEvent(
            event_type="command_received",
            payload={"goal_desc": goal_desc, "goal_conditions": [list(c) for c in goal.conditions]},
            source=envelope.source,
            cycle_id=cycle_id
        )
        self.emit_event(ev_cmd)
        emitted.append(ev_cmd)

        cycle_result = self.step(goal, available_actions)

        if cycle_result.executed:
            ev_act = CognitiveEvent(
                event_type="action_executed",
                payload={"plan_cost": getattr(cycle_result.plan, "total_cost", getattr(cycle_result.plan, "cost", 0.0)) if cycle_result.plan else 0.0},
                source=envelope.source,
                cycle_id=cycle_id
            )
            self.emit_event(ev_act)
            emitted.append(ev_act)

        if cycle_result.goal_achieved:
            ev_goal = CognitiveEvent(
                event_type="goal_achieved",
                payload={"reward": cycle_result.reward},
                source=envelope.source,
                cycle_id=cycle_id
            )
            self.emit_event(ev_goal)
            emitted.append(ev_goal)

        return AgentResponse(
            success=cycle_result.goal_achieved if cycle_result.plan else True,
            kind=InputKind.COMMAND,
            detail=f"Comando procesado: {cycle_result.environment_feedback}",
            data={"cycle_result": cycle_result},
            emitted_events=emitted
        )

    # =========================================================================
    # APIS RETROCOMPATIBLES PRESERVADAS
    # =========================================================================
    def perceive_environment(self, sensory_readings: List[Dict[str, Any]]) -> int:
        """Wrapper retrocompatible sobre receive(PERCEPTION)."""
        resp = self.receive(InputEnvelope(kind=InputKind.PERCEPTION, payload=sensory_readings))
        return resp.data.get("committed_transitions", 0) if resp.data else 0

    def ingest_text(self, text: str, source: str = "user") -> AgentResponse:
        """Wrapper retrocompatible sobre receive(ASSERTION)."""
        return self.receive(InputEnvelope(kind=InputKind.ASSERTION, payload=text, source=source))

    def parse_instruction(self, text: str, available_actions: Optional[List[Action]] = None) -> AgentResponse:
        """Wrapper retrocompatible sobre receive(COMMAND) para instrucciones textuales."""
        meta = {"available_actions": available_actions} if available_actions else {}
        return self.receive(InputEnvelope(kind=InputKind.COMMAND, payload=text, metadata=meta))

    def achieve_goal(self, goal: Goal, available_actions: Optional[List[Action]] = None) -> AgentCycleResult:
        """Wrapper retrocompatible para ejecución de metas."""
        return self.step(goal, available_actions or [])

    def run_deduction(self) -> int:
        """Ejecuta el cierre deductivo con EngineD sobre las reglas activas."""
        if not self.inference_rules:
            return 0
        return self.engine_d.saturate(self.inference_rules)

    def step(self, goal: Goal, available_actions: List[Action]) -> AgentCycleResult:
        """
        Ejecuta un ciclo cognitivo deliberativo completo del agente:
        INFER -> CONTEXT -> PLAN -> EVALUATE -> ACT -> OBSERVE -> LEARN.
        """
        deductions = self.run_deduction()
        current_state = self.kernel.state

        context = self.context_builder.build_context(current_state, goal)
        self.motor_c.action_priors = self.learner.action_values
        candidate_plan = self.motor_c.plan(current_state, goal, available_actions)

        if candidate_plan is None:
            reward = self.learner.compute_reward(goal_satisfied=False, total_cost=0.0, execution_ok=False)
            return AgentCycleResult(
                goal=goal,
                active_context=context,
                plan=None,
                plan_score=None,
                executed=False,
                goal_achieved=False,
                reward=reward,
                recorded_episode=None,
                new_state=current_state,
                deductions_count=deductions,
                epistemic_claims_count=len(self.knowledge_store.claims),
                environment_feedback="No se encontro ningun plan factible."
            )

        plan_score = self.evaluator.evaluate_plan(
            plan=candidate_plan,
            initial_state=current_state,
            goal=goal,
            episodic_memory=self.episodic_memory,
            action_priors=self.learner.action_values
        )

        executed = False
        goal_achieved = False
        if plan_score.is_valid and plan_score.utility > -100.0:
            executed = self.motor_c.execute(self.kernel, candidate_plan)
            goal_achieved = goal.is_satisfied(self.kernel.state)

        reward, episode = self.learner.update_from_execution(
            plan=candidate_plan,
            goal=goal,
            goal_satisfied=goal_achieved,
            execution_ok=executed,
            episodic_memory=self.episodic_memory
        )

        return AgentCycleResult(
            goal=goal,
            active_context=context,
            plan=candidate_plan,
            plan_score=plan_score,
            executed=executed,
            goal_achieved=goal_achieved,
            reward=reward,
            recorded_episode=episode,
            new_state=self.kernel.state,
            deductions_count=deductions,
            epistemic_claims_count=len(self.knowledge_store.claims),
            environment_feedback="Ejecutado con exito en Kernel." if executed else "Fallo de validacion."
        )
