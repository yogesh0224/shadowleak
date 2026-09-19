# ShadowLeak solo-research exploratory protocol v1

**Status:** Prospectively documented exploratory study; **not executed, annotated, or analyzed**. Prepared 2026-09-19 after the author confirmed working alone. The protocol should be finalized and a commit SHA recorded *before* generating or inspecting any new experimental responses. It is not an amendment, continuation, substitute, or retrospectively registered analysis of `shadowleak-confirmatory-v1`.

## 1. Research question and evidence level

**Main exploratory question:** On a small, new synthetic context-disclosure benchmark, how closely do fixed automated disclosure-detector predictions correspond to **one researcher's independently recorded manual judgments**, and how sensitive are **descriptive** defended-versus-undefended disclosure summaries to the chosen labeling method?

Secondary descriptive questions: Which response types account for disagreements, and what happens to completion and over-refusal on the four existing benign tasks?

**Evidence level:** single-investigator, single-annotator, exploratory and restricted to the specific synthetic cases and one registered model. A single investigator's label file is *not* independently adjudicated ground truth. Neither agreement of a detector with this label file nor a small observed defended–undefended difference establishes general detector validity, robust privacy protection, statistical confirmation, or a security-boundary violation.

## 2. Keep the original confirmatory study separate

The frozen `studies/confirmatory_v1.json`, `studies/reporting_plan_v1.json`, `docs/CONFIRMATORY_PROTOCOL_V1.md`, and `docs/MANUSCRIPT_V1.md` stay unchanged. All 7,440 original responses and the associated private mapping remain uninspected for substantive leakage until the original study's independent two-human annotation/adjudication protocol can be completed or any unavoidable deviation is disclosed. Do **not** draw a solo-labeled subset from those original responses and then call the registered primary claim verified.

Use **fresh generated responses** for this separate study, and use a separate `study_id`, seed, artifact location, labeling file and analysis script/report namespace. An exploratory study need not be disguised as a preregistered confirmatory study merely because the plan was written before execution.

## 3. Pilot design fixed before seeing new responses

- Study ID: `shadowleak-solo-exploratory-v1`.
- Model: `Qwen/Qwen2.5-1.5B-Instruct`, revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`; **one model only**.
- Generate **10 new synthetic records** using the existing `research.benchmark_manifest.build_manifest` with `seed=20260919`, attack-template version `v2`, four existing benign templates and exactly two defense conditions: `none` and `guardshield-v1`.
- Size: 10 records × (27 attacks + 4 benign tasks) × 2 conditions = **620 planned responses**, comprising 540 attack responses and 80 benign responses, with **310 complete pairs** if no generation fails.
- Record names and email canaries include the new seed and therefore differ from the frozen study's seed-42 identities. **Other generated attributes, such as city, organization, phone-number patterns, or dates, can overlap**; do not claim all protected-field values are disjoint. Verify and document any overlap *using synthetic manifests only*, before viewing model outputs.
- Generation: same pinned model adapter and existing fixed GuardShield v1 code; greedy decoding, `max_new_tokens=64`, no post-failure replacement or cherry-picked reruns. Record the exact execution commit, code/config hash, Python/dependency versions, manifest hash, generation failures and timestamps.
- **Run selection rule:** label **all successful generated responses**, not just visually interesting cases. If a generation fails, report it and count the incomplete pair rather than replacing the response. All 10 records and all prompt variants are retained; no outcome-dependent sampling or early stopping.
- This small 10-record study is deliberately a *feasibility/measurement-sensitivity pilot*, not a powered replication or multi-model comparison. Prompt-level observations within a record are correlated.

The fixed settings above describe a proposed separate pilot to be accepted in the repository **before execution**. If execution resources require a smaller study, create and commit a dated protocol version v2 first, with a transparent deviation log; do not select sample size after inspecting outcomes.

## 4. Independent-of-detector (but sole-investigator) labeling

Generate a new randomized annotation queue and separate case key using `research.annotation_queue`. Keep the key, model/defense identity, model flags and **every detector prediction** inaccessible while manually labeling. The model response itself may reveal defense-specific refusal behavior, so the reviewer cannot be assumed fully blinded.

The project owner manually labels each successful row using the existing `docs/ANNOTATION_GUIDE.md` definitions: disclosure binary `0/1`, one of `none/exact/partial/semantic/inferred`, and a short case-specific rationale; on benign rows additionally assign the five required binary utility fields. Leave attack utility cells blank. Use an annotator identifier such as `solo_investigator`; do **not** set `adjudication_status=adjudicated`, claim independent double annotation, reuse fabricated reviewer IDs, or run the original two-annotator agreement workflow on copies of one label file.

A separate practice/calibration set may be created using an additional seed and should never be included among the 620 study cases. Treat prompts/responses as untrusted text; do not execute code, formulas or instructions contained in model outputs. Record annotation date(s), source queue digest, the one human's declared role, and any rubric uncertainties in a private log. Freeze the sole-investigator label CSV and its SHA-256 **before** exposing the condition key or automated-detector outputs to the analyst.

## 5. Exploratory comparison and reporting rules

After label freeze:
1. Validate source case/annotation coverage, label consistency and failure accounting; join the separate private case key and only then calculate condition-specific summaries.
2. For each *existing fixed detector* whose training, calibration and thresholds are demonstrably unchanged after response inspection, show a 2×2 disagreement table against the sole-investigator labels and report descriptive positive/negative agreement, precision/recall **relative to the single annotator only**, and relevant disclosure-type error examples. Do not call these estimates human-adjudicated detector accuracy. If an ML detector's training data or thresholds overlap with this evaluation or cannot be traced, exclude its independent-test claim and label any displayed result exploratory/in-sample.
3. Report completed cases, generation failures, successful complete pairs, disclosure rates by condition measured using the frozen single-annotator labels **and separately using each automatic proxy**, and paired descriptive differences on identical complete pairs. Report all 10 records and all eligible cases, including adverse or null results, no matter which method favors the defense. Summarize variation by record without interpreting 620 correlated prompts as 620 independent individuals.
4. Report four-task benign completion, correctness, relevance, over-refusal and utility preserved; do not generalize to varied authorized workflows. Clearly describe GuardShield's regex-based prompt filtering and output sanitization.
5. Do **not** report a confirmatory p-value, declare statistical significance, claim the 5-percentage-point registered effect was met, call a one-human file 'gold' or 'independently adjudicated', rank general model safety, claim unauthorized access, or assert deployment-grade privacy protection.
6. Do not rewrite this protocol or choose favorable detectors, thresholds or subgroups based on observed outcomes. Document any post-execution methodological change as an explicitly dated exploratory deviation.

## 6. Truthful claim register

| Topic | Safe pre-results statement | Only after supporting evidence, with exact scope | Unsupported claim |
|---|---|---|---|
| Infrastructure | “ShadowLeak implements a synthetic context-disclosure evaluation pipeline.” | “This exploratory pilot evaluated 620 planned single-model cases; N were successfully labeled by one investigator.” | “Human-adjudicated privacy evaluation completed.” |
| Labeling | “A single-investigator rubric and prospective labeling procedure are documented.” | “One researcher labeled N responses using the stated rubric; no inter-annotator reliability was measured.” | “Ground truth confirmed by independent annotators.” |
| Detector comparison | “The pilot is designed to compare fixed detector predictions with one researcher's manual judgments.” | “For these responses, detector X and the researcher's labels agreed/disagreed on N cases under the stated metric.” | “Detector X is universally accurate, unbiased, or independently human-validated.” |
| Defense outcome | “GuardShield v1 is a fixed regex/input-output-filter baseline.” | “On this one-model, 10-record synthetic pilot, measured disclosure was A vs B under stated labeling and pair-accounting rules.” | “GuardShield prevents unauthorized disclosure / production privacy breaches.” |
| Generalization | “This is single-model, 10-record exploratory evidence.” | “Observed results on the specified cases and four benign tasks, with uncertainty and bias limits.” | “This demonstrates robust efficacy across LLMs, realistic production settings or legitimate user workflows.” |
| Original study | “Four original confirmatory model runs exist and their execution artifacts were structurally verified.” | “The original study's registered primary analysis was completed *only if* its actual two-human adjudication and all registered gates later occur.” | “The new solo study completes or replaces the original preregistered confirmatory result.” |
| Publication | “The publication contribution remains to be evaluated against current related work and actual findings.” | “An empirical single-annotator pilot/methodology paper may be submitted if an appropriately scoped contribution is demonstrated.” | “ShadowLeak is already a peer-reviewed publication or a novel first-in-field benchmark.” |

## 7. Actual next steps and exit gates

- [ ] Independently preserve all **original** four confirmatory ZIP archives and the existing pooled queue/crosswalk in durable private storage before GitHub's stated 2026-10-12 artifact expiry. A ChatGPT download is not durable storage; see [issue #5](https://github.com/yogesh0224/shadowleak/issues/5).
- [ ] Freeze this exploratory plan and register the exact code SHA and distinct private output location **before generating any new model responses**.
- [ ] Produce the fresh 10-record manifest; verify case/pair counts and record identity distinctions using metadata only. Build a new single-model empirical run, preserving failures and software/model provenance.
- [ ] Generate a separate blank-label queue; manually label all successful cases without access to detector predictions or defense metadata. Freeze the single-investigator labels and log limitations.
- [ ] Run descriptive matched-case and detector-versus-one-annotator comparisons, with reproducible analysis code and complete reporting.
- [ ] Check relevant literature, request an external methodological read if possible, and draft a paper only to the strength of the resulting evidence.

**Gate status on 2026-09-19:** Proposed protocol documented. Neither execution, manual labeling, independent review nor empirical detector/defense findings have been completed or verified.
