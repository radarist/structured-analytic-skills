---
name: position-competitor
description: "Maps three or more competitors onto a two-axis competitive landscape — axis choice tested for orthogonality, each placement justified by evidence, quadrants read, whitespace argued — and reports whether an empty region is an opportunity or simply unviable. Use when asked \"where does X sit versus Y and Z?\", \"who are the leaders in this category?\", \"build a competitive map of this space\" or \"make me a 2x2 of these vendors\". Not for industry-level structure and profitability (use `five-forces-analysis`) and not for how evolved one component is (use `evolution-stage`)."
license: MIT
metadata:
  category: technology-assessment
  method: Two-axis competitive positioning map
  origin: Michael E. Porter, Competitive Strategy (strategic-group maps), 1980
  version: "2.0.0"
---
# Position Competitor

A positioning map places rival firms or products on two axes so the *structure* of a market becomes visible — who clusters, who is isolated, which combinations nobody offers. The form descends from the strategic-group maps in Michael E. Porter's *Competitive Strategy* (1980) and is familiar from Gartner's Magic Quadrant (completeness of vision against ability to execute). Its core principle: a map is only as good as its axes, because two axes measuring the same underlying thing produce a diagonal line of dots confirming whatever the author already believed. The method therefore tests the axes for independence, demands an evidence sentence per placement, and treats empty space as a question rather than an answer — preventing the vendor-logo grid that looks analytical and asserts nothing.

## When to invoke

Invoke when:

- Asked "where does X sit versus Y?", "who leads this category?", "build a landscape map of this space" or "put these vendors on a 2x2".
- A decision between three or more suppliers needs the shape of the field rather than a feature list, or a claim that some region is unserved needs testing before it becomes strategy.

Do NOT invoke when:

- The question is industry-level structure and profitability — supplier power, entry barriers, substitutes — use `five-forces-analysis`.
- The question is how evolved a single component is and what method fits it — use `evolution-stage`.
- The question is how large the market is rather than who is in it — use `estimate-market-size`.
- The comparison is really about which job customers hire the product for — use `jtbd-framing`.
- Fewer than three entities are in scope (two points make a line), or the question is factual ("does X support Y?") and a feature table answers it.
- The market is in hypergrowth and positions turn over monthly — the map is stale on arrival; prefer `analysis-of-competing-hypotheses` on the contested question.

## Procedure

### 1 — Choose and test the axis pair

Good axes are **material** (they change what a buyer does), **measurable** (scored from evidence, not impression) and **orthogonal** (they do not measure the same thing twice). Candidate pairs and the evidence that scores each are catalogued in `references/axis-pairs.md`. Score every entity on both axes, then test independence with `scripts/positioning.py orthogonality`: |r| ≥ 0.7 means the pair is not independent and another axis is needed, 0.4–0.7 means documented caution, below 0.4 is acceptable. With fewer than about ten entities the coefficient rests on too few points to gate on — treat the verdict as indicative and lean on the per-axis evidence instead. Record why this pair was chosen and which alternative was rejected.

### 2 — Place each entity with an evidence sentence

Every placement carries one sentence of evidence — a benchmark result, a published integration surface, a price list, a customer count, a filing. Placement by impression is the failure this step prevents. Coordinates are directional: normalise to a common range and read the quadrant, not the decimal. Where evidence is thin, place the entity but mark it weak.

### 3 — Read the quadrants and the crowding

Name who occupies each quadrant and what they share: three entities in a quadrant is a fight, one is either a moat or a warning. Report the crowding measure — how close nearest neighbours sit — because two entities in the same square metre compete on something the axes do not capture, and that is usually the real story.

### 4 — Argue the whitespace

Find the empty regions and answer the only question that matters for each: empty because nobody has tried, or because the combination is unviable? Near-frontier quality at commodity prices is empty for a reason. Describe what a player there would have to look like and say plainly which explanation applies — whitespace reported without that judgement invites someone to walk into a wall.

### 5 — Run the stability checks

Swap one axis for another candidate: if the ordering barely changes, the axes miss the real variance and should be replaced. Then back-cast three years: if nothing moved, the axes measure something ossified, such as company size, rather than competitive dynamics. State how long the map stays valid and what it ignores.

## Output template

```
## Competitive positioning — {category}

**Axes:** {X-axis} (horizontal) × {Y-axis} (vertical) — {why they capture the variance; which alternative was rejected}
**Orthogonality:** Pearson r {value} · Spearman rho {value} · N {n} — {OK | caution | not independent}

| Entity | X {axis} | Y {axis} | Quadrant | Evidence |
|---|---|---|---|---|
| {name} | {score} | {score} | {quadrant} | {one sentence with a source} |

**Quadrants:** upper-right {who, what they share} · upper-left {who} · lower-right {who} · lower-left {who}
**Crowding:** {mean nearest-neighbour distance} · closest pair {a}–{b} at {d}
**Whitespace:** {region} — empty because {untried | unviable}; a player there would need {what}
**Stability:** axis-swap {stable | changes the story} · 3-year back-cast {who moved}
**Limitations:** {what the map ignores; how long it stays valid}
```

Mandatory fields: the axis pair with its justification, the orthogonality verdict, one evidence sentence per entity, the whitespace judgement (untried or unviable), and the limitations. Without the orthogonality check and the whitespace argument it is a logo grid.

## Worked example

Category: foundation-model API providers — the built-in synthetic landscape of eight fictional vendors, reproduced with `python3 scripts/positioning.py report --demo`. X is a platform-surface score 0–100 (integration depth), Y a benchmark composite 0–100 (frontier quality). Illustrative data.

```
$ python3 scripts/positioning.py orthogonality --demo
  Pearson r = +0.265   Spearman rho = +0.383
  Verdict: OK - |r| < 0.4: the axes move independently
  Same-axis pairs (|r| >= 0.7): integration depth (x) x size (r = +0.83)

$ python3 scripts/positioning.py map --demo        (normalised 0-10)
  Ardent  10.00 / 10.00  upper-right      Dune     9.75 / 0.70  lower-right
  Halcyon  9.50 /  9.53  upper-right      Fjord    7.25 / 4.42  lower-right
  Bramble  1.62 /  9.53  upper-left       Cobalt   4.75 / 3.95  lower-left
  Granite  2.88 /  5.81  upper-left       Ember    0.00 / 0.00  lower-left
  Crowding: mean nearest-neighbour distance 2.96; pairs closer than 1.00: Ardent-Halcyon (0.68)
  Centroid (5.72, 5.49); weighted by category spend (7.53, 6.41)

$ python3 scripts/positioning.py whitespace --demo --grid 4
  1. x [5,7.5) x y [7.5,10]  centre (6.25, 8.75)  nearest: Halcyon at 3.34
```

Reading: the axes pass the independence test at r = +0.265, and the correlation matrix catches a trap — headcount correlates with integration depth at r = +0.83, so "company size" would have been the same axis relabelled. Ardent and Halcyon sit 0.68 apart in the top-right, far below the 2.96 mean: neither axis differentiates them, so they compete on something the map does not show. The largest empty region is mid-integration, high-quality — near-frontier models sold as a composable component — and that is unviable rather than untried, because near-frontier training costs near-frontier money. The weighted centroid sits up and right of the plain centroid: spend concentrates on the integrated leaders.

## Verification

- [ ] Three or more entities are mapped, and the axis pair is named with the alternative rejected.
- [ ] The orthogonality check was run (`scripts/positioning.py orthogonality`) and |r| < 0.7; a 0.4–0.7 result carries a documented justification.
- [ ] Every placement has one evidence sentence with a source; impression-based placements are marked weak.
- [ ] Any other numeric column correlating above 0.7 with an axis was checked, so the axes are not one variable relabelled.
- [ ] The whitespace judgement says explicitly whether the region is untried or unviable.
- [ ] Axis-swap and three-year back-cast checks were run; the map states what it ignores and how long it holds.

## Companion tool

`scripts/positioning.py` (stdlib only) runs the step 1–3 arithmetic on a CSV/JSON of `name, x, y` rows (raw axis scores; optional `weight`, `evidence`, extra numeric columns). `orthogonality` — Pearson r, Spearman ρ; verdict |r| ≥ 0.7 not independent (exit 1), 0.4–0.7 caution, < 0.4 OK; correlation matrix and least-correlated pair over extra columns (suggestion, not decision). `map` — min–max 0–10 placements, quadrants, ASCII scatter, crowding index, centroid. `whitespace` — `--grid 4` empty cells ranked by distance from the nearest competitor, plus the empty-is-not-opportunity caveat. `report` — everything, in output-shape order. `--json`, `--demo`, `--selftest`.

```
$ python3 scripts/positioning.py map --demo
    ^ Y: frontier quality (high)
 10 |   B      :        HA|
    |          :          |
    |          :          |
    |          :          |
    |      G   :          |
  5 |..........+..........|
    |          C    F     |
    |          :          |
    |          :          |
    |          :         D|
  0 |E         :          |
    +---------------------+
     0         5        10
    X: integration depth (high) ->
```

The skill is fully usable without the tool — it only makes the correlation, normalisation and distance arithmetic auditable; placements still need evidence.

## Pair with adjacent skills

- `five-forces-analysis` — the map shows who competes; the five forces say whether anyone in it can make money.
- `evolution-stage` — entities at different evolution stages are not comparable feature-for-feature; tag them before placing them.
- `estimate-market-size` — sizes the market the map partitions; a crowded quadrant in a small market is worse news than the map alone shows.
- `jtbd-framing` — anchors axis choice in what customers hire the product to do, the test of whether an axis is material.
- `grounded-answer` — every placement's evidence sentence should survive verification before the map ships.

## Anti-patterns

- Do **not** place entities by impression; every placement needs a source and unsourced ones are marked weak.
- Do **not** use correlated axes — company size against revenue is one axis drawn twice; run the orthogonality check first.
- Do **not** report whitespace without saying whether it is untried or unviable; unargued whitespace is a trap.
- Do **not** map fewer than three entities, or present coordinates as if the scores were measurements.
- Do **not** publish a map of a hypergrowth market without stating it goes stale within months.
- Do **not** treat quadrant labels as verdicts; "leaders" is a position on two chosen axes, not a judgement of the business.

## Reference

- M. E. Porter, *Competitive Strategy: Techniques for Analyzing Industries and Competitors*. New York: Free Press, 1980. ISBN 978-0-02-925360-1 — ch. 7, strategic groups and strategic-group maps, the ancestor of the two-axis landscape.
- W. C. Kim and R. Mauborgne, *Blue Ocean Strategy*. Boston, MA: Harvard Business School Press, 2005. ISBN 978-1-59139-619-2 — the strategy canvas and the discipline of arguing uncontested space rather than assuming it.
- Gartner, "Magic Quadrant research methodology" — the two-axis form of completeness of vision against ability to execute, with Leaders, Challengers, Visionaries and Niche Players. https://www.gartner.com/en/research/methodologies/magic-quadrants-research
- Correlations used by the companion tool: K. Pearson, *Proceedings of the Royal Society of London*, vol. 58, pp. 240–242, 1895; C. Spearman, "The proof and measurement of association between two things," *American Journal of Psychology*, vol. 15, no. 1, pp. 72–101, 1904.
- The numeric cut-offs (|r| ≥ 0.7 not independent, 0.4–0.7 caution) operationalise Porter's qualitative rule in `scripts/positioning.py`.
