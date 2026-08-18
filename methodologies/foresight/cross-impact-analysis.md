---
name: Cross-Impact Analysis
category: foresight
origin: Theodore J. Gordon & Olaf Helmer (RAND, 1966); structural analysis (MICMAC) by Michel Godet (1970s–80s)
agent_suitability: High
tags: [cross-impact, interdependencies, matrices, micmac, structural-analysis, consistency, probabilities]
related: [../foresight/delphi-method.md, ../foresight/scenario-planning.md, ../foresight/steep-pestle-analysis.md, ../scientific-methods/bayesian-evidence-updating.md, ../agent-playbook.md, ../../skills/cross-impact-analysis/SKILL.md]
---

# Cross-Impact Analysis (incl. MICMAC Structural Analysis)

> **Essence:** A family of matrix methods that force analysts to ask how events, trends, or variables affect *each other* — because futures don't arrive one trend at a time — producing consistency-checked scenario sets and influence/dependence maps of the system.

## Overview

Single-trend thinking assumes developments proceed independently. Cross-impact analysis (CIA) starts from the observation that the occurrence of one event changes the probability of others — and builds a matrix to capture those interactions systematically. In the **Gordon–Helmer tradition**, the analyst lists key events/trends, estimates each one's standalone probability, then fills an N×N matrix: *if event i occurs, does the probability of event j rise, fall, or stay the same — and by how much?* Monte Carlo "runs" of the matrix then generate many internally consistent combinations, from which calibrated scenario families and adjusted probabilities emerge.

In the **French prospective tradition (Godet)**, the twin method is **structural analysis / MICMAC**: instead of probabilities, experts rate the *direct influence* of each variable on each other (0–3), and matrix algebra computes not just direct but **indirect** influence and dependence, classifying variables into: **determinant/input** variables (high influence, low dependence — the levers), **relay/intermediate** variables (high/high — unstable amplifiers), **dependent/output** variables (low influence, high dependence — indicators), and **excluded/autonomous** variables (low/low — disconnected). The influence/dependence map is a strategy instrument: act on determinants, watch relays, track outputs.

Both traditions share the core discipline: **consistency**. Scenario sets built from cross-impacts can't quietly combine mutually exclusive elements; strategy built on structural analysis targets the variables that actually move the system. CIA is the standard quantitative companion to [delphi-method.md](delphi-method.md) (Delphi supplies the probability estimates) and to [scenario-planning.md](scenario-planning.md) (cross-impact supplies the consistency engine).

## Origin & History

- **1966 — Gordon & Helmer at RAND**, "Report on a Long-Range Forecasting Study" follow-on work: *Initial Perceptions of a Cross-Impact Game* (Gordon & Hayward, 1968) introduced cross-impact matrices as a Delphi-extension ("game").
- **1970s — method development:** Gordon's Interax (1980s), stochastic cross-impact models (Dalkey's condition for matrix consistency), KSIM (Kane's simulation variant, 1972), and Battelle's BASICS.
- **1970s–90s — French prospective:** Michel Godet (SEMA/CNAM) built the *prospective* toolkit: structural analysis, MICMAC (direct/indirect influence-dependence), MACTOR (actor strategies), SMIC/Prob-Expert (expert probabilities → scenarios). *Scenarios and Strategic Management* (Godet, 1987/2000) is the reference text.
- **2000s–present:** CIA remains standard in futures methodology curricula (Glenn & Gordon, *Futures Research Methodology*) and is embedded in commercial foresight software.

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Cross-impact matrix | N×N matrix: cell (i,j) = effect of i's occurrence (or strength) on j. |
| Conditional probability | P(j | i) — the heart of Gordon–Helmer CIA. |
| Monte Carlo run | Randomly resolving events per matrix-adjusted probabilities to sample consistent scenario combinations. |
| Structural analysis | Godet's inventory + influence-rating of system variables. |
| MICMAC | Matrix multiplication method computing direct + indirect influence/dependence and variable classification. |
| Determinant / input variable | High influence, low dependence — strategic lever. |
| Relay variable | High influence, high dependence — unstable amplifier, must be watched. |
| Dependent / output variable | Low influence, high dependence — indicator of system state. |
| Excluded / autonomous variable | Low/low — disconnected or slow background. |
| Consistency check | Verifying a scenario's elements can co-occur (pairwise compatibility). |

## When to Use / When Not to Use

**Use when:**
- A scenario set needs internal-consistency discipline (10+ interacting elements).
- Strategy must target the 3–5 variables that actually drive the system (MICMAC map).
- You have expert probability estimates (from Delphi) and want calibrated scenario families.
- Comparing options against interdependent risks/events.

**Don't use when:**
- N is large and uncurated — matrices grow as N² and expert fatigue destroys data quality (keep N ≤ ~20–30; cluster first).
- Interactions are genuinely unknown even to experts (the matrix becomes numerology; use qualitative scenarios).
- You need dynamic trajectories over time (cross-impact is largely static; use system dynamics).
- The audience will read false precision into the numbers — present as structured judgment, not measurement.

## Process & Steps

**A. Gordon–Helmer probabilistic cross-impact:**
1. Define the event/trend set (10–25 items, from [horizon-scanning.md](horizon-scanning.md)/Delphi). *Artifact: item list.*
2. Estimate standalone probabilities (and timings) per item — classically via [delphi-method.md](delphi-method.md). *Artifact: priors.*
3. Fill the matrix: for each ordered pair (i→j), the direction and magnitude of impact on j's probability. *Artifact: N×N matrix.*
4. Run Monte Carlo iterations; collect adjusted probabilities and recurring event combinations. *Artifact: calibrated probabilities + scenario clusters.*
5. Cluster runs into scenario families; validate coherence; write up. *Artifact: scenario families + consistency statistics.*

**B. Godet structural analysis / MICMAC:**
1. Inventory system variables (internal + external; 20–80, then cluster to ≤30–40 key variables). *Artifact: variable list.*
2. Rate direct influences: cell (i,j) ∈ {0,1,2,3} by expert panel. *Artifact: direct-influence matrix.*
3. Compute direct and indirect (matrix-powered) influence/dependence scores. *Artifact: MICMAC scores.*
4. Plot the influence/dependence plane; classify variables (determinant/relay/dependent/excluded). *Artifact: the map.*
5. Interpret for strategy: which determinants to act on, which relays to stabilize, which outputs to monitor; optionally feed key determinants into scenario axes (Godet's full pipeline). *Artifact: strategy implications.*

## Techniques, Tools & Deliverables

- Pairwise influence workshops (silent rating then aggregation, à la Delphi).
- Spreadsheet or code for matrix multiplication (MICMAC) and Monte Carlo (probabilistic CIA).
- Godet-suite companions: MACTOR (actors), SMIC (expert-probability scenarios).
- Consistency tables for qualitative scenario auditing (pairwise ✓/✗ compatibility).
- **Deliverables:** cross-impact matrix, MICMAC influence/dependence map with classifications, calibrated probabilities / scenario families, strategy implications.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Forces interaction thinking; kills one-trend-at-a-time analysis | N² effort and fatigue; quality degrades fast with big matrices |
| Consistency-checked scenarios; exposes impossible combinations | Input ratings are judgment — precision is illusory if treated as measurement |
| MICMAC map is a genuinely strategic artifact (levers vs indicators) | Static: no time dimension, no feedback dynamics |
| Natural quantitative companion to Delphi | Methodological disputes (probability-calibration conditions, e.g., Dalkey's) |
| Reusable matrix: new evidence updates, not rebuilds | Software/format complexity can overshadow the thinking |

Two failure patterns recur in documented use. First, fatigue: an N×N matrix asks experts for N² judgments, and rating quality visibly degrades in the back third of a large matrix — past ~15 variables the precision becomes theater. Second, false precision: the output *looks* quantitative, so teams treat consistency coefficients and MICMAC coordinates as measurements when every input was a subjective rating. The method earns its keep when it kills an impossible scenario combination or exposes an unsuspected driver; it wastes its keep when the matrix becomes the deliverable instead of the argument. Keep N small, treat the numbers as structured judgment, and never present the map without the rating rationale.

## Worked Examples & Case Studies

- **Gordon & Hayward (1968), RAND:** the original cross-impact "game" applied to long-range events — founding demonstration; its documented result was that cross-impact couplings materially shifted event-probability estimates relative to treating events independently, which is the method's raison d'être.
- **Godet's prospective cases:** French national and corporate prospectives (e.g., SNCF, EDF and industry studies documented in Godet's books) using MICMAC/MACTOR/SMIC pipelines.
- **Normandy water/air and regional prospectives:** documented French regional studies using structural analysis for policy levers (Godet-school literature).
- **Standard teaching tool:** CIA/MICMAC exercises are core practicals in futures methodology courses (Millennium Project methodology series).

## Variants & Related Methodologies

- **KSIM, Interax, BASICS, SMIC Prob-Expert** — historical model variants.
- **Qualitative consistency analysis** — pairwise compatibility ✓/✗ without probabilities (common in scenario practice).
- **Fuzzy cognitive maps / system dynamics** — dynamic cousins for feedback over time.
- **MACTOR** — the actor-strategy companion matrix (Godet).
- Agent skill: [cross-impact-analysis](../../skills/cross-impact-analysis/SKILL.md) — one-page executable form of this methodology.
- Related: [delphi-method.md](delphi-method.md) (estimate source), [scenario-planning.md](scenario-planning.md) (consistency engine), [steep-pestle-analysis.md](steep-pestle-analysis.md) (variable inventory), [bayesian-evidence-updating.md](../scientific-methods/bayesian-evidence-updating.md) (formal probability updating).

## Agent Adaptation

### Suitability for agent execution

**High** — this is structured estimation plus matrix arithmetic, both agent-friendly. Agents don't fatigue on N² cell ratings (the human failure mode), can run the matrix math in code, and can audit consistency exhaustively. The judgment content (direction and magnitude of each influence) is genuinely contestable, so ratings should be produced by diverse Domain Expert personas and defended with one-line rationales, with a Critic auditing the rationale quality — otherwise you get fluent, unaudited numerology. MICMAC arithmetic must run in code (never "computed" by the LLM in prose).

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Analyst | Curate the variable/event set (cluster to N ≤ 25); define each item operationally. |
| Domain Expert (×5–10 personas) | Rate matrix cells independently (influence 0–3 or Δprobability), each with a one-line rationale. |
| Facilitator (agent) | Aggregate ratings (median), flag high-variance cells for a second round. |
| Critic / Red Team | Audit rationales; hunt asymmetric nonsense (i→j strong, j→i strong, no story); demand evidence for extreme ratings. |
| Code executor (tool) | MICMAC powers / Monte Carlo runs / consistency statistics. |
| Synthesizer | Maps, classifications, scenario clusters, strategy implications. |
| Verifier | Check any empirical claims embedded in rationales. |
| Human | Approves variable set; arbitrates contested high-impact cells; owns strategy conclusions. |

### Agent pipeline

1. Frame (human) → system/question; Analyst curates `variables.json` (N ≤ 25, operational definitions).
2. Rate (Domain Experts, independent, cell-by-cell with rationale) → `ratings_<persona>.jsonl`.
3. Aggregate (Facilitator) → median matrix + variance flags → contested cells re-rated once.
4. Compute (code) → MICMAC influence/dependence scores, classification; or Monte Carlo scenario clusters.
5. Stress-test (Critic) → rationale audit; sensitivity: which cells change the classification if flipped?
6. Report (Synthesizer) → map + classifications + implications → human arbitration of contested cells.

### Prompt templates

```text
SYSTEM: You are an expert rater (persona: {{persona_spec}}) in a structural analysis of
"{{system}}". Variables: {{variables_json}}. For EACH ordered pair (i -> j), rate the DIRECT
influence of i on j: 0 none, 1 weak, 2 moderate, 3 strong — plus a one-line rationale for any
rating >= 2. Judge influence as "if i changes, how much does j change", independent of
probability. Do not reciprocate automatically: i->j and j->i are separate judgments.
Output JSONL: {"i": ..., "j": ..., "rating": 0-3, "rationale": ...}.
```

```text
SYSTEM: You are the Critic auditing this cross-impact matrix: {{matrix}} and rationales:
{{rationales}}. Find: (1) asymmetric pairs where both directions are rated strong with no
feedback-loop story; (2) extreme ratings (3s) whose rationale is a bare assertion; (3) variables
whose ROW is all zeros — truly influence-free, or a blind spot?; (4) rating clusters that look
copied across similar pairs. Also run a sensitivity check: list the 5 cells whose flip would most
change the MICMAC classification (highest leverage ratings) for human arbitration.
```

```text
SYSTEM: You are the Synthesizer. MICMAC results: influence {{influence}}, dependence
{{dependence}}, classification {{classification}}. Write the strategic reading: (1) the
determinant variables are the levers — for each, one paragraph on what acting on it would mean
for "{{system}}"; (2) the relay variables are unstable amplifiers — how to watch them;
(3) the dependent variables are indicators — propose a monitoring signpost for each;
(4) the excluded variables — confirm they are truly background or flag for re-examination.
No new ratings — interpret only what the matrix says.
```

### Tools & data requirements

Structured store for ratings (JSONL), code execution for matrix powers/Monte Carlo (mandatory — no mental arithmetic), plotting for the influence/dependence plane, web retrieval for evidence-backed rationales.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Fluent numerology (rationale-free ratings) | Critic rationale audit | Rationale required for every rating ≥ 2 |
| Persona collusion (all raters similar) | Inter-persona variance report | Engineered persona diversity; variance surfaced, not hidden |
| Mental-arithmetic matrices | No code artifact | All computation in code with saved scripts |
| N bloat (50×50 matrix) | Variable count gate | Cluster/merge to N ≤ 25 before rating |
| False precision in presentation | Report format review | Present classifications and ranges, not decimal authority |
| Matrix treated as truth, not judgment | Sensitivity absent | Mandatory sensitivity analysis; contested cells get human call |

### Human-in-the-loop checkpoints

1. Variable-set approval (defines the system boundary).
2. Arbitration of contested/high-leverage cells.
3. Strategy conclusions from the map (which levers to actually pull).

### Inputs & outputs (chaining contract)

**Inputs:** curated event/variable set (from [horizon-scanning.md](horizon-scanning.md), [steep-pestle-analysis.md](steep-pestle-analysis.md)); probability estimates (from [delphi-method.md](delphi-method.md)).
**Outputs:** influence/dependence map with classifications, calibrated probabilities, consistent scenario families, sensitivity list — feeding [scenario-planning.md](scenario-planning.md) (consistency-checked scenarios, axis selection), [technology-roadmapping.md](technology-roadmapping.md) (lever identification).

## References & Further Reading

- Gordon, T.J. & Hayward, H. (1968). "Initial Experiments with the Cross-Impact Matrix Method of Forecasting." *Futures*, 1(2).
- Gordon, T.J. & Helmer, O. (1964). *Report on a Long-Range Forecasting Study.* RAND. (predecessor)
- Dalkey, N. (1972). "An Elementary Cross-Impact Model." *Technological Forecasting and Social Change*, 3.
- Godet, M. (2000). "The Art of Scenarios and Strategic Planning: Tools and Pitfalls." *Technological Forecasting and Social Change*, 65(1).
- Godet, M. (1987/2006). *Creating Futures: Scenario Planning as a Strategic Management Tool.* Economica. (structural analysis, MICMAC, MACTOR, SMIC)
- Arcade, J., Godet, M., Meunier, F. & Roubelat, F. (1999). "Structural Analysis with the MICMAC Method & Actors' Strategy with MACTOR Method." In *Futures Research Methodology.* AC/UNU Millennium Project.
- Kane, J. (1972). "A Primer for a New Cross-Impact Language — KSIM." *Technological Forecasting and Social Change*, 4.
- Glenn, J.C. & Gordon, T.J. (eds.) (2009). *Futures Research Methodology — Version 3.0.* The Millennium Project.
