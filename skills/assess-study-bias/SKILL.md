---
name: assess-study-bias
description: "Grades a randomised trial with Cochrane RoB 2 — the five domains of randomization process, deviations from intended interventions, missing outcome data, measurement of the outcome, and selection of the reported result — and emits per-domain and overall judgements of Low risk / Some concerns / High risk with the evidence cited. Use when a single study's trustworthiness is in question: \"is this trial reliable?\", \"assess risk of bias in this RCT\", \"run RoB 2 on this study\", \"how much weight does this result deserve?\". Not for grading a whole body of evidence (use `evidence-appraisal`) or for auditing an ML leaderboard claim (use `benchmark-model-claims`)."
license: "MIT (skill text); RoB 2 instrument © its authors, CC BY-NC-ND 4.0 — wording not reproduced"
metadata:
  category: quantitative
  method: Cochrane Risk of Bias 2 (RoB 2) for randomized trials
  origin: J. A. C. Sterne, J. Savović, M. J. Page et al., Cochrane RoB2 Development Group, 2019
  version: "2.0.0"
---
# Assess Study Bias (RoB 2)

RoB 2 is Cochrane's revised risk-of-bias tool for randomized trials (Sterne et al., *BMJ*, 2019; guidance version 22 August 2019). It grades **one result of one trial**, not a whole paper: the assessor answers fixed signalling questions with Yes / Probably yes / Probably no / No / No information, and published algorithms map those answers to Low risk of bias, Some concerns, or High risk of bias in each of five domains, then to an overall judgement. Its principle is that bias is judged from what the trial *did*, question by question, not from an impression of the paper's quality — which prevents treating a well-written, highly cited trial as reliable when differential attrition or outcome-switching could have manufactured the whole effect.

> **Instrument licensing — read this before running the tool.** RoB 2 is © its authors (Higgins, Savović, Page, Sterne and the RoB2 Development Group) and is published under **CC BY-NC-ND 4.0** (Attribution — NonCommercial — NoDerivatives), which allows neither commercial redistribution nor adaptation of the instrument's text. **The signalling-question wording is therefore deliberately not reproduced anywhere in this skill.** What is kept here is the unprotectable method: the five domain names, the question IDs, the response options and the published judgement algorithms. **Take the exact wording from https://www.riskofbias.info/welcome/rob-2-0-tool and answer against that text** — the one-line topics printed by `scripts/rob2.py questions` and listed in [references/rob2-domains.md](references/rob2-domains.md) are signposts for finding each question, not the question. The skill text and `scripts/rob2.py` are MIT-licensed; the `--sc-high-threshold` option is this skill's own addition and is not part of RoB 2.

## When to invoke

Invoke when:

- A randomized trial is used as evidence and its reliability matters: "is this study reliable?", "assess bias in this trial", "what's the risk of bias in {study}?".
- A trial result is about to be quoted, weighted or pooled, and its per-domain risk must travel with it.
- A review pipeline needs a per-study rating before synthesis.

Do NOT invoke when:

- The certainty of the *whole* evidence base is the question — `evidence-appraisal` applies GRADE across studies.
- The claim is an ML benchmark or leaderboard result — `benchmark-model-claims`.
- The studies are already rated and the task is pooling them — `meta-analysis`.
- The task is assembling and screening the study set — `systematic-review`.
- The claim is not empirical ("X is the market leader") — that is marketing copy, not a study.

## Procedure

### 1 — Fix the study type, the result, and the effect of interest

RoB 2 applies to randomized trials only. Non-randomized or observational studies go to ROBINS-I (Sterne et al., 2016); single-arm studies and case series are hypothesis-generating and fit neither. Name the specific outcome and result assessed — RoB 2 grades a result, so a trial with three outcomes needs three assessments. Domain 2 distinguishes two effects of interest: the **effect of assignment to intervention** (intention-to-treat) and the effect of adhering to intervention (per-protocol). This skill and `scripts/rob2.py` assess the assignment (ITT) effect; state that in the output.

### 2 — Answer the signalling questions with cited evidence

Fetch the published signalling questions from https://www.riskofbias.info/welcome/rob-2-0-tool first — the wording is not carried in this skill — then work through the five domains in order, answering Y / PY / PN / N / NI with a page, section, table or figure citation for each. `python3 scripts/rob2.py questions` prints the question IDs, a one-line topic for each, the response options and where to read the wording; domains, response options and judgement rules are summarised in [references/rob2-domains.md](references/rob2-domains.md). Conditional questions are answered only when their condition is met; NI is legitimate and must not be softened into "probably yes". The judgement is only as good as the evidence attached to these answers.

### 3 — Derive each domain judgement from the algorithm

Map the answers through the published algorithm rather than by impression. The five domains are: bias arising from the randomization process; bias due to deviations from intended interventions; bias due to missing outcome data; bias in measurement of the outcome; bias in selection of the reported result. Each resolves to Low risk of bias, Some concerns, or High risk of bias. Optionally record the predicted direction of bias per domain (favours experimental, favours comparator, towards null, away from null, unpredictable).

### 4 — Derive the overall judgement

Per RoB 2: **Low** when every domain is Low; **Some concerns** when at least one domain raises some concerns and none is High; **High** when at least one domain is at High risk of bias, **or** the trial has some concerns for multiple domains in a way that substantially lowers confidence in the result. That last clause is a review-author judgement, not arithmetic — state it when used. Never average domains: one High is enough, and a "3 of 5 are fine" pass is not a RoB 2 judgement.

### 5 — Restate what the result can and cannot support

Translate the judgement into consequences for the claim. Name the claims that survive, the claims a specific domain invalidates (with the mechanism — differential attrition, outcome-switching, unblinded self-report), and what a replication must do differently. When the study is a sole source judged High overall, cap downstream confidence and route the claim through `triangulate-sources` before treating the effect as established.

## Output template

```
## Risk of Bias (RoB 2) — {study title}, {authors, year}

**Result assessed:** {outcome, timepoint}   **Effect of interest:** effect of assignment to intervention (ITT)
**Design:** randomized trial   **Tool:** RoB 2 (22 Aug 2019 guidance)

| Domain | Judgement | Signalling answers | Supporting evidence |
|---|---|---|---|
| 1. Randomization process | {Low / Some concerns / High} | {1.1–1.3} | {page / section} |
| 2. Deviations from intended interventions | {…} | {2.1–2.7} | {…} |
| 3. Missing outcome data | {…} | {3.1–3.4} | {…} |
| 4. Measurement of the outcome | {…} | {4.1–4.5} | {…} |
| 5. Selection of the reported result | {…} | {5.1–5.3} | {…} |

**Overall:** {Low risk of bias | Some concerns | High risk of bias} — {rule: a High domain, or multiple Some concerns that substantially lower confidence}
**Direction of bias:** {favours experimental | favours comparator | towards null | away from null | unpredictable}
**Supports:** {claims that survive}
**Does NOT support:** {claims invalidated, with the mechanism}
**Follow-up:** {what a replication must do differently}
```

Every domain row is mandatory, as are the effect of interest, the overall judgement and the rule producing it. A table without supporting-evidence citations is an opinion, not a RoB 2 assessment.

## Worked example (illustrative)

An invented trial — "Illustrative et al., 2025", a 12-week mindfulness app versus waitlist control, self-reported stress at 12 weeks, n = 74 — assessed for the effect of assignment. Judgements derived mechanically with `python3 scripts/rob2.py judge --demo`:

```
D1: 1.1=NI 1.2=NI 1.3=N → Some concerns
    [randomization process] via 1.2=NI → 1.3=N/PN/NI
D2: 2.1=Y 2.2=Y 2.3=PN 2.4=NA 2.5=NA 2.6=PY 2.7=NA → Low
D3: 3.1=N 3.2=N 3.3=Y 3.4=Y → High
    [missing outcome data] via 3.1=N/PN/NI → 3.2=N/PN → 3.3=Y/PY/NI → 3.4=Y/PY/NI
    direction of bias (assessor-supplied): Favours experimental
D4: 4.1=PN 4.2=N 4.3=Y 4.4=Y 4.5=PN → Some concerns
D5: 5.1=N 5.2=Y 5.3=PN → High
Overall: High risk of bias   (Table 1: at least one domain at High risk of bias (D3, D5))
```

Evidence behind the answers: 22 % attrition in the app arm versus 4 % in control, complete-case analysis only (D3); no prospective registration and an abstract headline outcome differing from the registry's primary outcome (D5); "randomly assigned" stated without sequence generation or concealment (D1); unblinded participants self-reporting stress (D4). **Supports:** a pilot effect among completers, hypothesis-generating only. **Does NOT support:** "mindfulness apps reduce workplace stress" — differential attrition plus outcome-switching can manufacture the entire effect. **Follow-up:** prospective registration, intention-to-treat analysis, an active-control app, an objective stress marker.

## Verification

Before the assessment ships, confirm:

- [ ] The signalling questions were read in their published wording at riskofbias.info, not answered from the topic labels in this skill.
- [ ] The result assessed and the effect of interest (assignment/ITT) are named; several outcomes need several assessments.
- [ ] Every signalling question carries a page, table or figure citation; NI answers stay NI.
- [ ] Each domain judgement is re-derived with `python3 scripts/rob2.py judge --file answers.json` and checked against the table.
- [ ] The overall judgement follows the RoB 2 rule, and any escalation from multiple "Some concerns" is stated as a review-author judgement.
- [ ] No domain was averaged away: one High domain makes the overall judgement High.
- [ ] The "does NOT support" line names the mechanism, not just the domain number.

## Companion tool

`scripts/rob2.py` (stdlib only) walks the published RoB 2 decision trees (22 August 2019 guidance; effect of assignment to intervention) over the signalling-question answers, so judgements are derived mechanically. It carries the question IDs, response options and algorithms — never the instrument's wording, which the assessor fetches from riskofbias.info. The study still has to be read and the answers cited; the tool only removes slips in applying the algorithm.

```bash
python3 scripts/rob2.py questions                   # IDs, topics, options + where to read the wording; --template writes empty answers.json
python3 scripts/rob2.py judge --file answers.json   # --json; --sc-high-threshold N (default 3)
python3 scripts/rob2.py judge --demo                # the worked example above
python3 scripts/rob2.py --selftest                  # 67 checks against the published algorithm tables
```

It prints, per domain, the answers, the judgement and the algorithm path that produced it, then the overall judgement with its rule. Escalating several "Some concerns" to High is a review-author judgement in RoB 2, which sets no threshold for it; `--sc-high-threshold` is this skill's own mechanical stand-in, flagged as such in every output. Usable without the tool by walking the same trees by hand.

## Pair with adjacent skills

- `systematic-review` — RoB 2 grading is the per-study bias step inside a PRISMA pipeline.
- `meta-analysis` — grade studies before pooling; pooling high-risk studies gives a precise biased estimate.
- `evidence-appraisal` — GRADE the body of evidence once each study carries a RoB 2 judgement.
- `benchmark-model-claims` — the ML-benchmark sibling for leaderboard claims.
- `test-significance` — a p-value from a high-risk trial is precise, not trustworthy.
- Methodology counterpart: [methodologies/scientific-methods/evidence-appraisal.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/scientific-methods/evidence-appraisal.md) — the broader evidence-grading framework this feeds.

## Anti-patterns

- Do **not** grade a paper. RoB 2 grades one result; different outcomes can carry different judgements.
- Do **not** give a "3 of 5 domains are fine" pass. One High domain is enough.
- Do **not** convert No information into Probably yes to keep a domain Low.
- Do **not** apply RoB 2 to non-randomized or single-arm studies — use ROBINS-I, or state that no tool fits.
- Do **not** confuse a small sample with high risk of bias: small n is a precision problem, not a bias domain.

## Reference

- J. A. C. Sterne, J. Savović, M. J. Page, et al., "RoB 2: a revised tool for assessing risk of bias in randomised trials," *BMJ*, vol. 366, p. l4898, 2019. doi:10.1136/bmj.l4898
- J. P. T. Higgins, J. Savović, M. J. Page, J. A. C. Sterne (eds.), *Revised Cochrane risk-of-bias tool for randomized trials (RoB 2)*, full guidance, version 22 August 2019. https://www.riskofbias.info/welcome/rob-2-0-tool/current-version-of-rob-2
- J. P. T. Higgins, J. Thomas, J. Chandler, et al. (eds.), *Cochrane Handbook for Systematic Reviews of Interventions*, version 6.5, ch. 8. Cochrane, 2024. https://training.cochrane.org/handbook
- J. A. C. Sterne, M. A. Hernán, B. C. Reeves, et al., "ROBINS-I: a tool for assessing risk of bias in non-randomised studies of interventions," *BMJ*, vol. 355, p. i4919, 2016. doi:10.1136/bmj.i4919
