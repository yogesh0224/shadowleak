# ShadowLeak publication positioning — working research note

Status: **pre-results positioning draft** (2026-09-19). This note supplements, and does not amend, the frozen confirmatory protocol, study plan, reporting plan, or pre-results manuscript shell.

## Publication question

**How sensitive are conclusions about a fixed contextual-disclosure defense to the method used to label model outputs, and what benign-task costs accompany the measured disclosure effect?**

The existing primary confirmatory question remains unchanged: on the registered Qwen2.5-1.5B-Instruct revision, does guardshield-v1 reduce independently adjudicated benchmark-defined protected-attribute disclosure relative to no defense? Detector-versus-human comparisons proposed here are additional analyses and must retain the confirmatory/exploratory status assigned by the original reporting plan. They are **not** newly preregistered primary hypotheses.

## Operational threat model

- **Setting:** a single-turn chat model receives a synthetic record and request in one user message. This is controlled *context disclosure*, not verified exfiltration across a separate authorization or trust boundary.
- **Data:** benchmark-designated synthetic protected attributes, not real personal data or training-set secrets.
- **Requester:** benchmark prompts solicit attributes from the supplied record; the frozen protocol does not establish a distinct high-priority confidentiality policy or separate attacker-controlled tool surface.
- **Intervention:** fixed, versioned guardshield-v1 prompt filtering and output sanitization compared with no defense on matched record/prompt pairs.
- **Outcome:** adjudicated response disclosure under the frozen annotation rubric. The word “leakage” in the manuscript is shorthand for this **benchmark-defined** outcome, not proof of a production privacy breach.
- **Limits:** no claims about training-data memorization, actual unauthorized access, realistic multi-turn attacks, enterprise deployment, or legal compliance. The `multi_turn_setup` family is currently a single-turn prompt formulation, not an interactive multi-turn experiment.

## Closest related work and boundaries

| Source | Studied object | Implication for ShadowLeak |
|---|---|---|
| [PrivacyLens (Shao et al., NeurIPS 2024)](https://papers.nips.cc/paper_files/paper/2024/hash/a2a7e58309d5190082390ff10ff3b2b8-Abstract-Datasets_and_Benchmarks_Track.html) | Contextual privacy norms and leakage/helpfulness in model-agent actions | Privacy-sensitive inference-time evaluation and the privacy/helpfulness connection are not novel by themselves. ShadowLeak does not claim comparable contextual-integrity judgments or agent trajectories. |
| [AgentDojo (Debenedetti et al., NeurIPS 2024)](https://arxiv.org/abs/2406.13352) | Tool-using agent tasks, indirect prompt injection, attacks/defenses and task utility | Standardized defense/attack testing and utility measurement predate ShadowLeak; its single-turn user-message setup is not an indirect tool-output injection benchmark. |
| [Alizadeh et al. (2025), personal-data exfiltration from LLM agents](https://arxiv.org/abs/2506.01055) | Synthetic banking/agent tasks and personal-data leakage under prompt injection | Synthetic data, exfiltration, defense and utility have been studied together; ShadowLeak instead evaluates narrow protected-attribute disclosure with a fixed direct-request format. |
| [StrongREJECT (Souly et al., NeurIPS 2024)](https://papers.nips.cc/paper_files/paper/2024/hash/e2e06adf560b0706d3b1ddfca9f29756-Abstract-Datasets_and_Benchmarks_Track.html) | Agreement of jailbreak-success evaluators with human judgment | Automated outcome metrics can misrepresent attack success in another domain; this motivates—but does not establish—a disclosure-specific measurement question here. |
| [CASE-Bench (Sun et al., ICML 2025)](https://proceedings.mlr.press/v267/sun25ab.html) | Context-dependent safety judgments and inappropriate refusal | More blocking is not inherently better in legitimate contexts; ShadowLeak's four existing benign tasks are limited and do not establish authorization-sensitive utility. |

**Positioning hypothesis, not an established literature gap:** A paired, record-cluster-aware analysis of *human-labeled versus detector-labeled* disclosure effects in this narrow synthetic benchmark may add a useful disclosure-specific measurement study. Before claiming novelty, check additional recent disclosure-specific evaluator papers and compare methods and findings rather than asserting this is the first combination of these components.

## Research questions and evidence status

| ID | Question | Evidence class / required work |
|---|---|---|
| RQ1 | What is the guardshield-v1 effect on adjudicated disclosure in the registered primary model? | **Existing confirmatory primary:** frozen paired outcome and record-clustered interval, with failure accounting. |
| RQ2 | Do automatic and adjudicated labels yield different disclosure rates and defense-effect estimates? | **Additional measurement-sensitivity analysis:** run prespecified existing detectors on the same responses, evaluate against human gold labels and compare paired effect estimates. Do not market as a newly registered primary test. |
| RQ3 | Which kinds of disclosures account for detector errors? | **Descriptive/exploratory:** exact, partial, semantic, inferred; annotate and report counts, uncertainty and representative synthetic examples, subject to adequate subgroup sizes. |
| RQ4 | What benign utility and latency outcomes accompany the measured effect? | **Registered secondary/descriptive:** preserve the four-task benchmark's limited scope and show over-refusal separately. |
| RQ5 | Are the primary-model findings directionally consistent across registered replication models? | **Replication:** report each effect and interval, including null, contrary, failed and incomplete results. |

## Analysis integrity guardrails

1. Preserve the original frozen plan, prompt set, reporting plan, model revisions and hypothesis. Do not inspect outcomes and then rewrite the primary question.
2. Label every result as confirmatory, secondary, replication or exploratory before interpreting it.
3. Keep annotators blind to condition/model/detector outputs until gold labels are frozen. Detector outputs must not define gold labels.
4. Ensure any ML detector is evaluated on disjoint records and appropriately held-out prompts; never train on the responses used for its reported independent test metrics.
5. Compare gold-label and detector-label effects **on identical complete matched pairs**, reporting sample counts and how failed responses were handled. Preserve record clustering for uncertainty and distinguish descriptive comparisons from significance tests.
6. Report the four benign prompts as limited smoke tests of utility, not a comprehensive authorized-workflow evaluation.
7. If an inferential code error is identified, document the discovery time, exact fix and whether results were inspected. Preserve the original analysis and mark any revised analysis according to the registered deviation policy.
8. Preserve all findings, including negative, null, ambiguous, and adverse defense effects.

## Evidence gates before submission

- [ ] Confirm nearest related studies, including disclosure-specific evaluation work published through submission date; amend the literature matrix if needed.
- [ ] Verify frozen model-run bundles and provenance; report any missing, failed or out-of-protocol run.
- [ ] Finish independent double annotation, agreement measurement, disagreement adjudication, and label freezing.
- [ ] Execute and validate registered primary/secondary/replication analyses.
- [ ] Perform the properly scoped detector-versus-human measurement comparison and failure-mode analysis.
- [ ] Check that every manuscript contribution is supported by a table, figure, validated artifact, or explicit methodological description.
- [ ] Release reproducibility artifacts and state the scope limitations prominently.

## Provisional title and abstract aim

**Working title:** “ShadowLeak: Measuring the Reliability of Contextual-Disclosure Evaluation in Language Models.”

**Aim, not results:** Evaluate benchmark-defined protected-attribute disclosure on synthetic records, quantify a fixed defense's effect using blinded human labels and matched design, and examine whether automated disclosure metrics produce materially different estimates while accounting for benign task performance and model-to-model variation.

No numerical findings, defense-success statements or novelty claims should be inserted into an abstract before the required evidence exists.
