---
name: abstain-or-escalate
description: "Decides what to do with a claim that verification could not confirm — drop it, refuse it in plain words, escalate it as a named open question, or report the disagreement between conflicting sources — instead of shipping a hedged guess. Use when verification has already failed: \"there is no source for this\", \"the sources contradict each other\", \"should this claim be dropped or flagged?\", \"abstain rather than guess\". Not for running the verification pass itself (use `grounded-answer`) or for checking published numbers against live sources (use `grounded-fact-check`)."
license: MIT
metadata:
  category: evidence-verification
  method: Abstention and escalation decision for unverifiable claims
  origin: ODNI Intelligence Community Directive 203 analytic standards, 2015; Chain-of-Verification, Dhuliawala et al., 2023
  version: "2.0.0"
---
# Abstain or Escalate

A verification pass that comes back empty leaves a decision, not an answer. This skill makes that decision explicit: a claim with no usable source is dropped, refused in plain words, escalated as a named open question, or reported as an unresolved disagreement between sources — but never softened into "probably" and shipped anyway. It is the companion to Chain-of-Verification (Dhuliawala et al., 2023), which verifies, and it applies the sourcing and uncertainty discipline of the ODNI analytic standards (ICD 203, 2015): the quality of the underlying sources is described, uncertainty is expressed rather than smuggled, and assumptions are kept distinct from information. The failure it prevents is the hedged hallucination — a guess wearing a disclaimer, which reads as knowledge to everyone downstream.

## When to invoke

Invoke when:

- A verification step returned no usable source for a drafted claim, or the search results simply do not mention the fact.
- Two sources disagree and neither is clearly more authoritative: "the sources contradict each other — what should the report say?".
- A load-bearing number or recommendation is about to ship on nothing but plausibility: "there is no source for this — drop it or flag it?".
- Answering would need research beyond reach (a paid database, proprietary data, a specialist) and the gap must be handed on rather than filled by guesswork.

Do NOT invoke when:

- Verification has not been attempted yet — run `grounded-answer` (draft, verification questions, independent answers, revision) first; this skill starts where that one fails.
- Specific published numbers need checking against live sources — use `grounded-fact-check`.
- A single source exists but needs corroboration — use `triangulate-sources`; abstention is the last resort, not the first.
- The turn contains no factual claim at all (planning, clarifying questions, chat).

## Procedure

### 1 — Test whether the claim is load-bearing

A claim is load-bearing if removing it would change a decision, a recommendation, or a conclusion's direction. Peripheral colour ("NVIDIA is a large chip company") is not; a decision input ("NVIDIA holds a 40 % share lead in AI accelerators") is. Not load-bearing and unsourced: delete it silently — softened filler accumulates into an unreliable document. Load-bearing and unsourced: continue to step 2.

### 2 — Choose the disposition

Four dispositions, chosen by what is actually missing:

| Situation | Disposition |
| --- | --- |
| The question is answerable if the requester supplies context or narrows it | **Abstain and ask** — name the missing input |
| The answer needs research beyond current reach (paid database, proprietary data, specialist) | **Escalate** — record the open question and say where the answer likely lives |
| The claim is consequential and only a guess is available | **Abstain outright** — an explicit refusal, no hedge |
| Two credible sources disagree | **Report the disagreement** — cite both, state which is weighted higher and why |

### 3 — Write the disposition in plain words

Abstention: "No verifiable source was found for {claim}. The search covered {sources, date window}. Confirming it would need {specific input}." Escalation: "This needs research beyond what is available here: {specific gap}. It is recorded as an open question; the answer likely sits in {named source type}." Disagreement: "{Source A} reports {X}; {Source B} reports {Y}. {A} is weighted higher because {primacy / recency / grade}, but the uncertainty is real." No "probably", no "I think", no "as understood".

### 4 — Record the outcome so the gap is recoverable

In a chat reply, the stated abstention is the record. In a document, leave a marker at the claim site — `<!-- abstained: {claim} — no source as of {date} -->` — so a later pass can backfill rather than rediscover. For an escalation, log the open question wherever the working environment keeps them; if there is no such place, surface it to the requester as a structured note. Count the abstentions: several in one section means the section, not the claim, is unsupported.

## Output template

```
## Verification gap — {claim}

**Claim as drafted:** {verbatim}
**Load-bearing:** {yes — changes {decision} | no — dropped}
**Search performed:** {sources queried, date window, query terms}
**Disposition:** {abstain-and-ask | escalate | abstain outright | report disagreement}

**Statement for the reader:**
> {the plain-words abstention, escalation, or disagreement paragraph}

**What would close the gap:** {specific input, document, or dataset}
**Marker left in the document:** {<!-- abstained: … --> | n/a — chat reply}
```

Mandatory fields: the claim verbatim, the load-bearing verdict, the search actually performed, the disposition, and the reader-facing statement. An escalation is required to name the specific gap and where the answer likely lives — "more research needed" is not an escalation.

## Worked example

**Illustrative walk-through — the firms, claims, numbers and search log below are invented to show the format; none of it is a real verification record.**

A draft market brief on humanoid robotics contains three unsourced claims. Verification ran against web search and the vendor filings on 12 March 2026, and returned nothing usable for two of them.

| # | Drafted claim | Load-bearing? | Search result | Disposition |
| --- | --- | --- | --- | --- |
| 1 | "Arcus Robotics shipped 1,200 units in 2025" | Yes — the adoption argument rests on it | No filing, no press release, 3 blog posts all citing each other | Abstain outright |
| 2 | "Arcus Robotics is a well-known robotics firm" | No | n/a | Drop silently (kept as background, no citation needed) |
| 3 | "Unit costs fell 35 % between 2023 and 2025" | Yes — drives the 2027 forecast | Northgate Research says 35 %, Delvin Securities says 12 % | Report the disagreement |

```
## Verification gap — "Arcus Robotics shipped 1,200 units in 2025"

**Claim as drafted:** Arcus Robotics shipped 1,200 units in 2025.
**Load-bearing:** yes — the "adoption is accelerating" conclusion rests on this number
**Search performed:** web search 2026-03-12 (3 queries), company newsroom, SEC full-text search; 2019-2026 window
**Disposition:** abstain outright

**Statement for the reader:**
> No verifiable source was found for a 2025 shipment figure for Arcus Robotics. The three secondary
> articles carrying "1,200 units" all trace back to one unsourced blog post. Confirming it would
> need a company disclosure or an analyst note with a stated methodology.

**What would close the gap:** a Arcus Robotics disclosure, or a named analyst estimate with its method
**Marker left in the document:** <!-- abstained: Arcus Robotics 2025 shipments — no source as of 2026-03-12 -->
```

Claim 3 ships as a disagreement: "Northgate Research reports a 35 % decline and Delvin Securities reports 12 %; the Delvin Securities figure is weighted higher because it states its bill-of-materials method, but the range is real and the 2027 forecast is given as a band, not a point."

## Verification

- [ ] No load-bearing claim in the shipped text carries "probably", "I think", "as understood", or "reportedly" in place of a source — each is either sourced, dropped, or explicitly abstained.
- [ ] Every abstention in a document leaves its `<!-- abstained: … -->` marker; no claim is silently deleted after being judged load-bearing.
- [ ] Every escalation names the specific gap and the concrete input or source type that would close it; re-read each one and reject "further research is needed".
- [ ] Each reported disagreement cites both sources and states which is weighted higher and why.
- [ ] The abstention count per section is checked: three or more in one section means the section's conclusion is re-examined, not just its sentences.

## Pair with adjacent skills

- `grounded-answer` — the verification half (Chain-of-Verification); this skill decides what happens when that pass comes back empty.
- `grounded-fact-check` — targets load-bearing specifics against live sources; its failures route here.
- `triangulate-sources` — corroborate before abstaining; two independent sources beat one refusal.
- `rate-source-admiralty` — grade the two sources in a reported disagreement so the weighting is defensible.
- `red-team-claim` — an attack that ends in "retract" hands the claim to this skill.

## Anti-patterns

- Do **not** soften. "I think…", "Probably…", "It is widely believed…" attached to an unsourced load-bearing claim is a hallucination with a disclaimer.
- Do **not** invent a source to justify a guess. Fabricated provenance is the worst available outcome.
- Do **not** escalate trivia. Escalation signals real research work; if the answer is one search away, run the search.
- Do **not** abstain performatively. With three sourced claims and one unsourced, report the three and drop the fourth — refusing the whole answer is theatre.
- Do **not** treat "the sources disagree" as a reason to pick the convenient one silently. The disagreement is the finding.

## Reference

- Office of the Director of National Intelligence, *Intelligence Community Directive 203: Analytic Standards*, 2 January 2015 — analytic tradecraft standards on describing source quality and credibility, expressing uncertainty, and separating information from assumptions. https://irp.fas.org/dni/icd/icd-203.pdf
- S. Dhuliawala, M. Komeili, J. Xu, R. Raileanu, X. Li, A. Celikyilmaz, and J. Weston, "Chain-of-Verification Reduces Hallucination in Large Language Models," arXiv:2309.11495, 2023 — the four-step verify cycle this skill continues when verification fails.
- H. Zong, B. Li, Y. Long, S. Chang, J. Wu, and G. K. Hadfield, "I-CALM: Incentivizing Confidence-Aware Abstention for LLM Hallucination Mitigation," arXiv:2604.03904, 2026 — prompt-level abstention incentives plus humility norms lower the false-answer rate without retraining.
