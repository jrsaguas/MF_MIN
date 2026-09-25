"""
semantic_bridge.py - Puente Semántico: SemanticFrame -> Knowledge Layer -> MF_MIN.
Transforma el IR semántico en entidades y claims evaluados, y genera las transiciones
formales correspondientes para el Kernel con proyección garantizada en 2 pasos:
 1. Proyectar Entidades como Objetos formales (O).
 2. Proyectar Claims como Relaciones formales (M).
"""
from __future__ import annotations
import hashlib
import time
from typing import List, Tuple, Dict, Any, Optional
from mf_min_definitivo import Transition, Kernel
from knowledge_codec import SemanticFrame
from knowledge import Entity, Claim, Evidence, Provenance, EpistemicStatus
from epistemic import EpistemicEvaluator
from knowledge_store import KnowledgeStore

def time_hash(s: str) -> str:
    return hashlib.md5(f"{s}_{time.time()}".encode('utf-8')).hexdigest()[:6]

class SemanticBridge:
    def __init__(self, epistemic_evaluator: Optional[EpistemicEvaluator] = None):
        self.evaluator = epistemic_evaluator or EpistemicEvaluator()

    def frame_to_knowledge(
        self,
        frame: SemanticFrame,
        source: str = "user_input",
        modality: str = "text"
    ) -> Tuple[List[Entity], List[Claim]]:
        """
        Convierte un SemanticFrame en entidades canónicas y claims enriquecidos.
        """
        entities = [
            Entity(id=e["id"], type=e.get("type", "Entity"), label=e.get("label", e["id"]))
            for e in frame.entities
        ]

        claims = []
        for r in frame.relations:
            ev = Evidence(
                id=f"ev_{source}_{time_hash(r['subject'] + r['predicate'])}",
                source=source,
                reliability=r.get("confidence", frame.confidence),
                modality=modality,
                raw_data=frame.text
            )
            prov = Provenance(origin="semantic_bridge", actor=source)
            cl = Claim(
                subject=r["subject"],
                predicate=r["predicate"],
                object=r["object"],
                polarity=r.get("polarity", True),
                confidence_interpretation=frame.confidence,
                confidence_evidence=ev.reliability,
                provenance=prov,
                evidences=[ev]
            )
            claims.append(cl)

        return entities, claims

    def project_to_kernel_transitions(
        self,
        entities: List[Entity],
        claims: List[Claim],
        store: KnowledgeStore,
        kernel: Kernel
    ) -> List[Transition]:
        """
        Proyección formal estricta en 2 tiempos hacia MF_MIN:
        Tiempo 1: Dar de alta los objetos en O si no existen aún.
        Tiempo 2: Dar de alta las relaciones válidas en M.
        Garantiza que jamás ocurra MissingReferenceError.
        """
        transitions: List[Transition] = []
        state = kernel.state

        # Registro de IDs que ya existen o se crearán en este batch
        known_objects = set(state.objects.keys())

        # Tiempo 1: Proyección de Objetos
        for ent in entities:
            if ent.id not in known_objects:
                trans_obj = Transition("add_object", {
                    "id": ent.id,
                    "type": ent.type,
                    "properties": dict(ent.properties)
                })
                transitions.append(trans_obj)
                known_objects.add(ent.id)

        # Tiempo 2: Proyección de Relaciones (solo para claims evaluados y promovibles)
        for c in claims:
            # Asegurar que los extremos existan en O antes de evaluar la relación
            if c.subject not in known_objects:
                trans_s = Transition("add_object", {"id": c.subject, "type": "Entity"})
                transitions.append(trans_s)
                known_objects.add(c.subject)

            if c.object not in known_objects:
                trans_o = Transition("add_object", {"id": c.object, "type": "Entity"})
                transitions.append(trans_o)
                known_objects.add(c.object)

            # Evaluación epistemológica formal
            status = self.evaluator.evaluate_claim(c, store)
            if self.evaluator.can_promote_to_kernel(c):
                rel_id = f"r_kb_{c.subject}_{c.predicate}_{c.object}"
                if rel_id not in state.relations:
                    trans_rel = Transition("add_relation", {
                        "id": rel_id,
                        "source": c.subject,
                        "predicate": c.predicate,
                        "target": c.object,
                        "polarity": c.polarity,
                        "origin": "asserted"
                    })
                    transitions.append(trans_rel)

        return transitions
