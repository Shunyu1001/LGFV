# Read-only equation review

Reviewed file:
/Users/shunyuhao/.codex/worktrees/lgfv-validation-inference/LGFV/paper/sections/empirical_strategy.tex

The reviewed subsection is "Design-based estimation", lines 151-209 at the
time of review on 2026-09-10. No paper file was edited by this worker.

## Finding

At lines 179-185, define the variance sum over noncensus strata with n_h>=2,
or explicitly define every census contribution as zero before evaluating any
sample variance. As written, the all-strata display includes s^2_e,h for a
singleton census, where its n_h-1 denominator is zero. The intended result is
correct, and lines 186-191 already explain the relevant uncertainty distinction;
the needed clarification is that zero is assigned by the census design, not
obtained by multiplying an undefined sample variance by zero. If any noncensus
stratum has n_h=1, the engine keeps the point but returns no total variance.

## Agreement with the implementation

The mean in lines 166-168 matches estimate_mean exactly, conditional on fixed
predictions and the declared full frame. The design-expectation argument in
lines 171-175 is correct under positive known pi and complete selected responses.
The displayed SRSWOR formula has the correct N_h/N weights, finite-population
correction, and n_h denominator. Sample residual variance uses n_h-1.

The projection in lines 196-199 matches estimate_fixed_x. The Gram matrix is
known from full-frame X, not the labeled subset. Line 202 correctly identifies
the fixed, full-rank, associational target; the implementation additionally
rejects nonfinite X and condition numbers above 1e8.

Lines 153-159 correctly restrict this implementation to a fixed-prediction
finite-frame special case and do not claim the full cross-fitted algorithm.
Lines 186-191 correctly restrict census zero variance to label selection and
make no census efficiency claim. Lines 203-209 correctly reject missing controls,
response loss, and undefined outcomes as reasons to reuse proposed weights.
Failure to find a formal event is not a binary zero.

## Adapter requirements

The displayed F contains city-platform cases while this engine accepts issuer
units. The coordinator must verify an admissible one-to-one issuer/city-platform
mapping for this analytical F; the existing 94-case and 67-issuer objects are not
interchangeable. Status declarations are checked for consistency by the engine,
but actual evidence of approval, selection, eligibility, and human review must
be authenticated by the adapter. The prose about implemented checks should not
be interpreted as machine authentication of those source facts.

No additional mathematical mismatch was found in the reviewed subsection.
