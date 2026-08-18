---
name: premortem-analysis
description: "Runs Gary Klein's premortem — declare that the plan has already failed, then work backwards to surface the failure modes, pre-emptive mitigations and a kill threshold before the plan is locked in. Use before a strategy, roadmap, launch or investment decision is committed — \"premortem this plan\", \"what could go wrong with this decision?\", \"assume it's a year from now and the project has failed — why?\", \"stress-test this roadmap before committing\". Not for auditing the hidden premises behind a conclusion (use `key-assumptions-check`) or for choosing between rival explanations (use `analysis-of-competing-hypotheses`)."
license: MIT
metadata:
  category: decision-strategy
  method: Premortem (prospective hindsight)
  origin: Gary Klein — described in Sources of Power, 1998, ch. 5; popularised in Harvard Business Review, 2007; prospective hindsight — Mitchell, Russo & Pennington, 1989
  version: "2.0.0"
---
# Premortem Analysis

A premortem is the hypothetical opposite of a postmortem: before a plan is committed, the team is told it **has already failed**, and each person independently writes down every plausible reason why. Gary Klein described the exercise in *Sources of Power* (1998), ch. 5, and popularised it in "Performing a Project Premortem" (*Harvard Business Review*, 2007). It builds on the *prospective hindsight* of Mitchell, Russo and Pennington (1989), who found people generate **more reasons** for events framed as having already occurred — an effect the paper attributes to outcome certainty, not temporal perspective. The familiar "raises the ability to identify reasons by roughly 30 %" figure is not in that paper: it is Klein's gloss in HBR (2007). It counters the optimism bias and "damn-the-torpedoes" attitude that keep known weaknesses unspoken; Kahneman (2011) popularised it, crediting Klein.

## When to invoke

Invoke when:

- A strategy, roadmap, launch or investment is about to be locked in and reversal would be costly.
- A plan has been discussed at length with no serious objection — that silence is the symptom Klein targets.

Do NOT invoke when:

- The conclusion rests on unexamined premises, not a plan to execute — audit them with `key-assumptions-check`.
- The question is *which explanation is true*, not *whether a plan survives* — use `analysis-of-competing-hypotheses`.
- The recommendation cannot yet be stated in one sentence — sharpen it with `decompose-research-question`, or `abstain-or-escalate` if it has no verifiable basis.
- The decision is already executed (a postmortem, not covered here) or cheap and easily reversed.

## Procedure — Klein's premortem plus a scoring extension

Steps 1–3 and 5 are Klein's method; the five-domain scaffold, scores and kill threshold (steps 3, 4, 6) are this skill's additions so the output ranks and gates rather than lists.

### 1 — Brief the plan and fix the decision

Klein's premortem "begins after the team has been briefed on the plan". State the decision in one sentence with owner, date and success measure — "Ship X by Y to achieve Z" — and name the participants; a solo agent adopts several vantage points (engineering, buyer, finance, legal).

### 2 — Declare the failure

The leader "starts the exercise by informing everyone that the project has failed spectacularly" (Klein); in Kahneman's phrasing, it is a year into the future, the plan was implemented as it now exists, and the outcome was a disaster. Write a dated, present-tense, two-to-three-sentence vignette. Certainty is the mechanism — "has failed", never "might fail"; certainty invites explanation, uncertainty reassurance.

### 3 — Generate reasons independently, then share round-robin

Every participant **independently writes down every reason** for the failure — "especially the kinds of things they ordinarily wouldn't mention as potential problems, for fear of being impolitic" (Klein). Only then does the leader go round the room, "starting with the project manager", each reading one new reason until all are captured. Reasons must be concrete — named person, component, month, consequence; not "the team is weak". Check coverage of five domains — **technical, market, execution, regulatory/legal, external shock**; an empty domain is a blind spot to fill or justify.

### 4 — Rate likelihood × severity

Rate each reason Low/Medium/High on likelihood and severity (L=1, M=2, H=3) and multiply for a 1–9 score. Sort; the top three demand mitigation design, the rest are watched. Break ties toward the reason whose early evidence arrives latest.

### 5 — Strengthen the plan

After the session "the project manager reviews the list, looking for ways to strengthen the plan" (Klein). For each top-three risk propose **one** mitigation: actionable before commitment, testable and cheaper than the loss prevented. "Hire more engineers" for "too few engineers" restates the risk and does not count. No feasible mitigation is itself a finding — say so.

### 6 — Set the kill threshold and hand off

Specify "abandon, pivot or pause if {metric} {crosses threshold} by {date}", tied to the highest-ranked failure mode so failure becomes visible early. Feed mitigations in as pre-launch checkpoints and the kill threshold as a decision gate; the smallest test of each mitigation is a `cheapest-experiment` design.

## Output template

```
## Premortem — {decision}

**Decision:** {one sentence: action, owner, date, success measure}
**Participants / vantage points:** {names or roles}
**Failure declared:** {dated, present-tense, 2–3 sentence vignette}

| Domain | Reason (concrete) | L×S = Score | Mitigation (pre-commitment, testable) |
|---|---|---|---|
| {Technical/Market/Execution/Regulatory/External} | {reason} | {L/M/H}×{L/M/H} = {1–9} | {mitigation or "none feasible"} |

**Top 3 by score:** 1. {reason} — {mitigation}; 2. …; 3. …
**Kill threshold:** abandon/pivot/pause if {metric} {threshold} by {date}.
**Domains left empty and why:** {none | domain — justification}
**Confidence in this premortem:** {0.0–1.0} — {how well the reasons match known failure history}
```

Mandatory fields: decision, failure declared, one reason per domain (or a stated justification), scores, top-3 mitigations, kill threshold.

## Worked example

Illustrative case (all figures invented): a developer-tools company plans a $49/month self-serve API tier for Q4 2026, undercutting its sales-led plan at about $4,000/month.

```
## Premortem — "Self-serve API tier, Q4 2026"

**Decision:** Launch a $49/mo self-serve API tier on 15 October 2026 (owner: Priya Natarajan, VP Product); success = 5 % paid conversion and no fall in enterprise win rate by launch + 90 days.
**Participants / vantage points:** product, sales, support, security.
**Failure declared:** It is April 2027. The tier drew 400 sign-ups but only 3 % converted; two enterprise prospects walked away, quoted $4,000 for something listed at $49; support response times for paying customers doubled.

| Domain | Reason | L×S = Score | Mitigation |
|---|---|---|---|
| Market | Self-serve price anchors enterprise negotiations downward | H×H = 9 | Separate SKUs (no SLA, SSO or support on self-serve); value-based sales deck |
| Execution | Sign-ups never activate — first successful call takes > 1 hour | M×H = 6 | 15-minute quickstart as launch blocker; activation funnel instrumented |
| Execution | Unqualified users flood support; enterprise SLAs slip | M×M = 4 | Docs-first onboarding, forum, 48 h SLA on free-tier questions |
| Regulatory | Sign-ups from sanctioned jurisdictions bypass export screening | L×H = 3 | Sanctions screening at sign-up, signed off by legal |
| Technical | Open sign-up abused for scraping and card testing | L×M = 2 | Rate limits and card-required trial |

**Top 3 by score:** 1. price anchoring (9); 2. activation failure (6); 3. support flood (4).
**Kill threshold:** pause the tier if paid conversion < 5 % or enterprise win rate falls > 20 % versus the two-quarter baseline by 13 January 2027.
**Domains left empty and why:** external shock — none plausible beyond price moves already covered under Market.
**Confidence in this premortem:** 0.7 — reasons match the documented product-led vs sales-led tension.
```

## Verification

Before the premortem ships:

- [ ] The failure is declared in the past tense, dated and specific — "has failed", not "might fail".
- [ ] Reasons were generated independently before discussion (solo: at least three vantage points) and all were recorded.
- [ ] Each of the five domains has a reason, or the empty domain carries a justification.
- [ ] Recompute each score as likelihood × severity and check the top-3 list matches the sorted table.
- [ ] Each mitigation is actionable before commitment, testable, and not a restatement of the risk.
- [ ] The kill threshold names a metric, threshold and date and would fire on the top-ranked failure mode.

## Pair with adjacent skills

- `key-assumptions-check` — audits the premises a plan relies on; the premortem imagines its failure.
- `analysis-of-competing-hypotheses` — picks the leading explanation; the premortem stress-tests the plan built on it.
- `cheapest-experiment` — turns each mitigation and the kill threshold into the smallest pass/fail test.
- `scenario-planning` — the premortem imagines one failure; scenarios branch the environment into several futures.

## Anti-patterns

- Do **not** run a premortem without a specific decision — "what are the risks of AI?" is not one; "ship the assistant by Q3" is.
- Do **not** ask "what might go wrong?" — an ordinary critique session; Klein's mechanism is the declared, certain failure.
- Do **not** discuss before writing. Independent generation first, then round-robin; discussing first reproduces the groupthink the method breaks.
- Do **not** stop at the list — without scores, mitigations and a kill threshold the premortem is decoration.

## Reference

- G. Klein, "Performing a Project Premortem," *Harvard Business Review*, vol. 85, no. 9, pp. 18–19, Sept. 2007. https://hbr.org/2007/09/performing-a-project-premortem
- G. Klein, *Sources of Power: How People Make Decisions*. Cambridge, MA: MIT Press, 1998, ch. 5 — the first published description of the premortem exercise, with the Mitchell/Russo/Pennington footnote ("people generate more reasons ... if they could frame it as an event that had already occurred"). ISBN 0-262-11227-2.
- G. Klein, *The Power of Intuition: How to Use Your Gut Feelings to Make Better Decisions at Work*. New York: Currency/Doubleday, 2004. ISBN 0-385-50289-3.
- D. J. Mitchell, J. E. Russo and N. Pennington, "Back to the future: Temporal perspective in the explanation of events," *Journal of Behavioral Decision Making*, vol. 2, no. 1, pp. 25–38, 1989. doi:10.1002/bdm.3960020103.
- D. Kahneman, *Thinking, Fast and Slow*. New York: Farrar, Straus and Giroux, 2011, ch. 24 "The Engine of Capitalism", section "The Premortem: A Partial Remedy". ISBN 978-0-374-27563-1.
