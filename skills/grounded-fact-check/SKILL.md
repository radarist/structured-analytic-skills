---
name: grounded-fact-check
description: "Audits the load-bearing specifics of a finished draft before it is published — the qubit counts, market figures, benchmark scores, dates and precedence claims a reader would act on — verifying each against live sources with a neutral query and returning a ledger of confirmed, corrected, unverifiable claims. Use when a draft is written and its numbers must hold up — \"fact-check this report before it ships\", \"are these figures right?\", \"check the numbers in this brief\", \"verify the specifics in this draft\". Not for producing a fresh sourced answer (use `grounded-answer`) or recomputing a document's internal arithmetic (use `quantitative-sanity-check`)."
license: MIT
metadata:
  category: evidence-verification
  method: Pre-publication fact-check of load-bearing specifics (adaptation of newsroom fact-checking practice)
  origin: Adapted from professional fact-checking practice — Graves, 2016; IFCN Code of Principles, 2016
  version: "2.0.0"
---
# Grounded Fact-Check

A citation proves a number was written down somewhere; it does not prove the number is right. This skill is a pre-publication check on the handful of specifics a decision rests on: each is re-verified against live sources with a query that does not reveal the drafted value, and the draft is reconciled to what the sources say. It adapts the newsroom discipline described by Lucas Graves (*Deciding What's True*, 2016) and codified in the IFCN Code of Principles (2016), whose sourcing commitment requires evidence a reader can follow and replicate — applied here to a draft's own assertions rather than to a politician's. The failure it prevents is the fabricated-but-plausible specific — a wrong figure presented behind a citation and a confident tone, so every later reviewer assumes someone already checked it.

## When to invoke

Invoke when:

- A report, brief or document is drafted and about to be published, and it states specifics a reader would act on: "fact-check this report before it ships", "are these figures right?", "check the numbers in this brief".
- A draft carries vendor or product specs (qubit counts, parameter counts, context windows, benchmark scores), market figures (revenue, CAGR, headcount), dates and precedence ("released in 2025", "first to ship"), or named standards attached to a specific fact.
- A claim already carries a citation or a source grade — that is exactly the case this check exists for, not an exemption.

Do NOT invoke when:

- No draft exists yet and a fresh sourced answer is what is wanted — use `grounded-answer`.
- The concern is whether a document's own numbers reproduce each other (a CAGR, a unit-economics triple) rather than whether they match the world — use `quantitative-sanity-check`.
- The claim is a forecast, a subjective judgement, or already tagged as an estimate — checking those burns lookups and invents false contradictions; tag them with `claim-provenance` instead.
- A claim is contradicted and no honest correction exists — hand it to `abstain-or-escalate`.

## Procedure

### 1 — Extract the load-bearing claims

List the specific, present-or-past-tense, externally checkable claims a reader would act on — the top 5–12 by decision weight. Record each as drafted, with its exact value and whether it already carries a citation. Leave out forecasts, hedged framing and claims already marked as estimates: the budget of lookups belongs to the specifics that would change a decision if wrong.

### 2 — Verify each with a neutral query

For every claim, look it up with a question that does *not* state the drafted value — anchoring the search on the draft is how a wrong number gets confirmed. Draft "Majorana 1 has 32 logical qubits" becomes the query "how many qubits does Microsoft's Majorana 1 chip have, and are they physical or logical?". Read the sources returned, prefer the most original one (the vendor's own announcement, the filing, the standard), and record its locator.

### 3 — Classify each claim against what the sources state

| Sources vs. draft | Verdict | Action |
| --- | --- | --- |
| Sources state the **same** specific value | **confirmed** | Keep; ensure the citation points at a source that actually states it |
| Sources state a **different, specific** value | **corrected** | Replace the draft value with the sourced one and cite that source |
| No source states a specific value, or they conflict | **unverifiable** | Do not assert it: hedge ("reportedly", "as of {year}"), tag as an estimate, or drop it |

Bias toward *unverifiable* over *corrected* when the result is fuzzy: only correct when a source states a clearly different specific value. Inventing a "corrected" number from a vague result is a new fabrication.

### 4 — Reconcile and emit the ledger

Apply every correction before publication. The published text must contain zero claims still contradicted by the sources, and every claim kept as unverifiable must be visibly hedged — never left behind a citation as though confirmed. Then emit the ledger below alongside (not inside) the document, so the corrections are auditable by whoever reviews it.

## Output template

One line per load-bearing claim; the totals line is mandatory and the contradicted count must be zero in the published text.

```
Fact-check ledger — {document name}, {YYYY-MM-DD}
- {claim as drafted} → {confirmed | corrected | unverifiable} — {source locator} — {correction applied, if any}
- {…one line per load-bearing claim…}
Totals: {N} checked · {C} confirmed · {X} corrected · {U} unverifiable (hedged or dropped) · 0 contradicted remaining
```

## Worked example

Illustrative draft, a quantum-hardware brief with three load-bearing specifics. Step 1 extracts them; step 2 queries each neutrally; step 3 classifies:

| # | Claim as drafted | Neutral query | What sources state | Verdict |
| --- | --- | --- | --- | --- |
| 1 | "Microsoft's Majorana 1 carries 32 logical qubits [3]" | "How many qubits does Microsoft's Majorana 1 chip have, physical or logical?" | Microsoft announcement, 19 February 2025: "eight topological qubits on a chip designed to scale to one million" | **corrected** → 8 topological qubits |
| 2 | "Quantinuum's H2 system reaches 56 qubits" | "How many qubits does Quantinuum's System Model H2 have?" | Quantinuum product page: "56 fully-connected qubits" | **confirmed** |
| 3 | "China overtook the US in quantum computing in 2023" | "When did China surpass the US in quantum computing, by what measure?" | No source states a specific overtaking date or measure; commentary conflicts | **unverifiable** → hedged |

Claim 1 is the case this skill exists for: it carried citation [3] and a confident tone, and was wrong by both magnitude and kind (logical vs topological). Claim 3 is rewritten as "China leads the US on some published quantum metrics as of 2025 [estimate]". Ledger:

```
Fact-check ledger — Quantum hardware brief, 2026-08-16
- Majorana 1 = 32 logical qubits [3] → corrected — Microsoft announcement 2025-02-19 — 32 logical → 8 topological
- Quantinuum H2 = 56 qubits → confirmed — Quantinuum System Model H2 product page
- China overtook the US in quantum in 2023 → unverifiable — no source states a date or measure — hedged to [estimate]
Totals: 3 checked · 1 confirmed · 1 corrected · 1 unverifiable (hedged) · 0 contradicted remaining
```

## Verification

Before the document ships, confirm:

- [ ] Every query used in step 2 is neutral — re-read each one and check that the drafted value does not appear in it.
- [ ] Every verdict names a source locator; no claim was classified from memory or from the draft's own citation.
- [ ] Every claim classified *corrected* has been changed in the text, and the new value matches the cited source word for word.
- [ ] Every claim classified *unverifiable* is visibly hedged, tagged as an estimate, or removed — none is left behind a citation as though confirmed.
- [ ] The ledger's totals add up to the number of claims checked and the contradicted count is zero.

## Pair with adjacent skills

- `grounded-answer` — produces a fresh verified answer; this skill audits a draft that already exists.
- `claim-provenance` — tags what survives as validated or assumption, so hedged claims stay visibly hedged.
- `quantitative-sanity-check` — recomputes a document's internal arithmetic, which this check does not do.
- `triangulate-sources` — when one source is not enough to settle a contested specific.
- `abstain-or-escalate` — where a claim is contradicted and no honest correction exists.

## Anti-patterns

- Do **not** treat a citation, a source grade or a confident tone as verification. Those are the camouflage this check removes.
- Do **not** phrase the query so it echoes the draft ("is it true that Majorana 1 has 32 logical qubits?") — it biases the search toward confirmation.
- Do **not** spend lookups on forecasts or opinions. Scope to checkable specifics.
- Do **not** invent a corrected value when the result is fuzzy. Hedge or drop instead.
- Do **not** skip a claim because it looks obviously right. Obvious-looking numbers are the ones that ship wrong.

## Reference

- L. Graves, *Deciding What's True: The Rise of Political Fact-Checking in American Journalism*. New York: Columbia University Press, 2016. ISBN 978-0-231-17507-4 — the ethnography of newsroom fact-checking practice this procedure adapts.
- International Fact-Checking Network, *IFCN Code of Principles*, Poynter Institute, launched September 2016 — commitments to standards and transparency of sources and to open corrections. https://ifcncodeofprinciples.poynter.org/
- S. Dhuliawala et al., "Chain-of-Verification Reduces Hallucination in Large Language Models," in *Findings of the Association for Computational Linguistics: ACL 2024*, pp. 3563–3578, 2024. doi:10.18653/v1/2024.findings-acl.212 — the independence principle behind the neutral query.
