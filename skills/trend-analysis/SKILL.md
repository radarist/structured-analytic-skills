---
name: trend-analysis
description: "Turns a trend claim into an evidence-checked trend statement, quantifies its rate, curvature and S-curve position from a time series, then projects it — naive extrapolation, logistic fit, or event-adjusted Trend Impact Analysis (Gordon) — with an assumption sheet, counter-trend scan and signposts. Use when asked \"is {X} actually growing or is it a fad?\", \"how far can this trend run?\", \"extrapolate this trend to 2030\", \"validate this trend claim\" or \"is {X} a megatrend?\". Not for publication and citation curves (use `assess-research-momentum`) or for placing a technology on the hype curve (use `apply-hype-cycle`)."
license: MIT
metadata:
  category: foresight
  method: Trend analysis with Trend Impact Analysis (TIA)
  origin: Theodore J. Gordon (Trend Impact Analysis), The Futures Group, 1970s; Fisher & Pry substitution model, 1971; Rogers' diffusion curve, 1962/2003
  version: "2.0.0"
---
# Trend Analysis

Trend analysis converts a claim that something is changing into a measured trajectory and, where evidence supports it, a projection whose assumptions are visible. Its core principle comes from Trend Impact Analysis, as Theodore J. Gordon set it out for the Millennium Project (2009): extrapolate the series surprise-free, then state the events that could bend it, each with a probability and an impact, so hidden assumptions become a challengeable sheet rather than a silent forecast. Two constraints keep projections honest: adoption saturates, so growth follows S-shaped rather than straight paths (Fisher & Pry, 1971; Rogers, 2003), and a claim is not a trend until multi-source evidence and a mechanism say so. It prevents projecting a one-source spike, and extrapolating a real trend past its ceiling.

## When to invoke

Invoke when:

- A trend claim needs testing or projecting: "is {X} actually growing or is it a fad?", "how far can this trend run?".
- A number is needed for a plan and the series exists: adoption share, unit cost, penetration, price.

Do NOT invoke when:

- The series is publication or citation counts for a research field — use `assess-research-momentum`.
- The question is hype-narrative placement — use `apply-hype-cycle`.
- Fewer than about five comparable observations exist — say so rather than fit a line to three points.
- The system is reflexive or hinges on a discontinuity (elections, asset prices) — use `scenario-planning`.
- Nothing is measured yet — use `horizon-scanning`.

## Procedure

Steps 3–4 are arithmetic: use the companion tool. Curve choice and caveats: `references/projection-methods.md`.

### 1 — State the trend as a falsifiable claim

Force the claim into *{quantity} is {rising | falling | shifting} at {rate} in {population or geography}, horizon {year}*. "AI is changing everything" is not analysable; "electric share of global new car sales to 2030" is. If quantity and population cannot be named, that statement is the deliverable. Output: trend statement.

### 2 — Validate the evidence: trend or fad

Gather series from at least two independent sources — official statistics, industry datasets, registries, studies — ideally spanning five years. Check the fad markers: single source, media-only coverage, spike-shaped series, no mechanism. Name the structural driver that would sustain the change (cost curve, demographics, policy, installed base). Verdict: VALIDATED, UNCERTAIN or FAD MARKERS; the latter two stop the analysis. Output: evidence table and verdict.

### 3 — Quantify rate, curvature and position on the curve

Compute absolute and relative change per period, then read curvature from the period gains: growing gains mean acceleration, constant gains a linear path, shrinking gains saturation. For adoption trends locate the position on the diffusion curve, first checking which quantity the series is. Rogers' adopter categories partition **cumulative** adopters, so his boundaries — below roughly 16 % cumulative adoption the innovator and early-adopter phase, 16–50 % the early majority, above 50 % later — can only be read off a cumulative-adoption series. An annual sales share, new-registration count or shipment share is a *flow*, and the 16 % marker does not apply to it: read a flow in the Fisher–Pry substitution frame instead, as the fraction *f* of new units the challenger has taken from the incumbent, whose f/(1−f) is linear in time while the substitution runs to completion. Output: trend profile with drivers and inhibitors.

### 4 — Project, with the assumption sheet attached

Choose a method and justify it: naive extrapolation for slow, structurally driven quantities; a logistic fit where a ceiling exists, stating that ceiling and the fit quality; Trend Impact Analysis where identifiable events could bend the curve — extrapolate the baseline, list events with probability and impact, show the arithmetic. Report one alternative shape. Output: projection and assumption sheet (drivers, ceiling, events).

### 5 — Scan for the counter-trend and collisions

Name the counter-trend the change provokes (globalisation and localism, digital and analogue revival) — discontinuities usually enter there — and any collision with other validated trends. Output: counter-trend note.

### 6 — Verify and emit the trend card

Recompute the rate and projection arithmetic from the quoted series, confirm every number traces to a dated source, then set signposts and a cadence. Output: trend card.

## Output template

```
## Trend card — {trend name}

Trend statement: {quantity} is {direction} at {rate} in {population/geography}; horizon {year}.
Validation: {VALIDATED | UNCERTAIN | FAD MARKERS} — {sources, span, mechanism}

Rate: {absolute and relative change per period}
Curvature: {accelerating | linear | saturating} — {period-gain evidence}
Curve position: {early | mid | late}
Drivers: {forces}   Inhibitors: {frictions}   Counter-trend: {the opposition it generates}

Projection to {horizon}: {naive | logistic | TIA} → {value or range}; alternative shape: {value}
Assumptions: {drivers persist; ceiling; events with P × impact}
Signposts: {indicator} — breaks the projection if {condition}; review every {cadence}
Confidence: {low | medium | high} — {reason}
```

Mandatory fields: trend statement, validation verdict with sources, assumption sheet, signposts, confidence. A projection without an assumption sheet may not ship.

## Worked example

Claim, mid-2025: "EVs are taking over — how far does this run?" Trend statement: electric vehicles (BEV + PHEV) as a share of global new car sales, rising, horizon 2030. Illustrative series, rounded from published EV outlook data: 4 % (2020), 9 % (2021), 14 % (2022), 18 % (2023), 21 % (2024). **Validation: VALIDATED** — five years of sustained rise, independent sources, a mechanism (battery cost learning plus fleet-emission mandates); not spike-shaped. Fits from `scripts/trend.py describe --demo` and `fit --demo`:

```
Change: 4.00 → 21.00 = +17.00 (+425.0%) over 4 periods
Rate:   +4.25 per period (average absolute change)
Curvature: saturating — period gains +5.00, +5.00, +4.00, +3.00
  naive     R² 0.9766   y = 4.00 + 4.25·(t − 2020)
  linear    R² 0.9898   y = 4.60 + 4.30·(t − 2020) — OLS slope +4.30 per period
  logistic  R² 0.9976   y = 22.84 / (1 + e^(−0.9708·(t − 2021.54))) — K 22.84, last = 91.9% of K
```

The series is a share of *new* sales, so it is a Fisher–Pry substitution fraction, not cumulative adoption, and Rogers' 16 % boundary does not read off it — cumulative EV share of the global fleet was far below 21 % in 2024. In the Fisher–Pry frame, f = 0.21 gives f/(1−f) = 0.27: the substitution is still early. The logistic ceiling of 22.84 % is an artefact of five points on one segment — the tool's own caveat — so the naive baseline is used and the fitted ceiling reported as the alternative shape. Baseline to 2030: 21 + 4.25 × 6 ≈ 46.5 %. TIA adjustment, reproduced by the tool below: subsidy rollback (P 0.5, −5), charging bottlenecks (P 0.4, −4), battery cost breakthrough (P 0.3, +3) → **43.3 %**, against a logistic alternative near 23 %. Assumptions: no deep recession, mandates not repealed. Counter-trend: hybrid resurgence and pushback on phase-out dates. Signposts: annual share print within ±3 points of track; battery pack prices; the EU 2035 review. Confidence: medium — policy-driven, reflexive to election cycles.

## Verification

- [ ] The trend statement names quantity, population or geography, rate and horizon.
- [ ] Two or more independent sources cover the series; each quoted number traces to a dated source.
- [ ] Rate, curvature and projection arithmetic were recomputed with `scripts/trend.py`.
- [ ] The chosen curve is reported with an alternative shape, its fit quality and the ceiling assumption.
- [ ] Every TIA event carries a probability and impact, and the adjustment arithmetic is shown.
- [ ] Signposts and a review cadence are set; an UNCERTAIN or FAD verdict stopped the analysis.

## Companion tool

`scripts/trend.py` (stdlib only) does the arithmetic of steps 3–4 on a `period,value` series (`--file series.csv|json` or `--series "2020:4,2021:9,…"`; ≥ 3 points, warns below 5). `describe`: n, span, CAGR, average change, doubling time, YoY table, curvature read, spike check (Iglewicz & Hoaglin modified z-score). `fit`: OLS linear, exponential (log-linear) and logistic S-curve (Fisher–Pry linearisation over a K grid), best shape by R² with the Meade & Islam lower-half caveat. `project --to 2030 [--model naive|linear|exponential|logistic|auto] [--ceiling K] [--event "label:P:impact"]`: per-model projections, ± 2·RMSE band (not a prediction interval), horizon multiple, TIA arithmetic. `--json` everywhere; `--demo` reproduces the worked example; `--selftest` self-checks.

```
$ python3 scripts/trend.py project --demo --to 2030 --model naive --event "subsidy rollback in a major market:0.5:-5" --event "charging bottlenecks:0.4:-4" --event "battery cost breakthrough:0.3:+3"
TIA adjustment (Gordon): baseline 46.50
     -2.50   subsidy rollback in a major market   (P 0.50 × -5.00)
     -1.60   charging bottlenecks                 (P 0.40 × -4.00)
     +0.90   battery cost breakthrough            (P 0.30 × +3.00)
         = 43.30   adjusted projection (net adjustment -3.20)
```

The skill is fully usable without the tool; it only removes arithmetic effort.

## Pair with adjacent skills

- `assess-research-momentum` — owns the bibliometric case: publication and citation curves.
- `horizon-scanning` — upstream: emerging issues become candidates once they have a series.
- `scenario-planning` — downstream: validated trends enter as predetermined elements.
- `triangulate-sources` — checks the evidence table when numbers came from web search.
- Methodology counterpart: [methodologies/foresight/trend-analysis.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/trend-analysis.md).

## Anti-patterns

- Do **not** project an unvalidated trend; an UNCERTAIN or FAD verdict is itself the deliverable.
- Do **not** fit a line to three points; below five observations the honest output is a data request.
- Do **not** extrapolate reflexive systems such as markets or elections.
- Do **not** pick the curve that gives the wanted answer; report an alternative shape.
- Do **not** ship a projection without its assumption sheet.
- Do **not** skip the counter-trend, where discontinuity usually enters.
- Do **not** treat the card as permanent; a stale trend keeps steering strategy.

## Reference

- T. J. Gordon, "Trend Impact Analysis," ch. 8 in J. C. Glenn and T. J. Gordon (eds.), *Futures Research Methodology — Version 3.0*. Washington, DC: The Millennium Project, 2009. ISBN 978-0-9818941-1-9 — the surprise-free baseline plus probability-weighted events of step 4.
- J. C. Fisher and R. H. Pry, "A simple substitution model of technological change," *Technological Forecasting and Social Change*, vol. 3, pp. 75–88, 1971. https://doi.org/10.1016/S0040-1625(71)80005-7
- E. M. Rogers, *Diffusion of Innovations*, 5th ed. New York: Free Press, 2003. ISBN 978-0-7432-5823-4 — adopter categories, which partition *cumulative* adopters; step 3 uses the 16 % boundary only on a cumulative series.
- N. Meade and T. Islam, "Modelling and forecasting the diffusion of innovation — a 25-year review," *International Journal of Forecasting*, vol. 22, no. 3, pp. 519–545, 2006. https://doi.org/10.1016/j.ijforecast.2006.01.005
