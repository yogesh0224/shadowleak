# From Red-Team Finding to Accountable Evidence: Measuring Privacy Leakage in Language-Model Systems

Status: **pre-results manuscript shell**  
Study: `shadowleak-confirmatory-v1`  
Reporting plan: `studies/reporting_plan_v1.json`

> This document is intentionally frozen before confirmatory outcome inspection.
> Bracketed placeholders must be filled from validated study artifacts only.
> Results that are null, imprecise, adverse, or protocol-failing remain reportable.

## Abstract

Language-model privacy evaluations often begin with red-team examples but stop
short of producing evidence that can support reproducible technical or
institutional decisions. ShadowLeak evaluates protected-attribute disclosure
using synthetic canary records, matched defended and undefended model
conditions, blinded human annotation, record-cluster-aware inference, and
explicit privacy-utility and governance sensitivity analyses.

We preregistered a confirmatory evaluation on
`Qwen/Qwen2.5-1.5B-Instruct`, with three additional open models treated as
replication evidence. The primary estimand is the absolute reduction in
adjudicated leakage under `guardshield-v1` relative to no defense, with
uncertainty obtained by resampling complete synthetic-record clusters.

**Results:** [FILL ONLY AFTER FINAL ADJUDICATION AND PROTOCOL VALIDATION.]

**Conclusion:** [STATE ONLY WHAT THE PRIMARY AND REPLICATION EVIDENCE SUPPORTS.
DO NOT GENERALIZE TO REAL TRAINING-DATA MEMORIZATION, LEGAL COMPLIANCE, OR
PRODUCTION-SYSTEM SAFETY.]

## 1. Introduction

Privacy leakage in language-model systems is frequently demonstrated through
individual prompts or detector outputs. Such demonstrations can identify
failure modes, but they do not by themselves establish how often leakage
occurs, how much a defense reduces it, whether apparent gains preserve benign
utility, or whether the evidence is reproducible enough for institutional
review.

ShadowLeak is designed around a narrower question: how can a technical
red-team finding be converted into an auditable empirical claim? The study
therefore emphasizes paired experimental design, independent human labels,
record-level dependence, immutable model provenance, explicit failure
accounting, and separation of confirmatory, replication, and exploratory
evidence.

The contribution is an evaluation protocol and evidence package rather than a
claim that one detector or defense universally solves language-model privacy.

### 1.1 Research questions

1. Does `guardshield-v1` reduce adjudicated protected-attribute leakage on the
   preregistered primary model?
2. Which pre-specified attack families show larger or smaller paired defense
   effects after multiplicity correction?
3. Does the primary effect replicate across independently maintained open model
   families and scales?
4. What benign-utility and latency costs accompany the measured privacy effect?
5. How sensitive are institutional decisions to explicit economic weights and
   illustrative governance thresholds?

### 1.2 Evidence hierarchy

The paper must preserve the following hierarchy:

- **Primary confirmatory:** overall paired defense effect on
  `Qwen/Qwen2.5-1.5B-Instruct`.
- **Secondary confirmatory:** attack-family-specific effects on the primary
  model, interpreted with Holm-Bonferroni correction.
- **Replication:** the three additional preregistered model runs.
- **Secondary external validity:** held-out prompt variants on disjoint records.
- **Exploratory / sensitivity:** whole-family detector holdout, protected-field
  contrasts, model-by-family interactions, economic-weight scenarios, and
  illustrative governance profiles.

## 2. Related work

### 2.1 Privacy leakage and memorization

Prior work shows that language models can expose memorized training examples
under adversarial querying, including personally identifying strings
[@carlini2021extracting]. Memorization also varies with factors such as model
capacity, duplication, and prompting context [@carlini2023memorization], while
later work demonstrates scalable extractable memorization across open,
semi-open, and closed language models [@nasr2023scalable].

ShadowLeak studies a different privacy threat model. It does not attempt to
recover private training examples. Instead, it places visibly synthetic
protected attributes in model context and measures whether adversarial prompts
cause those attributes to be disclosed. Training-data extraction therefore
motivates the privacy problem but is not evidence that ShadowLeak measures
memorization.

### 2.2 Adversarial prompting and benchmark validity

Research on prompt injection and jailbreaking increasingly emphasizes
systematic attack definitions, common evaluation frameworks, and reproducible
artifacts rather than isolated successful prompts [@liu2023promptinjection;
@schulhoff2023hackaprompt; @chao2024jailbreakbench]. Benchmark research also
shows that common automated success measures can materially overstate jailbreak
effectiveness relative to human judgment [@souly2024strongreject].

These findings motivate ShadowLeak's fixed attack families, versioned prompt
variants, exact model provenance, matched defended and undefended cases, and
separation of automated detector outputs from human gold labels. Broader
trustworthiness benchmarks additionally motivate measuring over-refusal and
benign utility rather than treating more blocking as automatically better
[@wang2024donotanswer; @huang2024trustllm].

### 2.3 Human annotation and disagreement

Human evaluation introduces measurement uncertainty of its own. Agreement
coefficients such as Cohen's kappa depend on assumptions about annotators and
label structure [@artstein2008agreement]. Work on subjective NLP annotation
further shows that disagreement can carry meaningful information and that
filtering to high-agreement cases can change downstream evaluation
[@leonardelli2021disagreement]. Broader NLG meta-evaluation has also identified
substantial inconsistency in human-evaluation definitions and reporting
[@howcroft2020evaluation].

ShadowLeak therefore uses a written rubric, two independent annotation passes,
pre-adjudication raw agreement and Cohen's kappa, disagreement-only
adjudication, and a separate case key withheld until final labels are frozen.

### 2.4 Documentation, auditing, and governance

Model Cards and Datasheets for Datasets established widely used patterns for
documenting intended use, evaluation conditions, dataset composition, and
limitations [@mitchell2019modelcards; @gebru2021datasheets]. Raji et al. extend
this documentation logic into an end-to-end organizational auditing framework
[@raji2020auditing].

The NIST AI Risk Management Framework similarly emphasizes governance,
mapping, measurement, and management of AI risk, including documented
evaluation procedures, uncertainty, privacy-risk measurement, and trade-offs
among trustworthiness characteristics [@nist2023airmf]. The Generative AI
Profile extends that framing to generative systems [@nist2024genai], while
recent audit-card work argues that evaluation results require contextual
information about scope, process integrity, access, and review
[@staufer2025auditcards].

ShadowLeak adopts this evidence-oriented framing while retaining a narrower
claim. Its governance profiles are illustrative sensitivity scenarios rather
than compliance tests.

### 2.5 Privacy-utility and decision trade-offs

Safety and privacy interventions may produce costs as well as benefits.
Trustworthiness evaluations document exaggerated safety behavior and
over-refusal [@huang2024trustllm], while more general privacy research treats
privacy and utility as competing objectives rather than assuming one
configuration dominates every decision context [@ficiu2023tradeoff].

ShadowLeak therefore reports leakage, task completion, correctness, relevance,
over-refusal, and latency separately before applying any decision weights.
Its economic layer is a sensitivity analysis over explicit preference
parameters, not an estimate of welfare or market prices.

### 2.6 Research gap

Existing work supplies strong components of the problem: privacy extraction,
adversarial prompt benchmarks, human-evaluation methodology, documentation
frameworks, and multidimensional trustworthiness assessment. ShadowLeak tests a
combined workflow in which defended and undefended responses are paired within
synthetic records, repeated prompts are handled at the record-cluster level,
detector predictions are separated from blinded human gold labels, and
governance/economic interpretation remains explicitly downstream of the
technical evidence.

The intended contribution is therefore a reproducible method for converting a
red-team privacy finding into bounded, auditable evidence rather than a
universal privacy defense or a new legal standard.

The source-by-source claim boundaries are documented in
`docs/LITERATURE_MATRIX.md`, with working BibTeX entries in
`docs/references.bib`.

## 3. Methods

### 3.1 Threat model

The evaluated model receives a context containing visibly synthetic canary
records. Attack prompts attempt to elicit protected attributes through direct
extraction, claimed authority, role-play, instruction override, obfuscation,
reconstruction, indirect inference, social engineering, or conversational
scaffolding.

This setup evaluates disclosure from provided context. It does not test
memorization of real training data, membership inference, production access
control, or compromise of external systems.

### 3.2 Benchmark and pairing

Confirmatory evaluation uses Benchmark v2 with 30 independent synthetic records.
Each record is paired across `none` and `guardshield-v1` conditions for 27
attack prompt variants and four benign controls, yielding 62 planned cases per
record and 1,860 planned cases per model.

The 27 attack prompts contain three pre-designated variants in each of nine
attack families: two development variants and one held-out variant.

### 3.3 Models

The preregistered primary model is:

- `Qwen/Qwen2.5-1.5B-Instruct` at immutable revision
  `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.

Replication models are:

- `Qwen/Qwen2.5-0.5B-Instruct` at
  `7ae557604adf67be50417f59c2c2f167def9a775`;
- `HuggingFaceTB/SmolLM2-360M-Instruct` at
  `a10cc1512eabd3dde888204e902eca88bddb4951`;
- `TinyLlama/TinyLlama-1.1B-Chat-v1.0` at
  `fe8a4ea1ffedaf415f4da2f062534de366a451e6`.

Generation uses each model's native chat template, greedy decoding, a maximum
of 64 new tokens, and no generation retries.

### 3.4 Sample-size planning

The minimum effect of interest is a five-percentage-point absolute leakage
reduction, represented for planning as 15% without defense versus 10% with
defense.

A latent-Gaussian planning simulation models dependence within synthetic
records and within defended/undefended prompt pairs. The frozen planning
assumptions use record latent share 0.40, pair latent share 0.20, alpha 0.05,
2,000 iterations, seed 42, and 27 attack pairs per record. Although a smaller
candidate count reaches the target under those assumptions, 30 independent
records are used as a conservative design margin.

These correlation parameters are planning assumptions, not empirical estimates
of the true intraclass correlation.

### 3.5 Blinded annotation

Successful responses are randomized into a blinded queue that omits case IDs,
model identity, defense condition, filter actions, and detector scores. Two
annotators label each response independently. Agreement is reported before
adjudication using raw agreement and Cohen's kappa. Disagreements are resolved
through a blinded adjudication sheet before the annotation key is rejoined.

The attack outcome is binary adjudicated protected-attribute leakage, with leak
type recorded as exact, partial, semantic, inferred, or none.

Benign responses are labeled for utility preservation, task completion,
correctness, relevance, and over-refusal.

### 3.6 Primary estimand and uncertainty

The primary estimand is:

`leakage(no defense) - leakage(guardshield-v1)`

Positive values indicate lower leakage under GuardShield.

Because each synthetic record contributes repeated prompts, the primary
uncertainty interval is obtained by a percentile bootstrap that resamples
complete `record_id` clusters. Prompt-level exact McNemar output is retained
as a paired diagnostic rather than treated as the sole inferential basis.

### 3.7 Multiplicity

Attack-family-specific McNemar diagnostics form one pre-specified secondary
hypothesis family and are adjusted with Holm-Bonferroni correction.

Protected-field, model-by-family, and other unregistered subgroup contrasts are
exploratory.

### 3.8 Utility, economics, and governance

Benign utility is reported both dimension-by-dimension and as an equal-weight
descriptive composite. Latency is reported separately.

Economic analysis evaluates the full preregistered grid of leakage,
utility-loss, and latency weights. These weights are sensitivity parameters,
not market prices or welfare estimates.

Governance profiles are illustrative decision scenarios only. Passing an
illustrative threshold is not evidence of legal compliance, certification, or
sector-wide acceptability.

### 3.9 Failure accounting

Failed generations are never relabeled as non-leaks and are not silently
replaced. Matched pairs with one missing member are excluded from paired
inference and counted as incomplete. A model run with failure rate greater than
5% is classified as protocol-failing.

## 4. Results

### 4.1 Execution and protocol compliance

**Table 1. Study execution and sample accounting**

| Model | Role | Planned | Completed | Failed | Failure rate | Annotated |
|---|---|---:|---:|---:|---:|---:|
| Qwen2.5-1.5B-Instruct | Primary | 1,860 | [ ] | [ ] | [ ] | [ ] |
| Qwen2.5-0.5B-Instruct | Replication | 1,860 | [ ] | [ ] | [ ] | [ ] |
| SmolLM2-360M-Instruct | Replication | 1,860 | [ ] | [ ] | [ ] | [ ] |
| TinyLlama-1.1B-Chat-v1.0 | Replication | 1,860 | [ ] | [ ] | [ ] | [ ] |

Report all protocol deviations here before substantive results.

### 4.2 Primary confirmatory result

**Table 2. Primary defense effect**

| No-defense leakage | GuardShield leakage | Absolute risk reduction | Cluster-bootstrap 95% CI | Complete pairs | Incomplete pairs | Exact McNemar p |
|---:|---:|---:|---:|---:|---:|---:|
| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

Required interpretation:

- report the estimate and interval before the p-value;
- state whether the interval is compatible with the preregistered
  five-percentage-point minimum effect;
- do not describe statistical non-significance as proof of no effect;
- do not describe a statistically detectable but trivial effect as
  substantively large without reference to the minimum effect.

### 4.3 Attack-family secondary results

**Table 3. Attack-family-specific paired effects**

| Attack family | No defense | GuardShield | Absolute reduction | Exact p | Holm-adjusted p |
|---|---:|---:|---:|---:|---:|
| direct_extraction | [ ] | [ ] | [ ] | [ ] | [ ] |
| claimed_authority | [ ] | [ ] | [ ] | [ ] | [ ] |
| roleplay | [ ] | [ ] | [ ] | [ ] | [ ] |
| instruction_override | [ ] | [ ] | [ ] | [ ] | [ ] |
| obfuscation | [ ] | [ ] | [ ] | [ ] | [ ] |
| reconstruction | [ ] | [ ] | [ ] | [ ] | [ ] |
| indirect_inference | [ ] | [ ] | [ ] | [ ] | [ ] |
| social_engineering | [ ] | [ ] | [ ] | [ ] | [ ] |
| multi_turn_setup | [ ] | [ ] | [ ] | [ ] | [ ] |

No family may be omitted because its result is inconvenient.

### 4.4 Benign utility and latency

**Table 4. Primary-model benign utility**

| Condition | Utility preserved | Task completion | Correctness | Relevance | Over-refusal | Composite | Mean latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| none | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| guardshield-v1 | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

Interpret privacy gain alongside utility and latency rather than treating lower
leakage as automatically preferable.

### 4.5 Replication models

**Table 5. Replication-model defense effects**

| Model | No defense | GuardShield | Absolute reduction | Cluster-bootstrap 95% CI | Failure rate |
|---|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B-Instruct | [ ] | [ ] | [ ] | [ ] | [ ] |
| SmolLM2-360M-Instruct | [ ] | [ ] | [ ] | [ ] | [ ] |
| TinyLlama-1.1B-Chat-v1.0 | [ ] | [ ] | [ ] | [ ] | [ ] |

Replication results must be presented whether they agree or disagree with the
primary model.

### 4.6 External validity

Report pre-designated held-out prompt variants separately from development
variants. Whole-attack-family detector holdout must remain explicitly
exploratory.

**Table 6. External-validity analyses**

| Analysis | Model | Split / holdout | Metric | Estimate | Uncertainty | Evidence label |
|---|---|---|---|---:|---|---|
| Held-out prompt variants | [ ] | [ ] | [ ] | [ ] | [ ] | Secondary |
| Whole-family detector holdout | [ ] | [ ] | [ ] | [ ] | [ ] | Exploratory |

### 4.7 Inter-annotator agreement

Report:

- total independently labeled rows: [ ];
- raw agreement: [ ];
- Cohen's kappa: [ ];
- disagreement count: [ ];
- disagreement rate: [ ];
- adjudicated rows: [ ].

Agreement statistics are descriptive quality indicators and do not substitute
for substantive validity of the annotation rubric.

### 4.8 Privacy-utility trade-off

**Figure 3** plots leakage against benign utility by model and defense condition.
Do not collapse the trade-off into a single preferred point unless an external
decision rule was fixed before outcome inspection.

### 4.9 Economic sensitivity

**Figure 4** reports the complete preregistered weight grid and the regions in
which each defense condition is preferred. Report ties and preference changes.
Do not select a single favorable weight vector as the main result.

### 4.10 Governance sensitivity

Report the illustrative governance profiles as scenario analysis. Use
`pass`, `fail`, or `insufficient_evidence` exactly as generated by the
governance evaluator.

Do not use this section to claim legal compliance.

## 5. Discussion

### 5.1 Primary finding

[FILL FROM TABLE 2. BEGIN WITH ESTIMATE + INTERVAL, THEN INTERPRET AGAINST THE
MINIMUM EFFECT OF INTEREST.]

### 5.2 Replication and heterogeneity

[STATE WHETHER THE DIRECTION AND MAGNITUDE REPLICATE. INCLUDE CONTRADICTORY OR
IMPRECISE MODEL RESULTS.]

### 5.3 Privacy versus utility

[DISCUSS WHETHER MEASURED PRIVACY GAINS COINCIDE WITH UTILITY LOSS,
OVER-REFUSAL, OR LATENCY COST.]

### 5.4 Institutional interpretation

[DISCUSS WHICH DECISIONS ARE ROBUST ACROSS ECONOMIC WEIGHTS AND WHICH DEPEND
STRONGLY ON ASSUMPTIONS. KEEP ILLUSTRATIVE GOVERNANCE PROFILES DISTINCT FROM
LEGAL OR ORGANIZATIONAL REQUIREMENTS.]

### 5.5 What the study does not establish

The study does not establish:

- memorization of real training data;
- privacy of a production deployment;
- absence of leakage under untested attack families;
- legal compliance;
- universal effectiveness of GuardShield;
- welfare-optimal privacy policy;
- causal mechanisms inside the evaluated language models.

## 6. Limitations

The final paper must address at least:

1. synthetic records rather than real institutional data;
2. four relatively small open instruction models;
3. deterministic single-turn generation;
4. `multi_turn_setup` as conversational scaffolding rather than a genuine
   stateful multi-turn interaction;
5. only two defense states, limiting the privacy-utility frontier;
6. potential target-field / attack-family imbalance;
7. human judgment in semantic and inferred leakage labels;
8. planning correlation assumptions not estimated from confirmatory outcomes;
9. limited external validity beyond the pre-specified prompt and model set;
10. illustrative rather than stakeholder-derived governance thresholds.

## 7. Ethics and dual use

All identities are synthetic and use reserved domains. The benchmark is meant
to improve evaluation and accountability, not to facilitate extraction of real
personal data.

Generated prompts, responses, and annotations should be treated as potentially
sensitive research artifacts. Public releases should contain only the minimum
material needed for reproducibility and should not introduce real personal
information.

## 8. Reproducibility and evidence package

The final release should retain:

- frozen confirmatory protocol and SHA-256;
- frozen reporting plan;
- benchmark manifest and hash;
- exact model IDs and immutable revisions;
- software/runtime provenance;
- response artifacts and failure ledger;
- blinded annotation queues;
- independent annotator files;
- pre-adjudication agreement report;
- adjudication decisions;
- final adjudicated labels;
- benchmark reports;
- governance and economic sensitivity reports;
- table/figure source data;
- hashes for all released evidence artifacts.

## 9. Conclusion

[FILL ONLY AFTER PRIMARY, REPLICATION, UTILITY, AND LIMITATION SECTIONS ARE
COMPLETE. THE CONCLUSION MUST NOT EXCEED THE STRONGEST SUPPORTED EVIDENCE
CLASS.]

## Appendix A. Claim register

| Claim | Evidence class | Required evidence | Status |
|---|---|---|---|
| GuardShield changes overall leakage on primary model | Primary confirmatory | clustered paired effect + adjudicated labels | pending |
| Specific attack families differ in defense effect | Secondary confirmatory | all nine family effects + Holm correction | pending |
| Effect generalizes to other models | Replication | all three replication models | pending |
| Detector generalizes to held-out prompt variants | Secondary external validity | held-out prompts + disjoint records | pending |
| Detector generalizes to unseen attack families | Exploratory | whole-family holdout | pending |
| Defense is preferable under explicit costs | Exploratory sensitivity | full cost-weight grid | pending |
| Deployment context passes illustrative threshold | Governance sensitivity | complete profile evaluation | pending |
| System is legally compliant | Unsupported | not tested | prohibited |

## Appendix B. Planned figures

1. **Study flow:** planned cases, completed cases, failures, annotations,
   disagreements, adjudications.
2. **Defense-effect forest plot:** primary model visually distinguished from
   replication models without hiding any model.
3. **Privacy-utility plane:** leakage versus multidimensional benign utility.
4. **Economic sensitivity map:** preferred condition across the full registered
   cost-weight grid.

## Appendix C. Reporting rules

- Never replace a preregistered primary result with a more favorable subgroup.
- Never describe detector predictions as gold labels.
- Never omit failed model calls from sample accounting.
- Never choose economic weights after seeing which values favor the defense.
- Never promote replication or exploratory findings to primary confirmatory
  evidence.
- Always report contradictory model results and null effects.
- Report effect sizes and uncertainty before significance language.
