# ShadowLeak Confirmatory Execution Record

Study: `shadowleak-confirmatory-v1`

## Frozen execution code

All confirmatory model executions should use repository commit:

`c136f4315ca5c224cc1d4f802750a3baec089a6f`

This is the commit that triggered the primary Qwen2.5-1.5B execution.

The following execution-critical files were checked against the current research
branch and have identical Git blob SHAs:

| File | Git blob SHA |
|---|---|
| `studies/confirmatory_v1.json` | `3644de427cf1025f2ad830e118dcf50357f37465` |
| `research/study_plan.py` | `9f37da0ed8cf49f770629bbd3bae247521d6d352` |
| `research/run_benchmark.py` | `fca186fddf9e4cb556adf24482c05211ff7bcf86` |
| `research/benchmark_manifest.py` | `7e783f4924e963a0cfa3b87ec7ffd6e845cb9654` |
| `research/data/attack_templates_v2.json` | `5c649c73062e38e83752e6b91f72e3cedb553f6e` |
| `requirements-pilot.txt` | `3e1a1a9c6acfd6e047c38eccea31c3fa0199c577` |

Later commits add annotation, reporting, literature, and evidence-packaging
infrastructure but do not alter these frozen execution inputs.

## Primary execution

- Workflow: `.github/workflows/confirmatory-v1-primary.yml`
- Model key: `qwen2_5_1_5b_instruct`
- Frozen plan: `studies/confirmatory_v1.json`
- Planned cases: 1,860
- Execution commit: `c136f4315ca5c224cc1d4f802750a3baec089a6f`
- Evidence role: primary confirmatory
- Outcome inspection before annotation: prohibited

## Replication execution

Workflow: `.github/workflows/confirmatory-v1-replications.yml`

The workflow explicitly checks out the same frozen execution commit before
installing dependencies or running any model.

Replication order is serialized with `max-parallel: 1`:

1. `qwen2_5_0_5b_instruct`
2. `smollm2_360m_instruct`
3. `tinyllama_1_1b_chat_v1`

Each run uses:

- the same frozen study-plan file;
- Benchmark v2 and seed 42;
- deterministic greedy generation;
- maximum 64 new tokens;
- no retries;
- 1,860 planned cases;
- the model revision registered in the frozen plan;
- the same artifact names produced by `research.study_plan`.

Each artifact bundle additionally contains `execution_commit.txt` so the
execution code can be verified independently of the workflow metadata.

## Artifact bundle contract

Each successful model bundle should contain:

- `manifest.jsonl`
- `responses.jsonl`
- `annotation_queue.csv`
- `annotation_key.jsonl`
- `run_summary.json`
- `execution_commit.txt` for replication jobs

Before substantive outcome analysis, verify:

1. study ID is `shadowleak-confirmatory-v1`;
2. study-plan SHA-256 matches the frozen plan;
3. model ID and immutable revision match the plan;
4. planned cases equal 1,860;
5. completed + failed cases equals 1,860;
6. failure rate is at most 5% or the run is explicitly marked protocol-failing;
7. artifact hashes are present;
8. the execution commit is the frozen commit above;
9. no response-level substantive leakage results have been inspected before
   blinded annotation.

## Evidence interpretation

The primary model remains the only primary confirmatory model. Replication jobs
must not be promoted to separate primary discoveries. Their effect estimates,
clustered intervals, failure rates, and contradictory/null findings remain
reportable as replication evidence.

## Post-execution verification (administrative update: 2026-09-19)

The primary workflow [run 34701116937](https://github.com/yogesh0224/shadowleak/actions/runs/34701116937) and replication workflow [run 34703895719](https://github.com/yogesh0224/shadowleak/actions/runs/34703895719) are recorded by GitHub as completed successfully. A metadata-only audit retrieved all four ZIP archives, checked GitHub archive SHA-256 values and internal file hashes, verified the registered model/plan identities, and confirmed 1,860/1,860 generated responses and zero recorded generation failures **per model**. The replication workflow head differs from the frozen execution SHA, but the workflow checks out the frozen execution SHA and each replication archive records it in `execution_commit.txt`.

This finding verifies execution and metadata integrity **only**; it does not establish human gold labels or leakage findings. The original archives still need durable private storage before GitHub's reported **2026-10-12** expiry. The four model-specific blinded queues reuse annotation IDs and must not be concatenated without a new unique pooled-ID namespace and a protected private key.

See the [dated audit, artifact IDs and hashes](CONFIRMATORY_ARTIFACT_AUDIT_2026-09-19.md), [live publication status](PUBLICATION_STATUS.md) and [publication roadmap](RESEARCH_ROADMAP.md). This note does not amend the frozen model execution, protocol, or reporting plan.
