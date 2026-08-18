---
name: experimental-design
description: "Produces a preregisterable design card for a causal test before any data are collected — a falsifiable hypothesis with a minimum detectable effect, the randomization unit and mechanism, a power-based sample size per arm, a fixed stop rule and analysis plan, and an audit of the validity threats that survive randomization. Use when a test is being planned: \"design an A/B test\", \"how many users per arm are needed?\", \"run a power analysis\", \"preregister this experiment\", \"is this study design sound?\". Not for analysing a comparison whose data already exist (use `test-significance`) or for grading someone else's finished trial (use `assess-study-bias`)."
license: MIT
metadata:
  category: quantitative
  method: Randomized experimental design with a priori power analysis and validity audit
  origin: R. A. Fisher, 1935; D. T. Campbell & J. C. Stanley, 1963; J. Cohen, 1988
  version: "2.0.0"
---
# Experimental Design

A randomized experiment answers "does X cause Y?" rather than gesturing at it — but only when the commitments are fixed before the data arrive. Randomization does the controlling: it equalises the arms in expectation on every confounder, named and unnamed, leaving the manipulation as the only systematic difference (Fisher, *The Design of Experiments*, 1935). The rest is craft: a minimum detectable effect chosen from decision stakes, enough units to detect it, a stop rule and analysis plan written in advance, and an audit of the threats randomization does not remove (Campbell & Stanley, 1963). It prevents the two experiments that produce confident nonsense: the underpowered one reporting noise as a finding, and the peeked-at one stopped the moment p dipped below .05.

## When to invoke

Invoke when:

- A causal claim is about to be tested: "does the new {feature, model, prompt} cause the improvement?", "design an A/B test", "should we roll out X?".
- Sizing or feasibility is the question: "how many users per arm?", "run a power analysis".
- A design needs review before launch: "preregister this study", "is this design sound?".

Do NOT invoke when:

- The data are collected and the question is whether the gap is real — `test-significance`.
- The study is someone else's finished trial and its risk of bias is the question — `assess-study-bias`.
- Manipulation is impossible or unethical — use a quasi-experimental design (difference-in-differences, regression discontinuity, interrupted time series) from the methodology counterpart, labelled honestly.
- A much cheaper test could settle the decision — `cheapest-experiment` triages that first.
- No causal question exists; "what happened?" needs reporting, not an experiment.

## Procedure

### 1 — State the hypothesis and the minimum detectable effect

Write one falsifiable prediction with exactly one primary metric: "changing X causes Y to move by at least δ". Choose δ — the minimum detectable effect — from decision stakes, the smallest effect that would change what anyone does, and sanity-check it against prior evidence rather than affordability. Everything else is secondary or a guardrail, labelled now, not after the results are in.

### 2 — Choose the design, the unit, and the randomization mechanism

Pick between-subjects (the A/B default), within-subjects (more powerful, needs counterbalancing), factorial (estimates interactions) or cluster-randomized (effective n is the cluster count). Name the randomization unit — it must be independent, so users rather than page views — and record the mechanism (salted hash, seeded RNG), stratification and blinding. Options and costs: [references/power-and-validity.md](references/power-and-validity.md).

### 3 — Run the power analysis

Compute n per arm for δ at α = .05 two-sided and power ≥ .80, using the pooled normal approximation for proportions (Fleiss, Levin & Paik, 2003) or Cohen's (1988) formulas for means; `scripts/power.py` implements both. Fix the multiple-comparison rule now: k metrics or variants means a per-test α of α/k. If the required n is infeasible, say so before launching — accept a larger δ, get more units, or drop the causal claim.

### 4 — Preregister

Timestamp, before any data arrive: hypothesis, primary metric, δ, n per arm, α and power, the randomization mechanism, exclusions, the analysis plan per metric, guardrails and the stop rule — fixed horizon with no peeking, or a named sequential method. A dated file or commit hash suffices; preregistration turns later flexibility into a visible diff rather than an invisible degree of freedom.

### 5 — Run, log, and check the plumbing

Randomize by the documented mechanism and log allocation counts per arm, attrition by arm, protocol deviations and any manipulation check. On new bucketing infrastructure run an A/A test first: a biased assignment function manufactures lift from nothing, and only an A/A test catches it before the real experiment inherits it.

### 6 — Analyse exactly as preregistered

Run the preregistered analysis on the full fixed-horizon sample and hand the comparison to `test-significance` for the p-value, the interval and the effect size. Report the interval against δ, not only against zero: a significant lift whose interval reaches below δ has not met the decision threshold. Anything outside the plan is exploratory — a hypothesis for the next experiment.

### 7 — Audit the four validities

Name each surviving threat with its likely direction of bias. **Internal:** differential attrition, noncompliance, cross-arm contamination. **Statistical conclusion:** power, multiple comparisons, test assumptions. **Construct:** did the manipulation produce the intended state, and does the metric measure the construct or a proxy? **External:** novelty effects and whether the result generalises beyond these users and this period.

## Output template

```
## Experiment design card — {question}

**Hypothesis:** {changing X causes ≥ δ movement in primary metric Y}
**Primary metric:** {one}   **Secondary / guardrail:** {list}
**MDE (δ):** {absolute and relative; rationale from decision stakes + prior evidence}

**Design:** {between | within | factorial | cluster}   **Unit:** {user | session | cluster}
**Randomization:** {mechanism; stratification; blinding}
**Power:** alpha = {0.05, two-sided}, power = {0.80} → **n = {N} per arm ({2N} total)**
**Stop rule:** {fixed horizon, no peeking | named sequential method}
**Multiple comparisons:** {k tests → per-test alpha = alpha/k}   **Exclusions:** {rules}
**Analysis plan:** {test per metric → `test-significance`; CI and effect size, not p alone}
**Preregistered:** {timestamp / commit}   **A/A check:** {done | scheduled | n/a}

**Surviving validity threats:** {threat → likely direction of bias}
```

Mandatory: the MDE with its rationale, the randomization unit and mechanism, n per arm with α and power, the stop rule and the validity-threat list. A card without a stop rule is not preregisterable.

## Worked example (illustrative)

Does one-click checkout raise purchase conversion? All figures are illustrative.

- **Hypothesis and MDE:** one-click checkout raises 7-day conversion from a 10 % baseline by at least +2 pp (a 20 % relative lift); below that the engineering cost is not recovered.
- **Design:** between-subjects A/B; unit = user ID, not session; 50/50 by salted hash, stratified by new versus returning; the metric is behavioural, so no blinding.
- **Power:** `python3 scripts/power.py n-props --p1 0.10 --p2 0.12` gives

```
Two independent proportions  [pooled-variance normal approximation]
  p1 = 0.1, p2 = 0.12: MDE +0.02 absolute (+20.0% relative), Cohen's h = 0.064
  alpha = 0.05 two-sided, power = 0.8, ratio n2/n1 = 1
  n per group: 3841  (total 7682)   unrounded 3840.85
  achieved power at these n: 0.8000
```

  — **3,841 users per arm, 7,682 total.** At ~12,000 eligible users a week one week suffices arithmetically; the design runs two full weeks to cover the weekday cycle. Fixed horizon, no peeking.
- **Preregistered:** 2025-05-03, commit `a1b2c3d` — primary metric 7-day purchase conversion; guardrails refund rate and page latency; exclusions internal accounts and a bot user-agent list.
- **Analysis handoff:** control 376/3,841 (9.79 %) versus treatment 457/3,841 (11.90 %) → `test-significance` returns z = 2.972, p = 0.0030, 95 % CI [+0.72 pp, +3.50 pp], Cohen's h = 0.068. The interval includes values below +2 pp, so the honest report is "lift confirmed, decision threshold only partially met".
- **Validity audit:** novelty effect (upward bias early — check a week-2-only cut); shared-device crossover (minor; intention-to-treat holds); construct — conversion counts real purchases, the refund guardrail catching buyer's remorse.

## Verification

Before the design card ships, confirm:

- [ ] The MDE came from decision stakes and prior evidence, not from the available sample.
- [ ] Recompute n with `python3 scripts/power.py n-props --p1 0.10 --p2 0.12` (or the matching subcommand) and check n per group and achieved power against the card.
- [ ] The randomization unit is the unit that experiences the treatment, and the mechanism is reproducible.
- [ ] The stop rule is a fixed horizon or a named sequential method, decided before launch.
- [ ] The multiple-comparison rule covers every metric and variant to be tested.
- [ ] The analysis plan names the test per metric and requires a CI and effect size, not a bare p.
- [ ] All four validities were walked and each surviving threat carries a direction of bias.

## Companion tool

`scripts/power.py` (stdlib only, deterministic) computes step 3 and its inverses: `n-means`, `n-props`, `n-one-mean`, `n-paired`, `n-corr` for sample size; `power` for achieved power at a given n; `mde` for the detectable effect at a given n; `duration` for run length from daily eligible traffic. It implements Cohen (1988) normal approximations (`--t-correct` adds t quantiles) and the Fleiss, Levin & Paik (2003) pooled two-proportion formula (`--continuity`).

```bash
python3 scripts/power.py n-props --p1 0.10 --p2 0.12      # 3841 per group, 7682 total
python3 scripts/power.py n-means --d 0.5 --t-correct      # 64 per group (Cohen 1992, Table 2)
python3 scripts/power.py mde props --p1 0.10 --n 5000     # +0.0174 absolute at n = 5,000
python3 scripts/power.py --selftest                       # 56 checks against published values
```

`--json` gives machine output and `--demo` reproduces the worked example. Any power calculator fills step 3; the tool keeps the arithmetic reproducible and pinned to published tables.

## Pair with adjacent skills

- `test-significance` — the downstream sibling: this skill fixes the MDE, n and plan; that one analyses the result.
- `cheapest-experiment` — upstream triage: whether a fully powered experiment is warranted.
- `assess-study-bias` — extends the step-7 validity audit to trials designed by someone else.
- `meta-analysis` — where a series of such experiments is eventually pooled.
- `premortem-analysis` — how the rollout the experiment justifies could still fail.
- Methodology counterpart: [methodologies/research-methods/experimental-design.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/research-methods/experimental-design.md) — the quasi-experimental family (DiD, RDD, ITS), the four-validities framework and historical cases.

## Anti-patterns

- Do **not** peek. Daily checking with a stop at p < .05 inflates false positives severalfold (Kohavi, Tang & Xu, 2020); fix the horizon or name a sequential method.
- Do **not** size from the budget. "We have 500 users" is a constraint; run the MDE-given-n direction.
- Do **not** randomize the wrong unit — page views when users repeat breaks independence.
- Do **not** add metrics, subgroups or exclusions after seeing the data; post-hoc findings are exploratory.
- Do **not** read a non-significant underpowered result as "no effect", or report p without the interval.
- Do **not** skip the A/A test on new bucketing infrastructure.
- Do **not** generalise past the design — a two-week window on self-selected users bounds the claim.

## Reference

- R. A. Fisher, *The Design of Experiments*. Edinburgh: Oliver & Boyd, 1935 — randomization, blocking, factorial designs.
- D. T. Campbell and J. C. Stanley, *Experimental and Quasi-Experimental Designs for Research*. Chicago: Rand McNally, 1963 — the validity-threat framework; extended in W. R. Shadish, T. D. Cook and D. T. Campbell, *Experimental and Quasi-Experimental Designs for Generalized Causal Inference*, Houghton Mifflin, 2002. ISBN 978-0-395-61556-0
- J. Cohen, *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Lawrence Erlbaum, 1988; and "A power primer," *Psychological Bulletin*, vol. 112, no. 1, pp. 155–159, 1992. doi:10.1037/0033-2909.112.1.155
- J. L. Fleiss, B. Levin, and M. C. Paik, *Statistical Methods for Rates and Proportions*, 3rd ed. Wiley, 2003. doi:10.1002/0471445428 — the two-proportion formula the tool uses.
- R. Kohavi, D. Tang, and Y. Xu, *Trustworthy Online Controlled Experiments*. Cambridge University Press, 2020. doi:10.1017/9781108653985 — peeking, novelty effects, A/A tests.
- K. F. Schulz, D. G. Altman, and D. Moher, "CONSORT 2010 Statement," *BMJ*, vol. 340, p. c332, 2010. doi:10.1136/bmj.c332
