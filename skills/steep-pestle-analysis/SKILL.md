---
name: steep-pestle-analysis
description: "Sweeps the macro-environment around a decision with the STEEP / PESTLE category checklist (Aguilar's ETPS, 1967) — Social, Technological, Economic, Environmental, Political, plus Legal and Ethical — and delivers a rated driver inventory: every factor evidenced, scored for impact and uncertainty, sorted into predetermined elements versus critical uncertainties. Use when asked \"run a PESTLE analysis of {market}\", \"STEEP analysis for {decision}\", \"what external factors could affect {plan}?\" or \"what are the driving forces in {industry}?\". Not for industry structure (use `five-forces-analysis`) or writing the scenarios themselves (use `scenario-planning`)."
license: MIT
metadata:
  category: foresight
  method: STEEP / PESTLE macro-environment analysis
  origin: Francis J. Aguilar (ETPS, Scanning the Business Environment), 1967; PEST/STEEP/PESTLE variants, 1980s onward
  version: "2.0.0"
---
# STEEP / PESTLE Analysis

STEEP/PESTLE analysis is a category checklist for the macro-environment: Social, Technological, Economic, Environmental and Political forces (PESTLE adds Legal; STEEPLE adds Ethical), descended from the ETPS categories Francis J. Aguilar set out in *Scanning the Business Environment* (1967). Its principle is forced coverage — analysts over-scan the categories they understand, usually market and technology, and skip the rest, so a fixed set of letters makes each omission visible. The framework is trivial; the discipline is refusing to stop at a list: every factor is stated as an evidenced, directional change, rated for impact and uncertainty, clustered into named driving forces and sorted into predetermined elements versus critical uncertainties, as in scenario practice (Schwartz, 1991) and the *Futures Toolkit* driver-mapping tool. It prevents category blindness — the empty Environmental or Political column that later forks the plan.

## When to invoke

Invoke when:

- A decision, strategy or plan needs its external context swept before it is written: "run a PESTLE analysis of {market}", "STEEP analysis for {decision}", "what external factors could affect {plan}?", "what are the driving forces in {industry}?".
- A scenario, roadmap or risk process needs a rated driver inventory as input.
- Someone suspects a whole category of risk is being missed ("are we only looking at technology?").

Do NOT invoke when:

- The question is industry structure — suppliers, buyers, rivals, substitutes, entry barriers — use `five-forces-analysis`; STEEP covers the macro level above the industry.
- The ask is to build the scenarios themselves — use `scenario-planning`; this skill hands it the critical uncertainties.
- One trend needs validating or projecting from a time series — use `trend-analysis`.
- The couplings between drivers matter more than the list — use `cross-impact-analysis` after the inventory exists.
- The need is a standing sweep for weak signals rather than a decision-scoped inventory — use `horizon-scanning`.

## Procedure

### 1 — Frame the focal question

Name the decision, the geography and the horizon (typically 3–10 years) in one line — "Should {organisation} {decide X} in {geography} by {year}?" — and record who will use the inventory. Every later rating is relative to this question; a factor important in general but irrelevant to it scores low. Output: framing statement.

### 2 — Sweep every category for factors

For each letter — **S**ocial (demographics, values, lifestyles), **T**echnological (innovation, infrastructure, R&D), **E**conomic (growth, rates, employment, trade), **E**nvironmental (climate, resources, pollution), **P**olitical (governance, policy, stability), plus **L**egal and **E**thical where regulation or norms are live — list 4–10 concrete factors. Each is a short, directional, evidence-attachable phrase with a date: "EU AI Act enforcement practice crystallising 2025–27", not "regulation". Aim for 20–60 in total; a thin category is a finding to report, not to hide with filler. Output: factor inventory with one piece of evidence per factor.

### 3 — Rate every factor for impact and uncertainty

Score **impact** on the focal question (1–5) and **uncertainty** about the factor's state at the horizon (1–5), each with a one-line rationale. Uncertainty is about direction or magnitude, not about how much the analyst has read: a well-documented but genuinely open policy choice is high-uncertainty. Unrated factors cannot ship. Output: rated factor table.

### 4 — Deduplicate and cluster into named drivers

Merge overlaps (factors routinely fit two letters — assign a primary letter, note the secondary), then group related factors into 8–15 named driving forces, each with a one-line description and its members. The driver, not the raw factor, is the unit strategy and scenario work operate on. Output: driver list with membership.

### 5 — Sort drivers on the impact × uncertainty map

Place each driver: high impact and low uncertainty → **predetermined element**, a planning assumption in every scenario; high impact and high uncertainty → **critical uncertainty**, a scenario-axis candidate or research item; low impact and high uncertainty → watchlist; low impact and low uncertainty → park. Name the couplings between critical uncertainties. Output: 2×2 map with every driver placed.

### 6 — Audit coverage and specificity, then hand off

Check that every category has at least three factors or its thinness is declared; that no vague-noun factor survived; that ratings discriminate rather than sitting at 4/4; and that every driver is external (internal capabilities belong in a SWOT). Then hand off: predetermined elements to planning assumptions, critical uncertainties to `scenario-planning`. Output: coverage audit note and handoff pack.

## Output template

```
## STEEP driver inventory — {focal question}

Focal question: {decision, geography, horizon}   Prepared for: {user}
Coverage: S {n} · T {n} · E {n} · Env {n} · P {n} · L {n} factors — thin categories: {declared as findings}

### Predetermined elements (high impact, low uncertainty — plan on them)
| Driver | Letters | Impact | Uncertainty | Rationale | Evidence |
|---|---|---|---|---|---|
| {name} | {S/T/E/Env/P/L} | {1-5} | {1-5} | {one line} | {source, date} |

### Critical uncertainties (high impact, high uncertainty — scenario-axis candidates)
| Driver | Letters | Impact | Uncertainty | Rationale | Coupled with |
|---|---|---|---|---|---|
| {name} | {letters} | {1-5} | {1-5} | {one line} | {other driver} |

### Watchlist / parked (low impact)
- {driver}: {why it does not move the focal question}

Handoff: critical uncertainties → scenario-planning; predetermined elements → planning assumptions.
Coverage audit: {categories checked; empty or thin ones reported; internal factors removed}
```

Mandatory fields: focal question, coverage counts, and — for every driver — letters, impact, uncertainty and rationale. A driver without a rating or a rationale may not be handed off.

## Worked example

Focal question: "Should a mid-size European grocery retailer commit €40M to automated micro-fulfilment centres (MFCs) by 2029?" Illustrative factors and ratings.

Sweep (condensed): **S** — urban population share around 75 % and rising; online-grocery penetration stuck at 8–12 % after the pandemic. **T** — MFC robotics cost per order down about 30 % in five years. **E** — food-price inflation squeezing basket sizes; ECB rates raising the capex hurdle. **Env** — EU ETS2 carbon pricing extending to transport fuels from 2027; low-emission zones restricting diesel vans. **P/L** — EU platform-work directive reclassifying gig couriers; Sunday-trading rules varying by member state.

| Driver | Letters | Impact | Uncertainty | Sort |
|---|---|---|---|---|
| Automation cost curve keeps falling | T | 5 | 2 | Predetermined |
| Carbon and urban-access rules raise last-mile cost | Env, P | 4 | 2 | Predetermined |
| Online grocery: plateau versus second wave | S, E | 5 | 5 | Critical uncertainty |
| Courier labour cost and legal classification | P, L, E | 4 | 4 | Critical uncertainty |
| Capex financing cost | E | 3 | 3 | Watchlist |
| Sunday-trading liberalisation | P | 2 | 3 | Parked |

Coverage: S 2 · T 1 · E 2 · Env 2 · P/L 2 — thin by design here; a full run needs 4–10 per letter. Reading: the two critical uncertainties — online-demand trajectory and the courier-labour regime — are the axes `scenario-planning` needs; the predetermined elements enter every scenario as constants. The MFC bet pays off only in a "second wave" world, so the framing is staged capex with a demand signpost before tranche two.

## Verification

- [ ] Every category has at least three factors, or its thinness is stated as a finding in the coverage line.
- [ ] Every factor is a directional, dated, evidence-attachable phrase — no bare nouns such as "regulation" or "demographics".
- [ ] Every driver carries impact, uncertainty and a rationale, and the ratings are not a uniform wall of 4/4.
- [ ] Every driver is external to the organisation; internal strengths and weaknesses were removed.
- [ ] Each critical uncertainty is named as a scenario-axis candidate and each predetermined element as a planning assumption in the handoff.

## Pair with adjacent skills

- `horizon-scanning` — the upstream sweep whose entries feed the factor inventory.
- `scenario-planning` — the downstream consumer: critical uncertainties become axes, predetermined elements become constants.
- `cross-impact-analysis` — rates the couplings between the drivers this inventory names.
- `trend-analysis` — quantifies a single driver's rate and trajectory.
- `five-forces-analysis` — industry structure one level below the macro-environment.
- Methodology counterpart: [methodologies/foresight/steep-pestle-analysis.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/steep-pestle-analysis.md).

## Anti-patterns

- Do **not** ship an unrated list; sixty unranked factors prioritise nothing.
- Do **not** accept vague factors; a category label with no evidence or date is not a factor.
- Do **not** hide an empty category with filler; thin coverage is a finding.
- Do **not** rate everything 4/4; ratings that mirror generic priors instead of the focal question are decoration.
- Do **not** include internal factors; the organisation's own cost position is not a Political force.
- Do **not** treat the grid as the deliverable; the rated, clustered handoff is.

## Reference

- F. J. Aguilar, *Scanning the Business Environment*. New York: Macmillan, 1967 — the ETPS categories (Economic, Technical, Political, Social) from which PEST/STEEP/PESTLE descend.
- L. Fahey and V. K. Narayanan, *Macroenvironmental Analysis for Strategic Management*. St. Paul, MN: West Publishing, 1986. ISBN 0-314-85233-6.
- P. Schwartz, *The Art of the Long View*. New York: Doubleday/Currency, 1991. ISBN 0-385-26731-2 — driving forces, predetermined elements and critical uncertainties.
- R. Whittington, P. Regnér, D. Angwin, G. Johnson and K. Scholes, *Exploring Strategy: Text and Cases*, 13th ed. Harlow: Pearson, 2023, ch. 3 "Macro-environment analysis". ISBN 978-1-292-42874-1.
- UK Government Office for Science, *The Futures Toolkit*, edition 1.0, 2017 (2024 edition current), "Driver Mapping" tool — PESTLE categories mapped on an importance/certainty matrix. https://www.gov.uk/government/publications/futures-toolkit-for-policy-makers-and-analysts
