# ShadowLeak publication status

**Last verified update:** 2026-09-19  
**Current phase:** Dual track — protect unfinished original confirmatory evidence; prospectively define a separate single-investigator exploratory study.  
**Overall status:** **Pre-results on both tracks.** The original four model runs are complete and structurally verified but require independent human annotation. The separate solo pilot has a documented protocol only: **no new model execution, manual labels, or measured findings yet**.  
**Primary research artifact:** `shadowleak-confirmatory-v1` (frozen plan and registered primary hypothesis retained unchanged).

> Read this page first for the state of the publication project. For evidence and checked hashes, use the [2026-09-19 artifact audit](CONFIRMATORY_ARTIFACT_AUDIT_2026-09-19.md). For tasks and exit criteria, use the [publication roadmap](RESEARCH_ROADMAP.md) and linked GitHub issues.

## Evidence gate dashboard

| Gate | State as of 2026-09-19 | Evidence or next action |
|---|---|---|
| Initial framework, synthetic canaries, paired benchmark, workflows, analysis code | **Implemented** | Repository code and unit tests; implementation does not prove empirical efficacy. |
| Frozen protocol and registered model revisions | **Complete** | [Confirmatory protocol](CONFIRMATORY_PROTOCOL_V1.md); [machine-readable plan](../studies/confirmatory_v1.json). |
| Primary model run | **Executed and structurally verified** | 1,860 / 1,860; 0 recorded generation failures; [audit](CONFIRMATORY_ARTIFACT_AUDIT_2026-09-19.md). |
| Three replication model runs | **Executed and structurally verified** | Each 1,860 / 1,860; 0 recorded generation failures; [audit](CONFIRMATORY_ARTIFACT_AUDIT_2026-09-19.md). |
| Original ZIP evidence in durable private storage | **Not yet verified** | GitHub artifacts expire 2026-10-12; [issue #5](https://github.com/yogesh0224/shadowleak/issues/5). Downloads to a chat workspace do not count as permanent storage. |
| One combined blinded annotation queue | **Generated and structurally validated in a temporary workspace; not yet privately archived or handed to annotators** | 7,440 distinct new opaque IDs and a separate protected crosswalk. [Handoff guide](ANNOTATION_HANDOFF.md); [issue #6](https://github.com/yogesh0224/shadowleak/issues/6). |
| Two independent human annotation passes | **Pending; reviewer launch protocol and strict preflight validator implemented** | [Human annotation launch guide](HUMAN_ANNOTATION_LAUNCH.md), [issue #7](https://github.com/yogesh0224/shadowleak/issues/7). Reviewer assignments, durable private handoff and human labels are not verified. |
| Agreement report, adjudication and frozen gold labels | **Pending** | [Issue #7](https://github.com/yogesh0224/shadowleak/issues/7). |
| Statistical code consistency and analysis lock | **Pending review** | [Issue #8](https://github.com/yogesh0224/shadowleak/issues/8); do not inspect protected outcomes to make research-design changes. |
| Preregistered primary result and replication reporting | **Pending adjudicated data** | [Issue #9](https://github.com/yogesh0224/shadowleak/issues/9). |
| Detector/human measurement comparison and benign utility analysis | **Pending adjudicated data** | [Issue #9](https://github.com/yogesh0224/shadowleak/issues/9); preserve the registered vs additional-analysis distinction. |
| Literature positioning | **Draft for review** | [Draft PR #4](https://github.com/yogesh0224/shadowleak/pull/4) adds a working positioning note and updates related work; not a validated novelty claim. |
| Publication manuscript and evidence release | **Pre-results shell only** | [Frozen manuscript shell](MANUSCRIPT_V1.md); [issue #10](https://github.com/yogesh0224/shadowleak/issues/10). |
| Publication/acceptance | **Not submitted or verified** | Do not describe a venue, accepted paper, defense success or privacy guarantee as established. |

## Distinct research tracks (solo-investigator clarification, 2026-09-19)

| Track | What exists | What it can support now | What remains |
|---|---|---|---|
| **A. Original frozen confirmatory study** (`shadowleak-confirmatory-v1`) | Four completed model runs (7,440 total response cases) and structurally audited ZIP evidence. | Execution/provenance description only. **No adjudicated disclosure outcome, paired defense effect, or completed primary hypothesis.** | Privately preserve original ZIPs before reported 2026-10-12 expiry; acquire genuinely independent human annotation/adjudication or transparently report any deviation. [Original issues #5–#9](https://github.com/yogesh0224/shadowleak/issues). |
| **B. New, separate solo exploratory pilot** (`shadowleak-solo-exploratory-v1`) | [Prospective pilot protocol and evidence-specific claim register](SOLO_EXPLORATORY_PROTOCOL_V1.md) written after the owner disclosed working alone; [implementation/execution issue #13](https://github.com/yogesh0224/shadowleak/issues/13). | Research *plan*, not an empirical finding. Proposed one pinned model, 10 **new** synthetic records, 620 planned cases and one investigator's manually recorded labels. | Finalize protocol before fresh execution; validate new run, manually label all successful responses without detector scores or condition key; freeze labels; report only exploratory, descriptive comparisons. |

**Never infer:** the new one-human pilot cannot complete the original registered two-human confirmatory study; the original 7,440 responses must not be quietly repurposed or described as independently labeled. The solo label file is **one researcher's judgment**, not independently adjudicated ground truth. No claim that a model violated a distinct authorization policy or that GuardShield provides production-grade privacy protection is currently supported.

## Verified experiment accounting

- Four registered models; **7,440 completed responses** out of 7,440 planned, with **zero recorded generation failures**.
- Each model: 30 synthetic records, 930 complete defended–undefended pairs, 1,620 attack cases and 240 benign cases.
- Identical benchmark manifests across models, matched internal file hashes and archive digests, and recorded immutable model revisions; see the [audit](CONFIRMATORY_ARTIFACT_AUDIT_2026-09-19.md).
- These numbers concern **execution and data integrity only**. No human-labeled leakage or utility outcome has been verified, and no defense-effect estimate is available.

## Current critical path — two parallel tracks

**Solo pilot:** Follow [the separate exploratory protocol](SOLO_EXPLORATORY_PROTOCOL_V1.md) and [issue #13](https://github.com/yogesh0224/shadowleak/issues/13): freeze the distinct study plan/code first, generate new responses, manually label without detector access, freeze the one-human labels, and only then analyze descriptively. Do not claim publication readiness or significant defense effects from the plan alone.

**Original study:** Preserve originals and leave independent annotation/adjudication gates open unless actual human evidence establishes their completion. The steps below refer **only to the original confirmatory study**.



1. **Preserve originals, P0:** archive the four unchanged ZIP files in private durable storage and verify hashes **before 2026-10-12** ([#5](https://github.com/yogesh0224/shadowleak/issues/5)).
2. **Prepare the annotation handoff, P0:** collision-free packaging and structural validation are complete in a temporary workspace; preserve the exact blinded queue/crosswalk privately and arrange separate human-annotator handoff ([guide](ANNOTATION_HANDOFF.md); [#6](https://github.com/yogesh0224/shadowleak/issues/6)).
3. **Obtain independent human labels, P0:** two independent annotation passes (14,880 individual labeling decisions if all 7,440 rows receive two labels), agreement reporting and disagreement adjudication; freeze gold labels before unblinding ([#7](https://github.com/yogesh0224/shadowleak/issues/7)).
4. **Audit code and execute analysis, P1:** independently check pair-exclusion and clustered inference against the frozen plan, then run the registered and appropriately labeled additional analyses ([#8](https://github.com/yogesh0224/shadowleak/issues/8), [#9](https://github.com/yogesh0224/shadowleak/issues/9)).
5. **Prepare a bounded paper, P1:** complete the related-work review, report results and limitations, obtain critical review, package evidence with access controls and select a venue ([#10](https://github.com/yogesh0224/shadowleak/issues/10)).

## Roles and access boundaries

- **Project owner / research custodian:** authorize durable private archive location, appoint two human annotators and an adjudicator, approve ethics/data-release choices, and maintain custody of the unblinding key.
- **Annotators:** receive only the pooled blinded queue and rubric, not original evidence ZIPs, model identifiers, conditions, detector predictions or the reidentification crosswalk.
- **Research analyst:** works on frozen scripts and mock/synthetic test cases before label freeze; only after adjudication connects the hidden key and performs registered analysis.
- **Repository-maintenance work:** documentation, code, tests and issue tracking may proceed in parallel but must not mutate the frozen execution, leak unblinded inputs or imply a completed result.

## Update policy

Update this page only when the referenced issue is verified against an actual artifact or run. Include a date and evidence link for each status change. Track protocol deviations explicitly. Keep executed, annotated, adjudicated, analyzed, submitted and accepted as separate states. Do not convert an `[x]` for implemented code into an `[x]` for validated scientific evidence.

## Progress log

| Date | Verified change |
|---|---|
| 2026-09-12 | Registered confirmatory primary and replication workflows completed; see linked workflow run IDs in the [audit](CONFIRMATORY_ARTIFACT_AUDIT_2026-09-19.md). |
| 2026-09-19 | Four original ZIPs retrieved and structurally/hash audited without response-text inspection; cross-model annotation-ID collision identified. |
| 2026-09-19 | Research owner confirmed they are working alone. Created a **separate prospective solo exploratory pilot protocol** and [issue #13](https://github.com/yogesh0224/shadowleak/issues/13); did not alter or inspect the original study's outcomes. Both tracks remain pre-results. |
| 2026-09-19 | Added a human reviewer launch and blinded double-annotation quality-control procedure with synthetic-fixture tests. This is operational readiness only; no human labels, durable private archive, or human reviewer assignments have been verified. |
| 2026-09-19 | A pooled 7,440-row annotation queue with 7,440 distinct opaque IDs and a separate private crosswalk was generated and structurally checked in a temporary workspace. The [packaging code and handoff guide](ANNOTATION_HANDOFF.md) were prepared; durable private preservation and human annotation remain pending. |
| 2026-09-19 | Publication positioning proposed in [draft PR #4](https://github.com/yogesh0224/shadowleak/pull/4); six scoped GitHub issues (#5–#10) opened and this progress tracker added. |
