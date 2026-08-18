#!/usr/bin/env python3
"""sanity.py — recompute checks for the quantitative-sanity-check skill.

Recomputes the arithmetic a source's own numbers imply and flags claims
whose figures don't reproduce each other. Internal consistency only.

Subcommands:
  cagr      CAGR + growth multiple from (start, end, years); check a claimed CAGR.
  pp        percentage-point change AND relative % change side by side;
            flag a claim stated in the wrong unit.
  unit-econ margin, margin %, contribution total; recompute a claimed total.
  share     percentage-of-whole and its reverse.

Exit status: 0 = consistent / no claim given; 1 = flagged mismatch; 2 = usage error.

Run `python3 sanity.py --selftest` for built-in worked examples.
Stdlib only. Python 3.9+.
"""

import argparse
import sys

# Tolerances. One decimal place is enough to show a contradiction (see the
# skill's anti-patterns): don't flag rounding, do flag real gaps.
# Percentage points on implied-vs-claimed CAGR. A flat 0.2pp manufactures false
# positives: sources routinely round CAGR to a whole percent, so a claim of "30%"
# against an implied 29.68% is ordinary rounding, not a contradiction -- and the
# skill's own verification checklist says rounding must not be flagged. The
# tolerance therefore takes the larger of 0.2pp and half the last written digit
# of the claim (a whole-number claim tolerates 0.5pp, "29.7" tolerates 0.05pp).
CAGR_TOL_PP = 0.2        # floor; see cagr_tolerance_pp()


def cagr_tolerance_pp(claim_pct):
    """Half the last written digit of the claim, floored at CAGR_TOL_PP."""
    if claim_pct is None:
        return CAGR_TOL_PP
    txt = ("%r" % float(claim_pct)).rstrip("0").rstrip(".")
    decimals = len(txt.split(".")[1]) if "." in txt else 0
    return max(CAGR_TOL_PP, 0.5 * (10 ** -decimals))
UNIT_TOL = 1e-6          # exact-ish comparisons for pp / share arithmetic
UNIT_ECON_TOL_REL = 0.20  # ±20% per the skill: tiers/churn/FX blur exact multiplication


# ---------------------------------------------------------------- computations

def implied_cagr(start, end, years):
    """CAGR as a fraction (0.10 = 10%)."""
    if start <= 0 or end <= 0:
        raise ValueError("start and end must be positive")
    if years <= 0:
        raise ValueError("years must be positive")
    return (end / start) ** (1.0 / years) - 1.0


def pp_change(before_pct, after_pct):
    """Return (percentage-point change, relative % change)."""
    pp = after_pct - before_pct
    rel = None if before_pct == 0 else pp / before_pct * 100.0
    return pp, rel


def unit_econ(price, cost, volume=None):
    """Return (margin, margin_pct, contribution_total or None)."""
    margin = price - cost
    margin_pct = None if price == 0 else margin / price * 100.0
    total = None if volume is None else margin * volume
    return margin, margin_pct, total


def share_of(part, whole):
    if whole == 0:
        raise ValueError("whole must be non-zero")
    return part / whole * 100.0


def whole_from_share(part, pct):
    if pct == 0:
        raise ValueError("share percent must be non-zero")
    return part / (pct / 100.0)


def fmt(x, nd=2):
    return "undefined" if x is None else f"{x:,.{nd}f}"


# ------------------------------------------------------------------- commands

def cmd_cagr(args):
    cagr = implied_cagr(args.start, args.end, args.years)
    multiple = args.end / args.start
    print(f"growth multiple : {multiple:.4g}x  ({args.start:g} -> {args.end:g} over {args.years:g} years)")
    print(f"implied CAGR    : {cagr * 100:.1f}%")
    if args.claim is not None:
        gap = cagr * 100.0 - args.claim
        tol = cagr_tolerance_pp(args.claim)
        print(f"claimed CAGR    : {args.claim:.1f}%")
        if abs(gap) <= tol:
            note = " (half the last written digit of the claim)" if tol > CAGR_TOL_PP else ""
            print(f"consistent      : within {tol:g}pp tolerance{note}")
            return 0
        fwd = args.start * (1.0 + args.claim / 100.0) ** args.years
        print(f"INCONSISTENT    : claimed CAGR implies end of {fwd:,.4g}, not {args.end:g} "
              f"(gap {gap:+.1f}pp, tolerance {tol:g}pp) — one of the figures is wrong; "
              f"flag, don't pick a side")
        return 1
    return 0


def cmd_pp(args):
    pp, rel = pp_change(args.before, args.after)
    print(f"before -> after : {args.before:g}% -> {args.after:g}%")
    print(f"absolute change : {pp:+.4g} percentage points")
    print(f"relative change : {fmt(rel, 4)}%" if rel is not None
          else "relative change : undefined (before = 0)")
    claim_pp = getattr(args, "claim_pp", None)
    claim_pct = getattr(args, "claim_pct", None)
    rel_str = fmt(rel, 4)
    matches_pp = abs((claim_pp if claim_pp is not None else claim_pct) - pp) <= UNIT_TOL
    matches_rel = (rel is not None and claim_pct is not None
                   and abs(claim_pct - rel) <= max(UNIT_TOL, abs(rel) * 1e-9))
    if claim_pp is not None:
        if matches_pp:
            print(f"consistent      : claim of {claim_pp:g}pp matches the pp reading")
            return 0
        print(f"INCONSISTENT    : claim of {claim_pp:g}pp does not match {pp:+.4g}pp "
              f"(check for pp-vs-% unit confusion)")
        return 1
    if claim_pct is not None:
        if matches_rel:
            print(f"consistent      : claim of {claim_pct:g}% matches the relative reading")
            return 0
        if matches_pp:
            print(f"UNIT CONFUSION  : claim of {claim_pct:g}% matches the pp reading "
                  f"({pp:+.4g}pp), not the relative one ({rel_str}%) — restate as "
                  f"'{pp:+.4g} percentage points'")
            return 1
        print(f"INCONSISTENT    : claim of {claim_pct:g}% matches neither reading "
              f"({pp:+.4g}pp / {rel_str}% relative)")
        return 1
    print("note            : no claim given — both readings shown; do not silently pick "
          "the more impressive one")
    return 0


def cmd_unit_econ(args):
    margin, margin_pct, total = unit_econ(args.price, args.cost, args.volume)
    print(f"margin per unit : {fmt(margin)}  (price {args.price:g} - cost {args.cost:g})")
    print(f"margin %        : {fmt(margin_pct, 1)}%" if margin_pct is not None
          else "margin %        : undefined (price = 0)")
    if total is not None:
        print(f"contribution    : {fmt(total)}  (margin x {args.volume:g} units)")
    if args.claim_total is not None:
        if total is None:
            print("cannot check    : --claim-total needs --volume to recompute against")
            return 2
        if total == 0:
            consistent = args.claim_total == 0
        else:
            consistent = abs(args.claim_total - total) / abs(total) <= UNIT_ECON_TOL_REL
        print(f"claimed total   : {fmt(args.claim_total)}")
        if consistent:
            print(f"consistent      : within ±{UNIT_ECON_TOL_REL:.0%} tolerance")
            return 0
        ratio = args.claim_total / total if total else float("inf")
        print(f"INCONSISTENT    : claim is {ratio:.4g}x the recomputed total "
              f"(beyond ±{UNIT_ECON_TOL_REL:.0%}) — flag it and name the gap")
        return 1
    return 0


def cmd_share(args):
    if args.whole_from_share is not None:
        part, pct = args.part, args.whole_from_share
        whole = whole_from_share(part, pct)
        print(f"{part:g} at {pct:g}% of whole  ->  whole = {fmt(whole, 4)}")
        return 0
    if args.whole is None:
        print("error: share needs --whole Y or --whole-from-share PCT", file=sys.stderr)
        return 2
    pct = share_of(args.part, args.whole)
    print(f"{args.part:g} of {args.whole:g}  ->  {fmt(pct, 4)}%")
    return 0


# ------------------------------------------------------------------ selftest

def selftest():
    """Hand-verified worked examples (each expected value checked by hand)."""
    checks = []

    def check(name, got, want, tol=1e-9):
        ok = abs(got - want) <= tol
        checks.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got:.6g}, want {want:.6g}")

    # 100 -> 121 over 2 years: (121/100)^(1/2) - 1 = 1.1 - 1 = 0.10 exactly.
    check("cagr 100->121 over 2y", implied_cagr(100, 121, 2), 0.10)
    # growth multiple = 1.21
    check("multiple 100->121", 121 / 100, 1.21)
    # skill's worked example: 6.25 -> 50 over 8y implies ~29.7% CAGR (8^(1/8)-1).
    check("cagr 6.25->50 over 8y", implied_cagr(6.25, 50, 8), 8 ** (1 / 8) - 1)
    # doubling every 3 years: 2^(1/3) - 1 ≈ 25.99%
    check("doubling every 3y", implied_cagr(1, 2, 3), 2 ** (1 / 3) - 1)

    # 5% -> 7% is +2pp absolute and +40% relative (2/5 = 0.4).
    pp, rel = pp_change(5, 7)
    check("pp change 5->7", pp, 2.0)
    check("relative change 5->7", rel, 40.0)
    # reverse trap: "fell 50% to 20%" as relative means from 40%.
    pp2, rel2 = pp_change(40, 20)
    check("pp change 40->20", pp2, -20.0)
    check("relative change 40->20", rel2, -50.0)

    # price 99, cost 40: margin 59; margin% = 59/99*100; 1000 units -> 59,000.
    m, mpct, tot = unit_econ(99, 40, 1000)
    check("margin 99-40", m, 59.0)
    check("margin pct 99/40", mpct, 5900.0 / 99)
    check("contribution 1000u", tot, 59000.0)

    # share: 3 of 8 = 37.5%; reverse: 3 at 37.5% implies whole = 8.
    check("share 3 of 8", share_of(3, 8), 37.5)
    # Regression: a whole-number CAGR claim must not be flagged for ordinary
    # rounding. 6.25 -> 50 over 8 years implies 29.68%; a source writing "30%"
    # is rounding, and the skill's own checklist forbids flagging that.
    check("CAGR tolerance for a whole-number claim is 0.5pp", cagr_tolerance_pp(30), 0.5)
    check("CAGR tolerance for a 1-decimal claim is 0.2pp floor", cagr_tolerance_pp(29.7), 0.2)

    check("whole from 3 at 37.5%", whole_from_share(3, 37.5), 8.0)

    n_fail = checks.count(False)
    print(f"selftest: {len(checks) - n_fail}/{len(checks)} checks passed")
    return 0 if n_fail == 0 else 1


# ----------------------------------------------------------------------- CLI

def build_parser():
    p = argparse.ArgumentParser(
        prog="sanity.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--selftest", action="store_true",
                   help="run built-in hand-verified examples and exit")
    sub = p.add_subparsers(dest="cmd")

    c = sub.add_parser("cagr", help="recompute CAGR / growth multiple")
    c.add_argument("--start", type=float, required=True)
    c.add_argument("--end", type=float, required=True)
    c.add_argument("--years", type=float, required=True)
    c.add_argument("--claim", type=float, default=None,
                   help="claimed CAGR in percent (e.g. 24.8)")
    c.set_defaults(func=cmd_cagr)

    q = sub.add_parser("pp", help="percentage-point vs relative %% change")
    q.add_argument("--before", type=float, required=True, help="before, in percent")
    q.add_argument("--after", type=float, required=True, help="after, in percent")
    g = q.add_mutually_exclusive_group()
    g.add_argument("--claim-pp", type=float, default=None,
                   help="claim stated in percentage points")
    g.add_argument("--claim-pct", type=float, default=None,
                   help="claim stated in relative percent")
    q.set_defaults(func=cmd_pp)

    u = sub.add_parser("unit-econ", help="margin and contribution recompute")
    u.add_argument("--price", type=float, required=True)
    u.add_argument("--cost", type=float, required=True)
    u.add_argument("--volume", type=float, default=None)
    u.add_argument("--claim-total", type=float, default=None,
                   help="claimed contribution total to recompute (needs --volume)")
    u.set_defaults(func=cmd_unit_econ)

    s = sub.add_parser("share", help="percentage-of-whole and its reverse")
    s.add_argument("--part", type=float, required=True)
    s.add_argument("--whole", type=float, default=None)
    s.add_argument("--whole-from-share", type=float, default=None, metavar="PCT",
                   help="recover the whole from --part X at PCT percent")
    s.set_defaults(func=cmd_share)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest()
    if not getattr(args, "func", None):
        build_parser().print_help()
        return 2
    try:
        return args.func(args)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
