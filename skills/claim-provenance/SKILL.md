---
name: claim-provenance
description: "Tags every fact-claim in a document inline as either `[validated, {source}]` or `[assumption, retire-by {milestone}]`, so a reader can see at a glance which sentences rest on evidence and which rest on reasoning, and what would convert each assumption into knowledge. Use when a brief mixes cited facts with reasoned-from-priors numbers — \"mark which claims are sourced and which are assumptions\", \"tag the provenance of these claims\", \"which numbers here are actually validated?\", \"add validated/assumption tags to this draft\". Not for verifying whether a number is correct (use `grounded-fact-check`) or for corroborating one claim across sources (use `triangulate-sources`)."
license: MIT
metadata:
  category: evidence-verification
  method: Validated-vs-assumption claim tagging (adapted from Discovery-Driven Planning)
  origin: Adapted from Rita Gunther McGrath and Ian C. MacMillan, Discovery-Driven Planning, 1995
  version: "2.0.0"
---
# Claim Provenance

Discovery-Driven Planning — McGrath and MacMillan's method for venture planning (*Harvard Business Review*, July–August 1995) — rests on separating what is known from what is assumed, then listing every assumption with the milestone that will test it. This skill is an adaptation of that discipline from plan level to sentence level: every fact-claim in a document carries an inline bracket, `[validated, <source>]` when a specific source states it or `[assumption, retire-by <milestone>]` when it is reasoned from priors, and every assumption names the event that will convert it into knowledge or kill it. The failure it prevents is the brief in which cited facts and confident guesses read identically, so a decision-maker either over-trusts the guesses or discards the whole document as unreliable.

## When to invoke

Invoke when:

- A brief, report or analysis mixes sourced facts with reasoned estimates and the reader cannot tell which is which: "mark which claims are sourced and which are assumptions", "tag the provenance of these claims", "which numbers here are actually validated?".
- A document carries quantitative claims ("$6.25B market", "24.8% CAGR"), forward-looking projections, categorical assertions ("X is the category leader") or comparative claims that shape a recommendation.
- A decision-maker will act on the document before re-validating it, or the document is timestamped and its current-state claims will decay.

Do NOT invoke when:

- The question is whether a specific value is *correct* rather than how it is grounded — use `grounded-fact-check`.
- A single claim needs independent corroboration — use `triangulate-sources`.
- A claim has no source at all and cannot honestly be hedged — use `abstain-or-escalate`.
- The text is headings, methodology description, transitions or qualitative narrative; tagging those devalues every other tag.

## Procedure

### 1 — Identify the fact-claims

A fact-claim is a sentence whose truth-value changes what the reader does next. Test each: if this sentence were wrong, would the reader's next action change? "The AI-in-HR market reached $6.25B in 2026" passes — wrong by $2B and the investment thesis shifts. "AI is reshaping HR" fails: sharpen it into a checkable claim or leave it untagged. Methodology statements ("twelve vendors were surveyed") describe the work, not the world, and are not tagged.

### 2 — Decide validated versus assumption

A claim is **validated** only when a specific, reasonably authoritative source states *this* claim — not a source from the same category, and not a source that states something adjacent. Analyst reports for market sizing, filings for financials, registries for grants. A claim is an **assumption** when it is reasoned from priors, is a projection without a model behind it, rests on a party's self-report about itself, or cannot be traced to a specific sentence in a specific source. When unsure, tag it an assumption: a false `[validated]` is the failure the method exists to prevent.

### 3 — Write the bracket

Validated form: `<claim>. [validated, <source identifier>; <optional verification action>]`, where the identifier matches the reference list ("MarketsAndMarkets 2026", "[12]", "Form 10-K FY2026 Q3") and the optional action names a cross-check a single-sourced number still deserves. Assumption form: `<claim>. [assumption, retire-by <milestone>]`, where the milestone is a specific event, date or threshold that will convert or kill the assumption. "retire-by next earnings disclosure" is a milestone; "retire-by more research" is not.

### 4 — Place the brackets inline and check coverage

The bracket goes immediately after the sentence's terminating punctuation, inside the paragraph — never in a footnote, because the reader has moved on by then. Then check coverage across the whole document: at least 80 % of quantitative sentences tagged, 100 % of executive-summary and headline fact-claims tagged, and 100 % of forward-looking projections tagged as assumptions with retire-by milestones.

## Output template

The tagged document plus a coverage line. Each bracket is mandatory in one of exactly these two forms; an `[assumption]` without a retire-by milestone is not a valid tag.

```
{claim sentence}. [validated, {source identifier}{; optional verification action}]
{claim sentence}. [assumption, retire-by {specific event, date or threshold}]

Provenance coverage — {document name}, {YYYY-MM-DD}
Quantitative sentences tagged: {n}/{m} ({pct}%) · headline claims tagged: {n}/{m} · projections with retire-by milestones: {n}/{m}
Untagged by design: {headings, methodology, qualitative narrative}
```

## Worked example

Illustrative excerpt from a talent-technology brief, before and after tagging.

Before: "The AI-in-HR market reached $6.25B in 2026 and is growing at 24.8% CAGR. Workday acquired HiredScore for $530M in March 2024. Eightfold holds the largest installed base in skills intelligence, with 1.6B career profiles. Skills graphs will be the dominant talent-mobility primitive by Q2 2027."

After:

```
The AI-in-HR market reached $6.25B in 2026 [validated, MarketsAndMarkets 2026 [12]; cross-check against IDC by Q3].
It is growing at 24.8% CAGR [validated, MarketsAndMarkets 2026 [12]].
Workday acquired HiredScore for $530M in March 2024 [validated, Workday Form 10-Q FY2025 Q1 [7]].
Eightfold holds the largest installed base in skills intelligence, with 1.6B career profiles
  [assumption, retire-by independent third-party installed-base count] — the 1.6B figure is a vendor self-report.
Skills graphs will be the dominant talent-mobility primitive by Q2 2027
  [assumption, retire-by Q4 2026 Workday Skills Cloud installed-base disclosure].

Provenance coverage — Talent-technology brief, 2026-08-16
Quantitative sentences tagged: 5/5 (100%) · headline claims tagged: 2/2 · projections with retire-by milestones: 1/1
Untagged by design: section headings, the methodology paragraph
```

The two tags that matter most are the last two: the 1.6B profile count looks like a fact and carries a vendor citation, but a party's self-report about its own scale is an assumption until someone independent counts; and the 2027 projection has no model behind it, so it earns a dated milestone instead of a citation.

## Verification

Before the tagged document ships, confirm:

- [ ] Every `[validated, …]` tag points at a source that states *this specific* claim — open each one and match the value, not just the topic.
- [ ] Every `[assumption, …]` carries a retire-by milestone that is a specific event, date or threshold; reject "later", "more research", "when more is known".
- [ ] No self-report by an interested party is tagged validated on its own authority.
- [ ] Coverage meets the thresholds: ≥80 % of quantitative sentences, 100 % of headline claims, 100 % of projections.
- [ ] Headings, methodology statements and qualitative narrative are untagged, and the coverage line says so.

## Pair with adjacent skills

- `grounded-fact-check` — verifies that a validated claim's value is actually right; this skill records only how it is grounded.
- `triangulate-sources` — upgrades a single-sourced decision-grade claim before it is tagged validated.
- `cheapest-experiment` — designs the test that retires an assumption by its milestone.
- `red-team-claim` — attacks the `[validated, …]` claims in the executive summary: would a hostile reviewer accept that source for that number?
- `abstain-or-escalate` — for claims with no source and no honest hedge.

## Anti-patterns

- Do **not** tag a party's self-report about itself as validated. Use `[assumption, retire-by independent verification]`.
- Do **not** write `[assumption]` without a retire-by. The milestone is the discipline; without it the tag is decoration.
- Do **not** accept vague milestones. "Retire-by later this year" is the same as untagged.
- Do **not** tag every sentence. Methodology, transitions and framing stay clean, or the tags stop carrying information.
- Do **not** launder a citation: wrapping an interested party's number in `[validated, press release [4]]` changes the formatting, not the conflict.
- Do **not** confuse provenance with confidence. A validated claim can still be uncertain if its sources diverge; the bracket records the type of evidence, not how strongly it backs the claim.

## Reference

- R. G. McGrath and I. C. MacMillan, "Discovery-Driven Planning," *Harvard Business Review*, vol. 73, no. 4, pp. 44–54, July–August 1995 — the assumption-versus-knowledge planning discipline (assumption checklist, milestone planning) this skill adapts to sentence level. https://hbr.org/1995/07/discovery-driven-planning
- R. G. McGrath and I. C. MacMillan, *The Entrepreneurial Mindset*. Boston, MA: Harvard Business School Press, 2000, ch. 8 — the fuller treatment of assumption checklists and milestone-based assumption retirement. ISBN 978-0-87584-834-1.
- R. J. Heuer Jr. and R. H. Pherson, *Structured Analytic Techniques for Intelligence Analysis*, 3rd ed. Thousand Oaks, CA: CQ Press / SAGE, 2019 — the Key Assumptions Check, the analytic tradition of separating evidence from assumption that this sentence-level tagging serves.
