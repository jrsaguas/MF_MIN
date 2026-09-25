"""
perception.py - Módulo de Percepción Sensorial.
Convierte lecturas del entorno externo en propuestas estructuradas para Reconciler.
Detecta discrepancias entre el modelo mental del Kernel y la realidad física observada.
"""
from __future__ import annotations
from typing import List, Dict, Any, Tuple
from mf_min_definitivo import Transition, Kernel
from reconcile import Proposal, Reconciler

class PerceptionModule:
    """
    Sensor perceptual activo del agente.
    Genera transiciones propuestas y valida la correspondencia empírica.
    """
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.reconciler = Reconciler(kernel)
        self._proposal_counter = 0

    def process_sensory_data(self, readings: List[Dict[str, Any]]) -> List[Proposal]:
        """
        Toma lecturas sensoriales crudas del entorno y genera propuestas.
        """
        proposals: List[Proposal] = []
        for r in readings:
            self._proposal_counter += 1
            source = r.get("source", "sensor_desconocido")
            s = r["subject"]
            p = r["predicate"]
            o = r["object"]
            pol = r.get("polarity", True)

            # Generar ID determinista para la relación observada
            rel_id = f"r_perc_{s}_{p}_{o}"

            trans = Transition("add_relation", {
                "id": rel_id,
                "source": s,
                "predicate": p,
                "target": o,
                "polarity": pol,
                "origin": "perceived"
            })

            # Añadir con nivel de confianza según el sensor
            confidence = 0.95 if "optica" in source or "gps" in source else 0.85
            proposals.append(Proposal(source_id=source, transition=trans, confidence=confidence))

        return proposals

    def perceive_and_reconcile(self, readings: List[Dict[str, Any]]) -> Tuple[List[Transition], List[Proposal]]:
        """
        Ejecuta el ciclo de percepción: lecturas -> propuestas -> reconciliación.
        Retorna:
         - committed_transitions: transiciones listas para cometer en Kernel
         - disputed_proposals: observaciones que contradicen el estado o entre sí
        """
        proposals = self.process_sensory_data(readings)
        result = self.reconciler.reconcile(proposals)

        # Si hay propuestas disputed que contradicen creencias previas del Kernel,
        # significa que el mundo cambió físicamente (actualización empírica).
        # Resolvemos la creencia obsoleta eliminando la relación vieja y aceptando la nueva.
        committed = list(result.committed)
        for disp in result.disputed:
            p_trans = disp.transition
            p_load = p_trans.payload
            s, pred, tgt, pol = p_load["source"], p_load["predicate"], p_load["target"], p_load["polarity"]

            # Buscar la creencia obsoleta en el Kernel
            for old_rel in list(self.kernel.state.relations.values()):
                if old_rel.source == s and old_rel.predicate == pred and old_rel.target == tgt and old_rel.polarity != pol:
                    # El mundo contradice la creencia previa: el mundo manda
                    committed.append(Transition("remove_relation", {"id": old_rel.id}))
                    committed.append(p_trans)

        return committed, result.disputed
