---
name: apply-hype-cycle
description: "Places one discontinuous technology on the five phases of Gartner's Hype Cycle — Innovation Trigger, Peak of Inflated Expectations, Trough of Disillusionment, Slope of Enlightenment, Plateau of Productivity — by counting sourced indicators, then reports the phase, a time-to-plateau range and the stall risk. Use when asked \"is X overhyped?\", \"what hype cycle stage is X at?\", \"has X come out of the trough of disillusionment?\" or \"how long until X is boring infrastructure?\". Not for evidence of technical maturity (use `score-technology-readiness`) or one dated prediction (use `foresight`)."
license: MIT
metadata:
  category: technology-assessment
  method: Gartner Hype Cycle placement
  origin: Jackie Fenn, Gartner, 1995; Fenn & Raskino, 2008
  version: "2.0.0"
---
# Apply Hype Cycle

The Hype Cycle, introduced by Jackie Fenn at Gartner in 1995 and set out as a method in Fenn and Raskino's *Mastering the Hype Cycle* (2008), describes how expectations about a discontinuous innovation run ahead of its capability and then collapse before real productivity arrives. Its core principle is that visibility and capability are different curves: attention peaks early, competence arrives late, and the gap between them strands adopters. This skill derives the placement from observable indicators — press volume, funding, failed deployments, reference architectures, commoditisation — rather than repeating a published chart, so the phase can be defended and re-derived when the evidence moves. It prevents buying at the Peak and abandoning in the Trough.

## When to invoke

Invoke when:

- Asked "is X overhyped?", "what hype cycle stage is X at?", "has X passed the trough of disillusionment?" or "how long until X is mainstream?".
- An adoption or investment decision turns on whether enthusiasm about a technology is proportionate to what it can do.
- Strong press and weak deployments (or the reverse) conflict, and the divergence needs naming.

Do NOT invoke when:

- The question is what the technology can actually do or how proven it is — use `score-technology-readiness`.
- The question wants one dated, falsifiable prediction with kill-signals — use `foresight`.
- The question is which strategic method fits the component today — use `evolution-stage`.
- The subject is a market, company or funding round rather than a technology — a market mixes technologies at several phases; route market structure to `five-forces-analysis`.
- The subject is a sustaining improvement (a faster chip generation, a point release): the Hype Cycle models discontinuous innovation, and incremental improvement has no trigger — as does a technology less than about six months past first public disclosure, where indicator density is too thin to count.

## The five phases

1. **Innovation Trigger** — first demos, papers or patents; specialist coverage; nascent funding.
2. **Peak of Inflated Expectations** — mass-media coverage, absolute vendor language, funding surge.
3. **Trough of Disillusionment** — public failures, consolidation, sceptical retrospectives, narrowed scope.
4. **Slope of Enlightenment** — reference architectures, measured case studies, vertical variants.
5. **Plateau of Productivity** — infrastructure language, named job roles, buying on price and support.

Per-phase indicator checklists are in `references/hype-indicators.md`. Those checklists, the per-phase indicator budgets, the placement rule in step 3 and the year bands in step 4 are this skill's own construction, derived from the published phase descriptions — Fenn and Raskino supply the phases and the curve, not an indicator list, a counting rule or a dwell-time table. Treat the year bands as illustrative priors, not schedules: some technologies never leave the Trough, and Dedehayir and Steinert (2016) show the curve is a stylised composite, not a validated trajectory.

## Procedure

### 1 — Narrow the subject

State one discontinuous technology with a scope boundary. "AI" cannot be placed; "LLM-based autonomous agents for enterprise task automation" can. Narrow until every indicator can be evaluated against that exact thing, and say what the scope excludes — a broad label averages technologies sitting in different phases.

### 2 — Count sourced indicators per phase

Work through all five checklists in `references/hype-indicators.md`. Confirm an indicator only with a citation — a dated article, a filing, a funding entry, a published architecture, a named deployment — and record the count per phase as *confirmed / total*. An indicator that cannot be sourced counts for nothing.

### 3 — Place on the phase with the most confirmations

The phase with the highest confirmed count is the placement. On a tie take the *earlier* phase: later-phase indicators are often anticipatory (an announced reference architecture is not a used one). If the placement is Trough and the technology has sat there five years or more with no Slope indicators, record it as stalled rather than pre-Slope.

### 4 — Estimate time-to-plateau as a range

From the current phase project a range, not a point, starting from this skill's illustrative priors: Trigger 5–8 years, Peak 4–7, Trough 3–5 (or never, if stalled), Slope 1–3. Widen it whenever the underlying cost or capability curve is not public, and report the reason the range is wide.

### 5 — Calibrate against a named peer trajectory

Name one or two past technologies whose arc resembles this one and state where their Trigger-to-Plateau time actually landed, including at least one that stalled or was obsoleted. If the step-4 estimate contradicts every peer, revisit it: peer calibration is the check on wishful timing.

### 6 — Report what would move the placement

Name the specific indicator shifts that would re-place the technology in either direction, so the placement is revisited when the evidence changes rather than re-argued from scratch.

## Output template

```
## Hype Cycle placement — {technology}

**Subject:** {narrow-scoped technology; what is excluded}
**Phase: {N}. {Innovation Trigger | Peak of Inflated Expectations | Trough of Disillusionment | Slope of Enlightenment | Plateau of Productivity}**

**Confirmed indicators (sourced):**
- Innovation Trigger: {n}/5
- Peak of Inflated Expectations: {n}/6
- Trough of Disillusionment: {n}/5   ← placement (most confirmations)
- Slope of Enlightenment: {n}/5
- Plateau of Productivity: {n}/5

**Evidence:** {indicator} — {citation}; {indicator} — {citation}

**Peer calibration:** {named past technology} — {actual Trigger-to-Plateau time or stall}
**Time-to-plateau:** {low}–{high} years — range is wide because {reason}
**Stall risk:** {low | medium | high} — {why}
**What would move this placement:** {indicator shifts, in both directions}
```

Mandatory fields: subject with scope, phase named in full, per-phase counts, ≥3 cited indicators, the time-to-plateau range and the stall risk. A placement without citations is an opinion.

## Worked example

Subject: solid-state batteries for electric vehicles (cell and pack engineering, not laboratory chemistry), assessed at a fixed point in time. Illustrative data — the counts stand in for a real indicator sweep.

Sweep: two manufacturers run pilot lines shipping sample cells to OEMs (Slope-shaped); general-press coverage has fallen sharply from the "battery revolution" headlines of two years earlier (post-Peak); three startups missed announced production dates and one was acquired below its peak valuation (Trough); pilot cost per kWh is roughly 3–4× incumbent cells; no mass-production vehicle is on sale (not Plateau).

```
## Hype Cycle placement — solid-state EV batteries

**Subject:** solid-state cells and packs for passenger EVs; excludes lab-scale chemistry and grid storage
**Phase: 3. Trough of Disillusionment**

**Confirmed indicators (sourced):**
- Innovation Trigger: 1/5
- Peak of Inflated Expectations: 1/6
- Trough of Disillusionment: 4/5   ← placement (most confirmations)
- Slope of Enlightenment: 2/5
- Plateau of Productivity: 0/5

**Evidence:** missed production dates at 3 startups — company filings; 1 acquisition below peak valuation — deal reporting; general-press coverage down sharply — coverage counts, 24-month window; OEM sample-cell shipments with published specs — OEM announcements (Slope, confirmed)

**Peer calibration:** lithium-ion took ~10 years from working prototype to mass-market cost parity; hydrogen fuel-cell passenger cars stalled in the Trough instead
**Time-to-plateau:** 5–10 years — range is wide because pilot-line cost curves are not published
**Stall risk:** medium — pilot progress is real, but cost parity is unproven and incumbent chemistry keeps improving
**What would move this placement:** a mass-production vehicle on sale (→ Slope/Plateau); further OEM pilot cancellations (→ stall)
```

Reading: 4 of 5 Trough indicators against 2 Slope indicators places the technology in the Trough — the OEM shipments are real but outnumbered. One comparator reached the Plateau in a decade and one never did: hence the five-year band and a medium stall risk.

## Verification

- [ ] The subject is one discontinuous technology with a stated scope boundary, not a market or company.
- [ ] Every counted indicator carries a citation; unconfirmed indicators were left uncounted, not inferred.
- [ ] Per-phase counts are shown; the placement is the phase with the most confirmations, ties resolved to the earlier phase.
- [ ] The phase uses the published wording (Innovation Trigger / Peak of Inflated Expectations / Trough of Disillusionment / Slope of Enlightenment / Plateau of Productivity).
- [ ] Time-to-plateau is a range with a reason for its width, and one peer that stalled or was obsoleted was considered.
- [ ] The placement is derived from indicators, not copied from a published Hype Cycle chart.

## Pair with adjacent skills

- `score-technology-readiness` — TRL is evidence of what has been built; the phase is how the market talks about it. TRL 8 in the Trough is underrated infrastructure; TRL 3 at the Peak is overbought.
- `evolution-stage` — Wardley evolution gives the present strategic position; the Hype Cycle gives the arc through time.
- `assess-research-momentum` — publication and citation curves lead the Trigger and Peak phases.
- `foresight` — converts a placement into one dated, falsifiable prediction with kill-signals.
- `oss-project-health` — for open-source technologies, project vitality supplies Slope and Plateau indicators.

## Anti-patterns

- Do **not** cite a published Hype Cycle chart as the answer. That is someone else's placement; this method earns one from indicators.
- Do **not** apply the curve to a market or a category. Markets contain technologies at several phases at once.
- Do **not** report a point estimate for time-to-plateau; dwell times vary enormously and some technologies never traverse the curve.
- Do **not** treat absence of evidence as a Trough indicator — a quiet technology may simply be unreported.
- Do **not** pick only peers that succeeded; the stalled comparator keeps the estimate honest.

## Reference

- J. Fenn and M. Raskino, *Mastering the Hype Cycle: How to Choose the Right Innovation at the Right Time*. Boston, MA: Harvard Business Press, 2008. ISBN 978-1-4221-2110-8 — the method, the five phases and the adoption-timing decision framework. The Hype Cycle itself was introduced by Jackie Fenn at Gartner in 1995.
- O. Dedehayir and M. Steinert, "The hype cycle model: A review and future directions," *Technological Forecasting and Social Change*, vol. 108, pp. 28–41, 2016. doi:10.1016/j.techfore.2016.04.005 — the critical review: the curve is a stylised composite, not an empirically validated trajectory.
- E. M. Rogers, *Diffusion of Innovations*, 5th ed. New York: Free Press, 2003. ISBN 978-0-7432-2209-9 — the adoption-curve tradition behind the visibility curve.
