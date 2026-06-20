# LLM Labeling Prompt

Use this prompt with Claude, ChatGPT, or another large language model. Replace
the bracketed fields with the case information and source text.

```text
You are assisting with an academic research project on local government
financing vehicle (LGFV) exit reform in China. Your task is to classify the
exit type of a platform company using a fixed codebook. Do not invent facts.
Use only the source text provided below.

Coding categories:

1. Substantive exit: The company genuinely ceased performing government
   financing or quasi-fiscal functions and no longer acts as an off-budget
   fiscal arm of the local government.

2. Nominal exit: The company is officially removed from a list or declared
   transformed, but it continues to perform similar government financing,
   infrastructure construction, land development, public project, or implicit
   debt functions.

3. Functional transfer: The original company exits or reduces its role, but its
   financing, construction, debt rollover, or public project functions are
   transferred to another local SOE, subsidiary, merged entity, new group
   company, or quasi-state organization.

4. Liquidation: The company is dissolved, deregistered, liquidated, bankrupted,
   or otherwise ceases operations.

5. Unclear: The available evidence is insufficient or contradictory.

Case information:
- City:
- Province:
- Company name:
- Official exit year:
- Source type:
- Source date:

Source text:
<<<
[PASTE SOURCE TEXT HERE]
>>>

Please return a JSON object with the following fields:

{
  "label": "substantive_exit | nominal_exit | functional_transfer | liquidation | unclear",
  "confidence": "high | medium | low",
  "rationale": "one concise paragraph explaining the classification",
  "evidence": [
    {
      "excerpt": "short quote or paraphrase from the source text",
      "supports": "why this evidence matters"
    }
  ],
  "alternative_label": "the most plausible alternative label, or null",
  "missing_information": "what additional evidence would help resolve uncertainty"
}

Rules:
- If the source text only states that the company completed market-oriented
  transformation, do not automatically classify it as substantive exit.
- If post-exit financing or public project functions continue, consider nominal
  exit.
- If similar functions move to another local SOE or newly created entity,
  consider functional transfer.
- If the evidence is insufficient, choose unclear.
- Do not use outside knowledge.
```

