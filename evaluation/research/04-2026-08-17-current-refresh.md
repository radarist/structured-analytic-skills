# Current skill, evaluation and patent-analytics refresh — 2026-08-17

Research date: 2026-08-17. Primary sources were checked live. This note records the delta
from the preceding survey; it does not replace the earlier canon and fidelity audit.

## What changed in the skill ecosystem

- **OpenAI distribution and context budget.** Current OpenAI documentation keeps the open
  Agent Skills layout (`SKILL.md`, optional scripts/references/assets and
  `agents/openai.yaml`) but recommends plugins for reusable distribution. Codex discovers
  repository and user skills under `.agents/skills`. Its initial skill list is capped at 2%
  of context or 8,000 characters when the context size is unknown; descriptions are
  shortened and skills can be omitted when the collection is too large. Decision: add
  generated `agents/openai.yaml`, document focused/category installation, retain the
  vendor-neutral skill body, and run OpenAI's skill-creator reference validator over every
  skill. That validator exposed 25 descriptions which Claude accepted but a strict YAML
  loader rejected; descriptions now use a checked JSON-quoted YAML subset. Source:
  https://learn.chatgpt.com/docs/build-skills
- **Anthropic's eval contract is now exact and executable.** The current skill-creator
  schema is an object with `skill_name` and `evals`; each case has an integer `id`,
  `prompt`, `expected_output`, optional `files`, and `expectations`. The repository's old
  top-level lists were not directly compatible. Decision: migrate all cases canonically,
  retain routing fields as extensions, and gate schema plus fixture resolution. Sources:
  https://github.com/anthropics/skills/blob/main/skills/skill-creator/references/schemas.md
  and https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
- **Kimi supports the same directories directly.** Current Kimi Code CLI loads canonical
  `<name>/SKILL.md` directories from `.kimi/skills`, `.claude/skills`, `.codex/skills`, and
  the generic `.agents/skills`; it also accepts repeatable `--skills-dir`. Decision: publish
  an exact no-conversion Kimi command and keep all core instructions vendor-neutral.
  Source: https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/customization/skills.md
- **The Agent Skills standard remains the portability floor.** Clients load name and
  description first, then the complete body on activation. Decision: preserve spec-exact
  frontmatter and keep product metadata outside `SKILL.md`. Sources:
  https://agentskills.io/specification and https://agentskills.io/home

## New empirical evidence about skill quality

- GitSkills (Destefanis et al., 2026, arXiv:2608.10906) reports 3,797,117 `SKILL.md`
  occurrences from 282,200 public repositories, grouped into 1,877,981 distinct contents.
  A skill library is therefore competing in a very large copied ecosystem; deterministic
  identity, provenance, maintenance and machine-readable catalogs matter.
  https://arxiv.org/abs/2608.10906
- Shaposhnikov et al. evaluate 500 real-world skills with 1,000 tasks across 19
  agent/model configurations and find material variation in instruction adherence and
  performance gain. A single-model result cannot establish universal benefit.
  https://arxiv.org/abs/2606.17819
- ACES (Kevin et al., Agent Skills '26) runs paired live trials with the skill present and
  withheld, holds support/decoy skills fixed, grades trajectories across six dimensions,
  and reports Skill Lift. Across its published sample, structural scans and LLM-judge
  scores are weakly correlated (Spearman rho 0.14). Decision: retain the deterministic
  score as a conformance floor, keep paired behavior lift separate, and never relabel 100
  mechanical points as proven runtime usefulness. https://openreview.net/pdf?id=cf92xtZK47
- Skill-Synthesizer (2026) finds that retrieving and composing relevant passages can beat
  loading whole skills for complex scientific reasoning. Decision: document focused
  installation now; passage-level synthesis is a future host/runtime feature, not something
  a portable `SKILL.md` library can honestly claim to implement.
  https://openreview.net/pdf?id=T3WDCimC5K

## New patent and innovation sources checked

- WIPO's live Patent Analytics hub now lists 2026 SPARK updates on GenAI, sports technology,
  and a patent landscape on decarbonizing heavy-duty road transport. It explicitly frames
  patent analytics as one input to R&D, innovation policy, commercialization, licensing and
  technology transfer, and distinguishes patent landscapes from broader Technology Trends
  evidence. Decision: keep `read-patent-landscape` bounded to family-reduced patent data and
  require non-patent demand evidence before treating white space as opportunity.
  https://www.wipo.int/en/web/patent-analytics
- WIPO's 2025 *Intellectual Property Valuation Basics for Technology Transfer
  Professionals* formalizes cost, market, income, real-options and Monte Carlo approaches
  for early-stage IP (doi:10.34667/tind.50113). Its companion biotechnology/pharmaceutical
  guide applies rNPV and real-options thinking to staged development. This was a direct gap
  for innovation teams, so the final pre-publication pass adds `value-intellectual-property` and deterministic DCF,
  rNPV, comparable-adjustment and reconciliation arithmetic.
  https://doi.org/10.34667/tind.50113 and
  https://www.wipo.int/publications/en/details.jsp?id=4810
- The current USPTO MPEP remains Ninth Edition, Revision 01.2024; the claim-analysis skill's
  cited revision is still current. The consolidated patent rules received a July 2025
  update, which does not change the transition/dependency rules used by the companion
  parser. Sources: https://www.uspto.gov/web/offices/pac/mpep/index.html and
  https://www.uspto.gov/web/offices/pac/mpep/consolidated_rules.pdf

## Resulting acceptance criteria for the final pre-publication pass

1. All skill bodies remain Agent-Skills-compatible and vendor-neutral.
2. Every eval file passes the official skill-creator envelope checks without losing routing
   negatives or input-required flags.
3. Every skill has current Codex/ChatGPT UI metadata; Claude plugin validation and Kimi's
   canonical directory shape remain valid.
4. Structural, trigger and companion-tool gates remain green after adding IP valuation.
5. The report states the existing behavioral sample and its limits separately from the
   deterministic 100/100 conformance score.
