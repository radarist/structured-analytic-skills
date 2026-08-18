---
name: skill-name-here
description: "Third person, one or two sentences: what the skill does, then when to reach for it, with two to four quoted trigger phrases a user would actually type — \"score this on TRL\", \"is this claim safe to ship?\". Route the near misses explicitly: not for {adjacent situation} (use `sibling-skill`). No workflow summary, no angle brackets, 700 characters maximum."
license: MIT
metadata:
  category: decision-strategy
  method: Canonical method name as its originator wrote it
  origin: Originator(s), institution, year
  version: "1.0.0"
---
# Method Name

{One paragraph, three to six sentences. What the method is; who published it and when; the core principle that makes it work; and — this is the part that earns the skill — the specific failure it prevents. Name the mechanism, not the benefit: "forces every hypothesis to be tested against every item of evidence, so the analyst cannot quietly drop the one that does not fit" beats "improves rigour".}

## When to invoke

Invoke when:

- {A symptom the user reports, in their words, not the method's.}
- {A situation in the material itself — a shape of problem, not a request.}
- {A phrase a user types: "…".}

Do NOT invoke when:

- {The near miss that belongs to a sibling} — use `sibling-skill-one`.
- {The other near miss} — use `sibling-skill-two`.
- {The case where no skill applies and the honest answer is to say so} — use `abstain-or-escalate`.

## Procedure

### 1 — {Imperative naming the first move}

{What the agent does, on what input, producing what. Two to five sentences. State the rule the step enforces and what to do when the input will not support it. Use the method's own vocabulary and scale labels; never re-letter or re-number a published scale.}

### 2 — {Imperative naming the second move}

{As above. If a step is arithmetic, it belongs in `scripts/`, not in prose the agent must compute in its head.}

### 3 — {Imperative naming the third move}

{As above. Most skills land between four and eight steps.}

### 4 — {The step that produces the deliverable}

{Fill the output template, then run the verification checklist below before anything ships.}

## Output template

```
# {Deliverable title}: {subject} — {date}

## {Section one}
{placeholder describing what goes here, with its cap or unit}

## {Section two}
| {Column} | {Column} | {Column} |
|---|---|---|
| {value} | {value} | {value} |

## {Judgement}
- **{Field}:** {value} — {one-line justification}
- **Confidence:** {high | medium | low} — {what it rests on, what would change it}
```

{Mandatory fields: name them here and say what a reader may conclude when one is missing — "an assessment without the confidence line cannot be weighed against what the reader already knows."}

## Worked example

{One example, concrete, with real names and real numbers — an illustrative case with invented figures is fine if it is labelled as such. Prefer the originator's own published example where one exists, quoted and cited. Walk the numbers through the procedure so a reader can reproduce them; if the skill ships a companion tool, the numbers here must be the tool's output.}

## Verification

- [ ] {A check on the output's structure: every mandatory field present, in order.}
- [ ] {A check on fidelity: the published labels, scales and step order are unchanged.}
- [ ] {A check on the arithmetic, reproduced with the companion tool where one exists.}
- [ ] {A check on the reasoning: the conclusion follows, and what would overturn it is stated.}
- [ ] {A check on the boundary: nothing has been asserted that the input did not support.}

## Companion tool

{Delete this whole section if `scripts/` does not exist.}

`scripts/{tool}.py` computes {what}, implementing {definition, with citation}.

```bash
python3 scripts/{tool}.py {subcommand} --file {input}.json   # {what it prints}
python3 scripts/{tool}.py --selftest                         # hand-verified assertions
python3 scripts/{tool}.py --demo                             # reproduces the worked example
```

```
{sample output, copied verbatim from a real run}
```

## Pair with adjacent skills

- `sibling-skill-one` — {what it does before or after this one, and why the handover matters}.
- `sibling-skill-two` — {the same}.
- Methodology counterpart: [methodologies/{category}/{file}.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/{category}/{file}.md) — {what the longer treatment adds}. Link methodology files by absolute URL: a skill directory is copied out of this repository on install, so a `../../` path dangles for every installed user.

## Anti-patterns

- Do **not** {the specific misuse that produces a plausible-looking wrong answer}.
- Do **not** {the shortcut that silently drops the method's discipline}.
- Do **not** {the presentation failure — false precision, buried uncertainty, a menu instead of a judgement}.

## Reference

- {Author initials and surname, "Title," *Venue*, vol., no., pp., year, doi: — the canonical publication, with a clause saying which part of this skill it supports.}
- {Second source, if the skill leans on more than one — a standard, a guidebook, a replication.}
