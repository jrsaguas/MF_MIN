import pytest
from mf_min_definitivo import Kernel, Transition, ContradictionError

def add(k, op, payload):
    k.transition(Transition(op, payload))

def obj(k, oid, typ, value=None):
    p={"id":oid,"type":typ}
    if value is not None: p["value"]=value
    add(k,"add_object",p)

def rel(k,rid,s,p,t,**kw):
    x={"id":rid,"source":s,"predicate":p,"target":t}
    x.update(kw)
    add(k,"add_relation",x)

def test_possible_world_structure_is_representable():
    k=Kernel()
    obj(k,"w1","World")
    obj(k,"w2","World")
    obj(k,"p","Proposition")
    rel(k,"acc","w1","accessible_to","w2")
    rel(k,"holds","w2","holds","p")
    assert len(k.state.objects)==3 and len(k.state.relations)==2

def test_modal_vocabulary_does_not_activate_semantics():
    k=Kernel()
    obj(k,"w","World"); obj(k,"p","Proposition")
    rel(k,"r","w","possibly","p")
    assert len(k.state.relations)==1

def test_necessity_and_possibility_are_distinct_relations():
    k=Kernel()
    obj(k,"w","World"); obj(k,"p","Proposition")
    rel(k,"pos","w","possibly","p")
    rel(k,"nec","w","necessarily","p")
    assert set(k.state.relations)=={"pos","nec"}

def test_accessibility_does_not_imply_truth_without_external_semantics():
    k=Kernel()
    obj(k,"w1","World"); obj(k,"w2","World"); obj(k,"p","Proposition")
    rel(k,"acc","w1","accessible_to","w2")
    assert not any(r.predicate=="holds" for r in k.state.relations.values())

def test_counterfactual_antecedent_and_consequent_are_representable():
    k=Kernel()
    obj(k,"actual","World"); obj(k,"alt","World")
    obj(k,"a","Proposition"); obj(k,"b","Proposition")
    rel(k,"ante","alt","assumes","a")
    rel(k,"cons","alt","holds","b")
    rel(k,"cf","actual","counterfactual","alt")
    assert len(k.state.relations)==3

def test_counterfactual_does_not_equal_material_implication():
    k=Kernel()
    obj(k,"w","World"); obj(k,"a","Proposition"); obj(k,"b","Proposition")
    rel(k,"imp","a","implies","b")
    rel(k,"cf","w","counterfactual","b")
    assert len(k.state.relations)==2

def test_external_counterfactual_result_can_be_derived_with_provenance():
    k=Kernel()
    obj(k,"actual","World"); obj(k,"alt","World")
    obj(k,"a","Proposition"); obj(k,"b","Proposition")
    rel(k,"ante","alt","assumes","a")
    rel(k,"cons","alt","holds","b")
    rel(k,"cf","actual","counterfactual","alt")
    rel(k,"result","actual","would_hold","b",origin="derived",rule_id="cf_eval",premises=("cf","ante","cons"))
    assert k.state.relations["result"].origin=="derived"

def test_alternative_worlds_can_diverge():
    k=Kernel()
    obj(k,"w1","World"); obj(k,"w2","World"); obj(k,"p","Proposition")
    rel(k,"h1","w1","holds","p")
    rel(k,"nh2","w2","holds_not","p")
    assert len(k.state.relations)==2

def test_modal_conflict_still_obeys_invariant():
    k=Kernel()
    obj(k,"w","World"); obj(k,"p","Proposition")
    rel(k,"yes","w","holds","p")
    with pytest.raises(ContradictionError):
        rel(k,"no","w","holds","p",polarity=False)

def test_world_identity_and_delta_are_ordinary_core_operations():
    k=Kernel()
    obj(k,"w1","World"); obj(k,"w2","World")
    rel(k,"r","w1","accessible_to","w2")
    add(k,"remove_relation",{"id":"r"})
    assert "r" not in k.state.relations

def test_counterfactual_provenance_does_not_define_counterfactual_semantics():
    k=Kernel()
    obj(k,"w","World"); obj(k,"p","Proposition")
    rel(k,"r","w","would_hold","p",origin="derived",rule_id="external_cf",premises=())
    assert k.state.relations["r"].rule_id=="external_cf"

def test_modal_evaluation_is_external():
    k=Kernel()
    obj(k,"w","World"); obj(k,"p","Proposition")
    rel(k,"r","w","possibly","p")
    assert len(k.state.objects)==2

def test_no_fifth_primitive_is_required():
    k=Kernel()
    obj(k,"w","World"); obj(k,"p","Proposition")
    rel(k,"r","w","possibly","p")
    assert set(k.state.objects)=={"w","p"}

@pytest.mark.parametrize("predicate",["possibly","necessarily","counterfactual","accessible_to","assumes","would_hold"])
def test_modal_vocabulary_is_ordinary_relation(predicate):
    k=Kernel()
    obj(k,"w","World"); obj(k,"p","Proposition")
    rel(k,"r","w",predicate,"p")
    assert k.state.relations["r"].predicate==predicate

def test_multiple_alternative_worlds_need_external_selection():
    k=Kernel()
    obj(k,"w","World"); obj(k,"w1","World"); obj(k,"w2","World"); obj(k,"p","Proposition")
    rel(k,"a1","w","accessible_to","w1")
    rel(k,"a2","w","accessible_to","w2")
    assert len(k.state.relations)==2

def test_counterfactual_selection_and_closeness_are_external():
    k=Kernel()
    obj(k,"actual","World"); obj(k,"w1","World"); obj(k,"w2","World")
    rel(k,"a1","actual","accessible_to","w1")
    rel(k,"a2","actual","accessible_to","w2")
    assert len(k.state.relations)==2

def test_represented_modal_structure_can_be_preserved_without_inference():
    k=Kernel()
    obj(k,"w","World"); obj(k,"p","Proposition")
    rel(k,"r","w","necessarily","p")
    assert "r" in k.state.relations
