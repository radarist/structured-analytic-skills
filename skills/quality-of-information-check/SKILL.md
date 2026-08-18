---
name: quality-of-information-check
description: "Audits the whole evidence base behind an assessment's key judgments — the Quality of Information Check from the CIA Tradecraft Primer (2009), operationalising ICD 206. Maps sources to judgments, exposes single-source, thin and re-reported findings, and writes a source summary statement that tempers confidence per judgment. Use before an assessment ships — \"audit the sourcing behind these key judgments\", \"quality of information check\", \"which conclusions rest on a single source?\". Not for grading one source (`rate-source-admiralty`) or corroborating one claim (`triangulate-sources`)."
license: MIT
metadata:
  category: evidence-verification
  method: Quality of Information Check
  origin: U.S. Government / CIA Sherman Kent School, A Tradecraft Primer, 2009; ODNI ICD 206 sourcing requirements, 2015
  version: "1.0.0"
---
# Quality of Information Check

The Quality of Information Check is the *Tradecraft Primer* (2009, pp. 10–11) diagnostic technique that "evaluates completeness and soundness of available information sources" behind an analytic line. Its principle: confidence in a judgment "should ultimately rest on how accurate and reliable the information base is", and "having multiple sources on an issue is not a substitute for having good information that has been thoroughly examined". It prevents "over-reliance on a single, ambiguous source" — the WMD Commission's finding quoted by the Primer — and judgments anchored to weak reporting whose caveats are forgotten. ODNI ICD 206 (2015) standardised the output as per-source **source descriptors** and a product-level **source summary statement**; ICD 203 (2015) makes describing source quality and credibility the first analytic tradecraft standard. This skill audits an entire evidence base; siblings grade one source or corroborate one claim.

## When to invoke

Invoke when:

- An assessment, brief or report with key judgments is about to ship: "audit the sourcing behind these key judgments", "run a quality of information check on the evidence base", "which conclusions rest on a single source or on re-reported information?".
- Confidence levels are being assigned and must be traceable to the source base — "what we know / what we do not know".
- A standing analytic line is under periodic review, or a source has been recalled or discredited.

Do NOT invoke when:

- One source needs a trust grade — use `rate-source-admiralty`; this skill consumes those grades.
- One claim needs corroboration across independent sources — use `triangulate-sources`.
- One unfamiliar website or author needs a lateral check — use `sift-source-check`.
- The doubt is about hidden premises rather than sources — use `key-assumptions-check`.

## Procedure

### 1 — Fix the judgments under audit

List the key judgments exactly as the product states them (J1…Jn), each with its stated likelihood and confidence. If the product has no explicit judgments, extract the sentences a reader would act on. The check audits sourcing *for judgments*; citations that support no judgment are noise here.

### 2 — Inventory every source with a source descriptor

For every source a judgment relies on, record the ICD 206 descriptor factors — origin, dates, access, track record, motivation, primary-or-re-report, deception potential, corrections — set out with their rationale in [references/icd-206-descriptors.md](references/icd-206-descriptors.md). Grade each with `rate-source-admiralty`, after `sift-source-check` on anything not previously vetted, and confirm each is cited accurately.

### 3 — Build the source-to-judgment matrix

Rows are sources, columns judgments. Mark **S** (supports), **C** (contradicts), **–** (silent). Collapse re-reporting chains: items tracing to the same origin, author, document or incentive structure (the four independence tests of `triangulate-sources`) count once. Count *independent* supports per judgment on the collapsed set and name the most compelling source for each — the item whose failure would hurt most.

### 4 — Flag single-source, thin and conflicting judgments

Assign a status per judgment from this skill's own five-status taxonomy — neither the Primer nor ICD 206 defines these labels or their thresholds: **corroborated** (≥ 2 independent supports, one graded C3 or better, no unaddressed contradiction); **thin** (2 supports but one anonymous, modeled, second-hand, or graded D–F / 4–6); **single-source** (1); **conflicting** (a C the product does not address); **unsupported** (0). Reexamine previously dismissed reporting in light of newer facts, and check that ambiguous information was caveated rather than silently resolved.

### 5 — Look for gaps and for deception or denial

Per judgment ask: if this were true, what would a well-placed source have reported — and is it absent? Missing expected reporting is a collection gap or a sign of denial; either way it belongs in the output. Flag deception patterns — a single channel that is uniquely convenient, unverifiable, too consistent, or reports what the analyst hoped to see. Do not adjudicate deception here; route it to `analysis-of-competing-hypotheses` with an explicit deception hypothesis, as the Primer recommends.

### 6 — Write the source summary statement and temper confidence

Write the ICD 206 §D.3.d statement — strengths and weaknesses of the source base, the sources most important to the key judgments, what is meaningfully corroborative or conflicting, and any subject-matter expertise relied on (the four required elements are set out in [references/icd-206-descriptors.md](references/icd-206-descriptors.md)). Then, per judgment, state whether the stated confidence is warranted or must be lowered, and why. Hand the revised wording to `estimative-language`.

## Output template

```
## Quality of Information Check — {product title, date}

**Judgments audited:** J1 {judgment} ({stated likelihood / confidence}); J2 {…}

**Source inventory**
| ID | Source (originator, title, date) | Access / motive | Primary or re-report of | Grade |
|----|----------------------------------|-----------------|-------------------------|-------|
| S1 | {…} | {first-hand | second-hand}; {bias} | {primary | re-report of S_n} | {A1–F6} |

**Source-to-judgment matrix** (S supports · C contradicts · – silent · (S_n) collapsed into S_n)
| Judgment | S1 | S2 | … | Independent | Most compelling | Status |
|----------|----|----|---|-------------|-----------------|--------|
| J1 | S | (S1) | … | {n} | {S_n} | {corroborated | thin | single-source | conflicting | unsupported} |

**Gaps:** {per judgment — what a well-placed source should have reported but did not}
**Deception / denial flags:** {source or pattern → further review | none found}
**Recalled or previously dismissed reporting:** {items and the judgments they touch}
**Source summary statement:** {strengths and weaknesses; sources most important to key judgments; corroborative vs conflicting; expertise relied on}
**Confidence per judgment:** J1 {stated} → {warranted | lower to …} — {reason}; J2 …
```

The inventory, the matrix, the source summary statement and one confidence line per judgment are mandatory; gaps must be stated per judgment, never as "none identified".

## Worked example

Product: *"Acme Robotics will ship its humanoid platform to paying customers by Q2 2027"* (draft of 3 Mar 2026). Judgments: **J1** low-rate production has begun (stated: high confidence); **J2** at least three signed pilot customers (moderate); **J3** unit cost below $60,000 (moderate). Seven sources were cited.

```
Source inventory
S1  Acme press release, 14 Jan 2026 — first-hand; promotional — primary — B3
S2  Reuters, 15 Jan 2026 — second-hand; adds anonymous "person familiar" on cost — re-report of S1 for J1/J2; anonymous origin for J3 — B2 / F3
S3  RoboTrade Weekly, 20 Jan 2026 — second-hand — re-report of S2 — C3
S4  Alameda County building permit, 3 Nov 2025 — first-hand (capacity, not output) — primary — A2
S5  Two Acme line engineers, LinkedIn, 9 and 11 Feb 2026 — first-hand; employee pride — primary — D2
S6  NorthHaul Logistics COO, podcast, 2 Feb 2026 — first-hand for one pilot; customer — primary — B2
S7  Harbor Street Research broker note, 22 Jan 2026 — modeled from a prototype teardown; paid coverage — primary (model) — C3

Source-to-judgment matrix (re-reports collapsed)
                        S1   S2       S3     S4   S5   S6        S7        indep.  most compelling  status
J1 production begun     S    (S1)     (S1)   S    S    –         –         3       S5               corroborated — S4 shows capacity only
J2 three signed pilots  S    (S1)     (S1)   –    –    S (1/3)   –         2       S6               thin — one customer confirmed
J3 unit cost < $60k     –    S anon.  (S2)   –    –    –         S model   2       S7               thin — no primary cost data
```

**Gaps:** J1 — no shipping manifest, customer receipt or third-party sighting of a finished unit; J2 — two of three pilots have said nothing publicly, no contract evidence; J3 — no bill of materials, price list or customer quote. **Deception / denial:** none indicated; four of seven items trace to Acme's own announcement — a structural incentive to overstate, not deception. **Recalled reporting:** none.

**Source summary statement:** The source base is moderate overall and heavily weighted toward Acme's 14 January announcement, which S2 and S3 merely repeat. Production start (J1) is corroborated by two first-hand employee posts and a county permit that establishes capacity, not output. The three-customer claim (J2) has one independent confirmation covering one customer. The cost judgment (J3) rests on an anonymous "person familiar" relayed by Reuters and a broker's modeled estimate; no primary cost data exist. Expertise relied on: manufacturing ramp benchmarks.

**Confidence per judgment:** J1 high → moderate (independent evidence is D-grade posts plus an indirect permit); J2 moderate → low-to-moderate (one of three pilots confirmed); J3 moderate → low (anonymous plus modeled).

## Verification

Before the check ships, confirm:

- [ ] Every source a key judgment relies on is in the inventory with originator, date, access, motive and grade.
- [ ] Every "according to…" chain is traced; re-reports are collapsed and the independent-support count is recomputed on the collapsed set.
- [ ] Every judgment carries a status; every single-source, thin, conflicting or unsupported judgment has a confidence line that lowers the stated level or explicitly justifies keeping it.
- [ ] Gaps are stated per judgment as missing *expected* reporting, not as "no gaps identified".
- [ ] Recalled, corrected or previously dismissed reporting is flagged and its judgments re-checked.
- [ ] The source summary statement covers all four elements ICD 206 §D.3.d(2) says one should cover: strengths and weaknesses, most important sources, corroborative versus conflicting, expertise used.
- [ ] Grades reflect track record and access, not agreement with the judgment — cross-check against the two axes in `rate-source-admiralty`.

## Pair with adjacent skills

- `rate-source-admiralty` — grades each inventoried source (step 2); this check aggregates the grades across the base.
- `triangulate-sources` — its four independence tests collapse re-reporting chains (step 3); run it on any single-source judgment that must become corroborated.
- `sift-source-check` — lateral vetting of unfamiliar sources found during the inventory, before grading.
- `key-assumptions-check` — the sibling audit: this skill audits sources, that one audits premises; ICD 203 asks for both.
- `claim-provenance` — bracket individual fact-claims in the product once the base has been audited.
- `analysis-of-competing-hypotheses` — the further review for deception flags, with deception as an explicit hypothesis.
- `estimative-language` — express the tempered likelihood and confidence in standard terms.
- Methodology counterpart: [methodologies/scientific-methods/evidence-appraisal.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/scientific-methods/evidence-appraisal.md) — appraisal of a body of evidence at study scale.

## Anti-patterns

- Do **not** count re-reports as independent corroboration. Three outlets repeating one press release are one source — many sources are no substitute for good ones.
- Do **not** grade a source by whether it agrees with the judgment. Reliability comes from access and track record; a contradicting source still enters the matrix as a C.
- Do **not** let one anonymous or unverifiable source carry the headline judgment. Mark it single-source and lower the confidence, however compelling it reads.
- Do **not** stay silent about gaps. "What we do not know" is half of the check's value; a statement without gaps skipped step 5.
- Do **not** treat "official" as "reliable". Company statements, government releases and broker notes are primary but interested; record the motive.
- Do **not** run the check once and forget it. Caveats decay; re-run when reporting is recalled or a standing line is reviewed.

## Reference

- U.S. Government, *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis*. Washington, DC: Central Intelligence Agency (Sherman Kent School), 2009, pp. 10–11 "Quality of Information Check". https://www.cia.gov/resources/csi/static/Tradecraft-Primer-apr09.pdf
- Office of the Director of National Intelligence, *Intelligence Community Directive 206: Sourcing Requirements for Disseminated Analytic Products*, signed 22 January 2015 (technical amendments through 18 December 2025), §D.3 and glossary. https://archive.dni.gov/files/documents/ICD/ICD-206.pdf
- Office of the Director of National Intelligence, *Intelligence Community Directive 203: Analytic Standards*, signed 2 January 2015 (technical amendments 2022, 2023), §D.6.e(1). https://archive.dni.gov/files/documents/ICD/ICD-203.pdf
- R. J. Heuer Jr. and R. H. Pherson, *Structured Analytic Techniques for Intelligence Analysis*, 3rd ed. Thousand Oaks, CA: CQ Press / SAGE, 2019 (2nd ed. 2014), ch. 7 "Diagnostic Techniques" — the follow-on techniques (7.1 Key Assumptions Check, 7.6 ACH, 7.8 Deception Detection); the check itself is a Primer technique, not a numbered section of the book.
