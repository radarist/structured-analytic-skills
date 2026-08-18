---
name: Hypothetico-Deductive Method (incl. Falsificationism & Strong Inference)
category: scientific-method
origin: Karl Popper (Logik der Forschung, 1934; English 1959); strong inference: John R. Platt (1964); multiple working hypotheses: T.C. Chamberlin (1890)
agent_suitability: High
tags: [falsification, deduction, popper, strong-inference, hypotheses, testing, demarcation]
related: [../scientific-methods/scientific-method-cycle.md, ../scientific-methods/induction-abduction-analogy.md, ../scientific-methods/bayesian-evidence-updating.md, ../research-methods/experimental-design.md, ../agent-playbook.md]
---

# Hypothetico-Deductive Method

> **Essence:** Science as conjecture and refutation — deduce risky, falsifiable predictions from bold hypotheses, then try hard to prove them *wrong*; what survives severe testing is corroborated, never proven.

## Overview

The hypothetico-deductive (H-D) method is the logical engine inside the scientific cycle. Its moves: start from a **hypothesis** (a conjecture — its origin doesn't matter, only its testability); **deduce** specific observable consequences that must hold *if* the hypothesis is true; then **test** those consequences against evidence. The logic is asymmetric and Popper made it the cornerstone of his philosophy: no amount of confirming instances can *verify* a universal claim (a million white swans don't prove all swans are white), but a single genuine counter-instance *falsifies* it (one black swan does). Science progresses not by accumulating confirmations but by **eliminating error** — bold conjectures, severe tests, survival of the refuted hypotheses' rivals.

Popper's **demarcation criterion** follows: a claim is scientific only if it is *falsifiable in principle* — if some conceivable observation could count against it. Theories that explain everything (and hence forbid nothing) are not science, whatever their other virtues. From this flows the demand for **risky predictions**: a test is severe only when the predicted outcome is improbable unless the theory is true (Einstein's light-bending — not "the treatment might help"). Auxiliary hypotheses complicate the picture (a failed prediction can always be saved by blaming instruments or background assumptions — the Duhem–Quine problem), so methodological honesty requires stating in advance which auxiliaries are being assumed.

Two practice upgrades complete the file. **Chamberlin's multiple working hypotheses** (1890): carry several rival hypotheses at once to avoid "ruling theory" attachment — the parent-love bias toward your own idea. **Platt's strong inference** (1964): the speed secret of fast-moving fields — (1) devise alternative hypotheses, (2) devise a crucial experiment whose outcome excludes one or more, (3) do it, (4) recycle with new alternatives. Kuhn (1962) and Lakatos (1970) supply the sociological context: normal science tests hypotheses inside paradigms/research programmes, and single refutations rarely kill a programme outright — progressive vs degenerating problem-shifts judge whether a programme's protective belt is learning or merely patching.

## Origin & History

- Roots in Grosseteste and Whewell (19th c. coined the term "hypothetico-deductive" context); Herschel's *Preliminary Discourse* (1830).
- **1890:** T.C. Chamberlin, "The Method of Multiple Working Hypotheses" (*Science*) — the antidote to hypothesis attachment.
- **1934/1959:** Karl Popper, *Logik der Forschung* / *The Logic of Scientific Discovery* — falsificationism, demarcation, corroboration; *Conjectures and Refutations* (1963) develops it.
- **1962:** Thomas Kuhn, *The Structure of Scientific Revolutions* — paradigms, normal vs revolutionary science.
- **1964:** John R. Platt, "Strong Inference" (*Science*, 146) — the method as practiced by fast fields (molecular biology, particle physics).
- **1970s:** Imre Lakatos — research programmes, hard core + protective belt, progressive/degenerating shifts; Duhem (1906) & Quine (1951) — the underdetermination problem every tester must manage.

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Hypothesis/conjecture | A proposed explanation whose origin is irrelevant and whose testability is everything. |
| Deduced prediction | A consequence that logically follows if the hypothesis (plus auxiliaries) holds. |
| Falsifiability | The claim forbids some observable states of the world — demarcation of science. |
| Severe test | A test the hypothesis is unlikely to pass unless true (risky prediction). |
| Corroboration | Surviving severe tests — provisional support, never proof. |
| Auxiliary hypothesis | Background assumption in the deduction (instruments work, conditions hold) — Duhem–Quine. |
| Crucial experiment | A test whose outcomes discriminate decisively among rivals. |
| Multiple working hypotheses | Chamberlin's discipline: maintain rivals to avoid attachment. |
| Strong inference | Platt's loop: alternatives → crucial test → exclusion → recycle. |
| Research programme (Lakatos) | Hard core + protective belt; judged by progressive vs degenerating problem-shifts. |

## When to Use / When Not to Use

**Use when:**
- You have candidate explanations and need the fastest path to eliminating wrong ones.
- Designing tests that actually discriminate (vs fishing for confirmation).
- Auditing claims for scientific status (is this falsifiable? what's the risky prediction?).
- Any competitive-explanation setting: debugging, diagnostics, A/B programs, theory contests.

**Don't use when:**
- No hypothesis space exists yet (you're pre-hypothesis — generate candidates first: [induction-abduction-analogy.md](induction-abduction-analogy.md)).
- The domain's evidence is statistical belief-grading, not crisp refutation (add [bayesian-evidence-updating.md](bayesian-evidence-updating.md)).
- Claims are unfalsifiable by nature (metaphysics, values) — other tools, honestly labeled.
- Single-counterexample logic is applied naively to noisy domains (measurement error makes "the one black swan" itself suspect — replicate first).

## Process & Steps

Platt's strong-inference loop, H-D style:

1. **Enumerate rival hypotheses.** Include the boring/null and the disliked ones; enough alternatives to cover the plausible space. *Artifact: hypothesis set (H₁..Hₙ).*
2. **Deduce predictions per hypothesis.** For each Hᵢ: observable consequences if true — and explicitly what it *forbids*. Note auxiliary assumptions. *Artifact: prediction matrix (hypothesis × observation).*
3. **Find the discriminating test.** Identify an observation/experiment where rivals predict differently — ideally a crucial experiment. Pre-commit to the decision rule. *Artifact: test design + decision rule.*
4. **Execute the test.** Controls, blinding, pre-registered analysis where applicable ([experimental-design.md](../research-methods/experimental-design.md)). *Artifact: evidence.*
5. **Exclude and recycle.** Eliminate refuted hypotheses (or repair them openly, flagging the repair); take the survivor(s) and generate the next round of alternatives and tests. *Artifact: exclusion log + next-cycle hypotheses.*
6. **Report severity, not just outcome.** State what the surviving hypothesis has been protected against — which risks it has faced. *Artifact: corroboration account.*

## Techniques, Tools & Deliverables

- Prediction matrices (rows = hypotheses, columns = possible observations, cells = predicted/forbidden).
- Severe-test checklist (risky? discriminating? auxiliaries stated? decision rule pre-committed?).
- Crucial-experiment design (the exclusion tree — Platt's "logical tree" of alternatives).
- Falsifiability audit for claims (what observation would count against this?).
- **Deliverables:** hypothesis set with predictions, test outcomes, exclusion log, corroboration account, next-cycle alternatives.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Fastest error-elimination engine in inquiry | Duhem–Quine: failed predictions implicate hypothesis+auxiliaries jointly — blame is ambiguous |
| Confirmation-resistant by design (kills wishful thinking) | Crucial experiments are rarer and less decisive than the ideal suggests |
| Multiple-hypothesis discipline beats attachment bias | Pure falsificationism ignores graded/statistical evidence (needs Bayesian complement) |
| Clear demarcation audit for claims | Sociologically naive alone — Kuhn/Lakatos show real programmes absorb refutations |
| Strong inference measurably accelerates fields | Generating *good* alternatives is a creative act the method doesn't supply (see abduction) |

Two historical correctives keep this honest. Kuhn and Lakatos documented that real research programmes absorb refutations — auxiliary hypotheses get patched, and a single failed test rarely kills anything (nor should it; anomalous results are often instrument error). The method's clean logic is a norm to aspire to, not a description of how science behaves. Second, the demarcation audit can become a weapon against novelty: genuinely new claims often can't yet specify severe tests, and demanding Popperian maturity on day one kills them. The method's real strength — forcing "what would change my mind?" before the test — is also the discipline most often skipped; a hypothesis with no stated falsifier is the tell that the cycle is being performed rather than run.

## Worked Examples & Case Studies

- **Eddington's eclipse test (1919):** general relativity predicted 1.75 arcseconds deflection vs Newtonian 0.87 — a risky, discriminating prediction; survival made Einstein famous (severity, not confirmation count).
- **Ehrlich/biochemistry tradition and molecular biology:** Platt's own exhibit — fields racing via exclusion trees (his 1964 paper contrasts them with "slow" fields stuck in single-hypothesis devotion).
- **Semmes-Weinstein / diagnostic medicine:** differential diagnosis is everyday strong inference — competing hypotheses, discriminating tests, exclusion.
- **Cold fusion (1989):** failed replications and missing predicted radiation falsified the claim for mainstream science — community-scale refutation, including the auxiliary-hypothesis battles.

## Variants & Related Methodologies

- **Strong inference** (Platt) — the operational loop described here.
- **Inference to the best explanation** — the generative complement ([induction-abduction-analogy.md](induction-abduction-analogy.md)).
- **Bayesian confirmation** — graded successor to binary refutation ([bayesian-evidence-updating.md](bayesian-evidence-updating.md)).
- **Lakatosian programme appraisal** — judging problem-shifts rather than single tests.
- Related: [scientific-method-cycle.md](scientific-method-cycle.md) (the host loop), [experimental-design.md](../research-methods/experimental-design.md) (test machinery), [reproducibility-open-science.md](reproducibility-open-science.md) (severe testing at community scale).
- Skill counterpart: [skills/analysis-of-competing-hypotheses](../../skills/analysis-of-competing-hypotheses/SKILL.md) — ACH operationalizes severe-testing across a full hypothesis set.

## Agent Adaptation

### Suitability for agent execution

**High — this is the reasoning pattern multi-agent systems execute best.** Rival-hypothesis generation across isolated personas, prediction-matrix construction, test-design proposals, exclusion bookkeeping, and severity audits are all structured reasoning tasks. Agents are also immune to hypothesis *attachment* (no ego), which makes them natural strong-inference engines — but they are prone to *generating unfalsifiable mush* (flexible hypotheses that explain everything), so the falsifiability gate and Critic must be structural, not aspirational. For computational/documentary domains agents can execute tests too; physical experiments keep humans at the bench.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Domain Expert (×3–6 isolated personas) | Rival-hypothesis generation (diverse, including null and heterodox); prediction proposals per hypothesis. |
| Analyst | Prediction matrix; discriminating-test identification; test execution logistics (code where applicable). |
| Critic / Red Team | Falsifiability gate (reject mush); severity audit (is the test risky?); auxiliary-hypothesis inventory; exclusion-fairness review. |
| Verifier | Evidence fidelity; re-run computational tests. |
| Synthesizer | Exclusion log, corroboration account, next-cycle alternatives. |
| Facilitator (human) | Hypothesis-space sign-off, test approval, conclusion acceptance. |

### Agent pipeline

1. Generate (Domain Experts, isolated) → `hypotheses.json` (rivals, mechanisms, what each forbids).
2. Deduce (Analyst) → `prediction_matrix.md` + auxiliaries → Critic falsifiability/severity gate.
3. Design test (Analyst + Domain Experts) → decision rule pre-committed → human approves.
4. Execute (code/lab) → evidence; Verifier checks.
5. Exclude (Synthesizer, with Critic fairness review) → `exclusion_log.md` + survivors.
6. Recycle → next-cycle alternatives; corroboration account updated.

### Prompt templates

```text
SYSTEM: You are hypothesis generator {{persona_id}} working ALONE (no consensus-seeking).
Phenomenon: {{phenomenon}}. Existing evidence: {{evidence}}. Propose up to 3 hypotheses,
spanning: the conventional explanation, a structural/boring one (artifact, measurement,
confound), and one heterodox mechanism. For each: mechanism in 2-3 sentences, what it PREDICTS
(specific observations), and what it FORBIDS (observations that would refute it). A hypothesis
that forbids nothing is worthless — rewrite until it takes a risk.
```

```text
SYSTEM: You are the severe-test Critic. Hypotheses with predictions: {{prediction_matrix}}.
(1) FALSIFIABILITY GATE: reject or demand revision of any hypothesis whose predictions fit all
plausible outcomes. (2) SEVERITY: rank the proposed tests by how improbable the predicted
result is unless the hypothesis is true. (3) AUXILIARIES: list every assumption the deduction
smuggles in (instrument, sampling, background theory) — a failed prediction can retreat into
each one, so name them now. (4) Recommend the single most discriminating test and the
pre-committed decision rule.
```

```text
SYSTEM: You are the exclusion auditor. Test result: {{result}}. Prediction matrix:
{{prediction_matrix}}. Pre-committed decision rule: {{decision_rule}}. Apply the rule WITHOUT
adjusting it: which hypotheses are excluded, which survive? For each exclusion, check the
Duhem-Quine escape: is anyone blaming an auxiliary, and was that auxiliary on the pre-registered
list? Report: exclusions (rule-following), attempted auxiliary escapes (flagged), survivors,
and the next discriminating question the survivors disagree on.
```

### Tools & data requirements

Code execution (computational tests, statistics), retrieval (evidence), timestamped stores for pre-committed predictions/decision rules (integrity), test platforms as applicable.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Unfalsifiable hypothesis mush | Critic falsifiability gate | "What does it forbid?" is mandatory per hypothesis |
| Confirmation-seeking tests | Severity audit | Risky-prediction ranking before test selection |
| Duhem-Quine laundering (blame the instrument post hoc) | Auxiliary inventory diff | Auxiliaries pre-registered; post-hoc escapes flagged |
| Single-hypothesis devotion | Hypothesis count/diversity report | Rival generation across isolated personas mandatory |
| Moving decision rules | Pre-committed rule file | Timestamped rules; auditor applies them unchanged |
| Premature settlement | Corroboration account review | Reports state severity faced, never "proven" |

### Human-in-the-loop checkpoints

1. Hypothesis-space adequacy (are the rivals good?).
2. Test approval (resources, ethics).
3. Accepting exclusions and next-cycle direction (especially when a favored hypothesis dies).

### Inputs & outputs (chaining contract)

**Inputs:** candidate hypotheses (from [induction-abduction-analogy.md](induction-abduction-analogy.md), [grounded-theory.md](../research-methods/grounded-theory.md)); evidence base.
**Outputs:** exclusion log, corroborated survivors, next discriminating questions — feeding [bayesian-evidence-updating.md](bayesian-evidence-updating.md) (graded confidence), [experimental-design.md](../research-methods/experimental-design.md) (test execution), [reproducibility-open-science.md](reproducibility-open-science.md) (community verification).

## References & Further Reading

- Popper, K.R. (1959). *The Logic of Scientific Discovery.* Hutchinson. (orig. 1934)
- Popper, K.R. (1963). *Conjectures and Refutations.* Routledge.
- Platt, J.R. (1964). "Strong Inference." *Science*, 146(3642), 347–353.
- Chamberlin, T.C. (1890). "The Method of Multiple Working Hypotheses." *Science*, 15(366). (reprinted *Science* 1965, 148)
- Kuhn, T.S. (1962). *The Structure of Scientific Revolutions.* University of Chicago Press.
- Lakatos, I. (1970). "Falsification and the Methodology of Scientific Research Programmes." In Lakatos & Musgrave (eds.), *Criticism and the Growth of Knowledge.* Cambridge.
- Duhem, P. (1906/1954). *The Aim and Structure of Physical Theory.* Princeton.
- Quine, W.V.O. (1951). "Two Dogmas of Empiricism." *Philosophical Review*, 60.
- Mayo, D.G. (2018). *Statistical Inference as Severe Testing.* Cambridge. (modern severity formalization)
