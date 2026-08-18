---
name: decompose-research-question
description: "Breaks a question too large, vague or multi-part to answer directly into a MECE issue tree of atomic sub-questions — each mapped to the skill or research step that answers it, ordered by dependency, with a named method for recombining the answers. Use when a request would otherwise sprawl — \"help me understand the whole X landscape\", \"what's the future of Y and is it worth investing in?\", \"decompose this research question\", \"break this big question into parts before researching\". Not for structuring an answer already in hand — use `pyramid-principle`; not for a single factual lookup — use `grounded-answer`."
license: MIT
metadata:
  category: decision-strategy
  method: Issue-tree decomposition (MECE sub-questions with dependency order and a recombination plan)
  origin: Composite — Barbara Minto's MECE issue trees (1987) and Fermi-style decomposition (Weinstein & Adam, 2008)
  version: "2.0.0"
---
# Decompose Research Question

Before doing research, decide what research to do. This skill turns one unmanageable question into a tree of sub-questions each small enough to answer, mutually exclusive so no work is duplicated and collectively exhaustive so nothing load-bearing is missed — the MECE discipline Barbara Minto formalised for consulting analysis (*The Pyramid Principle*, 1987), applied to the questions rather than the finished argument, plus the Fermi habit of splitting an unanswerable quantity into estimable factors (Weinstein and Adam, 2008). It is a composite, not a canonical method. The failure it prevents is the sprawling non-answer: a broad question answered in one pass at uniform shallow depth, with no way to tell which part is weak.

## When to invoke

Invoke when:

- One sentence hides three or more distinct questions, or spans domains (technical × commercial × regulatory).
- The request is open-ended: "help me understand Y", "the future of Z?".
- A direct answer would run past ~2,000 words or need several methods to be credible.
- Work must be parallelised across people or agents and the split has to be clean.

Do NOT invoke when:

- The analysis is done and the *answer* needs structuring — use `pyramid-principle`.
- The question is a single factual lookup — use `grounded-answer`.
- The question is atomic and one method answers it; decomposing adds a layer, no insight.
- The question is unanswerable in principle (no data, pure speculation) — use `abstain-or-escalate`.
- The task is sizing a market, where the decomposition is standardised — use `estimate-market-size`.

## Procedure

### 1 — Restate the question, then confirm the reading

Write the question verbatim, then the interpretation being answered. These differ more often than not: "what's the future of agent frameworks?" may mean "which will still be maintained in three years?" or "which should we build on next quarter?". If the readings imply different trees, ask before decomposing — a well-built tree for the wrong question is the most expensive failure here.

### 2 — Choose the decomposition axis

Pick the axis that makes branches genuinely non-overlapping: **components** (5W+H — what, why, who, when, where, how — for broad "what about X?" questions, Kipling's six serving-men); **entity × dimension** for comparisons; **time slices** for "how will X evolve?"; **factors** where the answer is a product of estimable terms (Fermi); or **prerequisites** — "what must be answered before this can even start?" — for narrow analytical questions. Name the axis; mixing axes at one level is what makes trees overlap.

### 3 — Build the tree and test it for MECE

Draw the tree to at most two levels and check both halves of MECE at each level: siblings must not overlap (if two leaves would be answered with the same evidence, merge them) and together they must cover the parent (if a plausible answer to the parent is unreachable through any child, a branch is missing). Stop splitting when a leaf is atomic — one method or one search from an answer. Keep the tree to eight leaves or fewer; beyond that, recombination costs more than the decomposition saves and the question should become two research streams.

### 4 — Assign a method to every leaf

Every leaf gets a disposition: a named sibling skill, "direct research" where no skill fits, or "out of scope" with a reason. A leaf without one is a wish, not a plan. Where a leaf needs numbers, name the source class (registry, filing, published dataset) so it can be checked later.

### 5 — Order the leaves by dependency

Some leaves block others: "which frameworks exist?" must resolve before "how mature is each?". Mark each leaf's prerequisites, then group into waves — everything with no unmet prerequisite runs in parallel, the rest waits. If a blocking leaf resolves with low confidence, its dependents inherit that weakness and the answer must say so.

### 6 — Specify the recombination before any leaf runs

Say how leaf answers become the answer: a comparison matrix, a scenario set (`scenario-planning`), an evidence matrix (`analysis-of-competing-hypotheses`), a structured report (`write-imrad-report`) or a brief (`write-sbar-brief`). Decide now, because the recombination determines what each leaf must return — a matrix needs identical fields, a scenario set needs drivers. A tree with no recombination plan is a pile of fragments.

## Output template

```
## Decomposition — {original question}

Original question: {verbatim}
Restated as: {one-sentence interpretation being answered}
Axis: {components (5W+H) | entity × dimension | time slices | factors | prerequisites}

Tree:
- {sub-question 1} → {skill-name | direct research} — depends on: {none | leaf n}
- {sub-question 2} → {skill-name | direct research} — depends on: {none | leaf n}
- {sub-question 3} → {skill-name | direct research} — depends on: {none | leaf n}

Waves: wave 1 (parallel) {leaves}; wave 2 (after wave 1) {leaves}
MECE check: overlaps removed {…}; coverage gap checked against {what a complete answer needs}
Recombination: {matrix | scenarios | evidence matrix | report | brief} — each leaf returns {fields}
Stop conditions: {what would make the question unanswerable and trigger `abstain-or-escalate`}
```

Mandatory fields: the restated question, the axis, a disposition per leaf, the dependency waves and the recombination method. A tree missing dispositions or the recombination line does not go to execution.

## Worked example

Question: *"Should we invest in the foundation-model API space?"* — one sentence hiding five.

```
Original question: Should we invest in the foundation-model API space?
Restated as: Over a 3-year horizon, is a $20M position in foundation-model API vendors
             justified by market structure, competitive position and downside risk?
Axis: components (market × competition × maturity × size × risk)

Tree:
- What is the market structure and who captures margin? → `five-forces-analysis` — depends on: none
- Who are the vendors and how are they positioned? → `position-competitor` — depends on: none
- How big is the addressable market? → `estimate-market-size` — depends on: none
- Where is the category on the maturity curve? → `apply-hype-cycle` — depends on: none
- What could the market look like in 2029? → `scenario-planning` — depends on: leaves 1–4
- How could a $20M position fail? → `premortem-analysis` — depends on: leaf 5

Waves: wave 1 (parallel) leaves 1–4; wave 2 leaf 5; wave 3 leaf 6
MECE check: "who are the vendors" and "market structure" overlapped on concentration — 
             concentration assigned to leaf 1 only; coverage gap: regulation had no leaf,
             folded into leaf 5 as a scenario driver
Recombination: brief via `write-sbar-brief` — each leaf returns a claim, 2 numbers, a confidence
Stop conditions: if leaf 3 cannot produce top-down and bottom-up estimates within 3×,
             the investment question is unanswerable — escalate rather than guess
```

Six leaves, three waves, one recombination format. The MECE line is what makes this a tree rather than a list: the concentration overlap was removed and the missing regulatory branch was found by checking what a complete answer needs against the children.

## Verification

Before the plan goes to execution, confirm:

- [ ] The restated question was confirmed when it differed materially from the verbatim one.
- [ ] No two sibling leaves would be answered by the same evidence — check each pair for overlap.
- [ ] Every plausible answer to the parent is reachable through some leaf; name the coverage check.
- [ ] Every leaf has a disposition (skill, direct research, or out of scope with a reason).
- [ ] No wave contains a leaf whose prerequisite runs later — re-read the waves against the depends-on fields.
- [ ] The tree has eight leaves or fewer and the recombination names what each leaf must return.

## Pair with adjacent skills

- `pyramid-principle` — the mirror image: this structures the questions, that one the finished argument.
- `analysis-of-competing-hypotheses` — a recombination option when leaves produce rival explanations.
- `estimate-market-size` — the standard factor decomposition for sizing leaves.

- `scenario-planning` — recombines forward-looking leaves into branching futures.
- `grounded-answer` — the disposition for leaves that are plain factual lookups.
- `abstain-or-escalate` — when the tree shows the question cannot be answered with the evidence available.

## Anti-patterns

- Do **not** decompose an atomic question; a tree with one real leaf is overhead.
- Do **not** let sibling leaves overlap — duplicated evidence produces contradictory sub-answers.
- Do **not** leave a leaf without a disposition; that is where plans fail.
- Do **not** run dependent leaves alongside their prerequisites; they will assume facts they lack.
- Do **not** exceed eight leaves — split into two research streams instead.
- Do **not** defer the recombination decision; it determines what each leaf must return.

## Reference

- B. Minto, *The Pyramid Principle: Logic in Writing and Thinking*. London: Minto International, 1987 (rev. as *The Minto Pyramid Principle*, 1996, ISBN 0-9601910-3-8; 3rd ed. FT Prentice Hall, 2009) — MECE grouping and issue trees, developed at McKinsey & Company.
- L. Weinstein and J. A. Adam, *Guesstimation: Solving the World's Problems on the Back of a Cocktail Napkin*. Princeton University Press, 2008. ISBN 978-0-691-12949-5 — breaking an unanswerable quantity into estimable factors.
- O. Press et al., "Measuring and Narrowing the Compositionality Gap in Language Models," arXiv:2210.03350, 2022 (Findings of EMNLP 2023) — the self-ask prerequisite pattern used in step 2.
- T. Khot et al., "Decomposed Prompting: A Modular Approach for Solving Complex Tasks," arXiv:2210.02406, 2022 (ICLR 2023) — assigning each sub-task to a specialised solver, the basis of step 4.
- R. Kipling, "The Elephant's Child," in *Just So Stories*, 1902 — the "six honest serving-men" behind the 5W+H axis.
