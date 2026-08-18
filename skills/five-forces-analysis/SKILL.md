---
name: five-forces-analysis
description: "Assesses the structural profitability of an industry with Porter's Five Forces — entry threat, supplier power, buyer power, substitutes and rivalry — rating each on evidence, naming the one or two forces that actually control profits, and reporting how they are trending. Use when the question is whether a market is worth entering or staying in — \"how attractive is this industry?\", \"Porter five forces for this market\", \"what are the barriers to entry here?\", \"why are margins in this sector so thin?\". Not for placing one firm against its rivals (use `position-competitor`) or for sizing demand (use `estimate-market-size`)."
license: MIT
metadata:
  category: decision-strategy
  method: Five Forces (industry structure analysis)
  origin: Michael E. Porter, 1979 (Harvard Business Review); revised 2008
  version: "2.0.0"
---
# Five Forces Analysis

Five Forces explains why some industries sustain high returns and others compete their profits away. Michael Porter introduced it in "How Competitive Forces Shape Strategy" (*Harvard Business Review*, 1979) and extended it in 2008: the collective strength of five forces — threat of new entrants, supplier power, buyer power, substitutes and rivalry — determines an industry's profit potential, and **the strongest force or forces determine profitability**, though "the most salient force is not always obvious". It prevents mistaking visible attributes for structure — reading fast growth, hot technology or a famous incumbent as attractiveness while profits leak to a concentrated supplier or an improving substitute.

## When to invoke

Invoke when:

- An entry, exit or sustained-investment decision turns on whether an industry can support profits — "how attractive is this market?", "what are the barriers to entry?".
- Margins in a sector are unexplained and the question is structural, not operational.
- A strategy claims an industry is attractive because it is growing; structure must be checked before that ships.

Do NOT invoke when:

- The question is where one firm stands against named rivals — use `position-competitor`; for the customer's job behind the purchase, `jtbd-framing`.
- Demand size is the question — use `estimate-market-size`; a technology's maturity — `evolution-stage` or `apply-hype-cycle`.
- The industry is in hypergrowth or mid-restructuring so today's structure will not hold — branch it with `scenario-planning`.
- The internal value chain and build-buy boundary are the question — use `wardley-map-drafting`.

## Procedure — Porter's steps in industry analysis

### 1 — Define the relevant industry

Fix both dimensions Porter names — **product or service scope** and **geographic scope** — plus the time frame. "AI" is not an industry; "LLM inference APIs sold to regulated enterprises in the EU, 2027" is. Too broad obscures differences in buyers, suppliers and barriers; too narrow overlooks linkages. Porter's test: products sharing the same buyers, suppliers and entry barriers are one industry; where structure differs markedly, they are separate.

### 2 — Identify the participants

Name the buyers, suppliers, competitors, substitutes and potential entrants, segmented into groups where their economics differ. A force cannot be rated against an unnamed party: "suppliers" is not an answer, "three accelerator vendors, one holding most volume" is.

### 3 — Rate each force on at least three evidenced indicators

Assess each force's underlying drivers and rate Low / Medium / High, citing evidence per indicator — checklists in [references/force-indicators.md](references/force-indicators.md). Rate the *threat* of entry rather than observed entry, keep buyer leverage separate from price sensitivity, and confine substitutes to products performing the same function by different means. Fewer than three indicators is overfit; no evidence line is a vibe.

### 4 — Determine the structure and test for consistency

State why profitability is what it is, name the **controlling force or forces**, and test against reality: is it consistent with actual long-run profitability, and are the more profitable players better positioned against the five forces? Usually one or two forces govern. Growth rate, technology, government and complements act *through* the forces, never as a sixth force.

### 5 — Analyse recent and likely future changes

Structure is not static. Per force, say which drivers are moving and in which direction over a stated horizon, distinguishing structural change from cyclical or transient swings. Name the force most likely to reshape the industry and the observable evidence that would confirm it.

### 6 — Report the implications

Close on which aspects of structure the company could influence — positioning where the forces are weakest, exploiting change before rivals, or reshaping structure in its favour. Declaring an industry "attractive" or "unattractive" and stopping is one of the pitfalls Porter names.

## Output template

```
## Five Forces — {industry}

**Industry scope:** {product/service scope} × {geographic scope} × {time frame}
**Participants:** buyers {…} · suppliers {…} · competitors {…} · substitutes {…} · potential entrants {…}

| Force | Rating | Key evidenced indicators (≥3) | Direction over {horizon} |
|---|---|---|---|
| Threat of new entrants | {Low/Med/High} | {indicator — evidence}; … | {rising/stable/falling} |
| Supplier power / Buyer power / Substitutes / Rivalry | … | … | … |

**Controlling force(s):** {force(s)} — {why these govern profitability here}
**Structural verdict:** {why profitability is what it is}
**Consistency test:** {consistent with observed long-run profitability? are the more profitable players better positioned?}
**Structural change to watch:** {force} — {driver, direction, and the evidence that would confirm it}
**Strategic implications:** {position where forces are weakest / exploit the change / reshape the structure}
**Confidence:** {0.0–1.0} — {what the weakest evidence is}
```

Mandatory: the scope line, a rating with three or more evidenced indicators per force, the named controlling force, the consistency test and the direction of change. A rating with no evidence line must not ship.

## Worked example

Illustrative case (all figures invented): should Northwind Systems, a mid-size European software vendor, enter **frontier-model inference APIs sold to regulated enterprises in the EU, assessed for 2027**? Participants: buyers — about 400 regulated enterprises, the largest 30 taking ~60 % of spend; suppliers — accelerator vendors (one holding most volume), three hyperscale operators, ~5,000 people worldwide with frontier-training experience; competitors — four frontier labs and two EU sovereign entrants; substitutes — self-hosted open-weight models; potential entrants — hyperscalers' in-house teams.

| Force | Rating | Key evidenced indicators | Direction to 2029 |
|---|---|---|---|
| Threat of new entrants | Low | Frontier training run ~$180 M; talent pool ~5,000; accelerator allocation held by 3 operators | Rising slightly as rental capacity broadens |
| Supplier power | High | One vendor holds ~80 % of accelerator volume; 3-year power contracts; no substitute at parity | Falling if second-source silicon ships |
| Buyer power | Medium | Top 30 buyers = 60 % of spend; multi-homing across 2–3 APIs; migration cost ~6 weeks and falling | Rising |
| Threat of substitutes | Medium | Open-weight models within ~8 % of frontier quality on the two main tasks at ~30 % of cost | Rising |
| Rivalry | High | Six comparable players; price per million tokens fell ~90 % in 24 months; capability leads matched within ~4 months | Stable-high |

**Controlling forces:** supplier power and rivalry. High entry barriers would normally support profits, but value is captured upstream — the accelerator supplier takes the margin while rivals compete the rest away on price.
**Structural verdict:** unattractive at the frontier tier for a new entrant; profit accrues to the compute supplier, not the model layer.
**Consistency test:** consistent with observed results — the profitable players are the accelerator vendor and the hyperscale operators, and the model providers with the best economics are those with their own silicon or captive distribution.
**Structural change to watch:** substitutes — if open-weight quality closes to within 3 %, buyer power and substitution compound; the confirming evidence is regulated buyers moving production workloads self-hosted.
**Strategic implications:** the defensible position is the compliance-and-integration layer above the model, where switching costs exist and the supplier bottleneck does not bite.
**Confidence:** 0.6 — the substitute-quality gap is the weakest evidence and moves fastest.

## Verification

Before the assessment ships:

- [ ] The scope line names product scope, geographic scope and time frame; the same scope is used in every force.
- [ ] Every force has at least three indicators, each with an evidence line — recount and reject any rating carried by one indicator.
- [ ] Entry is rated as a *threat* (barriers plus expected retaliation), not as observed entry counts.
- [ ] Substitutes perform the same function by different means — cross-check that no direct rival is listed as one.
- [ ] The controlling force is named and the verdict follows from the ratings — if the verdict would stand whatever the ratings were, the analysis is theatre.
- [ ] The consistency test is answered: the verdict agrees with observed long-run profitability, or the gap is explained.
- [ ] Growth rate, technology, government and complements appear as factors acting through the forces, never as a sixth force.

## Pair with adjacent skills

- `position-competitor` — firm-level placement inside the industry characterised here.
- `estimate-market-size` — sizes the demand whose structure is assessed here.
- `scenario-planning` — branches the forces forward when structure is too unsettled for one snapshot.
- `jtbd-framing` — sharpens the substitute analysis by naming the job the buyer hires for.
- `premortem-analysis` — stress-tests the "enter this industry" recommendation that follows.
- `wardley-map-drafting` — maps the internal value chain and where the forces bite.

## Anti-patterns

- Do **not** define the industry too broadly or too narrowly — the commonest source of a wrong answer.
- Do **not** make lists instead of analysis: indicators with no rating or mechanism are inventory.
- Do **not** pay equal attention to all five forces; name the one or two that control profitability.
- Do **not** confuse effect with cause — price sensitivity is an effect of buyer economics, not a substitute for analysing them.
- Do **not** use a static snapshot, or mistake cyclical swings for structural change.
- Do **not** stop at "attractive / unattractive" — the framework guides strategic choices.
- Do **not** confuse substitutes with rivals: a competitor makes the same thing, a substitute meets the need another way.

## Reference

- M. E. Porter, "How Competitive Forces Shape Strategy," *Harvard Business Review*, vol. 57, no. 2, pp. 137–145, Mar.–Apr. 1979. https://hbr.org/1979/03/how-competitive-forces-shape-strategy
- M. E. Porter, "The Five Competitive Forces That Shape Strategy," *Harvard Business Review*, vol. 86, no. 1, pp. 78–93, Jan. 2008 — the revised statement, with the entry-barrier sources, the typical steps in industry analysis and the common pitfalls used above.
- M. E. Porter, *Competitive Strategy: Techniques for Analyzing Industries and Competitors*. New York: Free Press, 1980 — the book-length treatment.
