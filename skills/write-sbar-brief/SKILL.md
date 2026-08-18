---
name: write-sbar-brief
description: "Structures a one-page decision briefing as SBAR — Situation, Background, Assessment, Recommendation — with a hard length cap per section and a single named action, so a decision-maker gets the whole picture and the ask on one page. Use when someone asks for a short briefing rather than a report: \"give me a 1-pager on the outage\", \"SBAR on this vendor\", \"brief me before Thursday's board\", \"decision memo on the migration\". Not for a long research write-up with methods and results (use `write-imrad-report`) or a factual lookup with no recommendation (`grounded-answer`)."
license: MIT
metadata:
  category: writing
  method: SBAR (Situation, Background, Assessment, Recommendation)
  origin: Michael Leonard, Suzanne Graham and Doug Bonacum, Kaiser Permanente, 2004
  version: "2.0.0"
---
# Write SBAR Brief

SBAR is a situational briefing model in four fixed moves — Situation, Background, Assessment, Recommendation — described by Leonard, Graham and Bonacum at Kaiser Permanente in 2004 and spread through hospitals by Haig, Sutton and Whittington (2006) as a "shared mental model". In the original wording: situation — what is going on? background — what is the context? assessment — what do I think the problem is? recommendation — what would I do to correct it? The core principle is that the sender must have formed an assessment and a recommendation *before* opening the channel, so the receiver gets a diagnosis and an ask rather than a narrative to interpret. It prevents the failure in which a briefing delivers facts in the order they were discovered and leaves the reader to work out both what they mean and what to do.

## When to invoke

Invoke when:

- A decision-maker asks for a short briefing: "give me a 1-pager on the outage", "SBAR on this vendor", "brief me before Thursday's board".
- Something changed and someone must act on it — an incident, a competitor move, a supplier failure — and the ask fits on one page.
- A handover or escalation passes a live situation to someone who was not watching it.

Do NOT invoke when:

- The deliverable is a research write-up with methods, results and citations — use `write-imrad-report`.
- The question is factual with one right answer and no action attached — use `grounded-answer`.
- The argument needs building and ordering, not compressing into a container — use `pyramid-principle`; SBAR is the container, the pyramid the geometry inside it.
- The question is too large for one page — use `decompose-research-question`, then brief each part.
- The evidence is too thin for any recommendation — use `abstain-or-escalate` rather than guessing in the R slot.

## Procedure

### 1 — Name the decision the brief serves

Write, in one sentence, the decision the reader must make after reading. If no decision can be named, this is a status update, not a brief. The named decision fixes what belongs in Background — only what bears on that decision — and what the Recommendation must address.

### 2 — Situation: what is happening now, in ≤3 sentences

State the present state in plain language: what happened, when, to what, and how it is known. Present tense, no history, no judgement — "troubling", "impressive", "alarming" pre-empt the Assessment and cost the reader the ability to disagree with it. The first sentence must be intelligible with zero prior context.

### 3 — Background: the context that makes the Situation legible, in ≤4 sentences

Supply only the history bearing on the named decision: prior events, the trajectory, related moves, what has been tried. Prune anything the reader would not act differently for. Introduce no new claims — every fact must be sourced or derivable from the Situation, because Background is where unsupported assertions hide most easily.

### 4 — Assessment: what it means, in ≤5 sentences

This is the analytical contribution, and what separates a brief from a summary. Name what is really going on, the pivotal factor, the risks specifically — not "there are risks" — and the uncertainty that would change the picture. If it reads like restated facts, no assessment happened; rewrite it. Grade the sources with `rate-source-admiralty` when the conclusion rests on one.

### 5 — Recommendation: one action, with owner, timing and confidence

State what to do — one primary action, at most one fallback; decisions have singular actions. Give the owner and the date. Attach a confidence tag with a one-line justification: this tag is a library convention, not part of the original model, and it lets a reader tell a firm recommendation from a hedge. Below "medium — could go either way", route to `abstain-or-escalate` rather than shipping a guess.

### 6 — Cut to one page

Total ≈400–500 words. Over that, either the writing is loose or the question wants a report — cut Background first, Assessment last. The caps are the method: a brief that does not fit is not a brief.

## Output template

```
# Brief: {topic} — {date}

## Situation
{≤3 sentences · present state · what, when, how known · no evaluative adjectives}

## Background
{≤4 sentences · only the history bearing on the decision · no new claims}

## Assessment
{≤5 sentences · what it means · pivotal factor · named risks · the uncertainty that would change it}

## Recommendation
- **Action:** {one action}
- **Owner:** {who}
- **By:** {date}
- **Confidence:** {high | medium | low} — {one-line justification: what it rests on, what would change it}
- **Fallback:** {optional single alternative}
```

All four SBAR sections are mandatory and must appear in this order; the Recommendation must name an action, an owner and a confidence tag. A brief without a recommendation is a status update, and one without a confidence tag cannot be weighed.

## Worked example

Leonard, Graham and Bonacum's own clinical example (2004), which shows the four moves at their shortest:

```
Situation:      "Dr Preston, I'm calling about Mr. Lakewood, who's having trouble breathing."
Background:     "He's a 54 year old man with chronic lung disease who has been sliding
                 downhill, and now he's acutely worse."
Assessment:     "I don't hear any breath sounds in his right chest. I think he has a
                 pneumothorax."
Recommendation: "I need you to see him right now. I think he needs a chest tube."
```

Four sentences carry a patient, a trajectory, a diagnosis and an ask. The same shape outside medicine, in an illustrative incident brief with invented figures:

| Section | Content |
|---|---|
| Situation | The payments API has returned 502s for 11% of requests since 03:40 UTC on 14 March; 1,240 checkouts failed. Monitoring and two customer reports confirm it. |
| Background | Release 4.7 shipped a connection-pool change on 13 March. A similar exhaustion caused a 40-minute outage in November. The pool cap has not moved since 2024. |
| Assessment | The pattern matches pool exhaustion under peak load, not an upstream provider fault — provider status is green and latency flat. The pivotal unknown is whether traffic is genuinely up 30% or a retry storm inflates it; if retries, raising the cap makes it worse. |
| Recommendation | **Action:** roll back release 4.7 and re-measure before touching the cap. **Owner:** platform on-call. **By:** 16:00 UTC today. **Confidence:** medium — one metric series; a retry-storm signature in client logs would change it. |

Note the discipline: "11% of requests" is Situation; "matches pool exhaustion, not an upstream fault" is Assessment; the retry-storm caveat sits with the recommendation it would overturn.

## Verification

- [ ] Count the sentences: Situation ≤3, Background ≤4, Assessment ≤5, and the whole brief ≤500 words.
- [ ] Re-read the Situation for evaluative adjectives and move every one of them into the Assessment.
- [ ] Check each Background sentence is sourced or derivable from the Situation — delete any claim appearing only there.
- [ ] Confirm the Assessment names a specific risk and the uncertainty that would change the conclusion.
- [ ] Confirm the Recommendation names one primary action with an owner, a date and a justified confidence tag.
- [ ] Confirm the decision named in step 1 is the one the Recommendation addresses.

## Pair with adjacent skills

- `pyramid-principle` — the argument geometry inside the Assessment and Recommendation; SBAR is the container.
- `write-imrad-report` — the long-form counterpart when the reader needs methods and results, not a decision.
- `rate-source-admiralty` — grade the sources behind Situation and Background before the Assessment leans on them.
- `abstain-or-escalate` — the route when confidence is too low to recommend anything.
- `critique-report` — the pre-delivery review of the finished brief.

## Anti-patterns

- Do **not** exceed one page. A two-page brief is a report wearing a brief's headings.
- Do **not** editorialise in Situation. Neutral facts there are what let the Assessment land as analysis rather than as spin.
- Do **not** offer five recommendations. A menu returns the decision to the reader, which is the work the brief was meant to do.
- Do **not** omit the confidence tag or leave it unjustified; an unqualified recommendation cannot be weighed against what the reader already knows.
- Do **not** move the Recommendation to the top. The order is the method: the reader reaches the ask having already accepted the situation, the context and the diagnosis.
- Do **not** put new facts in the Assessment. It interprets what Situation and Background have already established.

## Reference

- M. Leonard, S. Graham, and D. Bonacum, "The human factor: the critical importance of effective teamwork and communication in providing safe care," *Quality and Safety in Health Care*, vol. 13, suppl. 1, pp. i85–i90, Oct. 2004, doi: 10.1136/qhc.13.suppl_1.i85 — SBAR as "a situational briefing model", with the four questions and the clinical example quoted above.
- K. M. Haig, S. Sutton, and J. Whittington, "SBAR: a shared mental model for improving communication between clinicians," *Joint Commission Journal on Quality and Patient Safety*, vol. 32, no. 3, pp. 167–175, Mar. 2006, doi: 10.1016/s1553-7250(06)32022-3 — implementation at OSF St. Joseph Medical Center, and the observed hesitancy in stating the Recommendation.
- Institute for Healthcare Improvement, "SBAR tool: situation, background, assessment, recommendation," 2024 — attributes the technique to M. Leonard, D. Bonacum and S. Graham at Kaiser Permanente of Colorado. [Online]. Available: https://www.ihi.org/resources/tools/sbar-tool-situation-background-assessment-recommendation
