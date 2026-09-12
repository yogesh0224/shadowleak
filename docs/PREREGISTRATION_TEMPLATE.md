# ShadowLeak Study Preregistration Template

Freeze this document and its referenced Git commit before collecting responses
from study models. Replace every placeholder; do not edit confirmatory decisions
after inspecting outcomes.

## Study metadata

- Title:
- Researchers and roles:
- Registration date and public timestamp:
- Repository commit:
- Benchmark version and expected manifest SHA-256:

## Research questions and hypotheses

- Primary research question:
- Primary directional hypothesis:
- Secondary hypotheses:
- Exploratory questions (not confirmatory):

## Systems and sampling

- Model IDs and immutable revisions:
- Inclusion rationale established before testing:
- Access mode and hardware:
- Decoding configuration:
- Records, templates, attack families, benign tasks, and repeated seeds:
- Minimum effect of interest and rationale:
- Assumed prevented/induced discordant-pair probabilities:
- Alpha and target power:
- Preliminary matched-pair requirement from `research.power_analysis`:
- Planned number of independent synthetic records:
- Planned number of successful matched pairs per model:
- Clustering inflation or simulation used to justify the final record count:

## Outcomes

- Primary outcome: adjudicated binary protected-attribute leakage.
- Primary estimand: matched absolute risk reduction from `none` to
  `guardshield-v1`.
- Primary uncertainty analysis: record-cluster percentile bootstrap for the
  matched absolute risk reduction, resampling whole `record_id` clusters.
- Paired diagnostic: exact two-sided McNemar test over discordant attack pairs;
  do not interpret it as independent-row evidence when records contribute
  repeated prompt pairs.
- Secondary outcomes: leakage by pre-specified family/field, leak-type counts, benign utility preservation, task completion, correctness, relevance, over-refusal, composite utility, latency, and model-failure rate.
- Privacy-utility analysis: pre-specify whether the composite is descriptive only or whether any weighted decision rule will be used. Any welfare weights must be frozen before outcome inspection.

## Annotation plan

- Two independent annotators and their training procedure:
- Blinding and queue assignment:
- Disagreement adjudicator:
- Agreement statistic: raw agreement and Cohen's kappa before adjudication.
- Rule for exact, partial, semantic, inferred, and non-leak labels:
- Rule for benign utility preservation:
- Rules for task completion, correctness, relevance, and over-refusal:
- Whether utility dimensions are independently double-annotated and adjudicated:

## Exclusions and missingness

- A failed generation is excluded from outcome estimation and reported as a
  failure; it is never relabeled as a non-leak.
- A matched pair with one failed member is excluded from the paired analysis
  and counted as incomplete.
- Retries, timeouts, and maximum retry count:
- Minimum successful-pair threshold and stopping rule:
- Any other exclusion established before data inspection:

## Statistical analysis

- Report every rate with numerator, denominator, and 95% Wilson interval.
- Report both condition rates, paired absolute difference, discordant counts,
  and exact McNemar p-value as a paired diagnostic.
- Report the record-cluster bootstrap estimate, number of independent record
  clusters, bootstrap seed/iterations, and 95% interval for the primary defense
  estimand.
- Family and protected-field analyses are:
  confirmatory / exploratory (choose and specify multiplicity treatment).
- Multiple-comparison correction, if applicable:
- Sensitivity analyses:
- No post-hoc prompt or threshold changes will be described as confirmatory.

## Ethics, release, and dual use

- Confirmation that benchmark records are visibly synthetic:
- Response access, retention, and deletion controls:
- Plan for releasing aggregate results and minimal reproducibility artifacts:
- Withheld artifacts and reason:
- Dual-use review and redaction rule:
- Institutional or ethics review status, if applicable:

## Deviations

Record every deviation from this plan with a timestamp, rationale, author, and
whether it occurred before or after outcome inspection.
