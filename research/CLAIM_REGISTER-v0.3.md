# Claim Register v0.3

## Documented by the experiment

**C3-01 — Attribution persistence is not monotonic in the reference chain.**  
Status: Experimental synthetic result.  
Evidence: Person attribution fell to 9.03% after summarization and later rose to 18.06%, 27.08%, and 25.69%.

**C3-02 — The strongest linkage channel can migrate across transformations.**  
Status: Experimental synthetic result.  
Evidence: The strongest single channel changed style → lexical → style → lexical during the tested chain.

**C3-03 — Removing simulated provenance does not establish unlinkability.**  
Status: Experimental synthetic result.  
Evidence: After paraphrase plus provenance/provider removal, person attribution remained 34.03% against an 8.33% random-person baseline.

**C3-04 — An intermediate near-baseline result does not establish end-to-end unlinkability.**  
Status: Experimental synthetic result / methodological rule.  
Evidence: Summarization reached 9.03%, but later stages re-exposed substantially higher attribution.

## Derived architectural implications

**D3-01 — Privacy state should preserve transformation lineage, not only the final artifact.**  
Status: Derived from C3-01 and C3-04.

**D3-02 — Privacy assessment should model linkage as a dynamic graph whose useful edges may change after every transformation.**  
Status: Derived from C3-02.

**D3-03 — A privacy gate should evaluate the complete intended release pipeline, not certify an intermediate artifact and assume later processing is harmless.**  
Status: Derived from C3-01 and C3-04.

## Hypotheses for later testing

**H3-01 — Transformation order is privacy-relevant.**  
Status: Hypothesis. v0.4 target.

**H3-02 — Some transformations may reveal features that were previously obscured by stronger competing signals.**  
Status: Hypothesis suggested by attribution resurgence; not established mechanistically by v0.3.

**H3-03 — Multi-provider transformation chains may create new provenance/linkage surfaces even when each provider independently removes or changes prior markers.**  
Status: Hypothesis. Not tested with deployed providers.

## Explicitly not claimed

- No claim that any deployed AI provider performs human attribution using these channels.
- No claim that Claude, SynthID, OpenAI, Gemini, LinkedIn, or any production translation system behaves like the transparent proxies.
- No claim that the v0.3 transforms are anonymization techniques suitable for real users.
- No claim that 9.03% constitutes anonymity.
- No claim that the final 25.69% result generalizes outside this deterministic synthetic benchmark.
- No claim that failed re-identification proves absence of another untested linkage mechanism.