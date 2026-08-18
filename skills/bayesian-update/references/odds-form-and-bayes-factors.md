# Odds form, Bayes factors and interpretation scales

Companion to `../SKILL.md`. Implemented in `../scripts/bayes.py`.

## The rule

```
posterior odds = prior odds × Bayes factor

P(H|E)/P(¬H|E) = [P(H)/P(¬H)] × [P(E|H)/P(E|¬H)]
```

Conversions:

```
odds = P / (1 − P)          P = odds / (1 + odds)
```

Odds form is preferred because the update is a single multiplication and the two inputs — where the belief started and how discriminating the evidence is — stay visible and separately criticisable.

## Bayes factor bands

The companion tool prints the rounded scale below. The boundaries are Jeffreys' half-unit grid rounded to 1/3/10/30/100 (as popularised by Lee & Wagenmakers, 2014); the labels mix Jeffreys' wording ("barely worth mentioning", "decisive") with Lee & Wagenmakers' "moderate". The combination is this skill's own, and matches neither published scale exactly:

| Bayes factor | Band printed |
|---|---|
| 1 – 3 | barely worth mentioning |
| 3 – 10 | moderate |
| 10 – 30 | strong |
| 30 – 100 | very strong |
| > 100 | decisive |

Two published scales sit behind it, both printed on the same page of Kass & Raftery (1995, JASA 90(430):777):

- **Jeffreys' scale as Kass & Raftery reproduce it** (Jeffreys 1961, app. B, with two categories pooled): 1–3.2 "not worth more than a bare mention", 3.2–10 "substantial", 10–100 "strong", > 100 "decisive". This one is Jeffreys', not theirs.
- **Kass & Raftery's own recommended scale** ("from our own experience, these categories seem to furnish appropriate guidelines"), stated on 2·log_e(B10): 1–3 "not worth more than a bare mention", 3–20 "positive", 20–150 "strong", > 150 "very strong".

All three are conventions for describing a continuous ratio, not decision thresholds; quote whichever is used, name whose it is, and do not mix them within one analysis.

## Worked conversions

| Prior P(H) | Prior odds | BF | Posterior odds | Posterior P(H|E) |
|---|---|---|---|---|
| 0.01 | 0.0101 | 20 | 0.202 | 0.168 |
| 0.10 | 0.1111 | 6 | 0.667 | 0.400 |
| 0.25 | 0.3333 | 8 | 2.667 | 0.727 |
| 0.50 | 1.0000 | 10 | 10.0 | 0.909 |

The first row is the base-rate lesson in one line: a Bayes factor of 20 on a 1 % prior still leaves the hypothesis at 17 %.

## Diagnosticity, not drama

The Bayes factor depends on the *contrast* between `P(E|H)` and `P(E|¬H)`, not on how surprising the evidence feels. Evidence expected under both stories carries a factor near 1 and moves nothing. `P(E|¬H)` is usually the harder estimate and the one most often set by wishful thinking; it is the first quantity to re-source when a conclusion is fragile.

## Independence when chaining

Chained updates multiply Bayes factors, which assumes each datum is independent given H (and given ¬H). Two reports citing the same primary source are one observation; multiplying them double-counts the evidence. For a correlated cluster, estimate one joint Bayes factor and record the judgement. `../scripts/bayes.py chain --dependent` prints this warning next to the arithmetic.

## Sensitivity sweep

`../scripts/bayes.py sweep --prior P --bf BF` prints posteriors over priors {P/4, P/2, P, 2P, 4P capped at 0.99} × Bayes factors {BF/3, BF, 3BF}. The question the table answers is not "how much does the number change?" but "does the *decision* change anywhere in the plausible range?" If it does, the analysis needs more diagnostic evidence, not more confidence.

## References

- T. Bayes (ed. R. Price), *Phil. Trans. R. Soc.* 53:370–418, 1763. doi:10.1098/rstl.1763.0053
- R. E. Kass and A. E. Raftery, *JASA* 90(430):773–795, 1995. doi:10.1080/01621459.1995.10476572
- M. D. Lee and E.-J. Wagenmakers, *Bayesian Cognitive Modeling: A Practical Course*, Cambridge University Press, 2014. ISBN 978-1-107-60357-8
