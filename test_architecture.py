"""
test_architecture.py - Batería de pruebas de integración para la arquitectura cognitiva.
Cubre Capa 1 (Kernel, reconcile, motor_c, atención básica) y Capa 2 (embeddings, QKV attention,
memoria episódica semántica, evaluación de planes, aprendizaje por refuerzo y ciclo del agente).
"""
import unittest
import numpy as np

from mf_min_definitivo import Kernel, Transition, Object, Relation, DuplicateIDError
from reconcile import Reconciler, Proposal
from motor_c import MotorC, Action, Goal, Plan
from attention import AttentionEngine, ScaledDotProductAttention, softmax
from embeddings import VectorEmbeddingEngine, cosine_similarity
from memory import Memory, EpisodicMemory
from retrieval import Retriever
from evaluation import PlanEvaluator
from learning import Learner
from agent import Agent

class TestCognitiveArchitecture(unittest.TestCase):

    def test_transition_batch_atomic(self):
        """Verifica que transition_batch() sea estrictamente atómico ante fallos."""
        k = Kernel()
        k.transition(Transition("add_object", {"id": "obj1", "type": "Item"}))
        initial_state = k.state

        # Batch con un paso válido y otro inválido (colisión de ID)
        bad_batch = [
            Transition("add_object", {"id": "obj2", "type": "Item"}),
            Transition("add_object", {"id": "obj1", "type": "Item"}) # Error
        ]

        with self.assertRaises(DuplicateIDError):
            k.transition_batch(bad_batch)

        # El estado no debe haber cambiado en lo absoluto
        self.assertEqual(k.state, initial_state)
        self.assertNotIn("obj2", k.state.objects)

    def test_reconcile_dispute(self):
        """Verifica la detección de contradicciones entre fuentes en reconcile."""
        k = Kernel()
        k.transition(Transition("add_object", {"id": "user1", "type": "Agent"}))
        k.transition(Transition("add_object", {"id": "door1", "type": "Door"}))
        rec = Reconciler(k)

        # Fuente A dice que la puerta está abierta (+), Fuente B dice que está cerrada (-)
        p1 = Proposal(
            source_id="sensor_A",
            transition=Transition("add_relation", {"id": "r1", "source": "door1", "predicate": "estado", "target": "abierta", "polarity": True})
        )
        p2 = Proposal(
            source_id="sensor_B",
            transition=Transition("add_relation", {"id": "r2", "source": "door1", "predicate": "estado", "target": "abierta", "polarity": False})
        )

        res = rec.reconcile([p1, p2])
        self.assertEqual(len(res.disputed), 2)
        self.assertEqual(len(res.committed), 0)

    def test_motor_c_plan(self):
        """Verifica que Motor C planifique correctamente encontrar la secuencia abrir -> entrar."""
        k = Kernel()
        k.transition(Transition("add_object", {"id": "persona", "type": "Agent"}))
        k.transition(Transition("add_object", {"id": "puerta", "type": "Door"}))
        k.transition(Transition("add_object", {"id": "habitacion", "type": "Room"}))
        k.transition(Transition("add_object", {"id": "cerrada", "type": "StateVal"}))
        k.transition(Transition("add_object", {"id": "abierta", "type": "StateVal"}))
        k.transition(Transition("add_object", {"id": "afuera", "type": "StateVal"}))
        k.transition(Transition("add_object", {"id": "adentro", "type": "StateVal"}))

        # Estado inicial: puerta cerrada, persona afuera
        k.transition(Transition("add_relation", {"id": "r_p_cerrada", "source": "puerta", "predicate": "estado", "target": "cerrada", "polarity": True}))
        k.transition(Transition("add_relation", {"id": "r_pers_afuera", "source": "persona", "predicate": "posicion", "target": "afuera", "polarity": True}))

        # Acciones disponibles
        abrir_puerta = Action(
            name="abrir_puerta",
            preconditions=(("puerta", "estado", "cerrada", True),),
            effects=(
                Transition("remove_relation", {"id": "r_p_cerrada"}),
                Transition("add_relation", {"id": "r_p_abierta", "source": "puerta", "predicate": "estado", "target": "abierta", "polarity": True})
            ),
            cost=1.0
        )
        entrar = Action(
            name="entrar",
            preconditions=(
                ("puerta", "estado", "abierta", True),
                ("persona", "posicion", "afuera", True)
            ),
            effects=(
                Transition("remove_relation", {"id": "r_pers_afuera"}),
                Transition("add_relation", {"id": "r_pers_adentro", "source": "persona", "predicate": "posicion", "target": "adentro", "polarity": True})
            ),
            cost=1.0
        )

        goal = Goal(conditions=(("persona", "posicion", "adentro", True),))
        motor = MotorC()
        plan = motor.plan(k.state, goal, [abrir_puerta, entrar])

        self.assertIsNotNone(plan)
        self.assertEqual(plan.action_names, ["abrir_puerta", "entrar"])
        self.assertEqual(plan.total_cost, 2.0)

    def test_motor_c_execute(self):
        """Verifica la ejecución atómica de un plan en el Kernel MF_MIN."""
        k = Kernel()
        k.transition(Transition("add_object", {"id": "puerta", "type": "Door"}))
        k.transition(Transition("add_object", {"id": "cerrada", "type": "StateVal"}))
        k.transition(Transition("add_object", {"id": "abierta", "type": "StateVal"}))
        k.transition(Transition("add_relation", {"id": "r_init", "source": "puerta", "predicate": "estado", "target": "cerrada", "polarity": True}))

        action = Action(
            name="abrir",
            preconditions=(("puerta", "estado", "cerrada", True),),
            effects=(
                Transition("remove_relation", {"id": "r_init"}),
                Transition("add_relation", {"id": "r_abierta", "source": "puerta", "predicate": "estado", "target": "abierta", "polarity": True})
            ),
            cost=1.0
        )
        plan = Plan(steps=[type('Step', (), {'action': action})], total_cost=1.0)
        motor = MotorC()
        ok = motor.execute(k, plan)

        self.assertTrue(ok)
        self.assertIn("r_abierta", k.state.relations)
        self.assertNotIn("r_init", k.state.relations)

    def test_attention_weights(self):
        """Verifica el cálculo de pesos softmax de atención."""
        attn = AttentionEngine(dim=4)
        scores = [1.0, 2.0, 3.0]
        weights = attn.compute_weights(scores)

        self.assertEqual(len(weights), 3)
        self.assertAlmostEqual(sum(weights), 1.0, places=5)
        self.assertTrue(weights[2] > weights[1] > weights[0])

    # ========================================================
    # PRUEBAS DE CAPA 2 (NUEVAS CAPACIDADES)
    # ========================================================

    def test_vector_embeddings_and_similarity(self):
        """Verifica embeddings densos y similitud semántica."""
        embedder = VectorEmbeddingEngine(dim=16)
        v1 = embedder.embed_text("abrir puerta entrar")
        v2 = embedder.embed_text("puerta abierta adentro")
        v3 = embedder.embed_text("galaxia astronomia telescopio")

        sim_12 = cosine_similarity(v1, v2)
        sim_13 = cosine_similarity(v1, v3)

        self.assertGreater(sim_12, sim_13)
        self.assertAlmostEqual(np.linalg.norm(v1), 1.0, places=4)

    def test_scaled_dot_product_attention(self):
        """Verifica la atención Q/K/V por producto punto escalado."""
        d_k = 8
        qkv = ScaledDotProductAttention(d_k=d_k)
        query = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        keys = np.array([
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # Idéntico a Q -> alta atención
            [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # Ortogonal a Q -> baja atención
        ])
        values = np.array([
            [10.0, 10.0],
            [1.0, 1.0]
        ])

        context, weights = qkv.forward(query, keys, values)
        self.assertGreater(weights[0], weights[1])
        self.assertAlmostEqual(sum(weights), 1.0, places=5)
        self.assertGreater(context[0], 5.0)

    def test_episodic_memory_semantic_retrieval(self):
        """Verifica el almacenamiento y recuperación semántica de episodios."""
        embedder = VectorEmbeddingEngine(dim=16)
        mem = Memory()
        retriever = Retriever(memory=mem, embedding_engine=embedder)

        g_vec = embedder.embed_text("persona adentro de habitacion")
        mem.episodic.record_episode(
            episode_id="EP_01",
            goal_desc="Llevar persona adentro",
            initial_state_summary="puerta cerrada persona afuera",
            plan_actions=["abrir_puerta", "entrar"],
            success=True,
            cost=2.0,
            reward=9.0,
            goal_embedding=g_vec
        )

        query = embedder.embed_text("entrar persona a la habitacion")
        results = retriever.retrieve_episodes(query, top_k=1)

        self.assertEqual(len(results), 1)
        sim, ep = results[0]
        self.assertGreater(sim, 0.5)
        self.assertEqual(ep.id, "EP_01")
        self.assertEqual(ep.plan_actions, ["abrir_puerta", "entrar"])

    def test_plan_evaluation_scoring(self):
        """Verifica la evaluación formal multidimensional de planes."""
        k = Kernel()
        for o, t in [("p", "Door"), ("cerrada", "StateVal"), ("abierta", "StateVal")]:
            k.transition(Transition("add_object", {"id": o, "type": t}))
        k.transition(Transition("add_relation", {"id": "r1", "source": "p", "predicate": "estado", "target": "cerrada", "polarity": True}))

        act = Action(
            name="abrir",
            preconditions=(("p", "estado", "cerrada", True),),
            effects=(
                Transition("remove_relation", {"id": "r1"}),
                Transition("add_relation", {"id": "r2", "source": "p", "predicate": "estado", "target": "abierta", "polarity": True})
            ),
            cost=1.0
        )
        plan = Plan(steps=[type('Step', (), {'action': act})], total_cost=1.0)
        goal = Goal(conditions=(("p", "estado", "abierta", True),))

        evaluator = PlanEvaluator()
        score = evaluator.evaluate_plan(plan, k.state, goal)

        self.assertTrue(score.is_valid)
        self.assertGreater(score.utility, 0.0)
        self.assertGreater(score.goal_alignment, 0.8)

    def test_learning_and_weight_adaptation(self):
        """Verifica la actualización de priors de acción tras la ejecución."""
        learner = Learner(learning_rate=0.5)
        act = Action(name="abrir_puerta", cost=1.0)
        plan = Plan(steps=[type('Step', (), {'action': act})], total_cost=1.0)
        goal = Goal(conditions=())
        episodic = EpisodicMemory()

        self.assertEqual(learner.get_action_prior("abrir_puerta"), 0.0)

        reward, ep = learner.update_from_execution(
            plan=plan,
            goal=goal,
            goal_satisfied=True,
            execution_ok=True,
            episodic_memory=episodic
        )

        self.assertGreater(reward, 0.0)
        self.assertGreater(learner.get_action_prior("abrir_puerta"), 0.0)
        self.assertEqual(len(episodic.get_all_episodes()), 1)

    def test_agent_full_cognitive_cycle_layer2(self):
        """Verifica el ciclo cognitivo integral del agente en Capa 2."""
        k = Kernel()
        for o, t in [("persona", "Agent"), ("puerta", "Door"), ("cerrada", "Val"), ("abierta", "Val"), ("afuera", "Val"), ("adentro", "Val")]:
            k.transition(Transition("add_object", {"id": o, "type": t}))
        k.transition(Transition("add_relation", {"id": "r_pc", "source": "puerta", "predicate": "estado", "target": "cerrada", "polarity": True}))
        k.transition(Transition("add_relation", {"id": "r_pa", "source": "persona", "predicate": "posicion", "target": "afuera", "polarity": True}))

        abrir = Action(
            name="abrir_puerta",
            preconditions=(("puerta", "estado", "cerrada", True),),
            effects=(
                Transition("remove_relation", {"id": "r_pc"}),
                Transition("add_relation", {"id": "r_pab", "source": "puerta", "predicate": "estado", "target": "abierta", "polarity": True})
            ),
            cost=1.0
        )
        entrar = Action(
            name="entrar",
            preconditions=(("puerta", "estado", "abierta", True), ("persona", "posicion", "afuera", True)),
            effects=(
                Transition("remove_relation", {"id": "r_pa"}),
                Transition("add_relation", {"id": "r_pad", "source": "persona", "predicate": "posicion", "target": "adentro", "polarity": True})
            ),
            cost=1.0
        )

        agent = Agent(kernel=k, dim=16)
        goal = Goal(conditions=(("persona", "posicion", "adentro", True),))

        # Ciclo cognitivo completo
        res = agent.step(goal=goal, available_actions=[abrir, entrar])

        self.assertTrue(res.executed)
        self.assertTrue(res.goal_achieved)
        self.assertIsNotNone(res.plan)
        self.assertEqual(res.plan.action_names, ["abrir_puerta", "entrar"])
        self.assertGreater(res.reward, 0.0)
        self.assertIsNotNone(res.recorded_episode)
        self.assertIn("r_pad", agent.state.relations)

if __name__ == "__main__":
    unittest.main()
