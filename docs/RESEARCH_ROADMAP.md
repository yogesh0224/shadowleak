# Research Roadmap

## Stage 1 - Valid measurement

- replace detector-derived ML labels with independent gold annotations;
- seed every randomized component;
- report real leakage-type rates instead of placeholder zeros;
- validate by sensitive-record group;
- add automated tests and a reproducibility workflow.

## Stage 2 - Publishable benchmark

- [x] generate a versioned 100-record synthetic benchmark without real personal data;
- [x] balance matched defended/undefended attack and benign cases;
- [x] implement blinded queues, a separate case key, and adjudication checks;
- [x] implement Wilson intervals, exact McNemar tests, failure accounting, and
  inter-annotator agreement;
- [x] freeze and automate a two-model feasibility pilot using immutable,
  ungated model revisions;
- [x] execute the frozen pilot with complete, hashed evidence bundles for both
  pre-specified models;
- [x] add record-cluster-aware uncertainty for repeated prompt observations;
- [x] add transparent paired-outcome power planning for preregistration inputs;
- [x] freeze a cluster-aware sample-size justification and preregister hypotheses,
  primary outcomes, exclusions, model selection, multiplicity families, and model-level contrasts;
- [x] expand each attack family with development and held-out prompt variants;
- [x] add detector evaluation on held-out prompts and disjoint sensitive records;
- [x] add whole-attack-family holdout with disjoint sensitive records as a harder external-validity analysis;
- [ ] evaluate multiple immutable model revisions over repeated seeds;
- [ ] complete two independent annotations and adjudication;
- [ ] publish aggregate results and qualitative error analysis;
- [x] freeze the manuscript structure, result-table shells, figure plan, and claim hierarchy before confirmatory outcome inspection.

## Stage 3 - Governance contribution

- evaluate whether detector thresholds behave differently by language and
  protected-field type;
- [x] quantify privacy-versus-utility trade-offs with multidimensional benign utility and latency;
- [x] add economic sensitivity analysis showing how defense preference changes across leakage, utility-loss, and latency cost assumptions;
- [ ] source stakeholder- or institution-specific cost assumptions for any substantive economics claim;
- create a model evaluation card and auditable evidence bundle;
- [x] add auditable decision profiles that compare measured leakage, utility, over-refusal, and latency against explicit organizational thresholds;
- [ ] replace illustrative profiles with stakeholder- or institution-supplied thresholds for any substantive deployment study;
- [ ] complete the final paper separating measurement findings from policy recommendations.

## Candidate paper framing

**From Red-Team Finding to Accountable Evidence: Measuring Privacy Leakage in
Language-Model Systems**

The contribution should be the evaluation protocol and evidence quality, not a
new dashboard or an unsupported claim that one detector solves privacy leakage.
