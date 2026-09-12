# ShadowLeak Open-Model Feasibility Pilot v1

Status: **frozen before model execution**  
Freeze date: **2026-09-12**  
Machine-readable plan: `studies/pilot_v1.json`

## Purpose

This pilot tests whether the benchmark executes reproducibly on two small,
ungated instruction models and produces complete response and annotation
artifacts. It is not powered for model comparison or defense-effect inference.
Pilot outcomes must not be presented as population leakage rates.

## Pre-specified systems

| Model | Immutable revision | Scale | License | Selection reason |
|---|---|---:|---|---|
| `Qwen/Qwen2.5-0.5B-Instruct` | `7ae557604adf67be50417f59c2c2f167def9a775` | 0.49B | Apache-2.0 | Small, instruction-tuned, ungated, independently maintained |
| `HuggingFaceTB/SmolLM2-360M-Instruct` | `a10cc1512eabd3dde888204e902eca88bddb4951` | 0.36B | Apache-2.0 | CPU-oriented compact instruction model from a different developer |

The study intentionally excludes gated models so another researcher can
reproduce the pilot without accepting model-specific access terms.

## Fixed design

- two synthetic canary records generated with seed 42;
- 12 attack templates and four benign controls per record;
- matched `none` and `guardshield-v1` conditions;
- 64 response cases per model, 128 total;
- native tokenizer chat template;
- greedy decoding (`do_sample = false`), maximum 64 new tokens;
- no generation retries;
- maximum tolerated model-failure rate: 0%;
- exact model and software revisions recorded in each response;
- model outputs retained as workflow artifacts, not committed to source control.

## Feasibility outcomes

1. Both pinned model revisions load without gated access.
2. Every planned case produces a response artifact.
3. No input prompt/context prefix is stored as generated model output.
4. Blinded annotation queues and separate case keys are produced.
5. Runtime and artifact hashes are recorded.

No leakage or utility hypothesis will be tested on pilot data. Human labels are
optional for rubric calibration and must be marked pilot-only.

## Decision rule

Proceed to a separately frozen confirmatory protocol only if both models finish
all cases and artifact validation passes. Engineering changes prompted by the
pilot require a new benchmark or prompt-format version. The pilot will remain
disclosed and excluded from confirmatory analysis.

## Ethics and dual use

All identities are visibly synthetic and use the reserved `example.invalid`
domain. Prompts and outputs are still treated as potentially sensitive research
artifacts. Only aggregate findings and the minimum artifacts needed for
reproduction should be published. This protocol does not test real training
data, real individuals, production access controls, or legal compliance.
