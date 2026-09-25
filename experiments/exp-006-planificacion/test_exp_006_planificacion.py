"""EXP-006 — Planificación sobre MF_MIN.

Prueba que un objetivo, acciones candidatas, precondiciones y resultado pueden
representarse con O/M/A/δ, mientras la búsqueda/selección del plan permanece
como algoritmo externo.
"""

from mf_min_definitivo import Kernel, Transition


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {"id": oid, "type": typ, "value": value}))


def rel(k, rid, s, p, t):
    k.transition(Transition("add_relation", {
        "id": rid, "source": s, "predicate": p, "target": t,
    }))


def test_goal_action_precondition_and_effect_are_representable():
    k = Kernel()
    obj(k, "start", "state", "at_A")
    obj(k, "goal", "state", "at_C")
    obj(k, "move_ab", "action", "move_A_B")
    obj(k, "move_bc", "action", "move_B_C")

    rel(k, "goal_rel", "start", "requires_goal", "goal")
    rel(k, "pre", "move_ab", "precondition", "start")
    rel(k, "eff", "move_ab", "effect", "goal")

    assert k.state.relations["goal_rel"].target == "goal"
    assert k.state.relations["pre"].predicate == "precondition"
    assert k.state.relations["eff"].predicate == "effect"


def test_plan_execution_is_a_sequence_of_transitions():
    k = Kernel()
    obj(k, "s1", "state", "at_A")
    obj(k, "s2", "state", "at_B")
    obj(k, "a1", "action", "move_A_B")
    rel(k, "e1", "a1", "effect", "s2")

    assert "e1" in k.state.relations
    k.transition(Transition("add_relation", {
        "id": "exec1", "source": "s1", "predicate": "transitions_to", "target": "s2",
    }))
    assert k.state.relations["exec1"].target == "s2"


def test_core_does_not_choose_a_plan():
    k = Kernel()
    obj(k, "a", "state", "A")
    obj(k, "b", "state", "B")
    obj(k, "c", "state", "C")
    rel(k, "ab", "a", "can_reach", "b")
    rel(k, "bc", "b", "can_reach", "c")

    # La existencia del grafo no impone una función de planificación óptima.
    assert not hasattr(k, "plan")
