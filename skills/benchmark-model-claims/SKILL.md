---
name: benchmark-model-claims
description: "Audits a claim about model or system performance against six integrity domains — test-set contamination, baseline pinning, seed and run variance, evaluator independence, metric selection, and whether the test set is large enough for the reported gap — and emits a 0–5 reliability score with named risk tags and a replication test. Use when a vendor post, paper or release note asserts a benchmark number: \"91% on GSM8K\", \"outperforms GPT-4o\", \"SOTA on MMLU\", \"audit this benchmark claim\". Not for grading a clinical or social-science trial (use `assess-study-bias`) and not for qualitative claims such as \"better reasoning\"."
license: MIT
metadata:
  category: quantitative
  method: Benchmark claim integrity audit (six-domain checklist)
  origin: Bespoke checklist; leakage and reporting evidence from Kapoor & Narayanan 2023 and Dodge et al. 2019
  version: "2.0.0"
---
# Benchmark Model Claims

A benchmark claim audit asks what would have to be true for a reported model score to mean what it appears to mean, and scores the claim on the six ways such numbers routinely fail. Its principle is that a leaderboard number is a measurement, not a verdict — reproducible only when the test data were unseen, the baseline was pinned, the run was repeated, the scorer was independent, the metric was fixed in advance and the test set was large enough to resolve the gap. This is a bespoke checklist, not a canonical published method; its load-bearing anchors are Kapoor and Narayanan's (2023) survey of leakage in machine-learning-based science and Dodge et al.'s (2019) demonstration that single-run scores without a reported search budget are not comparable. It prevents repeating a self-reported single-run win over a stale baseline as an established capability.

## When to invoke

Invoke when:

- A numerical model-quality claim is anchored to a named evaluation: "X % on HumanEval / MMLU / GSM8K / SWE-Bench", "beats state of the art", "leaderboard rank #N", "3× faster than {competitor}".
- A release note, vendor post or arXiv abstract is about to be summarised for a decision and the score is the load-bearing evidence.
- Two models are being compared and the comparison needs a reliability weight.

Do NOT invoke when:

- The study is a clinical, behavioural or field trial — `assess-study-bias` applies RoB 2 to randomized trials.
- The claim is qualitative ("more intuitive", "better reasoning") with no benchmark behind it — there is nothing to audit.
- The question is only whether the reported gap exceeds noise — `test-significance` answers that directly.
- The doubt is about the claim's own arithmetic — `quantitative-sanity-check`.
- The whole published literature on a capability is the subject — `systematic-review`.

## Procedure

### 1 — Normalise the claim

Rewrite the claim as `{model, pinned version} achieves {metric} = {value} on {benchmark, split} {comparator phrase}` and record the primary source (paper, DOI, arXiv ID, blog URL). If no benchmark or comparator is named, mark the claim **unstructured** and stop: it cannot be scored, only rejected. Record the model's training cutoff and the benchmark's release date now — the contamination domain depends on both.

### 2 — Score the six integrity domains

Score each domain Low risk / Some concerns / High risk with a one-sentence rationale citing what the source does or does not report. **D1 contamination** — was the test set plausibly in training data (cutoff versus benchmark release, decontamination report, held-out variant)? **D2 baseline pinning** — is the comparator an exact model ID with identical prompts and decoding? **D3 run variance** — averaged over three or more seeds with a spread and a disclosed tuning budget? **D4 evaluator independence** — did the model's builders produce the score? **D5 metric selection** — was the metric pre-specified, and are all canonical metrics reported? **D6 test-set size** — is n large enough that the gap exceeds sampling noise (compute it with `test-significance`)? Low-risk indicators and known traps: [references/domains-and-tags.md](references/domains-and-tags.md).

### 3 — Compute the reliability score and emit risk tags

Start from 5 and subtract 1 per High-risk domain and 0.5 per Some concerns: `reliability = max(0, 5 − 1×count(High) − 0.5×count(Some concerns))`. A 5 clears all six domains; a 0 means the claim carries no evidential weight. Attach a named tag for each non-Low domain from the fixed vocabulary in the reference file — `contamination-unverified`, `baseline-version-drift`, `single-seed`, `budget-unreported`, `self-evaluated`, `metric-cherry-picked`, `n-too-small` and their siblings — so the audit is machine-readable and every tag maps back to one domain.

### 4 — Separate what the claim supports from what it does not

The score is not the deliverable; the split is. State the weaker claim the evidence does support ("competitive with 2024-era frontier models on grade-school math"), then the claim it does not ("outperforms {competitor}", "state of the art") and the domain that kills it. A High-risk contamination or baseline domain invalidates a comparative ranking even when the other five are clean — never average a red domain into a "mixed" verdict.

### 5 — Name the replication that would raise the score

Specify the experiment that moves each non-Low domain to Low: which decontaminated or held-out variant, how many seeds with what spread, which pinned baseline version and decoding settings, which independent harness, and what test-set size the claimed delta needs. This turns the audit into a request the claimant can satisfy, and makes the score falsifiable rather than an opinion.

## Output template

```
## Benchmark claim audit — {claim}

**Normal form:** {model, version} {metric} = {value} on {benchmark, split} vs {comparator, version}
**Primary source:** {URL / DOI / arXiv ID}   **Training cutoff:** {date}   **Benchmark released:** {date}

| Domain | Judgement | Rationale |
|---|---|---|
| D1. Test-set contamination | {Low / Some concerns / High} | {one sentence} |
| D2. Baseline pinning | {…} | {…} |
| D3. Seed / run variance | {…} | {…} |
| D4. Evaluator independence | {…} | {…} |
| D5. Metric selection | {…} | {…} |
| D6. Test-set size vs the gap | {…} | {…} |

**Reliability score:** {0–5} = 5 − 1×{n High} − 0.5×{n Some concerns}
**Risk tags:** [{tag}, {tag}, …]
**Supports:** {the weaker claim the evidence sustains}
**Does NOT support:** {the claim invalidated, and the domain that kills it}
**Replication that would raise the score:** {specific experiment per non-Low domain}
```

Mandatory fields: all six domain rows, the arithmetic behind the reliability score, the risk tags, and both the supports and does-not-support lines. A score without the supports/does-not-support split must not ship.

## Worked example (illustrative)

Claim under audit, entirely invented: *"AcmeLM-2 scores 91.2 % on GSM8K, outperforming GPT-4o."* The source is a vendor blog post with no paper and no DOI; it reports one run, cites a GPT-4o number published in 2024, and gives accuracy only.

| Domain | Judgement | Rationale |
|---|---|---|
| D1. Test-set contamination | Some concerns | GSM8K has been scraped since 2021 and the post includes no decontamination report or held-out variant |
| D2. Baseline pinning | High | Compares against a 2024 GPT-4o figure, not a pinned current model ID with matched prompts and decoding |
| D3. Seed / run variance | High | A single run, no spread, no tuning budget reported |
| D4. Evaluator independence | Low | Public benchmark run with the standard harness, named in the post |
| D5. Metric selection | Some concerns | Accuracy only — pass@1 against competitors' majority-vote numbers, no cost or latency |
| D6. Test-set size vs the gap | Low | GSM8K test n = 1,319, adequate for the claimed several-point delta |

**Reliability score:** 5 − 1×2 − 0.5×2 = **2 / 5**. **Risk tags:** [`contamination-unverified`, `baseline-version-drift`, `single-seed`, `budget-unreported`, `metric-cherry-picked`]. **Supports:** "AcmeLM-2 is competitive with 2024-era frontier models on grade-school math." **Does NOT support:** "outperforms GPT-4o" or any state-of-the-art framing — D2 alone invalidates the ranking. **Replication:** rerun on GSM8K and a symbolic variant with the standard harness, 5 seeds with mean ± std and a disclosed budget, against the currently pinned GPT-4o at matched temperature.

## Verification

Before the audit ships, confirm:

- [ ] The normal form names the benchmark split and both model versions; unstructured claims were rejected rather than scored.
- [ ] The training cutoff and benchmark release date are both recorded, and D1's judgement follows from them.
- [ ] Recompute the reliability score from the domain counts: `5 − 1×High − 0.5×Some concerns`, and check it against the tags.
- [ ] D6 was decided with an actual significance calculation via `test-significance`, not by eye.
- [ ] Every non-Low domain has a tag from the fixed vocabulary, and every tag maps to a domain.
- [ ] The does-not-support line names the specific domain that invalidates the claim.

## Pair with adjacent skills

- `assess-study-bias` — the RoB 2 sibling for randomized trials; this skill is its ML-benchmark counterpart.
- `test-significance` — computes D6: whether the reported delta exceeds noise at the test-set size.
- `quantitative-sanity-check` — recompute the claim's own arithmetic before auditing its methodology.
- `grounded-fact-check` — verify the load-bearing numbers the audit surfaces against the primary source.
- `abstain-or-escalate` — the hand-off when the audit ends in "unsupported" and the claim is load-bearing.

## Anti-patterns

- Do **not** treat a leaderboard rank as evidence of quality. The leaderboard is a measurement, not a verdict.
- Do **not** skip the contamination check for a model released after the benchmark; a training cutoff is not self-documenting.
- Do **not** average a High D1 with a Low D2 into a "mixed" verdict. One critical red kills the comparative claim.
- Do **not** accept a single-run number as comparable to a tuned or averaged one — report the spread or mark it `single-seed`.
- Do **not** apply this checklist to clinical or field studies; its domains are calibrated to model evaluation.

## Reference

- S. Kapoor and A. Narayanan, "Leakage and the reproducibility crisis in machine-learning-based science," *Patterns*, vol. 4, no. 9, art. 100804, 2023. doi:10.1016/j.patter.2023.100804 — the taxonomy of leakage behind D1.
- J. Dodge, S. Gururangan, D. Card, R. Schwartz, and N. A. Smith, "Show Your Work: Improved Reporting of Experimental Results," in *Proc. EMNLP-IJCNLP*, Hong Kong, 2019, pp. 2185–2194. arXiv:1909.03004 — why single-run scores without a search budget are not comparable (D3, D5).
- P. Liang et al., "Holistic Evaluation of Language Models," *Transactions on Machine Learning Research*, 2023. arXiv:2211.09110 — multi-metric, independently run evaluation (D4, D5).
- X. Bouthillier et al., "Accounting for Variance in Machine Learning Benchmarks," in *Proc. MLSys*, 2021. arXiv:2103.03098 — variance sources and how many runs are needed (D3, D6).
