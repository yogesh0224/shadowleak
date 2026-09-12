# Research Roadmap

## Stage 1 - Valid measurement

- replace detector-derived ML labels with independent gold annotations;
- seed every randomized component;
- report real leakage-type rates instead of placeholder zeros;
- validate by sensitive-record group;
- add automated tests and a reproducibility workflow.

## Stage 2 - Publishable benchmark

- generate at least 100 synthetic canary records without real personal data;
- preregister attack families, primary outcomes, exclusions, and statistics;
- evaluate multiple openly identified model revisions;
- run repeated seeds and balanced defended/undefended conditions;
- use two blinded annotators for non-exact disclosures;
- publish aggregate results, uncertainty intervals, and error analysis.

## Stage 3 - Governance contribution

- evaluate whether detector thresholds behave differently by language and
  protected-field type;
- quantify privacy-versus-utility trade-offs;
- create a model evaluation card and auditable evidence bundle;
- compare observed coverage against organizational privacy-risk requirements;
- write a paper separating measurement findings from policy recommendations.

## Candidate paper framing

**From Red-Team Finding to Accountable Evidence: Measuring Privacy Leakage in
Language-Model Systems**

The contribution should be the evaluation protocol and evidence quality, not a
new dashboard or an unsupported claim that one detector solves privacy leakage.

