"""EXP-007 — Aprendizaje sobre MF_MIN.

Prueba que experiencia, resultado y modificación del estado pueden
representarse con O/M/A/δ, mientras el algoritmo que generaliza o actualiza
reglas permanece fuera del núcleo.
"""

from mf_min_definitivo import Kernel, Transition, state_from_dict, state_to_dict


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {"id": oid, "type": typ, "value": value}))


def rel(k, rid, s, p, t, origin="asserted", premises=()):
    k.transition(Transition("add_relation", {
        "id": rid, "source": s, "predicate": p, "target": t,
        "origin": origin, "premises": premises,
    }))


def test_experience_and_outcome_are_representable():
    k = Kernel()
    obj(k, "trial1", "episode")
    obj(k, "action1", "action", "move")
    obj(k, "success1", "outcome", True)
    rel(k, "performed", "trial1", "performed", "action1")
    rel(k, "result", "trial1", "has_result", "success1")
    assert k.state.relations["performed"].target == "action1"
    assert k.state.relations["result"].target == "success1"


def test_learning_can_add_a_derived_generalization():
    k = Kernel()
    obj(k, "case1", "case")
    obj(k, "action1", "action", "move")
    obj(k, "rule1", "rule")
    rel(k, "p1", "case1", "supports", "rule1")
    rel(k, "g1", "rule1", "suggests", "action1", origin="derived", premises=("p1",))
    assert k.state.relations["g1"].origin == "derived"
    assert k.state.relations["g1"].premises == ("p1",)


def test_learning_requires_an_external_update_algorithm():
    k = Kernel()
    obj(k, "r", "rule", "if_A_then_B")
    snapshot = state_to_dict(k.state)

    # El núcleo puede conservar y cambiar el estado, pero no define por sí
    # mismo qué generalización debe aprender de una experiencia.
    restored = state_from_dict(snapshot)
    assert restored.objects["r"].value == "if_A_then_B"
    assert not hasattr(k, "learning_algorithm")
