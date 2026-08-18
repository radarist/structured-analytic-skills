# Evaluation rubric v2 — deterministic, multidimensional

Every number this library reports about itself is produced by `evaluation/score_skills.py`
from mechanical checks — regexes over `SKILL.md`, file-system facts, and subprocess runs
of the companion tools. No model and no human judgement is in the loop, so two runs on
the same tree give byte-identical results and every lost point maps to a named check you
can fix. (The judgement-based v1 rubric and its scoresheets are kept under
`history/2026-08-v1/` for the record.)

The design borrows from the 2026 state of practice: spec-exact frontmatter (agentskills.io),
Anthropic's authoring checklist (specific descriptions, <500-line bodies, progressive
disclosure, worked examples, feedback loops), trigger evals with near-miss negatives and a
lexical rank-1 gate (addyosmani/agent-skills, microsoft/skills), token budgets and link
integrity (skill-validator, trailofbits/skills), and paired eval cases living with each
skill (anthropics/skills `skill-creator`).

## Scores

- **Skill score (0–100)** = Σ over 12 dimensions of `dimension_score × weight / 100`.
  A dimension's score is `points earned / points available × 100` from its checks.
- **Library score (0–100)** = `0.85 × mean(skill scores) + 0.15 × repo-hygiene score`.
- Also reported: median and minimum skill score, per-dimension means, checks passed /
  total, the most-failed checks, and the trigger-eval metrics (positive rank-1 rate, MRR,
  negatives held).

## Dimensions and weights

| Dimension | Weight | What it measures |
|---|---|---|
| D1 spec | 10 | Agent Skills spec compliance: frontmatter parses, `name` = directory and matches `^[a-z0-9]+(-[a-z0-9]+)*$` (≤64), `description` present and ≤1024 chars, only spec-allowed keys (`name, description, license, compatibility, metadata, allowed-tools`), body ≤500 lines, H1 present, no CRLF/tabs. |
| D2 discoverability | 12 | The description routes real requests: explicit "Use when…" trigger clause; third person; ≥2 quoted/backticked trigger phrases; states what it produces; 200–700 chars; names a near-miss it does *not* cover; TF-IDF nearest-neighbour similarity < 0.45 (not confusable with a sibling); non-generic name; `evals/evals.json` has ≥3 positive and ≥1 negative case; **all positive cases rank 1 and all negatives do not** in the BM25 trigger eval. |
| D3 procedure | 12 | ≥3 numbered, consecutively ordered steps under a procedure heading; mean ≥30 words per step; no empty steps. |
| D4 output | 10 | A section that names the output holds a fenced, copy-ready template (≥3 lines) using `{placeholders}`, `<slots>` or JSON keys; mandatory fields are named. |
| D5 boundaries | 8 | Explicit do-not-invoke / skip-for cases, and at least one resolving sibling skill named as the route for out-of-scope requests. |
| D6 crosslinks | 8 | A "Pair with" section naming ≥2 resolving siblings; no dangling skill references; where a same-named methodology file exists, the skill links to it and it links back. |
| D7 example | 10 | A worked-example section that is substantive (≥120 words), concrete (≥12 digits, ≥6 named entities), structured (table or fenced output), and — where a companion tool exists — reproduced with it. |
| D8 verification | 8 | A verification/self-check section with ≥3 checklist items or verification sentences (recompute, cross-check, must resolve …). |
| D9 provenance | 8 | A reference section with at least one dated entry, an attributable author/organisation, a locator (DOI, ISBN, URL, vol./pp.), and the originator dated in the body. |
| D10 tooling | 8 | For skills whose method has real arithmetic (explicit list `COMPUTATIONAL_SKILLS` in the scorer): a `scripts/*.py` that passes `--selftest`, prints usage on `--help`, is byte-for-byte deterministic across two runs, is referenced from SKILL.md, imports only the standard library, and has a docstring. Non-computational skills score N/A = full. |
| D11 efficiency | 3 | Body ≤1,600 words (partial credit to 3,200; a `references/` directory earns progressive-disclosure credit), no duplicate headings, ≤500 lines. |
| D12 hygiene | 3 | Self-contained (no origin-system tools/personas/paths — `check_repo.py` denylist), no origin jargon, relative links resolve, heading levels do not skip, no TODO/TBD placeholders, balanced code fences. |

Repo-hygiene checks (15 % of the library score): README catalog lists every skill; LICENSE,
CONTRIBUTING, CHANGELOG, CITATION.cff, SECURITY, CODE_OF_CONDUCT present; CI workflow;
generated `index.json` matches the skills on disk; plugin manifest; `.gitignore`; no junk
files; `check_repo.py` passes (including canonical eval fixtures and generated
`agents/openai.yaml` metadata); rubric present.

## Check catalogue

Regenerate with `python3 evaluation/score_skills.py --list-checks`.

| Dimension | Weight | Check | Points |
|---|---|---|---|
| D1_spec | 10 | `D1.frontmatter-parses` | 3 |
| D1_spec | 10 | `D1.name-present` | 2 |
| D1_spec | 10 | `D1.name-matches-dir` | 2 |
| D1_spec | 10 | `D1.name-format` | 2 |
| D1_spec | 10 | `D1.description-present` | 3 |
| D1_spec | 10 | `D1.description-length` | 2 |
| D1_spec | 10 | `D1.no-unknown-keys` | 2 |
| D1_spec | 10 | `D1.body-under-500-lines` | 2 |
| D1_spec | 10 | `D1.has-h1-title` | 1 |
| D1_spec | 10 | `D1.no-crlf-tabs` | 1 |
| D2_discoverability | 12 | `D2.trigger-clause` | 3 |
| D2_discoverability | 12 | `D2.third-person` | 3 |
| D2_discoverability | 12 | `D2.concrete-triggers` | 3 |
| D2_discoverability | 12 | `D2.states-output` | 2 |
| D2_discoverability | 12 | `D2.length-band` | 2 |
| D2_discoverability | 12 | `D2.exclusion-clause` | 1 |
| D2_discoverability | 12 | `D2.discriminable` | 3 |
| D2_discoverability | 12 | `D2.name-not-generic` | 1 |
| D2_discoverability | 12 | `D2.eval-cases-present` | 2 |
| D2_discoverability | 12 | `D2.trigger-rank1` | 3 |
| D3_procedure | 12 | `D3.has-3plus-steps` | 4 |
| D3_procedure | 12 | `D3.steps-ordered` | 2 |
| D3_procedure | 12 | `D3.steps-substantive` | 3 |
| D3_procedure | 12 | `D3.no-empty-steps` | 1 |
| D3_procedure | 12 | `D3.procedure-heading` | 2 |
| D4_output | 10 | `D4.output-section` | 3 |
| D4_output | 10 | `D4.fenced-template` | 4 |
| D4_output | 10 | `D4.placeholders-or-schema` | 2 |
| D4_output | 10 | `D4.mandatory-fields-named` | 1 |
| D5_boundaries | 8 | `D5.negative-triggers` | 4 |
| D5_boundaries | 8 | `D5.sibling-routing` | 4 |
| D6_crosslinks | 8 | `D6.pair-with-section` | 2 |
| D6_crosslinks | 8 | `D6.two-plus-siblings` | 3 |
| D6_crosslinks | 8 | `D6.no-dangling-skill-refs` | 1 |
| D6_crosslinks | 8 | `D6.methodology-link` | 1 |
| D6_crosslinks | 8 | `D6.methodology-backlink` | 1 |
| D7_example | 10 | `D7.example-section` | 3 |
| D7_example | 10 | `D7.concrete-numbers` | 2 |
| D7_example | 10 | `D7.named-entities` | 1 |
| D7_example | 10 | `D7.example-substantive` | 2 |
| D7_example | 10 | `D7.structured-example` | 1 |
| D7_example | 10 | `D7.tool-verified` | 1 |
| D8_verification | 8 | `D8.verification-section` | 4 |
| D8_verification | 8 | `D8.concrete-checks` | 3 |
| D8_verification | 8 | `D8.checklist-form` | 1 |
| D9_provenance | 8 | `D9.reference-section` | 3 |
| D9_provenance | 8 | `D9.dated-entry` | 2 |
| D9_provenance | 8 | `D9.attributable-entry` | 1 |
| D9_provenance | 8 | `D9.locator` | 1 |
| D9_provenance | 8 | `D9.originator-in-body` | 1 |
| D10_tooling | 8 | `D10.tool-present` | 2 |
| D10_tooling | 8 | `D10.selftest` | 2 |
| D10_tooling | 8 | `D10.help` | 1 |
| D10_tooling | 8 | `D10.deterministic` | 1 |
| D10_tooling | 8 | `D10.documented` | 1 |
| D10_tooling | 8 | `D10.stdlib-only` | 0.5 |
| D10_tooling | 8 | `D10.docstring` | 0.5 |
| D11_efficiency | 3 | `D11.word-budget` | 3 |
| D11_efficiency | 3 | `D11.no-duplicate-headings` | 1 |
| D11_efficiency | 3 | `D11.line-budget` | 1 |
| D12_hygiene | 3 | `D12.self-contained` | 3 |
| D12_hygiene | 3 | `D12.no-origin-jargon` | 2 |
| D12_hygiene | 3 | `D12.links-resolve` | 2 |
| D12_hygiene | 3 | `D12.heading-hierarchy` | 1 |
| D12_hygiene | 3 | `D12.no-placeholders` | 1 |
| D12_hygiene | 3 | `D12.fences-balanced` | 1 |

## What the scorer deliberately does not measure

Whether the *content* of a step is true to the published method, whether a citation
really says what the skill claims, and whether an agent following the skill produces a
better answer. Those need sources and models: the fidelity audit in `report.md` covers the
first two (source-by-source, with URLs), and the per-skill `evals/evals.json` cases are
written to be runnable with model-based harnesses (`claude plugin eval`, the
anthropics/skills `skill-creator` loop) for the third. A high deterministic score is a
necessary condition for a good skill, not a sufficient one — which is why the two are
reported side by side.

## Trigger (discoverability) eval

`evaluation/trigger_eval.py` builds a BM25 index over each skill's `name` + `description`
(method acronyms in the description are boosted, because users name methods by acronym),
scores every eval query, and reports: positive rank-1 rate, MRR, the share of negative
(near-miss) queries for which the owning skill does *not* rank first, confusion pairs, and
skills without cases. CI gates: rank-1 ≥ 0.90, negatives held ≥ 0.90, ≥3 positive cases per
skill. It is a lexical proxy for model routing — cheap, deterministic, and good at exposing
descriptions that overlap; it is not a claim about how any particular model will route.

## Running

```bash
python3 evaluation/score_skills.py                              # full scorecard → scores/latest.{json,md}
python3 evaluation/score_skills.py --skill NAME                 # per-check report for one skill
python3 evaluation/score_skills.py --baseline scores/baseline-2026-08-16.json   # deltas vs the pre-improvement tree
python3 evaluation/score_skills.py --min-score 90 --min-library 95              # CI gate
python3 evaluation/trigger_eval.py [--skill NAME]              # discoverability eval
python3 evaluation/build_index.py [--check]                    # regenerate / verify index.json
python3 evaluation/check_repo.py                               # structural gate
```
