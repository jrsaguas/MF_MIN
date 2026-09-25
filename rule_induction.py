"""
================================================================================
RULE_INDUCTION — Motor de Inducción Estructural y Descubrimiento de Reglas
================================================================================

Implementa el ciclo de aprendizaje inductivo formal sobre estados de MF_MIN:
    Observaciones en M -> Detección de Patrones -> Hipótesis de Regla ->
    Auditoría Formal en Kernel Efímero -> Calificación Epistémica ->
    Integración Controlada en EngineD.

Garantías:
1. No busca combinaciones arbitrarias: utiliza esquemas de meta-reglas canónicas
   (Transitividad, Simetría, Inversión, Composición).
2. Seguridad y Preservación del Núcleo: Toda regla candidata se audita en un
   Kernel efímero de prueba. Si genera una sola contradicción axiomática o
   semántica, se descarta (REJECTED) con confianza 0.0.
3. Trazabilidad Formal: Los hechos derivados a través de reglas inducidas portan
   el ID de la hipótesis y mantienen intacta la Invariante I2 de MF_MIN.
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


@dataclass
class RuleHypothesis:
    """
    Representa una regla candidata inducida empíricamente junto con su
    evaluación epistémica y auditoría formal.
    """
    id: str
    rule: Rule
    schema_type: str  # "transitivity", "symmetry", "composition", "inversion"
    predicate: str
    target_predicate: str
    body_count: int = 0
    support_count: int = 0
    counterexamples_count: int = 0
    predicted_count: int = 0
    confidence: float = 0.0
    status: str = "PROPOSED"  # "PROPOSED", "VALIDATED", "REJECTED"
    justification: str = ""

    def summary(self) -> str:
        prem_str = " ∧ ".join(f"{p.predicate}({p.source}, {p.target})" for p in self.rule.premises)
        conc_str = f"{self.rule.conclusion.predicate}({self.rule.conclusion.source}, {self.rule.conclusion.target})"
        return (
            f"[{self.status}] {self.id} ({self.schema_type}): {prem_str} => {conc_str} | "
            f"Conf: {self.confidence:.2f} (Body: {self.body_count}, Supp: {self.support_count}, "
            f"Contra: {self.counterexamples_count}, Nuevos: {self.predicted_count})"
        )


class RuleInductionEngine:
    """
    Motor inductivo que inspecciona el grafo relacional de un estado MF_MIN,
    genera hipótesis estructurales mediante esquemas y las valida formalmente.
    """

    def __init__(self, default_min_confidence: float = 0.5):
        self.default_min_confidence = default_min_confidence

    def mine_transitivity_candidates(self, state: State) -> List[RuleHypothesis]:
        """
        Detecta si un predicado P forma cadenas conexas P(X, Y) ∧ P(Y, Z) con X != Y != Z.
        Si existen cadenas de longitud >= 2, propone la regla de transitividad:
            P(?X, ?Y) ∧ P(?Y, ?Z) => P(?X, ?Z)
        """
        # Agrupar pares positivos por predicado
        rels_by_pred: Dict[str, Set[Tuple[str, str]]] = {}
        for r in state.relations.values():
            if r.polarity is True and r.origin != "proposed":
                rels_by_pred.setdefault(r.predicate, set()).add((r.source, r.target))

        candidates: List[RuleHypothesis] = []
        for pred, pairs in rels_by_pred.items():
            # Construir índice de adyacencia
            adj: Dict[str, Set[str]] = {}
            for s, t in pairs:
                adj.setdefault(s, set()).add(t)

            # Buscar caminos de longitud 2
            chains_count = 0
            for x, targets in adj.items():
                for y in targets:
                    if y in adj:
                        for z in adj[y]:
                            if x != y and y != z:
                                chains_count += 1

            if chains_count > 0:
                rule_id = f"ind_trans_{pred}"
                rule = Rule(
                    id=rule_id,
                    name=f"Transitividad inducida para '{pred}'",
                    premises=(
                        Pattern(predicate=pred, source="?X", target="?Y", polarity=True),
                        Pattern(predicate=pred, source="?Y", target="?Z", polarity=True),
                    ),
                    conclusion=Pattern(predicate=pred, source="?X", target="?Z", polarity=True),
                )
                hyp = RuleHypothesis(
                    id=rule_id,
                    rule=rule,
                    schema_type="transitivity",
                    predicate=pred,
                    target_predicate=pred,
                    body_count=chains_count,
                    justification=f"Se detectaron {chains_count} cadenas conexas de longitud 2 para el predicado '{pred}'.",
                )
                candidates.append(hyp)

        return candidates

    def mine_symmetry_candidates(self, state: State) -> List[RuleHypothesis]:
        """
        Detecta si para un predicado P existen pares recíprocos P(X, Y) ∧ P(Y, X).
        Si se observan tales pares y no hay contraejemplos, propone la regla de simetría:
            P(?X, ?Y) => P(?Y, ?X)
        """
        rels_by_pred: Dict[str, Set[Tuple[str, str]]] = {}
        for r in state.relations.values():
            if r.polarity is True and r.origin != "proposed":
                rels_by_pred.setdefault(r.predicate, set()).add((r.source, r.target))

        candidates: List[RuleHypothesis] = []
        for pred, pairs in rels_by_pred.items():
            reciprocal_count = 0
            for s, t in pairs:
                if s != t and (t, s) in pairs:
                    reciprocal_count += 1

            # Si hay al menos un par recíproco y no todos son asimétricos
            if reciprocal_count > 0:
                rule_id = f"ind_symm_{pred}"
                rule = Rule(
                    id=rule_id,
                    name=f"Simetría inducida para '{pred}'",
                    premises=(
                        Pattern(predicate=pred, source="?X", target="?Y", polarity=True),
                    ),
                    conclusion=Pattern(predicate=pred, source="?Y", target="?X", polarity=True),
                )
                hyp = RuleHypothesis(
                    id=rule_id,
                    rule=rule,
                    schema_type="symmetry",
                    predicate=pred,
                    target_predicate=pred,
                    body_count=len(pairs),
                    support_count=reciprocal_count // 2,
                    justification=f"Se detectaron {reciprocal_count // 2} pares simétricos para el predicado '{pred}'.",
                )
                candidates.append(hyp)

        return candidates

    def audit_and_evaluate(self, hypothesis: RuleHypothesis, kernel: Kernel) -> RuleHypothesis:
        """
        Audita una hipótesis ejecutando una simulación seca (dry-run) sobre un Kernel efímero:
        1. Comprueba si produce conclusiones que contradigan hechos con polaridad opuesta.
        2. Comprueba si alguna conclusión viola invariantes axiomáticas (I5) o estructurales de MF_MIN.
        3. Calcula la puntuación de confianza laplaciana y fija el estatus.
        """
        state = kernel.state
        existing_pos = {(r.source, r.predicate, r.target) for r in state.relations.values() if r.polarity is True}
        existing_neg = {(r.source, r.predicate, r.target) for r in state.relations.values() if r.polarity is False}

        # Clon efímero de trabajo
        working_kernel = Kernel(state)
        engine_test = EngineD(working_kernel)

        try:
            candidates = engine_test.infer_step(hypothesis.rule)
        except Exception as e:
            hypothesis.status = "REJECTED"
            hypothesis.confidence = 0.0
            hypothesis.justification = f"Error al generar deducciones de prueba: {e}"
            return hypothesis

        support = 0
        counter = 0
        new_valid = 0

        # Probar cada conclusión candidata
        for c in candidates:
            key = (c.source, c.predicate, c.target)
            
            # Contradicción empírica directa (polaridad opuesta ya conocida)
            if key in existing_neg:
                counter += 1
                continue

            # Hecho ya afirmado positivamente (soporte confirmatorio)
            if key in existing_pos:
                support += 1
                continue

            # Hecho nuevo: auditar si el Kernel lo acepta o si dispara contradicción con axiomas
            try:
                working_kernel.transition(Transition("add_relation", {
                    "id": c.id,
                    "source": c.source,
                    "predicate": c.predicate,
                    "target": c.target,
                    "polarity": c.polarity,
                    "origin": "derived",
                    "rule_id": hypothesis.rule.id,
                    "premises": c.premises,
                }))
                new_valid += 1
            except ContradictionError as ce:
                # Violación axiomática formal estricta (ej. axioma de irreflexividad o veto mutuo)
                counter += 1
            except ValidationError as ve:
                counter += 1

        hypothesis.support_count = support
        hypothesis.counterexamples_count = counter
        hypothesis.predicted_count = new_valid

        # Evaluación epistémica
        if counter > 0:
            # Una sola contradicción formal invalida la hipótesis
            hypothesis.status = "REJECTED"
            hypothesis.confidence = 0.0
            hypothesis.justification += f" [RECHAZADA: {counter} contraejemplos formales detectados]."
            return hypothesis

        # Confianza laplaciana / Bayesian smoothing
        # Si no hay contraejemplos:
        # En caso de soporte empírico explícito:
        total_eval = support + new_valid
        if total_eval == 0:
            hypothesis.confidence = 0.0
            hypothesis.status = "PROPOSED"
        elif support > 0:
            hypothesis.confidence = (support + 1.0) / (total_eval + 2.0)
            hypothesis.status = "VALIDATED" if hypothesis.confidence >= self.default_min_confidence else "PROPOSED"
        else:
            # Todos los candidatos son hechos nuevos consistentes con el formalismo
            # Asignamos confianza estructural inicial (cautela inductiva)
            hypothesis.confidence = min(0.85, (new_valid + 1.0) / (new_valid + 2.0))
            hypothesis.status = "VALIDATED" if hypothesis.confidence >= self.default_min_confidence else "PROPOSED"

        hypothesis.justification += f" [AUDITORÍA FORMAL OK: 0 contraejemplos, {new_valid} deducciones consistentes]."
        return hypothesis

    def induce_rules(self, kernel: Kernel, min_confidence: Optional[float] = None) -> List[RuleHypothesis]:
        """
        Ejecuta el pipeline completo de inducción:
        1. Minería de candidatos según esquemas estructurales.
        2. Auditoría formal contra el Kernel.
        3. Filtrado de hipótesis validadas.
        """
        threshold = min_confidence if min_confidence is not None else self.default_min_confidence
        raw_candidates = []
        raw_candidates.extend(self.mine_transitivity_candidates(kernel.state))
        raw_candidates.extend(self.mine_symmetry_candidates(kernel.state))

        validated_rules: List[RuleHypothesis] = []
        for cand in raw_candidates:
            evaluated = self.audit_and_evaluate(cand, kernel)
            if evaluated.status == "VALIDATED" and evaluated.confidence >= threshold:
                validated_rules.append(evaluated)

        return validated_rules

    def induce_and_saturate(self, kernel: Kernel, engine: EngineD, min_confidence: Optional[float] = None) -> Tuple[List[RuleHypothesis], int]:
        """
        Descubre reglas, las audita y promueve aquellas que superen el umbral de confianza,
        ejecutando a continuación EngineD.saturate() para expandir el conocimiento del Kernel.
        Retorna la lista de reglas promovidas y el número total de nuevos hechos deducidos.
        """
        validated_hypotheses = self.induce_rules(kernel, min_confidence=min_confidence)
        if not validated_hypotheses:
            return [], 0

        rules_to_apply = [h.rule for h in validated_hypotheses]
        new_facts_count = engine.saturate(rules_to_apply)
        return validated_hypotheses, new_facts_count

