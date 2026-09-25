"""
universal_extractor.py — Extractor de Representación Universal para MF_MIN.
Convierte aserciones en lenguaje natural no estructurado en hechos relacionales
atómicos (source, predicate, target, polarity), desacoplado de dominios específicos.
Incluye filtro de plausibilidad lingüística para rechazar entradas no derivables ("no sé").
"""
from __future__ import annotations
import re
from typing import Optional, Dict, Any, List, Tuple


class UniversalFactExtractor:
    """
    Extractor determinista de hechos relacionales universales.
    Reconoce construcciones estándar en español como pertenencia, dependencia,
    posesión, habilitación y atribución de estados.
    """

    # Palabras vacías / artículos para normalización de slugs
    ARTICLES = ("el", "la", "los", "las", "un", "una", "unos", "unas", "al", "del")

    # Patrones relacionales soportados (regex -> (predicado_canónico, swap_args))
    PATTERNS: List[Tuple[re.Pattern, str, bool]] = [
        # X pertenece a Y / X pertenece al Y
        (re.compile(r"^(.*?)\s+pertenece\s+(?:a|al)\s+(.*?)\.?$", re.IGNORECASE), "pertenece_a", False),
        # X no pertenece a Y
        (re.compile(r"^(.*?)\s+no\s+pertenece\s+(?:a|al)\s+(.*?)\.?$", re.IGNORECASE), "no_pertenece_a", False),
        # X depende de Y / X depende del Y
        (re.compile(r"^(.*?)\s+depende\s+(?:de|del)\s+(.*?)\.?$", re.IGNORECASE), "depende_de", False),
        # X tiene Y / X tiene un/una Y
        (re.compile(r"^(.*?)\s+tiene\s+(.*?)\.?$", re.IGNORECASE), "tiene", False),
        # X no tiene Y
        (re.compile(r"^(.*?)\s+no\s+tiene\s+(.*?)\.?$", re.IGNORECASE), "no_tiene", False),
        # X abre Y / X abre la Y
        (re.compile(r"^(.*?)\s+abre\s+(.*?)\.?$", re.IGNORECASE), "abre", False),
        # X está Y / X está en Y
        (re.compile(r"^(.*?)\s+(?:está|esta)\s+en\s+(.*?)\.?$", re.IGNORECASE), "esta_en", False),
        (re.compile(r"^(.*?)\s+(?:está|esta)\s+(.*?)\.?$", re.IGNORECASE), "está", False),
        # X es un/una Y
        (re.compile(r"^(.*?)\s+es\s+(?:un|una|de tipo)\s+(.*?)\.?$", re.IGNORECASE), "tipo", False),
        # X causa Y
        (re.compile(r"^(.*?)\s+causa\s+(.*?)\.?$", re.IGNORECASE), "causa", False),
        # X conecta con Y
        (re.compile(r"^(.*?)\s+conecta\s+(?:con)?\s*(.*?)\.?$", re.IGNORECASE), "conecta_con", False),
        # X vecino de Y
        (re.compile(r"^(.*?)\s+es\s+vecino\s+(?:de|del)\s+(.*?)\.?$", re.IGNORECASE), "vecino_de", False),
    ]

    def __init__(self):
        pass

    @classmethod
    def clean_slug(cls, text: str) -> str:
        """Normaliza una cadena a slug alfanumérico limpio eliminando artículos."""
        s = text.strip().lower()
        if s.startswith("al "):
            s = s[3:]
        elif s.startswith("del "):
            s = s[4:]
        else:
            for art in ["el ", "la ", "los ", "las ", "un ", "una ", "unos ", "unas "]:
                if s.startswith(art):
                    s = s[len(art):]
                    break
        slug = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ_]+", "_", s).strip("_")
        return slug

    @classmethod
    def is_plausible_natural_language(cls, text: str) -> bool:
        """
        Filtro de plausibilidad lingüística para evitar aceptar ruido de teclado
        (e.g., 'zxq wvbrt plkm') como si fuera un hecho válido.
        """
        t = text.strip()
        if len(t) < 3 or len(t) > 300:
            return False
        
        words = [w for w in re.split(r"\s+", t) if w]
        if len(words) < 2:
            return False

        vowels = set("aeiouáéíóúAEIOUÁÉÍÓÚ")
        has_vowels = all(any(c in vowels for c in w) for w in words if len(w) > 2)
        if not has_vowels:
            return False

        for w in words:
            if re.search(r"[bcdfghjklmnpqrstvwxyz]{5,}", w.lower()):
                return False

        return True

    def extract_relation(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extrae una única relación canónica a partir de una oración asertiva.
        Retorna un diccionario con {'subject', 'predicate', 'object', 'polarity', 'confidence'}
        o None si no es analizable gramaticalmente.
        """
        if not self.is_plausible_natural_language(text):
            return None

        clean_text = text.strip()
        for pattern, pred, swap in self.PATTERNS:
            m = pattern.match(clean_text)
            if m:
                raw_s, raw_o = m.group(1), m.group(2)
                s = self.clean_slug(raw_s)
                o = self.clean_slug(raw_o)
                if not s or not o:
                    continue

                polarity = True
                actual_pred = pred
                if pred.startswith("no_"):
                    polarity = False
                    actual_pred = pred[3:]

                if swap:
                    s, o = o, s

                return {
                    "subject": s,
                    "predicate": actual_pred,
                    "object": o,
                    "polarity": polarity,
                    "confidence": 0.95,
                    "raw_text": text
                }

        return None

    def extract_facts(self, text: str) -> List[Dict[str, Any]]:
        """
        Divide un texto multioracional (separado por puntos) y extrae todos los hechos válidos.
        """
        sentences = [s.strip() for s in re.split(r"[.\n]+", text) if s.strip()]
        facts = []
        for s in sentences:
            fact = self.extract_relation(s)
            if fact:
                facts.append(fact)
        return facts
