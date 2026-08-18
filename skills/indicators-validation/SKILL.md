---
name: indicators-validation
description: "Builds and validates a signpost list — indicators of change — for rival scenarios or hypotheses (Heuer & Pherson's Indicators and Indicators Validator), rating every indicator against every scenario, dropping those that would appear under all of them, and returning the diagnostic set with a monitoring plan. Use when the scenarios already exist and the question is which is unfolding — \"what early-warning indicators would tell us which scenario is unfolding?\", \"validate the indicator list\", \"build a signpost list for the scenario set\", \"are these indicators actually diagnostic?\". Not for building the scenarios (use `scenario-planning`) or an open-ended environmental scan (`horizon-scanning`)."
license: MIT
metadata:
  category: foresight
  method: Indicators and Indicators Validator (indicators generation, validation and evaluation)
  origin: Heuer & Pherson, 2011/2014/2019; Indicators Validator by Pherson Associates, 2008; U.S. Government Tradecraft Primer, 2009
  version: "2.0.0"
---
# Indicators and the Indicators Validator

An indicator — a signpost of change — is an observable event very unlikely unless a scenario or hypothesis were unfolding (the indicator-list tradition Grabo describes — she dates its beginning in US intelligence to "about 1948" and set out the craft in *Anticipating Surprise*, early 1970s; the *Tradecraft Primer*, 2009). Lists fail when they "confirm" every future at once. The Indicators Validator (Pherson Associates, 2008; Heuer & Pherson, 2011–2019) rates every indicator against **every** scenario and drops those likely under all of them: they say nothing about which world you are in.

## When to invoke

Invoke when:

- Scenarios, a forecast or rival hypotheses already exist; the question is which is unfolding.
- A watchlist becomes a diagnostic set with sources, thresholds, cadence and owners.

Do NOT invoke when:

- No scenarios yet — `scenario-planning` builds them; this skill closes its monitoring loop.
- A broad sweep for unframed signals — `horizon-scanning`; indicators presuppose a hypothesis.
- One dated prediction with kill-signals — `foresight`.
- Weighing evidence in hand — `analysis-of-competing-hypotheses`; indicators are evidence not yet observed.

## Procedure — seven steps

### 1 — Fix the scenarios to tell apart

List 2–5 mutually exclusive scenarios (or competing hypotheses), one line each plus horizon and the decision they serve: who acts when indicators fire. One matrix column per scenario; merge any two no observation could separate.

### 2 — Generate candidate indicators

Brainstorm 5–15 per scenario: what would we observe (actions, statements, transactions, numbers) if this world were emerging? Draw on logic, analogous cases and the actor's past behaviour (Grabo). Each must meet the five qualities of a good indicator in Pherson and Pherson's *Critical Thinking for Strategic Intelligence* (and in the Pherson Associates webinar cited below): **observable and collectable, valid, reliable, stable, unique**. Write a dated statement with a threshold ("≥ 30 % of MW awarded in 2027 utility tenders specifies 8-hour-plus duration"), never a theme ("more long-duration storage"). Include things that would *not* happen; mix leading and confirming indicators.

### 3 — Rate every indicator against every scenario

For each cell ask: *if this scenario were unfolding, how likely is this indicator?* Rate **Highly Likely/Likely/Could/Unlikely/Highly Unlikely** (HL/L/C/U/HU). Rate each row in isolation, the other scenarios' columns as honestly as the favoured one.

### 4 — Compute diagnosticity and prune

Spread = highest − lowest row rating (0–4). Spread ≤1 → **drop**; 2 → **weak** (reserve, or tighten wording); ≥3 → **keep**. The Validator ranks indicators by diagnosticity and says to discard the undiscriminating ones; these numeric cut-offs — and the coverage bar in step 5 — are this skill's operationalisation of that instruction, not published thresholds. Expected (L/HL) in exactly one scenario = *unique* to it; U/HU under a scenario = its appearance argues *against* it. Re-sort most diagnostic first; `scripts/indicators.py validate` does the arithmetic.

### 5 — Check coverage and iterate

Every scenario needs ≥3 unique kept indicators, mixing early and confirming ones — a house bar, set here rather than taken from the source. Fewer → back to step 2; never lower the bar. A scenario with no unique indicator is not distinct, or not yet understood.

### 6 — Build the monitoring plan

Per kept indicator: source (where it surfaces), threshold (when it fires), cadence, owner. Log absence: an indicator overdue by its date is evidence against its scenario, but separate "observed not to occur" from "no information" (Grabo's negative indications).

### 7 — Schedule re-validation

Set a date (every 6–12 months, or after any scenario revision): re-rate every row, retire poor pointers and any the actor has learned to fake, add new ones.

## Output template

```
## Indicator validation: {question}

**Scenarios (mutually exclusive, horizon {year}):** S1 {label}, S2 {label}, S3 {label}
**Decision served:** {who acts when indicators fire}

**Validator matrix** (HL/L/C/U/HU: likelihood if the scenario unfolds):
|ID|Indicator (observable, dated, thresholded)|S1|S2|S3|Spread|Verdict|For/against|
|{In}|{statement}|{HL}|{U}|{C}|{n}|{keep|weak|drop}|{S1}/{S2}|

**Dropped as non-diagnostic:** {ids}, {why}
**Coverage:** S1 {n} unique, S2 {n}, S3 {n} (≥3 each; gaps → {indicators added})

**Monitoring plan (kept, most diagnostic first):**
|ID|For|Source|Threshold (fires when)|Cadence|Owner|

**Absence rule:** {In} expected by {date} under {Sn}; not observed → evidence against {Sn}
**Re-validate by:** {YYYY-MM-DD}
```

Every field is mandatory: without spread and coverage it is a brainstorm, not a validation.

## Worked example

*Which of three 2030 grid-storage battery scenarios is unfolding?* S1 **Lithium Lock-in** (LFP ≥ 85 % of new GWh), S2 **Sodium Surge** (sodium-ion ≥ 25 %), S3 **Long-Duration Leap** (8-hour-plus ≥ 25 %); twelve candidates in `examples/battery-storage.json`. `python3 scripts/indicators.py validate --file examples/battery-storage.json` prints (seven rows elided):

```
ID    Indicator                                      S1   S2   S3  Spread Pairs  Verdict For       Against
I5    A top-5 cell maker commissions a sodium-i...   HU   HL    C       4   3/3  keep    S2*       S1
I9    At least two announced sodium-ion gigafac...   HL   HU    C       4   3/3  keep    S1*       S2
...   (I7 spread 4; I1 I2 I3 I10 I11 I12 spread 3; all keep)
I6    A major market adopts capacity-market rul...    C    C   HL       2   2/3  weak    S3*       -
I4    Global grid-storage installations exceed ...   HL   HL    L       1   0/3  drop    S1,S2,S3  -
I8    Government storage subsidies and mandates...    L    L    L       0   0/3  drop    S1,S2,S3  -
Kept 9 | weak 1 | dropped 2 (of 12)
Coverage: S1 3 (I3, I9, I11) | S2 3 (I1, I5, I10) | S3 3 (I2, I7, I12) + weak I6 — ok
```

I5 and I9 are ideal: highly likely in one world, highly unlikely in another (spread 4). I4 (installations exceed 100 GWh) and I8 (subsidies continue) are dropped: likely under every scenario, the shared outcome, not a signpost. I6 stays as S3 reserve (spread 2). Coverage is 3/3/3; `plan` prints the nine kept rows with source, threshold, cadence, owner, and re-validation date 2027-01-31.

## Verification

Before the list ships, confirm:

- [ ] Every row rated for every scenario; every indicator a dated, thresholded observable, not a theme or an outcome.
- [ ] Spreads recomputed (by hand or `scripts/indicators.py validate`): kept rows ≥3; rows ≤1 dropped or retention justified in writing.
- [ ] Each scenario has ≥3 unique kept indicators; gaps triggered new generation, not a lowered bar.
- [ ] Every kept indicator carries source, threshold, cadence and owner; the absence rule is written down.
- [ ] The favoured scenario's column is not all HL; a re-validation date is set.

## Companion tool

`scripts/indicators.py` does the Validator arithmetic on a JSON case file (scenarios, indicators rated HL/L/C/U/HU or 2…−2, optional source/threshold/cadence/owner). Stdlib only, deterministic.

```bash
python3 scripts/indicators.py validate --file case.json   # ranked table, verdicts, coverage; exit 1 on coverage gap
python3 scripts/indicators.py matrix   --file case.json   # rating grid
python3 scripts/indicators.py plan     --file case.json   # monitoring-plan skeleton
python3 scripts/indicators.py validate --demo --json      # worked example as JSON
python3 scripts/indicators.py --selftest                  # hand-verified checks
```

## Pair with adjacent skills

- `scenario-planning` — supplies the scenarios; this skill validates its early signals into a monitoring plan.
- `horizon-scanning` — finds unframed signals; its signposts feed step 2.
- `foresight` — its weak signals and kill-signals are a two-column indicator list; validate them here.
- `key-assumptions-check` — what would we see if a load-bearing assumption broke? Ready indicator candidates.
- `analysis-of-competing-hypotheses` — same diagnosticity logic on evidence in hand; fired indicators become ACH rows.
- `bayesian-update` — treats a fired unique indicator as a likelihood ratio on scenario probabilities.
- Methodology counterpart: [methodologies/foresight/scenario-planning.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/scenario-planning.md), step 8, implemented here.

## Anti-patterns

- Do **not** list outcomes as indicators: "sodium-ion reaches 25 % share" *is* S2; an indicator is observable on the way there.
- Do **not** keep unobservable indicators ("management gets nervous", "sentiment shifts"): no source and threshold, no indicator.
- Do **not** keep an indicator for feeling important when it is likely under every scenario: importance is not diagnosticity.
- Do **not** ignore absence: an indicator that should have fired and has not is a signal, distinct from "no information".
- Do **not** let the list go unrevisited: actors learn indicator lists and adapt; stale lists lull readers.

## Reference

- R. J. Heuer Jr. and R. H. Pherson, *Structured Analytic Techniques for Intelligence Analysis*, 3rd ed. CQ Press / SAGE, 2019, §9.11 "Indicators Generation, Validation, and Evaluation" (2nd ed. 2014, ch. 6 "Scenarios and Indicators"). ISBN 978-1-5063-6893-1.
- U.S. Government, *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis*, 2009, pp. 12–13 "Indicators or Signposts of Change". https://www.cia.gov/resources/csi/static/Tradecraft-Primer-apr09.pdf
- K. H. Pherson and R. H. Pherson, *Critical Thinking for Strategic Intelligence*, 2nd ed. CQ Press / SAGE, 2017 — indicator lists and the five qualities of a good indicator (observable and collectable, valid, reliable, stable, unique). ISBN 978-1-5063-1688-8.
- R. H. Pherson, "The Five Habits of the Master Thinker," *Journal of Strategic Security*, vol. 6, no. 3, pp. 54–60, 2013 — five analytic *habits* (key assumptions, alternative explanations, inconsistent evidence, key drivers, historical context), not the indicator qualities; background on why the checks are habitual. doi:10.5038/1944-0472.6.3.5
- R. H. Pherson, "The Tradecraft of Warning: Overcoming Cognitive Barriers," ODNI/INR warning seminar, 2009 — the Indicators Validator (Pherson Associates, 2008). https://pherson.org/wp-content/uploads/2013/11/02.-The-Tradecraft-of-Warning-Paper_FINAL.pdf
- Pherson Associates, "Indicators: The Lingua Franca of Analytic Techniques," IALEIA webinar, 18 July 2012 — the HL/L/C/U/HU scale and Validator steps. https://www.ialeia.org/docs/IALEIA_Webinar_Indicators_Presentation.pdf
- C. M. Grabo, *Anticipating Surprise: Analysis for Strategic Warning*, ed. J. Goldman. Joint Military Intelligence College, 2002 (University Press of America, 2004), ch. 2 "Indicator Lists", ch. 5 "Negative Indications". ISBN 0-9656195-6-7. https://www.govinfo.gov/app/details/GOVPUB-D5_200-PURL-gpo86445
