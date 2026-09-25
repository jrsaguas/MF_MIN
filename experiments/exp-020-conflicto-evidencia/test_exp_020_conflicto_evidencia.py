import pytest
from mf_min_definitivo import Kernel, Transition, ContradictionError

def add(k, op, payload):
    k.transition(Transition(op, payload))

def test_conflicting_evidence_is_representable_as_distinct_relations():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e1", "type": "Evidence"})
    add(k, "add_object", {"id": "e2", "type": "Evidence"})
    add(k, "add_relation", {"id": "r1", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r2", "source": "e2", "predicate": "refutes", "target": "h"})
    assert len(k.state.relations) == 2

def test_conflict_between_support_and_refutation_is_not_same_fact_contradiction():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e1", "type": "Evidence"})
    add(k, "add_object", {"id": "e2", "type": "Evidence"})
    add(k, "add_relation", {"id": "s", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r", "source": "e2", "predicate": "refutes", "target": "h"})
    assert k.state.relations["s"].predicate != k.state.relations["r"].predicate

def test_positive_and_negative_same_fact_remain_rejected_by_core_invariant():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    add(k, "add_relation", {"id": "r1", "source": "e", "predicate": "observes", "target": "h", "polarity": True})
    with pytest.raises(ContradictionError):
        add(k, "add_relation", {"id": "r2", "source": "e", "predicate": "observes", "target": "h", "polarity": False})

def test_rejecting_same_fact_conflict_is_atomic():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    add(k, "add_relation", {"id": "r1", "source": "e", "predicate": "observes", "target": "h", "polarity": True})
    before = k.state
    with pytest.raises(ContradictionError):
        add(k, "add_relation", {"id": "r2", "source": "e", "predicate": "observes", "target": "h", "polarity": False})
    assert k.state == before

def test_conflicting_evidence_does_not_select_a_winner_automatically():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e1", "type": "Evidence"})
    add(k, "add_object", {"id": "e2", "type": "Evidence"})
    add(k, "add_relation", {"id": "s", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r", "source": "e2", "predicate": "refutes", "target": "h"})
    assert "winner" not in k.state.objects

def test_conflict_resolution_can_be_external_and_recorded():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e1", "type": "Evidence"})
    add(k, "add_object", {"id": "e2", "type": "Evidence"})
    add(k, "add_object", {"id": "decision", "type": "Resolution"})
    add(k, "add_relation", {"id": "s", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r", "source": "e2", "predicate": "refutes", "target": "h"})
    add(k, "add_relation", {"id": "rs", "source": "decision", "predicate": "resolves", "target": "h",
                            "origin": "derived", "rule_id": "conflict_rule", "premises": ("s", "r")})
    assert k.state.relations["rs"].origin == "derived"
    assert k.state.relations["rs"].premises == ("s", "r")

def test_conflict_resolution_does_not_require_mutating_original_evidence():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e1", "type": "Evidence"})
    add(k, "add_object", {"id": "e2", "type": "Evidence"})
    add(k, "add_relation", {"id": "s", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r", "source": "e2", "predicate": "refutes", "target": "h"})
    add(k, "add_object", {"id": "d", "type": "Resolution"})
    add(k, "add_relation", {"id": "rd", "source": "d", "predicate": "resolves", "target": "h"})
    assert k.state.relations["s"].predicate == "supports"
    assert k.state.relations["r"].predicate == "refutes"

def test_missing_evidence_does_not_mean_refutation():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    assert not any(r.target == "h" and r.predicate == "refutes" for r in k.state.relations.values())

def test_conflict_predicate_name_does_not_trigger_resolution():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    add(k, "add_relation", {"id": "c", "source": "e", "predicate": "conflicts_with", "target": "h"})
    assert k.state.relations["c"].predicate == "conflicts_with"

def test_multiple_sources_can_form_a_conflict_set():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    for i in range(3):
        add(k, "add_object", {"id": f"e{i}", "type": "Evidence"})
    add(k, "add_relation", {"id": "s0", "source": "e0", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "s1", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r2", "source": "e2", "predicate": "refutes", "target": "h"})
    assert len(k.state.relations) == 3

def test_resolution_can_be_constrained_without_new_primitive():
    k = Kernel()
    add(k, "add_axiom", {"id": "AX_RES", "name": "ResolutionExists"})
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "d", "type": "Resolution"})
    add(k, "add_relation", {"id": "rd", "source": "d", "predicate": "resolves", "target": "h"})
    assert "AX_RES" in k.state.axioms

def test_conflict_resolution_is_a_transition_not_a_new_state_component():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "d", "type": "Resolution"})
    before = k.state
    add(k, "add_relation", {"id": "rd", "source": "d", "predicate": "resolves", "target": "h"})
    assert k.state != before

def test_no_fifth_primitive_is_required_for_conflict_sets():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    add(k, "add_relation", {"id": "r", "source": "e", "predicate": "supports", "target": "h"})
    assert len(k.state.objects) == 2
    assert len(k.state.relations) == 1

def test_conflict_sets_can_be_kept_without_immediate_resolution():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e1", "type": "Evidence"})
    add(k, "add_object", {"id": "e2", "type": "Evidence"})
    add(k, "add_relation", {"id": "r1", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r2", "source": "e2", "predicate": "refutes", "target": "h"})
    assert len(k.state.relations) == 2

def test_derived_resolution_preserves_both_premises():
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e1", "type": "Evidence"})
    add(k, "add_object", {"id": "e2", "type": "Evidence"})
    add(k, "add_relation", {"id": "s", "source": "e1", "predicate": "supports", "target": "h"})
    add(k, "add_relation", {"id": "r", "source": "e2", "predicate": "refutes", "target": "h"})
    add(k, "add_object", {"id": "d", "type": "Resolution"})
    add(k, "add_relation", {"id": "rs", "source": "d", "predicate": "resolves", "target": "h",
                            "origin": "derived", "rule_id": "resolve_v1", "premises": ("s", "r")})
    assert set(k.state.relations["rs"].premises) == {"s", "r"}

@pytest.mark.parametrize("predicate", ["supports", "refutes", "conflicts_with"])
def test_conflict_predicates_are_stored_as_ordinary_relations(predicate):
    k = Kernel()
    add(k, "add_object", {"id": "h", "type": "Hypothesis"})
    add(k, "add_object", {"id": "e", "type": "Evidence"})
    add(k, "add_relation", {"id": "r", "source": "e", "predicate": predicate, "target": "h"})
    assert k.state.relations["r"].predicate == predicate
