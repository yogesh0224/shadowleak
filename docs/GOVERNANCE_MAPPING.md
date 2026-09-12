# AI Governance and Accountability Mapping

ShadowLeak produces evidence for model-risk decisions; it does not itself
certify legal compliance or model safety.

The mapping is informed by the voluntary [NIST AI Risk Management Framework
1.0](https://www.nist.gov/itl/ai-risk-management-framework), its [Generative AI
Profile (NIST AI 600-1)](https://doi.org/10.6028/NIST.AI.600-1), and OWASP's
[LLM02:2025 Sensitive Information
Disclosure](https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/).
It is an evidence crosswalk, not a claim of conformance.

| Accountability question | ShadowLeak artifact |
|---|---|
| What privacy failure is in scope? | Explicit threat model and protected-field taxonomy |
| How was risk measured? | Versioned prompts, outputs, gold labels, detector predictions, and metrics |
| Can another reviewer reproduce it? | Seeds, model revisions, environment, tests, and generated reports |
| Who decided whether output leaked? | Blinded annotation and adjudication record |
| Does the defense reduce harm? | Paired defended/undefended leakage and benign-utility results |
| Where does evidence not generalize? | Model, language, dataset, attack, and annotation limitations |
| Can evidence be traced to one run? | Manifest hash, immutable model revision, run ID, seed, case ID, and pair ID |
| Were failures hidden as safe outputs? | Explicit failure counts and exclusions in the report |

| Governance function | ShadowLeak contribution | Residual responsibility |
|---|---|---|
| Govern | Named owner, threat model, evaluation card, prohibited claims | Organization sets risk appetite and decision rights |
| Map | Protected-field and attacker taxonomy, scope and exclusions | Deployment-specific actors, data flows, and harms |
| Measure | Paired red-team cases, independent labels, uncertainty and utility | Representative models, languages, and operating conditions |
| Manage | Defense comparison and documented unresolved risks | Mitigation selection, monitoring, incident response, and acceptance |

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
