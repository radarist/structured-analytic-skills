# Evaluation Report — skill-library improvement pass

Before/after scoring per `evaluation/rubric.md`. Before: `scores-before.md` (77 files).
After: `scores-after.md` (87 files — 59 skills + 28 methodologies; the 11 skills added
since the before-pass are scored for the first time).

## Headline

| | Before | After |
|---|---|---|
| Files scored | 77 | 87 |
| Overall mean | 87.8 | 98.2 |
| Skills mean (Rubric A) | ~84.8 (49 files) | 97.4 (59 files) |
| Methodologies mean (Rubric B) | ~93.1 (28 files) | 99.6 (28 files) |
| Min / Max | 72.5 / 100 | 90.0 / 100 |

Criterion means, skills (S1–S10): before 2.00 | 1.61 | 1.98 | 1.92 | 2.00 | 1.67 | 1.18 | 1.33 | 1.57 | 1.31
→ after 2.00 | 1.92 | 2.00 | 1.98 | 2.00 | 1.90 | 2.00 | 1.90 | 1.75 | 1.93.

The three weakest criteria in the before-pass — S7 cross-linking (1.18), S8 worked examples
(1.33), S10 computation tooling (1.31) — moved to 2.00, 1.90, 1.93. For methodologies, M6
strengths/limitations candor (1.25) moved to 2.00 across all 23 flagged files.

## What the pass actually changed

### 1. Self-containment (the audit this pass started from)

The README claimed "references to the origin system's internals were removed so each skill
stands alone." That was not true. Found and fixed:

- **Phantom tools** (skill procedures calling APIs that don't exist here):
  `searchOssHealth` (oss-project-health — the skill's step 1 *was* the tool call),
  `searchPapers` (assess-research-momentum), `searchPatents` (read-patent-landscape),
  `webSearch`/`webScrape`/`firecrawl`/`search_with_grounding` (abstain-or-escalate,
  grounded-answer, grounded-fact-check), `searchEntities` (analyze-release-notes,
  detect-funding-round), `recordKnowledgeGap`/`approveSignalForImport`
  (abstain-or-escalate, rate-source-admiralty). Rewritten capability-agnostically:
  each skill now names the data it needs and says to gather it with whatever
  search/API tooling the harness provides (with concrete public-API pointers such as
  OpenAlex, Ecosyste.ms, Google Patents, GitHub API).
- **Dangling skill references**: `generate-radar-report`, `research-technology`,
  `web-research`, `resolve-citations`, `postmortem`, `five-forces` (typo),
  `rdkit-normalize` — replaced by existing siblings or plain prose.
- **Origin agent personas**: "the Strategist / Curator / Creator / Scout" genericized
  in ~10 files; origin config/doc references removed (`SIGNAL_AUTO_APPROVE_THRESHOLD`,
  `mission-quality.ts:SKILL_PROCEDURE_MARKERS` in 5 files, `CLAUDE.md Relation Write
  Contract` in 3 files, `checkCreator*` tools and `public/` paths in critique-report).
- **Checker hardening** (`evaluation/check_repo.py`): the old checker structurally could
  not catch any of the above (it only validated markdown links). Added: origin-internals
  denylist, agent-persona regex, cue-based dangling-skill-ref detection, README catalog
  coverage, orphan skill-dir check. The denylist immediately caught 6 additional files
  the manual audit had missed. All green.

### 2. Catalog and structure coherence

- README catalog updated: 10 skills were missing (backcasting, causal-layered-analysis,
  cross-impact-analysis, evidence-appraisal, experimental-design, futures-wheel,
  horizon-scanning, meta-analysis, steep-pestle-analysis, trend-analysis); new Foresight
  section added. The "No scripts. No executables." claim was stale — 12 skills ship
  stdlib-only companion tools; intro rewritten to describe them accurately.
- `skills/meta-analysis/` was an orphan: a companion script (`metapool.py`) with no
  SKILL.md. Wrote the skill around it (house style, methodology link, tool-verified
  worked example).

### 3. Citations (S2, 1.61 → 1.92)

17 files fixed, each web-verified. Notable: the vague "I-CALM 2025" turned out to be a
real 2026 paper (arXiv:2604.03904) and is now cited fully; the garbled Leonard/SBAR
citation in write-srl-brief replaced with the verified 2004 *Quality & Safety in Health
Care* paper; the IMRAD-history misattribution replaced with Sollaci & Pereira (2004,
verified via PubMed); unverifiable citations in estimate-market-size and pyramid-principle
were *removed* rather than patched. Added canonical anchors where missing: Snowden &
Boone 2007 (cynefin), Wardley (evolution-stage), Ulwick + Christensen 2016 (jtbd),
Ries 2011 (cheapest-experiment), McGrath & MacMillan 1995 (claim-provenance), CHAOSS
(oss-project-health), Baghai/Coley/White 1999 + Curry/Hodgson disambiguation
(three-horizons), Price 1963 (assess-research-momentum), Sterne et al. 2019 RoB-2
(benchmark-model-claims).

Three skills remain at S2 = 1 *honestly*: `foresight` is a bespoke composite (now says
so, with verified Ansoff/Hiltunen anchors), `critique-report` is a bespoke checklist, and
`detect-funding-round`/`detect-ma-event` are bespoke extraction patterns — no canonical
source exists to cite, and inventing one is worse than the point loss.

### 4. Rubric gap closure

- **S7 cross-linking (1.18 → 2.00)**: added/extended `## Pair with` sections across
  ~25 skills; every skill with a methodology counterpart now links it by relative path
  (and methodology files link back — M8).
- **S8 worked examples (1.33 → 1.90)**: ~20 skills gained complete worked examples.
  Where a companion tool exists, examples use tool-verified numbers (brier `--demo`
  output, bayes update reproduced via `bayes.py`, significance via `significance.py`,
  meta-analysis via `metapool.py`). Illustrative data is framed as illustrative; nothing
  invented is presented as a real measurement.
- **S10 tooling (1.31 → 1.93)**: all 12 companion scripts are now documented in their
  SKILL.md. **Bug found while verifying:** `significance.py`'s CLI crashed on every
  subcommand (missing docstrings broke argparse wiring) while `--selftest` passed — the
  checker was green and the tool unusable. Fixed; CLI verified end-to-end.
- **S6/S9/S4**: skip-for lists gained named sibling routing; verification hooks name
  concrete check procedures (recompute, marker detection, zero-silent-drop rules);
  write-imrad-report and grounded-fact-check gained fenced fill-in templates.
- **Methodologies (M5/M6/M7)**: candid strengths/limitations commentary added to all 23
  flagged files (each names real failure modes — bandwagon-to-median in Delphi,
  integration theater in mixed-methods, label abuse in case-study research, etc.);
  participants/timeframes added to 4 process sections; worked cases upgraded to named,
  documented applications where verifiable (Eisenhardt & Bourgeois 1988, Fetters et al.
  2013, UK Foresight *Tackling Obesities* 2007, Gordon & Hayward 1968).

## Remaining gaps (deliberate)

- `chemistry-claim-check` and `verify-citations` still lack companion scripts (S10 = 0).
  Both are feasible stdlib builds (formula→MW/DBE arithmetic; DOI/arXiv format
  validation) — candidates for a future pass.
- `futures-triangle`/`futures-wheel` worked cases stay at M7 = 1: their documented use is
  pedagogical/diagnostic, and the rubric's M7 = 2 wants decision-level outcomes. Kept
  honest rather than embellished.
- Several skills keep S9 = 1 (loose verification mentions). A uniform "how the output
  gets checked" pattern across all skills would close this.
- S6 = 1 on a few parsing skills (analyze-patent-claims, analyze-release-notes,
  apply-hype-cycle, test-significance): skip-fors exist but don't name sibling routing.

## Judgment calls a reviewer should know about

- S10 for extraction skills (analyze-patent-claims, analyze-release-notes,
  detect-funding-round, detect-ma-event, benchmark-model-claims) scored 2 per the
  rubric's "non-computational → 2 by default" rule; the before-pass had scored them 0.
  These are language-extraction tasks where an LLM outperforms a regex script — the
  rubric's own N/A clause applies, but a stricter reading would keep them at 0.
- Scores-after were assigned by the editor of the changes against the rubric anchors,
  not by an independent scorer. The deltas are mechanical (each criterion change maps to
  a specific diff), but a blind re-score would be a useful audit.

## Verification

`python3 evaluation/check_repo.py` → OK (all checks incl. hardened self-containment
checks and every `scripts/*.py --selftest`).
