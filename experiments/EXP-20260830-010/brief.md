# EXP-20260830-010 Mechanism-discrimination audit

## Loop

Theory and claim evidence.

## Falsifiable bottleneck

Claim C-008 names three channels but does not specify evidence that separates
them from one another, from contemporary fiscal resources, or from financing
substitution and symbolic compliance.

## Hypothesis

The verified sources from EXP-20260830-009 permit distinct necessary
observables and falsifiers for fiscal absorption, bureaucratic coordination,
and project or state-asset governance, while also showing that the present
evidence cannot establish that historical elite density caused or mediated
these processes.

## Success criteria

- Define one necessary observable, one principal falsifier, and one distinction
  from contemporary fiscal capacity for each proposed channel.
- Identify adjacent explanations that could generate the same observed exit
  outcome, including financing migration, coordinated evasion, political
  connections, and human-capital or social-capital persistence.
- State what the current evidence supports without calling the mechanism
  identified or the historical relationship causal.
- Produce proposed theory prose and claim-ledger rows only as experiment
  artifacts.

The experiment is kept if the three channels become empirically
distinguishable and the resulting claim matches the present evidence. It is
discarded if the channels remain restatements of contemporary fiscal wealth.
It is quarantined if a proposed observable cannot be verified from an original
source. It is invalid if significance, preferred sign, or narrative appeal is
used as the retention rule.

## Permitted files

- `experiments/EXP-20260830-010/**`
- new audit memos under `docs/literature_audit/`

The central manuscript, bibliography, and ledgers are out of scope.

## Inputs

- Base commit: `e178e195704fe6ad6ec353a28081e444995350e7`
- Source audit: `experiments/EXP-20260830-009/artifacts/verified_source_matrix.csv`
- Claim C-008 in `ledgers/claims.csv`
- Mechanism evidence described in the current manuscript and handoff

## Commands

```text
python3 scripts/validate_immutable.py
python3 scripts/validate_ledgers.py
```

## Budget

- Three candidate mechanisms.
- At most two proposed paragraphs of theory prose plus one diagnostic table.
- No new statistical model and no change to the historical proxy.
