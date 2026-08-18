#!/usr/bin/env python3
"""bayes.py — companion tool for the `bayesian-update` skill.

Implements the skill's odds-form Bayes update:

    posterior odds = prior odds x Bayes factor
    P(H|E)/P(~H|E) = [P(H)/P(~H)] x [P(E|H)/P(E|~H)]

and its Bayes-factor interpretation bands (this skill's own hybrid: Jeffreys'
rounded boundaries, labels part Jeffreys and part Lee & Wagenmakers 2014 --
not the scale Kass & Raftery 1995 recommend):
    1-3 barely worth mentioning | 3-10 moderate | 10-30 strong
    30-100 very strong | >100 decisive

Subcommands:
    update  --prior P --bf BF           single update from a Bayes factor
    update  --prior P --pe-h X --pe-not-h Y   BF from the two likelihoods
    chain   --prior P --bf BF1,BF2,...  sequential updates (one datum at a time)
    sweep   --prior P --bf BF           sensitivity table (skill step 5):
                                        priors {P/4, P/2, P, 2P, 4P cap 0.99}
                                        x Bayes factors {BF/3, BF, 3BF}
    --selftest                          run hand-checked worked examples

Stdlib only; Python 3.9+.
"""

import argparse
import math
import sys


# ---------------------------------------------------------------------------
# Core math
# ---------------------------------------------------------------------------

def prob_to_odds(p):
    """Probability -> odds (H:~H as a single number, e.g. 0.25 -> 1/3)."""
    return p / (1.0 - p)


def odds_to_prob(o):
    """Odds -> probability."""
    return o / (1.0 + o)


def bayes_factor(pe_h, pe_not_h):
    """BF = P(E|H) / P(E|~H)."""
    return pe_h / pe_not_h


def update_odds(prior_odds, bf):
    """The whole method in one line: multiply odds by the Bayes factor."""
    return prior_odds * bf


def bf_band(bf):
    """Interpretation band for a Bayes factor, per the skill's convention."""
    if bf < 1.0:
        return "favors ~H (evidence against)"
    if bf > 100.0:
        return "decisive"
    if bf >= 30.0:
        return "very strong"
    if bf >= 10.0:
        return "strong"
    if bf >= 3.0:
        return "moderate"
    return "barely worth mentioning"


def absolute_state(p):
    """The skill's 'absolute' read of a posterior probability."""
    if p < 0.4:
        return "still unlikely"
    if p <= 0.6:
        return "roughly coin-flip"
    return "likely"


def fmt(x, nd=4):
    """Compact number formatting for the report."""
    if isinstance(x, float) and math.isclose(x, round(x)) and abs(x) >= 100:
        return str(int(round(x)))
    return f"{x:.{nd}g}"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def check_prob(p, name):
    if not (0.0 < p < 1.0):
        raise ValueError(f"{name} must be strictly between 0 and 1 (got {p})")


def check_bf(bf):
    if bf <= 0.0:
        raise ValueError(f"Bayes factor must be positive (got {bf})")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_update(prior, bf, label=None):
    """Print the skill's step-4/step-6 report for one update."""
    prior_odds = prob_to_odds(prior)
    post_odds = update_odds(prior_odds, bf)
    post = odds_to_prob(post_odds)
    if label:
        print(f"--- {label} ---")
    print(f"Prior P(H):        {fmt(prior)}")
    print(f"Prior odds:        {fmt(prior_odds)}  ({fmt(prior_odds)}:1 H:~H)")
    print(f"Bayes factor:      {fmt(bf)}  [{bf_band(bf)}]")
    print(f"Posterior odds:    {fmt(post_odds)}")
    print(f"Posterior P(H|E):  {fmt(post)}")
    print("Two reads:")
    print(f"- Relative: odds moved {fmt(bf)}x "
          f"(from {fmt(prior_odds)}:1 to {fmt(post_odds)}:1).")
    print(f"- Absolute: hypothesis is now {absolute_state(post)} "
          f"({fmt(post * 100, 3)}%).")
    return post


def cmd_update(args):
    prior = args.prior
    check_prob(prior, "--prior")
    if args.bf is not None:
        bf = args.bf
        pe_h = pe_not_h = None
    else:
        pe_h, pe_not_h = args.pe_h, args.pe_not_h
        if pe_h is None or pe_not_h is None:
            raise ValueError("update needs either --bf or both --pe-h and --pe-not-h")
        if not (0.0 < pe_h <= 1.0) or not (0.0 < pe_not_h <= 1.0):
            raise ValueError("likelihoods must be in (0, 1]")
        bf = bayes_factor(pe_h, pe_not_h)
    check_bf(bf)
    if pe_h is not None:
        print(f"P(E|H):            {fmt(pe_h)}")
        print(f"P(E|~H):           {fmt(pe_not_h)}")
    print_update(prior, bf)


def cmd_chain(args):
    prior = args.prior
    check_prob(prior, "--prior")
    bfs = [float(x) for x in args.bf.split(",")]
    for bf in bfs:
        check_bf(bf)
    if args.dependent:
        print("WARNING: --dependent set. Chained updates assume independent "
              "evidence.")
        print("Two reports citing the same primary source are ONE observation, "
              "not two —")
        print("multiplying their Bayes factors double-counts the evidence. "
              "Estimate a")
        print("single joint Bayes factor for the cluster instead, or discount "
              "each step.")
        print()
    odds = prob_to_odds(prior)
    print(f"Start: prior P(H) = {fmt(prior)}  (odds {fmt(odds)}:1)")
    for i, bf in enumerate(bfs, 1):
        odds = update_odds(odds, bf)
        p = odds_to_prob(odds)
        print(f"Step {i}: BF {fmt(bf)} [{bf_band(bf)}] -> "
              f"odds {fmt(odds)}:1 -> P(H) = {fmt(p)}")
    post = odds_to_prob(odds)
    print(f"Final posterior P(H|all E): {fmt(post)} "
          f"({absolute_state(post)})")


def cmd_sweep(args):
    prior = args.prior
    check_prob(prior, "--prior")
    bf = args.bf
    check_bf(bf)
    # Skill step 5: vary the prior across a plausible range, vary the BF,
    # see whether the decision changes.
    priors = [min(0.99, prior * m) for m in (0.25, 0.5, 1.0, 2.0, 4.0)]
    bfs = [bf / 3.0, bf, bf * 3.0]
    print("Sensitivity sweep — posterior P(H|E) by prior (rows) x "
          "Bayes factor (cols)")
    print("(priors are {P/4, P/2, P, 2P, 4P} capped at 0.99; "
          "BFs are {BF/3, BF, 3BF})")
    print()
    header = "prior \\ BF |" + "|".join(f"{fmt(b):>10}" for b in bfs)
    print(header)
    print("-" * len(header))
    for p in priors:
        row = []
        for b in bfs:
            post = odds_to_prob(update_odds(prob_to_odds(p), b))
            row.append(f"{post:>10.4f}")
        tag = " (P)" if math.isclose(p, prior) else ""
        print(f"{fmt(p):>10}{tag:<4}|" + "|".join(row))
    print()
    print("If the *decision* flips across a row or column, the conclusion is "
          "fragile —")
    print("you need more diagnostic evidence, not more confidence. Name the "
          "most load-bearing input.")


# ---------------------------------------------------------------------------
# Self-test: hand-checked worked examples
# ---------------------------------------------------------------------------

def selftest():
    checks = []

    def check(name, got, want, tol=1e-4):
        ok = abs(got - want) <= tol
        checks.append(ok)
        print(f"PASS  {name}: got {got:.6f}, expected {want:.6f}"
              if ok else
              f"FAIL  {name}: got {got:.6f}, expected {want:.6f}")

    def check_eq(name, got, want):
        ok = got == want
        checks.append(ok)
        print(f"PASS  {name}: got {got!r}, expected {want!r}"
              if ok else
              f"FAIL  {name}: got {got!r}, expected {want!r}")

    # Case 1: prior 0.01, BF 20 -> odds 1/99 * 20 = 20/99 -> P = 20/119.
    # Hand-verified: 20/119 = 0.168067...
    post = odds_to_prob(update_odds(prob_to_odds(0.01), 20.0))
    check("prior=0.01 bf=20 posterior", post, 20.0 / 119.0)

    # Case 2: prior 0.5, BF 10 -> odds 1 * 10 = 10 -> P = 10/11 = 0.909091.
    post = odds_to_prob(update_odds(prob_to_odds(0.5), 10.0))
    check("prior=0.5 bf=10 posterior", post, 10.0 / 11.0)

    # Case 3: likelihood ratio route. pe_h=0.8, pe_not_h=0.1 -> BF 8.
    # prior 0.25 -> odds 1/3 -> 8/3 -> P = 8/11 = 0.727273.
    bf = bayes_factor(0.8, 0.1)
    check("pe_h=0.8 pe_not_h=0.1 -> BF", bf, 8.0)
    post = odds_to_prob(update_odds(prob_to_odds(0.25), bf))
    check("prior=0.25 bf=8 posterior", post, 8.0 / 11.0)

    # Case 4: chain. prior 0.1 -> odds 1/9; BF 5 then 4 -> 5/9 -> 20/9
    # -> P = 20/29 = 0.689655.
    odds = prob_to_odds(0.1)
    for b in (5.0, 4.0):
        odds = update_odds(odds, b)
    check("chain prior=0.1 bf=[5,4] posterior", odds_to_prob(odds), 20.0 / 29.0)

    # Case 5: sweep corner — prior 0.5*4=2.0 capped at 0.99, BF 10:
    # odds 99 * 10 = 990 -> P = 990/991 = 0.998991.
    p = min(0.99, 0.5 * 4.0)
    post = odds_to_prob(update_odds(prob_to_odds(p), 10.0))
    check("sweep cap prior->0.99 bf=10 posterior", post, 990.0 / 991.0)

    # Case 6: odds<->probability roundtrip.
    check("odds/prob roundtrip", odds_to_prob(prob_to_odds(0.37)), 0.37)

    # Case 7: interpretation bands at the skill's boundaries.
    check_eq("band bf=2", bf_band(2.0), "barely worth mentioning")
    check_eq("band bf=3", bf_band(3.0), "moderate")
    check_eq("band bf=10", bf_band(10.0), "strong")
    check_eq("band bf=30", bf_band(30.0), "very strong")
    check_eq("band bf=150", bf_band(150.0), "decisive")

    n = len(checks)
    passed = sum(checks)
    print(f"\n{passed}/{n} checks passed.")
    return 0 if passed == n else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    ap = argparse.ArgumentParser(
        description="Odds-form Bayesian update — companion tool for the "
                    "bayesian-update skill.")
    ap.add_argument("--selftest", action="store_true",
                    help="run hand-checked worked examples and exit")
    sub = ap.add_subparsers(dest="cmd")

    up = sub.add_parser("update", help="single Bayesian update")
    up.add_argument("--prior", type=float, required=True, help="P(H), in (0,1)")
    up.add_argument("--bf", type=float, help="Bayes factor P(E|H)/P(E|~H)")
    up.add_argument("--pe-h", dest="pe_h", type=float,
                    help="P(E|H) — likelihood if H true")
    up.add_argument("--pe-not-h", dest="pe_not_h", type=float,
                    help="P(E|~H) — likelihood if H false")
    up.set_defaults(func=cmd_update)

    ch = sub.add_parser("chain", help="sequential updates on multiple data")
    ch.add_argument("--prior", type=float, required=True)
    ch.add_argument("--bf", required=True,
                    help="comma-separated Bayes factors, e.g. 5,4,1.5")
    ch.add_argument("--dependent", action="store_true",
                    help="print the skill's double-counting warning")
    ch.set_defaults(func=cmd_chain)

    sw = sub.add_parser("sweep", help="sensitivity table (skill step 5)")
    sw.add_argument("--prior", type=float, required=True)
    sw.add_argument("--bf", type=float, required=True)
    sw.set_defaults(func=cmd_sweep)
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    try:
        args.func(args)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
