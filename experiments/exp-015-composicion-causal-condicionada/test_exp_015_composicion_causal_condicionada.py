"""EXP-015 — Composición causal condicionada.

Hipótesis: una composición causal condicionada puede representarse con O/M/A/δ,
pero no debe inferirse automáticamente: requiere una condición explícita y un
procedimiento externo que aplique la regla. No se introduce una quinta primitiva.
"""

from mf_min_definitivo import Kernel, Transition


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {"id": oid, "type": typ, "value": value}))


def rel(k, rid, s, p, t, origin="asserted", premises=(), rule_id=None, polarity=True):
    k.transition(Transition("add_relation", {
        "id": rid, "source": s, "predicate": p, "target": t,
        "origin": origin, "premises": premises, "rule_id": rule_id,
        "polarity": polarity,
    }))


def base():
    k = Kernel()
    for oid, typ in (("a", "event"), ("b", "event"), ("c", "event"),
                     ("k", "condition"), ("rule1", "rule")):
        obj(k, oid, typ)
    return k


def pairs(k, predicate):
    return {(r.source, r.target) for r in k.state.relations.values()
            if r.predicate == predicate}


def test_causal_chain_is_explicitly_representable():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    assert pairs(k, "causes") == {("a", "b"), ("b", "c")}


def test_naive_causal_transitivity_is_not_automatic():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    assert ("a", "c") not in pairs(k, "causes")


def test_condition_is_explicitly_representable():
    k = base()
    rel(k, "cond", "k", "required_for", "rule1")
    assert pairs(k, "required_for") == {("k", "rule1")}


def test_rule_can_encode_condition_and_premises():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    rel(k, "cond", "k", "required_for", "rule1")
    # Las premisas son referencias de procedencia; no son objetos destino.
    assert ("a", "b") in pairs(k, "causes")
    assert ("b", "c") in pairs(k, "causes")
    assert ("k", "rule1") in pairs(k, "required_for")


def test_missing_condition_blocks_external_composition():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    premises = {"ab", "bc"}
    condition_present = ("k", "rule1") in pairs(k, "required_for")
    candidate = ("a", "c") if premises == {"ab", "bc"} and condition_present else None
    assert candidate is None


def test_satisfied_condition_allows_explicit_derived_result():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    rel(k, "cond", "k", "required_for", "rule1")
    rel(k, "ac", "a", "causes", "c", origin="derived",
        premises=("ab", "bc", "cond"), rule_id="rule1")
    assert pairs(k, "causes") == {("a", "b"), ("b", "c"), ("a", "c")}
    ac = k.state.relations["ac"]
    assert ac.origin == "derived"
    assert ac.premises == ("ab", "bc", "cond")
    assert ac.rule_id == "rule1"


def test_composition_is_external_algorithmic_work():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    rel(k, "cond", "k", "required_for", "rule1")
    premises = {"ab", "bc", "cond"}
    assert premises.issubset(k.state.relations)
    assert ("a", "c") not in pairs(k, "causes")


def test_counterexample_condition_can_invalidate_naive_composition():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    rel(k, "not_cond", "k", "not_required_for", "rule1", polarity=False)
    assert ("a", "c") not in pairs(k, "causes")


def test_different_context_requires_a_distinct_condition():
    k = base()
    obj(k, "k2", "condition")
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    rel(k, "cond2", "k2", "required_for", "rule1")
    assert ("k", "rule1") not in pairs(k, "required_for")
    assert ("k2", "rule1") in pairs(k, "required_for")


def test_predicate_name_does_not_create_causal_composition():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    rel(k, "magic", "a", "causal_transitive", "c")
    assert ("a", "c") in pairs(k, "causal_transitive")
    assert ("a", "c") not in pairs(k, "causes")


def test_delta_can_store_derived_composition_without_special_operation():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    rel(k, "cond", "k", "required_for", "rule1")
    before = len(k.state.relations)
    rel(k, "ac", "a", "causes", "c", origin="derived",
        premises=("ab", "bc", "cond"), rule_id="rule1")
    assert len(k.state.relations) == before + 1


def test_no_fifth_primitive_is_justified():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    rel(k, "cond", "k", "required_for", "rule1")
    assert k.state.objects["k"].type == "condition"
    assert pairs(k, "causes") == {("a", "b"), ("b", "c")}


def test_strong_causal_composition_remains_external_semantics():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    assert ("a", "c") not in pairs(k, "causes")


def test_condition_must_be_used_explicitly_in_the_derivation():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    # Even when the condition exists, δ does not invent the conclusion.
    rel(k, "cond", "k", "required_for", "rule1")
    assert ("a", "c") not in pairs(k, "causes")


def test_derived_claim_records_its_three_evidences():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    rel(k, "cond", "k", "required_for", "rule1")
    rel(k, "ac", "a", "causes", "c", origin="derived",
        premises=("ab", "bc", "cond"), rule_id="rule1")
    assert set(k.state.relations["ac"].premises) == {"ab", "bc", "cond"}


def test_phase_boundary_is_semantic_not_ontological():
    k = base()
    rel(k, "ab", "a", "causes", "b")
    rel(k, "bc", "b", "causes", "c")
    # La pregunta fuerte (si la composición es causalmente válida) no queda
    # resuelta por la existencia del triple en M.
    assert len(k.state.objects) == 5
    assert len(k.state.relations) == 2
