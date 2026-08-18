---
name: red-team-claim
description: "Attacks a headline claim the way a hostile reviewer would, along seven named vectors — definition, baseline, selection, counter-example, mechanism, base rate, incentive — then returns a survival score, a verdict of ship, hedge, rewrite or retract, and the hedged wording to publish. Use before a conclusion reaches a reader: \"red team this claim\", \"what would a skeptic say about this takeaway?\", \"attack this conclusion before it ships\", \"poke holes in this\". Not for auditing a whole report section by section (use `critique-report`) or for building the opposing case charitably (use `steelman-argument`)."
license: MIT
metadata:
  category: evidence-verification
  method: Red team / challenge analysis of a single claim
  origin: Seven-vector instrument built for this skill; challenge analysis after U.S. Government Tradecraft Primer, 2009 and Heuer & Pherson, Structured Analytic Techniques, 2nd ed. 2015; M. Zenko, 2015
  version: "2.0.0"
---
# Red Team a Claim

Adversarial review of one claim: the sharpest available critic gets the claim as written and says what breaks it. The method sits in the challenge-analysis family of structured analytic techniques — Devil's Advocacy and Red Team Analysis in the U.S. Government *Tradecraft Primer* (2009) and Heuer and Pherson's *Structured Analytic Techniques* (2nd ed., 2015) — and the practitioner literature on red teaming as institutional habit (Zenko, 2015). The instrument below is not from any of them: the seven named vectors, the 0–7 survival score and the ship/hedge/rewrite/retract bands are this skill's own construction. Core principle: a claim is only as strong as its weakest undefended flank, so the flanks are enumerated by name, not left to the reviewer's mood. It prevents the confident headline nobody attacks until a reader, competitor, or regulator does.

## When to invoke

Invoke when:

- A headline conclusion or "key takeaway" is about to reach a reader: "red team this claim", "what would a skeptic say?".
- A recommendation will be acted on, or the claim will propagate elsewhere.
- `analysis-of-competing-hypotheses` has picked a winner needing an adversarial pass before shipping.

Do NOT invoke when:

- The whole document needs auditing — sourcing, limitations, structure, next actions — use `critique-report`.
- The opposing position must first be built at full strength — use `steelman-argument`; attacking a caricature proves nothing.
- The claim is not verified yet — verify with `grounded-answer` and `triangulate-sources` first.
- The output is descriptive, not assertive (an extraction, record, or log): no claim to attack.

## Procedure

### 1 — State the claim verbatim

Lift the claim exactly as drafted, qualifiers included, at the top of the review. The red team attacks the claim *as stated*, never a charitable paraphrase — any rewording needed to make it defensible is itself the finding and belongs in the verdict, not the setup.

### 2 — Walk all seven attack vectors

For each vector, decide whether it applies and write the attack in one sentence. Name vectors where nothing lands too: "no counter-example found after searching {sources}" is a result.

| Vector | The question it asks | Failure it exposes |
| --- | --- | --- |
| Definition | What do the terms mean? "Dominate" — revenue, deployments, mindshare? | Unfalsifiable wording |
| Baseline | Faster or better *than what*, measured when? | Undefined comparator |
| Selection | Which cases examined, which left out? | Cherry-picked evidence |
| Counter-example | What credible case breaks the claim? | Overreach |
| Mechanism | *Why* is it true — what carries it causally? | Correlation as cause |
| Base rate | How often are claims of this type right? | Inside-view optimism |
| Incentive | Who benefits if the reader believes it? | Motivated evidence |

### 3 — Score survival and severity

Count the vectors where no attack lands: one point each; the score runs 0–7. Grade each landed attack L/M/H: three low-severity hits are not three high-severity ones. Read the score: **7** ship as stated; **5–6** ship with the weak vectors hedged; **3–4** revise or downgrade the language; **0–2** retract and rewrite.

### 4 — Write the verdict and the hedged rewrite

Pick one verdict — ship, hedge, rewrite, retract — and for hedge or rewrite produce the exact replacement wording. A real hedge narrows the segment, adds a condition, or drops an indefensible number; it does not merely add "may". Show original and replacement side by side.

### 5 — Route the outcome

Retract or rewrite hands the claim to `abstain-or-escalate`. A hedged version replaces the headline everywhere the claim appears, not just the summary. Attacks hedged rather than fixed become stated limitations and, where they describe how a plan could fail, feed `premortem-analysis`.

## Output template

```
## Red-team review — {claim}

**Claim as drafted:** {verbatim}

| Vector | Applies? | Specific attack | Severity |
|---|---|---|---|
| Definition | {yes/no/partial} | {attack, or "none lands: …"} | {L/M/H} |
| Baseline | {yes/no/partial} | {…} | {L/M/H} |
| Selection | {yes/no/partial} | {…} | {L/M/H} |
| Counter-example | {yes/no/partial} | {…} | {L/M/H} |
| Mechanism | {yes/no/partial} | {…} | {L/M/H} |
| Base rate | {yes/no/partial} | {…} | {L/M/H} |
| Incentive | {yes/no/partial} | {…} | {L/M/H} |

**Survival score:** {N}/7 (high-severity hits: {n})
**Verdict:** {ship | hedge | rewrite | retract}
**Replacement wording:** > {the claim as it should now be published}
**Attacks still open at ship time:** {named, or none}
```

Every field is mandatory. A verdict without the table, or a hedge without replacement wording, is an opinion, not a red-team result.

## Worked example

Claim under review (illustrative; vendors and numbers invented) from a chip-market brief: *"The Helio-9 accelerator is 30 % faster than the market leader, so Helio will lead the enterprise inference segment by 2027."*

| Vector | Applies? | Specific attack | Severity |
| --- | --- | --- | --- |
| Definition | yes | "Lead the segment" is undefined — revenue, units shipped, or deployed capacity? | H |
| Baseline | yes | "30 % faster" cites Helio's own MLPerf 4.1 run against a 2024 part; the 2025 refresh closed the gap to about 8 % | H |
| Selection | yes | The 30 % holds on 2 of 7 MLPerf benchmark tasks; the other 5 are omitted | H |
| Counter-example | yes | Northwind Silicon shipped 3 of the 5 largest 2025 inference clusters with no throughput lead — throughput does not decide leadership | M |
| Mechanism | partial | The brief never says *how* speed converts to share; procurement runs 18–24 months and turns on software ecosystems | M |
| Base rate | yes | Of 14 "chip X will lead segment Y" predictions (invented reference class), 3 came true — a 20 % base rate at two years | M |
| Incentive | no | The analyst is independent; no vendor relationship disclosed or found | L |

Survival score: **1/7** (three high-severity hits). Verdict: **retract and rewrite** — its benchmark selection fails the baseline check, and the causal step from throughput to share is unstated. Replacement: *"On 2 of 7 MLPerf 4.1 tasks the Helio-9 leads the current market leader by about 8 %; whether that converts to enterprise inference share by 2027 depends on software-ecosystem maturity and 18–24-month procurement cycles, and comparable predictions have a roughly 20 % hit rate."* The open attacks — selection and mechanism — become stated limitations; the retracted original goes to `abstain-or-escalate`.

## Verification

- [ ] All seven vectors appear in the table, including those where nothing lands (a searched-and-found-none result, not a blank).
- [ ] Each landed attack cites something specific — a number, benchmark, competitor, base rate — not a general worry.
- [ ] The survival score equals the count of non-landing vectors; recount it against the table.
- [ ] Re-attack every hedged vector against the replacement wording; it counts as resolved only if the attack surface is gone (segment narrowed, condition stated, number dropped), not merely softened.
- [ ] Any attack still open at ship time is named in the verdict and carried into limitations.

## Pair with adjacent skills

- `steelman-argument` — build the opposing case at full strength first.
- `critique-report` — the whole-document audit; this is the adversarial pass on one claim.
- `key-assumptions-check` — surface the load-bearing premises first; attacks land hardest there.
- `grounded-fact-check` — verify the specifics a landed attack says are wrong.
- `abstain-or-escalate` — destination of a "retract" verdict.
- `premortem-analysis` — landed attacks become failure modes for the decision the claim supports.

## Anti-patterns

- Do **not** red-team charitably. The point is the attack the claim will actually face.
- Do **not** treat the document's own evidence as the adversary's; look for what it does not cite.
- Do **not** run this on every sentence; it is for headline claims and recommendations.
- Do **not** let an incentive attack substitute for an evidence attack; "the author sells consulting here" discounts a claim, it does not refute it.

## Reference

- U.S. Government, *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis*, 2009 — Devil's Advocacy (pp. 17–18), Red Team Analysis (pp. 31–33). https://www.cia.gov/resources/csi/static/955180a45afe3f5013772c313b16face/Tradecraft-Primer-apr09.pdf
- R. J. Heuer Jr. and R. H. Pherson, *Structured Analytic Techniques for Intelligence Analysis*, 2nd ed. CQ Press/SAGE, 2015 — challenge analysis. The 3rd ed. (R. H. Pherson and R. J. Heuer Jr., 2019, with Pherson as first author) drops Devil's Advocacy and Red Team Analysis, but not in favour of Structured Self-Critique and Premortem Analysis: those already sat beside them in the 2nd ed. It keeps Red Hat Analysis and folds challenge analysis into ch. 8, "Reframing Techniques".
- M. Zenko, *Red Team: How to Succeed by Thinking Like the Enemy*. Basic Books, 2015. ISBN 9780465073955 — red teaming as institutional practice, and how it fails when it reports to the people it audits.
- P. E. Tetlock and D. Gardner, *Superforecasting: The Art and Science of Prediction*. Crown, 2015. ISBN 9780804136693 — the outside view and base-rate reasoning behind that vector.
- P. E. Tetlock, *Expert Political Judgment: How Good Is It? How Can We Know?* Princeton University Press, 2005 — measured accuracy of confident expert predictions.
