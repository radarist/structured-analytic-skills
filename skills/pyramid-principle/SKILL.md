---
name: pyramid-principle
description: "Restructures an analytical document top-down using Minto's Pyramid Principle — a single governing thought at the apex, a MECE set of supporting arguments beneath it, evidence beneath those — and checks the vertical and horizontal logic of the result. Use when a document must persuade and currently rambles: \"what's the governing thought?\", \"structure this argument\", \"Minto pyramid\", \"execs say my memo buries the point\". Not for a one-page decision briefing in fixed SBAR sections (use `write-sbar-brief`) or for a research report's section order (`write-imrad-report`)."
license: MIT
metadata:
  category: writing
  method: The Pyramid Principle (governing thought, MECE support, SCQ framing)
  origin: Barbara Minto, McKinsey & Company; first published 1987
  version: "2.0.0"
---
# Pyramid Principle

The Pyramid Principle — Barbara Minto's method, first published 1987 (3rd ed., Pearson, 2009) — organises ideas so the reader meets the point first and the support afterwards. One governing thought sits at the apex; beneath it a small group of arguments that are mutually exclusive and collectively exhaustive (MECE); beneath each, its evidence. The core principle is that every idea summarises the ideas grouped below it, so each downward step answers the reader's "why?" and any tier read alone still carries the message. It prevents the document that narrates the analysis in the order it was done and reaches its conclusion on the last page — where a reader who stops early leaves with nothing and a skeptic cannot find which support is load-bearing.

## When to invoke

Invoke when:

- An analytical document must persuade — a memo, a board deck, a proposal — and the reader's attention is scarce.
- The request names the problem: "what's the governing thought?", "structure this argument", "Minto pyramid", "execs say my memo buries the point".
- A reviewer keeps asking "is that everything?" or "isn't that the same reason twice?".

Do NOT invoke when:

- The deliverable is a one-page decision briefing in fixed sections — use `write-sbar-brief` (SBAR); the pyramid still governs its Assessment.
- The deliverable is a research report with a conventional section order — use `write-imrad-report`; the pyramid may govern its Discussion, not the Methods/Results order.
- No single point exists yet because the analysis is unfinished — finish it, or decompose the question with `decompose-research-question`; structure cannot supply a conclusion.
- The task is testing whether the conclusion survives attack — use `red-team-claim`, or `key-assumptions-check` for its premises.

## Procedure

### 1 — Write the governing thought

Force the document into one sentence answering the reader's question. Test it three ways: point or topic ("our cloud strategy" is a topic; "migrate to managed cloud in Q3 to cut infrastructure cost 30% before the renewal cliff" is a point); does it survive "so what?"; does it answer the reader's actual question? If it cannot be written in one sentence, the analysis is unfinished.

### 2 — Build the second tier as a MECE group of answers to "why?"

Ask why the governing thought is true and list the reasons. Then enforce MECE: mutually exclusive, so no two restate each other (overlapping support double-counts); collectively exhaustive, so together they establish the apex (a gap is where a skeptic walks in). Aim for about three — two often forces a false binary, five or more means grouping has not happened, so combine into higher-level reasons with sub-points below.

### 3 — Support each argument down to self-evident evidence

For each second-tier reason ask "why is *this* true?" and supply data, examples or sub-arguments. This recursion is the engine: every tier is the "why" of the tier above, and each idea summarises what sits beneath it. Stop descending when a claim is self-evidently backed for this audience — a tier restating what the reader already accepts wastes the attention the structure was built to save.

### 4 — Check the vertical logic

Read each path from apex to leaf. Every downward step must answer "why?" of the step above; every upward step must genuinely summarise the group below. Where a path breaks — evidence that does not support its reason, a reason that does not establish the apex — the fault is the logic, not the wording; fix the argument, not the transition.

### 5 — Check the horizontal logic

Within a tier, items must be parallel — same abstraction, same grammatical form — and ordered by a logic the reader can predict: priority, time, or cause to effect. A tier mixing a cost reason, a process reason and an anecdote is not parallel; re-cut it. Predictable order makes a structure feel inevitable rather than arbitrary.

### 6 — Add the SCQ opening when the reader needs orienting

For a reader without context, open with Minto's Situation–Complication–Question framing before the apex lands: Situation, the common ground already accepted; Complication, what changed; Question, the question the complication raises in the reader's mind — answered by the governing thought (the four moves together are commonly written SCQA). For a reader already inside the problem, go straight to the apex.

## Output template

```
## Pyramid — {document or argument}

**Governing thought (apex):** {one-sentence point that survives "so what?"}

**Second tier — the whys (MECE):**
1. {reason A}
2. {reason B}
3. {reason C}

**Evidence:**
- Under A: {data, examples or sub-arguments}
- Under B / C: {…}

**MECE check:** {overlaps merged; gaps closed — name each and how}
**Vertical check:** {each downward step answers "why?"; each idea summarises the group below}
**Horizontal check:** {tier parallel; ordered by {priority | time | cause→effect}}
**SCQ opening (if used):** S: {…} | C: {…} | Q: {…} → A: {apex}
```

The governing thought, the second tier and the three checks are mandatory: without the MECE, vertical and horizontal checks it is an outline, not a structured argument.

## Worked example

An engineering organisation deciding whether to consolidate three internal CI systems into one. Illustrative figures:

```
## Pyramid — "Consolidate CI onto one platform"

**Governing thought (apex):** Consolidate all three CI systems onto the platform team's
service by end of Q3.

**Second tier — the whys (MECE):**
1. Cost: three systems triple licence and maintenance spend for identical capability.
2. Velocity: engineers lose ~2 hours a week switching between three pipeline syntaxes.
3. Risk: two systems have a single maintainer each — one resignation stops releases.

**Evidence:**
- Under A: $210k/yr licences plus 1.5 FTE maintenance across three systems, against
  $80k/yr plus 0.8 FTE consolidated.
- Under B: onboarding survey — median engineer touches 2.3 pipeline systems; 61% name
  re-learning syntax as a top-three friction.
- Under C: both legacy systems' commit graphs show one active maintainer; the March
  bus-factor incident halted releases for 3 days.

**MECE check:** cost, velocity and risk do not overlap; "developer preference" folded into
velocity as switching cost rather than left as a fourth pillar.
**Vertical check:** each reason answers "why consolidate?"; each evidence item answers
"why is that reason true?"
**Horizontal check:** three reasons, parallel in form, ordered by decision weight — the
CFO is in the room, so cost leads.
**SCQ opening (if used):** S: three CI systems grew organically | C: spend and incidents
rising | Q: consolidate or keep three? → A: consolidate by end of Q3
```

Note what the checks caught: "developer preference" started as a fourth reason but was not exclusive of velocity — the same switching cost stated as a feeling — so keeping it would double-count. The horizontal order is a choice too: for platform engineers, risk would lead and cost come third.

## Verification

- [ ] The apex is a point, not a topic: answer "so what?" against it — if an answer remains, it is not yet the governing thought.
- [ ] Cover the apex and read the second tier alone; it must argue something specific, not list themes.
- [ ] Test each pair of reasons for overlap and ask what a skeptic could raise that none covers — record how each was resolved.
- [ ] Walk every path from apex to evidence, confirming each downward step answers "why?" of the step above.
- [ ] Confirm each tier is parallel in form and abstraction and ordered by one stated logic.
- [ ] Confirm the count: three second-tier arguments, or a stated reason for two, four or more.

## Pair with adjacent skills

- `write-sbar-brief` — SBAR is the short container; the pyramid is the geometry inside its Assessment and Recommendation.
- `write-imrad-report` — the pyramid governs the Discussion's argument; IMRAD the section order around it.
- `red-team-claim` — attack the apex and each reason; pyramids fail at the apex or a weak support, rarely between.
- `key-assumptions-check` — audit the premises beneath each reason once the structure exposes them.
- `critique-report` — pre-delivery review of the finished document.

## Anti-patterns

- Do **not** put a topic where the apex belongs; no reader can act on "an analysis of our options".
- Do **not** build bottom-up toward a surprise ending. Analytical writing leads with the answer; withholding it reads as evasive.
- Do **not** let the second tier overlap or leave a gap; non-MECE support looks thorough and collapses under questioning.
- Do **not** carry five or seven second-tier arguments; that many means grouping was skipped — find the higher-level reasons and demote the rest.
- Do **not** borrow a MECE cut ("people, process, technology") the substance did not produce; a cut that does not fit is decoration.
- Do **not** substitute structure for a point. A flawless pyramid with no real apex is polished emptiness — fix the analysis first.

## Reference

- B. Minto, *The Pyramid Principle: Logic in Writing and Thinking*, 3rd ed. Harlow, U.K.: Pearson Education (Financial Times Prentice Hall), 2009, 177 pp. ISBN 978-0-273-71051-6 — governing thought, MECE grouping, vertical and horizontal logic; first published 1987; the method comes from Minto's McKinsey years (she left in 1973).
- B. Minto, *The Minto Pyramid Principle: Logic in Writing, Thinking and Problem Solving*, Minto International, 1996 — the author's expanded edition, superseding the 1987 text on the problem-solving material.
- B. Minto, "The Minto Pyramid Principle." barbaraminto.com. Accessed: Aug. 16, 2026. [Online]. Available: https://www.barbaraminto.com/ — the author's statement of the publication history and the Situation–Complication–Question framework.
