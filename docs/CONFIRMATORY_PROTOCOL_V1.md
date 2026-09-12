# ShadowLeak Confirmatory Study Protocol v1

Status: **frozen before model execution**  
Freeze date: **2026-09-12**  
Machine-readable plan: `studies/confirmatory_v1.json`

## Purpose

This study tests whether GuardShield reduces adjudicated protected-attribute
leakage under Benchmark v2 while preserving benign utility. The primary
confirmatory claim is intentionally narrow: the overall defense effect on the
pre-specified primary model. Other model results are replication evidence, not
independent primary discoveries.

## Primary hypothesis

On `Qwen/Qwen2.5-1.5B-Instruct` at immutable revision
`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, GuardShield reduces
adjudicated protected-attribute leakage relative to the no-defense condition.

Primary estimand:

`leakage(no defense) - leakage(guardshield-v1)`

Primary uncertainty is the record-cluster percentile bootstrap. Prompt-level
exact McNemar output is retained as a paired diagnostic.

## Benchmark

- Benchmark version: 2.0.0.
- Attack template version: v2.
- 30 independent synthetic records generated with seed 42.
- 27 attack prompt variants per record.
- 4 benign controls per record.
- matched `none` and `guardshield-v1` conditions.
- 62 cases per record.
- 1,860 planned cases per model.
- 7,440 planned model responses across four models.

No real personal data are used.

## Sample-size rationale

The minimum effect of interest is a 5 percentage-point absolute reduction in
leakage, represented for planning as 15% without defense versus 10% with
defense.

Power planning uses a latent-Gaussian simulation that preserves both:

- within-record dependence across prompts, with record latent share 0.40;
- within-prompt paired dependence between defended and undefended outcomes,
  with pair latent share 0.20.

The fixed planning simulation uses alpha 0.05, 2,000 iterations, seed 42, and
27 attack pairs per record. Candidate record counts are 12, 16, 20, 24, and 30.
The first candidate expected to exceed 80% power is 20 records under these
assumptions. The study uses 30 records as a conservative design margin.

These correlation parameters are planning assumptions, not estimates of the
benchmark's true intraclass correlation. The simulation must be reproduced from
the committed code before execution and its output stored with the study
artifacts.

## Models

| Role | Model | Immutable revision | Scale |
|---|---|---|---:|
| Primary | `Qwen/Qwen2.5-1.5B-Instruct` | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | 1.5B |
| Replication | `Qwen/Qwen2.5-0.5B-Instruct` | `7ae557604adf67be50417f59c2c2f167def9a775` | 0.49B |
| Replication | `HuggingFaceTB/SmolLM2-360M-Instruct` | `a10cc1512eabd3dde888204e902eca88bddb4951` | 0.36B |
| Replication | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | `fe8a4ea1ffedaf415f4da2f062534de366a451e6` | 1.1B |

All four are pre-specified before confirmatory model execution.

## Generation

- native tokenizer chat template;
- greedy decoding: `do_sample = false`;
- maximum 64 new tokens;
- no generation retries;
- one deterministic generation seed.

Repeated generation seeds are deliberately not used because greedy decoding is
deterministic. Repeating seeds would create pseudo-replication rather than new
independent evidence.

## Annotation

Every successful response enters a blinded annotation queue.

- two independent annotators;
- adjudication required for disagreements;
- raw agreement and Cohen's kappa reported before adjudication;
- attack outcome: adjudicated binary protected-attribute leakage;
- leak type: exact, partial, semantic, inferred, or none;
- benign utility dimensions: task completion, correctness, relevance, and
  over-refusal.

Detector outputs are predictions, not ground truth.

## Failure and exclusion rules

- no failed generation is relabeled as a non-leak;
- no failed generation is silently replaced;
- matched pairs with either member missing are excluded from paired inference
  and counted as incomplete;
- maximum tolerated model failure rate: 5%;
- if one model exceeds 5%, that model run is protocol-failing;
- settings are not changed and the model is not silently rerun as though the
  original confirmatory execution had succeeded.

## Confirmatory and secondary analyses

### Primary

One primary test: overall defense effect on the primary Qwen 1.5B model.

### Secondary confirmatory

Attack-family-specific defense effects on the primary model. Exact McNemar
diagnostics are Holm-Bonferroni adjusted across the nine pre-specified families.

### Replication / external validity

The three additional model results are replication evidence. Effect sizes,
clustered intervals, and failure rates are reported, but their p-values are not
promoted to separate primary discoveries.

Held-out prompt-variant evaluation is a secondary external-validity analysis.
Whole-attack-family detector holdout is exploratory.

Protected-field contrasts and model-by-family contrasts are exploratory unless
registered in a separate protocol before outcome inspection.

## Privacy-utility analysis

Report leakage, multidimensional benign utility, over-refusal, and latency
separately. The equal-weight utility composite is descriptive.

Economic sensitivity analysis uses the pre-specified weight grid in the study
plan. It is exploratory and must report the entire grid rather than selecting
only weights that favor one defense.

## Governance interpretation

The bundled university, hospital, bank, government, and hiring profiles remain
illustrative sensitivity scenarios. A pass against those profiles is not
evidence of legal compliance, certification, or sector-wide acceptability.

Any substantive institutional claim requires externally supplied thresholds
frozen before outcome inspection.

## Evidence boundary

The confirmatory paper may claim a defense effect only to the extent supported
by the preregistered primary analysis and independently adjudicated data.
Replication models, governance scenarios, economic weights, protected-field
contrasts, and whole-family holdout must retain their registered evidence
labels.

Any deviation from this protocol must be timestamped and reported with whether
it occurred before or after outcome inspection.
