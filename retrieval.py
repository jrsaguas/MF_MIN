"""
retrieval.py - Recuperador Jerárquico Unificado (Memoria Semántica, Declarativa y Episódica).
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Any
import numpy as np
from memory import Memory, MemoryItem, Episode
from embeddings import VectorEmbeddingEngine, cosine_similarity

class Retriever:
    """
    Motor de recuperación unificado (Simbólico + Semántico vectorial).
    """
    def __init__(
        self,
        memory: Memory,
        knowledge_store: Optional[Any] = None,
        embedding_engine: Optional[VectorEmbeddingEngine] = None
    ):
        self.memory = memory
        self.knowledge_store = knowledge_store
        self.embedder = embedding_engine or VectorEmbeddingEngine()

    def retrieve_declarative(self, query: str, top_k: int = 5) -> List[Tuple[float, Any]]:
        q_vec = self.embedder.embed_text(query)
        scored: List[Tuple[float, Any]] = []

        for item in self.memory.all_items():
            if item.embedding is not None:
                sim = cosine_similarity(q_vec, item.embedding)
            else:
                item_vec = self.embedder.embed_text(item.content)
                sim = cosine_similarity(q_vec, item_vec)
            for tag in item.tags:
                if tag.lower() in query.lower():
                    sim += 0.2
            scored.append((float(sim), item))

        if self.knowledge_store is not None:
            for claim in self.knowledge_store.claims.values():
                c_text = f"{claim.subject} {claim.predicate} {claim.object}"
                c_vec = self.embedder.embed_text(c_text)
                sim = cosine_similarity(q_vec, c_vec) * claim.composite_confidence
                scored.append((float(sim), MemoryItem(
                    id=f"claim_{claim.subject}_{claim.predicate}",
                    content=c_text,
                    tags=[claim.subject, claim.predicate],
                    importance=claim.composite_confidence
                )))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def retrieve_episodes(
        self,
        query_vector: np.ndarray,
        top_k: int = 3,
        threshold: float = 0.0
    ) -> List[Tuple[float, Episode]]:
        episodes = self.memory.episodic.get_all_episodes()
        scored: List[Tuple[float, Episode]] = []

        for ep in episodes:
            target_vec = ep.goal_embedding if ep.goal_embedding is not None else ep.episode_embedding
            if target_vec is None:
                target_vec = self.embedder.embed_text(ep.goal_desc)

            sim = cosine_similarity(query_vector, target_vec)
            if sim >= threshold:
                scored.append((float(sim), ep))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]
