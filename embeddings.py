"""
embeddings.py - Representación vectorial de conceptos, estados, acciones y objetivos.
Proporciona vectores densos y funciones de distancia/similitud semántica para la Capa 2.
"""
from __future__ import annotations
import math
import hashlib
from typing import List, Dict, Any, Tuple, Optional, Union
import numpy as np

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calcula la similitud coseno entre dos vectores."""
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

def normalize_vector(v: np.ndarray) -> np.ndarray:
    """Normaliza un vector a norma euclídea unitaria."""
    norm = np.linalg.norm(v)
    if norm == 0.0:
        return v
    return v / norm

class VectorEmbeddingEngine:
    """
    Motor determinista de embeddings semánticos.
    Proyecta cadenas, relaciones, estados y metas en un espacio euclídeo R^dim.
    Soporta afinidades semánticas preconfiguradas y hashing denso de n-gramas.
    """
    def __init__(self, dim: int = 16, seed: int = 42):
        self.dim = dim
        self.rng = np.random.default_rng(seed)
        self._concept_cache: Dict[str, np.ndarray] = {}
        self._initialize_base_vocabulary()

    def _initialize_base_vocabulary(self):
        """Inicializa vectores ortogonales/semánticos para conceptos clave del dominio."""
        base_concepts = [
            # Acciones
            "abrir_puerta", "destrabar_puerta", "cerrar_puerta", "bloquear_puerta",
            "entrar", "salir", "mover", "inspeccionar", "esperar",
            # Entidades y Estados
            "puerta", "persona", "agente", "habitacion", "llave",
            "abierta", "cerrada", "adentro", "afuera", "bloqueada",
            # Relaciones
            "estado", "posicion", "tiene", "conectado_a", "bloquea",
            # Metas
            "persona_adentro", "puerta_abierta", "persona_afuera", "puerta_cerrada"
        ]
        
        # Generación de vectores base normalizados
        for concept in base_concepts:
            # Hash determinista para generar semilla por concepto
            h = int(hashlib.sha256(concept.encode('utf-8')).hexdigest()[:8], 16)
            concept_rng = np.random.default_rng(h)
            vec = concept_rng.normal(0.0, 1.0, size=(self.dim,))
            self._concept_cache[concept] = normalize_vector(vec)

        # Inyectar correlaciones semánticas inductivas (e.g. abrir_puerta afín a puerta y abierta)
        if "abrir_puerta" in self._concept_cache and "puerta" in self._concept_cache:
            v = 0.6 * self._concept_cache["abrir_puerta"] + 0.4 * self._concept_cache["puerta"]
            self._concept_cache["abrir_puerta"] = normalize_vector(v)

        if "entrar" in self._concept_cache and "persona" in self._concept_cache and "adentro" in self._concept_cache:
            v = 0.5 * self._concept_cache["entrar"] + 0.3 * self._concept_cache["persona"] + 0.2 * self._concept_cache["adentro"]
            self._concept_cache["entrar"] = normalize_vector(v)

        if "persona_adentro" in self._concept_cache and "persona" in self._concept_cache and "adentro" in self._concept_cache:
            v = 0.5 * self._concept_cache["persona"] + 0.5 * self._concept_cache["adentro"]
            self._concept_cache["persona_adentro"] = normalize_vector(v)

    def embed_text(self, text: str) -> np.ndarray:
        """Genera un vector para un texto arbitrario combinando palabras o n-gramas."""
        tokens = text.lower().replace("-", " ").replace("_", " ").split()
        if not tokens:
            return np.zeros((self.dim,), dtype=np.float32)

        accum = np.zeros((self.dim,), dtype=np.float32)
        for token in tokens:
            if token in self._concept_cache:
                accum += self._concept_cache[token]
            else:
                # Proyección determinista por hash
                h = int(hashlib.md5(token.encode('utf-8')).hexdigest()[:8], 16)
                token_rng = np.random.default_rng(h)
                vec = token_rng.normal(0.0, 1.0, size=(self.dim,))
                accum += normalize_vector(vec)

        return normalize_vector(accum)

    def embed_relation(self, source: str, predicate: str, target: str, polarity: bool = True) -> np.ndarray:
        """Genera embedding para una relación dirigida con polaridad."""
        v_src = self.embed_text(source)
        v_pred = self.embed_text(predicate)
        v_tgt = self.embed_text(target)
        
        # Composición no conmutativa: Predicado como operador modulador
        combined = v_pred + 0.7 * v_src + 0.7 * v_tgt
        if not polarity:
            combined = -combined
        return normalize_vector(combined)

    def embed_state(self, state: Any) -> np.ndarray:
        """
        Genera un embedding denso global a partir del estado MF_MIN (O, M).
        """
        accum = np.zeros((self.dim,), dtype=np.float32)
        count = 0

        # Objetos
        for obj in state.objects.values():
            accum += self.embed_text(f"{obj.id} {obj.type}")
            count += 1

        # Relaciones
        for rel in state.relations.values():
            accum += self.embed_relation(rel.source, rel.predicate, rel.target, rel.polarity)
            count += 1

        if count == 0:
            return np.zeros((self.dim,), dtype=np.float32)
        return normalize_vector(accum)

    def embed_goal(self, conditions: List[Tuple[str, str, str, bool]]) -> np.ndarray:
        """Genera embedding para un conjunto de condiciones objetivo."""
        if not conditions:
            return np.zeros((self.dim,), dtype=np.float32)
        accum = np.zeros((self.dim,), dtype=np.float32)
        for src, pred, tgt, pol in conditions:
            accum += self.embed_relation(src, pred, tgt, pol)
        return normalize_vector(accum)

    def embed_action(self, name: str, preconditions: Any = None, effects: Any = None) -> np.ndarray:
        """Genera embedding para una acción considerando su nombre y transformaciones."""
        v_name = self.embed_text(name)
        return v_name
