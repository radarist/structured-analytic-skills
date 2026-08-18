#!/usr/bin/env python3
"""Companion tool for the `test-significance` skill.

Implements the significance checks described in SKILL.md from summary
statistics: two-prop (pooled z-test + CI + Cohen's h), fisher (exact 2x2,
two-sided), chi2 (2x2, df = 1), welch (exact t-distribution p-value via the
regularized incomplete beta function), effect (Cohen's d + Hedges' g).

Standard library only, Python 3.9+. Run with --selftest to check the
implementation against hand-verified worked examples.
"""

import argparse
import math
import sys
from math import comb

Z_95 = 1.959964  # 97.5th percentile of the standard normal

# The skill's core anti-pattern: reporting p alone. Printed by every subcommand.
REMINDER = ("Reminder: p only says 'probably not noise' — always report the CI "
            "and effect size too; a significant result can be practically trivial.")


# --- statistical core ------------------------------------------------------

def _betacf(a, b, x):
    """Continued fraction for the incomplete beta function (Numerical Recipes)."""
    max_iter, eps, fpmin = 200, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < fpmin: d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin: d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin: c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin: d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin: c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps: break
    return h


def regularized_beta(a, b, x):
    """Regularized incomplete beta function I_x(a, b)."""
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    # Front factor via log-gamma to avoid over/underflow.
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                  + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def t_two_sided_p(t, df):
    """Two-sided P(|T| >= |t|) for a Student-t with df degrees of freedom.

    Exact: P = I_{df/(df+t^2)}(df/2, 1/2). No normal approximation is used
    at any df, so no approximation warning is ever needed.
    """
    return regularized_beta(df / 2.0, 0.5, df / (df + t * t))


def chi2_1df_p(x):
    """Survival function of chi-square with df = 1: p = erfc(sqrt(x/2))."""
    return math.erfc(math.sqrt(x / 2.0))


def two_prop(x1, n1, x2, n2):
    """Pooled two-proportion z-test. Returns dict with z, p, CI, Cohen's h."""
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se_pool = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se_pool if se_pool > 0 else 0.0
    p = math.erfc(abs(z) / math.sqrt(2))  # two-sided normal p for a z statistic
    # CI uses the unpooled standard error (SKILL.md step 4).
    se_ci = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    diff = p1 - p2
    ci = (diff - Z_95 * se_ci, diff + Z_95 * se_ci)
    h = 2.0 * (math.asin(math.sqrt(p1)) - math.asin(math.sqrt(p2)))
    return {"p1": p1, "p2": p2, "z": z, "p": p, "ci": ci, "h": h}


def _hypergeom_p(i, r1, c1, n):
    """Probability of a 2x2 table with top-left cell i, margins fixed."""
    return comb(c1, i) * comb(n - c1, r1 - i) / comb(n, r1)


def fisher_exact(a, b, c, d):
    """Fisher's exact test on [[a, b], [c, d]], two-sided by probability ordering.

    Sums the hypergeometric probabilities of every table with the same margins
    whose probability is <= the observed table's probability.
    """
    r1, c1, n = a + b, a + c, a + b + c + d
    lo, hi = max(0, r1 - (n - c1)), min(r1, c1)
    p_obs = _hypergeom_p(a, r1, c1, n)
    p_two = sum(
        _hypergeom_p(i, r1, c1, n)
        for i in range(lo, hi + 1)
        if _hypergeom_p(i, r1, c1, n) <= p_obs * (1 + 1e-9)
    )
    return p_obs, min(p_two, 1.0)


def chi2_stat(a, b, c, d):
    """Pearson chi-square statistic for [[a, b], [c, d]] (df = 1, no Yates)."""
    n = a + b + c + d
    denom = (a + b) * (c + d) * (a + c) * (b + d)
    if denom == 0:
        # An empty row or column: one variable never varies, so no association
        # can be estimated. chi-square is undefined here, not zero.
        raise ValueError(
            "chi-square is undefined: the table has an empty row or column "
            "(row totals %d/%d, column totals %d/%d). With no variation in one "
            "variable there is no association to test." % (a + b, c + d, a + c, b + d))
    return n * (a * d - b * c) ** 2 / denom


def welch(m1, s1, n1, m2, s2, n2):
    """Welch's t-test (unequal variances). Returns (t, df, two-sided p)."""
    v1, v2 = s1 * s1 / n1, s2 * s2 / n2
    t = (m1 - m2) / math.sqrt(v1 + v2)
    # Welch-Satterthwaite degrees of freedom.
    df = (v1 + v2) ** 2 / (v1 * v1 / (n1 - 1) + v2 * v2 / (n2 - 1))
    return t, df, t_two_sided_p(t, df)


def t_critical_95(df, conf=0.95):
    """Two-sided critical t for `conf` coverage, by bisection on t_two_sided_p.

    The module already computes an exact two-sided t p-value; inverting it by
    bisection avoids adding a second, independently-fallible implementation of
    the t distribution. Monotone in t, so bisection converges cleanly.
    """
    alpha = 1.0 - conf
    lo, hi = 0.0, 1000.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if t_two_sided_p(mid, df) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def paired_t(mean_diff, sd_diff, n):
    """Paired t-test on the within-pair differences: a one-sample t against 0.

    The same units are measured under both conditions, so the pairing removes
    between-unit variance and the test uses only the differences. Returns
    (t, df, two-sided p, 95% CI on the mean difference, Cohen's d_z).
    d_z = mean_diff / sd_diff is the paired effect size; it is NOT comparable
    with the two-independent-groups d, which uses the pooled SD.
    """
    if n < 2:
        raise ValueError("paired t-test needs at least 2 pairs")
    if sd_diff <= 0:
        raise ValueError("--sd-diff must be positive")
    df = n - 1
    se = sd_diff / math.sqrt(n)
    t = mean_diff / se
    p = t_two_sided_p(t, df)
    crit = t_critical_95(df)
    lo, hi = mean_diff - crit * se, mean_diff + crit * se
    return t, df, p, (lo, hi), mean_diff / sd_diff


def cohens_d_hedges_g(m1, s1, n1, m2, s2, n2):
    """Cohen's d with pooled SD, plus Hedges' g small-sample correction."""
    df = n1 + n2 - 2
    sp = math.sqrt(((n1 - 1) * s1 * s1 + (n2 - 1) * s2 * s2) / df)
    d = (m1 - m2) / sp
    j = 1.0 - 3.0 / (4.0 * df - 1.0)  # Hedges' correction factor
    return sp, d, j, j * d


def effect_label(v):
    """Cohen's benchmarks: 0.2 small, 0.5 medium, 0.8 large."""
    a = abs(v)
    if a < 0.2: return "negligible"
    if a < 0.5: return "small"
    if a < 0.8: return "medium"
    return "large"


# --- CLI --------------------------------------------------------------------

def _fail(msg):
    raise SystemExit(f"error: {msg}")


def _check_counts(x, n, xname, nname):
    if n <= 0:
        _fail(f"{nname} must be positive, got {n}")
    if not 0 <= x <= n:
        _fail(f"{xname} must be between 0 and {nname}, got {x}/{n}")


def _check_table(a, b, c, d):
    if min(a, b, c, d) < 0:
        _fail("cell counts must be non-negative")
    if a + b + c + d == 0:
        _fail("table is empty")


def _check_mean_args(args):
    if args.n1 < 2 or args.n2 < 2:
        _fail("need n1 >= 2 and n2 >= 2")
    if args.sd1 <= 0 or args.sd2 <= 0:
        _fail("standard deviations must be positive")


def cmd_two_prop(args):
    _check_counts(args.x1, args.n1, "--x1", "--n1")
    _check_counts(args.x2, args.n2, "--x2", "--n2")
    r = two_prop(args.x1, args.n1, args.x2, args.n2)
    print(f"p1 = {r['p1']:.4f} ({args.x1}/{args.n1}), "
          f"p2 = {r['p2']:.4f} ({args.x2}/{args.n2})")
    print(f"z = {r['z']:.3f}, two-sided p = {r['p']:.4f}")
    print(f"95% CI on (p1 - p2): [{r['ci'][0]:.4f}, {r['ci'][1]:.4f}]")
    print(f"Cohen's h = {r['h']:.3f} ({effect_label(r['h'])})")
    if min(args.x1, args.x2, args.n1 - args.x1, args.n2 - args.x2) < 5:
        print("Note: a cell count is < 5; the z-test may be unreliable — "
              "use fisher instead.")
    print(REMINDER)


def cmd_fisher(args):
    """Fisher's exact test on a 2x2 table (two-sided)"""
    a, b, c, d = args.a, args.b, args.c, args.d
    _check_table(a, b, c, d)
    p_obs, p_two = fisher_exact(a, b, c, d)
    print(f"table: [[{a}, {b}], [{c}, {d}]], "
          f"observed-table probability = {p_obs:.6f}")
    print(f"Fisher exact two-sided p = {p_two:.4f}")
    print(REMINDER)


def cmd_chi2(args):
    """Chi-square test on a 2x2 table (df = 1)"""
    a, b, c, d = args.a, args.b, args.c, args.d
    _check_table(a, b, c, d)
    n = a + b + c + d
    try:
        x = chi2_stat(a, b, c, d)
    except ValueError as exc:
        sys.exit("chi2: %s" % exc)
    p = chi2_1df_p(x)
    print(f"table: [[{a}, {b}], [{c}, {d}]]")
    print(f"chi-square = {x:.4f} (df = 1), p = {p:.4f}")
    min_expected = min((a + b) * (a + c), (a + b) * (b + d),
                       (c + d) * (a + c), (c + d) * (b + d)) / n
    if min_expected < 5:
        print(f"Note: smallest expected count is {min_expected:.1f} < 5; "
              "chi-square may be unreliable — use fisher instead.")
    print(REMINDER)


def cmd_welch(args):
    _check_mean_args(args)
    t, df, p = welch(args.mean1, args.sd1, args.n1,
                     args.mean2, args.sd2, args.n2)
    print(f"mean1 = {args.mean1:g} (n = {args.n1}), "
          f"mean2 = {args.mean2:g} (n = {args.n2})")
    print(f"Welch t = {t:.4f}, df = {df:.2f}, two-sided p = {p:.4f}")
    print(REMINDER)


def cmd_paired(args):
    if args.n < 2:
        sys.exit("paired: --n must be at least 2")
    if args.sd_diff <= 0:
        sys.exit("paired: --sd-diff must be positive")
    t, df, p, (lo, hi), dz = paired_t(args.mean_diff, args.sd_diff, args.n)
    print(f"mean difference = {args.mean_diff:g} (sd of differences = {args.sd_diff:g}, "
          f"{args.n} pairs)")
    print(f"paired t = {t:.4f}, df = {df}, two-sided p = {p:.4f}")
    print(f"95% CI on the mean difference = [{lo:.4f}, {hi:.4f}]")
    print(f"Cohen's d_z = {dz:.3f} ({effect_label(dz)}; paired effect size, "
          f"not comparable with the two-group d)")
    print(REMINDER)


def cmd_effect(args):
    _check_mean_args(args)
    sp, d, j, g = cohens_d_hedges_g(args.mean1, args.sd1, args.n1,
                                    args.mean2, args.sd2, args.n2)
    print(f"pooled SD = {sp:.4f}")
    print(f"Cohen's d = {d:.3f} ({effect_label(d)})")
    print(f"Hedges' g = {g:.3f} ({effect_label(g)}; correction J = {j:.4f})")
    print(REMINDER)


def build_parser():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("two-prop", help="pooled two-proportion z-test")
    for flag, helptext in (("--x1", "successes in group 1"),
                           ("--n1", "size of group 1"),
                           ("--x2", "successes in group 2"),
                           ("--n2", "size of group 2")):
        sp.add_argument(flag, type=int, required=True, help=helptext)
    sp.set_defaults(func=cmd_two_prop)

    for name, func in (("fisher", cmd_fisher), ("chi2", cmd_chi2)):
        sp = sub.add_parser(name, help=func.__doc__.splitlines()[0])
        for cell in "abcd":
            sp.add_argument(f"--{cell}", type=int, required=True,
                            help=f"cell {cell} of [[a, b], [c, d]]")
        sp.set_defaults(func=func)

    for name, func, helptext in (
            ("welch", cmd_welch, "Welch's t-test (unequal variances)"),
            ("effect", cmd_effect, "Cohen's d + Hedges' g correction")):
        sp = sub.add_parser(name, help=helptext)
        for k in ("1", "2"):
            sp.add_argument(f"--mean{k}", type=float, required=True)
            sp.add_argument(f"--sd{k}", type=float, required=True)
            sp.add_argument(f"--n{k}", type=int, required=True)
        sp.set_defaults(func=func)

    sp = sub.add_parser("paired", help="paired t-test on within-pair differences")
    sp.add_argument("--mean-diff", type=float, required=True,
                    help="mean of the within-pair differences")
    sp.add_argument("--sd-diff", type=float, required=True,
                    help="standard deviation of the differences (not of either arm)")
    sp.add_argument("--n", type=int, required=True, help="number of PAIRS")
    sp.set_defaults(func=cmd_paired)
    return p


# --- self-test ---------------------------------------------------------------
# Every expected value below was verified by hand or against a canonical
# published source before being encoded (see the comments per check).

def selftest():
    failures, total = [], [0]

    def check(name, got, want, tol):
        total[0] += 1
        ok = math.isclose(got, want, abs_tol=tol)
        print(f"{'PASS' if ok else 'FAIL'}: {name} — got {got:.6g}, "
              f"expected {want:.6g} ± {tol:g}")
        if not ok:
            failures.append(name)

    # chi2 df=1: x = 3.841 (~the 5% critical value 3.84146) must give p ≈ 0.05.
    # Hand check: erfc(sqrt(3.841/2)) = erfc(1.38582) = 0.050014.
    check("chi2 p at x=3.841", chi2_1df_p(3.841), 0.05, 5e-4)

    # chi2 statistic of [[3,1],[1,3]]: X^2 = 8*(3*3-1*1)^2/(4*4*4*4) = 2.0 exactly.
    check("chi2 statistic of [[3,1],[1,3]]", chi2_stat(3, 1, 1, 3), 2.0, 1e-12)

    # Fisher Tea-Tasting table [[3,1],[1,3]] (margins 4,4;4,4). By hand the table
    # probabilities over a = 0..4 are 1/70, 16/70, 36/70, 16/70, 1/70, so the
    # two-sided p = 34/70 = 0.485714. Matches R fisher.test (p = 0.4857).
    _, p_two = fisher_exact(3, 1, 1, 3)
    check("fisher two-sided p of [[3,1],[1,3]]", p_two, 34 / 70, 1e-9)

    # Welch textbook example (Wikipedia, "Welch's t-test"): summary stats
    # computed from the raw samples; published result t ≈ -2.46, df ≈ 24.9,
    # two-sided p ≈ 0.021.
    # Paired t, hand-computable: mean diff 2.0, sd 4.0, n 16
    #   SE = 4/sqrt(16) = 1.0 ; t = 2.0/1.0 = 2.0 ; df = 15
    #   t_crit(.95, 15) = 2.131 -> CI = 2.0 +/- 2.131 = [-0.131, 4.131]
    #   d_z = 2.0/4.0 = 0.5
    pt, pdf, pp_, (plo, phi), pdz = paired_t(2.0, 4.0, 16)
    check("paired t = 2.0", pt, 2.0, 1e-9)
    check("paired df = 15", pdf, 15, 1e-9)
    check("paired d_z = 0.5", pdz, 0.5, 1e-9)
    check("t critical 95%, df=15 (published table 2.131)", t_critical_95(15), 2.131, 1e-3)
    check("paired CI upper", phi, 2.0 + 2.131449 * 1.0, 1e-3)
    check("t critical 95%, df=10 (published table 2.228)", t_critical_95(10), 2.228, 1e-3)

    t, df, p = welch(20.82, 2.804894, 15, 22.986667, 1.952605, 15)
    check("welch t (Wikipedia example)", t, -2.4554, 1e-3)
    check("welch df (Wikipedia example)", df, 24.99, 0.05)
    check("welch p (Wikipedia example)", p, 0.0214, 5e-4)

    # two-prop 30/100 vs 20/100: SE = sqrt(0.25*0.75*0.02) = 0.061237,
    # z = 0.1/0.061237 = 1.6330, p = erfc(1.6330/sqrt(2)) = 0.10247,
    # h = 2*(asin(sqrt(0.3)) - asin(sqrt(0.2))) = 0.23198.
    r = two_prop(30, 100, 20, 100)
    check("two-prop z (30/100 vs 20/100)", r["z"], 1.6330, 1e-3)
    check("two-prop p (30/100 vs 20/100)", r["p"], 0.10247, 5e-4)
    check("two-prop Cohen's h", r["h"], 0.23198, 1e-3)

    # effect: sp = 15, d = -10/15 = -0.6667; df = 58, J = 1 - 3/231 = 0.98701.
    _, d_, _, g_ = cohens_d_hedges_g(100, 15, 30, 110, 15, 30)
    check("effect Cohen's d", d_, -0.6667, 1e-3)
    check("effect Hedges' g", g_, -0.6580, 1e-3)

    # Cross-check the incomplete-beta t CDF against the normal CDF at huge df:
    # t = 1.959964 with df = 1e6 must give p ≈ 0.05 (two-sided z).
    check("t CDF approaches normal at df=1e6",
          t_two_sided_p(1.959964, 1e6), 0.05, 1e-4)

    if failures:
        print(f"{len(failures)} of {total[0]} selftest checks FAILED")
        return 1
    print(f"All {total[0]} selftest checks passed.")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return selftest()
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
