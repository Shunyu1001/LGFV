# LLM Labeling Prompt

Use this prompt for preliminary coding only. The model output is not a final
label. A case becomes human validated only after the researcher checks the
original documents and records the result in
`data/processed/human_validated_labels.csv`.

```text
You are assisting with an academic research project on local government
financing vehicle exit reform in China. Your task is to classify one platform
company using the source text supplied below. Use only the supplied source
text. Do not use outside knowledge. Do not infer a formal exit event unless
the text provides direct evidence.

By a formal event, we mean one of the following: removal from a financing
platform list, transfer out of banking-regulator platform management, a
government or regulator notice of exit, an issuer disclosure that the company
no longer undertakes government financing functions, a market-oriented
transformation tied to no-government-financing language, a merger or asset
reorganization that moves platform functions to another entity, or
dissolution, liquidation, bankruptcy, or deregistration.

By continued-function evidence, we mean post-event evidence that the same
company or a successor entity continues to perform public infrastructure
construction, land development, shantytown redevelopment, entrusted
construction, project financing, debt rollover, government purchase service,
PPP, BT, public utility investment, fiscal settlement, policy lending,
government receivables, fiscal subsidies, or other quasi-fiscal functions.

Coding categories:

1. substantive_exit
The company has formal exit evidence and post-event evidence shows that it no
longer performs government financing or quasi-fiscal functions. Routine
commercial operations, budget-funded service contracts, or public utility
businesses do not by themselves make the exit nominal.

2. nominal_exit
The company has formal exit evidence, but the same legal entity continues to
perform similar public project, financing, land development, debt, or
government-support functions after the event.

3. functional_transfer
The original company exits, reduces its platform role, or is reorganized, but
similar public project, financing, land development, debt, or government-support
functions move to another local SOE, subsidiary, merged group, new platform, or
state-owned operating company.

4. liquidation
The company is dissolved, deregistered, liquidated, bankrupted, or otherwise
ceases operations, and the supplied evidence does not show a successor entity
continuing the same public function.

5. unclear
The source text is insufficient, contradictory, or contains only generic reform
language without enough evidence on either the formal event or post-event
function.

Case information:
- Case ID:
- City:
- Province:
- Company name:
- Source packet ID:
- Source document IDs:
- Source date range:

Source text:
<<<
[PASTE SOURCE TEXT HERE]
>>>

Return one JSON object with the following fields. Use null when the source text
does not provide enough information.

{
  "case_id": "",
  "company_name": "",
  "city": "",
  "province": "",
  "formal_event_found": true,
  "formal_event_year": null,
  "formal_event_summary": "",
  "formal_event_source_doc": "",
  "continued_function_found": true,
  "continued_function_summary": "",
  "continued_function_source_doc": "",
  "exit_type": "substantive_exit | nominal_exit | functional_transfer | liquidation | unclear",
  "confidence": "high | medium | low",
  "source_coverage_score": 1,
  "continued_function_evidence_score": 0,
  "alternative_label": "substantive_exit | nominal_exit | functional_transfer | liquidation | unclear | null",
  "missing_information": "",
  "classification_rationale": "",
  "evidence": [
    {
      "doc_id": "",
      "line_reference": "",
      "short_excerpt_or_paraphrase": "",
      "supports": "formal_event | continued_function | transfer | liquidation | ambiguity"
    }
  ],
  "do_not_validate_reason": ""
}

Scoring rules:
- source_coverage_score = 1 when there is only one weak or generic document.
- source_coverage_score = 2 when there is one relevant original or
  near-original document, such as a prospectus, rating report, government
  notice, company announcement, legal opinion, or business registration record.
- source_coverage_score = 3 when the packet contains at least two relevant
  source types and one of them is original or near-original.
- source_coverage_score = 4 when the packet contains a formal-event source and
  an independent post-event function source.
- source_coverage_score = 5 when the packet contains a formal-event source,
  multiple post-event function sources, and either a government or regulator
  source, a business-registration source, or an independent rating source.

- continued_function_evidence_score = 0 when no post-event function evidence is
  present.
- continued_function_evidence_score = 1 when the evidence shows broad public
  utility or city-service work without fiscal or financing links.
- continued_function_evidence_score = 2 when the evidence shows entrusted
  construction, land development, public project management, government
  receivables, fiscal settlement, subsidies, or government support.
- continued_function_evidence_score = 3 when the evidence directly shows
  continuing project financing, debt rollover, government repayment
  responsibility, BT, PPP, policy lending, hidden-debt resolution, or transfer
  of these functions to another entity.

Classification rules:
- Do not classify a case as substantive_exit only because the text says
  market-oriented transformation.
- If the case lacks a formal event but contains useful background evidence,
  classify it as unclear and explain what source is missing.
- If the same company formally exits but continues public project and fiscal
  functions, classify it as nominal_exit unless the evidence shows that those
  functions moved to another entity.
- If a reorganization moves the relevant functions to a new group, subsidiary,
  or local SOE, classify it as functional_transfer.
- If the company is cancelled or liquidated but the same public function moves
  elsewhere, classify it as functional_transfer rather than liquidation.
- If the evidence contains direct exit language and direct continued-function
  evidence, but the legal status of the continued function is ambiguous, choose
  the best label and record the ambiguity in alternative_label and
  missing_information.
```
