---
name: triangulate-sources
description: "Establishes one claim by independent corroboration — gathering candidate sources, grading each, collapsing those that share an author, a first-hand root document, a publication event or an incentive structure, and reporting whether at least two genuinely independent sources agree. Use when one source is not enough to rely on a claim — \"corroborate this claim\", \"find independent confirmation\", \"do these sources really agree or are they all quoting the same press release?\", \"triangulate this figure\". Not for grading a single source (use `rate-source-admiralty`) or vetting an unfamiliar site laterally (use `sift-source-check`)."
license: MIT
metadata:
  category: evidence-verification
  method: Source triangulation (data triangulation applied to sourcing)
  origin: Norman K. Denzin, 1978; ICD 206 sourcing standards, 2015
  version: "2.0.0"
---
# Triangulate Sources

Triangulation is Norman Denzin's discipline (*The Research Act*, 2nd ed., 1978) of establishing a finding by approaching it from several directions — his typology distinguishes data, investigator, theory and methodological triangulation. This skill applies the data-triangulation branch to sourcing: a claim counts as established only when two or more **genuinely independent** sources assert it. The core principle is that independence, not count, is what carries the weight — the same discipline the intelligence community codifies in ICD 206 (2015), which strongly encourages a source summary statement covering "what sources are meaningfully corroborative or conflicting" and says a citation "should reference the most original source" rather than a re-report. The four independence tests in step 4 are this skill's own instrument: neither Denzin nor ICD 206 supplies a test list, a collapsing rule or a count threshold. The failure it prevents is manufactured consensus: five articles that all trace to one press release look like five confirmations and are one.

## When to invoke

Invoke when:

- A claim is load-bearing enough that a single source is not sufficient: a headline conclusion, a recommendation, an executive-summary figure, a quantitative claim about a market, a funding amount, or a valuation.
- The question is explicitly about corroboration: "corroborate this claim", "find independent confirmation", "do these sources really agree?", "triangulate this figure".
- Several sources appear to agree and it matters whether they are echoing one another.

Do NOT invoke when:

- The task is grading how trustworthy one source is — use `rate-source-admiralty`; this skill calls that one per candidate.
- The source is unfamiliar and has not been vetted at all — run `sift-source-check` first.
- The claim is peripheral colour or already hedged; corroboration costs lookups, so reserve it for claims a reader would act on.
- No independent source can be found, or the sources conflict irreconcilably — hand the claim to `abstain-or-escalate` rather than forcing a verdict.

## Procedure

### 1 — State the claim in one specific sentence

Write the claim with its subject, value, unit and date: "Company X closed a $3.5 billion Series E at a $61.5 billion post-money valuation in March 2025". A vague claim cannot be corroborated, because different sources will be agreeing about different things. Everything downstream is judged against this sentence.

### 2 — Gather candidate sources

Collect three to five candidates that assert the claim, from as many different kinds of origin as available: primary records (filings, registries, standards, court documents), the party's own announcements, independent reporting, and specialist or academic literature. Record each candidate's originator, date, and the first-hand evidence it points to.

### 3 — Grade each candidate

Grade every candidate with `rate-source-admiralty` — reliability letter, credibility digit, one-sentence rationale. The grade does not decide independence, but it decides which source survives when a cluster is collapsed in the next step, and it keeps an F-graded source from silently counting as corroboration.

### 4 — Apply the four independence tests

Two sources are independent only if **all four** hold. Any failure means they are one source in different clothes. One documented exception: where a source that shares a root nonetheless contributes a separable first-hand element of its own — a named interview, an independent record check, a measurement it made — it may be counted, provided the judgement and what the source added are written into `rationale`. An undocumented exception is a failed test.

| Test | Independent when | Collapses when |
| --- | --- | --- |
| **Different originator** | Different author, newsroom or organisation | One quotes or syndicates the other; both carry the same byline |
| **Different first-hand root** | Each traces to a different underlying document or observation | Both trace to the same filing, release or dataset |
| **Different publication event** | Each adds content or observation of its own | One is a repost, update or aggregation of the other with nothing new |
| **Different incentive structure** | Different funding, ownership or interest in the outcome | Both are paid by, or invested in, the party the claim favours |

Collapse each failing cluster to its single highest-graded member and record what was collapsed — that record is what makes the corroboration auditable.

### 5 — Judge corroboration and emit the verdict

Count the surviving independent sources. Two or more agreeing → **corroborated**. Exactly one → **single-source**: report it as such and route to `abstain-or-escalate` to decide whether to hold or escalate. Zero → `abstain-or-escalate`. Surviving sources that disagree → **contested**: state both positions, say which source is more original and more recent, and do not average them. Never resolve a disagreement by picking the more convenient side.

## Output template

Every field is mandatory; `independent_sources` must equal the number of surviving clusters, and `collapsed` must list every source removed and why.

```json
{
  "claim": "{one specific sentence with value, unit and date}",
  "sources": [
    {"citation": "{originator, title, date, locator}", "grade": "{A1–F6}", "role": "{primary record | party announcement | independent reporting | literature}"}
  ],
  "collapsed": [
    {"citation": "{source removed}", "failed_test": "{originator | first-hand root | publication event | incentive}", "same_as": "{source it collapsed into}"}
  ],
  "independent_sources": {n},
  "verdict": "{corroborated | single-source | contested | uncorroborated}",
  "rationale": "{which sources survived, on what independent roots, and what remains unresolved}"
}
```

## Worked example

Illustrative data. Claim: "Company X closed a $3.5 billion Series E at a $61.5 billion post-money valuation in March 2025." Five candidates were gathered and graded:

| # | Source | Grade | First-hand root | Outcome |
| --- | --- | --- | --- | --- |
| 1 | SEC Form D filing, 4 March 2025 | A1 | The filing itself | survives |
| 2 | Company X blog post, 3 March 2025 | B2 | The same round, announced by the same party | collapsed into 1 (originator and incentive tests) |
| 3 | Reuters report, 3 March 2025 | B2 | Company announcement + a named investor interview | survives on the interview (documented exception) |
| 4 | Tech portal article, 3 March 2025 | C3 | Quotes Reuters verbatim | collapsed into 3 (originator test) |
| 5 | Newsletter, 5 March 2025 | D3 | Links to the company blog, adds nothing | collapsed into 1 (publication event test) |

Two independent sources survive. The filing and the blog post are one source in two clothes — Company X originated both and both serve its interest — so they collapse to the higher grade (A1). Reuters largely repeats the announcement, but its named investor interview is a separable first-hand element from a different originator with a different incentive, so it counts under the documented exception in step 4, with that reasoning written into `rationale`. Sources 4 and 5 add zero corroboration despite adding two URLs. Verdict: **corroborated**, 2 independent sources, best grade A1. Strip the investor interview out of source 3 and everything traces to Company X: 1 surviving source, verdict **single-source**.

## Verification

Before the verdict ships, confirm:

- [ ] Each surviving source was walked to its first-hand root, and the roots named in the output are actually different documents.
- [ ] Every collapsed source appears in `collapsed` with the test it failed and the source it merged into — none was dropped silently.
- [ ] `independent_sources` equals the number of surviving clusters, and a count of 1 is reported as single-source rather than rounded up.
- [ ] No surviving cluster consists only of parties that gain from the claim being true (incentive test applied, not skipped).
- [ ] Where sources disagree, both positions are stated with their grades; no digit or figure was averaged.

## Pair with adjacent skills

- `rate-source-admiralty` — grades each candidate before it counts, and decides which member of a collapsed cluster survives.
- `sift-source-check` — vets an unfamiliar candidate laterally before it joins the pool.
- `grounded-fact-check` — verifies the specific value once corroboration establishes the claim.
- `abstain-or-escalate` — when corroboration fails or the surviving sources conflict.
- Methodology counterpart: [methodologies/research-methods/mixed-methods.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/research-methods/mixed-methods.md) — corroboration across evidence types at study scale.

## Anti-patterns

- Do **not** count syndications of one wire story as several sources.
- Do **not** skip the incentive test. Two favourable analyst notes from firms paid by the same vendor are one source here.
- Do **not** average Admiralty grades across sources. The scale is ordinal: keep the most reliable letter and report the range.
- Do **not** force a verdict when sources genuinely disagree. Surface the disagreement with its sources.
- Do **not** treat volume as independence. Ten agreeing pages that share one root are one confirmation.

## Reference

- N. K. Denzin, *The Research Act: A Theoretical Introduction to Sociological Methods*, 2nd ed. New York: McGraw-Hill, 1978 — the data / investigator / theory / methodological typology; reissued Routledge, 2017, ch. "Strategies of Multiple Triangulation", ISBN 978-1-315-13454-3, doi:10.4324/9781315134543.
- Office of the Director of National Intelligence, *Intelligence Community Directive 206: Sourcing Requirements for Disseminated Analytic Products*, 22 January 2015 — source reference citations, source descriptors, and source summary statements covering "what sources are meaningfully corroborative or conflicting". https://irp.fas.org/dni/icd/icd-206.pdf
