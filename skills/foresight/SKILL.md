---
name: foresight
description: "Produces one dated, falsifiable prediction about a single technology, trend or market shift — the milestone with a date and a confidence, its accelerants and blockers with lead times, weak signals to watch now, kill-signals that would retract it, and a review date. Use for timing questions — \"when will X happen?\", \"is this accelerating or stalling?\", \"what should be watched to know if this is real?\", \"give a dated forecast with kill-signals\". Not for branching what-could-happen questions — use `scenario-planning`; not for a standing scan of many signals — use `horizon-scanning`; not for polling an expert panel — use `delphi-method`."
license: MIT
metadata:
  category: decision-strategy
  method: Single-trajectory dated prediction with weak-signal and kill-signal watchlist (composite)
  origin: Composite for agent use; weak-signal anchors — H. Igor Ansoff, 1975; Elina Hiltunen, 2008
  version: "2.0.0"
---
# Foresight

A forecast is only useful if someone could later show it was wrong. This skill turns a timing question into a single trajectory: one milestone with an absolute date and a numeric confidence, the forces that would pull it earlier or push it later with their lead times, the weak signals worth watching today, the kill-signals that would force a retraction, and a review date. It is a **composite** built for agent use, not a published method: the watchlist half descends from H. Igor Ansoff's weak-signal response (1975) and Elina Hiltunen's future sign (2008), and the falsification half is ordinary forecasting hygiene — never present it as canonical. The failure it prevents is the undated, unfalsifiable claim that no evidence can ever disturb.

## When to invoke

Invoke when:

- The question is about timing: "when will X happen?", "by what date?", "is this accelerating or stalling?".
- A brief is about to make a dated claim and needs it stated so it can be checked.
- Someone must decide whether to wait or commit and needs early indicators to time it.
- A scenario exercise picked a likely future and the trajectory now needs tracking.

Do NOT invoke when:

- The question branches — "what could happen over the next decade?" — use `scenario-planning`; this skill produces one line, not a matrix.
- The task is a standing sweep for many emerging issues — use `horizon-scanning`; it feeds this skill.
- The estimate should come from an expert panel rather than one reasoner — use `delphi-method`.
- The base rate of similar past cases is the real evidence — use `reference-class-forecasting` first.
- The prediction has already resolved and the question is accuracy — use `brier-score-calibration`.
- The claim is about the present rather than timing — use `apply-hype-cycle` or `position-competitor`.

## Procedure

### 1 — Name the prediction

Write one sentence with four parts: subject, verb, dated milestone, confidence. "Open-weight 70B-class models will run on sub-$5,000 consumer hardware by 2027-06-30 (confidence 0.7)" qualifies; "open-weight models will keep improving" does not. The date must be absolute — never "soon" or "eventually" — and the confidence a number; keep the probability wording consistent with `estimative-language`. If the sentence cannot be written, the question is not ripe: say so and stop.

### 2 — List three accelerants with lead times

Three forces that would make the milestone arrive earlier or become more likely. Each must be observable — "a GPU vendor ships a sub-$2,000 SKU with 48 GB of memory", not "the market matures". Record for each the lead time: how many months before the milestone the indicator would appear. That is the early-warning window a decision can be timed against.

### 3 — List three blockers with lead times

Three forces that would push the milestone later or make it less likely, symmetric to the accelerants: concrete, observable, each with a lead time. The purpose is not to predict which happens but to complete the watchlist. If the prediction still feels obvious here, the blockers have not been taken seriously.

### 4 — Commit to three weak signals to watch now

A weak signal is an observation available today that would move the confidence if it changed and that few people track yet — Ansoff's point that strategic surprise is preceded by information too faint for the usual filters. Name each specifically (a benchmark crossing a threshold, a company shipping a capability, a regulatory change, a hiring shift) and where it would be observed. "Sentiment shifts" is not a weak signal; grade each source with `rate-source-admiralty`.

### 5 — Commit to three kill-signals

A kill-signal is a specific, observable event that would make the prediction retractable, not merely weakened: a named event with a public trace, sufficient on its own. "If the market does not grow" is a vibe; "a leading GPU vendor publishes a roadmap with no consumer part above 32 GB through 2028" is a kill-signal. If three cannot be written, the confidence is not above 0.5 — lower it or withdraw it.

### 6 — Set the review horizon and confidence

Pick one review date: half the time to the milestone, or just after the next event expected to produce a weak signal, whichever is sooner. Then set the confidence: **0.7–0.9** when two independent lines of evidence point at the date, **0.5–0.7** on one strong line (mark it `directional`), **below 0.5** not publishable as a prediction — write it as an open question. Full bands: [references/confidence-bands.md](references/confidence-bands.md).

## Output template

```
Prediction: {subject} {verb} {dated milestone, absolute date} (confidence: 0.{nn}{, directional})

Accelerants:
- {observable event} (lead time: {n}m)
- {observable event} (lead time: {n}m)
- {observable event} (lead time: {n}m)

Blockers:
- {observable event} (lead time: {n}m)
- {observable event} (lead time: {n}m)
- {observable event} (lead time: {n}m)

Weak signals to watch now:
- {specific observation} → observed at {named source}
- {specific observation} → observed at {named source}
- {specific observation} → observed at {named source}

Kill-signals (if observed, retract):
- {named event with a public trace}
- {named event with a public trace}
- {named event with a public trace}

Review: {YYYY-MM-DD} — {what to look for on that date}
```

Every field is mandatory and the labels are kept verbatim so the block can be parsed and scored later. A prediction without kill-signals and a review date is an opinion, not a forecast.

## Worked example

Illustrative fill (all figures illustrative) for the question *will on-device inference displace cloud APIs for enterprise document summarisation?*

```
Prediction: On-device small models handle >50% of new enterprise document-summarisation
deployments by 2027-06-30 (confidence: 0.65, directional)

Accelerants:
- NPU-equipped laptops become the default enterprise fleet refresh (lead time: 18m)
- Cloud per-token prices stay flat while 7–13B models reach summarisation parity (lead time: 12m)
- Data-residency rules push regulated sectors to local processing (lead time: 24m)

Blockers:
- Fleet refresh cycles lag hardware availability by 2–3 years (lead time: 30m)
- Enterprise IT lacks tooling to update local models at scale (lead time: 18m)
- Cloud vendors bundle summarisation into existing suites at near-zero price (lead time: 12m)

Weak signals to watch now:
- Public-sector laptop tenders specifying an NPU minimum → observed at national procurement portals
- Offline-first summarisation shipping in a productivity suite beta → observed at vendor release notes
- Edge-ML operations roles opening at large enterprises → observed at company careers pages

Kill-signals (if observed, retract):
- Cloud summarisation prices fall more than 50% while the quality gap widens
- A named Fortune 500 on-device deployment is publicly rolled back for quality or manageability
- NPU penetration of enterprise fleets stays below 20% through 2026

Review: 2026-12-31 — check NPU share of new enterprise fleet purchases and whether Microsoft,
Google or Salesforce has made summarisation free inside an existing suite
```

Confidence is 0.65, not 0.8: one line of evidence — the hardware refresh plus quality parity — points at the date while the bundling blocker could delay it a year. The review sits at half the 18-month horizon; `brier-score-calibration` scores the call once 2027-06-30 passes.

## Verification

Before the prediction ships, confirm:

- [ ] The prediction sentence carries an absolute date and a numeric confidence matching the band it claims.
- [ ] Every accelerant and blocker is an observable event with a lead time in months — no "the market matures".
- [ ] Each weak signal names where it would be observed, and each source has been graded.
- [ ] Each kill-signal is specific, publicly observable and sufficient alone — check by asking whether the prediction would really be withdrawn if it occurred.
- [ ] The review date is no later than half the time to the milestone and says what to look for.
- [ ] The prediction is recorded so it can be scored after it resolves.

## Pair with adjacent skills

- `horizon-scanning` — the standing sweep that surfaces the signals this prediction watches.
- `scenario-planning` — when the question branches; a chosen scenario can then be tracked here.
- `brier-score-calibration` — scores the dated prediction once the outcome is known.
- `indicators-validation` — tests whether the indicators are diagnostic, not merely plausible.
- `estimative-language` — keeps the probability wording and the numeric confidence consistent.
- `reference-class-forecasting` — supplies the base rate before the confidence is set.

## Anti-patterns

- Do **not** publish an undated prediction; "within a few years" is not a date.
- Do **not** write kill-signals that cannot fire ("if adoption disappoints"). A kill-signal names an event.
- Do **not** list accelerants without lead times — the watchlist is then useless for timing.
- Do **not** recycle general trends as weak signals; "more enterprise adoption" is not an indicator.
- Do **not** claim above 0.7 on one line of evidence, and do **not** publish below 0.5 at all.

## Reference

- H. I. Ansoff, "Managing Strategic Surprise by Response to Weak Signals," *California Management Review*, vol. 18, no. 2, pp. 21–33, 1975. doi:10.2307/41164635 — the weak-signal concept and graduated response.
- E. Hiltunen, "The future sign and its three dimensions," *Futures*, vol. 40, no. 3, pp. 247–260, 2008. doi:10.1016/j.futures.2007.08.021 — signal, issue and interpretation as the three dimensions of a future sign.
- P. E. Tetlock and D. Gardner, *Superforecasting: The Art and Science of Prediction*. New York: Crown, 2015. ISBN 978-0-8041-3669-3 — dated, probabilistic, scoreable forecasts.
- G. W. Brier, "Verification of forecasts expressed in terms of probability," *Monthly Weather Review*, vol. 78, no. 1, pp. 1–3, 1950. doi:10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2 — the scoring rule that makes a dated prediction worth recording.
