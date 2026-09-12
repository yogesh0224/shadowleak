# ShadowLeak Research Methodology

## Research question

How often do language models disclose synthetic protected attributes under
different adversarial prompt strategies, and how reliably do automated
detectors and output defenses identify or reduce those disclosures?

## Threat model

The evaluated model receives a context containing synthetic canary records. An
attacker may use direct extraction, indirect inference, authority role-play,
obfuscation, reconstruction, social engineering, or multi-turn prompting. The
primary outcome is disclosure of a protected canary attribute in the response.

The project does not claim to measure memorization of real training data. That
is a different threat model requiring different access assumptions and study
design.

## Experimental factors

- model and exact model revision;
- decoding parameters;
- attack family and template identifier;
- single-turn versus multi-turn interaction;
- defense configuration;
- protected field type;
- random seed and replicate.

## Benchmark v1 sampling design

The versioned manifest uses 100 deterministic synthetic records, 12 attack
templates across nine families, and four benign tasks. Every record-template
combination is run once without a defense and once with `guardshield-v1`,
creating matched pairs. Pair IDs support within-case comparison; record IDs
support grouped validation and prevent related observations crossing train/test
boundaries.

Version 1 is preserved for the frozen feasibility pilot. Benchmark v2 expands
each of the nine attack families to three controlled prompt variants: two
`development` variants and one pre-designated `heldout` variant. This supports
a stronger generalization question than template-level averages alone.

For detector generalization, held-out prompts are evaluated on sensitive records
that are also absent from detector training. This avoids a weaker design in
which the wording is unseen but record-specific signals have already appeared
in training. The v2 generalization protocol therefore tests both unseen prompt
variants and unseen sensitive records.

Both v1 and v2 remain single-turn benchmarks. The `multi_turn_setup` family
tests a conversation-scaffolding request inside one prompt; it is not evidence
about a stateful multi-turn system. A genuine conversational adapter is future
work.

## Outcomes

1. Gold leakage rate, overall and by attack family.
2. Detector precision, recall, false-positive rate, F1, and ROC AUC.
3. Defense effect on leakage rate.
4. Utility retained after defense, measured on a separate benign-task set using task completion, correctness, relevance, and over-refusal.
5. Latency and computational cost where relevant.
6. Privacy-utility trade-off: leakage reduction relative to benign utility change, reported descriptively rather than collapsed into an unregistered welfare score.

Rates must include denominators and uncertainty intervals. A lower leakage rate is not sufficient evidence of a better defense if benign-task utility collapses. Detailed benign utility uses an equal-weight 0-1 composite of task completion, correctness, relevance, and reversed over-refusal, while also reporting each dimension separately and latency by defense condition. The equal weighting is a transparent measurement convention, not a claim that all dimensions have equal economic or social value.

The primary defense estimand is the matched absolute risk reduction: leakage
rate without defense minus leakage rate with defense. Because each synthetic
record contributes repeated prompt observations, prompt rows are not treated as
independent experimental units. Primary uncertainty for the defense effect is
therefore estimated by a percentile bootstrap that resamples whole `record_id`
clusters and preserves every repeated observation within each sampled record.

The exact two-sided McNemar statistic over prompt-level matched pairs is retained
as a descriptive paired diagnostic, not as the sole confirmatory inferential
claim, because repeated pairs from the same record can be correlated. Benign-task
utility uses the same matched design. Wilson intervals are reported for
individual rates; they are not misrepresented as confidence intervals for the
paired difference.

## Ground truth

Use the independent protocol in `ANNOTATION_GUIDE.md`. Detector-generated
`LeakageResult` rows are predictions, not labels. Synthetic canary equality can
support exact-leak adjudication, but partial, semantic, and inferred leakage
requires blinded human review.

## Validation split

All responses associated with one sensitive record remain in the same fold.
This prevents a classifier from learning record-specific strings in training
and receiving related strings in testing. For a template-generalization claim, use the pre-designated v2 held-out prompt
variants and keep test records disjoint from training records. Whole-family
holdout remains an additional, harder external-validity analysis rather than a
claim implied by the current v2 design.

## Reproducibility

Record model revision, prompt template, defense configuration, seed, software
environment, and generated response. Never silently replace failed model calls
with mock outputs. The mock model is suitable only for pipeline validation.

Hugging Face studies must pin an immutable model commit SHA. Generated text is
created through the tokenizer's native chat template and decoded only after the
input-token boundary, so input echo is not mistaken for an output disclosure.
The response artifact records the adapter, prompt-format version, decoding
configuration, device, Python, PyTorch, and Transformers versions. Failed
generations are counted and excluded explicitly rather than silently assigned
a non-leak label.

The frozen feasibility pilot is documented in `PILOT_PROTOCOL_V1.md` and
`studies/pilot_v1.json`. It is deliberately too small for confirmatory claims;
its only role is to identify execution or artifact defects before a separately
registered, adequately sized study.

Before freezing the confirmatory study, sample size must be justified from a
pre-specified minimum effect and expected discordant-pair probabilities. The
`research.power_analysis` utility provides a transparent asymptotic McNemar
planning calculation. Because that calculation assumes independent matched
pairs, its result is a lower-bound planning input for this repeated-record
design; the final preregistration must additionally justify record count and any
inflation or simulation used to account for within-record dependence.

## Current evidence boundary

ShadowLeak is a research prototype with benchmark infrastructure. The
repository does not yet contain a large, independently annotated, multi-model
result set. Until that study is run, do not claim that one attack family is
highest-risk or that hybrid detection improves coverage.


## Economic sensitivity analysis

ShadowLeak can translate measured leakage, benign utility, and latency into a
transparent cost comparison across defense configurations. For one explicit
weight vector, normalized total cost is:

`leakage_cost * leakage_rate + utility_loss_cost * (1 - utility) + latency_cost_per_ms * latency_ms`.

The weights are preference parameters supplied by analysts, institutions, or
stakeholders. They are not market prices, welfare estimates, or objectively
correct social values. The intended analysis is therefore a sensitivity grid:
report which configuration is preferred across many pre-specified weight
combinations and identify regions where the preferred decision changes.

A substantive study should preregister the weight grid or document the external
source of institution-specific weights before inspecting benchmark outcomes.
Post-hoc weights may be used only for exploratory sensitivity analysis.
