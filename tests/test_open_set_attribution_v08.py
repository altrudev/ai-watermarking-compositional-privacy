import unittest
from dataclasses import replace
from lab.open_set_attribution_v08 import *

class T(unittest.TestCase):
 def test_protocol_identity_and_matrix(self):
  self.assertEqual(BASE_PROTOCOL_COMMIT,"7ed99ac13e39946b2853c2b4e4ddf4193728bce9");self.assertEqual(AMENDED_AUDITED_PROTOCOL_HEAD,"0a3f970beb200be97e04b9bc86b56584021e040a");self.assertEqual(IMPLEMENTATION_SPEC_COMMIT,"87a01c30b4d7ea1185fbaba48966f8786a6b60a7");self.assertEqual((len(SCENARIOS),len(STATES),len(POLICIES),len(MODES),CORE_CELLS),(3,3,4,3,108));self.assertEqual((len(SCORE_GRID),len(MARGIN_GRID)),(60,31))
 def test_cohort_isolation(self):
  for n in SCENARIOS:
   s=prepare(n);self.assertTrue(s["K"].isdisjoint(s["Uc"]));self.assertTrue(s["K"].isdisjoint(s["Ut"]));self.assertTrue(s["Uc"].isdisjoint(s["Ut"]));self.assertEqual({g.person_id for g in s["candidate_population"]},set(s["K"]));self.assertTrue({g.person_id for g in s["candidate_population"]}.isdisjoint(s["Uc"]|s["Ut"]))
 def test_cohort_assignment_is_deterministic(self):
  for n in SCENARIOS:
   a=prepare(n);b=prepare(n);self.assertEqual((a["K"],a["Uc"],a["Ut"]),(b["K"],b["Uc"],b["Ut"]))
 def test_partition(self):
  s=prepare("S1");ca,ho=split_known(s["known_cal"]+s["known_hold"],s["candidate_population"]);self.assertEqual((len(ca),len(ho)),(48,48));self.assertTrue(all(a.target_generation_id.endswith("-gen-0") for a in ca));self.assertTrue(all(a.target_generation_id.endswith("-gen-1") for a in ho));self.assertFalse({a.target_generation_id for a in ca}&{a.target_generation_id for a in ho})
 def test_provenance_fail_closed_and_absent_fallback(self):
  s=prepare("S1");a=s["known_hold"][0];self.assertEqual(provenance_state(a),"complete");r=transform(a,"provenance_removed");self.assertEqual(provenance_state(r),"absent");e=Evaluator(s["candidate_population"]);self.assertEqual(len(e.rank(r,"global",POLICIES["canonical_combined"])),len(e.rank(r,"provider_model_narrowed",POLICIES["canonical_combined"])));self.assertRaises(ProtocolControlError,e.rank,replace(a,provider_hint=None),"provider_model_narrowed",POLICIES["canonical_combined"])
 def test_single_candidate_abstains(self):
  s=prepare("S1");g=next(x for x in s["candidate_population"] if x.generation_id.endswith("-gen-1"));a=next(x for x in s["known_hold"] if x.target_generation_id==g.generation_id);r=score(Evaluator([g]),a,g,"control","global","canonical_combined","published_derivative");self.assertEqual(r["candidate_count"],1);self.assertEqual(decision(r,0,0),(False,"INSUFFICIENT_COMPARATORS"))
 def test_truth_label_independence(self):
  s=prepare("S1");e=Evaluator(s["candidate_population"]);a=s["known_hold"][0];b=replace(a,target_generation_id="syn-hidden-label");self.assertEqual(e.rank(a,"global",POLICIES["canonical_combined"]),e.rank(b,"global",POLICIES["canonical_combined"]))
 def test_historical_parity_all_scenario_state_policy(self):
  for n in SCENARIOS:
   for st in STATES:
    for p in POLICIES:self.assertTrue(parity(n,st,p), (n,st,p))
 def test_all_negative_controls(self):
  x=controls();self.assertTrue(x["all_pass"],x);self.assertTrue(all(v for k,v in x.items() if k.startswith("C")))
 def test_calibration_is_deterministic_and_gated(self):
  s=prepare("S1");e=Evaluator(s["candidate_population"]);t=s["truth"];kr=records(e,s["known_cal"],t,"known_cal","published_derivative","global","canonical_combined");ur=records(e,s["u_cal"],t,"u_cal","published_derivative","global","canonical_combined");a=calibrate(kr,ur);b=calibrate(kr,ur);self.assertEqual(a,b);self.assertIn(a["status"],{"FEASIBLE","CALIBRATION_INFEASIBLE"})
  if a["status"]=="FEASIBLE":self.assertGreaterEqual(a["calibration_kcar"],.40);self.assertLessEqual(a["calibration_ufir"],.05);self.assertLessEqual(a["calibration_kwar"],.10);self.assertIsNotNone(a["high_score_reference"])
 def test_core_cell_retains_person_and_filter_metrics(self):
  x=cell(prepare("S1"),"published_derivative","canonical_combined","provider_model_narrowed");self.assertIn("feasible_set_sha256",x["calibration"])
  if x["holdout"]["status"]=="EVALUATED":
   for k in ("ufir","kcar","kwar","krr","precision","hs_ufir","uper","true_person_filter_exclusion_rate","forced_choice_known_person_top1","wrong_known_events"):self.assertIn(k,x["holdout"])
 def test_classification_precedence(self):
  cs=[{"calibration":{"status":"FEASIBLE"},"holdout":{"status":"EVALUATED","ufir":0.,"kcar":.8,"kwar":0.,"precision":1.,"hs_ufir":0.}} for _ in range(108)];tr=[{"acceptable":True},{"acceptable":True}];self.assertEqual(classify(cs,tr,True),"OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX");cs[0]["holdout"]["ufir"]=.2;self.assertEqual(classify(cs,tr,True),"FALSE_ATTRIBUTION_RISK_OBSERVED");self.assertEqual(classify(cs,tr,False),"CONTROL_FAILED")

if __name__=="__main__":unittest.main()
