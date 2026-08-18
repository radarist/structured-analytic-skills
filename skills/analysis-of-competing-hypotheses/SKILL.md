---
name: analysis-of-competing-hypotheses
description: "Ranks rival explanations of a question by which one the evidence contradicts least (Heuer's Analysis of Competing Hypotheses — ACH — CIA), then names the single piece of evidence the ranking hinges on. Use when a question has two or more plausible explanations and confirmation bias would be costly — \"why is adoption stalling?\", \"is this signal real or just noise?\", \"which of these causes explains the drop?\", or before a headline conclusion ships. Not for factual single-answer questions (use `grounded-answer`) or when only one hypothesis exists."
license: MIT
metadata:
  category: decision-strategy
  method: Analysis of Competing Hypotheses (ACH)
  origin: Richards J. Heuer Jr., CIA — developed in the late 1970s, collected in Psychology of Intelligence Analysis, 1999
  version: "2.0.0"
---
# Analysis of Competing Hypotheses (ACH)

Confirmation bias — reading evidence as support for the explanation you already favour — is the most robust failure mode of open-source analysis. ACH, developed by Richards J. Heuer Jr. at the CIA — its chapters were written as internal articles during 1978–86 and collected in *Psychology of Intelligence Analysis* in 1999, which is a publication date, not the method's origin — is the standard antidote: lay every plausible hypothesis side by side, grade each evidence item against each, and prefer the one with the **fewest inconsistencies**, not most confirmations.

## When to invoke

Invoke when:

- A question has 2+ plausible answers and real stakes: "why is adoption of X stalling?", "is Y about to pivot?", "is this signal genuine or noise?".
- Before an executive summary's headline conclusion or "most likely" recommendation ships.
- A surprising finding has several explanations and you are about to report one.

Do NOT invoke when:

- The question is factual with one right answer — use `grounded-answer`.
- Only one hypothesis is on the table — ACH on one is theatre; generate alternatives with `decompose-research-question` or `key-assumptions-check`.
- The stakes are low (a status check, internal summary). ACH costs time; reserve it for consequential claims.

## Procedure — Heuer's eight steps

### 1 — Enumerate hypotheses

Write down every plausible answer; aim for 3–7. Include the obvious one (often right, always the anchor to disconfirm), at least one you believe wrong (so the matrix visibly rejects real evidence, not just absent evidence), a null hypothesis ("nothing is happening — noise"), and variants differing in *cause* ("competitors accelerated" vs "we slowed" vs "market shrank"). Do not drop unlikely hypotheses; the method only works on the full space.

### 2 — List evidence and arguments

Collect every observation, number, quote, or argument bearing on the question. Be over-inclusive. Include direct evidence, the **absence** of expected evidence ("if X were true, Y should exist; Y does not"), contradictions, and base rates. Grade each item's source with `rate-source-admiralty` — step 6's sensitivity check needs it.

### 3 — Build the matrix

Rows are evidence, columns are hypotheses. Grade each cell in isolation — "if this hypothesis were true, would this evidence surprise me?" — without consulting the rest of the matrix:

| Mark   | Meaning |
| ------ | ------- |
| **CC / C** | Strongly / consistent — expected if the hypothesis were true |
| **N**  | Neutral — as likely under this hypothesis as any other |
| **I / II** | Inconsistent / strongly inconsistent — unexpected if the hypothesis were true |
| **NA** | Not applicable — evidence does not bear on this hypothesis |

Heuer (1999) marks cells "C, I, and N/A standing for consistent, inconsistent, or not applicable"; the five-level CC/C/N/I/II scale and the 1-point/2-point weighting in step 5 are the Heuer and Pherson refinement (*Structured Analytic Techniques*), not Heuer 1999.

### 4 — Refine

Rows marked C everywhere, or N/NA everywhere, discriminate nothing — drop them. Keep the **diagnostic** rows (C on some hypotheses, I on others). The final matrix should be mostly diagnostic rows.

### 5 — Score

Per hypothesis, count the I marks (II counts double; weight rows by source credibility × relevance). **Fewest inconsistencies wins.** Do not count C's — "most consistencies" rewards exactly the bias ACH exists to remove. Break ties by which inconsistencies are most damaging.

### 6 — Sensitivity check

For the top two or three hypotheses ask: which single piece of evidence, if retracted, flips the ranking? If that pivotal item comes from a C/D-grade source, re-source it or mark the conclusion tentative.

### 7 — Report

Fill the output template below: ranking with inconsistency counts, most-diagnostic evidence, sensitivity statement, and leftover uncertainty. This skill adds a loose-ends pass here: name every item inconsistent with the winning hypothesis and say why the hypothesis survives it. If the loose ends are many, the winner is wrong — go back to step 1.

### 8 — Identify milestones for future observation

Heuer's eighth step, verbatim: "Identify milestones for future observation that may indicate events are taking a different course than expected." Put two or three dated observable milestones — one confirming the winning hypothesis, one favouring a rival — in the output. Hand a longer list to `indicators-validation` for diagnosticity testing.

## Output template

```
## ACH result — {question}

**Ranking (fewest inconsistencies first):**
1. {Hn} {label} — weighted-I {w.ww} · raw-I {n}
2. {Hn} {label} — weighted-I {w.ww} · raw-I {n}
3. {Hn} {label} — weighted-I {w.ww} · raw-I {n}

**Most-diagnostic evidence:** {E_x} — {how its marks separate the top two hypotheses}

**Sensitivity:** if {E_x} were retracted, the ranking flips to {Hn}. {E_x} source grade: {A1–F6} — {re-sourced | load-bearing, conclusion tentative}.

**Loose ends:** {evidence inconsistent with the winner, and why it survives}

**Milestones for future observation:** {dated observable that would confirm the winner}; {dated observable that would favour a rival}

**Leftover uncertainty:** {Hn} not ruled out — disconfirming it would take {specific evidence to seek}.
```

Every field is mandatory. A result without the sensitivity line is a guess, not a conclusion.

## Worked example

Question: *why did Q4 revenue for a platform fall 8 % year-on-year?* Four hypotheses (H1 adoption slowing, H2 pivot to a new segment, H3 market shrank, H4 noise) and five evidence rows weighted by source credibility × relevance; case file `examples/adoption-stall.json`. Running `python3 scripts/ach.py score --file examples/adoption-stall.json` prints:

```
Evidence                                            W     H1     H2     H3     H4  Diag
E1 Q4 revenue -8% YoY (10-Q, A1)                 1.00      C      C      C      I     2
E2 No new logos in the roadmap-aligned ICP ...   0.81      C      N      I      I     2
E3 CEO on earnings call: 'we are re-evaluat...   0.80      I     CC      N      N     3
E4 Headcount flat; no reorg announced (Link...   0.42      C      I      C      C     2
E5 Two competitors reported +15% growth in ...   0.72      C      N     II      I     3
Weighted inconsistency                                  0.80   0.42   2.25   2.53
Raw I count (I=1, II=2)                                    1      1      3      3

Ranking (fewest weighted inconsistencies = leading hypothesis, per Heuer):
  1. H2  Company is pivoting to a different segment  weighted-I  0.42   raw-I 1
  2. H1  Adoption is genuinely slowing               weighted-I  0.80   raw-I 1
```

`diagnosticity` reports E3 and E5 as the most diagnostic rows (spread 3). H1 and H2 tie on raw inconsistencies; the weights break the tie for H2 *because* E3 (the CEO quote) is strongly consistent with a pivot and inconsistent with slowing adoption. So the sensitivity line reads: "if E3 were retracted, the ranking flips to H1; E3 is an A2 transcript quote — verified, conclusion holds." H3 and H4 carry three inconsistencies each — effectively ruled out.

## Verification

Before shipping, confirm:

- [ ] Every hypothesis has a mark in every row (no blank cells; NA is a mark).
- [ ] At least one row is diagnostic (spread ≥ 2); uniform-mark rows were dropped or justified.
- [ ] The winner has the **fewest** weighted inconsistencies — recompute column totals by hand or with `scripts/ach.py score`.
- [ ] The pivotal evidence in the sensitivity line really flips the ranking when removed (delete the row and re-score).
- [ ] The pivotal evidence carries a source grade; any C/D-grade pivot is flagged as tentative.
- [ ] Loose ends are listed, not silently dropped, and step 8's milestones are dated and observable.

## Companion tool

`scripts/ach.py` scores the matrix (steps 4–5) from a JSON case file — weighted inconsistency totals ranked fewest-first, the matrix as a text table, and per-row diagnosticity flagging rows that cannot discriminate. Stdlib only.

```bash
python3 scripts/ach.py score --file case.json          # matrix + ranked hypotheses
python3 scripts/ach.py diagnosticity --file case.json  # per-row diagnosticity + flags
python3 scripts/ach.py --selftest                      # built-in worked example, self-verifying
```

The skill works without it — count I's per column by hand; the tool only removes arithmetic slips on larger matrices.

## Pair with adjacent skills

- `grounded-answer` — factual single-answer questions route there; ACH is for interpretive, multi-hypothesis questions.
- `rate-source-admiralty` — grade pivotal evidence before the sensitivity check trusts it.
- `key-assumptions-check` — surface load-bearing premises inside each hypothesis.
- `bayesian-update` — quantify the leading pair after ACH narrows the field.
- `red-team-claim` — adversarial pass on the winner before it ships.
- Methodology counterpart: [methodologies/scientific-methods/hypothetico-deductive-method.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/scientific-methods/hypothetico-deductive-method.md) — the severe-testing tradition ACH operationalises.

## Anti-patterns

- Do **not** skip hypotheses you "know" are wrong — the matrix must visibly reject them.
- Do **not** grade a cell by looking at other cells. Grade it in isolation.
- Do **not** report "H1 wins because most C's". Report "H1 wins with fewest I's". The mental model matters.
- Do **not** use ACH for factual lookups. It serves interpretive questions with several plausible causes.
- Do **not** present the conclusion without the sensitivity check. A conclusion that flips on one item is a guess.

## Reference

- R. J. Heuer Jr., *Psychology of Intelligence Analysis*. Washington, DC: Center for the Study of Intelligence, Central Intelligence Agency, 1999, ch. 8 "Analysis of Competing Hypotheses". https://www.cia.gov/resources/csi/books-monographs/psychology-of-intelligence-analysis-2/
- R. J. Heuer Jr. and R. H. Pherson, *Structured Analytic Techniques for Intelligence Analysis*, 3rd ed. Thousand Oaks, CA: CQ Press / SAGE, 2019 (2nd ed. 2014), ch. 7 — diagnostic and contrarian ACH variants.
- U.S. Government, *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis*, 2009, pp. 14–16 — the one-page ACH procedure used across the intelligence community.
