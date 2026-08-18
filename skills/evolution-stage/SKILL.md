---
name: evolution-stage
description: "Tags a named technology, capability or vendor category with its Wardley evolution stage — Genesis, Custom built, Product (+rental) or Commodity (+utility) — anchored in observable evidence, and states the way of working that stage implies. Use when asked \"is this a product or still bespoke?\", \"build vs buy for X\", \"where are these tools in their lifecycle?\" or \"what evolution stage is X at?\". Not for the whole value chain and its dependencies (use `wardley-map-drafting`) and not for evidence of technical maturity (use `score-technology-readiness`)."
license: MIT
metadata:
  category: technology-assessment
  method: Wardley evolution stage (evolution axis)
  origin: Simon Wardley, Wardley Maps, 2016–
  version: "2.0.0"
---
# Evolution Stage (Wardley)

Simon Wardley's evolution axis, published in *Wardley Maps* from 2016, sorts every component by how evolved it is — **Genesis** (nobody sells it yet), **Custom built** (a few bespoke instances, each built to order), **Product (+rental)** (competing suppliers, published prices and documentation) and **Commodity (+utility)** (interchangeable supply bought on price and reliability). The core principle is that components move rightward as more people use them and what they do gets better defined, and that a stage's observable signature — how many suppliers exist, what leaving one costs, how long integration takes — determines which way of working succeeds. Applying one method everywhere is the failure this tagging prevents: running a Genesis experiment on a Commodity purchase wastes money, and running a Product playbook on a Custom-built component under-budgets the integration by months.

The evolution axis and its stage names are Wardley's, published in *Wardley Maps* (chapter 2, "Finding a Path", Medium, 2016) under the Creative Commons Attribution-ShareAlike 4.0 International licence, CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/); the diagnostics, tables and wording in this skill are this repository's own and carry its MIT licence.

## When to invoke

Invoke when:

- A brief, comparison or recommendation names specific technologies, tools or vendor categories and the reader must know how evolved each one is.
- The decision is build, buy, rent or outsource for a named capability — "is this a product or still bespoke?", "should this be built in-house?".
- A previous decision failed because a bespoke capability was treated as a finished product, or a commodity was custom-integrated.
- Several named options must be compared and one of them is obviously less evolved than the rest.

Do NOT invoke when:

- The whole value chain matters — the user need, the components beneath it and their dependencies. Use `wardley-map-drafting`; this skill scores one component at a time.
- The question is how proven the technology is in deployment evidence — use `score-technology-readiness`.
- The question is about market attention and expectation over time — use `apply-hype-cycle`.
- The comparison is really about what job the customer hires the technology for — use `jtbd-framing`.
- The stage cannot change anything: the contract is signed and the method is fixed.

## The four stages

| Stage | Signature | Way of working it implies |
|---|---|---|
| **Genesis** | No supplier sells it; every known deployment is an experiment; informed people disagree about its scope | Agile, experimental, time-boxed; expect to scrap and rebuild |
| **Custom built** | Several bespoke instances, each built to order by consultants or in-house teams; multi-month integration re-estimated per environment | Lean, borrowed from the closest comparable build |
| **Product (+rental)** | Defined category, competing vendors, documented integration patterns, published roadmap and reference customers | Playbook-driven adoption anchored on the vendor roadmap |
| **Commodity (+utility)** | Indistinguishable between suppliers; bought on price and reliability; treated as background infrastructure | Utility purchase; do not custom-integrate |

Evolution runs one way: Genesis → Custom built → Product → Commodity, driven by supply and demand competition. The strategic question is where the component sits *now*. Eight observable placement questions — supplier count, cost of switching, how it is paid for, time to integrate, public artefacts, who can operate it, whether informed people agree on its scope, and what a failure in it means — are in [references/placement-signals.md](references/placement-signals.md).

## Procedure

### 1 — Place the component on the axis

Ask the four diagnostic questions in order: is this the first or only example of its kind (Genesis); are there a handful of comparable implementations, all bespoke (Custom built); is it a defined category with competing vendors, documented integration patterns and named reference customers (Product); is it bought on price and service level with no meaningful differentiation (Commodity)? Pick one stage — the act of picking is the work. Where a component is genuinely mid-transition, write "Custom-to-Product transitional" and give both rationales; the lower stage's way of working usually still applies during the transition.

### 2 — Anchor the placement in observable evidence

Every placement needs a one-line rationale citing something countable or checkable: number of named reference customers, typical integration time, the existence of a published breaking-change log, whether integration patterns are documented, whether the price is per-seat list or negotiated per deployment. "It has customers" is not evidence — every product has customers, and the rationale has to reflect the category's signature. Cross-check at least two of the eight placement questions in [references/placement-signals.md](references/placement-signals.md), weighting supplier count and switching cost above the rest; when only vendor self-description supports the placement, mark it as an estimate and lower the confidence of any recommendation resting on it.

### 3 — Translate the stage into a way of working

State the method the stage implies in one sentence, using the table above, and check it against what the surrounding brief actually recommends. A recommendation to build a custom orchestration layer on top of a Product-stage platform treats a Product as Custom built — sometimes right, always expensive, and the mismatch must be named rather than left implicit.

### 4 — Flag cross-stage comparisons

When two compared components sit at different stages, say so before comparing features. A Product will look feature-rich and rigid next to a Custom-built alternative that looks flexible and half-finished; both are effects of evolution, not product flaws, and a feature-by-feature table that ignores this is a category error.

## Output template

One block per component:

```
Technology: {name}

Evolution stage: {Genesis | Custom built | Product (+rental) | Commodity (+utility)}
Rationale: {one line of observable evidence — reference-customer count, integration time, roadmap/breaking-change log, pricing model}
Placement questions checked: {question} = {answer}; {question} = {answer}
Way of working: {Agile/experimental | Lean/pattern-led | Playbook/vendor-roadmap | Utility purchase}
Confidence: {high | medium | estimate — vendor self-positioning only}
```

Mandatory fields: stage, rationale, way of working. A stage without a rationale is decorative; a rationale that cites no observable is an opinion. When components are compared, every named component must carry its own block.

## Worked example

Illustrative comparison for a team choosing how to deliver internal document search. Four components, one stage each.

| Component | Stage | Rationale (observable) | Way of working |
|---|---|---|---|
| Object storage (S3-compatible) | Commodity (+utility) | 6+ interchangeable suppliers, published per-GB list pricing, migration measured in hours | Utility purchase; no custom integration |
| PostgreSQL with a vector extension | Product (+rental) | 3 managed offerings, documented upgrade path, public breaking-change log, ~2-week integration | Playbook adoption on the vendor roadmap |
| Retrieval evaluation harness for the corpus | Custom built | 4 comparable published implementations, all bespoke; ~4 months of tuning per environment; no shared package | Lean, borrow the closest published pattern |
| Agent that negotiates access rights across 12 legacy systems | Genesis | 0 published reference architectures; the 2 known deployments are internal experiments | Agile, time-boxed; expect to rebuild |

Reading: the 4 components span the whole axis, so one delivery method cannot serve them. The Genesis component carries the schedule risk and should be time-boxed to 6–8 weeks with an explicit kill criterion; the Commodity component should be bought and forgotten, not wrapped in an abstraction layer. The Custom-built harness is the one most often mis-tagged — a vendor selling a "product" that needs 16 weeks of per-environment tuning is selling a Custom-built component, and budgeting it as a Product understates the cost by roughly 10× in engineer-weeks (2 weeks planned against ~20 actual).

## Verification

- [ ] Every named component carries exactly one stage (or an explicit transitional label with both rationales).
- [ ] Each rationale cites something countable or checkable — reference counts, integration time, a published log, a pricing model — not marketing language.
- [ ] At least two placement questions were answered and agree with the stage; disagreement was resolved or the confidence lowered.
- [ ] Placements resting only on vendor self-positioning are marked as estimates.
- [ ] The way of working stated for each component matches what the surrounding recommendation actually proposes; any mismatch is named.
- [ ] Comparisons that cross stages say so before comparing features.

## Pair with adjacent skills

- `wardley-map-drafting` — places every component of a value chain against the user need; this skill scores one component, that one gives the context and the dependencies.
- `score-technology-readiness` — TRL is empirical readiness from deployment evidence; the evolution stage is strategic method-fit. Both belong on a technology profile and they can disagree.
- `apply-hype-cycle` — the arc of expectation through time, against this skill's snapshot of present position.
- `jtbd-framing` — when a comparison spans stages, the job statement keeps it anchored in customer demand rather than feature counts.
- `five-forces-analysis` — commodity stages usually mean supplier power has collapsed; the structural read explains why.

## Anti-patterns

- Do **not** emit a stage without a rationale; the placement is only as good as the observable behind it.
- Do **not** accept a vendor's "product" claim when integration is multi-month and tuning is per-customer — that is Custom built regardless of the marketing.
- Do **not** use Genesis as a hedge. Most components labelled Genesis actually have two or more comparable implementations and are Custom built.
- Do **not** state a stage and then recommend a way of working from a different stage; exposing that mismatch is the point of the tagging.
- Do **not** compare across stages feature-by-feature without naming the gap first.
- Do **not** assume a component evolves backwards; if the evidence says it did, the earlier placement was wrong.

## Reference

- S. Wardley, "Finding a Path," chapter 2 of *Wardley Maps: Topographical Intelligence in Business*, Medium, 2016 — the source of the evolution axis and its four stage names, and of the author's own characteristics table, which this skill does not reproduce. Published by the author under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). https://medium.com/wardleymaps/finding-a-path-cdb1249078c0
- S. Wardley, "On being lost," *Wardley Maps* chapter 1, August 2016 — the map's anchor, position and movement, and the licence statement the series is published under. https://medium.com/wardleymaps/on-being-lost-2ef5f05eb1ec
- Placement questions and the stage-to-method mapping, written for this repository: [references/placement-signals.md](references/placement-signals.md).
