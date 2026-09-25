"""EXP-002 — Temporalidad usando únicamente MF_MIN O/M/A/δ."""

from mf_min_definitivo import Kernel, Transition


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {"id": oid, "type": typ, "value": value}))


def rel(k, rid, source, predicate, target):
    k.transition(Transition("add_relation", {
        "id": rid, "source": source, "predicate": predicate, "target": target
    }))


def build_timeline():
    k = Kernel()
    obj(k, "e1", "event", "inicio")
    obj(k, "e2", "event", "proceso")
    obj(k, "e3", "event", "fin")

    rel(k, "t1", "e1", "before", "e2")
    rel(k, "t2", "e2", "before", "e3")
    rel(k, "t3", "e1", "before", "e3")
    return k


def test_weak_temporal_order_is_core_expressible():
    k = build_timeline()
    facts = {(r.source, r.predicate, r.target) for r in k.state.relations.values()}

    assert ("e1", "before", "e2") in facts
    assert ("e2", "before", "e3") in facts
    assert ("e1", "before", "e3") in facts


def test_strong_temporal_semantics_are_not_implicitly_provided():
    k = build_timeline()

    # MF_MIN puede representar una relación temporal explícita,
    # pero el núcleo no debe fingir que "before" ya posee una semántica
    # universal de orden temporal. Transitividad, simultaneidad,
    # intervalos y métricas temporales requieren axiomas/algoritmos explícitos.
    before = [
        r for r in k.state.relations.values()
        if r.predicate == "before"
    ]
    assert len(before) == 3
    assert all(r.polarity for r in before)
