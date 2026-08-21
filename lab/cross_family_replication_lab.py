from __future__ import annotations
from dataclasses import asdict, replace
from itertools import combinations, permutations
from statistics import median
from typing import Callable, Sequence
from math import exp, sqrt
import hashlib, json, re
from lab.noncommutativity_lab import CachedEvaluator
from lab.transformation_chain_lab import Artifact,HEDGES,SENTENCE_RE,SIGNATURES,TOPICS,TRANSITIONS,evaluate,generate_population,make_artifacts,lexical_vector,semantic_vector,style_vector
POLICIES={"canonical_combined":(0.30,0.20,0.10,0.10,0.05,0.25),"text_only":(0.45,0.30,0.25,0,0,0),"lexical_heavy":(0.55,0.15,0.10,0.05,0.05,0.10),"timing_heavy":(0.20,0.15,0.10,0.10,0.05,0.40),"metadata_light":(0.35,0.20,0.15,0.10,0.05,0.15)}
SCENARIOS={"S1":{"persons":8,"seed":41,"artifact_seed":7000},"S2":{"persons":8,"seed":73,"artifact_seed":9001},"S3":{"persons":12,"seed":41,"artifact_seed":9001},"S4":{"persons":12,"seed":101,"artifact_seed":7000},"S5":{"persons":16,"seed":73,"artifact_seed":7000},"S6":{"persons":16,"seed":101,"artifact_seed":9001}}
SCENARIO_TRANSFERS=(("S1","S2"),("S3","S4"),("S5","S6"))
LEXICAL_GENERALIZE={"depends":"relates","change":"affect","isolated":"separate","combine":"join","survives":"remains","removed":"omitted","expose":"reveal","tested":"checked","interchangeable":"equivalent","important":"relevant"}
LEXICAL_SUBSTITUTE={"signal":"indicator","turn":"convert","through":"via","requires":"needs","separate":"distinct","looks":"appears","yet":"though","still":"continues","must":"should","why":"reason"}
def _replace_words(text,mapping):
    result=text
    for source,target in sorted(mapping.items(),key=lambda item:-len(item[0])): result=re.sub(rf"\b{re.escape(source)}\b",target,result,flags=re.I)
    return result
def _sentences(text): return [row.strip() for row in SENTENCE_RE.split(text.strip()) if row.strip()]
def lexical_generalize(a): return replace(a,text=_replace_words(a.text,LEXICAL_GENERALIZE))
def style_flatten(a):
    text=a.text
    for phrase in sorted((*TRANSITIONS,*HEDGES,*SIGNATURES),key=len,reverse=True): text=re.sub(rf"\b{re.escape(phrase)}\b,?\s*","",text,flags=re.I)
    text=text.replace(";",",").replace("\n\n"," "); return replace(a,text=re.sub(r"\s+"," ",text).strip())
def sentence_rotate(a):
    rows=_sentences(a.text)
    if len(rows)>1: rows=rows[1:]+rows[:1]
    return replace(a,text=" ".join(rows))
def bounded_compress(a):
    rows=_sentences(a.text); keep=rows if len(rows)<=2 else [row for i,row in enumerate(rows) if i%3!=1]
    if not keep and rows:keep=[rows[0]]
    return replace(a,text=" ".join(keep))
def topic_abstraction(a):
    mapping={}
    for terms in TOPICS.values():
        rep=terms[0]
        for term in terms:mapping[term]=rep
    return replace(a,text=_replace_words(a.text,mapping))
def clause_reorder(a):
    output=[]
    for sentence in _sentences(a.text):
        punctuation=";" if ";" in sentence else "," if "," in sentence else None
        if punctuation:
            left,right=sentence.split(punctuation,1); terminal="." if sentence.endswith(".") else "?" if sentence.endswith("?") else ""; right=right.rstrip(".?").strip(); output.append(f"{right}{punctuation} {left.strip()}{terminal}".strip())
        else:output.append(sentence)
    return replace(a,text=" ".join(output))
def segment_rechunk(a):
    rows=_sentences(a.text)
    if len(rows)<2:return a
    rebuilt=[]; i=0
    while i<len(rows):
        if i+1<len(rows):rebuilt.append(f"{rows[i].rstrip('.?!')}; {rows[i+1].rstrip('.?!')}."); i+=2
        else:rebuilt.append(rows[i]); i+=1
    return replace(a,text=" ".join(rebuilt))
def lexical_substitute(a): return replace(a,text=_replace_words(a.text,LEXICAL_SUBSTITUTE))
FAMILIES={"structural_normalization":{"lexical_generalize":lexical_generalize,"style_flatten":style_flatten,"sentence_rotate":sentence_rotate,"bounded_compress":bounded_compress},"representation_segmentation":{"topic_abstraction":topic_abstraction,"clause_reorder":clause_reorder,"segment_rechunk":segment_rechunk,"lexical_substitute":lexical_substitute}}
def _apply(artifacts,transforms,path):
    current=list(artifacts)
    for name in path: current=[transforms[name](a) for a in current]
    return current
def partition_artifacts(artifacts):
    cal=[]; hold=[]
    for a in artifacts:(cal if hashlib.sha256(a.target_generation_id.encode()).digest()[-1]&1==0 else hold).append(a)
    if not cal or not hold:raise ValueError("Deterministic partition produced an empty calibration or holdout set")
    return cal,hold
def _pearson(xs,ys):
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys); dx=[v-mx for v in xs]; dy=[v-my for v in ys]; den=(sum(v*v for v in dx)*sum(v*v for v in dy))**.5
    return 0.0 if den==0 else sum(a*b for a,b in zip(dx,dy))/den
def _pair_key(l,r):return f"{l}|{r}"
def _sparse(v):return tuple((i,x) for i,x in enumerate(v) if x)
def _norm(v):return sqrt(sum(x*x for x in v))
def _cosine_pre(a,an,b,bn):return 0.0 if an==0 or bn==0 else sum(x*y for x,y in zip(a,b))/(an*bn)
class MatrixEvaluator:
    """Top-1-only multi-policy evaluator preserving canonical ranking/tie semantics."""
    def __init__(self,population):
        self.population=list(population); self.by_generation={r.generation_id:r for r in self.population}; self._text_cache={}; self._metadata_cache={}
        self.candidates=[]
        for r in self.population:
            lx=lexical_vector(r.text); sm=semantic_vector(r.text); st=style_vector(r.text)
            self.candidates.append((r,lx,sm,_norm(sm),st,_norm(st)))
    def _text_features(self,text):
        cached=self._text_cache.get(text)
        if cached is None:
            lx=lexical_vector(text); sm=semantic_vector(text); st=style_vector(text); cached=(_sparse(lx),sm,_norm(sm),st,_norm(st)); self._text_cache[text]=cached
        return cached
    def _metadata_rows(self,a):
        key=(a.target_generation_id,a.published_minute,a.provider_hint,a.watermark_family); rows=self._metadata_cache.get(key)
        if rows is None:
            rows=[]
            for r,*_ in self.candidates:
                wm=float(a.watermark_family is not None and a.watermark_family==r.watermark_family); provider=float(a.provider_hint is not None and a.provider_hint==r.provider); delta=a.published_minute-r.created_minute; timing=exp(-delta/50) if delta>=0 else 0.0; rows.append((wm,provider,timing))
            rows=tuple(rows); self._metadata_cache[key]=rows
        return rows
    def evaluate_all(self,artifacts):
        counts={name:[0,0] for name in POLICIES}; n=len(artifacts)
        for a in artifacts:
            truth=self.by_generation[a.target_generation_id]; alx,asm,asmn,ast,astn=self._text_features(a.text); metadata=self._metadata_rows(a); best={name:(-float('inf'),None) for name in POLICIES}
            for idx,(candidate,clx,csm,csmn,cst,cstn) in enumerate(self.candidates):
                lexical=sum(value*clx[i] for i,value in alx); semantic=_cosine_pre(asm,asmn,csm,csmn); style=_cosine_pre(ast,astn,cst,cstn); wm,provider,timing=metadata[idx]; components=((lexical+1)/2,(semantic+1)/2,(style+1)/2,wm,provider,timing)
                for pname,w in POLICIES.items():
                    score=sum(x*y for x,y in zip(components,w)); old_score,old_cand=best[pname]
                    if score>old_score or (score==old_score and (old_cand is None or candidate.generation_id<old_cand.generation_id)):best[pname]=(score,candidate)
            for pname,(_score,pred) in best.items(): counts[pname][0]+=pred.person_id==truth.person_id; counts[pname][1]+=pred.generation_id==truth.generation_id
        return {name:{"person_top1":vals[0]/n,"generation_top1":vals[1]/n} for name,vals in counts.items()}
def pairwise_effects_all(evaluator,calibration,transforms):
    names=tuple(transforms); effects={p:{} for p in POLICIES}; rows={}
    for l,r in combinations(names,2):
        lrarts=_apply(calibration,transforms,(l,r)); rlarts=_apply(calibration,transforms,(r,l)); lm=evaluator.evaluate_all(lrarts); rm=evaluator.evaluate_all(rlarts); key=_pair_key(l,r); rows[key]={"left_before_right":[l,r],"right_before_left":[r,l],"final_text_difference_fraction":sum(a.text!=b.text for a,b in zip(lrarts,rlarts))/len(lrarts),"final_metadata_identical":all((a.target_generation_id,a.published_minute,a.provider_hint,a.watermark_family)==(b.target_generation_id,b.published_minute,b.provider_hint,b.watermark_family) for a,b in zip(lrarts,rlarts)),"policy_effects":{}}
        for pname in POLICIES:
            pe=lm[pname]["person_top1"]-rm[pname]["person_top1"]; ge=lm[pname]["generation_top1"]-rm[pname]["generation_top1"]; effects[pname][key]=pe; rows[key]["policy_effects"][pname]={"person_top1_difference":pe,"generation_top1_difference":ge}
    return {"effects_by_policy":effects,"pairs":rows}
def full_paths_all(evaluator,holdout,transforms):
    result={p:[] for p in POLICIES}
    for path in permutations(tuple(transforms)):
        metrics=evaluator.evaluate_all(_apply(holdout,transforms,path))
        for pname in POLICIES: result[pname].append({"path":list(path),"observed_person_top1":metrics[pname]["person_top1"]})
    return result
def correlate_paths(path_rows,effects,transform_names):
    pairs=list(combinations(tuple(transform_names),2)); scores=[]; observed=[]
    for row in path_rows:
        pos={name:i for i,name in enumerate(row["path"])}; score=0.0
        for l,r in pairs:
            effect=effects[_pair_key(l,r)]; score+=effect if pos[l]<pos[r] else -effect
        scores.append(score); observed.append(row["observed_person_top1"])
    return _pearson(scores,observed)
def _holdout_class(r):return "predictive" if r>=.70 else "partial" if r>=.30 else "not_predictive"
def _transfer_class(r):return "transfer_supported" if r>=.50 else "weak_context_dependent_transfer" if r>=.20 else "transfer_not_supported"
def commuting_control(evaluator,holdout,weights):
    left=[replace(row,text=" ".join(row.text.lower().split())) for row in holdout]; right=[replace(row,text=" ".join(row.text.split()).lower()) for row in holdout]; lm=evaluator.evaluate(left,weights); rm=evaluator.evaluate(right,weights); return {"control_pass":all(a.text==b.text for a,b in zip(left,right)) and lm.person_top1==rm.person_top1 and lm.generation_top1==rm.generation_top1,"person_top1_difference":lm.person_top1-rm.person_top1,"generation_top1_difference":lm.generation_top1-rm.generation_top1}
def pairwise_effects(evaluator,calibration,transforms,weights):
    # compatibility focused helper using exact predecessor evaluator
    effects={}; rows={}
    for l,r in combinations(tuple(transforms),2):
        lrarts=_apply(calibration,transforms,(l,r)); rlarts=_apply(calibration,transforms,(r,l)); lm=evaluator.evaluate(lrarts,weights); rm=evaluator.evaluate(rlarts,weights); key=_pair_key(l,r); effects[key]=lm.person_top1-rm.person_top1; rows[key]={}
    return {"effects":effects,"pairs":rows}
def predict_paths(evaluator,holdout,transforms,weights,effects):
    rows=[]
    for path in permutations(tuple(transforms)):
        observed=evaluator.evaluate(_apply(holdout,transforms,path),weights).person_top1; pos={name:i for i,name in enumerate(path)}; score=sum(effects[_pair_key(l,r)] if pos[l]<pos[r] else -effects[_pair_key(l,r)] for l,r in combinations(tuple(transforms),2)); rows.append({"path":list(path),"pairwise_score":score,"observed_person_top1":observed})
    return {"path_count":len(rows),"pearson_r":_pearson([r["pairwise_score"] for r in rows],[r["observed_person_top1"] for r in rows]),"paths":rows}
def prepare_scenario(name):
    p=SCENARIOS[name]; pop=generate_population(p["persons"],p["seed"]); arts=make_artifacts(pop,seed=p["artifact_seed"]); cal,hold=partition_artifacts(arts); return pop,cal,hold,CachedEvaluator(pop)
def scorer_parity(pop,hold,evaluator):
    transforms=FAMILIES["structural_normalization"]; sample=_apply(hold,transforms,tuple(transforms)); return asdict(evaluator.evaluate(sample,POLICIES["canonical_combined"]))==asdict(evaluate(pop,sample,POLICIES["canonical_combined"]))
def matrix_scorer_parity(pop,hold,exact,fast):
    transforms=FAMILIES["structural_normalization"]
    sample=_apply(hold,transforms,tuple(transforms))
    fast_metrics=fast.evaluate_all(sample)
    policy_parity={}
    for pname,weights in POLICIES.items():
        exact_metric=exact.evaluate(sample,weights)
        policy_parity[pname]=(
            fast_metrics[pname]["person_top1"]==exact_metric.person_top1
            and fast_metrics[pname]["generation_top1"]==exact_metric.generation_top1
        )
    return {"all_policies":all(policy_parity.values()),"by_policy":policy_parity}
def run_scenario(scenario_name: str) -> dict:
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")
    p=SCENARIOS[scenario_name]
    pop=generate_population(p["persons"],p["seed"])
    arts=make_artifacts(pop,seed=p["artifact_seed"])
    cal,hold=partition_artifacts(arts)
    exact=CachedEvaluator(pop)
    historical_parity=scorer_parity(pop,hold,exact)
    fast=MatrixEvaluator(pop)
    matrix_parity=matrix_scorer_parity(pop,hold,exact,fast)
    del exact
    left=[replace(row,text=" ".join(row.text.lower().split())) for row in hold]
    right=[replace(row,text=" ".join(row.text.split()).lower()) for row in hold]
    left_metrics=fast.evaluate_all(left)
    right_metrics=fast.evaluate_all(right)
    text_equal=all(a.text==b.text for a,b in zip(left,right))
    controls={pname:{
        "control_pass": text_equal and left_metrics[pname]==right_metrics[pname],
        "person_top1_difference": left_metrics[pname]["person_top1"]-right_metrics[pname]["person_top1"],
        "generation_top1_difference": left_metrics[pname]["generation_top1"]-right_metrics[pname]["generation_top1"],
    } for pname in POLICIES}
    families={}
    for fname,transforms in FAMILIES.items():
        pair=pairwise_effects_all(fast,cal,transforms)
        paths=full_paths_all(fast,hold,transforms)
        holdout_cells=[]
        for pname in POLICIES:
            r=correlate_paths(paths[pname],pair["effects_by_policy"][pname],transforms)
            holdout_cells.append({
                "scenario":scenario_name,
                "family":fname,
                "policy":pname,
                "calibration_samples":len(cal),
                "holdout_samples":len(hold),
                "pearson_r":r,
                "classification":_holdout_class(r),
            })
        families[fname]={
            "transforms":list(transforms),
            "pairwise_map":pair["pairs"],
            "effects_by_policy":pair["effects_by_policy"],
            "paths_by_policy":paths,
            "holdout_cells":holdout_cells,
        }
    return {
        "schema":"altru.dev/cross-family-replication-scenario/0.7",
        "research_scope":"synthetic-only",
        "protocol_commit":"786ebb3d097d999e15f72cbfce536e59566206a1",
        "scenario":scenario_name,
        "parameters":p,
        "population_generations":len(pop),
        "calibration_samples":len(cal),
        "holdout_samples":len(hold),
        "historical_scorer_parity":historical_parity,
        "matrix_scorer_parity":matrix_parity,
        "commuting_controls":controls,
        "families":families,
    }

def aggregate_scenario_results(shards: Sequence[dict]) -> dict:
    by_name={row["scenario"]:row for row in shards}
    if set(by_name)!=set(SCENARIOS):
        raise ValueError("Aggregate requires exactly one shard for every predeclared scenario")
    if any(row.get("protocol_commit")!="786ebb3d097d999e15f72cbfce536e59566206a1" for row in shards):
        raise ValueError("Scenario shard protocol mismatch")
    holdout_cells=[]; pairwise_maps={}; parity={}; matrix_parity={}; controls={}
    for s in SCENARIOS:
        shard=by_name[s]; parity[s]=bool(shard["historical_scorer_parity"]); matrix_parity[s]=shard["matrix_scorer_parity"]; controls[s]=shard["commuting_controls"]
        for fname in FAMILIES:
            frow=shard["families"][fname]
            pairwise_maps[f"{s}|{fname}"]=frow["pairwise_map"]
            holdout_cells.extend(frow["holdout_cells"])
    transfer_cells=[]
    for src,dst in SCENARIO_TRANSFERS:
        for fname,transforms in FAMILIES.items():
            source=by_name[src]["families"][fname]
            destination=by_name[dst]["families"][fname]
            for pname in POLICIES:
                r=correlate_paths(destination["paths_by_policy"][pname],source["effects_by_policy"][pname],transforms)
                transfer_cells.append({
                    "source_scenario":src,
                    "destination_scenario":dst,
                    "family":fname,
                    "policy":pname,
                    "pearson_r":r,
                    "classification":_transfer_class(r),
                })
    all_controls=all(row["control_pass"] for sc in controls.values() for row in sc.values())
    all_parity=all(parity.values()) and all(row["all_policies"] for row in matrix_parity.values())
    H=sum(r["pearson_r"]>=.70 for r in holdout_cells)
    T=sum(r["pearson_r"]>=.50 for r in transfer_cells)
    hm=median(r["pearson_r"] for r in holdout_cells)
    tm=median(r["pearson_r"] for r in transfer_cells)
    family_coverage=all(any(r["family"]==f and r["scenario"]==s and r["pearson_r"]>=.70 for r in holdout_cells) for f in FAMILIES for s in SCENARIOS)
    policy_coverage=all(any(r["policy"]==p and r["pearson_r"]>=.50 for r in transfer_cells) for p in POLICIES)
    if not all_controls or not all_parity:
        status="CONTROL_FAILED"
    elif H>=42 and T>=15 and hm>=.70 and tm>=.50 and family_coverage and policy_coverage:
        status="MECHANISM_REPLICATED_WITH_TRANSFER_FOR_DECLARED_MATRIX"
    elif H<30 or T<9:
        status="MECHANISM_NOT_REPLICATED"
    else:
        status="CONTEXT_DEPENDENT_REPLICATION"
    return {
        "schema":"altru.dev/cross-family-replication/0.7",
        "research_scope":"synthetic-only",
        "predecessor_commit":"c29b40db9000d3e0a49c2c25fadab215d3084480",
        "protocol_commit":"786ebb3d097d999e15f72cbfce536e59566206a1",
        "scenario_shards":[s for s in SCENARIOS],
        "historical_scorer_parity":parity,
        "matrix_scorer_parity":matrix_parity,
        "commuting_controls":controls,
        "pairwise_maps":pairwise_maps,
        "holdout_cells":holdout_cells,
        "transfer_cells":transfer_cells,
        "aggregate":{
            "holdout_predictive_count":H,
            "holdout_cell_count":len(holdout_cells),
            "transfer_supported_count":T,
            "transfer_cell_count":len(transfer_cells),
            "median_holdout_r":hm,
            "median_transfer_r":tm,
            "family_scenario_coverage":family_coverage,
            "policy_transfer_coverage":policy_coverage,
            "all_controls_pass":all_controls,
            "all_scorer_parity_pass":all_parity,
        },
        "claim":{"status":status,"boundary":"Declared synthetic transform families, adversary policies, scenarios, and scoring model only; not proof of anonymity, real-person attribution, or deployed-provider behavior."},
    }

def run_reference_matrix() -> dict:
    return aggregate_scenario_results([run_scenario(name) for name in SCENARIOS])

def main() -> None:
    import sys
    if len(sys.argv)>=3 and sys.argv[1]=="scenario":
        print(json.dumps(run_scenario(sys.argv[2]),indent=2,sort_keys=True))
        return
    if len(sys.argv)>=3 and sys.argv[1]=="aggregate":
        shards=[]
        for path in sys.argv[2:]:
            with open(path,"r",encoding="utf-8") as handle:
                shards.append(json.load(handle))
        print(json.dumps(aggregate_scenario_results(shards),indent=2,sort_keys=True))
        return
    raise SystemExit("Usage: python -m lab.cross_family_replication_lab scenario S1 | aggregate shard-S1.json ... shard-S6.json")

if __name__=="__main__":
    main()
