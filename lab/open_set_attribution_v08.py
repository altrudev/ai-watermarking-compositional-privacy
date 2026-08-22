from __future__ import annotations
from dataclasses import asdict, replace
from math import exp, sqrt
from statistics import median
import hashlib, json
from lab.transformation_chain_lab import (Artifact,Generation,evaluate,generate_population,lexical_vector,make_artifacts,model_edit_stage,multi_model_edit_stage,paraphrase_stage,semantic_vector,style_vector,summarize_stage)

BASE_PROTOCOL_COMMIT="7ed99ac13e39946b2853c2b4e4ddf4193728bce9"
AMENDED_AUDITED_PROTOCOL_HEAD="0a3f970beb200be97e04b9bc86b56584021e040a"
IMPLEMENTATION_SPEC_COMMIT="87a01c30b4d7ea1185fbaba48966f8786a6b60a7"
POLICIES={
 "canonical_combined":(.30,.20,.10,.10,.05,.25),
 "text_only":(.45,.30,.25,0,0,0),
 "provenance_heavy":(.20,.15,.10,.25,.15,.15),
 "timing_heavy":(.20,.15,.10,.10,.05,.40),
}
SCENARIOS={
 "S1":{"known":8,"u_cal":8,"u_test":8,"seed":41,"artifact_seed":7000},
 "S2":{"known":16,"u_cal":8,"u_test":8,"seed":73,"artifact_seed":9001},
 "S3":{"known":24,"u_cal":12,"u_test":12,"seed":101,"artifact_seed":12007},
}
STATES=("published_derivative","provenance_removed","post_transform_chain")
MODES=("global","provider_model_narrowed","provider_model_time_narrowed")
TRANSFERS=(("S1","S2"),("S2","S3"))
SCORE_GRID=tuple(i/100 for i in range(40,100)); MARGIN_GRID=tuple(i/100 for i in range(31)); CORE_CELLS=108
class ProtocolControlError(RuntimeError): pass

def _norm(v): return sqrt(sum(x*x for x in v))
def _sparse(v): return tuple((i,x) for i,x in enumerate(v) if x)
def _cos(a,an,b,bn): return 0.0 if an==0 or bn==0 else sum(x*y for x,y in zip(a,b))/(an*bn)
def stable_hash(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def provenance_state(a):
 p,w=a.provider_hint,a.watermark_family
 if p is None and w is None:return "absent"
 if p is None or w is None:raise ProtocolControlError("partial provenance")
 if not w.startswith(p+":"):raise ProtocolControlError("inconsistent provenance")
 return "complete"

def transform(a,state):
 if state=="published_derivative":return a
 if state=="provenance_removed":return paraphrase_stage(a)
 if state=="post_transform_chain":
  a=paraphrase_stage(a); a=summarize_stage(a); a=model_edit_stage(a); return multi_model_edit_stage(a)
 raise ValueError(state)

def split_known(arts,pop):
 by={g.generation_id:g for g in pop}; cal=[]; hold=[]; counts={g.person_id:[0,0] for g in pop}; seen=set()
 for a in arts:
  if a.target_generation_id in seen:raise ProtocolControlError("duplicate known artifact")
  seen.add(a.target_generation_id); t=by.get(a.target_generation_id)
  if t is None:raise ProtocolControlError("known target absent from K")
  if a.target_generation_id.endswith("-gen-0"):cal.append(a);counts[t.person_id][0]+=1
  elif a.target_generation_id.endswith("-gen-1"):hold.append(a);counts[t.person_id][1]+=1
  else:raise ProtocolControlError("partition suffix")
 if {a.target_generation_id for a in cal}&{a.target_generation_id for a in hold}:raise ProtocolControlError("partition overlap")
 if any(v!=[6,6] for v in counts.values()):raise ProtocolControlError("partition counts")
 return cal,hold

def prepare(name):
 c=SCENARIOS[name]; pop=generate_population(c["known"]+c["u_cal"]+c["u_test"],c["seed"])
 people=sorted({g.person_id for g in pop},key=lambda p:hashlib.sha256(f"{name}|{p}".encode()).digest())
 K=frozenset(people[:c["known"]]); Uc=frozenset(people[c["known"]:c["known"]+c["u_cal"]]); Ut=frozenset(people[c["known"]+c["u_cal"]:])
 if K&Uc or K&Ut or Uc&Ut:raise ProtocolControlError("cohort overlap")
 cand=[g for g in pop if g.person_id in K]; ucp=[g for g in pop if g.person_id in Uc]; utp=[g for g in pop if g.person_id in Ut]
 if not all(g.person_id.startswith("syn-") for g in pop):raise ProtocolControlError("non-synthetic id")
 if {g.generation_id for g in cand}&{g.generation_id for g in ucp+utp}:raise ProtocolControlError("unknown in candidate db")
 truth={g.generation_id:g for g in pop}; arts=make_artifacts(pop,c["artifact_seed"])
 ka=[a for a in arts if truth[a.target_generation_id].person_id in K]; uc=[a for a in arts if truth[a.target_generation_id].person_id in Uc]; ut=[a for a in arts if truth[a.target_generation_id].person_id in Ut]
 kcal,khold=split_known(ka,cand)
 return {"scenario":name,"candidate_population":cand,"truth":truth,"K":K,"Uc":Uc,"Ut":Ut,"known_cal":kcal,"known_hold":khold,"u_cal":uc,"u_test":ut}

class Evaluator:
 def __init__(self,pop):
  self.pop=list(pop);self.tc={};self.cc={};self.c=[]
  for g in self.pop:
   lx=lexical_vector(g.text);sm=semantic_vector(g.text);st=style_vector(g.text);self.c.append((g,lx,sm,_norm(sm),st,_norm(st)))
 def _af(self,text):
  if text not in self.tc:
   lx=lexical_vector(text);sm=semantic_vector(text);st=style_vector(text);self.tc[text]=(_sparse(lx),sm,_norm(sm),st,_norm(st))
  return self.tc[text]
 def _filtered(self,a,mode):
  ps=provenance_state(a)
  if mode=="global" or ps=="absent":return self.c
  rows=[r for r in self.c if r[0].provider==a.provider_hint and r[0].watermark_family==a.watermark_family]
  if mode=="provider_model_narrowed":return rows
  if mode!="provider_model_time_narrowed":raise ValueError(mode)
  return [r for r in rows if 0<=a.published_minute-r[0].created_minute<=60]
 def _components(self,a,mode):
  k=(a.text,a.published_minute,a.provider_hint,a.watermark_family,mode)
  if k in self.cc:return self.cc[k]
  alx,asm,asmn,ast,astn=self._af(a.text);out=[]
  for g,clx,csm,csmn,cst,cstn in self._filtered(a,mode):
   lx=sum(v*clx[i] for i,v in alx);sm=_cos(asm,asmn,csm,csmn);st=_cos(ast,astn,cst,cstn);wm=float(a.watermark_family is not None and a.watermark_family==g.watermark_family);pr=float(a.provider_hint is not None and a.provider_hint==g.provider);d=a.published_minute-g.created_minute;tm=exp(-d/50) if d>=0 else 0.0
   out.append((g,((lx+1)/2,(sm+1)/2,(st+1)/2,wm,pr,tm)))
  self.cc[k]=tuple(out);return self.cc[k]
 def rank(self,a,mode,weights):
  z=sum(weights);w=tuple(x/z for x in weights);rows=[(g,sum(x*y for x,y in zip(comp,w))) for g,comp in self._components(a,mode)];rows.sort(key=lambda r:(-r[1],r[0].generation_id));return rows

def score(e,a,t,cohort,mode,policy,state):
 a=transform(a,state); ranked=e.rank(a,mode,POLICIES[policy]);one=ranked[0] if ranked else None;two=ranked[1] if len(ranked)>1 else None;persons={g.person_id for g,_ in ranked};gens={g.generation_id for g,_ in ranked};inK=any(g.person_id==t.person_id for g in e.pop);ginK=any(g.generation_id==t.generation_id for g in e.pop)
 return {"target_person_id":t.person_id,"target_generation_id":t.generation_id,"cohort":cohort,"state":state,"policy":policy,"mode":mode,"candidate_count":len(ranked),"top1_person_id":one[0].person_id if one else None,"top1_generation_id":one[0].generation_id if one else None,"top1_score":one[1] if one else None,"top2_score":two[1] if two else None,"margin":one[1]-two[1] if one and two else None,"predicted_person_correct":bool(one and one[0].person_id==t.person_id),"predicted_generation_correct":bool(one and one[0].generation_id==t.generation_id),"target_person_present_after_filter":t.person_id in persons,"target_generation_present_after_filter":t.generation_id in gens,"filter_excluded_true_person":inK and t.person_id not in persons,"filter_excluded_true_generation":ginK and t.generation_id not in gens}
def records(e,arts,truth,cohort,state,mode,policy): return [score(e,a,truth[a.target_generation_id],cohort,mode,policy,state) for a in arts]
def decision(r,ts,tm):
 if r["candidate_count"]==0:return False,"NO_CANDIDATE"
 if r["candidate_count"]==1:return False,"INSUFFICIENT_COMPARATORS"
 return (True,"ACCEPTED") if r["top1_score"]>=ts and r["margin"]>=tm else (False,"THRESHOLD_REJECTED")
def _known(rs,ts,tm):
 c=w=q=0
 for r in rs:
  a,_=decision(r,ts,tm)
  if not a:q+=1
  elif r["predicted_person_correct"]:c+=1
  else:w+=1
 n=len(rs);return {"kcar":c/n if n else 0,"kwar":w/n if n else 0,"krr":q/n if n else 0,"correct":c,"wrong":w,"rejected":q}
def _unknown(rs,ts,tm):
 a=sum(decision(r,ts,tm)[0] for r in rs);return {"ufir":a/len(rs) if rs else 0,"accepted":a}
def _dist(rs):
 d={}
 for r in rs:d[str(r["candidate_count"])]=d.get(str(r["candidate_count"]),0)+1
 return dict(sorted(d.items(),key=lambda x:int(x[0])))
def _five(vals):
 x=sorted(v for v in vals if v is not None)
 if not x:return {"min":None,"p25":None,"median":None,"p75":None,"max":None}
 def q(p):
  if len(x)==1:return x[0]
  z=(len(x)-1)*p;i=int(z);j=min(i+1,len(x)-1);f=z-i;return x[i]*(1-f)+x[j]*f
 return {"min":x[0],"p25":q(.25),"median":q(.5),"p75":q(.75),"max":x[-1]}
def _score_summary(kr,ur):
 return {"known_top1":_five([r["top1_score"] for r in kr]),"unknown_top1":_five([r["top1_score"] for r in ur]),"known_margin":_five([r["margin"] for r in kr]),"unknown_margin":_five([r["margin"] for r in ur])}
def calibrate(kr,ur):
 f=[]
 for ts in SCORE_GRID:
  for tm in MARGIN_GRID:
   k=_known(kr,ts,tm);u=_unknown(ur,ts,tm)
   if u["ufir"]<=.05 and k["kcar"]>=.40 and k["kwar"]<=.10:f.append((ts,tm,k,u))
 pairs=[[x[0],x[1]] for x in f];base={"known_count":len(kr),"u_cal_count":len(ur),"feasible_pair_count":len(f),"feasible_set_sha256":stable_hash(pairs),"candidate_counts":{"known":_dist(kr),"unknown":_dist(ur)}}
 if not f:return {**base,"status":"CALIBRATION_INFEASIBLE","tau_score":None,"tau_margin":None,"calibration_ufir":None,"calibration_kcar":None,"calibration_kwar":None,"high_score_reference":None}
 f.sort(key=lambda x:(-x[2]["kcar"],x[3]["ufir"],x[2]["kwar"],-x[1],-x[0]));ts,tm,k,u=f[0];good=[r["top1_score"] for r in kr if decision(r,ts,tm)[0] and r["predicted_person_correct"]]
 if not good:return {**base,"status":"CALIBRATION_INFEASIBLE","tau_score":None,"tau_margin":None,"calibration_ufir":None,"calibration_kcar":None,"calibration_kwar":None,"high_score_reference":None}
 return {**base,"status":"FEASIBLE","tau_score":ts,"tau_margin":tm,"calibration_ufir":u["ufir"],"calibration_kcar":k["kcar"],"calibration_kwar":k["kwar"],"high_score_reference":median(good)}
def _person_rates(rs,ts,tm,known):
 d={}
 for r in rs:
  p=r["target_person_id"];d.setdefault(p,[0,0]);d[p][1]+=1;a,_=decision(r,ts,tm);d[p][0]+=int(a and (r["predicted_person_correct"] if known else True))
 return {p:h/n for p,(h,n) in d.items()}
def holdout(kr,ur,cal):
 if cal["status"]!="FEASIBLE":return {"status":"CALIBRATION_INFEASIBLE","ufir":None,"kcar":None,"kwar":None,"krr":None,"precision":None,"hs_ufir":None,"uper":None,"forced_choice_unknown_rate":sum(r["candidate_count"]>0 for r in ur)/len(ur) if ur else 0,"forced_choice_known_person_top1":sum(r["predicted_person_correct"] for r in kr)/len(kr) if kr else 0,"forced_choice_known_generation_top1":sum(r["predicted_generation_correct"] for r in kr)/len(kr) if kr else 0,"false_events":[],"high_score_false_events":[],"wrong_known_events":[],"candidate_counts":{"known":_dist(kr),"unknown":_dist(ur)},"score_separation":_score_summary(kr,ur)}
 ts,tm=cal["tau_score"],cal["tau_margin"];k=_known(kr,ts,tm);u=_unknown(ur,ts,tm);ref=cal["high_score_reference"];fe=[];he=[];we=[]
 for r in ur:
  if decision(r,ts,tm)[0]:
   x={q:r[q] for q in ("target_person_id","target_generation_id","top1_person_id","top1_generation_id","top1_score","margin","candidate_count")};fe.append(x)
   if r["top1_score"]>=ref:he.append(x)
 for r in kr:
  if decision(r,ts,tm)[0] and not r["predicted_person_correct"]:we.append({q:r[q] for q in ("target_person_id","target_generation_id","top1_person_id","top1_generation_id","top1_score","margin","candidate_count")})
 den=k["kcar"]+k["kwar"]+u["ufir"];upr=_person_rates(ur,ts,tm,False);kpr=_person_rates(kr,ts,tm,True)
 return {"status":"EVALUATED","ufir":u["ufir"],"kcar":k["kcar"],"kwar":k["kwar"],"krr":k["krr"],"precision":k["kcar"]/den if den else 1.0,"hs_ufir":len(he)/len(ur) if ur else 0,"uper":sum(v>0 for v in upr.values())/len(upr) if upr else 0,"median_person_ufir":median(upr.values()) if upr else None,"max_person_ufir":max(upr.values()) if upr else None,"median_person_kcar":median(kpr.values()) if kpr else None,"min_person_kcar":min(kpr.values()) if kpr else None,"true_person_filter_exclusion_rate":sum(r["filter_excluded_true_person"] for r in kr)/len(kr) if kr else 0,"forced_choice_unknown_rate":sum(r["candidate_count"]>0 for r in ur)/len(ur) if ur else 0,"forced_choice_known_person_top1":sum(r["predicted_person_correct"] for r in kr)/len(kr) if kr else 0,"forced_choice_known_generation_top1":sum(r["predicted_generation_correct"] for r in kr)/len(kr) if kr else 0,"false_events":fe,"high_score_false_events":he,"wrong_known_events":we,"candidate_counts":{"known":_dist(kr),"unknown":_dist(ur)},"score_separation":_score_summary(kr,ur)}
def cell(s,state,policy,mode):
 e=Evaluator(s["candidate_population"]);t=s["truth"];kc=records(e,s["known_cal"],t,"known_cal",state,mode,policy);uc=records(e,s["u_cal"],t,"u_cal",state,mode,policy);ca=calibrate(kc,uc);kh=records(e,s["known_hold"],t,"known_hold",state,mode,policy);ut=records(e,s["u_test"],t,"u_test",state,mode,policy);return {"scenario":s["scenario"],"state":state,"policy":policy,"mode":mode,"calibration":ca,"holdout":holdout(kh,ut,ca)}
def transfer(src,dst):
 if src["calibration"]["status"]!="FEASIBLE":return {"status":"SOURCE_CALIBRATION_INFEASIBLE","ufir":None,"kcar":None,"kwar":None}
 e=Evaluator(dst["candidate_population"]);t=dst["truth"];kr=records(e,dst["known_hold"],t,"known_hold",src["state"],src["mode"],src["policy"]);ur=records(e,dst["u_test"],t,"u_test",src["state"],src["mode"],src["policy"]);h=holdout(kr,ur,src["calibration"]);return {"status":h["status"],"ufir":h["ufir"],"kcar":h["kcar"],"kwar":h["kwar"]}
def transfer_summary(source,destination,cells):
 dst=prepare(destination);rs=[transfer(c,dst) for c in cells];ok=[r for r in rs if r["status"]=="EVALUATED"];m=lambda k:median([r[k] for r in ok]) if ok else None;u=len(rs)-len(ok);a=u==0 and m("ufir")<=.10 and m("kcar")>=.30 and m("kwar")<=.10;return {"source":source,"destination":destination,"unavailable":u,"median_ufir":m("ufir"),"median_kcar":m("kcar"),"median_kwar":m("kwar"),"acceptable":a,"cells":rs}
def classify(cs,trs,controls):
 if not controls:return "CONTROL_FAILED"
 ev=[c for c in cs if c["holdout"]["status"]=="EVALUATED"]
 if any(c["holdout"]["ufir"]>=.20 for c in ev) or sum(c["holdout"]["ufir"]>=.10 for c in ev)>=.20*CORE_CELLS or sum(c["holdout"]["hs_ufir"]>=.05 for c in ev)>=.10*CORE_CELLS:return "FALSE_ATTRIBUTION_RISK_OBSERVED"
 if len(cs)==CORE_CELLS and all(c["calibration"]["status"]=="FEASIBLE" for c in cs):
  uf=[c["holdout"]["ufir"] for c in ev];kc=[c["holdout"]["kcar"] for c in ev];kw=[c["holdout"]["kwar"] for c in ev];pr=[c["holdout"]["precision"] for c in ev]
  if sum(x<=.05 for x in uf)>=.90*CORE_CELLS and not any(x>=.10 for x in uf) and sum(x>=.40 for x in kc)>=.80*CORE_CELLS and not any(x>=.10 for x in kw) and median(pr)>=.90 and len(trs)==2 and all(x["acceptable"] for x in trs):return "OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX"
 return "CONTEXT_DEPENDENT_OPEN_SET_CONTROL"
def parity(name,state,policy,n=6):
 s=prepare(name);arts=[transform(a,state) for a in s["known_hold"][:n]];can=asdict(evaluate(s["candidate_population"],arts,POLICIES[policy]));e=Evaluator(s["candidate_population"]);rs=[score(e,a,s["truth"][a.target_generation_id],"known_hold","global",policy,"published_derivative") for a in arts];p=sum(r["predicted_person_correct"] for r in rs)/len(rs);g=sum(r["predicted_generation_correct"] for r in rs)/len(rs);return p==can["person_top1"] and g==can["generation_top1"]
def controls():
 s=prepare("S1");e=Evaluator(s["candidate_population"]);a=s["known_hold"][0];t=s["truth"][a.target_generation_id];z=replace(a,provider_hint="provider-z",watermark_family="provider-z:model-9");r=score(e,z,t,"control","provider_model_narrowed","canonical_combined","published_derivative");c1=decision(r,.4,0)==(False,"NO_CANDIDATE");re=Evaluator([g for g in s["candidate_population"] if g.person_id!=t.person_id]);rr=score(re,a,t,"control","global","canonical_combined","published_derivative");c2=not rr["target_person_present_after_filter"];alt=replace(a,target_generation_id="syn-hidden-label");c3=e.rank(a,"global",POLICIES["canonical_combined"])==e.rank(alt,"global",POLICIES["canonical_combined"]);c4=stable_hash([(g.generation_id,x) for g,x in e.rank(a,"global",POLICIES["canonical_combined"])])==stable_hash([(g.generation_id,x) for g,x in e.rank(a,"global",POLICIES["canonical_combined"])]);g=next(x for x in s["candidate_population"] if x.generation_id.endswith("-gen-1"));aa=next(x for x in s["known_hold"] if x.target_generation_id==g.generation_id);one=score(Evaluator([g]),aa,g,"control","global","canonical_combined","published_derivative");c5=decision(one,0,0)==(False,"INSUFFICIENT_COMPARATORS")
 try:e.rank(replace(a,provider_hint=None),"provider_model_narrowed",POLICIES["canonical_combined"]);c6=False
 except ProtocolControlError:c6=True
 ca,ho=split_known(s["known_cal"]+s["known_hold"],s["candidate_population"]);c7=all(x.target_generation_id.endswith("-gen-0") for x in ca) and all(x.target_generation_id.endswith("-gen-1") for x in ho);return {"C1":c1,"C2":c2,"C3":c3,"C4":c4,"C5":c5,"C6":c6,"C7":c7,"all_pass":all((c1,c2,c3,c4,c5,c6,c7))}
def narrowing_differentials(cs):
 idx={(c["scenario"],c["state"],c["policy"],c["mode"]):c for c in cs};out=[]
 for n in SCENARIOS:
  for st in STATES:
   for p in POLICIES:
    b=idx[(n,st,p,"global")]["holdout"]
    for m in ("provider_model_narrowed","provider_model_time_narrowed"):
     o=idx[(n,st,p,m)]["holdout"];d=lambda k:None if b.get(k) is None or o.get(k) is None else o[k]-b[k]
     out.append({"scenario":n,"state":st,"policy":p,"comparison":m+"-global","delta_ufir":d("ufir"),"delta_kcar":d("kcar"),"delta_kwar":d("kwar"),"delta_precision":d("precision"),"delta_true_person_filter_exclusion_rate":d("true_person_filter_exclusion_rate")})
 return out
def reference():
 ss={n:prepare(n) for n in SCENARIOS};cs=[];by={n:[] for n in SCENARIOS}
 for n,s in ss.items():
  for st in STATES:
   for p in POLICIES:
    for m in MODES:
     x=cell(s,st,p,m);cs.append(x);by[n].append(x)
 trs=[transfer_summary(a,b,by[a]) for a,b in TRANSFERS];co=controls();pa={n:{st:{p:parity(n,st,p) for p in POLICIES} for st in STATES} for n in SCENARIOS};pp=all(v for n in pa.values() for st in n.values() for v in st.values());coh={n:{"K":sorted(ss[n]["K"]),"U_cal":sorted(ss[n]["Uc"]),"U_test":sorted(ss[n]["Ut"]),"K_sha256":stable_hash(sorted(ss[n]["K"])),"U_cal_sha256":stable_hash(sorted(ss[n]["Uc"])),"U_test_sha256":stable_hash(sorted(ss[n]["Ut"])),"candidate_generation_count":len(ss[n]["candidate_population"])} for n in SCENARIOS};cl=classify(cs,trs,co["all_pass"] and pp);return {"schema":"altru.dev/open-set-false-attribution/0.8","scope":"synthetic-only","protocol":{"base":BASE_PROTOCOL_COMMIT,"amended":AMENDED_AUDITED_PROTOCOL_HEAD,"implementation_spec":IMPLEMENTATION_SPEC_COMMIT},"scenario_config":SCENARIOS,"cohorts":coh,"controls":co,"parity":pa,"all_parity_pass":pp,"cells":cs,"narrowing_differentials":narrowing_differentials(cs),"transfers":trs,"classification":cl}
