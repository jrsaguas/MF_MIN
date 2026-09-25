"""
================================================================================
CONCEPT_INDUCTION — Abstracción Conceptual e Inducción de Tipos
================================================================================

Este módulo implementa el descubrimiento inductivo de conceptos/clases abstractas
a partir de la estructura relacional observada en el Kernel MF_MIN:
    Entidades concretas con roles compartidos -> Detección de Congruencia ->
    Hipótesis Conceptual -> Auditoría Formal en Kernel Efímero ->
    Reificación Ontológica Atómica en Kernel (Objetos de Clase + 'instancia_de') ->
    Meta-Reglas de Tipificación para EngineD.

Garantías:
1. No requiere ontologías predefinidas (aprende las clases a partir del uso).
2. Preserva el Núcleo Formal MF_MIN = ⟨O, M, A, δ⟩ intacto: los conceptos
   abstractos son Objetos ordinarios de tipo 'AbstractConcept', y la membresía
   se representa como Relaciones ordinarias de tipo 'instancia_de'.
3. Genera Meta-Reglas de Propagación de Tipos compatibles con EngineD.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Mapping, Any

from mf_min_definitivo import (
    Kernel,
    State,
    Relation,
    Transition,
    ContradictionError,
    ValidationError,
    project_pi,
)
from engine_d import Rule, Pattern, EngineD


@dataclass(frozen=True)
class RoleSignature:
    """Firma topológica de los roles relacionales que desempeña una entidad."""
    outgoing_predicates: Tuple[str, ...]
    incoming_predicates: Tuple[str, ...]

    def __hash__(self):
        return hash((self.outgoing_predicates, self.incoming_predicates))


@dataclass
class ConceptHypothesis:
    """
    Representa una hipótesis de clase conceptual inducida a partir de un grupo
    de entidades que comparten roles relacionales.
    """
    id: str
    label: str
    role_type: str  # "subject_cluster", "object_cluster"
    inducing_predicate: str
    role_signature: RoleSignature
    instances: Set[str]
    support_count: int = 0
    confidence: float = 0.0
    status: str = "PROPOSED"  # "PROPOSED", "VALIDATED", "REJECTED"
    justification: str = ""
    complementary_concept_id: Optional[str] = None

    def summary(self) -> str:
        inst_list = ", ".join(sorted(self.instances))
        return (
            f"[{self.status}] Concepto '{self.id}' ({self.label}) | "
            f"Predicado: '{self.inducing_predicate}' ({self.role_type}) | "
            f"Extensión: {{{inst_list}}} (Soporte: {self.support_count}) | "
            f"Conf: {self.confidence:.2f}"
        )


class ConceptInductionEngine:
    """
    Motor de abstracción conceptual que identifica clases latentes y
    las formaliza en el Kernel y en EngineD.
    """

    def __init__(self, min_support: int = 2, default_min_confidence: float = 0.5):
        self.min_support = min_support
        self.default_min_confidence = default_min_confidence

    def extract_role_signatures(self, state: State) -> Dict[str, RoleSignature]:
        """
        Extrae para cada objeto en el estado su firma relacional (predicados salientes y entrantes).
        """
        out_map: Dict[str, Set[str]] = {oid: set() for oid in state.objects.keys()}
        in_map: Dict[str, Set[str]] = {oid: set() for oid in state.objects.keys()}

        for r in state.relations.values():
            if r.polarity is True and r.origin != "proposed":
                if r.source in out_map:
                    out_map[r.source].add(r.predicate)
                if r.target in in_map:
                    in_map[r.target].add(r.predicate)

        signatures: Dict[str, RoleSignature] = {}
        for oid in state.objects.keys():
            signatures[oid] = RoleSignature(
                outgoing_predicates=tuple(sorted(out_map[oid])),
                incoming_predicates=tuple(sorted(in_map[oid]))
            )
        return signatures

    def mine_concepts(self, state: State) -> List[ConceptHypothesis]:
        """
        Identifica predicados recurrentes y propone conceptos abstractos para sus
        roles activo (sujeto) y pasivo (objeto).
        """
        # Agrupar sujetos y objetos por predicado
        subjects_by_pred: Dict[str, Set[str]] = {}
        objects_by_pred: Dict[str, Set[str]] = {}

        for r in state.relations.values():
            if r.polarity is True and r.origin != "proposed":
                # Ignorar relaciones ontológicas meta ya inducidas (instancia_de)
                if r.predicate == "instancia_de":
                    continue
                subjects_by_pred.setdefault(r.predicate, set()).add(r.source)
                objects_by_pred.setdefault(r.predicate, set()).add(r.target)

        hypotheses: List[ConceptHypothesis] = []
        signatures = self.extract_role_signatures(state)

        for pred, subjects in subjects_by_pred.items():
            targets = objects_by_pred.get(pred, set())

            # Criterio de soporte mínimo en sujetos
            if len(subjects) >= self.min_support:
                c_actor_id = f"Concept_{pred}_Actor"
                c_target_id = f"Concept_{pred}_Target"

                # Firma representativa del sujeto
                sample_s = next(iter(subjects))
                sig_s = signatures.get(sample_s, RoleSignature((pred,), ()))

                hyp_actor = ConceptHypothesis(
                    id=c_actor_id,
                    label=f"Rol Activo de '{pred}'",
                    role_type="subject_cluster",
                    inducing_predicate=pred,
                    role_signature=sig_s,
                    instances=set(subjects),
                    support_count=len(subjects),
                    complementary_concept_id=c_target_id,
                    justification=f"Inducido a partir de {len(subjects)} entidades con rol activo en '{pred}'."
                )

                # Concepto objetivo complementario
                sample_t = next(iter(targets)) if targets else ""
                sig_t = signatures.get(sample_t, RoleSignature((), (pred,)))

                hyp_target = ConceptHypothesis(
                    id=c_target_id,
                    label=f"Rol Objetivo de '{pred}'",
                    role_type="object_cluster",
                    inducing_predicate=pred,
                    role_signature=sig_t,
                    instances=set(targets),
                    support_count=len(targets),
                    complementary_concept_id=c_actor_id,
                    justification=f"Inducido a partir de {len(targets)} entidades como destino de '{pred}'."
                )

                hypotheses.append(hyp_actor)
                hypotheses.append(hyp_target)

        return hypotheses

    def audit_and_evaluate(self, hypothesis: ConceptHypothesis, kernel: Kernel) -> ConceptHypothesis:
        """
        Audita una hipótesis conceptual en un Kernel efímero.
        Comprueba que la creación del concepto y sus membresías 'instancia_de'
        no violen ninguna invariante de MF_MIN (I1-I6).
        """
        state = kernel.state
        working_kernel = Kernel(state)

        # 1. Crear el objeto conceptual en el kernel efímero
        try:
            if hypothesis.id not in working_kernel.state.objects:
                working_kernel.transition(Transition("add_object", {
                    "id": hypothesis.id,
                    "type": "AbstractConcept",
                    "properties": {
                        "inducing_predicate": hypothesis.inducing_predicate,
                        "role_type": hypothesis.role_type
                    }
                }))
        except Exception as e:
            hypothesis.status = "REJECTED"
            hypothesis.confidence = 0.0
            hypothesis.justification = f"Fallo al registrar objeto conceptual: {e}"
            return hypothesis

        # 2. Asociar cada instancia
        failures = 0
        for inst in hypothesis.instances:
            rel_id = f"inst_{inst}_{hypothesis.id}"
            try:
                working_kernel.transition(Transition("add_relation", {
                    "id": rel_id,
                    "source": inst,
                    "predicate": "instancia_de",
                    "target": hypothesis.id,
                    "origin": "derived",
                    "rule_id": "concept_induction"
                }))
            except ContradictionError:
                failures += 1
            except ValidationError:
                failures += 1

        if failures > 0:
            hypothesis.status = "REJECTED"
            hypothesis.confidence = 0.0
            hypothesis.justification = f"Rechazado por {failures} contradicciones al asociar instancias."
            return hypothesis

        # Confianza basada en soporte
        support = len(hypothesis.instances)
        hypothesis.confidence = support / (support + 1.0)
        hypothesis.status = "VALIDATED" if hypothesis.confidence >= self.default_min_confidence else "PROPOSED"
        hypothesis.justification += f" [AUDITORÍA OK: {support} instancias formalmente consistentes]."
        return hypothesis

    def induce_concepts(self, kernel: Kernel) -> List[ConceptHypothesis]:
        """Ejecuta el descubrimiento y auditoría de conceptos abstractos."""
        raw = self.mine_concepts(kernel.state)
        validated = []
        for hyp in raw:
            audited = self.audit_and_evaluate(hyp, kernel)
            if audited.status == "VALIDATED" and audited.confidence >= self.default_min_confidence:
                validated.append(audited)
        return validated

    def commit_concepts(self, hypotheses: List[ConceptHypothesis], kernel: Kernel) -> List[Transition]:
        """
        Compromete atómicamente en el Kernel real los conceptos abstractos y sus membresías.
        """
        transitions: List[Transition] = []
        existing_objs = set(kernel.state.objects.keys())
        existing_rels = {(r.source, r.predicate, r.target) for r in kernel.state.relations.values()}

        # 1. Agregar Objetos AbstractConcept
        for h in hypotheses:
            if h.id not in existing_objs:
                transitions.append(Transition("add_object", {
                    "id": h.id,
                    "type": "AbstractConcept",
                    "properties": {
                        "inducing_predicate": h.inducing_predicate,
                        "role_type": h.role_type
                    }
                }))
                existing_objs.add(h.id)

        # 2. Agregar Relaciones 'instancia_de'
        for h in hypotheses:
            for inst in h.instances:
                if (inst, "instancia_de", h.id) not in existing_rels:
                    rel_id = f"inst_{inst}_{h.id}"
                    transitions.append(Transition("add_relation", {
                        "id": rel_id,
                        "source": inst,
                        "predicate": "instancia_de",
                        "target": h.id,
                        "origin": "derived",
                        "rule_id": "concept_induction"
                    }))
                    existing_rels.add((inst, "instancia_de", h.id))

        # 3. Agregar Esquemas de Orden Superior entre Conceptos Complementarios: (C_actor -> p -> C_target)
        for h in hypotheses:
            if h.role_type == "subject_cluster" and h.complementary_concept_id:
                tgt_id = h.complementary_concept_id
                if (h.id, h.inducing_predicate, tgt_id) not in existing_rels:
                    schema_rel_id = f"schema_{h.inducing_predicate}_{h.id}_{tgt_id}"
                    transitions.append(Transition("add_relation", {
                        "id": schema_rel_id,
                        "source": h.id,
                        "predicate": h.inducing_predicate,
                        "target": tgt_id,
                        "origin": "derived",
                        "rule_id": "concept_schema_induction"
                    }))
                    existing_rels.add((h.id, h.inducing_predicate, tgt_id))

        if transitions:
            kernel.transition_batch(transitions)

        return transitions

    def generate_type_propagation_rules(self, hypotheses: List[ConceptHypothesis]) -> List[Rule]:
        """
        Genera meta-reglas de propagación de tipos para EngineD:
        Dada la relación P(X, Y), si X es instancia de C_actor, se induce que Y es instancia de C_target.
        """
        rules: List[Rule] = []
        seen = set()

        for h in hypotheses:
            if h.role_type == "subject_cluster" and h.complementary_concept_id:
                p = h.inducing_predicate
                c_act = h.id
                c_tgt = h.complementary_concept_id
                pair_key = (p, c_act, c_tgt)
                if pair_key in seen:
                    continue
                seen.add(pair_key)

                # Regla: instancia_de(?X, C_act) ∧ P(?X, ?Y) => instancia_de(?Y, C_tgt)
                r_fwd = Rule(
                    id=f"rule_infer_type_tgt_{p}",
                    name=f"Propagación de tipo objetivo para '{p}'",
                    premises=(
                        Pattern("instancia_de", "?X", c_act, True),
                        Pattern(p, "?X", "?Y", True),
                    ),
                    conclusion=Pattern("instancia_de", "?Y", c_tgt, True)
                )
                rules.append(r_fwd)

                # Regla dual: P(?X, ?Y) ∧ instancia_de(?Y, C_tgt) => instancia_de(?X, C_act)
                r_bwd = Rule(
                    id=f"rule_infer_type_act_{p}",
                    name=f"Propagación de tipo actor para '{p}'",
                    premises=(
                        Pattern(p, "?X", "?Y", True),
                        Pattern("instancia_de", "?Y", c_tgt, True),
                    ),
                    conclusion=Pattern("instancia_de", "?X", c_act, True)
                )
                rules.append(r_bwd)

        return rules

