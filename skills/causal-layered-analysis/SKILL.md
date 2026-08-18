---
name: causal-layered-analysis
description: "Deconstructs an issue through the four levels of Causal Layered Analysis — litany, systemic causes, worldview/discourse, myth/metaphor (Inayatullah, Futures, 1998) — then reconstructs a vertically coherent alternative future, producing a four-layer table, deconstruction notes and a reframed narrative. Use when framing itself is the obstacle: \"why does this problem never get solved?\", \"reframe the debate on {issue}\", \"run a CLA on {issue}\", \"the scenarios all look like more of the same\". Not for verifying a factual claim (use `grounded-fact-check`) or for numeric estimates (use `estimate-market-size`)."
license: MIT
metadata:
  category: foresight
  method: Causal Layered Analysis (CLA)
  origin: Sohail Inayatullah, 1998 (Futures 30(8); CLA Reader, 2004)
  version: "2.0.0"
---
# Causal Layered Analysis (CLA)

Causal Layered Analysis, set out by Sohail Inayatullah in *Futures* in 1998, treats a problem as constituted at four levels: the **litany** (headlines, stock phrases, iconic statistics), the **systemic causes** (structures, incentives, institutions producing them), the **worldview or discourse** (the paradigm that makes those structures seem sensible), and the **myth or metaphor** (the deep story carrying the issue emotionally). Its principle is that solutions pitched at one level are absorbed by the levels beneath: a litany-level fix survives only if system, worldview and myth change too. So the method descends the layers, then rebuilds upward — a different metaphor, the worldview coherent with it, the systems that worldview would design, and the litany those systems would generate. It prevents the characteristic failure of futures and policy work: analysis that stays inside the framing which created the problem, so the outputs are more of the same.

## When to invoke

Invoke when:

- A problem persists through decades of policy effort and the framing looks like part of it: "why does this never get solved?", "our fixes never stick".
- The ask is to reframe: "reframe the debate on {issue}", "what story is being told about {issue}?", "go deeper than the headlines", "run a CLA on {issue}".
- Scenario or vision work keeps producing trend extrapolations, or stakeholders citing the same facts define the problem differently and talk past each other.

Do NOT invoke when:

- Verifying whether a specific claim is true — use `grounded-fact-check`; CLA operates on framing, not facts.
- The output needed is numeric — use `estimate-market-size` or `bayesian-update`.
- The problem is technical and well framed — the layered overhead buys nothing; use `cheapest-experiment`.
- Concrete alternative futures are needed rather than a reframing — use `scenario-planning`, then run CLA inside each scenario.
- The answer is needed within the hour; CLA is deliberately slow and unsettling.

## Procedure

Steps 2–5 descend the four levels; steps 6–8 deconstruct and rebuild. The descent makes the reconstruction possible: a new myth chosen without seeing the old one usually restates it.

### 1 — State the issue as it is conventionally framed

Write the issue in its current public framing — the way a headline or press release would put it. This wording is the object of analysis and the benchmark the reframe is measured against. Output: issue statement.

### 2 — Map the litany (level 1)

Harvest how the issue is actually talked about: headline claims, stock phrases, iconic statistics, official framings, and who repeats them. Include at least three different media or political positions, each with a source, so the litany is the public discourse rather than one outlet's version. Output: litany inventory.

### 3 — Map the systemic causes (level 2)

Identify the structures producing that litany: incentives, institutions, funding flows, technologies, demographics, legal regimes. Ask how the system *reproduces* the problem — whose budget, business model or career depends on it persisting — since that is what absorbs litany-level fixes. Output: systemic-cause map.

### 4 — Map competing worldviews (level 3)

Name the paradigm that makes the present system look sensible, and at least one genuinely different paradigm that defines the problem differently. Write each authentically, not as parody: what the problem is in this frame, what solutions become thinkable, what becomes unthinkable, what counts as evidence. Output: worldview statements.

### 5 — Map myths and metaphors (level 4)

Surface the deep stories carrying the issue: "the war on X", "the flood", "the machine that must be fed". Rule: every entry must be alive in the culture — findable in real speech, media, ritual or advertising — with evidence recorded. An analyst's coinage is not a myth. Output: myth list with liveness evidence.

### 6 — Deconstruct

Ask where the conventional framing is contingent rather than natural: what it hides, whom it serves, what it makes unthinkable, whose voice is absent, how another era or country framed it. Output: deconstruction notes.

### 7 — Reconstruct upward from a different myth

Choose a different metaphor for the preferred future, derive the worldview coherent with it, then the systems that worldview would build, then the litany those systems would produce. Where the preferred future is values-laden, build two candidate reconstructions from different myths and leave the choice with the user. Output: alternative-future column.

### 8 — Check coherence and sourcing, then emit

Test vertical coherence — does each reconstructed level imply the next, or would the old myth eat the new system? Confirm metaphor liveness, and that every empirical claim at levels 1–2 has a source while levels 3–4 are marked interpretive. Output: completed CLA table and reframe narrative.

## Output template

```
## Causal Layered Analysis — {issue}

Issue as conventionally framed: {the litany-level statement}

| Level | Current issue | Alternative future |
|---|---|---|
| 1. Litany | {headlines, stock phrases, iconic statistics} | {headlines the new system would generate} |
| 2. Systemic causes | {incentives, institutions, technologies producing it} | {redesigned systems and policies} |
| 3. Worldview | {dominant paradigm + 1-2 competitors} | {worldview chosen for the new future} |
| 4. Myth / metaphor | {deep stories carrying it now} | {new metaphor, alive in the culture} |

Deconstruction notes: {what the framing hides / whom it serves / what it makes unthinkable}
Reframe: {one paragraph, from new myth up to new litany}
Coherence check: {does each level imply the next? weakest link: …}
Sourcing: level 1-2 claims sourced {list}; metaphor liveness evidence {list}; levels 3-4 marked interpretive
```

Mandatory fields: all four levels in both columns, deconstruction notes, the coherence check with its weakest link, and the sourcing line.

## Worked example

Issue as conventionally framed: "Rising obesity is a public-health crisis caused by poor lifestyle choices." Illustrative; the level 1–2 claims below need sourcing before external use.

| Level | Current issue | Alternative future |
|---|---|---|
| 1. Litany | "1 in 3 adults is obese"; "obesity costs billions a year"; stock phrases "eat less, move more", "personal responsibility", "the obesity epidemic" | "City redesigns its food environment"; "diet-related admissions fall 12 % in 5 years"; stock phrases "the food environment", "healthy by default" |
| 2. Systemic causes | Calorie-dense food cheapest per 1,000 kcal; subsidies skewed to sugar and corn; marketing budgets far exceeding public-health spend; car-dependent design; healthcare paid to treat, not prevent | Subsidies shifted to produce; zoning for walkable mixed use; restrictions on marketing to under-16s; school and hospital procurement standards; prevention reimbursed |
| 3. Worldview | Consumer choice: health is individual market behaviour, the rational eater sovereign, evidence means trials of individual interventions. Competing paradigm: ecological public health — health is a property of environments and populations | Ecological worldview: the unit of intervention is the environment, not the eater's willpower |
| 4. Myth / metaphor | "The disciplined body" (thin as virtue, fat as moral failure); "the war on obesity" (the body as battlefield) | "The commons" — health as shared infrastructure that is maintained collectively |

Deconstruction notes: the individual-choice framing hides the producers of the food environment, serves an industry preference for voluntary self-regulation, and makes structural intervention nearly unthinkable ("nanny state"). Reframe: obesity stops being a war against undisciplined bodies and becomes maintenance of a commons; if health is shared infrastructure, subsidies, zoning, marketing rules and procurement are the levers, and the litany tracks environmental quality rather than personal failure. Coherence check: commons metaphor → ecological worldview → environment-level policy → environment-quality headlines; weakest link is the disciplined-body myth, embedded in diet and fitness culture, which will eat environment-level policy unless the communication shift is explicit.

## Verification

- [ ] All four levels are populated in both columns; a table without worldview or myth content is not a CLA.
- [ ] The litany draws on at least three different media or political positions, each with a source.
- [ ] Every level-4 entry has liveness evidence — where the metaphor is findable in real discourse.
- [ ] The competing worldviews genuinely disagree about what the problem *is*, not only about the remedy.
- [ ] Vertical coherence was tested upward and the weakest link is named.
- [ ] Empirical claims at levels 1–2 carry sources; levels 3–4 are marked interpretive.

## Pair with adjacent skills

- `scenario-planning` — one scenario per worldview, or a CLA inside each scenario for depth.
- `three-horizons` — the reconstructed myth is what a third-horizon identity is built from.
- `futures-wheel` — maps consequences of the redesigned systems the reconstruction proposes.
- `grounded-fact-check` — verifies the load-bearing level 1–2 claims.
- `red-team-claim` — adversarially tests the reframe before it propagates.
- Methodology counterpart: [methodologies/foresight/causal-layered-analysis.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/causal-layered-analysis.md).

## Anti-patterns

- Do **not** stop at levels 1–2; litany plus structure is ordinary systems analysis.
- Do **not** write the worldview level as one discourse with different adjectives.
- Do **not** invent metaphors; level 4 must be alive in the culture.
- Do **not** slogan-stack the reconstruction; each level must imply the next.
- Do **not** present levels 3–4 as empirical findings.
- Do **not** smuggle in the analyst's ideology; offer two reconstructions when the future is contested.

## Reference

- S. Inayatullah, "Causal layered analysis: Poststructuralism as method," *Futures*, vol. 30, no. 8, pp. 815–829, 1998. https://doi.org/10.1016/S0016-3287(98)00086-X
- S. Inayatullah (ed.), *The Causal Layered Analysis (CLA) Reader: Theory and Case Studies of an Integrative and Transformative Methodology*. Taipei: Tamkang University Press, 2004. ISBN 978-957-8736-83-2.
- S. Inayatullah, "Six pillars: Futures thinking for transforming," *Foresight*, vol. 10, no. 1, pp. 4–21, 2008. https://doi.org/10.1108/14636680810855991
