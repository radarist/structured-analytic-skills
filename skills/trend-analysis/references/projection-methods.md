# Trend analysis — choosing and caveating a projection method

Supplement to `../SKILL.md` step 4. The companion tool `../scripts/trend.py` implements every method described here.

## Choosing the shape

| Method | Use when | States explicitly | Main failure |
|---|---|---|---|
| Naive extrapolation | The quantity is slow and structurally driven (demographics, installed base) and the horizon is short relative to the observed span | "Present drivers persist unchanged" | Silent extension of a trend past a ceiling |
| Linear (OLS) | The period gains are roughly constant and no ceiling binds within the horizon | Slope with fit quality | Same as naive, with false precision |
| Exponential (log-linear) | Growth is proportional and far from any limit — early diffusion, cost declines | Growth rate per period, doubling time | Explosive projections; almost always wrong at the horizon |
| Logistic / S-curve | A ceiling exists (a share cannot exceed 100 %, a physical limit binds) | The assumed or fitted ceiling K, the inflection date, the fraction of K reached | K is poorly identified from data on the lower half of the curve (Meade & Islam, 2006) |
| Trend Impact Analysis | Identifiable future events could bend the curve | Baseline, then each event's probability and impact | Double counting events, or events whose impacts are not independent |

## Trend Impact Analysis arithmetic (Gordon)

1. Fit the surprise-free baseline from the historical series and project it to the horizon.
2. List the unprecedented or infrequent events that could plausibly alter the trajectory. Each needs a name specific enough to be checked later.
3. Assign each event a probability of occurring by the horizon and an impact on the projected value, in the units of the series.
4. Adjust the baseline by the sum of probability × impact, and report the baseline, each adjustment and the net effect separately — never only the adjusted number.
5. Convert each event into a signpost: what observation would show it occurring, and where that observation would surface.

Events must be mutually independent in their impacts, or their combined effect will be double counted; where two events share a cause, model the cause instead.

## Reading curvature from period gains

With observations at even intervals, the sequence of first differences answers the shape question before any fitting:

- growing differences → accelerating (candidate exponential, or the lower half of a logistic);
- roughly constant differences → linear;
- shrinking differences → saturating (candidate upper half of a logistic).

Where the series is short, curvature read from gains is more robust than a fitted parameter, and it is the read the tool reports first.

## Diffusion position (Rogers)

Rogers' categories partition **cumulative** adopters, so these boundaries apply only to a cumulative-adoption series — never to an annual sales share or shipment share, which is a flow and belongs in the Fisher–Pry substitution frame. On a cumulative series: adoption below roughly 16 % is the innovator and early-adopter phase; 16–50 % the early majority; above 50 % the later majority and laggards. Position matters more than rate for the "how far can it run" question: the same annual increment means something different before and after the inflection.

## Honest bands

The tool reports a ± 2 × in-sample RMSE band. This is a rough spread, not a prediction interval: it ignores parameter uncertainty and the growth of error with the horizon. Report the horizon multiple (periods projected divided by periods observed) alongside it; above 1, the projection has left the evidence behind and must travel with the assumption sheet and signposts.
