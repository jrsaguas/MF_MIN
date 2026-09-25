"""EXP-016 — Soporte y evidencia.

Hipótesis: soporte/evidencia puede representarse mediante O/M/A/δ sin una
quinta primitiva, pero el núcleo no convierte por sí mismo una relación
supports en grado de confianza, probabilidad ni creencia actualizada.
"""
import pytest
from mf_min_definitivo import ContradictionError, Kernel, Transition


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {"id": oid, "type": typ, "value": value}))


def rel(k, rid, s, p, t, polarity=True, origin="asserted", premises=(), rule_id=None):
    k.transition(Transition("add_relation", {
        "id": rid, "source": s, "predicate": p, "target": t,
        "polarity": polarity, "origin": origin,
        "premises": premises, "rule_id": rule_id,
    }))


def test_evidence_can_support_a_hypothesis():
    k = Kernel()
    obj(k, "obs1", "observation", "sensor_A")
    obj(k, "h1", "hypothesis", "rain")
    rel(k, "e1", "obs1", "supports", "h1")
    assert ("obs1", "h1") == (
        k.state.relations["e1"].source,
        k.state.relations["e1"].target,
    )


def test_multiple_evidence_sources_are_explicit_relations():
    k = Kernel()
    for oid in ("obs1", "obs2", "obs3"):
        obj(k, oid, "observation")
    obj(k, "h1", "hypothesis")
    for i, obs in enumerate(("obs1", "obs2", "obs3"), 1):
        rel(k, f"e{i}", obs, "supports", "h1")
    assert len([r for r in k.state.relations.values() if r.predicate == "supports"]) == 3


def test_support_does_not_become_probability_automatically():
    k = Kernel()
    obj(k, "obs", "observation")
    obj(k, "h", "hypothesis")
    rel(k, "e", "obs", "supports", "h")
    assert not hasattr(k.state.relations["e"], "probability")


def test_support_does_not_become_truth_automatically():
    k = Kernel()
    obj(k, "obs", "observation")
    obj(k, "h", "hypothesis")
    rel(k, "e", "obs", "supports", "h")
    assert k.state.relations["e"].polarity is True
    assert k.state.relations["e"].predicate == "supports"


def test_negative_evidence_is_explicit_not_absence():
    k = Kernel()
    obj(k, "obs", "observation")
    obj(k, "h", "hypothesis")
    rel(k, "e", "obs", "supports", "h", polarity=False)
    assert k.state.relations["e"].polarity is False


def test_positive_and_negative_same_fact_trigger_i3():
    k = Kernel()
    obj(k, "obs", "observation")
    obj(k, "h", "hypothesis")
    rel(k, "yes", "obs", "supports", "h", True)
    with pytest.raises(ContradictionError):
        rel(k, "no", "obs", "supports", "h", False)


def test_evidence_provenance_can_be_preserved_in_derived_claim():
    k = Kernel()
    obj(k, "o1", "observation")
    obj(k, "o2", "observation")
    obj(k, "h", "hypothesis")
    rel(k, "e1", "o1", "supports", "h")
    rel(k, "e2", "o2", "supports", "h")
    rel(k, "claim", "o1", "corroborates", "h",
        origin="derived", premises=("e1", "e2"), rule_id="corroboration_rule")
    r = k.state.relations["claim"]
    assert r.origin == "derived"
    assert r.premises == ("e1", "e2")
    assert r.rule_id == "corroboration_rule"


def test_missing_evidence_is_not_negative_evidence():
    k = Kernel()
    obj(k, "obs", "observation")
    obj(k, "h", "hypothesis")
    assert not any(r.source == "obs" and r.target == "h"
                   and r.predicate == "supports" for r in k.state.relations.values())


def test_support_relation_has_no_builtin_weight_field():
    k = Kernel()
    obj(k, "obs", "observation")
    obj(k, "h", "hypothesis")
    rel(k, "e", "obs", "supports", "h")
    r = k.state.relations["e"]
    assert not hasattr(r, "weight")
    assert not hasattr(r, "confidence")


def test_axiom_can_constrain_evidence_structure_without_new_primitive():
    k = Kernel()
    obj(k, "obs", "observation")
    obj(k, "h", "hypothesis")
    k.transition(Transition("add_axiom", {
        "id": "a1", "name": "evidence_constraint",
        "body": ({"predicate": "supports", "source": "obs", "target": "h"},)
    }))
    with pytest.raises(Exception):
        rel(k, "e", "obs", "supports", "h")


def test_delta_only_stores_evidence_and_does_not_update_belief():
    k = Kernel()
    obj(k, "obs", "observation")
    obj(k, "h", "hypothesis")
    rel(k, "e", "obs", "supports", "h")
    assert not any(r.predicate in {"believes", "probability", "confidence"}
                   for r in k.state.relations.values())


def test_support_is_core_expressible():
    k = Kernel()
    obj(k, "obs", "observation")
    obj(k, "h", "hypothesis")
    rel(k, "e", "obs", "supports", "h")
    assert len(k.state.objects) == 2
    assert len(k.state.relations) == 1


def test_strong_evidence_semantics_remain_external():
    k = Kernel()
    obj(k, "obs", "observation")
    obj(k, "h", "hypothesis")
    rel(k, "e", "obs", "supports", "h")
    assert k.state.relations["e"].predicate == "supports"
