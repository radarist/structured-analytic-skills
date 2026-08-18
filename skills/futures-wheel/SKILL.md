---
name: futures-wheel
description: "Maps the consequences of one defined change ring by ring — primary, secondary and tertiary impacts, each chained to a named parent with its mechanism — and returns an assessed consequence map with convergence points, a desirable/undesirable valence check and an implication-to-action table (Jerome C. Glenn's Futures Wheel, 1971). Use when asked \"what are the second-order effects of {change}?\", \"map the implications of {decision}\", \"futures wheel\", \"unintended consequences\" or \"and then what happens?\". Not for how likely a consequence is (use `bayesian-update`) or for branching alternative futures (use `scenario-planning`)."
license: MIT
metadata:
  category: foresight
  method: Futures Wheel
  origin: Jerome C. Glenn, 1971 (first published 1972; Futures Research Methodology V3.0, ch. 6, 2009)
  version: "2.0.0"
---
# Futures Wheel

The Futures Wheel identifies and organises the primary, secondary and tertiary consequences of a trend, event, decision or emerging issue: the change sits in the centre, primary impacts on spokes around it, and each further ring asks of *each* item "and because of that, what follows?" (Jerome C. Glenn, 1971; first published 1972). Its principle is structured brainstorming under a chain rule — every item hangs off one named parent by a stated mechanism — so the map is a causal picture, not word association. It defeats first-order thinking: the second- and third-order consequences usually decide strategy.

## When to invoke

Invoke when:

- One definite change is on the table and its knock-on effects matter: "what are the second-order effects of {change}?", "map the implications of {decision}".
- Someone asks for unintended consequences, ripple effects or a consequence map: "and then what happens?".
- A scenario, policy or launch plan needs stress-testing for side effects.

Do NOT invoke when:

- How likely a consequence is — a wheel carries no probabilities; use `bayesian-update`, or `delphi-method` for expert estimates.
- Which alternative futures could occur — use `scenario-planning`; a wheel elaborates one assumed future.
- Feedback loops and delays are the subject — a wheel is a tree, not a loop map; use `cross-impact-analysis`.
- The topic is vague ("the future of AI") — narrow it to a dated statement with `decompose-research-question`.
- Stress-testing a decision about to be committed — use `premortem-analysis`, which goes deep on failure; the wheel maps the whole consequence space.

## Procedure

Work ring by ring, never jumping ahead; three rings is the budget — readability collapses beyond that. Glenn supplies the wheel and the ring-by-ring question; the numeric scaffolding around it is this skill's own — the three-ring budget, the 5–10 primary-impact target, the "one named parent plus a stated mechanism" chain rule and the 70 % valence threshold are operational defaults set here, not figures from *Futures Research Methodology V3.0*.

### 1 — Write the central change statement

Put one definite occurrence at the centre, stated as if it had happened, with a quantity and a date: "30 % of a 2,000-person workforce is fully remote by 2028", not "remote work". Output: central statement.

### 2 — Generate the first ring of primary impacts

Ask "if this is true, what happens directly?" and place 5–10 primary impacts on spokes, one per bubble. Sweep domains deliberately — costs, behaviours, who loses, what becomes newly possible, regulation — so the ring is not all of one kind. Each must pass the chain test against the centre. Output: ring 1.

### 3 — Generate the second ring, parent by parent

Forget the centre and ask of *each* primary impact: "and because of that, what follows?" Add two to five children per parent, each recorded with its parent and mechanism. Include at least one unintended or perverse consequence per major branch — these surface here, not in production. Output: ring 2, every child linked to a parent.

### 4 — Generate the third ring

Apply the same rule one level further out. Insight concentrates here: third-order effects cross into domains the first ring never touched — municipal finance, labour law, supplier viability. Prune weak branches rather than expanding every node. Output: ring 3.

### 5 — Audit every link against the chain rule

Read each parent→child link as "because {parent}, therefore possibly {child}, since {mechanism}". Delete non-sequiturs and topic-adjacent items; mark speculative chains as such. Sweep for missing negatives: if more than about 70 % of items look desirable, the wheel is flattering the change. Output: cleaned wheel.

### 6 — Assess, mark convergence, and draw actions

Tag every surviving implication desirable (+), undesirable (−) or neutral (0), and circle **convergence points** — outcomes reached independently by two or more branches, the findings most worth acting on. For the top items decide: amplify, mitigate, monitor or research. Output: assessed wheel and implication-action table.

## Output template

```
## Futures Wheel — {central change statement, with quantity and date}

Ring 1 — primary impacts (direct):
1. {impact}
2. {impact}

Ring 2 — secondary impacts (each chained to a parent):
- {parent no.} → {impact} — because {parent}, therefore possibly {impact}, since {mechanism}

Ring 3 — tertiary impacts:
- {parent no.} → {parent} → {impact} — since {mechanism}

Convergence points: {outcomes reached by 2+ independent branches}
Valence check: {n desirable / n undesirable / n neutral} — {flag if >70 % one way}
Speculative chains: {links marked speculative}

| Implication | Ring | Valence | Action (amplify / mitigate / monitor / research) |
|---|---|---|---|
| {implication} | {1-3} | {+ / − / 0} | {action} |
```

Mandatory fields: the central statement with a date, every ring-2 and ring-3 item's parent and mechanism, the convergence points, the valence check and the implication-action table.

## Worked example

Central statement: "30 % of a 2,000-person workforce — about 600 people — is fully remote by 2028." Illustrative; one mid-size employer, single headquarters.

| Ring | Item | Chain |
|---|---|---|
| 1.1 | Office-space demand falls about 30 % | Direct: 600 staff no longer need a daily desk |
| 1.2 | Hiring pool widens beyond the headquarters metro | Direct: location stops filtering candidates |
| 1.3 | New joiners get far less in-person contact | Direct: fewer people on site on any given day |
| 1.4 | Coordination shifts to written and asynchronous channels | Direct: shoulder-tapping is unavailable |
| 2.1 | Lease renegotiated or subleased at renewal | Because 1.1, desk demand tracks attendance, so the footprint is oversized |
| 2.2 | Lunch and retail trade near the office falls | Because 1.1, several hundred daily commuters spend near home instead |
| 2.3 | Location-based pay becomes contested | Because 1.2, candidates in cheaper regions do the same job |
| 2.4 | Time-zone spread widens | Because 1.2, hiring is no longer metro-bound |
| 2.5 | Weak-tie networks thin out | Because 1.3, corridor and lunch encounters build cross-team ties |
| 3.1 | Municipal tax receipts near the district erode | Because 2.2, retail revenue and sales-tax receipts fall together |
| 3.2 | Pay-equity disputes or attrition of high-cost-city staff | Because 2.3, one job priced two ways angers one group |
| 3.3 | Decision latency rises | Because 2.4, synchronous overlap shrinks and approvals wait overnight |
| 3.4 | Cross-team idea flow declines | Because 2.5, novel combinations come mostly from acquaintances |

Convergence points: pressure on the headquarters district (via 1.1→2.1 and via 1.1→2.2→3.1); slower coordination (via 2.4→3.3 and via 1.4). Valence check: 3 desirable, 6 undesirable, 4 neutral — plausible; a version with no negatives would be suspect. Speculative: 3.1, since municipal revenue depends on the local tax base. Actions: mitigate 3.3 with written decision protocols; monitor 3.2 via a pay-band review; research 2.1 before the lease break date.

## Verification

- [ ] Every ring-2 and ring-3 item names one parent and its mechanism; topic-adjacent items were deleted.
- [ ] The wheel has at least two rings beyond the centre — a one-ring wheel is a list of obvious effects, not a futures wheel.
- [ ] At least one unintended consequence appears on each major branch, and the valence check is not over 70 % desirable.
- [ ] Convergence points were found by tracing two or more independent branches to one outcome.
- [ ] Speculative chains are marked as speculative rather than presented as established.
- [ ] Every top implication carries an action: amplify, mitigate, monitor or research.

## Pair with adjacent skills

- `scenario-planning` — one wheel per scenario stress-tests each future's side effects.
- `premortem-analysis` — goes deep on the failure branches the wheel maps broadly.
- `cross-impact-analysis` — rates mutual influence when the consequences interact rather than branch.
- `indicators-validation` — turns the convergence points into diagnostic indicators to monitor.
- `bayesian-update` — attaches probabilities to a chain the wheel surfaced.
- Methodology counterpart: [methodologies/foresight/futures-wheel.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/futures-wheel.md).

## Anti-patterns

- Do **not** let children be topic-adjacent instead of caused; every link needs a mechanism.
- Do **not** stop at ring 1; the method's value is rings 2 and 3.
- Do **not** let the wheel explode; beyond ten primary impacts and three rings it is unreadable.
- Do **not** mix grounded and speculative chains unmarked.
- Do **not** treat the map as probability analysis; the wheel is consequence topology.
- Do **not** run it on a vague topic; a theme yields mush, a dated statement yields a wheel.

## Reference

- J. C. Glenn, "The Futures Wheel," ch. 6 in J. C. Glenn and T. J. Gordon (eds.), *Futures Research Methodology — Version 3.0*. Washington, DC: The Millennium Project, 2009. ISBN 978-0-9818941-1-9 — the inventor's account: invented 1971, primary/secondary/tertiary impacts, ring-by-ring procedure, variants (Implementation Wheel, Impact Wheel, Mind Mapping, Webbing).
- J. C. Glenn, "Futurizing Teaching vs Futures Course," *Social Science Record*, Syracuse University, vol. IX, no. 3, Spring 1972 — the method's first appearance in the literature.
- D. P. Snyder, *The Futures Wheel: A Strategic Thinking Exercise* (monograph). Bethesda, MD: The Snyder Family Enterprise, 1993 — the workshop form cited by Glenn.
- UK Government Office for Science, *The Futures Toolkit*, edition 1.0, 2017 (2024 edition current) — the futures-wheel exercise in government practice. https://www.gov.uk/government/publications/futures-toolkit-for-policy-makers-and-analysts
