---
name: reference-class-forecasting
description: "Sanity-checks an inside-view estimate (schedule, cost, adoption, revenue) against the outside view — the outcome distribution of a reference class of similar past cases (Kahneman & Tversky; Flyvbjerg's reference class forecasting) — and computes the base rate, the estimate's percentile in the class and the uplift to a P50/P80 forecast. Use when a plan, budget or timeline rests on an internal estimate: \"sanity-check the 9-month estimate against similar projects\", \"what's the base rate before trusting the internal number?\", \"apply reference class forecasting to this budget\". Not for revising one belief with one datum (use `bayesian-update`) or TAM/SAM/SOM sizing (use `estimate-market-size`)."
license: MIT
metadata:
  category: quantitative
  method: Reference Class Forecasting (outside view)
  origin: Daniel Kahneman & Amos Tversky, 1979; Bent Flyvbjerg, 2006
  version: "2.0.0"
---
# Reference Class Forecasting

Plans are forecast from the **inside view** — their own tasks and scenarios — which is systematically optimistic because the specifics crowd out how projects like this one usually end (Kahneman & Tversky 1979; Kahneman & Lovallo 1993). Reference class forecasting is the **outside view** made procedural: place the case in a class of similar completed cases and let the class's outcome distribution, not the plan, set the forecast. Flyvbjerg (2006) fixed the three steps — identify a reference class; establish its outcome distribution; position the case in it — that UK project appraisal adopted in 2004. It prevents the planning fallacy — a 9-month estimate no comparable project ever met.

## When to invoke

Invoke when:

- A schedule, budget, cost, adoption or revenue estimate is about to be trusted as stated: "sanity-check the 9-month estimate against similar projects", "what is the base rate for this kind of migration?".
- A business case or roadmap needs a P50/P80 forecast with stated contingency, not a bottom-up point estimate.

Do NOT invoke when:

- One belief needs revising on one new datum — use `bayesian-update`.
- The question is market size (TAM/SAM/SOM) — use `estimate-market-size`.
- Numbers only need internal consistency (CAGR, unit economics) — use `quantitative-sanity-check`.
- Forecasts already exist and need scoring — use `brier-score-calibration`.
- No comparable completed cases exist (n < 3) — say so; de-risk with `premortem-analysis` and `cheapest-experiment` rather than invent a class.

## Procedure — the outside view in seven steps

### 1 — Define the forecast quantity and unit

Write the quantity as it will be measured at the end ("delivery of Feature X, months from kickoff"). Prefer a **ratio** to the plan (actual / estimated): ratios compare across project sizes. Record the inside view as stated — 1.0 is the plan; 1.2 if 20 % contingency is already inside it.

### 2 — Choose the reference class, and say why

Propose 2–3 candidate classes and pick one, stating the trade-off — the **reference-class problem** (Hájek 2007): narrower is more similar but smaller, broader is bigger but less comparable. Flyvbjerg's rule: "broad enough to be statistically meaningful but narrow enough to be truly comparable". Judge similarity on outcome drivers, not labels. Record the rejected classes.

### 3 — Assemble the class's outcome distribution

One outcome per completed case, with source and n; mark illustrative data as such. Report percentiles — P10, P50, P80, P90 — not the mean: overrun distributions are right-skewed and the mean flatters the plan. n < 8: percentiles are indicative only; n < 3: no distribution — refuse and return to step 2. `scripts/refclass.py describe` computes them with a skew note.

### 4 — Position the inside view in the class

Locate the inside estimate as a percentile of the class (`position`): the share of cases below it and at or below it. An estimate at the 0–10 % point assumes an outcome 90 % of comparable projects failed to reach — the planning-fallacy signature; read it before adjusting.

### 5 — Compute the uplift to the target percentile

Choose the confidence the decision needs: P50 for a portfolio owner who nets overruns against underruns; P80 (20 % overrun risk, the UK Department for Transport's standard) or higher for a stand-alone project (Flyvbjerg 2006). Uplift `multiplier = Q(P_target) / inside`; forecast `= base × multiplier`. Flyvbjerg's UK rail class needed +40 % (P50) / +57 % (P80); HM Treasury's guidance tabulates generic uplifts by project type when no better class exists.

### 6 — Adjust the inside view only with specific, evidenced reasons

The outside view is the anchor; move it only for reasons that make *this* case measurably different — a documented better-than-class track record, a fixed-scope contract (Tetlock & Gardner 2015: outside view first, then inside). State the adjustment as a multiplier with its evidence; "we are different" is not evidence. An adjustment landing below the class median has erased the base rate — the tool flags it and exits 1.

### 7 — Report

Fill the output template — every field, including rejected classes and the reason for any adjustment.

## Output template

```
## Reference class forecast — {quantity, unit}

**Inside view:** {estimate} (ratio to plan {r}) — source: {who / how}
**Reference class:** {definition} — n = {n}; sources: {datasets}; rejected: {class: reason}
**Class distribution:** P10 {x} · P50 {x} · P80 {x} · P90 {x} · mean {x} ({skew note})
**Position of the inside view:** {lo}–{hi} % of the class at or below it — {interpretation}
**Uplift to P{target}:** ×{m} ({+p %}) — {base} × {m} = {forecast} {unit}; P50 forecast {x}
**Residual inside-view adjustment:** ×{k} — reason: {specific evidence} | none
**Forecast:** {final} {unit} at P{target} — class confidence: {n, comparability, data quality}
```

Every field is mandatory; without the percentile line it is an inside view with bigger contingency, not an outside view.

## Worked example

*Feature X, an internal ML feature, is planned at 9 months — what should the roadmap commit to?* The reference class is ten illustrative completed internal ML/R&D features (≥ 3 engineers, novel model component): Alder 1.0, Birch 1.1, Cedar 1.2, Dogwood 1.3, Elm 1.5, Fir 1.6, Ginkgo 1.8, Hazel 2.0, Ironwood 2.4, Juniper 3.0 (actual / planned duration; `examples/feature-x-schedule.json`). The team's one evidenced reason to adjust: its last four comparable features finished at a median ratio of 1.3. `python3 scripts/refclass.py report --demo` prints (abridged):

```
   n 10   min 1.00   P10 1.09   P25 1.225   P50 1.55   P75 1.95   P80 2.08   P90 2.46   max 3.00
   mean 1.69   sd 0.6315   skew g1 +0.89 - right-skewed (mean > median): summarise with percentiles, not the mean
   outcomes below it: 0/10 (0 %)   at or below: 1/10 (10 %)   percentile rank: 0-10 % (interpolated 0.0 %)
   multiplier = Q(P80) / inside = 2.08 / 1.00 = x2.08 (+108 %)
   base 9.00 months -> P50 forecast 13.95 months -> P80 forecast 18.72 months
   final forecast: 18.72 months x 0.9 = 16.85 months at P80
```

The roadmap commits to 17 months at P80 (14 at P50), not 9: the plan sat below every completed case and the only adjustment is the team's documented record. Asking for ×0.7 instead would land at 13.1 months, below the class median — the tool returns the adjusting-away-the-base-rate verdict (exit 1).

## Verification

Before the forecast ships:

- [ ] The quantity has a unit; the inside estimate's ratio to the plan is stated; two or more candidate classes were named, the choice justified, rejected classes listed.
- [ ] Every class outcome has a source and n is stated; n < 8 carries the small-n warning, n < 3 was refused.
- [ ] Percentiles were recomputed with `scripts/refclass.py describe` — no mean of a skewed class.
- [ ] The inside view's percentile line is present.
- [ ] Every adjustment carries specific evidence; the final forecast is not below the class-median forecast (tool exit 0, not 2).

## Companion tool

`scripts/refclass.py` computes steps 3–6 from a JSON or CSV reference class: Hyndman & Fan (1996) type-7 quantiles with skew note and small-n warning, the inside view's percentile band, the uplift with its formula, and the residual adjustment (refused without `--reason`) with the median check. Stdlib only, deterministic.

```bash
python3 scripts/refclass.py describe --file class.json                # n, P10–P90, mean, sd, skew
python3 scripts/refclass.py report   --file class.json --inside 1.0 --base 9 --target-percentile 80 --adjust 0.9 --reason "..."
python3 scripts/refclass.py report   --demo                           # worked example; also position, uplift, --json, --selftest
```

Exit codes: 0 forecast rests on the class; 1 invalid input (n < 3, adjustment without reason); 2 the adjustment erased the base rate. Usable by hand: sort the class and read percentiles.

## Pair with adjacent skills

- `bayesian-update` — take the class percentile as the prior, then update on case-specific evidence.
- `estimate-market-size` — market-size questions route there.
- `quantitative-sanity-check` — check the inside estimate's arithmetic first.
- `premortem-analysis` — turn the inside/outside gap into named failure modes.
- `brier-score-calibration` — score reference-class forecasts once outcomes resolve.
- `cheapest-experiment` — when the plan is a lower bound, buy information before committing.
- Methodology counterpart: [methodologies/scientific-methods/bayesian-evidence-updating.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/scientific-methods/bayesian-evidence-updating.md) — the outside-view prior construction this skill operationalises.

## Anti-patterns

- Do **not** cherry-pick the class after seeing which one flatters the plan; name candidates first.
- Do **not** run a class of one ("last year's project took 8 months"); n < 3 is refused.
- Do **not** adjust away the base rate: a "correction" landing below the class median is the planning fallacy in a spreadsheet.
- Do **not** summarise a skewed overrun class by its mean; report P50/P80/P90.
- Do **not** stack an uplift on contingency already inside the estimate; state the inside ratio (1.2, not 1.0).

## Reference

- D. Kahneman and A. Tversky, "Intuitive Prediction: Biases and Corrective Procedures," *TIMS Studies in Management Science* 12:313–327, 1979. https://doi.org/10.1017/CBO9780511809477.031
- D. Kahneman and D. Lovallo, "Timid Choices and Bold Forecasts: A Cognitive Perspective on Risk Taking," *Management Science* 39(1):17–31, 1993. https://doi.org/10.1287/mnsc.39.1.17
- D. Lovallo and D. Kahneman, "Delusions of Success: How Optimism Undermines Executives' Decisions," *Harvard Business Review* 81(7):56–63, July 2003. https://hbr.org/2003/07/delusions-of-success-how-optimism-undermines-executives-decisions
- B. Flyvbjerg, "From Nobel Prize to Project Management: Getting Risks Right," *Project Management Journal* 37(3):5–15, 2006. https://doi.org/10.1177/875697280603700302
- HM Treasury, *Supplementary Green Book Guidance: Optimism Bias*, London, 2003 (GOV.UK, 2013). https://www.gov.uk/government/publications/green-book-supplementary-guidance-optimism-bias
- P. E. Tetlock and D. Gardner, *Superforecasting: The Art and Science of Prediction*, Crown, 2015, ch. 5 and Appendix commandment 3. ISBN 978-0-8041-3669-3
- A. Hájek, "The Reference Class Problem is Your Problem Too," *Synthese* 156(3):563–585, 2007. https://doi.org/10.1007/s11229-006-9138-5
