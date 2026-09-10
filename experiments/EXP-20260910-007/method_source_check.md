# Method source check

Opened on 10 September 2026:

- Egami, Hinck, Stewart, and Wei (2023), NeurIPS publication page:
  https://proceedings.neurips.cc/paper_files/paper/2023/hash/d862f7f5445255090de13b825b880d59-Abstract-Conference.html
- Original paper:
  https://proceedings.neurips.cc/paper_files/paper/2023/file/d862f7f5445255090de13b825b880d59-Paper-Conference.pdf

The title, four authors, conference year, volume, and DOI match the existing
egami2023dsl bibliography record. Section 2 requires known positive annotation
probabilities; Section 4 and Equation 4 give the prediction-plus-weighted-
residual construction with cross-fitting.

The manuscript's new derivation is narrower: condition on a finite assembled
frame and fixed auxiliary predictions, then average over stratified selection
without replacement. Its finite-population correction and census interpretation
are explicitly described as that special case. It does not identify this small
implementation with the paper's full learned-nuisance estimator or substitute
proposed probabilities for actual sampled and returned human records.

No quotations are reproduced. No source change, new outcome, or national
representativeness assumption is introduced by this method check.
