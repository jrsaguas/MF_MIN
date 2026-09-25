"""
epistemic.py - Motor de Evaluación Epistemológica.
Determina qué justificación tiene cada conocimiento, gestiona contradicciones
sin destruir información y evalúa si una afirmación puede promocionarse a MF_MIN.
"""
from __future__ import annotations
from typing import List, Tuple, Optional
from mf_min_definitivo import Kernel, Transition, Relation, ContradictionError
from knowledge import Claim, EpistemicStatus
from knowledge_store import KnowledgeStore

class EpistemicEvaluator:
    """
    Evaluador epistemológico que audita propuestas de conocimiento antes y durante
    su incorporación en el sistema cognitivo.
    """
    def __init__(self, kernel: Optional[Kernel] = None):
        self.kernel = kernel or Kernel()

    def evaluate_claim(self, claim: Claim, store: KnowledgeStore) -> EpistemicStatus:
        """
        Evalúa el estatus epistemológico de un Claim considerando evidencia y consistencia lógica.
        """
        # 1. Comprobar contradicción directa con el KnowledgeStore
        opp_claims = store.query_claims(
            subject=claim.subject,
            predicate=claim.predicate,
            object_=claim.object,
            polarity=(not claim.polarity)
        )
        if opp_claims:
            claim.status = EpistemicStatus.CONTRADICTED
            for opp in opp_claims:
                opp.status = EpistemicStatus.CONTRADICTED
            return EpistemicStatus.CONTRADICTED

        # 2. Comprobar compatibilidad formal con los axiomas del Kernel MF_MIN
        try:
            # Crear kernel candidato de prueba (dry-run)
            candidate = Kernel(self.kernel.state)
            test_rel = Transition("add_relation", {
                "id": f"test_claim_{claim.subject}_{claim.predicate}",
                "source": claim.subject,
                "predicate": claim.predicate,
                "target": claim.object,
                "polarity": claim.polarity
            })
            candidate.transition(test_rel)
            claim.confidence_logical = 1.0
        except ContradictionError:
            # Viola axiomas formales inmutables
            claim.status = EpistemicStatus.REJECTED
            claim.confidence_logical = 0.0
            return EpistemicStatus.REJECTED
        except Exception:
            # Incompatibilidad referencial u otra
            claim.confidence_logical = 0.5

        # 3. Comprobar respaldo de evidencia
        if not claim.evidences:
            claim.status = EpistemicStatus.ASSERTED
            return EpistemicStatus.ASSERTED

        # Promedio ponderado de fiabilidad de fuentes
        avg_rel = sum(e.reliability for e in claim.evidences) / len(claim.evidences)
        claim.confidence_evidence = avg_rel

        if avg_rel >= 0.75 and claim.confidence_interpretation >= 0.8:
            claim.status = EpistemicStatus.SUPPORTED
        else:
            claim.status = EpistemicStatus.ASSERTED

        return claim.status

    def can_promote_to_kernel(self, claim: Claim, threshold: float = 0.6) -> bool:
        """
        Determina si un Claim tiene la suficiente justificación epistemológica y lógica
        para ser comisionado como hecho formal inmutable en el Kernel MF_MIN.
        """
        if claim.status in (EpistemicStatus.REJECTED, EpistemicStatus.CONTRADICTED):
            return False
        if claim.status in (EpistemicStatus.SUPPORTED, EpistemicStatus.DERIVED):
            return True
        # Para ASSERTED, solo si la confianza compuesta supera el umbral
        return claim.composite_confidence >= threshold
