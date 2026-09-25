"""
memory.py - Subsistema de Memoria Cognitiva.
Combina Memoria de Trabajo/Declarativa (Capa 1) con Memoria Episódica Semántica (Capa 2).
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

@dataclass
class MemoryItem:
    """Elemento declarativo o perceptual almacenado en memoria de trabajo."""
    id: str
    content: str
    tags: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    embedding: Optional[np.ndarray] = None
    importance: float = 1.0

@dataclass
class Episode:
    """
    Episodio registrado en Memoria Episódica (Capa 2).
    Captura una trayectoria completa: Objetivo -> Plan -> Ejecución -> Recompensa.
    """
    id: str
    goal_desc: str
    initial_state_summary: str
    plan_actions: List[str]
    success: bool
    cost: float
    reward: float
    goal_embedding: Optional[np.ndarray] = None
    episode_embedding: Optional[np.ndarray] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class EpisodicMemory:
    """
    Almacén indexado de episodios pasados.
    Permite recuperar experiencias análogas y calcular antecedentes de éxito.
    """
    def __init__(self):
        self.episodes: Dict[str, Episode] = {}
        self._action_index: Dict[str, List[str]] = {} # action_name -> list of episode_ids

    def record_episode(
        self,
        episode_id: str,
        goal_desc: str,
        initial_state_summary: str,
        plan_actions: List[str],
        success: bool,
        cost: float,
        reward: float,
        goal_embedding: Optional[np.ndarray] = None,
        episode_embedding: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Episode:
        ep = Episode(
            id=episode_id,
            goal_desc=goal_desc,
            initial_state_summary=initial_state_summary,
            plan_actions=list(plan_actions),
            success=success,
            cost=cost,
            reward=reward,
            goal_embedding=goal_embedding,
            episode_embedding=episode_embedding,
            metadata=metadata or {}
        )
        self.episodes[ep.id] = ep

        for act in plan_actions:
            if act not in self._action_index:
                self._action_index[act] = []
            self._action_index[act].append(ep.id)

        return ep

    def get_all_episodes(self) -> List[Episode]:
        return list(self.episodes.values())

    def get_episodes_by_action(self, action_name: str) -> List[Episode]:
        ids = self._action_index.get(action_name, [])
        return [self.episodes[eid] for eid in ids if eid in self.episodes]

    def get_action_success_rate(self, action_name: str) -> float:
        """Calcula la tasa histórica empírica de éxito de una acción."""
        episodes = self.get_episodes_by_action(action_name)
        if not episodes:
            return 0.5  # Prior neutral
        successes = sum(1 for ep in episodes if ep.success)
        return float(successes / len(episodes))

class Memory:
    """
    Memoria unificada del Agente.
    Contiene la memoria de trabajo/declarativa y la memoria episódica.
    """
    def __init__(self):
        self.items: Dict[str, MemoryItem] = {}
        self.episodic: EpisodicMemory = EpisodicMemory()

    def store(self, item_id: str, content: str, tags: Optional[List[str]] = None, embedding: Optional[np.ndarray] = None, importance: float = 1.0) -> MemoryItem:
        item = MemoryItem(id=item_id, content=content, tags=tags or [], embedding=embedding, importance=importance)
        self.items[item.id] = item
        return item

    def get(self, item_id: str) -> Optional[MemoryItem]:
        return self.items.get(item_id)

    def all_items(self) -> List[MemoryItem]:
        return list(self.items.values())
