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

## Research gap

Existing work provides strong components of the problem: privacy extraction,
adversarial prompt benchmarks, human-evaluation methodology, documentation
frameworks, and multidimensional trustworthiness assessment. Less attention has
been paid to connecting these components into one pre-specified pipeline for a
privacy-defense claim in which:

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

ShadowLeak is designed to evaluate that combined workflow. Its intended
contribution is therefore not a universal privacy defense or a new legal
standard, but a reproducible method for converting a red-team privacy finding
into bounded, auditable evidence.

## Citation keys

The working BibTeX entries are in `docs/references.bib`. The source-by-source
claim boundaries are documented in `docs/LITERATURE_MATRIX.md`.
