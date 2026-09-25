"""
knowledge.py - Estructuras Fundamentales de la Capa de Conocimiento (Knowledge Layer).
Define:
 - EpistemicStatus: Estados epistemológicos formales (ASSERTED, SUPPORTED, DERIVED, UNKNOWN, CONTRADICTED, REJECTED).
 - Sense: Sentidos lingüísticos (desambiguación de lexemas, e.g. banco_financiero vs banco_asiento).
 - Entity: Representación canónica de entidades.
 - Evidence & Provenance: Justificación, fiabilidad y procedencia del dato.
 - Claim: Proposición atómica afirmada con desglose de confianza (interpretación, evidencia, lógica).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import time

class EpistemicStatus(str, Enum):
    ASSERTED = "ASSERTED"          # Afirmado por una fuente, aún sin verificación cruzada
    SUPPORTED = "SUPPORTED"        # Respaldado por evidencia empírica confiable
    DERIVED = "DERIVED"            # Deducido formalmente mediante reglas lógicas (EngineD)
    UNKNOWN = "UNKNOWN"            # Estado no determinado
    CONTRADICTED = "CONTRADICTED"  # Existen afirmaciones opuestas activas (ambas se conservan)
    REJECTED = "REJECTED"          # Violación directa de axiomas de consistencia de MF_MIN

@dataclass(frozen=True)
class Sense:
    """Sentido semántico que desambigua un término lingüístico."""
    id: str
    lexeme: str
    definition: str
    domain: str = "general"
    pos: str = "noun"

@dataclass
class Entity:
    """Entidad canónica única en el grafo de conocimiento."""
    id: str
    type: str
    label: str
    aliases: List[str] = field(default_factory=list)
    sense_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Evidence:
    """Respaldo empírico o sensorial de una afirmación."""
    id: str
    source: str
    reliability: float = 0.8
    modality: str = "sensor"  # "text", "sensor", "user", "api", "rule"
    timestamp: float = field(default_factory=time.time)
    raw_data: Any = None

@dataclass
class Provenance:
    """Procedencia y linaje del conocimiento."""
    origin: str               # "asserted", "perceived", "derived", "user_input"
    actor: Optional[str] = None
    rule_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class Claim:
    """
    Afirmación atómica formal con control epistemológico multidimensional.
    Separa:
     - Confianza de interpretación (c_i): ¿Se entendió bien el lenguaje/sensor?
     - Confianza de evidencia (c_e): ¿Qué tan confiable es la fuente?
     - Confianza lógica (c_l): ¿Es compatible formalmente con MF_MIN?
    """
    subject: str
    predicate: str
    object: str
    polarity: bool = True
    status: EpistemicStatus = EpistemicStatus.ASSERTED
    confidence_interpretation: float = 1.0
    confidence_evidence: float = 0.5
    confidence_logical: float = 1.0
    provenance: Optional[Provenance] = None
    evidences: List[Evidence] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None

    @property
    def spo_key(self) -> Tuple[str, str, str, bool]:
        return (self.subject, self.predicate, self.object, self.polarity)

    @property
    def composite_confidence(self) -> float:
        """C_comp = c_i * c_e * c_l"""
        return float(self.confidence_interpretation * self.confidence_evidence * self.confidence_logical)
