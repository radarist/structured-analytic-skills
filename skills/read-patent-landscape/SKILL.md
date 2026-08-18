---
name: read-patent-landscape
description: "Reads a cluster of patent families for competitive and white-space signal — assignee concentration (HHI, CR4), filing velocity by priority year, CPC/IPC density and the sparse classes next to the dense ones — and reports who owns the area, whether filing is accelerating and where the gaps sit. Use when the question spans many filings: \"who owns the IP around X?\", \"patent landscape for X\", \"is this space getting crowded?\", \"where is the white space?\". Not for a single named filing — use `analyze-patent-claims` for one patent's claims."
license: MIT
metadata:
  category: technology-assessment
  method: Patent landscape analysis (WIPO PLR methodology)
  origin: A. Trippe / WIPO Publication 946E, 2015
  version: "2.0.0"
---
# Read Patent Landscape

A cluster-level read across many patent families, following the WIPO patent-landscape methodology (A. Trippe, WIPO Publication 946E, 2015): count by family, plot families by year, rank the top applicants, tally the top classifications, read the gaps. Ownership and momentum are properties of a *set* of filings, so the unit of analysis is the deduplicated family and every statistic comes from the same reduced set. It prevents two failures: mistaking one company's continuation chain for a crowded field, and reading the dip in the most recent years (applications publish ~18 months after priority) as a cooling race.

## When to invoke

Invoke when:

- The question is about a technical area rather than a document: "who owns the IP around solid-state batteries?", "patent landscape for {topic}", "is this space getting crowded?", "where is the white space in {area}?".
- A competitive or diligence brief needs an IP-moat read or a multi-year filing trend.

Do NOT invoke when:

- The input is a single named filing — "US00000000", "this patent", freedom-to-operate on one claim set — use `analyze-patent-claims`.
- The cluster holds fewer than about 5 families: too small for concentration or velocity. Say so and use `analyze-patent-claims` per filing.
- The question is about publications and citations rather than patents — use `assess-research-momentum`.
- The item is a financing or acquisition mentioning the technology — use `detect-funding-round` or `detect-ma-event`.
- The set is trademarks or design patents: a different right, a different claim structure.

## Procedure

### 1 — Scope the cluster and reduce to families

Define the cluster one of three ways: a named assignee, a CPC/IPC class, or a topic keyword. Pull the candidate set from a patent search source (Google Patents, Espacenet/OPS, PatentsView, Lens.org, PATENTSCOPE — `references/cpc-and-search-sources.md`), capturing number, assignee, priority year and classification codes plus the total match count, itself a crowding signal. Reduce to one row per **family** (WIPO §8.3.2): a US continuation, an EP divisional and a CN national phase count once. State the rule, query and date, and use the same reduced set everywhere. If the search fails, say so and retry — never fabricate counts.

### 2 — Assignee concentration

Tally families per assignee and compute shares, the top-4 concentration ratio (CR4) and the Herfindahl-Hirschman Index (HHI = sum of squared percentage shares, 0–10,000). Read HHI against both published band sets, which disagree and are quoted together: DOJ/FTC 2010 Horizontal Merger Guidelines §5.3 (< 1,500 unconcentrated, 1,500–2,500 moderate, > 2,500 high) and 2023 Merger Guidelines Guideline 1 (< 1,000, 1,000–1,800, > 1,800 highly concentrated) — merger-review yardsticks used descriptively, never an antitrust finding. Call the area concentrated when the 2023 band reads highly concentrated or one holder holds ≥ 25 %; name the top 3–5 holders and the single-family long tail.

### 3 — Filing velocity by priority year

Bucket families by priority year (WIPO §8.4.1) and report counts per year, year-over-year change, the trailing mean, the peak year and a trend label. Rising counts mean an active race; flat or falling counts mean the wave has passed — or that protection moved to trade secrets. Always attach the publication-lag caveat: applications publish ~18 months after priority (WIPO §8.3.4) and family data lag further, so the last 18–36 months are under-counted.

### 4 — Classification density

Tally families by CPC/IPC at a stated level — subclass for "which technology area", full symbol for "which mechanism" (WIPO §8.4.4). The densest symbols show where crowding sits, often not where the keyword search suggested. Where the source returns no codes, say so and read density from titles and abstracts rather than reporting zeros.

### 5 — White space

Build the classification × assignee matrix (WIPO §6.2–6.3) and read the empty and near-empty cells: symbols next to the dense clusters with little filing, and dense symbols no major holder has entered. A gap is not an opportunity on its own — pair it with a demand signal (a customer pain point, a funding thesis via `detect-funding-round`) first. Empty classes sometimes mean unpatentable, not unclaimed.

### 6 — Report

Fill the output template. State confidence from how the cluster was assembled and how complete classification coverage is, and repeat the reduction rule so the read is reproducible.

## Output template

```
## Patent Landscape — {cluster scope: assignee / CPC class / topic}

**Cluster:** {scope}, {N} families after reduction ({rule}; {source}, {query}, {date})

**Top assignees:** {name: count, …} — HHI {value} ({2023 band} / {2010 band}), CR4 {pct}%, top holder {name} {pct}%

**Filing velocity:** {year: count, …} — {accelerating / flat / declining}; lag under-counts the last 18–36 months

**Dense sub-areas (CPC/IPC, level {subclass|group|full}):** {symbol: count, …}

**White-space:** {symbol with little activity} — demand signal: {present / absent, with source}

**Confidence:** {low / medium / high} — {how the cluster was assembled; classification coverage}
```

Every field is mandatory. A read without the family-reduction rule and the publication-lag caveat is not reproducible and must not ship; counts must come from the reduced set, never from raw document hits.

## Worked example

Illustrative cluster (synthetic data): "solid-state battery manufacturing", 42 families and 18 assignees over priority years 2019–2023, reduced by family. From `python3 scripts/landscape.py report --demo`.

| Read | Value from the tool |
| --- | --- |
| Top assignees | Incumbent A 9 (21.4 %), Incumbent B 7 (16.7 %), Startup C 5 (11.9 %) — top-3 = 21 of 42 |
| HHI | 1,066 — moderately concentrated (2023 bands), unconcentrated (2010 bands) |
| CR4 | 54.8 %; 9 of 18 assignees hold one family |
| Velocity | 3 → 5 → 9 → 14 → 11 per year; CAGR +38.4 %/yr; accelerating; latest year −21.4 % |
| Dense symbols | H01M 10/0562 solid materials 26 (61.9 %); H01M 10/0525 15; H01M 4/13 9; H01M 4/04 4 |

Reading it: no holder reaches 25 % and the HHI sits in the 2023 moderately-concentrated band — an incumbent-led but not closed field, half the assignees holding one family each. Velocity accelerates through 2022 and dips in 2023, but the tool flags 2022–2023 with `*` as inside the publication-lag window, so the dip is not evidence of cooling. The near-empty H01M 4/366 (1 family, Startup L) sits beside the dense electrolyte classes — candidate white space, pending a demand signal. Follow-on: `analyze-patent-claims` on the top holders' broadest claims before betting on the gap.

## Verification

- [ ] Every statistic came from the same family-reduced set; rule, query and pull date are stated.
- [ ] HHI and CR4 recomputed from the shares — `scripts/landscape.py concentrate` agrees — with both band sets quoted by year.
- [ ] The velocity read carries the publication-lag caveat and flags years inside the last 18–36 months.
- [ ] The classification level is named; missing codes are reported as missing, not as zeros.
- [ ] Each white-space claim names the adjacent dense symbol and whether a demand signal exists.
- [ ] Assignee names were checked for duplicate spellings first.

## Companion tool

`scripts/landscape.py` (stdlib only, deterministic) computes steps 2–5 from one row per family (`assignee, priority_year, cpc[;cpc]`; optional `jurisdictions, family_size, citations`; CSV or JSON):

- `concentrate` — shares, HHI with both DOJ/FTC bands (2023: 1,000/1,800; 2010: 1,500/2,500), CR4, single-family long tail
- `velocity` — families per year, YoY, CAGR, rolling mean, peak, recent share, trend; always prints the publication-lag warning (WIPO 2015 §8.3.4)
- `whitespace` — CPC × assignee matrix, empty/low cells, co-occurrence, breadth
- `entry` — entrants (`--recent 3`) and dormant assignees (`--dormant 4`)
- `report` — all, in template order. `--json` on every command; `--demo` reproduces the worked example (HHI 1,066 = "moderately concentrated"); `--selftest` runs 41 hand-verified checks

```
$ python3 scripts/landscape.py concentrate --demo --top 3
Assignee concentration (N = 42 families, 18 assignees)
  HHI: 1,066  (sum of squared % shares; 0-10,000)
    2023 Merger Guidelines, Guideline 1 (<1,000 / 1,000-1,800 / >1,800): moderately concentrated
    2010 Horizontal Merger Guidelines s5.3 (<1,500 / 1,500-2,500 / >2,500): unconcentrated
  CR4 (top-4 share): 54.8%   top holder: Incumbent A 21.4%
```

Usable without the tool; small clusters tally by hand.

## Pair with adjacent skills

- `analyze-patent-claims` — the per-filing claim read this points at.
- `position-competitor` — assignee concentration feeds a competitive map's IP-moat axis.
- `assess-research-momentum` — publication momentum beside filing velocity; they often diverge.
- `triangulate-sources` — corroborate velocity with hiring, funding or product signals.
- `estimate-market-size` / `detect-funding-round` — the demand signal white space needs.

## Anti-patterns

- Do **not** treat filing volume as commercialisation — patents precede, or replace, launch.
- Do **not** read white space as opportunity without a demand signal: an empty class can mean nobody wants it.
- Do **not** count documents where the method counts families; a continuation chain looks like a wave.
- Do **not** read the recent-year dip as a decline — the 18-month publication delay guarantees it.
- Do **not** run this on a single filing or fewer than ~5 families — use `analyze-patent-claims` per filing.

## Reference

- A. Trippe (Patinformatics LLC) and WIPO, 2015, WIPO Publication No. 946E, ISBN 978-92-805-2529-8, doi:10.34667/tind.28858 — *Guidelines for Preparing Patent Landscape
  Reports*: §8.3.2 family reduction, §8.3.4 the 18-month publication delay, §8.4.1 families by year, §8.4.4 top classifications, §8.4.6 top applicants, §6.2–6.3 co-occurrence matrices. https://www.wipo.int/edocs/pubdocs/en/wipo_pub_946.pdf
- U.S. Department of Justice and Federal Trade Commission, *Horizontal Merger Guidelines*, 19 August 2010, §5.3 (HHI bands 1,500 / 2,500). https://www.justice.gov/atr/horizontal-merger-guidelines-08192010
- U.S. Department of Justice and Federal Trade Commission, *Merger Guidelines*, 18 December 2023, Guideline 1 / §2.1 ("Markets with an HHI greater than 1,800 are highly concentrated"); lower bands in the DOJ HHI explainer, https://www.justice.gov/atr/herfindahl-hirschman-index
