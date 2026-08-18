# structured-analytic-skills

**Structured analytic techniques as agent skills.** Heuer's ACH, NATO Admiralty grading, GRADE, Cochrane RoB 2, AMSTAR 2, Delphi, scenario planning, Wardley mapping, NASA TRL, Brier scoring, meta-analysis, reference-class forecasting, AHP/MCDA, ICD 203 estimative language. Every skill implements a *published* method, cites it, and ships a copy-ready output template, a worked example, a verification checklist, eval cases, and — where the method contains arithmetic — a deterministic, standard-library-only companion tool.

[![validate](https://github.com/radarist/structured-analytic-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/radarist/structured-analytic-skills/actions/workflows/ci.yml)
![skills](https://img.shields.io/badge/skills-69-blue)
![deterministic per-skill score](https://img.shields.io/badge/deterministic%20per--skill%20score-100.0%2F100-brightgreen)
![companion tools](https://img.shields.io/badge/companion%20tools-36-blue)
![spec](https://img.shields.io/badge/Agent%20Skills%20spec-compliant-informational)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

---

Most agent-skill collections are prompt grab-bags. These are established analytical methods — from intelligence analysis, evidence-based medicine, foresight, decision analysis and strategy practice — adapted into agent-executable form and held to a bar you can measure:

- **Method fidelity.** Each skill uses the method's own labels, scales and step order, names the originator and year in the body, and cites the canonical publication with a locator. Fidelity is audited source-by-source; see the [independent audit](evaluation/independent-audit-2026-08-17.md), [second-pass verification](evaluation/second-pass-2026-08-18.md), and [changelog](CHANGELOG.md).
- **A deterministic quality score.** [`evaluation/score_skills.py`](evaluation/score_skills.py) scores every skill on 12 mechanically-checked dimensions. No model, no judgement: the same skill files give the same **per-skill** numbers, and every lost point names the check to fix. The single *library* score is a different thing and is not purely content-determined — it is `0.85 × mean(skill score) + 0.15 × repo hygiene`, and the hygiene component inspects the working tree, so a stray `.DS_Store` or an out-of-date `index.json` moves it. Reproduce the per-skill figures; read the library figure as a snapshot of the checkout it was run on.
- **Discoverability evals.** Every skill ships `evals/evals.json` — prompts phrased the way a user would ask, plus near-miss negatives naming the sibling that *should* handle them. A BM25 trigger eval gates rank-1 accuracy in CI; the same cases run under model-based harnesses (`claude plugin eval`, the anthropics/skills skill-creator loop) via [`evaluation/run_evals.py`](evaluation/run_evals.py).
- **Deterministic tools.** 36 companion scripts — the RoB 2 judgement algorithm, GRADE certainty, AMSTAR 2 ratings, Brier decomposition, meta-analytic pooling, ACH scoring, power and sample size, AHP consistency ratios, EVPI, IP valuation, S-curve fitting, HHI patent concentration, PRISMA counts and more. Standard library only, `--selftest`, `--help`, JSON I/O, byte-for-byte reproducible, offline unless you opt in.
- **Self-contained and spec-exact.** Frontmatter follows the [Agent Skills specification](https://agentskills.io/specification); all 69 skills pass the agentskills.io reference validator — `agentskills validate`, the console script from the PyPI package [`skills-ref`](https://pypi.org/project/skills-ref/), run per skill in CI — and `claude plugin validate --strict`; nothing references a tool or system that is not in this repository. (`skill-creator` is an authoring skill in [anthropics/skills](https://github.com/anthropics/skills), not a validator and not an OpenAI tool; what this repo takes from it is its eval-file schema, checked by `evaluation/eval_schema.py`.)

## Install

**Claude Code (plugin)**

```bash
claude plugin marketplace add radarist/structured-analytic-skills
claude plugin install structured-analytic-skills@structured-analytic-skills
```

Skills are then available as `/structured-analytic-skills:<skill-name>`, and Claude loads one automatically when a request matches its description.

**Codex / ChatGPT desktop**

```bash
git clone https://github.com/radarist/structured-analytic-skills.git
mkdir -p .agents/skills
cp -R structured-analytic-skills/skills/* .agents/skills/
```

Codex discovers `.agents/skills` from the working directory to the repository root and also supports `~/.agents/skills` for user-wide installation. Each skill includes optional `agents/openai.yaml` UI metadata. Codex budgets its initial skill listing, so for the strongest routing in a large personal library copy the relevant category or individual skill rather than every installed collection.

Concretely: the full 69-skill listing currently renders as approximately **58,400 characters** of skill metadata — about **7.3×** the 8,000-character initial skill-listing budget Codex documents. On any client with a capped listing, copy one category subset from [the catalog below](#the-catalog) rather than all 69, or the client may truncate descriptions or omit skills.

**Kimi Code CLI**

```bash
git clone https://github.com/radarist/structured-analytic-skills.git
kimi --skills-dir "$PWD/structured-analytic-skills/skills"
```

Kimi also discovers project or user skills under `.agents/skills` / `~/.agents/skills`; the canonical `<name>/SKILL.md` layout here needs no conversion.

**Other Agent-Skills-compatible harnesses** (Cursor, Copilot, Gemini CLI, Goose …)

Copy one or more directories from `skills/` into the client's Agent Skills directory. Each `SKILL.md` is self-contained; the content is plain method prose, usable as a prompt, checklist or reference. [`index.json`](index.json) is the machine-readable catalog (name, description, category, method, origin, version, scripts, references, evals, sha256).

## Quality at a glance

**Both columns were produced by the same scorer.** The "before" column is a preserved
pre-publication score artifact generated by applying the current rubric to an early development
tree. The public Git history begins at v1.0.0, so that earlier source tree is deliberately not
part of the release and the baseline cannot be re-run from a public clone. `make compare`
compares the current tree with the preserved JSON record. The library score is
`0.85 × mean(skill score) + 0.15 × repo hygiene`; the hygiene component inspects the working
tree, so it describes the checkout it was measured on rather than the commit alone.

| Metric | Before (pre-publication baseline) | Now (v1.0) |
|---|---|---|
| Library score (0–100; incl. working-tree hygiene) | 70.4 | **100.0** |
| Mean skill score | 77.5 | **100.0** |
| Median skill score | 77.1 | **100.0** |
| Lowest-scoring skill | 61.3 | **100.0** |
| Skills · with tools · with eval cases | 59 · 12 · 0 | **69 · 36 · 69** |
| Trigger eval — positives ranked 1 / negatives held | — | **100% / 100%** (365 cases) |
| Mechanical checks passed | 2902 / 3708 | **4356 / 4356** |

The 2026-08-18 second pass closed the seven remaining D11 word-budget checks without removing
the necessary attribution. The deterministic suite now reports every mechanical check passing;
that is evidence of structural conformance, reproducibility and internal consistency, not a
substitute for expert review of method fidelity or cross-model output quality.

Behavioral evidence is kept separate from mechanical conformance, and it is thin. The
Claude probe was ten skills, one eval case each, one run per arm, answered and scored by a
fast model (haiku answering, haiku judging), and four of the ten cases came out flat or
negative (one at −0.20); the **+0.38 mean expectation pass-rate lift** is that sample's
average, not a benchmark result. The pre-publication Codex IP-valuation forward test is likewise one
case, one run per arm: **6/8 → 8/8 (+33.3% relative)** after one documented revision.
Neither is a cross-model benchmark; the per-case table and caveats are in
[`evaluation/report.md`](evaluation/report.md) §5.

Dimension-by-dimension movement and the original behavioral probes are in the historical
[`evaluation/report.md`](evaluation/report.md); the release-readiness evidence is in the
[`independent audit`](evaluation/independent-audit-2026-08-17.md) and
[`second-pass verification`](evaluation/second-pass-2026-08-18.md). The rubric is
[`evaluation/rubric.md`](evaluation/rubric.md); the research the redesign was built on is in
[`evaluation/research/`](evaluation/research/).

## The catalog

<!-- CATALOG:BEGIN -->

<!-- Generated by evaluation/build_index.py — do not edit by hand. -->

### Decision & strategy

Choosing between options, ranking explanations, and stress-testing a decision before it is made.

| Skill | Method | Tool |
| --- | --- | --- |
| [`analysis-of-competing-hypotheses`](skills/analysis-of-competing-hypotheses/SKILL.md) | Analysis of Competing Hypotheses (ACH) | `ach.py` |
| [`cheapest-experiment`](skills/cheapest-experiment/SKILL.md) | Cheapest decisive experiment (minimum viable test with a pre-committed decision rule) | — |
| [`cynefin-classification`](skills/cynefin-classification/SKILL.md) | Cynefin framework | — |
| [`decision-matrix-mcda`](skills/decision-matrix-mcda/SKILL.md) | Weighted Decision Matrix / Multi-Criteria Decision Analysis (MCDA) with AHP weights | `mcda.py` |
| [`decompose-research-question`](skills/decompose-research-question/SKILL.md) | Issue-tree decomposition (MECE sub-questions with dependency order and a recombination plan) | — |
| [`delphi-method`](skills/delphi-method/SKILL.md) | Delphi method (anonymous iterated expert elicitation with controlled feedback) | `delphi.py` |
| [`expected-value-decision-tree`](skills/expected-value-decision-tree/SKILL.md) | Decision tree analysis — expected-value roll-back, EVPI/EVSI, one-way sensitivity (tornado) | `dtree.py` |
| [`five-forces-analysis`](skills/five-forces-analysis/SKILL.md) | Five Forces (industry structure analysis) | — |
| [`foresight`](skills/foresight/SKILL.md) | Single-trajectory dated prediction with weak-signal and kill-signal watchlist (composite) | — |
| [`jtbd-framing`](skills/jtbd-framing/SKILL.md) | Jobs to be Done (JTBD) framing — Ulwick's outcome-driven job and outcome statements with Christensen's hire / non-consumption lens | — |
| [`morphological-analysis`](skills/morphological-analysis/SKILL.md) | General Morphological Analysis (GMA) with Cross-Consistency Assessment (CCA) | `morph.py` |
| [`premortem-analysis`](skills/premortem-analysis/SKILL.md) | Premortem (prospective hindsight) | — |
| [`scenario-planning`](skills/scenario-planning/SKILL.md) | Scenario planning (Shell/GBN deductive 2×2) | — |
| [`three-horizons`](skills/three-horizons/SKILL.md) | Three Horizons of Growth (McKinsey) | — |
| [`wardley-map-drafting`](skills/wardley-map-drafting/SKILL.md) | Wardley mapping | — |

### Foresight

Looking further out: weak signals, alternative futures, and the indicators that tell you which one is arriving.

| Skill | Method | Tool |
| --- | --- | --- |
| [`backcasting`](skills/backcasting/SKILL.md) | Backcasting (normative foresight) | — |
| [`causal-layered-analysis`](skills/causal-layered-analysis/SKILL.md) | Causal Layered Analysis (CLA) | — |
| [`cross-impact-analysis`](skills/cross-impact-analysis/SKILL.md) | Cross-impact analysis with MICMAC-style structural analysis (direct stage) | `crossimpact.py` |
| [`futures-wheel`](skills/futures-wheel/SKILL.md) | Futures Wheel | — |
| [`high-impact-low-probability`](skills/high-impact-low-probability/SKILL.md) | High-Impact/Low-Probability Analysis (with "What If?" Analysis) | — |
| [`horizon-scanning`](skills/horizon-scanning/SKILL.md) | Horizon scanning | — |
| [`indicators-validation`](skills/indicators-validation/SKILL.md) | Indicators and Indicators Validator (indicators generation, validation and evaluation) | `indicators.py` |
| [`steep-pestle-analysis`](skills/steep-pestle-analysis/SKILL.md) | STEEP / PESTLE macro-environment analysis | — |
| [`trend-analysis`](skills/trend-analysis/SKILL.md) | Trend analysis with Trend Impact Analysis (TIA) | `trend.py` |

### Technology assessment

Reading the maturity, momentum and competitive position of a technology or the organisations building it.

| Skill | Method | Tool |
| --- | --- | --- |
| [`analyze-patent-claims`](skills/analyze-patent-claims/SKILL.md) | Patent claim construction and structural claim analysis | `claims.py` |
| [`analyze-release-notes`](skills/analyze-release-notes/SKILL.md) | Release-note parsing against SemVer, Conventional Commits and Keep a Changelog | `relnotes.py` |
| [`apply-hype-cycle`](skills/apply-hype-cycle/SKILL.md) | Gartner Hype Cycle placement | — |
| [`assess-research-momentum`](skills/assess-research-momentum/SKILL.md) | Bibliometric momentum assessment (publication S-curve + citation velocity) | `momentum.py` |
| [`estimate-market-size`](skills/estimate-market-size/SKILL.md) | TAM/SAM/SOM triangulation (top-down × bottom-up Fermi estimation) | `market.py` |
| [`evolution-stage`](skills/evolution-stage/SKILL.md) | Wardley evolution stage (evolution axis) | — |
| [`oss-project-health`](skills/oss-project-health/SKILL.md) | CHAOSS community-health metrics (repository vitality read) | `osshealth.py` |
| [`position-competitor`](skills/position-competitor/SKILL.md) | Two-axis competitive positioning map | `positioning.py` |
| [`read-patent-landscape`](skills/read-patent-landscape/SKILL.md) | Patent landscape analysis (WIPO PLR methodology) | `landscape.py` |
| [`score-technology-readiness`](skills/score-technology-readiness/SKILL.md) | Technology Readiness Level (TRL) assessment | `trl.py` |
| [`value-intellectual-property`](skills/value-intellectual-property/SKILL.md) | WIPO IP valuation using cost, market, income, rNPV and real-options approaches | `ipvalue.py` |

### Evidence & verification

Establishing what is actually known, how well it is sourced, and where a conclusion would break.

| Skill | Method | Tool |
| --- | --- | --- |
| [`abstain-or-escalate`](skills/abstain-or-escalate/SKILL.md) | Abstention and escalation decision for unverifiable claims | — |
| [`amstar2-review-appraisal`](skills/amstar2-review-appraisal/SKILL.md) | AMSTAR 2 (A MeaSurement Tool to Assess systematic Reviews, version 2) | `amstar2.py` |
| [`claim-provenance`](skills/claim-provenance/SKILL.md) | Validated-vs-assumption claim tagging (adapted from Discovery-Driven Planning) | — |
| [`critique-report`](skills/critique-report/SKILL.md) | Structured self-critique of a draft document | — |
| [`evidence-appraisal`](skills/evidence-appraisal/SKILL.md) | GRADE certainty of evidence (Grading of Recommendations Assessment, Development and Evaluation) | `grade.py` |
| [`grounded-answer`](skills/grounded-answer/SKILL.md) | Chain-of-Verification (CoVe) | — |
| [`grounded-fact-check`](skills/grounded-fact-check/SKILL.md) | Pre-publication fact-check of load-bearing specifics (adaptation of newsroom fact-checking practice) | — |
| [`key-assumptions-check`](skills/key-assumptions-check/SKILL.md) | Key Assumptions Check | — |
| [`meta-analysis`](skills/meta-analysis/SKILL.md) | Meta-analysis (fixed-effect and DerSimonian–Laird random-effects pooling) | `metapool.py` |
| [`quality-of-information-check`](skills/quality-of-information-check/SKILL.md) | Quality of Information Check | — |
| [`rate-source-admiralty`](skills/rate-source-admiralty/SKILL.md) | Admiralty Code (NATO System, 6×6 source reliability × information credibility) | `admiralty.py` |
| [`red-team-claim`](skills/red-team-claim/SKILL.md) | Red team / challenge analysis of a single claim | — |
| [`sift-source-check`](skills/sift-source-check/SKILL.md) | SIFT (Stop, Investigate the source, Find better coverage, Trace claims to the original context) | — |
| [`steelman-argument`](skills/steelman-argument/SKILL.md) | Steelmanning (Rapoport's rules; ideological Turing test) | — |
| [`triangulate-sources`](skills/triangulate-sources/SKILL.md) | Source triangulation (data triangulation applied to sourcing) | — |
| [`verify-citations`](skills/verify-citations/SKILL.md) | Scholarly identifier format and checksum validation (ISO 26324, ISO 2108, ISO/IEC 7064) | `citecheck.py` |

### Quantitative checks

The arithmetic behind a claim: significance, power, pooling, calibration, base rates.

| Skill | Method | Tool |
| --- | --- | --- |
| [`assess-study-bias`](skills/assess-study-bias/SKILL.md) | Cochrane Risk of Bias 2 (RoB 2) for randomized trials | `rob2.py` |
| [`bayesian-update`](skills/bayesian-update/SKILL.md) | Bayesian belief updating in odds form (prior odds × Bayes factor) | `bayes.py` |
| [`benchmark-model-claims`](skills/benchmark-model-claims/SKILL.md) | Benchmark claim integrity audit (six-domain checklist) | — |
| [`brier-score-calibration`](skills/brier-score-calibration/SKILL.md) | Brier score with Murphy decomposition and Brier Skill Score | `brier.py` |
| [`experimental-design`](skills/experimental-design/SKILL.md) | Randomized experimental design with a priori power analysis and validity audit | `power.py` |
| [`quantitative-sanity-check`](skills/quantitative-sanity-check/SKILL.md) | Quantitative sanity check (internal-consistency arithmetic checklist) | `sanity.py` |
| [`reference-class-forecasting`](skills/reference-class-forecasting/SKILL.md) | Reference Class Forecasting (outside view) | `refclass.py` |
| [`systematic-review`](skills/systematic-review/SKILL.md) | Systematic review reported to PRISMA 2020 | `prisma.py` |
| [`test-significance`](skills/test-significance/SKILL.md) | Null-hypothesis significance test with confidence interval and effect size | `significance.py` |

### Domain-specific

Checks that need a field's own rules.

| Skill | Method | Tool |
| --- | --- | --- |
| [`chemistry-claim-check`](skills/chemistry-claim-check/SKILL.md) | Formula arithmetic (DBE/RDBE, molecular weight) plus Lipinski's rule of five | `chem.py` |
| [`detect-funding-round`](skills/detect-funding-round/SKILL.md) | Funding-round event extraction (Form D / venture round taxonomy) | `funding.py` |
| [`detect-ma-event`](skills/detect-ma-event/SKILL.md) | M&A event extraction (deal-structure taxonomy) | `maevent.py` |
| [`smiles-sanity-check`](skills/smiles-sanity-check/SKILL.md) | SMILES syntax sanity check (Weininger 1988; OpenSMILES 1.0) | `smiles.py` |

### Writing

Getting the finished analysis in front of a reader in a form they can act on.

| Skill | Method | Tool |
| --- | --- | --- |
| [`cite-ieee`](skills/cite-ieee/SKILL.md) | IEEE numbered-bracket citation style | `ieee.py` |
| [`estimative-language`](skills/estimative-language/SKILL.md) | Estimative language — words of estimative probability and analytic confidence | `wep.py` |
| [`pyramid-principle`](skills/pyramid-principle/SKILL.md) | The Pyramid Principle (governing thought, MECE support, SCQ framing) | — |
| [`write-imrad-report`](skills/write-imrad-report/SKILL.md) | IMRAD (Introduction, Methods, Results, Discussion) | — |
| [`write-sbar-brief`](skills/write-sbar-brief/SKILL.md) | SBAR (Situation, Background, Assessment, Recommendation) | — |

<!-- CATALOG:END -->

## Methodology deep-dives

[`methodologies/`](methodologies/README.md) holds 28 long-form treatments of the underlying methods — origins, core concepts, full process detail, strengths and limitations, documented case studies, and an Agent Adaptation section (roles, pipeline, prompt templates, failure modes, human-in-the-loop gates, I/O contract) for each. Where a methodology counterpart exists, the skill and deep-dive link to one another. Start with [`methodologies/agent-playbook.md`](methodologies/agent-playbook.md) for the role catalog and end-to-end pipeline recipes. This directory is part of the published research and provenance record, not build residue.

## Evaluating and reporting issues

```bash
make check      # structural gate: frontmatter, links, self-containment, script self-tests
make score      # deterministic 12-dimension scorecard, with deltas against the baseline
make compare    # compare current results with the preserved pre-publication baseline JSON
make trigger    # discoverability eval over every skill's evals/evals.json
make index      # regenerate index.json and the catalog above from frontmatter
make validate   # claude plugin validate --strict (needs the Claude Code CLI)
make all        # all of the above
```

CI runs the same gates on every push to `main` and on manual dispatch. This is an
**issue-only, maintainer-authored repository**: pull requests, code contributions,
co-maintenance and collaboration proposals are not accepted. [`CONTRIBUTING.md`](CONTRIBUTING.md)
documents the reporting policy, house style, companion-tool conventions and maintainer review
bar. A skill that misrepresents a method is the most valuable issue you can file — quote the
line and the primary source. Pull requests are disabled in the repository settings.

## On provenance

These skills encode methods developed by other people. Where a technique has a canonical source, the skill names it: Heuer for ACH, Klein for the premortem, Wardley for evolution stages, NASA for TRL, Cochrane for RoB 2, Shea et al. for AMSTAR 2, the GRADE Working Group for certainty ratings, Saaty for AHP, Kahneman & Lovallo and Flyvbjerg for reference-class forecasting, ODNI/PHIA/IPCC for calibrated uncertainty language, Zwicky and Ritchey for morphological analysis, Dhuliawala et al. for Chain-of-Verification. The contribution here is the adaptation into an agent-executable, verifiable form — not the underlying method.

## Origin

Extracted from [Radarist](https://github.com/radarist), a technology-intelligence system where these skills run inside research missions. References to that system's internals were removed so each skill stands alone, and a denylist in `evaluation/check_repo.py` keeps them out. Skills specific to that system's workflow and development pipeline are deliberately not included — they are procedures, not analytical methods.

## License

MIT — see [LICENSE](./LICENSE). Cite with [CITATION.cff](./CITATION.cff).

The MIT grant covers this repository's own text and code. It does **not** relicense the
third-party material some skills reproduce: CC BY, CC BY-SA, OGL v3, Apache-2.0 and
US-public-domain sources are listed file by file, with their rights holders and the required
attribution statements, in [THIRD-PARTY-NOTICES.md](./THIRD-PARTY-NOTICES.md). Read it before
redistributing.
