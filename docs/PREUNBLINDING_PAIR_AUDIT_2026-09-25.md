# Pre-unblinding analysis-code audit: incomplete matched pairs (2026-09-25)

**Study:** `shadowleak-confirmatory-v1`  
**Change class:** Pre-outcome-inspection implementation correction proposed for peer review; **not** a change to the frozen plan, hypothesis, model generations, human-label rubric, or registered analysis family.  
**Status:** Patch and regression tests proposed on a separate branch. Do not merge or label this statistical gate complete until tests and independent methodological review have been recorded.

## Detected mismatch

The preregistered failure policy in `studies/confirmatory_v1.json` states that a matched prompt pair with either failed member is excluded from paired inference. `research.benchmark_analysis.paired_effect` does exclude such pairs, but the existing `research.inference._paired_record_effect` accepted any record containing at least one observation in each arm and averaged the arms independently. An unmatched observation could therefore affect the bootstrap result, meaning the paired point estimate and record-bootstrap estimate might use different cases.

The 2026-09-19 execution audit reports zero **recorded model-generation failures** in the original 7,440 cases. This code-path defect is therefore **not** proof of an observed bias in those original outcomes. It still matters for failure/exclusion handling and reproducibility, and it should be corrected before annotators unblind labels.

## Proposed implementation

- Validate that each `pair_id` belongs to one record, and that there is no duplicate condition within a pair.
- Retain **both observations or neither** for the two fixed conditions `none` and `guardshield-v1`.
- Build the record-bootstrap sample only from complete pairs, discarding any record with zero usable pairs for that particular analysis.
- Preserve the original **equal-record-weighted** bootstrap estimand and fixed random seed/iteration count. The pooled complete-pair rate in `paired_effect` and the equal-record-weighted bootstrap point estimate can differ **if different records have different numbers of complete pairs**. Report that distinction transparently and do not equate their estimands after exclusions.
- In a bootstrap draw where a record is selected more than once, uniquely namespace both its sampled record ID and its pair IDs. This keeps duplicate sampled records logically separate without changing their data.
- Do not backfill, retry, relabel, or inspect original response text to justify this code change.

## Synthetic regression-test cases

1. A fully complete four-record example remains deterministic with the fixed seed.
2. An unmatched positive no-defense observation is excluded from **both** the record-level estimate and all bootstrap draws; compare against the same synthetic data with the unmatched observation removed.
3. Duplicate pair/condition rows fail closed.
4. A `pair_id` spanning two records fails closed.
5. Only one record with complete pairs is insufficient for record-cluster bootstrap.

These tests use hand-constructed synthetic outcomes only; they do not read the original experiment's model responses, condition-level outcomes, or human labels.

## Review and lock gates

- [ ] Run the relevant unit tests and the full research test suite on this branch; record command, Python/dependency versions, and results.
- [ ] Have another reviewer inspect matched-pair exclusion, equal-record weighting, and consistency with the frozen estimand.
- [ ] Confirm whether annotation exclusions occur and whether any record has unequal numbers of complete pairs; report both paired and cluster-weighted estimands when applicable.
- [ ] Record the final analysis-code commit SHA **before** accessing any condition-joined human outcomes.
- [ ] Do not mark original analysis issue #8 complete until the wider gates (failure accounting, correction, primary/replication reporting, and reproducibility) are satisfied.

**Scientific claim boundary:** This is a software integrity correction, not a new privacy or defense-effect result. The confirmatory study still requires genuine independent double annotation, adjudication, preserved evidence, and the originally registered primary analysis.
