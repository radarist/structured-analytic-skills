---
name: critique-report
description: "Runs a structured self-critique of a finished draft before it is published — ten review points (does it answer the question, is the evidence sourced, is confidence honest, are limitations and counter-evidence stated, are the numbers defensible, is the next action actionable) plus three conditional ones — and returns a pass/fix/block verdict with located, specific fixes. Use when a draft is done but unsent: \"review this brief before it goes out\", \"critique my report\", \"is this ready to publish?\", \"what would a reviewer catch?\". Not for attacking one headline claim adversarially (use `red-team-claim`) or for checking reference identifiers (use `verify-citations`)."
license: MIT
metadata:
  category: evidence-verification
  method: Structured self-critique of a draft document
  origin: This skill's own thirteen-point checklist; influenced by Structured Self-Critique — R. J. Heuer Jr. & R. H. Pherson, Structured Analytic Techniques, 2015/2019
  version: "2.0.0"
---
# Critique a Report

A pre-publication gate that catches what a reviewer would catch, before the reviewer sees it. Its influence is Structured Self-Critique, the technique developed by Heuer and Pherson (*Structured Analytic Techniques*, 2nd ed. 2015, ch. 9 "Challenge Analysis"; 3rd ed. 2019, ch. 8 "Reframing Techniques", §8.2.3): rather than waiting for an outside critic, a team turns on its own product and answers a fixed list of eleven topics — analytic process, key assumptions, sources of uncertainty, information gaps, missing and anomalous evidence, deception, and the rest — then reassesses its confidence. The thirteen points below are **not** that list. They are this skill's own document-QA checklist, written for a finished draft rather than for a team's analytic line; roughly three of them (evidence sourced, confidence honest, counter-evidence addressed) overlap Heuer and Pherson's topics, and points 11–13 simply route to sibling skills. What carries over is the principle: the questions are fixed in advance, so a self-review cannot quietly skip the uncomfortable ones. The failure it prevents is the fluent, well-formatted document that answers a slightly different question, sources nothing load-bearing, and states no limitation.

## When to invoke

Invoke when:

- A structured document of roughly 400 words or more is drafted and about to reach its reader: "critique my report", "review this brief before it goes out", "is this ready to publish?".
- A producing skill has finished — `write-imrad-report`, `write-sbar-brief`, `systematic-review` — and its output has not yet been reviewed.
- A document will carry recommendations someone acts on, and no second reader is available.

Do NOT invoke when:

- One headline claim needs adversarial attack rather than a whole-document audit — use `red-team-claim`.
- Only the reference list needs checking — use `verify-citations` for identifier validity, `grounded-fact-check` for the specifics themselves.
- The output is a short chat reply or intermediate working note; only the reader-facing deliverable is gated.
- The document has already been reviewed and revised once with no structural change since. One critique, one revision, one confirmation — a third round means the problem is structural and needs a human.

## Procedure

### 1 — Take the whole draft and name its type

Review the complete document, never a fragment: points 1, 7, and 10 are unanswerable from an excerpt. Record the document type (IMRAD report, SBAR brief, systematic review, market or technology brief) and the intended reader, because the anti-patterns in point 3 and the calibration in point 7 are both type-specific.

### 2 — Walk the ten base points

Assign ✅ pass, ⚠️ fix, or 🔴 block to each, with a one-sentence rationale citing the section it applies to. The full pass/fix/block criteria for every point are in [references/checklists.md](references/checklists.md); the summary is:

| # | Point | The question it asks |
| --- | --- | --- |
| 1 | Answers the question | Does it answer the question asked, or an adjacent one? |
| 2 | Evidence sourced | Does every load-bearing claim carry a citation that resolves? |
| 3 | Anti-patterns avoided | Are the format's characteristic failures absent? |
| 4 | Reproducible | Could another analyst re-derive this from the same sources? |
| 5 | Confidence honest | Does stated confidence match the evidence grade? |
| 6 | Limitations stated | What was not covered, and which assumptions are load-bearing? |
| 7 | Audience calibrated | Do jargon, length, and authority level fit the reader? |
| 8 | Counter-evidence addressed | Is the strongest disconfirming evidence named and engaged? |
| 9 | Numbers defensible | Units, date, baseline, method — and do computed figures reproduce? |
| 10 | Next action actionable | Specific, owned, dated? |

### 3 — Apply the conditional points only where they fire

Points 11–13 cover job-to-be-done framing, evolution-stage placement, and horizon tagging. Each fires only on a specific document shape — three or more named technologies, a maturity claim, three or more bets across horizons — and is otherwise recorded as `N/A — {reason}`. The conditions and criteria are in [references/checklists.md](references/checklists.md). Forcing them onto a document that does not need them is itself a review failure.

### 4 — Compute the verdict

All ✅ is **approve**. Any ⚠️ with no 🔴 is **revise**: fix, then ship without a second full critique. Any 🔴 is **block**: rewrite the affected section, then re-review those points. The verdict follows mechanically from the table — a reviewer who feels good about a document with two 🔴s has reviewed their feelings.

### 5 — Specify every fix by location

A critique without actionable fixes is complaint. For each ⚠️ and 🔴 name three things: what specifically to change, where (section and paragraph, or line range), and what "fixed" looks like — the state in which that point would pass. Then state whether a re-review is needed: yes for any 🔴, no for ⚠️ alone.

## Output template

```
## Critique — {document title}

**Type:** {IMRAD | SBAR brief | systematic review | market brief | other}   **Reader:** {…}

| # | Point | Status | Rationale |
|---|---|---|---|
| 1 | Answers the question | {✅/⚠️/🔴} | {one sentence, with the section} |
| … | … | … | … |
| 10 | Next action actionable | {✅/⚠️/🔴} | {…} |
| 11–13 | Conditional points | {✅/⚠️/🔴/N/A} | {N/A — reason, or the finding} |

**Verdict: {APPROVE | REVISE | BLOCK}**

**Fixes required:**
1. [{location}] {specific change} → passes when {condition}
2. [{location}] {specific change} → passes when {condition}

**Re-review after fixes:** {yes — 🔴 present | no — ⚠️ only}
```

Mandatory: a status and rationale for all ten base points (conditional points may be `N/A` with a reason), the verdict, and a located fix for every non-pass. A review that reports "looks good" without the table is not a critique.

## Worked example

Draft under review (illustrative) — the executive summary of a skills-technology market brief:

> "The HR-tech skills market is at an inflection point. Eightfold is the clear leader with the largest installed base, and the market is growing 60 % year on year. We recommend prioritising a partnership with Eightfold. Competitors are falling behind."

| # | Point | Status | Rationale |
| --- | --- | --- | --- |
| 1 | Answers the question | ✅ | The recommendation matches the question asked ("who should we partner with?") |
| 2 | Evidence sourced | 🔴 | "largest installed base" and "60 % YoY" carry no citation |
| 3 | Anti-patterns avoided | 🔴 | "clear leader" is a verdict with no stated axis — the brief-format anti-pattern |
| 4 | Reproducible | 🔴 | No method: 4 vendors appear with no stated selection rule |
| 5 | Confidence honest | 🔴 | Single-assertion tone; no confidence stated on the recommendation |
| 6 | Limitations stated | 🔴 | None |
| 7 | Audience calibrated | ⚠️ | Right length for an executive, but the certainty is unsafe at this evidence level |
| 8 | Counter-evidence addressed | 🔴 | "Competitors are falling behind" is asserted, never examined |
| 9 | Numbers defensible | 🔴 | 60 % YoY has no date, no baseline, no source; it does not reproduce |
| 10 | Next action actionable | ⚠️ | "Prioritise a partnership" has no owner, no first step, no decision date |
| 11–13 | Conditional | N/A | Only 1 technology profiled; no maturity claim; 1 bet — none of the three conditions fires |

**Verdict: BLOCK** (7 red points). Fixes: (1) [¶2] source or delete "largest installed base", and run `grounded-fact-check` on the 60 % figure → passes when both carry resolving citations with measurement dates; (2) [¶2] replace "clear leader" with the axis and its source, e.g. enterprise seats deployed → passes when the axis is named; (3) [new section] add limitations and one competitor that is *not* falling behind → passes with 3 limitations and the counter-case engaged; (4) [¶3] give the recommendation an owner, a first step, and a decision date → passes when all 3 are present. Re-review after fixes: yes.

## Verification

- [ ] All ten base points carry a status and a rationale that cites a specific section — no blank rows, no "looks fine".
- [ ] Each conditional point is either applied or marked `N/A` with the reason its condition did not fire.
- [ ] The verdict follows mechanically from the statuses: any 🔴 blocks, any ⚠️ requires revision before shipping.
- [ ] Every ⚠️ and 🔴 has a fix naming the location and the condition under which the point would pass.
- [ ] The critique was run against the complete draft, not an excerpt — confirm points 1, 7, and 10 were answerable.
- [ ] Re-review after fixes covers the previously failing points only, and the cycle stops at one revision; a third round is escalated instead.

## Pair with adjacent skills

- `red-team-claim` — the claim-level adversarial pass; this skill is the whole-document audit around it.
- `verify-citations` — automates point 2's identifier checking (DOIs, arXiv IDs, URLs).
- `quantitative-sanity-check` — recomputes the figures point 9 depends on.
- `grounded-fact-check` — verifies the load-bearing specifics a point-2 or point-9 failure exposes.
- `abstain-or-escalate` — where point 5 fails because nothing supports the claim, abstention is the fix.
- `write-imrad-report`, `write-sbar-brief` — the producing skills whose output this gates.

## Anti-patterns

- Do **not** skip points because the document is short. Brevity is not an exemption; it usually makes points 4 and 6 fail faster.
- Do **not** return "looks good" with no table. The point-by-point table is the deliverable.
- Do **not** let a ⚠️ ship unfixed. The gate exists to change the document, not to annotate it.
- Do **not** critique one's own draft charitably. Apply the standard that would be applied to someone else's.
- Do **not** force the conditional points onto a document whose shape does not invoke them; `N/A` with a reason is the correct answer.
- Do **not** loop. One critique, one revision, one confirmation; a third iteration means a structural problem that a human should see.

## Reference

- R. J. Heuer Jr. and R. H. Pherson, *Structured Analytic Techniques for Intelligence Analysis*, 2nd ed. Thousand Oaks, CA: CQ Press/SAGE, 2015, ch. 9 "Challenge Analysis" (3rd ed. 2019, ch. 8 "Reframing Techniques", where challenge analysis is the §8.2 sub-family) — Structured Self-Critique: a team exercise over a fixed list of eleven topics, followed by a reassessment of confidence. The influence behind this skill; the thirteen points here are not its eleven topics.
- U.S. Government, *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis*, 2009, pp. 10–11 — the Quality of Information Check, the ancestor of points 2 and 5. https://www.cia.gov/resources/csi/static/955180a45afe3f5013772c313b16face/Tradecraft-Primer-apr09.pdf
- Office of the Director of National Intelligence, *Intelligence Community Directive 203: Analytic Standards*, 2015 — the tradecraft standards behind points 2, 5, 6 and 8: describe source quality, express uncertainty, distinguish information from assumptions, incorporate analysis of alternatives. https://irp.fas.org/dni/icd/icd-203.pdf
- J. Galef, *The Scout Mindset: Why Some People See Things Clearly and Others Don't*. Portfolio, 2021. ISBN 9780735217553 — the motivational problem this gate works around: how identity and motivated reasoning make an author review their own draft charitably. Galef argues about motivation, not about checklists.
- Full point-by-point criteria: [references/checklists.md](references/checklists.md).
