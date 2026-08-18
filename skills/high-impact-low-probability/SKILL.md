---
name: high-impact-low-probability
description: "Takes one event judged unlikely but devastating, postulates it has happened, and reasons backwards to the pathways that could produce it — returning the impact, 2–4 distinct pathways with their triggers, observable early-warning indicators, and a proportionate hedge (High-Impact/Low-Probability and \"What If?\" Analysis, US Tradecraft Primer 2009). Use when a severe scenario is being dismissed as improbable — \"what if the sole supplier were cut off?\", \"stress-test how this unlikely event could actually happen\", \"run a high-impact/low-probability analysis\". Not for a decision assumed to have failed (`premortem-analysis`) or a set of plausible futures (`scenario-planning`)."
license: MIT
metadata:
  category: foresight
  method: High-Impact/Low-Probability Analysis (with "What If?" Analysis)
  origin: US Government Tradecraft Primer, 2009; Heuer & Pherson reframing techniques
  version: "2.0.0"
---
# High-Impact/Low-Probability Analysis

An event everyone agrees is unlikely gets no analysis at all — so when it arrives nobody has a plan, and nobody noticed the warning signs. High-Impact/Low-Probability (HILP) analysis, a contrarian technique in the US Government's *Tradecraft Primer* (2009, pp. 22–23), breaks that reflex: it suspends the probability argument, postulates the event as fact, and asks **how it could have come about**. Its sibling "What If?" Analysis (same Primer, pp. 24–25) supplies the engine: think backwards, specifying what must occur at each stage. The deliverable is not a probability but pathways, the indicators each emits, and a hedge cheap enough to buy now.

## When to invoke

Invoke when:

- A severe outcome is waved away as improbable and its consequences were never thought through: "the fab will never be embargoed", "that regulator would never ban it".
- A judgment rests on thin information or an unproven assumption, and being wrong is expensive.
- Warning is the deliverable: someone must know *what to watch for* before the unlikely thing is obvious.

Do NOT invoke when:

- A decision is assumed to have failed and the question is why — `premortem-analysis` owns prospective hindsight on decisions, not external events.
- Several plausible futures must be spanned and compared — `scenario-planning`. HILP works one tail, not the distribution.
- Nothing is framed yet and a sweep for what could blindside the organisation is wanted — `horizon-scanning`.
- The event is not actually unlikely; if the honest estimate is "quite possibly", use `reference-class-forecasting`.

## Procedure — six steps

### 1 — Define the event precisely

One sentence fixing **what** happens, to **whom/where**, **by when**, at what **magnitude**. "Supplier trouble" is not an event; "Supplier S ships nothing to the site for ≥ 6 months before 2027-12-31" is. Record why it is judged unlikely: the estimate, who holds it, the reasons. That definition justifies analysing what most people believe will not happen.

### 2 — Assess the impact if it occurred

Postulate the event as fact. First-order: which programmes, revenues, obligations and people are hit, and how fast. Second-order: what that damage causes — penalty clauses, a missed regulatory window, a competitor's opening. Quantify one consequence and state the **time to bite**: how long before the damage is irreversible. If it is modest, stop and say so.

### 3 — Build the pathways

Run the "What If?" move: assume the event has happened and think backwards, specifying what must occur at each stage. Produce **2–4 pathways** — distinct mechanisms, not one story retold. Each names its **trigger** (a shock, ruling, failure, price move) and its **decider**, the actor whose choice makes the next link happen; borrow triggers from analogous cases. Every link needs an actor, a mechanism and a lag.

### 4 — Derive indicators from the pathways

Walk each pathway and ask what would be **observable** while it unfolded but before the event itself. Write each as a dated, thresholded statement with source and owner — "export-licence approvals fall below 10 per quarter (customs bulletin; procurement lead)" — never a theme or an outcome. Aim for 2–4 per pathway, mixing early-ambiguous with late-unambiguous; `indicators-validation` then drops any that appear whichever pathway ran.

### 5 — Assess what would move the estimate, and hedge now

State what would make the event materially more likely (which trigger firing, which threshold crossed) and what would deflect it. Then answer the decision-maker's question: what should be done **differently today**? Keep it proportionate — a contract clause, a stock cover, a monitoring cadence — plus **decision triggers**: "if I2 fires, qualify a second source within 30 days".

### 6 — Report and schedule the review

Fill the output template, then set a review date and re-read the indicators on that cadence. Periodic review is what counters the mindset that such a development is impossible; an analysis never revisited restores the blind spot it removed.

## Output template

```
## High-Impact/Low-Probability — {event name}

**Event:** {what, where/to whom, by when, magnitude}
**Judged unlikely because:** {reasons} — estimate {~x%}, held by {who}
**Impact:** first-order {…}; second-order {…}; quantified {money/months}; time to bite {n weeks}

**Pathways (postulating the event has occurred):**
| # | Pathway (backwards chain) | Trigger | Decider | Lag | Lead indicator |
| P1 | {stage 3 ← stage 2 ← stage 1} | {shock/ruling} | {actor who chooses} | {n months} | {In} |
| P2 | … | … | … | … | … |

**Indicators (observable, dated, owned):**
| ID | Indicator (threshold) | Pathway | Source | Cadence | Owner |
| I1 | {statement with a number and a date} | P1 | {where it surfaces} | {monthly} | {role} |

**Would raise the estimate:** {trigger}   **Would deflect it:** {factor}
**Posture now:** hedges {cheap actions}; monitoring {cadence}; triggers {if In fires → do X within n days}
**Review by:** {YYYY-MM-DD}
```

Every field is mandatory. A report without indicators and a posture is a scary story, not a warning.

## Worked example

**Event:** *Kanto Substrate Co. — sole qualified supplier of the 6-inch germanium wafers in Aurora Photonics' detector line — ships nothing to Aurora for 6 months or more before 2027-12-31.* Judged unlikely (~4 %, procurement lead): Kanto has shipped uninterrupted since 2014, under a 2026–2029 agreement.

**Impact:** the detector line (41 % of 2026 revenue) halts 11 weeks after stock-out; 3 customer programmes miss 2028 milestones, costing ~EUR 2.4M in penalties; requalification takes 9–14 months.

| # | Pathway (backwards chain) | Trigger | Decider | Lag | Lead indicator |
| --- | --- | --- | --- | --- | --- |
| P1 | Licence denied ← germanium added to a dual-use control list ← trade dispute escalates | Control-list entry | Licensing ministry | 4–7 months | I1 |
| P2 | Allocation to defence primes ← capacity short ← a competing buyer signs a multi-year exclusive | Competitor lock-up | Kanto sales board | 6–9 months | I2 |
| P3 | Plant offline ← seismic damage at the Sendai site ← no alternate line | Earthquake | Kanto operations | 0 months | I3 |

**Indicators:** I1 — germanium or 6-inch substrates appear in a draft control-list consultation (gazette; monthly; compliance lead). I2 — Kanto quotes lead times above 26 weeks for two consecutive quarters (purchase records; quarterly; procurement lead). I3 — Kanto discloses single-site production (supplier audit; annual; quality lead).

**Posture now:** 16 weeks of buffer stock (EUR 180K, ~7 % of penalty exposure); a 90-day notice-of-allocation clause at the 2027 renewal; lab-scale sampling of a second vendor. **Decision trigger:** if I1 or I2 fires, qualify a second source within 30 days. **Review by:** 2027-03-31. *(Illustrative case; figures constructed.)*

## Verification

Before the report ships, confirm:

- [ ] The event carries all four bounds — what, where/whom, by when, magnitude — plus why it is judged unlikely.
- [ ] The impact quantifies one consequence, states the time to bite, and names second-order effects.
- [ ] There are 2–4 pathways, each with a different trigger and decider; no step is merely "and then it happens".
- [ ] Every indicator is observable before the event, with threshold, source, cadence and owner, and maps to a named pathway; no pathway is left unwatched.
- [ ] The posture is proportionate — cheap hedges plus decision triggers, not a programme priced as if the event were likely — and a review date is set.

## Pair with adjacent skills

- `premortem-analysis` — imagines a *decision* has failed; HILP works one external event and how it could arise.
- `scenario-planning` — builds a spanning set of futures; a HILP event stresses that set instead of joining it.
- `futures-wheel` — takes the event as given and maps its consequence rings; use it to deepen step 2.
- `horizon-scanning` — the sweep that nominates candidates; severe-impact, low-estimate radar issues belong here.
- `key-assumptions-check` — audits the "it cannot happen" premise; a sensitive, weakly-grounded one is a HILP candidate.
- `indicators-validation` — validates the step-4 list against rival pathways, producing a monitoring plan.

## Anti-patterns

- Do **not** turn it into a probability debate. The move is to suspend the likelihood argument and ask *how*; "it's only 3 %" is not analysis.
- Do **not** list a dozen black swans. One bounded event per run; a catalogue of catastrophes gets skimmed, not watched.
- Do **not** write pathways whose links are "it happens". Every stage needs an actor, a mechanism, a lag.
- Do **not** use outcomes as indicators. "Supply is interrupted" is the event; an indicator shows while the pathway runs.
- Do **not** hedge everything — buy cheap options, and name the trigger that releases the expensive ones.
- Do **not** file it and move on. Indicators nobody reads are worse than none; the review date is part of the method.

## Reference

- U.S. Government, *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis*, March 2009, pp. 22–23 "High-Impact/Low-Probability Analysis" and pp. 24–25 "'What If?' Analysis" (Contrarian Techniques) — method steps, plus the Pearl Harbor, 9/11 and Yugoslavia 1990 illustrations. https://www.cia.gov/resources/csi/static/Tradecraft-Primer-apr09.pdf
- R. H. Pherson and R. J. Heuer Jr., *Structured Analytic Techniques for Intelligence Analysis*, 3rd ed. Thousand Oaks, CA: CQ Press / SAGE, 2019 — the Reframing Techniques family, carrying both techniques alongside Premortem Analysis. ISBN 978-1-5063-6893-1.
- N. N. Taleb, *The Black Swan: The Impact of the Highly Improbable*. New York: Random House, 2007 (2nd ed. 2010) — context for why tail events go under-analysed; not this method's source. ISBN 978-0-679-60418-1.
