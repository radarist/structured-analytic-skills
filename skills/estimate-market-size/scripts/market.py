#!/usr/bin/env python3
"""market.py — companion tool for the `estimate-market-size` skill.

Implements the skill's top-down x bottom-up triangulation:

  * topdown     — TAM -> SAM -> SOM cascade, plus implied customer counts
                  when an ARPU is supplied.
  * bottomup    — unit-economics estimate: customers x ARPU, or a sum over
                  named segments given as JSON.
  * triangulate — compares a top-down and a bottom-up estimate: ratio,
                  log10 gap, verdict per the skill's order-of-magnitude rule
                  (supported when 0.33 <= ratio <= 3), and a geometric-mean
                  midpoint suggestion.
  * --selftest  — hand-checked worked examples; one PASS line per check.

Stdlib only, Python 3.9+.
"""

import argparse
import json
import math
import sys

# Skill rule: estimates agree "within an order of magnitude" when the
# top-down / bottom-up ratio lies in [LOWER_RATIO, UPPER_RATIO] (0.33x to 3x).
LOWER_RATIO = 0.33
UPPER_RATIO = 3.0


def fmt_money(x):
    """Format a dollar figure with a T/B/M/K suffix, e.g. $1.73B."""
    sign = "-" if x < 0 else ""
    x = abs(float(x))
    for limit, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if x >= limit:
            return "%s$%.2f%s" % (sign, x / limit, suffix)
    return "%s$%.2f" % (sign, x)


def fmt_count(n):
    """Format a customer count with thousands separators."""
    return "{:,.0f}".format(n)


def topdown(tam, sam_pct=None, som_pct=None, arpu=None):
    """TAM -> SAM -> SOM cascade. Returns (rows, text) where rows is a list of
    (layer, dollars, implied_customers_or_None)."""
    sam = tam * (sam_pct / 100.0) if sam_pct is not None else tam
    som = sam * (som_pct / 100.0) if som_pct is not None else sam
    rows = [("TAM", tam), ("SAM", sam), ("SOM", som)]
    lines = ["Top-down cascade:"]
    prev = None
    for layer, dollars in rows:
        step = ""
        if prev is not None:
            pct = (sam_pct if layer == "SAM" else som_pct) or 100.0
            step = "  (= %s x %.4g%%)" % (fmt_money(prev), pct)
        implied = ""
        if arpu is not None:
            implied = "  implied customers: %s" % fmt_count(dollars / arpu)
        lines.append("  %s: %s%s%s" % (layer, fmt_money(dollars), step, implied))
        prev = dollars
    if arpu is not None:
        lines.append("  (ARPU used for implied counts: %s/yr)" % fmt_money(arpu))
    return rows, "\n".join(lines)


def bottomup(customers=None, arpu=None, segments=None):
    """Unit-economics estimate. Either customers x arpu, or the sum over
    segments [{name, customers, arpu}, ...]. Returns (total, text)."""
    lines = ["Bottom-up estimate:"]
    if segments is not None:
        total = 0.0
        for seg in segments:
            seg_total = seg["customers"] * seg["arpu"]
            total += seg_total
            lines.append(
                "  %s: %s customers x %s ARPU = %s"
                % (seg["name"], fmt_count(seg["customers"]),
                   fmt_money(seg["arpu"]), fmt_money(seg_total))
            )
        lines.append("  Total: %s" % fmt_money(total))
    else:
        total = customers * arpu
        lines.append(
            "  %s customers x %s ARPU = %s"
            % (fmt_count(customers), fmt_money(arpu), fmt_money(total))
        )
    return total, "\n".join(lines)


def triangulate(top, bottom):
    """Compare the two estimates per the skill's order-of-magnitude rule.
    Returns dict(ratio, log10_gap, verdict, midpoint, text)."""
    ratio = top / bottom
    gap = abs(math.log10(ratio))
    supported = LOWER_RATIO <= ratio <= UPPER_RATIO
    midpoint = math.sqrt(top * bottom)  # geometric mean of the two estimates
    verdict = "SUPPORTED" if supported else "REJECTED"
    lines = [
        "Triangulation:",
        "  Top-down:  %s" % fmt_money(top),
        "  Bottom-up: %s" % fmt_money(bottom),
        "  Ratio (top-down / bottom-up): %.4g" % ratio,
        "  Log10 gap: %.2f orders of magnitude" % gap,
        "  Verdict: %s (supported when %.2f <= ratio <= %.2f)"
        % (verdict, LOWER_RATIO, UPPER_RATIO),
        "  Geometric-mean midpoint: %s" % fmt_money(midpoint),
    ]
    if not supported:
        lines.append(
            "  Disagreement >3x is information: re-check the top-down ratios,"
            " the bottom-up ARPU/adoption, and that both estimates use the"
            " same market definition."
        )
    return {
        "ratio": ratio,
        "log10_gap": gap,
        "verdict": verdict,
        "supported": supported,
        "midpoint": midpoint,
        "text": "\n".join(lines),
    }


def selftest():
    """Hand-checked worked examples. Prints one PASS line per check and
    returns the number of failures."""
    checks = []

    def check(name, actual, expected, tol=1e-9):
        ok = abs(actual - expected) <= tol * max(1.0, abs(expected))
        checks.append((name, ok, actual, expected))

    # 1. Top-down cascade: TAM $1B, SAM 20% -> $200M, SOM 5% of SAM -> $10M.
    rows, _ = topdown(1e9, sam_pct=20, som_pct=5)
    check("topdown TAM", rows[0][1], 1e9)
    check("topdown SAM", rows[1][1], 2e8)
    check("topdown SOM", rows[2][1], 1e7)

    # 2. Top-down implied customers at ARPU $1,000/yr:
    #    TAM 1e9/1e3 = 1,000,000; SAM 2e8/1e3 = 200,000; SOM 1e7/1e3 = 10,000.
    rows, _ = topdown(1e9, sam_pct=20, som_pct=5, arpu=1000)
    check("implied customers SOM", rows[2][1] / 1000, 1e4)

    # 3. Bottom-up single segment: 1,000 customers x $500 = $500,000.
    total, _ = bottomup(customers=1000, arpu=500)
    check("bottomup simple", total, 5e5)

    # 4. Bottom-up segments: 100x$1000 + 200x$500 = $100k + $100k = $200,000.
    total, _ = bottomup(segments=[
        {"name": "enterprise", "customers": 100, "arpu": 1000},
        {"name": "smb", "customers": 200, "arpu": 500},
    ])
    check("bottomup segments", total, 2e5)

    # 5. Triangulation within an order of magnitude:
    #    top-down $1B vs bottom-up $3B -> ratio 1/3 ~= 0.3333 >= 0.33 -> SUPPORTED.
    r = triangulate(1e9, 3e9)
    check("triangulate ratio 1e9/3e9", r["ratio"], 1.0 / 3.0, tol=1e-6)
    check("triangulate log10 gap 1e9/3e9", r["log10_gap"], math.log10(3.0))
    check("triangulate midpoint 1e9x3e9", r["midpoint"], math.sqrt(3e18))
    check("triangulate supported flag", 1.0 if r["supported"] else 0.0, 1.0)

    # 6. Triangulation outside an order of magnitude:
    #    top-down $1B vs bottom-up $50B -> ratio 0.02 -> REJECTED (flagged).
    r = triangulate(1e9, 5e10)
    check("triangulate ratio 1e9/5e10", r["ratio"], 0.02)
    check("triangulate rejected flag", 1.0 if not r["supported"] else 0.0, 1.0)

    failures = 0
    for name, ok, actual, expected in checks:
        if ok:
            print("PASS: %s (got %.6g, expected %.6g)" % (name, actual, expected))
        else:
            failures += 1
            print("FAIL: %s (got %.6g, expected %.6g)" % (name, actual, expected))
    print("%d/%d checks passed" % (len(checks) - failures, len(checks)))
    return failures


def build_parser():
    p = argparse.ArgumentParser(
        description="Market-size triangulation: top-down cascade, bottom-up "
                    "unit economics, and order-of-magnitude comparison.",
    )
    p.add_argument("--selftest", action="store_true",
                   help="run built-in worked examples and exit")
    sub = p.add_subparsers(dest="cmd")

    td = sub.add_parser("topdown", help="TAM -> SAM -> SOM cascade")
    td.add_argument("--tam", type=float, required=True,
                    help="total addressable market in dollars/yr")
    td.add_argument("--sam-pct", type=float, default=None,
                    help="SAM as percent of TAM (e.g. 20)")
    td.add_argument("--som-pct", type=float, default=None,
                    help="SOM as percent of SAM (e.g. 5)")
    td.add_argument("--arpu", type=float, default=None,
                    help="average revenue per customer/yr, for implied counts")

    bu = sub.add_parser("bottomup", help="customers x ARPU, or summed segments")
    bu.add_argument("--customers", type=float, default=None,
                    help="number of customers")
    bu.add_argument("--arpu", type=float, default=None,
                    help="average revenue per customer/yr")
    bu.add_argument("--segments", default=None,
                    help='JSON list, e.g. [{"name":"ent","customers":100,'
                         '"arpu":1000}]')

    tr = sub.add_parser("triangulate", help="compare the two estimates")
    tr.add_argument("--topdown", type=float, required=True,
                    help="top-down estimate in dollars/yr")
    tr.add_argument("--bottomup", type=float, required=True,
                    help="bottom-up estimate in dollars/yr")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.selftest:
        return 1 if selftest() else 0

    if args.cmd == "topdown":
        if args.tam <= 0:
            sys.exit("error: --tam must be positive")
        _, text = topdown(args.tam, sam_pct=args.sam_pct,
                          som_pct=args.som_pct, arpu=args.arpu)
        print(text)
        return 0

    if args.cmd == "bottomup":
        if args.segments is not None:
            try:
                segments = json.loads(args.segments)
                for seg in segments:
                    if not all(k in seg for k in ("name", "customers", "arpu")):
                        raise ValueError("each segment needs name/customers/arpu")
            except (ValueError, TypeError) as e:
                sys.exit("error: bad --segments JSON: %s" % e)
            _, text = bottomup(segments=segments)
        elif args.customers is not None and args.arpu is not None:
            if args.customers <= 0 or args.arpu <= 0:
                sys.exit("error: --customers and --arpu must be positive")
            _, text = bottomup(customers=args.customers, arpu=args.arpu)
        else:
            sys.exit("error: give --customers and --arpu, or --segments")
        print(text)
        return 0

    if args.cmd == "triangulate":
        if args.topdown <= 0 or args.bottomup <= 0:
            sys.exit("error: estimates must be positive")
        print(triangulate(args.topdown, args.bottomup)["text"])
        return 0

    build_parser().print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
