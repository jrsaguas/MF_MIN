"""
motor_c.py - Motor C: Planificación de acciones y ejecución atómica sobre el Kernel MF_MIN.
Implementa:
 - Action: Operador con precondiciones, efectos (Transiciones de delta) y costo.
 - Goal: Especificación de estado objetivo.
 - PlanStep y Plan: Trayectoria de acciones estructurada.
 - MotorC: Algoritmo de planificación sobre el espacio de estados y ejecución vía transition_batch().
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Set, Any
from collections import deque
from mf_min_definitivo import Kernel, Transition, State

@dataclass(frozen=True)
class Action:
    """Acción ejecutable en el mundo formal."""
    name: str
    preconditions: Tuple[Tuple[str, str, str, bool], ...] = ()
    effects: Tuple[Transition, ...] = ()
    cost: float = 1.0

    def is_applicable(self, state: State) -> bool:
        """Verifica si todas las precondiciones se satisfacen en el estado actual."""
        rel_set = {(r.source, r.predicate, r.target, r.polarity) for r in state.relations.values()}
        for pre in self.preconditions:
            if pre not in rel_set:
                return False
        return True

    def simulate(self, state: State) -> Optional[State]:
        """Simula la aplicación de los efectos en un Kernel candidato sin alterar el original."""
        try:
            candidate = Kernel(state)
            for eff in self.effects:
                candidate.transition(eff)
            return candidate.state
        except Exception:
            return None

@dataclass(frozen=True)
class Goal:
    """Objetivo cognitivo expresado como conjunto de relaciones deseadas."""
    conditions: Tuple[Tuple[str, str, str, bool], ...]

    def is_satisfied(self, state: State) -> bool:
        """Comprueba si todas las condiciones del objetivo están presentes en M."""
        rel_set = {(r.source, r.predicate, r.target, r.polarity) for r in state.relations.values()}
        for cond in self.conditions:
            if cond not in rel_set:
                return False
        return True

@dataclass
class PlanStep:
    step_number: int
    action: Action

@dataclass
class Plan:
    steps: List[PlanStep] = field(default_factory=list)
    total_cost: float = 0.0

    @property
    def action_names(self) -> List[str]:
        return [s.action.name for s in self.steps]

    def all_transitions(self) -> List[Transition]:
        """Extrae todas las transiciones atómicas secuenciales del plan."""
        trans = []
        for step in self.steps:
            trans.extend(step.action.effects)
        return trans

class MotorC:
    """
    Planificador y Ejecutor Motor C.
    Explora el espacio de estados mediante búsqueda y comete planes vía Kernel.transition_batch().
    """
    def __init__(self, action_priors: Optional[Dict[str, float]] = None):
        # Priors de aprendizaje (Capa 2) para ordenar acciones aplicables
        self.action_priors = action_priors or {}

    def _state_key(self, state: State) -> Tuple[Tuple[str, str, str, bool], ...]:
        """Firma canónica inmutable del estado de relaciones."""
        rels = tuple(sorted((r.source, r.predicate, r.target, r.polarity) for r in state.relations.values()))
        return rels

    def plan(
        self,
        state: State,
        goal: Goal,
        actions: List[Action],
        max_depth: int = 10
    ) -> Optional[Plan]:
        """
        Búsqueda de trayectoria óptima de acciones (BFS guiado por priors/costo).
        """
        if goal.is_satisfied(state):
            return Plan([], 0.0)

        # Cola de BFS: (current_state, steps, cost)
        queue = deque([(state, [], 0.0)])
        visited: Set[Tuple[Tuple[str, str, str, bool], ...]] = {self._state_key(state)}

        while queue:
            curr_state, steps, curr_cost = queue.popleft()

            if len(steps) >= max_depth:
                continue

            # Ordenar acciones aplicables: favorecer acciones con mayor prior de aprendizaje
            sorted_actions = sorted(
                actions,
                key=lambda a: self.action_priors.get(a.name, 0.0),
                reverse=True
            )

            for act in sorted_actions:
                if not act.is_applicable(curr_state):
                    continue

                next_state = act.simulate(curr_state)
                if next_state is None:
                    continue

                next_key = self._state_key(next_state)
                if next_key in visited:
                    continue

                new_step = PlanStep(step_number=len(steps) + 1, action=act)
                new_steps = steps + [new_step]
                new_cost = curr_cost + act.cost

                if goal.is_satisfied(next_state):
                    return Plan(steps=new_steps, total_cost=new_cost)

                visited.add(next_key)
                queue.append((next_state, new_steps, new_cost))

        return None

    def execute(self, kernel: Kernel, plan: Plan) -> bool:
        """
        Ejecución atómica del plan en el Kernel MF_MIN mediante transition_batch().
        Garantiza que si algún efecto falla o viola axiomas, todo el plan se revierte.
        """
        if not plan or not plan.steps:
            return True

        transitions = plan.all_transitions()
        try:
            kernel.transition_batch(transitions)
            return True
        except Exception as e:
            return False
