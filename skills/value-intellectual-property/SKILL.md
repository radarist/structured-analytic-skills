---
name: value-intellectual-property
description: "Values an early-stage patent, software right, know-how bundle or other IP asset with an explicit valuation purpose, base date and evidence set; selects cost, market, income/DCF, probability-adjusted NPV or real-options framing; and returns a defensible range with sensitivities instead of a false-precision price. Use when asked to \"value this patent portfolio\", \"estimate a licensing value\", \"calculate rNPV for this IP\", or \"what is this university invention worth?\". Not for claim scope or patent crowding — use `analyze-patent-claims` or `read-patent-landscape` instead."
license: MIT
metadata:
  category: technology-assessment
  method: WIPO IP valuation using cost, market, income, rNPV and real-options approaches
  origin: WIPO Intellectual Property Valuation Basics, 2025
  version: "2.1.0"
---
# Value Intellectual Property

Value an early-stage intellectual-property asset using the World Intellectual Property Organization's 2025 technology-transfer guidance. The method treats value as purpose-, party-, date- and assumption-specific. It selects among cost, market, income, risk-adjusted net present value (rNPV), and real-options thinking, then reconciles the evidence into a range. It prevents two recurrent innovation errors: treating development spend as economic value and presenting a fragile discounted-cash-flow point estimate as a transaction price.

## When to invoke

Invoke for a patent, copyright/software right, trade secret, know-how package, data right, brand, or mixed bundle when a team must set a licensing range, portfolio carrying view, negotiation anchor, investment screen, or internal resource-allocation value.

Do not invoke for:

- Patent claim scope, validity or freedom-to-operate — use `analyze-patent-claims` and qualified patent counsel.
- Ownership concentration, filing velocity or white-space mapping across many families — use `read-patent-landscape`.
- A go/stop decision whose output is expected value rather than an asset valuation — use `expected-value-decision-tree`.
- A market forecast with no identified IP asset — use `estimate-market-size` first.

## Procedure

### 1 — Fix the valuation question before calculating

State the asset boundary, owner, intended user, valuation purpose, base date, currency, jurisdiction, transaction premise and remaining economic life. Separate registered rights from unregistered know-how, data, software and implementation support. A licensing negotiation, tax allocation, damages opinion and internal portfolio screen can produce different values from the same cash flows; never recycle one without restating its premise. Record exclusions such as future improvements, trademarks, regulatory data exclusivity or founder services. Repeat that scope beside the final range so the conclusion cannot detach from it.

### 2 — Build an evidence ledger for rights and economics

Verify ownership, inventors/authors, encumbrances, jurisdictions, legal status, expiry, prosecution or renewal risk, claim breadth, design-around paths and third-party dependencies. Then collect development cost, replacement time, comparable licences or sales, forecast revenue, incremental margin, royalty base, adoption timing, development milestones, success probabilities, remaining investment, tax, discount rate and terminal assumptions. Tag each input as observed, comparable-derived, management estimate or analyst assumption, with source date and confidence.

### 3 — Select approaches that fit the evidence

Use **cost** as a substitution ceiling — no rational buyer pays more than lawfully recreating an equivalent would cost — and as a negotiation fact, never as proof of economic benefit; the ceiling binds only where recreation is open to that buyer. Use **market** when genuinely comparable arm's-length licence or sale terms exist and adjust for territory, exclusivity, maturity, scope and date. Use **income/DCF** when incremental cash flows attributable to the IP can be separated. Use **rNPV** for staged technical or regulatory programs by weighting each cash flow with its unconditional occurrence probability. Use **real-options framing** when management can continue, delay, expand, license or abandon after learning; model the decisions with `expected-value-decision-tree` rather than dropping a Black–Scholes number into an illiquid project.

### 4 — Calculate a range and expose sensitivities

Compute at least low, base and high cases. For DCF, show annual cash flows, discount rate, explicit forecast horizon and terminal value separately. For rNPV, distinguish conditional stage success from the cumulative/unconditional probability applied to each cash flow. For market comparables, show raw consideration, adjustment factor and adjusted value. Run the dominant uncertain inputs across credible bands — usually time to launch, probability of success, royalty rate, addressable revenue, remaining life and discount rate — and name the variables that move value most.

### 5 — Reconcile without averaging away disagreement

Explain why each approach deserves its weight. Cost, market and income estimates can disagree because they answer different questions; a weighted reconciliation is useful only when the weights reflect evidence quality and purpose. When market or income evidence is available, keep replacement/reproduction cost as a separate cross-check rather than weighting it into economic value, unless the stated premise specifically values replacement or recreation. Report the approach range before any combined estimate, keep unsupported approaches as `not available`, and explain large gaps. Cross-check that the IP-attributable value does not exceed the economics of the product, business or transaction it enables without an explicit reason.

### 6 — Convert the valuation into a bounded decision

Return a value range, a base-case reference point, the purpose for which it is usable, a sensitivity table, evidence gaps, and a negotiation or experiment recommendation. State that the result is an analytic estimate and **not a valuation opinion**: it must not be relied on as one, nor as legal, tax, accounting, investment or fairness advice. Tax, transfer-pricing, damages, litigation and financial-reporting uses are a hard stop — route them through `abstain-or-escalate` to a qualified valuer, handing over the input ledger and model rather than the headline number.

## Output template

```json
{
  "asset": "{rights and know-how included}",
  "purpose": "{licensing | internal screen | investment | other}",
  "base_date_currency": "{YYYY-MM-DD, currency}",
  "premise_and_exclusions": ["{premise}", "{excluded asset}"],
  "approaches": {
    "cost": {"status": "used | not available", "range": [0, 0], "basis": "{evidence}"},
    "market": {"status": "used | not available", "range": [0, 0], "basis": "{comparables}"},
    "income_or_rnpv": {"status": "used | not available", "range": [0, 0], "basis": "{model}"}
  },
  "reconciled_range": [0, 0],
  "base_case": 0,
  "dominant_sensitivities": [{"input": "{name}", "band": [0, 0], "value_effect": [0, 0]}],
  "evidence_gaps": ["{gap}"],
  "decision_use": "{what this estimate can support}",
  "professional_review": ["{legal | tax | accounting | valuation specialist}"]
}
```

Mandatory: asset boundary, purpose, base date/currency, premise, evidence provenance, per-approach range or `not available`, reconciled range, dominant sensitivities, evidence gaps, decision use and professional-review gate.

## Worked example

**Hypothetical teaching example — institution, counterparties, patent number and every figure below are invented. `EP 9 999 999 A1` is not a real publication and nothing here may be cited as evidence.**

Northmoor University is considering an exclusive EU licence of EP 9 999 999 A1 plus its spin-out Verdanix Bio's cell-culture know-how to Torvell Pharma on 30 June 2026. The bundle has 12 years of expected economic life, EUR 1.8 million replacement cost and three arm's-length university comparables of EUR 3.2 million, EUR 4.5 million and EUR 5.1 million after territory and maturity adjustments. The application is still pending, so WIPO's purpose-and-evidence discipline keeps claim risk explicit rather than calling it a granted moat.

The income model uses incremental annual cash flows of EUR 0.4m, 0.9m, 1.5m, 2.0m and 2.2m, an 18% discount rate and no terminal value beyond the explicit period. `ipvalue.py income` returns EUR 3.89m present value. Low/base/high success and launch scenarios produce EUR 2.4m / 4.0m / 7.1m. Replacement cost remains a separate substitution cross-check. The team reconciles only market and income indications, weighting market 0.40 and income 0.60 because the comparables are relevant but the attributable-margin forecast remains the strongest decision evidence:

```bash
$ python3 scripts/ipvalue.py triangulate --estimates 4.5,3.89 --weights 0.40,0.60 --json
{"estimate":4.134,"high":4.5,"low":3.89,"normalized_weights":[0.4,0.6]}
```

The output is a EUR 2.4m–7.1m negotiation range with EUR 4.13m as a reference point, not a sale price. The EUR 1.8m replacement cost is disclosed beside it as a substitution ceiling that does not bind here, because the assumed exclusivity blocks lawful recreation. The largest sensitivities are launch delay (18 months), technical success (45%–70%), EU exclusivity, and the royalty-bearing margin. Counsel must verify chain of title and Torvell's field-of-use terms; a tax adviser must review any cross-border structure.

## Verification

- [ ] The final conclusion repeats the exact asset boundary, purpose, base date, currency, premise and exclusions.
- [ ] Every input has a source date and evidence tag; legal status came from an official register.
- [ ] DCF totals recompute from the stated cash flows and rate; rNPV uses unconditional occurrence probabilities.
- [ ] Comparable adjustments are visible and no unavailable approach is represented as zero.
- [ ] Replacement/reproduction cost stays outside economic reconciliation unless the stated premise makes it directly relevant.
- [ ] Low/base/high cases move the dominant inputs, and the headline remains inside the approach/scenario evidence.
- [ ] The output states it is not a valuation opinion, and tax, transfer-pricing, damages, litigation and financial-reporting uses are gated to a qualified valuer.

## Companion tool

`scripts/ipvalue.py` is a deterministic arithmetic aid for steps 3–5. It discounts explicit cash flows (`income`), probability-adjusts cash flows before discounting (`rnpv`), adjusts and ranges comparable values (`market`), and combines approach estimates with visible normalized weights (`triangulate`). Use `--json` for machine-readable output and `--selftest` for hand-checked assertions. The tool never supplies assumptions or selects a valuation premise.

## Pair with adjacent skills

- `analyze-patent-claims` — establish the scope and legal uncertainty of a named patent before valuing it.
- `read-patent-landscape` — measure ownership concentration, filing momentum and crowding around the asset.
- `expected-value-decision-tree` — model continue, delay, licence, expand and abandon decisions after learning.
- `estimate-market-size` — supply a demand-side cross-check for attributable revenue.
- `decision-matrix-mcda` — compare portfolio projects when strategic criteria cannot defensibly be monetized.

## Anti-patterns

- Do **not** equate sunk R&D expenditure, replacement cost, funding valuation or patent count with IP value.
- Do **not** hide an unavailable comparable set behind an industry royalty rule of thumb.
- Do **not** apply one probability to every staged cash flow or mix nominal cash flows with a real discount rate.
- Do **not** report a point estimate without purpose, date, premise, range and sensitivities.
- Do **not** present this as a valuation, fairness, tax, legal, accounting, infringement or investment opinion.

## Reference

- World Intellectual Property Organization, *Intellectual Property Valuation Basics for Technology Transfer Professionals*, 2025, WIPO Publication 2004E, ISBN 978-92-805-3683-6, doi:10.34667/tind.50113 — objectives and premises; cost, market, income, real-options and Monte Carlo approaches; assumption and sensitivity discipline. https://doi.org/10.34667/tind.50113
- World Intellectual Property Organization, *Intellectual Property Valuation in Biotechnology and Pharmaceuticals*, 2025, publication record 4810 — market, risk-adjusted NPV and real-options methods for staged biotechnology assets. https://www.wipo.int/publications/en/details.jsp?id=4810
