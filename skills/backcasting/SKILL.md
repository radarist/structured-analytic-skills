---
name: backcasting
description: "Works backwards from a desired end state to the present, producing a dated milestone chain, evidenced measure packages, a barrier and lock-in register and a near-term action agenda (Robinson's normative backcasting, Energy Policy, 1982). Use when the goal is a future that current trends will not deliver — \"how does the city reach net-zero by 2040?\", \"backcast from the 2030 vision\", \"what must be true by {year} for {goal}?\", \"build a roadmap back from the target\". Not for exploring which futures could happen (use `scenario-planning`) or for a probable-future forecast (use `foresight`)."
license: MIT
metadata:
  category: foresight
  method: Backcasting (normative foresight)
  origin: John B. Robinson, 1982 (energy backcasting); Karl H. Dreborg, 1996 (methodological essence); Quist & Vergragt participatory variant, 2006
  version: "2.0.0"
---
# Backcasting

Backcasting fixes a desired end state and reasons backwards to the present, asking at each step "what must already have been true, and by when, for this to be reachable?" John B. Robinson coined it for energy policy analysis in 1982 as the deliberate inverse of forecasting: a forecast asks what is likely, a backcast asks what would have to happen for a chosen future to be possible, so it is normative rather than predictive (Robinson, 1982; 1990). Dreborg (1996) gives the selection rule — the method suits complex problems needing major change, where dominant trends are part of the problem, which is exactly where planning forward from today's constraints only extends today's trajectory. It prevents incrementalism disguised as a plan: a roadmap whose first milestones are current projects renamed, with the hard discontinuities pushed past the planning horizon.

## When to invoke

Invoke when:

- A goal is set that present trends will not deliver: "how do we reach net-zero by 2040?", "backcast from the 2030 vision".
- A deliberate transition needs a route: decarbonisation, fleet conversion, a new capability, a fixed-date regulatory target.
- A vision exists but nobody has tested whether its path is feasible in the time available.

Do NOT invoke when:

- The question is which futures could occur — use `scenario-planning` to explore and choose, then backcast from the chosen future.
- The question is what will probably happen by when — use `foresight`.
- One trend needs quantifying or projecting — use `trend-analysis`.
- Nobody holds the mandate to define "desirable" — run `scenario-planning`, or backcast several competing visions rather than picking one.
- The environment is so volatile that any fixed end state is fiction within months.

## Procedure

Steps 1–4 are Robinson's sequence (objectives and constraints, end state, work backwards, test feasibility); steps 5–7 add checks later practice made standard (Quist & Vergragt, 2006). Variants: `references/variants.md`.

### 1 — Frame the problem, scope and horizon

Name the transition, the system boundary and the target year — commonly 15–50 years for societal transitions, 5–15 for a firm. Record who holds the mandate to define "desirable": that is a values decision, and the vision stays with its owner while being elaborated and stress-tested. Output: terms of reference.

### 2 — Set the criteria the vision must satisfy

Before drafting the end state, fix the principles and constraints it must meet — statutory targets, sustainability principles, service levels that may not degrade, budget envelopes. Criteria keep the vision principled rather than arbitrary and make it possible to reject one that merely sounds attractive. Output: vision criteria.

### 3 — Define the end state in numbers

Write a concrete picture of the system at the target year: how it works, what it costs, what everyday experience looks like. Hard rule: at least five quantified indicators — adjectives cannot be backcast from — and they must be simultaneously achievable. Output: vision document and indicator table.

### 4 — Build the milestone chain backwards

From the target year, iterate "what must already be true N years earlier?" back to the present. Date every milestone, record its dependencies, and flag any step needing a discontinuity: a cost fall of roughly ten times, a law change, unproven technology, new behaviour at scale. Physical lead times set the binding constraints — replacement cycles, grid connections, permitting, training pipelines — so schedule around them, not through them. Output: dated milestone timeline.

### 5 — Evidence each milestone with precedents and measure packages

For every milestone and the leg leading to it, specify the measures that deliver it — policies, investments, procurement, behaviour change — and find who did something comparable: which jurisdiction or firm, what measures, how long it took, the source. Every flagged discontinuity needs a precedent or an explicitly owned research bet; no miracle steps. Output: measure-package table.

### 6 — Run gap and lock-in analysis

Compare the pathway against the current trajectory: which blocking infrastructure, contracts, regulation, incumbents or capability gaps must break, and by when. If the first milestones are current projects renamed, the chain has become a forward plan — return to step 4. Output: barrier and lock-in register.

### 7 — Set near-term actions and a review cadence

Decide what starts now, what waits for a named decision point, and what needs experiment first. Keep two pathways alive through one decision point so the plan is not brittle. Fix the review cycle and re-backcast trigger. Output: action agenda with owners and dates.

## Output template

```
## Backcast — {vision in one line}

Vision ({target year}): {2-3 sentences, concrete}
Indicators: {>=5 quantified, with target values}
Vision owner / mandate: {who defines "desirable"}

Milestone chain (backwards):
- {T}:    {end state}
- {T-x}:  {milestone} — depends on {…} — discontinuity: {none | flagged}
- {T-y}:  {milestone} — depends on {…} — discontinuity: {none | flagged}
- {now}:  {first milestone reachable from the present}

Measure packages and precedents:
- {leg}: {policies / investments / behaviours} — precedent: {who, when, how long, source}

Barriers and lock-ins: {top 3-5}
Decision points: {where the pathway branches; what keeps options open}
Near-term actions:
- {action} — owner {who} — starts {date} — serves milestone {which}

Review cadence: {cycle}; re-backcast trigger: {what}
Confidence: {high | medium | low} — weakest link: {which}
```

Mandatory fields: vision owner, at least five quantified indicators, a dated chain with no gaps, a precedent or owned research bet for every flagged discontinuity, and near-term actions with owners and start dates.

## Worked example

Vision (2040): all 1,200 municipal buses zero-emission on renewable electricity, no diesel vehicle in service. Indicators: fleet composition 1,200/1,200; kWh per vehicle-km; depot charging capacity (MW); renewable share; service reliability at or above today's. Illustrative figures, one mid-size transit authority.

| Year | Milestone | Depends on | Discontinuity |
|---|---|---|---|
| 2040 | Fleet 100 % zero-emission (1,200 buses) | Steady replacement from 2029 | None |
| 2035 | At least 600 buses zero-emission; second-generation vehicles ordered | Long-route technology proven | Flagged |
| 2028 | Final diesel bus purchased; every replacement from 2029 is zero-emission | Procurement framework in force | None |
| 2026 | Depot upgrades for the first 300 vehicles complete; 150 buses in service | Substation contracts signed 2024 | Lead time 3–5 years |
| 2025 | 20-bus pilot on two routes; procurement framework drafted; training begun | Budget approval | None |

The binding constraint is the 12-year bus service life: full turnover by 2040 forces the last diesel purchase in 2028, which forces the depot upgrades to be contracted in 2024. Precedents: Shenzhen converted roughly 16,000 buses to battery-electric by 2017 — ten times this scale, depot-first charging; Norway moved new-car sales from about 3 % electric in 2012 to a majority by 2020, showing incentives plus charging policy can turn a fleet inside one replacement cycle. Barriers: grid-connection queues, procurement contracts with rolling diesel options, the workshop skills transition. Actions: pilot purchase (transit operations, 2025); substation upgrade application (facilities, 2025, serving the 2026 milestone); the 2028 diesel freeze booked as a decision point with a fallback review. Confidence: medium — weakest link is long-route technology in 2035.

## Verification

- [ ] The vision carries at least five quantified indicators with target values, simultaneously achievable.
- [ ] The chain runs from target year to present with no undated gaps; every milestone lists its dependencies.
- [ ] Every flagged discontinuity has a precedent (who, when, how long, source) or an owned research bet.
- [ ] The pathway was compared against the current trajectory; the first milestones are not current projects renamed.
- [ ] Two or more pathways remain live through a decision point; each near-term action names an owner and start date.
- [ ] The vision owner is named; the review cadence and re-backcast trigger are stated.

## Pair with adjacent skills

- `scenario-planning` — explores which futures could happen; backcast from the chosen one.
- `three-horizons` — the vision is horizon 3, the milestone chain horizon 2, the actions horizon 1.
- `foresight` — the predictive sibling; its accelerants and blockers become pathway risks.
- `premortem-analysis` — exposes links the chain assumed away.
- Methodology counterpart: [methodologies/foresight/backcasting.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/backcasting.md); variants in `references/variants.md`.

## Anti-patterns

- Do **not** let the vision drift into slogans; the five-indicator rule is the discipline.
- Do **not** permit miracle steps; a discontinuity without a precedent or owned bet is where backcasts fail.
- Do **not** let the backward chain become a forward plan; the gap analysis is mandatory.
- Do **not** invent the vision on the owner's behalf; that choice is a values decision.
- Do **not** lock into a single pathway; keep two live through a decision point.
- Do **not** treat the backcast as finished; confidence decays fast beyond the first milestones.

## Reference

- J. B. Robinson, "Energy backcasting: A proposed method of policy analysis," *Energy Policy*, vol. 10, no. 4, pp. 337–344, 1982. https://doi.org/10.1016/0301-4215(82)90048-9
- J. B. Robinson, "Futures under glass: A recipe for people who hate to predict," *Futures*, vol. 22, no. 8, pp. 820–842, 1990. https://doi.org/10.1016/0016-3287(90)90018-D
- K. H. Dreborg, "Essence of backcasting," *Futures*, vol. 28, no. 9, pp. 813–828, 1996. https://doi.org/10.1016/S0016-3287(96)00044-4
- J. Quist and P. Vergragt, "Past and future of backcasting: The shift to stakeholder participation and a proposal for a methodological framework," *Futures*, vol. 38, no. 9, pp. 1027–1045, 2006. https://doi.org/10.1016/j.futures.2006.02.010
- J. Holmberg and K.-H. Robèrt, "Backcasting — a framework for strategic planning," *International Journal of Sustainable Development & World Ecology*, vol. 7, no. 4, pp. 291–308, 2000. https://doi.org/10.1080/13504500009470049
