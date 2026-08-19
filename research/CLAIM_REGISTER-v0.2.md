# Claim Register — Textual Compositional Privacy Benchmark v0.2

This register prevents synthetic textual benchmark results from silently becoming deployment or anonymity claims.

| Claim | Maturity | v0.2 treatment |
|---|---|---|
| Multiple text-derived and metadata signals can compose into stronger attribution in the declared synthetic model. | Experimental | Directly measured as correlation gain against the strongest single signal. |
| Removing an abstract provenance/provider signal alone does not necessarily eliminate residual identity linkage. | Experimental | Measured after provenance/provider removal while semantic, lexical, style, and timing evidence remain. |
| Text-derived stylometry and semantic evidence can be attacked after privacy transformation. | Experimental / methodological | The benchmark derives features from generated text and reruns attribution after each transformation. |
| A privacy transformation should be evaluated against an adaptive rather than only a fixed attacker. | Methodological / derived | v0.2 calibrates remaining signal utility on a held-out calibration partition before evaluation. |
| Privacy protection has a measurable utility trade-off. | Experimental / methodological | v0.2 reports a privacy/utility frontier using declared semantic and content-retention metrics. |
| Full-strength transformation proves anonymity. | Explicitly rejected | The harness emits only `SUPPORTED_FOR_DECLARED_TEST` or `NOT_SUPPORTED`. |
| The benchmark reproduces Claude, SynthID, OpenAI, Gemini, or another deployed watermark/provenance system. | Not claimed | Provenance is an abstract synthetic provider/model signal. |
| Synthetic textual results establish real-world unlinkability. | Not claimed | No real identity, provider, account, conversation, or platform data is ingested. |
| The declared semantic-retention score is equivalent to human semantic-quality judgment. | Not claimed | It is an internal controlled-topic feature metric only. |

## Standing distinctions

- Detection ≠ Provenance ≠ Linkability ≠ Attribution ≠ Identity
- De-identification ≠ Unlinkability ≠ Anonymity
- Watermark/provenance removal ≠ Unlinkability
- Component privacy ≠ Compositional privacy
- Privacy transformation ≠ Privacy evidence
- Fixed-attack failure ≠ adaptive-attack failure
- Failed re-identification ≠ proven anonymity
- Experimental support ≠ deployment validation
- Correlation capability ≠ authority to perform identity resolution
