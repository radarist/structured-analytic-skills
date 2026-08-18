---
name: cynefin-classification
description: "Classifies a decision situation into one of Cynefin's five contexts — Clear, Complicated, Complex, Chaotic or Disorder — and names the matching decision mode, so recommendations are framed as playbooks, expert analysis, safe-to-fail probes or stabilising action. Use before advising action under uncertainty — \"classify this with Cynefin\", \"is there a best practice here or is this new territory?\", \"what kind of problem is this — known, knowable, or emergent?\", \"nobody agrees which kind of problem this even is\". Not for enumerating a chosen plan's failure modes (use `premortem-analysis`) or designing the probe itself (use `cheapest-experiment`)."
license: MIT
metadata:
  category: decision-strategy
  method: Cynefin framework
  origin: David J. Snowden and Mary E. Boone, 2007 (Harvard Business Review); Cynefin Co renames, 2020
  version: "2.0.0"
---
# Cynefin Classification

Cynefin sorts a situation by its kind of cause-and-effect relationship, because each kind rewards a different way of deciding — applying the wrong one is how competent leaders fail in unfamiliar territory. Snowden and Boone set out the framework in "A Leader's Framework for Decision Making" (*Harvard Business Review*, 2007), naming **five** contexts: Clear (called Simple in 2007, renamed by the Cynefin Co in 2020), Complicated, Complex, Chaotic, and **Disorder** — where it is unclear which of the other four applies, renamed Confused / Aporetic (A/C) in 2020. It prevents treating a Complex situation as Complicated: hiring an expert to "analyse and answer" a question whose causation is only visible in hindsight, dressing untested hypotheses as best practice.

## When to invoke

Invoke when:

- Action is about to be recommended in an unfamiliar, fast-moving or contested space — new regulation, emerging technology, a novel business model — and the framing (answer vs experiment) is unsettled.
- Someone asks "what's the best practice here?", "should we copy what worked at a peer?", or "how do we navigate this?" in a domain where no playbook may exist.
- Recommendations are in fact probes but are written as commitments, or a review found a Complex problem handled as a Complicated one.

Do NOT invoke when:

- The brief is purely descriptive — for industry structure use `five-forces-analysis`, for a market map `position-competitor`.
- A course of action is already chosen and its failure modes are the question — use `premortem-analysis`.
- The domain is settled and what is needed is the probe or pilot design itself — use `cheapest-experiment`.
- The question is how an environment could evolve over years rather than what kind of problem it is now — use `scenario-planning`.

## Procedure — classify, name the mode, state the implication

### 1 — Classify the context

Work the diagnostic questions in order and pick exactly one context:

| Context | Causation | Diagnostic question | Decision mode |
|---|---|---|---|
| **Clear** (Simple, 2007) | Obvious to everyone; the realm of known knowns | Is the right answer self-evident and undisputed? | sense – categorise – respond |
| **Complicated** | A clear cause-and-effect relationship exists but not everyone can see it; known unknowns | Can experts discover the answer with analysis and effort? | sense – analyse – respond |
| **Complex** | Right answers cannot be ferreted out; patterns emerge only in retrospect; unknown unknowns | Will the causation only be legible afterwards? | probe – sense – respond |
| **Chaotic** | No manageable patterns; relationships shift constantly; unknowables | Is the situation acutely unstable and demanding immediate action? | act – sense – respond |
| **Disorder** (Confused / Aporetic, 2020) | It is unclear which of the other four applies | Are people arguing past each other from different implicit contexts? | break the situation into its constituent parts and assign each to one of the other four |

Snowden and Boone's rule for Disorder is explicit: "the way out is to break the situation into its constituent parts and assign each to one of the other four realms". Never act from the centre — a decision taken while in Disorder defaults to whatever mode the loudest participant is most comfortable with.

### 2 — Name the matching decision mode

State the mode, not just the context — the mode changes how the reader consumes the recommendations: Clear → apply the documented playbook; Complicated → commission expert analysis and expect several defensible answers; Complex → run safe-to-fail experiments, amplify what works, dampen what does not; Chaotic → act first to establish order, sense where stability appears, then move the situation towards Complex. Write it as a contrast where the mismatch is live: "the right mode here is probe – sense – respond, not sense – analyse – respond".

### 3 — Split, if the answer was Disorder

When the classification is Disorder, decompose the situation into named parts and classify each separately, then report the parts and their contexts rather than one label. A situation that cannot be decomposed is still Disorder and the honest output says so, along with what information would resolve it.

### 4 — State the implication and check for consistency

Write one sentence telling the reader how to consume the rest of the analysis given the context — for Complex, that the recommendations are hypotheses to falsify, each needing a readout date. Then check the recommendations actually match: if the classification says Complex but the text says "the proven approach", either the wording or the classification is wrong. Do not hedge across two contexts; if the choice is genuinely impossible, that is Disorder, which has its own rule.

## Output template

```
**Decision context:** {Clear | Complicated | Complex | Chaotic | Disorder} — {one-line reason keyed to causation}
**Decision mode:** {sense-categorise-respond | sense-analyse-respond | probe-sense-respond | act-sense-respond | decompose-and-assign}
**Implication:** {one sentence on how to read the recommendations that follow}
```

For Disorder, the decomposition is mandatory and replaces the single-context line:

```
**Decision context:** Disorder — {why no single context governs}
**Parts:**
- {part 1} → {context} → {mode}
- {part 2} → {context} → {mode}
**Implication:** {how each part is to be handled; what would resolve the remaining ambiguity}
```

All three fields are mandatory; a context without its decision mode is decorative, and a recommendation set that contradicts the stated mode must be rewritten before it ships.

## Worked example

Illustrative case: in March 2027 Meridian Bank, a mid-size European lender with 4,200 staff, must respond to a regulator's new consultation paper on AI in credit decisions. No compliance practice exists yet; three peer banks have taken visibly different positions; two internal pilots produced contradictory results — a 12 % improvement in default prediction on one portfolio and a 3 % degradation on another.

The naive reading is Complicated: hire a Big Four adviser to analyse the paper and produce the answer. The diagnostic says otherwise — no playbook exists, peer responses diverge, and the pilot results only make sense in retrospect, so causation is visible only afterwards.

```
**Decision context:** Complex — brand-new regulation, no established practice, divergent peer responses, contradictory pilot results
**Decision mode:** probe-sense-respond
**Implication:** the options below are safe-to-fail probes, not a compliance plan; each carries a readout date and a dampening rule, and none should be scaled before its readout.
```

Calibration contrast: had the question been "implement the controls the regulator finalised in 2025", the context would be **Complicated** (expert analysis of known rules, sense-analyse-respond); "apply the published control checklist to a standard mortgage product" would be **Clear**. Had the bank instead been mid-incident with a live model outage across all lending, it would be **Chaotic** — act first to restore a manual process, then reclassify.

## Verification

Before the classification ships:

- [ ] Exactly one of the five contexts is named, with a reason keyed to the kind of causation — no "between Complicated and Complex" hedges.
- [ ] The decision mode matching that context is stated verbatim (sense-categorise-respond, sense-analyse-respond, probe-sense-respond, act-sense-respond, or decompose-and-assign for Disorder).
- [ ] Cross-check the recommendations against the mode: a Complex classification must not carry "best practice" or "the proven approach" wording, and a Clear classification must not read as a set of experiments.
- [ ] If the context is Disorder, the decomposition into parts with their own contexts is present — no decision is taken from the centre.
- [ ] Chaotic classifications name the stabilising action first and say what would move the situation to Complex.

## Pair with adjacent skills

- `cheapest-experiment` — designs the probe once the context says probe-sense-respond; a Complex classification without bounded, safe-to-fail probes is unfinished.
- `premortem-analysis` — assumes a path is chosen; Cynefin asks whether that kind of bet is even the right kind for the context.
- `key-assumptions-check` — surfaces the premises behind a Complicated-domain expert analysis.
- `three-horizons` — the far-horizon bets in a portfolio are usually Complex, near-horizon ones Clear or Complicated.
- `evolution-stage` — early-stage components sit in Complex territory; commodity components are Clear.

## Anti-patterns

- Do **not** classify as Complicated to flatter the analysis. Most emerging-technology and new-regulation briefs are Complex; defaulting to Complicated lets a report sound expert without the honest uncertainty.
- Do **not** hedge between two contexts. Picking is the work; genuine inability to pick is Disorder, which has its own rule — decompose and assign, never act from the centre.
- Do **not** name a context without its decision mode; the mode is what changes the reader's behaviour.
- Do **not** write Complicated-mode language ("the proven approach") under a Complex classification.
- Do **not** treat a Complex classification as licence for unbounded experiments — probes are small, fast and safe to fail.

## Reference

- D. J. Snowden and M. E. Boone, "A Leader's Framework for Decision Making," *Harvard Business Review*, vol. 85, no. 11, pp. 68–76, Nov. 2007. PMID 18159787. https://hbr.org/2007/11/a-leaders-framework-for-decision-making — the five contexts, their decision modes and the Disorder rule.
- C. F. Kurtz and D. J. Snowden, "The new dynamics of strategy: Sense-making in a complex and complicated world," *IBM Systems Journal*, vol. 42, no. 3, pp. 462–483, 2003. doi:10.1147/sj.423.0462 — the original Cynefin paper.
- D. Snowden, "Cynefin St David's Day 2020," parts 1 and 2 of 5, The Cynefin Co, Mar. 2020 — part 1 introduces both Obvious→Clear and Disorder→A/C (Aporetic or Confused), https://thecynefin.co/cynefin-st-davids-day-2020-cynefin-framework/; part 2 elaborates the A/C terminology, https://thecynefin.co/cynefin-st-davids-day-2020-2-of-n/.
