"""
natural_language.py - Interfaz de Lenguaje Natural Bidireccional.
1. Parser semántico: Convierte comandos de usuario en Goals formales para el Kernel con umbral epistémico.
2. Generador explicativo: Traduce el razonamiento interno y resultados a explicaciones humanas.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, Tuple, List
from motor_c import Goal
from embeddings import VectorEmbeddingEngine, cosine_similarity
from universal_extractor import UniversalFactExtractor


class NaturalLanguageInterface:
    def __init__(self, embedder: Optional[VectorEmbeddingEngine] = None, default_threshold: float = 0.35):
        self.embedder = embedder or VectorEmbeddingEngine()
        self.default_threshold = default_threshold

        # Plantillas de objetivos formales asociados a descripciones semánticas
        self._goal_templates = [
            (
                "entrar a la sala de servidores o acceder a servidores",
                Goal(conditions=(("agente", "posicion", "sala_servidores", True),))
            ),
            (
                "ir al deposito o entrar al deposito",
                Goal(conditions=(("agente", "posicion", "deposito", True),))
            ),
            (
                "recoger la tarjeta azul o conseguir tarjeta de acceso",
                Goal(conditions=(("tarjeta_azul", "estado", "en_mano", True),))
            ),
            (
                "recoger la llave de bronce del suelo",
                Goal(conditions=(("llave_bronce", "estado", "en_mano", True),))
            ),
            (
                "abrir la puerta de servidores",
                Goal(conditions=(("puerta_servidores", "estado", "abierta", True),))
            ),
            (
                "abrir la puerta del deposito",
                Goal(conditions=(("puerta_deposito", "estado", "abierta", True),))
            )
        ]

    def parse_instruction_to_goal(self, user_text: str, threshold: Optional[float] = None) -> Tuple[Optional[Goal], float, str]:
        """
        Interpreta una instrucción en lenguaje natural y la proyecta al Goal formal más afín.
        Aplica filtro de plausibilidad lingüística y umbral mínimo de similitud semántica.
        Si la similitud no supera el umbral, retorna (None, sim, "") ejerciendo honestidad epistémica ("no sé").
        """
        if not user_text or not isinstance(user_text, str):
            return None, 0.0, ""

        # 1. Filtro de plausibilidad ante ruido de teclado
        if not UniversalFactExtractor.is_plausible_natural_language(user_text):
            return None, 0.0, ""

        th = self.default_threshold if threshold is None else threshold
        query_vec = self.embedder.embed_text(user_text)
        best_goal = None
        best_sim = -1.0
        best_desc = ""

        for desc, goal in self._goal_templates:
            tmpl_vec = self.embedder.embed_text(desc)
            sim = cosine_similarity(query_vec, tmpl_vec)
            if sim > best_sim:
                best_sim = sim
                best_goal = goal
                best_desc = desc

        # 2. Umbral mínimo de afinidad semántica
        if best_sim < th:
            return None, best_sim, ""

        return best_goal, best_sim, best_desc

    def generate_explanation(
        self,
        goal_desc: str,
        plan_names: List[str],
        executed: bool,
        real_world_success: bool,
        reward: float,
        deductions_count: int,
        feedback_message: str
    ) -> str:
        """
        Genera un informe explicativo legible para el usuario humano.
        """
        lines = []
        lines.append(f"Misión recibida: '{goal_desc}'")
        lines.append(f"• Inferencia deductiva: Se derivaron {deductions_count} nuevos hechos mediante EngineD.")
        lines.append(f"• Plan estratégico formulado: {' -> '.join(plan_names) if plan_names else 'Ninguno factible'}")

        if real_world_success:
            lines.append(f"• Resultado en el entorno: ÉXITO. {feedback_message}")
            lines.append(f"• Evaluación y aprendizaje: Recompensa ambiental de {reward:.2f}. Trayectoria consolidada en memoria episódica.")
        else:
            lines.append(f"• Resultado en el entorno: FALLO / DISCREPANCIA. {feedback_message}")
            lines.append(f"• Adaptación: Se penalizaron las acciones fallidas en Q(a) y se actualizó el modelo mental.")

        return "\n".join(lines)
