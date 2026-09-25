"""
reconcile.py - Reconciliación de propuestas cognitivas y perceptuales contra el Kernel MF_MIN.
Clasifica propuestas en:
 - committed: aceptadas para ejecución en el Kernel.
 - redundant: hechos que ya existen idénticos en el Kernel o repetidos entre fuentes.
 - disputed: contradicciones entre fuentes o contra el estado actual del Kernel / incompatibilidad de tipos.
 - deferred: operaciones no reconocidas o postergadas.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Tuple, Optional
from mf_min_definitivo import Kernel, Transition, State, Object, Relation

@dataclass
class Proposal:
    source_id: str
    transition: Transition
    confidence: float = 1.0

@dataclass
class ReconciliationResult:
    committed: List[Transition] = field(default_factory=list)
    redundant: List[Proposal] = field(default_factory=list)
    disputed: List[Proposal] = field(default_factory=list)
    deferred: List[Proposal] = field(default_factory=list)

class Reconciler:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel

    def reconcile(self, proposals: List[Proposal]) -> ReconciliationResult:
        result = ReconciliationResult()
        state = self.kernel.state

        # Registro para detectar colisiones/contradicciones entre fuentes en este batch
        seen_objects: Dict[str, Tuple[str, Proposal]] = {}  # id -> (type, proposal)
        seen_relations: Dict[Tuple[str, str, str], Tuple[bool, Proposal]] = {} # (src, pred, tgt) -> (polarity, proposal)
        seen_exact_trans: Set[str] = set()

        for p in proposals:
            t = p.transition
            op = t.operation
            payload = t.payload

            if op == "add_object":
                obj_id = payload.get("id")
                obj_type = payload.get("type")

                # Chequeo contra Kernel
                if obj_id in state.objects:
                    existing_obj = state.objects[obj_id]
                    if existing_obj.type != obj_type:
                        result.disputed.append(p)
                        continue
                    else:
                        result.redundant.append(p)
                        continue

                # Chequeo entre propuestas concurrentes
                if obj_id in seen_objects:
                    prev_type, prev_p = seen_objects[obj_id]
                    if prev_type != obj_type:
                        result.disputed.append(p)
                        if prev_p.transition in result.committed:
                            result.committed.remove(prev_p.transition)
                            result.disputed.append(prev_p)
                    else:
                        result.redundant.append(p)
                    continue

                seen_objects[obj_id] = (obj_type, p)
                result.committed.append(t)

            elif op == "add_relation":
                src = payload.get("source")
                pred = payload.get("predicate")
                tgt = payload.get("target")
                pol = payload.get("polarity", True)
                edge = (src, pred, tgt)

                # Chequeo contra Kernel: ¿Existe la relación?
                existing_match = [r for r in state.relations.values() if r.source == src and r.predicate == pred and r.target == tgt]
                if existing_match:
                    if any(r.polarity != pol for r in existing_match):
                        # Contradicción contra el Kernel
                        result.disputed.append(p)
                        continue
                    else:
                        # Mismo hecho ya conocido
                        result.redundant.append(p)
                        continue

                # Chequeo entre propuestas de distintas fuentes
                if edge in seen_relations:
                    prev_pol, prev_p = seen_relations[edge]
                    if prev_pol != pol:
                        # Contradicción entre fuentes
                        result.disputed.append(p)
                        if prev_p.transition in result.committed:
                            result.committed.remove(prev_p.transition)
                            result.disputed.append(prev_p)
                    else:
                        # Propuestas iguales entre fuentes: una committed, las demás redundant
                        result.redundant.append(p)
                    continue

                seen_relations[edge] = (pol, p)
                result.committed.append(t)

            elif op in ("remove_object", "remove_relation", "remove_axiom", "batch_derive"):
                result.committed.append(t)

            else:
                # Operación no entendida -> deferred
                result.deferred.append(p)

        return result
