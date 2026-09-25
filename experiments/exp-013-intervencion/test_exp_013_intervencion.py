"""EXP-013 — Intervención causal.

Hipótesis:
Una intervención deliberada puede representarse mediante O/M/A/δ como
un evento/acción explícito, relaciones que describen su objetivo y un
estado posterior obtenido por una transición. La semántica fuerte de
"intervenir" y la interpretación causal del cambio permanecen externas.
"""

from mf_min_definitivo import Kernel, Transition


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {
        "id": oid, "type": typ, "value": value
    }))


def rel(k, rid, source, predicate, target, polarity=True):
    k.transition(Transition("add_relation", {
        "id": rid,
        "source": source,
        "predicate": predicate,
        "target": target,
        "polarity": polarity,
    }))


def baseline():
    k = Kernel()
    obj(k, "x0", "value", 1)
    obj(k, "y0", "value", 2)
    obj(k, "z0", "outcome", 3)
    obj(k, "s0", "state")
    rel(k, "v1", "s0", "has_value", "y0")
    rel(k, "v2", "s0", "has_value", "z0")
    return k


def pairs(k, predicate):
    return {
        (r.source, r.target)
        for r in k.state.relations.values()
        if r.predicate == predicate
    }


def test_intervention_is_representable_as_explicit_event_and_relations():
    k = baseline()
    obj(k, "i1", "intervention")
    rel(k, "t1", "i1", "targets", "y0")
    rel(k, "a1", "i1", "acts_on", "s0")
    assert k.state.objects["i1"].type == "intervention"
    assert pairs(k, "targets") == {("i1", "y0")}
    assert pairs(k, "acts_on") == {("i1", "s0")}


def test_intervention_does_not_modify_existing_object_in_place():
    k = baseline()
    obj(k, "y1", "value", 5)
    obj(k, "s1", "state")
    rel(k, "v3", "s1", "has_value", "y1")
    assert k.state.objects["y0"].value == 2
    assert k.state.objects["y1"].value == 5
    assert k.state.objects["s0"].id == "s0"
    assert k.state.objects["s1"].id == "s1"


def test_intervention_transition_can_encode_before_and_after_states():
    k = baseline()
    obj(k, "i1", "intervention")
    obj(k, "y1", "value", 5)
    obj(k, "s1", "state")
    rel(k, "t1", "i1", "targets", "y0")
    rel(k, "from1", "i1", "starts_from", "s0")
    rel(k, "to1", "i1", "produces", "s1")
    rel(k, "v3", "s1", "has_value", "y1")
    assert pairs(k, "starts_from") == {("i1", "s0")}
    assert pairs(k, "produces") == {("i1", "s1")}
    assert pairs(k, "has_value") >= {("s0", "y0"), ("s0", "z0"), ("s1", "y1")}


def test_intervention_is_not_equivalent_to_observational_dependency():
    k = baseline()
    rel(k, "d1", "z0", "depends_on", "y0")
    assert pairs(k, "depends_on") == {("z0", "y0")}
    assert pairs(k, "intervenes_on") == set()
    assert pairs(k, "targets") == set()


def test_observation_alone_does_not_create_intervention():
    k = baseline()
    obj(k, "obs1", "observation")
    rel(k, "o1", "obs1", "observes", "y0")
    assert pairs(k, "observes") == {("obs1", "y0")}
    assert pairs(k, "targets") == set()
    assert pairs(k, "produces") == set()


def test_predicate_name_intervenes_on_does_not_change_state():
    k = baseline()
    obj(k, "i1", "event")
    rel(k, "i1r", "i1", "intervenes_on", "y0")
    assert k.state.objects["y0"].value == 2
    assert pairs(k, "intervenes_on") == {("i1", "y0")}


def test_intervention_effect_requires_explicit_comparison_of_states():
    k = baseline()
    obj(k, "i1", "intervention")
    obj(k, "y1", "value", 5)
    obj(k, "s1", "state")
    rel(k, "from1", "i1", "starts_from", "s0")
    rel(k, "to1", "i1", "produces", "s1")
    rel(k, "v3", "s1", "has_value", "y1")
    before = {r.target for r in k.state.relations.values()
              if r.source == "s0" and r.predicate == "has_value"}
    after = {r.target for r in k.state.relations.values()
             if r.source == "s1" and r.predicate == "has_value"}
    assert before == {"y0", "z0"}
    assert after == {"y1"}
    assert before != after

def test_intervention_can_be_applied_as_ordinary_delta_transition():
    k = baseline()
    before = len(k.state.objects)
    k.transition(Transition("add_object", {
        "id": "i1", "type": "intervention", "value": None
    }))
    k.transition(Transition("add_relation", {
        "id": "t1", "source": "i1", "predicate": "targets",
        "target": "y0", "polarity": True
    }))
    assert len(k.state.objects) == before + 1
    assert pairs(k, "targets") == {("i1", "y0")}


def test_intervention_branch_can_be_kept_separate_from_baseline():
    baseline_kernel = baseline()
    branch_kernel = baseline()
    obj(branch_kernel, "i1", "intervention")
    obj(branch_kernel, "y1", "value", 5)
    obj(branch_kernel, "s1", "state")
    rel(branch_kernel, "t1", "i1", "targets", "y0")
    rel(branch_kernel, "to1", "i1", "produces", "s1")
    rel(branch_kernel, "v3", "s1", "has_value", "y1")
    assert pairs(baseline_kernel, "produces") == set()
    assert pairs(branch_kernel, "produces") == {("i1", "s1")}


def test_intervention_does_not_automatically_imply_causality():
    k = baseline()
    obj(k, "i1", "intervention")
    obj(k, "y1", "value", 5)
    obj(k, "s1", "state")
    rel(k, "t1", "i1", "targets", "y0")
    rel(k, "to1", "i1", "produces", "s1")
    rel(k, "v3", "s1", "has_value", "y1")
    assert pairs(k, "causes") == set()
    assert pairs(k, "caused_by") == set()


def test_intervention_semantics_are_not_created_by_relation_name():
    k = baseline()
    obj(k, "i1", "event")
    rel(k, "i1r", "i1", "intervenes_on", "y0")
    rel(k, "i2r", "y0", "intervenes_on", "i1")
    assert pairs(k, "intervenes_on") == {("i1", "y0"), ("y0", "i1")}


def test_no_new_primitive_is_justified_by_basic_intervention():
    k = baseline()
    obj(k, "i1", "intervention")
    rel(k, "t1", "i1", "targets", "y0")
    assert k.state.objects["i1"].type == "intervention"
    assert pairs(k, "targets") == {("i1", "y0")}


def test_strong_intervention_remains_an_open_semantic_question():
    k = baseline()
    obj(k, "i1", "intervention")
    rel(k, "t1", "i1", "targets", "y0")
    rel(k, "from1", "i1", "starts_from", "s0")
    assert pairs(k, "targets") == {("i1", "y0")}
    assert pairs(k, "starts_from") == {("i1", "s0")}
    # El núcleo representa la estructura; no decide por sí mismo si la
    # intervención tiene efecto causal, contrafactual o identificabilidad.
