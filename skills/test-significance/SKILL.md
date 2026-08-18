---
name: test-significance
description: "Decides whether a reported gap between two groups is a real difference or sampling noise, and reports the p-value, the 95 % confidence interval on the difference and an effect size rather than a bare verdict. Use when a claim rests on a comparison — \"Model A scored 87% vs Model B's 85%\", \"the new variant lifted conversion 12%\", \"is this A/B test result significant?\", \"run a significance test on these two proportions\". Not for pooling several studies into one estimate (use `meta-analysis`) or for planning a test before data exist (use `experimental-design`)."
license: MIT
metadata:
  category: quantitative
  method: Null-hypothesis significance test with confidence interval and effect size
  origin: R. A. Fisher, 1925; W. S. Gosset ("Student"), 1908; B. L. Welch, 1947
  version: "2.0.0"
---
# Test Significance

A significance test asks whether a measured gap between two groups is larger than sampling variation alone would produce. Its core principle, from Fisher's *Statistical Methods for Research Workers* (1925), is that a difference means nothing without the sample sizes and variability behind it. Modern practice adds the second half: a p-value alone is not a result — the ASA statement (Wasserstein & Lazar, 2016) and the estimation tradition (Cumming, 2014) require the confidence interval on the difference and an effect size beside it. The failure prevented is confident repetition of a two-point gap that 800 observations cannot distinguish from noise — and its mirror image, a trivial effect called important because n was huge.

## When to invoke

Invoke when:

- A claim compares two groups on a number: "significantly better than", "outperforms", "+12 % over baseline", "A/B test result", "benchmark comparison".
- A small gap is treated as a real difference and the sample sizes are available or obtainable.
- A published result cites a p-value alone and its interval and effect size need reconstructing.

Do NOT invoke when:

- Several studies estimate the same effect and one pooled number is wanted — `meta-analysis`.
- No data exist yet and the question is how many observations are needed — `experimental-design`.
- The doubt is the source's own arithmetic, not sampling noise — `quantitative-sanity-check`.
- The numbers are probabilistic forecasts to be graded for accuracy — `brier-score-calibration`.
- The design may be biased, so no test can rescue it — `assess-study-bias`.

## Procedure

### 1 — Extract the four numbers

Every check needs each group's metric value and sample size. For proportions get raw counts (x out of n), not just the rate: 12 % of 800 is 96 successes, and the counts drive the test. If the source reports only a gap ("+12 % over baseline") with no n, mark the claim **unverifiable** and stop — never guess a sample size.

### 2 — Choose the test that matches the data

Two proportions (click rate, pass rate, accuracy on a fixed test set) → pooled two-proportion z-test, or Fisher's exact when any expected cell count is below 5. Two means (latency, a continuous score) → Welch's t-test, the safe default under unequal variances. Same units under both variants → paired t-test on the differences. Non-normal continuous → Mann–Whitney U. Full selection table, formulas and traps: [references/tests-and-effect-sizes.md](references/tests-and-effect-sizes.md).

### 3 — Compute the statistic

For two proportions, `z = (p_A − p_B) / √(p̄(1 − p̄)(1/n_A + 1/n_B))` with `p̄ = (x_A + x_B)/(n_A + n_B)`; |z| > 1.96 is p < 0.05 two-sided, |z| > 2.58 is p < 0.01. For two means use Welch's t with Welch–Satterthwaite degrees of freedom. Use two-sided tests unless a one-sided hypothesis was genuinely pre-specified; `scripts/significance.py` computes each exactly.

### 4 — Report the confidence interval on the difference

The interval, not the p-value, carries the information. For a proportion difference use the unpooled standard error: `(p_A − p_B) ± 1.96 √(p_A(1 − p_A)/n_A + p_B(1 − p_B)/n_B)`. An interval crossing zero means no significant difference at α = 0.05; one entirely on a side is directional, and its width states the precision. Read both ends against the decision threshold — a low end below the smallest worthwhile effect does not license acting as if the point estimate were true.

### 5 — Report an effect size

Significance says "probably not noise"; effect size says how much it matters. Cohen's h for proportions, `2(arcsin√p_A − arcsin√p_B)`; Cohen's d for means, `(mean_A − mean_B)/pooled SD`, with Hedges' g for small samples. Cohen's (1988) bands — 0.2 small, 0.5 medium, 0.8 large — are guides, not thresholds. Relative lift communicates well but is not a formal effect size. A result can be significant and practically trivial at large n; report both.

### 6 — Flag underpowered and multiplicity problems

If either arm is small (n < 30 continuous, or expected cell counts below 5 for proportions), a null result means "we cannot tell", never "the groups are equivalent". If many subgroups or metrics were tested, one reaches p < 0.05 by chance: correct with Bonferroni (α/k) or FDR, and check the stopping rule — a test stopped the moment it crossed 0.05 has an inflated p-value.

### 7 — Render the verdict

Fill the output template with the test used, p, the interval, the effect size and a one-sentence plain-language reading naming the decision consequence — not just "significant".

## Output template

```
## Significance check — {comparison}

- Group A: {metric} = {value} ({x_A}/{n_A})
- Group B: {metric} = {value} ({x_B}/{n_B})
- Test used: {two-proportion z (pooled) | Welch's t | Fisher's exact | paired t}
- **p-value:** {p} (two-sided)
- **95 % CI on the difference:** [{lo}, {hi}]
- **Effect size:** {Cohen's h | d} = {value} ({negligible | small | medium | large})
- **Power/multiplicity:** {counts adequate? k tests → corrected alpha? stopping rule pre-specified?}

**Verdict:** {significant | not significant | underpowered | inconclusive}
**What this means:** {the decision the interval supports, not the p-value}
```

Mandatory fields: both sample sizes, the test used, the confidence interval and the effect size. A verdict without the interval must not ship.

## Worked example

Illustrative case: a team at the retailer Northwind reports "the new onboarding flow lifted conversion from 12 % to 16 % — roll it out?" The four numbers are control 96/800 (12.0 %) and treatment 128/800 (16.0 %). Expected counts are well above 5, so the pooled two-proportion z-test applies:

```
$ python3 scripts/significance.py two-prop --x1 128 --n1 800 --x2 96 --n2 800
p1 = 0.1600 (128/800), p2 = 0.1200 (96/800)
z = 2.306, two-sided p = 0.0211
95% CI on (p1 - p2): [0.0061, 0.0739]
Cohen's h = 0.116 (negligible)
Reminder: p only says 'probably not noise' — always report the CI and effect size too; a significant result can be practically trivial.
```

Filled in: test = two-proportion z (pooled); p = 0.021 two-sided; 95 % CI on the difference [+0.6 pp, +7.4 pp]; Cohen's h = 0.116 (negligible); single pre-specified metric on a fixed horizon, so no multiplicity correction. **Verdict:** significant, small effect. **What this means:** the lift is unlikely to be noise, but the interval reaches down to +0.6 pp — below the level that repays the rebuild — so the decision turns on the economics of that low end, not on p = 0.021.

## Verification

Before the verdict ships, confirm:

- [ ] Both sample sizes (and raw counts for proportions) are stated; a comparison without n is reported as unverifiable.
- [ ] The test matches the data type — proportions, means, paired, or exact when any expected cell count is below 5.
- [ ] Recompute p and the interval with the matching `scripts/significance.py` subcommand and check the printed values against the report.
- [ ] The confidence interval is present and its low end was read against the decision threshold.
- [ ] The effect size is reported with its band, and a non-significant result is not described as "equivalent".
- [ ] Multiplicity and the stopping rule are addressed when more than one comparison was run.

## Companion tool

`scripts/significance.py` (stdlib only, Python 3.9+) computes the summary-statistic tests: `two-prop` (pooled z-test, 95 % CI on the difference, Cohen's h), `fisher` (exact 2×2), `chi2` (2×2, df = 1), `welch` (exact t-distribution p-value), `paired` (paired t on the differences, with CI and Cohen's d_z) and `effect` (Cohen's d with Hedges' g). Mann–Whitney U is deliberately absent: it needs the raw observations to rank, not summary statistics, so run it in your stats environment and bring the result back. Every subcommand prints a reminder not to report p alone.

```bash
python3 scripts/significance.py two-prop --x1 128 --n1 800 --x2 96 --n2 800
python3 scripts/significance.py welch --mean1 20.82 --sd1 2.804894 --n1 15 --mean2 22.986667 --sd2 1.952605 --n2 15
python3 scripts/significance.py fisher --a 3 --b 1 --c 1 --d 3
python3 scripts/significance.py --selftest       # 12 hand-verified checks
```

Sample (`welch` above):

```
mean1 = 20.82 (n = 15), mean2 = 22.9867 (n = 15)
Welch t = -2.4554, df = 24.99, two-sided p = 0.0214
```

Usable without the tool; it removes arithmetic slips and gives the exact p rather than a threshold.

## Pair with adjacent skills

- `experimental-design` — the upstream sibling: it fixes the MDE, sample size and analysis plan before data exist; this skill reads the result.
- `meta-analysis` — pool several comparable studies instead of testing one.
- `quantitative-sanity-check` — recompute the source's arithmetic before testing whether its gap is real.
- `assess-study-bias` — a significant result from a biased design is still unreliable.
- `brier-score-calibration` — accuracy scoring for probabilistic forecasts, a different question.

## Anti-patterns

- Do **not** treat p < 0.05 as a pass/fail gate. The decision lives at the interval's ends.
- Do **not** report a comparison without sample sizes. "+12 %" with no n cannot be checked.
- Do **not** convert non-significant into "equivalent" — absence of evidence is not evidence of absence, especially at small n.
- Do **not** use a one-sided test unless the direction was pre-specified; the default is two-sided.
- Do **not** report the one subgroup out of twenty that reached 0.05 without a multiplicity correction.

## Reference

- R. A. Fisher, *Statistical Methods for Research Workers*. Edinburgh: Oliver and Boyd, 1925 — the significance-testing framework and the 0.05 convention.
- B. L. Welch, "The Generalization of 'Student's' Problem when Several Different Population Variances are Involved," *Biometrika*, vol. 34, no. 1–2, pp. 28–35, 1947. doi:10.1093/biomet/34.1-2.28 — the unequal-variance t-test.
- J. Cohen, *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Hillsdale, NJ: Lawrence Erlbaum, 1988 — d and h and their conventional bands.
- R. L. Wasserstein and N. A. Lazar, "The ASA Statement on p-Values: Context, Process, and Purpose," *The American Statistician*, vol. 70, no. 2, pp. 129–133, 2016. doi:10.1080/00031305.2016.1154108.
- G. Cumming, "The New Statistics: Why and How," *Psychological Science*, vol. 25, no. 1, pp. 7–29, 2014. doi:10.1177/0956797613504966 — estimation over dichotomous testing.
