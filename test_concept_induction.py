"""
test_concept_induction.py — Pruebas de Abstracción Conceptual e Inducción de Tipos.
Verifica:
  1. Caso Canónico: Juan, Pedro, María están en A -> Inducción autónoma de clases Sujeto/Objeto.
  2. Reificación Ontológica en MF_MIN: Integración atómica respetando invariantes I1-I6.
  3. Generalización Cruzada en EngineD: Propagación deductiva de tipos ante nuevas entidades.
  4. Discriminación: Entidades sin afinidad relacional no se colapsan erróneamente.
"""
from __future__ import annotations
import unittest

from mf_min_definitivo import (
    Kernel, Transition, Object, Relation, State,
    ContradictionError, ValidationError
)
from engine_d import EngineD, Rule, Pattern
from concept_induction import ConceptInductionEngine, ConceptHypothesis


class TestConceptInduction(unittest.TestCase):

    def setUp(self):
        self.engine = ConceptInductionEngine(min_support=2, default_min_confidence=0.5)

    def test_1_caso_canonico_juan_pedro_maria_en_a(self):
        """
        Escenario central de la asesoría:
        Entidades concretas: juan, pedro, maria, A.
        Relaciones: juan está_en A, pedro está_en A, maría está_en A.
        El sistema debe:
        - Detectar que juan, pedro, maría comparten rol activo en 'esta_en'.
        - Inducir Concept_esta_en_Actor (Sujeto / Agente) y Concept_esta_en_Target (Lugar).
        - Reificar en el Kernel las relaciones 'instancia_de' y el esquema abstracto.
        """
        k = Kernel()
        for ind in ["juan", "pedro", "maria"]:
            k.transition(Transition("add_object", {"id": ind, "type": "Individuo"}))
        k.transition(Transition("add_object", {"id": "A", "type": "EntidadFisica"}))

        k.transition(Transition("add_relation", {"id": "r1", "source": "juan", "predicate": "esta_en", "target": "A", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "pedro", "predicate": "esta_en", "target": "A", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r3", "source": "maria", "predicate": "esta_en", "target": "A", "origin": "asserted"}))

        print("\n=== TEST 1: Inducción Conceptual del Caso Canónico ===")
        # 1. Inducción de hipótesis conceptuales
        hypotheses = self.engine.induce_concepts(k)
        for h in hypotheses:
            print(f"-> {h.summary()}")

        self.assertEqual(len(hypotheses), 2)
        h_actor = next(h for h in hypotheses if h.role_type == "subject_cluster")
        h_target = next(h for h in hypotheses if h.role_type == "object_cluster")

        self.assertEqual(h_actor.instances, {"juan", "pedro", "maria"})
        self.assertEqual(h_target.instances, {"A"})
        self.assertEqual(h_actor.status, "VALIDATED")
        self.assertEqual(h_target.status, "VALIDATED")

        # 2. Compromiso atómico en el Kernel
        trans_committed = self.engine.commit_concepts(hypotheses, k)
        print(f"-> Transiciones atómicas comprometidas en Kernel: {len(trans_committed)}")

        # Verificación en el Kernel:
        # Objetos abstractos creados en O:
        self.assertIn("Concept_esta_en_Actor", k.state.objects)
        self.assertIn("Concept_esta_en_Target", k.state.objects)
        self.assertEqual(k.state.objects["Concept_esta_en_Actor"].type, "AbstractConcept")

        # Relaciones de membresía en M:
        ed = EngineD(k)
        self.assertEqual(ed.query_evidence("juan", "instancia_de", "Concept_esta_en_Actor"), "TRUE")
        self.assertEqual(ed.query_evidence("pedro", "instancia_de", "Concept_esta_en_Actor"), "TRUE")
        self.assertEqual(ed.query_evidence("maria", "instancia_de", "Concept_esta_en_Actor"), "TRUE")
        self.assertEqual(ed.query_evidence("A", "instancia_de", "Concept_esta_en_Target"), "TRUE")

        # Esquema abstracto de orden superior: (Concept_esta_en_Actor está_en Concept_esta_en_Target)
        self.assertEqual(ed.query_evidence("Concept_esta_en_Actor", "esta_en", "Concept_esta_en_Target"), "TRUE")
        print("-> Reificación ontológica formal verificada con 100% de consistencia en Kernel.")

    def test_2_generalizacion_deductiva_cruzada_con_engine_d(self):
        """
        Verifica la cooperación entre Inducción Conceptual y Deducción Formal:
        Una vez inducidos los conceptos y sus meta-reglas de tipificación:
        Si ingresa una nueva entidad 'carlos' que 'esta_en' 'B', y afirmamos que 'carlos'
        es un Concept_esta_en_Actor, EngineD deduce formalmente que 'B' es un Concept_esta_en_Target.
        """
        k = Kernel()
        for ind in ["juan", "pedro"]:
            k.transition(Transition("add_object", {"id": ind, "type": "Individuo"}))
        k.transition(Transition("add_object", {"id": "A", "type": "Lugar"}))

        k.transition(Transition("add_relation", {"id": "r1", "source": "juan", "predicate": "esta_en", "target": "A", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "pedro", "predicate": "esta_en", "target": "A", "origin": "asserted"}))

        # Inducir conceptos y comprometerlos
        hypotheses = self.engine.induce_concepts(k)
        self.engine.commit_concepts(hypotheses, k)

        # Generar meta-reglas de propagación de tipo para EngineD
        type_rules = self.engine.generate_type_propagation_rules(hypotheses)
        print("\n=== TEST 2: Generalización Deductiva Cruzada con EngineD ===")
        for r in type_rules:
            print(f"-> Meta-Regla generada: {r.name}")

        self.assertGreater(len(type_rules), 0)

        # Nuevas entidades no vistas antes: carlos y B
        k.transition(Transition("add_object", {"id": "carlos", "type": "Individuo"}))
        k.transition(Transition("add_object", {"id": "B", "type": "Lugar"}))
        k.transition(Transition("add_relation", {"id": "r_cb", "source": "carlos", "predicate": "esta_en", "target": "B", "origin": "asserted"}))
        # Se informa que carlos es un Actor de esta_en
        k.transition(Transition("add_relation", {
            "id": "r_carlos_type",
            "source": "carlos",
            "predicate": "instancia_de",
            "target": "Concept_esta_en_Actor",
            "origin": "asserted"
        }))

        ed = EngineD(k)
        # Antes de saturar: no sabemos qué es B
        self.assertEqual(ed.query_evidence("B", "instancia_de", "Concept_esta_en_Target"), "UNKNOWN")

        # Saturar con las meta-reglas inducidas
        new_facts = ed.saturate(type_rules)
        print(f"-> Hechos deducidos por propagación de tipos: {new_facts}")

        # EngineD dedujo automáticamente que B es un Concept_esta_en_Target
        self.assertEqual(ed.query_evidence("B", "instancia_de", "Concept_esta_en_Target"), "TRUE")
        rel_b = next(r for r in k.state.relations.values() if r.source == "B" and r.target == "Concept_esta_en_Target")
        self.assertEqual(rel_b.origin, "derived")
        print(f"-> Deducción confirmada: 'B' es formalmente instancia de '{rel_b.target}' (Procedencia: {rel_b.rule_id})")

    def test_3_discriminacion_de_entidades_con_firmas_divergentes(self):
        """
        Verifica que entidades que realizan acciones diferentes NO se colapsen en la misma clase:
        juan y pedro 'programan'; ana y maria 'gestionan'.
        Deben formarse conceptos independientes para cada rol funcional.
        """
        k = Kernel()
        for p in ["juan", "pedro", "ana", "maria"]:
            k.transition(Transition("add_object", {"id": p, "type": "Empleado"}))
        for t in ["tarea_codigo", "tarea_agenda"]:
            k.transition(Transition("add_object", {"id": t, "type": "Tarea"}))

        k.transition(Transition("add_relation", {"id": "r1", "source": "juan", "predicate": "programa", "target": "tarea_codigo", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "pedro", "predicate": "programa", "target": "tarea_codigo", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r3", "source": "ana", "predicate": "gestiona", "target": "tarea_agenda", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r4", "source": "maria", "predicate": "gestiona", "target": "tarea_agenda", "origin": "asserted"}))

        hypotheses = self.engine.induce_concepts(k)
        print("\n=== TEST 3: Discriminación de Firmas Divergentes ===")
        for h in hypotheses:
            print(f"-> {h.summary()}")

        # Deben existir 4 conceptos: Programa_Actor, Programa_Target, Gestiona_Actor, Gestiona_Target
        actor_concepts = [h for h in hypotheses if h.role_type == "subject_cluster"]
        self.assertEqual(len(actor_concepts), 2)
        
        c_prog = next(h for h in actor_concepts if h.inducing_predicate == "programa")
        c_gest = next(h for h in actor_concepts if h.inducing_predicate == "gestiona")

        self.assertEqual(c_prog.instances, {"juan", "pedro"})
        self.assertEqual(c_gest.instances, {"ana", "maria"})
        print("-> Discriminación estricta verificada: ninguna clase mezcló entidades con roles dispares.")


if __name__ == "__main__":
    unittest.main()
