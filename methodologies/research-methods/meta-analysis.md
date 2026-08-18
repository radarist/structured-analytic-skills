---
name: Meta-Analysis
category: research-method
origin: Gene V. Glass (1976); codified by Hedges & Olkin (1985) and the Cochrane tradition
agent_suitability: High
tags: [effect-size, pooling, heterogeneity, forest-plot, publication-bias, statistics, evidence-synthesis]
related: [../research-methods/systematic-literature-review.md, ../scientific-methods/evidence-appraisal.md, ../scientific-methods/reproducibility-open-science.md, ../agent-playbook.md]
---

# Meta-Analysis

> **Essence:** The statistical pooling of effect sizes across multiple studies of the same question, yielding a single best estimate of effect magnitude — plus an explicit account of how much and why the studies disagree.

## Overview

Individual studies are noisy: small samples, idiosyncratic contexts, and publication filters mean any single p-value is a weak instrument. Meta-analysis treats each study as a data point, converts each study's result to a common **effect size** (Cohen's d / Hedges' g for mean differences, odds ratios or risk ratios for binary outcomes, correlations), **weights studies** by precision (inverse variance), and computes a pooled estimate with a confidence interval. Done well, it answers not only "does it work, and how much?" but "how consistent is the effect?" — the second answer being as informative as the first.

The core judgment is the pooling model. **Fixed-effect** assumes one true effect that all studies estimate (differences are just sampling error). **Random-effects** assumes a *distribution* of true effects across contexts and estimates its mean and variance — almost always the honest choice in social/biomedical research. **Heterogeneity** is quantified (Cochran's Q test; **I²** = the percentage of variability due to real differences rather than chance, with rough guideposts of 25/50/75% for low/moderate/high); high heterogeneity demands investigation (subgroup analyses, meta-regression on moderators), not just pooling.

The method's dark side is the input pool: if published studies are a biased sample of all conducted studies, meta-analysis produces a precise estimate of a biased quantity. Hence the standard toolkit for **publication bias**: funnel plots (asymmetry suggests missing small negative studies), Egger's regression test, trim-and-fill adjustment, and p-curve/fail-safe-N approaches. And the modern corrective upstream: preregistration and registered reports (see [reproducibility-open-science.md](../scientific-methods/reproducibility-open-science.md)).

Meta-analysis is usually the statistical engine inside a [systematic-literature-review.md](systematic-literature-review.md); PRISMA governs the search, the meta-analysis governs the pooling. All computation belongs in code (R `metafor`/`meta`, Python, RevMan) — never in prose.

## Origin & History

- **1904:** Karl Pearson averages correlations across studies (typhoid inoculation) — the ur-meta-analysis.
- **1976:** Gene V. Glass coins "meta-analysis" in his presidential address to AERA, pooling psychotherapy outcome studies (Smith & Glass, 1977).
- **1985:** Hedges & Olkin, *Statistical Methods for Meta-Analysis* — the reference statistical treatment (inverse-variance weighting, Q, fixed/random effects).
- **1993:** Cochrane Collaboration institutionalizes meta-analysis in medicine; RevMan software.
- **1997–2005:** publication-bias methodology matures (Egger et al., 1997; Duval & Tweedie's trim-and-fill, 2000).
- **2010s:** replication crisis spotlights p-hacking's contamination of meta-analytic pools; p-curve (Simonsohn et al., 2014); registered reports and many-labs replications ([reproducibility-open-science.md](../scientific-methods/reproducibility-open-science.md)).

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Effect size | Standardized magnitude: Hedges' g / Cohen's d (continuous), OR/RR (binary), r (association). |
| Inverse-variance weighting | Precise studies count more; weight ∝ 1/SE². |
| Fixed-effect model | One true effect; only sampling error varies. |
| Random-effects model | True effects vary (τ² between-study variance); pooled estimate = mean of the distribution. |
| Cochran's Q | Test statistic for whether observed variability exceeds chance. |
| I² | Percentage of variability from real heterogeneity (25/50/75% ≈ low/moderate/high). |
| Forest plot | The standard visual: per-study estimates + CI, weights, and the pooled diamond. |
| Publication bias | Distortion because the published pool isn't all studies. |
| Funnel plot | Effect size vs precision; asymmetry suggests missing studies. |
| Egger's test | Regression test for funnel asymmetry. |
| Trim-and-fill | Imputes "missing" studies to estimate an adjusted pooled effect. |
| Subgroup analysis / meta-regression | Explaining heterogeneity via moderators. |

## When to Use / When Not to Use

**Use when:**
- Multiple commensurable studies address one question (same outcome construct, comparable designs).
- You need a defensible magnitude estimate with precision, not just "significant or not".
- Understanding consistency/moderation matters as much as the mean effect.
- As the synthesis stage of an SLR.

**Don't use when:**
- Studies are too heterogeneous in design/outcome to pool honestly ("apples and oranges" — do narrative/thematic synthesis instead).
- The evidence base is tiny or uniformly low quality (a pooled estimate of garbage is still garbage; say so).
- You haven't assessed publication bias (an unaudited pooled estimate is irresponsible).
- The question is about mechanisms or contexts (qualitative/realist synthesis instead).

## Process & Steps

1. **Define the effect and eligibility** (inherits the SLR protocol: PICO, outcome metric, design requirements). *Artifact: analysis plan — pre-specify model, moderators, bias tests.*
2. **Extract effect data** per study: effect sizes or the raw statistics to compute them (means/SDs, event counts, r), plus moderators. *Artifact: extraction table (from the SLR stage).*
3. **Compute/convert effect sizes** and variances on a common metric. *Artifact: analysis dataset (code-generated).*
4. **Choose the model**: random-effects by default; justify. *Artifact: model decision note.*
5. **Pool and visualize**: pooled estimate + CI; forest plot. *Artifact: forest plot + pooled estimate.*
6. **Assess heterogeneity**: Q, I², τ²; if substantial, subgroup analyses and meta-regression on pre-specified moderators. *Artifact: heterogeneity report.*
7. **Assess publication bias**: funnel plot, Egger's, trim-and-fill, sensitivity analyses. *Artifact: bias report.*
8. **Robustness and reporting**: leave-one-out sensitivity; report per PRISMA with limitations. *Artifact: the synthesis section.*

## Techniques, Tools & Deliverables

- R: `metafor` (Viechtbauer) / `meta`; Python: custom or `statsmodels`-based; RevMan for Cochrane-style reviews.
- Standardized mean differences with small-sample correction (Hedges' g); log-OR for binary.
- Influence/leave-one-out diagnostics; Baujat plots for heterogeneity contributors.
- p-curve for evidential value (Simonsohn et al.).
- **Deliverables:** analysis dataset + scripts, forest/funnel plots, pooled estimates with heterogeneity and bias assessments, limitations.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Precision no single study can reach | Precise estimate of a biased pool is still biased (GIGO) |
| Makes disagreement measurable (I², τ²) and investigable | "Apples and oranges" pooling can manufacture false coherence |
| Standardized, auditable, reproducible | Publication bias correction methods are imperfect bandages |
| Moderators turn heterogeneity into knowledge | Observational inputs carry confounding into the pool |
| Mature tooling and reporting standards | Statistical choices (model, metric, outliers) are researcher degrees of freedom — pre-specify |

## Worked Examples & Case Studies

- **Smith & Glass (1977):** meta-analysis of psychotherapy outcome studies (~375 studies) — founded the field's modern use and triggered decades of methodological refinement.
- **Cochrane reviews:** e.g., meta-analyses establishing effects of interventions (steroids in preterm labor — the Cochrane logo's forest plot) where individual trials were equivocal.
- **Many Labs / Registered Replication Reports:** large-scale replications pooled meta-analytically (e.g., Open Science Collaboration 2015 context) showing original literatures' inflated effects — the cautionary case.

## Variants & Related Methodologies

- **Individual participant data (IPD) meta-analysis** — pools raw data, not summaries; the gold standard where feasible.
- **Network meta-analysis** — compares multiple treatments via direct+indirect evidence.
- **Bayesian meta-analysis** — priors, full posterior for τ²; natural for small literatures.
- **Meta-synthesis / thematic synthesis** — the qualitative analog (no pooling of numbers).
- Agent skill: [meta-analysis](../../skills/meta-analysis/SKILL.md) — one-page executable form of this methodology (pooling, heterogeneity, Egger's test, with a companion script for the arithmetic).
- Related: [systematic-literature-review.md](systematic-literature-review.md) (the host protocol), [evidence-appraisal.md](../scientific-methods/evidence-appraisal.md) (GRADE on the result), [experimental-design.md](experimental-design.md) (what's being pooled).

## Agent Adaptation

### Suitability for agent execution

**High — with code execution mandatory.** Extraction of effect statistics, metric conversion, pooling, heterogeneity/bias batteries, and plotting are exactly code-bound tasks agents orchestrate well; all arithmetic must run in code, and every extracted number must be quote-anchored to its source (the single biggest agent risk is a fluent but wrong extraction). Human judgment remains essential for: commensurability decisions (is pooling these studies honest?), moderator selection, and interpretation of heterogeneity/bias findings.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Analyst (extraction) | Pull effect statistics + moderators from each study, quote-anchored. |
| Verifier | Confirm every extracted number against source text; check conversions. |
| Code executor (tool) | All computation: conversions, pooling, Q/I²/τ², funnel/Egger/trim-and-fill, plots. |
| Domain Expert (persona) | Judge commensurability, model choice, moderator set; interpret findings. |
| Critic / Red Team | Attack pooling decisions, outlier handling, bias-test interpretation; run alternative specifications. |
| Synthesizer | Write the synthesis with forest/funnel figures and limitations. |
| Facilitator (human) | Approves protocol, adjudicates commensurability, owns conclusions. |

### Agent pipeline

1. Frame (human) → effect definition, eligibility, pre-specified analysis plan.
2. Extract (Analyst, quote-anchored) → `effects_raw.jsonl`; Verifier audit → `effects_verified.csv`.
3. Compute (code) → common metric, model fit, heterogeneity, bias tests, plots → `results/`.
4. Stress-test (Critic) → alternative model/metric/outlier specifications; sensitivity deltas reported.
5. Interpret (Domain Expert + Synthesizer) → synthesis narrative + limitations → human sign-off.

### Prompt templates

```text
SYSTEM: You are the extraction analyst for a meta-analysis. Study text: {{paper}}. Extract:
outcome measure used, sample sizes per group, means/SDs (or event counts, or r, as applicable),
the exact statistic reported, plus moderators: {{moderator_list}}. For EVERY number, attach the
supporting quote (<= 20 words) from the text. If a needed statistic is not reported, mark
NOT-REPORTED — never estimate silently. Output JSON with quote fields per datum.
```

```text
SYSTEM: You are the Critic reviewing this meta-analysis specification and results:
{{analysis_summary}}. Challenge: (1) commensurability — name the study pair least deserving of
being pooled and why; (2) model choice — rerun interpretation under the alternative model and
report how the conclusion changes; (3) outliers/influence — which single study moves the pooled
estimate most, and is its inclusion defensible?; (4) publication bias — given funnel/Egger
results, state in one sentence how much trust the pooled estimate deserves. Be specific; no
generic caveats.
```

### Tools & data requirements

Code execution with R/Python statistics packages (mandatory), PDF text extraction, structured store for extractions, plotting; upstream SLR pipeline ([systematic-literature-review.md](systematic-literature-review.md)) for the study pool.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Fabricated/mis-copied statistics | Verifier quote audit | No unanchored numbers enter the dataset |
| LLM arithmetic | No code artifact | All computation scripted and saved |
| Specification shopping (agent picks convenient model) | Critic alternative-specification pass | Pre-specified plan; deviations reported |
| Pooling incommensurable studies | Domain Expert commensurability review | Documented inclusion judgment per study |
| Ignoring publication bias | Bias section missing | Mandatory funnel/Egger/trim-and-fill block in output |
| Over-claiming from weak pools | GRADE-style confidence note missing | End every synthesis with a confidence statement |

### Human-in-the-loop checkpoints

1. Analysis plan (model, moderators, bias tests) — pre-specified.
2. Commensurability adjudications.
3. Interpretation and claims (what magnitude means practically).

### Inputs & outputs (chaining contract)

**Inputs:** eligible study set + extractions (from [systematic-literature-review.md](systematic-literature-review.md)); pre-specified analysis plan.
**Outputs:** pooled estimate + CI, heterogeneity and publication-bias assessments, plots, confidence statement — feeding [evidence-appraisal.md](../scientific-methods/evidence-appraisal.md) (GRADE), guidelines, and decision documents.

## References & Further Reading

- Glass, G.V. (1976). "Primary, Secondary, and Meta-Analysis of Research." *Educational Researcher*, 5(10).
- Hedges, L.V. & Olkin, I. (1985). *Statistical Methods for Meta-Analysis.* Academic Press.
- Borenstein, M., Hedges, L.V., Higgins, J.P.T. & Rothstein, H.R. (2009). *Introduction to Meta-Analysis.* Wiley.
- Egger, M., Davey Smith, G., Schneider, M. & Minder, C. (1997). "Bias in Meta-Analysis Detected by a Simple, Graphical Test." *BMJ*, 315.
- Duval, S. & Tweedie, R. (2000). "Trim and Fill: A Simple Funnel-Plot-Based Method of Testing and Adjusting for Publication Bias in Meta-Analysis." *Biometrics*, 56(2).
- Higgins, J.P.T. & Thompson, S.G. (2002). "Quantifying Heterogeneity in a Meta-Analysis." *Statistics in Medicine*, 21. (I²)
- Simonsohn, U., Nelson, L.D. & Simmons, J.P. (2014). "P-Curve: A Key to the File Drawer." *Journal of Experimental Psychology: General*, 143(2).
- Viechtbauer, W. (2010). "Conducting Meta-Analyses in R with the metafor Package." *Journal of Statistical Software*, 36(3).
