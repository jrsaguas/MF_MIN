import pytest
from mf_min_definitivo import Kernel, Transition

def obj(k, oid, typ):
    k.transition(Transition("add_object", {"id": oid, "type": typ}))

def rel(k, rid, s, p, t, origin="asserted", premises=(), rule_id=None):
    k.transition(Transition("add_relation", {
        "id": rid, "source": s, "predicate": p, "target": t,
        "origin": origin, "premises": premises, "rule_id": rule_id,
    }))

def base():
    k = Kernel()
    for oid, typ in (("a", "event"), ("b", "event"), ("c", "event"),
                     ("t1", "time"), ("t2", "time"), ("t3", "time")):
        obj(k, oid, typ)
    return k

def test_temporal_order_and_causal_relation_are_distinct():
    k = base()
    rel(k, "t12", "t1", "before", "t2")
    rel(k, "t23", "t2", "before", "t3")
    rel(k, "ab", "a", "causes", "b")
    assert k.state.relations["t12"].predicate == "before"
    assert k.state.relations["ab"].predicate == "causes"

def test_temporal_order_does_not_create_causality():
    k = base()
    rel(k, "t12", "t1", "before", "t2")
    rel(k, "ab", "a", "occurs_at", "t1")
    rel(k, "bb", "b", "occurs_at", "t2")
    assert not any(r.predicate == "causes" and r.source == "a" and r.target == "b"
                   for r in k.state.relations.values())

def test_causality_does_not_create_temporal_order():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    assert not any(r.predicate == "before" and r.source == "a" and r.target == "b"
                   for r in k.state.relations.values())

def test_explicit_temporal_causal_composition_is_representable():
    k = base()
    rel(k, "t12", "t1", "before", "t2")
    rel(k, "t23", "t2", "before", "t3")
    rel(k, "at", "a", "occurs_at", "t1")
    rel(k, "bt", "b", "occurs_at", "t2")
    rel(k, "ct", "c", "occurs_at", "t3")
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    assert len(k.state.relations) == 7

def test_naive_temporal_causal_inference_is_not_automatic():
    k = base()
    rel(k, "t12", "t1", "before", "t2")
    rel(k, "at", "a", "occurs_at", "t1")
    rel(k, "bt", "b", "occurs_at", "t2")
    rel(k, "ab", "a", "causes", "b")
    assert not any(r.predicate == "causes" and r.source == "t1" and r.target == "t2"
                   for r in k.state.relations.values())

def test_temporal_causal_rule_can_be_recorded_as_external_derivation():
    k = base()
    rel(k, "t12", "t1", "before", "t2")
    rel(k, "at", "a", "occurs_at", "t1")
    rel(k, "bt", "b", "occurs_at", "t2")
    rel(k, "ab", "a", "causes", "b")
    rel(k, "derived", "a", "temporally_related_to", "b",
        origin="derived", premises=("t12", "at", "bt", "ab"), rule_id="temporal_rule")
    r = k.state.relations["derived"]
    assert r.origin == "derived"
    assert set(r.premises) == {"t12", "at", "bt", "ab"}

def test_same_time_or_order_does_not_imply_causal_direction():
    k = base()
    rel(k, "same", "t1", "simultaneous", "t2")
    rel(k, "at", "a", "occurs_at", "t1")
    rel(k, "bt", "b", "occurs_at", "t2")
    assert not any(r.predicate == "causes" for r in k.state.relations.values())

def test_temporal_counterexample_can_coexist_with_causal_claim():
    k = base()
    rel(k, "t12", "t1", "before", "t2")
    rel(k, "at", "a", "occurs_at", "t1")
    rel(k, "bt", "b", "occurs_at", "t2")
    rel(k, "ab", "a", "causes", "b")
    rel(k, "cb", "c", "occurs_at", "t1")
    assert len(k.state.relations) == 5

def test_no_fifth_primitive_is_required_for_temporal_causal_structure():
    k = base()
    rel(k, "t12", "t1", "before", "t2")
    rel(k, "at", "a", "occurs_at", "t1")
    rel(k, "ab", "a", "causes", "b")
    assert len(k.state.objects) == 6
    assert len(k.state.relations) == 3

def test_predicate_names_do_not_execute_temporal_causal_reasoning():
    k = base()
    rel(k, "x", "a", "causes_before", "b")
    assert k.state.relations["x"].predicate == "causes_before"

def test_derived_temporal_causal_claim_requires_explicit_rule_id():
    k = base()
    rel(k, "t12", "t1", "before", "t2")
    rel(k, "at", "a", "occurs_at", "t1")
    rel(k, "bt", "b", "occurs_at", "t2")
    rel(k, "ab", "a", "causes", "b")
    with pytest.raises(Exception):
        rel(k, "d", "a", "temporally_related_to", "b",
            origin="derived", premises=("t12", "at", "bt", "ab"))

def test_temporal_causal_semantics_remain_external():
    k = base()
    rel(k, "t12", "t1", "before", "t2")
    rel(k, "at", "a", "occurs_at", "t1")
    rel(k, "bt", "b", "occurs_at", "t2")
    rel(k, "ab", "a", "causes", "b")
    assert all(r.predicate in {"before", "occurs_at", "causes"}
               for r in k.state.relations.values())

