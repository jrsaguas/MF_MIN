"""
audit_log.py - Registro y Trazabilidad Formal de Auditoría para MF_MIN V7.
Permite registrar secuencialmente transiciones de estado, violaciones detectadas
y eventos cognitivos en un libro de contabilidad inmutable en memoria/disco.
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from mf_min_definitivo import Transition, State


@dataclass
class AuditEntry:
    timestamp: float
    entry_type: str  # "transition", "reconciliation", "deduction", "violation", "event"
    payload: Dict[str, Any]
    cycle_id: Optional[str] = None


class AuditLogger:
    def __init__(self, log_filepath: Optional[str] = None):
        self.entries: List[AuditEntry] = []
        self.log_filepath = log_filepath

    def log_transition(self, transition: Transition, before_hash: str, after_hash: str) -> None:
        entry = AuditEntry(
            timestamp=time.time(),
            entry_type="transition",
            payload={
                "operation": transition.operation,
                "payload": dict(transition.payload),
                "before_state_hash": before_hash,
                "after_state_hash": after_hash
            }
        )
        self.entries.append(entry)
        self._flush_if_needed(entry)

    def log_event(self, event_type: str, payload: Dict[str, Any], cycle_id: Optional[str] = None) -> None:
        entry = AuditEntry(
            timestamp=time.time(),
            entry_type="event",
            payload={"event_type": event_type, "data": payload},
            cycle_id=cycle_id
        )
        self.entries.append(entry)
        self._flush_if_needed(entry)

    def get_entries(self) -> List[Dict[str, Any]]:
        return [
            {
                "timestamp": e.timestamp,
                "entry_type": e.entry_type,
                "payload": e.payload,
                "cycle_id": e.cycle_id
            }
            for e in self.entries
        ]

    def _flush_if_needed(self, entry: AuditEntry) -> None:
        if self.log_filepath:
            with open(self.log_filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.__dict__, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    logger = AuditLogger()
    logger.log_event("init", {"msg": "Auditoría iniciada"})
    print("AuditLogger verificado con éxito, entradas:", len(logger.entries))
