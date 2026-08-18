# ICD 206 source descriptors and source summary statements

Reference detail for `quality-of-information-check`. Read this when building the source
inventory in step 2 or writing the source summary statement in step 6; the procedure in
SKILL.md is self-contained without it.

Source: Office of the Director of National Intelligence, *Intelligence Community Directive
206: Sourcing Requirements for Disseminated Analytic Products*, 22 January 2015.

## Descriptor factors to record per source

The table below is this skill's adaptation, not ICD 206's own list. The directive says descriptor
factors "may include accuracy and completeness, possible denial and deception, age and continued
currency of information, and technical elements of collection as well as source access, validation,
motivation, possible bias, or expertise"; the rows here drop *accuracy and completeness*, *validation*
and *technical elements of collection* as inapplicable to open-source work, and add *primary or
re-report* and *corrections*, which the directive does not name.

| Factor | What to record | Why it matters |
|---|---|---|
| Identity and origin | What the source is, who originated the information, and the document or channel it arrived through | Distinguishes a primary account from a re-report of one |
| Dates | Date the information describes, date it was acquired, date it was published | Stale information about a fast-moving situation supports a weaker judgment than its publication date implies |
| Access | Whether the originator was in a position to know first-hand, and how directly | Second-hand access is the single most common overstated strength |
| Track record and expertise | Prior accuracy; relevant subject-matter expertise | Distinguishes a well-informed voice from a confident one |
| Motivation and bias | Who benefits from the information being believed; commercial, political or reputational incentives | A source with an interest in the conclusion is not disqualified, but the interest must be visible |
| Primary or re-report | The full "according to…" chain traced back to its origin | Collapses apparent corroboration that is really one source echoed |
| Denial and deception potential | Whether the channel could be controlled, uniquely convenient, or unverifiable | Feeds the deception flag in step 5 |
| Corrections | Any recall, retraction or correction issued after publication | A retracted item must not silently continue to support a judgment |

## What the source summary statement must cover

ICD 206 §D.3.d does not require a source summary statement: statements are "strongly encouraged in
covered analytic products", and the directive says one "should cover" the following (§D.3.d(2)). This
skill treats them as mandatory output fields — that is a house rule, stricter than the directive:

1. **Strengths and weaknesses of the source base** as a whole — not source by source.
2. **Which sources are most important** to the key judgments — the items whose failure would
   do most damage.
3. **What is meaningfully corroborative or conflicting**, including reporting that
   contradicts the judgment and how it was treated.
4. **Subject-matter expertise relied on**, where a judgment rests on specialist
   interpretation rather than on the reporting itself.

Write it as prose a reader can audit, not as a citation list: the point is to tell the
reader how much weight the evidence base can carry, and where it would break first.

## Related standards

- ODNI, *Intelligence Community Directive 203: Analytic Standards*, 2 January 2015 (amended
  2022) — the tradecraft standard requiring products to "properly describe the quality and
  credibility of underlying sources, data, and methodologies", to distinguish underlying
  information from assumptions and judgments, and to express uncertainty in calibrated
  language (see the `estimative-language` skill).
- U.S. Government, *A Tradecraft Primer: Structured Analytic Techniques for Improving
  Intelligence Analysis*, March 2009 — "Quality of Information Check", the technique this
  skill operationalises.
