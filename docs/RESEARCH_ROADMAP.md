# ShadowLeak — Publication Roadmap

**Status date:** 2026-09-19 · **Current work:** preserve evidence and prepare independent human annotation.  
**Source of truth for live progress:** [Publication status](PUBLICATION_STATUS.md).  
**Evidence for completed executions:** [2026-09-19 artifact audit](CONFIRMATORY_ARTIFACT_AUDIT_2026-09-19.md).  
**Tracking:** [GitHub issues](https://github.com/yogesh0224/shadowleak/issues).  
**Frozen design (DO NOT RETROACTIVELY CHANGE):** [Confirmatory protocol](CONFIRMATORY_PROTOCOL_V1.md), [registered study plan](../studies/confirmatory_v1.json), [reporting plan](../studies/reporting_plan_v1.json). The [pre-results manuscript shell](MANUSCRIPT_V1.md) must retain its original evidence-class distinctions.

This roadmap tracks **implemented infrastructure**, **executed model runs**, **verified data**, **independent labels**, **completed analysis**, and **publication** separately. An implemented method is not an empirical result; a passing model-generation job is not an adjudicated privacy finding.

## Current snapshot

| Stage | Status | Gate for completion |
|---|---|---|
| 0. Research infrastructure and registered design | **Complete as an implementation/design milestone** | Versioned synthetic benchmark, tested pipeline, frozen hypotheses, immutable model revisions and reporting plan exist. |
| 1. Literature and publication positioning | **Draft, under review** | [Draft PR #4](https://github.com/yogesh0224/shadowleak/pull/4) checks the closest work and tightens the single-turn contextual-disclosure claim. Novelty is not established merely by this draft. |
| 2. Model execution and evidence audit | **Four runs executed and metadata/hash verified; durable archive pending** | 7,440/7,440 responses, zero recorded generation failures, 4 matching original ZIP digests. Complete [#5](https://github.com/yogesh0224/shadowleak/issues/5). |
| 3. Annotation preparation, double labeling, adjudication | **Packaging and reviewer quality gate implemented; durable handoff and human labels pending** | Preserve evidence and distribute two private copies [#5](https://github.com/yogesh0224/shadowleak/issues/5), [#6](https://github.com/yogesh0224/shadowleak/issues/6); follow [human annotation launch](HUMAN_ANNOTATION_LAUNCH.md), then obtain genuine independent labels and adjudicate [#7](https://github.com/yogesh0224/shadowleak/issues/7). |
| 4. Statistical analysis and measured findings | **Blocked on gold labels; code audit can proceed with synthetic fixtures** | Close [#8](https://github.com/yogesh0224/shadowleak/issues/8) and [#9](https://github.com/yogesh0224/shadowleak/issues/9). |
| 5. Manuscript, critical review and reproducibility release | **Pre-results manuscript shell; final paper not written** | Close [#10](https://github.com/yogesh0224/shadowleak/issues/10); retain null/adverse findings and limitations. |
| 6. Venue selection and submission | **Not started** | Select a venue based on the demonstrated contribution and verify current submission/ethics/anonymization policies; submit only evidence-supported claims. |

## Stage 0 — Completed infrastructure (historical development)

- [x] Implement synthetic-data generators, versioned attack and benign templates, two defense conditions, model adapters and detector components.
- [x] Implement matched-case execution, independent-label tooling, adjudication pipeline, record-clustered uncertainty code, and automated research tests.
- [x] Complete the two-model feasibility pilot and its documented execution checks.
- [x] Freeze confirmatory Benchmark v2, four immutable model revisions, 30-record design, primary hypothesis, reporting plan and failure policy.
- [x] Prepare a preregistered manuscript **shell** and evidence-package tooling.

**Evidence boundary:** Features or tests being present does not mean downstream annotation, detector validity or scientific findings have been completed.

## Stage 1 — Defensible research positioning (draft for review)

- [x] Prepare a proposed contribution around *measurement sensitivity*: compare detector-derived and adjudicated-human disclosure conclusions under a fixed defense, without asserting the comparison will reveal disagreement.
- [x] Prepare related-work and threat-model revisions in [draft PR #4](https://github.com/yogesh0224/shadowleak/pull/4).
- [ ] Check the full texts of the closest contextual privacy and leakage-evaluation papers, including relevant 2025–2026 work, before claiming novelty.
- [ ] Preserve the frozen confirmatory primary claim on adjudicated disclosure; label new detector-versus-human comparisons as secondary/exploratory in accordance with the reporting plan.
- [ ] Finalize a one-page contribution statement once supported by actual results.

**Exit gate:** A precise threat model and candidate contribution, an up-to-date comparable-work table, and no unsupported “first”, universal-privacy or authorization-breach claims.

## Stage 2 — Preserve and verify original model evidence (P0)

- [x] Primary Qwen2.5-1.5B model workflow completed, 1,860/1,860 cases and 0 recorded generation failures.
- [x] All three replication jobs completed with the same per-model case count and recorded failure count.
- [x] Retrieve four ZIPs, verify each GitHub archive digest, ZIP integrity, internal run-summary hashes, model revisions, identical manifests and full case/pair counts. See [audit](CONFIRMATORY_ARTIFACT_AUDIT_2026-09-19.md).
- [ ] **Before 2026-10-12**, store all four original ZIPs in durable private storage; recheck and privately log archival hashes/location/access controls. [Issue #5](https://github.com/yogesh0224/shadowleak/issues/5).

**Exit gate:** Evidence originals preserved outside GitHub Actions, with a verified chain of custody and no public exposure of model responses or annotation keys. A temporary chat download alone **does not** satisfy this gate.

## Stage 3 — Prepare blinded human annotation (P0)

- [x] Implement and test pooled-ID packaging: four source queues together contain 7,440 rows and reuse original IDs; generate 7,440 unique opaque pooled IDs, a separate private reversible crosswalk, and preserve original response text. One package was generated and structurally verified in a temporary workspace. [Handoff guide](ANNOTATION_HANDOFF.md), [issue #6](https://github.com/yogesh0224/shadowleak/issues/6).
- [x] Validate 7,440 rows, unique IDs, source-archive hashes, label blanks, output digests and absence of explicit model/defense/case metadata. Package-generation shuffling is implemented; residual unblinding through unchanged response wording is documented in [handoff guide](ANNOTATION_HANDOFF.md).
- [ ] Preserve the **exact generated** pooled queue and private crosswalk in separate, access-controlled durable storage; then appoint two independent human annotators and an adjudicator and calibrate the rubric on separate pilot data. Temporary workspace output does not satisfy the archival/handoff gate.
- [x] Implement and test a **pre-adjudication human-file quality gate** for source integrity, all 7,440 labels per annotator, benign utility completeness, unchanged stimuli, rationales and distinct reviewer IDs. This validates files, not human independence. See [human launch protocol](HUMAN_ANNOTATION_LAUNCH.md).
- [ ] Obtain two independent **human** labels per successful confirmatory response (up to 14,880 separate decisions), document independent procedure, run the pre-adjudication gate, report raw agreement and Cohen's kappa, adjudicate disagreements and freeze labels with hashes. [Issue #7](https://github.com/yogesh0224/shadowleak/issues/7).
- [ ] Keep annotation crosswalk, raw ZIPs, detector predictions and model-condition labels inaccessible to annotators until final labels are frozen.

**Exit gate:** Two independently completed label sets, recorded agreement, adjudication trail, immutable gold labels and an auditable unblinding point. No detector-generated substitute for human gold labels.

## Stage 4 — Verify statistical integrity and run the registered analyses (P1)

- [ ] Using only synthetic fixtures before unblinding, check incomplete-pair exclusion, cluster bootstrap, reproducibility, Holm correction, failure accounting and announced estimand against the frozen protocol. Record any discovered issue, timestamp and deviation class without overwriting the original registered analysis. [Issue #8](https://github.com/yogesh0224/shadowleak/issues/8).
- [ ] After label freeze, join the private case key and run the registered primary analysis for Qwen2.5-1.5B, all prespecified family-level secondary analyses and each replication model. Report effect estimates, uncertainty, paired case counts and all contradictory/null results.
- [ ] Report four-task benign utility, over-refusal and latency without claiming representativeness for authorized real-world workflows.
- [ ] Evaluate detectors against human labels using valid record/prompt holdouts; compare detector-based and human-based defense-effect estimates on identical complete pairs as an **additional, transparently labeled** analysis. [Issue #9](https://github.com/yogesh0224/shadowleak/issues/9).

**Exit gate:** Reproducible tables and figures from frozen labels and versioned analysis code; all primary/secondary/replication/exploratory labels and limitations stated.

## Stage 5 — Complete the manuscript and reproducibility evidence (P1)

- [ ] Revise the manuscript from verified evidence, preserving the preregistered shell's evidence hierarchy and keeping the single-turn contextual-disclosure threat model explicit.
- [ ] Complete literature review and discussion without unsupported first-in-field, real-person reidentification, training-data memorization, or unauthorized-exfiltration claims.
- [ ] Obtain a critical external methodological read; address issues openly without selectively omitting findings.
- [ ] Release tagged code, exact reproducibility instructions, safe synthetic benchmark documentation, hashed artifacts and appropriately access-controlled original model outputs/keys.
- [ ] Finalize the evaluation card using validated results only. [Issue #10](https://github.com/yogesh0224/shadowleak/issues/10).

**Exit gate:** A full, evidence-supported paper and a release another authorized researcher can audit; no claim that a hash proves scientific correctness.

## Stage 6 — Submission

- [ ] Select the venue once the actual scientific contribution is clear; verify current scope, dates, anonymity, ethics, preprint, data-availability and concurrent-submission rules.
- [ ] Prepare venue-specific paper and supplementary files; document public-repository identity and any anonymity implications.
- [ ] Submit, then update [publication status](PUBLICATION_STATUS.md) with a dated submission identifier only after submission is confirmed.

**Exit gate:** Submission confirmed with a verifiable record. Acceptance and publication are separate future milestones.

## Deferred or optional follow-up research

A stronger authorization boundary, genuine multi-turn attack interactions, more diverse benign workflows, larger model coverage and institution-specific governance/economic thresholds would require **new, separately versioned protocols**. Do not insert these into the original frozen confirmatory study or present exploratory governance profiles as deployment certification.

## Maintenance rule

Track work via issues [#5](https://github.com/yogesh0224/shadowleak/issues/5)–[#10](https://github.com/yogesh0224/shadowleak/issues/10). On every verified milestone, update [PUBLICATION_STATUS.md](PUBLICATION_STATUS.md) with the date, evidence link, owner or custodian as appropriate, and any deviation. This roadmap is planning documentation, **not** the frozen scientific protocol.
