"""EXP-003 — Causalidad en MF_MIN.

Separa representación de una afirmación causal de las propiedades semánticas
fuertes que una teoría causal podría exigir.
"""

from mf_min_definitivo import Kernel, Transition


def add_object(k, oid, typ, value=None):
    k.transition(Transition("add_object", {"id": oid, "type": typ, "value": value}))


def add_relation(k, rid, source, predicate, target, polarity=True):
    k.transition(Transition("add_relation", {
        "id": rid, "source": source, "predicate": predicate,
        "target": target, "polarity": polarity,
    }))


def build_causal_case():
    k = Kernel()
    add_object(k, "fire", "event", "fuego")
    add_object(k, "heat", "event", "calentamiento")
    add_object(k, "smoke", "event", "humo")
    add_relation(k, "c1", "fire", "causes", "heat")
    add_relation(k, "c2", "fire", "causes", "smoke")
    return k


def test_causal_claim_is_representable_as_relation():
    k = build_causal_case()
    facts = {(r.source, r.predicate, r.target) for r in k.state.relations.values()}
    assert ("fire", "causes", "heat") in facts
    assert ("fire", "causes", "smoke") in facts


def test_causality_is_not_inferred_from_relation_name():
    k = Kernel()
    add_object(k, "a", "event")
    add_object(k, "b", "event")
    add_object(k, "c", "event")
    add_relation(k, "r1", "a", "causes", "b")
    add_relation(k, "r2", "b", "causes", "c")

    # El núcleo almacena las dos afirmaciones; no debe atribuir
    # automáticamente una teoría causal transitiva a la cadena.
    facts = {(r.source, r.predicate, r.target) for r in k.state.relations.values()}
    assert ("a", "causes", "b") in facts
    assert ("b", "causes", "c") in facts
    assert ("a", "causes", "c") not in facts


def test_causal_provenance_can_be_explicit():
    k = build_causal_case()
    add_relation(k, "e1", "heat", "evidence_for", "fire")
    causal = next(r for r in k.state.relations.values() if r.id == "c1")
    evidence = next(r for r in k.state.relations.values() if r.id == "e1")
    assert causal.predicate == "causes"
    assert evidence.predicate == "evidence_for"
