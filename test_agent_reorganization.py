"""
test_agent_reorganization.py — Pruebas de la Reorganización Modular de Agent (MF_MIN V7).
Verifica:
  1. Contrato de InputEnvelope y InputKind.
  2. Canal de Percepción (InputKind.PERCEPTION).
  3. Canal de Afirmaciones en Lenguaje Natural (InputKind.ASSERTION).
  4. Rechazo honesto de entradas ambiguas / ruido de teclado ("no sé").
  5. Canal de Comandos y Deliberación (InputKind.COMMAND).
  6. Emisión y trazabilidad de eventos cognitivos (CognitiveEvent).
  7. Retrocompatibilidad total con la API existente (perceive_environment, ingest_text, step, etc.).
  8. Integración E2E del Hook de Aprendizaje: Texto -> Kernel -> Evento -> RuleCandidateBuilder -> Promoción -> EngineD.
"""
from __future__ import annotations
import unittest

from agent import Agent, InputKind, InputEnvelope, AgentResponse, CognitiveEvent
from mf_min_definitivo import Kernel, Transition
from motor_c import Action, Goal


class TestAgentReorganization(unittest.TestCase):

    def setUp(self):
        self.agent = Agent()

    def test_1_canal_afirmacion_lenguaje_natural(self):
        """Verifica la ingesta declarativa universal vía receive(ASSERTION)."""
        envelope = InputEnvelope(
            kind=InputKind.ASSERTION,
            payload="A pertenece a B.",
            source="user_test"
        )
        resp = self.agent.receive(envelope)
        self.assertTrue(resp.success)
        self.assertEqual(resp.kind, InputKind.ASSERTION)
        self.assertIn("a —pertenece_a→ b", resp.detail)

        # Verificar presencia en KnowledgeStore y Kernel
        self.assertIn("a", self.agent.kernel.state.objects)
        self.assertIn("b", self.agent.kernel.state.objects)
        rel = next((r for r in self.agent.kernel.state.relations.values() if r.source == "a" and r.target == "b"), None)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.predicate, "pertenece_a")
        self.assertEqual(rel.origin, "asserted")

    def test_2_rechazo_plausibilidad_no_se(self):
        """Verifica el mecanismo de honestidad epistémica ("no sé") ante basura de teclado."""
        envelope = InputEnvelope(
            kind=InputKind.ASSERTION,
            payload="zxq wvbrt plkm",
            source="user_noise"
        )
        resp = self.agent.receive(envelope)
        self.assertFalse(resp.success)
        self.assertIn("Rechazado", resp.detail)

    def test_3_canal_percepcion_sensorial(self):
        """Verifica el canal de sensores estructurados vía receive(PERCEPTION)."""
        readings = [
            {"source": "sensor_optico", "subject": "sala", "predicate": "iluminacion", "object": "alta", "polarity": True}
        ]
        envelope = InputEnvelope(
            kind=InputKind.PERCEPTION,
            payload=readings,
            source="sensor_optico"
        )
        resp = self.agent.receive(envelope)
        self.assertTrue(resp.success)
        self.assertEqual(resp.kind, InputKind.PERCEPTION)

        # Comprobar en Kernel
        rel = next((r for r in self.agent.kernel.state.relations.values() if r.source == "sala" and r.target == "alta"), None)
        self.assertIsNotNone(rel)
        self.assertEqual(rel.predicate, "iluminacion")

    def test_4_canal_comando_deliberativo(self):
        """Verifica el canal de comandos operativos vía receive(COMMAND)."""
        # Configurar estado y acción para abrir puerta
        for obj_id, obj_type in [("persona", "Agente"), ("puerta", "Estructura"), ("cerrada", "Estado"), ("abierta", "Estado")]:
            self.agent.kernel.transition(Transition("add_object", {"id": obj_id, "type": obj_type}))
        self.agent.kernel.transition(Transition("add_relation", {"id": "r_init", "source": "puerta", "predicate": "estado", "target": "cerrada", "origin": "asserted"}))

        action_abrir = Action(
            name="abrir_puerta",
            preconditions=(("puerta", "estado", "cerrada", True),),
            effects=(
                Transition("remove_relation", {"id": "r_init"}),
                Transition("add_relation", {"id": "r_abierta", "source": "puerta", "predicate": "estado", "target": "abierta", "origin": "asserted"})
            ),
            cost=1.0
        )

        goal = Goal(
            conditions=(("puerta", "estado", "abierta", True),)
        )

        envelope = InputEnvelope(
            kind=InputKind.COMMAND,
            payload=goal,
            metadata={"available_actions": [action_abrir]}
        )
        resp = self.agent.receive(envelope)
        self.assertTrue(resp.success)
        self.assertTrue(resp.data["cycle_result"].executed)
        self.assertTrue(resp.data["cycle_result"].goal_achieved)

    def test_5_trazabilidad_eventos_cognitivos(self):
        """Verifica que el agente emita y archive eventos en event_log."""
        self.agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="X depende de Y."))
        event_types = [e.event_type for e in self.agent.event_log]
        self.assertIn("fact_asserted", event_types)
        self.assertIn("fact_committed", event_types)

    def test_6_retrocompatibilidad_apis_existentes(self):
        """Verifica que perceive_environment, ingest_text y parse_instruction funcionen sin cambios."""
        # 1. ingest_text
        resp1 = self.agent.ingest_text("Ana tiene una llave.")
        self.assertTrue(resp1.success)

        # 2. perceive_environment
        committed = self.agent.perceive_environment([
            {"source": "camara", "subject": "puerta", "predicate": "color", "object": "rojo"}
        ])
        self.assertGreaterEqual(committed, 1)

        # 3. state property
        self.assertIsInstance(self.agent.state, type(self.agent.kernel.state))

        # 4. parse_instruction (retrocompatibilidad verificada)
        resp_cmd = self.agent.parse_instruction("abrir la puerta de servidores")
        self.assertTrue(resp_cmd.success)
        self.assertEqual(resp_cmd.kind, InputKind.COMMAND)

    def test_7_integracion_completa_e2e_aprendizaje_inductivo(self):
        """
        Demostración del circuito completo:
        1. Ingesta secuencial de hechos de transitividad vía Agent.receive().
        2. Hook de aprendizaje notifica a RuleCandidateBuilder en cada hecho comprometido.
        3. El builder detecta regularidad estructural y acumula soporte.
        4. Se valida y promueve la regla candidata a Rule formal.
        5. Se registra la regla en el Agent y EngineD deduce sobre nuevos casos.
        """
        # Ingestar hechos del patrón 1
        self.agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="A pertenece a B."))
        self.agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="B pertenece a C."))
        self.agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="A pertenece a C."))

        # Ingestar hechos del patrón 2
        self.agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="X pertenece a Y."))
        self.agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="Y pertenece a Z."))
        self.agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="X pertenece a Z."))

        # Verificar que el builder capturó la hipótesis
        builder = self.agent.rule_candidate_builder
        candidates = builder.get_candidates()
        self.assertEqual(len(candidates), 1)

        cand = candidates[0]
        self.assertEqual(cand.support_count, 2)
        self.assertEqual(cand.counterexample_count, 0)

        # Promover a regla formal de EngineD
        promoted_rule = builder.promote(cand.candidate_id)
        self.assertIsNotNone(promoted_rule)
        self.agent.add_inference_rule(promoted_rule)

        # Nuevo caso que requiere deducción
        self.agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="Alfa pertenece a Beta."))
        self.agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="Beta pertenece a Gamma."))

        # Antes de deducción: Alfa pertenece a Gamma es UNKNOWN
        self.assertEqual(self.agent.engine_d.query_evidence("alfa", "pertenece_a", "gamma"), "UNKNOWN")

        # Ejecutar deducción
        nuevos_hechos = self.agent.run_deduction()
        self.assertEqual(nuevos_hechos, 1)

        # Ahora es TRUE formalmente en el Kernel
        self.assertEqual(self.agent.engine_d.query_evidence("alfa", "pertenece_a", "gamma"), "TRUE")


    def test_8_comando_lenguaje_natural_ejecucion_completa(self):
        """Verifica que parse_instruction interprete texto natural, planifique y ejecute en Kernel."""
        for oid, otype in [("puerta_servidores", "Door"), ("cerrada", "StateVal"), ("abierta", "StateVal")]:
            self.agent.kernel.transition(Transition("add_object", {"id": oid, "type": otype}))
        self.agent.kernel.transition(Transition("add_relation", {"id": "r_ps_init", "source": "puerta_servidores", "predicate": "estado", "target": "cerrada", "origin": "asserted"}))

        action_abrir = Action(
            name="abrir_puerta_servidores",
            preconditions=(("puerta_servidores", "estado", "cerrada", True),),
            effects=(
                Transition("remove_relation", {"id": "r_ps_init"}),
                Transition("add_relation", {"id": "r_ps_open", "source": "puerta_servidores", "predicate": "estado", "target": "abierta", "origin": "asserted"})
            ),
            cost=1.0
        )

        resp = self.agent.parse_instruction("abrir la puerta de servidores", available_actions=[action_abrir])
        self.assertTrue(resp.success)
        self.assertTrue(resp.data["cycle_result"].executed)
        self.assertTrue(resp.data["cycle_result"].goal_achieved)
        self.assertTrue(self.agent.kernel.state.relations["r_ps_open"].polarity)

    def test_9_comando_lenguaje_natural_rechazo_epistemico(self):
        """Verifica que comandos no reconocibles o de baja similitud sean rechazados con honestidad epistémica."""
        # 1. Ruido de teclado
        resp_ruido = self.agent.parse_instruction("zxq wvbrt plkm")
        self.assertFalse(resp_ruido.success)
        self.assertIn("Rechazado epistémicamente", resp_ruido.detail)

        # 2. Comando no relacionado (poesía / tema fuera de dominio)
        resp_ajeno = self.agent.parse_instruction("un poema sobre las constelaciones")
        self.assertFalse(resp_ajeno.success)
        self.assertIn("Rechazado epistémicamente", resp_ajeno.detail)

    def test_10_autopromocion_reglas_e_inferencia_automatica(self):
        """Verifica que el hook de aprendizaje promueva reglas automáticamente a inference_rules."""
        agent2 = Agent()
        # Ingestar patrón 1
        agent2.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="A pertenece a B."))
        agent2.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="B pertenece a C."))
        agent2.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="A pertenece a C."))

        # Ingestar patrón 2 (alcanza min_support=2)
        agent2.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="X pertenece a Y."))
        agent2.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="Y pertenece a Z."))
        agent2.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="X pertenece a Z."))

        # Verificar auto-promoción sin intervención manual
        rule_ids = [r.id for r in agent2.inference_rules]
        self.assertIn("ind_transitivity_pertenece_a", rule_ids)

        # Verificar evento emitido
        event_types = [e.event_type for e in agent2.event_log]
        self.assertIn("rule_promoted", event_types)

        # Deducción inmediata sobre nuevos hechos
        agent2.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="M pertenece a N."))
        agent2.receive(InputEnvelope(kind=InputKind.ASSERTION, payload="N pertenece a P."))
        deducidos = agent2.run_deduction()
        self.assertEqual(deducidos, 1)
        self.assertEqual(agent2.engine_d.query_evidence("m", "pertenece_a", "p"), "TRUE")


if __name__ == "__main__":
    unittest.main()
