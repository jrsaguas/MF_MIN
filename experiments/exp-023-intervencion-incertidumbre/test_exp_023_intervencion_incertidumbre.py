import pytest
from mf_min_definitivo import Kernel, Transition, ContradictionError

def add(k, op, payload):
    k.transition(Transition(op, payload))

def base():
    k = Kernel()
    for oid, typ in (
        ("y0", "state"), ("y1", "state"), ("y2", "state"),
        ("i1", "intervention"), ("e1", "Evidence"), ("h", "Hypothesis"),
        ("t1", "time"), ("t2", "time"),
    ):
        add(k, "add_object", {"id": oid, "type": typ})
    return k

def test_intervention_and_uncertainty_are_structurally_representable():
    k = base()
    add(k, "add_relation", {"id": "target", "source": "i1", "predicate": "targets", "target": "y0"})
    add(k, "add_relation", {"id": "before", "source": "i1", "predicate": "starts_from", "target": "y0"})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.25})
    add(k, "add_relation", {"id": "iu", "source": "i1", "predicate": "has_uncertainty", "target": "u"})
    assert len(k.state.relations) == 3

def test_intervention_result_can_be_a_new_state():
    k = base()
    add(k, "add_relation", {"id": "p", "source": "i1", "predicate": "produces", "target": "y1"})
    assert k.state.relations["p"].target == "y1"
    assert k.state.objects["y0"] != k.state.objects["y1"]

def test_uncertainty_does_not_execute_intervention():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.9})
    add(k, "add_relation", {"id": "iu", "source": "i1", "predicate": "has_uncertainty", "target": "u"})
    assert "produces" not in {r.predicate for r in k.state.relations.values()}

def test_intervention_does_not_automatically_imply_causality():
    k = base()
    add(k, "add_relation", {"id": "target", "source": "i1", "predicate": "targets", "target": "y0"})
    add(k, "add_relation", {"id": "p", "source": "i1", "predicate": "produces", "target": "y1"})
    assert not any(r.predicate == "causes" for r in k.state.relations.values())

def test_evidence_can_support_an_uncertain_intervention_result():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.4})
    add(k, "add_relation", {"id": "p", "source": "i1", "predicate": "produces", "target": "y1"})
    add(k, "add_relation", {"id": "eu", "source": "e1", "predicate": "has_uncertainty", "target": "u"})
    add(k, "add_relation", {"id": "s", "source": "e1", "predicate": "supports", "target": "h"})
    assert len(k.state.relations) == 3

def test_temporal_order_can_bound_intervention_evidence():
    k = base()
    add(k, "add_relation", {"id": "it", "source": "i1", "predicate": "occurs_at", "target": "t1"})
    add(k, "add_relation", {"id": "et", "source": "e1", "predicate": "observed_at", "target": "t2"})
    add(k, "add_relation", {"id": "tt", "source": "t1", "predicate": "before", "target": "t2"})
    assert len(k.state.relations) == 3

def test_intervention_uncertainty_can_be_recorded_with_provenance():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.3})
    add(k, "add_relation", {"id": "iu", "source": "i1", "predicate": "has_uncertainty", "target": "u"})
    add(k, "add_relation", {"id": "d", "source": "i1", "predicate": "estimated_effect", "target": "y1",
                            "origin": "derived", "rule_id": "effect_estimator",
                            "premises": ("iu",)})
    assert k.state.relations["d"].origin == "derived"
    assert k.state.relations["d"].premises == ("iu",)

def test_missing_uncertainty_is_not_zero():
    k = base()
    assert not any(r.predicate == "has_uncertainty" and r.source == "i1"
                   for r in k.state.relations.values())

def test_conflicting_intervention_evidence_can_coexist():
    k = base()
    add(k, "add_relation", {"id": "s", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_object", {"id": "e2", "type": "Evidence"})
    add(k, "add_relation", {"id": "r", "source": "e2", "predicate": "refutes", "target": "h"})
    assert len([r for r in k.state.relations.values() if r.target == "h"]) == 2

def test_same_fact_positive_negative_still_violates_i3():
    k = base()
    add(k, "add_relation", {"id": "r1", "source": "e1", "predicate": "observes", "target": "h", "polarity": True})
    with pytest.raises(ContradictionError):
        add(k, "add_relation", {"id": "r2", "source": "e1", "predicate": "observes", "target": "h", "polarity": False})
    assert len(k.state.relations) == 1

def test_intervention_branch_can_be_compared_with_baseline():
    k = base()
    add(k, "add_object", {"id": "baseline", "type": "state"})
    add(k, "add_relation", {"id": "b", "source": "baseline", "predicate": "before_intervention", "target": "y0"})
    add(k, "add_relation", {"id": "p", "source": "i1", "predicate": "produces", "target": "y1"})
    assert len(k.state.objects) == 9
    assert len(k.state.relations) == 2

def test_resolution_or_estimation_is_external():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.5})
    add(k, "add_relation", {"id": "iu", "source": "i1", "predicate": "has_uncertainty", "target": "u"})
    assert not any(r.predicate in {"resolves", "updates", "calculates"} for r in k.state.relations.values())

def test_predicate_names_do_not_execute_intervention_or_uncertainty():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.5})
    add(k, "add_relation", {"id": "x", "source": "i1", "predicate": "certainly_causes", "target": "y1"})
    assert len(k.state.relations) == 1

def test_no_fifth_primitive_is_required():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.5})
    add(k, "add_relation", {"id": "iu", "source": "i1", "predicate": "has_uncertainty", "target": "u"})
    assert len(k.state.objects) == 9
