"""
knowledge_codec.py - Códecs de Dominio para Conversión Bidireccional.
Traduce entre KnowledgeArtifact y representaciones estructuradas (SemanticFrame / Claims),
incluyendo soporte inicial para Texto, Mediciones con Unidades y LaTeX Matemático.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from universal_io import KnowledgeArtifact
from knowledge import Entity, Claim, EpistemicStatus

@dataclass
class SemanticFrame:
    """Estructura intermedia canónica (IR Semántico)."""
    text: str
    confidence: float
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DomainCodec:
    """Contrato base para códecs de dominio."""
    def decode(self, artifact: KnowledgeArtifact) -> SemanticFrame:
        raise NotImplementedError

    def encode(self, frame: SemanticFrame, target_media_type: str) -> KnowledgeArtifact:
        raise NotImplementedError

class TextCodec(DomainCodec):
    """Códec para lenguaje natural general."""
    def decode(self, artifact: KnowledgeArtifact) -> SemanticFrame:
        text = str(artifact.content).strip()
        entities = []
        relations = []
        # Parser básico determinista para patrones frecuentes
        # e.g. "X está en Y" o "X tiene Y"
        words = text.lower().replace(".", "").split()
        if "está en" in text.lower() or "esta en" in text.lower():
            idx = words.index("en") if "en" in words else -1
            if idx > 1 and idx < len(words) - 1:
                subj = words[idx-2] if words[idx-2] not in ("el", "la", "un", "una") else words[idx-1]
                obj = words[idx+1] if words[idx+1] not in ("el", "la", "un", "una") else words[idx+2]
                entities.append({"id": subj, "type": "Entity", "label": subj})
                entities.append({"id": obj, "type": "Location", "label": obj})
                relations.append({
                    "subject": subj, "predicate": "esta_en", "object": obj, "polarity": True, "confidence": 0.9
                })

        return SemanticFrame(text=text, confidence=0.85, entities=entities, relations=relations)

    def encode(self, frame: SemanticFrame, target_media_type: str = "text/plain") -> KnowledgeArtifact:
        # Genera resumen en texto
        rel_descs = [f"{r['subject']} {r['predicate']} {r['object']}" for r in frame.relations]
        text_out = f"Hechos reportados: {', '.join(rel_descs)}." if rel_descs else frame.text
        return KnowledgeArtifact(
            id=f"art_out_{id(frame)}",
            media_type="text/plain",
            domain="general",
            content=text_out
        )

class LatexCodec(DomainCodec):
    """
    Códec para expresiones matemáticas en LaTeX (para futuros graficadores y razonamiento matemático).
    Demuestra que matemáticas y física se procesan bajo el mismo contrato universal.
    """
    def decode(self, artifact: KnowledgeArtifact) -> SemanticFrame:
        latex_str = str(artifact.content).strip()
        entities = []
        relations = []

        # Reconocimiento de ecuaciones como f(x) = ... o y = mx + b
        if "=" in latex_str:
            lhs, rhs = latex_str.split("=", 1)
            lhs, rhs = lhs.strip(), rhs.strip()
            eq_id = f"eq_{hash(latex_str) % 10000}"
            entities.append({"id": eq_id, "type": "Equation", "label": latex_str})
            entities.append({"id": lhs, "type": "MathExpression", "label": lhs})
            entities.append({"id": rhs, "type": "MathExpression", "label": rhs})
            relations.append({"subject": eq_id, "predicate": "lhs", "object": lhs, "polarity": True, "confidence": 1.0})
            relations.append({"subject": eq_id, "predicate": "rhs", "object": rhs, "polarity": True, "confidence": 1.0})

        return SemanticFrame(text=latex_str, confidence=0.98, entities=entities, relations=relations)

    def encode(self, frame: SemanticFrame, target_media_type: str = "application/x-latex") -> KnowledgeArtifact:
        # Reconstruye fórmula en formato LaTeX formal
        eq_rel = next((r for r in frame.relations if r["predicate"] == "lhs"), None)
        rhs_rel = next((r for r in frame.relations if r["predicate"] == "rhs"), None)
        if eq_rel and rhs_rel:
            content = f"{eq_rel['object']} = {rhs_rel['object']}"
        else:
            content = frame.text
        return KnowledgeArtifact(
            id=f"latex_{id(frame)}",
            media_type="application/x-latex",
            domain="mathematics",
            content=content
        )

class UniversalCodecRegistry:
    def __init__(self):
        self._codecs: Dict[str, DomainCodec] = {
            "text/plain": TextCodec(),
            "application/x-latex": LatexCodec()
        }

    def register_codec(self, media_type: str, codec: DomainCodec) -> None:
        self._codecs[media_type] = codec

    def decode_artifact(self, artifact: KnowledgeArtifact) -> SemanticFrame:
        codec = self._codecs.get(artifact.media_type, self._codecs["text/plain"])
        return codec.decode(artifact)

    def encode_to_artifact(self, frame: SemanticFrame, media_type: str) -> KnowledgeArtifact:
        codec = self._codecs.get(media_type, self._codecs["text/plain"])
        return codec.encode(frame, media_type)
