import unittest
from lab.cross_family_replication_lab import FAMILIES,POLICIES,SCENARIOS,SCENARIO_TRANSFERS,_holdout_class,_transfer_class,commuting_control,pairwise_effects,partition_artifacts,predict_paths,prepare_scenario,run_scenario,aggregate_scenario_results,scorer_parity,MatrixEvaluator,matrix_scorer_parity
HISTORICAL={"paraphrase","summarize","translate","model_edit"}
ALLOWED={"MECHANISM_REPLICATED_WITH_TRANSFER_FOR_DECLARED_MATRIX","CONTEXT_DEPENDENT_REPLICATION","MECHANISM_NOT_REPLICATED","CONTROL_FAILED"}
class T(unittest.TestCase):
 def test_protocol(self):
  self.assertEqual((len(FAMILIES),len(POLICIES),len(SCENARIOS)),(2,5,6)); self.assertEqual(SCENARIO_TRANSFERS,(("S1","S2"),("S3","S4"),("S5","S6")))
 def test_families(self):
  for t in FAMILIES.values(): self.assertEqual(len(t),4); self.assertTrue(HISTORICAL.isdisjoint(set(t)))
 def test_transforms(self):
  pop,cal,hold,e=prepare_scenario("S1"); a=hold[0]
  for ts in FAMILIES.values():
   for fn in ts.values():
    l=fn(a); r=fn(a); self.assertEqual(l,r); self.assertTrue(l.text.strip()); self.assertEqual((l.target_generation_id,l.provider_hint,l.watermark_family,l.published_minute),(a.target_generation_id,a.provider_hint,a.watermark_family,a.published_minute))
 def test_partition(self):
  pop,cal,hold,e=prepare_scenario("S1"); lc,lh=partition_artifacts(cal+hold); self.assertTrue({a.target_generation_id for a in lc}.isdisjoint({a.target_generation_id for a in lh})); self.assertEqual(len(lc)+len(lh),len(pop))
 def test_parity(self):
  pop,cal,hold,e=prepare_scenario("S1"); self.assertTrue(scorer_parity(pop,hold,e)); fast=MatrixEvaluator(pop); result=matrix_scorer_parity(pop,hold,e,fast); self.assertTrue(result["all_policies"]); self.assertTrue(all(result["by_policy"].values()))
 def test_control(self):
  pop,cal,hold,e=prepare_scenario("S1")
  for w in POLICIES.values(): self.assertTrue(commuting_control(e,hold,w)["control_pass"])
 def test_pair(self):
  pop,cal,hold,e=prepare_scenario("S1"); ts=FAMILIES["structural_normalization"]; w=POLICIES["canonical_combined"]; p=pairwise_effects(e,cal,ts,w); self.assertEqual(len(p["effects"]),6); pred=predict_paths(e,hold,ts,w,p["effects"]); self.assertEqual(pred["path_count"],24); self.assertTrue(-1<=pred["pearson_r"]<=1)
 def test_thresholds(self):
  self.assertEqual(_holdout_class(.70),"predictive"); self.assertEqual(_holdout_class(.69),"partial"); self.assertEqual(_transfer_class(.50),"transfer_supported"); self.assertEqual(_transfer_class(.49),"weak_context_dependent_transfer")
 def test_scenario_shard(self):
  result=run_scenario("S1"); self.assertEqual(result["scenario"],"S1"); self.assertTrue(result["historical_scorer_parity"]); self.assertTrue(result["matrix_scorer_parity"]["all_policies"]); self.assertEqual(sum(len(row["holdout_cells"]) for row in result["families"].values()),10)

if __name__=='__main__': unittest.main()
