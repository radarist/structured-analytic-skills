---
name: cheapest-experiment
description: "Turns a recommendation into its cheapest decisive test — the smallest bounded pilot, its cost and duration, a pass/fail rule fixed before the run, and what each outcome would change — in the spirit of Ries's Lean Startup build-measure-learn loop and MVP. Use when a brief ends in recommendations or a bet is about to be funded — \"should this be piloted before committing?\", \"what is the cheapest experiment that would validate this bet?\", \"design an MVP test with a go/no-go rule\", \"how can this recommendation be de-risked?\". Not for powered trials needing sample size — use `experimental-design`; not for enumerating how a chosen plan fails — use `premortem-analysis`."
license: MIT
metadata:
  category: decision-strategy
  method: Cheapest decisive experiment (minimum viable test with a pre-committed decision rule)
  origin: Eric Ries, The Lean Startup, 2011 (build-measure-learn, MVP, innovation accounting); antecedent — Steve Blank, customer development, 2005
  version: "2.0.0"
---
# Cheapest Experiment

Every recommendation is a bet, and most bets can be tested for a fraction of what committing to them costs. This skill attaches to each recommendation the smallest test whose result would change the decision, its cost and duration, and a pass/fail rule written **before** the test runs. The discipline comes from Eric Ries's *The Lean Startup* (2011) — the build-measure-learn loop, the minimum viable product and innovation accounting — which in turn builds on Steve Blank's customer development (2005). The failure it prevents is escalation of commitment: a "pilot" with no thresholds always reads as a success, so the organisation funds the full bet on evidence that never tested anything.

## When to invoke

Invoke when:

- A brief ends in recommendations, next steps, investment options or a go/no-go: "should this be piloted?", "what would validate this?", "how is this de-risked?".
- A large, reversible commitment is about to be funded and no one has named what would falsify the case for it.
- A premortem has surfaced failure modes and each one needs a cheap early-warning test.
- A dated prediction is load-bearing but uncertain — a bounded probe reduces the uncertainty before the bigger commitment.

Do NOT invoke when:

- The test needs statistical power, a randomisation unit and preregistration — use `experimental-design`; this skill designs the bounded check that precedes a powered trial.
- The answer is already in the literature — use `systematic-review` for a large evidence base, or `triangulate-sources` for a handful of conflicting claims.
- No cheap test exists because the bet cannot be bounded below full commitment — a token pilot is theatre; run `premortem-analysis` on the failure modes instead.
- The decision is irreversible: framing a one-way door as an experiment is dishonest. Route the decision to `decision-matrix-mcda` or `premortem-analysis`.
- The brief is purely descriptive, with no recommendation to test.

## Procedure

### 1 — State the recommendation in one sentence

Subject, verb, object, scope — no preamble and no hedging. "Pilot the Eightfold talent platform for engineering requisitions in the Frankfurt office in Q3 2026" is a recommendation; "we should consider exploring potential AI tools for talent strategy" is five hedge words and no commitment. If the recommendation cannot be written in one sentence, the bet is not yet clear enough to test — clarify it first, then return.

### 2 — Name the smallest test that would change the decision

Smallest means the cheapest test whose *negative* result would stop the commitment — not the smallest test technically possible. The test must be bounded (N requisitions, N customers, N sites, N weeks), executable today with no "after a new hire" precondition, and independent of the full commitment so that failing costs only the test. "Run a thorough internal evaluation" has no scope, no timebox and no mechanism; "eight weeks on fifty requisitions in one office, stopping short of automated offers" does.

### 3 — Price it and time it

Give both numbers with units: cost as an all-in range (vendor fees, internal time, opportunity cost) and duration in weeks or months from kickoff to the decision moment, including readout. Without them, the reader cannot compare this experiment against the next one. If the cost is genuinely unknown, the smallest test is a two-week scoping spike that prices the pilot — not the pilot itself. Mark reasoned figures `(estimate)` and sourced figures with their source.

### 4 — Fix the decision rule before the run

Write both branches with metrics and thresholds: *pass if {metric} {comparator} {threshold} AND …; fail if either misses.* Thresholds are the lower bound of the conviction case, not a stretch goal — if a 15 % improvement would justify the commitment, write 15 %, not 25 %. A rule such as "pass if it works" is escalation in disguise: without a number, whatever happens gets rationalised as success. The rule is agreed and recorded before data collection starts.

### 5 — State what each outcome would change

One sentence naming the asymmetry: what a pass triggers, what a fail triggers, and what is saved by learning early. If both branches lead to the same next action, the experiment is not worth running — pick a different test or admit the decision has already been made.

## Output template

```
Recommendation: {subject + verb + object + scope, one sentence}
Smallest test: {bounded scope, executable today, independent of the full commitment}
Cost: ${low}–${high} all-in {(estimate) | source}. Duration: {N} weeks to the decision moment.
Decision rule: pass if {metric} {comparator} {threshold} AND {metric} {comparator} {threshold}; fail if either misses.
What each outcome changes: pass → {next action}; fail → {next action, and what is saved}.
```

One block per recommendation. All five fields are mandatory — a block without numeric thresholds in the decision rule, or without both cost and duration, must not ship.

## Worked example

Illustrative case (figures illustrative). Helios Semiconductor is considering a $4.2M global rollout of the Eightfold talent platform after a vendor demo. The brief's recommendation is turned into a bounded test:

```
Recommendation: Roll out Eightfold Talent Intelligence to all 12 Helios engineering sites in 2027.
Smallest test: 8-week pilot on 50 engineering requisitions in the Frankfurt office; the tool ranks
  internal candidates only and stops before offer generation; recruiters log every override.
Cost: $95,000–$130,000 all-in (estimate: $60,000 vendor pilot fee, 0.5 FTE recruiter time for 10
  weeks, $15,000 bias-audit review). Duration: 10 weeks (8 pilot + 2 readout).
Decision rule: pass if median time-to-shortlist falls from 19 days to ≤ 14 days AND hiring-manager
  satisfaction ≥ 3.5/5 AND the bias audit returns zero adverse-impact findings; fail if any misses.
What each outcome changes: pass → fund the 12-site rollout at $4.2M; fail → stop, keep the agency
  contract, and save the $4.2M commitment for the cost of a $130,000 pilot.
```

| Field | Value | Check |
| --- | --- | --- |
| Test cost as share of the bet | $130,000 / $4,200,000 = 3.1 % | bounded well below the commitment |
| Pass threshold | ≤ 14 days (from 19) | lower bound of conviction, not a stretch target |
| Duration to decision | 10 weeks | decision moment dated, not open-ended |
| Outcome asymmetry | rollout vs stop | branches diverge, so the test is worth running |

The 26 % improvement demanded of time-to-shortlist is what the business case assumed; setting the bar at 40 % would have guaranteed a "fail" no one would honour.

## Verification

Before the experiment block ships, confirm:

- [ ] The recommendation is one sentence with a named subject, verb, object and scope.
- [ ] The test is bounded by explicit numbers (units, sites, weeks) and could start this week.
- [ ] Cost and duration are both present with units, and any unsourced figure carries `(estimate)`.
- [ ] The decision rule names a metric, a comparator and a numeric threshold on both branches — recompute the test cost as a share of the full commitment and confirm it is materially smaller.
- [ ] The pass and fail branches lead to different next actions; if they do not, the test is dropped.
- [ ] The thresholds match the business case's own assumptions rather than a stretch goal.

## Pair with adjacent skills

- `premortem-analysis` — enumerate failure modes first, then design the cheapest test that would surface each one early.
- `experimental-design` — hand over when the check needs power, randomisation and preregistration.
- `red-team-claim` — attack the decision rule: would a hostile reviewer call these thresholds rigged?
- `triangulate-sources` — cross-check single-source pilot quotes; vendor cost estimates routinely miss by 2–3×.
- `foresight` — when the bet depends on a dated milestone, the experiment becomes the in-flight check on that prediction.
- `jtbd-framing` — confirm the test measures the job the option is hired for, not merely whether it ships.

## Anti-patterns

- Do **not** accept a pilot without scope: "run a pilot" is not a design; "50 requisitions, one office, eight weeks" is.
- Do **not** ship a rule without thresholds — "pass if it works" guarantees an escalating commitment.
- Do **not** design symmetric outcomes; if pass and fail lead to the same action, the test buys nothing.
- Do **not** leave cost unknown. When the number is unavailable, the smallest test is a scoping spike that produces it.
- Do **not** set stretch-goal thresholds; an unreachable bar produces a "fail" verdict that will be overruled.
- Do **not** design a test that can only confirm. If no plausible result would stop the commitment, this is not an experiment.

## Reference

- E. Ries, *The Lean Startup: How Today's Entrepreneurs Use Continuous Innovation to Create Radically Successful Businesses*. New York: Crown Business, 2011. ISBN 978-0-307-88789-4 — build-measure-learn, minimum viable product, validated learning and innovation accounting.
- S. G. Blank, *The Four Steps to the Epiphany: Successful Strategies for Products That Win*, first published 2005; 3rd ed., Pescadero, CA: S. G. Blank, 2007. ISBN 978-0-9764707-0-0 — customer development, the antecedent Ries adapted.
- P. E. Tetlock and D. Gardner, *Superforecasting: The Art and Science of Prediction*. New York: Crown, 2015. ISBN 978-0-8041-3669-3 — why thresholds must be fixed before the outcome is known.
