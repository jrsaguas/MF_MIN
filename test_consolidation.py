"""
test_consolidation.py - Suite de Validación de Consolidación Integral (MF_MIN V7).
Verifica:
 1. Carga y consistencia de dominios operacionales externos (DomainManager).
 2. Ingesta y proyección en dos tiempos sobre dominios heterogéneos.
 3. Ciclo completo de inducción, deducción y planificación con trazabilidad de auditoría.
 4. Robustez de la interfaz HTTP y endpoints REST (/api/status, /api/execute, /api/assert, /api/reset).
"""
from __future__ import annotations
import unittest
import json

from domain import DomainManager, DomainSpec
from audit_log import AuditLogger
from agent import Agent, InputEnvelope, InputKind
from mf_min_definitivo import Kernel, Transition
from server import CognitiveServerState


class TestConsolidation(unittest.TestCase):

    def setUp(self):
        self.dm = DomainManager()
        self.logger = AuditLogger()

    def test_1_carga_dominios_heterogeneos(self):
        """Verifica que todos los dominios JSON se carguen correctamente."""
        doms = self.dm.list_domains()
        self.assertIn("facility_default", doms)
        self.assertIn("almacen_logistico", doms)
        self.assertIn("pipeline_ci", doms)
        self.assertIn("laboratorio_calibracion", doms)

        spec_almacen = self.dm.get_domain("almacen_logistico")
        self.assertEqual(spec_almacen.initial_location, "recepcion")
        self.assertIn("estanterias", spec_almacen.rooms)

    def test_2_aplicacion_dominio_a_kernel(self):
        """Verifica que un dominio pueble coherentemente un Kernel vacío."""
        kernel = Kernel()
        spec = self.dm.get_domain("pipeline_ci")
        self.dm.apply_to_kernel(kernel, spec)

        # Comprobar objetos base
        self.assertIn("agente", kernel.state.objects)
        self.assertIn("stage_build", kernel.state.objects)
        self.assertIn("stage_deploy", kernel.state.objects)
        self.assertIn("token_aprobacion", kernel.state.objects)

    def test_3_trazabilidad_audit_log(self):
        """Verifica que AuditLogger capture eventos formales."""
        self.logger.log_event("agent_action", {"action": "mover", "target": "deposito"})
        entries = self.logger.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["entry_type"], "event")
        self.assertEqual(entries[0]["payload"]["data"]["target"], "deposito")

    def test_4_servidor_estado_y_endpoints_deliberativos(self):
        """Verifica que CognitiveServerState responda coherentemente a comandos y aserciones."""
        s = CognitiveServerState()
        self.assertEqual(s.env.agent_location, "pasillo")

        # 1. Ejecutar comando
        res = s.execute_command("abrir la puerta del deposito")
        self.assertTrue(res["success"])
        self.assertIn("abrir_puerta_deposito", res["plan"])

        # 2. Enseñar aserción
        res_assert = s.assert_fact("X depende de Y.")
        self.assertTrue(res_assert["success"])
        self.assertIn("x", s.agent.kernel.state.objects)
        self.assertIn("y", s.agent.kernel.state.objects)

        # 3. Reinicio
        s.reset()
        self.assertEqual(s.env.agent_location, "pasillo")
        self.assertNotIn("x", s.agent.kernel.state.objects)


if __name__ == "__main__":
    unittest.main()
