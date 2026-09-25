"""
test_dominio_cero.py — Batería de Estrés de "Dominio Cero" para MF_MIN V7.
Evalúa el comportamiento de V7 frente a conocimiento completamente abstracto y no pre-programado:
  1. Transitividad abstracta: A pertenece a B, B pertenece a C, C pertenece a D.
  2. Dependencias y Causalidad: X depende de Y, Y depende de Z.
  3. Mundo de estados y precondiciones: Ana tiene una llave. La llave abre la puerta. La puerta está cerrada.
  4. Límite epistémico ("No sé"): Pregunta si X causa Y sin regla de derivación.
"""
from __future__ import annotations
import unittest

from mf_min_definitivo import (
    Kernel, Transition, Object, Relation, State,
    ContradictionError, ValidationError, MissingReferenceError,
    extract_facts_from_text
)
from engine_d import EngineD, Rule, Pattern
from knowledge import Entity, Claim, Evidence, EpistemicStatus
from knowledge_store import KnowledgeStore
from knowledge_codec import UniversalCodecRegistry, KnowledgeArtifact
from semantic_bridge import SemanticBridge
from epistemic import EpistemicEvaluator


class TestDominioCero(unittest.TestCase):

    def setUp(self):
        self.kernel = Kernel()
        self.engine = EngineD(self.kernel)
        self.store = KnowledgeStore()
        self.epistemic = EpistemicEvaluator(self.kernel)
        self.bridge = SemanticBridge(self.epistemic)
        self.registry = UniversalCodecRegistry()

    def test_caso_1_transitividad_abstracta(self):
        """
        Caso 1: A pertenece a B, B pertenece a C, C pertenece a D.
        Pregunta: ¿A pertenece a D?
        """
        texto = "A pertenece a B. B pertenece a C. C pertenece a D."
        
        # 1. Extracción en TextCodec
        art = KnowledgeArtifact("c1", "text/plain", "general", texto)
        frame = self.registry.decode_artifact(art)
        print("\n========================================================")
        print("CASO 1: TRANSITIVIDAD ABSTRACTA (A ∈ B ∈ C ∈ D)")
        print("========================================================")
        print(f"Texto: '{texto}'")
        print(f"-> TextCodec extrajo: {len(frame.relations)} relaciones")
        
        # 2. Extracción en extract_facts_from_text
        trans_prop = extract_facts_from_text(texto, self.kernel)
        print(f"-> extract_facts_from_text propuso: {len(trans_prop)} transiciones")

        # 3. Representación formal directa en Kernel MF_MIN
        k = Kernel()
        for nodo in ["A", "B", "C", "D"]:
            k.transition(Transition("add_object", {"id": nodo, "type": "Concepto"}))
        
        k.transition(Transition("add_relation", {"id": "r1", "source": "A", "predicate": "pertenece", "target": "B", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "B", "predicate": "pertenece", "target": "C", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r3", "source": "C", "predicate": "pertenece", "target": "D", "origin": "asserted"}))
        
        ed = EngineD(k)
        print(f"-> Kernel MF_MIN: {len(k.state.objects)} objetos, {len(k.state.relations)} relaciones.")
        
        # 4. Inferencia deductiva sin reglas
        derivados = ed.saturate([])
        print(f"-> EngineD sin reglas previas derivó: {derivados} nuevos hechos.")
        self.assertEqual(derivados, 0)
        
        # 5. Evidencia de la conclusión transitiva (A pertenece a D)
        ev_ad = ed.query_evidence("A", "pertenece", "D")
        print(f"-> EngineD.query_evidence('A', 'pertenece', 'D'): {ev_ad}")
        self.assertEqual(ev_ad, "UNKNOWN")

    def test_caso_2_dependencias_y_causalidad(self):
        """
        Caso 2: X depende de Y, Y depende de Z.
        Pregunta: ¿Qué relación existe entre X y Z?
        """
        texto = "X depende de Y. Y depende de Z."
        print("\n========================================================")
        print("CASO 2: DEPENDENCIAS Y CAUSALIDAD (X -> Y -> Z)")
        print("========================================================")
        print(f"Texto: '{texto}'")
        art = KnowledgeArtifact("c2", "text/plain", "general", texto)
        frame = self.registry.decode_artifact(art)
        print(f"-> TextCodec extrajo: {len(frame.relations)} relaciones")

        k = Kernel()
        for nodo in ["X", "Y", "Z"]:
            k.transition(Transition("add_object", {"id": nodo, "type": "Variable"}))
        k.transition(Transition("add_relation", {"id": "r_xy", "source": "X", "predicate": "depende_de", "target": "Y", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r_yz", "source": "Y", "predicate": "depende_de", "target": "Z", "origin": "asserted"}))

        ed = EngineD(k)
        ev_xz = ed.query_evidence("X", "depende_de", "Z")
        print(f"-> EngineD.query_evidence('X', 'depende_de', 'Z'): {ev_xz} (Honestidad Epistémica: no infiere transitividad sin regla)")
        self.assertEqual(ev_xz, "UNKNOWN")

    def test_caso_3_mundo_estados_y_precondiciones(self):
        """
        Caso 3: Ana tiene una llave. La llave abre la puerta. La puerta está cerrada.
        """
        texto = "Ana tiene una llave. La llave abre la puerta. La puerta está cerrada."
        print("\n========================================================")
        print("CASO 3: ESTADOS Y PRECONDICIONES NO LOGÍSTICAS")
        print("========================================================")
        print(f"Texto: '{texto}'")
        art = KnowledgeArtifact("c3", "text/plain", "general", texto)
        frame = self.registry.decode_artifact(art)
        print(f"-> TextCodec extrajo: {len(frame.entities)} entidades, {len(frame.relations)} relaciones")

        # Demostración del rigor de Invariante I2 en MF_MIN:
        # Si 'cerrada' se usa como relación sin ser objeto, I2 lo rechaza
        k = Kernel()
        k.transition(Transition("add_object", {"id": "ana", "type": "Persona"}))
        k.transition(Transition("add_object", {"id": "llave_1", "type": "Objeto"}))
        k.transition(Transition("add_object", {"id": "puerta_principal", "type": "Estructura"}))

        k.transition(Transition("add_relation", {"id": "r_tiene", "source": "ana", "predicate": "tiene", "target": "llave_1", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r_abre", "source": "llave_1", "predicate": "abre", "target": "puerta_principal", "origin": "asserted"}))

        try:
            k.transition(Transition("add_relation", {"id": "r_bad", "source": "puerta_principal", "predicate": "estado", "target": "cerrada", "origin": "asserted"}))
            crashes_on_i2 = False
        except MissingReferenceError:
            crashes_on_i2 = True

        print(f"-> Invariante I2 rechaza 'cerrada' como target si no fue declarada como Objeto: {crashes_on_i2}")
        self.assertTrue(crashes_on_i2)

        # Para representarla formalmente en MF_MIN, o 'cerrada' es un Objeto (estado discreto), o es una propiedad del Objeto:
        k.transition(Transition("add_object", {"id": "cerrada", "type": "Estado"}))
        k.transition(Transition("add_relation", {"id": "r_estado", "source": "puerta_principal", "predicate": "estado", "target": "cerrada", "origin": "asserted"}))
        print(f"-> Representación formal completada con 4 objetos y 3 relaciones.")
        self.assertEqual(len(k.state.objects), 4)
        self.assertEqual(len(k.state.relations), 3)

    def test_caso_4_limite_epistemico_no_se(self):
        """
        Caso 4: Límite Epistémico y "No sé"
        Dados: X asociado con Z, Z asociado con Y.
        Pregunta: ¿X causa Y?
        """
        print("\n========================================================")
        print("CASO 4: LÍMITE EPISTÉMICO Y 'NO SÉ'")
        print("========================================================")
        k = Kernel()
        for o in ["X", "Y", "Z"]:
            k.transition(Transition("add_object", {"id": o, "type": "Evento"}))
        k.transition(Transition("add_relation", {"id": "r1", "source": "X", "predicate": "asociado_con", "target": "Z", "origin": "asserted"}))
        k.transition(Transition("add_relation", {"id": "r2", "source": "Z", "predicate": "asociado_con", "target": "Y", "origin": "asserted"}))

        ed = EngineD(k)
        ev_causa = ed.query_evidence("X", "causa", "Y")
        print(f"-> EngineD.query_evidence('X', 'causa', 'Y'): {ev_causa} (MF_MIN devuelve UNKNOWN determinista)")
        self.assertEqual(ev_causa, "UNKNOWN")

        # Comprobar en KnowledgeStore y EpistemicEvaluator
        store = KnowledgeStore()
        claim_hipotesis = Claim(subject="X", predicate="causa", object="Y", polarity=True)
        store.add_claim(claim_hipotesis)
        evaluator = EpistemicEvaluator(k)
        status = evaluator.evaluate_claim(claim_hipotesis, store)
        print(f"-> EpistemicEvaluator estatus de hipótesis sin evidencias: {status.name}")
        self.assertEqual(status, EpistemicStatus.ASSERTED)
        
        # Al no tener evidencias empíricas que respalden el claim, can_promote_to_kernel con threshold estricto lo rechaza:
        promovible = evaluator.can_promote_to_kernel(claim_hipotesis, threshold=0.8)
        print(f"-> ¿Es promovible al Kernel con threshold 0.8? {promovible}")
        self.assertFalse(promovible)


if __name__ == "__main__":
    unittest.main()
