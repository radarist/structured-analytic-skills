---
name: scenario-planning
description: "Builds a small set of divergent, equally plausible futures on the two most consequential uncertainties — the Shell/GBN 2×2 scenario method — and stress-tests a strategy against every one of them, ending with robust moves and signposts to watch. Use when the horizon is 3–10 years and a single forecast would be false precision — \"scenario planning for this market\", \"what are the plausible futures for X by 2030?\", \"build 2x2 scenarios\", \"alternative futures for the sector\". Not for one dated prediction about a single trend (use `foresight`) or for a macro-factor inventory on its own (use `steep-pestle-analysis`)."
license: MIT
metadata:
  category: decision-strategy
  method: Scenario planning (Shell/GBN deductive 2×2)
  origin: Pierre Wack, Royal Dutch/Shell, 1985; Peter Schwartz / Global Business Network, 1991
  version: "2.0.0"
---
# Scenario Planning

Scenario planning builds a small set of divergent but **equally plausible** stories about how the environment around a decision could unfold, then tests the strategy against each. It comes from Pierre Wack's planning group at Royal Dutch/Shell (Wack, *Harvard Business Review*, 1985), codified by Peter Schwartz and Global Business Network (Schwartz 1991; Ogilvy & Schwartz 2004) — the Shell/GBN tradition; the deductive 2×2 on two critical uncertainties is the GBN form. Its core principle: scenarios are not forecasts — no probabilities are assigned, no scenario is "most likely"; their job is to change the decision-maker's mental model and expose strategies that work in only one future. It prevents the official-future failure: betting on a single extrapolation and being surprised.

## When to invoke

Invoke when:

- A decision depends on how the environment evolves over 3–10 years and at least two material uncertainties could swing either way — "how will enterprise AI procurement look in 2030?", "plausible futures for grid storage".

Do NOT invoke when:

- The question is "when will X happen?", has one uncertainty, or a horizon under 12 months — one dated prediction is `foresight`; a trend's rate and curvature is `trend-analysis`.
- The question is about the present — `five-forces-analysis` (industry structure) or `position-competitor` (market map).
- A probability on a specific variable is needed — `bayesian-update` or `delphi-method` estimate it; scenarios do not.
- Only the macro-factor inventory is wanted — `steep-pestle-analysis` produces it and feeds step 2.
- The consequences of one already-decided change are wanted — `futures-wheel`.

## Procedure — the deductive 2×2 in seven steps

### 1 — Frame the focal question and horizon

Name the decision the scenarios must inform, the decision-maker and the horizon (3–10 years). "Commit €40 M to an in-house claims platform over 2027–2030?" is a focal question; "the future of AI" is not. A scenario set with no decision behind it is entertainment.

### 2 — Identify the driving forces

List 10–20 forces that could shape the outcome across social, technological, economic, environmental and political/legal categories (`steep-pestle-analysis` is the front-end). For each write **which way it could swing** over the horizon, not just what it is — "model capability: saturates vs keeps compounding", not "AI models".

### 3 — Rank by impact and uncertainty

Rate every force Low / Medium / High on impact on the focal question and on uncertainty over the horizon. High impact, low uncertainty = **predetermined elements**, constants in every scenario. High impact, high uncertainty = the **critical uncertainties** the scenarios branch on. Low-impact forces leave the axes but may reappear as texture.

### 4 — Choose two critical uncertainties as axes

Pick two that are **independent** (one end does not predict the other), **distinct** (they drive different dynamics) and **bipolar** (two clear, plausible ends each). If "axis X already implies axis Y" can be argued, the corners collapse into a diagonal — pick again. Two axes give four scenarios — the deliberate limit of the deductive form.

### 5 — Build and narrate the four scenarios

Each corner is a scenario with a **memorable name** carrying its logic, a present-tense **vignette** of the world at the horizon (3–5 sentences, internally consistent, containing the predetermined elements), two or three observable **leading indicators** that would show the world heading there, and the **implication for the focal question**. All four are **equally plausible**: "Do not assign probabilities to the scenarios. Do not categorize them as either the most or least likely" (Ogilvy & Schwartz 2004); Wack insisted on the same (Millett 2009). A corner nobody believes means the axes are wrong.

### 6 — Wind-tunnel the strategy

Test each candidate move against all four. Moves that hold in three or four are **robust**. Moves that pay off in one corner are **options**, taken only when that corner's indicators appear. Name at least one assumption the current plan makes that only one scenario supports, and set a **monitoring plan**: which indicator, how often, pointing to which scenario.

### 7 — Report

Fill the output template below, stating explicitly that the scenarios are equally plausible and carry no probabilities. Every implication must answer the focal question, not a general one.

## Output template

```
## Scenario set — {focal question}

**Focal question:** {decision} · **Decision-maker:** {who} · **Horizon:** {year}
**Forces reviewed:** {N} · **Predetermined elements:** {element — why baked in}; …

**Axes:** X: {uncertainty} — {end A} ↔ {end B} · Y: {uncertainty} — {end A} ↔ {end B}
**Independence check:** {why X does not predict Y}

| | X = {end A} | X = {end B} |
|---|---|---|
| **Y = {end A}** | **{Name 1}** — {one-line logic} | **{Name 2}** — {one-line logic} |
| **Y = {end B}** | **{Name 3}** — {one-line logic} | **{Name 4}** — {one-line logic} |

Per scenario: **Vignette** {3–5 sentences, present tense} · **Leading indicators** {2–3 signposts} · **Implication** {what the decision-maker does}

**Robust moves (hold in ≥ 3 scenarios):** {move — scenarios}; …
**Options (one scenario):** {move — take when {indicator} appears}; …
**Assumption only {Name} supports:** {…}
**Monitoring plan:** {indicator — cadence — scenario}; …
**Plausibility statement:** all four scenarios are equally plausible; no probabilities are assigned.
```

Mandatory: focal question and horizon, predetermined elements, both axes with the independence check, four named scenarios with indicators and implications, robust moves, monitoring plan, plausibility statement.

## Worked example

Illustrative case (all figures invented): a mid-size European insurer must decide whether to commit €40 M over 2027–2030 to an in-house claims-automation platform or rent one. Fourteen forces reviewed; two predetermined elements — EU AI Act high-risk obligations from August 2026, and claims volume growing about 3 % a year — appear in every scenario. Axes: X = **model capability** (saturating ↔ compounding); Y = **regulatory regime for automated decisions** (permissive ↔ restrictive). Independence check: 2024–2026 capability gains arrived under both permissive and restrictive regimes.

| | Capability compounding | Capability saturating |
|---|---|---|
| **Permissive regime** | **Cambrian Agents** — thousands of vertical agents; AI-native insurers underprice incumbents by 15–20 % on expenses | **Utility Plateau** — models a commodity layer; competition on data, distribution and brand |
| **Restrictive regime** | **Walled Garden** — three or four certified vendors dominate; capability concentrated in the largest platforms | **Frozen Winter** — investment dries up; deployment stalls in compliance review |

Leading indicators (examples): Cambrian — two or more agent-native insurers above 100,000 policies by 2028; Walled Garden — a certification scheme with under five approved vendors by 2029; Frozen Winter — sector AI capex down 30 % year on year.

Robust moves: build the claims-data pipeline and labelling capability (needed in all four); rent the model layer (wins in three corners; not fatal in Cambrian Agents). Option: a 20-engineer in-house agent team only if two Cambrian indicators appear before 2028. Assumption only Cambrian Agents supports: a proprietary model still differentiates in 2030. Monitoring: vendor-certification counts (quarterly), sector capex (annually), agent-native competitor policies (quarterly). All four scenarios are equally plausible; no probabilities are assigned.

## Verification

Before the set ships:

- [ ] Independence re-checked: state one plausible way each corner could exist; near-duplicate corners mean correlated axes — re-pick.
- [ ] No probabilities, weights or "most likely" labels appear; the plausibility statement is present.
- [ ] Every scenario contains the same predetermined elements and at least two observable leading indicators.
- [ ] Every robust move was re-read against all four scenarios; each option names its triggering indicator.
- [ ] Focal question, decision-maker and horizon are stated; every implication answers that question.

## Pair with adjacent skills

- `steep-pestle-analysis` — the coverage-disciplined driver inventory that feeds steps 2–3.
- `foresight` — one dated, falsifiable prediction for single-branch or short-horizon questions.
- `cross-impact-analysis` — checks the internal consistency of the set when forces interact strongly.
- `futures-wheel` — consequences within one chosen scenario; `backcasting` — the route to a preferred one.
- `bayesian-update` / `delphi-method` — a probability on a specific variable; the scenarios themselves stay unweighted.
- `premortem-analysis` — stress-tests the plan chosen after wind-tunnelling.
- Methodology counterpart: [methodologies/foresight/scenario-planning.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/scenario-planning.md) — history, variants, facilitation detail.

## Anti-patterns

- Do **not** assign probabilities to scenarios or rank them most-to-least likely — the Shell/GBN doctrine is explicit (Ogilvy & Schwartz 2004): a weighted set collapses back into a forecast, and the least expected corner is often the one that matters.
- Do **not** build on correlated axes — a diagonal is one story told twice — nor a best/worst/middle trio, where the middle becomes the forecast. Two axes, four corners.
- Do **not** name scenarios "A/B/C/D" — the name carries the memory.
- Do **not** stop at the narratives — robust moves, options and the monitoring plan are the deliverable.

## Reference

- P. Wack, "Scenarios: Uncharted Waters Ahead," *Harvard Business Review*, vol. 63, no. 5, pp. 73–89, Sept.–Oct. 1985. https://hbr.org/1985/09/scenarios-uncharted-waters-ahead
- P. Schwartz, *The Art of the Long View*. New York: Doubleday/Currency, 1991. ISBN 0-385-26731-2.
- J. Ogilvy and P. Schwartz, *Plotting Your Scenarios*. Global Business Network, 2004 (first published in L. Fahey and R. Randall, eds., *Learning from the Future*, Wiley, 1998).
- K. van der Heijden, *Scenarios: The Art of Strategic Conversation*. Chichester: Wiley, 1996. ISBN 0-471-96639-8.
- P. J. H. Schoemaker, "Scenario Planning: A Tool for Strategic Thinking," *Sloan Management Review*, vol. 36, no. 2, pp. 25–40, 1995. https://sloanreview.mit.edu/article/scenario-planning-a-tool-for-strategic-thinking/
- S. M. Millett, "Should Probabilities Be Used with Scenarios?," *Journal of Futures Studies*, vol. 13, no. 4, pp. 61–68, May 2009. https://jfsdigital.org/wp-content/uploads/2014/01/134-AE04.pdf — argues probabilities can be used with care; documents the Wack no-probability stance it challenges.
