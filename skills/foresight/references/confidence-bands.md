# Confidence bands for a foresight prediction

The confidence attached to a dated prediction is a number, and the number has to mean
something consistent across predictions. These bands are the convention this skill uses.

| Confidence | Meaning | Publication rule |
| --- | --- | --- |
| 0.9+ | The milestone has effectively happened or is weeks away. | Rare — most 0.9 claims are overconfident; require two independent, dated sources. |
| 0.7–0.9 | Two independent lines of evidence point to the milestone inside the horizon. | Normal publishable range. |
| 0.5–0.7 | One strong line of evidence; reasonable counterarguments exist. | Publish, marked `directional`. |
| < 0.5 | The evidence does not support a dated milestone. | Do not publish as a prediction — write it as an open question. |

Two practical rules follow from the bands:

- **Confidence decays with horizon.** A 0.8 claim about a milestone 5 years out is almost
  always a 0.6 claim in disguise; the further out the date, the more of the confidence is
  carried by assumptions rather than observations.
- **Confidence must be scoreable.** Whatever band is chosen, the prediction is recorded so
  that `brier-score-calibration` can score it after the date passes. Bands that are never
  scored drift toward optimism.

Word choices should match the number — see `estimative-language` for the probability
vocabulary (for example "likely" for roughly 0.55–0.80) so that the prose and the figure
cannot be read as different claims.
