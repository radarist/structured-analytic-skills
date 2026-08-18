---
name: estimate-market-size
description: "Sizes a market by triangulating two independent estimates — a top-down cut from a larger market and a bottom-up build from buyer counts and revenue per buyer — and reports the TAM/SAM/SOM layer, a range, and whether the two estimates agree within an order of magnitude. Use when asked \"how big is the X market?\", \"what's the TAM for this?\", \"is that multi-billion market number real?\" or \"size the opportunity before the board sees it\". Not for recomputing one published figure's internal arithmetic (use `quantitative-sanity-check`) and not for industry attractiveness (use `five-forces-analysis`)."
license: MIT
metadata:
  category: technology-assessment
  method: TAM/SAM/SOM triangulation (top-down × bottom-up Fermi estimation)
  origin: Fermi estimation tradition; TAM/SAM/SOM layering standardised in venture practice — Blank & Dorf, 2012; Aulet, 2013
  version: "2.0.0"
---
# Estimate Market Size

Fermi estimation applied to markets. A single market-size figure is unfalsifiable — analyst houses publish several-fold different numbers for the same words — so this method builds **two independent estimates from different directions** and treats their agreement as the test. The top-down estimate cuts a known larger market by successive share ratios; the bottom-up estimate multiplies a buyer count by adoption and revenue per buyer. Agreement within an order of magnitude supports the size; a gap wider than 3× rejects the claim, and the disagreement is itself the finding because it localises the wrong input. The TAM / SAM / SOM layering comes from venture practice — Blank and Dorf (2012), Aulet (2013) — where a factor of ten between TAM and SOM is normal, which is why an unlabelled "$50B market" means nothing.

## When to invoke

Invoke when:

- Asked "how big is the X market?" or "what is the TAM for X?".
- A document asserts a market size or "$X by {year}" forecast that a decision rests on, or two published figures for the same market disagree and the spread must be explained, not averaged.

Do NOT invoke when:

- The task is recomputing one published figure's own arithmetic — CAGR, unit economics, percent vs percentage point — use `quantitative-sanity-check`.

- How attractive the industry is — use `five-forces-analysis`; where competitors sit inside it — `position-competitor`.
- The estimate to check is a plan, budget or schedule rather than a market — use `reference-class-forecasting`.
- The market is pre-revenue: sizing what does not yet exist is forecasting — route to `scenario-planning`.
- One named source's number is wanted — quote it with its definition, no triangulation.

## The three layers

- **TAM** (total addressable) — everyone who could buy, ignoring reach constraints; 100%.
- **SAM** (serviceable addressable) — the part reachable given geography, regulation and channel; typically 10–30% of TAM.
- **SOM** (serviceable obtainable) — realistic near-term capture; typically 1–10% of SAM.

Every figure must carry its layer and market definition or it cannot be compared with anything.

## Procedure

### 1 — Fix the market definition

Write it as **product category × buyer segment × geography × time frame** — "LLM API services for enterprise developers in North America and the EU, 2026". Vague definitions ("the AI market") cannot be sized — no two estimates would cover the same thing; both estimates below must use this identical definition.

### 2 — Pick the layer

State whether the figure is TAM, SAM or SOM. If a source does not say, default to TAM and record the ambiguity — a TAM quoted as obtainable revenue is the commonest market-size error.

### 3 — Build the top-down estimate

Start from a larger market whose total is independently published, then apply successive share ratios: containing market × category share × geography share × segment share. Cite every ratio and name any uncited one as the weakest link.

### 4 — Build the bottom-up estimate

Start from unit economics: potential buyers × adoption rate × annual revenue per buyer, summed over segments differing materially in size or price. Cite each buyer count and revenue figure.

### 5 — Triangulate and rule

Compute top-down ÷ bottom-up. Between 0.33 and 3 the size is **supported** — geometric mean as midpoint, the two estimates as the range. Outside it the claim is **rejected**: report both figures, the ratio, and the input most likely to explain the gap (usually a mismatched definition, adoption rate or revenue per buyer).

### 6 — Report range, sensitivity and what to verify first

Never report a point estimate. Give the range, the midpoint, the input whose error moves the answer most, and the citation to check first. When sizing for one vendor, cascade the TAM to SAM and SOM with stated reach and capture percentages.

## Output template

```
## Market size estimate — {market definition}

**Definition:** {product category} × {buyer segment} × {geography} × {time frame} · **Layer:** {TAM | SAM | SOM}

**Top-down:** {containing market} {$} ({source}) × {category share} % ({source}) × {geography/segment share} % ({source}) = **{$top-down}**
**Bottom-up:** {buyers} ({source}) × {adoption} % ({source}) × {ARPU} ({source}) = **{$bottom-up}**

**Triangulation:** ratio {x.xx} · log10 gap {x.xx} · verdict {SUPPORTED | REJECTED} (supported when 0.33 ≤ ratio ≤ 3)
**Estimate:** {$low}–{$high}, midpoint {$mid} (geometric mean)
**Cascade (vendor-specific):** SAM {$} = {reach %} of TAM · SOM {$} = {capture %} of SAM · implied buyers {n}
**Most sensitive input:** {input whose error moves the answer most} · **Verify first:** {citation that would change the verdict}
```

Mandatory fields: definition, layer, both estimates with sources, ratio and verdict, range with midpoint, most sensitive input. A single-direction estimate is not an output of this method.

## Worked example

Market: LLM API services for enterprise developers in North America and the EU, 2026. Illustrative inputs; arithmetic reproduced with `scripts/market.py`.

Top-down, from a global LLM API services TAM to the serviceable geography and segment, then to one vendor's obtainable share:

```
$ python3 scripts/market.py topdown --tam 120e9 --sam-pct 48 --som-pct 5 --arpu 1.8e6
  TAM: $120.00B  implied customers: 66,667
  SAM: $57.60B  (= $120.00B x 48%)  implied customers: 32,000
  SOM: $2.88B  (= $57.60B x 5%)  implied customers: 1,600
```

The 48% cut is the assumed North America-and-EU enterprise-developer share and therefore
defines SAM. The 5% cut is the illustrative vendor capture rate and therefore defines SOM.

Bottom-up, from buyer counts and revenue per buyer across three segments:

```
$ python3 scripts/market.py bottomup --segments '[{"name":"large enterprise","customers":12000,"arpu":3000000}, ...]'
  large enterprise (>5,000 staff): 12,000 customers x $3.00M ARPU = $36.00B
  mid-market (500-5,000): 20,000 customers x $600.00K ARPU = $12.00B
  public sector: 1,500 customers x $600.00K ARPU = $900.00M
  Total: $48.90B

$ python3 scripts/market.py triangulate --topdown 57.6e9 --bottomup 48.9e9
  Ratio (top-down / bottom-up): 1.178
  Log10 gap: 0.07 orders of magnitude
  Verdict: SUPPORTED (supported when 0.33 <= ratio <= 3.00)
  Geometric-mean midpoint: $53.07B
```

Reading: the two directions land within 18% of each other, inside the 0.33–3 band, so the
North America-and-EU enterprise-developer **SAM** is supported at **$48.9B–$57.6B, midpoint
$53.1B**. At the stated 5% capture assumption, one vendor's SOM is approximately
**$2.45B–$2.88B**. The convergence is partly structural — the cascade implies 32,000 buyers
at $1.8M each, while the bottom-up estimate counts 33,500 at a blended $1.46M — so they agree
on the buyer population and differ on price. Blended revenue per buyer is therefore the most
sensitive input: a 30% error moves the SAM by about $16B, more than any other single bottom-up
input. Verify the $3.0M large-enterprise ARPU first; it carries nearly three-quarters of the
bottom-up total.

## Verification

- [ ] Both estimates cover the identical definition — same product, buyer segment, geography and time frame.
- [ ] Every ratio, buyer count and revenue figure carries a citation; uncited inputs are named as assumptions.
- [ ] The ratio was recomputed (`scripts/market.py triangulate`) and the verdict follows the 0.33 ≤ ratio ≤ 3 rule, not judgement.
- [ ] Disagreement above 3× is reported as a rejection with the likely offending input, never averaged away.
- [ ] The output is a range with a midpoint and a stated layer, and the most sensitive input is named.

## Companion tool

`scripts/market.py` (stdlib only) runs the arithmetic: the TAM→SAM→SOM cascade with implied customer counts, bottom-up unit economics for one segment or a JSON list, and the triangulation — ratio, log10 gap, verdict per the 0.33 ≤ ratio ≤ 3 rule, geometric-mean midpoint.

```bash
python3 scripts/market.py topdown --tam 120e9 --sam-pct 48 --som-pct 5 --arpu 1.8e6
python3 scripts/market.py bottomup --customers 32000 --arpu 1800000
python3 scripts/market.py bottomup --segments '[{"name":"ent","customers":100,"arpu":1000}]'
python3 scripts/market.py triangulate --topdown 57.6e9 --bottomup 48.9e9
python3 scripts/market.py --selftest      # hand-verified worked examples
```

Usable without the tool — it only removes arithmetic slips and makes the verdict mechanical.

## Pair with adjacent skills

- `quantitative-sanity-check` — recomputes a published sizing's own arithmetic; this skill builds an independent estimate instead.
- `reference-class-forecasting` — for a plan or budget, the outside view of a reference class replaces triangulation.
- `five-forces-analysis` — a large market is not an attractive one; the structural read says whether it is capturable.
- `position-competitor` — maps who is already inside the market just sized.
- `triangulate-sources` — every ratio and buyer count should rest on two independent sources.


## Anti-patterns

- Do **not** take a single source at face value; the spread between houses is the information.
- Do **not** mix a top-down figure for one definition with a bottom-up figure for another — same product, buyers, geography and period, or the comparison is void.
- Do **not** hide disagreement: a ratio above 3 is the report, not a problem to smooth.
- Do **not** report a point estimate or quote a figure without its layer.
- Do **not** fold growth into the current size; "reaching $X by {year}" needs today's size and the growth assumption separately.

## Reference

- S. Blank and B. Dorf, *The Startup Owner's Manual*. Pescadero, CA: K&S Ranch, 2012. ISBN 978-0-9849993-0-9 — TAM/SAM/SOM layering in customer-development practice.
- B. Aulet, *Disciplined Entrepreneurship: 24 Steps to a Successful Startup*. Hoboken, NJ: Wiley, 2013. ISBN 978-1-118-69228-8 — step 4 (beachhead market) and step 5 (TAM), the bottom-up build used here.
- L. Weinstein and J. A. Adam, *Guesstimation: Solving the World's Problems on the Back of a Cocktail Napkin*. Princeton, NJ: Princeton University Press, 2008. ISBN 978-0-691-12949-5 — bounding an unknown by two independent routes. https://press.princeton.edu/books/paperback/9780691129495/guesstimation
- The 0.33–3× band and the geometric-mean midpoint operationalise "agree within an order of magnitude"; they are conventions of the tradition above, not a published standard.
