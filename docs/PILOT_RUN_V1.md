# ShadowLeak Open-Model Pilot v1 — Execution Record

## Immutable identity

- Source commit: `97daa24d2e5c8cb644d2607ee750bbc458a0f8ed`
- Frozen plan: `studies/pilot_v1.json`
- Plan SHA-256: `cb477d6f2f2d0c60c6b0aa04ddaba908f4d3ae6ed9aab909ec04d9267d737ba9`
- Workflow run: [open-model-pilot #2](https://github.com/yogesh0224/shadowleak/actions/runs/34698469349)
- Trigger: branch push
- Run date: 2026-09-12 UTC
- Total workflow duration: 3 minutes 41 seconds

## Feasibility result

Both pre-specified model jobs completed the plan-validation, pinned-model
execution, and artifact-upload steps successfully. Because the executor enforces
64 planned cases per model and a maximum failure rate of zero, successful job
completion establishes that every planned case completed without a recorded
generation failure.

| Model key | Planned/completed cases | Job | Artifact archive SHA-256 |
|---|---:|---|---|
| `qwen2_5_0_5b_instruct` | 64/64 | success | `6f28bfd087c7ff15efde55ef6bec4c1c286fecd2501aa84c1caf6d8e4a2c5c29` |
| `smollm2_360m_instruct` | 64/64 | success | `a1d4867ca709a27455df0f60cb4a53e32265f4fb7f52908e5c208820a7607027` |

Each evidence bundle contains the benchmark manifest, final model responses,
randomized blinded annotation queue, separate case key, run summary, per-file
hashes, model revision, prompt-format version, decoding settings, and software
runtime provenance. GitHub retains these workflow artifacts for 30 days.

## Interpretation boundary

This is an execution and artifact-completeness result only. Model responses
have not been independently annotated or adjudicated. No leakage rate,
model ranking, defense-effect estimate, or safety conclusion is reported from
the pilot. Pilot responses are excluded from any future confirmatory analysis.

The next gate is to review the two run summaries, calibrate the annotation
rubric without changing benchmark v1, freeze a separately powered confirmatory
protocol, and arrange two independent annotators.
