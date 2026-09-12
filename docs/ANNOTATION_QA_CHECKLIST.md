# ShadowLeak Annotation QA Checklist

Use this checklist before annotation starts, after each annotator finishes, and
again before final labels are joined to the hidden case key.

## Before annotation starts

- [ ] Confirm the model run passed the protocol/completeness check.
- [ ] Confirm the annotation queue came from the verified run artifact.
- [ ] Confirm `annotation_key.jsonl` is stored separately.
- [ ] Create identical copies for Annotator A and Annotator B.
- [ ] Give annotators only the blinded CSV and `ANNOTATOR_PACKET_V1.md`.
- [ ] Do not provide model identity, defense condition, detector outputs, or case IDs.
- [ ] Assign stable anonymous annotator IDs.
- [ ] Confirm annotators understand that they must work independently.

## After Annotator A finishes

- [ ] No rows were deleted.
- [ ] No duplicate `annotation_id` values were introduced.
- [ ] Every row has `gold_label`.
- [ ] Every row has `leak_type`.
- [ ] Every row has `annotator_id`.
- [ ] Every row has a rationale.
- [ ] `gold_label=0` always uses `leak_type=none`.
- [ ] `gold_label=1` never uses `leak_type=none`.
- [ ] Benign rows have all utility fields.
- [ ] Attack rows keep utility fields blank.
- [ ] `adjudication_status` is not set to `adjudicated`.

## After Annotator B finishes

Repeat the same checks used for Annotator A.

Also confirm:

- [ ] Annotator A and Annotator B contain the same annotation IDs.
- [ ] Neither annotator saw the other annotator's labels before completion.
- [ ] Neither annotator saw the hidden key or study condition metadata.

## Before adjudication

Run:

```bat
python -m research.adjudication prepare ^
  --annotator-a annotator_a.csv ^
  --annotator-b annotator_b.csv ^
  --queue adjudication_queue.csv ^
  --agreement-output agreement.json
```

Then confirm:

- [ ] `agreement.json` was created before any adjudication edits.
- [ ] Raw agreement is recorded.
- [ ] Cohen's kappa is recorded.
- [ ] Disagreement count is recorded.
- [ ] Disagreement rate is recorded.
- [ ] Only disagreement rows are present in `adjudication_queue.csv`.
- [ ] The adjudication queue remains blinded to model and defense condition.

## During adjudication

- [ ] A third reviewer handles disagreement rows.
- [ ] Every disagreement receives a final leakage label.
- [ ] Every disagreement receives a final leak type.
- [ ] Benign disagreements receive all final utility labels.
- [ ] Every disagreement has an `adjudicator_id`.
- [ ] Every disagreement has an adjudication rationale.
- [ ] The adjudicator does not see detector outputs or condition metadata.

## Finalization

Run:

```bat
python -m research.adjudication finalize ^
  --annotator-a annotator_a.csv ^
  --annotator-b annotator_b.csv ^
  --decisions adjudication_queue.csv ^
  --output annotations_final.csv
```

Confirm:

- [ ] Finalization completes without an error.
- [ ] Every successful annotation ID appears exactly once.
- [ ] Every final row has `adjudication_status=adjudicated`.
- [ ] Agreement rows were preserved automatically.
- [ ] Disagreement rows use the adjudicator's final decision.
- [ ] `annotations_final.csv` is copied to a read-only or versioned location.
- [ ] A SHA-256 hash is recorded for the final file.
- [ ] No final label changes are made after the hash is recorded without documenting a protocol deviation.

## Before unblinding for analysis

Do not join the hidden key until all boxes above are complete.

Then confirm:

- [ ] `annotations_final.csv` is frozen.
- [ ] Its SHA-256 is recorded.
- [ ] `agreement.json` is frozen.
- [ ] The adjudication file is frozen.
- [ ] The final file passes the benchmark analysis annotation validator.
- [ ] The hidden key is joined only for the preregistered statistical analysis.

## Evidence to retain

Keep the following files in the final evidence package:

- [ ] original `annotation_queue.csv`;
- [ ] `annotator_a.csv`;
- [ ] `annotator_b.csv`;
- [ ] `agreement.json`;
- [ ] `adjudication_queue.csv`;
- [ ] `annotations_final.csv`;
- [ ] hidden `annotation_key.jsonl`;
- [ ] file hashes;
- [ ] any documented annotation protocol deviations.

Do not publish the hidden key or raw response material unless the release plan
explicitly allows it. The public evidence package should contain only what is
needed for reproducibility and responsible review.
