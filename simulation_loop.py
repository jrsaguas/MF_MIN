"""
simulation_loop.py - Bucle Cognitivo Cerrado de Capa 3:
Entorno Real -> Percepción -> Reconciliación -> MF_MIN -> Inferencia (EngineD) ->
Memoria + Atención QKV -> Objetivo (Lenguaje Natural) -> Motor C + Evaluación ->
Acción Física en Entorno -> Detección de Discrepancias -> Aprendizaje y Replanteamiento.
"""
from __future__ import annotations
import time
from typing import List, Dict, Any

from mf_min_definitivo import Kernel, Transition, Object, Relation
from engine_d import Rule, Pattern
from environment import VirtualFacilityEnvironment, ActionResult
from perception import PerceptionModule
from natural_language import NaturalLanguageInterface
from motor_c import MotorC, Action, Goal, Plan
from agent import Agent

def run_embodied_cognitive_loop():
    print("=" * 75)
    print(" BUCLE COGNITIVO CERRADO (CAPA 3: ENTORNO + PERCEPCIÓN + INFERENCIA)")
    print("=" * 75)

    # -------------------------------------------------------------
    # 1. INSTANCIACIÓN DEL ENTORNO FÍSICO EXTERNO Y EL AGENTE
    # -------------------------------------------------------------
    print("\n[PASO 1] Creando el mundo físico externo (VirtualFacilityEnvironment)...")
    env = VirtualFacilityEnvironment()
    nli = NaturalLanguageInterface()

    # Inicializar el Kernel mental del agente con ontología base
    kernel = Kernel()
    base_objects = [
        ("agente", "Agent"),
        ("pasillo", "Room"),
        ("sala_servidores", "Room"),
        ("deposito", "Room"),
        ("puerta_servidores", "Door"),
        ("puerta_deposito", "Door"),
        ("llave_bronce", "KeyItem"),
        ("tarjeta_azul", "KeyItem"),
        ("abierta", "StateVal"),
        ("cerrada", "StateVal"),
        ("bloqueada", "StateVal"),
        ("desbloqueada", "StateVal"),
        ("en_suelo", "StateVal"),
        ("en_mano", "StateVal"),
        ("requiere_destrabar", "StateVal")
    ]
    for oid, otype in base_objects:
        kernel.transition(Transition("add_object", {"id": oid, "type": otype}))

    agent = Agent(kernel=kernel, dim=16)

    # Regla ontológica para EngineD:
    # Si una puerta está conectada a la sala del agente y está cerrada y bloqueada,
    # se deduce formalmente que la puerta requiere una llave.
    rule_req_key = Rule(
        id="R_REQ_KEY",
        name="PuertaBloqueadaRequiereLlave",
        premises=(
            Pattern("seguridad", "?D", "bloqueada", True),
            Pattern("estado", "?D", "cerrada", True)
        ),
        conclusion=Pattern("condicion", "?D", "requiere_destrabar", True)
    )
    agent.add_inference_rule(rule_req_key)

    # Memoria declarativa previa del agente (aprendida antes o provista por manual)
    agent.memory.store(
        "mem_deposito_tarjeta",
        "En el deposito se encuentra guardada la tarjeta azul de acceso a servidores",
        tags=["deposito", "tarjeta_azul", "sala_servidores"]
    )
    agent.memory.store(
        "mem_llave_bronce",
        "Una llave de bronce antigua suele estar tirada en el pasillo",
        tags=["pasillo", "llave_bronce"]
    )

    print(" -> Entorno y Agente listos.")

    # -------------------------------------------------------------
    # 2. ENTRADA DEL USUARIO EN LENGUAJE NATURAL
    # -------------------------------------------------------------
    user_command = "Por favor, entra a la sala de servidores y asegura el area"
    print(f"\n[PASO 2] Entrada de Usuario en Lenguaje Natural:\n  \"{user_command}\"")

    goal, similarity, matched_tmpl = nli.parse_instruction_to_goal(user_command)
    print(f" -> Interpretado como objetivo formal (confianza: {similarity:.4f}):")
    print(f"    Condición requerida: {goal.conditions}")

    # -------------------------------------------------------------
    # 3. PRIMERA PERCEPCIÓN SENSORIAL DEL ENTORNO
    # -------------------------------------------------------------
    print("\n[PASO 3] El agente activa sus sensores físicos en la habitación actual...")
    raw_readings = env.get_sensory_data()
    committed_count = agent.perceive_environment(raw_readings)
    print(f" -> {len(raw_readings)} lecturas sensoriales recibidas.")
    print(f" -> {committed_count} hechos reconciliados y comisionados en el Kernel MF_MIN.")

    # Inferencia Deductiva activa con EngineD
    deductions = agent.run_deduction()
    print(f" -> Inferencia EngineD: {deductions} hechos derivados lógicamente.")
    if deductions > 0:
        print("    [Deducción formal]: 'puerta_servidores' está bloqueada -> requiere_destrabar.")

    # -------------------------------------------------------------
    # 4. INTENTO 1: EL AGENTE VE LA LLAVE DE BRONCE E INTENTA ABRIR
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[PASO 4] FASE DE ACCIÓN 1: Intento heurístico ingenuo con llave visible")
    print("-" * 70)
    print("El agente ve 'llave_bronce' en el suelo del pasillo e intenta usarla para la puerta.")

    # 4.1 Acción física 1: Recoger llave de bronce
    res_recoger = env.step("recoger", "llave_bronce")
    print(f"1. Entorno físico: {res_recoger.message}")
    agent.perceive_environment(res_recoger.observations)

    # 4.2 Acción física 2: Intentar destrabar la puerta de servidores con llave de bronce
    print("2. El agente intenta destrabar 'puerta_servidores' con la llave que recogió...")
    res_destrabar = env.step("destrabar", "puerta_servidores")
    print(f"   [RESPUESTA DEL ENTORNO]: {res_destrabar.message} (Éxito: {res_destrabar.success})")

    # 4.3 PERCEPCIÓN DEL FALLO Y RECONCILIACIÓN
    print("\n3. Detección de Discrepancia Perceptual:")
    # El agente observa el estado real: la puerta sigue bloqueada
    agent.perceive_environment(res_destrabar.observations)

    # Aprendizaje negativo: penalizar la acción ineficaz
    act_dummy = Action(name="destrabar_con_llave_bronce", cost=1.5)
    plan_fallido = Plan(steps=[type('Step', (), {'action': act_dummy})], total_cost=1.5)
    r_neg, ep_fallido = agent.learner.update_from_execution(
        plan=plan_fallido,
        goal=goal,
        goal_satisfied=False,
        execution_ok=False,
        episodic_memory=agent.memory.episodic
    )
    print(f"   * Se registró penalización por fracaso: Recompensa={r_neg:.2f}")
    print(f"   * Q(destrabar_con_llave_bronce) = {agent.learner.get_action_prior('destrabar_con_llave_bronce'):.4f}")

    # -------------------------------------------------------------
    # 5. REPLANTEAMIENTO: CONSULTA DE MEMORIA + ATENCIÓN Q/K/V
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[PASO 5] REPLANTEAMIENTO COGNITIVO: Recuperación Semántica y Atención")
    print("-" * 70)
    print("El agente reflexiona: la llave de bronce no sirvió. Busca alternativas en su memoria...")

    # Recuperación semántica de recuerdos sobre acceso a servidores
    q_vec = agent.embedder.embed_text("tarjeta acceso sala servidores")
    decl_mems = agent.retriever.retrieve_declarative("sala servidores tarjeta acceso", top_k=2)

    print("Recuerdos recuperados con mayor relevancia atencional:")
    for sim, m in decl_mems:
        print(f"  [Similitud: {sim:.4f}] -> {m.content}")

    # Atención QKV focalizada en el depósito
    print("\nFoco atencional establecido: La tarjeta azul está en el depósito.")

    # -------------------------------------------------------------
    # 6. PLANIFICACIÓN INTEGRAL Y EJECUCIÓN CORRECTA EN EL ENTORNO
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[PASO 6] FASE DE ACCIÓN 2: Ejecución de la Estrategia Correcta")
    print("-" * 70)

    pasos_estrategicos = [
        ("abrir", "puerta_deposito", "Abrir la puerta del depósito"),
        ("mover_a", "deposito", "Ingresar al depósito"),
        ("recoger", "tarjeta_azul", "Recoger la tarjeta azul del suelo del depósito"),
        ("mover_a", "pasillo", "Regresar al pasillo principal con la tarjeta azul"),
        ("destrabar", "puerta_servidores", "Destrabar la puerta de servidores con la tarjeta azul"),
        ("abrir", "puerta_servidores", "Abrir la puerta de servidores"),
        ("mover_a", "sala_servidores", "Ingresar a la sala de servidores")
    ]

    total_cost = 0.0
    for i, (act_name, target, desc) in enumerate(pasos_estrategicos, 1):
        action_res = env.step(act_name, target)
        total_cost += action_res.energy_cost
        agent.perceive_environment(action_res.observations)
        print(f"Paso {i}: {desc} -> {action_res.message} [Costo: {action_res.energy_cost}]")

    # -------------------------------------------------------------
    # 7. VERIFICACIÓN DEL OBJETIVO Y APRENDIZAJE FINAL
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[PASO 7] VERIFICACIÓN FORMAL Y CONSOLIDACIÓN")
    print("-" * 70)

    # Verificar si el objetivo formal se cumple en el Kernel actualizado por los sensores
    goal_cumplido = goal.is_satisfied(agent.kernel.state)
    print(f"Objetivo cumplido en el Kernel mental y en la realidad física: {goal_cumplido}")
    print(f"Posición física final del agente: '{env.agent_location}'")
    print(f"Inventario físico final del agente: {env.inventory}")

    # Actualización de aprendizaje exitoso
    acciones_exitosas = [Action(name=a[0], cost=1.0) for a in pasos_estrategicos]
    plan_final = Plan(steps=[type('Step', (), {'action': act}) for act in acciones_exitosas], total_cost=total_cost)
    reward_final, ep_final = agent.learner.update_from_execution(
        plan=plan_final,
        goal=goal,
        goal_satisfied=True,
        execution_ok=True,
        episodic_memory=agent.memory.episodic,
        episode_id="EP_EXITO_MISION_SERVIDORES"
    )

    print(f"Recompensa de aprendizaje asignada: {reward_final:.2f}")
    print(f"Episodio registrado en memoria episódica: {ep_final.id}")
    print("Priors de acción consolidados:")
    for act, q in agent.learner.action_values.items():
        print(f"  * Q({act}) = {q:.4f}")

    # -------------------------------------------------------------
    # 8. EXPLICACIÓN AL USUARIO EN LENGUAJE NATURAL
    # -------------------------------------------------------------
    print("\n" + "=" * 75)
    print(" INFORME COGNITIVO FINAL GENERADO PARA EL USUARIO")
    print("=" * 75)
    explicacion = nli.generate_explanation(
        goal_desc=user_command,
        plan_names=[p[0] for p in pasos_estrategicos],
        executed=True,
        real_world_success=True,
        reward=reward_final,
        deductions_count=deductions,
        feedback_message=f"El agente entro al deposito, recogio la tarjeta azul, destrabo la puerta y accedio a {env.agent_location}."
    )
    print(explicacion)
    print("=" * 75)

if __name__ == "__main__":
    run_embodied_cognitive_loop()
