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

## Outcomes

1. Gold leakage rate, overall and by attack family.
2. Detector precision, recall, false-positive rate, F1, and ROC AUC.
3. Defense effect on leakage rate.
4. Utility retained after defense, measured on a separate benign-task set.
5. Latency and computational cost where relevant.

Rates must include denominators and uncertainty intervals. A lower leakage rate
is not sufficient evidence of a better defense if benign-task utility collapses.

## Ground truth

Use the independent protocol in `ANNOTATION_GUIDE.md`. Detector-generated
`LeakageResult` rows are predictions, not labels. Synthetic canary equality can
support exact-leak adjudication, but partial, semantic, and inferred leakage
requires blinded human review.

## Validation split

All responses associated with one sensitive record remain in the same fold.
This prevents a classifier from learning record-specific strings in training
and receiving related strings in testing. For a template-generalization claim,
hold out attack templates or entire attack families as an additional analysis.

## Reproducibility

Record model revision, prompt template, defense configuration, seed, software
environment, and generated response. Never silently replace failed model calls
with mock outputs. The mock model is suitable only for pipeline validation.

## Current evidence boundary

ShadowLeak is a research prototype. The repository does not yet contain a
large, independently annotated, multi-model benchmark. Until that study is run,
do not claim that one attack family is highest-risk or that hybrid detection
improves coverage.

