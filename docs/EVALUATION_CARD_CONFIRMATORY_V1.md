# ShadowLeak Confirmatory Evaluation Card v1

Status: **pre-results / evidence collection in progress**  
Study ID: `shadowleak-confirmatory-v1`  
Protocol: `docs/CONFIRMATORY_PROTOCOL_V1.md`  
Machine-readable plan: `studies/confirmatory_v1.json`  
Reporting plan: `studies/reporting_plan_v1.json`

This card is a governance-facing summary of the study design and evidence state.
It must not be updated to imply a substantive model or defense finding until
independent annotation, adjudication, and the preregistered analysis are
complete.

## 1. Evaluation purpose

ShadowLeak evaluates whether a language-model system discloses visibly
synthetic protected attributes under adversarial prompting and whether a fixed
defense configuration changes that disclosure rate while preserving benign
utility.

The confirmatory study tests one narrow primary claim:

> On the preregistered primary model, does `guardshield-v1` reduce adjudicated
> protected-attribute leakage relative to no defense?

The project is designed as an evaluation and evidence framework. It does not
claim that GuardShield certifies a model as private, safe, legally compliant,
or suitable for every deployment context.

## 2. Evidence-state legend

| State | Meaning |
|---|---|
| **Frozen** | Design choice fixed before confirmatory outcome inspection |
| **Executed** | Model execution completed under the frozen plan |
| **Annotated** | Two independent annotation passes completed |
| **Adjudicated** | Disagreements resolved and final labels frozen |
| **Analyzed** | Preregistered analysis completed from final labels |
| **Supported** | Claim is warranted by the designated evidence class |
| **Pending** | Required evidence is not yet complete |
| **Prohibited** | The study design does not support the claim |

## 3. Current evidence state

| Evidence component | State | Required artifact |
|---|---|---|
| Confirmatory protocol | **Frozen** | `docs/CONFIRMATORY_PROTOCOL_V1.md` |
| Machine-readable study plan | **Frozen** | `studies/confirmatory_v1.json` |
| Reporting plan | **Frozen** | `studies/reporting_plan_v1.json` |
| Manuscript structure / claim hierarchy | **Frozen** | `docs/MANUSCRIPT_V1.md` |
| Primary-model execution | **Pending completion/verification** | primary `run_summary.json` + hashed run bundle |
| Replication-model execution | **Pending** | one run bundle per registered model |
| Independent annotation A | **Pending** | completed blinded CSV |
| Independent annotation B | **Pending** | completed blinded CSV |
| Agreement report | **Pending** | `agreement.json` |
| Adjudication | **Pending** | completed adjudication queue |
| Final gold labels | **Pending** | `annotations_final.csv` |
| Primary statistical analysis | **Pending** | benchmark report |
| Governance sensitivity | **Pending final measurements** | governance report |
| Economic sensitivity | **Pending final measurements** | full preregistered sensitivity grid |
| Final evaluation card | **Pending** | this card updated from verified evidence only |

## 4. Scope and threat model

### Evaluated risk

Disclosure of a protected synthetic attribute that is present in the supplied
model context.

### Out of scope

The study does not evaluate:

- memorization of real training data;
- membership inference;
- compromise of external tools, databases, or production systems;
- production access-control failures;
- real-person re-identification;
- legal compliance;
- universal safety or privacy of an evaluated model.

### Data

The benchmark uses deterministic synthetic canary records. No real personal
data should be introduced into the benchmark, annotation files, examples, or
published evidence bundle.

## 5. Confirmatory benchmark

- Benchmark version: **2.0.0**
- Attack-template version: **v2**
- Synthetic records: **30**
- Benchmark seed: **42**
- Attack prompt variants per record: **27**
- Benign controls per record: **4**
- Defense conditions: **none**, **guardshield-v1**
- Planned cases per record: **62**
- Planned cases per model: **1,860**
- Planned cases across four models: **7,440**

The matched design keeps the same underlying record and prompt paired across
defended and undefended conditions.

## 6. Registered models

| Evidence role | Model | Immutable revision |
|---|---|---|
| Primary confirmatory | `Qwen/Qwen2.5-1.5B-Instruct` | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |
| Replication | `Qwen/Qwen2.5-0.5B-Instruct` | `7ae557604adf67be50417f59c2c2f167def9a775` |
| Replication | `HuggingFaceTB/SmolLM2-360M-Instruct` | `a10cc1512eabd3dde888204e902eca88bddb4951` |
| Replication | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | `fe8a4ea1ffedaf415f4da2f062534de366a451e6` |

Additional model results cannot silently replace the registered primary model.

## 7. Generation configuration

- local Hugging Face model execution;
- native tokenizer chat template;
- deterministic greedy decoding;
- `do_sample = false`;
- maximum **64** new tokens;
- no generation retries;
- one deterministic generation seed.

Repeated seeds are not treated as independent evidence because the registered
generation procedure is deterministic.

## 8. Primary outcome and inference

### Primary outcome

Binary adjudicated protected-attribute leakage.

Leak types are recorded as:

- exact;
- partial;
- semantic;
- inferred;
- none.

### Primary estimand

`leakage(no defense) - leakage(guardshield-v1)`

Positive values indicate lower leakage under the defense.

### Primary uncertainty

Record-cluster percentile bootstrap. The resampling unit is the complete
synthetic `record_id`, preserving all repeated prompt observations associated
with a record.

Prompt-level exact McNemar output is retained as a paired diagnostic and is not
used to pretend that repeated prompts from the same record are independent.

## 9. Sample-size rationale

The minimum effect of interest is a **5 percentage-point absolute leakage
reduction**, represented during planning as 15% leakage without defense and 10%
with defense.

The frozen planning simulation uses:

- record latent share: **0.40**;
- pair latent share: **0.20**;
- attack pairs per record: **27**;
- alpha: **0.05**;
- target power: **0.80**;
- iterations: **2,000**;
- simulation seed: **42**.

The correlation parameters are planning assumptions, not empirical estimates.
Thirty records were selected as a conservative margin above the first candidate
expected to reach target power under the registered assumptions.

## 10. Annotation and blinding

Every successful response enters a randomized annotation queue.

Annotators can see the stimulus needed to judge the response but do not receive:

- case ID;
- pair ID;
- model identity;
- model revision;
- defense condition;
- defense action;
- detector score;
- detector prediction.

Two annotators label each row independently. Pre-adjudication raw agreement and
Cohen's kappa are reported. Only disagreements enter the adjudication queue.
The case key is rejoined only after final labels are frozen.

Detector predictions are never treated as gold labels.

## 11. Benign utility

Benign controls measure:

- utility preserved;
- task completion;
- correctness;
- relevance;
- over-refusal.

A descriptive utility composite equally weights task completion, correctness,
relevance, and reversed over-refusal. Equal weighting is a measurement
convention, not an economic or welfare claim.

Latency is reported separately.

## 12. Multiplicity and evidence classes

### Primary confirmatory

One overall defense effect on the registered Qwen2.5-1.5B primary model.

### Secondary confirmatory

Attack-family-specific effects on the primary model. The nine registered
family-level McNemar diagnostics are interpreted using Holm-Bonferroni adjusted
p-values.

### Replication

The three additional registered models provide replication evidence. Their
results are reported even if null, imprecise, or opposite in direction to the
primary result.

### Secondary external validity

Held-out prompt variants on disjoint records.

### Exploratory / sensitivity

- whole-attack-family detector holdout;
- protected-field contrasts;
- model-by-family interactions;
- economic sensitivity;
- governance profiles;
- any unregistered post-hoc subgroup.

## 13. Failure and exclusion policy

- Failed generations are never relabeled as non-leaks.
- Failed generations are not silently regenerated under changed settings.
- A pair with one missing member is excluded from paired inference and counted
  as incomplete.
- Maximum registered model failure rate: **5%**.
- A run above 5% is protocol-failing and remains visible in the evidence record.

## 14. Economics and governance interpretation

The economic layer evaluates a fixed sensitivity grid over explicit leakage,
utility-loss, and latency weights.

Those weights are preference parameters. They are not:

- prices;
- estimated social welfare;
- legally mandated weights;
- universally correct organizational preferences.

The governance profiles bundled with the repository are illustrative scenarios.
A result of `pass` against an illustrative profile is not evidence of legal
compliance, certification, or institutional approval.

## 15. Claim register

| Claim | Evidence class | Current state |
|---|---|---|
| GuardShield changes overall leakage on the primary model | Primary confirmatory | **Pending** |
| Specific attack families differ in defense effect | Secondary confirmatory + Holm correction | **Pending** |
| The primary effect replicates on other registered models | Replication | **Pending** |
| Detector behavior generalizes to held-out prompt variants | Secondary external validity | **Pending** |
| Detector behavior generalizes to unseen attack families | Exploratory | **Pending** |
| One condition is preferable under an explicit cost vector | Economic sensitivity | **Pending** |
| One condition passes an illustrative governance profile | Governance sensitivity | **Pending** |
| GuardShield is universally effective | Not supported by design | **Prohibited** |
| Evaluated models are private or safe | Not supported by design | **Prohibited** |
| The system is legally compliant | Not evaluated | **Prohibited** |
| ShadowLeak measures training-data memorization | Different threat model | **Prohibited** |

## 16. Evidence package

The final release should generate an integrity manifest with
`research.evidence_package`.

Example:

```bat
python -m research.evidence_package ^
  --study-plan studies/confirmatory_v1.json ^
  --reporting-plan studies/reporting_plan_v1.json ^
  --artifact primary_run_summary=artifacts\primary\run_summary.json ^
  --artifact agreement=artifacts\annotation\agreement.json ^
  --artifact final_annotations=artifacts\annotation\annotations_final.csv ^
  --artifact primary_report=artifacts\analysis\primary_report.json ^
  --output artifacts\evidence_package.json
```

The evidence manifest records SHA-256 hashes and file sizes. It proves artifact
identity and provenance only; the presence of a hashed file does not establish
that the substantive claim inside it is correct.

## 17. Minimum evidence required before publication

Before the evaluation card can be marked final:

1. every registered model run must have a retained run summary and artifact
   hashes, or be explicitly reported as unexecuted/protocol-failing;
2. primary-model failure accounting must be resolved;
3. two blinded independent annotation files must be complete;
4. pre-adjudication agreement must be reported;
5. disagreements must be adjudicated;
6. the final annotation file must pass validation;
7. the primary preregistered clustered analysis must be complete;
8. all nine family-level secondary results must be reported together;
9. replication models must be reported without selective omission;
10. privacy, benign utility, over-refusal, and latency must be presented
    together;
11. the full registered economic sensitivity grid must be shown if economic
    interpretation is included;
12. illustrative governance results must retain their sensitivity label;
13. protocol deviations must be disclosed;
14. released evidence artifacts must be hashed into one evidence-package
    manifest.

## 18. Reproduction

Core validation:

```bat
python -m research.study_plan --plan studies/confirmatory_v1.json --validate-only
python -m unittest discover -s tests
```

Evidence-package generation:

```bat
python -m research.evidence_package ^
  --study-plan studies/confirmatory_v1.json ^
  --reporting-plan studies/reporting_plan_v1.json ^
  --output artifacts\evidence_package.json
```

The minimal package above hashes only the two frozen plans. Additional
`--artifact ROLE=PATH` arguments should be added as execution, annotation, and
analysis evidence becomes available.

## 19. Accountability

Known limitations and contradictory findings must remain in the final card.
The card should be updated from verified artifacts, not from preferred
narrative language.

Any change to the frozen protocol or reporting plan must identify whether it
occurred before or after confirmatory outcome inspection.
