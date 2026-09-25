"""
================================================================================
MF_MIN FACADE — Capa ergonómica de conveniencia
================================================================================
Fachada sobre Kernel + EngineD. No duplica lógica formal ni de inferencia.
Dependencias:
    mf_min_facade -> mf_min_definitivo
    mf_min_facade -> engine_d
"""
from __future__ import annotations
import os
from typing import Any, Dict, List, Optional, Tuple, Mapping

from mf_min_definitivo import Kernel, State, Transition, save_state, load_state
from engine_d import EngineD, Rule, save_rules, load_rules

class MFMin:
    """
    Fachada ergonómica sobre Kernel + EngineD. No duplica ninguna lógica:
    cada método arma el Transition/payload correspondiente y delega. Existe
    porque usar Kernel directamente exige escribir a mano diccionarios de
    payload para cada operación, lo cual es correcto pero incómodo para uso
    cotidiano.

    Mantiene además un registro opcional de reglas (self._rules), para que
    save()/load() puedan persistir el conjunto ⟨hechos, axiomas, reglas⟩
    completo, no solo el State — sin esto, guardar un MFMin conservaba lo
    que ya se había derivado, pero no las reglas con las que se derivó, y
    había que redefinirlas en código cada vez.

    Todos los métodos que mutan devuelven self, para poder encadenar:
        mf = MFMin().add_object("a", "N").add_object("b", "N") \\
                     .add_relation("r1", "a", "step", "b")
    """

    def __init__(self, state: Optional[State] = None, rules: Optional[List[Rule]] = None):
        self._kernel = Kernel(state)
        self._engine = EngineD(self._kernel)
        self._rules: Dict[str, Rule] = {r.id: r for r in (rules or [])}

    @property
    def state(self) -> State:
        return self._kernel.state

    @property
    def kernel(self) -> Kernel:
        return self._kernel

    @property
    def engine(self) -> EngineD:
        return self._engine

    @property
    def rules(self) -> List[Rule]:
        return list(self._rules.values())

    def add_rule(self, rule: Rule) -> "MFMin":
        self._rules[rule.id] = rule
        return self

    def add_object(self, id: str, type: str, value: Any = None, **properties: Any) -> "MFMin":
        self._kernel.transition(Transition("add_object", {"id": id, "type": type, "value": value, "properties": properties}))
        return self

    def add_relation(self, id: str, source: str, predicate: str, target: str,
                      polarity: bool = True, rule_id: Optional[str] = None,
                      premises: Tuple[str, ...] = (), origin: str = "asserted") -> "MFMin":
        self._kernel.transition(Transition("add_relation", {
            "id": id, "source": source, "predicate": predicate, "target": target,
            "polarity": polarity, "origin": origin, "rule_id": rule_id, "premises": premises,
        }))
        return self

    def add_axiom(self, id: str, name: str, body: Tuple[Tuple[str, str, str, bool], ...] = (),
                  min_val: Optional[float] = None, max_val: Optional[float] = None,
                  numeric_type: Optional[str] = None) -> "MFMin":
        """
        `body` acepta tuplas cortas (predicate, source, target[, polarity])
        además del formato dict completo, para que escribir axiomas a mano
        sea menos verboso.
        """
        clause_dicts = []
        for c in body:
            if isinstance(c, Mapping):
                clause_dicts.append(dict(c))
            else:
                predicate, source, target = c[0], c[1], c[2]
                polarity = c[3] if len(c) > 3 else True
                clause_dicts.append({"predicate": predicate, "source": source, "target": target, "polarity": polarity})
        self._kernel.transition(Transition("add_axiom", {
            "id": id, "name": name, "body": clause_dicts,
            "min_numeric_val": min_val, "max_numeric_val": max_val, "numeric_target_type": numeric_type,
        }))
        return self

    def remove_object(self, id: str) -> "MFMin":
        self._kernel.transition(Transition("remove_object", {"id": id}))
        return self

    def remove_relation(self, id: str) -> "MFMin":
        self._kernel.transition(Transition("remove_relation", {"id": id}))
        return self

    def remove_axiom(self, id: str) -> "MFMin":
        self._kernel.transition(Transition("remove_axiom", {"id": id}))
        return self

    def propose_from_text(self, text: str, predicate: str = "implica", commit: bool = False) -> List[Transition]:
        """
        Propone hechos (origin='proposed') a partir de texto vía
        extract_facts_from_text(). Por defecto NO los aplica (commit=False):
        el llamador revisa la lista y decide. Si commit=True, los aplica de
        una vez como una única unidad atómica vía transition_batch() —
        todos entran o ninguno.
        """
        proposals = extract_facts_from_text(text, self._kernel, predicate=predicate)
        if commit and proposals:
            self._kernel.transition_batch(proposals)
        return proposals

    def promote(self, relation_id: str) -> "MFMin":
        """Transforma una relación origin='proposed' en 'asserted' (ver Kernel: promote_relation)."""
        self._kernel.transition(Transition("promote_relation", {"id": relation_id}))
        return self

    def transition_batch(self, transitions: List[Transition]) -> "MFMin":
        """Aplica una lista de Transition como una única unidad atómica (ver Kernel.transition_batch)."""
        self._kernel.transition_batch(transitions)
        return self

    def query(self, source: str, predicate: str, target: str) -> str:
        return self._engine.query_evidence(source, predicate, target)

    def derive(self, rules: Optional[List[Rule]] = None, max_rounds: int = 10_000, max_total_derived: Optional[int] = None) -> int:
        """Si no se pasan `rules` explícitamente, usa el registro interno (self.rules)."""
        active_rules = rules if rules is not None else self.rules
        return self._engine.saturate(active_rules, max_rounds=max_rounds, max_total_derived=max_total_derived)

    def verify(self, relation_id: str, rules_by_id: Optional[Mapping[str, Rule]] = None) -> bool:
        rel = self._kernel.state.relations.get(relation_id)
        if rel is None:
            return False
        return self._engine.verify_derivation(rel, rules_by_id if rules_by_id is not None else self._rules)

    def facts(self) -> Set[Tuple[str, str, str, bool]]:
        return project_pi(self._kernel.state)

    def save(self, path: str, rules_path: Optional[str] = None) -> None:
        """
        Guarda el estado. Si se da `rules_path` (o si self.rules no está
        vacío y se omite `rules_path`, usando '<path>.rules.json' por
        defecto), también guarda el registro de reglas.
        """
        save_state(self._kernel.state, path)
        if self.rules:
            target = rules_path or (path + ".rules.json")
            save_rules(self.rules, target)

    @classmethod
    def load(cls, path: str, rules_path: Optional[str] = None) -> "MFMin":
        """
        Carga el estado. Si `rules_path` no se da, intenta '<path>.rules.json'
        automáticamente; si no existe, se carga sin reglas (comportamiento
        idéntico al de antes de esta extensión).
        """
        state = load_state(path)
        candidate_rules_path = rules_path or (path + ".rules.json")
        rules: List[Rule] = []
        if os.path.exists(candidate_rules_path):
            rules = load_rules(candidate_rules_path)
        return cls(state=state, rules=rules)

    def summary(self) -> str:
        s = self._kernel.state
        return f"MFMin(objects={len(s.objects)}, relations={len(s.relations)}, axioms={len(s.axioms)}, rules={len(self._rules)})"

    def __repr__(self) -> str:
        return self.summary()


