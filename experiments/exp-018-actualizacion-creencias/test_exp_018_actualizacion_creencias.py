import pytest
from mf_min_definitivo import Kernel, Transition, ContradictionError

def add(k, op, payload):
    k.transition(Transition(op, payload))

def belief(k, bid, hypothesis, value):
    add(k, "add_object", {"id": bid, "type": "Belief", "value": value})
    add(k, "add_relation", {
        "id": f"about_{bid}",
        "source": bid,
        "predicate": "belief_of",
        "target": hypothesis,
    })

def test_initial_belief_is_representable_as_object_data():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    assert k.state.objects["b0"].value == 0.4
    assert any(r.source == "b0" and r.predicate == "belief_of" for r in k.state.relations.values())

def test_evidence_is_representable_in_relations():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    belief(k, "b0", "h", 0.4)
    add(k, "add_relation", {"id": "supports", "source": "e", "predicate": "supports", "target": "h"})
    assert k.state.relations["supports"].source == "e"
    assert k.state.relations["supports"].target == "h"

def test_evidence_does_not_automatically_change_belief():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    belief(k, "b0", "h", 0.4)
    add(k, "add_relation", {"id": "supports", "source": "e", "predicate": "supports", "target": "h"})
    assert k.state.objects["b0"].value == 0.4

def test_update_is_a_new_state_object_not_in_place_mutation():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    before = k.state.objects["b0"].value
    belief(k, "b1", "h", 0.75)
    add(k, "add_relation", {"id": "u", "source": "b0", "predicate": "updated_to", "target": "b1"})
    assert before == 0.4
    assert k.state.objects["b0"].value == 0.4
    assert k.state.objects["b1"].value == 0.75

def test_update_can_be_applied_by_delta():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    add(k, "add_object", {"id": "b1", "type": "Belief", "value": 0.75})
    add(k, "add_relation", {"id": "about_b1", "source": "b1", "predicate": "belief_of", "target": "h"})
    add(k, "add_relation", {"id": "u", "source": "b0", "predicate": "updated_to", "target": "b1"})
    assert k.state.objects["b1"].value == 0.75
    assert k.state.relations["u"].predicate == "updated_to"

def test_update_rule_can_be_external_and_recorded_with_provenance():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    belief(k, "b0", "h", 0.4)
    belief(k, "b1", "h", 0.7)
    add(k, "add_relation", {"id": "supports", "source": "e", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {
        "id": "u", "source": "b0", "predicate": "updated_to", "target": "b1",
        "origin": "derived", "rule_id": "belief_update_rule", "premises": ("supports",)
    })
    r = k.state.relations["u"]
    assert r.origin == "derived"
    assert r.rule_id == "belief_update_rule"
    assert r.premises == ("supports",)

def test_bayesian_style_update_is_external_calculation():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "prior", "h", 0.4)
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    add(k, "add_object", {"id": "likelihood", "type": "Probability", "value": 0.8})
    add(k, "add_relation", {"id": "supports", "source": "e", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "like", "source": "e", "predicate": "has_likelihood", "target": "likelihood"})
    assert k.state.objects["prior"].value == 0.4
    assert k.state.objects["likelihood"].value == 0.8

def test_conflicting_evidence_can_be_represented_without_automatic_resolution():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e_pos", "type": "Evidence"})
    add(k, "add_object", {"id": "e_neg", "type": "Evidence"})
    add(k, "add_relation", {"id": "rp", "source": "e_pos", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "rn", "source": "e_neg", "predicate": "refutes", "target": "h"})
    assert len(k.state.relations) == 2

def test_conflicting_evidence_does_not_force_a_belief_value():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e1", "type": "Evidence"})
    add(k, "add_object", {"id": "e2", "type": "Evidence"})
    add(k, "add_relation", {"id": "r1", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r2", "source": "e2", "predicate": "refutes", "target": "h"})
    assert not any(r.predicate == "belief_value" for r in k.state.relations.values())

def test_insufficient_evidence_leaves_belief_unchanged():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    assert k.state.objects["b0"].value == 0.4
    assert not any(r.predicate == "updated_to" for r in k.state.relations.values())

def test_update_requires_explicit_computed_result():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    add(k, "add_relation", {"id": "s", "source": "e", "predicate": "supports", "target": "h"})
    assert "b1" not in k.state.objects

def test_predicate_name_does_not_execute_belief_update():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    add(k, "add_relation", {"id": "u", "source": "e", "predicate": "updates_belief", "target": "h"})
    assert k.state.objects["b0"].value == 0.4
    assert "b1" not in k.state.objects

def test_atomic_rejection_preserves_state_when_update_constraint_fails():
    k = Kernel()
    add(k, "add_axiom", {
        "id": "AX_PROB", "name": "ProbabilityRange",
        "numeric_target_type": "Belief", "min_numeric_val": 0.0, "max_numeric_val": 1.0
    })
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    before = k.state
    with pytest.raises(ContradictionError):
        add(k, "add_object", {"id": "bad", "type": "Belief", "value": 1.2})
    assert k.state == before

def test_belief_update_does_not_require_a_fifth_primitive():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    belief(k, "b1", "h", 0.75)
    add(k, "add_relation", {"id": "u", "source": "b0", "predicate": "updated_to", "target": "b1"})
    assert len(k.state.objects) == 3
    assert len(k.state.relations) == 3

def test_update_preserves_identity_of_hypothesis():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    belief(k, "b1", "h", 0.75)
    add(k, "add_relation", {"id": "u", "source": "b0", "predicate": "updated_to", "target": "b1"})
    assert k.state.relations["about_b0"].target == "h"
    assert k.state.relations["about_b1"].target == "h"

def test_update_relation_can_be_traced_to_evidence():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    belief(k, "b0", "h", 0.4)
    belief(k, "b1", "h", 0.7)
    add(k, "add_relation", {"id": "s", "source": "e", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {
        "id": "u", "source": "b0", "predicate": "updated_to", "target": "b1",
        "origin": "derived", "rule_id": "update_v1", "premises": ("s",)
    })
    assert k.state.relations["u"].premises == ("s",)

def test_missing_evidence_is_not_evidence_against_hypothesis():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    assert not any(r.target == "h" and r.predicate == "refutes" for r in k.state.relations.values())

def test_external_update_can_be_iterated_as_successive_states():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b0", "h", 0.4)
    belief(k, "b1", "h", 0.6)
    belief(k, "b2", "h", 0.8)
    add(k, "add_relation", {"id": "u1", "source": "b0", "predicate": "updated_to", "target": "b1"})
    add(k, "add_relation", {"id": "u2", "source": "b1", "predicate": "updated_to", "target": "b2"})
    assert [k.state.objects[x].value for x in ("b0", "b1", "b2")] == [0.4, 0.6, 0.8]

@pytest.mark.parametrize("value", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_belief_values_remain_ordinary_numeric_data(value):
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    belief(k, "b", "h", value)
    assert k.state.objects["b"].value == value
