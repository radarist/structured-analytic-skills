---
name: delphi-method
description: "Aggregates independent expert judgments into a consensus estimate — or an honest map of where experts split — with the RAND Delphi method: anonymous panel, iterated rounds, controlled feedback of the group median and interquartile range, and a stability stopping rule. Use when data alone cannot answer and structured expert judgment is needed — \"run a Delphi study\", \"expert consensus forecast on X\", \"when will X happen, according to the experts?\", \"expert elicitation of a date or probability\". Not for a single reasoner's dated forecast — use `foresight`; not for branching futures — use `scenario-planning`; not for scoring forecasts afterwards — use `brier-score-calibration`."
license: MIT
metadata:
  category: decision-strategy
  method: Delphi method (anonymous iterated expert elicitation with controlled feedback)
  origin: Norman Dalkey and Olaf Helmer, RAND Corporation, 1963
  version: "2.0.0"
---
# Delphi Method

A panel of experts answers a scoped question independently; between rounds each sees the anonymised group distribution and the outliers' reasoning, then revises. The range tightens — and when it does not, the disagreement is the finding. Norman Dalkey and Olaf Helmer developed the method at RAND, publishing the first controlled experiment in 1963; Linstone and Turoff's 1975 volume remains the reference text. The failure it prevents is the committee estimate, where the senior voice sets the number and everyone else converges on it.

## When to invoke

Invoke when:

- No dataset can settle the question and judgment is the best evidence available: "when will X mature, according to the field?", "expert consensus on Y", "panel forecast".
- Qualified people disagree and seniority, not argument, is deciding the answer.
- The spread of expert opinion is itself the deliverable — where the field splits, and why.

Do NOT invoke when:

- One reasoner should produce a dated, falsifiable prediction — use `foresight`.
- The question branches into plausible futures — use `scenario-planning`; Delphi converges, scenarios diverge.
- Public data can answer it — `estimate-market-size` or `reference-class-forecasting` is cheaper.
- One expert with a trusted track record can answer it; averaging adds nothing.
- Forcing consensus would manufacture agreement on a contested policy question — use the Policy Delphi ([references/variants-and-evidence.md](references/variants-and-evidence.md)).
- The forecast has resolved and accuracy is the question — use `brier-score-calibration`.

## Procedure

### 1 — Frame one scoped question

Delphi fails on vague prompts. The question must resolve to a scalar with a unit and a date — not "the future of quantum computing" but "the year a fault-tolerant quantum computer first demonstrates commercial advantage on a logistics-optimization workload". Define what counts as the event before the panel sees it. If it cannot be stated as a year, probability or percentage, decompose it first with `decompose-research-question`.

### 2 — Define the panel

Select for track record on this question, not title or seniority. Aim for 7–30 panelists: below seven the median is noisy, above thirty attrition dominates. Keep the panel heterogeneous — at least one genuine skeptic and one practitioner, from more than one school of thought — and record each credential for the facilitator only.

### 3 — Round 1: elicit independently

Each panelist privately submits an estimate, a rationale of one to three sentences and a self-rated confidence. The self-rating is recorded but never used to weight answers: it tracks overconfidence more than accuracy, so arguments are weighted on merit. Round 1 must be blind — if panelists see each other's answers first, the result is groupthink.

### 4 — Aggregate and feed back, anonymously

The facilitator computes the median and interquartile range and returns to every panelist: the median, the Q1–Q3 spread, their own position marked against it, and the anonymised rationales — especially from panelists outside the IQR. Outlier reasoning is the highest-value content in a Delphi, and a well-argued minority view can move the median. Never reveal names or employers.

### 5 — Rounds 2–3: revise

Each panelist revises after seeing the distribution and rationales: moving toward the median, holding and strengthening a rationale, or moving further out if a round-1 argument revealed something new. Run two to four rounds and stop on **stability** — the median has settled and fewer than 15 % of panelists changed — not on unanimity.

### 6 — Read the result: consensus or mapped dissent

A narrow IQR with a stable median gives a panel estimate: report the median with the IQR as its uncertainty band. A persistent two-camp split must **not** be averaged — the mean of two peaks is a value no expert holds; report both positions and hand them to `scenario-planning`. A wide unimodal distribution is deep uncertainty: report the median, the range and low confidence.

## Output template

```
## Delphi panel — {question}

Question (scoped): {event definition + unit + date}
Panel: {N} experts — {anonymised composition, e.g. "4 academic, 3 industry, 2 regulators"}
Rounds run: {n} (stopped: {reason, e.g. "12.5% changed in round 3, below the 15% level"})

Result: {consensus | persistent split | wide uncertainty}
Central estimate (median): {value}
Spread (Q1–Q3): {range}   Full range (min–max): {range}

Dominant reasoning: {2–3 sentences on the arguments that moved the median}
Minority / dissenting view: {the best-argued outlier position, in its own terms}
Confidence: {low | medium | high} — {why}
```

Every field is mandatory. A report omitting the spread, the stopping reason or the dissenting view is a poll dressed up as a method.

## Worked example

Illustrative panel of eight experts on the question above (data illustrative). Arithmetic from `python3 scripts/delphi.py aggregate --file examples/round1.json`:

```
Item: fault-tolerant advantage year
  n=8  median=2035.5  Q1=2034  Q3=2040  IQR=6  min=2031  max=2055
  Outliers (outside the IQR):
    E1: 2031 — "error-correction overhead falling faster than roadmaps assume"
    E2: 2033 — "steady qubit scaling, no new physics needed"
    E7: 2042 — "materials yield has slipped every roadmap since 2019"
    E8: 2055 — "no credible path to logical-qubit counts at this cost"
```

After the rationales are fed back, `stability --round1 examples/round1.json --round2 examples/round2.json` reports `changed: 3/8 (37.5%)  verdict: MOVING`, so a third round runs; round 3 gives `changed: 1/8 (12.5%) verdict: STABLE`, `median=2035.5 Q1=2034.5 Q3=2038.5 IQR=4`. The IQR narrowed from 6 to 4 while the median never moved: convergence came from the wings.

| Round | Median | Q1–Q3 | IQR | Changed | Verdict |
| --- | --- | --- | --- | --- | --- |
| 1 | 2035.5 | 2034–2040 | 6 | — | — |
| 2 | 2035.5 | 2034.5–2039 | 4.5 | 3/8 (37.5 %) | MOVING |
| 3 | 2035.5 | 2034.5–2038.5 | 4 | 1/8 (12.5 %) | STABLE |


The report gives 2035–2036 as the estimate with a 2034.5–2038.5 band and records E8's dissent verbatim: the logical-qubit cost argument went unanswered, so the 2055 position is preserved, not averaged away.

## Verification

Before the panel result ships, confirm:

- [ ] The question resolves to one scalar, with the event definition fixed before round 1.
- [ ] Round 1 was blind; no identity, employer or seniority appeared in a feedback packet.
- [ ] Median, Q1, Q3 and the stopping percentage are recomputed with `scripts/delphi.py` and match.
- [ ] The stopping reason is stability, not unanimity, and names the round it was reached.
- [ ] A bimodal distribution is reported as a split, never as an average.
- [ ] At least one dissenting rationale appears in the dissenter's own terms.
- [ ] Self-rated confidence was recorded but not used to weight any estimate.

## Companion tool

`scripts/delphi.py` (standard library only, Python 3.9+) does the facilitator's arithmetic: per item, n, median, IQR, min/max and the estimates outside the IQR with their rationales; across two rounds, the share who changed, the median shift and a STABLE/MOVING verdict at the 15 % level; and Kendall's W for rankings. Round files are JSON — `{"items": {"item": [{"panelist": "E1", "estimate": 2035, "rationale": "…"}]}}` — or a flat `{"responses": [...]}`; rankings are `{"rankings": {"E1": ["best", …, "worst"]}}`.

```bash
python3 scripts/delphi.py aggregate --file examples/round1.json   # median, IQR, outliers
python3 scripts/delphi.py stability --round1 examples/round2.json --round2 examples/round3.json
python3 scripts/delphi.py kendall --file rankings.json           # Kendall's W
python3 scripts/delphi.py --selftest                             # hand-verified checks
```

The 15 % level comes from Scheibe, Skutsch and Schofer (1975), who defined it on the change in the response *distribution*; the script applies it to the share of panelists who revise — an approximation, discussed in [references/variants-and-evidence.md](references/variants-and-evidence.md). The skill works without the tool.

## Pair with adjacent skills

- `foresight` — package the panel's date as one dated prediction with accelerants and kill-signals.
- `scenario-planning` — when the panel splits, hand the two camps over as branches.
- `key-assumptions-check` — surface the premises the panel shares before trusting the median.
- `brier-score-calibration` — score the panel's dated estimate once it resolves.
- `decompose-research-question` — break up a question that will not reduce to one scalar.
- Methodology counterpart: [methodologies/foresight/delphi-method.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/delphi-method.md) — history, variants and multi-agent panel design.

## Anti-patterns

- Do **not** reveal panelist identities between rounds; a name on a number restores deference bias.
- Do **not** weight estimates by self-rated expertise — it tracks overconfidence, not accuracy.
- Do **not** force consensus, or average a bimodal distribution into a value no expert holds.
- Do **not** run Delphi where one trusted expert or a public dataset would answer better.
- Do **not** collect bare numbers: without rationales a Delphi is a poll and outliers cannot move it.
- Do **not** treat the median as fact — Rowe and Wright find the advantage real but modest.

## Reference

- N. Dalkey and O. Helmer, "An Experimental Application of the Delphi Method to the Use of Experts," *Management Science*, vol. 9, no. 3, pp. 458–467, 1963. doi:10.1287/mnsc.9.3.458 — the founding RAND experiment.
- T. J. Gordon and O. Helmer, *Report on a Long-Range Forecasting Study*. Santa Monica, CA: RAND Corporation, P-2982, 1964. https://www.rand.org/pubs/papers/P2982.html — the first large technology forecast.
- H. A. Linstone and M. Turoff (eds.), *The Delphi Method: Techniques and Applications*. Reading, MA: Addison-Wesley, 1975. ISBN 978-0-201-04294-8 — the reference volume, including Turoff's "The Policy Delphi".
- M. Scheibe, M. Skutsch and J. Schofer, "Experiments in Delphi Methodology," in Linstone & Turoff (1975), pp. 262–287 — the 15 % stability criterion used as the stopping rule.
- G. Rowe and G. Wright, "The Delphi technique as a forecasting tool: issues and analysis," *International Journal of Forecasting*, vol. 15, no. 4, pp. 353–375, 1999. doi:10.1016/S0169-2070(99)00018-7 — critical review of what the evidence supports.
