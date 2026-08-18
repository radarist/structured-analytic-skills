---
name: Trend Analysis
category: foresight
origin: statistical forecasting tradition; popularized in futures by John Naisbitt (Megatrends, 1982); Trend Impact Analysis by Theodore J. Gordon (1994)
agent_suitability: High
tags: [trends, megatrends, extrapolation, s-curves, diffusion, forecasting, indicators]
related: [../foresight/horizon-scanning.md, ../foresight/steep-pestle-analysis.md, ../foresight/scenario-planning.md, ../foresight/technology-roadmapping.md, ../agent-playbook.md, ../../skills/trend-analysis/SKILL.md]
---

# Trend Analysis

> **Essence:** Identify patterns of change with momentum, quantify their direction and drivers, and reason about how far they can run — distinguishing durable trends from fads, and extrapolation from assumption.

## Overview

Trend analysis occupies the middle ground between scanning (what's emerging?) and scenarios (what might happen?): it works on developments that already have **visible momentum** and asks how far, how fast, and under what conditions they continue. Its basic moves are: find candidate trends (from [horizon-scanning.md](horizon-scanning.md), [steep-pestle-analysis.md](steep-pestle-analysis.md), or data); validate them (is there real, sustained, multi-source evidence — or is this a fad, a hype cycle, or one vendor's marketing?); characterize them (direction, rate, drivers, geographic/social spread, maturity on the adoption curve); and project them — naively by extrapolation, or intelligently by modeling the drivers and constraints.

Mature trend analysis is disciplined about what it can claim. **Extrapolation** is legitimate for slow-moving, structurally driven quantities (demographics) and dangerous for reflexive ones (markets, politics). The field's key corrective tools: **Trend Impact Analysis (TIA)** (Gordon) — start with a "surprise-free" extrapolation, then systematically adjust for the impact of possible future events; **S-curve / diffusion modeling** (Rogers; Foster) — adoption saturates, so growth follows logistic shapes, not straight lines; and **counter-trend scanning** — every strong trend breeds opposition (globalization → localism; digital → analog revival), and the counter-trend is often where discontinuity enters.

Trend outputs feed scenarios as **predetermined elements**, roadmaps as lane evidence, and strategy as planning assumptions. A "megatrend" (Naisbitt) is simply a trend of exceptional scope, duration, and self-reinforcing power (urbanization, aging, digitalization) — useful as orientation, dangerous as autopilot.

## Origin & History

- **Quantitative roots:** time-series extrapolation in economics/demography (mid-20th century); RAND-era technological forecasting (1950s–60s: Delphi, TIA, cross-impact grew from the same milieu).
- **1962 — Everett Rogers**, *Diffusion of Innovations*: the S-curve of adoption and adopter categories (innovators → laggards) — still the standard model of how trends spread.
- **1982 — John Naisbitt**, *Megatrends*: content-analysis of newspapers to name society-level trends; commercial breakthrough for trend watching (later Faith Popcorn and the trend-consulting industry).
- **1986 — Richard Foster**, *Innovation: The Attacker's Advantage*: S-curves for technology performance and substitution timing.
- **1994 — Theodore J. Gordon**, "Trend Impact Analysis" (in *Futures Research Methodology*, AC/UNU Millennium Project): the standard method for adjusting extrapolations with future-event judgments.
- **2000s–present:** institutional megatrend programmes (EU ESPAS, UN, NIC *Global Trends*), data-driven trend mining (publications, patents, search data), and critique of hype cycles (Gartner's Hype Cycle as a popular fad-vs-trend lens, 1995).

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Trend | A sustained, directional pattern of change with observable evidence over time. |
| Megatrend | A trend of great scope (global), duration (decades), and momentum (multiple reinforcing drivers). |
| Fad | Rapid rise and fall without structural drivers; the trend analyst's false positive. |
| Weak signal | Pre-trend anomaly (see [horizon-scanning.md](horizon-scanning.md)); some graduate into trends. |
| Driver | The causal force(s) pushing a trend (demographics, economics, technology cost curves, policy). |
| Extrapolation / surprise-free forecast | Projection of the trend assuming present drivers persist unchanged. |
| Trend Impact Analysis (TIA) | Gordon's method: extrapolate, list future events that could bend the curve, estimate probabilities and impacts, adjust. |
| S-curve / logistic diffusion | Saturation-bounded growth; adoption or performance vs time/effort. |
| Counter-trend | The opposing movement a strong trend provokes. |
| Trend card | Standard one-page format: description, evidence, drivers, trajectory, implications, signposts. |

## When to Use / When Not to Use

**Use when:**
- You need planning assumptions with evidence behind them (the "predetermined" layer for scenarios).
- Validating or puncturing trend claims ("everyone knows X is growing" — show me).
- Timing questions where momentum is real: adoption curves, cost curves, demographic shifts.
- Building trend cards/briefs as standing strategy inputs.

**Don't use when:**
- The phenomenon is reflexive or contested (elections, markets, wars) — extrapolation is astrology there; use scenarios.
- The decision depends on a discontinuity (that's [horizon-scanning.md](horizon-scanning.md) + scenarios).
- You need to *change* the trend (normative work: [backcasting.md](backcasting.md), [three-horizons.md](three-horizons.md)).
- Data is too sparse to distinguish trend from noise — say so, don't fit lines to three points.

## Process & Steps

**Elapsed time and participants:** one analyst can validate a candidate trend in 1–2 days (steps 1–2); full characterization and projection (3–4) take another 1–2 days per trend and benefit from one domain-expert review pass. Once instrumented, maintenance is ~an hour per trend per month; the implications pass (5–6) is best run with the decision-owners in the room, a half-day per planning cycle.

1. **Nominate candidate trends.** From scanning, STEEP drivers, data anomalies, expert claims. *Artifact: candidate list.*
2. **Validate.** For each: multi-source, time-series evidence of sustained change? Structural drivers identified? Or fad markers (single source, media-only, no mechanism)? *Artifact: validated trend set + rejected list with reasons.*
3. **Characterize.** Direction, rate, curvature (accelerating/linear/saturating), geographic and demographic spread, drivers, inhibitors, maturity (early/mid/late on the S-curve). *Artifact: trend profiles.*
4. **Project.** Choose per trend: naive extrapolation (with explicit assumptions), S-curve fit, or TIA (extrapolate → list bending events with probabilities/impacts → adjusted projection). Always show the assumption set. *Artifact: projections with assumption sheets.*
5. **Scan for counter-trends and collisions.** What opposition does each trend generate? Where do trends collide (automation ↑ + labor shortage ↑ = ?). *Artifact: interaction notes.*
6. **Derive implications and signposts.** So-what per trend for the organization; observable indicators to track; review cadence. *Artifact: trend cards + watchlist.*

## Techniques, Tools & Deliverables

- **Trend cards** — the standard deliverable (description, evidence, drivers, trajectory, implications, signposts, confidence).
- **TIA worksheets** — event list with probability × impact adjustments to a baseline curve.
- **S-curve / logistic fitting** — spreadsheet or code; Bass diffusion for adoption with innovation/imitation coefficients.
- **Gartner Hype Cycle** as a fad-filter heuristic (peak of inflated expectations → trough → plateau).
- **Data sources:** official statistics, industry datasets, publication/patent counts (tech mining), search-interest data — always multi-source.
- **Deliverables:** validated trend set, projections + assumptions, trend cards, watchlist.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Evidence-based; punctures hype and fad claims | Backward-looking by construction; blind to discontinuity |
| Quantified, communicable (curves, cards) | Extrapolation seduces: curves get treated as destiny |
| Direct input to scenarios (predetermineds) and roadmaps | TIA adjustments are still expert judgment (bias enters) |
| Cheap to maintain once instrumented | Reflexivity: publishing a trend can change it |
| S-curve logic gives real timing discipline | Aggregation hides distributional reality (who adopts first, who's left) |

The core temptation is extrapolation-as-destiny: a fitted S-curve feels like physics, but every curve assumes the carrying capacity (K) stays put — and K moves with policy, prices, and complementary infrastructure. The reflexivity problem is subtler and real: publishing a confident trend forecast can accelerate it (hype) or kill it (a warning that triggers the response it warned about). TIA adjustments restore honesty but reintroduce expert bias by the back door — record the adjustment rationale or you've traded a false model for an invisible one. Finally, aggregate curves conceal who adopts and who's left behind; for decisions that depend on segments, disaggregate before you extrapolate.

## Worked Examples & Case Studies

- **Naisbitt's Megatrends (1982):** content analysis of US newspapers named industrial→information society and other shifts; methodology crude by modern standards but foundational for trend watching as practice.
- **NIC Global Trends (every ~4 years since 1997):** US National Intelligence Council's megatrend-plus-scenarios reports (e.g., demographic aging, climate stress) — the reference institutional example of trend-to-scenario layering.
- **Technology cost/performance curves:** learning-curve tracking of solar PV, batteries (Swanson's law, battery $/kWh) — trend analysis that repeatedly beat expert judgment (documented in energy-economics literature).
- **IEA energy outlooks:** explicitly scenario-conditioned projections — the honest institutional model of "trends + assumptions", not prediction.

## Variants & Related Methodologies

- **Trend Impact Analysis (TIA)** — event-adjusted extrapolation.
- **Tech mining / bibliometric trend analysis** — publication/patent curve tracking ([technology-roadmapping.md](technology-roadmapping.md)).
- **Megatrends programmes** — NIC, EU ESPAS, UN-style institutional variants.
- **Counter-trend / contra-trend analysis** — systematic opposition scanning.
- Agent skill: [trend-analysis](../../skills/trend-analysis/SKILL.md) — one-page executable form of this methodology.
- Related: [horizon-scanning.md](horizon-scanning.md) (upstream), [steep-pestle-analysis.md](steep-pestle-analysis.md) (categorization), [scenario-planning.md](scenario-planning.md) (downstream; trends = predetermined elements), [technology-roadmapping.md](technology-roadmapping.md) (lane evidence).

## Agent Adaptation

### Suitability for agent execution

**High** for validation, characterization, and maintenance: gathering multi-source time-series evidence, fitting curves, drafting trend cards, and re-checking on a cadence are automatable with web search + code execution. **Medium** for projection judgments (TIA event selection, counter-trend reasoning), which are genuine expert-judgment tasks — agents draft, humans ratify. The discipline agents add is consistency: every trend gets the same evidence bar and the same assumption sheet.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Scout | Gather multi-source time-series evidence per candidate trend (statistics, datasets, studies). |
| Analyst | Validate (trend vs fad), characterize (rate, curvature, drivers), fit curves, run TIA drafts. |
| Domain Expert (personas) | Judge driver persistence and event impacts; nominate counter-trends. |
| Critic / Red Team | Attack data quality, curve choices, hidden assumptions, reflexivity, hype contamination. |
| Synthesizer | Produce trend cards, projections with assumption sheets, watchlist. |
| Verifier | Check every number against its source; confirm time series actually support "sustained change". |
| Facilitator (human) | Approves validated trends, projections, and planning assumptions. |

### Agent pipeline

1. Frame (human) → candidate trend list + domains + horizons.
2. Gather (Scout per trend) → `evidence_<trend>.json` [source, series, dates, urls].
3. Analyze (Analyst) → validation verdicts; characterizations; curve fits (code execution); TIA drafts → `trend_profiles.json`.
4. Stress-test (Critic + Domain Experts) → assumption challenges, counter-trends, event-impact debates.
5. Verify (Verifier) → numeric source checks.
6. Report (Synthesizer) → trend cards + projections + watchlist → human ratification → handoff to scenarios/roadmaps. Re-run on cadence.

### Prompt templates

```text
SYSTEM: You are the Scout validating the trend claim: "{{trend_claim}}". Find multi-source,
time-series evidence: official statistics, industry datasets, peer-reviewed studies. For each
source: the series (values + dates), geography, and URL. Then give a preliminary verdict:
VALIDATED (sustained change, multiple independent sources) / UNCERTAIN (sparse or single-source)
/ FAD MARKERS PRESENT (media-only, no mechanism, spike pattern). No trend inflation: if the
evidence is weak, say so. JSON output.
```

```text
SYSTEM: You are the Analyst. Evidence pack: {{evidence_json}}. (1) Characterize the trend:
direction, rate, curvature (accelerating | linear | saturating), drivers, inhibitors, maturity
(early|mid|late S-curve), with justification. (2) Fit an appropriate simple model (linear,
logistic, or Bass) to the series — show parameters and fit quality. (3) Draft a surprise-free
projection to {{horizon}} with the explicit assumption list. Flag every place where the model
could break (saturation, policy intervention, substitution).
```

```text
SYSTEM: You are the Critic. Trend profile and projection: {{trend_profile}}. Attack: Is the
"driver" actually causal or correlational? Is the curve choice motivated reasoning (logistic
when you want saturation, linear when you want growth)? What future events could bend this
curve — list 5 with rough probability and impact direction (this seeds the TIA). What is the
counter-trend this trend is generating? Where is reflexivity (the forecast changing the thing
forecast)? Return challenges ranked by how much they move the projection.
```

### Tools & data requirements

Web search + official data sources (Scout/Verifier), code execution for curve fitting (Analyst), spreadsheet/JSON store, charting for cards; scheduled re-runs for maintenance.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Numbers hallucinated or misquoted | Verifier numeric check | Every datum carries source + retrieval date |
| Curve-motivated reasoning | Critic pass | Require fit-quality reporting and alternative-curve comparison |
| Trend inflation (everything validated) | Validation verdict distribution | Scout prompt mandates explicit FAD verdict option; drop-rate tracked |
| Extrapolation treated as destiny | Assumption sheets missing | No projection ships without assumptions + TIA events |
| Stale trends keep steering strategy | Evidence older than cadence | Scheduled re-validation; auto-expiry flags |

### Human-in-the-loop checkpoints

1. Ratifying validated trends and planning assumptions.
2. TIA event judgments (probabilities/impacts).
3. Deciding which trends become scenario predetermineds vs uncertainties.

### Inputs & outputs (chaining contract)

**Inputs:** candidate trends (from [horizon-scanning.md](horizon-scanning.md), [steep-pestle-analysis.md](steep-pestle-analysis.md)); data sources.
**Outputs:** validated trend set, projections + assumption sheets, trend cards, watchlist — feeding [scenario-planning.md](scenario-planning.md) (predetermined elements), [technology-roadmapping.md](technology-roadmapping.md) (lane evidence), [backcasting.md](backcasting.md) (baseline trajectory).

## References & Further Reading

- Naisbitt, J. (1982). *Megatrends: Ten New Directions Transforming Our Lives.* Warner Books.
- Rogers, E.M. (1962/2003). *Diffusion of Innovations* (5th ed.). Free Press.
- Foster, R. (1986). *Innovation: The Attacker's Advantage.* Summit Books.
- Gordon, T.J. (1994/2009). "Trend Impact Analysis." In Glenn & Gordon (eds.), *Futures Research Methodology.* The Millennium Project.
- Glenn, J.C. & Gordon, T.J. (eds.) (2009). *Futures Research Methodology — Version 3.0.* The Millennium Project.
- Bass, F.M. (1969). "A New Product Growth Model for Consumer Durables." *Management Science*, 15(5).
- US National Intelligence Council — *Global Trends* report series.
- Martino, J.P. (1993). *Technological Forecasting for Decision Making* (3rd ed.). McGraw-Hill.
