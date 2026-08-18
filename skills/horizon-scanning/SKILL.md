---
name: horizon-scanning
description: "Runs a horizon scan — a systematic early-warning sweep of sources outside an organisation's usual reading for weak signals and emerging issues — and delivers a prioritised horizon-scanning report with impact/likelihood ratings, verified sources and next steps (UK Government Office for Science Futures Toolkit; Amanatidou et al.). Use when asked \"what's on the horizon for {domain} over the next ten years?\", \"what should the strategy team be watching?\", \"scan for weak signals\", \"what could blindside us?\" or \"set up horizon scanning\". Not for a dated prediction on one named trend (use `foresight`) or a rated inventory of macro-environment factors (use `steep-pestle-analysis`)."
license: MIT
metadata:
  category: foresight
  method: Horizon scanning
  origin: F. J. Aguilar (environmental scanning), 1967; H. I. Ansoff (weak signals), 1975; UK Government Office for Science (horizon scanning tool, Futures Toolkit), 2017
  version: "2.0.0"
---
# Horizon Scanning

Horizon scanning is the systematic examination of information to identify emerging trends, weak signals of change, threats and opportunities — including those at the margins of current thinking — early enough to respond (Amanatidou et al., 2012; UK Government Office for Science *Futures Toolkit*, 2017). It descends from Aguilar's environmental scanning (1967) and Ansoff's weak signals (1975): change is cheapest to act on while its evidence is fragmentary, and that evidence is found only by reading outside the sources an organisation already trusts. The discipline is gather first, judge second — log every entry in a common structure, then cluster, rate and verify — so the report shows what the environment is doing, not what leadership already believes; it prevents being blindsided by change that was visible in advance but outside anyone's reading list.

## When to invoke

Invoke when:

- The request is a broad sweep, not a single-topic question: "what's on the horizon for {domain}?", "what should we be watching?", "what could blindside us?"
- A standing early-warning capability is wanted: "set up horizon scanning", "environmental scan of {industry}", "scan for weak signals in {field}".
- A strategy, scenario or risk process needs fresh emerging issues, not re-read known trends.

Do NOT invoke when:

- The question is a dated prediction on one named trend ("when will X happen?") — use `foresight`; scanning finds candidates, not dates.
- A rated inventory of macro-environment factors for one decision is needed — use `steep-pestle-analysis`.
- One trend has a time series and the ask is "is it real, how fast, how far?" — use `trend-analysis`.
- The ask is the consequences of one defined change — use `futures-wheel`.
- The ask is branching 3–10-year futures — use `scenario-planning`.
- Scenarios already exist and the question is which indicators would show which one is unfolding — use `indicators-validation`.

## Procedure

Run on a fixed cadence (weekly gathering, monthly analysis, quarterly report). Steps 1–3 and 6 follow the Futures Toolkit's horizon-scanning tool; step 4 adds Hiltunen's (2008) signal/issue/interpretation split. Detail: `references/sources-and-report.md`.

### 1 — Set the scope and recruit the scanners

State the focal area, time horizon, the questions the scan serves and who will consume the report. Recruit a small group of scanners with deliberately different backgrounds (about ten at most; one person can run a reduced version). Fix the cadence and report date. Output: one-page scanning brief.

### 2 — Identify sources beyond the usual reading

Name sources likely to carry signals of emerging change *outside the organisation's normal parameters*: preprints, patents, regulatory consultations, niche communities, start-up filings, adjacent industries, non-English media, others' published scans. Track coverage across STEEP/PESTLE categories so technology does not crowd out the rest, and set a quota for fringe sources. Output: source list with category coverage.

### 3 — Gather scan entries in a common structure

Each scanner produces short entries (about a paragraph, roughly one a week) recording: what was observed, the original source link and date, how it relates to the focal area, why it may matter, a STEEP/PESTLE category, and an initial view of timescale and importance. Silence from a source is a valid result — never manufacture entries. Output: scan log.

### 4 — Analyse the log into emerging issues

On cadence, deduplicate, drop restatements of known trends and marketing without new facts, and cluster the survivors. Keep three things distinct (Hiltunen, 2008): the observation (weak signal), the emerging issue the cluster may point to, and the interpretation for the organisation. Open an issue on two or more independent sources, or one extraordinary observation. Type each issue (established trend, expected development, newly emerging issue, new risk or opportunity, possible future event), rate impact and likelihood (1–5 each) with a one-line rationale, and place it on the impact/likelihood matrix. Output: rated issue list.

### 5 — Verify before anything is reported

Confirm every entry against its original source (the source itself, not an interpretation of it), check that clustered sources are genuinely independent (two reports of one primary source count once), and run the boring-explanation test — "is this a known trend rebranded?". Give each issue a verdict: escalate, monitor or drop; zero drops means the filter is not working. Output: verified issues and drop list.

### 6 — Write up and route

Produce the horizon-scanning report: the four to eight issues most warranting action, each with evidence, ratings, newness to the organisation, two readings, signposts and a recommended action. Route escalations to the process that can act on them — `foresight` for a dated prediction, `scenario-planning` for driving forces — then refine the next cycle's scope and retire dead issues. Output: the report and next-cycle brief.

## Output template

```
## Horizon-scanning report — {organisation / focal area} — {YYYY-MM-DD}

Scope: {focal area, horizon, cadence}   Sources: {n} across {STEEP categories}
Entries: {n}   Issues open: {n}   Dropped: {n} — {reasons}

### Issue: {short name}
Type: {established trend | expected development | emerging issue | risk/opportunity | possible event}
Status: {new | strengthening | stable | fading | retired}   Newness: {well understood | partly | novel}
Evidence (independent sources, verified at origin):
- {observation} — {source, date} — why it may matter: {one line}
- {observation} — {source, date} — why it may matter: {one line}
Impact: {1-5}   Likelihood: {1-5}   Timescale: {years}   Rationale: {one line}
Readings: (a) {interpretation}; (b) {divergent reading}
Signposts: {observable development} → {where it would surface}
Recommended action: {escalate to … | monitor | drop}   Next review: {YYYY-MM-DD}
```

Mandatory fields: scope, per-issue evidence with sources, impact, likelihood, rationale, recommended action and next review; an issue with a single source or no rationale may not appear.

## Worked example

Focal area: in-store technology for a mid-size grocery retailer; monthly cycle, June 2026. Illustrative entries from public announcements — dates and counts approximate.

| Field | Content |
|---|---|
| Issue | Robotic shelf-scanning moves from pilots to chain-wide deployment |
| Type / status | Expected development / strengthening; newness: partly understood |
| Evidence 1 | Schnuck Markets extends Simbe Robotics' Tally shelf-scanning robot to 100+ stores — trade press, 2020–21 — why it matters: unit economics work below top-3 scale |
| Evidence 2 | BJ's Wholesale Club announces Tally across all ~230 clubs after a pilot — company announcement, 2022 — why it matters: a second, independent chain-wide commitment |
| Evidence 3 | Ahold Delhaize deploys ~500 Badger Technologies "Marty" robots across Giant, Martin's and Stop & Shop — company announcement, 2019 — why it matters: shoppers and unions tolerate robots in aisles |
| Impact / likelihood | 4 / 4 — costs are public, three chains have committed; timescale 2–4 years |
| Readings | (a) labour play: shelf-audit hours shift to exception handling; (b) data play: shelf imagery becomes a planogram-compliance product |
| Signposts | a top-10 US grocer announcing chain-wide deployment (trade press); per-store subscription pricing published; union or OSHA filings on robot–worker interaction |
| Action | Escalate to `foresight` — "robotic shelf-scanning in ≥30 % of the estate by 2028"; next review 2026-09-30 |

Dropped: "drone delivery to suburban homes" — one entry, a vendor's repost of a 2023 pilot; "ghost kitchens for private-label grocery" — a known trend rebranded.

## Verification

- [ ] Every entry in the report was checked against its original source and the claim matches it.
- [ ] Every open issue rests on two or more independent sources (or one flagged extraordinary); reports of one primary source were merged.
- [ ] Impact and likelihood each carry a rationale, and the ratings are not a uniform wall of 4s and 5s.
- [ ] Coverage was checked across all STEEP/PESTLE categories and the fringe-source quota was met, or the gap is stated.
- [ ] The drop list is non-empty with reasons, and each escalated issue names its downstream process and next-review date.

## Pair with adjacent skills

- `foresight` — where a strengthening issue goes for a dated, falsifiable prediction.
- `steep-pestle-analysis` — turns scan entries into a rated factor inventory.
- `trend-analysis` — validates and projects an issue once it has a time series.
- `futures-wheel` — maps the consequences of one surfaced issue.
- `scenario-planning` — takes escalated issues as driving forces for branching futures.
- `indicators-validation` — turns an issue's signposts into a validated, diagnostic indicator set once scenarios exist.
- Methodology counterpart: [methodologies/foresight/horizon-scanning.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/horizon-scanning.md).

## Anti-patterns

- Do **not** scan for confirmation; if every entry supports what leadership already believes, widen the sources.
- Do **not** skip the "why it may matter" line; an entry without a hypothesis is archiving.
- Do **not** report the interpretation as the observation; keep signal, issue and interpretation separate.
- Do **not** confuse scanning with forecasting: the report says *watch this*, not *this will happen*.

## Reference

- E. Amanatidou, M. Butter, V. Carabias, T. Könnölä, M. Leis, O. Saritas, P. Schaper-Rinkel and V. van Rij, "On concepts and methods in horizon scanning: Lessons from initiating policy dialogues on emerging issues," *Science and Public Policy*, vol. 39, no. 2, pp. 208–221, 2012. https://doi.org/10.1093/scipol/scs017
- UK Government Office for Science, *The Futures Toolkit: Tools for Futures Thinking and Foresight Across UK Government*, edition 1.0, 2017 (2024 edition current), "Horizon Scanning" tool. https://www.gov.uk/government/publications/futures-toolkit-for-policy-makers-and-analysts
- H. I. Ansoff, "Managing Strategic Surprise by Response to Weak Signals," *California Management Review*, vol. 18, no. 2, pp. 21–33, 1975. https://doi.org/10.2307/41164635
- E. Hiltunen, "The future sign and its three dimensions," *Futures*, vol. 40, no. 3, pp. 247–260, 2008. https://doi.org/10.1016/j.futures.2007.08.021
- F. J. Aguilar, *Scanning the Business Environment*. New York: Macmillan, 1967.
