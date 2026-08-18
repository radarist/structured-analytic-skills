# Integrity domains, risk tags and contamination traps

Companion to `../SKILL.md`.

## The six domains

| Domain | Question | Low-risk indicator |
|---|---|---|
| **D1. Test-set contamination** | Was the test set plausibly inside the model's training data? | Training cutoff precedes the benchmark's release; or a decontamination report; or canary strings checked; or a held-out / regenerated variant used (Kapoor & Narayanan, 2023). |
| **D2. Baseline pinning** | Is the comparator fixed to an exact version, prompt and decoding configuration? | Exact model ID (e.g. `gpt-4o-2024-08-06`), identical prompt templates, identical temperature/top-p, evaluated in the same harness run. |
| **D3. Seed / run variance** | Was the number averaged over repeated runs, with the spread and tuning budget disclosed? | Mean ± std over ≥ 3 seeds, and the hyperparameter search budget reported (Dodge et al., 2019; Reimers & Gurevych, 2017; Bouthillier et al., 2021). |
| **D4. Evaluator independence** | Did the team that built the model produce the score? | A third-party leaderboard or an independent harness run by disjoint authors (Liang et al., 2023). |
| **D5. Metric selection** | Was the metric fixed before the results were seen? | A pre-registered evaluation plan, or all canonical metrics reported rather than only the favourable one. |
| **D6. Test-set size vs the gap** | Is n large enough that the claimed delta exceeds sampling noise? | The 95 % interval on the difference excludes zero — computed with `test-significance`, not eyeballed. |

## Scoring

```
reliability = max(0, 5 − 1 × count(High risk) − 0.5 × count(Some concerns))
```

5 = all six domains clear. 0 = the claim carries no evidential weight. A High judgement in D1 or D2 invalidates a *comparative* ranking regardless of the total.

## Risk-tag vocabulary

| Domain | Tags |
|---|---|
| D1 | `contamination-unverified`, `contamination-likely` |
| D2 | `baseline-unpinned`, `baseline-version-drift` |
| D3 | `single-seed`, `seed-unreported`, `budget-unreported` |
| D4 | `self-evaluated`, `conflict-of-interest` |
| D5 | `metric-cherry-picked`, `metric-selected-post-hoc` |
| D6 | `n-too-small`, `underpowered-delta` |

Every non-Low domain gets at least one tag; every tag maps back to exactly one domain.

## Known contamination traps

- **HumanEval** — solutions have been scraped and memorised since 2022; prefer the EvalPlus / HumanEval+ extended test suite (Liu et al., 2023, arXiv:2305.01210).
- **MMLU** — items have leaked to web mirrors; require a held-out or regenerated variant.
- **GSM8K** — documented contamination; symbolic-template variants such as GSM-Symbolic (Mirzadeh et al., 2024, arXiv:2410.05229) expose pattern-matching behind high scores.
- **Vendor-run leaderboards** — treat D4 as High unless an independent re-evaluation exists.

## References

- S. Kapoor and A. Narayanan, *Patterns* 4(9):100804, 2023. doi:10.1016/j.patter.2023.100804
- J. Dodge et al., *Proc. EMNLP-IJCNLP* 2019, pp. 2185–2194. arXiv:1909.03004
- N. Reimers and I. Gurevych, *Proc. EMNLP* 2017, pp. 338–348
- X. Bouthillier et al., *Proc. MLSys* 2021. arXiv:2103.03098
- P. Liang et al., *TMLR* 2023. arXiv:2211.09110
