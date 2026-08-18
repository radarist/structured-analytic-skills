---
name: Survey Research
category: research-method
origin: social-survey tradition (early 20th c.); sampling theory (Neyman, 1934); codified questionnaire design: Don Dillman's Tailored Design Method (1978 onward)
agent_suitability: Medium
tags: [survey, questionnaire, sampling, likert, validity, response-bias, quantitative]
related: [../research-methods/mixed-methods.md, ../research-methods/experimental-design.md, ../research-methods/systematic-literature-review.md, ../agent-playbook.md]
---

# Survey Research

> **Essence:** Systematically collect standardized self-report data from a sample to describe, compare, or explain characteristics of a population — where rigor lives in question wording, sampling, and response-rate honesty, not in the statistics.

## Overview

Surveys are the workhorse of descriptive and correlational social research: attitudes, behaviors, intentions, demographics — measured the same way across many respondents so results can be aggregated and (with probability sampling) generalized to a population. The method's apparent ease is its trap: anyone can write questions; almost no one writes them well, and survey methodology research has shown for decades that **question wording, order, scale format, and response options measurably change answers** (Schwarz's work on context effects; Krosnick on satisficing). A survey is a measurement instrument, and instruments are validated, not improvised.

The three pillars of rigor. **Measurement**: write items people can understand identically (single-barreled, concrete, balanced); choose response formats deliberately (Likert agreement scales, behavior frequencies with real anchors); pilot with cognitive interviews (ask respondents to think aloud — you will discover your questions don't mean what you think); establish reliability (Cronbach's alpha for multi-item scales) and validity (does it measure the construct?). **Sampling**: define the population; get a sampling frame; draw probability samples where generalization is claimed (random/stratified/cluster), size for needed precision, and *report the response rate with an honest nonresponse analysis* (who didn't answer, and does it bias results?). **Administration**: Dillman's Tailored Design — multiple contacts, personalized communication, trust-building — remains the response-rate bible across mail, web, and mixed modes; mode effects are real (people answer differently by web vs phone vs paper).

Standard designs: cross-sectional (one point in time — description, comparison, correlation), longitudinal/panel (change over time), and surveys embedded as the quantitative arm of [mixed-methods.md](mixed-methods.md) designs. The method's endemic diseases: low response rates, satisficing respondents (straight-lining, speeding), leading questions, sampling-frame fantasy (surveying who's reachable, claiming who's relevant), and — in the agent era — the seductive shortcut of **synthetic respondents** (see Agent Adaptation for the honest position).

## Origin & History

- **Early 20th c.:** social surveys (Booth's London poverty studies; 1930s polling — Gallup's quota sampling success vs *Literary Digest*'s catastrophic 1936 non-representative poll, the founding cautionary tale).
- **1934:** Jerzy Neyman's sampling theory — the statistical foundation of probability sampling and confidence intervals.
- **1978:** Don Dillman, *Mail and Telephone Surveys: The Total Design Method* — administration science; updated as *Internet, Phone, Mail, and Mixed-Mode Surveys: The Tailored Design Method* (2000/2014).
- **1990s–2000s:** cognitive-methods revolution (Willis's *Cognitive Interviewing*); satisficing theory (Krosnick); web surveys and online panels become dominant; paradata and nonresponse-bias methodology matures (Groves).
- **2010s–present:** probability panel decline, nonprobability panels + weighting/calibration debates, mobile-first design, and LLM-based "synthetic sample" proposals (contested — see Agent Adaptation).

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Population / sampling frame | Who you want to describe vs the list you can actually draw from — the gap is bias. |
| Probability sampling | Random selection with known inclusion probabilities (simple/stratified/cluster) — the basis of generalization. |
| Nonprobability sampling | Convenience/quota/panel opt-in — usable with care, generalization argued not assumed. |
| Construct → item | What you mean to measure vs the actual question; items operationalize constructs. |
| Likert scale | Multi-point agreement format; multi-item scales aggregated into a score. |
| Reliability (alpha) | Internal consistency of a multi-item scale (≥ .70 conventional floor). |
| Validity | Content/construct/criterion: does the instrument measure the construct? |
| Cognitive interviewing | Think-aloud pretesting of items — the cheapest validity investment. |
| Satisficing | Respondents optimizing effort, not accuracy (straight-lining, first-acceptable-answer). |
| Nonresponse bias | Systematic difference between responders and nonresponders. |
| Weighting/calibration | Post-stratification to population margins — mitigates, doesn't cure, frame problems. |

## When to Use / When Not to Use

**Use when:**
- You need population-level description or comparison of attitudes/behaviors/characteristics.
- Constructs are self-reportable and operationalizable into items.
- Sample size and frame support the generalization you want to claim.
- As the quantitative arm of mixed designs or pre/post measurement in interventions.

**Don't use when:**
- The phenomenon is behavior people can't or won't report accurately (observe, log, or measure instead — said-vs-done gap).
- You need causal attribution (survey correlations don't deliver it; see [experimental-design.md](experimental-design.md)).
- The accessible frame has no defensible relationship to the population.
- The "survey" is 40 improvised questions with no pilot — that's content generation, not measurement.

## Process & Steps

1. **Define constructs and population.** What exactly is measured, in whom; write research questions in measurable form. *Artifact: construct map + population definition.*
2. **Design the instrument.** Prefer validated existing scales (measurement libraries); write new items per the craft rules (single-barreled, concrete, mutually exclusive exhaustive options, balanced scales); order to manage context effects; keep it short. *Artifact: draft questionnaire.*
3. **Pilot.** Cognitive interviews (5–15 respondents, think-aloud), then a pilot run for timing, reliability (alpha), and item performance. Revise. *Artifact: pilot report + revised instrument.*
4. **Sample.** Define frame; choose design (probability where possible); compute size for precision/power; document everything. *Artifact: sampling plan.*
5. **Administer.** Tailored Design: pre-notice, invitation, reminders (2–4 contacts), salience, trust, incentives where appropriate; monitor paradata (speeders, straight-liners) in real time. *Artifact: fieldwork log + raw data.*
6. **Clean and weight.** Data-quality screens (attention checks, speeding, straight-lining); nonresponse analysis; weighting/calibration if used, documented. *Artifact: analysis dataset + quality report.*
7. **Analyze and report.** Descriptives with uncertainty; scale reliabilities; subgroup comparisons with corrections; report response rate, mode, dates, question wording (AAPOR-style transparency). *Artifact: the report.*

## Techniques, Tools & Deliverables

- Validated scale libraries (use them before inventing items).
- Cognitive interviewing protocols (think-aloud + probes).
- Dillman's contact sequences; attention-check items; paradata quality dashboards.
- Platforms (Qualtrics, LimeSurvey, panels); R/survey packages for weighting and design-based analysis.
- **Deliverables:** instrument + codebook, pilot report, sampling + fieldwork documentation, weighted dataset, report with reliability/validity and response-rate transparency.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Standardized measurement at scale | Self-report: said-vs-done and social-desirability gaps |
| Probability sampling enables generalization | Nonresponse and frame problems increasingly severe |
| Efficient cost per case (web) | Satisficing degrades data silently; quality screens essential |
| Comparable across groups/time (repeated instruments) | Correlational; causal claims overreach |
| Huge methodological literature and validated instruments | Question-craft failures are invisible until piloted (or published and wrong) |

## Worked Examples & Case Studies

- **1936 Literary Digest poll:** 2+ million responses, wrong winner — the canonical lesson that sample size cannot fix sampling bias (Gallup's smaller quota sample called Roosevelt).
- **General Social Survey (GSS, since 1972):** the model of repeated, documented, generalizable social measurement.
- **Dillman's tailored-design field experiments:** decades of randomized administration experiments showing contact design, salience, and incentives moving response rates — administration as science.
- **Schwarz & colleagues' context-effect studies:** tiny wording/order changes (e.g., frequency scales) producing large response shifts — the craft's empirical basis.

## Variants & Related Methodologies

- **Cross-sectional vs panel/longitudinal surveys.**
- **Conjoint/max-diff** — trade-off measurement variants.
- **Experience sampling (ESM)** — in-the-moment micro-surveys.
- **Delphi** — expert-judgment iterative variant ([delphi-method.md](../foresight/delphi-method.md)).
- Related: [mixed-methods.md](mixed-methods.md) (survey as quant arm), [experimental-design.md](experimental-design.md) (causal alternative), [grounded-theory.md](grounded-theory.md) (item discovery upstream).

## Agent Adaptation

### Suitability for agent execution

**Medium.** Agents are strong at instrument engineering: drafting items from constructs, auditing question craft (double-barrels, leading, scale balance), simulating cognitive interviews to catch interpretation failures, generating codebooks, monitoring paradata, and running cleaning/weighting pipelines in code. Field administration and respondent ethics remain human/platform work. One firm rule: **LLM-generated "synthetic respondents" are not survey data.** Agent panels can pilot instruments (do answers vary as intended? do items discriminate?) and rehearse analysis code, but presenting persona-generated answers as evidence about humans is fabrication with extra steps. Use agents to make real surveys better, not to replace respondents.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Facilitator (human) | Constructs, population, ethics, administration decisions, final claims. |
| Analyst | Instrument drafting from construct map; codebook; analysis pipeline in code. |
| Domain Expert (personas of target population) | Simulated cognitive interviewing: how would this population read each item? |
| Critic / Red Team | Question-craft audit (leading, double-barreled, scale balance, order effects); sampling-plan critique; over-claim audit on the report. |
| Scout | Find validated existing scales for the constructs; population statistics for weighting targets. |
| Verifier | Check scale provenance; recompute reliability/weights from data. |
| Synthesizer | Pilot report, fieldwork documentation, results report drafts. |

### Agent pipeline

1. Frame (human) → construct map + population/frame.
2. Instrument (Analyst + Scout's validated scales) → draft questionnaire; Critic craft audit; Domain Expert simulated cognitive read → revise; human pilots with real people.
3. Field (human/platform) → data + paradata; Analyst quality screens → `quality_report.md`.
4. Analyze (Analyst in code; Verifier recomputes) → weighted descriptives, reliabilities → `results/`.
5. Report (Synthesizer + Critic over-claim audit) → draft → human owns claims.

### Prompt templates

```text
SYSTEM: You are a survey-methodology Critic. Draft questionnaire: {{questionnaire}}. Constructs:
{{construct_map}}. Audit every item for: double-barreled wording, leading/loaded terms, assumed
knowledge, unbalanced scales, missing response options (or non-exhaustive overlaps), ambiguous
reference periods, social-desirability pressure, and order effects (what earlier item could
contaminate this one?). For each finding: the problem, why it biases, and a rewrite. Also flag
constructs measured by a single item that need multi-item scales. Be exhaustive — this is the
cheapest validity pass the project will get.
```

```text
SYSTEM: You are simulating a cognitive interview. Persona: {{respondent_persona}} (a member of
the survey's target population). For each item below, think ALOUD in character: what you think
the question is asking, what answer options you'd expect, any confusion or "it depends", and
your answer with reasoning. Then out-of-character: list every interpretation failure you found.
Items: {{items}}. NOTE: your answers are pilot feedback about item comprehensibility, NOT data.
```

```text
SYSTEM: You are the data-quality analyst. Survey dataset: {{dataset_description}} with paradata
{{paradata}}. In code: (1) flag speeders ({{threshold_rule}}), straight-liners, and failed
attention checks; (2) compute scale reliabilities (alpha) per construct; (3) compare sample
margins to population targets {{population_margins}} and propose post-stratification weights
(report effective sample size after weighting); (4) output the cleaning decisions table with
counts and justifications. All decisions reproducible from the script.
```

### Tools & data requirements

Survey platform + panel (human-run), code execution for psychometrics/weighting, retrieval for validated scales and population margins, document store for instruments/codebooks.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Improvised items, no craft audit | Critic pass missing | Mandatory item-by-item audit + simulated cognitive interviews |
| Synthetic respondents as "data" | Provenance check | Hard rule: persona answers = piloting only, never analysis data |
| Silent satisficing | Paradata screens | Speeding/straight-lining/attention-check flags in every dataset |
| Frame fantasy | Population vs frame table | Documented frame assessment; claims bounded to frame |
| Reliability theater (unreported alpha) | Verifier recompute | Psychometrics from data, in code, every scale |
| Over-generalized claims | Critic report audit | Claims must cite design (probability or not) and response rate |

### Human-in-the-loop checkpoints

1. Constructs, instrument sign-off, real cognitive piloting with humans.
2. Sampling design and administration.
3. Analysis interpretations and population claims.

### Inputs & outputs (chaining contract)

**Inputs:** constructs (often from [grounded-theory.md](grounded-theory.md)/[case-study-research.md](case-study-research.md) qual work), population/frame, validated scales.
**Outputs:** validated instrument, weighted dataset, descriptive/comparative findings — feeding [mixed-methods.md](mixed-methods.md) integration, [experimental-design.md](experimental-design.md) (measurement arm), and [evidence-appraisal.md](../scientific-methods/evidence-appraisal.md) contexts.

## References & Further Reading

- Dillman, D.A., Smyth, J.D. & Christian, L.M. (2014). *Internet, Phone, Mail, and Mixed-Mode Surveys: The Tailored Design Method* (4th ed.). Wiley.
- Groves, R.M. et al. (2009). *Survey Methodology* (2nd ed.). Wiley.
- Fowler, F.J. (2014). *Survey Research Methods* (5th ed.). Sage.
- Krosnick, J.A. (1991). "Response Strategies for Coping with the Cognitive Demands of Attitude Measures in Surveys." *Applied Cognitive Psychology*, 5.
- Schwarz, N. (1999). "Self-Reports: How the Questions Shape the Answers." *American Psychologist*, 54(2).
- Willis, G.B. (2005). *Cognitive Interviewing: A Tool for Improving Questionnaire Design.* Sage.
- AAPOR — *Standard Definitions* (response-rate reporting standards; aapor.org).
- Neyman, J. (1934). "On the Two Different Aspects of the Representative Method." *JRSS*, 97(4).
