# Literature and Citation Matrix

Status: **source-checked working bibliography**  
Purpose: support `docs/MANUSCRIPT_V1.md` without silently importing claims from memory.

This matrix separates literature by the empirical object it actually studies.
A paper about training-data memorization is not treated as evidence about
context disclosure; a jailbreak benchmark is not treated as a privacy
benchmark; and governance frameworks are not treated as legal thresholds.

## A. Privacy leakage and memorization

| Key | Source | What the source establishes | Relevance to ShadowLeak | Boundary / caution |
|---|---|---|---|---|
| carlini2021extracting | Carlini et al., “Extracting Training Data from Large Language Models,” USENIX Security 2021 | Querying a language model can recover memorized training examples, including personally identifying strings, under an extraction threat model. | Establishes that language models can expose sensitive text and motivates privacy-oriented adversarial evaluation. | ShadowLeak does **not** test memorization of real training data. Its primary threat model is disclosure of synthetic protected attributes supplied in context. |
| carlini2023memorization | Carlini et al., “Quantifying Memorization Across Neural Language Models,” ICLR 2023 | Memorization varies with model capacity, duplication, and prompting context, and can differ across model families. | Supports treating model identity and scale as sources of heterogeneity rather than assuming one model generalizes to all others. | Memorization frequency is not the same estimand as context leakage under adversarial prompting. |
| nasr2023scalable | Nasr et al., “Scalable Extraction of Training Data from (Production) Language Models,” 2023 | Demonstrates extractable memorization across open, semi-open, and closed language models and shows alignment does not eliminate training-data extraction. | Reinforces the need to evaluate privacy failures after alignment or safety layers rather than assuming safeguards eliminate leakage. | The attack target is memorized training data; ShadowLeak’s canary benchmark measures disclosure from supplied context. |

## B. Adversarial prompting, jailbreaks, and benchmark design

| Key | Source | What the source establishes | Relevance to ShadowLeak | Boundary / caution |
|---|---|---|---|---|
| liu2023promptinjection | Liu et al., “Formalizing and Benchmarking Prompt Injection Attacks and Defenses,” 2023 | Formalizes prompt-injection attacks and evaluates multiple attacks, defenses, models, and tasks in a common framework. | Supports systematic attack-family and defense evaluation instead of isolated red-team anecdotes. | Prompt injection in integrated applications is broader than protected-attribute leakage from a model context. |
| schulhoff2023hackaprompt | Schulhoff et al., “Ignore This Title and HackAPrompt,” EMNLP 2023 | Collects more than 600K adversarial prompts and develops an ontology of prompt-hacking strategies. | Supports diverse attack taxonomies and motivates testing multiple controlled adversarial formulations. | Competition prompts optimize prompt-hacking success, not specifically privacy leakage or paired privacy-utility effects. |
| chao2024jailbreakbench | Chao et al., “JailbreakBench,” 2024 | Argues jailbreak evaluation needs standardized threat models, prompts, chat templates, scoring, cost accounting, and reproducible artifacts. | Closely aligns with ShadowLeak’s emphasis on fixed manifests, model provenance, reproducible prompts, and comparable evaluation. | JailbreakBench evaluates harmful-content refusal/robustness, not protected-attribute privacy leakage. |
| souly2024strongreject | Souly et al., “A StrongREJECT for Empty Jailbreaks,” NeurIPS 2024 Datasets and Benchmarks | Shows common jailbreak metrics can overstate attack success and introduces an evaluator that better agrees with human judgments. | Strong motivation for independent human gold labels and for avoiding “anything except refusal = success” style proxies. | StrongREJECT evaluates harmful assistance quality; ShadowLeak evaluates protected-attribute disclosure and benign utility. |
| wang2024donotanswer | Wang et al., “Do-Not-Answer: Evaluating Safeguards in LLMs,” Findings of EACL 2024 | Provides a curated safety dataset and evaluates safeguards using both model responses and automated classifiers. | Useful precedent for structured safeguard evaluation and independent benchmark datasets. | Its instructions are intentionally unsafe; ShadowLeak additionally requires benign controls and privacy-specific labels. |
| huang2024trustllm | Huang et al., “TrustLLM: Trustworthiness in Large Language Models,” ICML 2024 | Evaluates multiple trustworthiness dimensions, including privacy, safety, robustness, and exaggerated safety/over-refusal. | Supports reporting trustworthiness as multidimensional and motivates measuring over-refusal rather than maximizing blocking alone. | TrustLLM is broad; ShadowLeak narrows to a paired privacy-defense experiment with a pre-specified causal comparison. |

## C. Human annotation and evaluation reliability

| Key | Source | What the source establishes | Relevance to ShadowLeak | Boundary / caution |
|---|---|---|---|---|
| artstein2008agreement | Artstein & Poesio, “Inter-Coder Agreement for Computational Linguistics,” Computational Linguistics 2008 | Surveys agreement coefficients, including Cohen’s kappa, and their assumptions for annotation tasks. | Supports reporting both raw agreement and chance-corrected agreement before adjudication. | Kappa is a reliability indicator, not proof that the annotation construct is valid. |
| leonardelli2021disagreement | Leonardelli et al., “Agreeing to Disagree,” EMNLP 2021 | Shows annotator disagreement can carry meaningful information and that filtering to only high-agreement items changes model evaluation. | Supports preserving disagreement counts and adjudication records rather than treating disagreement as mere annotation noise. | Offensive-language subjectivity differs from privacy leakage, where the rubric aims for a more operational disclosure judgment. |
| howcroft2020evaluation | Howcroft et al., “Twenty Years of Confusion in Human Evaluation,” INLG 2020 | Documents inconsistent human-evaluation terminology and reporting in NLG and recommends more standardized evaluation documentation. | Supports ShadowLeak’s explicit annotation rubric, named utility dimensions, and fixed reporting structure. | The paper concerns NLG evaluation broadly, not privacy-specific annotation. |

## D. Documentation, accountability, and governance

| Key | Source | What the source establishes | Relevance to ShadowLeak | Boundary / caution |
|---|---|---|---|---|
| mitchell2019modelcards | Mitchell et al., “Model Cards for Model Reporting,” FAT* 2019 | Proposes standardized model documentation including intended use, evaluation procedures, and performance across relevant conditions. | Supports evaluation cards, explicit scope, model revision documentation, and subgroup reporting. | A model card is a documentation mechanism, not a safety certification. |
| gebru2021datasheets | Gebru et al., “Datasheets for Datasets,” CACM 2021 | Proposes structured documentation of dataset motivation, composition, collection, and recommended uses. | Supports documenting the synthetic benchmark, generation process, intended use, and limits. | Dataset documentation does not itself establish external validity. |
| raji2020auditing | Raji et al., “Closing the AI Accountability Gap,” FAccT 2020 | Proposes an end-to-end internal algorithmic-auditing framework in which evaluation artifacts feed organizational accountability. | Strong conceptual precedent for treating evaluation as an evidence process rather than a one-off benchmark score. | ShadowLeak is not an organizational audit and should not imply independent certification. |
| nist2023airmf | NIST, “Artificial Intelligence Risk Management Framework (AI RMF 1.0),” 2023 | Frames AI risk management through Govern, Map, Measure, and Manage and emphasizes documented, repeatable evaluation and trade-off analysis. | Supports ShadowLeak’s emphasis on documented TEVV, uncertainty, privacy-risk measurement, and traceable decision inputs. | AI RMF is voluntary and non-sector-specific; it does not supply ShadowLeak’s illustrative profile thresholds. |
| nist2024genai | NIST, “Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile,” 2024 | Extends AI RMF guidance to generative AI risks and organizational risk management. | Provides current governance context for documenting generative-AI risk evaluations and limitations. | It does not validate any particular GuardShield threshold or certify a deployment. |
| staufer2025auditcards | Staufer et al., “Audit Cards: Contextualizing AI Evaluations,” 2025 | Argues that technically rigorous evaluations require contextual reporting about scope, process integrity, access, and review mechanisms. | Closely matches ShadowLeak’s artifact provenance, evidence-class labels, and reporting freeze. | Emerging preprint literature; useful framing, not a binding standard. |

## E. Statistical and decision-analysis foundations

| Key | Source | What the source establishes | Relevance to ShadowLeak | Boundary / caution |
|---|---|---|---|---|
| holm1979 | Holm, “A Simple Sequentially Rejective Multiple Test Procedure,” Scandinavian Journal of Statistics 1979 | Introduces the sequentially rejective family-wise error procedure now commonly called Holm correction. | Direct basis for the pre-specified attack-family multiplicity adjustment. | Multiplicity correction does not rescue post-hoc hypothesis families that were not pre-specified. |
| ficiu2023tradeoff | Ficiu, Lawrence & Paleyes, “Automated discovery of trade-off between utility, privacy and fairness in machine learning models,” 2023 | Frames privacy, utility, and fairness as a multi-objective deployment trade-off rather than a single metric. | Supports presenting privacy and utility jointly and examining preference-sensitive decision regions. | This is general ML work and does not justify ShadowLeak’s economic weights as welfare estimates or prices. |

## Positioning synthesis

The literature supports five premises that ShadowLeak can safely build on:

1. language models can disclose sensitive or memorized text under adversarial querying;
2. adversarial evaluations are highly sensitive to benchmark construction and scoring choices;
3. automated success proxies can disagree with human judgment;
4. trustworthy-AI evaluation requires explicit scope, documentation, and uncertainty;
5. privacy improvements can conflict with utility and therefore should not be interpreted in isolation.

The literature **does not** directly establish ShadowLeak’s primary empirical
claim. Whether `guardshield-v1` reduces adjudicated protected-attribute leakage
on the frozen primary model is an empirical question reserved for the
confirmatory study.

## Sources checked

- Carlini et al. 2021: https://www.usenix.org/conference/usenixsecurity21/technical-sessions
- Carlini et al. 2023: https://openreview.net/forum?id=TatRHT_1cK
- Nasr et al. 2023: https://arxiv.org/abs/2311.17035
- Liu et al. 2023: https://arxiv.org/abs/2310.12815
- Schulhoff et al. 2023: https://aclanthology.org/2023.emnlp-main.302/
- Chao et al. 2024: https://arxiv.org/abs/2404.01318
- Souly et al. 2024: https://arxiv.org/abs/2402.10260
- Wang et al. 2024: https://aclanthology.org/2024.findings-eacl.61/
- Huang et al. 2024: https://arxiv.org/abs/2401.05561
- Artstein & Poesio 2008: https://aclanthology.org/J08-4004/
- Leonardelli et al. 2021: https://aclanthology.org/2021.emnlp-main.822/
- Howcroft et al. 2020: https://aclanthology.org/2020.inlg-1.23/
- Mitchell et al. 2019: https://arxiv.org/abs/1810.03993
- Gebru et al. 2021: https://arxiv.org/abs/1803.09010
- Raji et al. 2020: https://arxiv.org/abs/2001.00973
- NIST AI RMF 1.0: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- NIST GenAI Profile: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- Staufer et al. 2025: https://arxiv.org/abs/2504.13839
- Holm 1979: https://www.jstor.org/stable/4615733
- Ficiu et al. 2023: https://arxiv.org/abs/2311.15691
