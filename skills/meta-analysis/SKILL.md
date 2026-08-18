---
name: meta-analysis
description: "Pools the effect sizes of several comparable studies into one estimate — inverse-variance fixed-effect and DerSimonian–Laird random-effects — and reports how much the studies disagree (Cochran's Q, I², tau²) and whether small studies skew the pool (Egger's test), with a forest table. Use when a user asks to \"run a meta-analysis\", \"pool these trial results\", \"what's the overall effect size across the studies?\", or \"how heterogeneous are the findings?\". Not for a single study's significance (use `test-significance`) or for assembling the study set (use `systematic-review`); this skill is the statistical endpoint once comparable studies are in hand."
license: MIT
metadata:
  category: evidence-verification
  method: Meta-analysis (fixed-effect and DerSimonian–Laird random-effects pooling)
  origin: G. V. Glass, 1976 (term); R. DerSimonian & N. Laird, 1986 (random-effects estimator)
  version: "2.0.0"
---
# Meta-Analysis

Meta-analysis — named by Glass (1976); standard random-effects estimator by DerSimonian and Laird (1986) — pools effect estimates from studies measuring the same thing, precision-weighted, into one estimate with a confidence interval. Its core principle: report pooling and heterogeneity together — a pooled number is only as meaningful as the agreement behind it (Higgins & Thompson, 2002).

## When to invoke

Invoke when:

- Several studies report the same effect on a common scale and a pooled answer is wanted: "pool these trials", "overall effect size", "meta-analysis of {intervention}".
- How consistent a literature is: "how heterogeneous are the findings?".
- A `systematic-review` has produced a comparable included-study table.

Do NOT invoke when:

- Only one study — use `test-significance`; nothing to pool.
- The studies still need finding and screening — use `systematic-review`.
- How much certainty the pooled body deserves — use `evidence-appraisal` (GRADE).
- No common effect scale exists — write a narrative synthesis; pooling unlike measures gives a precise, meaningless number.

## Procedure

### 1 — Fix the question and the inclusion rule

State the PICO and which studies qualify before touching numbers. If the pooling ends a `systematic-review`, the protocol already answers this — never renegotiate inclusion after seeing results. Fewer than three comparable studies: report them individually; pooling adds false authority.

### 2 — Extract per-study effect sizes on one scale

Record each study's name, its effect on a common scale (log odds ratio, standardized mean difference, or mean difference — pick one and convert), and its standard error or 95 % CI (SE = CI width ÷ 3.92). Record every conversion for the audit trail. Carry each study's `assess-study-bias` rating alongside its effect.

### 3 — Pool both ways

Compute the inverse-variance fixed-effect and DerSimonian–Laird random-effects estimates. They answer different questions: fixed-effect assumes one true effect; random-effects estimates the mean of a distribution of true effects. Report both; when they diverge materially, heterogeneity is the story, not the pooled point.

### 4 — Quantify heterogeneity

Read Cochran's Q with its p-value, I², and tau². I² is the share of observed variance beyond sampling error (Higgins & Thompson, 2002). The familiar adjectives come from a different paper — Higgins, Thompson, Deeks & Altman (*BMJ*, 2003) — which assigns *low*, *moderate* and *high* to I² values of **25 %, 50 % and 75 %**, and says a naive categorisation "would not be appropriate for all circumstances" and that the adjectives are tentative. They are anchor points, not bands, and reading them as cut-offs is this skill's simplification. Moderate or high I² calls for random-effects plus subgroup explanation (by design, population, dose); at high I² no single number should headline — report the range and its drivers.

### 5 — Probe small-study effects

Run Egger's regression test for funnel-plot asymmetry (Egger et al., 1997). Interpret it only with ten or more studies; below that it is underpowered — a null result proves nothing, a significant one merely suggests. Asymmetry may reflect publication bias or genuine small-study effects (different populations, lower quality); say which is more plausible and why.

### 6 — Report with sensitivity checks

Fill the output template: both pooled estimates with intervals, which headlines and why; heterogeneity with interpretation; the Egger result or why it is not interpreted; the forest table so every study's contribution is visible; and leave-one-out on the heaviest study — whether one trial drives the pool.

## Output template

```
## Meta-analysis — {question / PICO}

**Studies pooled:** {k} ({designs}); scale: {SMD | log OR | MD}; source: {protocol/search}
**Fixed-effect:** {estimate} (95 % CI {low} to {high})
**Random-effects (DL):** {estimate} (95 % CI {low} to {high}); tau² = {tau2}
**Headline estimate:** {FE | RE} — {reason tied to heterogeneity}
**Heterogeneity:** Q = {Q} (df {df}, p = {p}); I² = {i2} % — {low | moderate | high}; drivers: {subgroups or "unexplained"}
**Small-study effects:** Egger t({df}) = {t}, p = {p} — {interpretation | not interpreted, k < 10}
**Forest table:** {study | effect | SE | 95 % CI | weight %}
**Sensitivity:** without {heaviest study}: {estimate} ({unchanged | changed} conclusion)
**Caveats:** {risk-of-bias profile; conversions applied}
```

Mandatory fields: studies pooled, both pooled estimates, headline choice with reason, heterogeneity with interpretation, the Egger line, and the sensitivity line. A pooled estimate without its heterogeneity line is not a result.

## Worked example

Question (illustrative, invented studies): does a workplace mindfulness programme reduce burnout versus waitlist — standardized mean difference on an emotional-exhaustion scale, negative = less burnout? Six RCTs, SMDs and standard errors in `examples/mindfulness-burnout.json`. `python3 scripts/metapool.py --file examples/mindfulness-burnout.json` prints:

```
Forest table (fixed-effect weights)
study              effect       SE 95% CI                 weight %
------------------------------------------------------------------
Andersen 2017      -0.420    0.150 [-0.714, -0.126]           16.3
Bianchi 2018       -0.250    0.120 [-0.485, -0.015]           25.4
Chen 2019          -0.610    0.200 [-1.002, -0.218]            9.1
Dubois 2020        -0.100    0.110 [-0.316, 0.116]           30.2
Ekstrom 2021       -0.380    0.170 [-0.713, -0.047]           12.7
Farah 2022         -0.550    0.240 [-1.020, -0.080]            6.3
------------------------------------------------------------------
Fixed-effect pooled:    -0.301  SE 0.0605  95% CI [-0.419, -0.182]
Random-effects (DL):    -0.330  SE 0.0788  95% CI [-0.485, -0.176]

Heterogeneity: Q = 7.828 (df 5, p = 0.1660);  I^2 = 36.1%;  tau^2 = 0.0131
Egger's test: intercept = -4.013 (slope 0.274), t(4) = -4.273, p = 0.0129
  note: k = 6 < 10 -- Egger's test has low power; interpret with care.
```

Reading: I² = 36 % is moderate, so the random-effects estimate (SMD −0.33, 95 % CI −0.49 to −0.18) headlines, fixed-effect −0.30 beside it; both exclude zero. Dubois 2020 carries 30 % of the weight and is near null; without it the pool is −0.39 (95 % CI −0.53 to −0.25) with I² = 0 % — the conclusion (small-to-moderate reduction) stands, though its size hinges on one large near-null trial, and the report says so. The Egger intercept is negative and nominally significant — the two smallest studies (Chen 2019, Farah 2022) show the largest effects, a small-study pattern worth naming — but with k = 6 it is no proof of publication bias.

## Verification

- [ ] Every effect and SE traces to its source table or figure; conversions recorded.
- [ ] Recompute the pool with `scripts/metapool.py` (by hand for k ≤ 4): weights sum to 100 %, estimate = Σ(w·y)/Σw.
- [ ] The headline choice (fixed vs random) follows from the heterogeneity line, not the better-looking interval.
- [ ] Egger's test is marked "not interpreted" when k < 10; otherwise the plausible cause of asymmetry is named.
- [ ] The leave-one-out check on the heaviest study is reported; exclusions are named, with both pools shown.

## Companion tool

`scripts/metapool.py` does the arithmetic of steps 3–5: from a JSON or CSV file it prints the forest table, both pooled estimates with 95 % CIs, Cochran's Q with p, I², tau², and Egger's test (low-power note when k < 10). Stdlib only; deterministic. Sample output: the worked example.

```bash
python3 scripts/metapool.py --file studies.json   # pool + heterogeneity + Egger
python3 scripts/metapool.py --selftest            # hand-verified checks (4-study case), exits 0
```

JSON: `[{"study": "A", "effect": 0.5, "se": 0.2}, ...]` or `{"studies": [...]}`; CSV: `study,effect,se` or `study,effect,ci_low,ci_high`. By hand this works for three or four studies; beyond that, use the tool.

## Pair with adjacent skills

- `systematic-review` — the upstream pipeline; its included-study table is the input.
- `assess-study-bias` — rate each study (RoB 2) before pooling; biased studies pool into a precise biased estimate.
- `evidence-appraisal` — GRADE the pooled body; I² feeds its inconsistency factor, Egger its publication-bias factor.
- `test-significance` — the single-study case.
- `quantitative-sanity-check` — recompute pooled figures from published meta-analyses before repeating them.
- Methodology counterpart: [methodologies/research-methods/meta-analysis.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/research-methods/meta-analysis.md).

## Anti-patterns

- Do **not** report a pooled estimate without heterogeneity; I² = 80 % is a cover-up, not a summary.
- Do **not** choose fixed versus random by which gives the wanted answer; decide from what the studies are and the heterogeneity statistics.
- Do **not** interpret Egger's test below about ten studies; underpowered asymmetry tests are decoration.
- Do **not** mix effect scales; convert to one scale and record the conversion.
- Do **not** let pooling launder quality; ten high-risk-of-bias studies pool into one high-risk number.
- Do **not** drop outliers silently to lower I²; name exclusions and show the pool both ways.

## Reference

- G. V. Glass, "Primary, Secondary, and Meta-Analysis of Research," *Educational Researcher*, vol. 5, no. 10, pp. 3–8, 1976. doi:10.3102/0013189X005010003
- R. DerSimonian and N. Laird, "Meta-analysis in clinical trials," *Controlled Clinical Trials*, vol. 7, no. 3, pp. 177–188, 1986. doi:10.1016/0197-2456(86)90046-2
- J. P. T. Higgins and S. G. Thompson, "Quantifying heterogeneity in a meta-analysis," *Statistics in Medicine*, vol. 21, no. 11, pp. 1539–1558, 2002. doi:10.1002/sim.1186 — I² and its estimation; it contains no low/moderate/high categorisation.
- J. P. T. Higgins, S. G. Thompson, J. J. Deeks and D. G. Altman, "Measuring inconsistency in meta-analyses," *BMJ*, vol. 327, no. 7414, pp. 557–560, 2003. doi:10.1136/bmj.327.7414.557 — the tentative low/moderate/high adjectives at I² = 25 %, 50 % and 75 %.
- M. Egger, G. Davey Smith, M. Schneider, and C. Minder, "Bias in meta-analysis detected by a simple, graphical test," *BMJ*, vol. 315, pp. 629–634, 1997. doi:10.1136/bmj.315.7109.629
- M. Borenstein, L. V. Hedges, J. P. T. Higgins, and H. R. Rothstein, *Introduction to Meta-Analysis*. Wiley, 2009. doi:10.1002/9780470743386
- J. P. T. Higgins and J. Thomas (eds.), *Cochrane Handbook for Systematic Reviews of Interventions*, v6.5, 2024, ch. 10 (meta-analysis) and ch. 13 (missing results). https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current
