---
name: morphological-analysis
description: "Maps the solution space of a design, architecture, or business-model problem with General Morphological Analysis (Zwicky box, 1969; Ritchey's Cross-Consistency Assessment) — parameters × discrete values, every cross-parameter value pair judged consistent or excluded for a stated reason, then the count and shortlist of internally consistent configurations. Use when many interacting choices must be explored without missing viable combinations — \"map all viable configurations\", \"Zwicky box / morphological analysis\", \"how many internally consistent combinations exist?\", \"prune the impossible combos\". Not for consequences of one decision (`futures-wheel`) or 2×2 futures (`scenario-planning`)."
license: MIT
metadata:
  category: decision-strategy
  method: General Morphological Analysis (GMA) with Cross-Consistency Assessment (CCA)
  origin: Fritz Zwicky, Caltech, 1940s (book 1969); computer-aided GMA and CCA — Tom Ritchey, Swedish Defence Research Agency / Swedish Morphological Society, 1995–2006
  version: "2.0.0"
---
# General Morphological Analysis (Zwicky box + CCA)

General Morphological Analysis (GMA) is Fritz Zwicky's method (Caltech, 1940s; *Discovery, Invention, Research through the Morphological Approach*, 1969) for structuring a multi-dimensional, non-quantifiable problem: name its parameters, list each one's discrete values, and treat every combination of one value per parameter as a candidate configuration. Tom Ritchey's computer-aided form (Swedish Defence Research Agency, 1995–2006) adds **Cross-Consistency Assessment (CCA)**: every value pair is judged for mutual consistency and only the survivors form the solution space. It prevents anchoring on the few familiar combinations while viable ones go unexamined.

## When to invoke

Invoke when:

- A product architecture, business model or policy option has 4–8 interacting choices and *all* viable combinations matter — "map the solution space", "explore all viable architectures", "Zwicky box", "morphological analysis".
- The question is *how many* internally consistent configurations exist and which contain a required feature ("must sell grid flexibility").

Do NOT invoke when:

- The change is fixed and the question is its downstream effects — `futures-wheel`.
- Two critical uncertainties are to be narrated into four futures — `scenario-planning`; GMA is for more than two dimensions where consistency is the issue.
- Trends influence each other directionally — `cross-impact-analysis`; CCA judges compatibility, never causation.
- The problem cannot yet be stated as parameters — `decompose-research-question` first.
- A shortlist already exists and needs scoring or testing — `decision-matrix-mcda`, then `cheapest-experiment`.

## Procedure — the Zwicky/Ritchey cycle

### 1 — Define the problem and its parameters

State the problem in one sentence. Choose 4–8 parameters (dimensions) — the independent questions any solution must answer ("what stores energy?", "who owns the hardware?"). Parameters must be MECE: no parameter is a value of another, and one value per parameter fully specifies a configuration. Beyond eight the field becomes unwieldy.

### 2 — List the values of each parameter

Give each parameter 2–6 discrete, named values (Ritchey: "conditions"). Discretise continuous quantities into bands (5 kWh / 15 kWh); include "none" when it is a real option. Values within a parameter are mutually exclusive by construction — that is what makes the field a box, not a checklist.

### 3 — Build the box and size the raw space

Set the parameters as columns with their values beneath — the morphological field, or Zwicky box. The raw count is the product of the value counts, N = n₁ × n₂ × … × nₖ (`morph.py box`): five parameters with 3–4 values give 432 configurations; 6–10 parameters give 50,000–5,000,000 (Ritchey 2006).

### 4 — Cross-Consistency Assessment

Compare every value with every value of every other parameter, pair by pair, asking only "can these two coexist?" — no direction, no causality. Record each pair as **consistent**, or excluded as a **logical** contradiction (the concepts cannot both hold), an **empirical** implausibility (very unlikely on evidence) or a **normative** exclusion (ruled out by policy, law or values — Ritchey: use sparingly, label clearly), each with a one-line reason. Pairs grow only quadratically (115 against 432 configurations below), which is why the field is reducible; `morph.py cca` lists what is still un-assessed.

### 5 — Derive the solution space

Configurations containing no excluded pair are the internally consistent solution space. Count them and the reduction with `morph.py space`; Ritchey reports typical fields shrinking by 90–99 %. A tiny reduction means a permissive CCA; a total one means a wrong exclusion or an over-constrained problem — revisit step 4.

### 6 — Select drivers and label configurations

Fix one or more values as **drivers** — a required feature or a scenario condition — and list the consistent configurations containing them (`morph.py solutions --must`). Name each interesting configuration and note what would have to be true for it to work.

### 7 — Report

Fill the output template: problem, box, raw versus consistent counts, exclusion register, drivers, named shortlist. The exclusions *are* the analysis; the counts merely follow, so show the reasons.

## Output template

```
## Morphological analysis — {problem}

**Box ({k} parameters):**
| {P1} ({n1}) | {P2} ({n2}) | … |
|---|---|---|
| {value} | {value} | … |

**Space:** raw {N} = {n1 × n2 × …}; exclusions {x} ({logical}/{empirical}/{normative}); consistent {M} ({reduction} % removed) — `morph.py space`
**Exclusion register:** X1 {Param:Value × Param:Value} — {type} — {reason} · X2 …
**Drivers:** {Param:Value, …} → {m} consistent configurations
**Shortlist:** 1. {Name} — {values} — works if {condition}; rests on {assumption} …
**Open pairs:** {none — CCA complete | list} · **Load-bearing exclusion:** {the one whose reversal changes the shortlist most}
```

Every field is mandatory — without the exclusion register the count has no argument.

## Worked example

Problem: *which architectures for a residential home-energy product are internally consistent, and which can sell grid flexibility?* Five parameters — Storage (3 values), Control (4), Revenue (3), Ownership (3), Pricing (4) — and nine reasoned exclusions (`examples/home-energy.json`). `python3 scripts/morph.py --demo` prints (header lines omitted):

```
Parameters: Storage(3) × Control(4) × Revenue(3) × Ownership(3) × Pricing(4)
Raw configurations: 3 × 4 × 3 × 3 × 4 = 432
Exclusions: 9 value pairs (logical 5, empirical 3, normative 1) in 5 of 10 parameter-pair blocks (115 value pairs to assess in total)
Consistent configurations: 172 of 432 (260 removed = 60.2 % reduction)

Consistent configurations containing Revenue:Grid flexibility (VPP): 54 of 172 consistent (raw 432)
#  Storage                Control              Revenue                 Ownership       Pricing
1  Small battery (5 kWh)  Rule-based schedule  Grid flexibility (VPP)  Customer-owned  One-off purchase
2  Small battery (5 kWh)  Rule-based schedule  Grid flexibility (VPP)  Customer-owned  Monthly subscription
(showing 2 of 54; raise --limit to see more)
```

Nine judgements out of 115 removed 260 of 432 configurations. Two do most of the work: *Storage: None × Revenue: Tariff arbitrage* (logical — nothing to shift) and *Control: Manual app × Revenue: Grid flexibility (VPP)* (logical — dispatch is machine-to-machine); with the empirical exclusion of controls-only VPP they force every VPP configuration onto a battery with automated control, so 2 × 3 × 9 = 54 survive the driver. The single normative exclusion (Customer-owned × Bundled in tariff, company policy) removes 36 configurations a policy decision could restore. Shortlist: **"Buy-and-earn"** (small battery, cloud optimiser, VPP, customer-owned, revenue share — works if the aggregator contract clears the customer's payback threshold); **"Utility VPP fleet"** (large battery, local edge optimiser, VPP, utility-owned, bundled in tariff — rests on the utility carrying the asset). `morph.py cca` reports CCA COMPLETE for all 10 blocks, so the count is a finding, not an artefact of un-assessed pairs.

## Verification

Before shipping, confirm:

- [ ] Parameters are MECE — no parameter is a value of another; nothing continuous left un-banded.
- [ ] Every cross-parameter value pair assessed — `morph.py cca` exits 0 with `CCA COMPLETE`; silence is never read as consistent.
- [ ] Every exclusion has a type and a reason a colleague could dispute; normative exclusions are few and labelled.
- [ ] Raw count = product of the value counts; consistent count reconciled with `morph.py space` after every edit.
- [ ] Each shortlisted configuration appears in `morph.py solutions --must` output — it contains the drivers and violates no exclusion.

## Companion tool

`scripts/morph.py` does the arithmetic of steps 3–6 from a JSON box (`parameters`; `exclusions` with `type` and `reason`; optional `consistent` pairs and `assessed_blocks`): raw and consistent counts, deterministic solution listing with driver filters, CCA coverage. Stdlib only, offline; every command takes `--json`.

```bash
python3 scripts/morph.py box --file box.json                        # Markdown box + raw count
python3 scripts/morph.py space --file box.json [--max-enumerate N]   # counts (bounds above N)
python3 scripts/morph.py solutions --file box.json --must "Revenue:Grid flexibility (VPP)" --limit 20
python3 scripts/morph.py cca --file box.json                        # coverage; exit 1 if pairs un-assessed
python3 scripts/morph.py --demo | --selftest
```

## Pair with adjacent skills

- `scenario-planning` — Ritchey pairs an external scenario field with an internal strategy field; hand consistent configurations to the 2×2 method or vice versa.
- `futures-wheel` — map the consequences of the configuration finally chosen.
- `cross-impact-analysis` — when interactions are directional influences, not compatibilities.
- `decompose-research-question` — turns a sprawling question into step 1's parameters.
- `key-assumptions-check` — audit the premises behind the empirical and normative exclusions.
- `decision-matrix-mcda` — score the shortlisted configurations against weighted criteria.
- `cheapest-experiment` — the smallest test for each shortlisted configuration.
- Methodology counterpart: [methodologies/foresight/cross-impact-analysis.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/cross-impact-analysis.md) — the pairwise-matrix family CCA belongs to.

## Anti-patterns

- Do **not** list values as parameters ("Battery" as a column) — a parameter is a question, its values the answers.
- Do **not** leave a parameter continuous ("price") — discretise into named bands.
- Do **not** skip the CCA and present the raw product as "the options" — that is drowning, not analysis.
- Do **not** treat un-assessed pairs as consistent by default — silence is not a judgement.
- Do **not** smuggle the preferred answer in through the CCA — excluding everything but the configuration you wanted is a decision dressed as analysis.

## Reference

- F. Zwicky, *Discovery, Invention, Research through the Morphological Approach*. New York: Macmillan, 1969. https://archive.org/details/discoveryinventi0000zwic
- T. Ritchey, "Problem structuring using computer-aided morphological analysis," *Journal of the Operational Research Society* 57(7):792–801, 2006. https://doi.org/10.1057/palgrave.jors.2602177
- T. Ritchey, *Wicked Problems – Social Messes: Decision Support Modelling with Morphological Analysis*. Springer, 2011. https://doi.org/10.1007/978-3-642-19653-9
- A. Álvarez and T. Ritchey, "Applications of General Morphological Analysis: From Engineering Design to Policy Analysis," *Acta Morphologica Generalis* 4(1), 2015, ISSN 2001-2241. https://www.swemorph.com/amg/pdf/amg-4-1-2015.pdf
- R. H. Pherson and R. J. Heuer Jr., *Structured Analytic Techniques for Intelligence Analysis*, 3rd ed. CQ Press / SAGE, 2019, ch. 9, §9.8 "Morphological Analysis". ISBN 978-1-5063-6893-1.
