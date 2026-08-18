---
name: Experimental & Quasi-Experimental Design
category: research-method
origin: agricultural statistics (R.A. Fisher, 1925/1935); clinical trials (Bradford Hill, 1948); quasi-experimentation codified by Campbell & Stanley (1963)
agent_suitability: Medium
tags: [experiment, rct, randomization, control, ab-testing, quasi-experiment, validity, causation]
related: [../scientific-methods/scientific-method-cycle.md, ../scientific-methods/hypothetico-deductive-method.md, ../scientific-methods/reproducibility-open-science.md, ../research-methods/meta-analysis.md, ../agent-playbook.md]
---

# Experimental & Quasi-Experimental Design

> **Essence:** Establish causation by manipulating an independent variable while controlling everything else — randomization does the controlling in true experiments; design cleverness substitutes when randomization is impossible.

## Overview

Experiments answer the question other designs can only gesture at: *does X cause Y?* The logic is comparison under control. In a **true experiment**, units are **randomly assigned** to conditions (treatment vs control); randomization is the master stroke because it equalizes groups on *all* confounders — known and unknown, measured and unmeasured — in expectation, leaving the manipulation as the only systematic difference. Fisher's design trilogy: **randomization** (kill confounding), **replication** (estimate error, generalize across units), **blocking** (soak up known nuisance variation to sharpen precision). Add **blinding** (participants and/or assessors don't know allocation — single/double-blind) to kill expectancy and measurement bias, and you have the randomized controlled trial (RCT): medicine's evidence apex since Bradford Hill's 1948 streptomycin trial.

Design variations trade precision and cost: **between-subjects** (different people per condition — clean, expensive) vs **within-subjects** (same people in all conditions — powerful, but order effects need counterbalancing); **factorial designs** (manipulate 2+ factors to estimate main effects *and* interactions — Fisher's efficiency insight); **A/B testing** (industry RCTs at scale, with its own craft: power calculations, peeking problems, novelty effects, interference between units). When random assignment is impossible (policy, ethics, practicality), **quasi-experiments** approximate it: nonequivalent control groups with pretests, **interrupted time series** (many pre/post measurements), **regression discontinuity** (assignment by a cutoff), **difference-in-differences** (compare changes, not levels), natural experiments — each with assumptions that must be argued, not assumed.

Campbell & Stanley's **validity typology** is the field's permanent audit framework: **internal validity** (is the effect real, or confounded? — threats: history, maturation, selection, regression to the mean, instrumentation, attrition), **external validity** (does it generalize across people/settings/times?), **construct validity** (did we manipulate/measure what we think?), **statistical conclusion validity** (is the inference sound — power, error rates, violated assumptions?). Every experiment report is implicitly a defense against these threats. Modern additions: **preregistration** and power analysis as honesty devices (see [reproducibility-open-science.md](../scientific-methods/reproducibility-open-science.md)), and CONSORT reporting standards for trials.

## Origin & History

- **1925/1935:** R.A. Fisher, *Statistical Methods for Research Workers* / *The Design of Experiments* — randomization, blocking, factorial designs (agricultural field trials at Rothamsted); the lady-tasting-tea thought experiment.
- **1948:** Bradford Hill's streptomycin trial — the modern RCT's founding clinical demonstration.
- **1963:** Donald Campbell & Julian Stanley, *Experimental and Quasi-Experimental Designs for Research* — the validity-threat framework; expanded by Cook & Campbell (1979) and Shadish, Cook & Campbell (2002).
- **2000s–present:** online A/B testing industrialized experimentation (Kohavi et al.); causal-inference formalization (Rubin's potential outcomes; Pearl's do-calculus) sharpened what experiments license; replication crisis put preregistration and power front and center.

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Independent/dependent variable | What you manipulate / what you measure. |
| Random assignment | Units allocated by chance — equalizes confounders in expectation. |
| Control condition | The comparison baseline (placebo, business-as-usual, alternative). |
| Blinding | Allocation concealed from participants/assessors to prevent expectancy and measurement bias. |
| Factorial design | 2+ factors crossed; estimates main effects + interactions efficiently. |
| Power | Probability of detecting a true effect of a given size; set by n, effect size, α (target ≥ .80). |
| Quasi-experiment | No random assignment; design approximates control (pre-post, comparison series). |
| Regression discontinuity | Assignment by cutoff — compare just-above vs just-below the threshold. |
| Difference-in-differences | Compare *changes* in treated vs comparison groups (needs parallel-trends assumption). |
| Interrupted time series | Many measurements before/after an intervention; level/slope changes as evidence. |
| Four validities | Internal, external, construct, statistical conclusion (Campbell tradition). |

## When to Use / When Not to Use

**Use when:**
- The question is causal and the variable can ethically/practically be manipulated.
- You can randomize (or exploit discontinuities/natural experiments) with adequate power.
- Decisions depend on effect size, not just association (product changes, treatments, policies).
- Mechanism isolation matters (which ingredient does the work — factorial designs).

**Don't use when:**
- Manipulation is unethical or impossible (harm exposures, immutable characteristics) — observational causal inference or quasi-experiments, honestly labeled.
- The outcome takes decades to emerge (longitudinal/observational designs).
- n is tiny and effects are small — underpowered experiments manufacture noise dressed as findings.
- Context is the phenomenon (the lab strips what you're studying — field experiments or qualitative methods).

## Process & Steps

1. **Hypothesis and design choice.** Falsifiable prediction; between/within/factorial; manipulation + control conditions; measures (operationalize constructs). *Artifact: design plan.*
2. **Power analysis.** Expected effect size (from prior evidence, honestly) → required n; fix α and corrections for multiple comparisons upfront. *Artifact: power analysis.*
3. **Preregister** (modern standard): hypotheses, design, measures, analysis plan, exclusion rules — timestamped before data collection. *Artifact: registration.*
4. **Run the experiment.** Randomize (document the mechanism); maintain blinding; log everything (attrition, protocol deviations); manipulation checks. *Artifact: dataset + procedural log.*
5. **Analyze per the preregistered plan.** Estimate effect size + confidence interval (not just p); check assumptions; pre-specified subgroup analyses only; sensitivity analyses labeled as such. *Artifact: analysis.*
6. **Audit validity.** Walk the four validities: name the surviving threats and their likely direction of bias. *Artifact: validity audit.*
7. **Report transparently.** CONSORT-style: allocation flow, deviations, all conditions measured, exact statistics; exploratory findings labeled exploratory. *Artifact: the report.*

## Techniques, Tools & Deliverables

- Randomization and blinding procedures (documented, auditable).
- Power analysis tools (G*Power; code); manipulation and attention checks.
- Factorial analysis (ANOVA family); effect-size reporting (d, RR) with CIs.
- A/B-test craft: sequential-testing corrections (no peeking), CUPED/variance reduction, interference checks.
- Quasi-experimental toolkits: DiD, RDD, ITS, matching/propensity methods.
- **Deliverables:** preregistration, powered dataset with procedural log, effect estimates + CIs, validity audit, transparent report.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| The strongest warrant for causal claims | Artificiality risk: control can strip the phenomenon (external validity) |
| Randomization handles unknown confounders | Ethics/feasibility bar many manipulations |
| Factorial designs test mechanisms efficiently | Power failures produce noise-as-findings; p-hacking corrupts inference |
| A/B industrialization makes causation routine at scale | Interference/network effects break naive randomization in real systems |
| Validity framework gives a permanent audit language | Precision in the lab can mislead about messy deployment contexts |

## Worked Examples & Case Studies

- **Bradford Hill streptomycin trial (1948):** randomized allocation + objective assessment in tuberculosis treatment — the RCT's founding demonstration.
- **Fisher's Rothamsted designs (1920s–30s):** blocking and factorial logic in field agriculture — the design canon.
- **Tech A/B testing:** large-scale experimentation programs (Microsoft/Google/Booking; Kohavi et al.'s trustworthiness work — e.g., documenting how most ideas fail and peeking inflates false positives).
- **Regression discontinuity classics:** Thistlethwaite & Campbell (1960) on scholarship cutoffs — the founding RD study.

## Variants & Related Methodologies

- **Field experiments / natural experiments; RCT clusters; stepped-wedge.**
- **Quasi-experimental family:** DiD, RD, ITS, matching.
- **Single-case experimental designs** (N-of-1, multiple-baseline — behavioral sciences).
- **Factorial/fractional-factorial screening designs** (industrial DOE — Box).
- Related: [scientific-method-cycle.md](../scientific-methods/scientific-method-cycle.md) (the cycle it operationalizes), [hypothetico-deductive-method.md](../scientific-methods/hypothetico-deductive-method.md) (its logic), [meta-analysis.md](meta-analysis.md) (pooling experiments), [reproducibility-open-science.md](../scientific-methods/reproducibility-open-science.md) (preregistration).
- Skill counterpart: [skills/experimental-design](../../skills/experimental-design/SKILL.md) — the executable design card, with a power-analysis tool.

## Agent Adaptation

### Suitability for agent execution

**Medium.** Agents can run the entire analytical and procedural machinery: power analysis, randomization code, preregistration drafting, analysis pipelines, validity-threat audits, and report generation — all in code, all reproducible. Where the experiment is *digital* (A/B tests, agent-mediated interventions, simulation experiments), agents can additionally run the experiment itself. Human-essential: ethical judgments about manipulation, construct operationalization choices, and interpretation. Biggest agent-specific risk: flexible-analysis temptation (agents can re-run until results "improve" — the preregistration + code-log discipline must be enforced by the pipeline, not promised by the agent).

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Facilitator (human) | Ethics, construct choices, claim sign-off. |
| Domain Expert (personas) | Design advice: confound candidates, manipulation realism, measure validity. |
| Analyst | Power analysis, randomization, analysis pipeline — in code with saved scripts. |
| Critic / Red Team | Four-validities audit; p-hacking/peeking detection (analysis-log review); alternative-explanation generation. |
| Verifier | Re-run analysis from raw data; check preregistration-vs-executed diff. |
| Synthesizer | Preregistration and report drafts (CONSORT-style). |
| Code executor (tool) | All computation. |

### Agent pipeline

1. Design (human + Domain Experts) → hypothesis, design, measures → Analyst power analysis → human approves.
2. Preregister (Synthesizer) → timestamped plan → human locks it.
3. Execute (experiment platform; Analyst's randomization) → `data/` + `procedural_log.md`.
4. Analyze (Analyst, code) → effect estimates; Verifier re-runs; prereg diff report.
5. Audit (Critic) → validity-threat walk-through + analysis-log p-hacking check.
6. Report (Synthesizer) → transparent report → human claims sign-off.

### Prompt templates

```text
SYSTEM: You are the experimental-design analyst. Research question: {{question}}. Proposed
design: {{design}}. Prior evidence for effect size: {{prior_evidence}}. In code: (1) compute
required n for power .80 at alpha .05 (state the effect-size assumption and its source; show
sensitivity to smaller effects); (2) draft the randomization procedure (unit, mechanism,
blocking/stratification variables) as runnable code; (3) list the manipulation check and
exclusion rules that must be preregistered. Output: power table + randomization script +
preregistration checklist.
```

```text
SYSTEM: You are the validity auditor. Experiment: {{design_and_log}}. Results: {{results}}.
Walk all four validities with SPECIFICS: INTERNAL — attrition by condition? differential
compliance? what confound survives randomization here?; STATISTICAL CONCLUSION — power adequate?
multiple comparisons handled? assumptions checked (show diagnostics)?; CONSTRUCT — did the
manipulation produce the intended psychological/behavioral state (manipulation check evidence)?
did measures measure the construct?; EXTERNAL — who/what/where can't this generalize to?
For each surviving threat: its likely DIRECTION of bias. End with the three strongest
alternative explanations for the headline result.
```

```text
SYSTEM: You are the preregistration-integrity Verifier. Preregistration: {{prereg}}. Executed
analysis: {{analysis_code_and_output}}. Produce the diff report: every hypothesis, measure,
exclusion rule, and analysis that was added, dropped, or changed after registration; for each
change classify: JUSTIFIED (documented reason consistent with plan) / DEVIATION (unjustified —
must be reported as such) / EXPLORATORY (new analysis — must be labeled exploratory). Then
re-run the preregistered primary analysis from raw data and confirm the numbers match.
```

### Tools & data requirements

Code execution (power, randomization, analysis — mandatory), experiment/A-B platform access where applicable, preregistration timestamping (a dated file/commit suffices), immutable analysis logs.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| p-hacking by re-run | Analysis-log vs preregistration diff | Locked prereg + immutable logs; exploratory labeling |
| Underpowered fishing | Power table missing | No execution without power analysis |
| Peeking (sequential looks) | Look-log vs correction check | Pre-specified sequential methods or no looks |
| Strawman controls | Domain Expert review | Control condition justified against alternatives |
| Attrition blindness | Flow table | CONSORT-style flow mandatory; differential-attrition tests |
| Over-generalized claims | Critic external-validity audit | Claims bounded to sampled units/settings |

### Human-in-the-loop checkpoints

1. Ethics of manipulation and consent.
2. Construct operationalization and design approval.
3. Preregistration lock.
4. Claim sign-off (what the experiment licenses saying).

### Inputs & outputs (chaining contract)

**Inputs:** falsifiable hypothesis (from [hypothetico-deductive-method.md](../scientific-methods/hypothetico-deductive-method.md)), prior effect-size evidence (from [meta-analysis.md](meta-analysis.md)/[systematic-literature-review.md](systematic-literature-review.md)), manipulation capability.
**Outputs:** effect estimates + CIs, validity audit, preregistration-integrity report — feeding [meta-analysis.md](meta-analysis.md) (pooling), [evidence-appraisal.md](../scientific-methods/evidence-appraisal.md) (grading), decisions.

## References & Further Reading

- Fisher, R.A. (1935). *The Design of Experiments.* Oliver & Boyd.
- Campbell, D.T. & Stanley, J.C. (1963). *Experimental and Quasi-Experimental Designs for Research.* Rand McNally.
- Shadish, W.R., Cook, T.D. & Campbell, D.T. (2002). *Experimental and Quasi-Experimental Designs for Generalized Causal Inference.* Houghton Mifflin.
- Kohavi, R., Tang, D. & Xu, Y. (2020). *Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing.* Cambridge University Press.
- Medical Research Council (1948). "Streptomycin Treatment of Pulmonary Tuberculosis." *BMJ*, 2. (Bradford Hill's trial)
- Thistlethwaite, D. & Campbell, D. (1960). "Regression-Discontinuity Analysis." *Journal of Educational Psychology*, 51(6).
- Box, G.E.P., Hunter, J.S. & Hunter, W.G. (2005). *Statistics for Experimenters* (2nd ed.). Wiley.
- Schulz, K.F., Altman, D.G. & Moher, D. (2010). "CONSORT 2010 Statement: Updated Guidelines for Reporting Parallel Group Randomised Trials." *BMJ*, 340.
