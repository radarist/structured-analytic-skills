#!/usr/bin/env python3
"""brier.py — Brier score, Murphy decomposition, and Brier Skill Score.

Implements the exact definitions in ../SKILL.md:

  * Mean Brier score:          BS = (1/N) * sum (f_t - o_t)^2
  * Murphy (1973) decomposition: BS = RELIABILITY - RESOLUTION + UNCERTAINTY
  * Brier Skill Score vs the climatological base-rate reference:
        BSS = 1 - BS / BS_ref

Forecasts whose outcome is ambiguous or never resolved ("?") are EXCLUDED and
reported separately — never silently counted as losses (SKILL.md step 1).

Stdlib only. Python 3.9+.

Usage:
    python3 brier.py score     --file forecasts.csv
    python3 brier.py decompose --file forecasts.json --bins 10
    python3 brier.py skill     --demo
    python3 brier.py --selftest
"""

import argparse
import csv
import json
import sys

# --- input parsing -----------------------------------------------------------

# Accepted outcome spellings. Anything in AMBIGUOUS is excluded, not scored.
YES = {"1", "true", "yes", "y"}
NO = {"0", "false", "no", "n"}
AMBIGUOUS = {"?", "", "na", "n/a", "none", "null", "ambiguous", "unresolved"}

# A bin counts as calibrated when |observed - mean stated| is within this much.
# Without a tolerance, floating-point noise turns an exactly calibrated bin into
# a spurious over/under verdict.
DIRECTION_TOL = 1e-9

# Flexible column names for CSV headers / JSON object keys.
PROB_KEYS = ("probability", "forecast", "prob", "f", "p")
OUTCOME_KEYS = ("outcome", "o", "resolved", "result")

# Built-in example set for --demo: a forecaster who is decent in the middle of
# the range but overconfident at the high end, plus one ambiguous question.
DEMO = [
    {"probability": 0.05, "outcome": 0},
    {"probability": 0.10, "outcome": 0},
    {"probability": 0.20, "outcome": 0},
    {"probability": 0.30, "outcome": 0},
    {"probability": 0.40, "outcome": 1},
    {"probability": 0.50, "outcome": 1},
    {"probability": 0.50, "outcome": 0},
    {"probability": 0.60, "outcome": 1},
    {"probability": 0.70, "outcome": 0},
    {"probability": 0.70, "outcome": 1},
    {"probability": 0.80, "outcome": 0},
    {"probability": 0.80, "outcome": 1},
    {"probability": 0.90, "outcome": 0},
    {"probability": 0.95, "outcome": 1},
    {"probability": 0.65, "outcome": "?"},  # never resolved -> excluded
]


def parse_outcome(raw):
    """Map a raw outcome value to 1, 0, or None (ambiguous -> excluded)."""
    s = str(raw).strip().lower()
    if s in YES:
        return 1
    if s in NO:
        return 0
    if s in AMBIGUOUS:
        return None
    raise ValueError(f"unrecognized outcome {raw!r} (use 1/0/yes/no/?)")


def _find_key(mapping, candidates):
    """Return the actual key in `mapping` matching one of `candidates`."""
    lowered = {str(k).strip().lower(): k for k in mapping}
    for cand in candidates:
        if cand in lowered:
            return lowered[cand]
    return None


def parse_rows(dicts):
    """Split raw row-dicts into (scored, excluded).

    scored:   list of (probability, outcome) with outcome in {0, 1}
    excluded: list of (probability, raw_outcome) reported separately
    """
    scored, excluded = [], []
    for i, row in enumerate(dicts, start=1):
        pkey = _find_key(row, PROB_KEYS)
        okey = _find_key(row, OUTCOME_KEYS)
        if pkey is None or okey is None:
            raise ValueError(
                f"row {i}: need probability {PROB_KEYS} and outcome {OUTCOME_KEYS} "
                f"columns; got keys {list(row)}"
            )
        f = float(row[pkey])
        if not 0.0 <= f <= 1.0:
            raise ValueError(f"row {i}: probability {f} outside [0, 1]")
        o = parse_outcome(row[okey])
        if o is None:
            excluded.append((f, row[okey]))
        else:
            scored.append((f, o))
    return scored, excluded


def load_file(path):
    """Load forecasts from CSV or JSON (chosen by extension).

    CSV: header row with probability + outcome columns.
    JSON: a list of objects, or {"forecasts": [...]}, with the same keys.
    """
    with open(path, newline="", encoding="utf-8") as fh:
        if path.lower().endswith(".json"):
            data = json.load(fh)
            if isinstance(data, dict):
                data = data.get("forecasts", [])
            return parse_rows(data)
        return parse_rows(list(csv.DictReader(fh)))


# --- the math (SKILL.md steps 2-5) -------------------------------------------


def brier_score(scored):
    """Mean Brier score: BS = (1/N) * sum (f - o)^2. Lower is better; 0 perfect."""
    return sum((f - o) ** 2 for f, o in scored) / len(scored)


def base_rate(scored):
    """Observed overall frequency of the event (the 'climatology')."""
    return sum(o for _, o in scored) / len(scored)


def bin_index(f, n_bins):
    """Bin k covers [k/n, (k+1)/n); the top bin also contains f = 1.0.

    The tiny epsilon keeps exact edge values (0.2, 0.4, ...) in their upper
    bin despite floating-point representation error.
    """
    return min(int(f * n_bins + 1e-9), n_bins - 1)


def decompose(scored, n_bins):
    """Murphy (1973) decomposition: BS = RELIABILITY - RESOLUTION + UNCERTAINTY.

    REL = (1/N) sum_k n_k (f_bar_k - o_bar_k)^2   calibration error (lower better)
    RES = (1/N) sum_k n_k (o_bar_k - o_bar)^2     discrimination (higher better)
    UNC = o_bar (1 - o_bar)                       outcome variance (fixed)

    f_bar_k is the mean forecast *within* bin k. The identity is exact only
    when every forecast inside a bin is identical; otherwise the residual is
    the within-bin term (1/N) sum_k [ sum(f - f_bar_k)^2 - 2 sum(f - f_bar_k)(o - o_bar_k) ],
    so REL - RES + UNC approaches BS as the binning gets finer. `decompose`
    reports both numbers and the residual rather than asserting equality.
    Returns (rel, res, unc, table); table rows are per non-empty bin dicts.
    """
    n = len(scored)
    base = base_rate(scored)
    unc = base * (1.0 - base)
    groups = {}
    for f, o in scored:
        groups.setdefault(bin_index(f, n_bins), []).append((f, o))

    rel = res = 0.0
    table = []
    for k in sorted(groups):
        g = groups[k]
        nk = len(g)
        mean_f = sum(f for f, _ in g) / nk
        obs = sum(o for _, o in g) / nk
        rel += nk * (mean_f - obs) ** 2
        res += nk * (obs - base) ** 2
        lo = k / n_bins
        hi = (k + 1) / n_bins
        mid = (lo + hi) / 2.0
        # Calibration curve read (SKILL.md step 5): compare the observed
        # frequency with the MEAN STATED PROBABILITY in the bin, never with the
        # bin midpoint -- the midpoint is an artefact of how the axis was cut,
        # and a forecaster who says 0.70 inside a [0.70,0.80) bin is calibrated
        # when 70% of those questions resolve yes. Observed above stated =
        # underconfident; below = overconfident; equal = calibrated.
        if obs > mean_f + DIRECTION_TOL:
            direction = "underconfident"
        elif obs < mean_f - DIRECTION_TOL:
            direction = "overconfident"
        else:
            direction = "calibrated"
        table.append(
            {
                "k": k,
                "bin": f"[{lo:.2f},{hi:.2f}{']' if k == n_bins - 1 else ')'}",
                "n": nk,
                "midpoint": mid,
                "mean_f": mean_f,
                "observed": obs,
                "direction": direction,
            }
        )
    return rel / n, res / n, unc, table


def brier_skill(scored):
    """BSS = 1 - BS/BS_ref vs the climatological reference (always predict the
    base rate). BS_ref of climatology equals o_bar(1 - o_bar) = UNCERTAINTY.
    Returns (bss, bs, bs_ref, base); bss is None when BS_ref == 0."""
    base = base_rate(scored)
    bs = brier_score(scored)
    bs_ref = base * (1.0 - base)
    bss = None if bs_ref == 0.0 else 1.0 - bs / bs_ref
    return bss, bs, bs_ref, base


# --- CLI ---------------------------------------------------------------------


def get_data(args, parser):
    if args.demo:
        return parse_rows(DEMO)
    if args.file:
        try:
            return load_file(args.file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(f"could not load {args.file}: {exc}")
    parser.error("pass --file PATH or --demo")


def cmd_score(scored, excluded):
    bs = brier_score(scored)
    print(f"Forecasts scored (N): {len(scored)}")
    print(f"Excluded (ambiguous/unresolved): {len(excluded)}")
    print(f"Mean Brier score: {bs:.4f}   (0 = perfect; 0.25 = always-50% on balanced questions)")


def cmd_decompose(scored, excluded, n_bins):
    rel, res, unc, table = decompose(scored, n_bins)
    bs = brier_score(scored)
    print(f"Murphy decomposition over N = {len(scored)} forecasts ({len(excluded)} excluded), {n_bins} bins:")
    print(f"  Reliability (calibration error):  {rel:.4f}   (lower is better; 0 = perfectly calibrated)")
    print(f"  Resolution (discrimination):      {res:.4f}   (higher is better)")
    print(f"  Uncertainty (base-rate variance): {unc:.4f}   (fixed by the question set)")
    _lhs = rel - res + unc
    _resid = bs - _lhs
    if abs(_resid) < 5e-5:
        print(f"  Check: REL - RES + UNC = {_lhs:.4f} = mean Brier {bs:.4f}")
    else:
        print(f"  Check: REL - RES + UNC = {_lhs:.4f} vs mean Brier {bs:.4f} "
              f"(within-bin residual {_resid:+.4f}; exact only when each bin holds one distinct forecast)")
    print()
    print(f"{'bin':<14}{'n':>4}{'midpoint':>10}{'mean f':>9}{'observed':>10}   direction")
    for row in table:
        print(
            f"{row['bin']:<14}{row['n']:>4}{row['midpoint']:>10.2f}"
            f"{row['mean_f']:>9.3f}{row['observed']:>10.3f}   {row['direction']}"
        )
    empties = n_bins - len(table)
    if empties:
        print(f"({empties} empty bin(s) omitted)")


def cmd_skill(scored, excluded):
    bss, bs, bs_ref, base = brier_skill(scored)
    print(f"Forecasts scored (N): {len(scored)}  ({len(excluded)} excluded)")
    print(f"Base rate (climatology): {base:.4f}")
    print(f"Mean Brier score:        {bs:.4f}")
    print(f"Reference Brier (always predict the base rate): {bs_ref:.4f}")
    if bss is None:
        print("Brier Skill Score: undefined (base rate is 0 or 1 — climatology is already perfect)")
    else:
        print(f"Brier Skill Score: {bss:+.4f}   (>0 beats the base rate; <0 is worse than guessing)")


# --- selftest ----------------------------------------------------------------


def _assert_eq(label, got, want, why=""):
    """Assert first, then report -- never print PASS before evaluating."""
    if got != want:
        print(f"FAIL  {label}: got {got!r}, want {want!r}" + (f" ({why})" if why else ""))
        sys.exit(1)
    print(f"PASS  {label}: {got}" + (f" ({why})" if why else ""))
    return True


def run_selftest():
    """Hand-verified worked examples. Every expected value below was computed
    by hand from the formulas in SKILL.md before being encoded here."""
    checks = []

    def check(name, got, want, tol=1e-9):
        ok = abs(got - want) <= tol
        checks.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got:.6f}, expected {want:.6f}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    # Miniature set (hand computation):
    #   (f, o) = (0.2,0) (0.2,1) (0.4,0) (0.6,1) (0.8,1) (0.8,0);  plus one "?"
    # Squared errors: 0.04, 0.64, 0.16, 0.16, 0.04, 0.64  ->  sum 1.68, N = 6.
    mini = [
        {"probability": 0.2, "outcome": 0},
        {"probability": 0.2, "outcome": 1},
        {"probability": 0.4, "outcome": 0},
        {"probability": 0.6, "outcome": 1},
        {"probability": 0.8, "outcome": 1},
        {"probability": 0.8, "outcome": 0},
        {"probability": 0.7, "outcome": "?"},  # ambiguous -> excluded
    ]
    scored, excluded = parse_rows(mini)

    check("exclusion: ambiguous forecast excluded, not scored", len(excluded), 1)
    check("exclusion: scored N", len(scored), 6)

    # Mean Brier by hand: 1.68 / 6 = 0.28.
    check("mean Brier = 1.68/6", brier_score(scored), 0.28)

    # Base rate by hand: 3 events / 6 = 0.5  ->  UNC = 0.5 * 0.5 = 0.25.
    check("base rate = 3/6", base_rate(scored), 0.5)

    # Murphy decomposition with 10 bins. Non-empty bins and by-hand terms:
    #   [0.2,0.3): n=2, f_bar=0.2, o_bar=0.5 -> REL 2*(0.3)^2=0.18, RES 2*(0)^2=0
    #   [0.4,0.5): n=1, f_bar=0.4, o_bar=0.0 -> REL 0.16,          RES 0.25
    #   [0.6,0.7): n=1, f_bar=0.6, o_bar=1.0 -> REL 0.16,          RES 0.25
    #   [0.8,0.9): n=2, f_bar=0.8, o_bar=0.5 -> REL 2*(0.3)^2=0.18, RES 0
    # REL = 0.68/6, RES = 0.50/6, UNC = 0.25.
    rel, res, unc, table = decompose(scored, 10)
    check("reliability = 0.68/6", rel, 0.68 / 6)
    check("resolution = 0.50/6", res, 0.50 / 6)
    check("uncertainty = 0.25", unc, 0.25)
    check("identity REL - RES + UNC = BS", rel - res + unc, 0.28)

    # Per-bin table: 4 non-empty bins. Direction is read against the MEAN
    # STATED probability, not the bin midpoint.
    check("non-empty bins", len(table), 4)
    by_k = {row["k"]: row for row in table}
    check("bin[0.6,0.7) observed freq", by_k[6]["observed"], 1.0)
    _assert_eq("direction bin[0.6,0.7)", by_k[6]["direction"], "underconfident",
               f"observed 1.00 > mean stated {by_k[6]['mean_f']:.2f}")
    _assert_eq("direction bin[0.8,0.9)", by_k[8]["direction"], "overconfident",
               f"observed 0.50 < mean stated {by_k[8]['mean_f']:.2f}")

    # Regression test for the midpoint bug: a forecaster who states 0.70 ten
    # times and resolves 7/10 is exactly calibrated. Judged against the bin
    # midpoint (0.75) this reads "overconfident"; judged against the mean
    # stated probability it reads "calibrated", which is correct.
    cal = [{"probability": 0.70, "outcome": 1} for _ in range(7)]
    cal += [{"probability": 0.70, "outcome": 0} for _ in range(3)]
    cal_scored, _ = parse_rows(cal)
    cal_rel, _, _, cal_table = decompose(cal_scored, 10)
    check("calibrated set: reliability = 0", cal_rel, 0.0)
    _assert_eq("calibrated bin is not mislabelled", cal_table[0]["direction"], "calibrated",
               "mean stated 0.70 == observed 0.70")

    # BSS by hand: BS_ref = climatology = 0.25 (= UNC); BSS = 1 - 0.28/0.25 = -0.12.
    bss, bs, bs_ref, _ = brier_skill(scored)
    check("reference Brier = uncertainty", bs_ref, 0.25)
    check("BSS = 1 - 0.28/0.25", bss, -0.12)

    # Perfect miniature set: (0.0, 0), (1.0, 1). BS = 0 by hand; base rate 0.5
    # -> BS_ref = 0.25; BSS = 1 - 0/0.25 = 1.0 (maximal skill).
    perfect, _ = parse_rows(
        [{"probability": 0.0, "outcome": 0}, {"probability": 1.0, "outcome": 1}]
    )
    check("perfect set: BS = 0", brier_score(perfect), 0.0)
    bss_p, _, _, _ = brier_skill(perfect)
    check("perfect set: BSS = 1", bss_p, 1.0)

    print(f"ALL {len(checks)} CHECKS PASSED")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Brier score, Murphy decomposition, and Brier Skill Score "
        "for a set of resolved probabilistic forecasts."
    )
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    sub = parser.add_subparsers(dest="command")
    for name, helptext in [
        ("score", "N, mean Brier score, excluded count"),
        ("decompose", "reliability / resolution / uncertainty + per-bin calibration table"),
        ("skill", "Brier Skill Score vs the climatological base-rate reference"),
    ]:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--file", help="CSV or JSON file of forecasts (probability, outcome 1/0/?)")
        p.add_argument("--demo", action="store_true", help="use the built-in example forecast set")
        if name == "decompose":
            p.add_argument("--bins", type=int, default=10, help="number of calibration bins (default 10)")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.command:
        parser.error("choose a command: score | decompose | skill  (or --selftest)")
    scored, excluded = get_data(args, parser)
    if not scored:
        parser.error("no resolved forecasts to score (all rows excluded?)")
    if args.command == "score":
        cmd_score(scored, excluded)
    elif args.command == "decompose":
        if args.bins < 1:
            parser.error("--bins must be >= 1")
        cmd_decompose(scored, excluded, args.bins)
    else:
        cmd_skill(scored, excluded)
    return 0


if __name__ == "__main__":
    sys.exit(main())
