# Category cues and versioning rules

Companion reference for `analyze-release-notes` (steps 2 and 3). The categories are fixed;
only the cue lists grow. `scripts/relnotes.py` implements exactly this table.

## Categories, in classification order

| Category | Explicit markers | Section headings | Phrase cues |
| --- | --- | --- | --- |
| breaking change | `type!:` prefix, uppercase `BREAKING CHANGE:` / `BREAKING-CHANGE:` footer (Conventional Commits rules 12, 13, 16) | Breaking, Breaking changes, ⚠ BREAKING | "backwards-incompatible", "renamed", "dropped support", "migration guide", "now requires", "no longer" (unless a bug-fix cue is present) |
| deprecation | — | Deprecated (Keep a Changelog) | "deprecated", "will be removed in {version}", "sunset", "scheduled for removal" |
| removal | — | Removed (Keep a Changelog) | "removed", "dropped support", entry begins "remove"/"drop" |
| new feature | `feat:` | Added, Features, What's New | "adds", "introduces", "new" |
| enhancement | `refactor:`, `style:` | Changed, Improvements | "improved", "better", "now also" |
| bug fix | `fix:` | Fixed, Bug fixes | "fixes", "resolves", "corrects" |
| security fix | CVE id `CVE-YYYY-NNNN+`, GitHub advisory `GHSA-xxxx-xxxx-xxxx` | Security | "vulnerability", "advisory", "XSS", "RCE", "privilege escalation" |
| performance | `perf:` | Performance | "faster", "reduces latency", "lower memory" |
| docs | `docs:` | Documentation | "docs", "README", "typo in the guide" |
| dependency bump | `build(deps):`, `chore(deps):` | Dependencies | "bump", "upgrade {package} to" |
| other | — | — | anything unmatched |

Precedence: explicit marker > final section heading or Conventional Commits type >
non-final label (Added / Changed) that a high-priority phrase may override > phrase cues in
the order above. Removal entries map into `breaking_changes[]`, because removing public
functionality is backwards-incompatible under SemVer §8.

## Version schemes

- **SemVer 2.0.0** `MAJOR.MINOR.PATCH[-prerelease][+build]`. MAJOR for backwards-incompatible
  changes (§8), MINOR for backwards-compatible functionality or a deprecation marked in place
  (§7), PATCH for backwards-compatible bug fixes (§6). `0.y.z` is initial development where
  anything may change (§4); `1.0.0` defines the public API (§5). Build metadata is ignored for
  precedence (§10); pre-release versions sort below the associated normal version (§11).
- **CalVer** `YYYY.MM.DD`, `YY.MM`, `YYYY.MINOR` — no compatibility promise is encoded in the
  number, so `semver_bump` is `"calver"` and no bump comparison is made.
- **Rolling / date-tagged builds** (`nightly-2026-03-14`): treat as calver, and note that
  breaking changes may appear in any build.

## Heading and date conventions (Keep a Changelog 1.1.0)

`## [2.0.0] - 2026-03-14`, `## [Unreleased]`, `## [0.0.5] - 2014-12-13 [YANKED]`; ISO 8601
dates (`YYYY-MM-DD`). Section names: Added, Changed, Deprecated, Removed, Fixed, Security.
A yanked release is recorded as yanked and never treated as the current version.

Sources: Semantic Versioning 2.0.0 (T. Preston-Werner, 2013), https://semver.org/spec/v2.0.0.html ;
Conventional Commits 1.0.0 (2019), https://www.conventionalcommits.org/en/v1.0.0/ ;
Keep a Changelog 1.1.0 (O. Lacan, 2019), https://keepachangelog.com/en/1.1.0/ ;
CVE Program, https://www.cve.org/
