# Indicator thresholds and metric provenance

Default bands used by `oss-project-health` (steps 3–7) and printed by `scripts/osshealth.py`
next to every indicator. CHAOSS publishes metric *definitions*, not thresholds; the bands
below are this skill's documented defaults, chosen so that a stable, feature-complete
library is not read as dead. Change them deliberately and say so in the report.

| Indicator | Green | Amber | Red | Definition / provenance |
| --- | --- | --- | --- | --- |
| Bus factor (Contributor Absence Factor) | ≥ 3 | 2 | 1 | Smallest number of authors whose commits, in descending order, reach ≥ 50 % of all commits in the window; bots (`*[bot]`, dependabot, renovate) excluded — CHAOSS "Contributor Absence Factor" (formerly "Bus Factor") |
| Elephant factor | ≥ 2 | 1 | — | Same computation over organisations, 50 % share — CHAOSS "Elephant Factor" |
| Last commit | ≤ 90 d | 91–180 d | > 180 d (or archived) | Days since last commit; 90-day window follows the OpenSSF Scorecard "Maintained" check — CHAOSS "Activity Dates and Times", "Code Changes Commits" |
| Last release | ≤ 180 d | 181–365 d | > 365 d | Days since last release; count-only data: 0 in window amber, ≥ 1 green — CHAOSS "Release Frequency" |
| Issue first response | median ≤ 2 d | ≤ 14 d | > 14 d | CHAOSS "Time to First Response", "Issue Response Time" |
| PR merge time | median ≤ 7 d | ≤ 30 d | > 30 d | CHAOSS "Change Requests Duration" |
| Issue backlog ratio | < 1 | 1–3 | > 3 | Open issues ÷ issues closed in the window — CHAOSS "Issues New", "Issues Closed" (closure-ratio style) |
| New contributors | ≥ 1 | 0 | — | New authors in the window — CHAOSS "New Contributors", "Contributors" |
| Advisories | 0 open | open, ≤ 90 d | open > 90 d | Open, unpatched security advisories; 90 d = default "normal fix window" — OpenSSF Scorecard "Vulnerabilities" |
| Hygiene | licence OSI-approved and ≤ 1 of {SECURITY.md, CI, CoC} missing | licence not OSI-recognised, or ≥ 2 missing | no licence | CHAOSS "OSI Approved Licenses", "Licenses Declared", "Code of Conduct for a Project"; OpenSSF Scorecard "License", "Security-Policy", "CI-Tests" |
| Adoption (stars, forks, downloads, dependents) | not rated | not rated | not rated | Context only — CHAOSS "Project Popularity", "Technical Fork", "Number of Downloads" |
| Governance and funding | not rated | not rated | not rated | Context only — governance document, CHAOSS "Sponsorship" |

## Verdict rule (step 7)

- **abandoned** — no commits for > 365 days *and* no release for > 365 days (or none in the window) *and* median issue first response > 14 days, all three fields known.
- **at-risk** — any red indicator, or ≥ 3 amber.
- **healthy** — no red and ≤ 2 amber.

Adoption and governance rows are context and never counted. The biggest risk is the first red (then amber) indicator in the order: bus factor, advisories, last commit, last release, issue first response, PR merge, backlog, hygiene, elephant factor, new contributors.

## Confidence (step 8)

High when the five core fields are present — commits by author (bus factor), days since last commit, releases, issue first-response median, open advisories; medium when one is null; low when two or more are null. Name the null fields.

Sources: CHAOSS knowledge base https://chaoss.community/kb-metrics-and-metrics-models/ ; OpenSSF Scorecard checks https://github.com/ossf/scorecard/blob/main/docs/checks.md
