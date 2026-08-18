# Issue and maintenance policy

This library holds **structured analytic techniques as agent skills**. Every skill
implements a published method, cites it, and can be executed by an agent from the
`SKILL.md` alone.

This is an **issue-only, maintainer-authored repository**. It does not accept pull requests,
code or documentation contributions, co-maintenance requests, or collaboration proposals.
Please use the repository issue templates to report a method-fidelity problem, a reproducible
bug, or a high-value method that may be worth adding. Reports are inputs for the maintainer;
filing one does not create an expectation that a patch will be accepted or implemented.

The technical material below documents the standards the maintainer applies. It is published
so releases can be audited and issue reports can point to a specific invariant.

## Ground rules

1. **One method per skill.** If you cannot name the originator or the canonical
   publication, it is probably a procedure, not a method — it belongs elsewhere.
2. **Fidelity over flair.** Use the method's own labels, scales and step order. Do not
   "improve" a published scale (e.g. NATO Admiralty A–F / 1–6, NASA TRL 1–9,
   Cochrane RoB 2 domains). Cite the source with author, year, title, venue.
3. **Self-contained.** No references to tools, files, agents or data stores that do not
   exist in this repository. Name the *data* a step needs and let the harness decide how
   to fetch it. `evaluation/check_repo.py` enforces a denylist of known leaks.
4. **Deterministic where possible.** Arithmetic goes into a companion script under
   `scripts/`, never into prose the agent must recompute in its head.
5. **Every change is scored.** Run the scorer before and after; a change that lowers a
   dimension without a stated reason will be sent back.

## SKILL.md house style (v2)

Section order is fixed so agents and tools can rely on it:

```markdown
---
name: <must equal the directory name; ^[a-z0-9]+(-[a-z0-9]+)*$>
description: <third person; what it does + when to use it; 2–4 quoted trigger phrases; no workflow summary; ≤ 700 chars>
license: MIT
metadata:
  category: <decision-strategy | foresight | technology-assessment | evidence-verification | quantitative | domain | writing>
  method: <canonical method name>
  origin: <originator(s), year>
---
# <Method name>

<One paragraph: what the method is, the core principle, the failure it prevents.>

## When to invoke
Invoke when: … (symptoms, situations, phrases)
Do NOT invoke when: … (each bullet routes to a sibling skill in backticks)

## Procedure                       ← or "The N steps"; numbered `### 1 — …` headings
## Output template                 ← fenced, copy-ready; `{placeholders}` or JSON keys
## Worked example                  ← concrete numbers and names; reproduced with the tool if one exists
## Verification                    ← checklist: how the output is checked before it ships
## Companion tool                  ← only if scripts/ exists: what it computes, commands, sample output
## Pair with adjacent skills       ← ≥ 2 sibling skills; methodology counterpart by relative path
## Anti-patterns                   ← method-specific "do not" list
## Reference                       ← author, year, title, venue; DOI/ISBN/URL where canonical
```

Rules of thumb: keep the body under 1,600 words and 500 lines; move heavy reference
material into `references/`; one excellent worked example beats three sketches; write
descriptions in the third person and never summarise the workflow in them (a description
that already tells the agent the whole procedure invites it to skip the body).

## Companion tool conventions (`skills/<name>/scripts/*.py`)

- Python 3.9+, **standard library only**, executable (`#!/usr/bin/env python3`).
- Module docstring: what it computes, the definitions it implements (with the citation),
  and a `Usage:` block.
- `argparse` with subcommands; `--help` exits 0 and prints usage.
- `--selftest` runs hand-verified assertions (known answers from the literature or a
  worked example), prints a pass line (e.g. `selftest OK (41 checks)`), exits 0. This is
  the test suite; a self-test that inspects zero items must fail.
- `--demo` (optional) prints the SKILL.md worked example so readers can reproduce it.
- Input via `--file path.json|csv` (or stdin); `--json` switches output to JSON.
- **Deterministic:** no unseeded randomness, no wall-clock in output, sorted iteration
  over dicts/sets. Two runs must produce byte-identical output.
- **Offline by default.** Any network access sits behind an explicit flag or subcommand
  (`--online` in `citecheck.py`, `fetch --github` in `osshealth.py`) and is never
  exercised by `--selftest`. See `SECURITY.md`.
- **Exit codes** — `0` the check passed, `1` the tool ran and its verdict is a failure
  (where the tool has one), `2` usage error or input it cannot analyse. This is the
  convention of `grep`, `diff`, `flake8` and `pytest`, and it is the one `argparse`
  already enforces: `ArgumentParser.error()` exits `2`, so any scheme that assigns `2`
  another meaning needs a parser subclass in *every* script and breaks silently in the
  ones that forget. Do not subclass `ArgumentParser` to change this. `evaluation/exit_codes.py`
  enforces all three cases against the real binaries.
- The SKILL.md `## Companion tool` section names the script, lists the commands, and
  shows sample output; the worked example's numbers come from the tool.

## Evaluation workflow

```bash
python3 evaluation/check_repo.py                    # structural gate: frontmatter, links, self-containment, selftests
python3 evaluation/score_skills.py                  # deterministic 12-dimension scorecard → evaluation/scores/latest.{json,md}
python3 evaluation/score_skills.py --skill <name>   # per-check report while editing one skill
python3 evaluation/trigger_eval.py                  # description discoverability (retrieval) eval
python3 evaluation/build_index.py                   # regenerate index.json from frontmatter (CI checks it is current)
python3 evaluation/run_evals.py --skill <name>      # optional: model-based paired eval (with vs without skill), costs money
make all                                            # check + score + trigger + index
```

CI runs the first four and fails on any regression below the thresholds in
`.github/workflows/ci.yml`. See `evaluation/rubric.md` for the meaning of every check.

## Maintainer workflow for adding a skill

1. Copy `skills/_TEMPLATE/` — its `SKILL.md` and `evals/evals.json` are fill-in
   skeletons in the house style — or model on `analysis-of-competing-hypotheses`. A
   `skills/` directory whose name starts with `_` is scaffolding: the catalog, the
   scorecard and every validator skip it.
2. Fill every section of the house style; cite the canonical source.
3. Add `skills/<name>/evals/evals.json`: ≥ 3 positive prompts phrased as a user would
   phrase them, plus ≥ 1 near-miss negative whose `skills` field names the sibling that
   should handle it. Flag any case that presupposes an artifact the user would attach
   (a draft, a reference list, a dataset) with `"requires_input": true`, or supply the
   artifact under `files` — otherwise the model-based eval scores it zero in both arms
   because the only correct answer is "send me the document".
4. Add the skill to the README catalog and regenerate `index.json`.
5. Run the evaluation workflow and record the before/after scorer line in the release notes.

## Reporting a misrepresented method

Open an issue titled `fidelity: <skill> — <what is wrong>` quoting the offending line and
the primary source that contradicts it. These are triaged first.
