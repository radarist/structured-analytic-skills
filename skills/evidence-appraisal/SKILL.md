---
name: evidence-appraisal
description: "Rates how much certainty a body of evidence deserves, outcome by outcome, on the GRADE scale (Grading of Recommendations Assessment, Development and Evaluation — high, moderate, low, very low), naming the reason behind every downgrade or upgrade and writing the summary-of-findings row and a calibrated certainty statement. Use when asked \"how strong is the evidence for X?\", \"GRADE this evidence\", \"is this proven or just one study?\", or \"the studies conflict — what is actually known?\". Not for one study's risk of bias (use `assess-study-bias`) or for grading a non-study source such as an article or dataset (use `rate-source-admiralty`)."
license: MIT
metadata:
  category: evidence-verification
  method: GRADE certainty of evidence (Grading of Recommendations Assessment, Development and Evaluation)
  origin: GRADE Working Group — G. H. Guyatt et al., 2008 (BMJ series); GRADE Handbook, 2013
  version: "2.0.0"
---
# Evidence Appraisal (GRADE)

GRADE — from the GRADE Working Group (Guyatt et al., 2008; GRADE Handbook, 2013) — rates the certainty of a body of evidence **per outcome**, not per study: randomized bodies start High, observational bodies Low, five named factors rate down and three rate up, and the result is stated as high / moderate / low / very low. Its core principle: certainty is a judged, argued property of the whole evidence base for one outcome, every move traceable to a reason. It prevents two symmetrical failures — treating one exciting trial as a fact, and a pile of weak studies as one.

## When to invoke

Invoke when:

- The question is how far a body of studies deserves trust: "how strong is the evidence for {X}?", "GRADE this".
- The literature is mixed and a decision must still be made: "the studies conflict — what is known?".
- A `systematic-review` or `meta-analysis` result needs a certainty rating.

Do NOT invoke when:

- One study's quality is the question — use `assess-study-bias` (RoB 2 / ROBINS-I); its ratings are an *input* here.
- The study set is not assembled yet — use `systematic-review`; GRADE starts once the body is known.
- The source is not a study (article, dataset, vendor claim) — use `rate-source-admiralty`.
- Several studies need pooling first — use `meta-analysis`; its results feed the factors.

## Procedure

### 1 — Frame the question and the outcomes

GRADE is per question, per outcome; "does X work?" is unappraisable as stated. Write the PICO (population, intervention, comparator, outcomes) and rank outcomes by importance to the decision — the outcome list, not the study list, sets how many ratings to produce. *Artifact: PICO plus ranked outcomes.*

### 2 — Assemble the evidence body

Take the study set from a `systematic-review` where one exists; otherwise document the search (sources, date window, inclusion rules) so the body is auditable. Record each design and sample size. A randomized body starts **High** (4); an observational body **Low** (2). *Artifact: study table.*

### 3 — Appraise each study, routed by design

Route each study to its per-study tool: randomized → RoB 2, non-randomized → ROBINS-I (via `assess-study-bias`); other designs → the matching CASP checklist; single-arm series → hypothesis-generating. Every judgment carries a quote (≤ 20 words) or is marked NOT REPORTED — unreported methods are never assumed done. *Artifact: appraisal table.*

### 4 — GRADE the body, one outcome at a time

Start from the design level and apply the five **rate-down** factors, each 0 / −1 (serious) / −2 (very serious), with a one-line reason grounded in the appraisal table: risk of bias; inconsistency (unexplained heterogeneity, I²); indirectness (population, intervention, comparator or outcome differ from the PICO); imprecision (the CI crosses the minimal important difference); publication bias (small-study asymmetry, unpublished trials). Then the three **rate-up** factors: large effect (RR > 2 or < 0.5, +1; RR > 5 or < 0.2, +2) with no plausible confounder; dose–response gradient (+1); residual confounding working *against* the observed effect (+1). Rating up is "mostly applicable to observational studies" and comes only after rating down; the Handbook has "yet to find a compelling example" of rating up randomized evidence, so such an upgrade is exceptional and must be argued. State the strongest case for every factor *not* applied. *Artifact: evidence profile with reasons.*

### 5 — Communicate in certainty language and set the surveillance trigger

Write one summary-of-findings row per outcome and a plain statement ("moderate certainty that X probably reduces Y"). Banned words: "proven", "conclusive", "no evidence" (write "no eligible studies found" if true). Name the new evidence — trials in progress, replications, an explained heterogeneity — that would change the grade. *Artifact: summary-of-findings table and surveillance note.*

## Output template

```
## Evidence Appraisal — {question}

**PICO:** P={population} | I={intervention} | C={comparator} | O={outcomes, ranked}
**Evidence body:** {N studies} — {designs, total n, source}

| Outcome | Studies (n) | Effect (95% CI) | Certainty | Factors applied (reason) |
|---|---|---|---|---|
| {outcome 1} | {N RCTs, n=…} | {MD/RR …} | ⊕⊕⊕⊕ High | none |
| {outcome 2} | {…} | {…} | ⊕⊕◯◯ Low | −1 inconsistency ({reason}); −1 imprecision ({reason}) |

**Certainty statement:** "{high/moderate/low/very-low} certainty that {X} {will/probably/may} {effect}"
**Surveillance trigger:** {trials, replications or mechanisms that would change the grade}
```

Mandatory: the PICO, one row per outcome with factor-by-factor reasons (including "none"), the certainty statement in GRADE language, and the surveillance trigger. A level without reasons is not a grade.

## Worked example

Question (illustrative body): in adults with chronic insomnia (P), does CBT-I (I) versus sleep-hygiene education (C) improve sleep-onset latency (O)? Body: 5 RCTs, n = 412, documented search — start **High**. Appraisal: four studies at low RoB 2 risk, one "some concerns" (unblinded outcome logging) at about 8 % of pooled weight. `python3 scripts/grade.py rate --demo` reproduces the rating (abridged: risk of bias, indirectness, publication bias and all three rate-up factors print 0 with reasons):

```
GRADE certainty of evidence — Sleep-onset latency (min)
Body: 5 RCTs, n = 412, effect MD −12 min (95% CI −18 to −3)
Starting level: High (4) — randomized trials  [Handbook §5.1.1]

Rate down (Handbook Table 5.2; 0 / −1 serious / −2 very serious):
  inconsistency     −1  serious       point estimates range −4 to −22 min, I² = 68%
  imprecision       −1  serious       95% CI −18 to −3 spans the pre-set 10-min MID

Arithmetic: 4 (High) −1 inconsistency −1 imprecision = 2 → Low
Certainty: ⊕⊕◯◯ Low
```

Summary-of-findings row: Sleep-onset latency (min) | 5 RCTs (n = 412) | MD −12 (−18 to −3) | ⊕⊕◯◯ Low | −1 inconsistency (I² = 68 %); −1 imprecision (CI spans the 10-min MID). Certainty statement: "Low certainty that CBT-I may shorten sleep-onset latency by about 12 minutes versus sleep-hygiene education." Surveillance trigger: the 300-patient SLEEPIQ-2 trial — a CI wholly beyond the 10-min MID removes the imprecision downgrade (→ Moderate); the inconsistency downgrade stands until the heterogeneity is explained.

## Verification

- [ ] Every PICO outcome has its own row and certainty; none is averaged or omitted for looking worse.
- [ ] Every move cites a reason from the appraisal table or pooled statistics; every factor not applied has its contrary case stated.
- [ ] Recompute the arithmetic (start + downgrades + upgrades, clamped) with `scripts/grade.py rate --file` or by hand.
- [ ] Any rate-up on a randomized body, or alongside a rate-down for the same concern, is flagged and argued.
- [ ] The certainty statement uses GRADE language and none of the banned words.

## Companion tool

`scripts/grade.py` (stdlib only) does the step-4 bookkeeping: start level by design (RCT → High, observational → Low; `--start high` for ROBINS-I-appraised bodies), five rate-down factors (0/−1/−2), three rate-up factors (+1/+2 large effect, +1 dose–response, +1 opposing confounding), the clamp to Very low…High, and the Table 5.1 interpretation. Judgements stay with the analyst; the tool totals them and warns when rating up meets rating down or randomized evidence.

- `python3 scripts/grade.py rate --file body.json [--json]` — one outcome; `rate --demo` reproduces the worked example
- `python3 scripts/grade.py sof --file bodies.json` — Summary-of-Findings rows
- `python3 scripts/grade.py factors` — the 5+3 factor definitions, cited
- `python3 scripts/grade.py --selftest`

Sample output: the worked example above. Usable without the tool; the rules are those of step 4.

## Pair with adjacent skills

- `assess-study-bias` — the per-study sibling; its RoB 2 / ROBINS-I ratings feed the risk-of-bias factor.
- `systematic-review` — assembles the study set (PRISMA flow) this skill grades.
- `meta-analysis` — pools the body first; its I² and Egger results feed two of the factors.
- `rate-source-admiralty` — grades non-study sources before they enter an evidence body.
- `bayesian-update` — a GRADE level plus effect size disciplines the likelihoods.
- Methodology counterpart: [methodologies/scientific-methods/evidence-appraisal.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/scientific-methods/evidence-appraisal.md) — hierarchies, CASP, causation viewpoints.

## Anti-patterns

- Do **not** grade one study and call it "the certainty of the evidence"; GRADE rates the body per outcome.
- Do **not** apply the evidence hierarchy mechanically; it ranks bias-resistance for therapy questions, other question types need their own frames, and a well-run cohort can outrank a badly run RCT.
- Do **not** move a factor without a reason from the appraisal table; "feels weak" is not a downgrade, "3 of 5 studies have high attrition risk" is.
- Do **not** rate up casually: the upgrades are mostly for observational bodies not already rated down, and a randomized-body upgrade is exceptional.
- Do **not** average certainty across outcomes or report only the best; "probably helps A, uncertain for B" is the deliverable.
- Do **not** write "proven", "conclusive" or "no evidence"; decisions rest on imperfect evidence, graded honestly.
- Do **not** let checklist scores replace judgment; careful teams can differ by one level.

## Reference

- G. H. Guyatt et al., "GRADE: an emerging consensus on rating quality of evidence and strength of recommendations," *BMJ*, vol. 336, pp. 924–926, 2008. doi:10.1136/bmj.39489.470347.AD
- H. Balshem et al., "GRADE guidelines: 3. Rating the quality of evidence," *J Clin Epidemiol*, vol. 64, no. 4, pp. 401–406, 2011. doi:10.1016/j.jclinepi.2010.07.015
- H. Schünemann, J. Brożek, G. Guyatt, A. Oxman (eds.), *GRADE Handbook*, GRADE Working Group, 2013, §5 (Tables 5.1–5.3, 5.9). https://gdt.gradepro.org/app/handbook/handbook.html
- H. J. Schünemann et al., "GRADE guidelines: 18. How ROBINS-I and other tools … should be used to rate the certainty of a body of evidence," *J Clin Epidemiol*, vol. 111, pp. 105–114, 2019. doi:10.1016/j.jclinepi.2018.01.012
- J. A. C. Sterne et al., "ROBINS-I: a tool for assessing risk of bias in non-randomised studies of interventions," *BMJ*, vol. 355, i4919, 2016. doi:10.1136/bmj.i4919
