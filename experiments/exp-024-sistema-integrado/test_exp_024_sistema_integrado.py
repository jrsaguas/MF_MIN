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

def integrated():
    k = Kernel()
    for oid, typ, value in (
        ("intervention", "intervention", None),
        ("baseline", "state", None),
        ("after", "state", None),
        ("outcome", "state", None),
        ("evidence_a", "Evidence", None),
        ("evidence_b", "Evidence", None),
        ("claim", "Hypothesis", None),
        ("u", "Uncertainty", 0.25),
        ("t0", "time", None),
        ("t1", "time", None),
        ("t2", "time", None),
    ):
        obj(k, oid, typ, value)
    return k

def test_integrated_structure_is_representable():
    k = integrated()
    rel(k, "target", "intervention", "targets", "baseline")
    rel(k, "occ_i", "intervention", "occurs_at", "t0")
    rel(k, "occ_b", "baseline", "occurs_at", "t0")
    rel(k, "produces", "intervention", "produces", "after")
    rel(k, "occ_a", "after", "occurs_at", "t1")
    rel(k, "before_01", "t0", "before", "t1")
    rel(k, "evidence_support", "evidence_a", "supports", "claim")
    rel(k, "evidence_time", "evidence_a", "observed_at", "t2")
    rel(k, "uncertain", "evidence_a", "has_uncertainty", "u")
    rel(k, "claim_causal", "intervention", "causes", "outcome")
    assert len(k.state.objects) == 11
    assert len(k.state.relations) == 10

def test_full_chain_preserves_explicit_temporal_and_causal_distinctions():
    k = integrated()
    rel(k, "occ_i", "intervention", "occurs_at", "t0")
    rel(k, "occ_a", "after", "occurs_at", "t1")
    rel(k, "before", "t0", "before", "t1")
    rel(k, "produces", "intervention", "produces", "after")
    rel(k, "causes", "intervention", "causes", "outcome")
    assert {k.state.relations[x].predicate for x in ("before", "produces", "causes")} == {"before","produces","causes"}

def test_uncertainty_evidence_and_temporal_location_can_coexist():
    k = integrated()
    rel(k, "support", "evidence_a", "supports", "claim")
    rel(k, "when", "evidence_a", "observed_at", "t2")
    rel(k, "uncertain", "evidence_a", "has_uncertainty", "u")
    rel(k, "time_order", "t1", "before", "t2")
    assert len(k.state.relations) == 4

def test_two_sources_can_disagree_without_structural_contradiction():
    k = integrated()
    rel(k, "s1", "evidence_a", "supports", "claim")
    rel(k, "s2", "evidence_b", "refutes", "claim")
    assert len(k.state.relations) == 2

def test_exact_same_fact_positive_negative_remains_forbidden():
    k = integrated()
    rel(k, "p", "evidence_a", "observes", "claim", polarity=True)
    with pytest.raises(ContradictionError):
        rel(k, "n", "evidence_a", "observes", "claim", polarity=False)
    assert len(k.state.relations) == 1

def test_integrated_derived_conclusion_can_preserve_all_premises():
    k = integrated()
    rel(k, "target", "intervention", "targets", "baseline")
    rel(k, "occ_i", "intervention", "occurs_at", "t0")
    rel(k, "occ_a", "after", "occurs_at", "t1")
    rel(k, "before", "t0", "before", "t1")
    rel(k, "produces", "intervention", "produces", "after")
    rel(k, "support", "evidence_a", "supports", "claim")
    rel(k, "when", "evidence_a", "observed_at", "t2")
    rel(k, "uncertain", "evidence_a", "has_uncertainty", "u")
    rel(k, "derived", "intervention", "estimated_effect", "outcome",
        origin="derived",
        rule_id="integrated_estimator",
        premises=("target","occ_i","occ_a","before","produces","support","when","uncertain"))
    r = k.state.relations["derived"]
    assert r.origin == "derived"
    assert set(r.premises) == {"target","occ_i","occ_a","before","produces","support","when","uncertain"}

def test_derived_claim_is_external_not_automatic():
    k = integrated()
    rel(k, "target", "intervention", "targets", "baseline")
    rel(k, "produces", "intervention", "produces", "after")
    assert not any(r.predicate == "estimated_effect" for r in k.state.relations.values())

def test_predicate_names_do_not_activate_integrated_reasoning():
    k = integrated()
    rel(k, "magic", "intervention", "certainly_causes_before_with_probability", "outcome")
    assert len(k.state.relations) == 1

def test_no_special_integrated_transition_is_required():
    k = integrated()
    rel(k, "x", "intervention", "targets", "baseline")
    assert k.state.relations["x"].source == "intervention"

def test_missing_evidence_is_not_negative_evidence():
    k = integrated()
    assert not any(r.predicate == "refutes" and r.target == "claim" for r in k.state.relations.values())

def test_missing_uncertainty_is_not_zero():
    k = integrated()
    assert not any(r.predicate == "has_uncertainty" for r in k.state.relations.values())

def test_temporal_order_does_not_create_causal_claim():
    k = integrated()
    rel(k, "before", "t0", "before", "t1")
    rel(k, "occ_i", "intervention", "occurs_at", "t0")
    rel(k, "occ_o", "outcome", "occurs_at", "t1")
    assert not any(r.predicate == "causes" for r in k.state.relations.values())

def test_causal_claim_does_not_create_temporal_order():
    k = integrated()
    rel(k, "causes", "intervention", "causes", "outcome")
    assert not any(r.predicate == "before" and r.source == "intervention" and r.target == "outcome"
                   for r in k.state.relations.values())

def test_intervention_does_not_select_a_winner_between_evidence_sources():
    k = integrated()
    rel(k, "s1", "evidence_a", "supports", "claim")
    rel(k, "s2", "evidence_b", "refutes", "claim")
    assert not any(r.predicate in {"wins","majority","resolves"} for r in k.state.relations.values())

def test_no_fifth_primitive_is_required_by_the_integrated_case():
    k = integrated()
    rel(k, "target", "intervention", "targets", "baseline")
    rel(k, "uncertain", "evidence_a", "has_uncertainty", "u")
    rel(k, "when", "evidence_a", "observed_at", "t2")
    assert len(k.state.objects) == 11
    assert len(k.state.relations) == 3
