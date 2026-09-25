"""
server.py - Servidor Web Ligero de Observabilidad y Control en Tiempo Real para MF_MIN V7.
Usa únicamente la biblioteca estándar de Python (http.server, socketserver, json, urllib).
Sirve visualizer.html en http://localhost:8000 y expone endpoints REST para:
 - /api/status   (GET): Estado del Kernel, inventario, ubicación, Q-values, memoria y reglas inducidas.
 - /api/execute  (POST): Despacho deliberativo de comandos en lenguaje natural con planificación física.
 - /api/assert   (POST): Ingesta universal de hechos en lenguaje natural, deducción y aprendizaje inductivo.
 - /api/reset    (POST): Reinicio sincronizado del entorno físico y del Kernel del agente.
 - /api/save     (POST): Persistencia del estado completo del agente en checkpoint JSON.
 - /api/load     (POST): Restauración del agente desde checkpoint JSON.
"""
from __future__ import annotations
import http.server
import socketserver
import json
import os
import urllib.parse
from typing import Dict, Any, Optional, List

from mf_min_definitivo import Kernel, Transition, State
from environment import VirtualFacilityEnvironment
from agent import Agent, InputEnvelope, InputKind
from motor_c import Action, Goal, Plan, PlanStep
from natural_language import NaturalLanguageInterface
from llm_adapter import OllamaAdapter
from storage import save_agent_checkpoint, load_agent_checkpoint


class CognitiveServerState:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reinicia el entorno físico y el agente cognitivo a sus estados iniciales."""
        self.env = VirtualFacilityEnvironment()
        self.kernel = Kernel()

        # Ontología base para el entorno
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
            self.kernel.transition(Transition("add_object", {"id": oid, "type": otype}))

        self.agent = Agent(kernel=self.kernel, dim=16)
        self.nli = NaturalLanguageInterface(embedder=self.agent.embedder)
        self.llm = OllamaAdapter(model="llama3.2:3b")

        # Percepción sensorial inicial del entorno físico
        self.agent.perceive_environment(self.env.get_sensory_data())
        self.last_result: Optional[Dict[str, Any]] = None

    def execute_command(self, user_text: str) -> Dict[str, Any]:
        """Procesa una instrucción de usuario en lenguaje natural a través del ciclo deliberativo."""
        goal, sim, desc = self.nli.parse_instruction_to_goal(user_text)
        if goal is None:
            return {
                "status": "rejected",
                "explanation": f"Instrucción rechazada: Afinidad semántica insuficiente ({sim:.2f}) para formular un objetivo operativo.",
                "similarity": sim,
                "plan": [],
                "reward": 0.0
            }

        # Generar secuencia de acciones según el objetivo y el estado físico actual
        steps = []
        loc = self.env.agent_location
        inv = self.env.inventory
        doors = self.env.doors

        # Planificación dinámica de metas
        if "sala_servidores" in str(goal.conditions):
            if "tarjeta_azul" not in inv:
                if not doors["puerta_deposito"]["open"]:
                    steps.append(("abrir", "puerta_deposito", "Abrir la puerta del depósito"))
                if loc != "deposito":
                    steps.append(("mover_a", "deposito", "Ingresar al depósito"))
                steps.append(("recoger", "tarjeta_azul", "Recoger la tarjeta azul del suelo"))
                steps.append(("mover_a", "pasillo", "Regresar al pasillo principal"))
            if doors["puerta_servidores"]["locked"]:
                steps.append(("destrabar", "puerta_servidores", "Destrabar la puerta de servidores"))
            if not doors["puerta_servidores"]["open"]:
                steps.append(("abrir", "puerta_servidores", "Abrir la puerta de servidores"))
            steps.append(("mover_a", "sala_servidores", "Ingresar a la sala de servidores"))

        elif "deposito" in str(goal.conditions) and "posicion" in str(goal.conditions):
            if not doors["puerta_deposito"]["open"]:
                steps.append(("abrir", "puerta_deposito", "Abrir la puerta del depósito"))
            steps.append(("mover_a", "deposito", "Ingresar al depósito"))

        elif "tarjeta_azul" in str(goal.conditions):
            if not doors["puerta_deposito"]["open"]:
                steps.append(("abrir", "puerta_deposito", "Abrir la puerta del depósito"))
            if loc != "deposito":
                steps.append(("mover_a", "deposito", "Ingresar al depósito"))
            steps.append(("recoger", "tarjeta_azul", "Recoger la tarjeta azul"))

        elif "llave_bronce" in str(goal.conditions):
            if loc != "pasillo":
                steps.append(("mover_a", "pasillo", "Volver al pasillo"))
            steps.append(("recoger", "llave_bronce", "Recoger llave de bronce"))

        elif "puerta_servidores" in str(goal.conditions) and "abierta" in str(goal.conditions):
            if "tarjeta_azul" not in inv:
                if not doors["puerta_deposito"]["open"]:
                    steps.append(("abrir", "puerta_deposito", "Abrir la puerta del depósito"))
                if loc != "deposito":
                    steps.append(("mover_a", "deposito", "Ingresar al depósito"))
                steps.append(("recoger", "tarjeta_azul", "Recoger la tarjeta azul"))
                steps.append(("mover_a", "pasillo", "Regresar al pasillo principal"))
            if doors["puerta_servidores"]["locked"]:
                steps.append(("destrabar", "puerta_servidores", "Destrabar la puerta de servidores"))
            steps.append(("abrir", "puerta_servidores", "Abrir la puerta de servidores"))

        elif "puerta_deposito" in str(goal.conditions) and "abierta" in str(goal.conditions):
            steps.append(("abrir", "puerta_deposito", "Abrir la puerta del depósito"))

        action_names = []
        executed = False
        total_cost = 0.0
        plan_steps = []

        for act_cmd, target, act_desc in steps:
            res = self.env.step(act_cmd, target)
            total_cost += res.energy_cost
            action_names.append(f"{act_cmd}_{target}")
            self.agent.perceive_environment(res.observations)
            plan_steps.append(PlanStep(step_number=len(plan_steps)+1, action=Action(name=f"{act_cmd}_{target}", cost=res.energy_cost)))

        executed = len(steps) > 0
        goal_satisfied = goal.is_satisfied(self.agent.kernel.state)

        plan_obj = Plan(steps=plan_steps, total_cost=total_cost) if plan_steps else None
        if plan_obj:
            reward, ep = self.agent.learner.update_from_execution(
                plan=plan_obj,
                goal=goal,
                goal_satisfied=goal_satisfied,
                execution_ok=executed,
                episodic_memory=self.agent.episodic_memory
            )
        else:
            reward = 0.0

        explanation = self.nli.generate_explanation(
            goal_desc=user_text,
            plan_names=action_names,
            executed=executed,
            real_world_success=goal_satisfied,
            reward=reward,
            deductions_count=len(self.agent.inference_rules),
            feedback_message=f"Ubicación actual: '{self.env.agent_location}', Inventario: {self.env.inventory}."
        )

        self.last_result = {
            "status": "success" if goal_satisfied else "partial",
            "user_command": user_text,
            "goal": str(goal.conditions),
            "plan": action_names,
            "success": goal_satisfied,
            "location": self.env.agent_location,
            "inventory": self.env.inventory,
            "reward": reward,
            "explanation": explanation
        }
        return self.last_result

    def assert_fact(self, text: str) -> Dict[str, Any]:
        """Ingesta un hecho en lenguaje natural, actualiza el Kernel y ejecuta deducción e inducción."""
        resp = self.agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload=text, source="web_user"))
        deductions = self.agent.run_deduction()

        return {
            "success": resp.success,
            "detail": resp.detail,
            "deductions_count": deductions,
            "total_relations": len(self.agent.kernel.state.relations),
            "promoted_rules": [r.name for r in self.agent.inference_rules]
        }


server_state = CognitiveServerState()


class CognitiveRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.path = "/visualizer.html"
            return super().do_GET()

        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()

            state = server_state.agent.state
            rels = [
                {
                    "source": r.source,
                    "predicate": r.predicate,
                    "target": r.target,
                    "polarity": r.polarity,
                    "origin": r.origin,
                    "id": r.id
                }
                for r in state.relations.values()
            ]
            episodes = [
                {"id": ep.id, "plan": ep.plan_actions, "success": ep.success, "reward": ep.reward}
                for ep in server_state.agent.episodic_memory.get_all_episodes()
            ]
            q_vals = {k: round(v, 4) for k, v in server_state.agent.learner.action_values.items()}
            rules = [
                {"id": r.id, "name": r.name, "premises_count": len(r.premises)}
                for r in server_state.agent.inference_rules
            ]

            doors_status = {
                dname: {"open": dinfo["open"], "locked": dinfo["locked"]}
                for dname, dinfo in server_state.env.doors.items()
            }

            data = {
                "ollama_available": server_state.llm.is_available(),
                "model": server_state.llm.model,
                "agent_location": server_state.env.agent_location,
                "inventory": server_state.env.inventory,
                "doors": doors_status,
                "relations": rels,
                "episodes": episodes,
                "action_values": q_vals,
                "inference_rules": rules,
                "last_result": server_state.last_result
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        payload = json.loads(body) if body else {}

        if parsed.path == "/api/execute":
            command = payload.get("command", "entra a la sala de servidores")
            result = server_state.execute_command(command)
            self.send_json(result)
            return

        if parsed.path == "/api/assert":
            text = payload.get("text", "")
            result = server_state.assert_fact(text)
            self.send_json(result)
            return

        if parsed.path == "/api/reset":
            server_state.reset()
            self.send_json({"status": "reset_completed", "agent_location": server_state.env.agent_location})
            return

        if parsed.path == "/api/save":
            filepath = payload.get("filepath", "checkpoint_agent.json")
            save_agent_checkpoint(server_state.agent, filepath)
            self.send_json({"status": "saved", "filepath": filepath})
            return

        if parsed.path == "/api/load":
            filepath = payload.get("filepath", "checkpoint_agent.json")
            if os.path.exists(filepath):
                server_state.agent = load_agent_checkpoint(filepath)
                self.send_json({"status": "loaded", "filepath": filepath})
            else:
                self.send_json({"status": "error", "message": "Archivo no encontrado"}, status=404)
            return

        self.send_response(404)
        self.end_headers()

    def send_json(self, data: Dict[str, Any], status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


def run_server(port: int = 8000):
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cur_dir)
    with socketserver.TCPServer(("", port), CognitiveRequestHandler) as httpd:
        print("=" * 65)
        print(f" SERVIDOR COGNITIVO MF_MIN V7 ACTIVO")
        print(f" URL de la interfaz: http://localhost:{port}")
        print(" Presiona Ctrl+C para detener el servidor.")
        print("=" * 65)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido con éxito.")


if __name__ == "__main__":
    run_server(8000)
