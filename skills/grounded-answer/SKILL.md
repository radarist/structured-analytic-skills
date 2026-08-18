---
name: grounded-answer
description: "Produces a factual answer in which every claim has been independently checked against a source and cited, using Chain-of-Verification (CoVe — Dhuliawala et al., 2023) — the answer ships only with claims that survived verification, plus a list of what could not be verified. Use when a factual answer will reach a reader or a decision — \"give me a sourced answer\", \"what year did that happen? verify it\", \"run chain-of-verification on this question\", \"answer with citations, no guessing\". Not for auditing the numbers in an already-written draft (use `grounded-fact-check`) or for interpretive questions where several explanations compete (use `analysis-of-competing-hypotheses`)."
license: MIT
metadata:
  category: evidence-verification
  method: Chain-of-Verification (CoVe)
  origin: Dhuliawala, Komeili, Xu, Raileanu, Li, Celikyilmaz and Weston (Meta AI), 2023
  version: "2.0.0"
---
# Grounded Answer (Chain-of-Verification)

Chain-of-Verification (CoVe) is the four-step procedure of Dhuliawala et al. (Meta AI, 2023; Findings of ACL 2024): generate a baseline response, plan verification questions for it, execute those verifications *without the draft in view*, and generate a final verified response. The core principle is independence — verification answers that cannot see the draft cannot copy its mistakes; in the paper, CoVe (factored) raised closed-book MultiSpanQA F1 from 0.39 to 0.48 and longform-biography FactScore from 55.9 to 71.4 (factor+revise), while its two-step variant cut hallucinated entities per Wikidata list answer from 2.95 to 0.68. The paper verifies with the model alone and names retrieval as an unexplored extension; this skill adopts that extension and executes every verification against a source (document, web page, primary record) whose locator is recorded. The failure it prevents is the fluent, confident, uncited fabrication.

## When to invoke

Invoke when:

- A response will contain factual claims — a founding year, a date, a count, a specification, a relation between two entities, a numeric value, a comparison — and will reach a reader, be stored, or influence a decision: "give me a sourced answer", "verify that before answering", "answer with citations".
- A single-answer factual question is asked and guessing would be costly.

Do NOT invoke when:

- The turn contains no factual claims — greetings, clarifying questions, planning talk.
- A finished draft needs its load-bearing specifics audited rather than a fresh answer produced — use `grounded-fact-check`.
- A claim failed verification and no honest softening exists — hand it to `abstain-or-escalate` to refuse or escalate instead of shipping a guess.
- Only the identifiers of already-verified citations (DOIs, arXiv IDs, URLs) need checking — use `verify-citations`.
- The question is interpretive with several plausible explanations — use `analysis-of-competing-hypotheses`.

## Procedure

### 1 — Generate the baseline response

Write the proposed answer as it would normally be written, in full, and keep it. Do not publish it. The draft exists to be checked, and its every factual sentence becomes a candidate for verification in the next step; an answer that skips the draft has nothing concrete to test.

### 2 — Plan verification questions

For each factual claim in the draft, write one short question that a neutral third party could answer from a primary source: "In what year was Anthropic founded?", not "Is it true that Anthropic was founded in 2021?" — a question that embeds the draft's value biases its own answer. Aim for 3–8 questions per response and write each independently, without reference to the others.

### 3 — Execute the verifications independently against sources

Answer each question with the draft out of view (the paper's factored variant), by looking it up: facts held in the team's own records or documents → that store; current or live-web facts → web search and page fetch; academic facts → a scholarly index; patents → a patent search. Record the raw locator for every answer — URL, DOI, document id, record and field — and quote or use structured fields rather than paraphrase. An answer without a locator is a guess, not a verification.

### 4 — Generate the final verified response

Compare the draft against the verified answers and revise:

| Check | Action |
| --- | --- |
| Draft claim matches a verified answer | Keep it and attach the citation |
| Draft claim contradicts a verified answer | Replace it with the verified claim and citation |
| Draft claim cannot be verified from any source | Soften to "reportedly / as of {year}" **or** remove, and list it under "Not verified" |
| Two sources disagree | State both, say which is more recent or authoritative; if irreconcilable, name the gap |

## Output template

Every factual sentence must carry an inline citation; the `Not verified` line is mandatory (write "none" if nothing was dropped or softened). Verification questions and intermediate answers stay out of the output unless the reader asks for the trace.

```
{answer text — only claims that survived step 3, each with an inline citation [n]}

Sources:
[1] {locator — URL / DOI / document id / record and field}, accessed {YYYY-MM-DD}
[2] {…}

Not verified: {dropped or softened claim} — {no source found | sources disagree: {A} says {x}, {B} says {y}} | none
```

## Worked example

Question: *Which paper introduced Chain-of-Verification, when, what did it report on MultiSpanQA, and where was it published?* Step 1, draft: "CoVe was introduced by Dhuliawala et al. of Meta AI in September 2023 (arXiv:2309.11495); it reported an F1 improvement from 0.39 to 0.48 on MultiSpanQA and was published at ACL 2024." Steps 2–3, planned and executed against sources:

| Verification question | Verified answer | Locator |
| --- | --- | --- |
| Who authored the CoVe paper and what is its arXiv identifier? | Dhuliawala, Komeili, Xu, Raileanu, Li, Celikyilmaz, Weston; arXiv:2309.11495 | arxiv.org/abs/2309.11495 |
| When was the first version submitted? | 20 September 2023 (v2 25 September 2023) | arxiv.org/abs/2309.11495 |
| What MultiSpanQA F1 did the paper report for the baseline and for CoVe? | 0.39 → 0.48, described as a 23 % improvement | arXiv PDF v2, Section 5 |
| At what venue was the paper published? | *Findings of the Association for Computational Linguistics: ACL 2024*, pp. 3563–3578 | doi:10.18653/v1/2024.findings-acl.212 |

Step 4: three claims match; the fourth contradicts — the venue is *Findings of ACL 2024*, not the main ACL 2024 proceedings — so it is replaced. Final response: "Chain-of-Verification was introduced by Dhuliawala et al. (Meta AI) in September 2023 [1]; the paper reports MultiSpanQA F1 rising from 0.39 to 0.48 [1] and appeared in Findings of ACL 2024, pp. 3563–3578 [2]. Not verified: none."

## Verification

Before the answer ships, confirm:

- [ ] Every verification question was answered with a recorded locator — none from memory; if no lookup was made, the claim moves to "Not verified".
- [ ] No verification question embeds the draft's value ("in what year…", not "is it true that … 2021").
- [ ] Every factual sentence in the final answer carries a citation whose source actually states the claim.
- [ ] Contradictions were resolved in favour of the verified value; disagreements between sources are stated, not averaged.
- [ ] The "Not verified" line lists every dropped or softened claim, or says "none".

## Pair with adjacent skills

- `grounded-fact-check` — audits the load-bearing specifics of a finished draft; this skill produces a fresh verified answer.
- `abstain-or-escalate` — the hand-off when step 3 finds no usable source.
- `triangulate-sources` — establishes a claim by independent corroboration when one source is not enough.
- `verify-citations` — checks the identifiers of the surviving citations.
- `cite-ieee` — formats the surviving citations when the output is a report.

## Anti-patterns

- Do **not** answer verification questions from memory. Without a lookup and a locator, the answer is a guess.
- Do **not** phrase verification questions so they echo the draft. "Is it true that X was founded in 2021?" biases the answer; ask "In what year was X founded?".
- Do **not** skip step 3 because the draft "is obviously correct". The paper's gains come from catching obvious-seeming hallucinations.
- Do **not** ship the verification trace by default. Only the final verified response goes to the reader unless the trace is requested.

## Reference

- S. Dhuliawala, M. Komeili, J. Xu, R. Raileanu, X. Li, A. Celikyilmaz and J. Weston, "Chain-of-Verification Reduces Hallucination in Large Language Models," arXiv:2309.11495, 20 September 2023 (v2, 25 September 2023). https://arxiv.org/abs/2309.11495
- S. Dhuliawala et al., "Chain-of-Verification Reduces Hallucination in Large Language Models," in *Findings of the Association for Computational Linguistics: ACL 2024*, pp. 3563–3578, 2024. doi:10.18653/v1/2024.findings-acl.212
