---
name: oss-project-health
description: "Reads one open-source repository's maintenance vitality — contributor concentration (the CHAOSS Contributor Absence Factor, i.e. bus factor), commit and release cadence, issue responsiveness, unpatched security advisories — and returns a healthy / at-risk / abandoned verdict naming the single biggest risk. Use when deciding whether to adopt, keep or replace a dependency: \"is X well-maintained?\", \"what is the bus factor of X?\", \"is this project dying?\", \"is this GitHub repo abandoned?\". Not for market hype (use `apply-hype-cycle`) or deployment maturity (use `score-technology-readiness`)."
license: "MIT (skill text); CHAOSS metric names MIT; Ecosyste.ms data CC BY-SA 4.0"
metadata:
  category: technology-assessment
  method: CHAOSS community-health metrics (repository vitality read)
  origin: CHAOSS Project, Linux Foundation, 2017; OpenSSF Scorecard, 2020
  version: "2.0.0"
---
# OSS Project Health

A repository-level vitality read built on the CHAOSS metrics (Community Health Analytics in Open Source Software, a Linux Foundation project started in 2017) and the OpenSSF Scorecard checks (2020). It measures who is still doing the work — contributor concentration, commit and release cadence, time to first response, open advisories — not how popular the project once was: health is current maintenance capacity, not accumulated attention. It prevents adopting a dependency on star count and finding later that one burned-out maintainer or an unpatched advisory sits underneath.

## When to invoke

Invoke when:

- A decision hangs on adopting, keeping or replacing an open-source dependency: "is {owner/repo} well-maintained?", "what is the bus factor of X?", "is this project dying or abandoned?", "is this repository actively developed?".
- A technology assessment names a reference implementation whose maintenance risk belongs beside its maturity.

Do NOT invoke when:

- The question is market narrative ("is X overhyped?") — use `apply-hype-cycle`; hype and health are independent axes.
- The question is deployment maturity ("what TRL is X?") — use `score-technology-readiness`; a TRL-9 project can still be one resignation from unmaintained.
- The input is a single release note — use `analyze-release-notes`; cadence feeds this skill, the release is that skill's job.
- The project has no public repository — use `abstain-or-escalate` rather than force a verdict.

## Procedure

### 1 — Gather the snapshot

Resolve the full `owner/repo` slug (`pgvector/pgvector`, not `pgvector`) and assemble, over a stated window (default 12 months): commits by author and organisation, days since the last commit, releases, median issue first-response and PR merge times, open and closed issues, new contributors, open advisories with age and severity, licence, SECURITY.md, CI, code of conduct, plus context (stars, downloads, dependents). Sources: the GitHub REST API, the Ecosyste.ms repository API, an OpenSSF Scorecard run, web search for abandonment notices. A null field means "data not found", not zero.

### 2 — Adoption (context only)

Read stars and their trajectory and, where available, downloads or dependents. High stars with flat growth means past-peak attention, not ill health; growth does not prove maintenance. Adoption is context and never counted toward the verdict — pair it with cadence first.

### 3 — Bus factor

Compute the CHAOSS Contributor Absence Factor (formerly "Bus Factor"): rank authors by commits in the window, excluding bots, and count how many reach 50 % of all commits. Read 1 as fragile (red), 2 amber, ≥ 3 spread (green), and state the top author's share. Repeat over organisations for the Elephant Factor — one organisation at ≥ 50 % is a dependence worth naming.

### 4 — Cadence

Read days since the last commit and the release rhythm (CHAOSS Release Frequency): last commit ≤ 90 days green (the OpenSSF Scorecard "Maintained" window), 91–180 amber, > 180 red; last release ≤ 180 / 181–365 / > 365 days; archived is red. A long gap beats a low commit count as an abandonment signal — a feature-complete library commits rarely and still lives. Look for the combination: no commits *and* no releases *and* no answers on issues.

### 5 — Responsiveness

Read the median time to first response on issues (CHAOSS Time to First Response; ≤ 2 days green, ≤ 14 amber, > 14 red), median PR merge time (≤ 7 / ≤ 30 / > 30 days) and open issues over issues closed (< 1 / 1–3 / > 3). Unanswered issues plus a stalled cadence reinforce an at-risk read; one statistic does not. Bands with provenance: `references/indicator-thresholds.md`.

### 6 — Risk

Check open security advisories (OpenSSF Scorecard "Vulnerabilities"). Any advisory unpatched beyond a normal fix window — default 90 days — is red on its own, whatever the other indicators say. Hygiene: no licence is red; a non-OSI licence, or two of SECURITY.md, CI and code of conduct missing, is amber.

### 7 — Verdict

Call exactly one label: **abandoned** — no commits for > 365 days *and* no release for > 365 days (or none in the window) *and* median first response > 14 days, all three known; **at-risk** — any red, or ≥ 3 amber; **healthy** — no red and ≤ 2 amber. Adoption and governance rows never count. Name the biggest risk in priority order: bus factor, advisories, commit stall, release stall, responsiveness.

### 8 — Report

Fill the template below. Confidence follows data completeness — high when bus factor, last commit, releases, issue response and advisories are all present; lower, naming the null fields, otherwise. Keep the Ecosyste.ms attribution when a quoted number came from it (a CC BY-SA 4.0 requirement).

## Output template

```
## OSS Project Health — {owner/repo}

**Adoption:** {stars, trajectory}; downloads/dependents: {value or "data not found"}

**Bus factor:** {absence factor} — top author {name} {share}% over {window} ({active}; {all-time}) — {fragile / spread}

**Cadence:** last commit {days} d ago; releases: {count in window, days since last, or "data not found"}

**Advisories:** {open count, oldest age, severity — or "none found"}

**Verdict: {healthy / at-risk / abandoned}** — biggest risk: {one sentence naming the driving indicator}

**Confidence:** {low / medium / high} — {core fields present or null}

**Data:** {sources; "Ecosyste.ms (CC-BY-SA 4.0)" when its numbers are quoted}
```

All fields are mandatory; a null field is written "data not found", never estimated. `scripts/osshealth.py assess --json` returns the same content as JSON.

## Worked example

Illustrative snapshot for `acme-utils/htmltidy` (fictional repository, 12-month window) from `python3 scripts/osshealth.py assess --demo`, abridged from its 12-row scorecard:

| Indicator | Value | Rating |
| --- | --- | --- |
| Bus factor | 1 — top author m.reyes 71.0 % of 200 commits (10 authors; 340 all-time) | red |
| Elephant factor | 1 — Acme Utils 81.5 % of commits (3 organisations) | amber |
| Last commit | 243 d ago; 16.7 commits/month | red |
| Last release | 426 d ago; 0 in 12 months | red |
| Issue first response | median 46 d | red |
| Advisories | 2 open (oldest 190 d), 1 moderate | red |
| Adoption (context) | 28.4k stars, flat (+1 %); downloads −30 % YoY | not rated |

Full counts: 6 red, 2 amber, 2 green. Adoption is strong but stalling, and the bus factor of 1 is decisive on its own, so the report reads **Verdict: at-risk** — biggest risk: single-maintainer dependence — m.reyes authored 71 % of commits in the last 12 months; the project is one resignation from unmaintained. Confidence: high, all five core fields present. Data: Ecosyste.ms (CC-BY-SA 4.0). Not "abandoned": the commit stall is 243 days, below the 365-day bar — at-risk, re-check in six months.

## Verification

- [ ] Bus factor recomputed as the smallest author set holding ≥ 50 % of window commits, bots excluded.
- [ ] Every null field reads "data not found"; nothing was estimated.
- [ ] The verdict follows step 7: any red → at-risk; "abandoned" only when commit, release and issue-response stalls all exceed their bars.
- [ ] The biggest risk names a red or amber indicator; adoption was not counted.
- [ ] The Data line carries "Ecosyste.ms (CC-BY-SA 4.0)" when its numbers are quoted; slug and window are stated.

## Companion tool

`scripts/osshealth.py` (stdlib only, deterministic) computes steps 2–7 and prints the step-8 report. Bus factor = CHAOSS Contributor Absence Factor (smallest author set holding ≥ 50 % of commits); each indicator prints its threshold and CHAOSS metric; verdicts follow step 7 (any red or ≥ 3 amber → at-risk; commit, release and issue-response stall > 365 d → abandoned).

- `assess --file metrics.json [--json]` — scorecard + report (exit 1 if at-risk/abandoned)
- `assess --demo` — the worked example above
- `fetch --github owner/repo --out metrics.json` — only networked command (GitHub REST); add advisories/dependents by hand
- `--selftest` — hand-verified checks

`assess --demo` excerpt:

```
  RED    Bus factor                     1 — top author m.reyes 71.0% of 200 commits over 12 months (10 authors)
         threshold: 1 red | 2 amber | >= 3 green (SKILL.md step 3; cumulative-share threshold 50 %)
Verdict: AT-RISK — biggest risk: single-maintainer dependence — m.reyes authored 71% of commits in the last 12 months; the project is one resignation from unmaintained
```

The skill is fully usable without the tool, which only removes arithmetic.

## Pair with adjacent skills

- `apply-hype-cycle` — orthogonal: hype is market narrative, health is engineering vitality.
- `score-technology-readiness` — orthogonal: TRL is deployment maturity; a TRL-9 project can read at-risk here.
- `analyze-release-notes` — parses the releases step 4 counts.
- `evolution-stage` — a Commodity call over an abandoned reference implementation is a flagged risk.
- `abstain-or-escalate` — for a mostly-null snapshot.

## Anti-patterns

- Do **not** equate stars with health — star count is past attention, not current maintenance.
- Do **not** call a feature-complete project "abandoned" on commit cadence alone; check releases, responsiveness and advisories.
- Do **not** guess at a null metric — write "data not found".
- Do **not** count bot commits (dependabot, renovate) as contributors — they hide the real bus factor.
- Do **not** drop the "Data: Ecosyste.ms (CC-BY-SA 4.0)" line when its numbers are quoted.

## Reference

- CHAOSS Project (Linux Foundation, est. 2017), *CHAOSS Metrics and Metrics Models* knowledge base — "Contributor Absence Factor" (formerly Bus Factor), "Elephant Factor", "Time to First Response", "Release Frequency". https://chaoss.community/kb-metrics-and-metrics-models/
- N. Zahan et al., "OpenSSF Scorecard: On the Path Toward Ecosystem-wide Automated Security Metrics," *IEEE Security & Privacy*, 2023, doi:10.1109/MSEC.2023.3279773; checks: https://github.com/ossf/scorecard/blob/main/docs/checks.md
- Ecosyste.ms repository API, https://repos.ecosyste.ms — data licensed CC BY-SA 4.0, attribution required.
