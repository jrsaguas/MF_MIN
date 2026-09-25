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

def test_finite_prefix_of_infinite_structure_is_representable():
    k=Kernel()
    for i in range(5): obj(k,f"n{i}","Natural",i)
    assert len(k.state.objects)==5

def test_generator_can_be_stored_as_an_object():
    k=Kernel(); obj(k,"gen","Generator","n -> n+1")
    assert k.state.objects["gen"].value=="n -> n+1"

def test_generator_semantics_are_not_activated_by_value_text():
    k=Kernel(); obj(k,"gen","Generator","n -> n+1"); obj(k,"n0","Natural",0)
    assert len(k.state.relations)==0

def test_external_generator_can_materialize_finite_members():
    k=Kernel(); obj(k,"gen","Generator","n -> n+1")
    for i in range(4): obj(k,f"n{i}","Natural",i); rel(k,f"m{i}","gen","generated",f"n{i}")
    assert len(k.state.objects)==5 and len(k.state.relations)==4

def test_non_finite_intent_can_be_related_to_finite_observations():
    k=Kernel(); obj(k,"S","Set","{0,1,2,...}"); obj(k,"n3","Natural",3)
    rel(k,"m","S","contains","n3")
    assert k.state.relations["m"].predicate=="contains"

def test_membership_does_not_imply_complete_enumeration():
    k=Kernel(); obj(k,"S","Set","N"); obj(k,"n0","Natural",0); rel(k,"m0","S","contains","n0")
    assert len(k.state.objects)==2

def test_infinite_cardinality_can_be_stored_as_external_metadata():
    k=Kernel(); obj(k,"S","Set","N"); obj(k,"card","Cardinality","aleph_0")
    rel(k,"c","S","has_cardinality","card")
    assert k.state.objects["card"].value=="aleph_0"

def test_cardinality_text_does_not_create_new_objects():
    k=Kernel(); obj(k,"S","Set","infinite")
    assert len(k.state.objects)==1

def test_schema_can_describe_unbounded_family():
    k=Kernel(); obj(k,"schema","Schema","forall n in N: object(n)")
    assert k.state.objects["schema"].type=="Schema"

def test_schema_does_not_auto_instantiate_unbounded_members():
    k=Kernel(); obj(k,"schema","Schema","forall n in N: object(n)")
    assert len(k.state.objects)==1

def test_external_instantiation_can_add_arbitrary_finite_prefix():
    k=Kernel(); obj(k,"schema","Schema","n in N")
    for i in range(10): obj(k,f"x{i}","Element",i)
    assert len(k.state.objects)==11

def test_infinite_structure_can_be_extended_by_delta():
    k=Kernel(); obj(k,"S","Set","N"); obj(k,"n0","Natural",0)
    s1=k.state; obj(k,"n1","Natural",1)
    assert "n0" in s1.objects and "n1" in k.state.objects

def test_snapshot_remains_finite():
    k=Kernel()
    for i in range(3): obj(k,f"n{i}","Natural",i)
    s=k.state
    assert len(s.objects)==3

def test_no_implicit_infinite_closure():
    k=Kernel(); obj(k,"S","Set","N"); obj(k,"n0","Natural",0); rel(k,"r","S","contains","n0")
    assert len(k.state.relations)==1

def test_external_closure_can_derive_further_members():
    k=Kernel(); obj(k,"S","Set","N"); obj(k,"n0","Natural",0)
    rel(k,"r0","S","contains","n0")
    obj(k,"n1","Natural",1)
    rel(k,"r1","S","contains","n1",origin="derived",rule_id="successor",premises=("r0",))
    assert k.state.relations["r1"].origin=="derived"

def test_external_computation_can_represent_arbitrary_finite_slice():
    k=Kernel(); obj(k,"seq","Sequence","a_n=n^2")
    for i in range(6): obj(k,f"a{i}","Term",i*i)
    assert k.state.objects["a5"].value==25

def test_non_finite_sequence_semantics_remain_external():
    k=Kernel(); obj(k,"seq","Sequence","a_n=n^2")
    assert not any(r.predicate=="computes" for r in k.state.relations.values())

def test_infinite_process_can_be_represented_without_running_forever():
    k=Kernel(); obj(k,"p","Process","repeat forever")
    assert k.state.objects["p"].value=="repeat forever"

def test_process_execution_requires_external_algorithm():
    k=Kernel(); obj(k,"p","Process","repeat forever")
    assert len(k.state.relations)==0

def test_finite_delta_operations_remain_atomic():
    k=Kernel(); obj(k,"S","Set","N")
    with pytest.raises(Exception):
        add(k,"add_relation",{"id":"bad","source":"S","predicate":"contains","target":"missing"})
    assert "bad" not in k.state.relations

def test_infinite_description_does_not_break_id_uniqueness():
    k=Kernel(); obj(k,"S","Set","N")
    with pytest.raises(DuplicateIDError): obj(k,"S","Set","N")

def test_no_fifth_primitive_is_required_for_symbolic_non_finite_structure():
    k=Kernel(); obj(k,"S","Set","N"); obj(k,"schema","Schema","n -> n+1")
    rel(k,"def","schema","describes","S")
    assert set(k.state.objects)=={"S","schema"}

@pytest.mark.parametrize("predicate",["contains","generated","describes","has_cardinality","next"])
def test_non_finite_vocabulary_is_ordinary_relation(predicate):
    k=Kernel(); obj(k,"a","A"); obj(k,"b","B")
    rel(k,"r","a",predicate,"b")
    assert k.state.relations["r"].predicate==predicate
def test_no_automatic_totality_from_finite_prefix():
    k=Kernel()
    for i in range(3): obj(k,f"n{i}","Natural",i)
    assert len(k.state.objects)==3

def test_external_limit_can_control_materialization():
    k=Kernel(); obj(k,"gen","Generator","n -> n+1")
    for i in range(7): obj(k,f"n{i}","Natural",i)
    assert len(k.state.objects)==8

def test_symbolic_reference_can_point_to_non_materialized_domain():
    k=Kernel(); obj(k,"D","Domain","all natural numbers")
    obj(k,"rule","Rule","successor over D")
    rel(k,"uses","rule","over","D")
    assert k.state.relations["uses"].target=="D"

def test_finite_representation_and_infinite_intent_are_distinct():
    k=Kernel(); obj(k,"D","Domain","N"); obj(k,"n0","Natural",0)
    rel(k,"m","D","contains","n0")
    assert k.state.objects["D"].value=="N"

def test_boundary_is_external_not_an_ontological_primitive():
    k=Kernel(); obj(k,"D","Domain","N"); obj(k,"limit","Parameter",100)
    rel(k,"lim","limit","bounds","D")
    assert len(k.state.objects)==2

def test_classification_requires_no_new_primitive():
    k=Kernel(); obj(k,"D","Domain","N"); obj(k,"zero","Element",0); rel(k,"r","D","describes","zero")
    assert len(k.state.relations)==1
