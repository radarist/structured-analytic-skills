---
name: The Scientific Method Cycle
category: scientific-method
origin: layered origins — Bacon's Novum Organum (1620), Descartes (1637), Newton's rules (1687); cycle form codified in 20th-century science education and philosophy of science
agent_suitability: High
tags: [hypothesis, experiment, observation, iteration, variables, controls, method]
related: [../scientific-methods/hypothetico-deductive-method.md, ../scientific-methods/induction-abduction-analogy.md, ../scientific-methods/reproducibility-open-science.md, ../research-methods/experimental-design.md, ../agent-playbook.md]
---

# The Scientific Method Cycle

> **Essence:** The iterative loop at the heart of empirical inquiry — observe, question, hypothesize, predict, test, analyze, conclude — where every answer feeds back as a better question and knowledge accumulates by disciplined correction.

## Overview

The scientific method is less a single procedure than a **disciplined error-correction cycle**. Its classic loop: **observation** (notice something about the world) → **question** (frame what's puzzling, specifically) → **hypothesis** (a testable candidate explanation) → **prediction** (what must be observable if the hypothesis is true, and — equally important — if it is false) → **experiment/test** (gather evidence that can discriminate) → **analysis** (does the evidence match prediction?) → **conclusion** (support, refine, or reject — then loop back with a sharper question). The cycle's power is that it is *self-correcting*: conclusions are provisional, tied to evidence quality, and always re-enterable.

Several disciplines inside the loop do the real work. **Operationalization**: turn fuzzy concepts into measurable variables (and name the independent, dependent, and — critically — the **control variables** that must be held constant). **Falsifiability of the test design**: a test that can't come out against the hypothesis isn't a test (developed fully in [hypothetico-deductive-method.md](hypothetico-deductive-method.md)). **Replication**: results count when independent re-runs converge (developed in [reproducibility-open-science.md](reproducibility-open-science.md)). And **iteration honesty**: refining a hypothesis after seeing data is fine — as long as the refined hypothesis is then tested on *new* evidence, not re-credited with the data that inspired it.

Three vocabulary distinctions prevent perennial confusion. A **hypothesis** is a testable, specific candidate explanation. A **theory** is a well-substantiated, integrated explanatory framework (gravity, evolution — theories are *stronger* than hypotheses, not weaker, despite colloquial usage). A **law** is a concise description of a regularity (often mathematical) — theories explain laws. The cycle applies across scales: a student's lab, an R&D team's debugging, a data team's A/B program, and community-level science all run the same loop with different machinery ([experimental-design.md](../research-methods/experimental-design.md) is the cycle's rigorous formalization for causal questions).

## Origin & History

- **1620:** Francis Bacon, *Novum Organum* — systematic observation and induction against armchair speculation (see [induction-abduction-analogy.md](induction-abduction-analogy.md)).
- **1637:** René Descartes, *Discourse on Method* — systematic doubt and methodical reasoning.
- **1687:** Newton's *Principia* with its "Rules of Reasoning in Philosophy" — the exemplar of hypothesis-prediction-mathematical-test integration.
- **19th c.:** John Herschel, William Whewell (coins "scientist"), Claude Bernard's *An Introduction to the Study of Experimental Medicine* (1865) — the experimental loop articulated for life sciences.
- **20th c.:** Karl Popper reframes the cycle around falsification ([hypothetico-deductive-method.md](hypothetico-deductive-method.md)); Kuhn shows how the cycle runs inside paradigms; science education codifies the loop as the standard teaching form (while philosophers note real science is messier — Feyerabend's *Against Method*, 1975, is the famous provocation).

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Observation | Noticing phenomena — the loop's entry point (and itself theory-laden). |
| Question | A specific, answerable framing of the puzzle. |
| Hypothesis | A testable candidate explanation, stated so evidence can count against it. |
| Prediction | A specific observable consequence deduced from the hypothesis (and from its rivals). |
| Variable (IV/DV/control) | What you vary / measure / hold constant. |
| Operationalization | Defining constructs as measurable procedures. |
| Test/experiment | Evidence-gathering designed to discriminate among predictions. |
| Analysis | Comparing evidence to predictions — with stated error tolerances. |
| Replication | Independent repetition; the loop at community scale. |
| Hypothesis vs theory vs law | Candidate explanation / substantiated framework / described regularity. |

## When to Use / When Not to Use

**Use when:**
- Any empirical question where claims must answer to evidence — from debugging to drug trials.
- Teaching and structuring inquiry in teams (the loop is the shared protocol).
- As the organizing frame for more specialized methods (experiment, survey, modeling).
- Engineering investigations: root-causing failures, validating designs.

**Don't use when:**
- The question is normative, aesthetic, or conceptual (values, meanings, definitions) — the loop doesn't apply to "should we" or "what does this mean".
- Phenomena are unobservable even in principle by available instruments (speculation — label it as such).
- The cycle is recited as ritual without its disciplines (operationalization, controls, replication) — that's cargo-cult science.
- A single pass is treated as settlement: the method is a *cycle*, and one loop is a beginning.

## Process & Steps

**Elapsed time:** a full cycle scales with the question — hours for an agent-tractable question over existing data, weeks to months when new empirical data must be collected. The steps most often starved are 1 (observation) and 7 (revision); budget them explicitly. Participants: a lone researcher can run the whole cycle, but steps 3–4 improve sharply with a rival-hypothesis partner or red team.

1. **Observe and record.** Gather what's actually happening; separate observation from interpretation; log anomalies (they're often the real question). *Artifact: observation log.*
2. **Frame the question.** Specific and answerable: "Does X affect Y under conditions Z?" not "Why is the world weird?" *Artifact: question statement.*
3. **Form hypothesis(es).** Candidate explanation(s) — ideally several rivals (see [hypothetico-deductive-method.md](hypothetico-deductive-method.md) on multiple working hypotheses). *Artifact: hypothesis set.*
4. **Deduce predictions.** For each hypothesis: what must be observed if true? What if false? Make predictions discriminating — the same observation shouldn't confirm everything. *Artifact: prediction table.*
5. **Design and run the test.** Operationalize variables; control confounders; pre-commit to what result supports/refutes. *Artifact: test protocol + data.*
6. **Analyze honestly.** Compare evidence to predictions; report effect sizes and uncertainty; check whether alternative explanations survive. *Artifact: analysis.*
7. **Conclude provisionally.** Support / refine / reject — and state the next question the answer raises. Feed back to step 1–2. *Artifact: conclusion + next-cycle question.*
8. **Report and invite replication.** Methods and data open enough for others to re-run the loop. *Artifact: report.*

## Techniques, Tools & Deliverables

- Prediction tables (hypothesis × observable consequence, if-true/if-false).
- Operationalization worksheets (construct → measure → instrument).
- Control-design checklists (confound inventory; what varies, what's held).
- Lab notebooks / experiment logs (the audit trail); analysis code and data.
- **Deliverables:** the tested hypothesis set, evidence, provisional conclusions, next-cycle questions, replicable methods.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Self-correcting by construction — error is the fuel | Real science is messier than the tidy loop (serendipity, paradigm effects) |
| Universal across domains and scales | Says nothing about where good hypotheses come from (see abduction) |
| Teaches as a protocol; onboards teams fast | Ritual recitation without controls/replication is theater |
| Accumulates: each cycle sharpens the next | Slow; shortcuts (p-hacking, HARKing) corrupt it silently |
| Foundation frame for all rigorous methods here | Not designed for meaning/value questions |

The cycle's failure modes are silent corruption, not open error: p-hacking and HARKing keep the ritual of testing while inverting the logic (hypothesis after results), and each shortcut is individually invisible. That's why the method's strictest artifacts — pre-registered hypotheses, held-out tests, reported null results — exist as tripwires, and why skipping them "just this once" is the standard slide. The scope limit is also real: the cycle answers empirical questions and has no purchase on meaning, value, or identity questions (that's what interpretive methods like CLA are for). And it's slow by design; teams that compress the loop usually compress the observation or revision step — the two steps that carry the learning.

## Worked Examples & Case Studies

- **Semmelweis (1840s):** observed differing maternity-ward mortality, hypothesized cadaverous contamination, predicted handwashing would cut deaths, tested it (mortality fell) — the cycle in medicine before germ theory existed.
- **Eddington's 1919 eclipse expedition:** Einstein's general relativity predicted specific light-bending; the observation discriminated against Newtonian prediction — prediction-driven testing at its cleanest.
- **Debugging as the cycle:** every competent engineer runs observe→hypothesize→predict→test against software/hardware faults — the loop's most common daily use.

## Variants & Related Methodologies

- **Hypothetico-deductive method** — the cycle's formal logic ([hypothetico-deductive-method.md](hypothetico-deductive-method.md)).
- **Experimental design** — the cycle's rigorous causal form ([experimental-design.md](../research-methods/experimental-design.md)).
- **PDCA/PDSA (Deming)** — the quality-improvement cousin (Plan-Do-Check-Act).
- **OODA loop** — decision-cycle cousin in competitive contexts.
- Related: [induction-abduction-analogy.md](induction-abduction-analogy.md) (hypothesis generation), [bayesian-evidence-updating.md](bayesian-evidence-updating.md) (belief revision inside the loop), [reproducibility-open-science.md](reproducibility-open-science.md) (cycle integrity at scale).

## Agent Adaptation

### Suitability for agent execution

**High — the cycle maps directly onto agent orchestration.** Each loop stage has a natural agent role, and agents are *tireless* at enforcing the disciplines humans skip (prediction tables, control checklists, logging). For questions testable via computation, documents, or web evidence, agents can run full loops autonomously; for physical experiments, agents run everything except the bench work. The standing risk is loop corruption: agents must be structurally prevented from quietly revising hypotheses after seeing data (HARKing) — enforce pre-committed prediction files and cycle logs.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Scout | Observation gathering (literature, data, anomalies) with sources. |
| Analyst | Question framing, operationalization, prediction tables, analysis (in code). |
| Domain Expert (personas) | Rival-hypothesis generation (multiple working hypotheses); prediction discrimination review. |
| Critic / Red Team | Pre-test: is the prediction falsifiable? would any result "confirm"? Post-test: alternative explanations surviving? HARKing check vs pre-committed files. |
| Verifier | Data/evidence fidelity; re-run analyses. |
| Synthesizer | Cycle report, next-cycle questions, accumulated knowledge log. |
| Facilitator (human) | Question selection, ethics, conclusion acceptance. |

### Agent pipeline

1. Observe (Scout) → `observations.md` (sourced).
2. Frame (Analyst + human) → question + operationalization.
3. Hypothesize (Domain Experts, isolated, then compared) → `hypotheses.md` (rivals preserved).
4. Predict (Analyst) → `predictions.md` — **committed before testing** (timestamped).
5. Test (experiment/data collection; code executor) → `data/`.
6. Analyze (Analyst; Verifier re-run) → results vs pre-committed predictions.
7. Stress-test (Critic) → surviving alternatives + HARKing audit (diff hypotheses vs predictions).
8. Conclude + loop (Synthesizer) → cycle report; next question enters queue.

### Prompt templates

```text
SYSTEM: You are the hypothesis generator. Question: {{question}}. Observations: {{observations}}.
Generate 3-5 RIVAL hypotheses that could each explain the observations (include at least one
"null/boring" explanation and one you'd bet against). For each: the mechanism, and two
DISCRIMINATING predictions — observations that would support it while counting against at least
one rival. Avoid hypotheses so flexible any result fits them. Output structured table.
```

```text
SYSTEM: You are the cycle-integrity Critic. Pre-committed predictions (timestamped):
{{predictions_file}}. Data and analysis: {{analysis}}. Hypothesis as now stated: {{hypothesis_now}}.
Audit: (1) HARKing — diff the current hypothesis against the pre-committed one; list every quiet
revision. (2) Discrimination — did the observed result actually discriminate among rivals, or
was it consistent with all of them? (3) Control check — which confound was NOT controlled, and
could it produce this result? (4) Verdict: what does this cycle license concluding — support,
refine (and re-test on new data), reject, or inconclusive?
```

### Tools & data requirements

Depends on the domain: code execution (analysis), web/retrieval (evidence), experiment platforms (tests), timestamped stores for pre-committed predictions (cycle integrity), logs for the audit trail.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| HARKing (hypothesis revised to fit data) | Critic diff vs pre-committed file | Timestamped prediction/hypothesis files; revision requires new-data re-test |
| Non-discriminating predictions | Pre-test Critic gate | Prediction must count against ≥1 rival |
| Uncontrolled confounds | Control checklist audit | Confound inventory mandatory per cycle |
| Single-loop settlement claims | Report review | Conclusions always provisional + next question stated |
| Silent analysis flexibility | Verifier re-run | All analysis in logged code |

### Human-in-the-loop checkpoints

1. Question selection (what's worth cycles).
2. Test-design approval (ethics, resources).
3. Conclusion acceptance and next-cycle direction.

### Inputs & outputs (chaining contract)

**Inputs:** observations/anomalies (any source, incl. [horizon-scanning.md](../foresight/horizon-scanning.md)); domain access for testing.
**Outputs:** tested hypotheses, provisional conclusions, next-cycle questions — feeding [hypothetico-deductive-method.md](hypothetico-deductive-method.md) (strong inference), [bayesian-evidence-updating.md](bayesian-evidence-updating.md) (belief revision), [reproducibility-open-science.md](reproducibility-open-science.md) (community replication).

## References & Further Reading

- Bacon, F. (1620). *Novum Organum.*
- Bernard, C. (1865). *An Introduction to the Study of Experimental Medicine.*
- Popper, K.R. (1959). *The Logic of Scientific Discovery.* (cycle reframed as conjecture-refutation)
- Kuhn, T.S. (1962). *The Structure of Scientific Revolutions.* (cycles within paradigms)
- Platt, J.R. (1964). "Strong Inference." *Science*, 146(3642). (the cycle at full speed)
- Feyerabend, P. (1975). *Against Method.* New Left Books. (the famous counterpoint)
- Newton, I. (1687). *Principia* — "Rules of Reasoning in Philosophy" (Book III).
