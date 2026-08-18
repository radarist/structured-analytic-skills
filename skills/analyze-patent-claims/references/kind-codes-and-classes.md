# Kind codes, jurisdictions and classification symbols

Companion reference for `analyze-patent-claims` (steps 1 and 4).

## Publication levels (WIPO Standard ST.16)

ST.16 assigns letter codes to publication levels within a numbering series: for the primary
patent series, **A** = first publication level, **B** = second publication level, **C** =
third publication level; utility models use U / Y / Z. The digit after the letter
distinguishes documents published at the same level. Offices apply the scheme differently,
so read the code together with the issuing office.

| Prefix | Office | Reading |
| --- | --- | --- |
| `US\d{7,8}` | USPTO | `A1` pre-grant publication of an application, `A9` corrected publication; `B1` grant with no earlier pre-grant publication, `B2` grant that had one; `E` reissue, `H` statutory invention registration, `P` plant patent, `S` design patent |
| `EP\d{7}` | EPO | `A1` application published with the search report, `A2` application published without it, `A3` later search report; `B1` granted specification, `B2` specification amended after opposition |
| `WO\d{4}/\d{6}` | WIPO (PCT) | international application — a filing, never a grant; rights arise only through national/regional phase entry |
| `CN\d{9,}` | CNIPA | `A` published application, `B` granted invention patent, `U`/`Y` utility model |
| `JP\d{7,}` | JPO | `A` published application, `B` granted patent |
| `KR\d{7,}` | KIPO | `A` published application, `B1`/`Y1` granted |

Design patents and trademarks are outside this method: design rights claim ornamental
appearance, not functional limitations, and have a single claim by construction.

## Classification symbols that recur in technology-intelligence work

CPC (the joint EPO–USPTO scheme, built on the WIPO-administered IPC) is finer-grained than
IPC; a filing usually carries several symbols, and the full set — not a cherry-picked one —
describes the domain mix.

| Symbol | Title (abridged from the CPC scheme) |
| --- | --- |
| `G06N` | Computing arrangements based on specific computational models (neural networks `G06N 3/…`, machine learning `G06N 20/00`) |
| `G06F` | Electric digital data processing |
| `G06V` | Image or video recognition or understanding |
| `G10L` | Speech analysis or synthesis; speech or audio coding |
| `G16B` | Bioinformatics |
| `G16C` | Computational chemistry; chemoinformatics; computational materials science |
| `G16H` | Healthcare informatics |
| `G16Y` | ICT for the Internet of Things |
| `G01N` | Investigating or analysing materials by determining their chemical or physical properties |
| `A61K` | Preparations for medical, dental or toiletry purposes |
| `H01M` | Processes or means, e.g. batteries, for the direct conversion of chemical into electrical energy |

Sources: WIPO Standard ST.16 (revision adopted 30 May 1997),
https://www.wipo.int/export/sites/www/standards/en/pdf/03-16-01.pdf ; Cooperative Patent
Classification scheme, https://www.cooperativepatentclassification.org/

## Drafting flags and where they come from

| Flag | Trigger | Authority |
| --- | --- | --- |
| `112F` | "means for" / "step for", or a generic placeholder plus a function | 35 U.S.C. §112(f); MPEP §2181 |
| `REL` | relative terms — "about", "substantially", "approximately" | MPEP §2173.05(b) Relative Terminology |
| `NEG` | negative limitation — "free of", "without" | MPEP §2173.05(i) |
| `MULTI` | multiple dependent claim (alternative reference only, no chaining, extra fee) | 35 U.S.C. §112(e); 37 CFR 1.75(c), 1.16(j); MPEP §608.01(n) |
| forward / dangling reference | dependent claim referring to a later, missing or cancelled claim | 35 U.S.C. §112(d) ("a claim previously set forth"); MPEP §608.01(n) |
| no further limitation | dependent claim that narrows nothing, or duplicates a sibling | 35 U.S.C. §112(d); MPEP §608.01(m), (n) |
