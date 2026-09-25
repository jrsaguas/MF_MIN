"""EXP-011 — Concurrencia y restricciones temporales.

Hipótesis:
La concurrencia, la simultaneidad y las restricciones entre eventos pueden
representarse mediante O/M/A/δ, pero sus criterios semánticos requieren
relaciones explícitas y algoritmos/restricciones; el orden de ejecución de δ
no debe confundirse con el tiempo del dominio modelado.
"""

from mf_min_definitivo import ContradictionError, Kernel, Transition


def obj(k, oid, typ):
    k.transition(Transition("add_object", {"id": oid, "type": typ}))


def rel(k, rid, source, predicate, target):
    k.transition(Transition("add_relation", {
        "id": rid, "source": source, "predicate": predicate, "target": target
    }))


def base_events():
    k = Kernel()
    for oid in ("e1", "e2", "e3"):
        obj(k, oid, "event")
    return k


def edges(k, pairs, predicate="before"):
    for i, (source, target) in enumerate(pairs, 1):
        rel(k, f"r{i}", source, predicate, target)


def relation_pairs(k, predicate):
    return {
        (r.source, r.target)
        for r in k.state.relations.values()
        if r.predicate == predicate
    }


def validate_irreflexive_before(k):
    pairs = relation_pairs(k, "before")
    return all(source != target for source, target in pairs)


def test_independent_events_do_not_implicitly_mean_concurrent():
    k = base_events()
    assert relation_pairs(k, "before") == set()
    assert relation_pairs(k, "simultaneous") == set()
    # La ausencia de before tampoco demuestra simultaneidad.
    assert not ("e1", "e2") in relation_pairs(k, "simultaneous")


def test_concurrency_can_be_represented_as_explicit_relation():
    k = base_events()
    rel(k, "c1", "e1", "concurrent_with", "e2")
    assert relation_pairs(k, "concurrent_with") == {("e1", "e2")}


def test_simultaneity_can_be_represented_without_new_primitive():
    k = base_events()
    rel(k, "s1", "e1", "simultaneous", "e2")
    assert relation_pairs(k, "simultaneous") == {("e1", "e2")}


def test_domain_time_is_not_execution_order_of_delta():
    k = base_events()
    # δ se ejecuta secuencialmente, pero el dominio puede declarar e1 y e2
    # simultáneos o independientes; no se infiere un before entre ellos.
    rel(k, "s1", "e1", "simultaneous", "e2")
    assert relation_pairs(k, "before") == set()
    assert relation_pairs(k, "simultaneous") == {("e1", "e2")}


def test_multiple_temporal_constraints_are_stored_in_M():
    k = base_events()
    edges(k, [("e1", "e2"), ("e1", "e3")])
    rel(k, "c1", "e2", "concurrent_with", "e3")
    assert relation_pairs(k, "before") == {("e1", "e2"), ("e1", "e3")}
    assert relation_pairs(k, "concurrent_with") == {("e2", "e3")}


def test_restriction_can_be_checked_as_external_algorithm():
    k = base_events()
    rel(k, "b1", "e1", "before", "e2")
    assert validate_irreflexive_before(k)

    rel(k, "b2", "e2", "before", "e1")
    # La estructura M puede contener el contraejemplo; la restricción
    # de aciclicidad/asimetría es una condición verificable sobre M.
    pairs = relation_pairs(k, "before")
    assert pairs == {("e1", "e2"), ("e2", "e1")}
    assert validate_irreflexive_before(k)


def test_axiom_can_reject_reflexive_temporal_constraint():
    k = base_events()
    k.transition(Transition("add_axiom", {
        "id": "a_no_reflexive_before",
        "name": "before_irreflexive",
        "body": [{
            "predicate": "before",
            "source": "?x",
            "target": "?x",
            "polarity": True,
        }],
    }))

    try:
        rel(k, "bad", "e1", "before", "e1")
    except ContradictionError:
        pass
    else:
        raise AssertionError("La restricción no rechazó before(e1,e1).")

    assert "bad" not in k.state.relations
def test_axiom_rejection_is_atomic():
    k = base_events()
    rel(k, "b1", "e1", "before", "e2")
    k.transition(Transition("add_axiom", {
        "id": "a_no_reflexive_before",
        "name": "before_irreflexive",
        "body": [{
            "predicate": "before",
            "source": "?x",
            "target": "?x",
            "polarity": True,
        }],
    }))
    before = dict(k.state.relations)

    try:
        rel(k, "bad", "e2", "before", "e2")
    except ContradictionError:
        pass
    else:
        raise AssertionError("Se esperaba rechazo de la restricción.")

    assert dict(k.state.relations) == before
    assert "b1" in k.state.relations
    assert "bad" not in k.state.relations


def test_predicate_name_alone_does_not_create_concurrency_semantics():
    k = base_events()
    rel(k, "r1", "e1", "concurrent_with", "e2")
    rel(k, "r2", "e2", "concurrent_with", "e1")
    # Sin una restricción adicional, ambas son relaciones M ordinarias.
    assert relation_pairs(k, "concurrent_with") == {
        ("e1", "e2"), ("e2", "e1")
    }


def test_temporal_constraints_can_be_combined_without_new_primitive():
    k = base_events()
    rel(k, "b1", "e1", "before", "e2")
    rel(k, "b2", "e1", "before", "e3")
    rel(k, "c1", "e2", "concurrent_with", "e3")
    assert relation_pairs(k, "before") == {
        ("e1", "e2"), ("e1", "e3")
    }
    assert relation_pairs(k, "concurrent_with") == {("e2", "e3")}


def test_no_new_temporal_primitive_is_justified_by_this_boundary():
    k = base_events()
    rel(k, "b1", "e1", "before", "e2")
    rel(k, "c1", "e2", "concurrent_with", "e3")
    rel(k, "s1", "e1", "simultaneous", "e3")
    assert set(k.state.objects) == {"e1", "e2", "e3"}
    assert len(k.state.relations) == 3
