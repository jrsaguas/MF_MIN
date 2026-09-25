"""EXP-008 — Orden temporal fuerte sin modificar el núcleo MF_MIN.

Hipótesis:
O/M/A/δ pueden representar y validar una estructura de orden temporal
explícita, pero la semántica de orden no debe atribuirse al predicado
"before" por nombre. Se prueba qué parte queda expresada por M, qué parte
requiere A y qué parte requiere un algoritmo sobre M/δ.
"""

from mf_min_definitivo import Kernel, Transition, ContradictionError


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {
        "id": oid, "type": typ, "value": value
    }))


def rel(k, rid, source, predicate, target, **extra):
    payload = {
        "id": rid,
        "source": source,
        "predicate": predicate,
        "target": target,
    }
    payload.update(extra)
    k.transition(Transition("add_relation", payload))


def base_events():
    k = Kernel()
    for oid in ("e1", "e2", "e3", "e4"):
        obj(k, oid, "event", oid)
    return k


def edges(k, pairs):
    for rid, (source, target) in enumerate(pairs, 1):
        rel(k, f"t{rid}", source, "before", target)


def before_edges(k):
    return {
        (r.source, r.target)
        for r in k.state.relations.values()
        if r.predicate == "before" and r.polarity
    }


def test_explicit_order_is_representable_by_objects_and_relations():
    """Una relación temporal explícita cabe directamente en M."""
    k = base_events()
    edges(k, [("e1", "e2"), ("e2", "e3")])

    assert before_edges(k) == {("e1", "e2"), ("e2", "e3")}
    assert {o.type for o in k.state.objects.values()} == {"event"}


def test_order_properties_can_be_checked_without_new_primitive():
    """Irreflexividad y asimetría son propiedades sobre M, no nuevos datos."""
    k = base_events()
    edges(k, [("e1", "e2"), ("e2", "e3")])
    b = before_edges(k)

    assert all(source != target for source, target in b)
    assert all((target, source) not in b for source, target in b)


def test_transitivity_is_not_implicit_in_relation_storage():
    """M almacena e1<e2 y e2<e3; no inventa e1<e3 por sí solo."""
    k = base_events()
    edges(k, [("e1", "e2"), ("e2", "e3")])

    assert ("e1", "e3") not in before_edges(k)
def transitive_closure(edges_set):
    """Algoritmo externo mínimo para calcular el cierre transitivo de M."""
    closure = set(edges_set)
    changed = True
    while changed:
        changed = False
        for a, b in tuple(closure):
            for c, d in tuple(closure):
                if b == c and (a, d) not in closure:
                    closure.add((a, d))
                    changed = True
    return closure


def test_transitive_closure_is_algorithmic_over_m():
    """δ + un algoritmo puede producir una consecuencia sin nuevo primitivo."""
    k = base_events()
    edges(k, [("e1", "e2"), ("e2", "e3")])

    closure = transitive_closure(before_edges(k))
    assert ("e1", "e3") in closure
    assert ("e1", "e2") in closure
    assert ("e2", "e3") in closure
    # El estado del núcleo no cambia solo por calcular el cierre.
    assert ("e1", "e3") not in before_edges(k)


def test_axiom_can_reject_reflexive_before_without_new_primitive():
    """A puede imponer una restricción local sobre la relación temporal."""
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
        raise AssertionError("El axioma no rechazó before(e1,e1).")

    assert not k.state.relations
def test_axiom_rejection_preserves_previous_state():
    """δ conserva atomicidad cuando una restricción temporal rechaza el cambio."""
    k = base_events()
    rel(k, "t1", "e1", "before", "e2")
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
        raise AssertionError("Se esperaba rechazo de la relación reflexiva.")

    assert dict(k.state.relations) == before
    assert "t1" in k.state.relations
    assert "bad" not in k.state.relations


def test_semantic_order_is_not_conferred_by_predicate_name():
    """'before' sigue siendo un símbolo relacional salvo restricciones explícitas."""
    k = base_events()
    rel(k, "r1", "e1", "before", "e2")
    rel(k, "r2", "e2", "before", "e1")

    # Sin un axioma/algoritmo que imponga asimetría, ambas relaciones
    # son estructuralmente almacenables. Por tanto, el nombre no aporta
    # por sí mismo semántica universal de orden.
    assert before_edges(k) == {("e1", "e2"), ("e2", "e1")}


def test_no_new_temporal_primitive_is_required_by_this_experiment():
    """La evidencia reunida no exige añadir un componente a <O,M,A,δ>."""
    k = base_events()
    edges(k, [("e1", "e2"), ("e2", "e3")])
    closure = transitive_closure(before_edges(k))

    assert ("e1", "e3") in closure
    assert all(o.type == "event" for o in k.state.objects.values())
    assert all(r.predicate == "before" for r in k.state.relations.values())
