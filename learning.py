"""
learning.py - Mecanismo de Aprendizaje y Adaptación (Capa 2).
Actualiza priors de acción y consolida trayectorias exitosas o fallidas en memoria episódica.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import time
import numpy as np

from motor_c import Plan, Goal
from memory import EpisodicMemory, Episode
from embeddings import VectorEmbeddingEngine

class Learner:
    """
    Motor de Aprendizaje por Refuerzo y Consolidación Episódica.
    Ajusta pesos de preferencia de acciones y almacena trazas para inferencia analógica futura.
    """
    def __init__(
        self,
        learning_rate: float = 0.25,
        discount_factor: float = 0.9,
        embedder: Optional[VectorEmbeddingEngine] = None
    ):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.action_values: Dict[str, float] = {}
        self.embedder = embedder or VectorEmbeddingEngine()

    def get_action_prior(self, action_name: str) -> float:
        """Devuelve el valor aprendido de preferencia para una acción."""
        return self.action_values.get(action_name, 0.0)

    def compute_reward(self, goal_satisfied: bool, total_cost: float, execution_ok: bool) -> float:
        """
        Función de recompensa ambiental:
        Premia el cumplimiento del objetivo penalizando el costo incurrido.
        """
        if execution_ok and goal_satisfied:
            return 10.0 - (0.5 * total_cost)
        elif execution_ok and not goal_satisfied:
            return -2.0 - (0.5 * total_cost)
        else:
            # Fallo catastrófico de ejecución (violación de invariante o KernelError)
            return -10.0 - total_cost

    def update_from_execution(
        self,
        plan: Plan,
        goal: Goal,
        goal_satisfied: bool,
        execution_ok: bool,
        episodic_memory: EpisodicMemory,
        episode_id: Optional[str] = None
    ) -> Tuple[float, Episode]:
        """
        Ciclo de retroalimentación de aprendizaje:
        1. Calcula la recompensa escalar R.
        2. Actualiza Q(a) para cada acción del plan: Q(a) <- Q(a) + lr * (R - Q(a)).
        3. Consolida el episodio con embedding en memoria episódica.
        """
        reward = self.compute_reward(goal_satisfied, plan.total_cost, execution_ok)

        # Actualización de pesos Q(a) por asignación de crédito
        for step in plan.steps:
            act_name = step.action.name
            current_q = self.action_values.get(act_name, 0.0)
            new_q = current_q + self.lr * (reward - current_q)
            self.action_values[act_name] = float(new_q)

        # Generar embeddings para el episodio
        goal_conditions = list(goal.conditions)
        goal_vec = self.embedder.embed_goal(goal_conditions)
        plan_str = " -> ".join(plan.action_names)
        episode_vec = self.embedder.embed_text(f"meta:{str(goal_conditions)} plan:{plan_str}")

        eid = episode_id or f"EP_{int(time.time() * 1000)}"
        episode = episodic_memory.record_episode(
            episode_id=eid,
            goal_desc=f"Goal: {goal_conditions}",
            initial_state_summary="Initial state snapshot",
            plan_actions=plan.action_names,
            success=(goal_satisfied and execution_ok),
            cost=plan.total_cost,
            reward=reward,
            goal_embedding=goal_vec,
            episode_embedding=episode_vec,
            metadata={"action_values_snapshot": dict(self.action_values)}
        )

        return reward, episode
