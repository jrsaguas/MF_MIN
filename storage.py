"""
storage.py - Persistencia y serialización para la arquitectura cognitiva MF_MIN.
Permite exportar e importar el estado del Kernel, los episodios de memoria y los pesos
aprendidos a archivos JSON estructurados.
"""
from __future__ import annotations
import json
from typing import Dict, Any, Optional
import numpy as np

from mf_min_definitivo import State, Object, Relation, AxiomConstraint, Clause, Kernel
from memory import Memory, Episode
from agent import Agent

def state_to_dict(state: State) -> Dict[str, Any]:
    return {
        "objects": {
            oid: {
                "id": o.id,
                "type": o.type,
                "value": o.value,
                "properties": dict(o.properties)
            }
            for oid, o in state.objects.items()
        },
        "relations": {
            rid: {
                "id": r.id,
                "source": r.source,
                "predicate": r.predicate,
                "target": r.target,
                "polarity": r.polarity,
                "origin": r.origin,
                "rule_id": r.rule_id,
                "premises": list(r.premises)
            }
            for rid, r in state.relations.items()
        },
        "axioms": {
            aid: {
                "id": a.id,
                "name": a.name,
                "body": [{"predicate": c.predicate, "source": c.source, "target": c.target, "polarity": c.polarity} for c in a.body],
                "min_numeric_val": a.min_numeric_val,
                "max_numeric_val": a.max_numeric_val,
                "numeric_target_type": a.numeric_target_type
            }
            for aid, a in state.axioms.items()
        }
    }

def dict_to_state(d: Dict[str, Any]) -> State:
    objects = {
        oid: Object(id=od["id"], type=od["type"], value=od.get("value"), properties=od.get("properties", {}))
        for oid, od in d.get("objects", {}).items()
    }
    relations = {
        rid: Relation(
            id=rd["id"], source=rd["source"], predicate=rd["predicate"], target=rd["target"],
            polarity=rd.get("polarity", True), origin=rd.get("origin", "asserted"),
            rule_id=rd.get("rule_id"), premises=tuple(rd.get("premises", ()))
        )
        for rid, rd in d.get("relations", {}).items()
    }
    axioms = {
        aid: AxiomConstraint(
            id=ad["id"], name=ad["name"],
            body=tuple(Clause(**c) for c in ad.get("body", ())),
            min_numeric_val=ad.get("min_numeric_val"),
            max_numeric_val=ad.get("max_numeric_val"),
            numeric_target_type=ad.get("numeric_target_type")
        )
        for aid, ad in d.get("axioms", {}).items()
    }
    return State(objects=objects, relations=relations, axioms=axioms)

def save_agent_checkpoint(agent: Agent, filepath: str) -> None:
    data = {
        "state": state_to_dict(agent.state),
        "action_values": agent.learner.action_values,
        "episodes": [
            {
                "id": ep.id,
                "goal_desc": ep.goal_desc,
                "initial_state_summary": ep.initial_state_summary,
                "plan_actions": ep.plan_actions,
                "success": ep.success,
                "cost": ep.cost,
                "reward": ep.reward,
                "goal_embedding": ep.goal_embedding.tolist() if ep.goal_embedding is not None else None,
                "timestamp": ep.timestamp,
                "metadata": ep.metadata
            }
            for ep in agent.memory.episodic.get_all_episodes()
        ]
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_agent_checkpoint(filepath: str, dim: int = 16) -> Agent:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    state = dict_to_state(data["state"])
    kernel = Kernel(state)
    agent = Agent(kernel=kernel, dim=dim)
    agent.learner.action_values = data.get("action_values", {})

    for ep_dict in data.get("episodes", []):
        g_emb = np.array(ep_dict["goal_embedding"], dtype=np.float32) if ep_dict.get("goal_embedding") is not None else None
        agent.memory.episodic.record_episode(
            episode_id=ep_dict["id"],
            goal_desc=ep_dict["goal_desc"],
            initial_state_summary=ep_dict.get("initial_state_summary", ""),
            plan_actions=ep_dict.get("plan_actions", []),
            success=ep_dict.get("success", True),
            cost=ep_dict.get("cost", 0.0),
            reward=ep_dict.get("reward", 0.0),
            goal_embedding=g_emb,
            metadata=ep_dict.get("metadata", {})
        )

    return agent
