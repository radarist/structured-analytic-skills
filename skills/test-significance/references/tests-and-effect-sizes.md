# Test selection, formulas and effect-size conventions

Companion to `../SKILL.md`. Every formula here is implemented exactly in `../scripts/significance.py`.

## Choosing the test

| Data | Test | Notes |
|---|---|---|
| Two proportions (click rate, pass rate, accuracy on a fixed test set) | Two-proportion z-test, pooled variance | Requires expected counts ≥ 5 in every cell |
| Two proportions, small counts | Fisher's exact (two-sided) | Exact hypergeometric; no large-sample assumption |
| Two proportions, 2×2 table | Chi-square, df = 1 | Equivalent to the z-test squared |
| Two means, unequal variances | Welch's t-test | The safe default for continuous metrics |
| Two means, same units measured twice | Paired t-test | Test the differences, not the two samples |
| Non-normal continuous | Mann–Whitney U | Rank-based; tests stochastic dominance, not means |

## Formulas

Two-proportion z-test (pooled):

```
p̄ = (x_A + x_B) / (n_A + n_B)
z  = (p_A − p_B) / √( p̄(1 − p̄)(1/n_A + 1/n_B) )
```

`|z| > 1.96` → p < 0.05 two-sided; `|z| > 2.576` → p < 0.01.

95 % confidence interval on the difference of proportions (unpooled SE):

```
(p_A − p_B) ± 1.96 √( p_A(1 − p_A)/n_A + p_B(1 − p_B)/n_B )
```

Welch's t and its degrees of freedom (Welch, 1947):

```
t  = (m_A − m_B) / √( s_A²/n_A + s_B²/n_B )
df = (s_A²/n_A + s_B²/n_B)² / [ (s_A²/n_A)²/(n_A−1) + (s_B²/n_B)²/(n_B−1) ]
```

## Effect sizes

```
Cohen's h = 2 arcsin√p_A − 2 arcsin√p_B          (proportions)
Cohen's d = (m_A − m_B) / s_pooled               (means)
Hedges' g = d × J,  J = 1 − 3/(4(n_A+n_B) − 9)   (small-sample correction)
```

Cohen's (1988) conventional bands, as guides rather than thresholds — the tool prints `negligible` below 0.2:

| |d| or |h| | Label |
|---|---|
| < 0.2 | negligible |
| 0.2 – 0.5 | small |
| 0.5 – 0.8 | medium |
| ≥ 0.8 | large |

Relative lift, `(p_A − p_B)/p_B`, communicates well but is not a formal effect size and is not comparable across baselines.

## Multiplicity and stopping rules

- Bonferroni: with k tests, use α/k per test. Conservative but transparent.
- False discovery rate (Benjamini–Hochberg): preferable when k is large and some false positives are tolerable.
- A test stopped the moment p crossed 0.05 has an inflated error rate; a fixed horizon or a pre-specified sequential method is required for the reported p to mean what it says.

## Common traps

- **Rates without counts.** A "significant" lift at a 0.1 % base rate with n = 1,000 rests on one or two events. Check absolute counts.
- **Metric switching.** "Significantly better on X" may quietly be "significantly worse on Y"; ask what was pre-specified.
- **One-sided by convenience.** Only pre-specified directional hypotheses justify a one-sided test.

## References

- B. L. Welch, *Biometrika* 34(1–2):28–35, 1947. doi:10.1093/biomet/34.1-2.28
- J. Cohen, *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed., 1988.
- R. L. Wasserstein and N. A. Lazar, *The American Statistician* 70(2):129–133, 2016. doi:10.1080/00031305.2016.1154108
