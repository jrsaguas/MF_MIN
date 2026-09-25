"""
environment.py - Entorno Simulado Externo al Kernel MF_MIN.
Representa la realidad física independiente del modelo mental del agente.
Posee estado propio, leyes de causalidad física y sensores que devuelven lecturas parciales.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

@dataclass
class ActionResult:
    success: bool
    message: str
    energy_cost: float
    observations: List[Dict[str, Any]] = field(default_factory=list)

class VirtualFacilityEnvironment:
    """
    Entorno físico simulado: Instalación con habitaciones, puertas y llaves.
    Mantiene la verdad física del mundo exterior.
    """
    def __init__(self):
        # Estado físico real del entorno
        self.agent_location: str = "pasillo"
        self.inventory: List[str] = []

        # Puertas y cerraduras
        # puerta_servidores requiere "tarjeta_azul" estrictamente
        self.doors: Dict[str, Dict[str, Any]] = {
            "puerta_servidores": {
                "connects": ("pasillo", "sala_servidores"),
                "open": False,
                "locked": True,
                "required_key": "tarjeta_azul"
            },
            "puerta_deposito": {
                "connects": ("pasillo", "deposito"),
                "open": False,
                "locked": False,
                "required_key": None
            }
        }

        # Ubicación física de ítems
        self.items_location: Dict[str, str] = {
            "llave_bronce": "pasillo",      # Llave incorrecta tirada en el pasillo
            "tarjeta_azul": "deposito"      # Tarjeta correcta dentro del depósito
        }

    def get_sensory_data(self) -> List[Dict[str, Any]]:
        """
        Simula los sensores físicos del agente según su posición actual (percepción parcial).
        """
        readings: List[Dict[str, Any]] = []

        # 1. Sensor de posición del agente
        readings.append({
            "source": "sensor_gps_interno",
            "type": "relation",
            "subject": "agente",
            "predicate": "posicion",
            "object": self.agent_location,
            "polarity": True
        })

        # 2. Sensor de inventario (manos)
        for item in self.inventory:
            readings.append({
                "source": "sensor_carga",
                "type": "relation",
                "subject": item,
                "predicate": "estado",
                "object": "en_mano",
                "polarity": True
            })

        # 3. Sensor visual de la habitación actual (solo ve objetos en la misma sala)
        for item, loc in self.items_location.items():
            if loc == self.agent_location and item not in self.inventory:
                readings.append({
                    "source": "camara_optica",
                    "type": "relation",
                    "subject": item,
                    "predicate": "estado",
                    "object": "en_suelo",
                    "polarity": True
                })
                readings.append({
                    "source": "camara_optica",
                    "type": "relation",
                    "subject": item,
                    "predicate": "ubicacion",
                    "object": self.agent_location,
                    "polarity": True
                })

        # 4. Sensor de puertas adyacentes a la habitación actual
        for door_id, d_data in self.doors.items():
            room_a, room_b = d_data["connects"]
            if self.agent_location in (room_a, room_b):
                readings.append({
                    "source": "sensor_puerta",
                    "type": "relation",
                    "subject": door_id,
                    "predicate": "estado",
                    "object": "abierta" if d_data["open"] else "cerrada",
                    "polarity": True
                })
                readings.append({
                    "source": "sensor_seguridad",
                    "type": "relation",
                    "subject": door_id,
                    "predicate": "seguridad",
                    "object": "bloqueada" if d_data["locked"] else "desbloqueada",
                    "polarity": True
                })

        return readings

    def step(self, action_name: str, target: Optional[str] = None) -> ActionResult:
        """
        Ejecución física en el mundo real con validación causal.
        """
        if action_name == "recoger":
            item = target
            if item in self.items_location and self.items_location[item] == self.agent_location:
                self.inventory.append(item)
                del self.items_location[item]
                return ActionResult(
                    success=True,
                    message=f"Recogiste {item} del suelo.",
                    energy_cost=1.0,
                    observations=self.get_sensory_data()
                )
            return ActionResult(
                success=False,
                message=f"No hay ningun {item} alcanzable en {self.agent_location}.",
                energy_cost=0.5,
                observations=self.get_sensory_data()
            )

        elif action_name == "destrabar":
            door_id = target
            if door_id not in self.doors:
                return ActionResult(False, f"La puerta {door_id} no existe.", 0.5, self.get_sensory_data())

            door = self.doors[door_id]
            if self.agent_location not in door["connects"]:
                return ActionResult(False, f"No estas cerca de {door_id}.", 0.5, self.get_sensory_data())

            if not door["locked"]:
                return ActionResult(True, f"{door_id} ya estaba desbloqueada.", 0.5, self.get_sensory_data())

            # Comprobar si el agente tiene la llave requerida en su inventario
            req_key = door["required_key"]
            if req_key and req_key in self.inventory:
                door["locked"] = False
                return ActionResult(
                    success=True,
                    message=f"Destrabaste {door_id} exitosamente usando {req_key}.",
                    energy_cost=1.5,
                    observations=self.get_sensory_data()
                )
            else:
                # Intento con llave equivocada o con las manos vacías: FALLO FÍSICO REAL
                used_items = [i for i in self.inventory if "llave" in i or "tarjeta" in i]
                return ActionResult(
                    success=False,
                    message=f"Fallo al destrabar {door_id}: Ninguno de tus objetos ({used_items}) coincide con la cerradura.",
                    energy_cost=1.0,
                    observations=self.get_sensory_data()
                )

        elif action_name == "abrir":
            door_id = target
            if door_id not in self.doors:
                return ActionResult(False, f"Puerta desconocida {door_id}.", 0.5, self.get_sensory_data())

            door = self.doors[door_id]
            if door["locked"]:
                return ActionResult(
                    success=False,
                    message=f"No se puede abrir {door_id}: El pestillo esta bloqueado físicamente.",
                    energy_cost=0.8,
                    observations=self.get_sensory_data()
                )

            door["open"] = True
            return ActionResult(
                success=True,
                message=f"Abriste {door_id}.",
                energy_cost=1.0,
                observations=self.get_sensory_data()
            )

        elif action_name == "mover_a":
            destination = target
            # Verificar si hay una puerta abierta conectando la sala actual con el destino
            connected = False
            for d_id, d_data in self.doors.items():
                if self.agent_location in d_data["connects"] and destination in d_data["connects"]:
                    if d_data["open"]:
                        connected = True
                        break
                    else:
                        return ActionResult(
                            success=False,
                            message=f"No puedes pasar a {destination}: {d_id} esta cerrada.",
                            energy_cost=0.8,
                            observations=self.get_sensory_data()
                        )

            if connected:
                self.agent_location = destination
                return ActionResult(
                    success=True,
                    message=f"Te moviste a {destination}.",
                    energy_cost=1.5,
                    observations=self.get_sensory_data()
                )

            return ActionResult(
                success=False,
                message=f"No hay conexion transitable entre {self.agent_location} y {destination}.",
                energy_cost=0.5,
                observations=self.get_sensory_data()
            )

        return ActionResult(False, f"Accion desconocida: {action_name}", 0.0, self.get_sensory_data())
