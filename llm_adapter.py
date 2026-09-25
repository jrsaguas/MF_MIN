"""
llm_adapter.py - Adaptador desacoplado para LLMs Locales (Ollama) y Remotos.
Aísla al sistema de cualquier proveedor específico. El LLM es tratado como un transcriptor
lingüístico no confiable cuya salida debe ser validada por SemanticBridge y EpistemicEvaluator.
"""
from __future__ import annotations
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

class LLMAdapter:
    """Contrato base para cualquier motor de lenguaje natural."""
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        raise NotImplementedError

    def extract_semantic_frame(self, user_text: str) -> Dict[str, Any]:
        raise NotImplementedError

class OllamaAdapter(LLMAdapter):
    """
    Adaptador nativo para Ollama corriendo localmente (gratuito, sin conexión externa).
    Compatible con llama3.1, qwen2.5, gemma, etc.
    """
    def __init__(
        self,
        model: str = "llama3.2:3b",
        host: str = "http://localhost:11434",
        timeout: float = 10.0
    ):
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        """Comprueba si el servidor local de Ollama está encendido y respondiendo."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                return res_json.get("response", "").strip()
        except Exception as e:
            # Fallback seguro si Ollama no está activo en este momento
            return f"[Ollama no disponible en {self.host}: {e}]"

    def extract_semantic_frame(self, user_text: str) -> Dict[str, Any]:
        """
        Pide a Ollama estructurar el texto en formato JSON (SemanticFrame).
        Si Ollama no está activo, activa el fallback heurístico determinista.
        """
        if not self.is_available():
            return self._heuristic_fallback(user_text)

        system_prompt = (
            "Eres un extractor semántico para un sistema neuro-simbólico. "
            "Convierte la frase del usuario en un JSON con la estructura: "
            '{"text": "...", "confidence": 0.95, "entities": [{"id": "...", "type": "..."}], '
            '"relations": [{"subject": "...", "predicate": "...", "object": "...", "polarity": true}]}. '
            "Responde estrictamente con JSON válido sin explicaciones adicionales."
        )

        raw_response = self.generate(prompt=user_text, system_prompt=system_prompt)
        try:
            # Limpiar posibles bloques ```json ... ```
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception:
            return self._heuristic_fallback(user_text)

    def _heuristic_fallback(self, user_text: str) -> Dict[str, Any]:
        """Fallback determinista que garantiza funcionamiento offline o sin GPU."""
        text_lower = user_text.lower()
        entities = []
        relations = []

        if "servidores" in text_lower or "sala" in text_lower:
            entities.append({"id": "agente", "type": "Agent"})
            entities.append({"id": "sala_servidores", "type": "Room"})
            relations.append({
                "subject": "agente", "predicate": "posicion", "object": "sala_servidores", "polarity": True, "confidence": 0.9
            })
        elif "deposito" in text_lower:
            entities.append({"id": "agente", "type": "Agent"})
            entities.append({"id": "deposito", "type": "Room"})
            relations.append({
                "subject": "agente", "predicate": "posicion", "object": "deposito", "polarity": True, "confidence": 0.9
            })

        return {
            "text": user_text,
            "confidence": 0.85,
            "entities": entities,
            "relations": relations
        }
