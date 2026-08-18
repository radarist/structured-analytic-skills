# Brier score, Murphy decomposition and skill — definitions

Companion to `../SKILL.md`. Implemented exactly in `../scripts/brier.py`.

## Brier score

```
BS = (1/N) Σ (f_t − o_t)²        f_t ∈ [0,1],  o_t ∈ {0,1}
```

Negatively oriented: 0 is perfect, 1 is the worst possible single binary forecast, 0.25 is the score of a forecaster who always says 0.50 on balanced questions. Strictly proper (Gneiting & Raftery, 2007): expected score is optimised by reporting the honest probability, so neither hedging nor exaggerating improves the expected grade.

Cost of a miss by stated confidence:

| Stated | Outcome | Contribution |
|---|---|---|
| 0.99 | did not happen | 0.9801 |
| 0.80 | did not happen | 0.6400 |
| 0.55 | did not happen | 0.3025 |
| 0.55 | happened | 0.2025 |

## Murphy (1973) decomposition

Bin the N forecasts into K bins by stated probability; bin k has n_k forecasts, mean forecast f̄_k and observed frequency ō_k. With overall base rate ō:

```
BS = RELIABILITY − RESOLUTION + UNCERTAINTY

RELIABILITY = (1/N) Σ_k n_k (f̄_k − ō_k)²      lower is better; 0 = perfectly calibrated
RESOLUTION  = (1/N) Σ_k n_k (ō_k − ō)²        higher is better; 0 = no discrimination
UNCERTAINTY = ō (1 − ō)                       fixed by the question set
```

Binning introduces small rounding, so the identity reconciles approximately when computed from binned means; `../scripts/brier.py decompose` prints the check line so the gap is visible.

### Resolution is not sharpness

- **Resolution** (Murphy, 1973) is an *outcome-dependent* decomposition term: how far the bins' conditional event frequencies depart from the base rate.
- **Sharpness** (Gneiting, Balabdaoui & Raftery, 2007) is a property of the *forecasts alone* — the concentration of the predictive distributions — computable with no outcomes at all. Their paradigm is to maximise sharpness subject to calibration.

The two are related in spirit (both reward informative rather than hedged forecasts) but they are different quantities. Report each under its own name.

## The two failure modes the decomposition exposes

| Pattern | Reading |
|---|---|
| Low reliability, low resolution | Well calibrated but uninformative — "correctly admits ignorance about everything". |
| High reliability, high resolution | Bold but miscalibrated — decisive and frequently wrong about how sure it is. |
| Low reliability, high resolution | The target: honest *and* informative. |

## Brier Skill Score

```
BSS = 1 − BS / BS_ref
```

`BS_ref` is the climatological reference — predicting the base rate ō on every question — which numerically equals the uncertainty term ō(1 − ō). BSS > 0 beats naive base-rate guessing; BSS < 0 means the forecasting subtracted value. Always report the reference used: on a question set with a lopsided base rate, a low raw Brier can still be worse than always answering "yes".

## Calibration table

Per bin, compare the stated probability with the observed frequency:

- observed **below** stated → overconfident (said 80 %, happened 60 %)
- observed **above** stated → underconfident (said 60 %, happened 80 %)

Points on the diagonal are perfectly calibrated. Overconfidence at the high end — the right side of the curve sagging below the diagonal — is the common human pattern (Tetlock & Gardner, 2015).

## Excluding unresolved forecasts

Ambiguous or never-resolved questions are excluded from N and reported separately. Scoring them as losses biases the mean toward "wrong" and rewards writing questions too vague to resolve.
