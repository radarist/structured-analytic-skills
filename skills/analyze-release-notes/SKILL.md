---
name: analyze-release-notes
description: "Turns a release note or changelog into a structured record — version and prior version, the SemVer bump, breaking changes and deprecations quoted verbatim, bug-fix count, CVE/GHSA advisories — and rates how much the release should worry a consumer. Use when a version delta is on the table: \"what changed in v2.4?\", \"read this changelog\", \"any breaking changes before upgrading?\", \"what deprecations land in the next release?\". Not for repository-level maintenance health — use `oss-project-health` instead."
license: MIT
metadata:
  category: technology-assessment
  method: Release-note parsing against SemVer, Conventional Commits and Keep a Changelog
  origin: T. Preston-Werner, Semantic Versioning 2.0.0, 2013; Keep a Changelog 1.1.0, 2019 (2.0.0 in 2026)
  version: "2.0.0"
---
# Analyze Release Notes

A structured read of one release note against the three conventions its authors most likely followed: Semantic Versioning 2.0.0 (Tom Preston-Werner, 2013) — MAJOR means backwards-incompatible change, MINOR new backwards-compatible functionality, PATCH backwards-compatible fixes; Conventional Commits 1.0.0 (2019), whose `!` marker and `BREAKING CHANGE:` footer name breakage explicitly; and Keep a Changelog (Olivier Lacan; 1.1.0 in 2019, 2.0.0 in 2026 — the six section types are unchanged), whose Added / Changed / Deprecated / Removed / Fixed / Security sections carry the author's own classification. The version number is a compatibility claim that the note's text can confirm or contradict, so the parse always compares the two. It prevents shipping "just a patch" past a consumer who then breaks in production.

## When to invoke

Invoke when:

- A version delta needs reading: "what changed in v2.4?", "read this changelog", "any breaking changes before upgrading?", "what deprecations land in the next release?".
- A dependency bump, upgrade plan or migration note depends on what a release removed or renamed.

Do NOT invoke when:

- The question is whether the project is maintained — bus factor, cadence, abandonment — use `oss-project-health`; this skill reads one release, that one the repository.
- The text is a launch post with no version and no dated delta: nothing to diff.
- The announcement is a financing or acquisition — use `detect-funding-round` or `detect-ma-event`.
- The claim to check is a benchmark number in the notes — use `benchmark-model-claims` for the measurement.

## Procedure

### 1 — Identify the version, the prior version and the scheme

Parse the version from the heading, tag or URL and determine the scheme: SemVer (`MAJOR.MINOR.PATCH` with optional `-prerelease` and `+build`) or calendar versioning (`2026.04.01`). For SemVer, compare with the prior version — from an explicit "since X", the next-lower changelog heading, or the caller — and set the bump from the first differing component. For calendar versions set `semver_bump: "calver"` and skip the comparison: a date encodes no compatibility promise. Record a yanked release as yanked.

### 2 — Partition the body and tag every entry

Split the note into entries — top-level bullets, or the sentences of prose paragraphs — and tag each with one category: breaking change, deprecation, removal, new feature, enhancement, bug fix, security fix, performance, docs, dependency bump, other. Classify in precedence order: explicit markers first (`type!:` or an uppercase `BREAKING CHANGE:` footer per Conventional Commits; a CVE or GHSA identifier), then the author's own section heading (Keep a Changelog's Added / Changed / Deprecated / Removed / Fixed / Security), then phrase cues. Cue lists: `references/cue-vocabulary.md`. Removals map into breaking changes: removing public functionality is backwards-incompatible under SemVer §8.

### 3 — Quote breaking changes and deprecations verbatim

Capture each breaking change as the author wrote it, with the migration path if one is given, and each deprecation with its removal horizon ("will be removed in 3.0"). Do not paraphrase: downstream consumers match on the exact symbol name, and a reworded entry stops matching. Count bug fixes as an integer — an entry saying "7 fixes" counts 7 — and list CVE and GHSA identifiers separately from bug fixes, since advisories have their own handling.

### 4 — Check the version against the content

Compare the bump with the entries. Breaking changes without a major bump, or a major bump with no breaking entry, is an inconsistency worth flagging: the version's compatibility claim is not supported by the note. Two exceptions stay informational: `0.y.z`, where anything may change (SemVer §4), and `0.x → 1.0.0`, which may be a stabilisation release (SemVer §5). Say which convention the project appears to follow, and whether it followed it here.

### 5 — Grade the source

Grade the note with `rate-source-admiralty`: a release tag on the project's own repository or docs domain is A1; a vendor email or package-registry page (npm, PyPI) A2; a third-party changelog aggregator B2–C2; a blog rewrite C3 or worse. The grade travels with the record, because a rewritten changelog loses the verbatim wording step 3 depends on.

### 6 — Rate the impact and report

Rate the release: **high** — a major bump, any breaking change, or any security advisory; **medium** — a minor bump with features or deprecations; **low** — a patch bump with only fixes. Then fill the output template, keeping the category counts, the consistency flag and the parse confidence so a reader sees how much came from structure and how much from cues.

## Output template

```json
{
  "project_name": "vectordb-lite",
  "version": "2.0.0",
  "prior_version": "1.9.3",
  "scheme": "semver | calver",
  "semver_bump": "major | minor | patch | prerelease | calver | none",
  "released_date": "2026-03-14",
  "yanked": false,
  "breaking_changes": ["verbatim entry text"],
  "new_features": ["verbatim entry text"],
  "deprecations": ["verbatim entry text — removal horizon"],
  "bug_fixes": 7,
  "security_advisories": ["CVE-2026-12345"],
  "semver_consistency": "ok | flag: breaking changes without a major bump",
  "impact": "high | medium | low",
  "source_url": "https://...",
  "source_grade": "A1",
  "confidence": 90
}
```

Mandatory fields: `version`, `scheme`, `semver_bump`, `breaking_changes`, `deprecations`, `security_advisories`, `impact`, `source_grade`. Absent categories are empty lists, never invented; `prior_version` is `null` when none could be established, and the bump is then `null` too.

## Worked example

Illustrative changelog fragment (synthetic project `vectordb-lite`), reproduced with `python3 scripts/relnotes.py --demo`:

```
## [2.0.0] - 2026-03-14
### Breaking
- Dropped Python 3.8 support; minimum is now 3.10
- query() now returns a Result object instead of a plain dict
### Added
- Hybrid search (BM25 + vector fusion)
### Deprecated
- search() — use query(); will be removed in 3.0
### Fixed
- 7 fixes, including index corruption on concurrent writes
```

`scan --from 1.9.3 --report` gives: version 2.0.0, prior 1.9.3, bump **major**, scheme semver, released 2026-03-14; 5 entries — 2 breaking changes, 1 deprecation, 1 new feature, 1 bug-fix entry counting `bug_fixes: 7`; the deprecation carries removal horizon 3.0; no CVE or GHSA identifiers, so `security_advisories: []`. Consistency: ok — a major bump with two breaking entries is what SemVer §8 requires. Impact: **high**, from both the bump and the breaking changes. Parse confidence 90/100: +40 base, +20 version from a heading, +10 date, +10 prior version supplied, +10 recognised Keep a Changelog headings. Note what is *not* paraphrased: "query() now returns a Result object instead of a plain dict" is stored exactly, because a consumer greps for `query(` and `Result`; and "dropped Python 3.8 support" is breaking even though it reads as a support-matrix line.

## Verification

- [ ] The bump was recomputed from the two version strings (`scripts/relnotes.py semver bump`), not read from the announcement's adjective.
- [ ] Every breaking change and deprecation is the author's wording, with symbol names intact; nothing was paraphrased.
- [ ] Deprecations carry a removal horizon where the note states one.
- [ ] CVE and GHSA identifiers are in `security_advisories`, not folded into `bug_fixes`.
- [ ] Absent sections are empty lists; no category was invented to fill the schema.
- [ ] The consistency flag was evaluated, with `0.y.z` and `0.x → 1.0.0` treated as informational per SemVer §4 and §5.

## Companion tool

`scripts/relnotes.py` (Python 3.9+, stdlib only, offline) makes steps 1, 2 and 5 deterministic: SemVer 2.0.0 precedence and bumps; cue-based tagging (Conventional Commits `!`/`BREAKING CHANGE`, Keep a Changelog headings, CVE/GHSA ids, "will be removed in" horizons); the ReleaseEvent JSON with per-category counts; a semver-consistency flag (breaking entries without a major bump, or a major bump with none); a printed parse-confidence trace.

```
$ python3 scripts/relnotes.py scan --file CHANGELOG.md --from 1.9.3 --report   # abridged
Release: 2.0.0  (prior 1.9.3, bump major, released 2026-03-14, scheme semver)
Entries: 5 — breaking change 2, deprecation 1, new feature 1, bug fix 1  (bug_fixes=7)
  L8    [section:deprecated] search() — use query(); will be removed in 3.0  -> removal: 3.0
Semver consistency: ok — consistent: bump 1.9.3 -> 2.0.0 is major with 2 breaking-change entries
Confidence: 90/100
```

Also `semver parse|compare|bump`, `--demo` (the worked example), `--selftest` (SemVer §11 ordering example, sample changelog); `scan` prints JSON by default; exit 1 = flag at warn. The skill is usable without the tool — the model reads and judges; the tool guarantees consistent semver arithmetic and verbatim, cue-based tags.

## Pair with adjacent skills

- `oss-project-health` — release cadence feeds that vitality verdict; this parses one release.
- `rate-source-admiralty` — grade the changelog's source before trusting the parse.
- `triangulate-sources` — corroborate breaking changes consumers will act on.
- `benchmark-model-claims` — for performance numbers quoted in the notes.
- `detect-ma-event` / `detect-funding-round` — parsers for corporate announcements.

## Anti-patterns

- Do **not** treat every release as high impact — a patch bump with only fixes is routine.
- Do **not** skip the prior-version comparison; "what changed since" is the whole point.
- Do **not** paraphrase a breaking change. The exact symbol name is what consumers match on.
- Do **not** invent missing sections — an absent Deprecated section means `deprecations: []`.
- Do **not** fold CVEs into the bug-fix count; advisories are a separate axis.
- Do **not** trust the number over the text: a "patch" containing a rename is still breaking.

## Reference

- T. Preston-Werner, *Semantic Versioning 2.0.0*, 2013 (CC BY 3.0) — §4 major version zero, §5 the public API, §6–8 patch/minor/major rules, §9–10 pre-release and build metadata, §11 precedence. https://semver.org/spec/v2.0.0.html
- *Conventional Commits 1.0.0*, 2019 (CC BY 3.0) — rules 12, 13 and 16: the `BREAKING CHANGE:` footer, the `!` marker, and their mapping onto SemVer MAJOR. https://www.conventionalcommits.org/en/v1.0.0/
- O. Lacan, *Keep a Changelog* — 1.1.0 released 15 February 2019, 2.0.0 released 7 June 2026; the Added / Changed / Deprecated / Removed / Fixed / Security sections, ISO 8601 dates, `[Unreleased]` and `[YANKED]` are identical in both. https://keepachangelog.com/en/2.0.0/
- CVE Program (MITRE / CISA), CVE identifier format `CVE-YYYY-NNNN+`, https://www.cve.org/
