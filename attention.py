"""
attention.py - Mecanismos de atención para la arquitectura cognitiva.
Evolución de Softmax escalar (Capa 1) a Scaled Dot-Product Attention (Q, K, V) y Multi-Head (Capa 2).
"""
from __future__ import annotations
import math
from typing import List, Tuple, Any, Dict, Optional, Union
import numpy as np

def softmax(scores: Union[List[float], np.ndarray]) -> np.ndarray:
    """
    Función Softmax numéricamente estable:
    softmax(x_i) = exp(x_i - max(x)) / sum_j exp(x_j - max(x))
    """
    x = np.array(scores, dtype=np.float64)
    if x.size == 0:
        return np.array([], dtype=np.float64)
    e_x = np.exp(x - np.max(x))
    sum_e = np.sum(e_x)
    if sum_e == 0:
        return np.ones_like(x) / x.size
    return e_x / sum_e

class ScaledDotProductAttention:
    """
    Atención por Producto Punto Escalado formal:
    Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V
    """
    def __init__(self, d_k: int):
        self.d_k = d_k
        self.scale = 1.0 / math.sqrt(d_k)

    def forward(
        self,
        query: np.ndarray,
        keys: np.ndarray,
        values: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula la atención entre queries y keys, ponderando values.
        query: shape (d_k,) o (seq_q, d_k)
        keys: shape (seq_k, d_k)
        values: shape (seq_k, d_v)
        Retorna:
          context: vector o matriz agregada de valores atendidos
          weights: distribución de atención softmax
        """
        q = np.atleast_2d(query)
        k = np.atleast_2d(keys)
        v = np.atleast_2d(values)

        # Matriz de productos punto escalados: (seq_q, seq_k)
        scores = np.matmul(q, k.T) * self.scale

        if mask is not None:
            scores = np.where(mask == 0, -1e9, scores)

        # Aplicar softmax a lo largo del eje de las llaves
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)

        # Ponderar valores: (seq_q, d_v)
        context = np.matmul(weights, v)

        if query.ndim == 1:
            return context[0], weights[0]
        return context, weights

class AttentionEngine:
    """
    Motor de atención cognitivo unificado.
    Soporta:
      1. Modo Escalar (Capa 1): Distribución de pesos sobre lista de puntuaciones numéricas.
      2. Modo Q/K/V Vectorial (Capa 2): Ponderación semántica de memorias u objetos basada en Scaled Dot-Product.
    """
    def __init__(self, dim: int = 16):
        self.dim = dim
        self.qkv_attention = ScaledDotProductAttention(d_k=dim)

    def compute_weights(self, scores: List[float]) -> List[float]:
        """Modo Capa 1: Calcula pesos softmax a partir de scores escalares."""
        if not scores:
            return []
        weights = softmax(scores)
        return weights.tolist()

    def attend_qkv(
        self,
        query_vector: np.ndarray,
        keys: List[np.ndarray],
        values: List[Any],
        value_vectors: Optional[List[np.ndarray]] = None
    ) -> Tuple[np.ndarray, List[float], List[Tuple[float, Any]]]:
        """
        Modo Capa 2:
        Aplica Scaled Dot-Product Attention entre query_vector y keys.
        Retorna:
          - context_vector: vector semántico ponderado en R^dim
          - attention_weights: pesos asignados a cada elemento
          - ranked_items: lista de tuplas (peso, value) ordenadas descendentemente
        """
        if not keys or not values:
            return np.zeros((self.dim,), dtype=np.float32), [], []

        k_mat = np.stack(keys, axis=0) # (N, dim)
        if value_vectors is not None:
            v_mat = np.stack(value_vectors, axis=0)
        else:
            v_mat = k_mat # Auto-representación de valores si no se especifican

        context_vec, weights = self.qkv_attention.forward(query_vector, k_mat, v_mat)

        ranked = []
        for i, val in enumerate(values):
            ranked.append((float(weights[i]), val))
        ranked.sort(key=lambda x: x[0], reverse=True)

        return context_vec, weights.tolist(), ranked
