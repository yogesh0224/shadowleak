# AI Governance and Accountability Mapping

ShadowLeak produces evidence for model-risk decisions; it does not itself
certify legal compliance or model safety.

| Accountability question | ShadowLeak artifact |
|---|---|
| What privacy failure is in scope? | Explicit threat model and protected-field taxonomy |
| How was risk measured? | Versioned prompts, outputs, gold labels, detector predictions, and metrics |
| Can another reviewer reproduce it? | Seeds, model revisions, environment, tests, and generated reports |
| Who decided whether output leaked? | Blinded annotation and adjudication record |
| Does the defense reduce harm? | Paired defended/undefended leakage and benign-utility results |
| Where does evidence not generalize? | Model, language, dataset, attack, and annotation limitations |

For governance-facing reporting, publish a concise evaluation card containing:

- responsible owner and evaluation date;
- model/version and deployment context;
- threat actors and protected attributes;
- evaluation coverage and exclusions;
- leakage and false-positive results with uncertainty;
- defense-utility trade-offs;
- unresolved risks and required mitigations;
- links to reproducible evidence.

This structure supports testing, evaluation, verification, validation, and
documentation practices associated with AI risk management. A governance claim
must remain proportional to the evaluated threat model.

