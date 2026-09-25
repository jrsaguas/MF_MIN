"""EXP-001 — prueba de memoria sin importar memory.py.

La prueba usa únicamente las primitivas ejecutables del núcleo:
Object, Relation/State mediante Transition y δ mediante Kernel.transition().
"""

from mf_min_definitivo import Kernel, Transition, state_from_dict, state_to_dict


def add_object(kernel, object_id, object_type, value=None):
    kernel.transition(
        Transition(
            "add_object",
            {"id": object_id, "type": object_type, "value": value},
        )
    )


def add_relation(kernel, relation_id, source, predicate, target):
    kernel.transition(
        Transition(
            "add_relation",
            {
                "id": relation_id,
                "source": source,
                "predicate": predicate,
                "target": target,
            },
        )
    )


def relation_tuples(kernel):
    return {
        (r.source, r.predicate, r.target, r.polarity)
        for r in kernel.state.relations.values()
    }


def retrieve_episode(kernel, episode_id):
    """Consulta mínima: recupera las relaciones que pertenecen al episodio."""
    episode_relations = [
        r
        for r in kernel.state.relations.values()
        if r.source == episode_id
        and r.predicate == "contains"
        and r.polarity
    ]
    contained_ids = {r.target for r in episode_relations}
    return {
        r
        for r in kernel.state.relations.values()
        if r.source in contained_ids or r.target in contained_ids
    }


def build_episode():
    kernel = Kernel()

    add_object(kernel, "ep1", "episode")
    add_object(kernel, "goal1", "goal", "mover_objeto")
    add_object(kernel, "event1", "event", "inicio")
    add_object(kernel, "event2", "event", "fin")
    add_object(kernel, "action1", "action", "mover")
    add_object(kernel, "result1", "result", "success")

    add_relation(kernel, "m1", "ep1", "contains", "goal1")
    add_relation(kernel, "m2", "ep1", "contains", "event1")
    add_relation(kernel, "m3", "ep1", "contains", "event2")
    add_relation(kernel, "m4", "event1", "precedes", "event2")
    add_relation(kernel, "m5", "event1", "performed", "action1")
    add_relation(kernel, "m6", "event2", "has_result", "result1")

    return kernel


def test_episode_memory_is_core_expressible():
    kernel = build_episode()

    objects = kernel.state.objects
    relations = relation_tuples(kernel)

    assert {"ep1", "goal1", "event1", "event2", "action1", "result1"} <= set(objects)
    assert ("event1", "precedes", "event2", True) in relations
    assert ("event1", "performed", "action1", True) in relations

    recovered = retrieve_episode(kernel, "ep1")

    assert any(
        r.source == "event1"
        and r.predicate == "performed"
        and r.target == "action1"
        for r in recovered
    )
    assert any(
        r.source == "event1"
        and r.predicate == "precedes"
        and r.target == "event2"
        for r in recovered
    )


def test_memory_representation_survives_state_round_trip():
    kernel = build_episode()

    encoded = state_to_dict(kernel.state)
    restored = state_from_dict(encoded)

    assert relation_tuples(kernel) == {
        (r.source, r.predicate, r.target, r.polarity)
        for r in restored.relations.values()
    }
    assert set(kernel.state.objects) == set(restored.objects)
