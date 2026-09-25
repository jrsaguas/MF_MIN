import pytest
from mf_min_definitivo import Kernel, Transition, ContradictionError

def add(k, op, payload):
    k.transition(Transition(op, payload))

def test_uncertainty_bounds_are_representable_with_axioms():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX_U", "name": "UncertaintyRange",
                         "numeric_target_type": "Uncertainty",
                         "min_numeric_val": 0.0, "max_numeric_val": 1.0})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.35})
    assert k.state.objects["u"].value == 0.35

def test_out_of_range_uncertainty_is_rejected_atomically():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX_U", "name": "UncertaintyRange",
                         "numeric_target_type": "Uncertainty",
                         "min_numeric_val": 0.0, "max_numeric_val": 1.0})
    before = k.state
    with pytest.raises(ContradictionError):
        add(k, "add_object", {"id": "bad", "type": "Uncertainty", "value": 1.2})
    assert k.state == before

def test_uncertainty_can_be_attached_to_a_claim():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.2})
    add(k, "add_relation", {"id": "r", "source": "h", "predicate": "has_uncertainty", "target": "u"})
    assert k.state.relations["r"].target == "u"

def test_constraint_does_not_create_uncertainty_semantics():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX_U", "name": "UncertaintyRange",
                         "numeric_target_type": "Uncertainty",
                         "min_numeric_val": 0.0, "max_numeric_val": 1.0})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.7})
    assert not hasattr(k.state.objects["u"], "probability_distribution")

def test_multiple_uncertainty_values_do_not_automatically_normalize():
    k = Kernel()
    for oid, value in [("u1", 0.2), ("u2", 0.3), ("u3", 0.9)]:
        add(k, "add_object", {"id": oid, "type": "Uncertainty", "value": value})
    assert sum(k.state.objects[x].value for x in ("u1", "u2", "u3")) == pytest.approx(1.4)

def test_uncertainty_constraint_can_coexist_with_evidence():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX_U", "name": "UncertaintyRange",
                         "numeric_target_type": "Uncertainty",
                         "min_numeric_val": 0.0, "max_numeric_val": 1.0})
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.4})
    add(k, "add_relation", {"id": "s", "source": "e", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "hu", "source": "h", "predicate": "has_uncertainty", "target": "u"})
    assert len(k.state.relations) == 2

def test_uncertainty_does_not_automatically_change_belief():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "b", "type": "Belief", "value": 0.5})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.2})
    add(k, "add_relation", {"id": "bu", "source": "b", "predicate": "has_uncertainty", "target": "u"})
    assert k.state.objects["b"].value == 0.5

def test_constraints_can_relate_multiple_numeric_quantities_without_new_primitive():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX_P", "name": "ProbabilityRange",
                         "numeric_target_type": "Probability",
                         "min_numeric_val": 0.0, "max_numeric_val": 1.0})
    add(k, "add_axiom", {"id": "AX_U", "name": "UncertaintyRange",
                         "numeric_target_type": "Uncertainty",
                         "min_numeric_val": 0.0, "max_numeric_val": 1.0})
    add(k, "add_object", {"id": "p", "type": "Probability", "value": 0.8})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.2})
    assert k.state.objects["p"].value + k.state.objects["u"].value == pytest.approx(1.0)

def test_delta_stores_constrained_uncertainty_but_does_not_solve_constraints():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX_U", "name": "UncertaintyRange",
                         "numeric_target_type": "Uncertainty",
                         "min_numeric_val": 0.0, "max_numeric_val": 1.0})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.4})
    before = k.state
    add(k, "add_relation", {"id": "r", "source": "u", "predicate": "constrained_by", "target": "u"})
    assert k.state != before
    assert k.state.objects["u"].value == 0.4

def test_conflicting_numeric_constraints_are_rejected_by_validation():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX1", "name": "Low",
                         "numeric_target_type": "Uncertainty",
                         "min_numeric_val": 0.0, "max_numeric_val": 0.4})
    add(k, "add_axiom", {"id": "AX2", "name": "High",
                         "numeric_target_type": "Uncertainty",
                         "min_numeric_val": 0.6, "max_numeric_val": 1.0})
    before = k.state
    with pytest.raises(ContradictionError):
        add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.5})
    assert k.state == before

def test_missing_uncertainty_is_not_zero_uncertainty():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    assert not any(r.source == "h" and r.predicate == "has_uncertainty" for r in k.state.relations.values())

def test_uncertainty_predicate_name_does_not_execute_reasoning():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.3})
    add(k, "add_relation", {"id": "r", "source": "h", "predicate": "uncertain_about", "target": "u"})
    assert k.state.objects["u"].value == 0.3

def test_derived_uncertainty_can_preserve_provenance():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.25})
    add(k, "add_relation", {"id": "s", "source": "e", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r", "source": "h", "predicate": "has_uncertainty",
                            "target": "u", "origin": "derived", "rule_id": "uncertainty_rule",
                            "premises": ("s",)})
    assert k.state.relations["r"].origin == "derived"
    assert k.state.relations["r"].premises == ("s",)

def test_constraint_failure_is_not_an_uncertainty_value():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX_U", "name": "UncertaintyRange",
                         "numeric_target_type": "Uncertainty",
                         "min_numeric_val": 0.0, "max_numeric_val": 1.0})
    with pytest.raises(ContradictionError):
        add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": -0.1})
    assert "u" not in k.state.objects

def test_no_fifth_primitive_is_required_for_constrained_uncertainty():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": 0.45})
    add(k, "add_relation", {"id": "r", "source": "h", "predicate": "has_uncertainty", "target": "u"})
    assert len(k.state.objects) == 2
    assert len(k.state.relations) == 1

@pytest.mark.parametrize("value", [0.0, 0.1, 0.5, 0.9, 1.0])
def test_boundary_values_are_ordinary_numeric_data(value):
    k = Kernel()
    add(k, "add_object", {"id": "u", "type": "Uncertainty", "value": value})
    assert k.state.objects["u"].value == value
