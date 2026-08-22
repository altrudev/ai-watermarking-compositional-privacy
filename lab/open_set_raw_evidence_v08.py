from __future__ import annotations
import hashlib, json
from lab import open_set_attribution_v08 as v

RAW_SCHEMA="altru.dev/open-set-false-attribution/raw-evidence/0.8"
CORE_BLOB="9f9d82e6a560c7fa62f0ccf716e63b8f0bccada0"
REFERENCE_BLOB="32eca12b0671841cb19de34c6a6a15f2a65736c0"
HISTORICAL_BLOB="30b9bde830eaa8f00771957d50ed78d21979fa49"
COHORTS=("known_cal","u_cal","known_hold","u_test")
RECORD_COLUMNS=(
 "state_index","policy_index","mode_index","cohort_index",
 "target_person_index","target_generation_index","candidate_count",
 "top1_person_index","top1_generation_index","top1_score","top2_score","margin",
 "predicted_person_correct","predicted_generation_correct",
 "target_person_present_after_filter","target_generation_present_after_filter",
 "filter_excluded_true_person","filter_excluded_true_generation",
)

def stable_bytes(value):
 return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def raw_cell(s,state,policy,mode,cohort):
 e=v.Evaluator(s["candidate_population"]);truth=s["truth"]
 return v.records(e,s[cohort],truth,cohort,state,mode,policy)

def raw_scenario(name):
 s=v.prepare(name)
 persons=sorted({g.person_id for g in s["truth"].values()})
 generations=sorted(s["truth"])
 pi={x:i for i,x in enumerate(persons)};gi={x:i for i,x in enumerate(generations)}
 states=list(v.STATES);policies=list(v.POLICIES);modes=list(v.MODES);cohorts=list(COHORTS)
 rows=[]
 for si,state in enumerate(states):
  for pj,policy in enumerate(policies):
   for mi,mode in enumerate(modes):
    for ci,cohort in enumerate(cohorts):
     for r in raw_cell(s,state,policy,mode,cohort):
      rows.append([
       si,pj,mi,ci,pi[r["target_person_id"]],gi[r["target_generation_id"]],r["candidate_count"],
       pi[r["top1_person_id"]] if r["top1_person_id"] is not None else -1,
       gi[r["top1_generation_id"]] if r["top1_generation_id"] is not None else -1,
       r["top1_score"],r["top2_score"],r["margin"],
       r["predicted_person_correct"],r["predicted_generation_correct"],
       r["target_person_present_after_filter"],r["target_generation_present_after_filter"],
       r["filter_excluded_true_person"],r["filter_excluded_true_generation"],
      ])
 expected=(s["candidate_population"].__len__()+len(s["u_cal"])+len(s["u_test"]))
 expected_records=sum(len(s[c]) for c in COHORTS)*len(states)*len(policies)*len(modes)
 if len(rows)!=expected_records:raise v.ProtocolControlError("raw evidence record count mismatch")
 out={
  "schema":RAW_SCHEMA,"scope":"synthetic-only","scenario":name,
  "protocol":{"base":v.BASE_PROTOCOL_COMMIT,"amended":v.AMENDED_AUDITED_PROTOCOL_HEAD,"implementation_spec":v.IMPLEMENTATION_SPEC_COMMIT},
  "source_blobs":{"core":CORE_BLOB,"reference_wrapper":REFERENCE_BLOB,"historical_scorer":HISTORICAL_BLOB},
  "enums":{"states":states,"policies":policies,"modes":modes,"cohorts":cohorts},
  "person_ids":persons,"generation_ids":generations,"record_columns":list(RECORD_COLUMNS),"records":rows,
 }
 raw=stable_bytes(out);out["payload_sha256"]=hashlib.sha256(raw).hexdigest();return out
