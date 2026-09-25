"""EXP-009 — Intervalos y duración sin modificar el núcleo MF_MIN.

Hipótesis:
Los intervalos pueden representarse mediante objetos y relaciones entre
intervalo, inicio y fin. La duración numérica puede almacenarse como dato,
pero sus propiedades temporales (cálculo, aditividad y composición) requieren
semántica/algoritmos externos y no deben atribuirse al nombre de un predicado.
"""

from mf_min_definitivo import Kernel, Transition


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {"id": oid, "type": typ, "value": value}))


def rel(k, rid, source, predicate, target, **extra):
    payload = {"id": rid, "source": source, "predicate": predicate, "target": target}
    payload.update(extra)
    k.transition(Transition("add_relation", payload))


def interval_base():
    k = Kernel()
    obj(k, "i1", "interval")
    obj(k, "s1", "event")
    obj(k, "e1", "event")
    obj(k, "d1", "duration", 5)
    return k


def interval_relations(k):
    rel(k, "r_start", "i1", "starts_at", "s1")
    rel(k, "r_end", "i1", "ends_at", "e1")
    rel(k, "r_duration", "i1", "has_duration", "d1")


def test_interval_structure_is_representable_by_objects_and_relations():
    k = interval_base()
    interval_relations(k)
    assert k.state.objects["i1"].type == "interval"
    assert k.state.objects["s1"].type == "event"
    assert k.state.objects["e1"].type == "event"
    assert k.state.objects["d1"].value == 5
    assert k.state.relations["r_start"].target == "s1"
    assert k.state.relations["r_end"].target == "e1"
    assert k.state.relations["r_duration"].target == "d1"


def test_start_and_end_are_distinct_structural_roles():
    k = interval_base()
    interval_relations(k)
    assert k.state.relations["r_start"].predicate == "starts_at"
    assert k.state.relations["r_end"].predicate == "ends_at"
    assert k.state.relations["r_start"].target != k.state.relations["r_end"].target


def test_duration_can_be_stored_as_an_object_value():
    k = interval_base()
    interval_relations(k)
    duration = k.state.objects["d1"]
    assert duration.type == "duration"
    assert duration.value == 5


def test_duration_arithmetic_is_not_implicit_in_object_values():
    k = interval_base()
    interval_relations(k)
    assert not hasattr(k, "duration_arithmetic")
    assert not hasattr(k, "temporal_calculus")


def test_endpoint_difference_requires_external_semantics():
    k = Kernel()
    obj(k, "s1", "time_point", 10)
    obj(k, "e1", "time_point", 15)
    obj(k, "i1", "interval")
    rel(k, "r_start", "i1", "starts_at", "s1")
    rel(k, "r_end", "i1", "ends_at", "e1")
    start = k.state.objects["s1"].value
    end = k.state.objects["e1"].value
    assert end - start == 5
    assert "duration" not in {r.predicate for r in k.state.relations.values()}


def test_duration_additivity_can_be_computed_externally():
    k = Kernel()
    for oid, value in (("d1", 5), ("d2", 7), ("d3", 12)):
        obj(k, oid, "duration", value)
    assert k.state.objects["d1"].value + k.state.objects["d2"].value == 12
    assert k.state.objects["d3"].value == 12
    assert not k.state.relations


def test_interval_composition_is_representable_but_not_semantically_automatic():
    k = Kernel()
    for oid in ("i1", "i2", "e1", "e2", "e3"):
        obj(k, oid, "interval" if oid.startswith("i") else "event")
    rel(k, "i1_start", "i1", "starts_at", "e1")
    rel(k, "i1_end", "i1", "ends_at", "e2")
    rel(k, "i2_start", "i2", "starts_at", "e2")
    rel(k, "i2_end", "i2", "ends_at", "e3")
    assert k.state.relations["i1_end"].target == k.state.relations["i2_start"].target
    assert all(r.predicate != "adjacent" for r in k.state.relations.values())


def test_predicate_names_do_not_create_interval_semantics():
    k = Kernel()
    for oid in ("i1", "s1", "e1"):
        obj(k, oid, "interval" if oid == "i1" else "event")
    rel(k, "r1", "i1", "starts_at", "s1")
    rel(k, "r2", "i1", "ends_at", "e1")
    assert len(k.state.relations) == 2
    assert ("s1", "e1") not in {(r.source, r.target) for r in k.state.relations.values()}


def test_no_new_primitive_is_justified_by_this_boundary():
    k = interval_base()
    interval_relations(k)
    assert all(o.type in {"interval", "event", "duration"} for o in k.state.objects.values())
    assert all(r.predicate in {"starts_at", "ends_at", "has_duration"} for r in k.state.relations.values())
