from __future__ import annotations

from dataclasses import dataclass, replace, asdict
from math import exp, sqrt
from random import Random
from statistics import mean, pstdev
from typing import Optional, Sequence
import hashlib, json, re

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

TOPICS = {
    "privacy": ("privacy","identity","linkage","metadata","consent","anonymity"),
    "security": ("security","authority","access","verification","attack","recovery"),
    "systems": ("system","transition","state","resource","boundary","invariant"),
    "provenance": ("provenance","watermark","attribution","origin","evidence","trace"),
    "agents": ("agent","memory","tool","directive","model","execution"),
    "networks": ("network","signal","correlation","channel","graph","propagation"),
}
PARAPHRASE = {
    "privacy":"confidentiality","identity":"personhood","linkage":"association","metadata":"contextdata",
    "consent":"permission","anonymity":"unlinkability","security":"protection","authority":"authorization",
    "access":"entry","verification":"validation","attack":"threat","recovery":"restoration","system":"architecture",
    "transition":"change","state":"condition","resource":"capacity","boundary":"limit","invariant":"constraint",
    "provenance":"lineage","watermark":"marker","attribution":"association","origin":"source","evidence":"proof",
    "trace":"trail","agent":"worker","memory":"context","tool":"instrument","directive":"instruction",
    "model":"engine","execution":"operation","network":"mesh","signal":"indicator","correlation":"association",
    "channel":"path","graph":"map","propagation":"spread",
}
def _translation_code(token:str)->str:
    digest=hashlib.sha256(token.encode()).digest()[:7]
    return "z"+ "".join(chr(97+(b%26)) for b in digest)

TRANSLATION = {k:_translation_code(k)
               for k in set(sum((list(v) for v in TOPICS.values()),[])) | set(PARAPHRASE.values())}
REVERSE_PARAPHRASE = {v:k for k,v in PARAPHRASE.items()}
CANONICAL = dict(REVERSE_PARAPHRASE)
CANONICAL.update({v:REVERSE_PARAPHRASE.get(k,k) for k,v in TRANSLATION.items()})
TRANSITIONS=("however","therefore","in practice","more importantly","at the same time","for example","in other words","as a result")
HEDGES=("probably","roughly","usually","potentially","often","sometimes")
SIGNATURES=("the important part","what matters here","the actual issue","the useful question","the main point","the real distinction")
GENERIC=("system","process","information","result","context","risk")

@dataclass(frozen=True)
class Generation:
    person_id:str
    account_id:str
    session_id:str
    generation_id:str
    provider:str
    model:str
    created_minute:int
    watermark_family:str
    topic:str
    text:str

@dataclass(frozen=True)
class Artifact:
    target_generation_id:str
    text:str
    published_minute:int
    provider_hint:Optional[str]
    watermark_family:Optional[str]

@dataclass(frozen=True)
class Metrics:
    samples:int
    person_top1:float
    generation_top1:float
    generation_top5:float
    mean_generation_rank:float
    mean_anonymity_set:float

WEIGHTS=(.30,.20,.10,.10,.05,.25)
SINGLE_SIGNALS={
    "lexical":(1,0,0,0,0,0),
    "semantic":(0,1,0,0,0,0),
    "style":(0,0,1,0,0,0),
    "watermark":(0,0,0,1,0,0),
    "time":(0,0,0,0,0,1),
}

def _tokens(text:str)->list[str]:
    return [x.lower() for x in TOKEN_RE.findall(text)]

def _norm(v:Sequence[float])->float:
    return sqrt(sum(x*x for x in v))

def cosine(a:Sequence[float],b:Sequence[float])->float:
    na,nb=_norm(a),_norm(b)
    if na==0 or nb==0:return 0.0
    return sum(x*y for x,y in zip(a,b))/(na*nb)

def _bucket(token:str,n:int=96)->int:
    return int.from_bytes(hashlib.sha256(token.encode()).digest()[:4],"big")%n

def lexical_vector(text:str,n:int=96)->tuple[float,...]:
    counts=[0.0]*n
    ignored=set("the a an and or to of is are it this that can may still needs own rather than because how surrounding signal changes practical meaning tested against".split())
    for token in _tokens(text):
        if token not in ignored:
            counts[_bucket(token,n)]+=1
    z=_norm(counts)
    return tuple(x/z for x in counts) if z else tuple(counts)


def semantic_vector(text:str)->tuple[float,...]:
    tokens=[CANONICAL.get(x,x) for x in _tokens(text)]
    vec=[float(sum(x in set(vals) for x in tokens)) for vals in TOPICS.values()]
    vec.append(float(sum(x in GENERIC for x in tokens)))
    z=_norm(vec)
    return tuple(x/z for x in vec) if z else tuple(vec)


def style_vector(text:str)->tuple[float,...]:
    tokens=_tokens(text)
    if not tokens:return (0.0,)*12
    sentences=[s for s in SENTENCE_RE.split(text.strip()) if s.strip()] or [text]
    lengths=[max(1,len(_tokens(s))) for s in sentences]
    words=len(tokens); low=text.lower()
    return (
        min(mean(lengths)/30,1), min((pstdev(lengths) if len(lengths)>1 else 0)/15,1),
        len(set(tokens))/words, min(text.count(",")/words*8,1), min(text.count(";")/words*20,1),
        min(text.count("?")/len(sentences)*2,1), min(sum(low.count(x) for x in TRANSITIONS)/len(sentences),1),
        min(sum(low.count(x) for x in HEDGES)/len(sentences),1), min(sum(low.count(x) for x in SIGNATURES)/len(sentences),1),
        min(sum("'" in x for x in tokens)/words*20,1), min(sum(x in {"we","our","i","my"} for x in tokens)/words*10,1),
        min(text.count("\n\n")/len(sentences),1),
    )


def generate_population(persons:int=24,seed:int=41)->list[Generation]:
    if persons<=0: raise ValueError("persons must be positive")
    rows=[]; providers=("provider-a","provider-b","provider-c"); models=("model-1","model-2"); topic_names=list(TOPICS)
    for p in range(persons):
        transition=TRANSITIONS[p%len(TRANSITIONS)]
        hedge=HEDGES[(p*3)%len(HEDGES)]
        signature=SIGNATURES[(p*5)%len(SIGNATURES)]
        person=f"syn-person-{p:04d}"
        for a in range(2):
            account=f"{person}-acct-{a}"; provider=providers[(p+a)%3]; model=models[(p+2*a)%2]; watermark=f"{provider}:{model}"
            for s in range(3):
                session=f"{account}-sess-{s}"; topic=topic_names[(p+a+s)%len(topic_names)]; terms=TOPICS[topic]
                for g in range(2):
                    gid=f"{session}-gen-{g}"; rng=Random(seed*100000+p*1000+a*100+s*10+g); sentences=[]
                    for i in range(6):
                        q=list(terms); rng.shuffle(q); x,y,z,w=q[:4]
                        templates=(
                            f"{transition.capitalize()}, {x} depends on {y}, because {z} can change {w}.",
                            f"{signature.capitalize()} is that {x} and {y} are not interchangeable; {z} needs its own {w}.",
                            f"We {hedge} treat {x} as a signal, but {y} can turn that signal into {z} through {w}.",
                            f"The {x} looks isolated, yet {y} and {z} can combine around {w}.",
                            f"If {x} survives while {y} is removed, does {z} still expose {w}?",
                            f"This is why {x} must be tested against {y}, {z}, and {w}.",
                        )
                        sentences.append(templates[i])
                    text=" ".join(sentences[:3])+"\n\n"+" ".join(sentences[3:]) if p%3==0 else " ".join(sentences)
                    created=300000+(p*13+a*19+s*29+g*7)%300
                    rows.append(Generation(person,account,session,gid,provider,model,created,watermark,topic,text))
    assert all(r.person_id.startswith("syn-") for r in rows)
    return rows


def make_artifacts(population:Sequence[Generation],seed:int=7000)->list[Artifact]:
    artifacts=[]
    for i,row in enumerate(population):
        rng=Random(seed+i)
        sentences=[x.strip() for x in SENTENCE_RE.split(row.text) if x.strip()]
        if len(sentences)>2: sentences=sentences[1:]+sentences[:1]
        text=" ".join(sentences)
        terms=list(TOPICS[row.topic]); rng.shuffle(terms)
        for term in terms[:3]:
            text=re.sub(rf"\b{re.escape(term)}\b",PARAPHRASE[term],text,flags=re.I)
        artifacts.append(Artifact(row.generation_id,text,row.created_minute+rng.randint(2,45),row.provider,row.watermark_family))
    return artifacts


def _features(text:str):
    return lexical_vector(text),semantic_vector(text),style_vector(text)


def evaluate(population:Sequence[Generation],artifacts:Sequence[Artifact],weights:Sequence[float]=WEIGHTS)->Metrics:
    by={r.generation_id:r for r in population}
    cfeat={r.generation_id:_features(r.text) for r in population}
    total=sum(weights)
    w=[x/total for x in weights]
    p1=g1=g5=0; ranks=[]; anonymity=[]
    for artifact in artifacts:
        target=by[artifact.target_generation_id]; af=_features(artifact.text); ranked=[]
        for candidate in population:
            cf=cfeat[candidate.generation_id]
            lx=(cosine(af[0],cf[0])+1)/2; sm=(cosine(af[1],cf[1])+1)/2; st=(cosine(af[2],cf[2])+1)/2
            wm=float(artifact.watermark_family is not None and artifact.watermark_family==candidate.watermark_family)
            provider=float(artifact.provider_hint is not None and artifact.provider_hint==candidate.provider)
            delta=artifact.published_minute-candidate.created_minute
            timing=exp(-delta/50) if delta>=0 else 0.0
            score=sum(x*y for x,y in zip((lx,sm,st,wm,provider,timing),w))
            ranked.append((candidate,score))
        ranked.sort(key=lambda x:(-x[1],x[0].generation_id))
        pos=next(i for i,(c,_) in enumerate(ranked) if c.generation_id==target.generation_id)
        pred=ranked[0][0]
        p1+=pred.person_id==target.person_id; g1+=pos==0; g5+=pos<5; ranks.append(pos+1)
        best=ranked[0][1]; anonymity.append(sum(score>=best-.02 for _,score in ranked))
    n=len(artifacts)
    return Metrics(n,p1/n,g1/n,g5/n,mean(ranks),mean(anonymity))


def edit_stage(a:Artifact)->Artifact:
    return replace(a,text=a.text.replace(" needs its own "," requires separate ").replace(" can combine "," may combine "))


def paraphrase_stage(a:Artifact)->Artifact:
    text=a.text
    for source,target in sorted(PARAPHRASE.items(),key=lambda x:-len(x[0])):
        text=re.sub(rf"\b{re.escape(source)}\b",target,text,flags=re.I)
    text=text.replace("The important part","A key point").replace("What matters here","A relevant point")
    return replace(a,text=text,watermark_family=None,provider_hint=None)


def summarize_stage(a:Artifact)->Artifact:
    sentences=[x.strip() for x in SENTENCE_RE.split(a.text) if x.strip()]
    keep=sentences[::2][:3] if len(sentences)>3 else sentences[:2]
    return replace(a,text=" ".join(keep),published_minute=a.published_minute+90)


def translate_stage(a:Artifact)->Artifact:
    parts=re.split(r"(\W+)",a.text); out=[]
    for part in parts:
        replacement=TRANSLATION.get(part.lower())
        out.append(replacement.capitalize() if replacement and part[:1].isupper() else replacement if replacement else part)
    return replace(a,text="".join(out),published_minute=a.published_minute+120)


def model_edit_stage(a:Artifact)->Artifact:
    sentences=[x.strip() for x in SENTENCE_RE.split(a.text) if x.strip()]
    text=" ".join(reversed(sentences)).replace("We ","The analysis ").replace("?",".")
    return replace(a,text=text,published_minute=a.published_minute+180)


def multi_model_edit_stage(a:Artifact)->Artifact:
    text=a.text.lower()
    text=re.sub(r"\b(however|therefore|usually|probably|potentially|often|sometimes)\b,?\s*","",text,flags=re.I)
    text=text.replace("; ",". ").replace("\n\n"," ")
    return replace(a,text=text,published_minute=a.published_minute+240,watermark_family=None,provider_hint=None)


STAGE_FUNCTIONS=(
    ("edit",edit_stage),("paraphrase",paraphrase_stage),("summarize",summarize_stage),
    ("translate",translate_stage),("model_edit",model_edit_stage),("multi_model_edit",multi_model_edit_stage),
)


def utility(original:Artifact,current:Artifact)->dict:
    original_tokens=set(_tokens(original.text)); current_tokens=set(_tokens(current.text))
    return {
        "semantic_retention":(cosine(semantic_vector(original.text),semantic_vector(current.text))+1)/2,
        "content_word_retention":len(original_tokens & current_tokens)/max(1,len(original_tokens)),
        "length_ratio":len(_tokens(current.text))/max(1,len(_tokens(original.text))),
    }


def run_experiment(persons:int=12,seed:int=41)->dict:
    population=generate_population(persons,seed); original=make_artifacts(population)
    stages={"original":original}; current=original
    for name,fn in STAGE_FUNCTIONS:
        current=[fn(a) for a in current]; stages[name]=current
    stage_results={name:asdict(evaluate(population,arts)) for name,arts in stages.items()}
    channel_results={}
    strongest={}
    for name,arts in stages.items():
        channel_results[name]={signal:asdict(evaluate(population,arts,weights)) for signal,weights in SINGLE_SIGNALS.items()}
        strongest[name]=max(channel_results[name].items(),key=lambda kv:kv[1]["person_top1"])[0]
    utilities={}
    for name,arts in stages.items():
        rows=[utility(o,c) for o,c in zip(original,arts)]
        utilities[name]={key:mean(row[key] for row in rows) for key in rows[0]}
    migration=[]
    names=list(stages)
    for left,right in zip(names,names[1:]):
        if strongest[left]!=strongest[right]:
            migration.append({"from_stage":left,"to_stage":right,"from_channel":strongest[left],"to_channel":strongest[right]})
    random_baseline=1/persons
    final=stage_results["multi_model_edit"]["person_top1"]
    return {
        "research_scope":"synthetic-only",
        "population":{"persons":persons,"generations":len(population)},
        "chain":names,
        "stage_metrics":stage_results,
        "single_channel_metrics":channel_results,
        "strongest_channel_by_stage":strongest,
        "channel_migration_events":migration,
        "utility":utilities,
        "random_person_baseline":random_baseline,
        "final_claim":{
            "status":"supported_for_declared_test" if final<=random_baseline*1.5 else "not_supported",
            "person_top1":final,
            "boundary":"Declared synthetic population and scoring model only; not proof of anonymity."
        },
        "limitations":[
            "Synthetic identities and generated text only.",
            "Translation is a deterministic proxy transformation, not a production translation model.",
            "Model-edit stages are transparent deterministic proxies, not deployed proprietary model behavior.",
            "Failed re-identification is evidence only for the declared test and adversary."
        ],
    }


def main():
    print(json.dumps(run_experiment(),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
