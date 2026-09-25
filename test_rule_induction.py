"""
test_rule_induction.py — Pruebas de Inducción Estructural y Autoconstrucción de Reglas.
Verifica:
  1. Descubrimiento autónomo de transitividad abstracta (A ∈ B ∈ C ∈ D => A ∈ D).
  2. Discriminación estricta ante contraejemplos (rechazo de relaciones intransitivas).
  3. Respeto absoluto a los axiomas formales del Kernel (invariante I5).
  4. Descubrimiento autónomo de relaciones simétricas.
"""
from __future__ import annotations
import unittest

from mf_min_definitivo import (
    Kernel, Transition, Object, Relation, State,
    ContradictionError, ValidationError, Clause, AxiomConstraint
)
from engine_d import EngineD, Rule, Pattern
from rule_induction import RuleHypothesis, RuleInductionEngine


class TestRuleInduction(unittest.TestCase):

    def setUp(self):
        self.engine_induction = RuleInductionEngine(default_min_confidence=0.5)

    def test_1_induccion_transitividad_abstracta_completa(self):
        """
        Demostración del objetivo central:
        A partir de hechos no logísticos (A pertenece a B, B pertenece a C, C pertenece a D),
        el sistema detecta el patrón relacional, propone la regla de transitividad,
        la audita formalmente en un Kernel efímero, la promueve a EngineD,
        y deduce deterministamente que A pertenece a D con procedencia demostrable.
        """
        k = Kernel()
        for nodo in ["A", "B", "C", "D"]:
            k.transition(Transition("add_object", {"id": nodo, "type": "Concepto"}))

        k.transition(Transition("add_relation", {"id": "r1", "source": "A", "predicate": "pertenece", "target": "B", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "B", "predicate": "pertenece", "target": "C", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r3", "source": "C", "predicate": "pertenece", "target": "D", "origin": "asserted"}))

        ed = EngineD(k)

        # 1. Antes de la inducción: EngineD no sabe nada de transitividad
        self.assertEqual(ed.query_evidence("A", "pertenece", "D"), "UNKNOWN")
        self.assertEqual(ed.saturate([]), 0)

        # 2. Ciclo de Inducción Estructural
        hypotheses, new_facts = self.engine_induction.induce_and_saturate(k, ed)

        print("\n=== TEST 1: Inducción de Transitividad Abstracta ===")
        for h in hypotheses:
            print(f"-> {h.summary()}")
        print(f"-> Nuevos hechos derivados formalmente: {new_facts}")

        # Se debe haber inducido exactamente 1 regla de transitividad
        self.assertEqual(len(hypotheses), 1)
        hyp = hypotheses[0]
        self.assertEqual(hyp.schema_type, "transitivity")
        self.assertEqual(hyp.predicate, "pertenece")
        self.assertEqual(hyp.status, "VALIDATED")
        self.assertGreater(hyp.confidence, 0.5)

        # 3. Verificación de las deducciones en el Kernel
        # La cadena A -> B -> C -> D produce 3 nuevos hechos: (A, C), (B, D), (A, D)
        self.assertEqual(new_facts, 3)
        self.assertEqual(ed.query_evidence("A", "pertenece", "D"), "TRUE")
        self.assertEqual(ed.query_evidence("A", "pertenece", "C"), "TRUE")
        self.assertEqual(ed.query_evidence("B", "pertenece", "D"), "TRUE")

        # 4. Auditoría de Procedencia e Invariante I2:
        # El hecho derivado A -> D debe portar origin='derived', rule_id de la regla inducida, y premisas válidas
        rel_ad = next(r for r in k.state.relations.values() if r.source == "A" and r.target == "D")
        self.assertEqual(rel_ad.origin, "derived")
        self.assertEqual(rel_ad.rule_id, "ind_trans_pertenece")
        self.assertTrue(len(rel_ad.premises) > 0)
        print(f"-> Trazabilidad confirmada: Hecho {rel_ad.id} derivado mediante regla '{rel_ad.rule_id}' con premisas {rel_ad.premises}")

    def test_2_discriminacion_ante_contraejemplo_negativo(self):
        """
        Verifica que el sistema NO sobregeneralice:
        Si una relación tiene una cadena estructural (P1 padre_de P2, P2 padre_de P3),
        pero se sabe explícitamente que P1 NO es padre_de P3 (evidencia negativa polarity=False),
        la hipótesis de transitividad es RECHAZADA inmediatamente.
        """
        k = Kernel()
        for p in ["P1", "P2", "P3"]:
            k.transition(Transition("add_object", {"id": p, "type": "Persona"}))

        k.transition(Transition("add_relation", {"id": "r1", "source": "P1", "predicate": "padre_de", "target": "P2", "origin": "asserted", "polarity": True}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "P2", "predicate": "padre_de", "target": "P3", "origin": "asserted", "polarity": True}))
        
        # Hecho negativo explícito: P1 NO es padre_de P3 (es su abuelo)
        k.transition(Transition("add_relation", {"id": "r_contra", "source": "P1", "predicate": "padre_de", "target": "P3", "origin": "asserted", "polarity": False}))

        ed = EngineD(k)
        hypotheses = self.engine_induction.induce_rules(k)

        print("\n=== TEST 2: Discriminación ante Contraejemplo Negativo ===")
        print(f"-> Hipótesis generadas y validadas: {len(hypotheses)}")
        
        # Ninguna regla debe haber sido validada
        self.assertEqual(len(hypotheses), 0)

        # Si inspeccionamos manualmente la hipótesis rechazada:
        raw_candidates = self.engine_induction.mine_transitivity_candidates(k.state)
        self.assertEqual(len(raw_candidates), 1)
        evaluated = self.engine_induction.audit_and_evaluate(raw_candidates[0], k)
        print(f"-> Resultado de auditoría: {evaluated.summary()}")
        self.assertEqual(evaluated.status, "REJECTED")
        self.assertEqual(evaluated.counterexamples_count, 1)
        self.assertEqual(evaluated.confidence, 0.0)

    def test_3_seguridad_contra_violacion_axiomatica_del_kernel(self):
        """
        Verifica que si una hipótesis violaría un axioma formal declarado en el Kernel,
        la simulación seca (dry-run) detecte la violación y RECHACE la hipótesis sin
        corromper el Kernel real.
        """
        k = Kernel()
        for o in ["X", "Y"]:
            k.transition(Transition("add_object", {"id": o, "type": "Nodo"}))

        # Axioma: Ninguna relación 'desigual' puede vincular un objeto consigo mismo (irreflexividad)
        # Clausula: si desigual(?A, ?B) y ?A == ?B -> CONTRADICCION
        k.transition(Transition("add_axiom", {
            "id": "ax_irreflexivo",
            "name": "Irreflexividad estricta de desigual",
            "body": (
                {"predicate": "desigual", "source": "?A", "target": "?A", "polarity": True},
            )
        }))

        # Hechos: X desigual Y, Y desigual X
        k.transition(Transition("add_relation", {"id": "r1", "source": "X", "predicate": "desigual", "target": "Y", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "Y", "predicate": "desigual", "target": "X", "origin": "asserted"}))

        # Si intentáramos aplicar transitividad: X desigual Y ∧ Y desigual X => X desigual X (viola axioma)
        raw_candidates = self.engine_induction.mine_transitivity_candidates(k.state)
        self.assertEqual(len(raw_candidates), 1)

        evaluated = self.engine_induction.audit_and_evaluate(raw_candidates[0], k)
        print("\n=== TEST 3: Seguridad contra Violación Axiomática ===")
        print(f"-> Resultado de auditoría: {evaluated.summary()}")
        self.assertEqual(evaluated.status, "REJECTED")
        self.assertEqual(evaluated.confidence, 0.0)
        self.assertGreater(evaluated.counterexamples_count, 0)

        # El Kernel real permanece completamente íntegro y sin relaciones ilegales
        self.assertEqual(len(k.state.relations), 2)

    def test_4_induccion_de_simetria(self):
        """
        Verifica el descubrimiento y promoción de relaciones simétricas:
        Si N1 y N2 son vecinos_de mutuamente, y se observa que N3 es vecino_de N4,
        el motor induce que vecino_de es simétrica y deduce que N4 es vecino_de N3.
        """
        k = Kernel()
        for n in ["N1", "N2", "N3", "N4"]:
            k.transition(Transition("add_object", {"id": n, "type": "Casa"}))

        # Par simétrico observado
        k.transition(Transition("add_relation", {"id": "r1", "source": "N1", "predicate": "vecino_de", "target": "N2", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "N2", "predicate": "vecino_de", "target": "N1", "origin": "asserted"}))
        # Par unidireccional nuevo
        k.transition(Transition("add_relation", {"id": "r3", "source": "N3", "predicate": "vecino_de", "target": "N4", "origin": "asserted"}))

        ed = EngineD(k)
        hypotheses, new_facts = self.engine_induction.induce_and_saturate(k, ed)

        print("\n=== TEST 4: Inducción de Simetría ===")
        for h in hypotheses:
            print(f"-> {h.summary()}")
        print(f"-> Nuevos hechos derivados: {new_facts}")

        # Se induce simetría
        symm_hyp = next((h for h in hypotheses if h.schema_type == "symmetry"), None)
        self.assertIsNotNone(symm_hyp)
        self.assertEqual(symm_hyp.status, "VALIDATED")

        # N4 vecino_de N3 ahora es TRUE
        self.assertEqual(ed.query_evidence("N4", "vecino_de", "N3"), "TRUE")


if __name__ == "__main__":
    unittest.main()
