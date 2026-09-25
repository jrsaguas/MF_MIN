"""EXP-004 — Reglas sobre el núcleo MF_MIN.

Prueba si una regla conjuntiva puede expresarse como estructura de relaciones
y realizarse mediante una transición, sin introducir una quinta primitiva.
"""

from mf_min_definitivo import Kernel, Transition


def obj(k, oid, typ, value=None):
    k.transition(Transition("add_object", {"id": oid, "type": typ, "value": value}))


def rel(k, rid, s, p, t, origin="asserted", premises=()):
    k.transition(Transition("add_relation", {
        "id": rid, "source": s, "predicate": p, "target": t,
        "origin": origin, "premises": premises,
    }))


def test_rule_premises_and_conclusion_are_core_relations():
    k = Kernel()
    obj(k, "s1", "person", "Ana")
    obj(k, "s2", "person", "Luis")
    obj(k, "r1", "fact")
    rel(k, "p1", "s1", "knows", "s2")

    # Una regla puede tener sus premisas representadas como relaciones.
    # Su aplicación posterior será una operación/transición.
    obj(k, "r2", "fact")
    rel(k, "c1", "s1", "trusts", "s2", origin="derived", premises=("p1",))
    assert k.state.relations["p1"].predicate == "knows"
    assert k.state.relations["c1"].origin == "derived"
    assert k.state.relations["c1"].premises == ("p1",)


def test_rule_metadata_does_not_become_a_new_primitive():
    k = Kernel()
    obj(k, "a", "event")
    obj(k, "b", "event")
    rel(k, "p", "a", "causes", "b")

    # La identidad de una regla/derivación se conserva como metadato
    # operacional de una relación, no como componente fundamental del estado.
    rel(k, "q", "a", "leads_to", "b", origin="derived", premises=("p",))
    q = k.state.relations["q"]
    assert (q.source, q.predicate, q.target) == ("a", "leads_to", "b")
    assert q.origin == "derived"


def test_core_does_not_assume_rule_semantics_without_transition():
    k = Kernel()
    obj(k, "a", "object")
    obj(k, "b", "object")
    rel(k, "p", "a", "connected", "b")

    # Almacenar una premisa no ejecuta una regla por sí mismo.
    assert not any(r.predicate == "derived_result" for r in k.state.relations.values())

    k.transition(Transition("add_relation", {
        "id": "d", "source": "a", "predicate": "derived_result",
        "target": "b", "origin": "derived", "premises": ("p",),
    }))
    assert k.state.relations["d"].origin == "derived"
