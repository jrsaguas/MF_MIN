"""
evaluation.py - Evaluación y puntuación de planes (Capa 2).
Evalúa candidatos según costo operativo, alineación semántica con el objetivo,
factibilidad axiomática y antecedentes empíricos en memoria episódica.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import numpy as np

from mf_min_definitivo import State, Kernel
from motor_c import Plan, Goal
from memory import EpisodicMemory
from embeddings import VectorEmbeddingEngine, cosine_similarity

@dataclass
class PlanScore:
    """Métricas y utilidad de un plan evaluado."""
    utility: float
    goal_alignment: float
    cost_penalty: float
    episodic_prior: float
    is_valid: bool
    simulated_final_state: Optional[State] = None

class PlanEvaluator:
    """
    Evaluador formal de planes cognitivos antes de su confirmación en el Kernel.
    """
    def __init__(
        self,
        embedder: Optional[VectorEmbeddingEngine] = None,
        w_goal: float = 1.0,
        w_prior: float = 0.8,
        w_cost: float = 0.3
    ):
        self.embedder = embedder or VectorEmbeddingEngine()
        self.w_goal = w_goal
        self.w_prior = w_prior
        self.w_cost = w_cost

    def evaluate_plan(
        self,
        plan: Plan,
        initial_state: State,
        goal: Goal,
        episodic_memory: Optional[EpisodicMemory] = None,
        action_priors: Optional[Dict[str, float]] = None
    ) -> PlanScore:
        """
        Calcula la puntuación multidimensional y utilidad de un plan.
        """
        # 1. Simulación formal en Kernel candidato para verificar invariantes y axiomas
        try:
            candidate = Kernel(initial_state)
            candidate.transition_batch(plan.all_transitions())
            simulated_state = candidate.state
            is_valid = True
        except Exception:
            return PlanScore(
                utility=-999.0,
                goal_alignment=0.0,
                cost_penalty=plan.total_cost,
                episodic_prior=0.0,
                is_valid=False,
                simulated_final_state=None
            )

        # 2. Alineación semántica con el objetivo
        goal_vec = self.embedder.embed_goal(list(goal.conditions))
        state_vec = self.embedder.embed_state(simulated_state)
        goal_alignment = max(0.0, cosine_similarity(state_vec, goal_vec))

        # Si el objetivo se cumple formalmente, bonificación máxima
        if goal.is_satisfied(simulated_state):
            goal_alignment = max(1.0, goal_alignment + 0.5)

        # 3. Antecedente en Memoria Episódica y Priors de Acción
        episodic_scores = []
        action_priors = action_priors or {}
        for action_name in plan.action_names:
            prior = 0.5
            if episodic_memory is not None:
                prior = episodic_memory.get_action_success_rate(action_name)
            
            # Ponderar con tabla de valores aprendidos
            learned_q = action_priors.get(action_name, 0.0)
            adjusted_prior = 0.6 * prior + 0.4 * (1.0 / (1.0 + np.exp(-learned_q)))
            episodic_scores.append(float(adjusted_prior))

        episodic_prior = float(np.mean(episodic_scores)) if episodic_scores else 0.5

        # 4. Penalización de costo operativo
        cost_penalty = float(plan.total_cost)

        # 5. Función de Utilidad Compuesta
        utility = (
            (self.w_goal * goal_alignment) +
            (self.w_prior * episodic_prior) -
            (self.w_cost * (cost_penalty / max(1.0, len(plan.steps))))
        )

        return PlanScore(
            utility=float(utility),
            goal_alignment=float(goal_alignment),
            cost_penalty=float(cost_penalty),
            episodic_prior=float(episodic_prior),
            is_valid=is_valid,
            simulated_final_state=simulated_state
        )

    def rank_plans(
        self,
        plans: List[Plan],
        initial_state: State,
        goal: Goal,
        episodic_memory: Optional[EpisodicMemory] = None,
        action_priors: Optional[Dict[str, float]] = None
    ) -> List[Tuple[Plan, PlanScore]]:
        """Ordena una lista de planes candidatos por su utilidad proyectada."""
        evaluated = []
        for p in plans:
            score = self.evaluate_plan(p, initial_state, goal, episodic_memory, action_priors)
            evaluated.append((p, score))

        evaluated.sort(key=lambda item: item[1].utility, reverse=True)
        return evaluated
