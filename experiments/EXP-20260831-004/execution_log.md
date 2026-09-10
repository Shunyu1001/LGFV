# Interrupted execution record

This record was reconstructed on 2026-09-10 from the execution transcript.
The original registration and authorization are in commit `2fe53f1`.

| Attempt | Date | Action and observed result | Disposition |
|---|---|---|---|
| A01 | 2026-09-02 | `build_probability_validation_frame.py --integrate-exp004` produced 67 eligible units. `validate_probability_validation_frame.py` rejected the Dongyangguang geography excerpt because it joined noncontinuous fields with ellipsis and compressed punctuation. | crash |
| A02 | 2026-09-02 | The continuous Dongyangguang excerpt was corrected and the builder rerun. Validation then rejected the Guiyang identity excerpt for the same continuity problem. | crash |
| A03 | 2026-09-02 | Guiyang's four excerpts were replaced with continuous cache text. Validation passed source checks but stopped at stale metric expectations: observed 87 unique/1 multiple versus expected 86/2 among the original 88 gaps. The user interrupted the turn. | crash |

No attempt changed an exit label or drew a sample. Candidate counts alone did
not establish acceptance. The resumed coordinator restored Experiment 001's
metrics byte for byte and registered a separate corrective experiment before
further execution.

Other unsuccessful diagnostic calls included an unmatched shell glob,
unavailable PyYAML, a misnamed parser helper, an unsuccessful patch context,
and an out-of-range text-preview slice. They produced no accepted evidence
or final data changes. The registered manifest hashes were subsequently
checked successfully using the existing parser.
