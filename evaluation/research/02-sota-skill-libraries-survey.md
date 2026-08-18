# Best-in-class agent-skill libraries in 2026 — survey

Research date: 2026-08-16. Verified unless marked *inferred*.

## Headline findings

- The format is standardised (agentskills.io spec; ~46 listed client products incl.
  Claude Code, Codex/ChatGPT, Copilot/VS Code, Cursor, Gemini CLI, Goose, OpenCode).
  Packaging is converging on Agent Plugins 1.0.0 (`plugin.json` + `skills/` + `mcp.json`);
  Claude Code keeps `.claude-plugin/plugin.json` + `marketplace.json`.
- The quality bar has moved from "valid frontmatter" to **paired evals** (with vs. without
  skill), **trigger evals** (should/should-not-trigger with near-miss negatives) and
  **deterministic linters with token budgets** in CI. SkillsBench (arXiv:2602.12670) found
  curated skills lift pass rate 33.9 → 50.5 % while self-generated skills add ~nothing, and
  that focused skills (≤ 3 modules) beat exhaustive bundles — the strongest published
  argument for lean SKILL.md + references/.
- The most rigorous public repos (Trail of Bits, microsoft/skills, github/awesome-copilot)
  treat the library like software: validator self-tests, version-bump enforcement,
  loadability smoke tests against pinned agent CLIs, generated catalogs.

## Comparison

| Library | Structure | Validation / CI | Evals | Notable practice |
|---|---|---|---|---|
| anthropics/skills | `skills/<name>/SKILL.md` + scripts/ references/ assets/; `.claude-plugin/marketplace.json` | `skill-creator/scripts/quick_validate.py` (6 allowed keys, limits) | `evals/evals.json` → grading → benchmark (pass rate, tokens, time); description optimiser | Blind A/B comparator with 1–5 rubric → 1–10 overall |
| agentskills/agentskills | spec + `skills-ref` (validate, read-properties, to-prompt) | frontmatter validation | guides: evaluating skills, optimising descriptions | progressive-disclosure targets (metadata ~100 tokens; SKILL.md < 5k tokens / 500 lines) |
| obra/superpowers | skills + agents + hooks; per-harness manifests; release notes; version-bump script | per-harness plugin tests, pre-commit | external "drill" harness (real sessions, LLM actor + verifier); RED→GREEN→REFACTOR pressure scenarios | description rules: "Use when…", third person, ≤ 500 chars, never summarise workflow |
| vercel-labs/agent-skills | `skills/`, `AGENTS.md`, `skills.sh.json` | GH Actions: validate + build; rules compiled into AGENTS.md; test-case corpus | test cases only | scripts: JSON → stdout, status → stderr, `set -e` |
| trailofbits/skills | plugins/<p>/.claude-plugin + skills/{SKILL.md,references/,workflows/,scripts/}; root marketplace.json; CODEOWNERS | `make check` = validator self-test, ruff, shellcheck, bats, pytest, metadata validator; CI: hardcoded-path/PII scans, version-increment vs base, loadability with pinned Claude Code & Codex | bats/pytest for scripts | "a checker that inspects zero items must fail"; > 500-line SKILL.md and dangling links = warnings |
| microsoft/skills | language plugins; symlinked skills/; SECURITY.md | nightly harness; `vally` eval workflows; llms.txt; skill explorer | `tests/scenarios/<skill>/acceptance-criteria.md` + scenarios.yaml (1,169 scenarios) | description ≥ 150 chars with "USE FOR / DO NOT USE FOR" |
| github/awesome-copilot | skills/, plugins/, eng/*.mjs | `validate-skills.mjs` (name ≤ 64, description 10–1024, folder match, ≤ 5 MB, duplicates); external-plugin quality gates | — | intake gate pipeline for third-party plugins |
| OpenAI Codex | `.agents/skills/`, optional `agents/openai.yaml` | `$skill-creator`, `$skill-installer` | outcome/process/style/efficiency checks over `codex exec --json` traces | listing budget 8,000 chars or 2 % of context |
| addyosmani/agent-skills | `evals/cases/<skill>.json`, fixtures | CI: structural + trigger tiers | ≥ 3 positive / 2 negative triggers + 1 behavioural per skill; TF-IDF rank-1 rate (86 % baseline, CI gate 80 %) | cheapest reproducible trigger-collision test |

## Conventions a best-in-class library must have (2026)

1. Spec-exact frontmatter (only `name, description, license, compatibility, metadata,
   allowed-tools`; `name` = directory; description ≤ 1024, ideally ≤ 500).
2. Description = triggering contract ("Use when…", user-intent keywords, near-miss
   exclusions, no workflow summary).
3. Progressive disclosure (SKILL.md < 500 lines / < 5k tokens; references one level deep
   with "read X when Y" pointers).
4. Focused scope; defaults not menus; gotchas; procedures over declarations.
5. Companion scripts: non-interactive, `--help`, JSON stdout / diagnostics stderr, distinct
   exit codes, deterministic, stdlib or PEP 723; self-tests that fail on zero items.
6. Deterministic validator in CI with self-test, run on every PR: spec checks, token
   budgets, broken/orphan links, no absolute paths, secrets/PII scan.
7. Paired evals per skill (`evals/evals.json`), graded with evidence, benchmarked with vs.
   without skill; blind A/B for revisions.
8. Trigger evals: labelled queries incl. near-miss negatives; lexical collision check
   across all descriptions.
9. Loadability smoke test against pinned agent CLIs (`claude plugin validate`).
10. Machine-readable catalog generated, never hand-edited (`index.json`; marketplace).
11. Semantic versioning per skill and per plugin; CHANGELOG.
12. Repo hygiene: CONTRIBUTING with quality bar and PR checklist, CODEOWNERS, SECURITY,
    LICENSE + per-skill `license:`, CITATION.cff, badges.
13. Multi-client install paths documented; MCP is complementary (skills = procedure,
    MCP = connectivity).
14. Human review pass recorded — assertions miss "technically correct but useless".

## Dimensions worth adopting in a deterministic scorer

Spec compliance (hard fail); context economy (SKILL.md ≤ 500 lines / ≤ 5k tokens;
description ≤ 500 soft); trigger quality (imperative/"Use when", intent keywords,
exclusion clause, keyword-stuffing guard, pairwise description similarity, rank-1 rate
≥ 80 %); structure integrity (relative links resolve, ≤ 1 hop, orphan files, no absolute
paths, scripts referenced from SKILL.md); actionability (imperative ratio, strong markers,
code-block ratio, required sections: quick start, gotchas, validation checklist, worked
example); script contract (`--help` 0, self-test passes, JSON parses, non-zero on bad
input, no TTY prompts); eval coverage (≥ 2 cases, ≥ 3 positive / 2 negative triggers,
benchmark delta reported); governance (semver, license, catalog synced, version bumped).

## Caveats

`claude plugin eval` and `/skill-doctor` are early access. moutons/skills-validator
enforces description ≤ 250 chars (stricter than spec). SkillsBench numbers differ between
versions. SkillRouter (arXiv:2603.22455) shows name+description-only routing loses 37–44 pp
at ~80k-skill scale — relevant only for very large registries.

## Sources

agentskills.io (specification; skill-creation best-practices, evaluating-skills,
optimizing-descriptions, using-scripts); github.com/anthropics/skills (skill-creator
SKILL.md, references/schemas.md); claude.com/blog "improving skill-creator";
code.claude.com/docs (skills, plugins-reference); github.com/obra/superpowers
(writing-skills, testing-skills-with-subagents, docs/testing.md);
github.com/vercel-labs/agent-skills (AGENTS.md); github.com/trailofbits/skills (AGENTS.md,
Makefile, .github/workflows/validate.yml, validate_plugin_metadata.py);
github.com/microsoft/skills; github.com/microsoft/waza; github.com/github/awesome-copilot
(eng/validate-skills.mjs, eng/external-plugin-quality-gates.mjs); learn.chatgpt.com
build-skills; developers.openai.com/blog/eval-skills; agent-plugins.org/specification;
github.blog changelog 2026-04-16 (gh skill install); validators: agent-ecosystem/
skill-validator, moutons/skills-validator, mgechev/skillgrade, JoaquinCampo/skill-doctor,
addyosmani/agent-skills/evals; research: arXiv:2602.12670 (SkillsBench), 2606.11543
(SkillJuror), 2603.22455 (SkillRouter), 2606.10388 (SkillResolve-Bench), 2606.11435
(survey), 2605.18693 (SkillGenBench).
