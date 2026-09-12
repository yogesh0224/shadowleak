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


## Decision profiles

ShadowLeak can evaluate one measured model-defense configuration against explicit
organizational decision thresholds with `python -m research.governance_report`.
The profile file must state the deployment context, threshold values, and profile
status. Built-in example profiles are intentionally marked `illustrative_only`.

A profile can constrain:

- maximum observed leakage rate;
- minimum benign composite utility;
- maximum benign over-refusal rate;
- maximum mean latency.

A pass/fail result means only that the measured configuration satisfies the
numbers encoded in that profile for the evaluated benchmark. It is not legal
compliance, certification, regulatory approval, or proof of safety. Sector or
organization-specific thresholds should be supplied by accountable decision
makers and frozen before outcome inspection when used for confirmatory claims.

The example university, hospital, bank, government, and hiring profiles are
sensitivity-analysis scenarios, not claims about what those sectors legally
require. Their purpose is to make risk appetite explicit and auditable rather
than burying it in narrative interpretation.
