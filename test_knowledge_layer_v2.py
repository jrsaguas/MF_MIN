"""
test_knowledge_layer_v2.py - Pruebas de integración para la Capa de Conocimiento y Evaluación Epistemológica.
"""
import unittest
from knowledge import Entity, Claim, Evidence, EpistemicStatus
from knowledge_store import KnowledgeStore
from epistemic import EpistemicEvaluator
from universal_io import KnowledgeArtifact
from knowledge_codec import TextCodec, LatexCodec, UniversalCodecRegistry
from semantic_bridge import SemanticBridge
from retrieval_indexed import IndexedRetriever
from mf_min_definitivo import Kernel, Transition

class TestKnowledgeLayer(unittest.TestCase):

    def test_knowledge_store_indexing_and_deduplication(self):
        store = KnowledgeStore()
        e1 = Entity(id="juan", type="Person", label="Juan")
        e2 = Entity(id="sala", type="Room", label="Sala")
        store.add_entity(e1)
        store.add_entity(e2)

        c1 = Claim(subject="juan", predicate="esta_en", object="sala", polarity=True)
        store.add_claim(c1)

        # Re-agregar el mismo hecho con nueva evidencia
        ev2 = Evidence(id="ev_camara", source="camara", reliability=0.95)
        c2 = Claim(subject="juan", predicate="esta_en", object="sala", polarity=True, evidences=[ev2])
        merged = store.add_claim(c2)

        self.assertEqual(len(store.claims), 1)
        self.assertEqual(len(merged.evidences), 1)
        # Consulta O(1)
        res = store.query_claims(subject="juan", predicate="esta_en")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].object, "sala")

    def test_epistemic_contradiction_preservation(self):
        """Verifica que las contradicciones se detecten y conserven como conocimiento sin borrarse."""
        store = KnowledgeStore()
        evaluator = EpistemicEvaluator()

        c_pos = Claim(subject="puerta", predicate="estado", object="abierta", polarity=True)
        c_neg = Claim(subject="puerta", predicate="estado", object="abierta", polarity=False)

        store.add_claim(c_pos)
        evaluator.evaluate_claim(c_pos, store)
        self.assertEqual(c_pos.status, EpistemicStatus.ASSERTED)

        # Segunda fuente afirma lo opuesto
        store.add_claim(c_neg)
        evaluator.evaluate_claim(c_neg, store)

        self.assertEqual(c_pos.status, EpistemicStatus.CONTRADICTED)
        self.assertEqual(c_neg.status, EpistemicStatus.CONTRADICTED)
        # Ambos claims se conservan
        self.assertEqual(len(store.claims), 2)
        self.assertEqual(len(store.find_conflicts()), 1)

    def test_universal_codec_latex_and_text(self):
        registry = UniversalCodecRegistry()
        
        # Prueba texto
        art_txt = KnowledgeArtifact("1", "text/plain", "general", "La persona está en la sala.")
        frame_txt = registry.decode_artifact(art_txt)
        self.assertEqual(len(frame_txt.relations), 1)
        self.assertEqual(frame_txt.relations[0]["predicate"], "esta_en")

        # Prueba LaTeX
        art_latex = KnowledgeArtifact("2", "application/x-latex", "mathematics", "f(x) = x^2 + 1")
        frame_latex = registry.decode_artifact(art_latex)
        self.assertEqual(len(frame_latex.relations), 2)
        encoded_latex = registry.encode_to_artifact(frame_latex, "application/x-latex")
        self.assertEqual(encoded_latex.content, "f(x) = x^2 + 1")

    def test_indexed_retrieval(self):
        store = KnowledgeStore()
        c1 = Claim(subject="servidor", predicate="ubicacion", object="sala_rack", polarity=True)
        c2 = Claim(subject="servidor", predicate="estado", object="encendido", polarity=True)
        store.add_claim(c1)
        store.add_claim(c2)

        retriever = IndexedRetriever(store)
        results = retriever.query_hierarchical("donde esta el rack del servidor", subject="servidor")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][1].object, "sala_rack")

if __name__ == "__main__":
    unittest.main()
