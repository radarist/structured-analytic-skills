---
name: assess-research-momentum
description: "Reads a scholarly result set for one research area — publication S-curve phase, citation velocity and acceleration, author and institution concentration — and reports a research-front or maturing verdict with the observation that would flip it. Use when asked \"is research on X heating up?\", \"is this a hot area or has it plateaued?\", \"what does the publication trend for X look like?\" or \"how much academic attention is X getting?\". Not for market perception of a technology (use `apply-hype-cycle`) or for synthesising what the papers actually found (use `systematic-review`)."
license: MIT
metadata:
  category: technology-assessment
  method: Bibliometric momentum assessment (publication S-curve + citation velocity)
  origin: Derek J. de Solla Price, Little Science, Big Science, 1963
  version: "2.0.0"
---
# Assess Research Momentum

Derek J. de Solla Price showed in *Little Science, Big Science* (1963) that scientific literature grows exponentially and that such growth must eventually saturate — the exponential is the early arm of a logistic, and where a field sits on that curve says more than its current volume does. Bornmann and Mutz (2015) put the modern global rate at roughly 8–9% per year, doubling every eight to nine years: the baseline any one area is judged against, since a field growing at 8% merely keeps pace with science at large. This skill reads *one* result set's metadata — counts by year, citations, authors, institutions — into a momentum verdict, preventing the two standard errors: reading one year's spike as a trend, and reading volume as importance.

## When to invoke

Invoke when:

- Asked "is research on X heating up?", "is X a hot area?", "what is the publication trend for X?" or "is the field maturing or fading?".
- A technology assessment needs a leading indicator (literature momentum moves years before deployment evidence), or a claim that a field is "exploding" needs a number attached.

Do NOT invoke when:

- The question is market perception or "is X overhyped?" — use `apply-hype-cycle`; momentum is an input to a phase placement, not the placement.
- A reproducible synthesis of what the papers found is needed — use `systematic-review`; this skill reads metadata, not findings.
- The question is whether the technology is deployable — use `score-technology-readiness`; a field can be red-hot at TRL 2.
- The series is a market, demographic or societal trend rather than a bibliometric one — use `trend-analysis`.
- Fewer than ~15 papers or three years of coverage exist: report the sparsity instead of forcing a verdict.

## Procedure

### 1 — Gather the result set

Query a scholarly index — OpenAlex (`works?search=…` with `group_by=publication_year` returns per-year counts), Semantic Scholar, Crossref or an arXiv listing. Narrow the query the way a technology is narrowed: "AI" is not assessable, "diffusion models for protein structure prediction" is. Pull a multi-year window and record per paper: publication year, citation count, authors, affiliations where available. State the index, query string and window — the call is reproducible only if the search is.

### 2 — Fit the publication curve

Bucket papers by publication year and read the shape: **rising** (counts increasing, no plateau), **plateau** (flat for two or more years after a rise), **decline** (falling for two or more years), or **too sparse to call**. With four or more buckets, fit the logistic using `scripts/momentum.py fit` and report K, r, t₀, R² and the phase — emergent below 20% of K, growth 20–80%, mature above 80%. A low R² is itself a finding: the field is not on a single S-curve.

### 3 — Measure citation velocity and acceleration

Compute mean citations per paper per year, then compare the recent half of the window against the early half: **accelerating**, **steady** or **decelerating**. `scripts/momentum.py velocity` reports year-on-year growth, CAGR and the acceleration sign. Papers under a year old have structurally noisy citation counts — say so rather than reading a low count as neglect.

### 4 — Measure concentration

Count distinct authors and institutions across the set. A handful of labs means nascent or proprietary work, not a broad front; many institutions means no single group can dominate, and a widening count over the window is the strongest sign of a genuine research front. Where affiliation data is missing, say the concentration read is unavailable rather than inferring it from author names.

### 5 — Call the verdict and name what would flip it

Call **research front** (rising curve, accelerating citations, broadening concentration) or **maturing/mature** (plateau or decline, steady or decelerating citations, concentration no longer broadening). Report mixed evidence as mixed, naming the dominant signal. State the observation that would flip the call, and compare growth against the 8–9% baseline so "growing" means faster than science at large.

## Output template

```
## Research momentum — {area}

**Query:** {index} · `{query string}` · window {yearFrom}–{yearTo} · {N} papers
**Publication trend:** {rising | plateau | decline | too sparse} — {counts by year}
**S-curve fit:** K {value} · r {value}/yr · t₀ {year} · R² {value} · {pct}% of K → {emergent | growth | mature}
**Citation velocity:** {mean cites/paper/yr} · CAGR {pct}% · {accelerating | steady | decelerating}
**Concentration:** {n} authors / {m} institutions — {nascent | broad front} · {widening | stable | narrowing}
**Versus baseline:** {pct}%/yr against ~8–9%/yr global literature growth
**Verdict:** {research front | maturing | mature | too sparse to call}
**Confidence:** {low | medium | high} — {reason}
**What would flip it:** {next-window observation}
```

Mandatory fields: query and window, publication trend, citation-velocity call, verdict, confidence with its reason, and what would flip it. A verdict without the query that produced it cannot be reproduced and must not ship.

## Worked example

Area: CRISPR-based genetic screens (illustrative counts). The series are in `examples/pubs.csv` and `examples/cites.csv`; every number below comes from `scripts/momentum.py`.

```
$ python3 scripts/momentum.py fit --file examples/pubs.csv
  data:            11 points, 2014–2024
  K (capacity):    405.3 papers/year
  r (growth rate): 0.7372 /year
  t0 (midpoint):   2019.8
  R²:              0.9993
  current level:   388.0 = 95.7% of K (year 2024)
  doubling time:   n/a (past inflection — level already exceeds K/2)
  phase:           mature (<20% of K = emergent, 20–80% = growth, >80% = mature)

$ python3 scripts/momentum.py velocity --file examples/cites.csv
  YoY:    2020 +50.0%, 2021 +61.1%, 2022 +72.4%, 2023 +72.0%
  CAGR:   +63.6% per year (2019–2023)
  signal: accelerating (recent-half mean YoY − early-half = +16.7 pp)
```

Reading: the two signals disagree, and the disagreement is the finding. Publication output has flattened — 388 papers in 2024 against a fitted ceiling of 405.3, so 95.7% of K, squarely mature, with the midpoint back in 2019.8 and a near-perfect fit (R² 0.9993). Citations are still accelerating at 63.6% CAGR, because citation accumulation lags publication by two to three years. The honest verdict is **maturing**: the publication front has closed while earlier output is still being absorbed — the pattern that precedes a citation plateau two windows later. What would flip it: 2025–2026 adding 2× the 2024 count, which no logistic at K ≈ 405 can accommodate; that would be a new sub-front, not a continuation.

## Verification

- [ ] The index, query string and window are stated so the result set can be re-pulled.
- [ ] At least three yearly buckets and ~15 papers exist; below that the output says "too sparse to call".
- [ ] Curve and velocity numbers were recomputed with `scripts/momentum.py`, not estimated by eye, and the R² is reported — a poor fit is a finding, not something to smooth over.
- [ ] The growth rate is compared against the ~8–9%/yr global baseline before the field is called fast-growing.
- [ ] Disagreement between the publication curve and the citation curve is reported, not averaged.
- [ ] The verdict names a specific observation that would flip it.

## Companion tool

`scripts/momentum.py` (Python 3.9+, stdlib only) automates steps 2 and 3.

```bash
python3 scripts/momentum.py fit --file examples/pubs.csv        # K, r, t0, R², %-of-K, doubling time, phase
python3 scripts/momentum.py velocity --file examples/cites.csv  # YoY growth, CAGR, acceleration sign
python3 scripts/momentum.py --selftest                          # known-answer checks
```

`fit` grid-searches (K, r, t₀) for the logistic K / (1 + e^{−r(t − t₀)}) minimising SSE, then refines by pattern search; it needs four or more yearly buckets. `velocity` compares recent-half against early-half mean year-on-year growth. Both take a `year,value` CSV with optional header and comments. Usable without the tool, but the fit is guesswork by hand.

## Pair with adjacent skills

- `apply-hype-cycle` — momentum is the quantitative input to a phase placement, which also needs press, funding and deployment indicators.
- `systematic-review` — reach for PRISMA when the content of the papers, not their volume, is the question.
- `score-technology-readiness` — orthogonal: TRL tracks what has been built, not what is written about.
- `trend-analysis` — the general trend validator for non-bibliometric series; this is the bibliometric case.
- `triangulate-sources` — corroborate a call against non-academic signals before treating it as decision-grade.

## Anti-patterns

- Do **not** call momentum from a single year's count; a call needs three or more yearly buckets.
- Do **not** equate citations with quality — this measures attention, not truth, and heavily cited work includes work cited for being wrong.
- Do **not** force a verdict on fewer than ~15 papers; report low confidence and say the set is too sparse.
- Do **not** call a field fast-growing without comparing it to the ~8–9%/yr global baseline.
- Do **not** present a momentum reading as a hype-cycle phase; a rising curve feeds that placement, it is not the placement.
- Do **not** extrapolate the fitted K as a prediction; it describes the observed window and moves as the window extends.

## Reference

- D. J. de Solla Price, *Little Science, Big Science*. New York: Columbia University Press, 1963 — exponential growth of the literature and its eventual logistic saturation; the basis of the curve read.
- L. Bornmann and R. Mutz, "Growth rates of modern science: A bibliometric analysis based on the number of publications and cited references," *Journal of the Association for Information Science and Technology*, vol. 66, no. 11, pp. 2215–2222, 2015. doi:10.1002/asi.23329 — the ~8–9%/yr modern growth rate used as the baseline.
- Phase thresholds (emergent < 20% of K, growth 20–80%, mature > 80%) and the half-window acceleration test are this skill's operationalisation in `scripts/momentum.py` — conventions, not published standards.
