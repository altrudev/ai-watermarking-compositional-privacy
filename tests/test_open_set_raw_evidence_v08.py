import unittest
from lab import open_set_attribution_v08 as v
from lab.open_set_raw_evidence_v08 import COHORTS,RECORD_COLUMNS,raw_cell,raw_scenario,stable_bytes
class T(unittest.TestCase):
 def test_columns_cover_protocol_raw_fields(self):
  required={"candidate_count","top1_score","top2_score","margin","predicted_person_correct","predicted_generation_correct","target_person_present_after_filter","target_generation_present_after_filter","filter_excluded_true_person","filter_excluded_true_generation"}
  self.assertTrue(required.issubset(RECORD_COLUMNS))
 def test_raw_cell_matches_cohort_size(self):
  s=v.prepare("S1");rows=raw_cell(s,"published_derivative","canonical_combined","global","known_hold");self.assertEqual(len(rows),len(s["known_hold"]));self.assertTrue(all(r["cohort"]=="known_hold" for r in rows))
 def test_s1_complete_raw_evidence_is_deterministic(self):
  a=raw_scenario("S1");b=raw_scenario("S1");self.assertEqual(stable_bytes(a),stable_bytes(b));self.assertEqual(len(a["records"]),10368);self.assertTrue(all(x.startswith("syn-") for x in a["person_ids"]))
if __name__=="__main__":unittest.main()
