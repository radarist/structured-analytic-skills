---
name: three-horizons
description: "Tags every bet in a portfolio with a growth horizon — H1 defend-and-extend the core, H2 build emerging businesses, H3 create options for the future — and holds each to the evidence bar its horizon deserves, exposing a portfolio starved at one horizon. Use when several investments are proposed together — \"three horizons for this portfolio\", \"which of these bets are core versus exploratory?\", \"is the investment mix balanced?\", \"H1/H2/H3 tagging for the roadmap\". Not for placing one technology on a maturity curve (use `evolution-stage`) or for a single dated prediction (use `foresight`)."
license: MIT
metadata:
  category: decision-strategy
  method: Three Horizons of Growth (McKinsey)
  origin: Mehrdad Baghai, Stephen Coley and David White, 1999 (The Alchemy of Growth)
  version: "2.0.0"
---
# Three Horizons

Three Horizons is a portfolio-balance framework: growth needs businesses defended today (H1), built for tomorrow (H2), and seeded as options for the day after (H3) — all managed **concurrently**. Baghai, Coley and White set it out in *The Alchemy of Growth* (1999). Its core principle: each horizon earns a different evidence bar and method — an H3 option judged on H1's hard-ROI threshold dies before it teaches anything, an H1 extension given H3's patience wastes a year. It prevents the undeclared portfolio — bets that look comparable, justified with the same numbers, hiding that nothing is being built beyond this year.

## When to invoke

Invoke when:

- Several investments or product bets are proposed together and the reader must allocate capital or attention across them.
- A roadmap mixes core optimisations with speculative bets and demands the same business case of both.

Do NOT invoke when:

- One technology's maturity is the question — `evolution-stage` for its stage, `apply-hype-cycle` for the hype curve.
- A single dated, falsifiable prediction is wanted — use `foresight`.
- A single bet needs validating rather than a portfolio classifying — use `cheapest-experiment`.
- The choice is between options on weighted criteria — use `decision-matrix-mcda`.
- The question is how the environment could unfold over years — use `scenario-planning`.

## Procedure — tag, evidence, balance

### 1 — Tag every bet with one horizon

For each named investment ask which description fits. **H1**: the core businesses most readily identified with the company, providing the greatest profits and cash flow; the work is defending and extending performance. **H2**: emerging opportunities — rising ventures likely to generate substantial profits later but requiring considerable investment now. **H3**: ideas for profitable growth further out — research projects, pilot programmes, minority stakes; options, not plans. Pick one horizon per bet — refusing to choose is what the framework exists to stop; a straddling bet is split into its parts.

### 2 — Attach a time-to-impact estimate with confidence

State when the bet first produces measurable revenue or cost impact, with units and confidence: high where pilot data exists, medium where a comparable reference exists, low where reasoned from priors. "H2, 18–24 months, medium confidence (one lighthouse pilot, no second comparable)" is usable; "H2, a few years" is not — re-scope or drop the bet rather than ship a vague range. As indicative guidance only (the source fixes no time bands), practitioners commonly read H1 as roughly 0–12 months, H2 as 1–3 years, H3 as 3–5 years; horizons are defined by the *state of the business*, not the calendar, so state the band used.

### 3 — Set the evidence bar and method per horizon

Translate the horizon into what the bet must show and how it is run:

| Horizon | Purpose | Evidence bar | Method |
|---|---|---|---|
| **H1** | Defend and extend the core | Hard ROI, validated demand, named customers | Stage-gate go/no-go |
| **H2** | Build emerging businesses | Pilot data, named early customers, leading indicators | Innovation accounting, build–measure–learn |
| **H3** | Create options | A thesis, named weak signals, optionality preserved | Probes, thesis-and-watchlist |

Each bet carries an implication line naming the bar that applies, so an H3 thesis is not killed by a hurdle rate it was never meant to clear.

### 4 — Report the mix and flag the imbalance

Sum the bets by horizon — by capital, attention or count, saying which — and state the imbalance plainly: all-H1 means no future, all-H3 no business. Nagji and Tuff (*Harvard Business Review*, 2012) found better-performing firms allocated roughly **70 % core / 20 % adjacent / 10 % transformational**, returns running the inverse way; that ratio is from their ambition matrix, not *The Alchemy of Growth*, and is a benchmark, not a target Three Horizons prescribes. Report the actual mix, the comparison, and the starved horizon.

## Output template

```
## Three Horizons — {portfolio or roadmap}

| Bet | Horizon | Time to first impact | Confidence | Evidence bar | Method | Implication |
|---|---|---|---|---|---|---|
| {bet} | {H1/H2/H3} | {range with units} | {high/med/low} | {hard ROI / innovation accounting / weak-signal thesis} | {stage-gate / build-measure-learn / thesis-and-watchlist} | {how to judge this bet} |

**Mix:** {x}% H1 / {y}% H2 / {z}% H3 — by {capital | attention | count}
**Benchmark comparison:** {vs the 70/20/10 core/adjacent/transformational finding, Nagji & Tuff 2012}
**Imbalance flag:** {none | over-indexed on H1 | starving H3 | …}
**Split bets:** {bet — which part is H{n} and which is H{m}}
```

Every bet must carry a horizon, a unit-bearing time-to-impact estimate with confidence, and an evidence bar; the mix line and imbalance flag are mandatory whenever three or more bets are listed.

## Worked example

Illustrative case (all figures invented): Kestrel Logistics, a European freight broker, brings six bets to its 2027 planning round with €48 M discretionary budget.

| Bet | Horizon | Time to first impact | Confidence | Evidence bar | Method | Implication |
|---|---|---|---|---|---|---|
| Pricing-engine rebuild for the core brokerage | H1 | 6–9 months | High | Hard ROI: ≥ 4 % margin on €300 M booked freight | Stage-gate | Kill if lift under 2 % at the month-9 gate |
| Automated customs filing for shippers | H1 | 9–12 months | Medium | Named customers: 15 of the top 40 signed | Stage-gate | Judge on adoption, not story |
| Carrier marketplace for mid-size fleets | H2 | 18–24 months | Medium | Two pilots, GMV per carrier trending | Build–measure–learn | Expect validated learning at month 12, not revenue |
| Embedded freight insurance | H2 | 24–30 months | Low | One pilot, no second comparable | Build–measure–learn | Re-scope unless a second reference lands by Q3 |
| Autonomous-yard robotics stake | H3 | 3–5 years | Low | Thesis plus three weak signals | Thesis-and-watchlist | Quarterly review against signposts; no ROI hurdle |
| Hydrogen-corridor consortium seat | H3 | 5+ years | Low | Optionality: a seat at the standard-setting table | Thesis-and-watchlist | Judge on option value, not revenue |

**Mix:** 78 % H1 (€37.4 M) / 17 % H2 (€8.2 M) / 5 % H3 (€2.4 M) — by capital.
**Benchmark comparison:** against the 70/20/10 finding (Nagji & Tuff, 2012) the portfolio is heavy at the core, thin beyond it.
**Imbalance flag:** starving H3 — two options at 5 % of capital, both low confidence; if the H2 marketplace slips, 2030 is empty.
**Split bets:** the pricing engine's real-time carrier-bidding module is H2 (18 months, marketplace-dependent), separated from the H1 rebuild.

## Verification

Before the portfolio view ships:

- [ ] Every bet carries exactly one horizon; straddling bets were split into named parts, not tagged "H2–H3".
- [ ] Every time-to-impact estimate has units and a confidence level, and the horizon time bands are stated as indicative.
- [ ] Recompute the mix percentages from the figures; confirm they sum to 100 % and match the stated basis.
- [ ] Cross-check each evidence bar against its horizon — no hard-ROI hurdle on an H3 option, no weak-signal patience on an H1 extension.
- [ ] The 70/20/10 comparison is attributed to Nagji & Tuff (2012) as a benchmark, never as a Three Horizons target.
- [ ] The imbalance flag names the starved horizon and what breaks if the next-horizon bets slip.

## Pair with adjacent skills

- `evolution-stage` — places one technology on its maturity axis; H1 bets rest on product or commodity components, H3 bets on novel ones.
- `foresight` — supplies the dated prediction and kill-signals that become an H3 bet's watchlist.
- `cheapest-experiment` — designs the validation for each H1 and H2 bet.
- `cynefin-classification` — H3 bets are almost always Complex; H1 bets Clear or Complicated.
- `premortem-analysis` — stress-tests the portfolio as a whole, including over-indexing on one horizon.
- Methodology counterpart: [methodologies/foresight/three-horizons.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/three-horizons.md) — the Curry & Hodgson futures variant (*Journal of Futures Studies*, 2008), a different framework sharing the name.

## Anti-patterns

- Do **not** tag without a time-to-impact estimate; the unit-bearing number is the discipline, the letter alone decoration.
- Do **not** treat the horizons as a sequence — they run concurrently; "H1 this year, H2 next year" misreads the framework.
- Do **not** attribute 70/20/10 to *The Alchemy of Growth* — the ratio is Nagji & Tuff's core/adjacent/transformational finding (2012), and it is a benchmark, not a rule.
- Do **not** present indicative time bands as though the source fixed them; horizons describe a business's state, not calendar windows.
- Do **not** let H3 shelter unevidenced bets — an H3 thesis still needs named weak signals and a review cadence.
- Do **not** confuse this with the futures-studies Three Horizons (Curry & Hodgson) — same name, different framework.

## Reference

- M. Baghai, S. Coley and D. White, *The Alchemy of Growth: Practical Insights for Building the Enduring Enterprise*. Reading, MA: Perseus Books, 1999. ISBN 978-0-7382-0100-9 — the McKinsey three-horizons portfolio framework.
- "Enduring Ideas: The three horizons of growth," *McKinsey Quarterly*, Dec. 2009. https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/enduring-ideas-the-three-horizons-of-growth — McKinsey's restatement of the horizon definitions.
- B. Nagji and G. Tuff, "Managing Your Innovation Portfolio," *Harvard Business Review*, vol. 90, no. 5, pp. 66–74, May 2012. https://hbr.org/2012/05/managing-your-innovation-portfolio — the 70/20/10 core/adjacent/transformational allocation finding.
- A. Curry and A. Hodgson, "Seeing in Multiple Horizons: Connecting Futures to Strategy," *Journal of Futures Studies*, vol. 13, no. 1, pp. 1–20, Aug. 2008 — the futures-studies framework of the same name.
