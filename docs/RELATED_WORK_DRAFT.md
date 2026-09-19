# Related Work Draft

This section is a pre-results literature synthesis for
`docs/MANUSCRIPT_V1.md`. It is deliberately written to preserve distinctions
between privacy threat models and evidence classes.

## Privacy leakage and memorization

Early empirical work established that neural language models can emit memorized
training examples when queried appropriately. Carlini et al. demonstrated
training-data extraction from GPT-2, including personally identifying strings,
while later work quantified how memorization varies with model scale,
duplication, and prompt context. Nasr et al. subsequently showed that scalable
extraction remains possible across open, semi-open, and closed language models
and that alignment does not eliminate extractable memorization.

ShadowLeak is motivated by the broader privacy risk demonstrated by this line
of work but studies a different threat model. Its benchmark does not claim to
recover private training examples. Instead, it places visibly synthetic
protected attributes in model context and measures whether adversarial prompts
cause those attributes to be disclosed. This distinction matters because
training-data memorization and context disclosure involve different access
assumptions, attack surfaces, and causal interpretations.

## Adversarial prompting and benchmark validity

A second literature examines prompt injection, prompt hacking, and jailbreaking.
Liu et al. formalize prompt-injection attacks and compare multiple attacks and
defenses in a shared experimental framework. HackAPrompt demonstrates the
diversity of prompt-hacking strategies at large scale, while JailbreakBench
argues for standardized threat models, prompts, chat templates, scoring
functions, and reproducible artifacts.

This work is methodologically important for ShadowLeak because adversarial
prompting results can be highly benchmark-dependent. ShadowLeak therefore fixes
attack families and prompt variants before outcome inspection, records exact
model revisions and prompt provenance, and evaluates matched defended and
undefended cases rather than relying on isolated successful examples.

Recent benchmark research also highlights problems with outcome measurement.
StrongREJECT shows that common jailbreak success measures can materially
overstate attack effectiveness relative to human judgments, particularly when
a model produces a non-refusal response that is nevertheless low quality.
Do-Not-Answer and TrustLLM similarly demonstrate the value of structured safety
evaluation across multiple models and dimensions. These findings motivate
ShadowLeak's separation of detector predictions from human gold labels and its
decision to score benign utility and over-refusal rather than interpreting
maximum blocking as an unqualified safety improvement.

## Human annotation and disagreement

Human evaluation introduces its own measurement risks. Artstein and Poesio
survey inter-coder agreement methods and emphasize that agreement coefficients
depend on assumptions about annotators and label structure. Work on subjective
NLP annotation further shows that disagreement is not always random error.
Leonardelli et al., for example, find that annotator agreement levels can
materially change downstream evaluation behavior. Howcroft et al. document
substantial inconsistency in human-evaluation terminology and reporting across
NLG research.

ShadowLeak responds by using a written annotation rubric, two independent
annotation passes, pre-adjudication raw agreement and Cohen's kappa,
disagreement-only adjudication, and a separate key that withholds case and
condition metadata until labels are frozen. Agreement statistics are treated as
annotation-quality evidence, not as proof that the leakage construct itself is
valid.

## Documentation, auditing, and AI governance

Model Cards and Datasheets for Datasets established influential documentation
patterns for reporting intended use, evaluation conditions, dataset
composition, and limitations. Raji et al. extend this logic into an
organizational auditing framework in which evaluation artifacts contribute to
an end-to-end accountability process.

The NIST AI Risk Management Framework similarly emphasizes governance,
mapping, measurement, and management of AI risk. Its measurement function
calls for documented evaluation methods, uncertainty, relevant benchmarks,
independent review where appropriate, and explicit attention to trade-offs
among trustworthiness characteristics. The NIST Generative AI Profile extends
that risk-management framing to generative systems. More recent work on audit
cards argues that evaluation results require contextual information about
scope, process integrity, access, and review before they can support governance
decisions.

ShadowLeak adopts this evidence-oriented framing while retaining a narrower
claim. Its governance profiles are illustrative sensitivity scenarios, not
compliance tests. Model provenance, annotation procedures, failure accounting,
analysis code, artifact hashes, and evidence labels are retained so a reviewer
can reconstruct how a technical finding was produced and assess whether it is
relevant to a particular institutional decision.

## Privacy-utility and decision trade-offs

Safety and privacy interventions can produce costs as well as benefits.
TrustLLM explicitly observes exaggerated safety behavior in which benign
prompts are incorrectly refused, while StrongREJECT shows that some adversarial
interventions can alter useful capabilities. More general privacy research also
treats privacy and utility as competing objectives rather than assuming that a
single configuration dominates every decision context.

ShadowLeak therefore reports protected-attribute leakage, task completion,
correctness, relevance, over-refusal, and latency separately before computing
any composite or decision score. Its economic layer is a sensitivity analysis
over explicit preference weights, not an estimate of social welfare or market
cost. This preserves the distinction between empirical measurements and the
institutional values used to act on those measurements.

## Closest work on inference-time privacy and evaluation validity

PrivacyLens evaluates contextual privacy norms and harmful information flows in model-agent communication, including leakage and action helpfulness (Shao et al., NeurIPS 2024; https://papers.nips.cc/paper_files/paper/2024/hash/a2a7e58309d5190082390ff10ff3b2b8-Abstract-Datasets_and_Benchmarks_Track.html). AgentDojo tests attack and defense behavior in interactive applications where untrusted tool outputs can redirect agents away from legitimate tasks (Debenedetti et al., NeurIPS 2024; https://arxiv.org/abs/2406.13352). Alizadeh et al. (2025; https://arxiv.org/abs/2506.01055) further investigate personal-data exfiltration in synthetic banking-agent tasks and report utility consequences alongside attack and defense outcomes. Thus, inference-time privacy evaluation, synthetic sensitive data, adversarial testing, and privacy–utility comparisons are **not** novel in isolation.

ShadowLeak tests a different and narrower empirical object: benchmark-defined protected-attribute disclosure from synthetic information already provided in the same user message as a single-turn request, under a fixed regex-based input/output defense. The current experiment does not establish an independent high-priority confidentiality policy or lower-trust attacker-controlled tool surface; it must not be described as demonstrating unauthorized access, a tool-output prompt-injection breach, or interactive multi-turn attack success. Its `multi_turn_setup` templates are single-turn formulations.

Evaluation validity is a plausible motivation rather than a previously demonstrated ShadowLeak result. StrongREJECT (Souly et al., NeurIPS 2024; https://papers.nips.cc/paper_files/paper/2024/hash/e2e06adf560b0706d3b1ddfca9f29756-Abstract-Datasets_and_Benchmarks_Track.html) finds consequential differences between common jailbreak-success metrics and human judgment in a related *but different* outcome domain. CASE-Bench (Sun et al., ICML 2025; https://proceedings.mlr.press/v267/sun25ab.html) likewise shows the importance of context when evaluating apparently safe or harmful requests. ShadowLeak can investigate whether analogous measurement sensitivity arises for its narrower disclosure outcome, without assuming it does, and without equating its four benign prompts with a comprehensive authorized-use evaluation.

## Research gap

Prior research already combines several relevant components, including
contextual privacy evaluation, adversarial benchmarks, human assessment, defense
comparisons, and task utility. ShadowLeak's **candidate** contribution is a
bounded, auditable measurement study: test how independently adjudicated and
automated disclosure labels affect paired estimates of a *fixed* defense's
effect, while retaining the frozen primary analysis and its limitations. Its
existing protocol operationalizes this question using:

1. the privacy threat model is explicit and uses only synthetic protected data;
2. defended and undefended responses are matched within the same prompt and
   synthetic record;
3. repeated prompt observations are not treated as independent experimental
   units;
4. detector outputs are separated from blinded human gold labels;
5. benign utility, over-refusal, latency, failures, and replication models are
   reported alongside privacy outcomes; and
6. governance and economic interpretation remains explicitly downstream of the
   measured technical evidence.

Whether the proposed measurement comparison yields an empirically distinctive
finding remains unresolved until independent annotation, registered analysis,
and a more exhaustive comparison with disclosure-specific recent literature
are complete. The new measurement question is not a retroactively registered
primary confirmatory claim; see `docs/PUBLICATION_POSITIONING_V1.md`.

## Citation keys

The working BibTeX entries are in `docs/references.bib`. The source-by-source
claim boundaries are documented in `docs/LITERATURE_MATRIX.md`.
