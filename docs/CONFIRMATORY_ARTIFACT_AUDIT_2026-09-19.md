# Confirmatory evidence audit — 2026-09-19

**Study:** `shadowleak-confirmatory-v1`  
**Status:** Execution and structural integrity verified; *human labeling and substantive outcomes have not been reviewed*.  
**Scope of inspection:** GitHub Actions run/job states, archive digests, archive and JSON/CSV structure, model/plan metadata, paired IDs, manifest identity, and annotation-queue metadata only. No model-response text was inspected or evaluated for leakage.

This is a post-execution **audit report**, not an amendment to the frozen protocol or a publication of experimental results.

## Chain of custody and verified archives

| Evidence role | Model key | Workflow run | Artifact ID | ZIP SHA-256 |
|---|---|---:|---:|---|
| Primary | `qwen2_5_1_5b_instruct` | [34701116937](https://github.com/yogesh0224/shadowleak/actions/runs/34701116937) | `10304330613` | `f29ea5db8363d2080077edadf1f115d9d114b196ada3540d4c5852143a59a482` |
| Replication | `qwen2_5_0_5b_instruct` | [34703895719](https://github.com/yogesh0224/shadowleak/actions/runs/34703895719) | `10302094369` | `22c00fd7eb035734660c80905588af24c8e78428d7e6d45850df494a213b4093` |
| Replication | `smollm2_360m_instruct` | [34703895719](https://github.com/yogesh0224/shadowleak/actions/runs/34703895719) | `10303647240` | `d41b1da9b6855f5bed2903f501a1839934f02fb97a04cd60653a234774572346` |
| Replication | `tinyllama_1_1b_chat_v1` | [34703895719](https://github.com/yogesh0224/shadowleak/actions/runs/34703895719) | `10306499250` | `ee42ac977255335a823d4bfa62e825821d410c7d62d1f6f7c570c25e12a7ba13` |

The primary workflow head was frozen execution commit `c136f4315ca5c224cc1d4f802750a3baec089a6f`. The replication workflow head was `158e78ac8cc7205a9ae432ce5d260fc9ec818a1d` but its configured checkout and each archived `execution_commit.txt` identify the **same frozen execution commit** `c136f4315ca5c224cc1d4f802750a3baec089a6f`. All four run summaries record frozen study-plan SHA-256 `ad9aadfa7b08de909795d1679ead723ae00333595440c1fda4b4d877d7ebe21e`.

## Checks completed

- All four model jobs and the execution/artifact-upload steps completed successfully on 2026-09-12.
- All four ZIP archives were retrieved and their exact SHA-256 digests matched GitHub's published artifact digest. ZIP integrity checks passed.
- Every archive contains `manifest.jsonl`, `responses.jsonl`, `annotation_queue.csv`, `annotation_key.jsonl` and `run_summary.json`; replication bundles also record the execution commit.
- All internal file hashes listed in each run summary matched the archived files.
- Each run summary records **1,860 planned / 1,860 completed / 0 failed** cases, a registered model revision, the expected study ID and study-plan digest.
- Each model has **30 records**, **930 complete matched pairs**, **1,620 attack cases**, **240 benign cases**, and **1,860 blank-label annotation queue rows**. Manifests are identical across models. No mock-model evidence class was found.
- Thus the registered four-model set contains **7,440 successfully generated responses** and **0 recorded generation failures**. There are still **no verified independently adjudicated gold labels**, leakage estimates or utility findings.

## Annotation packaging blocker

The four model-specific queues each have 1,860 unique IDs, but they reuse the *same* 1,860 `annotation_id` values across models. Concatenating these queues produces 7,440 rows with only 1,860 distinct annotation IDs.

For a pooled blinded queue, create a fresh, unique opaque ID for each response, shuffle across models and keep a **separate access-controlled** crosswalk to (model key, original annotation ID, original case ID). Validate reversibility and 1:1 correspondence without altering any response text, frozen model outputs, registered prompt, or defense setting. Annotators and adjudicator must not see this key, model identity, original case ID, pair ID, defense condition or detector scores until labels are finalized. Defense-specific response content may still reveal a condition; document this residual blinding limitation.

Relevant task: [#6 — pooled blinded annotation](https://github.com/yogesh0224/shadowleak/issues/6).

## Preservation and access control

GitHub reported all four artifacts as **not expired** on 2026-09-19 and reported an expiration date of **2026-10-12** for each. The copies retrieved into a chat workspace are temporary, **not** a verified durable research archive.

Preserve byte-identical ZIPs in durable, access-controlled user-managed storage **before 2026-10-12**, independently verify the ZIP SHA-256 values above, and record private custody and access details. Do not commit the archives, model-response files, annotation queues containing response text, or unblinding keys to this public repository. If an original artifact is lost, report the loss and any replacement execution transparently; do not silently present a rerun as the original preregistered execution.

Relevant task: [#5 — preserve original evidence](https://github.com/yogesh0224/shadowleak/issues/5).

## What this audit does not establish

Successful generation and structurally valid data do not establish disclosure, defense efficacy, inter-annotator agreement, detector quality, statistical significance, generalization, or publishability. Only begin registered outcome analysis after independent double annotation, adjudication, label freezing, and a documented analysis-integrity check.

See [publication status](PUBLICATION_STATUS.md), [publication roadmap](RESEARCH_ROADMAP.md), and the original [frozen protocol](CONFIRMATORY_PROTOCOL_V1.md).
