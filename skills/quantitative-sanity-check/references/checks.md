# Check catalogue — formulas, traps and tolerances

Companion to `../SKILL.md`. Each check is one line of arithmetic; the tolerances are the ones `scripts/sanity.py` applies.

## Compounding / CAGR

```
end          = start × (1 + CAGR)^years
implied CAGR = (end / start)^(1/years) − 1
growth multiple = end / start
```

- Compounding periods = end year − start year (2024→2032 is 8 periods, not 9).
- Simple-vs-compound: "25 %/yr for 8 years" is 1.25^8 = 5.96×, not 3.0×.
- "Doubling every N years" implies CAGR = 2^(1/N) − 1 (every 3 years → 26.0 %/yr, not 33 %).
- Tolerance: implied vs claimed CAGR within ±0.2 percentage points is consistent (tool default).

## Unit economics

```
implied revenue      = customers × price per period × periods per year
implied contribution = (price − unit cost) × volume
```

- Tolerance: reproduces within ±20 % (pricing tiers, churn timing, currency). Beyond that, the source must explain the gap (enterprise tier dominates revenue; free seats counted as customers; annual vs monthly price).
- For a revenue triple, run `unit-econ` with the *annual* price and `--cost 0`.

## Percentage vs percentage-point

| Baseline | "improved 5 %" read as relative | read as percentage points |
|---|---|---|
| 10 % | 10.5 % (×1.05) | 15 % (+5 pp) |
| 40 % | 42 % | 45 % |

- Both readings must be shown when only the delta is given; the claim is **ambiguous**.
- Reverse trap: "share fell 50 % to 20 %" — from 40 % (relative) or from 70 % (points).
- Style convention: state absolute changes in percentage points and relative changes as percent (Miller, 2015, ch. 5–6; Huff, 1954).

## Survivorship and base rate

- Survivorship: "90 % of unicorns pivoted early" needs the denominator "what fraction of all early pivoters became unicorns". Sampling only winners → tag `survivorship-biased`, treat as anecdote (Wald, 1943; Mangel & Samaniego, 1984).
- Base rate / positive predictive value:

```
PPV = (sens × prev) / (sens × prev + (1 − spec) × (1 − prev))
```

  sens 0.99, spec 0.95, prev 0.01 → 0.0099 / (0.0099 + 0.0495) = 0.1667 — five of six positives are false, so "99 % accurate" is not the operative number.

## Fermi decomposition

```
quantity ≈ population × participation rate × frequency × unit value
```

- Round each factor to the nearest half-order of magnitude (1, 3, 10, 30, 100 …).
- Within ~3× of the claim: plausible. 10× or more apart: implausible-as-stated; name the likely conflation (e.g. tool spend vs total productivity value).
- Example: "US developers spend $50B/yr on AI coding tools" vs ~4M developers × ~50 % adoption × ~$300/yr ≈ $0.6B — an ~80× gap.

## Verdict vocabulary

- **consistent** — reproduces within tolerance.
- **inconsistent** — the source's own numbers contradict each other (show the recomputation).
- **ambiguous** — two readings possible (show both).
- **unverifiable** — no linked numbers to check against.
