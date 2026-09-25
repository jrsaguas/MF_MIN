"""
domain.py - Gestor y Cargador de Dominios Operacionales para MF_MIN V7.
Permite instanciar configuraciones de entorno y ontologías formales a partir
de especificaciones JSON externas (domains/*.json).
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

from mf_min_definitivo import Kernel, Transition
from environment import VirtualFacilityEnvironment


@dataclass
class DomainSpec:
    name: str
    description: str
    initial_location: str
    rooms: List[str]
    doors: Dict[str, Dict[str, Any]]
    items: Dict[str, Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DomainSpec:
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            initial_location=data["initial_location"],
            rooms=list(data.get("rooms", [])),
            doors=dict(data.get("doors", {})),
            items=dict(data.get("items", {}))
        )

    @classmethod
    def from_file(cls, filepath: str) -> DomainSpec:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class DomainManager:
    """Administra los dominios disponibles en el sistema."""
    def __init__(self, domains_dir: Optional[str] = None):
        if domains_dir is None:
            domains_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "domains")
        self.domains_dir = domains_dir
        self.domains: Dict[str, DomainSpec] = {}
        self.load_all_domains()

    def load_all_domains(self) -> None:
        if not os.path.exists(self.domains_dir):
            return
        for fname in os.listdir(self.domains_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(self.domains_dir, fname)
                try:
                    spec = DomainSpec.from_file(fpath)
                    self.domains[spec.name] = spec
                except Exception as e:
                    pass

    def get_domain(self, name: str) -> Optional[DomainSpec]:
        return self.domains.get(name)

    def list_domains(self) -> List[str]:
        return list(self.domains.keys())

    def apply_to_kernel(self, kernel: Kernel, spec: DomainSpec) -> None:
        """Puebla el Kernel con los objetos y relaciones base del dominio."""
        # Objeto agente
        kernel.transition(Transition("add_object", {"id": "agente", "type": "Agent"}))
        # Habitaciones
        for room in spec.rooms:
            kernel.transition(Transition("add_object", {"id": room, "type": "Room"}))
        # Puertas
        for door_id in spec.doors.keys():
            kernel.transition(Transition("add_object", {"id": door_id, "type": "Door"}))
        # Items
        for item_id, item_info in spec.items.items():
            kernel.transition(Transition("add_object", {"id": item_id, "type": item_info.get("type", "Item")}))
        # Estados estándar
        for val in ["abierta", "cerrada", "bloqueada", "desbloqueada", "en_suelo", "en_mano"]:
            kernel.transition(Transition("add_object", {"id": val, "type": "StateVal"}))


if __name__ == "__main__":
    dm = DomainManager()
    print("Dominios cargados exitosamente:", dm.list_domains())
