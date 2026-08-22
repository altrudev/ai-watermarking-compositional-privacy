from __future__ import annotations
from statistics import median
from lab import open_set_attribution_v08 as v

def _five(values):
 rows=sorted(x for x in values if x is not None)
 if not rows:return {"min":None,"p25":None,"median":None,"p75":None,"max":None}
 def q(p):
  if len(rows)==1:return rows[0]
  z=(len(rows)-1)*p;i=int(z);j=min(i+1,len(rows)-1);f=z-i;return rows[i]*(1-f)+rows[j]*f
 return {"min":rows[0],"p25":q(.25),"median":q(.5),"p75":q(.75),"max":rows[-1]}

def _score_summary(known,unknown):
 return {"known_top1":_five([r["top1_score"] for r in known]),"unknown_top1":_five([r["top1_score"] for r in unknown]),"known_margin":_five([r["margin"] for r in known]),"unknown_margin":_five([r["margin"] for r in unknown])}

def _dist(rows):
 out={}
 for r in rows:out[str(r["candidate_count"])]=out.get(str(r["candidate_count"]),0)+1
 return dict(sorted(out.items(),key=lambda x:int(x[0])))

def evidence_holdout(s,state,policy,mode,cal):
 e=v.Evaluator(s["candidate_population"]);t=s["truth"]
 known=v.records(e,s["known_hold"],t,"known_hold",state,mode,policy);unknown=v.records(e,s["u_test"],t,"u_test",state,mode,policy)
 if cal["status"]=="FEASIBLE":
  h=v.holdout(known,unknown,cal)
 else:
  h={"status":"CALIBRATION_INFEASIBLE","ufir":None,"kcar":None,"kwar":None,"krr":None,"precision":None,"hs_ufir":None,"uper":None,"false_events":[],"high_score_false_events":[],"wrong_known_events":[]}
 h.update({"forced_choice_unknown_rate":sum(r["candidate_count"]>0 for r in unknown)/len(unknown) if unknown else 0,"forced_choice_known_person_top1":sum(r["predicted_person_correct"] for r in known)/len(known) if known else 0,"forced_choice_known_generation_top1":sum(r["predicted_generation_correct"] for r in known)/len(known) if known else 0,"candidate_counts":{"known":_dist(known),"unknown":_dist(unknown)},"score_separation":_score_summary(known,unknown)})
 return h

def build_cell(s,state,policy,mode):
 base=v.cell(s,state,policy,mode);base["holdout"]=evidence_holdout(s,state,policy,mode,base["calibration"]);return base

def narrowing_differentials(cells):
 idx={(c["scenario"],c["state"],c["policy"],c["mode"]):c for c in cells};out=[]
 for n in v.SCENARIOS:
  for st in v.STATES:
   for p in v.POLICIES:
    b=idx[(n,st,p,"global")]["holdout"]
    for m in ("provider_model_narrowed","provider_model_time_narrowed"):
     o=idx[(n,st,p,m)]["holdout"]
     def d(k):return None if b.get(k) is None or o.get(k) is None else o[k]-b[k]
     out.append({"scenario":n,"state":st,"policy":p,"comparison":m+"-global","delta_ufir":d("ufir"),"delta_kcar":d("kcar"),"delta_kwar":d("kwar"),"delta_precision":d("precision"),"delta_true_person_filter_exclusion_rate":d("true_person_filter_exclusion_rate")})
 return out

def reference():
 ss={n:v.prepare(n) for n in v.SCENARIOS};cells=[];by={n:[] for n in v.SCENARIOS}
 for n,s in ss.items():
  for st in v.STATES:
   for p in v.POLICIES:
    for m in v.MODES:
     c=build_cell(s,st,p,m);cells.append(c);by[n].append(c)
 transfers=[v.transfer_summary(a,b,by[a]) for a,b in v.TRANSFERS];controls=v.controls();parity={n:{st:{p:v.parity(n,st,p) for p in v.POLICIES} for st in v.STATES} for n in v.SCENARIOS};parity_pass=all(x for nr in parity.values() for sr in nr.values() for x in sr.values());cohorts={n:{"K":sorted(ss[n]["K"]),"U_cal":sorted(ss[n]["Uc"]),"U_test":sorted(ss[n]["Ut"]),"K_sha256":v.stable_hash(sorted(ss[n]["K"])),"U_cal_sha256":v.stable_hash(sorted(ss[n]["Uc"])),"U_test_sha256":v.stable_hash(sorted(ss[n]["Ut"])),"candidate_generation_count":len(ss[n]["candidate_population"])} for n in v.SCENARIOS};classification=v.classify(cells,transfers,controls["all_pass"] and parity_pass)
 return {"schema":"altru.dev/open-set-false-attribution/0.8","scope":"synthetic-only","protocol":{"base":v.BASE_PROTOCOL_COMMIT,"amended":v.AMENDED_AUDITED_PROTOCOL_HEAD,"implementation_spec":v.IMPLEMENTATION_SPEC_COMMIT},"scenario_config":v.SCENARIOS,"cohorts":cohorts,"controls":controls,"parity":parity,"all_parity_pass":parity_pass,"cells":cells,"narrowing_differentials":narrowing_differentials(cells),"transfers":transfers,"classification":classification}

def summary(r):
 ev=[c for c in r["cells"] if c["holdout"]["status"]=="EVALUATED"]
 med=lambda k:median([c["holdout"][k] for c in ev]) if ev else None
 return {"classification":r["classification"],"core_cells":len(r["cells"]),"calibration_infeasible":sum(c["calibration"]["status"]!="FEASIBLE" for c in r["cells"]),"ufir_ge_10pct_cells":sum(c["holdout"]["ufir"] is not None and c["holdout"]["ufir"]>=.10 for c in r["cells"]),"ufir_ge_20pct_cells":sum(c["holdout"]["ufir"] is not None and c["holdout"]["ufir"]>=.20 for c in r["cells"]),"hs_ufir_ge_5pct_cells":sum(c["holdout"]["hs_ufir"] is not None and c["holdout"]["hs_ufir"]>=.05 for c in r["cells"]),"median_ufir":med("ufir"),"median_kcar":med("kcar"),"median_kwar":med("kwar"),"median_uper":med("uper"),"controls_pass":r["controls"]["all_pass"],"parity_pass":r["all_parity_pass"],"transfer_acceptable":[x["acceptable"] for x in r["transfers"]]}
