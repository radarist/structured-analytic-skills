# Power formulas, design choices and the four validities

Companion to `../SKILL.md`. The formulas below are the ones `../scripts/power.py` implements.

## Sample-size formulas (planning approximations)

Two independent means, Cohen's d, equal allocation (Cohen, 1988):

```
n per group = 2 (z_{1−α/2} + z_{1−β})² / d²
```

`--t-correct` replaces the normal quantiles with Cornish–Fisher t quantiles for small samples: d = 0.50 at α = .05, power = .80 gives 63 per group under the normal approximation and 64 with the t correction — the value in Cohen's (1992) table.

Two independent proportions, pooled-variance normal approximation with allocation ratio r = n₂/n₁ (Fleiss, Levin & Paik, 2003):

```
p̄ = (p₁ + r p₂) / (r + 1)
n₁ = [ z_{1−α/2} √((r+1) p̄(1−p̄)) + z_{1−β} √(r p₁(1−p₁) + p₂(1−p₂)) ]² / (r (p₁ − p₂)²)
```

`--continuity` applies Fleiss's continuity correction:

```
n = (n'/4) [1 + √(1 + 2(r+1) / (n' r |p₁ − p₂|))]²
```

Worked: p₁ = 0.10, p₂ = 0.12, α = .05 two-sided, power = .80, r = 1 → n' = 3840.85 → **3,841 per group, 7,682 total**; with the continuity correction, 3,941 per group.

One-sample and paired means: `n = (z_{1−α/2} + z_{1−β})² / d²`. Pearson correlation vs zero (Fisher z): `n = ((z_{1−α/2} + z_{1−β}) / atanh|r|)² + 3`.

Standard quantiles: z_{0.975} = 1.9600, z_{0.80} = 0.8416, z_{0.90} = 1.2816, z_{0.95} = 1.6449.

## Design choice

| Design | When | Cost |
|---|---|---|
| Between-subjects | The A/B default; no carry-over risk | Needs the most units |
| Within-subjects | Each unit is its own control; far more powerful | Order and carry-over effects; requires counterbalancing |
| Factorial | Two or more manipulated factors; estimates interactions | Cell counts multiply |
| Cluster-randomized | Treatment is delivered to groups (classrooms, stores) | Effective n is the number of clusters, not members |

Randomize the unit that *experiences* the treatment. Randomizing page views when users return breaks independence and understates variance.

## The four validities (Campbell & Stanley, 1963; Shadish, Cook & Campbell, 2002)

| Validity | The question | Typical threats |
|---|---|---|
| **Internal** | Did the manipulation cause the change? | Differential attrition, noncompliance, contamination between arms, broken randomization |
| **Statistical conclusion** | Is the inference from the numbers sound? | Underpowered test, unaddressed multiple comparisons, violated test assumptions, unreliable measures |
| **Construct** | Does the manipulation and the metric represent the intended concepts? | Failed manipulation check, proxy metrics (clicks ≠ value), experimenter expectancy |
| **External** | Does the result generalise? | Novelty effects, self-selected users, one time window, one context |

## Preregistration contents

Hypothesis and primary metric · minimum detectable effect and its rationale · design, randomization unit and mechanism · sample size, α and power · fixed stop rule (or a named sequential method) · exclusion rules · analysis plan per metric · guardrail metrics · multiple-comparison rule.

## References

- J. Cohen, *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed., Lawrence Erlbaum, 1988.
- J. Cohen, "A power primer," *Psychological Bulletin* 112(1):155–159, 1992. doi:10.1037/0033-2909.112.1.155
- J. L. Fleiss, B. Levin, M. C. Paik, *Statistical Methods for Rates and Proportions*, 3rd ed., Wiley, 2003. doi:10.1002/0471445428
- W. R. Shadish, T. D. Cook, D. T. Campbell, *Experimental and Quasi-Experimental Designs for Generalized Causal Inference*, Houghton Mifflin, 2002. ISBN 978-0-395-61556-0
- R. Kohavi, D. Tang, Y. Xu, *Trustworthy Online Controlled Experiments*, Cambridge University Press, 2020. doi:10.1017/9781108653985
