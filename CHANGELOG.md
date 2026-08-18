# Changelog

All notable changes to this library are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/) at the library level (`.claude-plugin/plugin.json`).
Per-skill `metadata.version` records that skill's content revision; it is not a separately
tagged package release. Version 1.0.0 is the first public tag. The development history below
records pre-publication milestones and does not imply earlier public tags or retained public
commits.

## [1.0.0] — 2026-08-18

Initial public release: 69 structured analytic skills, 36 deterministic companion tools,
365 routing eval cases, multi-client plugin metadata, and an evidence-oriented audit trail.
There is no earlier public release to upgrade from; the detailed entries below record the
corrections and hardening completed before publication.

An independent audit of the whole library, run against published sources and the Agent
Skills specification rather than this repository's own rubric, followed by remediation of
everything it found. Full findings: [`evaluation/independent-audit-2026-08-17.md`](evaluation/independent-audit-2026-08-17.md).

### Pre-publication corrections
- **`brier-score-calibration`** — the calibration direction compared observed frequency to
  the *bin midpoint* instead of the mean stated probability, so a perfectly calibrated
  forecaster (ten forecasts at 0.70, seven resolving true) was reported as
  "underconfident". Now compared against the mean forecast, with a regression test.
- **`detect-funding-round`** — exponential-backtracking ReDoS. Compiling name-embedding
  patterns with `re.IGNORECASE` let `[A-Z]` match lowercase, creating ambiguous alternation
  inside an unbounded quantifier; a 134-byte input took 6.6 s. Case-insensitivity is now
  scoped with inline `(?i:...)` and the same input takes 0.3 ms.
- **`systematic-review`** — the PRISMA 2020 flow omitted the "reports sought for retrieval"
  and "reports not retrieved" boxes, so the arithmetic could not reproduce a compliant
  diagram. Added, with `--sought` and `--not-retrieved`.
- **`verify-citations`** — the DOI pattern rejected legacy SICI-style DOIs containing
  `<` and `>`, which made the checker fail on genuine citations, and its error message
  attributed the Crossref `\d{4,9}` heuristic to ISO 26324. Both corrected; the crawl
  delay now defaults to 3 s to match arXiv's terms.
- **`meta-analysis`** — non-finite input passed validation (every NaN comparison is false,
  so `se <= 0` never caught it), and Egger's regression divided by zero when all standard
  errors were equal. Both rejected with messages that distinguish "k < 3" from
  "no spread in precision".
- **`smiles-sanity-check`** — the valence test rejected valid hypervalent sulfur and
  phosphorus (`CS(C)C`, `CP(C)(C)C`) by testing set membership rather than the maximum
  permitted valence, contrary to OpenSMILES 3.1.5.
- **`chemistry-claim-check`** — Unicode homoglyphs in element symbols were silently parsed
  as valid; they now raise with the offending codepoint.
- **`quantitative-sanity-check`** — the CAGR tolerance ignored the precision of the stated
  claim, flagging correctly rounded figures.
- Four incorrect ISBNs, verified against Open Library and corrected.

### Included and hardened
- **Provenance labelling across 15 skills.** Where this library adds thresholds, scoring
  bands, checklists or categories that the cited method does not contain, the addition is
  now labelled as this library's own rather than left under the cited author's authority.
  Corrections found in the same pass include: I² adjectives re-attributed to Higgins,
  Thompson, Deeks & Altman (*BMJ* 2003); Heuer's eighth ACH step (milestones) restored;
  ICD 203 §D.2.e corrected to §D.6.e; IEEE combined citations changed from `[1, 4]` to
  `[1], [4]` per the IEEE Reference Guide; Klein's 30 % premortem figure attributed to the
  2007 *HBR* piece; the Kass & Raftery Bayes-factor scale distinguished from Jeffreys'.
- **Third-party licensing.** [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) records the
  licence of every instrument the library builds on. Material from sources that do not
  permit redistribution — Cochrane RoB 2 (CC BY-NC-ND), the amstar.ca checklist, the GRADE
  Handbook, the IEEE Reference Guide, IPCC AR5, the UK PHIA yardstick — is now described
  and cited rather than reproduced. Wardley Maps material (CC BY-SA) is attributed in
  place, since CC BY-SA is not compatible with this library's MIT licence.
- **Gates made falsifiable.** The trigger eval's routing metric was printed but never
  enforced — a deliberately sabotaged retriever still passed. It is now gated by
  `--min-routed`. A skill with no computational component was awarded full D10 tooling
  credit, gifting 264 of 552 points across 33 skills; D10 is now marked not-applicable and
  its weight redistributed. Checkers that inspect zero items now fail instead of passing.
- `make all` now runs the same thresholds as CI (`--min-rank1 0.98`, `--min-negative 0.98`,
  `--min-routed 0.90`, `--min-score 95`, `--min-library 99`), so a green local run predicts
  a green CI run.
- **One exit-code convention, enforced.** The documented house rule was `1` usage / `2`
  failing verdict, but `argparse` hardcodes `2` for usage errors, so honouring it required
  an `ArgumentParser` subclass in every script — and 13 of 36 did not have one. A caller
  could not tell "you invoked me wrong" from "your citations are bad", which matters
  because `verify-citations` is documented as dropping into a publishing gate. All 36
  tools now follow the convention of `grep`, `diff`, `flake8` and `pytest`: `0` the check
  passed, `1` the tool ran and its verdict is a failure, `2` usage error or unusable
  input. Sixteen `ArgumentParser` subclasses were removed, 13 verdict paths moved from `2`
  to `1`, and 24 input-error paths from `1` to `2`. `evaluation/exit_codes.py` enforces all
  three codes against the real binaries (194 cases) and statically rejects the two patterns
  that caused the collision; it is wired into `make all` and CI.
- Scorecards in [`README.md`](README.md) and [`evaluation/report.md`](evaluation/report.md)
  were regenerated from `evaluation/scores/*.json`, with both columns produced by the same
  scorer before the clean-root public release. The baseline JSON remains for comparison; its
  pre-publication source tree is not part of the public Git history.
- **Issue-only governance and release packaging.** The public maintenance policy now accepts
  issue reports but not pull requests, code contributions, co-maintenance or collaboration
  proposals. Issue templates cover fidelity, reproducible bugs and skill proposals, and pull
  requests are disabled in the GitHub repository settings.
- GitHub Actions dependencies are pinned to immutable commits for the current Node 24-based
  releases; `setup-uv` caching is disabled because this stdlib-only repository has no dependency
  lockfile to cache.

### First audit measurement (superseded by the second pass)
Library **99.9**, mean skill **99.9**, median **100.0**, lowest **99.3**, repo hygiene
**100.0**, **4,349 / 4,356** mechanical checks, 365 trigger cases at 100 % rank-1 and 100 %
negative hold, 36 / 36 tool self-tests passing, and 194 / 194 exit-code cases conforming. The seven outstanding checks are one soft
rule — seven skills 40–113 words over the D11 word budget, all of them skills whose sourced
attribution grew in the labelling pass. That residual is deliberate: closing it would mean
deleting cited text or adding a `references/` directory purely to claim the rule's +1
credit.

### Final verification and measurement (2026-08-18)

An independent verification pass re-checked every Fix-first/Hold finding from the audit
against the remediated tree ([`evaluation/second-pass-2026-08-18.md`](evaluation/second-pass-2026-08-18.md)).
All eight blockers verified closed; 35 of 45 findings verified as remediated. Ten findings
re-opened and fixed the same day: the Saaty random-index provenance disclosure
(`decision-matrix-mcda`), stale DOI-rule documentation (`verify-citations`), an impossible
filing date in a `[validated]` tag (`claim-provenance`), a small-n caveat on the orthogonality
verdict (`position-competitor`), an S-curve example plotted over years with no literature
(`assess-research-momentum`), a market-sizing cascade that confused its TAM/SAM/SOM layers
(`estimate-market-size`), the unsupported "written while Minto was at McKinsey"
(`pyramid-principle`), the Keep a Changelog date (1.1.0 is 2019-02-15) and version (2.0.0
shipped 2026-06-07) (`analyze-release-notes`), both 2020 Cynefin renames attributed to the
St David's Day post that introduces them (`cynefin-classification`), and the MICMAC label scoped
to the direct stage actually computed (`cross-impact-analysis`). The seven skills over the
D11 word budget were tightened under it without deleting cited text; the library now scores
**100.0** with **4,356 / 4,356** checks.

## Pre-publication development history

These milestones explain how the initial public release was built. They were never published
as installable releases or Git tags.

### Final capability refresh — 2026-08-17

#### Added
- `value-intellectual-property`, implementing WIPO's 2025 cost, market, income/DCF,
  probability-adjusted NPV and real-options triage for innovation and technology-transfer
  teams, plus deterministic `ipvalue.py` calculations.
- `agents/openai.yaml` metadata for every skill, generated and checked by
  `evaluation/build_openai_metadata.py`, so Codex and ChatGPT show readable skill titles,
  compact descriptions and invocation prompts.
- A current research refresh covering Codex, Claude and Kimi loading, the latest official
  eval schema, 2026 agent-skill evaluation research, and WIPO's 2026 patent-analytics work.

#### Changed
- All 69 `evals/evals.json` files now use Anthropic skill-creator's canonical
  `{skill_name, evals}` envelope with integer IDs, `prompt`, `expected_output`, `files` and
  `expectations`. Routing negatives retain `kind`, `skills`, `case_id` and
  `requires_input` as extensions. `evaluation/eval_schema.py` validates and migrates the
  format, and the structural gate rejects stale or unresolved fixtures.
- Codex, Claude and Kimi installation instructions now use each client's current discovery
  mechanism and call out Codex's initial skill-list budget.
- Frontmatter descriptions now use a strict JSON-quoted YAML subset. This fixes 25
  cross-client parse failures that Claude's plugin validator accepted but OpenAI's
  agentskills.io reference validator (`agentskills validate`) rejected; the local structural gate now prevents a
  recurrence, and all 69 skills pass both validators.
- A blind Codex forward test iterated `value-intellectual-property` from a 6/8 tie to 8/8
  versus 6/8 without the skill (+33.3% relative on that case), chiefly by fixing scope
  restatement and keeping replacement cost outside economic reconciliation.
- The deterministic gate now covers 69 skills, 36 companion tools and 365 trigger cases;
  trigger rank-1 and negative hold are both 100%. (Check counts quoted in this and earlier
  entries were measured by the scorer as it stood at that milestone; see 1.0.0 for the current
  figures under the hardened scorer.)

### Library expansion and evaluation redesign — 2026-08-17

The library grew from 59 to 68 skills and from 12 to 35 companion tools. Measured with the
deterministic scorer (`make score`), the library score moved **73.4 → 100.0** and every
skill now passes all of its mechanical checks (4,290 / 4,290); the trigger eval ranks the
owning skill first for 100 % of 216 positive prompts and holds 100 % of 143 near-miss
negatives. The before-figure is the previous development snapshot scored with the *same* scorer.

#### Added
- **Deterministic evaluation suite** (`evaluation/`): `score_skills.py` (12-dimension,
  weighted, mechanically-checked scorecard with per-check diagnostics, baseline diffing
  and CI gates), `trigger_eval.py` (BM25 discoverability eval over per-skill
  `evals/evals.json` cases: rank-1 rate, MRR, near-miss negatives), `build_index.py`
  (generated machine-readable catalog `index.json`, `--check` for CI).
- **Per-skill eval cases** (`skills/<name>/evals/evals.json`, superset of the
  anthropics/skills `skill-creator` schema): positive prompts, near-miss negatives that
  route to a named sibling, and expected behaviours.
- **Nine new skills** from the coverage audit against Heuer & Pherson's technique families,
  ODNI ICD 203/206, the UK PHIA yardstick, IPCC uncertainty guidance and evidence-based
  practice: `estimative-language` (calibrated likelihood and confidence language),
  `reference-class-forecasting` (the outside view), `indicators-validation` (signpost
  diagnosticity), `decision-matrix-mcda` (AHP weights with a consistency ratio),
  `expected-value-decision-tree` (EV roll-back, EVPI/EVSI, tornado sensitivity),
  `morphological-analysis` (Zwicky box with cross-consistency assessment),
  `quality-of-information-check` (ICD 206 source audit),
  `amstar2-review-appraisal` (critical appraisal of systematic reviews),
  `high-impact-low-probability` (pathways and warnings for improbable, severe events).
- **Companion tools** (stdlib-only, `--selftest`, `--help`, JSON I/O, deterministic,
  offline by default) for skills whose method contains real arithmetic:
  `chem.py`, `citecheck.py`, `rob2.py`, `grade.py`, `power.py`, `ieee.py`, `claims.py`,
  `trl.py`, `admiralty.py`, `landscape.py`, `funding.py`, `maevent.py`, `osshealth.py`,
  `trend.py`, `relnotes.py`, `positioning.py`, plus `wep.py`, `refclass.py`,
  `indicators.py`, `mcda.py`, `dtree.py`, `morph.py` and `amstar2.py` for the new skills —
  35 in total, up from 12. Self-tests assert against published values (Saaty's AHP
  matrices, Cohen's power tables, the RoB 2 algorithm figures, the GRADE Handbook tables,
  PubChem molecular weights, semver.org's precedence chain, ISO check-digit specs).
- `requires_input` on eval cases that presuppose an artifact the user would attach, so the
  model-based harness skips them instead of scoring an "I need the document" reply as a
  failure. Twenty-five of 216 positive cases carry the flag.
- Plugin packaging (`.claude-plugin/plugin.json`, `marketplace.json`), CI workflow,
  `CONTRIBUTING.md` (house style v2 + tool conventions), `CITATION.cff`, `SECURITY.md`,
  `CODE_OF_CONDUCT.md`.

#### Changed
- Every `SKILL.md` restructured to house style v2: third-person, trigger-focused
  descriptions with quoted phrases and an exclusion clause; `license` and `metadata`
  (category, method, origin, version) frontmatter; fixed section order (When to invoke →
  Procedure → Output template → Worked example → Verification → Companion tool → Pair with →
  Anti-patterns → Reference).
- Method-fidelity corrections found by a source-by-source audit (details in
  `evaluation/report.md`): NATO Admiralty credibility definitions, NASA TRL 6/7 wording
  and citations, RoB 2 overall-judgement rule, GRADE two-level down/upgrades,
  scenario-planning probability doctrine, Cynefin's fifth domain, Three Horizons
  attributions, SIFT/lateral-reading citation, and others.
- Remaining origin-system jargon removed; `check_repo.py` denylist extended.

- Generated README catalog: the tables between the `CATALOG` markers are rebuilt from
  frontmatter by `build_index.py`, so the catalog cannot drift from the skills on disk.

#### Fixed
- `sanity.py --help` crashed on an unescaped `%` in an argparse help string while
  `--selftest` passed — the tool's CLI was unusable and the old checker was green. D10 now
  runs `--help` as well as `--selftest`.
- Scorer section detection took the first heading matching a pattern, so a prose heading
  containing "format" or "validation" could hijack a check away from the real
  `## Output template` or `## Verification`. Checks now evaluate across every matching
  section and take the best result.

#### Removed
- Judgement-scored spreadsheets from the previous evaluation pass (moved to
  `evaluation/history/2026-08-v1/`); superseded by the deterministic scorer.
- Citations that could not be verified against a primary source, rather than patching them:
  an unverifiable IEEE SysCon software-TRL paper, a mis-scoped Hiltunen reference, a false
  Drucker attribution, the SBAR "U.S. Navy submarine" origin story, and several others
  listed in `evaluation/report.md`.

### Earlier milestones

- **2026-08 — self-containment pass:** citation fixes, worked examples and hardened repository checks.
- **2026-07 — initial extraction:** 41 structured analytic techniques adapted as agent skills.
