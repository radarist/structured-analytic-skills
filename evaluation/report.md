# Evaluation report — pre-publication pass

> **Historical report.** This records an internal pre-publication measurement pass and its
> original behavioral probes. It is not the current release scorecard. For v1.0.0 release readiness, read the
> [`independent audit`](independent-audit-2026-08-17.md), the
> [`second-pass verification`](second-pass-2026-08-18.md), and the generated
> [`scores/latest.md`](scores/latest.md). The named baseline commit belongs to the private
> pre-publication development history and is not present in the clean-root public repository;
> its score artifacts are retained, but the source-tree rerun described below is historical.

How this library was measured, what the measurement found, what changed, and what the
numbers say now. Every figure in the scorecard tables comes from
[`score_skills.py`](score_skills.py). The "before" column is the pre-improvement commit
(`6882e92`) scored with the **same** scorer via `make baseline`, so the comparison is
like-for-like rather than a rubric change dressed up as an improvement.

## 1. Headline

| Metric | Before (commit 6882e92) | After (pre-publication pass) | Δ |
|---|---|---|---|
| Library score (0–100) | 70.4 | **99.9** | +29.5 |
| Mean skill score | 77.5 | **99.9** | +22.4 |
| Median skill score | 77.1 | **100.0** | +22.9 |
| Lowest skill score | 61.3 | **99.3** | +38.0 |
| Repo-hygiene score | 30.0 | **100.0** | +70.0 |
| Skills scored | 59 | **69** | +10 |
| Mechanical checks passed | 2902 / 3708 | **4349 / 4356** | +1447 checks |
| Companion tools | 12 | **36** | +24 |
| Skills with eval cases | 0 | **69** | +69 |

Per-dimension means (0–100 per dimension, weighted into the skill score):

| Dimension | Weight | Before | After | Δ |
|---|---|---|---|---|
| D1 spec compliance | 10 | 100.0 | **100.0** | +0.0 |
| D2 discoverability | 12 | 62.9 | **100.0** | +37.1 |
| D3 procedure | 12 | 98.6 | **100.0** | +1.4 |
| D4 output contract | 10 | 77.6 | **100.0** | +22.4 |
| D5 boundaries | 8 | 93.2 | **100.0** | +6.8 |
| D6 cross-links | 8 | 96.0 | **100.0** | +4.0 |
| D7 worked example | 10 | 61.7 | **100.0** | +38.3 |
| D8 verification | 8 | 20.8 | **100.0** | +79.2 |
| D9 provenance | 8 | 83.3 | **100.0** | +16.7 |
| D10 tooling | 8 | 72.7 | **100.0** | +27.3 |
| D11 efficiency | 3 | 97.6 | **98.0** | +0.4 |
| D12 hygiene | 3 | 96.1 | **100.0** | +3.9 |

Trigger (discoverability) eval: 365 eval cases across 69 skills: 100% of 219 positive prompts rank the owning skill first (MRR 1.000), and 100% of 146 near-miss negatives correctly do not. The library score rose 29.5 points, or 41.9% relative to the 70.4 baseline, far exceeding the requested 10% improvement threshold.

**Why 99.9 and not 100.0.** Seven skills sit 40–113 words above the D11 soft word budget (1600 words), scoring 2 of 3 on `D11.word-budget`; every other check in the suite passes. Those seven are the skills whose provenance text grew during the labelling pass that separated each method's published content from this library's own additions. The two ways to close the gap — cutting sourced attribution, or adding a `references/` directory purely to collect the rule's +1 progressive-disclosure credit — would both trade reader value for a counter. The residual is left in place deliberately: a defensible 99.9 is worth more than a gamed 100.0, and D11 is a soft budget by design.

The final pre-publication refresh adds a current WIPO-backed IP-valuation skill and tool, migrates every eval
to Anthropic skill-creator's executable schema, and adds generated Codex/ChatGPT metadata
for every skill. The deterministic conformance score was already at its 100-point ceiling in
the preceding expansion pass; these additions expand capability and interoperability without pretending the ceiling
measures runtime usefulness.

## 2. What "state of the art" meant for this pass

Four research threads fed the redesign; the full notes, with source URLs, are in
[`research/`](research/).

1. **Standards and official tooling** ([`research/01`](research/01-agent-skills-spec-and-tooling.md)).
   The Agent Skills specification fixes the frontmatter contract (`name` = directory name,
   `^[a-z0-9]+(-[a-z0-9]+)*$`, ≤ 64 chars; `description` ≤ 1024; optional `license`,
   `compatibility`, `metadata`, `allowed-tools`) and the progressive-disclosure budget
   (SKILL.md under ~500 lines, heavy material one level deep in `references/`). Anthropic's
   authoring guidance adds third-person what-plus-when descriptions with specific triggers,
   concrete examples, workflows with checklists, feedback loops, and the skill-creator eval
   loop (`evals/evals.json` → grade → benchmark). Claude Code contributes
   `claude plugin validate --strict` and the plugin/marketplace manifests.
2. **What the strongest public libraries do** ([`research/02`](research/02-sota-skill-libraries-survey.md)).
   Surveying anthropics/skills, obra/superpowers, trailofbits/skills, microsoft/skills,
   vercel-labs/agent-skills, github/awesome-copilot and addyosmani/agent-skills: the 2026 bar
   is deterministic linters with token budgets in CI, trigger evals with near-miss negatives
   and a lexical rank-1 gate, paired with/without-skill evals, generated machine-readable
   catalogs, per-skill semantic versions, and loadability checks against the real CLI.
   SkillsBench's finding that focused skills beat exhaustive bundles is why SKILL.md stays
   lean and depth moves into `references/` and tools.
3. **The analytic canon** ([`research/03`](research/03-analytic-canon-coverage-and-fidelity.md)).
   A coverage map against Heuer & Pherson's six technique families, ODNI ICD 203/206, the UK
   PHIA yardstick, IPCC uncertainty guidance, GRADE/Cochrane/PRISMA/AMSTAR-2, and decision
   analysis — producing ten recommended additions and a source-by-source fidelity check of
   ten existing skills.
4. **Current ecosystem and patent refresh** ([`research/04`](research/04-2026-08-17-current-refresh.md)).
   Current OpenAI, Anthropic, Agent Skills and Kimi loading/eval contracts; GitSkills,
   ACES and cross-model skill-evaluation research; and WIPO's 2025–2026 patent analytics
   and IP-valuation guidance. This produced canonical eval envelopes, per-skill
   `agents/openai.yaml`, exact Kimi/Codex install paths and `value-intellectual-property`.

## 3. What changed

### 3.1 A deterministic evaluation suite (new)

The previous pass scored the library with a human-judgement rubric: the editor of the
changes assigned 0/1/2 per criterion against prose anchors. That is unreproducible and
unfalsifiable, so it was replaced (the v1 rubric and scoresheets are preserved under
[`history/2026-08-v1/`](history/2026-08-v1/)).

- **[`score_skills.py`](score_skills.py)** — 12 dimensions, 66 named mechanical checks, weights
  summing to 100. Every check is a regex, a file-system fact or a subprocess result, so two
  runs on the same tree are byte-identical and every lost point names the check to fix.
  `--skill NAME` prints the per-check report, `--baseline` diffs against a previous run,
  `--min-score`/`--min-library` gate CI, and `--list-checks` emits the catalogue that
  [`rubric.md`](rubric.md) documents.
- **[`trigger_eval.py`](trigger_eval.py)** — BM25 over each skill's `name` + `description`
  (method acronyms boosted, because that is how users name methods), scored against every
  case in `skills/*/evals/evals.json`: positive rank-1 rate, MRR, negatives held, confusion
  pairs, and skills with no cases. It is a lexical proxy for model routing — cheap,
  deterministic, and effective at exposing descriptions that overlap.
- **[`build_index.py`](build_index.py)** — generates `index.json` *and* the README catalog
  tables from frontmatter. The catalog cannot drift from the skills on disk because it is
  never hand-edited; `--check` fails CI when either is stale.
- **[`run_evals.py`](run_evals.py)** — optional model-based paired eval: each case is run
  with and without the skill in the system prompt through headless `claude -p`, and a judge
  model scores the answer against the case's canonical `expectations` list. Non-deterministic and
  billable, so it is reported, never gated.
- **[`eval_schema.py`](eval_schema.py)** and **[`build_openai_metadata.py`](build_openai_metadata.py)**
  — migrate/check the official skill-creator eval envelope and generate/check Codex/ChatGPT
  UI metadata for every skill.
- **[`check_repo.py`](check_repo.py)** (kept, extended) — the structural gate: frontmatter,
  strict JSON-quoted YAML descriptions, link resolution, origin-system denylist, dangling
  skill references, catalog coverage, canonical eval fixtures, current UI metadata, and
  `--selftest` for every companion script.

A robustness fix worth recording: section detection originally took the first heading
matching a pattern, so a prose heading containing the word "format" or "validation" could
hijack the check away from the real `## Output template` or `## Verification`. Checks now
evaluate across *every* matching section and take the best result — the question is whether
the skill has a copy-ready template at all, not whether the first pattern match contains one.

### 3.2 Per-skill eval cases (new)

Every skill ships `evals/evals.json` in the current anthropics/skills skill-creator envelope:
`skill_name` plus cases with integer `id`, `prompt`, `expected_output`, `files` and
`expectations`. The library adds `case_id`, `kind` (`positive` / `negative` / `edge`) and,
for negatives, the sibling that *should* handle the request. Cases are phrased as a user would phrase them — a direct
method request, a symptom-based request, a situation-based request — and each carries the
behaviours a correct answer must exhibit. They serve three purposes: the deterministic
trigger gate, a specification of what the skill is for, and a ready input to model-based
harnesses.

### 3.3 House style v2

Every `SKILL.md` was restructured to a fixed section order — overview naming the originator
and year, `When to invoke` with negative triggers that route to named siblings, numbered
`Procedure` steps, a fenced `Output template` marking mandatory fields, a concrete
`Worked example`, a `Verification` checklist, `Companion tool` where one exists,
`Pair with adjacent skills`, `Anti-patterns`, and a `Reference` list where every entry
carries author, year, venue and a locator. Descriptions were rewritten in the third person
as triggering contracts: what the skill produces, when to reach for it, quoted trigger
phrases, and an exclusion clause naming the sibling that covers the near miss — with no
summary of the procedure, since a description that gives away the workflow invites the model
to skip the body. Frontmatter gained `license` and `metadata` (category, method, origin,
version). Origin-system vocabulary that had survived the previous pass was removed.

### 3.4 Fidelity corrections (source-verified)

Each of these was checked against the primary source; the correction is what the source
actually says.

| Skill | Was | Now | Source |
|---|---|---|---|
| `rate-source-admiralty` | Credibility grade 3 defined with grade 4's wording ("possible but not logical"); other cells paraphrased | Both axes in the standard wording | NATO STANAG 2511 (2003) / AJP-2.1; U.S. Army FM 2-22.3 (2006) App. B, Tables B-1/B-2 |
| `score-technology-readiness` | TRL 6 "prototype in operational environment", TRL 7 "system prototype demonstrated"; cited NPR 7123.1C §6.5 and an unverifiable IEEE SysCon 2021 paper; "HRL" | TRL 6 relevant environment, TRL 7 operational environment; NPR 7123.1D App. E; SEI CMU/SEI-2002-SR-027 and DoD TRA Guidebook (2025) Table 2-2 for software TRL; MRL/IRL/SRL | NASA NPR 7123.1D; H2020 General Annex G; DoD TRA Guidebook (Feb 2025) |
| `assess-study-bias` | Overall rule "High = at least one high-risk domain"; description used RoB 1 vocabulary | Table 1's full rule including the several-some-concerns clause; RoB 2 domain names; assignment (ITT) effect stated | Sterne et al., *BMJ* 2019;366:l4898; RoB 2 guidance, 22 Aug 2019 |
| `evidence-appraisal` | "Move at most one level per factor"; worked example labelled a two-level downgrade "Moderate" | One or two levels per factor; large effect +1/+2; example corrected to Low | GRADE Handbook Tables 5.2/5.3/5.9; Guyatt et al. 2008; Balshem et al. 2011 |
| `scenario-planning` | Anti-pattern instructed assigning 40/30/20/10 probabilities to scenarios | Scenarios are equally plausible and carry no probabilities; probability requests route to `bayesian-update`/`delphi-method`; "Shell/GBN tradition" rather than "Shell's methodology" | Ogilvy & Schwartz, *Plotting Your Scenarios* (GBN); Millett, *JFS* 13(4):61–68 (2009); Wack, *HBR* 63(5) (1985) |
| `three-horizons` | 70/20/10 attributed to Baghai, Coley & White; time bands attributed to the book | Attributed to Nagji & Tuff, *HBR* 90(5) (2012), framed as a benchmark; bands labelled indicative | *The Alchemy of Growth* (1999); Nagji & Tuff (2012); Curry & Hodgson, *JFS* 13(1) (2008) |
| `cynefin-classification` | Four domains | Five contexts including Disorder (renamed Confused/Aporetic, 2020) with Snowden & Boone's decomposition rule | Snowden & Boone, *HBR* 85(11):68–76 (2007); The Cynefin Co. (2020) |
| `premortem-analysis` | Originator credit ambiguous | Klein (2007) credited as originator, Kahneman as populariser; procedure re-grounded on the article | Klein, *HBR* 85(9) (2007); Mitchell, Russo & Pennington, *JBDM* 2(1) (1989) |
| `sift-source-check` | Wineburg & McGrew citation conflated a 2017 working paper with the 2019 journal article; fourth move paraphrased | Both cited correctly; move 4 in Caulfield's wording | SHEG Working Paper 2017-A1 (SSRN 3048994); *Teachers College Record* 121(11) (2019) |
| `grounded-answer` | Vague "~23% F1" improvement claim | The paper's actual figures, with the ACL 2024 locator | Dhuliawala et al., Findings of ACL 2024, pp. 3563–3578 |
| `five-forces-analysis` | 2008 *HBR* volume wrong; an unverifiable Christensen "sixth force" claim | 1979 *HBR* 57(2):137–145 and 2008 86(1):78–93; complements explicitly not a sixth force | Porter (1979, 1980, 2008) |
| `brier-score-calibration` | "Resolution (sharpness/discrimination)" | Resolution (Murphy 1973) distinguished from sharpness, a property of the forecasts alone | Gneiting, Balabdaoui & Raftery, *JRSS-B* 69(2) (2007) |
| `experimental-design` | Worked example 3,842 / 7,684 per group | 3,841 / 7,682, reproduced by `power.py` | Fleiss, Levin & Paik (2003), pooled normal approximation |
| `triangulate-sources` | Mis-attributed methodological anchor | Denzin's four-type typology and ICD 206 sourcing | Denzin, *The Research Act* (1978); ICD 206 (2015) |
| `red-team-claim` | "M. Tetlock" | P. E. Tetlock | Tetlock & Gardner (2015) |
| `wardley-map-drafting` | Vague blog-range citation; unverifiable GDS reference | *Wardley Maps* (2016, CC BY-SA 4.0) with chapter locators; unverifiable entry removed | Wardley (2016–) |

Where a citation could not be verified it was **removed** rather than patched, and where a
skill is a bespoke composite rather than a published method (`foresight`, `critique-report`,
`decompose-research-question`, `grounded-fact-check`, the two event extractors) the skill now
says so instead of borrowing someone else's authority.

### 3.5 Companion tools

| Skill | Tool | What it computes |
|---|---|---|
| `amstar2-review-appraisal` | `amstar2.py` | AMSTAR 2 (A MeaSurement Tool to Assess systematic Reviews, version 2) |
| `analysis-of-competing-hypotheses` | `ach.py` | Analysis of Competing Hypotheses (ACH) |
| `analyze-patent-claims` | `claims.py` | Patent claim construction and structural claim analysis |
| `analyze-release-notes` | `relnotes.py` | Release-note parsing against SemVer, Conventional Commits and Keep a Changelog |
| `assess-research-momentum` | `momentum.py` | Bibliometric momentum assessment (publication S-curve + citation velocity) |
| `assess-study-bias` | `rob2.py` | Cochrane Risk of Bias 2 (RoB 2) for randomized trials |
| `bayesian-update` | `bayes.py` | Bayesian belief updating in odds form (prior odds × Bayes factor) |
| `brier-score-calibration` | `brier.py` | Brier score with Murphy decomposition and Brier Skill Score |
| `chemistry-claim-check` | `chem.py` | Formula arithmetic (DBE/RDBE, molecular weight) plus Lipinski's rule of five |
| `cite-ieee` | `ieee.py` | IEEE numbered-bracket citation style |
| `cross-impact-analysis` | `crossimpact.py` | Cross-impact analysis with MICMAC structural analysis |
| `decision-matrix-mcda` | `mcda.py` | Weighted Decision Matrix / Multi-Criteria Decision Analysis (MCDA) with AHP weights |
| `delphi-method` | `delphi.py` | Delphi method (anonymous iterated expert elicitation with controlled feedback) |
| `detect-funding-round` | `funding.py` | Funding-round event extraction (Form D / venture round taxonomy) |
| `detect-ma-event` | `maevent.py` | M&A event extraction (deal-structure taxonomy) |
| `estimate-market-size` | `market.py` | TAM/SAM/SOM triangulation (top-down × bottom-up Fermi estimation) |
| `estimative-language` | `wep.py` | Estimative language — words of estimative probability and analytic confidence |
| `evidence-appraisal` | `grade.py` | GRADE certainty of evidence (Grading of Recommendations Assessment, Development and Evaluation) |
| `expected-value-decision-tree` | `dtree.py` | Decision tree analysis — expected-value roll-back, EVPI/EVSI, one-way sensitivity (tornado) |
| `experimental-design` | `power.py` | Randomized experimental design with a priori power analysis and validity audit |
| `indicators-validation` | `indicators.py` | Indicators and Indicators Validator (indicators generation, validation and evaluation) |
| `meta-analysis` | `metapool.py` | Meta-analysis (fixed-effect and DerSimonian–Laird random-effects pooling) |
| `morphological-analysis` | `morph.py` | General Morphological Analysis (GMA) with Cross-Consistency Assessment (CCA) |
| `oss-project-health` | `osshealth.py` | CHAOSS community-health metrics (repository vitality read) |
| `position-competitor` | `positioning.py` | Two-axis competitive positioning map |
| `quantitative-sanity-check` | `sanity.py` | Quantitative sanity check (internal-consistency arithmetic checklist) |
| `rate-source-admiralty` | `admiralty.py` | Admiralty Code (NATO System, 6×6 source reliability × information credibility) |
| `read-patent-landscape` | `landscape.py` | Patent landscape analysis (WIPO PLR methodology) |
| `reference-class-forecasting` | `refclass.py` | Reference Class Forecasting (outside view) |
| `score-technology-readiness` | `trl.py` | Technology Readiness Level (TRL) assessment |
| `smiles-sanity-check` | `smiles.py` | SMILES syntax sanity check (Weininger 1988; OpenSMILES 1.0) |
| `systematic-review` | `prisma.py` | Systematic review reported to PRISMA 2020 |
| `test-significance` | `significance.py` | Null-hypothesis significance test with confidence interval and effect size |
| `trend-analysis` | `trend.py` | Trend analysis with Trend Impact Analysis (TIA) |
| `verify-citations` | `citecheck.py` | Scholarly identifier format and checksum validation (ISO 26324, ISO 2108, ISO/IEC 7064) |

All are standard-library-only, deterministic (two `--selftest` runs are byte-identical — CI
enforces this), offline unless an explicit flag opts in, and documented in their skill with
real sample output. Self-tests assert against published values: Saaty's own AHP matrices,
Cohen's power tables, the RoB 2 algorithm figures, the GRADE Handbook's rating tables,
PubChem molecular weights, semver.org's precedence chain, ISO check-digit specifications.

One bug worth recording: `sanity.py --help` crashed on an unescaped `%` in an argparse help
string while `--selftest` passed — the old checker was green and the tool's CLI was unusable.
D10 now runs `--help` as well as `--selftest`, which is how it was found.

### 3.6 New skills from the coverage audit

| Skill | Method | Canonical source | Tool |
|---|---|---|---|
| `amstar2-review-appraisal` | AMSTAR 2 (A MeaSurement Tool to Assess systematic Reviews, version 2) | Beverley J. Shea et al., BMJ 2017 (original AMSTAR — Shea et al., 2007) | `amstar2.py` |
| `decision-matrix-mcda` | Weighted Decision Matrix / Multi-Criteria Decision Analysis (MCDA) with AHP weights | Thomas L. Saaty (AHP, 1980); Ralph L. Keeney and Howard Raiffa (additive value model, 1976); Heuer and Pherson (Decision Matrix, SAT 3rd ed., 2019) | `mcda.py` |
| `estimative-language` | Estimative language — words of estimative probability and analytic confidence | Sherman Kent, CIA Office of National Estimates, 1964; codified in ODNI ICD 203, 2015 | `wep.py` |
| `expected-value-decision-tree` | Decision tree analysis — expected-value roll-back, EVPI/EVSI, one-way sensitivity (tornado) | Howard Raiffa, Decision Analysis (1968); Ronald A. Howard, decision analysis (1966, 1968) | `dtree.py` |
| `high-impact-low-probability` | High-Impact/Low-Probability Analysis (with "What If?" Analysis) | US Government Tradecraft Primer, 2009; Heuer & Pherson reframing techniques | — |
| `indicators-validation` | Indicators and Indicators Validator (indicators generation, validation and evaluation) | Heuer & Pherson, 2011/2014/2019; Indicators Validator by Pherson Associates, 2008; U.S. Government Tradecraft Primer, 2009 | `indicators.py` |
| `morphological-analysis` | General Morphological Analysis (GMA) with Cross-Consistency Assessment (CCA) | Fritz Zwicky, Caltech, 1940s (book 1969); computer-aided GMA and CCA — Tom Ritchey, Swedish Defence Research Agency / Swedish Morphological Society, 1995–2006 | `morph.py` |
| `quality-of-information-check` | Quality of Information Check | U.S. Government / CIA Sherman Kent School, A Tradecraft Primer, 2009; ODNI ICD 206 sourcing requirements, 2015 | — |
| `reference-class-forecasting` | Reference Class Forecasting (outside view) | Daniel Kahneman & Amos Tversky, 1979; Bent Flyvbjerg, 2006 | `refclass.py` |

Recorded but deliberately not added: real options for staged R&D, Bass diffusion fitting,
MRL/IRL/SRL readiness scales, QUADAS-2, causal loop diagrams, chronologies and timelines,
argument mapping, TRIZ.

### 3.7 Repository and packaging

Plugin and marketplace manifests (`claude plugin validate --strict` passes for the skill
tree and marketplace), agentskills.io reference validation (`agentskills validate`) over all 69 skills, a CI
workflow running the structural gate, canonical eval and UI-metadata gates, the scorecard
gate, trigger gate, catalog check, tool determinism and the agentskills reference validator; plus
`CONTRIBUTING.md` (house style and tool conventions), `CHANGELOG.md`, `CITATION.cff`,
`SECURITY.md`, `CODE_OF_CONDUCT.md`, a `Makefile`, and generated `index.json`.

## 4. Remaining gaps

Every skill passes every mechanical check, so the gaps that remain are ones the scorer
cannot see and were left deliberately:

- **Coverage.** IP valuation is now implemented, but eight high-value standalone techniques
  remain: real-options pricing for staged R&D, Bass diffusion fitting, MRL/IRL/SRL readiness,
  QUADAS-2, causal-loop diagrams, chronologies and timelines, argument mapping, and TRIZ.
  Each has a canonical source and a plausible deterministic or structured implementation.
- **Second-reader fidelity audit.** Ten skills were audited against primary sources
  line-by-line and the rest were corrected where an agent's verification surfaced an error.
  A full independent re-read of all 69 against their sources has not been done.
- **Behavioural evidence is a sample.** The Claude result covers ten skills with one case
  and one fast-judge run each; the Codex IP-valuation forward test adds one case and one run
  per arm. A defensible benchmark would need multiple runs, stronger judges, cross-model
  execution, and fixtures for the twenty-five `requires_input` cases.
- **Methodology files were not re-audited.** The 28 long-form treatments in
  `methodologies/` gained skill back-links and a corrected depth target, but their own
  citations were not re-verified in this pass.
- **Cross-model testing remains narrow.** The original paired sample used Claude and the
  IP-valuation forward test used Codex, but a complete matrix across Codex, Claude,
  Kimi and model tiers has not been run.

## 5. Does the skill actually change the answer?

The deterministic score says a skill is well-formed; it cannot say the skill helps. For
that, [`run_evals.py`](run_evals.py) runs each eval case twice in a headless session — once
with the skill's body in the system prompt, once without — and asks a judge model whether
each canonical `expectations` check holds. The sample below is small, single-run and scored
by a fast judge model, so treat it as a signal rather than a benchmark; it is reported, not
gated.

| Skill | Case | With skill | Without skill | Δ |
|---|---|---|---|---|
| `analysis-of-competing-hypotheses` | ach-pos-1 | 0.00 | 0.00 | +0.00 |
| `decision-matrix-mcda` | mcda-pos-1 | 0.00 | 0.20 | -0.20 |
| `estimative-language` | estimative-language-pos-2 | 0.75 | 0.25 | +0.50 |
| `evidence-appraisal` | grade-pos-1 | 0.75 | 0.25 | +0.50 |
| `indicators-validation` | indval-pos-1 | 1.00 | 0.00 | +1.00 |
| `key-assumptions-check` | kac-pos-1 | 1.00 | 0.20 | +0.80 |
| `premortem-analysis` | premortem-pos-1 | 1.00 | 0.40 | +0.60 |
| `rate-source-admiralty` | admiralty-pos-1 | 0.75 | 0.75 | +0.00 |
| `reference-class-forecasting` | rcf-pos-1 | 0.17 | 0.17 | +0.00 |
| `scenario-planning` | scenario-pos-1 | 1.00 | 0.40 | +0.60 |
| **Mean** | | | | **+0.38** |

Each cell is the fraction of that case's `expectations` checks a judge model found in the answer (model haiku, judge haiku, one run per arm). A positive Δ means the skill changed what the model actually did.

The IP-valuation addition also received a separate Codex forward test on an unseen
licensing task. Its first draft tied the unassisted answer at 6/8; the misses led to an
explicit scope-restatement rule and to keeping replacement cost outside economic
reconciliation. The revised skill-guided answer scored **8/8 versus 6/8 unassisted** under
a blind eight-check rubric: +25 percentage points, or **+33.3% relative**. The complete
protocol, iteration trace, rubric and single-run caveat are in
[`scores/forward-test-2026-08-17.md`](scores/forward-test-2026-08-17.md).

The pattern matters more than the mean. The six skills with a large lift
(`indicators-validation` +1.00, `key-assumptions-check` +0.80, `premortem-analysis` and
`scenario-planning` +0.60, `estimative-language` and `evidence-appraisal` +0.50) are those
where the method supplies structure the model can apply immediately to the request as
stated. The four flat-or-negative results are all skills whose method operates on data the
user holds — an evidence set for ACH, a reference class of past outcomes, a scored option
matrix for MCDA — and where a model's correct first move is to ask for that data rather
than invent it. `rate-source-admiralty` is flat for a different reason: grading a single
source is something a capable model already does reasonably well without the skill, and the
skill's value there is the two-axis discipline and the shared vocabulary, which this rubric
does not reward. None of these are reasons to claim a uniform benefit, and the numbers are
reported as measured.

Running this eval also surfaced a defect in the eval cases themselves, which is the point of
running it. Twenty-five of the 219 positive cases ask the model to work on an artifact the
user would attach — "rewrite **this** assessment", "validate the identifiers in **this**
bibliography" — without supplying it. Those are realistic trigger phrasings and correct for
the retrieval eval, but as behavioural cases both arms correctly answer "send me the
document" and score zero, which reads as a skill failure and is not one. They now carry
`"requires_input": true`; the harness skips them by default and says how many it skipped, and
`CONTRIBUTING.md` requires new cases to be self-contained or to declare their fixture.

## 6. Limitations and judgement calls

- **A perfect score means the gate is met, not that the work is finished.** Every skill
  now passes every mechanical check, so the scorer no longer discriminates between the
  skills — by design. It is a conformance floor: it certifies that each skill is
  spec-valid, self-contained, procedurally complete, has a copy-ready output contract, a
  concrete worked example, a verification checklist, resolving cross-links, dated and
  located citations, and a working tool where the method needs one. What separates a good
  skill from a merely conforming one is method fidelity and usefulness, which the score
  cannot see. CI gates the floor (`--min-score 95 --min-library 99`) so it cannot silently
  erode.
- **A deterministic score measures structure, not truth.** It cannot tell whether a
  procedure faithfully represents its method or whether a citation says what the skill
  claims. That is what the fidelity audit in §3.4 is for, and a full second-reader audit of
  every skill remains the natural next step.
- **The trigger eval is a lexical proxy.** BM25 rank-1 accuracy exposes overlapping and
  under-specified descriptions cheaply and reproducibly; it is not a claim about how any
  particular model routes. `run_evals.py` and `claude plugin eval --ablation` are the
  model-based complements.
- **Model-based paired evals were sampled, not exhaustive.** They cost money and vary run to
  run, so they are reported rather than gated.
- **Content was edited by parallel agents against a written specification**, each change
  verified by the scorer, `check_repo.py` and the official validator, with fidelity notes
  drawn from the audit and re-checked against primary sources. Numbers in worked examples
  come from the companion tools where one exists; illustrative data is labelled as such.
- **Methodology deep-dives were left as-is** apart from skill back-links. They average
  ~2,200 words against a template that asked for "400–700 lines" — a target that conflated
  lines with depth, now restated in words.
