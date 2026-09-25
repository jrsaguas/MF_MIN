"""
universal_io.py - Contrato Universal de Entrada y Salida (Universal I/O).
Permite que cualquier fuente de conocimiento (texto, LaTeX, JSON, código, mediciones)
ingrese y egrese del sistema cognitivo sin alterar el Kernel MF_MIN.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import time

@dataclass
class KnowledgeArtifact:
    """
    Artefacto de conocimiento universal.
    Empaqueta cualquier contenido con su tipo MIME, dominio y procedencia.
    """
    id: str
    media_type: str       # "text/plain", "application/x-latex", "application/json", "application/measurement"
    domain: str           # "general", "mathematics", "physics", "programming", "facility"
    content: Any
    source: str = "user"
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
