# Blinded confirmatory annotation handoff

**Study:** shadowleak-confirmatory-v1  
**Status (2026-09-19):** Four model runs structurally verified. A collision-free pooled queue has been generated in a temporary workspace, **not** preserved to durable private storage or independently human-labeled. The original four model-specific queues are individually valid but reuse anonymous IDs across models. See [dated artifact audit](CONFIRMATORY_ARTIFACT_AUDIT_2026-09-19.md) and [publication status](PUBLICATION_STATUS.md).

## Trust boundaries

| Asset | Who may access it | Contains |
|---|---|---|
| Four original ZIP archives | Research custodian / authorized analyst only | Unblinded response metadata, model identity and original annotation keys. Do not send to annotators or commit publicly. |
| blinded_annotation_queue.csv | Two independent human annotators; disagreement adjudicator as needed | Synthetic context, target field/value, prompt, original response, a newly generated opaque annotation ID and **blank** labeling fields. No explicit model/case/pair/defense metadata or detector outputs. |
| PRIVATE_annotation_crosswalk.jsonl | Research custodian only until both passes and adjudication are frozen | Pooled anonymous ID to original model key, original annotation ID, original case ID, pair/record ID and defense condition. **Never** send with the annotator-facing CSV. |
| PRIVATE_packaging_manifest.json | Research custodian | Source ZIP digests, output CSV/crosswalk digests, case counts and packaging status. This file does **not** prove human labeling is complete. |

**Residual blinding limitation:** The original response may explicitly say it was blocked or contain other model/defense-specific writing. Annotators may also notice repeated prompts or contexts. The packaging script does not rewrite, mask or selectively remove original responses to hide these cues; report the limitation transparently.

## Packaging command

Use Python 3.12+ and run from the repository root. Put the four previously downloaded **unchanged** original GitHub Actions ZIPs in a private local folder, e.g. \`/secure/shadowleak/source/\`, and run the following command with paths adapted to your system:

~~~bash
python -m research.pooled_annotation \
  --archive qwen2_5_1_5b_instruct=/secure/shadowleak/source/primary.zip \
  --archive qwen2_5_0_5b_instruct=/secure/shadowleak/source/qwen05.zip \
  --archive smollm2_360m_instruct=/secure/shadowleak/source/smollm.zip \
  --archive tinyllama_1_1b_chat_v1=/secure/shadowleak/source/tinyllama.zip \
  --sha256 qwen2_5_1_5b_instruct=f29ea5db8363d2080077edadf1f115d9d114b196ada3540d4c5852143a59a482 \
  --sha256 qwen2_5_0_5b_instruct=22c00fd7eb035734660c80905588af24c8e78428d7e6d45850df494a213b4093 \
  --sha256 smollm2_360m_instruct=d41b1da9b6855f5bed2903f501a1839934f02fb97a04cd60653a234774572346 \
  --sha256 tinyllama_1_1b_chat_v1=ee42ac977255335a823d4bfa62e825821d410c7d62d1f6f7c570c25e12a7ba13 \
  --output-dir /secure/shadowleak/private_annotation_package
~~~

The script **refuses** an unexpected original ZIP digest, incorrect registered model identity/revision, incorrect case counts, inconsistent internal source-file hashes, already labeled original queues, incomplete original queue/key/response mapping and unexpected CSV columns. It checks model manifests match; it does not inspect or summarize leakage outcomes. It does not alter the originals. Each invocation generates new random pooled IDs and queue order; **archive the generated CSV, crosswalk and packaging manifest as one immutable package rather than regenerating a different version after human annotation begins**.

Files are created inside a private directory with restrictive local POSIX permissions (directory 0700, files 0600). These permissions are not a substitute for secure sharing and access control when copying files to other systems.

## Before annotators receive any file

1. **Preserve the four unchanged source archives outside expiring GitHub Actions storage.** Confirm original ZIP SHA-256 values and record a private custodian log. GitHub Actions reports that the original artifacts expire on **2026-10-12**; a temporary ChatGPT workspace is not durable archival storage. See [issue #5](https://github.com/yogesh0224/shadowleak/issues/5).
2. Check the output manifest reports 7,440 blank-label responses, four registered sources, 7,440 unique pooled IDs, and matching output digests. Ensure the CSV has no model/condition/case/pair columns.
3. Privately retain the two \`PRIVATE_*\` files; do not place them alongside the annotator copies in an accessible shared folder. Keep the original model ZIPs separate from annotators.
4. Make two **independent copies of the same blinded queue**, one for each human annotator. Assign anonymous annotator identifiers and never allow them to consult one another's labels before submission. Provide the [annotation guide](ANNOTATION_GUIDE.md).
5. Calibrate on *separate pilot data*, not by viewing/discussing confirmatory outcomes before the independent passes. Resolve rubric ambiguity without changing the frozen confirmatory protocol after outcome inspection.

## Human annotation and analysis handoff

- Annotator A and Annotator B label all successful responses independently, including required benign-utility fields. Expected workload is **7,440 responses × 2 human passes = 14,880 annotation decisions**.
- Calculate pre-adjudication agreement and generate the disagreement-only blinded adjudication queue using the existing \`research.adjudication\` workflow. A third reviewer resolves disagreements without the private crosswalk.
- Freeze and hash the full final-label dataset and agreement/adjudication artifacts **before** any join with model keys or defense conditions.
- **After the freeze only**, the custodian uses the preserved pooled crosswalk to split the final pooled annotations back into four model-specific files and build model-specific \`annotation_id -> original_case_id\` keys for the registered \`research.benchmark_analysis\` commands. The original model response files stay unchanged. Verify all successful cases and the original paired structure are represented exactly once per model.
- Keep the registered primary analysis, secondary family tests, replication evidence and additional detector-versus-human analyses appropriately separated. Never turn a detector prediction into human ground truth.

## Completion criteria for issue #6

- [x] Implement offline pooled packaging and synthetic-fixture tests.
- [x] Generate one 7,440-row, collision-free blinded queue and separate private crosswalk from the verified original ZIPs in a temporary workspace.
- [ ] Verify custodian-controlled **durable private** storage of the original archives and this exact generated package, with recorded hashes and restricted access.
- [ ] Confirm separate annotator handoff and the independent annotation assignments.
- [ ] Record a private artifact location and custodial handoff date (do not publish private storage URLs or the crosswalk in GitHub).

This document is an operational handoff guide, not evidence that human annotation has started or been completed.
