---
name: Evidence Appraisal (Hierarchies, GRADE & Critical Appraisal)
category: scientific-method
origin: evidence-based medicine (McMaster group — Sackett, Guyatt; 1980s–90s); GRADE working group (2000s); Bradford Hill criteria (1965)
agent_suitability: High
tags: [evidence-hierarchy, grade, critical-appraisal, casp, bradford-hill, risk-of-bias, certainty]
related: [../research-methods/systematic-literature-review.md, ../research-methods/meta-analysis.md, ../scientific-methods/reproducibility-open-science.md, ../scientific-methods/bayesian-evidence-updating.md, ../agent-playbook.md, ../../skills/evidence-appraisal/SKILL.md]
---

# Evidence Appraisal (Hierarchies, GRADE & Critical Appraisal)

> **Essence:** Not all evidence deserves equal weight — appraise each source's methodological quality and each conclusion's certainty explicitly, so decisions rest on graded confidence rather than citation counts.

## Overview

Evidence appraisal is the discipline of asking, before any "studies show X" is believed: *how good is this evidence, really?* Its classic instrument is the **evidence hierarchy** (evidence-based medicine, 1990s): at the top, systematic reviews/meta-analyses of randomized trials; then individual RCTs; then cohort studies, case-control studies, case series/reports; at the base, mechanistic reasoning and expert opinion. The hierarchy encodes one insight — designs differ in their vulnerability to bias — and its honest use requires knowing its limits: it ranks *average* resistance to bias for *therapy questions*, and it is the wrong frame for questions of harm, diagnosis, prognosis, mechanism, or meaning (a well-done cohort study can outrank a badly done RCT; qualitative questions need qualitative evidence).

**Critical appraisal** operationalizes the hierarchy per study: structured checklists (the CASP family — RCT, cohort, case-control, qualitative, diagnostic, economic) that walk through validity (was bias controlled? randomization, blinding, follow-up, confounding), results (size, precision), and applicability (does it transfer to my context?). For causation from non-randomized evidence, the **Bradford Hill criteria** (1965 — viewpoints, strictly, not a checklist verdict) remain the reasoning scaffold: strength of association, consistency across studies, specificity, temporality (cause precedes effect — the only absolute), biological gradient (dose-response), plausibility, coherence, experiment, analogy.

**GRADE** (Grading of Recommendations Assessment, Development and Evaluation, 2000s) extends appraisal from single studies to *bodies of evidence*, rating certainty per outcome: start high (randomized) or low (observational), then **rate down** for risk of bias, inconsistency, indirectness, imprecision, or publication bias — and **rate up** (observational only) for large effects, dose-response, or when plausible confounders would work *against* the observed effect. Output: high/moderate/low/very-low certainty per outcome, and (for guidelines) strong or conditional recommendations. GRADE's lesson for any evidence consumer: certainty is a *judged property of the whole evidence base for one outcome*, not an adjective attached to one exciting paper. The **Sagan standard** — "extraordinary claims require extraordinary evidence" — is the same idea from the other direction: prior implausibility raises the evidential bar (connecting appraisal to [bayesian-evidence-updating.md](bayesian-evidence-updating.md): quality and quantity of evidence set the likelihood ratio; the prior sets how much is needed).

## Origin & History

- **1965:** Austin Bradford Hill, "The Environment and Disease: Association or Causation?" (*Proceedings of the Royal Society of Medicine*) — the nine viewpoints.
- **1981:** Canadian Task Force on the Periodic Health Examination — early formal evidence levels for recommendations.
- **1990s:** evidence-based medicine movement (McMaster: David Sackett, Gordon Guyatt and colleagues) — hierarchies, critical-appraisal teaching (JAMA "Users' Guides to the Medical Literature" series).
- **1993–present:** Oxford Centre for Evidence-Based Medicine (OCEBM) levels; CASP checklists (Critical Appraisal Skills Programme, Oxford, 1990s) become the standard teaching tools.
- **2000s:** GRADE working group formed; GRADE adopted by Cochrane, WHO and 100+ organizations — now the default for guideline certainty ratings.
- **2010s–present:** ROBINS-I for non-randomized studies' risk of bias; replication-crisis awareness folds replication status into appraisal (see [reproducibility-open-science.md](reproducibility-open-science.md)).

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Evidence hierarchy | Design ranking by bias resistance (SR/MA > RCT > cohort > case-control > case series > mechanistic/opinion). |
| Critical appraisal | Structured per-study validity/results/applicability assessment (CASP etc.). |
| Risk of bias | Systematic-error assessment per domain (randomization, blinding, attrition, confounding, selective reporting). |
| GRADE certainty | High/moderate/low/very-low confidence in an effect estimate for one outcome, judged across the evidence body. |
| Rate-down factors | Risk of bias, inconsistency, indirectness, imprecision, publication bias. |
| Rate-up factors | Large effect, dose-response, opposing plausible confounding. |
| Bradford Hill viewpoints | Strength, consistency, specificity, temporality, gradient, plausibility, coherence, experiment, analogy. |
| Indirectness | Evidence from a different population/intervention/comparator/outcome than your question. |
| Sagan standard | Extraordinary claims require extraordinary evidence (prior-weighted appraisal). |
| Users' Guides triad | Validity → results → applicability, in that order. |

## When to Use / When Not to Use

**Use when:**
- Consuming or synthesizing evidence for decisions (guidelines, policy, product claims, "what does the literature say").
- Grading certainty before relying on findings (with [reproducibility-open-science.md](reproducibility-open-science.md) status).
- Comparing conflicting studies (appraisal usually reveals why they differ).
- Communicating evidence honestly (certainty language, not "proven").

**Don't use when:**
- The hierarchy is applied as a mechanical ranking across question types (harm, diagnosis, mechanism, meaning need their own frames).
- Checklist scores replace judgment (appraisal informs judgment; it doesn't compute truth).
- Used to dismiss everything ("no RCT, no evidence") — GRADE exists precisely because decisions must be made on imperfect evidence, graded honestly.
- A single study is being graded when the question is about the *body* of evidence (use GRADE over the synthesis).

## Process & Steps

1. **Frame the question and the outcome(s).** Appraisal is per question, per outcome — "does X work?" is unappraisable as stated. *Artifact: PICO-style question + outcome list.*
2. **Assemble the evidence body** (from [systematic-literature-review.md](../research-methods/systematic-literature-review.md) where possible; otherwise documented search). *Artifact: study set.*
3. **Appraise each study**: design identification → appropriate checklist/risk-of-bias tool → validity findings → results (effect, precision) → applicability/indirectness notes. *Artifact: per-study appraisal table.*
4. **Grade the body per outcome (GRADE)**: start rating by design; apply rate-down/rate-up factors with reasons; assign certainty. *Artifact: evidence profile (outcome × certainty with rationale).*
5. **Reason about causation where needed**: Bradford Hill viewpoints as an argued case, not a tally. *Artifact: causation memo.*
6. **Communicate with certainty language**: "moderate certainty that X reduces Y (probably reduces)"; name what would raise/lower certainty. *Artifact: summary-of-findings statement.*
7. **Set the monitoring trigger**: what new evidence (trials in progress, replications) would change the grade. *Artifact: surveillance note.*

## Techniques, Tools & Deliverables

- CASP checklists (per design); Cochrane RoB 2 (RCTs); ROBINS-I (non-randomized); Jadad (legacy).
- GRADE evidence profiles & Summary-of-Findings tables (GRADEpro software).
- OCEBM levels table for quick design placement.
- Bradford Hill viewpoint worksheet (argued prose per viewpoint).
- **Deliverables:** appraisal tables, evidence profiles with certainty ratings, causation memos, summary-of-findings statements, surveillance notes.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Makes confidence explicit and argued, not implied | Judgment-heavy: GRADE ratings legitimately differ between careful teams |
| Per-outcome granularity exposes "works for what?" gaps | Hierarchy misuse (mechanical ranking, wrong question types) is endemic |
| Connects methods to decisions (certainty → recommendation strength) | Checklist compliance theater (boxes ticked, thinking skipped) |
| Standardized language (moderate certainty = probably) | Publication bias and replication status complicate every rating |
| Auditable: factors and reasons are recorded | Slow done properly; shortcuts destroy the point |

The known misuse is the summary-judgment shortcut: collapsing five domains into one vibe rating. The system only works because the *reasons* per factor are written down — an unexplained "moderate certainty" is astrology with vocabulary. Publication bias is the structural caveat: even a perfectly graded body of published evidence can be systematically wrong because the unpublished half is missing (the replication crisis made this concrete in psychology). And GRADE-style language helps only if readers actually calibrate to it — "moderate certainty = probably" needs to be said aloud, or stakeholders read "moderate" as "weak." Done properly it is slow; that is the price of an audit trail, and the shortcut versions are strictly worse than no grading.

## Worked Examples & Case Studies

- **WHO and Cochrane guidelines:** GRADE evidence profiles are standard in modern clinical/public-health guidelines (e.g., COVID-19 living guidelines with per-outcome certainty).
- **Smoking–lung cancer causation (1950s–60s):** the Bradford Hill viewpoints' founding application context — consistent, strong, gradient-bearing cohort/case-control evidence carried causation without RCTs.
- **Hormone-replacement therapy reversal (2002):** observational evidence (HERS/nurses' studies) suggested cardiovascular benefit; the Women's Health Initiative RCT found harm — the canonical lesson in design-ranking and confounding (healthy-user bias).
- **CASP in education:** critical-appraisal workshops using CASP checklists are the global standard for teaching evidence consumption in health professions.

## Variants & Related Methodologies

- **OCEBM levels** — quick design placement; **GRADE** — body-of-evidence certainty.
- **Jadad scale** (RCT quality, legacy); **Newcastle–Ottawa** (observational); **QUADAS-2** (diagnostic).
- **SBAR/structured evidence summaries** for policy contexts.
- **Realist appraisal** (what works for whom — context-mechanism-outcome).
- Agent skill: [evidence-appraisal](../../skills/evidence-appraisal/SKILL.md) — one-page executable form of this methodology.
- Skill counterpart (bias grading): [skills/assess-study-bias](../../skills/assess-study-bias/SKILL.md) — the RoB-2 per-study pass that feeds the GRADE-style body-of-evidence judgment.
- Related: [systematic-literature-review.md](../research-methods/systematic-literature-review.md) (body assembly), [meta-analysis.md](../research-methods/meta-analysis.md) (pooled estimates to grade), [reproducibility-open-science.md](reproducibility-open-science.md) (replication status), [bayesian-evidence-updating.md](bayesian-evidence-updating.md) (certainty ↔ posterior confidence).

## Agent Adaptation

### Suitability for agent execution

**High.** Appraisal is structured rule-application over documents — checklists, risk-of-bias domains, GRADE factors — exactly what disciplined agent pipelines do consistently (and what tired humans do inconsistently). Agents never skip the "applicability" section and never inflate a study because it's famous. The human-essential parts: applicability judgments to *this* decision context, final certainty calls, and recommendation strength. The characteristic agent risk is **checklist theater without text-grounding** — counter by requiring every appraisal judgment to quote the passage that justifies it (e.g., the randomization sentence), with a Verifier confirming quotes.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Analyst | Per-study appraisal against the right checklist/tool, every judgment quote-anchored. |
| Verifier | Confirm appraisal quotes exist and support the judgments. |
| Domain Expert (personas) | Indirectness/applicability assessments for the decision context; GRADE rate-up/down debates. |
| Critic / Red Team | Challenge certainty ratings (too generous? too harsh?); checklist-theater detection; alternative-rating arguments. |
| Synthesizer | Evidence profiles, summary-of-findings statements, surveillance notes. |
| Facilitator (human) | Final certainty and recommendation decisions. |

### Agent pipeline

1. Frame (human) → PICO + outcomes + decision context.
2. Appraise (Analyst per study, quote-anchored) → `appraisals.jsonl`; Verifier checks.
3. Grade (Domain Experts + Synthesizer) → draft evidence profiles; Critic challenges; contested factors flagged.
4. Decide (human) → final certainty ratings.
5. Report (Synthesizer) → summary-of-findings + surveillance note.

### Prompt templates

```text
SYSTEM: You are the critical-appraisal analyst. Study: {{paper}}. Question context: {{pico}}.
(1) Identify the design. (2) Apply the appropriate appraisal tool ({{tool}}) item by item: for
EACH item give your judgment (yes/no/unclear) AND the supporting quote from the text (<= 20
words); where the text doesn't report it, mark NOT-REPORTED (never assume). (3) Summarize:
main validity threats, effect with precision, applicability/indirectness notes for the context.
Output structured JSON.
```

```text
SYSTEM: You are the GRADE Critic. Evidence profile draft: {{profile}}. Per-study appraisals:
{{appraisals}}. For each outcome: (1) Is the starting rating right given the designs? (2) For
each rate-down factor applied or NOT applied: argue the strongest contrary case (e.g., why
inconsistency IS present given study X vs Y; why publication bias CANNOT be ruled out given the
pool). (3) Any rate-up factor wrongly claimed? (4) State your certainty verdict per outcome and
name the single factor that most deserves human adjudication. No factor changes without a reason
grounded in the appraisal table.
```

```text
SYSTEM: You are the summary-of-findings writer. Final evidence profiles: {{profiles}}. Decision
context: {{context}}. Write per-outcome statements in GRADE certainty language ("high certainty
that...", "X probably reduces...", "we are uncertain whether..."), each followed by: what the
effect estimate is, what evidence it rests on, and what would change the grade (named trials/
replications/mechanisms). Banned words: "proven", "conclusive", "no evidence" (use "no eligible
studies found" if true). End with the surveillance trigger list.
```

### Tools & data requirements

Document/PDF access with quote extraction, retrieval for tool criteria, structured stores for appraisal tables; optional GRADEpro-compatible exports.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Checklist theater (ungrounded judgments) | Quote-anchor audit | Every item judgment carries a quote or NOT-REPORTED |
| Mechanical hierarchy ranking | Design-question fit check | Question type documented; hierarchy applied per type |
| Inflated certainty | Critic contrary-case pass | Rate-down factors must be argued both ways |
| Ignoring replication status | Evidential cross-check | [reproducibility-open-science.md](reproducibility-open-science.md) audit feeds risk-of-bias |
| Certainty language violations | Synthesizer lint pass | Banned-words list enforced |
| Applicability skipped | Profile completeness check | Indirectness row mandatory per outcome |

### Human-in-the-loop checkpoints

1. Question/outcome framing and decision context.
2. Final certainty ratings (the judgment).
3. Recommendation strength and communication.

### Inputs & outputs (chaining contract)

**Inputs:** evidence body (from [systematic-literature-review.md](../research-methods/systematic-literature-review.md), [meta-analysis.md](../research-methods/meta-analysis.md)); decision context; replication status (from [reproducibility-open-science.md](reproducibility-open-science.md)).
**Outputs:** appraisal tables, GRADE evidence profiles, summary-of-findings statements, surveillance triggers — feeding guidelines, policy decisions, [bayesian-evidence-updating.md](bayesian-evidence-updating.md) (evidence quality → LRs).

## References & Further Reading

- Guyatt, G.H. et al. (2008). "GRADE: An Emerging Consensus on Rating Quality of Evidence and Strength of Recommendations." *BMJ*, 336:924.
- Schünemann, H., Brożek, J., Guyatt, G. & Oxman, A. (eds.) (2013). *GRADE Handbook.* GRADE Working Group.
- Bradford Hill, A. (1965). "The Environment and Disease: Association or Causation?" *Proceedings of the Royal Society of Medicine*, 58(5).
- Sackett, D.L. et al. (1996). "Evidence Based Medicine: What It Is and What It Isn't." *BMJ*, 312:71.
- OCEBM Levels of Evidence Working Group (2011). *The Oxford 2011 Levels of Evidence.* Oxford CEBM.
- CASP — Critical Appraisal Skills Programme checklists (casp-uk.net).
- Sterne, J.A.C. et al. (2016). "ROBINS-I: A Tool for Assessing Risk of Bias in Non-Randomised Studies of Interventions." *BMJ*, 355.
- Straus, S.E. et al. (2019). *Evidence-Based Medicine: How to Practice and Teach EBM* (5th ed.). Elsevier. (Users' Guides tradition)
- Sagan, C. (1980). "Encyclopaedia Galactica." *Cosmos*, episode 12. (the standard)
