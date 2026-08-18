---
name: jtbd-framing
description: "Frames a technology, vendor or product comparison around the customer's Job to be Done (JTBD) — a solution-free job statement, Ulwick's desired-outcome metrics, the competing solutions a customer could hire (including non-consumption) and the struggling moment that triggers the search. Use when a brief compares options — \"which of these tools is the right one to adopt?\", \"buy vs build\", \"how do these vendors compare?\", \"what job does this product get hired for?\" — and the comparison risks describing what each option is instead of what it is hired to do. Not for scoring options along chosen axes — use `position-competitor`; not for maturity placement — use `apply-hype-cycle`."
license: MIT
metadata:
  category: decision-strategy
  method: Jobs to be Done (JTBD) framing — Ulwick's outcome-driven job and outcome statements with Christensen's hire / non-consumption lens
  origin: Anthony W. Ulwick (Outcome-Driven Innovation, 2005; Jobs to be Done — Theory to Practice, 2016); Clayton M. Christensen et al. (Competing Against Luck, 2016)
  version: "2.0.0"
---
# JTBD Framing (Jobs to be Done)

Customers do not buy products; they *hire* them to make progress in a circumstance — the "job to be done" (Christensen, Hall, Dillon and Duncan, 2016; the hire metaphor and "competing against non-consumption" go back to Christensen and Raynor, 2003). Anthony Ulwick's Outcome-Driven Innovation (2005; 2016) supplies the grammar: a solution-free **job statement** and measurable **desired-outcome statements**. This skill applies both to a vendor or technology comparison, so each option is placed against the job it is hired for and the alternatives it must displace. The failure it prevents is the tautological comparison — a feature matrix describing what each tool *is* while never saying what anyone hires it to do.

## When to invoke

Invoke when:

- A brief compares vendors, tools or technologies: "which should be adopted?", "buy vs build", "are these tools even competing?".
- A scan has surfaced three or more vendors in one space that need placing against demand, not against each other's feature lists.
- Someone asks "what's the right tool for {context}?" — the answer depends on the job, so the job comes first.

Do NOT invoke when:

- The axes are already chosen and the task is to place options on them — use `position-competitor`.
- The question is where a technology sits in its maturity arc — use `apply-hype-cycle`, or `score-technology-readiness` for a per-technology profile.
- The question is timing ("when will X be viable?") — use `foresight`.
- The plan is chosen and the risk is failure, not fit — use `premortem-analysis`.

## Procedure

### 1 — Write the job statement (Ulwick's job grammar)

State what the customer is trying to accomplish, independent of any solution: **verb + object of the verb + contextual clarifier** — Ulwick's canonical example is "listen to music while commuting to work". A job statement names no product, feature or technology and stays stable while solutions change. "Deploy AI for HR" is a solution; "fill an open engineering requisition with a qualified internal candidate" is a job. Write one per distinct job — most comparisons need one to three.

### 2 — Add the desired outcomes (Ulwick's outcome grammar)

For each job, write two to four desired-outcome statements — the metrics the customer uses to judge whether it is done well: **direction of improvement + metric + object of control + contextual clarifier**, e.g. "minimize the time it takes to identify high-fit internal candidates for an open requisition". Ulwick's direction words are almost always *minimize* or *increase*. Outcomes are solution-free and measurable; "better hiring" is neither.

### 3 — List the competing solutions, including non-consumption

For the same job, list three or four things the customer could hire instead: incumbent products, adjacent tools, manual services — and at least one **non-consumption** entry (what the customer does with no tool: waits, works around, leaves the requisition open). Christensen's point is that non-consumption is usually the strongest competitor and the most vivid description of the current pain; a list of only named vendors has not done the JTBD work.

### 4 — Capture the circumstance and the struggling moment

Record who has the job (segment, size, industry) and, in thirty words or fewer, the moment the customer hits the wall — in the customer's own words where an interview or case study exists, paraphrased otherwise. Label the line *sourced*, *paraphrased* or *speculative*; a speculative moment lowers the confidence of the whole comparison and must say so. "HR is hard" is a complaint, not a struggling moment.

### 5 — Place each option against the job

Write one short paragraph per option: which job and outcomes it serves most directly, which competing solution it is built to displace, and how it changes the struggling moment. Several options may serve the same job — that is the point. If every option maps to the same job, outcomes and competitors in the same context, either find the segment-level difference or say the category is commoditising and a feature comparison is the honest deliverable.

## Output template

```
## JTBD framing — {comparison title}

Technology: {name}
Job: {verb} {object of the verb} {contextual clarifier}
Desired outcomes:
- {minimize | increase} the {metric} it takes to {object of control} {contextual clarifier}
- {minimize | increase} the {metric} …
Circumstance: {who has the job — segment, size, industry}
Competing solutions:
- {named solution 1}
- {named solution 2}
- Non-consumption: {what the customer does with no tool}
Struggling moment: "{≤ 30 words, customer voice or paraphrase}" — {sourced | paraphrased | speculative}
How {name} addresses the job: {which competing solution it displaces; how it changes the struggling moment}
```

One block per technology. Mandatory fields: `Job`, at least one desired outcome, a `Non-consumption` entry, and the `Struggling moment` with its evidence label; a block missing any of them is not a JTBD framing.

## Worked example

Illustrative comparison (company, quotations and figures invented) for Helios Semiconductor, a 12,000-engineer manufacturer choosing between an AI internal-mobility platform (Eightfold), an external recruiter database (LinkedIn Recruiter) and its current agency-plus-referrals process.

```
Technology: Eightfold Talent Intelligence
Job: fill an open engineering requisition with a qualified internal candidate before the role goes external
Desired outcomes:
- minimize the time it takes to identify high-fit internal candidates for an open requisition
- increase the likelihood that a candidate's adjacent skills are recognised without a title match
- minimize the cost per hire of engineering requisitions while holding hire-quality scores
Circumstance: Helios HR business partners, EMEA and Americas sites, 800–1,200 open requisitions per year
Competing solutions:
- LinkedIn Recruiter (external search first; internal profiles incomplete)
- Contingency agencies at a 22 % fee (about $37,000 on a $168,000 role)
- Non-consumption: requisitions stay open 90+ days while managers ask their own network
Struggling moment: "We have 12,000 engineers, but a hiring manager can only search the 200 they have worked with." — format demonstration; the quotation is invented
How Eightfold addresses the job: displaces the agency and the 90-day wait by surfacing internal matches on day one; changes the struggling moment from "who do I know?" to "who is already here?"
```

| Option | Job served | Displaces | Struggling moment change |
| --- | --- | --- | --- |
| Eightfold | internal fill before external search | agencies, 90-day wait | internal search on day 1 |
| LinkedIn Recruiter | fill from the external market fast | agencies | shortens external sourcing, not internal discovery |
| Agency + referrals (status quo) | fill at any cost | — | none; 4 hours of manual CSV export per Director-level role |

The three options serve two different jobs; the brief should say so rather than rank them on one feature list.

## Verification

Before the framing ships, confirm:

- [ ] Each `Job` line contains no product, vendor, feature or technology noun (verb + object + context only).
- [ ] Every desired outcome starts with *minimize* or *increase* and names a metric and an object of control.
- [ ] The competing-solutions list contains a `Non-consumption` entry that describes what the customer does today.
- [ ] The struggling moment is thirty words or fewer, carries its evidence label, and any *speculative* label is echoed in the brief's confidence statement.
- [ ] The options do not all map to an identical job, outcomes and competitor list; if they do, the brief states that the category is commoditising.

## Pair with adjacent skills

- `position-competitor` — after the framing, use the competing-solutions list to choose the map's axes.
- `apply-hype-cycle` — different jobs sit at different points of the maturity curve even inside one category.
- `score-technology-readiness` — build the per-technology profile first, then anchor it in demand here.
- `red-team-claim` — attack a paraphrased struggling moment: would a real customer say it that way?
- `cheapest-experiment` — test whether the recommended option actually serves the named job for the named segment.

## Anti-patterns

- Do **not** put solution language in the `Job` line ("deploy an AI agent"). Push back and rewrite as verb + object + context.
- Do **not** compare technologies without a `Job` line — the comparison is tautological without demand.
- Do **not** omit non-consumption; the customer's current workaround is the competitor that matters most.
- Do **not** accept a vague struggling moment ("talent is competitive"); demand a named segment, a named pain and evidence.
- Do **not** copy the same job across every option — that is a feature matrix wearing JTBD labels.

## Reference

- A. W. Ulwick, *What Customers Want: Using Outcome-Driven Innovation to Create Breakthrough Products and Services*. New York: McGraw-Hill, 2005. ISBN 978-0-07-140867-7 — Outcome-Driven Innovation; desired-outcome statements as the customer's success metrics.
- A. W. Ulwick, *Jobs to be Done: Theory to Practice*. Idea Bite Press, 2016. ISBN 978-0-9905767-4-7 — job statement (verb + object + contextual clarifier) and desired-outcome statement (direction + metric + object of control + contextual clarifier) grammar used in steps 1–2.
- C. M. Christensen, T. Hall, K. Dillon and D. S. Duncan, *Competing Against Luck: The Story of Innovation and Customer Choice*. New York: HarperBusiness, 2016. ISBN 978-0-06-243561-3 — jobs as progress in a circumstance; the struggle that triggers a hire.
- C. M. Christensen, T. Hall, K. Dillon and D. S. Duncan, "Know Your Customers' 'Jobs to Be Done'," *Harvard Business Review*, vol. 94, no. 9, pp. 54–62, Sep. 2016. https://hbr.org/2016/09/know-your-customers-jobs-to-be-done
- C. M. Christensen and M. E. Raynor, *The Innovator's Solution: Creating and Sustaining Successful Growth*. Boston: Harvard Business School Press, 2003. ISBN 978-1-57851-852-4 — competing against non-consumption.
