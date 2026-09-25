import pytest
from mf_min_definitivo import Kernel, Transition, ContradictionError

def add(k, op, payload):
    k.transition(Transition(op, payload))

def base():
    k = Kernel()
    for oid, typ in (
        ("h", "Hypothesis"), ("e1", "Evidence"), ("e2", "Evidence"),
        ("a", "event"), ("b", "event"), ("t1", "time"), ("t2", "time"),
    ):
        add(k, "add_object", {"id": oid, "type": typ})
    return k

def test_temporal_evidence_is_structurally_representable():
    k = base()
    add(k, "add_relation", {"id": "at", "source": "a", "predicate": "occurs_at", "target": "t1"})
    add(k, "add_relation", {"id": "s", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "es", "source": "e1", "predicate": "observed_at", "target": "t1"})
    assert len(k.state.relations) == 3

def test_temporal_order_can_be_attached_to_evidence():
    k = base()
    add(k, "add_relation", {"id": "e1t", "source": "e1", "predicate": "observed_at", "target": "t1"})
    add(k, "add_relation", {"id": "e2t", "source": "e2", "predicate": "observed_at", "target": "t2"})
    add(k, "add_relation", {"id": "t12", "source": "t1", "predicate": "before", "target": "t2"})
    assert all(x in k.state.relations for x in ("e1t", "e2t", "t12"))

def test_uncertainty_can_be_attached_to_temporal_evidence():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.3})
    add(k, "add_relation", {"id": "eu", "source": "e1", "predicate": "has_uncertainty", "target": "u"})
    add(k, "add_relation", {"id": "et", "source": "e1", "predicate": "observed_at", "target": "t1"})
    assert k.state.objects["u"].value == 0.3

def test_uncertainty_does_not_change_temporal_order():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.8})
    add(k, "add_relation", {"id": "eu", "source": "e1", "predicate": "has_uncertainty", "target": "u"})
    add(k, "add_relation", {"id": "t12", "source": "t1", "predicate": "before", "target": "t2"})
    assert k.state.relations["t12"].predicate == "before"

def test_temporal_evidence_does_not_automatically_become_causal():
    k = base()
    add(k, "add_relation", {"id": "e1t", "source": "e1", "predicate": "observed_at", "target": "t1"})
    add(k, "add_relation", {"id": "e2t", "source": "e2", "predicate": "observed_at", "target": "t2"})
    add(k, "add_relation", {"id": "t12", "source": "t1", "predicate": "before", "target": "t2"})
    assert not any(r.predicate == "causes" for r in k.state.relations.values())

def test_missing_temporal_evidence_is_not_negative_evidence():
    k = base()
    assert not any(r.predicate == "refutes" and r.target == "h" for r in k.state.relations.values())

def test_positive_and_negative_same_temporal_fact_still_obeys_i3():
    k = base()
    add(k, "add_relation", {"id": "r1", "source": "e1", "predicate": "observes", "target": "h", "polarity": True})
    with pytest.raises(ContradictionError):
        add(k, "add_relation", {"id": "r2", "source": "e1", "predicate": "observes", "target": "h", "polarity": False})
    assert len(k.state.relations) == 1

def test_temporal_evidence_conflict_can_coexist_across_sources():
    k = base()
    add(k, "add_relation", {"id": "s", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r", "source": "e2", "predicate": "refutes", "target": "h"})
    add(k, "add_relation", {"id": "e1t", "source": "e1", "predicate": "observed_at", "target": "t1"})
    add(k, "add_relation", {"id": "e2t", "source": "e2", "predicate": "observed_at", "target": "t2"})
    assert len(k.state.relations) == 4

def test_derived_temporal_uncertain_claim_can_preserve_all_premises():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.2})
    add(k, "add_relation", {"id": "s", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "et", "source": "e1", "predicate": "observed_at", "target": "t1"})
    add(k, "add_relation", {"id": "eu", "source": "e1", "predicate": "has_uncertainty", "target": "u"})
    add(k, "add_relation", {"id": "d", "source": "h", "predicate": "temporally_supported", "target": "t1",
                            "origin": "derived", "rule_id": "temporal_evidence_rule",
                            "premises": ("s", "et", "eu")})
    assert set(k.state.relations["d"].premises) == {"s", "et", "eu"}

def test_delta_stores_temporal_uncertainty_without_special_operation():
    k = base()
    before = k.state
    add(k, "add_relation", {"id": "et", "source": "e1", "predicate": "observed_at", "target": "t1"})
    assert k.state != before

def test_multiple_temporal_uncertainties_do_not_normalize_automatically():
    k = base()
    for oid, value in (("u1", 0.2), ("u2", 0.8)):
        add(k, "add_object", {"id": oid, "type": "Uncertainty", "value": value})
    assert k.state.objects["u1"].value + k.state.objects["u2"].value == pytest.approx(1.0)
    add(k, "add_object", {"id": "u3", "type": "Uncertainty", "value": 0.8})
    assert sum(k.state.objects[x].value for x in ("u1", "u2", "u3")) == pytest.approx(1.8)

def test_temporal_constraint_can_be_explicit_without_new_primitive():
    k = base()
    add(k, "add_axiom", {"id": "AX_TIME", "name": "TemporalEvidenceConstraint"})
    add(k, "add_relation", {"id": "et", "source": "e1", "predicate": "observed_at", "target": "t1"})
    assert "AX_TIME" in k.state.axioms

def test_predicate_name_does_not_execute_temporal_uncertainty_reasoning():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.4})
    add(k, "add_relation", {"id": "x", "source": "e1", "predicate": "probably_before", "target": "e2"})
    assert k.state.objects["u"].value == 0.4

def test_resolution_of_temporal_uncertainty_is_external():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.4})
    add(k, "add_relation", {"id": "et", "source": "e1", "predicate": "observed_at", "target": "t1"})
    add(k, "add_relation", {"id": "eu", "source": "e1", "predicate": "has_uncertainty", "target": "u"})
    assert not any(r.predicate == "resolves" for r in k.state.relations.values())

def test_no_fifth_primitive_is_required():
    k = base()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.5})
    add(k, "add_relation", {"id": "et", "source": "e1", "predicate": "observed_at", "target": "t1"})
    add(k, "add_relation", {"id": "eu", "source": "e1", "predicate": "has_uncertainty", "target": "u"})
    assert len(k.state.objects) == 8
