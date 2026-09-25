"""
test_context_representation.py — Batería de Pruebas para la Representación Contextual (Fase A).
Verifica:
  1. Determinismo e Invariancia a IDs de Relación y Orden de Inserción.
  2. Diferenciabilidad de Estados Físicos Distintos.
  3. Sensibilidad al Objetivo Cognitivo (Goal Sensitivity).
  4. Sensibilidad a Acciones Aplicables (Affordances).
  5. Serialización y Reconstrucción JSON sin Pérdidas.
  6. Integración en ActiveContext.
"""
from __future__ import annotations
import json
import unittest

from mf_min_definitivo import Kernel, Transition, State, Object, Relation
from motor_c import Goal, Action
from memory import Memory
from knowledge_store import KnowledgeStore
from retrieval import Retriever
from attention import AttentionEngine
from embeddings import VectorEmbeddingEngine
from context import ContextBuilder, ContextSignature, ActiveContext


class TestContextRepresentation(unittest.TestCase):

    def setUp(self):
        self.embedder = VectorEmbeddingEngine(dim=16)
        self.memory = Memory()
        self.store = KnowledgeStore()
        self.retriever = Retriever(memory=self.memory, knowledge_store=self.store, embedding_engine=self.embedder)
        self.attention = AttentionEngine(dim=16)
        self.builder = ContextBuilder(self.retriever, self.attention, self.embedder)

    def test_1_determinismo_e_invariancia_orden_e_ids(self):
        """
        Dos estados semánticamente idénticos (mismas entidades y relaciones),
        pero construidos con IDs de relación diferentes y en orden inverso,
        DEBEN producir exactamente la misma exact_key y structural_key.
        """
        k1 = Kernel()
        for o, t in [("agente", "Agent"), ("puerta", "Door"), ("pasillo", "Location"), ("cerrada", "StateVal"), ("sala", "Location")]:
            k1.transition(Transition("add_object", {"id": o, "type": t}))
        k1.transition(Transition("add_relation", {"id": "r_a", "source": "agente", "predicate": "posicion", "target": "pasillo"}))
        k1.transition(Transition("add_relation", {"id": "r_b", "source": "puerta", "predicate": "estado", "target": "cerrada"}))

        k2 = Kernel()
        for o, t in [("agente", "Agent"), ("puerta", "Door"), ("pasillo", "Location"), ("cerrada", "StateVal"), ("sala", "Location")]:
            k2.transition(Transition("add_object", {"id": o, "type": t}))
        # Orden inverso e IDs completamente diferentes
        k2.transition(Transition("add_relation", {"id": "rel_999", "source": "puerta", "predicate": "estado", "target": "cerrada"}))
        k2.transition(Transition("add_relation", {"id": "rel_111", "source": "agente", "predicate": "posicion", "target": "pasillo"}))

        goal = Goal(conditions=(("agente", "posicion", "sala", True),))

        sig1 = self.builder.build_context_signature(k1.state, goal)
        sig2 = self.builder.build_context_signature(k2.state, goal)

        print("\n=== TEST 1: Determinismo e Invariancia ===")
        print(f"Sig 1 Exact Key: {sig1.exact_key}")
        print(f"Sig 2 Exact Key: {sig2.exact_key}")

        self.assertEqual(sig1.exact_key, sig2.exact_key)
        self.assertEqual(sig1.structural_key, sig2.structural_key)
        self.assertEqual(sig1.focal_relations, sig2.focal_relations)

    def test_2_diferenciabilidad_de_estados_fisicos(self):
        """
        Tres estados con diferentes posiciones o estados de puerta deben producir
        firmas y claves diferenciadas.
        """
        goal = Goal(conditions=(("agente", "posicion", "sala", True),))

        # Estado A: pasillo, cerrada
        kA = Kernel()
        for o, t in [("agente", "Agent"), ("puerta", "Door"), ("pasillo", "Location"), ("cerrada", "StateVal"), ("abierta", "StateVal"), ("sala", "Location")]:
            kA.transition(Transition("add_object", {"id": o, "type": t}))
        kA.transition(Transition("add_relation", {"id": "r1", "source": "agente", "predicate": "posicion", "target": "pasillo"}))
        kA.transition(Transition("add_relation", {"id": "r2", "source": "puerta", "predicate": "estado", "target": "cerrada"}))

        # Estado B: sala, cerrada
        kB = Kernel()
        for o, t in [("agente", "Agent"), ("puerta", "Door"), ("pasillo", "Location"), ("cerrada", "StateVal"), ("abierta", "StateVal"), ("sala", "Location")]:
            kB.transition(Transition("add_object", {"id": o, "type": t}))
        kB.transition(Transition("add_relation", {"id": "r1", "source": "agente", "predicate": "posicion", "target": "sala"}))
        kB.transition(Transition("add_relation", {"id": "r2", "source": "puerta", "predicate": "estado", "target": "cerrada"}))

        # Estado C: pasillo, abierta
        kC = Kernel()
        for o, t in [("agente", "Agent"), ("puerta", "Door"), ("pasillo", "Location"), ("cerrada", "StateVal"), ("abierta", "StateVal"), ("sala", "Location")]:
            kC.transition(Transition("add_object", {"id": o, "type": t}))
        kC.transition(Transition("add_relation", {"id": "r1", "source": "agente", "predicate": "posicion", "target": "pasillo"}))
        kC.transition(Transition("add_relation", {"id": "r2", "source": "puerta", "predicate": "estado", "target": "abierta"}))

        sigA = self.builder.build_context_signature(kA.state, goal)
        sigB = self.builder.build_context_signature(kB.state, goal)
        sigC = self.builder.build_context_signature(kC.state, goal)

        print("\n=== TEST 2: Diferenciabilidad de Estados ===")
        print(f"Estado A (pasillo, cerrada): {sigA.exact_key}")
        print(f"Estado B (sala, cerrada):    {sigB.exact_key}")
        print(f"Estado C (pasillo, abierta): {sigC.exact_key}")

        self.assertNotEqual(sigA.exact_key, sigB.exact_key)
        self.assertNotEqual(sigA.exact_key, sigC.exact_key)
        self.assertNotEqual(sigB.exact_key, sigC.exact_key)

    def test_3_sensibilidad_al_objetivo(self):
        """
        El mismo estado físico exacto, pero evaluado bajo dos objetivos diferentes,
        debe producir firmas y claves distintas.
        """
        k = Kernel()
        for o, t in [("agente", "Agent"), ("puerta", "Door"), ("pasillo", "Location"), ("sala", "Location"), ("deposito", "Location"), ("cerrada", "StateVal"), ("abierta", "StateVal")]:
            k.transition(Transition("add_object", {"id": o, "type": t}))
        k.transition(Transition("add_relation", {"id": "r1", "source": "agente", "predicate": "posicion", "target": "pasillo"}))

        goal_1 = Goal(conditions=(("agente", "posicion", "sala", True),))
        goal_2 = Goal(conditions=(("agente", "posicion", "deposito", True),))

        sig1 = self.builder.build_context_signature(k.state, goal_1)
        sig2 = self.builder.build_context_signature(k.state, goal_2)

        print("\n=== TEST 3: Sensibilidad al Objetivo ===")
        print(f"Goal 1 (ir a sala):     {sig1.exact_key}")
        print(f"Goal 2 (ir a deposito): {sig2.exact_key}")

        self.assertNotEqual(sig1.exact_key, sig2.exact_key)
        self.assertNotEqual(sig1.structural_key, sig2.structural_key)

    def test_4_sensibilidad_a_acciones_aplicables(self):
        """
        Verifica que exact_key distinga estados donde las acciones aplicables difieren,
        mientras structural_key conserve la identidad base del estado físico+meta.
        """
        k = Kernel()
        for o, t in [("agente", "Agent"), ("puerta", "Door"), ("pasillo", "Location"), ("sala", "Location"), ("deposito", "Location"), ("cerrada", "StateVal"), ("abierta", "StateVal")]:
            k.transition(Transition("add_object", {"id": o, "type": t}))
        k.transition(Transition("add_relation", {"id": "r1", "source": "agente", "predicate": "posicion", "target": "pasillo"}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "puerta", "predicate": "estado", "target": "cerrada"}))

        goal = Goal(conditions=(("agente", "posicion", "sala", True),))

        act_abrir = Action(name="abrir_puerta", preconditions=(("puerta", "estado", "cerrada", True),))
        act_entrar = Action(name="entrar", preconditions=(("puerta", "estado", "abierta", True),))

        # En estado actual: solo act_abrir es aplicable
        sig_one_act = self.builder.build_context_signature(k.state, goal, available_actions=[act_abrir, act_entrar])
        # Si no pasamos acciones aplicables:
        sig_no_acts = self.builder.build_context_signature(k.state, goal, available_actions=[])

        print("\n=== TEST 4: Sensibilidad a Acciones Aplicables ===")
        print(f"Con acciones aplicables: {sig_one_act.exact_key} | Acts: {sig_one_act.applicable_actions}")
        print(f"Sin acciones:            {sig_no_acts.exact_key} | Acts: {sig_no_acts.applicable_actions}")

        self.assertEqual(sig_one_act.applicable_actions, ("abrir_puerta",))
        self.assertEqual(sig_no_acts.applicable_actions, ())
        self.assertNotEqual(sig_one_act.exact_key, sig_no_acts.exact_key)
        # Ambas comparten el mismo structural_key porque el estado físico y objetivo son idénticos
        self.assertEqual(sig_one_act.structural_key, sig_no_acts.structural_key)

    def test_5_serializacion_y_reconstruccion_json(self):
        """
        La firma debe ser serializable a JSON y reconstruible exactamente.
        """
        k = Kernel()
        for o, t in [("agente", "Agent"), ("pasillo", "Location"), ("sala", "Location")]:
            k.transition(Transition("add_object", {"id": o, "type": t}))
        k.transition(Transition("add_relation", {"id": "r1", "source": "agente", "predicate": "posicion", "target": "pasillo"}))
        goal = Goal(conditions=(("agente", "posicion", "sala", True),))

        sig = self.builder.build_context_signature(k.state, goal, domain_hint="facility")
        d = sig.to_dict()
        json_str = json.dumps(d)
        data_loaded = json.loads(json_str)
        sig_rebuilt = ContextSignature.from_dict(data_loaded)

        print("\n=== TEST 5: Serialización JSON ===")
        print(f"JSON Payload: {json_str}")

        self.assertEqual(sig, sig_rebuilt)
        self.assertEqual(sig.exact_key, sig_rebuilt.exact_key)
        self.assertEqual(sig.domain_hint, "facility")

    def test_6_integracion_en_active_context(self):
        """
        Verifica que build_context retorne un ActiveContext con su signature integrada.
        """
        k = Kernel()
        for o, t in [("agente", "Agent"), ("pasillo", "Location"), ("sala", "Location")]:
            k.transition(Transition("add_object", {"id": o, "type": t}))
        k.transition(Transition("add_relation", {"id": "r1", "source": "agente", "predicate": "posicion", "target": "pasillo"}))
        goal = Goal(conditions=(("agente", "posicion", "sala", True),))

        ctx = self.builder.build_context(k.state, goal)

        self.assertIsNotNone(ctx.signature)
        self.assertTrue(ctx.signature.exact_key.startswith("CTX_EXT_"))
        self.assertTrue(ctx.signature.structural_key.startswith("CTX_STR_"))
        print("\n=== TEST 6: ActiveContext Integration ===")
        print(f"ActiveContext Signature: {ctx.signature.summary()}")


if __name__ == "__main__":
    unittest.main()
