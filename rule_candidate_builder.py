"""
rule_candidate_builder.py — Constructor y Descubridor de Reglas Candidatas.

Implementa la inducción estructural basada en eventos y hechos observados:
- Observa hechos consolidados en el Kernel (origin != "derived").
- Detecta regularidades abstractas mediante índices estructurales eficientes.
- Genera y mantiene hipótesis deterministas como CandidateRule.
- Rastrea soporte empírico y contraejemplos explícitos (ausencia != negación).
- Realiza validación controlada y promoción a Rule de EngineD.
- Seguridad epistémica estricta: nunca muta directamente el Kernel.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set, Any
import hashlib
import time

from engine_d import Rule, Pattern, ValidationError


class CandidateStatus(str, Enum):
    PROPOSED = "PROPOSED"
    VALIDATING = "VALIDATING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass
class CandidateRule:
    """
    Representación formal de una hipótesis de regla inducida.
    """
    candidate_id: str
    pattern_type: str  # "transitivity", "symmetry", "composition"
    premises: Tuple[Pattern, ...]
    conclusion: Pattern
    support_count: int = 0
    counterexample_count: int = 0
    confidence: float = 0.0
    evidence_ids: List[str] = field(default_factory=list)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    status: CandidateStatus = CandidateStatus.PROPOSED
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Serialización determinista para persistencia."""
        return {
            "candidate_id": self.candidate_id,
            "pattern_type": self.pattern_type,
            "premises": [
                {"predicate": p.predicate, "source": p.source, "target": p.target, "polarity": p.polarity}
                for p in self.premises
            ],
            "conclusion": {
                "predicate": self.conclusion.predicate,
                "source": self.conclusion.source,
                "target": self.conclusion.target,
                "polarity": self.conclusion.polarity
            },
            "support_count": self.support_count,
            "counterexample_count": self.counterexample_count,
            "confidence": self.confidence,
            "evidence_ids": list(self.evidence_ids),
            "observations": list(self.observations),
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CandidateRule":
        premises = tuple(
            Pattern(
                predicate=p["predicate"],
                source=p["source"],
                target=p["target"],
                polarity=p.get("polarity", True)
            )
            for p in data["premises"]
        )
        conc_data = data["conclusion"]
        conclusion = Pattern(
            predicate=conc_data["predicate"],
            source=conc_data["source"],
            target=conc_data["target"],
            polarity=conc_data.get("polarity", True)
        )
        return cls(
            candidate_id=data["candidate_id"],
            pattern_type=data["pattern_type"],
            premises=premises,
            conclusion=conclusion,
            support_count=data.get("support_count", 0),
            counterexample_count=data.get("counterexample_count", 0),
            confidence=data.get("confidence", 0.0),
            evidence_ids=data.get("evidence_ids", []),
            observations=data.get("observations", []),
            status=CandidateStatus(data.get("status", "PROPOSED")),
            created_at=data.get("created_at", time.time()),
        )

    def summary(self) -> str:
        prem_str = " ∧ ".join(f"{p.predicate}({p.source}, {p.target})" for p in self.premises)
        conc_str = f"{self.conclusion.predicate}({self.conclusion.source}, {self.conclusion.target})"
        return (
            f"[{self.status.value}] {self.candidate_id} ({self.pattern_type}): "
            f"{prem_str} => {conc_str} | Conf: {self.confidence:.2f} "
            f"(Supp: {self.support_count}, Contra: {self.counterexample_count})"
        )


class RuleCandidateBuilder:
    """
    Descubridor y evaluador inductivo de reglas.
    Observa hechos primarios (ASSERTED/PERCEIVED) y construye hipótesis estructurales.
    """

    def __init__(self, min_support: int = 2, min_precision: float = 0.8):
        self.min_support = min_support
        self.min_precision = min_precision
        self.candidates: Dict[str, CandidateRule] = {}
        
        # Índices estructurales para evitar O(N^2)
        # (pred) -> set of (source, target)
        self.predicate_index: Dict[str, Set[Tuple[str, str]]] = {}
        # (pred, source) -> set of target
        self.source_index: Dict[Tuple[str, str], Set[str]] = {}
        # (pred, target) -> set of source
        self.target_index: Dict[Tuple[str, str], Set[str]] = {}
        
        # Hechos positivos y negativos conocidos: (source, predicate, target) -> polarity
        self.known_polarities: Dict[Tuple[str, str, str], bool] = {}
        # Registro de evidencias por triple
        self.fact_evidences: Dict[Tuple[str, str, str], List[str]] = {}

    @classmethod
    def compute_candidate_id(cls, pattern_type: str, premises: Tuple[Pattern, ...], conclusion: Pattern) -> str:
        """
        Calcula una identidad determinista basada en SHA-256 de la forma canónica abstracta.
        Dos observaciones de la misma regularidad generan exactamente el mismo candidate_id.
        """
        canonical_premises = tuple(
            sorted((p.predicate, p.source, p.target, p.polarity) for p in premises)
        )
        canonical_conc = (conclusion.predicate, conclusion.source, conclusion.target, conclusion.polarity)
        raw_repr = f"{pattern_type}::{canonical_premises}::{canonical_conc}"
        digest = hashlib.sha256(raw_repr.encode("utf-8")).hexdigest()[:12]
        return f"CR_{pattern_type[:4]}_{digest}"

    def observe(self, fact: Dict[str, Any], evidence_id: Optional[str] = None) -> List[CandidateRule]:
        """
        Punto de anclaje de aprendizaje: observa un hecho consolidado.
        Previene autoalimentación descartando hechos derivados (origin == 'derived').
        """
        origin = fact.get("origin", "asserted")
        if origin == "derived":
            # REGLA FUNDAMENTAL 23: hechos derivados no generan evidencia primaria para descubrir reglas
            return []

        s = str(fact["subject"]).strip()
        p = str(fact["predicate"]).strip()
        o = str(fact["object"]).strip()
        pol = bool(fact.get("polarity", True))
        ev_id = evidence_id or fact.get("evidence_id") or f"ev_{s}_{p}_{o}"

        triple = (s, p, o)
        self.known_polarities[triple] = pol
        self.fact_evidences.setdefault(triple, []).append(ev_id)

        # Si es un hecho negativo, actualizar contraejemplos sobre hipótesis activas
        if not pol:
            return self._record_negative_observation(s, p, o, ev_id)

        # Si es positivo, indexar
        self.predicate_index.setdefault(p, set()).add((s, o))
        self.source_index.setdefault((p, s), set()).add(o)
        self.target_index.setdefault((p, o), set()).add(s)

        updated_candidates: List[CandidateRule] = []

        # 1. Explorar cadenas de transitividad: P(X, Y) ∧ P(Y, Z) => P(X, Z)
        trans_candidates = self._check_transitivity_regularity(s, p, o, ev_id)
        updated_candidates.extend(trans_candidates)

        # 2. Explorar simetría: P(X, Y) => P(Y, X)
        symm_candidates = self._check_symmetry_regularity(s, p, o, ev_id)
        updated_candidates.extend(symm_candidates)

        return updated_candidates

    def _check_transitivity_regularity(self, s: str, p: str, o: str, ev_id: str) -> List[CandidateRule]:
        """
        Busca si el nuevo hecho (s, p, o) forma o completa una cadena transitiva P(X, Y) ∧ P(Y, Z) => P(X, Z).
        """
        updated = []

        # Caso A: (s, p, o) es la conclusión (A, p, C) que cierra una cadena existente (A, p, B) y (B, p, C)
        # Buscamos B tal que (s, p, B) y (B, p, o) existan positivamente
        targets_from_s = self.source_index.get((p, s), set())
        sources_to_o = self.target_index.get((p, o), set())
        middle_nodes = targets_from_s.intersection(sources_to_o)

        for b in middle_nodes:
            if b != s and b != o and s != o:
                # Regularidad observada: s->b y b->o y s->o
                cand = self._get_or_create_transitivity_candidate(p)
                self._register_support(cand, {
                    "type": "transitivity",
                    "instance": (s, b, o),
                    "premises": [(s, p, b), (b, p, o)],
                    "conclusion": (s, p, o),
                    "evidence_id": ev_id
                })
                updated.append(cand)

        # Caso B: (s, p, o) es el paso 1 (A -> B), buscamos B -> C tal que A -> C ya sea conocido
        targets_from_o = self.source_index.get((p, o), set())
        for c in targets_from_o:
            if c != s and c != o:
                conclusion_triple = (s, p, c)
                if self.known_polarities.get(conclusion_triple) is True:
                    cand = self._get_or_create_transitivity_candidate(p)
                    self._register_support(cand, {
                        "type": "transitivity",
                        "instance": (s, o, c),
                        "premises": [(s, p, o), (o, p, c)],
                        "conclusion": (s, p, c),
                        "evidence_id": ev_id
                    })
                    updated.append(cand)
                elif self.known_polarities.get(conclusion_triple) is False:
                    cand = self._get_or_create_transitivity_candidate(p)
                    self._register_counterexample(cand, (s, o, c), ev_id)
                    updated.append(cand)

        # Caso C: (s, p, o) es el paso 2 (B -> C), buscamos A -> B tal que A -> C ya sea conocido
        sources_to_s = self.target_index.get((p, s), set())
        for a in sources_to_s:
            if a != s and a != o:
                conclusion_triple = (a, p, o)
                if self.known_polarities.get(conclusion_triple) is True:
                    cand = self._get_or_create_transitivity_candidate(p)
                    self._register_support(cand, {
                        "type": "transitivity",
                        "instance": (a, s, o),
                        "premises": [(a, p, s), (s, p, o)],
                        "conclusion": (a, p, o),
                        "evidence_id": ev_id
                    })
                    updated.append(cand)
                elif self.known_polarities.get(conclusion_triple) is False:
                    cand = self._get_or_create_transitivity_candidate(p)
                    self._register_counterexample(cand, (a, s, o), ev_id)
                    updated.append(cand)

        return updated

    def _check_symmetry_regularity(self, s: str, p: str, o: str, ev_id: str) -> List[CandidateRule]:
        """
        Busca regularidad simétrica P(X, Y) => P(Y, X).
        """
        updated = []
        if s == o:
            return updated

        # Comprobar si existe el recíproco positivo (o, p, s)
        if self.known_polarities.get((o, p, s)) is True:
            cand = self._get_or_create_symmetry_candidate(p)
            self._register_support(cand, {
                "type": "symmetry",
                "instance": (s, o),
                "premises": [(s, p, o)],
                "conclusion": (o, p, s),
                "evidence_id": ev_id
            })
            updated.append(cand)
        elif self.known_polarities.get((o, p, s)) is False:
            cand = self._get_or_create_symmetry_candidate(p)
            self._register_counterexample(cand, (s, o), ev_id)
            updated.append(cand)

        return updated

    def _get_or_create_transitivity_candidate(self, predicate: str) -> CandidateRule:
        premises = (
            Pattern(predicate=predicate, source="?X", target="?Y", polarity=True),
            Pattern(predicate=predicate, source="?Y", target="?Z", polarity=True),
        )
        conclusion = Pattern(predicate=predicate, source="?X", target="?Z", polarity=True)
        cand_id = self.compute_candidate_id("transitivity", premises, conclusion)

        if cand_id not in self.candidates:
            self.candidates[cand_id] = CandidateRule(
                candidate_id=cand_id,
                pattern_type="transitivity",
                premises=premises,
                conclusion=conclusion,
            )
        return self.candidates[cand_id]

    def _get_or_create_symmetry_candidate(self, predicate: str) -> CandidateRule:
        premises = (
            Pattern(predicate=predicate, source="?X", target="?Y", polarity=True),
        )
        conclusion = Pattern(predicate=predicate, source="?Y", target="?X", polarity=True)
        cand_id = self.compute_candidate_id("symmetry", premises, conclusion)

        if cand_id not in self.candidates:
            self.candidates[cand_id] = CandidateRule(
                candidate_id=cand_id,
                pattern_type="symmetry",
                premises=premises,
                conclusion=conclusion,
            )
        return self.candidates[cand_id]

    def _register_support(self, candidate: CandidateRule, observation_data: Dict[str, Any]) -> None:
        """Registra una instancia positiva confirmatoria."""
        # Evitar contar exactamente la misma instancia dos veces
        inst = observation_data.get("instance")
        already_seen = any(obs.get("instance") == inst for obs in candidate.observations)
        if not already_seen:
            candidate.support_count += 1
            candidate.observations.append(observation_data)
            ev_id = observation_data.get("evidence_id")
            if ev_id and ev_id not in candidate.evidence_ids:
                candidate.evidence_ids.append(ev_id)
            
            # Recalcular confianza laplaciana
            total = candidate.support_count + candidate.counterexample_count
            candidate.confidence = (candidate.support_count + 1.0) / (total + 2.0)

    def _register_counterexample(self, candidate: CandidateRule, instance: Any, ev_id: str) -> None:
        """Registra un contraejemplo empírico negativo explícito."""
        candidate.counterexample_count += 1
        if ev_id and ev_id not in candidate.evidence_ids:
            candidate.evidence_ids.append(ev_id)
        total = candidate.support_count + candidate.counterexample_count
        candidate.confidence = (candidate.support_count + 1.0) / (total + 2.0)
        # Si hay contraejemplos, se rechaza
        candidate.status = CandidateStatus.REJECTED

    def _record_negative_observation(self, s: str, p: str, o: str, ev_id: str) -> List[CandidateRule]:
        """Maneja la observación de un hecho negativo explícito (s, p, o, False)."""
        updated = []
        for cand in self.candidates.values():
            if cand.conclusion.predicate == p:
                # Comprobar si alguna observación previa vincula (s, o)
                if cand.pattern_type == "transitivity":
                    # Si existen premisas s->b y b->o pero la conclusión s->o es falsa
                    targets_from_s = self.source_index.get((p, s), set())
                    sources_to_o = self.target_index.get((p, o), set())
                    if targets_from_s.intersection(sources_to_o):
                        self._register_counterexample(cand, (s, o), ev_id)
                        updated.append(cand)
                elif cand.pattern_type == "symmetry":
                    if self.known_polarities.get((o, p, s)) is True:
                        self._register_counterexample(cand, (s, o), ev_id)
                        updated.append(cand)
        return updated

    def get_candidates(self) -> List[CandidateRule]:
        return list(self.candidates.values())

    def get_candidate(self, candidate_id: str) -> Optional[CandidateRule]:
        return self.candidates.get(candidate_id)

    def validate(
        self,
        candidate_id: str,
        knowledge: Optional[Any] = None,
        min_support: Optional[int] = None,
        min_precision: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Valida rigurosamente un candidato contra la memoria empírica disponible.
        Exige soporte mínimo y ausencia de contraejemplos.
        """
        cand = self.get_candidate(candidate_id)
        if not cand:
            raise ValidationError(f"Candidato '{candidate_id}' no encontrado.")

        req_support = min_support if min_support is not None else self.min_support
        req_precision = min_precision if min_precision is not None else self.min_precision

        total = cand.support_count + cand.counterexample_count
        precision = cand.support_count / total if total > 0 else 0.0
        coverage = cand.support_count

        if cand.counterexample_count > 0:
            cand.status = CandidateStatus.REJECTED
            cand.confidence = 0.0
        elif cand.support_count >= req_support and precision >= req_precision:
            cand.status = CandidateStatus.ACCEPTED
            cand.confidence = (cand.support_count + 1.0) / (total + 2.0)
        else:
            cand.status = CandidateStatus.VALIDATING
            cand.confidence = (cand.support_count + 1.0) / (total + 2.0)

        return {
            "candidate_id": cand.candidate_id,
            "status": cand.status.value,
            "support": cand.support_count,
            "counterexamples": cand.counterexample_count,
            "precision": precision,
            "coverage": coverage,
            "confidence": cand.confidence,
            "is_valid": cand.status == CandidateStatus.ACCEPTED
        }

    def promote(self, candidate_id: str) -> Optional[Rule]:
        """
        Promoción controlada: convierte una CandidateRule en una Rule activa de EngineD.
        REGLA FUNDAMENTAL 20 y 26: solo se promueve si fue VALIDADA y ACCEPTED.
        """
        cand = self.get_candidate(candidate_id)
        if not cand:
            return None

        # Si aún está en propuesta o validación, intentar validar primero
        if cand.status != CandidateStatus.ACCEPTED:
            val = self.validate(candidate_id)
            if not val["is_valid"]:
                return None

        # Construir Rule de EngineD con nombre e ID limpios
        rule_name = f"Regla inducida de {cand.pattern_type} para '{cand.conclusion.predicate}'"
        rule = Rule(
            id=f"ind_{cand.pattern_type}_{cand.conclusion.predicate}",
            name=rule_name,
            premises=cand.premises,
            conclusion=cand.conclusion
        )
        return rule

    def explain(self, candidate_id: str) -> str:
        """Genera una explicación estructurada real a partir de los datos internos."""
        cand = self.get_candidate(candidate_id)
        if not cand:
            return f"Candidato '{candidate_id}' no encontrado."

        prem_str = " ∧ ".join(f"{p.predicate}({p.source}, {p.target})" for p in cand.premises)
        conc_str = f"{cand.conclusion.predicate}({cand.conclusion.source}, {cand.conclusion.target})"
        total = cand.support_count + cand.counterexample_count
        precision = cand.support_count / total if total > 0 else 0.0

        lines = [
            f"CandidateRule: {cand.candidate_id}",
            f"  Patrón: {cand.pattern_type}",
            f"  Premisas: {prem_str}",
            f"  Conclusión: {conc_str}",
            f"  Soporte empírico: {cand.support_count}",
            f"  Contraejemplos: {cand.counterexample_count}",
            f"  Precisión: {precision:.2f}",
            f"  Confianza: {cand.confidence:.2f}",
            f"  Estado: {cand.status.value}",
            f"  Evidencias observadas: {cand.evidence_ids}",
            f"  Instancias registradas: {len(cand.observations)}"
        ]
        return "\n".join(lines)
