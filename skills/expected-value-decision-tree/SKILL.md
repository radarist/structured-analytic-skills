---
name: expected-value-decision-tree
description: "Lays out a staged bet as a decision tree, rolls it back to expected values and prices the information a pilot or test would buy — expected value of perfect information (EVPI), expected value of sample information (EVSI) and a one-way sensitivity (tornado) with switching probabilities (Raiffa 1968). Use when a go/no-go, invest/wait or pilot-then-commit choice hinges on chance outcomes — \"is the pilot worth running before committing?\", \"expected value of perfect information\", \"which uncertainty is the decision most sensitive to?\", \"build the decision tree\". Not for designing the experiment itself (`cheapest-experiment`) or revising one probability (`bayesian-update`)."
license: MIT
metadata:
  category: decision-strategy
  method: Decision tree analysis — expected-value roll-back, EVPI/EVSI, one-way sensitivity (tornado)
  origin: Howard Raiffa, Decision Analysis (1968); Ronald A. Howard, decision analysis (1966, 1968)
  version: "2.0.0"
---
# Expected-Value Decision Tree

A decision tree draws a staged choice as decision nodes (options, costs), chance nodes (exclusive outcomes, probabilities) and terminal payoffs, then **rolls back** from the leaves: a chance node is worth its probability-weighted average, a decision node its best branch. Raiffa (1968) and Howard (1966, 1968) built decision analysis on it; its distinctive product is the **value of information** — what a perfect forecast (EVPI) or an imperfect pilot (EVSI) adds — which experiments deserve money before the big commitment.

## When to invoke

Invoke when:

- A staged R&D or investment bet has a go/no-go with an option to pilot, test or wait — "should we run the $2M pilot before committing $20M?".
- Someone asks for each option's expected value, the value of perfect or sample information, or "which uncertainty is my decision most sensitive to?".

Do NOT invoke when:

- Designing the pilot itself (scope, cost, duration, pass/fail rule) — `cheapest-experiment`; this skill prices a test, that one designs it.
- One probability needs revising on new evidence — `bayesian-update`.
- Options are ranked on several criteria with no material chance node — `decision-matrix-mcda`.
- The probabilities are unknown — elicit them with `delphi-method` or `foresight` first.
- One option, or no outcome would change the choice — nothing to roll back; run `premortem-analysis` instead.

## Procedure

### 1 — Frame the decision

Name the decision-maker, horizon and options in time order: commit, do nothing, wait, pilot then decide. Fix one payoff basis for the whole tree — NPV at a stated discount rate, or utility if a branch is bet-the-company — and state the risk attitude: expected value assumes risk neutrality, right for repeated bets, wrong for one ruinous bet.

### 2 — Lay out the chance nodes

List mutually exclusive, exhaustive outcomes per uncertainty with probabilities that sum to 1 and come from somewhere — base rates, expert elicitation, a Bayes update on a test. Name one uncertainty identically wherever it appears. A pilot's branch probabilities are posteriors: write the likelihood matrix P(signal | outcome) explicitly so the tree can be checked against Bayes.

### 3 — Attach payoffs and costs

Terminal payoffs on the single basis from step 1; each cost on the branch that incurs it (pilot on the pilot branch, development on the commit branch); sunk costs nowhere. Soft inputs get a `{min, mode, max}` range for the sensitivity and Monte Carlo steps.

### 4 — Roll back

Chance node = Σ p × (EV of child − branch cost); decision node = best branch. Record every node's EV, the optimal policy (root choice plus each contingent choice) and its risk profile — the distribution of net outcomes, including the probability of a loss. `scripts/dtree.py solve` does this.

### 5 — Price the information

EVPI = EV with perfect information − best EV: fix every node of the uncertainty at each outcome, re-optimise, weight by the prior. EVSI turns a test's likelihood matrix into posteriors and repeats the re-optimisation; EVSI ≤ EVPI. Run a test only when EVSI exceeds its cost; EVSI ≈ 0 means it cannot change the decision. Hand worthwhile tests to `cheapest-experiment`.

### 6 — One-way sensitivity

Move every probability, payoff and cost ±20 % with the others at base, rank by swing (the tornado) and find the switching points — the input value at which the recommended branch changes. The top inputs are where estimation effort and the next test go. If several inputs are soft, run the Monte Carlo over their ranges: P10/P50/P90 of the EV and how often the choice stays optimal.

### 7 — Report

Fill the template: recommended policy, EVs, risk profile, value of information with a run/skip verdict per test, sensitivity, assumptions.

## Output template

```
## Decision tree — {decision}
**Options:** {A} | {B} | {do nothing / wait} — payoffs in {units, basis}; risk attitude {neutral | utility}
**Recommended policy:** {root choice}; if {signal 1} → {choice}; if {signal 2} → {choice}
**Expected values:** {A} {EV} · {B} {EV} · {C} {EV} → best {EV}
**Risk profile:** P(loss) {p}; worst {v} (p = {p}); best {v} (p = {p})
**Value of information:** EVPI({uncertainty}) = {x}; EVSI({test}) = {x} vs cost {c} → {run | skip}
**Sensitivity:** most sensitive input {key} (swing {x}); switches if {input} {< | >} {value}
**Assumptions:** {probability sources; payoff basis; costs excluded}
**Next step:** {test handed to cheapest-experiment | commit | wait}
```

Every line is mandatory.

## Worked example

Decision: commit USD 20M to full development now, do nothing, or run a USD 2M pilot first. Demand is High with prior 0.4 (payoff 60) or Low (payoff 5), USD M NPV. The pilot reads demand imperfectly — P(Positive | High) = 0.9, P(Positive | Low) = 0.4 — so P(Positive) = 0.6, P(High | Positive) = 0.6, P(High | Negative) = 0.1. `python3 scripts/dtree.py solve --demo` (`examples/rd-pilot.json`; sub-trees elided):

```
[D] Go / no-go   EV = 8.80   choose: Pilot first
  - Commit now  [cost 20.00]  EV = 7.00
  - Do nothing  [payoff 0.00]  EV = 0.00
  * Pilot first  [cost 2.00]  EV = 8.80
    [C] Pilot result   EV = 10.80
      - Positive  [p=0.600]  EV = 18.00
        [D] After positive pilot   EV = 18.00   choose: Commit
      - Negative  [p=0.400]  EV = 0.00
        [D] After negative pilot   EV = 0.00   choose: Stop
```

The pilot policy loses money 64 % of the time (−2 after a negative pilot, −17 after a false positive) and pays +38 with probability 0.36. `evpi --demo`: EVPI(Demand) = 16.00 − 8.80 = 7.20. `evpi --demo --evsi --drop "Pilot first"` prices the pilot as a signal on the base decision and reproduces the hand-built branch: best EV without it 7.00 (Commit now), EVPI 9.00, EVSI = 10.80 − 7.00 = 3.80, cost 2.00, net 1.80 → run (7.00 + 1.80 = 8.80). `sensitivity --demo`: the High payoff swings the EV most (48 → 72 moves it 4.48 → 13.12); the choice switches to Commit now if P(High) > 0.4327 or P(Positive) < 0.5000; the pilot breaks even at cost 3.80. `montecarlo --demo --draws 10000 --seed 42`: P10 5.44 / P50 8.89 / P90 12.72, pilot optimal in 95.7 % of draws.

## Verification

- [ ] Every chance node's probabilities sum to 1 (the tool rejects the file otherwise); outcomes exhaustive.
- [ ] One payoff basis and unit; each cost once, on the branch that incurs it; no sunk costs.
- [ ] EVs recomputed with `scripts/dtree.py solve` match the report; the risk profile's mean equals the root EV.
- [ ] EVPI ≥ 0 and EVSI ≤ EVPI — a negative value means Bayes-inconsistent probabilities across branches; fix the tree.
- [ ] Sensitivity done: top inputs and the recommendation's switching point stated.
- [ ] Risk attitude addressed when the worst branch is material.

## Companion tool

`scripts/dtree.py` (stdlib only): `solve` (roll-back, policy, risk profile), `evpi` (`--evsi --likelihood` for an imperfect signal; `--all` per uncertainty), `sensitivity` (±20 % tornado with switching points; `--param KEY --range a:b:steps`), `montecarlo --draws N --seed S` over `{min, mode, max}` ranges; `--json`, `--demo`. `--selftest` checks the oil-wildcatter textbook tree (EV, EVPI, EVSI, switching probability) by hand.

```bash
python3 scripts/dtree.py solve --file tree.json
python3 scripts/dtree.py evpi --file tree.json --evsi --likelihood signal.json --drop "Pilot first"
python3 scripts/dtree.py montecarlo --file tree.json --draws 10000 --seed 42
```

Usable without it — roll back by hand — but EVSI and the tornado are error-prone by hand.

## Pair with adjacent skills

- `cheapest-experiment` — receives every test whose EVSI exceeds its cost and designs it.
- `bayesian-update` — the arithmetic behind a pilot's posteriors and likelihood matrix.
- `premortem-analysis` — on the recommended branch.
- `scenario-planning` — when uncertainties are too coupled to be independent chance nodes.
- `estimate-market-size` — payoffs for the market-outcome branches.
- `decision-matrix-mcda` — the multi-criteria sibling when no chance node dominates.
- `delphi-method` / `foresight` — sources for the probabilities.

## Anti-patterns

- Do **not** let a chance node's probabilities sum to anything but 1, or leave out an outcome.
- Do **not** mix bases — revenue on one leaf, NPV on another; gross here, net there.
- Do **not** report a risk-neutral EV for a bet-the-company branch without the risk profile or a utility view.
- Do **not** treat the EV as a forecast: 8.8 never happens; the outcomes are +38, −2 or −17.
- Do **not** build a tree for a one-option decision, or run a pilot whose EVSI is below its cost — theatre.
- Do **not** give one uncertainty un-Bayesed probabilities in different subtrees — negative EVPI is the tool telling you so.

## Reference

- H. Raiffa, *Decision Analysis: Introductory Lectures on Choices under Uncertainty*. Reading, MA: Addison-Wesley, 1968. ISBN 0-201-06290-9. https://archive.org/details/decisionanalysis0000raif
- R. A. Howard, "Decision Analysis: Applied Decision Theory," in D. B. Hertz and J. Melese (eds.), *Proceedings of the Fourth International Conference on Operational Research*. New York: Wiley-Interscience, 1966, pp. 55–71.
- R. A. Howard, "The Foundations of Decision Analysis," *IEEE Transactions on Systems Science and Cybernetics*, vol. SSC-4, no. 3, pp. 211–219, 1968. https://doi.org/10.1109/TSSC.1968.300115
- R. T. Clemen and T. Reilly, *Making Hard Decisions with DecisionTools*, 3rd ed. Mason, OH: South-Western / Cengage Learning, 2014. ISBN 978-0-538-79757-3 — ch. 5 (tornado diagrams), ch. 12 (value of information).
- D. W. Hubbard, *How to Measure Anything: Finding the Value of Intangibles in Business*, 3rd ed. Hoboken, NJ: Wiley, 2014. ISBN 978-1-118-53927-9 — ch. 7.
- J. S. Hammond, R. L. Keeney and H. Raiffa, *Smart Choices: A Practical Guide to Making Better Decisions*. Boston, MA: Harvard Business School Press, 1999. ISBN 978-0-87584-857-0.
