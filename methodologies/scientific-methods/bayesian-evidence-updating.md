---
name: Bayesian Evidence Updating
category: scientific-method
origin: Thomas Bayes (essay published 1763); Pierre-Simon Laplace (1774+); modern revival: Jeffreys (1939), Jaynes; forecasting craft: Tetlock (2015)
agent_suitability: High
tags: [bayes, probability, priors, likelihood, updating, calibration, forecasting, base-rates]
related: [../scientific-methods/hypothetico-deductive-method.md, ../scientific-methods/induction-abduction-analogy.md, ../foresight/delphi-method.md, ../agent-playbook.md]
---

# Bayesian Evidence Updating

> **Essence:** Treat beliefs as probabilities and update them in proportion to how much more likely the evidence is if a hypothesis is true than if it isn't — prior × likelihood ratio → posterior, which becomes the next prior.

## Overview

Bayesian reasoning is the arithmetic of graded belief. Where falsification gives a binary verdict (refuted / not yet refuted), most real evidence is diagnostic rather than decisive: it should move confidence *by an amount*, in a direction. Bayes' theorem supplies the amount. In odds form (the practical version): **posterior odds = prior odds × likelihood ratio**, where the likelihood ratio is P(evidence | hypothesis) ÷ P(evidence | ¬hypothesis). Evidence that is equally likely either way moves nothing (LR = 1); evidence that is expected if true but surprising if false moves a lot. This single rule mechanically enforces the two disciplines humans chronically violate: **base rates matter** (a 99%-accurate test on a 1-in-1000 condition still yields mostly false positives — the canonical medical-screening example), and **absence of evidence is evidence of absence only when you'd expect to see it** (a negative search of your desk is strong evidence the keys aren't there; a negative glance is not).

The practice layer comes from forecasting research. Tetlock's *Superforecasting* (2015) — built on the Good Judgment Project's IARPA tournament wins — showed that ordinary people trained in a handful of habits systematically beat pundits and matched or beat intelligence analysts: think in probabilities not yes/no; start from **outside-view base rates** before adjusting for case specifics; **update frequently in small increments** rather than waiting for certainty; decompose hard questions (Fermi-ization); actively seek disconfirming evidence; and keep score. Scoring is the honesty device: **calibration** (when you say 70%, do things happen ~70% of the time?) measured with proper scoring rules like the **Brier score** (mean squared probability error), which punishes both timidity and overconfidence. A Bayesian practice that never keeps score is astrology with arithmetic.

For agents this is the most naturally executable reasoning discipline in the library: priors, likelihood ratios, posteriors, and calibration tracking are all explicit arithmetic — and it composes perfectly with [delphi-method.md](../foresight/delphi-method.md) (panels supply estimates), [hypothetico-deductive-method.md](hypothetico-deductive-method.md) (severe tests are just very large likelihood ratios), and foresight signpost monitoring (each observed signpost updates scenario odds).

## Origin & History

- **1763:** Thomas Bayes' posthumous essay ("An Essay towards solving a Problem in the Doctrine of Chances", *Philosophical Transactions*).
- **1774–1812:** Laplace independently develops and applies inverse probability (*Théorie Analytique des Probabilités*), including early forms of the theorem in practical use.
- **1939:** Harold Jeffreys, *Theory of Probability* — Bayesian inference as the logic of science; **1946/2003:** E.T. Jaynes (*Probability Theory: The Logic of Science*) — probability as extended logic.
- **1950s–80s:** subjective Bayesianism (de Finetti, Savage); Bayesian decision theory; early medical-diagnosis systems; frequentist dominance in mainstream statistics notwithstanding.
- **1990s–present:** computational Bayesian revolution (MCMC) in statistics; Kahneman & Tversky's heuristics-and-biases program documents human base-rate neglect (1970s); **2011–2015:** Tetlock's Good Judgment Project wins IARPA's ACE tournament; *Superforecasting* (2015) codifies the craft; **2016+:** calibration training platforms (e.g., prediction tournaments) spread the practice.

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Prior | Belief before the new evidence, as a probability (or odds). |
| Likelihood ratio (LR) | P(E\|H) ÷ P(E\|¬H) — the evidence's diagnostic strength. |
| Posterior | Updated belief: prior odds × LR (odds form). Becomes the next prior. |
| Base rate | The reference-class frequency — the default prior. |
| Inside vs outside view | Case-specific reasoning vs reference-class statistics; start outside, adjust inside. |
| Calibration | Alignment of stated confidence with realized frequency. |
| Brier score | Mean squared error of probabilistic forecasts (lower is better); the standard scorecard. |
| Over/underconfidence | Systematic calibration error direction (humans: usually over). |
| Fermi-ization | Decomposing an estimable quantity into multiplyable estimable parts. |
| Belief logging | Recording dated probabilities so updating and scoring are auditable. |

## When to Use / When Not to Use

**Use when:**
- Evidence is diagnostic, not decisive (most real questions): intelligence, diagnosis, forecasting, due diligence.
- You must aggregate sequential evidence over time (signposts arriving, tests accumulating).
- Decisions need probabilities, not verdicts (risk management, options, hedges).
- You want an auditable, improvable forecasting practice (scoring makes skill visible).

**Don't use when:**
- Crisp refutation is available and sufficient (use [hypothetico-deductive-method.md](hypothetico-deductive-method.md)).
- Priors cannot be defended even roughly (deep ignorance — wide intervals and humility, or more data first).
- False precision would be read as knowledge (a spurious 63.7% can mislead worse than "somewhat likely" — report ranges).
- The question is one-shot and unscoreable with no base rate (updating works; calibration training doesn't).

## Process & Steps

1. **Define the question precisely.** Resolvable, dated, unambiguous ("By 31 Dec 2027, will X?") — forecasting dies of vague questions. *Artifact: resolvable question.*
2. **Set the prior from the outside view.** Find the reference class and its base rate; only then adjust for case specifics (each adjustment justified). *Artifact: prior + rationale, logged.*
3. **Identify candidate evidence and its diagnosticity in advance.** For each expected signal: what's its LR under each hypothesis? (Pre-committing LRs blocks rationalization.) *Artifact: evidence plan.*
4. **Update as evidence arrives.** Prior odds × LR → posterior; small frequent updates; log every update with the evidence and LR used. *Artifact: belief log.*
5. **Hunt disconfirming evidence deliberately.** Assign the strongest counter-case (steelman the rival); update honestly when it lands. *Artifact: counter-evidence entries.*
6. **Resolve and score.** When the question resolves, compute Brier score; run calibration review across many resolved questions. *Artifact: scorecard + calibration curve.*
7. **Feed back.** Where was error concentrated (priors? LRs? update discipline?) → adjust practice. *Artifact: post-mortem notes.*

## Techniques, Tools & Deliverables

- Odds-form updating worksheet (prior odds × LR table per evidence item).
- Reference-class research (base-rate hunting is a research skill).
- Fermi decomposition templates; premortems for tail risks.
- Belief logs / forecasting journals (dated, versioned); Brier scoring in code; calibration plots.
- **Deliverables:** resolvable question set, logged prior + updates + rationales, resolution scorecard, calibration analysis, practice improvements.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Correct arithmetic for graded evidence | Priors and LRs are judgments — garbage in, gospel out |
| Enforces base rates and evidence quality | False precision risk: numbers borrowed confidence they didn't earn |
| Auditable and improvable (scoring) | One-shot questions can't be calibrated individually (only across a practice) |
| Composes with Delphi, scenarios, signposts | Reflexive/adversarial domains shift base rates under you |
| Small-update discipline beats waiting-for-certainty | Mathematical ease can hide the hard part: *what should the prior be?* |

The honest failure modes are at the inputs, not the arithmetic. A base rate picked from the wrong reference class corrupts every update downstream, and the arithmetic's ease makes that corruption invisible — the posterior looks rigorous because it's a number. Likelihood ratios have the same problem: "how likely is this evidence under H?" is itself a judgment, and motivated reasoning enters there most cleanly. In adversarial or reflexive domains (markets, politics), base rates shift while you're updating, so treat the prior as dated. The practice that survives audit: record prior, likelihoods, and rationale *before* the update, and score yourself later (calibration/Brier) — the method without the scoring loop trains nothing.

## Worked Examples & Case Studies

- **Medical screening arithmetic:** the mammography-style example — 1% prevalence, 90% sensitivity, 9% false-positive rate → a positive result means only ~9% probability of disease (P(B) = 0.9×0.01 / (0.9×0.01 + 0.09×0.99)) — the standard demonstration that base rates dominate intuition.
- **Good Judgment Project (2011–2015):** superforecasters, using explicit probabilistic updating with base rates and frequent small revisions, beat prediction markets' unaided forecasts and outperformed intelligence analysts in IARPA's tournament (documented in Tetlock & Gardner, 2015).
- **Intelligence analysis reform:** CIA's *A Tradecraft Primer* and post-Iraq-WMD analytic standards (Analysis of Competing Hypotheses — Heuer — is essentially likelihood-ratio tabulation) institutionalized Bayesian-flavored discipline.

## Variants & Related Methodologies

- **Analysis of Competing Hypotheses (ACH)** — Heuer's structured LR matrix (intelligence tradecraft).
- **Bayesian statistics/modeling** — the full statistical machinery (priors on parameters, posteriors via MCMC).
- **Prediction markets** — price as aggregated probability (a social alternative to individual updating).
- **Subjective expected utility / decision analysis** — Bayesian beliefs + utilities → decisions.
- Related: [hypothetico-deductive-method.md](hypothetico-deductive-method.md) (severe tests = huge LRs), [delphi-method.md](../foresight/delphi-method.md) (panel priors), [induction-abduction-analogy.md](induction-abduction-analogy.md) (prior generation), [evidence-appraisal.md](evidence-appraisal.md) (evidence quality feeding LRs).
- Skill counterparts: [skills/bayesian-update](../../skills/bayesian-update/SKILL.md) (the single-update arithmetic, with tool) and [skills/brier-score-calibration](../../skills/brier-score-calibration/SKILL.md) (scoring whether your updates were accurate).

## Agent Adaptation

### Suitability for agent execution

**High — the most computationally native reasoning method here.** The full loop — base-rate research, pre-committed LRs, odds-form updating, dated belief logs, Brier scoring, calibration dashboards — is explicit arithmetic plus record-keeping, ideal for agent pipelines with code execution. Two agent-specific cautions: (1) LLMs' spontaneous probability statements are miscalibrated (they mirror verbal confidence norms, not frequencies) — so priors/LRs must be *researched and logged*, not vibed; (2) an agent can launder rationalization through invented LRs — pre-commitment and Critic review of every LR's justification are structural requirements.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Scout | Base-rate research (reference classes, historical frequencies) with sources; evidence gathering. |
| Analyst | Question resolution-criteria drafting; prior construction (outside view first); odds-form updates in code; scorekeeping. |
| Domain Expert (personas) | Inside-view adjustments with justifications; LR proposals per hypothesis. |
| Critic / Red Team | LR audit (justified or invented?); rationalization detection (LR drift after evidence known); alternative reference-class challenges; overconfidence checks. |
| Verifier | Recompute all arithmetic; source-check base rates. |
| Synthesizer | Belief log maintenance, calibration dashboards, forecast reports. |
| Facilitator (human) | Question selection, resolution judgments, decision use of probabilities. |

### Agent pipeline

1. Frame (human) → resolvable question set with resolution criteria.
2. Prior (Scout base rates → Analyst outside-view prior, logged) → `priors.json` [question, prior, reference_class, source, date].
3. Evidence plan (Domain Experts) → pre-committed LR table per expected signal → `lr_plan.md`.
4. Update loop (Scout evidence → Analyst code update → Critic LR audit → Verifier recompute) → append-only `belief_log.jsonl`.
5. Resolve + score (human resolution → Analyst Brier/calibration in code) → `scorecard.md`.
6. Post-mortem (Synthesizer + Critic) → error decomposition → practice fixes.

### Prompt templates

```text
SYSTEM: You are the base-rate Scout. Forecast question: {{question}}. Find 2-4 candidate
reference classes for this event, each with: the class definition, the historical frequency
(with source and date range), and how well this case matches the class. Recommend the primary
reference class and an outside-view prior, stating what makes this case typical or atypical.
No single-source base rates if alternatives exist. JSON output with sources.
```

```text
SYSTEM: You are the Bayesian updater. Question: {{question}}. Current belief: {{current_odds}}
(as of {{date}}). New evidence: {{evidence}} (sourced). Pre-committed LR plan: {{lr_plan}}.
(1) If the evidence matches a pre-committed signal, apply ITS LR — do not invent a new one.
(2) Otherwise propose an LR with explicit justification: P(E|H) and P(E|¬H) each with a
one-sentence defense. (3) Compute the update in code-form (show the arithmetic). (4) State the
largest objection to your LR. Output: log entry {date, evidence_id, lr, justification,
prior_odds, posterior_odds, objection}.
```

```text
SYSTEM: You are the calibration Critic. Belief log and resolutions: {{log_and_resolutions}}.
Compute (in code): Brier score overall and by question type; calibration table (predicted
bucket vs realized frequency). Diagnose: over/underconfidence pattern, base-rate adherence
(did forecasts track reference classes or wander?), update behavior (too few/too many updates?
panic swings after single items?). Then name the TWO most expensive recurring judgment errors
and a concrete practice change for each.
```

### Tools & data requirements

Code execution (all arithmetic + scoring — mandatory), web research (base rates), append-only belief log (versioned store), resolution tracking (dates/criteria), dashboards optional.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Vibed probabilities (unresearched priors/LRs) | Source/justification fields empty | Every number carries a source or an explicit rationale |
| Rationalizing LRs post hoc | LR drift vs pre-committed plan | Pre-committed LR table; deviations flagged by Critic |
| Base-rate neglect | Outside-view check in every prior | Prior construction starts from reference class, always |
| Overconfident point estimates | Calibration review | Report ranges; track overconfidence metric |
| No scoring, no learning | Scorecard missing | Resolution + Brier scoring is a hard pipeline stage |
| Arithmetic errors | Verifier recompute | All updates recomputed independently |

### Human-in-the-loop checkpoints

1. Question framing and resolution criteria.
2. Prior acceptance (the consequential judgment).
3. Resolution calls (did it happen?).
4. Decisions taken on the probabilities (acting is human).

### Inputs & outputs (chaining contract)

**Inputs:** resolvable questions; evidence streams (from [horizon-scanning.md](../foresight/horizon-scanning.md) signposts, literature, data); prior estimates (from [delphi-method.md](../foresight/delphi-method.md)).
**Outputs:** dated probability forecasts with audit trail, calibration scorecards, updated scenario/issue odds — feeding decision processes, [scenario-planning.md](../foresight/scenario-planning.md) (scenario odds over time), risk management.

## References & Further Reading

- Bayes, T. (1763). "An Essay towards solving a Problem in the Doctrine of Chances." *Philosophical Transactions*, 53.
- Laplace, P.-S. (1814). *A Philosophical Essay on Probabilities.*
- Jeffreys, H. (1939). *Theory of Probability.* Oxford.
- Jaynes, E.T. (2003). *Probability Theory: The Logic of Science.* Cambridge.
- Tetlock, P. & Gardner, D. (2015). *Superforecasting: The Art and Science of Prediction.* Crown.
- Tetlock, P. (2005). *Expert Political Judgment.* Princeton. (the prequel: why pundits fail)
- Kahneman, D. & Tversky, A. (1973). "On the Psychology of Prediction." *Psychological Review*, 80. (base-rate neglect)
- Heuer, R.J. (1999). *Psychology of Intelligence Analysis.* CIA. (ACH)
- Brier, G.W. (1950). "Verification of Forecasts Expressed in Terms of Probability." *Monthly Weather Review*, 78(1).
- Mellers, B. et al. (2015). "The Psychology of Intelligence Analysis: Drivers of Prediction Accuracy in World Politics." *Journal of Experimental Psychology: Applied*, 21(1).
