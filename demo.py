"""
demo.py - Demostración integral de la Capa 2 de la Arquitectura Cognitiva MF_MIN.
Muestra:
  1. Núcleo formal MF_MIN y preservación de invariantes <O, M, A, delta>.
  2. Embeddings y similitud semántica.
  3. Atención por producto punto escalado (Q, K, V).
  4. Recuperación episódica semántica.
  5. Planificación guiada en Motor C.
  6. Evaluación multidimensional de planes (PlanEvaluator).
  7. Ejecución atómica en el Kernel mediante transition_batch().
  8. Aprendizaje por refuerzo y consolidación de experiencia.
"""
import numpy as np

from mf_min_definitivo import Kernel, Transition
from reconcile import Reconciler, Proposal
from motor_c import MotorC, Action, Goal, Plan
from attention import AttentionEngine
from embeddings import VectorEmbeddingEngine, cosine_similarity
from memory import Memory
from retrieval import Retriever
from evaluation import PlanEvaluator
from learning import Learner
from agent import Agent

def print_separator(title: str):
    print("\n" + "=" * 65)
    print(f" {title}")
    print("=" * 65)

def run_demo():
    print_separator("ARQUITECTURA COGNITIVA MF_MIN - CAPA 2: INTEGRACIÓN TOTAL")

    # -------------------------------------------------------------
    # 1. EMBEDDINGS VECTORIALES Y SIMILITUD SEMÁNTICA
    # -------------------------------------------------------------
    print_separator("1. REPRESENTACIÓN VECTORIAL & SIMILITUD SEMÁNTICA")
    embedder = VectorEmbeddingEngine(dim=16)
    v_goal = embedder.embed_text("persona adentro de habitacion")
    v_similar = embedder.embed_text("agente en interior de sala")
    v_unrelated = embedder.embed_text("planeta orbita sistema solar")

    sim_high = cosine_similarity(v_goal, v_similar)
    sim_low = cosine_similarity(v_goal, v_unrelated)

    print(f"Embedding Query: 'persona adentro de habitacion' (dim={embedder.dim})")
    print(f"Similitud con 'agente en interior de sala' (afín): {sim_high:.4f}")
    print(f"Similitud con 'planeta orbita sistema solar' (no afín): {sim_low:.4f}")

    # -------------------------------------------------------------
    # 2. ATENCIÓN FORMAL Q / K / V (SCALED DOT-PRODUCT)
    # -------------------------------------------------------------
    print_separator("2. ATENCIÓN SCALED DOT-PRODUCT (Q, K, V)")
    attn_engine = AttentionEngine(dim=16)
    
    # Supongamos 3 recuerdos/hechos en memoria
    facts = [
        "la puerta esta trabada con cerrojo",
        "la persona se encuentra esperando afuera",
        "hay una llave en el escritorio"
    ]
    k_vecs = [embedder.embed_text(f) for f in facts]
    
    # Query: El objetivo es entrar a la habitación
    context_vec, weights, ranked = attn_engine.attend_qkv(
        query_vector=v_goal,
        keys=k_vecs,
        values=facts
    )

    print("Query cognitivo: 'persona adentro de habitacion'")
    print("Distribución de pesos de atención QKV sobre memoria:")
    for w, fact in ranked:
        print(f"  [peso: {w:.4f}] -> '{fact}'")
    print(f"Norma del vector de contexto activo resultante: {np.linalg.norm(context_vec):.4f}")

    # -------------------------------------------------------------
    # 3. KERNEL MF_MIN, MOTOR C Y RECONCILIACIÓN
    # -------------------------------------------------------------
    print_separator("3. ESTADO FORMAL MF_MIN & RECONCILIACIÓN INICIAL")
    kernel = Kernel()

    # Creación del mundo formal
    objects_data = [
        ("persona", "Agent"),
        ("puerta", "Door"),
        ("habitacion", "Room"),
        ("cerrada", "StateVal"),
        ("abierta", "StateVal"),
        ("afuera", "StateVal"),
        ("adentro", "StateVal")
    ]
    for oid, otype in objects_data:
        kernel.transition(Transition("add_object", {"id": oid, "type": otype}))

    # Estado inicial: Puerta cerrada, Persona afuera
    kernel.transition(Transition("add_relation", {"id": "r_puerta_cerrada", "source": "puerta", "predicate": "estado", "target": "cerrada", "polarity": True}))
    kernel.transition(Transition("add_relation", {"id": "r_persona_afuera", "source": "persona", "predicate": "posicion", "target": "afuera", "polarity": True}))

    print(f"Objetos en Kernel: {list(kernel.state.objects.keys())}")
    print(f"Relaciones activas: {[(r.source, r.predicate, r.target) for r in kernel.state.relations.values()]}")

    # -------------------------------------------------------------
    # 4. DEFINICIÓN DE OPERADORES Y OBJETIVO
    # -------------------------------------------------------------
    abrir_puerta = Action(
        name="abrir_puerta",
        preconditions=(("puerta", "estado", "cerrada", True),),
        effects=(
            Transition("remove_relation", {"id": "r_puerta_cerrada"}),
            Transition("add_relation", {"id": "r_puerta_abierta", "source": "puerta", "predicate": "estado", "target": "abierta", "polarity": True})
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
            Transition("remove_relation", {"id": "r_persona_afuera"}),
            Transition("add_relation", {"id": "r_persona_adentro", "source": "persona", "predicate": "posicion", "target": "adentro", "polarity": True})
        ),
        cost=1.0
    )

    goal = Goal(conditions=(("persona", "posicion", "adentro", True),))

    # -------------------------------------------------------------
    # 5. AGENTE COGNITIVO COMPLETO: CICLO DE DELIBERACIÓN Y EJECUCIÓN
    # -------------------------------------------------------------
    print_separator("4. EJECUCIÓN DEL CICLO COGNITIVO DEL AGENTE")
    agent = Agent(kernel=kernel, dim=16)

    # Pre-cargar un episodio en memoria episódica para demostrar antecedente análogo
    agent.memory.episodic.record_episode(
        episode_id="EP_PREVIA_00",
        goal_desc="entrar a la habitacion",
        initial_state_summary="persona afuera puerta cerrada",
        plan_actions=["abrir_puerta", "entrar"],
        success=True,
        cost=2.0,
        reward=9.0,
        goal_embedding=embedder.embed_text("entrar a la habitacion")
    )

    print("Estado inicial verificado.")
    print("Ejecutando agent.step(goal)...")
    res = agent.step(goal=goal, available_actions=[abrir_puerta, entrar])

    print("\n[RESULTADO DEL CICLO COGNITIVO]")
    print(f"Plan generado: {' -> '.join(res.plan.action_names)}")
    print(f"Costo del plan: {res.plan.total_cost}")
    print(f"Puntuación del PlanEvaluator:")
    print(f"   - Utilidad compuesta: {res.plan_score.utility:.4f}")
    print(f"   - Alineación semántica con el objetivo: {res.plan_score.goal_alignment:.4f}")
    print(f"   - Antecedente episódico / prior: {res.plan_score.episodic_prior:.4f}")
    print(f"   - Validez formal en Kernel: {res.plan_score.is_valid}")
    print(f"Ejecutado atómicamente en MF_MIN: {res.executed}")
    print(f"Objetivo cumplido: {res.goal_achieved}")
    print(f"Recompensa ambiental calculada: {res.reward:.2f}")

    # -------------------------------------------------------------
    # 6. APRENDIZAJE & CONSOLIDACIÓN EPISÓDICA
    # -------------------------------------------------------------
    print_separator("5. APRENDIZAJE POR REFUERZO & ADAPTACIÓN")
    print("Valores de preferencia aprendidos Q(a):")
    for act_name, q_val in agent.learner.action_values.items():
        print(f"   Acción '{act_name}': Q-value = {q_val:.4f}")

    print("\nEpisodios consolidados en memoria episódica:")
    for ep in agent.memory.episodic.get_all_episodes():
        print(f"   - [{ep.id}] Meta: '{ep.goal_desc}' | Plan: {ep.plan_actions} | Exito: {ep.success} | Recompensa: {ep.reward:.2f}")

    print("\nEstado final del Kernel:")
    for r in agent.state.relations.values():
        print(f"   - Relación: ({r.source}) --[{r.predicate}]--> ({r.target}) [Polaridad={r.polarity}, ID={r.id}]")

    print_separator("DEMOSTRACIÓN FINALIZADA CON ÉXITO")

if __name__ == "__main__":
    run_demo()
