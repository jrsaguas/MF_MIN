import pytest
from mf_min_definitivo import Kernel, Transition

def add(k, op, payload):
    k.transition(Transition(op, payload))

def obj(k, oid, typ, value=None):
    p={"id":oid,"type":typ}
    if value is not None: p["value"]=value
    add(k,"add_object",p)

def rel(k,rid,s,p,t,**kw):
    q={"id":rid,"source":s,"predicate":p,"target":t}
    q.update(kw)
    add(k,"add_relation",q)

def base():
    k=Kernel()
    for x,t in (("x","Variable"),("y","Variable"),("a","Entity"),("b","Entity"),
                ("P","Predicate"),("Q","Predicate"),("c1","Claim"),("c2","Claim"),
                ("domain","Domain"),("formula","Formula")):
        obj(k,x,t)
    return k

def test_variable_and_domain_are_representable():
    k=base()
    rel(k,"member_a","a","member_of","domain")
    rel(k,"bind_x","x","ranges_over","domain")
    assert len(k.state.relations)==2

def test_atomic_predication_is_representable():
    k=base()
    rel(k,"pa","a","has_property","P")
    assert k.state.relations["pa"].source=="a"

def test_universal_claim_can_be_structured():
    k=base()
    rel(k,"body","c1","has_body","formula")
    rel(k,"binder","c1","binds","x")
    rel(k,"scope","c1","has_scope","domain")
    assert len(k.state.relations)==3

def test_existential_claim_can_be_structured():
    k=base()
    rel(k,"witness","c2","has_witness","a")
    rel(k,"body","c2","has_body","formula")
    assert len(k.state.relations)==2

def test_quantifier_name_does_not_execute_inference():
    k=base()
    rel(k,"q","c1","for_all","x")
    assert len(k.state.relations)==1

def test_external_instantiation_can_add_derived_fact():
    k=base()
    rel(k,"q","c1","for_all","x")
    rel(k,"pa","a","has_property","P")
    rel(k,"d","a","instance_of_claim","c1",origin="derived",
        rule_id="instantiate",premises=("q","pa"))
    r=k.state.relations["d"]
    assert r.origin=="derived"
    assert set(r.premises)=={"q","pa"}

def test_scope_can_be_preserved_as_relational_structure():
    k=base()
    obj(k,"body1","Formula")
    rel(k,"contains","c1","has_scope","body1")
    rel(k,"binder","c1","binds","x")
    rel(k,"uses","body1","mentions","x")
    assert len(k.state.relations)==3

def test_no_implicit_universalization():
    k=base()
    rel(k,"pa","a","has_property","P")
    assert not any(r.predicate=="for_all" for r in k.state.relations.values())

def test_no_implicit_existentialization():
    k=base()
    rel(k,"pa","a","has_property","P")
    assert not any(r.predicate=="exists" for r in k.state.relations.values())

def test_multiple_variables_are_representable():
    k=base()
    rel(k,"b1","c1","binds","x")
    rel(k,"b2","c1","binds","y")
    rel(k,"r","x","related_to","y")
    assert len(k.state.relations)==3

def test_constraints_can_restrict_a_domain():
    k=base()
    add(k,"add_axiom",{"id":"ax1","name":"domain_nonempty"})
    assert "ax1" in k.state.axioms

def test_quantifier_semantics_remain_external():
    k=base()
    rel(k,"q","c1","for_all","x")
    rel(k,"scope","c1","has_scope","domain")
    assert not any(r.predicate in {"satisfies_all","witness_exists","proves"} for r in k.state.relations.values())

def test_counterexample_can_be_recorded():
    k=base()
    rel(k,"q","c1","for_all","x")
    rel(k,"bad","b","counterexample_to","c1")
    assert k.state.relations["bad"].target=="c1"

def test_no_fifth_primitive_is_required():
    k=base()
    rel(k,"bind","c1","binds","x")
    rel(k,"scope","c1","has_scope","domain")
    assert len(k.state.objects)==10
    assert len(k.state.relations)==2




