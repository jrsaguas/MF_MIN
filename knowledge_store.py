"""
knowledge_store.py - Almacén de Conocimiento Indexado con Deduplicación.
Garantiza consultas en O(1) / O(k) mediante índices invertidos (SPO, Sujeto, Objeto, Predicado),
evitando escaneos lineales O(N) de millones de hechos.
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
from knowledge import Entity, Claim, Sense, EpistemicStatus

class KnowledgeStore:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.senses: Dict[str, Sense] = {}
        self.claims: Dict[Tuple[str, str, str, bool], Claim] = {}

        # Índices invertidos para recuperación eficiente en memoria
        self._by_subject: Dict[str, Set[Tuple[str, str, str, bool]]] = defaultdict(set)
        self._by_object: Dict[str, Set[Tuple[str, str, str, bool]]] = defaultdict(set)
        self._by_predicate: Dict[str, Set[Tuple[str, str, str, bool]]] = defaultdict(set)

    def add_sense(self, sense: Sense) -> None:
        self.senses[sense.id] = sense

    def add_entity(self, entity: Entity) -> Entity:
        """Almacena o fusiona una entidad canónica sin duplicar identidades."""
        if entity.id in self.entities:
            existing = self.entities[entity.id]
            for alias in entity.aliases:
                if alias not in existing.aliases:
                    existing.aliases.append(alias)
            existing.properties.update(entity.properties)
            return existing
        self.entities[entity.id] = entity
        return entity

    def add_claim(self, claim: Claim) -> Claim:
        """
        Registra una afirmación. Si el hecho formal (S, P, O, pol) ya existe,
        fusiona la evidencia y actualiza su respaldo sin crear duplicados innecesarios.
        """
        key = claim.spo_key
        if key in self.claims:
            existing = self.claims[key]
            # Fusionar evidencias
            for ev in claim.evidences:
                if ev.id not in [e.id for e in existing.evidences]:
                    existing.evidences.append(ev)
            # Actualizar confianza de evidencia de forma incremental
            if existing.evidences:
                avg_rel = sum(e.reliability for e in existing.evidences) / len(existing.evidences)
                existing.confidence_evidence = max(existing.confidence_evidence, avg_rel)
            return existing

        # Nuevo claim
        self.claims[key] = claim
        self._by_subject[claim.subject].add(key)
        self._by_object[claim.object].add(key)
        self._by_predicate[claim.predicate].add(key)
        return claim

    def query_claims(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_: Optional[str] = None,
        polarity: Optional[bool] = None
    ) -> List[Claim]:
        """
        Consulta rápida mediante intersección de índices en O(1) inicial.
        """
        candidate_keys: Optional[Set[Tuple[str, str, str, bool]]] = None

        if subject is not None:
            candidate_keys = set(self._by_subject.get(subject, set()))
        if predicate is not None:
            p_keys = self._by_predicate.get(predicate, set())
            candidate_keys = p_keys if candidate_keys is None else (candidate_keys & p_keys)
        if object_ is not None:
            o_keys = self._by_object.get(object_, set())
            candidate_keys = o_keys if candidate_keys is None else (candidate_keys & o_keys)

        if candidate_keys is None:
            keys_to_filter = list(self.claims.keys())
        else:
            keys_to_filter = list(candidate_keys)

        results = []
        for k in keys_to_filter:
            c = self.claims[k]
            if polarity is not None and c.polarity != polarity:
                continue
            results.append(c)

        return results

    def find_conflicts(self) -> List[Tuple[Claim, Claim]]:
        """
        Encuentra afirmaciones mutuamente contradictorias (mismo S, P, O pero distinta polaridad).
        """
        conflicts: List[Tuple[Claim, Claim]] = []
        seen = set()
        for (s, p, o, pol), c_pos in self.claims.items():
            opp_key = (s, p, o, not pol)
            if opp_key in self.claims:
                pair = tuple(sorted([id(c_pos), id(self.claims[opp_key])]))
                if pair not in seen:
                    seen.add(pair)
                    conflicts.append((c_pos, self.claims[opp_key]))
        return conflicts
