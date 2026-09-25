import pytest
from mf_min_definitivo import Kernel, Transition, ContradictionError

def add(k, op, payload):
    k.transition(Transition(op, payload))

def test_probability_value_is_storable_as_object_data():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "p", "type": "Probability", "value": 0.8})
    add(k, "add_relation", {"id": "r", "source": "h", "predicate": "has_probability", "target": "p"})
    assert k.state.objects["p"].value == 0.8

def test_zero_and_one_are_valid_numeric_values():
    k = Kernel()
    add(k, "add_object", {"id": "p0", "type": "Probability", "value": 0.0})
    add(k, "add_object", {"id": "p1", "type": "Probability", "value": 1.0})
    assert {k.state.objects["p0"].value, k.state.objects["p1"].value} == {0.0, 1.0}

def test_axiom_can_constrain_probability_range():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX_PROB", "name": "ProbabilityRange",
                         "numeric_target_type": "Probability",
                         "min_numeric_val": 0.0, "max_numeric_val": 1.0})
    add(k, "add_object", {"id": "ok", "type": "Probability", "value": 0.8})
    before = k.state
    with pytest.raises(ContradictionError):
        add(k, "add_object", {"id": "bad", "type": "Probability", "value": 1.2})
    assert k.state == before

def test_negative_probability_is_rejected_by_range_axiom():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX_PROB", "name": "ProbabilityRange",
                         "numeric_target_type": "Probability",
                         "min_numeric_val": 0.0, "max_numeric_val": 1.0})
    with pytest.raises(ContradictionError):
        add(k, "add_object", {"id": "bad", "type": "Probability", "value": -0.1})

def test_probability_name_does_not_create_probability_semantics():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "p", "type": "Probability", "value": 0.8})
    add(k, "add_relation", {"id": "r", "source": "h", "predicate": "has_probability", "target": "p"})
    assert "has_probability" in {r.predicate for r in k.state.relations.values()}
    assert not hasattr(k.state.relations["r"], "measure_semantics")

def test_two_values_can_be_stored_without_automatic_normalization():
    k = Kernel()
    for oid, typ in [("h1", "Hypothesis"), ("h2", "Hypothesis"),
                     ("p1", "Probability"), ("p2", "Probability")]:
        add(k, "add_object", {"id": oid, "type": typ,
                              **({"value": 0.8} if oid.startswith("p") else {})})
    add(k, "add_relation", {"id": "r1", "source": "h1", "predicate": "has_probability", "target": "p1"})
    add(k, "add_relation", {"id": "r2", "source": "h2", "predicate": "has_probability", "target": "p2"})
    assert k.state.objects["p1"].value + k.state.objects["p2"].value == pytest.approx(1.6)

def test_probability_calculus_is_not_performed_by_delta():
    k = Kernel()
    add(k, "add_object", {"id": "a", "type": "Probability", "value": 0.2})
    add(k, "add_object", {"id": "b", "type": "Probability", "value": 0.5})
    before = k.state
    add(k, "add_relation", {"id": "r", "source": "a", "predicate": "multiplies_with", "target": "b"})
    assert k.state.objects["a"].value == 0.2 and k.state.objects["b"].value == 0.5
    assert k.state != before

def test_conditional_probability_can_be_structured_without_builtin_update():
    k = Kernel()
    for oid, typ in [("a", "Event"), ("b", "Event"), ("p", "Probability")]:
        add(k, "add_object", {"id": oid, "type": typ,
                              **({"value": 0.7} if oid == "p" else {})})
    add(k, "add_relation", {"id": "r1", "source": "p", "predicate": "estimates_conditional", "target": "a"})
    add(k, "add_relation", {"id": "r2", "source": "p", "predicate": "conditioned_on", "target": "b"})
    assert len(k.state.relations) == 2
def test_bayes_update_requires_external_algorithm():
    k = Kernel()
    add(k, "add_object", {"id": "prior", "type": "Probability", "value": 0.4})
    add(k, "add_object", {"id": "evidence", "type": "Evidence"})
    add(k, "add_relation", {"id": "r", "source": "evidence", "predicate": "supports", "target": "prior"})
    assert k.state.objects["prior"].value == 0.4

def test_probability_can_be_represented_with_provenance():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "p", "type": "Probability", "value": 0.6})
    add(k, "add_relation", {"id": "e1", "source": "h", "predicate": "supported_by", "target": "h"})
    add(k, "add_relation", {"id": "e2", "source": "h", "predicate": "estimated_from", "target": "h"})
    add(k, "add_relation", {"id": "r", "source": "h", "predicate": "has_probability",
                            "target": "p", "origin": "derived", "rule_id": "prob_rule",
                            "premises": ("e1", "e2")})
    r = k.state.relations["r"]
    assert r.origin == "derived" and r.rule_id == "prob_rule" and r.premises == ("e1", "e2")

def test_missing_probability_is_not_probability_zero():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    assert not any(r.source == "h" and r.predicate == "has_probability" for r in k.state.relations.values())

def test_probability_semantics_do_not_require_fifth_primitive():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "p", "type": "Probability", "value": 0.75})
    add(k, "add_relation", {"id": "r", "source": "h", "predicate": "has_probability", "target": "p"})
    assert len(k.state.objects) == 2 and len(k.state.relations) == 1

@pytest.mark.parametrize("value", [0.0, 0.25, 0.5, 0.999999, 1.0])
def test_finite_probability_values_are_ordinary_numeric_objects(value):
    k = Kernel()
    add(k, "add_object", {"id": "p", "type": "Probability", "value": value})
    assert k.state.objects["p"].value == value
