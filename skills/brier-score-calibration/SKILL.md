---
name: brier-score-calibration
description: "Scores a set of resolved probabilistic forecasts with the Brier score, decomposes it into reliability, resolution and uncertainty, compares it against the base-rate reference with a Brier Skill Score, and reports a per-bin calibration table showing where the forecaster is over- or underconfident. Use after predictions resolve — \"how accurate were those forecasts?\", \"score my predictions\", \"was the panel overconfident?\", \"run a calibration check\", \"Brier score for this forecast set\". Not for testing whether two groups differ (use `test-significance`) or for revising a single belief on new evidence (use `bayesian-update`)."
license: MIT
metadata:
  category: quantitative
  method: Brier score with Murphy decomposition and Brier Skill Score
  origin: G. W. Brier, 1950; A. H. Murphy (decomposition), 1973
  version: "2.0.0"
---
# Brier Score & Calibration

The Brier score (Brier, *Monthly Weather Review*, 1950) is the mean squared error between forecast probabilities and 0/1 outcomes: 0 is perfect, 0.25 is what always saying 50 % earns on balanced questions. It is **strictly proper** (Gneiting & Raftery, 2007) — expected score is optimised by reporting the honest probability, so hedging and exaggeration both cost points. Murphy's (1973) decomposition splits it into reliability, resolution and uncertainty, where the diagnosis lives: a good mean can hide a forecaster who is well calibrated but says 50 % about everything, or one bold and frequently wrong about how sure they are. It prevents a forecasting practice that never closes the loop — probabilities issued, outcomes observed, and no one checking whether the 70 % calls came true about 70 % of the time.

## When to invoke

Invoke when:

- A set of dated probabilistic forecasts has resolved and accuracy is the question: "how good were these forecasts?", "score my predictions", "was {forecaster} overconfident?".
- A forecasting practice needs an audit: "calibration check", "did our panel beat guessing?".
- A published Brier score or calibration claim is about to be quoted and needs recomputing.

Do NOT invoke when:

- The forecasts are not probabilistic or not dated — produce the dated prediction first with `foresight`.
- Only one prediction exists; calibration is a property of a *set*.
- The question is whether two groups differ — `test-significance`.
- The task is revising one belief as new evidence lands, before resolution — `bayesian-update`.
- The subject is how a decision could fail, not how accurate its probabilities were — `premortem-analysis`.

## Procedure

### 1 — Resolve the forecasts and exclude the unresolvable

For each prediction record the forecast probability `f` in [0,1], the resolution date and the binary outcome `o` (1 or 0). Forecasts that never resolved, or whose criteria turned out ambiguous, are **excluded and counted separately** — never silently scored as losses, which biases the mean toward "wrong" and rewards vague question-writing. Report the excluded count and reason alongside N.

### 2 — Compute the mean Brier score

`BS = (1/N) Σ (fₜ − oₜ)²` over the resolved set. It punishes confident errors hardest: 99 % on something that did not happen costs 0.98, while 55 % on the same miss costs 0.30. Read it against the two anchors — 0 perfect, 0.25 the always-50 % score on balanced questions — but do not stop, because the mean alone cannot distinguish a well-calibrated but uninformative forecaster from a bold and lucky one.

### 3 — Decompose into reliability, resolution and uncertainty

Bin the forecasts by stated probability and compute each bin's observed frequency. Murphy's (1973) decomposition gives `BS = reliability − resolution + uncertainty`. **Reliability** (calibration error) is how far each bin's observed frequency sits from the probability stated — lower is better, 0 is perfect calibration. **Resolution** is how far the bins' conditional frequencies depart from the base rate — higher is better, meaning the forecasts discriminate. **Uncertainty** is the base-rate variance, fixed by the question set. Resolution is *not* sharpness: sharpness is a property of the forecasts alone, computable without any outcomes (Gneiting, Balabdaoui & Raftery, 2007), whereas resolution is Murphy's outcome-dependent term. Formulas and the two failure modes: [references/decomposition.md](references/decomposition.md).

### 4 — Compare against the base-rate reference

A raw Brier score means nothing without a benchmark. Compute the Brier Skill Score against climatology — predicting the base rate on every question: `BSS = 1 − BS/BS_ref`, where `BS_ref` is the base-rate forecaster's score (numerically the uncertainty term). Positive beats naive base-rate guessing; negative means the base rate would have done better. On a lopsided question set, a Brier of 0.20 can be worse than always saying "yes".

### 5 — Read the calibration table and name the correction

Per bin, compare the stated probability with the observed frequency. Observed below stated is **overconfidence** (said 80 %, happened 60 %); above is **underconfidence**. Overconfidence at the high end is the common human pattern. Convert the table into one specific correction for next cycle — "pull 90 % calls down toward 0.7 until the top bin resolves near its stated probability" — and, where the set allows, split by topic to see whether the skill is real but narrow.

### 6 — Emit the result

Fill the output template: N and exclusions, the mean Brier, the skill score against the base rate, the three decomposition terms under their own names, the calibration table, and the two lessons.

## Output template

```
## Calibration & Brier score — {forecaster / forecast set}

**Resolved:** N = {n}  (excluded {m}: {reason})   **Span:** {first–last resolution date}

**Mean Brier score:** {BS}          (0 = perfect; 0.25 = always-50 % on balanced questions)
**Base rate (climatology):** {p}    **Reference Brier:** {BS_ref}
**Brier Skill Score:** {BSS}        (> 0 beats the base rate; < 0 is worse than guessing)
**Reliability (calibration error):** {REL}   (lower is better)
**Resolution (discrimination):** {RES}       (higher is better)
**Uncertainty (base-rate variance):** {UNC}  (fixed by the question set)

| bin | n | stated (mean f) | observed | direction |
|---|---|---|---|---|
| {[0.80,0.90)} | {n} | {0.85} | {0.50} | {overconfident} |

**Calibration lesson:** {the one correction for next cycle}
**Skill lesson:** {where the edge is real and where it is not}
```

Mandatory: N with the excluded count, the mean Brier, the Brier Skill Score with its reference, all three decomposition terms, and the calibration table. A mean Brier reported without the decomposition and the baseline must not ship.

## Worked example (illustrative)

An invented forecast set of 15 dated predictions — decent in the middle of the range, overconfident at the top — one of which never resolved. `python3 scripts/brier.py score --demo`, `decompose --demo` and `skill --demo` produce:

```
Forecasts scored (N): 14
Excluded (ambiguous/unresolved): 1
Mean Brier score: 0.2311   (0 = perfect; 0.25 = always-50% on balanced questions)

Murphy decomposition over N = 14 forecasts (1 excluded), 10 bins:
  Reliability (calibration error):  0.0917   (lower is better; 0 = perfectly calibrated)
  Resolution (discrimination):      0.1020   (higher is better)
  Uncertainty (base-rate variance): 0.2449   (fixed by the question set)
  Check: REL - RES + UNC = 0.2346 = mean Brier 0.2311

bin              n  midpoint   mean f  observed   direction
[0.40,0.50)      1      0.45    0.400     1.000   underconfident
[0.70,0.80)      2      0.75    0.700     0.500   overconfident
[0.80,0.90)      2      0.85    0.800     0.500   overconfident
[0.90,1.00]      2      0.95    0.925     0.500   overconfident

Base rate (climatology): 0.4286
Reference Brier (always predict the base rate): 0.2449
Brier Skill Score: +0.0565   (>0 beats the base rate; <0 is worse than guessing)
```

Reading it: the skill score is positive but slim (+0.057), so this forecaster beats base-rate guessing only marginally. Reliability 0.0917 against resolution 0.1020 says the discrimination is real but calibration error eats most of it. The top three bins state 0.70–0.95 and resolve at 0.50. **Calibration lesson:** pull high-confidence forecasts down toward 0.7 until the top bin resolves near its stated probability. **Skill lesson:** the edge is genuine but thin.

## Verification

Before the scorecard ships, confirm:

- [ ] Unresolved and ambiguous forecasts are excluded and counted, never scored as losses.
- [ ] N is large enough to say anything; rare-event sets need far more.
- [ ] Recompute with `python3 scripts/brier.py decompose --file forecasts.csv` and check `REL − RES + UNC` reconciles with the mean Brier (small gaps are bin rounding).
- [ ] The Brier Skill Score is reported with the reference it was computed against.
- [ ] Reliability and resolution are named correctly, and sharpness is not used as a synonym for resolution.
- [ ] The calibration lesson is a specific correction, not "be better calibrated".

## Companion tool

`scripts/brier.py` (stdlib only, Python 3.9+) computes everything above from a CSV or JSON of `probability,outcome` rows. Outcomes accept `1`/`0`/`yes`/`no`/`true`/`false`; `?`, empty and `n/a` are unresolved and excluded, never counted as losses. Subcommands: `score` (N, excluded count, mean Brier), `decompose` (reliability, resolution, uncertainty plus the per-bin calibration table, `--bins` default 10) and `skill` (base rate, reference Brier, Brier Skill Score). Each takes `--file PATH` or `--demo`.

```bash
python3 scripts/brier.py score --file forecasts.csv
python3 scripts/brier.py decompose --file forecasts.csv --bins 10
python3 scripts/brier.py skill --demo
python3 scripts/brier.py --selftest        # 16 hand-verified checks, including the decomposition identity
```

Usable without the tool for the mean Brier, but the decomposition and the per-bin table are tedious by hand and easy to get wrong.

## Pair with adjacent skills

- `foresight` — produces the dated probabilistic prediction this skill scores once it resolves.
- `delphi-method` — a panel median is itself a forecast; score panels over time to find which compositions have skill.
- `bayesian-update` — the update discipline whose priors and likelihoods these scores audit.
- `reference-class-forecasting` — supplies the base rate the climatological reference leans on.
- `quantitative-sanity-check` — recompute anyone else's published Brier claim before quoting it.
- Methodology counterpart: [methodologies/scientific-methods/bayesian-evidence-updating.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/scientific-methods/bayesian-evidence-updating.md) — the updating discipline these scores audit.

## Anti-patterns

- Do **not** score a single prediction as if it meant something. Calibration is a set property.
- Do **not** count unresolved or ambiguous forecasts as losses. Exclude them and say how many.
- Do **not** report the mean Brier without the decomposition and a baseline; a good mean hides both failure modes.
- Do **not** call resolution "sharpness". Sharpness is a property of the forecasts alone; resolution is Murphy's outcome-dependent term.
- Do **not** score rare events on a small set — the Brier score discriminates poorly between small probabilities without many forecasts.

## Reference

- G. W. Brier, "Verification of Forecasts Expressed in Terms of Probability," *Monthly Weather Review*, vol. 78, no. 1, pp. 1–3, 1950. doi:10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2
- A. H. Murphy, "A New Vector Partition of the Probability Score," *Journal of Applied Meteorology*, vol. 12, no. 4, pp. 595–600, 1973. doi:10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2 — the reliability/resolution/uncertainty decomposition.
- T. Gneiting and A. E. Raftery, "Strictly Proper Scoring Rules, Prediction, and Estimation," *Journal of the American Statistical Association*, vol. 102, no. 477, pp. 359–378, 2007. doi:10.1198/016214506000001437 — why strict propriety makes the Brier score ungameable.
- T. Gneiting, F. Balabdaoui, and A. E. Raftery, "Probabilistic Forecasts, Calibration and Sharpness," *Journal of the Royal Statistical Society: Series B*, vol. 69, no. 2, pp. 243–268, 2007. doi:10.1111/j.1467-9868.2007.00587.x — sharpness as a property of the forecasts, maximised subject to calibration.
- P. E. Tetlock and D. Gardner, *Superforecasting: The Art and Science of Prediction*. New York: Crown, 2015. ISBN 978-0-8041-3669-3 — the empirical case that calibration is measurable and trainable.
