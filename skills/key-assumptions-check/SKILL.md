---
name: key-assumptions-check
description: "Surfaces every premise a conclusion rests on — especially the unstated ones — then challenges each and sorts it into the Key Assumptions Check categories (basically solid, correct with caveats, unsupported or questionable), turning load-bearing unsupported premises into named key uncertainties with a disposition. Use when a conclusion may rest on unexamined premises: \"key assumptions check\", \"what is this conclusion assuming?\", \"what would have to be true for this to hold?\", \"stress-test the reasoning\". Not for ranking rival explanations (use `analysis-of-competing-hypotheses`) or for imagining how a plan fails (use `premortem-analysis`)."
license: MIT
metadata:
  category: evidence-verification
  method: Key Assumptions Check
  origin: U.S. Government Tradecraft Primer, 2009; R. J. Heuer Jr. & R. H. Pherson, Structured Analytic Techniques, 2014/2019
  version: "2.0.0"
---
# Key Assumptions Check

Most bad conclusions are not wrong about the evidence; they are wrong about something assumed without noticing. The Key Assumptions Check — a core diagnostic technique in the U.S. Government *Tradecraft Primer* (2009) and Heuer and Pherson's *Structured Analytic Techniques* (2nd ed. 2014; 3rd ed. 2019, ch. 7) — makes each working premise explicit and challenges why it "must" be true. The Primer supplies the four-step method; the three categories this skill sorts premises into — **basically solid**, **correct with some caveats**, **unsupported or questionable** — are Heuer and Pherson's, and appear nowhere in the Primer. That third category is the point: unsupported premises become named *key uncertainties* and turn into research tasks.

## When to invoke

Invoke when:

- A consequential conclusion is about to ship with its premises unlisted: "key assumptions check", "what is this conclusion assuming?".
- Reasoning moved fast and premises went unwritten: "what would have to be true for {X}?".
- A conclusion has held a while unexamined — the Primer recommends rechecking at project start and before final judgements.
- `analysis-of-competing-hypotheses` has picked a winner whose hidden premises need auditing.

Do NOT invoke when:

- Rival explanations need ranking — use `analysis-of-competing-hypotheses`; this starts from a leading conclusion.
- For future failure modes use `premortem-analysis`; it invents failures, this excavates present premises.
- A stated factual claim needs verifying — use `grounded-fact-check`; the targets here are *unstated* premises.
- A single published headline needs attacking — use `red-team-claim`.

## Procedure

### 1 — Write down the current line of reasoning

State the conclusion under audit in one sentence — "the conclusion is {X}, because {Y}". Sharpen a fuzzy conclusion first (`decompose-research-question` if it is several questions). This is the Primer's first step: write down the current line of reasoning.

### 2 — Articulate every premise, stated and unstated

List everything that must be true for the conclusion to follow. Unstated premises are the dangerous majority — name them: **implicit** ("past patterns continue", "the sources are independent"); **boundary** ("this holds within {scope}, not outside"); **absence-of-evidence** ("no news means nothing changed" — silence is not evidence of stability). Over-list: premises too obvious to write down are usually load-bearing.

### 3 — Challenge each premise and categorise it

For each premise ask why it must be true, whether it holds in all conditions, what would undermine it, whether it was truer in the past, and whether the conclusion changes if it is wrong. Rate two axes, then map to Heuer and Pherson's categories. The grounding × sensitivity grid, and the fourth "Deprioritise" bucket it produces, are this skill's addition — neither source splits weak grounding by sensitivity:

| Grounding × sensitivity | Category | Meaning |
| --- | --- | --- |
| Evidence-backed | **Basically solid (S)** | Supported; record what the conclusion rests on |
| Partly supported, or scope-limited | **Correct with some caveats (C)** | Keep, with the caveat stated |
| Weakly grounded **and** high sensitivity | **Unsupported or questionable (U)** | A **key uncertainty** — conclusion at risk until resolved |
| Weakly grounded, low sensitivity | Deprioritise | Right or wrong, it does not move the answer |

Consensus is not grounding: "everyone assumes X" is a weak premise with confidence attached.

### 4 — Convert key uncertainties into work

Every (U) premise gets one disposition: **re-source** it (`triangulate-sources`, `sift-source-check`); **test** it cheaply (`cheapest-experiment`); **bound** the conclusion to where it holds; or **flag** it and lower stated confidence. The Primer stops earlier: its fourth step refines the list to the premises that "must be true" and asks whether the process "identified new factors that need further analysis" — it never mentions collection requirements. Turning every open (U) premise into a task with an owner is this skill's addition, not the Primer's.

### 5 — Refine the list and sweep for sensitivity

Reduce the list to premises that *must* be true to sustain it, then retract the top two or three one at a time. If the conclusion survives none, it is that premise restated, and the output says so. Name what would force abandoning each surviving premise so the check can be re-run against real events.

## Output template

```
## Key Assumptions Check — {conclusion}

**Conclusion under audit:** {one sentence: {X}, because {Y}}

| # | Assumption | Sensitivity | Grounding | Category | Disposition |
|---|---|---|---|---|---|
| 1 | {implicit premise} | High | Weak | U — key uncertainty | {re-source / test / bound / flag} |
| 2 | {boundary assumption} | High | Strong | S — solid | Note (load-bearing) |
| 3 | {absence-of-evidence premise} | Med | Partial | C — caveats | Bound to {scope} |

**Key uncertainties (U):** {count} — {each with owner and the work that closes it}
**Sensitivity sweep:** {survives losing any single top-3 premise | collapses on #N — fragile}
**Confidence after the check:** {level} — {lowered because #N is unresolved}
**Watch for:** {the information or development that would force abandoning a premise}
```

Mandatory fields: one-sentence conclusion, every assumption with its category, key-uncertainty list with dispositions, and the sweep. A check producing no (U) and no caveat has probably challenged nothing.

## Verification

- [ ] Every assumption traces to a sentence or step in the reasoning audited — no invented premises, no generic risks.
- [ ] At least one implicit premise appears; already-stated premises alone audit the argument's front, not its foundations.
- [ ] Every (U) premise carries a disposition and an owner; reject any resolving to "keep an eye on that".
- [ ] The sensitivity sweep ran — each top premise retracted in turn, the conclusion re-tested — not asserted.
- [ ] No premise is "resolved" by reassertion; grounding means evidence or a test, consensus counts as weak.
- [ ] Confidence moved if a key uncertainty is open; unchanged confidence with open (U) items fails.

## Worked example

Conclusion under audit (illustrative): *"Replatform the SaaS product to multi-region active-active in 2026."*

| # | Assumption | Sensitivity | Grounding | Category | Disposition |
| --- | --- | --- | --- | --- | --- |
| 1 | Churn is driven by availability, not missing features | High | Weak — 47 churn interviews, never segmented by cause | **U** | Re-source: segment them before committing |
| 2 | 2 regions can run without doubling the 14-person ops team | High | Weak — no runbook, no region-2 on-call rotation | **U** | Test: tabletop failover drill in Q1 |
| 3 | The architecture can go active-active without a rewrite | High | Weak — Postgres state layer is single-leader by design | **U** | Re-source: architecture review gates the programme |
| 4 | EU data-residency demand justifies a Frankfurt region | Med | Strong — 3 named prospects, €1.8M ARR | **S** | Note (documented demand) |
| 5 | Cloud pricing stays within ±10 % | Low | Strong — 3-year committed-use discount signed | Deprioritise | — |
| 6 | No competitor ships this first (absence of evidence) | Med | Weak — no monitoring; silence read as stability | **C** | Bound: revisit each quarter |

Key uncertainties: 3 (#1, #2, #3). Sweep: collapses on #1 — if churn is feature-driven, the availability-wins-churn-back premise evaporates and the 2026 programme is the wrong bet regardless of #2 and #3. Confidence: lowered to "recommended conditionally, pending churn segmentation". Watch for: a competitor announcing multi-region GA — flips #6 from caveat to decision input.

## Pair with adjacent skills

- `analysis-of-competing-hypotheses` — picks the hypothesis the evidence favours; this audits what the winner assumes.
- `premortem-analysis` — invents future failures; together they bracket a decision.
- `red-team-claim` — sharper when opened from the key-uncertainty list.
- `triangulate-sources` — the usual way a (U) premise becomes an (S).
- `abstain-or-escalate` — when a key uncertainty cannot close in time, refuse the conclusion.

## Anti-patterns

- Do **not** skip implicit premises; explicit ones are already defended — conclusions die on the unstated.
- Do **not** rate everything medium to dodge the hard call; obvious ratings need no check.
- Do **not** "resolve" a weak premise by restating it; only evidence or a test grounds it.
- Do **not** treat consensus as grounding; shared assumptions are the least recently examined.
- Do **not** leave key uncertainties unflagged; that silent premise is the failure this check catches.
- Do **not** run it only on shaky-feeling conclusions; it pays most on the certain ones, whose assumptions have gone invisible.

## Reference

- U.S. Government, *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis*, 2009, pp. 7–9 — the four-step method, the questions to ask, and the DC sniper case. https://www.cia.gov/resources/csi/static/955180a45afe3f5013772c313b16face/Tradecraft-Primer-apr09.pdf
- R. J. Heuer Jr. and R. H. Pherson, *Structured Analytic Techniques for Intelligence Analysis*, 3rd ed. CQ Press/SAGE, 2019 (2nd ed. 2014), ch. 7 "Diagnostic Techniques" — the Key Assumptions Check and its three categories (solid, correct with caveats, unsupported/questionable = key uncertainties).
- R. J. Heuer Jr., *Psychology of Intelligence Analysis*. Center for the Study of Intelligence, CIA, 1999 — mental models and the failures that follow from unexamined assumptions. https://www.cia.gov/resources/csi/books-monographs/psychology-of-intelligence-analysis-2/
- R. M. Clark, *Intelligence Analysis: A Target-Centric Approach*, 6th ed. CQ Press/SAGE, 2019 — assumption surfacing as the hinge of sound analysis. ISBN 9781544369143
