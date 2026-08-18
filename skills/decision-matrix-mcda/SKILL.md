---
name: decision-matrix-mcda
description: "Ranks several options against weighted criteria with a decision matrix / multi-criteria decision analysis (Heuer & Pherson's Decision Matrix; Saaty's AHP pairwise comparisons for the weights, with a consistency check) and reports how robust the winner is to weight and score changes. Use when a choice has 3+ options and competing criteria — \"which of these vendors/platforms/projects to pick?\", \"build a weighted decision matrix\", \"derive criteria weights with AHP pairwise comparisons\", \"score these options against the criteria\". Not for ranking rival explanations of a cause (use `analysis-of-competing-hypotheses`) or picking the smallest validating test (use `cheapest-experiment`)."
license: MIT
metadata:
  category: decision-strategy
  method: Weighted Decision Matrix / Multi-Criteria Decision Analysis (MCDA) with AHP weights
  origin: Thomas L. Saaty (AHP, 1980); Ralph L. Keeney and Howard Raiffa (additive value model, 1976); Heuer and Pherson (Decision Matrix, SAT 3rd ed., 2019)
  version: "2.0.0"
---
# Weighted Decision Matrix (MCDA)

Trade-off choices fail in two ways: the loudest criterion decides, or the numbers are arranged afterwards to bless a favourite. A weighted decision matrix (Heuer & Pherson's Decision Matrix, 2019; Keeney & Raiffa's additive value model, 1976) makes the trade-off explicit: state criteria, weight them, score every option on a common scale, add up. Saaty's Analytic Hierarchy Process (1980) derives the weights from pairwise judgements and flags contradictory ones with a **consistency ratio**. The payoff is the sensitivity analysis: how little must change for the winner to change.

## When to invoke

Invoke when:

- A choice has 3+ options and 3+ criteria pulling in different directions: "which of these four platform vendors?".
- Someone asks for "a weighted scoring", "a decision matrix", "criteria weights" or "AHP".

Do NOT invoke when:

- The rivals are *explanations* of something that happened — use `analysis-of-competing-hypotheses`.
- The question is "what is the smallest test that validates this bet?" — use `cheapest-experiment`.
- One option dominates every criterion, or a hard constraint leaves one standing — no matrix needed.
- The job is to stress-test a decision already taken — use `premortem-analysis` or `key-assumptions-check`.

## Procedure — seven steps

### 1 — Frame the decision and the options

State the decision in one sentence ("which programme gets the FY27 discretionary R&D budget?"). List ≥ 3 options, always including the status quo. Screen out options that violate a hard constraint before scoring — constraints filter, criteria trade off.

### 2 — Define the criteria

Pick 3–7 criteria that cover what matters, do not overlap and are measurable per option. Give each a direction (benefit or cost) and a stated scale (1–5 anchors) or raw unit. The additive model assumes preferential independence (Keeney & Raiffa): the trade-off between two criteria must not depend on a third's level.

### 3 — Elicit the weights and check consistency

State weights directly (sum 1) or run Saaty's pairwise comparisons: per pair, "how much more important is A than B?" on the 1–9 scale (1 equal … 9 extreme; 2/4/6/8 between; reciprocals the other way). Weights are the principal eigenvector of the reciprocal matrix. Compute λmax, CI = (λmax − n)/(n − 1), CR = CI/RI with Saaty's random index (n = 3..10 → 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49, Saaty 1980; re-simulations give lower values — Alonso & Lamata 2006 — pushing CR up, so a borderline gate can flip). **CR ≤ 0.10 is acceptable; above it, revisit the most inconsistent judgement and re-elicit**.

### 4 — Score the options and normalise

Score every option on every criterion with a cited source, then map to a common 0–1 "higher is better" scale, direction-aware: min–max (`(x − lo)/(hi − lo)` for benefits, `(hi − x)/(hi − lo)` for costs — prefer a stated global range over the observed min/max) or ratio (`x/max`; costs `min/x`).

### 5 — Compute weighted totals and rank

Total for option j = Σ w_i · v_ij. Rank descending; report the margin between the top two, absolute and as a share of the leader's score. Do the arithmetic in the tool, never in prose.

### 6 — Run the sensitivity analysis

Answer three questions numerically (Belton & Stewart, 2002): (a) per criterion, at what weight does the leader change? (b) which single score cell needs the smallest change to flip the leader? (c) does dropping a non-leading option reorder the rest? Say exactly what the leader hinges on.

### 7 — Report

Fill the template: ranking, margin, weights and CR, the three sensitivity answers, and the load-bearing assumptions.

## Output template

```
## Decision matrix — {decision, one sentence}

**Options:** {O1 …} (incl. status quo); screened out: {option — constraint}
**Criteria & weights** ({direct | AHP, CR {0.xx}}): {C1 (direction, scale)} {w1} · {C2} {w2} · …

**Ranking (weighted total, 0–1):** 1. {O} {0.xxx} · 2. {O} {0.xxx} · 3. {O} {0.xxx}
**Margin top two:** {0.xxx} ({xx}% of the leader's score)

**Sensitivity:**
- Weights: leader holds unless {Ck} {falls below | rises above} {0.xx} (from {0.xx}) → {O}
- Scores: most fragile cell {O × Ck} — {raw} → {raw'} flips the leader to {O}
- Rank reversal on dropping/adding an option: {none | pair, condition}

**Assumptions & uncertainties:** {criteria independence; weakest scores; what to re-source before committing}
```

Every field is mandatory. A ranking without the sensitivity block is an opinion with decimals.

## Worked example

Decision: *which of four R&D programmes gets the FY27 discretionary budget?* Options O1 status quo, O2 solid-state cell pilot line, O3 AI materials-discovery platform, O4 flow-battery demonstrator. Criteria C1 strategic fit (1–5), C2 expected NPV (EUR m), C3 time to first revenue (months, cost), C4 technical risk (1–5, cost), C5 capability fit (1–5). Weights come from a 5 × 5 pairwise matrix (`examples/rd-portfolio.json`); `python3 scripts/mcda.py report --file examples/rd-portfolio.json` prints (abridged):

```
lambda_max = 5.0555   n = 5   CI = (lambda_max - n)/(n - 1) = 0.0139   RI(n=5) = 1.12   CR = CI/RI = 0.0124
Verdict: consistent (CR 0.012 <= 0.10) — weights usable.
Weights (AHP principal eigenvector of the pairwise matrix): C1 0.334, C2 0.321, C3 0.096, C4 0.159, C5 0.090

Opt  Option                                   C1       C2       C3       C4       C5    Total  Rank
     normalised (0-1, higher = better)
O1   Status quo (incremental roadmap)      0.500    0.000    1.000    1.000    1.000    0.512     3
O2   Solid-state cell pilot line           1.000    1.000    0.000    0.250    0.500    0.740     1
O3   AI materials-discovery platform       0.750    0.625    0.500    0.500    0.750    0.646     2
O4   Flow-battery demonstrator             0.500    0.375    0.250    0.500    0.250    0.413     4
Margin between top two: O2 - O3 = 0.094 (12.7% of the leader's score)

Break-even weights (one criterion varied, the others rescaled proportionally):
  C2   w = 0.321  leader changes to O1 if w falls below 0.120 (shift of 0.200)
Most sensitive score cells (smallest rescoring that flips the leader; '!' = within +/- 1 raw units):
    O3 x C2: raw 9 -> 11.34 (+2.34, 10% of the criterion's range) -> leader becomes O3
Rank reversal (leave-one-out): none — dropping any non-leading option keeps the survivors' order
```

Reading: O2 leads by 0.094; the lead survives every weight break-even (smallest shift 0.14, on C3) and any one-point rescoring on the 1–5 criteria, but an EUR 2–3 m error in either NPV estimate hands it to O3. Recommendation: O2, conditional on re-estimating both NPVs.

## Verification

Before shipping:

- [ ] ≥ 3 options including the status quo; hard constraints used as screens, not criteria.
- [ ] Criteria non-redundant and preferentially independent; none restates another.
- [ ] Weights sum to 1; if AHP, CR ≤ 0.10 — recompute with `scripts/mcda.py weights`.
- [ ] Every cell has a sourced raw score; cost criteria reversed before weighting.
- [ ] Totals and margin recomputed by the tool, not typed from memory.
- [ ] Sensitivity block present — break-even weights, most fragile cell, rank-reversal check.

## Companion tool

`scripts/mcda.py` (stdlib only, deterministic) does steps 3–6 from a JSON case file: `weights` — principal eigenvector by power iteration, λmax, CI, RI, CR and verdict (exit 1 when CR > 0.10); `score` — direction-aware normalisation (`--normalise minmax|ratio|none`; stated `range` = global scale), totals, ranking, margin; `sensitivity` — break-even weights, leader-flipping score cells, leave-one-out rank reversal; `report` — all of it in template order (`--json`, `--demo`).

```bash
python3 scripts/mcda.py weights --file pairwise.json     # AHP weights + CR verdict
python3 scripts/mcda.py report --file case.json --normalise minmax
python3 scripts/mcda.py --selftest                       # hand-verified checks
```

## Pair with adjacent skills

- `analysis-of-competing-hypotheses` — ranks *hypotheses about causes*, not options.
- `key-assumptions-check` — audit the premises behind weights and scores.
- `estimate-market-size` — re-source the market/revenue inputs behind fragile cells.
- `cheapest-experiment` — the smallest test that narrows the cell the winner hinges on.
- `premortem-analysis` — stress-test the winner after the matrix picks it.
- `three-horizons` — tag options on different horizons first so criteria are horizon-aware.

## Anti-patterns

- Do **not** score two criteria that measure the same thing (cost and NPV) — correlated criteria double their weight silently.
- Do **not** let weights carry hidden scores ("cost matters more *because* option A is cheap").
- Do **not** present three-decimal totals as measurements; report the margin and what flips it.
- Do **not** proceed with CR > 0.10 — the eigenvector of contradictory judgements is a number, not a preference.
- Do **not** ignore rank reversal: if adding a dud option reorders the front-runners, the normalisation is deciding.
- Do **not** launder a decision already taken; if criteria or weights were chosen after seeing the scores, say so and start over.

## Reference

- T. L. Saaty, *The Analytic Hierarchy Process: Planning, Priority Setting, Resource Allocation*. New York: McGraw-Hill, 1980. ISBN 0-07-054371-2.
- T. L. Saaty, "How to make a decision: The Analytic Hierarchy Process," *European Journal of Operational Research* 48(1):9–26, 1990. https://doi.org/10.1016/0377-2217(90)90057-I — CI/CR and the 10% rule; matrices reproduced in the tool's selftest.
- J. A. Alonso and M. T. Lamata, "Consistency in the Analytic Hierarchy Process: A New Approach," *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, vol. 14, no. 4, pp. 445–459, 2006. doi:10.1142/S0218488506004114 — re-simulated random indices, lower than Saaty's 1980 table.
- R. L. Keeney and H. Raiffa, *Decisions with Multiple Objectives: Preferences and Value Tradeoffs*. New York: Wiley, 1976; Cambridge University Press, 1993. ISBN 0-521-43883-7.
- V. Belton and T. J. Stewart, *Multiple Criteria Decision Analysis: An Integrated Approach*. Boston: Kluwer, 2002. https://doi.org/10.1007/978-1-4615-1495-4.
- R. J. Heuer Jr. and R. H. Pherson, *Structured Analytic Techniques for Intelligence Analysis*, 3rd ed. Thousand Oaks, CA: CQ Press / SAGE, 2019, ch. 10, §10.7 "Decision Matrix".
