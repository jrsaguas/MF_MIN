import pytest
from mf_min_definitivo import Kernel, Transition, ContradictionError

def add(k, op, payload): k.transition(Transition(op, payload))
def obj(k, oid, typ, value=None):
    p={"id":oid,"type":typ}
    if value is not None: p["value"]=value
    add(k,"add_object",p)
def rel(k,rid,s,p,t,**kw):
    x={"id":rid,"source":s,"predicate":p,"target":t}; x.update(kw)
    add(k,"add_relation",x)

def test_partial_observation_is_representable():
    k=Kernel(); obj(k,"s","System"); obj(k,"o","Observation"); obj(k,"x","Variable")
    rel(k,"obs","o","observes","s"); rel(k,"var","o","about","x")
    assert len(k.state.objects)==3 and len(k.state.relations)==2

def test_unobserved_does_not_mean_false():
    k=Kernel(); obj(k,"s","System"); obj(k,"p","Property")
    assert not any(r.source=="s" and r.target=="p" for r in k.state.relations.values())

def test_explicit_negative_observation_is_distinct_from_missing_observation():
    k=Kernel(); obj(k,"s","System"); obj(k,"p","Property")
    rel(k,"neg","s","has_property","p",polarity=False)
    assert k.state.relations["neg"].polarity is False

def test_open_system_boundary_can_be_structured():
    k=Kernel(); obj(k,"s","System"); obj(k,"env","Environment")
    rel(k,"boundary","s","interacts_with","env")
    rel(k,"input","env","input_to","s")
    rel(k,"output","s","output_to","env")
    assert len(k.state.relations)==3

def test_external_event_can_enter_open_system():
    k=Kernel(); obj(k,"s","System"); obj(k,"e","Event")
    rel(k,"in","e","enters","s")
    assert k.state.relations["in"].predicate=="enters"

def test_external_event_does_not_trigger_transition_automatically():
    k=Kernel(); obj(k,"s","System"); obj(k,"e","Event"); obj(k,"p","Property")
    rel(k,"in","e","enters","s")
    assert not any(r.predicate=="has_property" for r in k.state.relations.values())

def test_observation_can_be_provenance_for_derived_result():
    k=Kernel(); obj(k,"s","System"); obj(k,"o","Observation"); obj(k,"p","Property")
    rel(k,"obs","o","observes","s")
    rel(k,"seen","o","reports","p")
    rel(k,"derived","s","has_property","p",origin="derived",rule_id="obs_rule",premises=("obs","seen"))
    assert k.state.relations["derived"].origin=="derived"

def test_multiple_observations_can_conflict_without_exact_structural_contradiction():
    k=Kernel(); obj(k,"s","System"); obj(k,"o1","Observation"); obj(k,"o2","Observation"); obj(k,"p","Property")
    rel(k,"a","o1","reports","p"); rel(k,"b","o2","reports","p")
    assert len(k.state.relations)==2

def test_same_observation_positive_negative_still_rejected():
    k=Kernel(); obj(k,"o","Observation"); obj(k,"p","Property")
    rel(k,"yes","o","reports","p")
    with pytest.raises(ContradictionError): rel(k,"no","o","reports","p",polarity=False)

def test_partial_state_can_be_extended_by_delta():
    k=Kernel(); obj(k,"s","System"); obj(k,"p","Property")
    before=len(k.state.objects)
    obj(k,"new","Observation")
    assert len(k.state.objects)==before+1

def test_unknown_external_state_is_not_silently_invented():
    k=Kernel(); obj(k,"s","System")
    assert "external_fact" not in k.state.objects

def test_system_identity_survives_new_observations():
    k=Kernel(); obj(k,"s","System"); obj(k,"o1","Observation"); rel(k,"r1","o1","observes","s")
    obj(k,"o2","Observation"); rel(k,"r2","o2","observes","s")
    assert "s" in k.state.objects

def test_open_boundary_semantics_are_external():
    k=Kernel(); obj(k,"s","System"); obj(k,"env","Environment")
    rel(k,"b","s","boundary","env")
    assert len(k.state.relations)==1

def test_observation_time_can_be_stored_without_builtin_temporal_inference():
    k=Kernel(); obj(k,"o","Observation"); obj(k,"t","Time")
    rel(k,"at","o","occurs_at","t")
    assert k.state.relations["at"].predicate=="occurs_at"

def test_sensor_reliability_can_be_external_data():
    k=Kernel(); obj(k,"sensor","Sensor"); obj(k,"q","Quality"); obj(k,"v","0.9")
    rel(k,"quality","sensor","has_quality","q")
    assert len(k.state.relations)==1

def test_multiple_partial_views_can_coexist():
    k=Kernel(); obj(k,"s","System"); obj(k,"o1","Observation"); obj(k,"o2","Observation")
    rel(k,"r1","o1","observes","s"); rel(k,"r2","o2","observes","s")
    assert len(k.state.relations)==2

def test_no_fifth_primitive_required_for_open_systems():
    k=Kernel(); obj(k,"s","System"); obj(k,"env","Environment")
    rel(k,"r","s","interacts_with","env")
    assert set(k.state.objects)=={"s","env"}

def test_open_system_processing_is_external():
    k=Kernel(); obj(k,"s","System"); obj(k,"e","Event")
    rel(k,"r","e","enters","s")
    assert len(k.state.relations)==1

@pytest.mark.parametrize("predicate",["observes","reports","enters","interacts_with","input_to","output_to"])
def test_open_system_vocabulary_is_ordinary_relation(predicate):
    k=Kernel(); obj(k,"a","Entity"); obj(k,"b","Entity")
    rel(k,"r","a",predicate,"b")
    assert k.state.relations["r"].predicate==predicate

def test_external_update_can_be_recorded_with_provenance():
    k=Kernel(); obj(k,"s","System"); obj(k,"e","Event"); obj(k,"p","Property")
    rel(k,"e1","e","enters","s")
    rel(k,"u","s","has_property","p",origin="derived",rule_id="external_update",premises=("e1",))
    assert k.state.relations["u"].premises==("e1",)

def test_partial_observation_does_not_require_closed_world_assumption():
    k=Kernel(); obj(k,"s","System"); obj(k,"p","Property")
    assert not any(r.predicate=="has_property" for r in k.state.relations.values())
