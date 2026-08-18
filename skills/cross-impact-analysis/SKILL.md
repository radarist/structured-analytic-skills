---
name: cross-impact-analysis
description: "Builds an N x N cross-impact matrix over a set of events or variables, rating each ordered pair's direct influence, then computes direct-stage MICMAC influence/dependence rankings that separate strategic levers from indicators and flags asymmetric pairs for re-rating (Gordon & Hayward, Futures, 1968; Godet's structural analysis). Use when asked \"how do these trends affect each other?\", \"build a cross-impact matrix\", \"which of these drivers actually drive the system?\", \"run MICMAC on these variables\" or \"if X happens, does Y become more likely?\". Not for eliciting the underlying estimates (use `delphi-method`) or writing scenario narratives (use `scenario-planning`)."
license: MIT
metadata:
  category: foresight
  method: Cross-impact analysis with MICMAC-style structural analysis (direct stage)
  origin: Theodore J. Gordon & H. Hayward, 1968 (cross-impact matrix); Michel Godet and colleagues, 1970s onward (MICMAC structural analysis)
  version: "2.0.0"
---
# Cross-Impact Analysis

Cross-impact analysis asks what single-trend forecasting skips: if event i occurs, what happens to event j? Theodore J. Gordon and H. Hayward introduced the matrix form in *Futures* in 1968: forecasting events independently silently assumes they do not interact. Every ordered pair (i→j) gets its own judgement, so the matrix is asymmetric by construction, and the arithmetic over it — row totals as influence, column totals as dependence, in the MICMAC structural-analysis tradition of Michel Godet and colleagues — sorts the set into levers, relays, indicators and background. That arithmetic is MICMAC's **direct stage** only: full MICMAC raises the matrix to successive powers for indirect influence, which this skill does not compute — a variable acting only through intermediaries ranks lower here. Its principle: ratings are judgement, but the ranking and classification are reproducible arithmetic, done in code. It prevents scenario sets that combine mutually exclusive elements, and attention spent on variables that reflect the system rather than move it.

## When to invoke

Invoke when:

- Several trends or events interact and the question is which drive the rest: "how do these trends affect each other?".
- A matrix method is named: "build a cross-impact matrix", "run MICMAC on these variables".
- A scenario set needs a consistency check before its combinations are trusted.

Do NOT invoke when:

- The ratings still need eliciting from experts — run `delphi-method` first.
- The deliverable is the scenario narratives — use `scenario-planning`; this skill is its consistency engine.
- Fewer than five items interact — reason about the pairs directly.
- Behaviour over time with feedback is the question — cross-impact is a static snapshot.
- Downstream consequences of one change are wanted — use `futures-wheel`.

## Procedure

### 1 — Curate the event or variable set

Define 8–25 events or variables, each operational: a falsifiable state with a threshold and date ("carbon price reaches $100/t"), not a theme ("climate policy"). Above 25 items, cluster and merge first — the matrix grows as N². Output: item list with definitions.

### 2 — Choose the mode and gather any priors

Impact mode rates signed influence on −3…+3 and needs no priors. Probability mode uses conditional probabilities P(j|i) and needs each event's standalone probability first, classically from an expert panel. Record the mode: arithmetic and reading differ. Output: mode note and priors.

### 3 — Rate the matrix cell by cell

For each **ordered** pair (i→j), judge the direct impact of i on j — −3 strong negative through 0 to +3 strong positive, or P(j|i) in probability mode. Judge i→j and j→i separately, never reciprocating: one-way influence is the method's most interesting finding. Require a rationale for every rating of magnitude 2 or more; aggregate raters by median. Output: matrix and rationale log.

### 4 — Audit consistency and asymmetry before computing

Flag pairs whose two directions diverge sharply with no story, rows that are entirely zero (autonomous, or a blind spot?), and strongly negative pairings. Resolve each by re-rating or writing down the story. Output: flag list.

### 5 — Compute influence and dependence in code

Run the companion tool or equivalent code — never sum rows by hand. It ranks influence (row totals) and dependence (column totals) and classifies each item: **determinants** (high influence, low dependence — levers), **relays** (high both — unstable amplifiers), **dependents** (low influence, high dependence — indicators), **excluded** (low both). Output: rankings and classification.

### 6 — Read the map and test its sensitivity

Translate the classification into a decision: act on determinants, watch relays, monitor dependents as the scoreboard. Name the cells whose flip would move an item between quadrants; mark contested ones for arbitration. Report classifications and ranges, never decimal authority. Output: strategic reading with sensitivity note.

## Output template

```
## Cross-impact analysis — {system or question}

Mode: {impact -3..+3 | conditional probability}   N: {n} events
Events: {numbered list with operational definitions}
Matrix: {N x N block or attached JSON}

Influence ranking (levers first): {event: score, …}
Dependence ranking (indicators first): {event: score, …}
Direct-stage MICMAC classification:
- Determinants (act here): {…}
- Relays (watch — unstable): {…}
- Dependents (monitor as indicators): {…}
- Excluded (background): {…}

Asymmetric pairs resolved: {pair → story or re-rating}
Strategic reading: act on {…}; watch {…}; monitor {…}
Sensitivity: flipping {i→j} would reclassify {event} — {resolved | flagged for arbitration}
Confidence: {low | medium | high} — ratings are judgement, not measurement
```

Mandatory fields: mode, operational definitions, both rankings, the four-quadrant classification, resolved asymmetric pairs and the sensitivity note.

## Worked example

System: the G20 energy transition, 2025–2035, four events — E1 carbon price reaches $100/t across the G20; E2 grid storage cost falls 50 %; E3 electric vehicles exceed 50 % of new car sales; E4 fossil-fuel subsidies phased out. Illustrative impact-mode ratings, rationale logged for every magnitude of 2 or more; input `examples/energy-transition.json`. Public analogues rating the same levers: the IEA *World Energy Outlook* and the IPCC AR6 scenario ensembles.

```
     E1   E2   E3   E4
E1 [  0,  +2,  +2,  +1 ]   carbon price makes storage and EVs more competitive, builds reform momentum
E2 [  0,   0,  +3,   0 ]   cheap batteries cheapen EVs; no direct policy effect
E3 [ -1,  +1,   0,   0 ]   EV scale spills into grid storage; falling oil demand softens the carbon-price case
E4 [ +2,  +1,  +3,   0 ]   subsidy phase-out aligns with pricing and raises fossil driving costs
```

`python3 scripts/crossimpact.py --file examples/energy-transition.json` returns influence E4 6, E1 5, E2 3, E3 2 and dependence E3 8, E2 4, E1 3, E4 1, classifying E1 and E4 as **determinants**, E3 as **dependent**, E2 as **excluded**, with no relays. It flags four asymmetric pairs at the default threshold (E1→E3 +2 vs E3→E1 −1 among them) and two at `--asym 3`. Reading: the policy levers are carbon pricing and subsidy reform; electric-vehicle share is the scoreboard, not a lever; storage cost moves the system but is barely moved by it, so treat it as exogenous. Sensitivity: E4→E1 is load-bearing — flipping it to 0 drops E4's influence to 4 and merges the determinant group, so it needs a human call.

## Verification

- [ ] Every event is operational: a falsifiable state with threshold and date, not a theme.
- [ ] The diagonal is zero, cells are inside the mode's bounds, and i→j was judged separately from j→i.
- [ ] Every rating of magnitude 2 or more carries a rationale.
- [ ] Influence and dependence totals came out of code, not mental arithmetic.
- [ ] Every flagged asymmetric pair was re-rated or given a story.
- [ ] The sensitivity note names cells whose flip would reclassify an item; contested ones are marked.

## Companion tool

`scripts/crossimpact.py` (stdlib only, Python 3.9+) computes the direct-stage MICMAC totals and rankings (no matrix powering), classifies the four quadrants, flags asymmetric pairs beyond a threshold, and validates bounds — ±3 in impact mode, 0–1 in probability mode, zero diagonal. Input is JSON (`events` + `matrix`, `mode` selects impact vs probability); a ready input for the worked example is in `examples/energy-transition.json`.

```
$ python3 scripts/crossimpact.py --file examples/energy-transition.json
Influence ranking (total impact exerted, row totals of |rating|):
  1. G20 fossil-fuel subsidies phased out  influence 6   net +6
  2. Carbon price reaches $100/t in G20    influence 5   net +5
  ...
Asymmetric pairs (|i->j - j->i| >= 2) - give each a one-line story or re-rate:
  Carbon price reaches $100/t in G20 -> EVs exceed 50% of new car sales: +2 vs -1
  ...

$ python3 scripts/crossimpact.py --file examples/energy-transition.json --asym 3
... 2 asymmetric pairs (only the ≥3 divergences) ...

$ python3 scripts/crossimpact.py --selftest
PASS: impact: influence totals
...
SELFTEST OK: all checks passed.
```

Usable without the tool — any spreadsheet's row/column sums do the same arithmetic.

## Pair with adjacent skills

- `delphi-method` — the classic source of standalone probabilities and cell ratings.
- `scenario-planning` — determinants make good axes; the matrix prunes inconsistent combinations.
- `steep-pestle-analysis` — supplies the rated driver inventory the matrix works on.
- `indicators-validation` — turns dependent variables into a diagnostic indicator set.
- `key-assumptions-check` — surfaces load-bearing cells before the map is trusted.
- Methodology counterpart: [methodologies/foresight/cross-impact-analysis.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/cross-impact-analysis.md).

## Anti-patterns

- Do **not** compute matrix arithmetic in prose; totals come out of code.
- Do **not** reciprocate automatically; a symmetric matrix hides the one-way levers.
- Do **not** rate cells without rationales; a bare +3 is uncheckable.
- Do **not** let N bloat past about 25; fatigue destroys rating quality.
- Do **not** present scores as measurement; report classifications and ranges.
- Do **not** skip the sensitivity pass; an uninterrogable matrix is a horoscope.

## Reference

- T. J. Gordon and H. Hayward, "Initial experiments with the cross impact matrix method of forecasting," *Futures*, vol. 1, no. 2, pp. 100–116, 1968. https://doi.org/10.1016/S0016-3287(68)80003-5
- T. J. Gordon, "Cross-Impact Analysis," ch. 9 in J. C. Glenn and T. J. Gordon (eds.), *Futures Research Methodology — Version 3.0*. Washington, DC: The Millennium Project, 2009. ISBN 978-0-9818941-1-9.
- J. Arcade, M. Godet, F. Meunier and F. Roubelat, "Structural Analysis with the MICMAC Method & Actors' Strategy with MACTOR Method," ch. 11 in *Futures Research Methodology — Version 3.0*. Washington, DC: The Millennium Project, 2009 — the full MICMAC method; only its direct stage is computed here.
- M. Godet, "Introduction to la prospective: Seven key ideas and one scenario method," *Futures*, vol. 18, no. 2, pp. 134–157, 1986. https://doi.org/10.1016/0016-3287(86)90094-7
- J. C. Duperrin and M. Godet, "SMIC 74 — A method for constructing and ranking scenarios," *Futures*, vol. 7, no. 4, pp. 302–312, 1975. https://doi.org/10.1016/0016-3287(75)90048-8
