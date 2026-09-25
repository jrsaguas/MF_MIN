"""
test_rule_candidate_builder.py — Suite de pruebas rigurosa para RuleCandidateBuilder.
Verifica los 10 requerimientos obligatorios y la prueba de extremo a extremo:
  Test 1: Observación insuficiente
  Test 2: Repetición y soporte sin duplicados
  Test 3: Generalización estructural a variables
  Test 4: Registro explícito de contraejemplos
  Test 5: Distinción entre ausencia y negación (UNKNOWN != NOT)
  Test 6: Prevención de autoalimentación circular
  Test 7: Determinismo de identidad e invarianza de orden
  Test 8: Seguridad epistémica y separación del Kernel
  Test 9: Promoción controlada a Rule
  Test 10: Integración efectiva con EngineD
  Test 11: Prueba de Extremo a Extremo completa
  Test 12: Prueba Negativa (coocurrencia vs regularidad estructural)
"""
from __future__ import annotations
import unittest

from mf_min_definitivo import Kernel, Transition, State
from engine_d import EngineD, Rule, Pattern
from rule_candidate_builder import RuleCandidateBuilder, CandidateRule, CandidateStatus


class TestRuleCandidateBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = RuleCandidateBuilder(min_support=2, min_precision=0.8)

    def test_1_observacion_insuficiente(self):
        """Test 1: Una sola instancia genera hipótesis en PROPOSED pero NO la promueve."""
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "b", "origin": "asserted"})
        self.builder.observe({"subject": "b", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})
        cands = self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})

        self.assertEqual(len(cands), 1)
        cand = cands[0]
        self.assertEqual(cand.support_count, 1)
        self.assertEqual(cand.status, CandidateStatus.PROPOSED)

        # No debe promoverse con soporte insuficiente (< 2)
        promoted = self.builder.promote(cand.candidate_id)
        self.assertIsNone(promoted)

    def test_2_repeticion_sin_duplicar(self):
        """Test 2: Dos instancias estructuralmente equivalentes aumentan support_count sin duplicar el candidate_id."""
        # Instancia 1
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "b", "origin": "asserted"})
        self.builder.observe({"subject": "b", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})

        # Instancia 2
        self.builder.observe({"subject": "x", "predicate": "pertenece_a", "object": "y", "origin": "asserted"})
        self.builder.observe({"subject": "y", "predicate": "pertenece_a", "object": "z", "origin": "asserted"})
        self.builder.observe({"subject": "x", "predicate": "pertenece_a", "object": "z", "origin": "asserted"})

        all_cands = self.builder.get_candidates()
        self.assertEqual(len(all_cands), 1, "Debe existir exactamente 1 candidato único para la transitividad de pertenece_a")
        cand = all_cands[0]
        self.assertEqual(cand.support_count, 2)
        self.assertEqual(len(cand.observations), 2)

    def test_3_generalizacion_estructural(self):
        """Test 3: La regla se formula con variables (?X, ?Y, ?Z), no con individuos concretos (a, b, c)."""
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "b", "origin": "asserted"})
        self.builder.observe({"subject": "b", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})

        cand = self.builder.get_candidates()[0]
        # Verificar que las premisas usan variables
        self.assertEqual(cand.premises[0].source, "?X")
        self.assertEqual(cand.premises[0].target, "?Y")
        self.assertEqual(cand.premises[1].source, "?Y")
        self.assertEqual(cand.premises[1].target, "?Z")
        self.assertEqual(cand.conclusion.source, "?X")
        self.assertEqual(cand.conclusion.target, "?Z")

    def test_4_registro_contraejemplo(self):
        """Test 4: Una instancia con polaridad opuesta explícita incrementa counterexample_count y no oculta la evidencia anterior."""
        # Soporte previo
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "b", "origin": "asserted"})
        self.builder.observe({"subject": "b", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})

        # Contraejemplo explícito: d->e, e->f, pero NO d->f (polarity=False)
        self.builder.observe({"subject": "d", "predicate": "pertenece_a", "object": "e", "origin": "asserted"})
        self.builder.observe({"subject": "e", "predicate": "pertenece_a", "object": "f", "origin": "asserted"})
        self.builder.observe({"subject": "d", "predicate": "pertenece_a", "object": "f", "polarity": False, "origin": "asserted"})

        cand = self.builder.get_candidates()[0]
        self.assertEqual(cand.support_count, 1)
        self.assertEqual(cand.counterexample_count, 1)
        self.assertEqual(cand.status, CandidateStatus.REJECTED)

        # No debe promoverse jamás si tiene contraejemplos
        promoted = self.builder.promote(cand.candidate_id)
        self.assertIsNone(promoted)

    def test_5_distincion_ausencia_vs_negacion(self):
        """Test 5: Si la conclusión simplemente no aparece, es UNKNOWN y NO incrementa counterexamples."""
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "b", "origin": "asserted"})
        self.builder.observe({"subject": "b", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})
        # No se dice nada sobre a->c

        all_cands = self.builder.get_candidates()
        # No hay conclusión, no hay contraejemplo
        for c in all_cands:
            self.assertEqual(c.counterexample_count, 0)

    def test_6_no_autoalimentacion_circular(self):
        """Test 6: Hechos con origin='derived' son ignorados y no aumentan evidencia independiente primaria."""
        # Un hecho derivado por una regla previa
        cands = self.builder.observe({
            "subject": "a", "predicate": "pertenece_a", "object": "c",
            "origin": "derived", "rule_id": "rule_previa"
        })
        self.assertEqual(len(cands), 0)
        self.assertEqual(len(self.builder.get_candidates()), 0)

    def test_7_determinismo_invarianza_orden(self):
        """Test 7: La misma secuencia de hechos en diferente orden produce el mismo candidate_id."""
        b1 = RuleCandidateBuilder()
        b2 = RuleCandidateBuilder()

        # Orden 1: premisas luego conclusión
        b1.observe({"subject": "a", "predicate": "pertenece_a", "object": "b", "origin": "asserted"})
        b1.observe({"subject": "b", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})
        b1.observe({"subject": "a", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})

        # Orden 2: conclusión primero, luego premisas
        b2.observe({"subject": "a", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})
        b2.observe({"subject": "a", "predicate": "pertenece_a", "object": "b", "origin": "asserted"})
        b2.observe({"subject": "b", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})

        c1 = b1.get_candidates()[0]
        c2 = b2.get_candidates()[0]
        self.assertEqual(c1.candidate_id, c2.candidate_id)
        self.assertEqual(c1.pattern_type, c2.pattern_type)

    def test_8_separacion_kernel(self):
        """Test 8: RuleCandidateBuilder observa hechos pero nunca muta directamente el Kernel."""
        k = Kernel()
        for nodo in ["A", "B", "C"]:
            k.transition(Transition("add_object", {"id": nodo, "type": "Concepto"}))
        k.transition(Transition("add_relation", {"id": "r1", "source": "A", "predicate": "pertenece_a", "target": "B", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "B", "predicate": "pertenece_a", "target": "C", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r3", "source": "A", "predicate": "pertenece_a", "target": "C", "origin": "asserted"}))

        initial_relations = len(k.state.relations)
        
        # Builder observa
        for r in k.state.relations.values():
            self.builder.observe({"subject": r.source, "predicate": r.predicate, "object": r.target, "origin": r.origin})

        # El Kernel no cambió en absoluto
        self.assertEqual(len(k.state.relations), initial_relations)

    def test_9_promocion_controlada(self):
        """Test 9: Una candidata no validada NO se convierte en Rule; una que cumple criterios SÍ se convierte en Rule."""
        # 1 instancia: insuficiente
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "b", "origin": "asserted"})
        self.builder.observe({"subject": "b", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})

        cand = self.builder.get_candidates()[0]
        self.assertIsNone(self.builder.promote(cand.candidate_id))

        # 2da instancia: suficiente y consistente
        self.builder.observe({"subject": "x", "predicate": "pertenece_a", "object": "y", "origin": "asserted"})
        self.builder.observe({"subject": "y", "predicate": "pertenece_a", "object": "z", "origin": "asserted"})
        self.builder.observe({"subject": "x", "predicate": "pertenece_a", "object": "z", "origin": "asserted"})

        rule = self.builder.promote(cand.candidate_id)
        self.assertIsNotNone(rule)
        self.assertIsInstance(rule, Rule)
        self.assertEqual(rule.id, "ind_transitivity_pertenece_a")

    def test_10_integracion_con_engine_d(self):
        """Test 10: La regla promovida se entrega a EngineD y deduce formalmente la conclusión con procedencia."""
        # Entrenar builder con 2 instancias
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "b", "origin": "asserted"})
        self.builder.observe({"subject": "b", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})
        self.builder.observe({"subject": "a", "predicate": "pertenece_a", "object": "c", "origin": "asserted"})

        self.builder.observe({"subject": "x", "predicate": "pertenece_a", "object": "y", "origin": "asserted"})
        self.builder.observe({"subject": "y", "predicate": "pertenece_a", "object": "z", "origin": "asserted"})
        self.builder.observe({"subject": "x", "predicate": "pertenece_a", "object": "z", "origin": "asserted"})

        rule = self.builder.promote(self.builder.get_candidates()[0].candidate_id)
        self.assertIsNotNone(rule)

        # Ahora aplicar en un nuevo Kernel con cadena m -> n -> p
        k = Kernel()
        for nodo in ["M", "N", "P"]:
            k.transition(Transition("add_object", {"id": nodo, "type": "Concepto"}))
        k.transition(Transition("add_relation", {"id": "r_mn", "source": "M", "predicate": "pertenece_a", "target": "N", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r_np", "source": "N", "predicate": "pertenece_a", "target": "P", "origin": "asserted"}))

        ed = EngineD(k)
        self.assertEqual(ed.query_evidence("M", "pertenece_a", "P"), "UNKNOWN")

        # Saturar con la regla inducida
        new_facts = ed.saturate([rule])
        self.assertEqual(new_facts, 1)
        self.assertEqual(ed.query_evidence("M", "pertenece_a", "P"), "TRUE")

        # Comprobar procedencia del hecho derivado
        rel_mp = next(r for r in k.state.relations.values() if r.source == "M" and r.target == "P")
        self.assertEqual(rel_mp.origin, "derived")
        self.assertEqual(rel_mp.rule_id, "ind_transitivity_pertenece_a")
        self.assertEqual(rel_mp.premises, ("r_mn", "r_np"))

    def test_11_prueba_extremo_a_extremo(self):
        """
        Test 11 (Req 29): Secuencia completa:
        Entrada 1: 'A pertenece a B'
        Entrada 2: 'B pertenece a C'
        Entrada 3: 'A pertenece a C'
        Entrada 4: 'X pertenece a Y'
        Entrada 5: 'Y pertenece a Z'
        Entrada 6: 'X pertenece a Z'
        El sistema detecta la regularidad, formula la hipótesis, la valida, la promueve,
        y EngineD la aplica a un caso nuevo 'U pertenece a V', 'V pertenece a W' -> deduce 'U pertenece a W'.
        """
        from universal_extractor import UniversalFactExtractor

        extractor = UniversalFactExtractor()
        builder = RuleCandidateBuilder(min_support=2)

        inputs = [
            "A pertenece a B.",
            "B pertenece a C.",
            "A pertenece a C.",
            "X pertenece a Y.",
            "Y pertenece a Z.",
            "X pertenece a Z."
        ]

        for text in inputs:
            fact = extractor.extract_relation(text)
            self.assertIsNotNone(fact, f"Extractor falló en: {text}")
            builder.observe(fact)

        cands = builder.get_candidates()
        self.assertEqual(len(cands), 1)
        cand = cands[0]
        self.assertEqual(cand.support_count, 2)
        self.assertEqual(cand.counterexample_count, 0)

        # Validación
        val = builder.validate(cand.candidate_id)
        self.assertTrue(val["is_valid"])

        # Promoción
        rule = builder.promote(cand.candidate_id)
        self.assertIsNotNone(rule)

        # Aplicación deductiva con EngineD sobre caso no visto
        k = Kernel()
        for nodo in ["u", "v", "w"]:
            k.transition(Transition("add_object", {"id": nodo, "type": "Concepto"}))
        k.transition(Transition("add_relation", {"id": "r_uv", "source": "u", "predicate": "pertenece_a", "target": "v", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r_vw", "source": "v", "predicate": "pertenece_a", "target": "w", "origin": "asserted"}))

        ed = EngineD(k)
        derived = ed.saturate([rule])
        self.assertEqual(derived, 1)
        self.assertEqual(ed.query_evidence("u", "pertenece_a", "w"), "TRUE")

    def test_12_prueba_negativa_coocurrencia(self):
        """
        Test 12 (Req 30): Coocurrencia de palabras sin regularidad estructural
        (e.g., 'Ana tiene una llave', 'La llave abre una puerta')
        NO debe inventar una regla espuria como 'Ana abre la puerta' sin soporte estructural.
        """
        self.builder.observe({"subject": "ana", "predicate": "tiene", "object": "llave", "origin": "asserted"})
        self.builder.observe({"subject": "llave", "predicate": "abre", "object": "puerta", "origin": "asserted"})

        # No se ha observado que ana abre la puerta
        # Por tanto, no debe existir candidato validado para esa inferencia
        cands = self.builder.get_candidates()
        for c in cands:
            self.assertEqual(c.support_count, 0)
            self.assertNotEqual(c.status, CandidateStatus.ACCEPTED)


if __name__ == "__main__":
    unittest.main()
