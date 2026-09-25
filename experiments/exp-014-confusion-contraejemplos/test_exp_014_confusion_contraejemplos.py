"""EXP-014 — Confusión y contraejemplos.

Hipótesis:
Una intervención y un cambio posterior pueden representarse en O/M/A/δ,
pero una asociación observacional o un cambio coincidente no basta para
atribuir el efecto a la intervención. Los factores de confusión deben
representarse explícitamente y su análisis queda fuera del significado
intrínseco del núcleo.
"""

from mf_min_definitivo import Kernel, Transition


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {
        "id": oid, "type": typ, "value": value
    }))


def rel(k, rid, source, predicate, target, polarity=True):
    k.transition(Transition("add_relation", {
        "id": rid,
        "source": source,
        "predicate": predicate,
        "target": target,
        "polarity": polarity,
    }))


def base():
    k = Kernel()
    obj(k, "x", "exposure", 1)
    obj(k, "y", "outcome", 1)
    obj(k, "c", "confounder", 1)
    obj(k, "s0", "state")
    obj(k, "s1", "state")
    return k


def pairs(k, predicate):
    return {
        (r.source, r.target)
        for r in k.state.relations.values()
        if r.predicate == predicate
    }


def test_confounder_is_representable_as_object_and_relations():
    k = base()
    rel(k, "r1", "c", "associated_with", "x")
    rel(k, "r2", "c", "associated_with", "y")
    assert pairs(k, "associated_with") == {("c", "x"), ("c", "y")}


def test_association_does_not_automatically_become_causation():
    k = base()
    rel(k, "r1", "x", "associated_with", "y")
    assert pairs(k, "associated_with") == {("x", "y")}
    assert pairs(k, "causes") == set()


def test_common_cause_structure_can_be_explicit_without_causal_inference():
    k = base()
    rel(k, "r1", "c", "associated_with", "x")
    rel(k, "r2", "c", "associated_with", "y")
    rel(k, "r3", "x", "associated_with", "y")
    assert pairs(k, "causes") == set()
    assert pairs(k, "associated_with") == {
        ("c", "x"), ("c", "y"), ("x", "y")
    }


def test_observed_change_after_intervention_is_not_sufficient_for_attribution():
    k = base()
    obj(k, "i", "intervention")
    rel(k, "r1", "i", "targets", "x")
    rel(k, "r2", "i", "produces", "s1")
    rel(k, "r3", "s1", "has_outcome", "y")
    rel(k, "r4", "c", "associated_with", "y")
    assert pairs(k, "produces") == {("i", "s1")}
    assert pairs(k, "has_outcome") == {("s1", "y")}
    assert pairs(k, "causes") == set()


def test_counterexample_same_outcome_can_be_present_without_intervention():
    observed = base()
    no_intervention = base()
    rel(observed, "r1", "x", "associated_with", "y")
    rel(observed, "r2", "s1", "has_outcome", "y")
    rel(no_intervention, "r1", "s1", "has_outcome", "y")
    assert pairs(observed, "has_outcome") == {("s1", "y")}
    assert pairs(no_intervention, "has_outcome") == {("s1", "y")}
    assert pairs(no_intervention, "produces") == set()


def test_baseline_and_intervention_branches_can_be_compared():
    baseline = base()
    intervention = base()
    obj(intervention, "i", "intervention")
    rel(intervention, "r1", "i", "targets", "x")
    rel(intervention, "r2", "i", "produces", "s1")
    rel(intervention, "r3", "s1", "has_outcome", "y")
    assert pairs(baseline, "produces") == set()
    assert pairs(intervention, "produces") == {("i", "s1")}


def test_relation_name_confounder_does_not_impose_confounding_semantics():
    k = base()
    rel(k, "r1", "c", "confounds", "x")
    rel(k, "r2", "x", "confounds", "c")
    assert pairs(k, "confounds") == {("c", "x"), ("x", "c")}


def test_negative_association_can_be_stored_as_an_explicit_claim():
    k = base()
    rel(k, "r1", "x", "associated_with", "y", polarity=True)
    rel(k, "r2", "c", "associated_with", "y", polarity=False)
    assert k.state.relations["r1"].polarity is True
    assert k.state.relations["r2"].polarity is False


def test_conditioning_is_external_algorithmic_structure():
    k = base()
    rel(k, "r1", "c", "associated_with", "x")
    rel(k, "r2", "c", "associated_with", "y")
    rel(k, "r3", "x", "associated_with", "y")
    associated = pairs(k, "associated_with")
    conditioned = {
        ("x", "y")
    } if ("c", "x") in associated and ("c", "y") in associated else set()
    assert conditioned == {("x", "y")}
    assert pairs(k, "causes") == set()


def test_delta_stores_counterexample_structure_without_special_operation():
    k = base()
    before = len(k.state.relations)
    rel(k, "r1", "x", "associated_with", "y")
    assert len(k.state.relations) == before + 1


def test_no_new_primitive_is_justified_by_confounding_representation():
    k = base()
    rel(k, "r1", "c", "associated_with", "x")
    rel(k, "r2", "c", "associated_with", "y")
    assert k.state.objects["c"].type == "confounder"
    assert pairs(k, "associated_with") == {("c", "x"), ("c", "y")}


def test_strong_causal_attribution_remains_open():
    k = base()
    obj(k, "i", "intervention")
    rel(k, "r1", "i", "targets", "x")
    rel(k, "r2", "i", "produces", "s1")
    rel(k, "r3", "c", "associated_with", "y")
    assert pairs(k, "targets") == {("i", "x")}
    assert pairs(k, "produces") == {("i", "s1")}
    assert pairs(k, "causes") == set()
