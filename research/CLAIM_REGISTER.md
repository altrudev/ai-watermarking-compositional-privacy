# Claim Register — Unlinkability Lab v0.1

The purpose of this register is to prevent experimental results from silently becoming stronger public claims.

| Claim | Maturity | v0.1 treatment |
|---|---|---|
| Multiple weak signals can compose into stronger attribution in the synthetic model. | Experimental | Directly measured as correlation gain. |
| Removing a simulated watermark alone does not necessarily eliminate linkage. | Experimental | Tested against remaining semantic/style/time signals. |
| Privacy transformations require adversarial re-identification testing. | Methodological / derived | Enforced by the test harness and claim gate. |
| A failed re-identification test proves anonymity. | Explicitly rejected | The harness never emits a universal anonymity claim. |
| Anthropic currently links Claude-watermarked text to individual users. | Not claimed | Outside v0.1 evidence and outside the experiment. |
| The simulated watermark accurately reproduces Claude/SynthID behavior. | Not claimed | It is an abstract provider/model provenance channel only. |
| Real-world unlinkability can be established from synthetic tests alone. | Not claimed | Synthetic results are architecture evidence, not deployment proof. |

## Standing distinctions

- Detection ≠ Provenance ≠ Linkability ≠ Attribution ≠ Identity
- De-identification ≠ Unlinkability ≠ Anonymity
- Watermark removal ≠ Unlinkability
- Component privacy ≠ Compositional privacy
- Privacy transformation ≠ Privacy evidence
- Failed re-identification ≠ proven anonymity
- Correlation capability ≠ authority to perform identity resolution
