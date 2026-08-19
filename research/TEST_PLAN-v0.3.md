# Test Plan v0.3 — Transformation-Chain Attribution Persistence

## Research objective

Measure attribution after each transition in a controlled synthetic text-processing chain and determine whether privacy improvement is monotonic, whether linkage channels migrate, and whether later transformations can re-expose attribution.

## DDC scope boundary

Authorized scope:

- synthetic persons/accounts/sessions/generations only
- locally generated synthetic text only
- transparent deterministic transformation proxies
- declared lexical, semantic, style, simulated provenance/provider, and timing evidence channels
- adversarial re-identification only against the synthetic population created by the harness

Explicitly outside scope:

- real people or accounts
- private provider logs
- scraped profiles/social graphs
- user deanonymization
- external identity corpora
- proprietary watermark reverse engineering
- claims about deployed provider behavior

## Transition chain

1. Original publication derivative
2. Edit
3. Paraphrase and simulated provenance removal
4. Summarization
5. Translation proxy
6. Model-edit proxy
7. Multi-model-edit proxy

Every stage preserves the target synthetic generation ID solely for ground-truth evaluation. The evaluator does not receive that ID as attribution evidence.

## Required measurements at every stage

- person top-1 attribution
- generation top-1 attribution
- generation top-5 attribution
- mean generation rank
- near-best anonymity-set size
- lexical-only attribution
- semantic-only attribution
- stylometry-only attribution
- simulated-watermark-only attribution
- timing-only attribution
- strongest individual channel
- semantic retention
- content-word retention
- length retention

## Required falsification tests

The suite must reject these assumptions if the evidence does not support them:

- more transformations always improve privacy
- provenance removal equals unlinkability
- paraphrasing destroys attribution
- translation necessarily destroys attribution
- model editing necessarily destroys attribution
- the strongest linkage channel remains constant
- a temporary fall near random attribution proves anonymity

## Claim gate

No stage may be labeled `ANONYMOUS` or `UNTRACEABLE`.

The only positive bounded status is `SUPPORTED_FOR_DECLARED_TEST`, and only when the declared residual-linkability threshold is satisfied for the specified synthetic population and scoring model.

A later stage that rises above the threshold invalidates any claim that the complete chain is unlinkable, even if an earlier intermediate stage passed.

## Standing invariants

**Privacy transformation ≠ privacy evidence.**

**Failed re-identification ≠ proven anonymity.**

**Intermediate unlinkability ≠ end-to-end unlinkability.**

**Final artifact state ≠ complete privacy lineage.**

**Transformation order may be security-relevant and must be preserved as evidence.**

## Regression requirements

- deterministic population generation
- synthetic namespace enforcement
- exact required chain order
- material baseline attribution
- combined evidence stronger than every individual channel
- provenance removal verified
- residual linkage measured after provenance removal
- summarization effect measured rather than assumed
- translation semantic preservation checked
- final chain evaluated without assuming success
- at least one channel-migration event required in the reference fixture
- explicit proxy and synthetic-only limitations recorded

## Publication rule

Unexpected or adverse findings are publication results, not test failures, unless they contradict the harness contract. A privacy increase followed by re-identification resurgence must be preserved rather than tuned away.