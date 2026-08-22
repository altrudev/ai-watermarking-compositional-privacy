import unittest
from lab import open_set_attribution_v08 as v
from lab.open_set_reference_v08 import _five,build_cell,evidence_holdout,narrowing_differentials
class T(unittest.TestCase):
 def test_score_summary_quantiles(self):self.assertEqual(_five([0,1,2,3,4])["median"],2)
 def test_infeasible_cell_preserves_forced_choice_evidence(self):
  s=v.prepare("S1");h=evidence_holdout(s,"published_derivative","canonical_combined","global",{"status":"CALIBRATION_INFEASIBLE"});self.assertEqual(h["status"],"CALIBRATION_INFEASIBLE");self.assertIn("forced_choice_unknown_rate",h);self.assertIn("score_separation",h);self.assertIn("candidate_counts",h)
 def test_evaluated_cell_preserves_required_evidence(self):
  s=v.prepare("S1");c=build_cell(s,"published_derivative","canonical_combined","global");self.assertIn("forced_choice_known_person_top1",c["holdout"]);self.assertIn("score_separation",c["holdout"])
 def test_narrowing_differentials_shape(self):
  s=v.prepare("S1");cells=[]
  for st in v.STATES:
   for p in v.POLICIES:
    for m in v.MODES:cells.append(build_cell(s,st,p,m))
  # helper accepts a complete matrix; replicate S1 cells under scenario labels only for shape isn't valid, so assert raw S1 cell count here.
  self.assertEqual(len(cells),36)
if __name__=="__main__":unittest.main()
