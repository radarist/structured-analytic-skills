# Evaluation Rubric — skill-library

This rubric scores the two artifact types in this repository: **skills** (`skills/*/SKILL.md`)
and **methodology files** (`methodologies/<category>/*.md`). It is used for the
before/after evaluation recorded in `scores-before.md`, `scores-after.md`, and `report.md`.

## How to score

- Score each criterion **0, 1, or 2** against the anchors below. Use only the anchors —
  do not invent extra criteria and do not average "vibes".
- Weighted points per criterion = `(raw / 2) × weight`. Totals are out of **100**.
- Score what is **in the file**, not what could be inferred. A missing section scores 0
  for its criteria even if the content exists elsewhere in the repo.
- Be candid: a 2 means "as good as this repo's best exemplar"; most files should not
  sweep the board.
- Report per file: the 10 raw scores, the weighted total, and the **top-2 concrete gaps**
  (one short phrase each, actionable).

---

## Rubric A — Skills (100 pts)

House style reference: frontmatter (`name`, `description`), then prose sections —
typically `## When to invoke`, procedure steps, `## Anti-patterns`, `## Reference`.

| # | Criterion | Weight | 0 | 1 | 2 |
|---|---|---|---|---|---|
| S1 | **Trigger quality** — frontmatter `description` names concrete invocation phrases/questions and the decision the skill supports | 10 | vague or missing description | describes the method but few/no trigger phrases | rich trigger phrases + what the skill decides/produces |
| S2 | **Method fidelity & provenance** — implements a recognizable published method; canonical source cited accurately (author, year, venue) | 15 | no identifiable method or source | method named, partial/loose citation | faithful to the published method + accurate canonical citation(s) |
| S3 | **Procedural actionability** — numbered, ordered steps an agent can execute without further research | 15 | no procedure | steps exist but abstract/under-specified | concrete ordered steps with inputs and per-step artifacts |
| S4 | **Output template** — a copy-ready emit format for the result | 10 | none | partial structure described in prose | fenced/structured fill-in template present |
| S5 | **Anti-patterns / failure modes** — explicit "do not" list tied to real misuse | 10 | none | generic cautions | specific, method-true anti-patterns |
| S6 | **Boundaries** — when NOT to use; routing to sibling skills for out-of-scope cases | 10 | none | implicit boundaries only | explicit skip-for list with named sibling routing |
| S7 | **Cross-linking** — `## Pair with` (or equivalent) linking related skills; methodology counterpart linked where one exists | 10 | no links | some links, or one direction only | links both to sibling skills and to any `methodologies/` counterpart (relative path) |
| S8 | **Worked-example concreteness** — at least one fully worked example or filled-in illustration (numbers, names, not just placeholders) | 10 | none | partial example or toy fragment | complete worked example a reader could imitate |
| S9 | **Verification hooks** — tells the agent how the output gets checked (verifier pass, recomputation, quote-anchoring, scoring) | 5 | none | mentioned loosely | concrete check procedure named |
| S10 | **Computation tooling** — for skills with real math: a runnable companion tool, documented in the SKILL.md; for non-computational skills score 2 by default (criterion not applicable) | 5 | math described in prose only, no tool | tool exists but undocumented/untested | stdlib-only tool with `--selftest`, documented in SKILL.md |

## Rubric B — Methodology files (100 pts)

Template reference: `methodologies/_TEMPLATE.md` (12 sections + Agent Adaptation with 8
mandatory subsections).

| # | Criterion | Weight | 0 | 1 | 2 |
|---|---|---|---|---|---|
| M1 | **Frontmatter compliance** — name, category, origin, agent_suitability, tags, related; valid per template | 10 | missing/invalid | partial fields | all fields, correct category values |
| M2 | **Origin & history accuracy** — founders, key publications with years; no fabricated citations | 15 | missing or errors found | present but thin/unchecked | specific, plausible, verifiable names/years/titles |
| M3 | **Core concepts glossary** — term/definition table covering the method's vocabulary | 10 | absent | partial glossary | complete, precise glossary table |
| M4 | **When / when-not** — concrete contexts, scale, data needs on both sides | 10 | absent or one-sided | generic lists | concrete, decision-ready lists |
| M5 | **Process detail** — numbered steps with participants, timeframes, inputs, artifact per step | 15 | absent | steps without artifacts | full step detail with artifacts |
| M6 | **Strengths & limitations candor** — table + honest commentary, no overselling | 10 | absent | table only, boosterish | candid table + commentary incl. real failure cases |
| M7 | **Worked examples** — 1–3 real, documented applications (named org/project + outcome) | 10 | none | unnamed/generic examples | named, documented cases with outcomes |
| M8 | **Variants & cross-links** — variants listed; relative links to sibling methodology files; skill counterpart linked where one exists | 10 | none | variants or links, not both | variants + working relative links incl. any `skills/` counterpart |
| M9 | **Agent Adaptation completeness** — all 8 mandatory subsections, practical and copy-ready (workflow table, pipeline with artifacts, 2–4 prompt templates, tools, failure-mode table, human gates, I/O contract) | 15 | missing section | some subsections | all 8, concrete and usable |
| M10 | **References quality** — canonical works by author/year/title; links only where canonical/stable; nothing invented | 5 | missing or fabricated-looking | partial | complete, accurate, conservative with URLs |

Depth commentary (not scored): the template targets ~400–700 lines; current files run
~178–207. Note this as commentary in the report; do not deduct points for it.

## Aggregation

- Report per-file totals and per-category means (skills by README category; methodologies
  by directory).
- Track criterion-level means across each population — that is what shows systematic gaps
  (e.g., S7 cross-linking near zero before the improvement pass).
