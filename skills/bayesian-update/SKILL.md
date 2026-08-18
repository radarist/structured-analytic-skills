---
name: bayesian-update
description: "Revises a stated probability in light of one new piece of evidence using the odds form of Bayes' rule — prior odds × Bayes factor = posterior odds — and reports the posterior in both relative and absolute terms with a sensitivity sweep over the prior and the likelihood ratio. Use when a belief has to move by a defensible amount: \"update my prior\", \"how much should this evidence change my estimate?\", \"what's the posterior probability?\", \"run a Bayesian update on this\". Not for enumerating and ranking several rival explanations (use `analysis-of-competing-hypotheses`) or for scoring forecasts after they resolve (use `brier-score-calibration`)."
license: MIT
metadata:
  category: quantitative
  method: Bayesian belief updating in odds form (prior odds × Bayes factor)
  origin: T. Bayes (ed. R. Price), 1763; P.-S. Laplace, 1812
  version: "2.0.0"
---
# Bayesian Update

A Bayesian update replaces "does this evidence prove it?" with "how far should this evidence move me?" In odds form — posterior odds = prior odds × Bayes factor — it forces three things into the open: the base rate the belief started from, how expected the evidence is under the hypothesis *and* under its negation, and the resulting probability read both relatively and absolutely. The rule descends from Bayes' posthumous essay (ed. Price, 1763) and Laplace's general development (1812). It fixes two failures: base-rate neglect, where a striking test result on a rare condition reads as near-certainty because the prior was never named; and overreaction, where one vivid datum overwrites a grounded belief though it is nearly as likely under the alternative.

## When to invoke

Invoke when:

- A stated probability must move on new information: "update my prior", "does this change anything?", "given this evidence, how likely is {X} now?".
- A signal is read as decisive and the base rate is low: "is this enough to act on?".
- A forecast needs revising before resolution and the size of the revision must be defensible, not felt.

Do NOT invoke when:

- Several rival explanations need enumerating and ranking — `analysis-of-competing-hypotheses` does that across all hypotheses.
- The forecasts have resolved and the question is whether they were accurate — `brier-score-calibration`.
- The question is factual with one right answer — `grounded-answer`.
- No prior exists and no reference class can be found — build one with `reference-class-forecasting`.
- The answer follows deterministically from rules, not from evidence weight.

## Procedure

### 1 — State one binary hypothesis

Write H as a specific, resolvable proposition ("the supplier misses the March deadline") so ¬H is unambiguous. This form handles two hypotheses; for a messy space either update the leading pair only and say so, or run `analysis-of-competing-hypotheses`. A posterior computed across a hypothesis space that was never enumerated is arithmetic dressed as analysis.

### 2 — Set the prior from a reference class

`P(H)` is the base rate: how often this kind of thing has been true in a class of comparable cases. Name the class — "companies at this stage acquired within any 18-month window" — and its source. If no reference class exists, say so and use a deliberately wide prior; a wide honest prior beats a precise invented one, and step 5 shows how much the choice matters. Convert to odds: `odds = P/(1 − P)`.

### 3 — Estimate both likelihoods and read the Bayes factor

Ask two questions, not one: if H were true, how expected is this evidence — `P(E|H)`; and if H were false, how expected is it anyway — `P(E|¬H)`. Their ratio is the Bayes factor, the entire strength of the evidence. Evidence likely under both stories has a factor near 1 and moves nothing, however dramatic it feels. Most single signals land in the 1–10 range.

The tool prints the rounded scale — 1–3 barely worth mentioning, 3–10 moderate, 10–30 strong, 30–100 very strong, above 100 decisive. Those boundaries are Jeffreys' half-unit grid rounded, the labels are drawn partly from Jeffreys and partly from Lee and Wagenmakers (2014), and the combination is this skill's, not any one source's. Kass and Raftery (1995, p. 777) print two further grids — Jeffreys' as they reproduce it, and their own recommended 1–3 / 3–20 / 20–150 / >150 scale. All are descriptive conventions, not thresholds. Conversions, worked rows and the independence rule: [references/odds-form-and-bayes-factors.md](references/odds-form-and-bayes-factors.md).

### 4 — Multiply, and report both reads

`posterior odds = prior odds × Bayes factor`, then `P = odds/(1 + odds)`. Report the **relative** shift ("odds moved 6×") and the **absolute** posterior ("still 40 %, less likely than not") together. Either alone misleads: a tenfold move on a 1-in-1,000 prior leaves the hypothesis at 1-in-100, and quoting only the multiple is how weak evidence is sold as a breakthrough.

### 5 — Sweep the prior and the Bayes factor

Vary the prior across its plausible range and the Bayes factor across the range the likelihood estimates could defensibly take, and check whether the **decision** — not the number — changes anywhere in that grid; `scripts/bayes.py sweep` prints it. If a small, defensible change in the prior flips the call, there is no conclusion yet, only a need for more diagnostic evidence. Name the most load-bearing input, usually `P(E|¬H)` — the hardest quantity to estimate and the one most often set by wishful thinking.

### 6 — Chain further evidence only if it is independent

When several data arrive, multiply their Bayes factors only if they are genuinely independent given H. Two reports citing the same primary source are one observation; multiplying them double-counts. Estimate a single joint Bayes factor for a correlated cluster and record the judgement. `scripts/bayes.py chain --dependent` prints this warning alongside the arithmetic.

## Output template

```
## Bayesian update — {question}

**Hypothesis (H):** {specific, resolvable proposition}
**Prior P(H):** {value} — reference class: {class and its source}   **Prior odds:** {a:b}

**Evidence (E):** {the specific datum, dated and sourced}
**P(E|H):** {value} — {why}
**P(E|¬H):** {value} — {why}
**Bayes factor:** {ratio} — {barely worth mentioning | moderate | strong | very strong | decisive}

**Posterior odds:** {value}  →  **Posterior P(H|E):** {value}
- Relative: odds moved {N}×.
- Absolute: {still unlikely | roughly coin-flip | likely} at {P}.

**Sensitivity:** decision is {robust | fragile} — it flips if the prior exceeds {X} or the Bayes factor exceeds {Y}.
**Most load-bearing input:** {which quantity, and what would re-source it}
**Independence:** {this evidence is independent of prior updates | correlated with {…}, so a joint factor of {…} was used}
```

Mandatory: the reference class behind the prior, both likelihoods with their reasoning, the Bayes factor, both reads of the posterior, and the sensitivity line. A posterior without the sensitivity line is a guess with decimal places.

## Worked example (illustrative)

Question: *will this startup be acquired within 18 months?* A first corporate-development executive appears on the team page. All figures are invented for the illustration. The arithmetic comes from `python3 scripts/bayes.py update --prior 0.10 --pe-h 0.6 --pe-not-h 0.1`:

```
P(E|H):            0.6
P(E|~H):           0.1
Prior P(H):        0.1
Prior odds:        0.1111  (0.1111:1 H:~H)
Bayes factor:      6  [moderate]
Posterior odds:    0.6667
Posterior P(H|E):  0.4
Two reads:
- Relative: odds moved 6x (from 0.1111:1 to 0.6667:1).
- Absolute: hypothesis is now roughly coin-flip (40%).
```

The prior of 0.10 comes from a reference class of comparable venture-backed companies at this stage acquired within any 18-month window. The likelihoods say most companies in late acquisition talks staff corporate development (0.6), while a minority of non-acquired startups make the same hire (0.1) — a Bayes factor of 6, moderate, not decisive. `python3 scripts/bayes.py sweep --prior 0.10 --bf 6` shows the posterior running from 0.13 at a prior of 0.025 to 0.82 at a prior of 0.20 on the same evidence:

```
prior \ BF |         2|         6|        18
     0.025    |    0.0488|    0.1333|    0.3158
       0.1 (P)|    0.1818|    0.4000|    0.6667
       0.2    |    0.3333|    0.6000|    0.8182
```

**Sensitivity:** fragile — "more likely than not" arrives at a prior of about 0.15 or a Bayes factor of about 9. **Most load-bearing input:** `P(E|¬H)`, the rate of corp-dev hiring among companies that are *not* acquired; re-sourcing that from hiring data would firm up the conclusion far more than refining the prior.

## Verification

Before the update ships, confirm:

- [ ] H is stated so ¬H is unambiguous, and the update covers a genuine binary, not a collapsed multi-hypothesis space.
- [ ] The prior names its reference class and source; an unsourced prior is flagged and widened.
- [ ] Both `P(E|H)` and `P(E|¬H)` are stated with reasoning — quoting only `P(E|H)` is not a Bayesian update.
- [ ] Recompute with `python3 scripts/bayes.py update --prior … --pe-h … --pe-not-h …` and check the posterior.
- [ ] Both the relative shift and the absolute posterior appear; neither is quoted alone.
- [ ] The sensitivity sweep was run and the most load-bearing input is named.
- [ ] Chained updates use independent evidence, or one joint Bayes factor with the dependence recorded.

## Companion tool

`scripts/bayes.py` (stdlib only, Python 3.9+) does the odds-form arithmetic so the emitted numbers are computed, not estimated. `update` takes `--prior` with either `--bf` or the likelihoods `--pe-h`/`--pe-not-h`, printing the Bayes factor with its band, posterior odds, posterior probability and both reads. `chain` applies a comma-separated list of factors one at a time, `--dependent` adding the double-counting warning. `sweep` prints the step-5 grid over priors {P/4, P/2, P, 2P, 4P capped at 0.99} × factors {BF/3, BF, 3BF}.

```bash
python3 scripts/bayes.py update --prior 0.10 --pe-h 0.6 --pe-not-h 0.1
python3 scripts/bayes.py chain --prior 0.1 --bf 5,4 --dependent
python3 scripts/bayes.py sweep --prior 0.25 --bf 10
python3 scripts/bayes.py --selftest        # 12 hand-checked cases, including the band boundaries
```

Usable without the tool — the update is one multiplication — but the sweep and the band boundaries are what the tool makes cheap enough to always run.

## Pair with adjacent skills

- `analysis-of-competing-hypotheses` — enumerate and rank all hypotheses first; this skill puts a number on the leading pair.
- `reference-class-forecasting` — supplies the base rate that becomes the prior.
- `key-assumptions-check` — the prior is an assumption; challenge it when it dominates the result.
- `brier-score-calibration` — over many updates, scores whether the priors and likelihoods were any good.
- `rate-source-admiralty` — grade the evidence before its Bayes factor is trusted.
- Methodology counterpart: [methodologies/scientific-methods/bayesian-evidence-updating.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/scientific-methods/bayesian-evidence-updating.md) — the broader Bayesian evidence framework this operationalises.

## Anti-patterns

- Do **not** skip the prior. "Looking only at the evidence" is base-rate neglect wearing objectivity as a costume.
- Do **not** invent a precise prior. A wide honest prior with a sweep beats a fabricated point estimate.
- Do **not** confuse vividness with diagnosticity. A shocking fact that is equally likely under ¬H has a Bayes factor near 1.
- Do **not** quote the relative shift alone. "Odds tripled" on a 1-in-1,000 hypothesis still leaves it near zero.
- Do **not** multiply Bayes factors for correlated evidence — two retellings of one source are one observation.
- Do **not** use an update to decorate a foregone conclusion; if the prior is 0.99, no evidence will move it and the real work is `key-assumptions-check`.

## Reference

- T. Bayes (posthumous, communicated by R. Price), "An Essay towards solving a Problem in the Doctrine of Chances," *Philosophical Transactions of the Royal Society of London*, vol. 53, pp. 370–418, 1763. doi:10.1098/rstl.1763.0053
- P.-S. Laplace, *Théorie analytique des probabilités*. Paris: Courcier, 1812 — the general development that made the rule usable.
- R. E. Kass and A. E. Raftery, "Bayes Factors," *Journal of the American Statistical Association*, vol. 90, no. 430, pp. 773–795, 1995. doi:10.1080/01621459.1995.10476572 — the Bayes factor, Jeffreys' scale as they reproduce it, and their own recommended scale (both on p. 777).
- M. D. Lee and E.-J. Wagenmakers, *Bayesian Cognitive Modeling: A Practical Course*. Cambridge: Cambridge University Press, 2014. ISBN 978-1-107-60357-8 — the rounded 1/3/10/30/100 boundaries, after Jeffreys, that this skill's hybrid band labels sit on.
- P. E. Tetlock and D. Gardner, *Superforecasting: The Art and Science of Prediction*. New York: Crown, 2015. ISBN 978-0-8041-3669-3 — incremental updating as a measured driver of forecasting accuracy.
