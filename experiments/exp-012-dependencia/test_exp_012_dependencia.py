"""EXP-012 — Dependencia causal.

Hipótesis:
Una afirmación de dependencia puede representarse como M entre objetos O,
pero la mera existencia de una relación "depends_on" no constituye por sí
misma una teoría causal ni autoriza inferencias causales fuertes.
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


def base_case():
    k = Kernel()
    obj(k, "x", "variable", 1)
    obj(k, "y", "variable", 2)
    obj(k, "z", "variable", 3)
    return k


def pairs(k, predicate):
    return {
        (r.source, r.target)
        for r in k.state.relations.values()
        if r.predicate == predicate
    }


def test_dependency_claim_is_representable_as_relation():
    k = base_case()
    rel(k, "d1", "y", "depends_on", "x")
    assert pairs(k, "depends_on") == {("y", "x")}


def test_dependency_can_be_explicitly_composed_as_a_structure():
    k = base_case()
    rel(k, "d1", "y", "depends_on", "x")
    rel(k, "d2", "z", "depends_on", "y")
    assert pairs(k, "depends_on") == {("y", "x"), ("z", "y")}


def test_dependency_does_not_implicitly_become_causality():
    k = base_case()
    rel(k, "d1", "y", "depends_on", "x")
    assert pairs(k, "causes") == set()
    assert pairs(k, "depends_on") == {("y", "x")}


def test_dependency_chain_does_not_imply_direct_dependency_without_algorithm():
    k = base_case()
    rel(k, "d1", "y", "depends_on", "x")
    rel(k, "d2", "z", "depends_on", "y")
    assert ("z", "x") not in pairs(k, "depends_on")
def test_dependency_is_not_identical_to_temporal_order():
    k = base_case()
    rel(k, "d1", "y", "depends_on", "x")
    assert pairs(k, "before") == set()
    assert pairs(k, "depends_on") == {("y", "x")}


def test_negative_dependency_claim_is_storable_without_contradicting_positive_other_pair():
    k = base_case()
    rel(k, "d1", "y", "depends_on", "x", polarity=True)
    rel(k, "d2", "z", "depends_on", "x", polarity=False)
    relations = {
        (r.source, r.predicate, r.target, r.polarity)
        for r in k.state.relations.values()
    }
    assert ("y", "depends_on", "x", True) in relations
    assert ("z", "depends_on", "x", False) in relations


def test_dependency_evidence_can_be_explicit_relation():
    k = base_case()
    obj(k, "obs", "observation")
    rel(k, "d1", "y", "depends_on", "x")
    rel(k, "e1", "obs", "supports", "y")
    assert pairs(k, "depends_on") == {("y", "x")}
    assert pairs(k, "supports") == {("obs", "y")}


def test_dependency_relation_name_does_not_create_semantics():
    k = base_case()
    rel(k, "d1", "x", "depends_on", "y")
    rel(k, "d2", "y", "depends_on", "x")
    # Sin una restricción explícita, ambas relaciones son M válidas.
    assert pairs(k, "depends_on") == {("x", "y"), ("y", "x")}


def test_external_dependency_closure_is_algorithmic():
    k = base_case()
    rel(k, "d1", "y", "depends_on", "x")
    rel(k, "d2", "z", "depends_on", "y")
    direct = pairs(k, "depends_on")
    inferred = {("z", "x")} if ("z", "y") in direct and ("y", "x") in direct else set()
    assert inferred == {("z", "x")}
    assert ("z", "x") not in pairs(k, "depends_on")


def test_no_new_primitive_is_justified_by_basic_dependency():
    k = base_case()
    rel(k, "d1", "y", "depends_on", "x")
    assert k.state.objects["y"].type == "variable"
    assert pairs(k, "depends_on") == {("y", "x")}
def test_delta_applies_dependency_claim_as_an_ordinary_transition():
    k = base_case()
    before = len(k.state.relations)
    rel(k, "d1", "y", "depends_on", "x")
    after = len(k.state.relations)
    assert after == before + 1
    assert pairs(k, "depends_on") == {("y", "x")}


def test_strong_dependency_remains_an_open_semantic_question():
    k = base_case()
    rel(k, "d1", "y", "depends_on", "x")
    # El núcleo conserva la afirmación, pero no decide si "dependencia"
    # significa necesidad, contrafactualidad, intervención o causalidad.
    assert k.state.relations["d1"].predicate == "depends_on"
    assert ("y", "x") in pairs(k, "depends_on")
