# Agent Skills specification, authoring guidance, and official tooling

Research date: 2026-08-16. Sources: agentskills.io/specification; platform.claude.com
"Agent Skills best practices"; code.claude.com docs (skills, plugins reference);
github.com/anthropics/skills (skill-creator); github.com/agentskills/agentskills (skills-ref).

## Specification (agentskills.io)

- Required frontmatter: `name` (1–64 chars, `^[a-z0-9]+(-[a-z0-9]+)*$`, **must equal the
  parent directory name**), `description` (1–1024 chars; what the skill does *and* when to
  use it).
- Optional: `license` (string), `compatibility` (≤500 chars; environment requirements),
  `metadata` (string→string map), `allowed-tools` (space-separated; experimental).
- Body: no format restriction; keep SKILL.md under ~500 lines / ~5k tokens; split heavier
  material into `references/`, executables into `scripts/`, templates into `assets/`; keep
  file references one level deep from SKILL.md; use forward-slash relative paths.
- Progressive disclosure: metadata (~100 tokens per skill) is always loaded; SKILL.md loads
  on activation; resources load on demand.
- Reference validator: `skills-ref validate <dir>` (frontmatter validity, name/description
  constraints, optional-field formats, file references). Exit 0/1.

## Anthropic authoring guidance (best-practices doc)

- Descriptions: third person; specific about what + when; include the key terms a user
  would say; if the description alone summarises the whole workflow the model may skip
  the body — keep it a trigger contract, not a procedure.
- Naming: lowercase-hyphen; gerunds, noun phrases or verb-first all acceptable; avoid
  vague names (`helper`, `utils`) and reserved words (`anthropic`, `claude`).
- Body: only add what the model does not already know; default with escape hatch rather
  than many options; concrete examples; workflows with checklists; feedback loops
  (validate → fix → re-run); scripts that solve, not defer, errors; no magic constants; no
  time-sensitive information (or fenced in an "old patterns" block); consistent terminology.
- Checklist: description specific (what + when); SKILL.md < 500 lines; details in separate
  files; examples concrete; references one level deep; workflows with clear steps; tested
  across models.
- Eval loop (skill-creator): create evals first (`evals/evals.json`:
  `{skill_name, evals: [{id, prompt, expected_output, files, expectations}]}`), run with
  and without the skill, grade, benchmark (pass rate, tokens, time), iterate; blind A/B
  comparator for revisions.

## Claude Code tooling

- `claude plugin validate <path> [--strict]` — validates plugin/marketplace manifests or
  the skills/agents/commands in a directory; `--strict` treats warnings as errors (CI).
- `claude plugin eval <target>` — runs eval cases (`evals/**/case.yaml` or
  `prompt.md` + `graders/*.md`; graders: regex, tool_used, tool_order, file_exists, llm,
  baseline) in isolated sessions, `--ablation with-without`, HTML/JSON reports. Early
  access, enabled per organisation (not available on this account at research time).
- `/skill-doctor` — usage/context-cost report for loaded skills (early access).
- Plugin packaging: `.claude-plugin/plugin.json` (`name`, `description`, `version`,
  `author`, `homepage`, `repository`, `license`, `keywords`); skills live in `skills/` at
  the plugin root and are namespaced `plugin-name:skill-name`; a marketplace is
  `.claude-plugin/marketplace.json` with `plugins[].source` (relative path or git);
  users run `claude plugin marketplace add owner/repo` then
  `claude plugin install plugin@marketplace`.

## Decisions taken

Adopted the allowed-key set and constraints as hard checks (D1); third-person + trigger
clause + concrete triggers + exclusion clause + length band as D2; body budgets as
D1/D11; per-skill `evals/evals.json` uses the canonical skill-creator envelope plus
routing extensions (`case_id`, `kind`, `skills`, and optional `requires_input`);
plugin + marketplace manifests; `claude plugin validate
--strict` as an external gate; `run_evals.py` as an optional stand-in for the gated
`claude plugin eval --ablation`.
