# Patent search sources and CPC/IPC reading aids

Companion reference for `read-patent-landscape`. Nothing here changes the procedure; it
collects the lookup material that would otherwise bloat the skill body.

## Where a cluster comes from (step 1)

| Source | Access | Returns | Notes |
| --- | --- | --- | --- |
| Google Patents | `patents.google.com`, XHR query endpoint | number, title, assignee, dates, total match count | broad coverage; CPC codes are not always returned |
| Espacenet / OPS (EPO) | `worldwide.espacenet.com`, OPS REST API | bibliographic data, INPADOC family, CPC | authoritative family data; API key needed |
| PatentsView (USPTO) | `search.patentsview.org/api` | US grants and pre-grant publications, CPC, assignee | US-only; good for disambiguated assignees |
| Lens.org | `lens.org` | families, CPC, citations, jurisdictions | free tier with attribution |
| WIPO PATENTSCOPE | `patentscope.wipo.int` | PCT applications and national collections | the place to check national-phase entries |
| Patent-specialist press | Lexology, IPWatchdog, Managing IP | filing numbers to seed a search | never a substitute for a search count |

Record which source produced the set, the query string, the date of the pull, the family
reduction rule and the total match count. That trail is what makes the read reproducible;
WIPO's guidelines require the family-reduction choice to be stated (§8.3.2) and applied
consistently across every statistic in the report.

## Family reduction (step 1, anti-pattern 4)

One row per **family**, not per document. A US continuation, an EP divisional and a CN
national-phase entry of the same invention are one family. Common reductions: INPADOC
extended family (broadest; can under-represent US/JP investment), simple family, or
"one document per invention" (ODPI, keeping the primary-jurisdiction member). Say which
one was used.

## Classification levels

A CPC symbol decomposes as section / class / subclass / group / subgroup, e.g.
`H01M 10/0562` → section `H`, class `H01`, subclass `H01M`, main group `H01M 10/00`,
subgroup `H01M 10/0562`. Tally at the level that answers the question: subclass for
"which technology area", full symbol for "which specific mechanism". The companion tool's
`--level subclass|group|full` switches this.

## Subclasses that recur in technology-intelligence clusters

| Symbol | Title (CPC scheme) |
| --- | --- |
| `G06N` | Computing arrangements based on specific computational models (incl. neural networks, `G06N 3/…`; machine learning `G06N 20/00`) |
| `G06F` | Electric digital data processing |
| `G16B` | Bioinformatics — ICT for genetic or protein-related data processing |
| `G16C` | Computational chemistry; chemoinformatics; computational materials science |
| `G16H` | Healthcare informatics — ICT for handling or processing medical or healthcare data |
| `G16Y` | ICT specially adapted for the Internet of Things |
| `G01N` | Investigating or analysing materials by determining their chemical or physical properties |
| `A61K` | Preparations for medical, dental or toiletry purposes |
| `H01M` | Processes or means, e.g. batteries, for the direct conversion of chemical into electrical energy (`H01M 10/052` Li-accumulators; `H01M 10/0562` solid materials; `H01M 4/…` electrodes) |

Titles are abridged from the CPC scheme, https://www.cooperativepatentclassification.org/
(CPC is the joint EPO–USPTO scheme built on the WIPO-administered IPC).

## Concentration bands used in step 2

HHI = sum of squared percentage shares (0–10,000). Two published band sets, printed side
by side by the companion tool because they disagree:

| Band set | Unconcentrated | Moderately concentrated | Highly concentrated |
| --- | --- | --- | --- |
| DOJ/FTC *Horizontal Merger Guidelines* (19 Aug 2010) §5.3 | < 1,500 | 1,500–2,500 | > 2,500 |
| DOJ/FTC *Merger Guidelines* (18 Dec 2023) Guideline 1 / §2.1 | < 1,000 | 1,000–1,800 | > 1,800 |

The 2023 Guidelines state "Markets with an HHI greater than 1,800 are highly concentrated,
and a change of more than 100 points is a significant increase"; the lower bands
(1,000 / 1,800) are the 1982–1997 thresholds the 2023 Guidelines revert to, restated in the
DOJ Antitrust Division's HHI explainer (justice.gov/atr/herfindahl-hirschman-index).
These are merger-review yardsticks borrowed as a descriptive scale for filing shares —
never an antitrust finding about the patent holders.
