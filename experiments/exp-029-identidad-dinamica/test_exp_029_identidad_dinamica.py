import pytest
from mf_min_definitivo import Kernel, Transition, DuplicateIDError

def add(k, op, payload): k.transition(Transition(op, payload))
def obj(k, oid, typ, value=None):
    p={"id":oid,"type":typ}
    if value is not None: p["value"]=value
    add(k,"add_object",p)
def rel(k,rid,s,p,t,**kw):
    x={"id":rid,"source":s,"predicate":p,"target":t}; x.update(kw)
    add(k,"add_relation",x)

def test_identity_survives_value_change_across_states():
    k=Kernel(); obj(k,"x","Entity","v1")
    first=k.state
    obj(k,"x_v2","Entity","v2")
    rel(k,"same","x_v2","represents","x")
    assert "x" in first.objects and "x_v2" in k.state.objects

def test_object_ids_are_unique():
    k=Kernel(); obj(k,"x","Entity")
    with pytest.raises(DuplicateIDError): obj(k,"x","Entity")

def test_reference_can_track_a_persistent_identity():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"r","Reference")
    rel(k,"points","r","refers_to","x")
    assert k.state.relations["points"].target=="x"

def test_transformation_can_be_external_relation():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"x2","Representation")
    rel(k,"t","x","transformed_to","x2")
    assert k.state.relations["t"].predicate=="transformed_to"

def test_transformation_does_not_implicitly_create_identity_equivalence():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"y","Entity")
    rel(k,"t","x","transformed_to","y")
    assert not any(r.predicate=="same_as" for r in k.state.relations.values())

def test_composition_can_change_without_replacing_identity_object():
    k=Kernel(); obj(k,"machine","System"); obj(k,"part1","Part")
    rel(k,"contains1","machine","contains","part1")
    obj(k,"part2","Part")
    rel(k,"contains2","machine","contains","part2")
    assert "machine" in k.state.objects

def test_reference_can_be_retargeted_with_delta():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"y","Entity"); obj(k,"r","Reference")
    rel(k,"ref1","r","refers_to","x")
    add(k,"remove_relation",{"id":"ref1"})
    rel(k,"ref2","r","refers_to","y")
    assert k.state.relations["ref2"].target=="y"

def test_aliases_are_relations_not_new_identity_primitive():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"alias","Label")
    rel(k,"a","alias","aliases","x")
    assert len(k.state.relations)==1

def test_identity_and_value_are_separate_structurally():
    k=Kernel(); obj(k,"x","Entity","100")
    assert k.state.objects["x"].id=="x" and k.state.objects["x"].value=="100"

def test_historical_snapshot_preserves_previous_object_value():
    k=Kernel(); obj(k,"x","Entity","v1"); s1=k.state
    obj(k,"y","Entity","v2")
    assert s1.objects["x"].value=="v1"

def test_external_identity_policy_can_derive_same_as():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"y","Entity")
    rel(k,"eq","x","same_as","y",origin="derived",rule_id="identity_policy",premises=())
    assert k.state.relations["eq"].origin=="derived"

def test_identity_policy_is_not_triggered_by_predicate_name():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"y","Entity")
    rel(k,"eq","x","same_as","y")
    assert len(k.state.relations)==1

def test_reference_failure_can_be_explicit_without_inventing_target():
    k=Kernel(); obj(k,"r","Reference"); obj(k,"missing","Placeholder")
    rel(k,"points","r","refers_to","missing")
    assert "missing" in k.state.objects

def test_removing_target_relation_does_not_delete_identity_object():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"r","Reference")
    rel(k,"p","r","refers_to","x")
    add(k,"remove_relation",{"id":"p"})
    assert "x" in k.state.objects

def test_dynamic_identity_semantics_remain_external():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"y","Entity")
    rel(k,"r","x","transformed_to","y")
    assert len(k.state.objects)==2

def test_no_fifth_primitive_required():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"y","Entity")
    rel(k,"r","x","same_as","y")
    assert set(k.state.objects)=={"x","y"}

@pytest.mark.parametrize("predicate",["same_as","refers_to","transformed_to","aliases","contains"])
def test_identity_vocabulary_is_ordinary_relation(predicate):
    k=Kernel(); obj(k,"a","Entity"); obj(k,"b","Entity")
    rel(k,"r","a",predicate,"b")
    assert k.state.relations["r"].predicate==predicate

def test_new_representation_can_preserve_external_identity_link():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"xv2","Representation")
    rel(k,"rep","xv2","represents","x")
    assert k.state.relations["rep"].target=="x"

def test_identity_relation_can_have_provenance():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"y","Entity")
    rel(k,"eq","x","same_as","y",origin="derived",rule_id="external_match",premises=())
    assert k.state.relations["eq"].rule_id=="external_match"

def test_reference_and_identity_can_coexist():
    k=Kernel(); obj(k,"x","Entity"); obj(k,"r","Reference")
    rel(k,"p","r","refers_to","x"); rel(k,"i","r","same_as","x")
    assert len(k.state.relations)==2
