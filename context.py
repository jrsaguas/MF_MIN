"""
context.py - Construcción y Firma de Contexto Activo (ActiveContext y ContextSignature).
Sintetiza el estado formal de MF_MIN, recuerdos recuperados, antecedentes episódicos,
el vector de atención Q/K/V y genera una firma contextual canónica inmutable (ContextSignature)
que sirve como clave 's' para el aprendizaje contextual Q(s, a).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Optional, Dict, Set, Mapping
import hashlib
import numpy as np

from mf_min_definitivo import State
from motor_c import Goal
from memory import MemoryItem, Episode
from attention import AttentionEngine
from embeddings import VectorEmbeddingEngine
from retrieval import Retriever


@dataclass(frozen=True)
class ContextSignature:
    """
    Firma canónica, determinista e inmutable del contexto cognitivo.
    Sirve como clave 's' para Q(s, a) y como punto de anclaje para generalización.

    Jerarquía:
      1. exact_key: Firma canónica estricta (Hechos focales + Objetivo + Acciones aplicables).
      2. structural_key: Firma canónica estructural (Hechos focales + Objetivo, sin acciones).
      3. focal_relations: Tupla ordenada de cuádruplas (source, predicate, target, polarity).
      4. goal_conditions: Tupla ordenada de condiciones del objetivo.
      5. applicable_actions: Tupla ordenada de nombres de acciones ejecutables.
      6. domain_hint: Identificador de dominio/espacio de nombres (evita contaminación cruzada).
    """
    exact_key: str
    structural_key: str
    focal_relations: Tuple[Tuple[str, str, str, bool], ...]
    goal_conditions: Tuple[Tuple[str, str, str, bool], ...]
    applicable_actions: Tuple[str, ...]
    domain_hint: str = "general"

    def to_dict(self) -> Dict[str, Any]:
        """Serialización determinista para checkpoints y persistencia JSON."""
        return {
            "exact_key": self.exact_key,
            "structural_key": self.structural_key,
            "focal_relations": [list(r) for r in self.focal_relations],
            "goal_conditions": [list(c) for c in self.goal_conditions],
            "applicable_actions": list(self.applicable_actions),
            "domain_hint": self.domain_hint,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ContextSignature":
        """Reconstrucción determinista a partir de datos serializados."""
        return cls(
            exact_key=data["exact_key"],
            structural_key=data["structural_key"],
            focal_relations=tuple(tuple(r) for r in data.get("focal_relations", ())),
            goal_conditions=tuple(tuple(c) for c in data.get("goal_conditions", ())),
            applicable_actions=tuple(data.get("applicable_actions", ())),
            domain_hint=data.get("domain_hint", "general"),
        )

    def summary(self) -> str:
        focal_str = "; ".join(f"{s}-{p}->{t}({pol})" for s, p, t, pol in self.focal_relations)
        goal_str = "; ".join(f"{s}-{p}->{t}({pol})" for s, p, t, pol in self.goal_conditions)
        acts_str = ",".join(self.applicable_actions)
        return f"[ContextSignature {self.exact_key[:12]}] Focal: [{focal_str}] | Goal: [{goal_str}] | Acts: [{acts_str}]"


def extract_focal_relations(
    state: State,
    goal: Goal,
    max_focal_threshold: int = 25
) -> Tuple[Tuple[str, str, str, bool], ...]:
    """
    Extrae la proyección relacional focalmente relevante para el contexto actual.
    
    Estrategia inteligente multirriesgo:
    - Si el estado tiene <= max_focal_threshold relaciones (caso habitual en dominios cerrados),
      conserva todas las relaciones activas ordenadas canónicamente por (source, predicate, target, polarity).
      Esto garantiza CERO pérdida de información y CERO falsos negativos.
    - Si el estado supera el umbral (estados grandes), filtra a la vecindad de 1 salto de las entidades
      focales: el Agente, su ubicación y los objetos/propiedades explícitamente citados en Goal.
      Esto evita la explosión combinatoria.
    - Los IDs de relación (r1, r_test, etc.) son completamente omitidos para asegurar que
      dos estados formalmente isomórficos bajo π produzcan la misma clave.
    """
    all_rels = [
        (r.source, r.predicate, r.target, r.polarity)
        for r in state.relations.values()
        if r.polarity is not None and r.origin != "proposed"
    ]

    if len(all_rels) <= max_focal_threshold:
        return tuple(sorted(all_rels))

    # Identificar entidades focales
    focal_entities: Set[str] = set()
    for c in goal.conditions:
        focal_entities.add(c[0])
        focal_entities.add(c[2])

    for oid, obj in state.objects.items():
        if obj.type in ("Agent", "Persona", "Robot") or oid in ("agente", "persona"):
            focal_entities.add(oid)

    # Si encontramos al agente, incluir entidades con las que interactúa directamente
    for r in state.relations.values():
        if r.source in focal_entities or r.target in focal_entities:
            focal_entities.add(r.source)
            focal_entities.add(r.target)

    # Filtrar hechos que involucren entidades focales
    filtered = [
        (r.source, r.predicate, r.target, r.polarity)
        for r in state.relations.values()
        if (r.source in focal_entities or r.target in focal_entities) and r.origin != "proposed"
    ]

    return tuple(sorted(filtered))


@dataclass
class ActiveContext:
    """Estructura rica del contexto activo disponible para la toma de decisiones."""
    state: State
    goal: Goal
    goal_embedding: np.ndarray
    context_vector: np.ndarray
    declarative_items: List[MemoryItem] = field(default_factory=list)
    episodes: List[Episode] = field(default_factory=list)
    attention_weights: List[float] = field(default_factory=list)
    ranked_memories: List[Tuple[float, Any]] = field(default_factory=list)
    signature: Optional[ContextSignature] = None


class ContextBuilder:
    """Constructor del contexto cognitivo integrado y generador de firmas contextuales."""
    def __init__(
        self,
        retriever: Retriever,
        attention_engine: AttentionEngine,
        embedder: Optional[VectorEmbeddingEngine] = None
    ):
        self.retriever = retriever
        self.attention = attention_engine
        self.embedder = embedder or VectorEmbeddingEngine()

    def build_context_signature(
        self,
        state: State,
        goal: Goal,
        available_actions: Optional[List[Any]] = None,
        domain_hint: str = "general"
    ) -> ContextSignature:
        """
        Genera la firma determinista inmutable para un estado y objetivo.
        """
        focal_rels = extract_focal_relations(state, goal)
        goal_conds = tuple(sorted(list(goal.conditions)))

        act_names: List[str] = []
        if available_actions:
            for act in available_actions:
                name = getattr(act, "name", str(act))
                # Considerar solo acciones que sean aplicables en este estado
                if hasattr(act, "is_applicable"):
                    if act.is_applicable(state):
                        act_names.append(name)
                else:
                    act_names.append(name)
        act_tuple = tuple(sorted(act_names))

        # Serialización canónica para hashing
        repr_structural = f"DOM:{domain_hint}|FOCAL:{focal_rels}|GOAL:{goal_conds}"
        repr_exact = f"{repr_structural}|ACTS:{act_tuple}"

        struct_hash = hashlib.sha256(repr_structural.encode("utf-8")).hexdigest()[:16]
        exact_hash = hashlib.sha256(repr_exact.encode("utf-8")).hexdigest()[:16]

        struct_key = f"CTX_STR_{struct_hash}"
        exact_key = f"CTX_EXT_{exact_hash}"

        return ContextSignature(
            exact_key=exact_key,
            structural_key=struct_key,
            focal_relations=focal_rels,
            goal_conditions=goal_conds,
            applicable_actions=act_tuple,
            domain_hint=domain_hint
        )

    def build_context(
        self,
        state: State,
        goal: Goal,
        available_actions: Optional[List[Any]] = None,
        domain_hint: str = "general"
    ) -> ActiveContext:
        """
        Construye el contexto activo y calcula su ContextSignature correspondiente.
        """
        goal_vec = self.embedder.embed_goal(list(goal.conditions))

        # 1. Recuperar memorias declarativas relevantes
        decl_results = self.retriever.retrieve_declarative(str(goal.conditions), top_k=5)
        decl_items = [item for _, item in decl_results]

        # 2. Recuperar episodios análogos
        ep_results = self.retriever.retrieve_episodes(goal_vec, top_k=3)
        episodes = [ep for _, ep in ep_results]

        # 3. Preparar vectores K y V para atención
        all_candidates = []
        keys = []
        for it in decl_items:
            vec = it.embedding if it.embedding is not None else self.embedder.embed_text(it.content)
            keys.append(vec)
            all_candidates.append(it)

        for ep in episodes:
            vec = ep.goal_embedding if ep.goal_embedding is not None else self.embedder.embed_text(ep.goal_desc)
            keys.append(vec)
            all_candidates.append(ep)

        # 4. Calcular atención QKV si hay candidatos
        if keys:
            context_vec, weights, ranked = self.attention.attend_qkv(
                query_vector=goal_vec,
                keys=keys,
                values=all_candidates
            )
        else:
            context_vec = np.zeros((self.attention.dim,), dtype=np.float32)
            weights = []
            ranked = []

        # 5. Generar firma contextual
        signature = self.build_context_signature(state, goal, available_actions, domain_hint)

        return ActiveContext(
            state=state,
            goal=goal,
            goal_embedding=goal_vec,
            context_vector=context_vec,
            declarative_items=decl_items,
            episodes=episodes,
            attention_weights=weights,
            ranked_memories=ranked,
            signature=signature
        )

