import unittest
from lab.transformation_chain_lab import (
    generate_population, make_artifacts, evaluate, SINGLE_SIGNALS, STAGE_FUNCTIONS,
    run_experiment, paraphrase_stage, utility
)

class TransformationChainLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.population=generate_population(persons=12,seed=41)
        cls.original=make_artifacts(cls.population)
        cls.stages={"original":cls.original}
        cls.report=run_experiment(persons=12,seed=41)
        current=cls.original
        for name,fn in STAGE_FUNCTIONS:
            current=[fn(a) for a in current]
            cls.stages[name]=current

    def test_synthetic_only(self):
        self.assertTrue(all(r.person_id.startswith("syn-") for r in self.population))

    def test_deterministic_population(self):
        self.assertEqual(self.population,generate_population(persons=12,seed=41))

    def test_chain_has_required_stages(self):
        self.assertEqual(list(self.stages),["original","edit","paraphrase","summarize","translate","model_edit","multi_model_edit"])

    def test_original_combined_linkage_is_material(self):
        self.assertGreater(evaluate(self.population,self.original).person_top1,.70)

    def test_no_original_single_channel_matches_combined(self):
        combined=evaluate(self.population,self.original).person_top1
        singles=[evaluate(self.population,self.original,w).person_top1 for w in SINGLE_SIGNALS.values()]
        self.assertGreater(combined-max(singles),.30)

    def test_paraphrase_removes_provenance_but_not_all_linkage(self):
        rows=[paraphrase_stage(a) for a in self.stages["edit"]]
        self.assertTrue(all(a.watermark_family is None and a.provider_hint is None for a in rows))
        self.assertGreater(evaluate(self.population,rows).person_top1,.15)

    def test_summarization_reduces_linkage(self):
        self.assertLess(evaluate(self.population,self.stages["summarize"]).person_top1,
                        evaluate(self.population,self.stages["paraphrase"]).person_top1)

    def test_translation_proxy_preserves_some_semantics(self):
        values=[utility(o,c)["semantic_retention"] for o,c in zip(self.original,self.stages["translate"])]
        self.assertGreater(sum(values)/len(values),.55)

    def test_final_chain_reduces_linkage_without_assuming_anonymity(self):
        result=evaluate(self.population,self.stages["multi_model_edit"])
        baseline=evaluate(self.population,self.original)
        self.assertLess(result.person_top1,baseline.person_top1)
        self.assertGreater(result.mean_anonymity_set,5)

    def test_channel_migration_is_observed(self):
        self.assertGreaterEqual(len(self.report["channel_migration_events"]),1)

    def test_claim_is_bounded(self):
        self.assertIn(self.report["final_claim"]["status"],{"supported_for_declared_test","not_supported"})
        self.assertIn("not proof of anonymity",self.report["final_claim"]["boundary"])

    def test_report_explicitly_records_proxy_limitations(self):
        joined=" ".join(self.report["limitations"]).lower()
        self.assertIn("translation",joined)
        self.assertIn("synthetic",joined)
        self.assertIn("failed re-identification",joined)

if __name__=="__main__":
    unittest.main()
