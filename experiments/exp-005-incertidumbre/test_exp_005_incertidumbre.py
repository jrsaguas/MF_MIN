"""EXP-005 — Incertidumbre en MF_MIN.

Evalúa si distintos estados epistémicos pueden representarse mediante
relaciones y objetos sin introducir una quinta primitiva.
"""

from mf_min_definitivo import Kernel, Transition


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {"id": oid, "type": typ, "value": value}))


def rel(k, rid, s, p, t, polarity=True):
    k.transition(Transition("add_relation", {
        "id": rid, "source": s, "predicate": p, "target": t,
        "polarity": polarity,
    }))


def test_uncertain_claim_can_be_represented_without_claiming_truth():
    k = Kernel()
    obj(k, "obs1", "observation", "sensor")
    obj(k, "hyp1", "hypothesis", "lluvia")
    rel(k, "supports", "obs1", "supports", "hyp1")
    assert k.state.relations["supports"].predicate == "supports"


def test_positive_and_negative_claims_are_distinct_relational_states():
    k = Kernel()
    obj(k, "a", "event")
    obj(k, "b", "event")
    rel(k, "yes", "a", "causes", "b", True)
    rel(k, "no", "a", "causes", "b", False)
    assert k.state.relations["yes"].polarity is True
    assert k.state.relations["no"].polarity is False


def test_probability_is_not_invented_by_core():
    k = Kernel()
    obj(k, "h", "hypothesis")
    obj(k, "v", "value")
    rel(k, "r", "h", "has_estimate", "v")

    # El núcleo representa un valor si se proporciona, pero no interpreta
    # automáticamente la relación como probabilidad ni asigna un número.
    assert k.state.relations["r"].predicate == "has_estimate"
    assert not hasattr(k.state.relations["r"], "probability")
