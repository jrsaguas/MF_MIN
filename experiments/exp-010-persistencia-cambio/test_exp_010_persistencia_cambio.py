"""EXP-010 — Persistencia y cambio sin modificar el núcleo MF_MIN.

Hipótesis:
La identidad de un objeto puede mantenerse a través de estados sucesivos de
S mediante el mismo identificador, mientras el cambio puede representarse
como nuevas relaciones/objetos en estados posteriores. Kernel/δ no mantiene
por sí mismo una línea temporal histórica completa.
"""

from mf_min_definitivo import Kernel, Transition, state_to_dict


def obj(k, oid, typ, value=None, properties=None):
    payload = {"id": oid, "type": typ, "value": value}
    if properties is not None:
        payload["properties"] = properties
    k.transition(Transition("add_object", payload))


def rel(k, rid, source, predicate, target):
    k.transition(Transition("add_relation", {
        "id": rid, "source": source, "predicate": predicate, "target": target
    }))


def test_same_object_id_persists_across_successive_states():
    k = Kernel()
    obj(k, "p1", "entity", {"status": "A"})
    state_1 = state_to_dict(k.state)
    obj(k, "e1", "event", "change")
    rel(k, "r1", "p1", "participates_in", "e1")
    state_2 = state_to_dict(k.state)
    assert state_1["objects"]["p1"]["id"] == "p1"
    assert state_2["objects"]["p1"]["id"] == "p1"
    assert state_2["objects"]["p1"]["type"] == "entity"


def test_change_can_be_represented_as_a_new_relation():
    k = Kernel()
    obj(k, "p1", "entity")
    obj(k, "v1", "state_value", "A")
    obj(k, "v2", "state_value", "B")
    rel(k, "state_1", "p1", "has_state", "v1")
    before = state_to_dict(k.state)
    rel(k, "state_2", "p1", "has_state", "v2")
    after = state_to_dict(k.state)
    assert "state_1" in before["relations"]
    assert "state_2" not in before["relations"]
    assert "state_2" in after["relations"]
    assert after["objects"]["p1"]["id"] == before["objects"]["p1"]["id"]


def test_identity_and_state_value_are_distinct_structurally():
    k = Kernel()
    obj(k, "p1", "entity")
    obj(k, "v1", "state_value", "A")
    rel(k, "r1", "p1", "has_state", "v1")
    obj(k, "v2", "state_value", "B")
    rel(k, "r2", "p1", "has_state", "v2")
    assert "p1" not in {"v1", "v2"}
    assert k.state.relations["r1"].source == "p1"
    assert k.state.relations["r2"].source == "p1"


def test_core_does_not_mutate_an_existing_object_value_in_place():
    k = Kernel()
    obj(k, "p1", "entity", {"status": "A"})
    original = state_to_dict(k.state)["objects"]["p1"]
    obj(k, "v2", "state_value", "B")
    rel(k, "r2", "p1", "has_state", "v2")
    assert state_to_dict(k.state)["objects"]["p1"] == original


def test_history_requires_explicit_external_snapshots_or_relations():
    k = Kernel()
    obj(k, "p1", "entity")
    snapshot_1 = state_to_dict(k.state)
    obj(k, "v1", "state_value", "A")
    rel(k, "r1", "p1", "has_state", "v1")
    snapshot_2 = state_to_dict(k.state)
    assert snapshot_1["objects"]["p1"]["id"] == snapshot_2["objects"]["p1"]["id"]
    assert not hasattr(k, "history")
    assert not hasattr(k, "timeline")


def test_temporal_order_can_be_added_without_a_persistence_primitive():
    k = Kernel()
    for oid in ("s1", "s2"):
        obj(k, oid, "state")
    obj(k, "p1", "entity")
    rel(k, "r1", "p1", "has_state_at", "s1")
    rel(k, "r2", "p1", "has_state_at", "s2")
    rel(k, "t1", "s1", "before", "s2")
    assert k.state.relations["t1"].predicate == "before"
    assert k.state.relations["r1"].source == "p1"
    assert k.state.relations["r2"].source == "p1"


def test_change_does_not_imply_persistence_semantics_by_predicate_name():
    k = Kernel()
    obj(k, "p1", "entity")
    obj(k, "v1", "state_value", "A")
    rel(k, "r1", "p1", "has_state", "v1")
    obj(k, "q1", "entity")
    rel(k, "r2", "p1", "successor_of", "q1")
    assert k.state.relations["r2"].predicate == "successor_of"
    assert k.state.relations["r2"].source == "p1"


def test_no_new_persistence_primitive_is_justified():
    k = Kernel()
    obj(k, "p1", "entity")
    obj(k, "s1", "state")
    obj(k, "s2", "state")
    rel(k, "r1", "p1", "has_state_at", "s1")
    rel(k, "r2", "p1", "has_state_at", "s2")
    rel(k, "r3", "s1", "before", "s2")
    assert k.state.objects["p1"].type == "entity"
    assert {k.state.relations[x].source for x in ("r1", "r2")} == {"p1"}
    assert k.state.relations["r3"].predicate == "before"
