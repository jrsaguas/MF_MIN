import pytest
from mf_min_definitivo import Kernel, Transition, ContradictionError

def add(k, op, payload):
    k.transition(Transition(op, payload))

def obj(k, oid, typ, value=None):
    p = {"id": oid, "type": typ}
    if value is not None:
        p["value"] = value
    add(k, "add_object", p)

def rel(k, rid, s, p, t, **kw):
    payload = {"id": rid, "source": s, "predicate": p, "target": t}
    payload.update(kw)
    add(k, "add_relation", payload)

def test_default_rule_structure_is_representable():
    k = Kernel()
    obj(k, "bird", "Bird")
    obj(k, "flies", "Property")
    obj(k, "rule", "Rule")
    rel(k, "r1", "rule", "applies_to", "bird")
    rel(k, "r2", "rule", "concludes", "flies")
    assert len(k.state.objects) == 3
    assert len(k.state.relations) == 2

def test_exception_structure_is_representable():
    k = Kernel()
    obj(k, "bird", "Bird")
    obj(k, "penguin", "Exception")
    obj(k, "flies", "Property")
    rel(k, "is_bird", "penguin", "is_a", "bird")
    rel(k, "exception", "penguin", "exception_to", "flies")
    assert len(k.state.relations) == 2

def test_absence_of_exception_does_not_trigger_default_inference():
    k = Kernel()
    obj(k, "bird", "Bird")
    obj(k, "flies", "Property")
    rel(k, "is_bird", "bird", "is_a", "bird")
    assert not any(r.target == "flies" for r in k.state.relations.values())

def test_predicate_names_do_not_activate_non_monotonic_reasoning():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    rel(k, "magic", "a", "normally_implies", "b")
    assert len(k.state.relations) == 1

def test_explicit_negative_information_is_distinct_from_missing_information():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    rel(k, "not_fly", "a", "flies", "b", polarity=False)
    assert k.state.relations["not_fly"].polarity is False
    assert not any(r.predicate == "flies" and r.target == "b" and r.polarity is True
                   for r in k.state.relations.values())

def test_same_fact_positive_negative_remains_forbidden():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    rel(k, "yes", "a", "flies", "b", polarity=True)
    with pytest.raises(ContradictionError):
        rel(k, "no", "a", "flies", "b", polarity=False)

def test_external_default_inference_can_be_recorded_with_provenance():
    k = Kernel()
    obj(k, "tweety", "Bird")
    obj(k, "Bird", "Class")
    obj(k, "flies", "Property")
    rel(k, "bird_fact", "tweety", "is_a", "Bird")
    rel(k, "default_fly", "tweety", "flies", "flies",
        origin="derived", rule_id="default_bird_flies", premises=("bird_fact",))
    assert k.state.relations["default_fly"].origin == "derived"
    assert k.state.relations["default_fly"].rule_id == "default_bird_flies"
def test_exception_can_be_added_after_default_and_external_algorithm_can_retract():
    k = Kernel()
    obj(k, "tweety", "Bird")
    obj(k, "Bird", "Class")
    obj(k, "flies", "Property")
    obj(k, "penguin", "Exception")
    rel(k, "bird_fact", "tweety", "is_a", "Bird")
    rel(k, "default_fly", "tweety", "flies", "flies",
        origin="derived", rule_id="default_bird_flies", premises=("bird_fact",))
    rel(k, "exception", "tweety", "exception_to", "flies")
    add(k, "remove_relation", {"id": "default_fly"})
    assert "default_fly" not in k.state.relations
    assert "exception" in k.state.relations

def test_removal_is_a_delta_operation_not_a_new_primitive():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    rel(k, "r", "a", "flies", "b")
    before = len(k.state.relations)
    add(k, "remove_relation", {"id": "r"})
    assert before == 1
    assert len(k.state.relations) == 0

def test_reinstatement_can_be_represented_by_a_later_derived_relation():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    obj(k, "flies", "Property")
    rel(k, "e", "a", "exception_to", "flies")
    rel(k, "new_rule", "a", "overrides_exception", "flies")
    rel(k, "restored", "a", "flies", "b",
        origin="derived", rule_id="reinstatement_v1", premises=("e", "new_rule"))
    assert k.state.relations["restored"].origin == "derived"

def test_non_monotonic_priority_is_external_semantics():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    rel(k, "r1", "a", "normally_implies", "b")
    rel(k, "r2", "a", "exception_to", "b")
    assert len(k.state.relations) == 2

def test_multiple_defaults_can_coexist_without_automatic_priority():
    k = Kernel()
    obj(k, "a", "Animal")
    obj(k, "b", "Property")
    obj(k, "c", "Property")
    rel(k, "d1", "a", "normally_implies", "b")
    rel(k, "d2", "a", "normally_implies", "c")
    assert len(k.state.relations) == 2

def test_retraction_can_be_atomic():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    rel(k, "r", "a", "flies", "b")
    before = k.state
    add(k, "remove_relation", {"id": "r"})
    assert k.state != before
    assert "r" not in k.state.relations

def test_missing_information_is_not_closed_world_negation():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    assert not any(r.source == "a" and r.target == "b" and r.predicate == "flies"
                   for r in k.state.relations.values())

def test_non_monotonic_resolution_does_not_require_fifth_primitive():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    rel(k, "r", "a", "normally_implies", "b")
    assert len(k.state.objects) == 2
    assert len(k.state.relations) == 1

@pytest.mark.parametrize("predicate", ["normally_implies", "exception_to", "overrides_exception"])
def test_default_logic_vocabulary_is_stored_as_ordinary_relations(predicate):
    k = Kernel()
    obj(k, "a", "Entity")
    obj(k, "b", "Property")
    rel(k, "r", "a", predicate, "b")
    assert k.state.relations["r"].predicate == predicate
def test_derived_retraction_policy_is_not_implicit():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    obj(k, "Bird", "Class")
    rel(k, "fact", "a", "is_a", "Bird")
    rel(k, "d", "a", "flies", "b",
        origin="derived", rule_id="r1", premises=("fact",))
    assert "d" in k.state.relations

def test_original_evidence_can_be_preserved_after_retraction():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    obj(k, "Bird", "Class")
    obj(k, "flies", "Property")
    rel(k, "fact", "a", "is_a", "Bird")
    rel(k, "d", "a", "flies", "b",
        origin="derived", rule_id="r1", premises=("fact",))
    rel(k, "exception", "a", "exception_to", "flies")
    add(k, "remove_relation", {"id": "d"})
    assert "fact" in k.state.relations
    assert "exception" in k.state.relations

def test_non_monotonic_cycle_is_stored_without_special_cycle_primitive():
    k = Kernel()
    obj(k, "a", "Entity")
    obj(k, "b", "Property")
    rel(k, "r1", "a", "normally_implies", "b")
    rel(k, "r2", "a", "depends_on", "b")
    assert len(k.state.relations) == 2

def test_strong_default_logic_requires_external_semantics():
    k = Kernel()
    obj(k, "a", "Bird")
    obj(k, "b", "Property")
    obj(k, "Bird", "Class")
    rel(k, "bird", "a", "is_a", "Bird")
    rel(k, "default", "a", "normally_implies", "b")
    assert not any(r.predicate == "flies" for r in k.state.relations.values())

def test_non_monotonic_case_is_representable_without_changing_core_file():
    k = Kernel()
    obj(k, "a", "Entity")
    obj(k, "b", "Property")
    rel(k, "r", "a", "normally_implies", "b")
    assert set(k.state.objects) == {"a", "b"}
    assert set(k.state.relations) == {"r"}

