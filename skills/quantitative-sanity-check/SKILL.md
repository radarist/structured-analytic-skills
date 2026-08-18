---
name: quantitative-sanity-check
description: "Recomputes the arithmetic that a document's own numbers imply — CAGR and compounding, price × volume unit economics, percentage vs percentage-point change, share-of-whole, survivorship and base-rate framing, Fermi order-of-magnitude — and flags every claim whose figures do not reproduce each other. Use when a report, pitch or press release states linked numbers — \"$6B growing to $50B at a 25% CAGR\", \"40,000 customers at $99 a month is $120M ARR\", \"conversion improved 5%\", \"run a quantitative sanity check on these figures\". Internal consistency only — not for checking a lone figure against outside sources (use `grounded-fact-check`) or sizing a market (use `estimate-market-size`)."
license: MIT
metadata:
  category: quantitative
  method: Quantitative sanity check (internal-consistency arithmetic checklist)
  origin: Bespoke checklist built on textbook conventions — Huff 1954; Wald 1943 via Mangel & Samaniego 1984; Miller 2015
  version: "2.0.0"
---
# Quantitative Sanity Check

A quantitative sanity check recomputes, from a source's own figures, the numbers those figures imply — before anyone trusts, repeats or fact-checks them. Its principle is over-determination: start, end, period and growth rate fix each other; price, customers and revenue must multiply through. It is a bespoke checklist rather than one published method; each check applies a textbook convention — percentage versus percentage-point change (Huff, 1954; Miller, 2015), survivorship bias (Wald, 1943, via Mangel & Samaniego, 1984), base-rate neglect (Kahneman, 2011) and Fermi decomposition. It prevents repeating a headline number its own companions contradict.

## When to invoke

Invoke when:

- A document states two or more numbers that imply a third: "grows from $A to $B by {year} at X% CAGR", "{N} customers at ${P}/month generate ${R}".
- A change is reported without units — "improved 5%", "up 12 points" — and could be read either way.
- A "{X}% of successful {companies} did Y" statistic is about to be quoted, or a bare headline figure has a decomposable structure.

Do NOT invoke when:

- The claim is a single isolated number with nothing to check it against — `grounded-fact-check` verifies it externally.
- The question is whether a measured gap is real or noise — `test-significance`.
- The job is building a market estimate from scratch — `estimate-market-size`.
- The doubt is about a study's design, not its arithmetic — `assess-study-bias`.

## Procedure

Formulas, traps and tolerances: [references/checks.md](references/checks.md).

### 1 — Inventory the linked numbers

List every quantitative claim and mark the ones that are **linked** — presented as arithmetically related (start + end + rate; price + volume + total; share before + after + change; sensitivity + prevalence + "accuracy"). Only linked sets are checkable here; isolated figures need external verification. Record each claim verbatim; the verdict quotes it.

### 2 — Recompute compounding and CAGR

A (start, end, years, CAGR) quadruple is over-determined: recompute one member from the other three with `end = start × (1 + CAGR)^years` and `implied CAGR = (end/start)^(1/years) − 1`. Compounding periods = end year − start year (2024→2032 is 8, not 9); watch simple-versus-compound confusion and "doubling every N years" (CAGR = 2^(1/N) − 1). A gap beyond the claim's own precision is inconsistent — tolerance is half the last written digit, floored at ±0.2 pp, so a claim of "30 %" tolerates ±0.5 pp while "29.7 %" tolerates ±0.05 pp. Rounding is not a contradiction.

### 3 — Multiply through the unit economics

A (price, volume, total) triple must reproduce: `implied total = volume × price per period × periods per year` (or margin × volume for a contribution claim). Accept it within about ±20 % — tiers, churn timing and currency blur exact multiplication; beyond that the burden is on the source. State the gap as a multiple ("2.5× the recomputation") and name the benign explanations the source would owe.

### 4 — Separate percentage from percentage-point change

"Improved by 5%" from a 10 % baseline means either 10.5 % (relative) or 15 % (+5 percentage points) — a tenfold difference in implied impact. With before and after values, compute both readings and state which the prose matches. With only the delta, mark the claim **ambiguous**, report both readings and never silently choose the more impressive one. Reverse trap: "fell 50% to 20%" — from 40 % or from 70 %?

### 5 — Run the survivorship and base-rate checks

For "X% of {winners} did Y", ask for the inverted statistic — what fraction of *all* who did Y became winners? If only survivors were sampled, tag the claim survivorship-biased and treat it as anecdote. For a "99 % accurate" detection claim, recompute the positive predictive value at the stated prevalence, `PPV = sens × prev / (sens × prev + (1 − spec)(1 − prev))` — at 1 % prevalence a 99 %/95 % screen gives PPV ≈ 17 %.

### 6 — Cross-check a bare headline with a Fermi decomposition

For a headline with no companions but a decomposable structure, build one independent estimate — `quantity ≈ population × participation rate × frequency × unit value` — rounding each factor to the nearest half-order of magnitude. Within about 3× of the claim: plausible; 10× or more apart: implausible-as-stated — name the likely conflation. A market size worth two cited estimates goes to `estimate-market-size`.

### 7 — Render the verdict

Fill the output template. Each verdict is exactly one of **consistent** (reproduces within tolerance), **inconsistent** (the numbers contradict each other — show the recomputation), **ambiguous** (two readings — show both) or **unverifiable** (no linked numbers). Never resolve an inconsistency by picking the more plausible number; flag and re-source.

## Output template

```
## Quantitative sanity check — {document / claim set}

| # | Claim (verbatim) | Check | Recomputed | Verdict |
|---|------------------|-------|------------|---------|
| 1 | {claim} | {compounding | unit economics | pp vs % | base rate | Fermi} | {what the other numbers imply} | {consistent | inconsistent | ambiguous | unverifiable} |

**Overall:** {consistent | inconsistent | ambiguous | unverifiable}
**Action:** {pass through | flag in report | re-source via grounded-fact-check | drop claim}
**Tolerances used:** {CAGR ± half the claim's last written digit, min 0.2 pp; unit economics ±20 %; Fermi 3×}
```

Mandatory fields: every row's *Recomputed* and *Verdict*, plus *Overall* and *Action*. A verdict without recomputation is an opinion.

## Worked example

Illustrative investor memo for a fictional vendor, "Northwind Metrics" (figures invented). Rows 1–3 reproduced with `scripts/sanity.py` (each exits 1); row 4 by hand.

```
python3 scripts/sanity.py cagr --start 6.25 --end 50 --years 8 --claim 24.8    # implied CAGR 29.7% → INCONSISTENT
python3 scripts/sanity.py unit-econ --price 1188 --cost 0 --volume 40000 --claim-total 120000000   # 2.525x gap
python3 scripts/sanity.py pp --before 10 --after 15 --claim-pct 5              # +5pp, not 50% → UNIT CONFUSION
```

| # | Claim (verbatim) | Check | Recomputed | Verdict |
|---|------------------|-------|------------|---------|
| 1 | "$6.25B (2024) to $50B by 2032 at a 24.8% CAGR" | compounding | 8 periods → 29.7 % implied; 24.8 % implies $36.8B | inconsistent |
| 2 | "$120M ARR from 40,000 customers at $99/month" | unit economics | 40,000 × $1,188 = $47.5M; claim is 2.5× | inconsistent |
| 3 | "conversion improved 5%, from 10% to 15%" | pp vs % | +5 pp; relative change 50 % | ambiguous — restate as +5 pp |
| 4 | "screen is 99% accurate" (sens 99 %, spec 95 %, prevalence 1 %) | base rate | PPV = 0.0099 / 0.0594 = 16.7 % | inconsistent with "99 %" framing |

**Overall:** inconsistent. **Action:** flag rows 1, 2 and 4 for re-sourcing; restate row 3. The growth and revenue headlines cannot both be right.

## Verification

Before the verdict ships:

- [ ] Every inconsistent row shows the recomputation; every ambiguous row shows both readings.
- [ ] Compounding periods equal end year minus start year — recompute with `scripts/sanity.py cagr` (exit code 1 = flagged).
- [ ] Unit-economics rows state the period basis (monthly price × 12) and used the ±20 % tolerance.
- [ ] Rounding was not flagged as inconsistency ("$48M" for $47.5M is fine).
- [ ] No claim was "fixed" by choosing a side; survivorship-tagged claims name the missing denominator.

## Companion tool

`scripts/sanity.py` (stdlib only, Python 3.9+) recomputes steps 2–4: `cagr` (implied CAGR and multiple vs a claimed CAGR), `pp` (percentage-point and relative change, claim in either unit), `unit-econ` (margin, contribution vs a claimed total — for a revenue triple pass the annual price and `--cost 0`) and `share` (share-of-whole and reverse). Exit status: 0 consistent or no claim, 1 flagged, 2 usage error.

```bash
python3 scripts/sanity.py cagr --start 6.25 --end 50 --years 8 --claim 24.8
python3 scripts/sanity.py pp --before 5 --after 7 --claim-pct 2
python3 scripts/sanity.py unit-econ --price 99 --cost 40 --volume 40000 --claim-total 120000000
python3 scripts/sanity.py --selftest        # 13 hand-checked cases, one PASS line each
```

Sample (`pp` command above):

```
before -> after : 5% -> 7%
absolute change : +2 percentage points
relative change : 40.0000%
UNIT CONFUSION  : claim of 2% matches the pp reading (+2pp), not the relative one (40.0000%) — restate as '+2 percentage points'
```

Usable without the tool — every check is one line of arithmetic; the tool removes slips.

## Pair with adjacent skills

- `grounded-fact-check` — external verification of numbers that pass the internal check; run this skill first, since an inconsistent claim has nothing to ground.
- `test-significance` — when the question shifts from "do these numbers agree?" to "is the gap noise?".
- `estimate-market-size` — two-sided sizing when a Fermi cross-check is not enough.
- `abstain-or-escalate` — when a load-bearing number is inconsistent and cannot be re-sourced.

## Anti-patterns

- Do **not** "fix" an inconsistent claim by picking the more plausible number. Flag it; re-sourcing is another skill's job.
- Do **not** confuse internal consistency with truth — consistent numbers can still be externally wrong.
- Do **not** apply false precision: one decimal place shows a contradiction.
- Do **not** flag rounding as inconsistency, nor let the ±20 % tolerance excuse a 2.5× gap; statistical tests belong to `test-significance`.

## Reference

- J. E. Miller, *The Chicago Guide to Writing about Numbers*, 2nd ed. Chicago: University of Chicago Press, 2015. ISBN 978-0-226-18577-4 — percentage vs percentage-point conventions.
- D. Huff, *How to Lie with Statistics*. New York: W. W. Norton, 1954 — baseline games and percentage traps.
- M. Mangel and F. J. Samaniego, "Abraham Wald's Work on Aircraft Survivability," *Journal of the American Statistical Association*, vol. 79, no. 386, pp. 259–267, 1984. doi:10.1080/01621459.1984.10478038 — Wald's 1943 survivorship-bias case.
- D. Kahneman, *Thinking, Fast and Slow*. New York: Farrar, Straus and Giroux, 2011, ch. 14–16 — base-rate neglect.
