"""
retrieval_indexed.py - Recuperación Jerárquica Indexada (Simbólica + Vectorial).
Evita el cuello de botella O(N) al filtrar primero por índices de grafo/SPO
y luego aplicar ranking vectorial sólo sobre el subconjunto de candidatos.
"""
from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np
from knowledge_store import KnowledgeStore
from knowledge import Claim
from embeddings import VectorEmbeddingEngine, cosine_similarity

class IndexedRetriever:
    def __init__(self, store: KnowledgeStore, embedder: Optional[VectorEmbeddingEngine] = None):
        self.store = store
        self.embedder = embedder or VectorEmbeddingEngine()

    def query_hierarchical(
        self,
        query_text: str,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_: Optional[str] = None,
        top_k: int = 5
    ) -> List[Tuple[float, Claim]]:
        """
        Fase 1: Filtrado exacto en O(1) usando índices invertidos del KnowledgeStore.
        Fase 2: Ranking por similitud coseno sólo sobre los candidatos resultantes.
        """
        candidates = self.store.query_claims(subject=subject, predicate=predicate, object_=object_)
        if not candidates:
            return []

        q_vec = self.embedder.embed_text(query_text)
        scored: List[Tuple[float, Claim]] = []

        for c in candidates:
            # Embeber la afirmación
            claim_text = f"{c.subject} {c.predicate} {c.object}"
            c_vec = self.embedder.embed_text(claim_text)
            sim = cosine_similarity(q_vec, c_vec)
            # Ponderar por la confianza compuesta del claim
            final_score = sim * c.composite_confidence
            scored.append((float(final_score), c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def retrieve_declarative(self, query_text: str, top_k: int = 5) -> List[Tuple[float, Any]]:
        results = self.query_hierarchical(query_text=query_text, top_k=top_k)
        # Adaptar a tupla (score, item)
        from memory import MemoryItem
        adapted = []
        for score, claim in results:
            adapted.append((score, MemoryItem(
                id=f"cl_{claim.subject}_{claim.predicate}",
                content=f"{claim.subject} {claim.predicate} {claim.object}",
                tags=[claim.subject, claim.predicate],
                importance=claim.composite_confidence
            )))
        return adapted

    def retrieve_episodes(self, query_vector: Any, top_k: int = 3, threshold: float = 0.0) -> List[Any]:
        return []
