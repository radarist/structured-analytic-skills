#!/usr/bin/env python3
"""power.py — sample size, achieved power, minimum detectable effect and run
duration for the designs in ../SKILL.md (step 3, "Power analysis").

Everything is a closed-form planning approximation; the analysis test used
afterwards must match the design (two-proportion z, Welch/Student t, paired t,
Fisher z). Sources: J. Cohen, Statistical Power Analysis for the Behavioral
Sciences, 2nd ed., 1988 (ch. 2 means, ch. 3 correlation); J.L. Fleiss, B. Levin
& M.C. Paik, Statistical Methods for Rates and Proportions, 3rd ed., 2003 (ch. 4).

Definitions implemented (z_a = z_{1-alpha/2} two-sided, z_{1-alpha} one-sided;
z_b = z_{1-beta}; r = n2/n1 allocation ratio):

  * Two-sample means, Cohen's d = (mu1 - mu2)/sigma  (n-means):
        n1 = (1 + 1/r) * ((z_a + z_b) / d)^2,   n2 = r * n1
    i.e. n = 2 ((z_a + z_b)/d)^2 per group for equal groups (normal
    approximation). --t-correct replaces z by Student-t quantiles with
    df = n1 + n2 - 2 and iterates to the smallest n satisfying the inequality
    (Cohen's tables use the t distribution: 64 per group for d = .50, not 63).
    The t quantile is the Cornish-Fisher expansion in powers of 1/df
    (Abramowitz & Stegun 1964, eq. 26.7.5, four correction terms); checked
    against the exact quantile: |error| < 1e-4 for df >= 10, < 1e-3 for
    df >= 4 at p <= .975.  The t-based power uses the central t as an
    approximation to the noncentral t (same approximation, inverted).
  * Two independent proportions p1, p2, pooled variance under H0
    (Fleiss, Levin & Paik 2003, ch. 4, eq. 4.14 = Fleiss 1981 eq. 3.14):
        n' = [z_a sqrt(2 pbar qbar) + z_b sqrt(p1 q1 + p2 q2)]^2 / (p1 - p2)^2
    unequal allocation (same chapter):
        n1 = [z_a sqrt((r+1) pbar qbar) + z_b sqrt(r p1 q1 + p2 q2)]^2 / (r (p1-p2)^2)
    with pbar = (p1 + r p2)/(r + 1); --continuity applies Fleiss's correction
        n = (n'/4) [1 + sqrt(1 + 2 (r+1) / (n' r |p1 - p2|))]^2   (= 4/(n'|p1-p2|) for r = 1).
  * One-sample mean (n-one-mean) and paired means (n-paired; d = mean
    difference / SD of the differences):  n = ((z_a + z_b) / d)^2, df = n - 1.
  * Pearson r against 0 via Fisher's z (n-corr):
        n = ((z_a + z_b) / atanh(r))^2 + 3.
  * power: the same expressions solved for 1 - beta. Two-sided power omits the
    (negligible) rejection probability in the wrong direction, as the sample-
    size formulas, Cohen's tables and R's power.*.test defaults do.
  * mde: solved for the effect (closed form; bisection on p2 for proportions).
  * duration: days = ceil(n_total / (per_day * allocation)).

Reference values asserted by --selftest and where they were verified:
  * Cohen (1992) "A power primer", Psychological Bulletin 112(1):155-159,
    Table 2 (alpha .05, power .80): d = .20 -> 393; d = .50 -> 64 (t-based;
    normal approximation gives 63); r = .30 -> 85.
  * R stats::power.prop.test documentation examples: p1 = .50, p2 = .75,
    power .90 -> n = 76.7 per group; n = 50 -> power = 0.740.
  * Fleiss, Levin & Paik (2003) p. 74 (P1 = .70, P2 = .60, alpha = .01
    two-sided, continuity-corrected): 827 per group at power .95, 499 at .75;
    pp. 76-77 (P1 = .25, P2 = .40, alpha .01, power .95, n2 = n1/2): 530 and 265.
  * Exact noncentral-t check (numerical integration; matches R power.t.test):
    d = .50, n = 64 per group -> power 0.8015; n = 63 -> 0.795.

Stdlib only. Python 3.9+. Deterministic (no randomness, no clock).

Usage:
    python3 power.py n-means   --d 0.5 [--alpha 0.05 --power 0.8 --sided 2 --ratio 1 --t-correct]
    python3 power.py n-means   --delta 2 --sd 4                # d = delta/sd
    python3 power.py n-props   --p1 0.10 --p2 0.12 [--continuity]
    python3 power.py n-props   --baseline 0.10 --mde 0.02      # p2 = p1 + mde
    python3 power.py n-one-mean --d 0.5      python3 power.py n-paired --delta 3 --sd-diff 6
    python3 power.py n-corr    --r 0.3
    python3 power.py power  means --d 0.5 --n 64
    python3 power.py power  props --p1 0.10 --p2 0.12 --n 3841
    python3 power.py mde    props --p1 0.10 --n 5000
    python3 power.py mde    means --n 100 [--sd 4]
    python3 power.py duration --n-total 7682 --per-day 1714 --allocation 1.0
    python3 power.py --demo          # SKILL.md worked example
    python3 power.py --selftest      # hand-verified assertions
Add --json to any command for machine-readable output.
"""

import argparse
import contextlib
import io
import json
import math
import sys
from statistics import NormalDist

_N01 = NormalDist()

DESIGNS = ("means", "props", "one-mean", "paired", "corr")

REMINDER = (
    "NOTE: planning approximations (Cohen 1988, Statistical Power Analysis for the Behavioral "
    "Sciences, 2nd ed.; Fleiss, Levin & Paik 2003, Statistical Methods for Rates and Proportions, "
    "3rd ed.) - the analysis test must match the design (two-proportion z / Welch t / paired t / Fisher z)."
)

# --- quantiles ---------------------------------------------------------------


def z_quantile(p):
    """Standard normal quantile."""
    return _N01.inv_cdf(p)


def norm_cdf(x):
    return _N01.cdf(x)


def crit_z(alpha, sided):
    """z_{1-alpha/2} for a two-sided test, z_{1-alpha} for one-sided."""
    return z_quantile(1.0 - alpha / sided)


def t_quantile(p, df):
    """Student-t quantile by the Cornish-Fisher expansion in 1/df
    (Abramowitz & Stegun 1964, 26.7.5). Adequate for df >= 4 (see module doc)."""
    z = z_quantile(p)
    g1 = (z ** 3 + z) / 4.0
    g2 = (5 * z ** 5 + 16 * z ** 3 + 3 * z) / 96.0
    g3 = (3 * z ** 7 + 19 * z ** 5 + 17 * z ** 3 - 15 * z) / 384.0
    g4 = (79 * z ** 9 + 776 * z ** 7 + 1482 * z ** 5 - 1920 * z ** 3 - 945 * z) / 92160.0
    return z + g1 / df + g2 / df ** 2 + g3 / df ** 3 + g4 / df ** 4


def t_cdf(x, df):
    """Central-t CDF obtained by inverting t_quantile (monotone in p) with
    bisection; accurate to the quantile approximation, ~1e-12 in p."""
    lo, hi = 1e-12, 1.0 - 1e-12
    if x <= t_quantile(lo, df):
        return 0.0
    if x >= t_quantile(hi, df):
        return 1.0
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if t_quantile(mid, df) < x:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def ceil_int(x):
    """Ceiling that ignores floating-point fuzz just above an integer."""
    return int(math.ceil(x - 1e-9))


def _z_pair(alpha, power, sided):
    za, zb = crit_z(alpha, sided), z_quantile(power)
    if za + zb <= 0:
        raise ValueError("power must exceed the type-I error rate (z_a + z_b <= 0)")
    return za, zb


# --- sample size -------------------------------------------------------------


def n_two_means(d, alpha, power, sided=2, ratio=1.0, t_correct=False):
    """Per-group n for two independent means (Cohen 1988, ch. 2).
    Returns dict(n1, n2, n_raw, df, method)."""
    d = abs(d)
    za, zb = _z_pair(alpha, power, sided)
    k = 1.0 + 1.0 / ratio
    n_raw = k * ((za + zb) / d) ** 2
    n1 = max(2, ceil_int(n_raw))
    if not t_correct:
        return {"n1": n1, "n2": max(2, ceil_int(ratio * n1)), "n_raw": n_raw, "df": None,
                "method": "normal approximation"}

    def need(n1_):
        df = n1_ + max(2, ceil_int(ratio * n1_)) - 2
        return k * ((t_quantile(1 - alpha / sided, df) + t_quantile(power, df)) / d) ** 2

    n1 = _t_fixed_point(n1, need)
    n2 = max(2, ceil_int(ratio * n1))
    return {"n1": n1, "n2": n2, "n_raw": need(n1), "df": n1 + n2 - 2,
            "method": "t-corrected (Cornish-Fisher t quantiles)"}


def _t_fixed_point(n_start, need):
    """Smallest integer n >= n_start with n >= need(n), where need() is a
    decreasing function of n (t quantiles fall as df grows). Deterministic."""
    n = n_start
    for _ in range(10000):
        req = need(n)
        if n + 1e-9 >= req:
            break
        n = max(n + 1, ceil_int(req))
    while n > 2 and (n - 1) + 1e-9 >= need(n - 1):  # undo any overshoot
        n -= 1
    return n


def n_one_mean(d, alpha, power, sided=2, t_correct=False):
    """n for a one-sample mean, or n pairs for paired means (d = delta / SD of
    differences). Cohen 1988, ch. 2 (one-sample case)."""
    d = abs(d)
    za, zb = _z_pair(alpha, power, sided)
    n_raw = ((za + zb) / d) ** 2
    n = max(2, ceil_int(n_raw))
    if not t_correct:
        return {"n": n, "n_raw": n_raw, "df": None, "method": "normal approximation"}

    def need(n_):
        df = n_ - 1
        return ((t_quantile(1 - alpha / sided, df) + t_quantile(power, df)) / d) ** 2

    n = _t_fixed_point(max(n, 3), need)
    return {"n": n, "n_raw": need(n), "df": n - 1, "method": "t-corrected (Cornish-Fisher t quantiles)"}


def n_two_props(p1, p2, alpha, power, sided=2, ratio=1.0, continuity=False):
    """Per-group n for two independent proportions, pooled-variance normal
    approximation (Fleiss, Levin & Paik 2003, ch. 4, eq. 4.14 and its unequal-
    allocation form), optional Fleiss continuity correction."""
    za, zb = _z_pair(alpha, power, sided)
    r = ratio
    delta = abs(p1 - p2)
    pbar = (p1 + r * p2) / (1.0 + r)
    qbar = 1.0 - pbar
    n_raw = (za * math.sqrt((r + 1) * pbar * qbar)
             + zb * math.sqrt(r * p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (r * delta ** 2)
    n_uncorrected = n_raw
    if continuity:
        n_raw = n_raw / 4.0 * (1.0 + math.sqrt(1.0 + 2.0 * (r + 1) / (n_raw * r * delta))) ** 2
    n1 = max(2, ceil_int(n_raw))
    return {"n1": n1, "n2": max(2, ceil_int(r * n1)), "n_raw": n_raw, "n_raw_uncorrected": n_uncorrected,
            "method": "pooled-variance normal approximation"
                      + (" + Fleiss continuity correction" if continuity else "")}


def n_corr(r, alpha, power, sided=2):
    """n to detect Pearson r != 0 via Fisher's z (Cohen 1988, ch. 3)."""
    za, zb = _z_pair(alpha, power, sided)
    n_raw = ((za + zb) / math.atanh(abs(r))) ** 2 + 3.0
    return {"n": max(4, ceil_int(n_raw)), "n_raw": n_raw, "method": "Fisher z approximation"}


# --- achieved power ----------------------------------------------------------


def power_two_means(d, n1, n2, alpha, sided=2, t_correct=False):
    lam = abs(d) / math.sqrt(1.0 / n1 + 1.0 / n2)
    if t_correct:
        df = n1 + n2 - 2
        return 1.0 - t_cdf(t_quantile(1 - alpha / sided, df) - lam, df)
    return norm_cdf(lam - crit_z(alpha, sided))


def power_one_mean(d, n, alpha, sided=2, t_correct=False):
    lam = abs(d) * math.sqrt(n)
    if t_correct:
        df = n - 1
        return 1.0 - t_cdf(t_quantile(1 - alpha / sided, df) - lam, df)
    return norm_cdf(lam - crit_z(alpha, sided))


def power_two_props(p1, p2, n1, n2, alpha, sided=2, continuity=False):
    """Power of the pooled two-proportion z test (R power.prop.test formula,
    generalised to unequal n; continuity subtracts (1/n1 + 1/n2)/2 from |p1-p2|)."""
    delta = abs(p1 - p2)
    pbar = (n1 * p1 + n2 * p2) / (n1 + n2)
    se0 = math.sqrt(pbar * (1 - pbar) * (1.0 / n1 + 1.0 / n2))
    se1 = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    c = 0.5 * (1.0 / n1 + 1.0 / n2) if continuity else 0.0
    return norm_cdf((delta - c - crit_z(alpha, sided) * se0) / se1)


def power_corr(r, n, alpha, sided=2):
    lam = math.atanh(abs(r)) * math.sqrt(n - 3)
    return norm_cdf(lam - crit_z(alpha, sided))


# --- minimum detectable effect -----------------------------------------------


def mde_two_means(n1, n2, alpha, power, sided=2, t_correct=False):
    za, zb = _z_pair(alpha, power, sided)
    if t_correct:
        df = n1 + n2 - 2
        za, zb = t_quantile(1 - alpha / sided, df), t_quantile(power, df)
    return (za + zb) * math.sqrt(1.0 / n1 + 1.0 / n2)


def mde_one_mean(n, alpha, power, sided=2, t_correct=False):
    za, zb = _z_pair(alpha, power, sided)
    if t_correct:
        za, zb = t_quantile(1 - alpha / sided, n - 1), t_quantile(power, n - 1)
    return (za + zb) / math.sqrt(n)


def mde_corr(n, alpha, power, sided=2):
    za, zb = _z_pair(alpha, power, sided)
    return math.tanh((za + zb) / math.sqrt(n - 3))


def mde_two_props(p1, n1, n2, alpha, power, sided=2, continuity=False, direction="up"):
    """Smallest p2 (above p1 for 'up', below for 'down') whose difference from
    p1 is detected with the requested power at n1, n2. Bisection on the power
    function (monotone in |p2 - p1|); None if not reachable inside (0, 1)."""
    _z_pair(alpha, power, sided)
    lo, hi = 0.0, (1.0 - p1 if direction == "up" else p1)

    def pw(delta):
        p2 = p1 + delta if direction == "up" else p1 - delta
        return power_two_props(p1, p2, n1, n2, alpha, sided, continuity)

    if pw(hi * (1 - 1e-9)) < power:
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if pw(mid) < power:
            lo = mid
        else:
            hi = mid
    delta = 0.5 * (lo + hi)
    return p1 + delta if direction == "up" else p1 - delta


def cohen_h(p1, p2):
    return abs(2 * math.asin(math.sqrt(p2)) - 2 * math.asin(math.sqrt(p1)))


def duration_days(n_total, per_day, allocation):
    enrolled_per_day = per_day * allocation
    days = ceil_int(n_total / enrolled_per_day)
    return {"days": days, "weeks": ceil_int(days / 7.0), "enrolled_per_day": enrolled_per_day}


# --- CLI helpers -------------------------------------------------------------


def fail(msg):
    """Usage / invalid-input error: exit 2 (1 is reserved for a failing verdict)."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def emit(payload, as_json, lines):
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for line in lines:
            print(line)
        print(REMINDER)


def check_common(args):
    if not 0.0 < args.alpha < 1.0:
        fail(f"--alpha must be in (0, 1); got {args.alpha}")
    if not 0.0 < args.power < 1.0:
        fail(f"--power must be in (0, 1); got {args.power}")
    try:
        _z_pair(args.alpha, args.power, args.sided)
    except ValueError as exc:
        fail(str(exc))


def check_ratio(args):
    if getattr(args, "ratio", 1.0) <= 0:
        fail(f"--ratio must be > 0; got {args.ratio}")


def resolve_d(args, sd_flag="sd"):
    """Cohen's d from --d, or --delta with --sd (or --sd-diff)."""
    sd = getattr(args, sd_flag.replace("-", "_"), None)
    if args.d is not None:
        if args.delta is not None or sd is not None:
            fail(f"give either --d or --delta with --{sd_flag}, not both")
        d = args.d
    elif args.delta is not None:
        if sd is None:
            fail(f"--delta needs --{sd_flag}")
        if sd <= 0:
            fail(f"--{sd_flag} must be > 0")
        d = args.delta / sd
    else:
        fail(f"give --d, or --delta with --{sd_flag}")
    if d == 0:
        fail("effect size must be non-zero (d = 0 needs infinite n)")
    return d


def resolve_props(args, need_p2=True):
    p1 = args.p1
    if p1 is None:
        fail("give --p1 (alias --baseline)")
    if not 0.0 < p1 < 1.0:
        fail(f"--p1 must be in (0, 1); got {p1}")
    if not need_p2:
        return p1, None
    if args.p2 is not None and args.mde is not None:
        fail("give either --p2 or --mde, not both")
    if args.p2 is not None:
        p2 = args.p2
    elif args.mde is not None:
        p2 = round(p1 + args.mde, 12)  # 0.10 + 0.02 -> 0.12, not 0.12000000000000001
    else:
        fail("give --p2, or --mde (absolute difference added to --p1)")
    if not 0.0 < p2 < 1.0:
        fail(f"p2 must be in (0, 1); got {p2}")
    if p1 == p2:
        fail("p1 == p2: no effect to detect (infinite n)")
    return p1, p2


def resolve_r(args):
    if args.r is None:
        fail("give --r")
    if not -1.0 < args.r < 1.0 or args.r == 0:
        fail(f"--r must be in (-1, 1) and non-zero; got {args.r}")
    return args.r


def check_n(n, minimum=2, flag="--n"):
    if n is None:
        fail(f"give {flag}")
    if n < minimum:
        fail(f"{flag} must be >= {minimum}; got {n}")


def fmt_alpha(args):
    return f"alpha = {args.alpha:g} {'two' if args.sided == 2 else 'one'}-sided"


def _sizes_line(n1, n2):
    if n1 == n2:
        return f"n per group: {n1}  (total {n1 + n2})"
    return f"n1 = {n1}, n2 = {n2}  (total {n1 + n2})"


def _tag(t_correct):
    return " [t-corrected]" if t_correct else " [normal approximation]"


def _props_tag(continuity):
    return " [pooled z, continuity-corrected]" if continuity else " [pooled z]"


def _single_title(design):
    return "One-sample mean" if design == "one-mean" else "Paired means"


# --- commands ----------------------------------------------------------------


def cmd_n_means(args):
    check_common(args)
    check_ratio(args)
    d = resolve_d(args)
    res = n_two_means(d, args.alpha, args.power, args.sided, args.ratio, args.t_correct)
    pw = power_two_means(d, res["n1"], res["n2"], args.alpha, args.sided, args.t_correct)
    payload = {"command": "n-means", "d": d, "alpha": args.alpha, "power_target": args.power,
               "sided": args.sided, "ratio": args.ratio, "t_correct": args.t_correct,
               "method": res["method"], "n1": res["n1"], "n2": res["n2"], "n_total": res["n1"] + res["n2"],
               "n_raw": res["n_raw"], "df": res["df"], "power_at_n": pw}
    lines = [f"Two-sample means, Cohen's d = {d:.4g}  [{res['method']}]",
             f"  {fmt_alpha(args)}, power = {args.power:g}, ratio n2/n1 = {args.ratio:g}",
             f"  {_sizes_line(res['n1'], res['n2'])}   unrounded {res['n_raw']:.2f}"
             + (f", df = {res['df']}" if res["df"] is not None else ""),
             f"  achieved power at these n: {pw:.4f}"]
    if res["df"] is not None and res["df"] < 5:
        lines.append("  warning: df < 5, the t-quantile approximation is rough here")
    emit(payload, args.json, lines)


def cmd_n_props(args):
    check_common(args)
    check_ratio(args)
    p1, p2 = resolve_props(args)
    res = n_two_props(p1, p2, args.alpha, args.power, args.sided, args.ratio, args.continuity)
    pw = power_two_props(p1, p2, res["n1"], res["n2"], args.alpha, args.sided, args.continuity)
    mde_abs, mde_rel, h = p2 - p1, (p2 - p1) / p1, cohen_h(p1, p2)
    payload = {"command": "n-props", "p1": p1, "p2": p2, "mde_abs": mde_abs, "mde_rel": mde_rel,
               "cohen_h": h, "alpha": args.alpha, "power_target": args.power, "sided": args.sided,
               "ratio": args.ratio, "continuity": args.continuity, "method": res["method"],
               "n1": res["n1"], "n2": res["n2"], "n_total": res["n1"] + res["n2"], "n_raw": res["n_raw"],
               "n_raw_uncorrected": res["n_raw_uncorrected"], "power_at_n": pw}
    lines = [f"Two independent proportions  [{res['method']}]",
             f"  p1 = {p1:.4g}, p2 = {p2:.4g}: MDE {mde_abs:+.4g} absolute ({mde_rel:+.1%} relative), "
             f"Cohen's h = {h:.3f}",
             f"  {fmt_alpha(args)}, power = {args.power:g}, ratio n2/n1 = {args.ratio:g}",
             f"  {_sizes_line(res['n1'], res['n2'])}   unrounded {res['n_raw']:.2f}",
             f"  achieved power at these n: {pw:.4f}"]
    emit(payload, args.json, lines)


def cmd_n_single(args, kind):
    """n-one-mean and n-paired share the formula; kind labels the output."""
    check_common(args)
    d = resolve_d(args, "sd" if kind == "one-mean" else "sd-diff")
    res = n_one_mean(d, args.alpha, args.power, args.sided, args.t_correct)
    pw = power_one_mean(d, res["n"], args.alpha, args.sided, args.t_correct)
    unit = "n" if kind == "one-mean" else "n pairs"
    payload = {"command": "n-" + kind, "d": d, "alpha": args.alpha, "power_target": args.power,
               "sided": args.sided, "t_correct": args.t_correct, "method": res["method"],
               "n": res["n"], "n_raw": res["n_raw"], "df": res["df"], "power_at_n": pw}
    title = "One-sample mean" if kind == "one-mean" else "Paired means (d = mean difference / SD of differences)"
    lines = [f"{title}, d = {d:.4g}  [{res['method']}]",
             f"  {fmt_alpha(args)}, power = {args.power:g}",
             f"  {unit}: {res['n']}   unrounded {res['n_raw']:.2f}"
             + (f", df = {res['df']}" if res["df"] is not None else ""),
             f"  achieved power at this n: {pw:.4f}"]
    if res["df"] is not None and res["df"] < 5:
        lines.append("  warning: df < 5, the t-quantile approximation is rough here")
    emit(payload, args.json, lines)


def cmd_n_corr(args):
    check_common(args)
    r = resolve_r(args)
    res = n_corr(r, args.alpha, args.power, args.sided)
    pw = power_corr(r, res["n"], args.alpha, args.sided)
    payload = {"command": "n-corr", "r": r, "alpha": args.alpha, "power_target": args.power,
               "sided": args.sided, "method": res["method"], "n": res["n"], "n_raw": res["n_raw"],
               "power_at_n": pw}
    lines = [f"Pearson correlation r = {r:g} vs 0  [{res['method']}]",
             f"  {fmt_alpha(args)}, power = {args.power:g}",
             f"  n: {res['n']}   unrounded {res['n_raw']:.2f}",
             f"  achieved power at this n: {pw:.4f}"]
    emit(payload, args.json, lines)


def _n_pair(args):
    check_n(args.n)
    n2 = args.n2 if args.n2 is not None else max(2, ceil_int(args.ratio * args.n))
    check_n(n2, flag="--n2")
    return args.n, n2


def cmd_power(args):
    check_common(args)
    check_ratio(args)
    design = args.design
    if design == "means":
        d = resolve_d(args)
        n1, n2 = _n_pair(args)
        pw = power_two_means(d, n1, n2, args.alpha, args.sided, args.t_correct)
        payload = {"design": design, "d": d, "n1": n1, "n2": n2, "t_correct": args.t_correct}
        head = f"Two-sample means, d = {d:.4g}, n1 = {n1}, n2 = {n2}" + _tag(args.t_correct)
    elif design == "props":
        p1, p2 = resolve_props(args)
        n1, n2 = _n_pair(args)
        pw = power_two_props(p1, p2, n1, n2, args.alpha, args.sided, args.continuity)
        payload = {"design": design, "p1": p1, "p2": p2, "n1": n1, "n2": n2, "continuity": args.continuity}
        head = f"Two proportions p1 = {p1:.4g}, p2 = {p2:.4g}, n1 = {n1}, n2 = {n2}" + _props_tag(args.continuity)
    elif design in ("one-mean", "paired"):
        d = resolve_d(args, "sd" if design == "one-mean" else "sd-diff")
        check_n(args.n)
        pw = power_one_mean(d, args.n, args.alpha, args.sided, args.t_correct)
        payload = {"design": design, "d": d, "n": args.n, "t_correct": args.t_correct}
        head = f"{_single_title(design)}, d = {d:.4g}, n = {args.n}" + _tag(args.t_correct)
    else:  # corr
        r = resolve_r(args)
        check_n(args.n, minimum=4)
        pw = power_corr(r, args.n, args.alpha, args.sided)
        payload = {"design": design, "r": r, "n": args.n}
        head = f"Correlation r = {r:g}, n = {args.n} [Fisher z]"
    payload.update({"command": "power", "alpha": args.alpha, "sided": args.sided, "power": pw})
    emit(payload, args.json, [head, f"  {fmt_alpha(args)}", f"  achieved power: {pw:.4f}"])


def cmd_mde(args):
    check_common(args)
    check_ratio(args)
    design = args.design
    if design == "means":
        n1, n2 = _n_pair(args)
        d = mde_two_means(n1, n2, args.alpha, args.power, args.sided, args.t_correct)
        payload = {"design": design, "n1": n1, "n2": n2, "mde_d": d, "t_correct": args.t_correct}
        lines = [f"Two-sample means, n1 = {n1}, n2 = {n2}" + _tag(args.t_correct),
                 f"  {fmt_alpha(args)}, power = {args.power:g}", f"  minimum detectable d: {d:.4f}"]
        if args.sd is not None:
            if args.sd <= 0:
                fail("--sd must be > 0")
            payload["mde_delta"] = d * args.sd
            lines.append(f"  = {d * args.sd:.4g} in raw units (sd = {args.sd:g})")
    elif design == "props":
        p1, _ = resolve_props(args, need_p2=False)
        n1, n2 = _n_pair(args)
        p2 = mde_two_props(p1, n1, n2, args.alpha, args.power, args.sided, args.continuity, args.direction)
        if p2 is None:
            print(f"Two proportions, p1 = {p1:.4g}, n1 = {n1}, n2 = {n2}: "
                  f"no p2 in (0, 1) reaches power {args.power:g}", file=sys.stderr)
            sys.exit(2)
        payload = {"design": design, "p1": p1, "n1": n1, "n2": n2, "direction": args.direction,
                   "continuity": args.continuity, "mde_p2": p2, "mde_abs": p2 - p1, "mde_rel": (p2 - p1) / p1,
                   "cohen_h": cohen_h(p1, p2)}
        lines = [f"Two proportions, p1 = {p1:.4g}, n1 = {n1}, n2 = {n2}, direction = {args.direction}"
                 + _props_tag(args.continuity),
                 f"  {fmt_alpha(args)}, power = {args.power:g}",
                 f"  minimum detectable p2: {p2:.4f}  = {p2 - p1:+.4f} absolute ({(p2 - p1) / p1:+.1%} relative), "
                 f"Cohen's h = {cohen_h(p1, p2):.3f}"]
    elif design in ("one-mean", "paired"):
        check_n(args.n)
        d = mde_one_mean(args.n, args.alpha, args.power, args.sided, args.t_correct)
        payload = {"design": design, "n": args.n, "mde_d": d, "t_correct": args.t_correct}
        lines = [f"{_single_title(design)}, n = {args.n}" + _tag(args.t_correct),
                 f"  {fmt_alpha(args)}, power = {args.power:g}", f"  minimum detectable d: {d:.4f}"]
        sd = args.sd if design == "one-mean" else args.sd_diff
        if sd is not None:
            if sd <= 0:
                fail("sd must be > 0")
            payload["mde_delta"] = d * sd
            lines.append(f"  = {d * sd:.4g} in raw units (sd = {sd:g})")
    else:  # corr
        check_n(args.n, minimum=4)
        r = mde_corr(args.n, args.alpha, args.power, args.sided)
        payload = {"design": design, "n": args.n, "mde_r": r}
        lines = [f"Correlation, n = {args.n} [Fisher z]", f"  {fmt_alpha(args)}, power = {args.power:g}",
                 f"  minimum detectable |r|: {r:.4f}"]
    payload.update({"command": "mde", "alpha": args.alpha, "power_target": args.power, "sided": args.sided})
    emit(payload, args.json, lines)


def cmd_duration(args):
    if args.n_total <= 0:
        fail("--n-total must be > 0")
    if args.per_day <= 0:
        fail("--per-day must be > 0")
    if not 0.0 < args.allocation <= 1.0:
        fail(f"--allocation must be in (0, 1]; got {args.allocation}")
    res = duration_days(args.n_total, args.per_day, args.allocation)
    payload = {"command": "duration", "n_total": args.n_total, "per_day": args.per_day,
               "allocation": args.allocation, "enrolled_per_day": res["enrolled_per_day"],
               "days": res["days"], "weeks": res["weeks"]}
    lines = [f"Duration: {args.n_total:g} units at {args.per_day:g} eligible/day x allocation {args.allocation:g}"
             f" = {res['enrolled_per_day']:.1f} enrolled/day",
             f"  days needed: {res['days']}  (whole weeks: {res['weeks']}; "
             "fixed horizon - decide the stop rule now, no peeking)"]
    emit(payload, args.json, lines)


# --- demo & selftest ---------------------------------------------------------


def run_demo(as_json):
    """SKILL.md worked example: one-click checkout, 7-day conversion 10% -> 12%
    (+2pp, +20% relative), alpha .05 two-sided, power .80, ~12k eligible
    users/week (1714/day)."""
    calls = [["n-props", "--p1", "0.10", "--p2", "0.12"],
             ["duration", "--n-total", "7682", "--per-day", "1714", "--allocation", "1.0"]]
    if as_json:  # one JSON document keyed by command
        out = {}
        for argv in calls:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                main(argv + ["--json"])
            out[argv[0]] = json.loads(buf.getvalue())
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    print("Demo - SKILL.md worked example: one-click checkout, conversion 0.10 -> 0.12")
    for argv in calls:
        print("$ python3 power.py " + " ".join(argv))
        main(argv)
    return 0


def run_selftest():
    """Hand-verified assertions. Sources for every expected value are listed in
    the module docstring ("Reference values")."""
    checks = []

    def check(name, got, want, tol=0):
        ok = abs(got - want) <= tol
        checks.append(ok)
        shown = f"got {got:.6g}, expected {want:.6g}" + (f" (tol {tol:g})" if tol else "")
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {shown}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    A, P = 0.05, 0.80
    # Cohen (1992) Table 2, alpha .05 two-sided, power .80.
    check("Cohen 1992 Tbl 2: two-sample d=.50 -> 64 (t-based)", n_two_means(0.5, A, P, t_correct=True)["n1"], 64)
    check("two-sample d=.50 normal approx -> 63", n_two_means(0.5, A, P)["n1"], 63)
    check("two-sample d=.50 normal unrounded 62.79", n_two_means(0.5, A, P)["n_raw"], 62.791, 0.001)
    check("Cohen 1992 Tbl 2: two-sample d=.20 -> 393 (normal)", n_two_means(0.2, A, P)["n1"], 393)
    check("two-sample d=.20 t-corrected -> 394 (R power.t.test 393.4)",
          n_two_means(0.2, A, P, t_correct=True)["n1"], 394)
    check("Cohen 1992 Tbl 2: r=.30 -> 85 (Fisher z 84.93)", n_corr(0.3, A, P)["n"], 85)
    check("Fisher z unrounded 84.93", n_corr(0.3, A, P)["n_raw"], 84.928, 0.001)
    # One-sample / paired: ((1.95996 + 0.84162)/0.5)^2 = 31.40 -> 32.
    check("one-sample d=.50 normal -> 32", n_one_mean(0.5, A, P)["n"], 32)
    check("one-sample d=.50 t-corrected -> 34 (R power.t.test 33.37)", n_one_mean(0.5, A, P, t_correct=True)["n"], 34)
    check("paired dz=.50 normal -> 32 (same formula)", n_one_mean(2.0 / 4.0, A, P)["n"], 32)
    # Two proportions, pooled (Fleiss et al. 2003 eq. 4.14): SKILL.md worked example.
    res = n_two_props(0.10, 0.12, A, P)
    check("two-prop .10 vs .12 -> 3841 per group", res["n1"], 3841)
    check("two-prop .10 vs .12 unrounded 3840.85", res["n_raw"], 3840.847, 0.001)
    check("two-prop .10 vs .12 + continuity -> 3941", n_two_props(0.10, 0.12, A, P, continuity=True)["n1"], 3941)
    check("--mde alias: p2 = p1 + 0.02 gives same n", n_two_props(0.10, 0.10 + 0.02, A, P)["n1"], 3841)
    # R power.prop.test documentation examples (pooled variance, no continuity).
    check("R power.prop.test: p1=.5 p2=.75 power .9 -> n = 76.7", n_two_props(0.5, 0.75, A, 0.9)["n_raw"], 76.7, 0.05)
    check("R power.prop.test: n=50 p1=.5 p2=.75 -> power 0.740", power_two_props(0.5, 0.75, 50, 50, A), 0.740, 0.0005)
    # Fleiss, Levin & Paik (2003) p. 74, continuity-corrected, alpha .01 two-sided.
    check("Fleiss 2003 p.74: .70 vs .60, power .95, CC -> 827",
          n_two_props(0.7, 0.6, 0.01, 0.95, continuity=True)["n1"], 827)
    check("Fleiss 2003 p.74: .70 vs .60, power .75, CC -> 499.4 (Fleiss 499)",
          n_two_props(0.7, 0.6, 0.01, 0.75, continuity=True)["n_raw"], 499.39, 0.01)
    # Fleiss, Levin & Paik (2003) pp. 76-77, unequal allocation n2 = n1/2, CC.
    res = n_two_props(0.25, 0.40, 0.01, 0.95, ratio=0.5, continuity=True)
    check("Fleiss 2003 pp.76-77: n1 unrounded 530.08 (Fleiss 530)", res["n_raw"], 530.08, 0.01)
    check("Fleiss 2003 pp.76-77: n2 = 266 (= 0.5 * 531 rounded up; Fleiss 265)", res["n2"], 266)
    check("power at n1=531,n2=266 >= .95",
          float(power_two_props(0.25, 0.40, 531, 266, 0.01, 2, True) >= 0.95), 1.0)
    check("power at n1=530,n2=265 < .95 (PASS: 'slightly less')",
          float(power_two_props(0.25, 0.40, 530, 265, 0.01, 2, True) < 0.95), 1.0)
    # Achieved power.
    check("power d=.5, n=64/group, normal -> 0.8074", power_two_means(0.5, 64, 64, A), 0.8074, 0.0005)
    check("power d=.5, n=64/group, t-corrected ~ 0.8015 (exact noncentral t)",
          power_two_means(0.5, 64, 64, A, t_correct=True), 0.8015, 0.002)
    check("power d=.5, n=63/group, t-corrected < 0.80 (exact 0.795)",
          float(power_two_means(0.5, 63, 63, A, t_correct=True) < 0.80), 1.0)
    check("power r=.3, n=85 >= .80", float(power_corr(0.3, 85, A) >= 0.80), 1.0)
    check("one-sided power >= two-sided",
          float(power_two_means(0.5, 64, 64, A, sided=1) > power_two_means(0.5, 64, 64, A)), 1.0)
    check("one-sided n <= two-sided n (d=.5: 50 vs 63)", n_two_means(0.5, A, P, sided=1)["n1"], 50)
    # Unequal allocation for means: n1 = (1 + 1/r)((z_a+z_b)/d)^2 -> r = 2: 47.09 -> 48, n2 = 96.
    res = n_two_means(0.5, A, P, ratio=2.0)
    check("means ratio 2: n1 = 48", res["n1"], 48)
    check("means ratio 2: n2 = 96", res["n2"], 96)
    # MDE round trips.
    check("mde means n=63 -> d = 0.4992", mde_two_means(63, 63, A, P), 0.4992, 0.0005)
    check("mde one-mean n=32 -> d = 0.4953", mde_one_mean(32, A, P), 0.4953, 0.0005)
    check("mde corr n=85 -> r = 0.2999", mde_corr(85, A, P), 0.2999, 0.0005)
    p2 = mde_two_props(0.10, 3841, 3841, A, P)
    check("mde props n=3841, p1=.10 -> p2 = 0.1200", p2, 0.1200, 0.0001)
    p2 = mde_two_props(0.10, 5000, 5000, A, P)
    check("mde props n=5000, p1=.10 -> +0.0175 abs (17.5% rel)", p2 - 0.10, 0.0175, 0.0002)
    check("mde props direction down: p2 < p1",
          float(mde_two_props(0.10, 5000, 5000, A, P, direction="down") < 0.10), 1.0)
    check("mde props unreachable -> None", float(mde_two_props(0.999, 5, 5, A, P) is None), 1.0)
    # t-quantile approximation vs tabled exact values (Abramowitz & Stegun Table 26.10).
    check("t_.975,10 = 2.2281", t_quantile(0.975, 10), 2.2281, 0.0005)
    check("t_.975,30 = 2.0423", t_quantile(0.975, 30), 2.0423, 0.0005)
    check("t_.995,4 = 4.6041", t_quantile(0.995, 4), 4.6041, 0.011)
    check("t_cdf inverts t_quantile", t_cdf(t_quantile(0.9, 12), 12), 0.9, 1e-9)
    # Duration.
    check("duration 7682 units at 1714/day -> 5 days", duration_days(7682, 1714, 1.0)["days"], 5)
    check("duration allocation .5 doubles days -> 9", duration_days(7682, 1714, 0.5)["days"], 9)
    # Invalid inputs exit 1; --json parses; determinism of the CLI path.
    for argv in (["n-means", "--d", "0.5", "--alpha", "1.5"], ["n-means", "--d", "0"],
                 ["n-props", "--p1", "0", "--p2", "0.1"], ["n-props", "--p1", "0.1", "--p2", "0.1"],
                 ["n-corr", "--r", "1"], ["power", "means", "--d", "0.5", "--n", "1"],
                 ["n-means", "--d", "0.5", "--power", "0.02"], ["duration", "--n-total", "10", "--per-day", "0"],
                 ["n-means", "--d", "0.5", "--ratio", "0"], ["bogus"]):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                main(argv)
                code = 0
            except SystemExit as exc:
                code = exc.code
        check(f"usage error exits 2: {' '.join(argv)}", code, 2)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        main(["n-props", "--p1", "0.10", "--p2", "0.12", "--json"])
    data = json.loads(buf.getvalue())
    check("--json: n1 key", data["n1"], 3841)
    check("--json: relative MDE", data["mde_rel"], 0.20, 1e-9)
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        main(["n-props", "--baseline", "0.10", "--mde", "0.02", "--json"])
    check("aliases --baseline/--mde give identical JSON", float(buf.getvalue() == buf2.getvalue()), 1.0)

    print(f"ALL {len(checks)} CHECKS PASSED")
    print("selftest OK")
    return 0


# --- parser ------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(description="Sample size, achieved power, minimum detectable effect and run duration "
                                "for two-sample means, two proportions, one-sample/paired means and correlations "
                                "(planning approximations: Cohen 1988; Fleiss, Levin & Paik 2003).")
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true", help="reproduce the SKILL.md worked example")
    parser.add_argument("--json", action="store_true", help="(with --demo) machine-readable output")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--alpha", type=float, default=0.05, help="type-I error rate (default 0.05)")
    common.add_argument("--power", type=float, default=0.80, help="target power 1-beta (default 0.80)")
    common.add_argument("--sided", type=int, choices=(1, 2), default=2, help="1- or 2-sided test (default 2)")
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="machine-readable output")

    def add_d(p, sd_flag="--sd"):
        p.add_argument("--d", type=float, help="standardized effect (Cohen's d)")
        p.add_argument("--delta", type=float, help="raw effect; give with " + sd_flag)
        p.add_argument(sd_flag, type=float, help="standard deviation for --delta")
        p.add_argument("--t-correct", action="store_true", help="use Student-t quantiles (small-sample correction)")

    def add_ratio(p):
        p.add_argument("--ratio", "--allocation-ratio", dest="ratio", type=float, default=1.0,
                       help="allocation ratio n2/n1 (default 1)")

    def add_props(p, need_p2=True):
        p.add_argument("--p1", "--baseline", dest="p1", type=float, help="control / baseline proportion")
        if need_p2:
            p.add_argument("--p2", type=float, help="treatment proportion")
            p.add_argument("--mde", type=float, help="absolute difference: p2 = p1 + mde (alternative to --p2)")
        p.add_argument("--continuity", action="store_true", help="Fleiss continuity correction")

    def add_r(p):
        p.add_argument("--r", type=float, help="Pearson correlation under H1 (non-zero, in (-1, 1))")

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    p = sub.add_parser("n-means", aliases=["means"], parents=[common], help="n per group, two independent means")
    add_d(p)
    add_ratio(p)
    p = sub.add_parser("n-props", aliases=["props"], parents=[common],
                       help="n per group, two independent proportions")
    add_props(p)
    add_ratio(p)
    p = sub.add_parser("n-one-mean", parents=[common], help="n, one-sample mean vs a constant")
    add_d(p)
    p = sub.add_parser("n-paired", parents=[common], help="n pairs, paired means (d = mean diff / SD of diffs)")
    add_d(p, "--sd-diff")
    p = sub.add_parser("n-corr", parents=[common], help="n, Pearson r vs 0 (Fisher z)")
    add_r(p)

    for name, helptext in (("power", "achieved power at a given n"),
                           ("mde", "minimum detectable effect at a given n")):
        p = sub.add_parser(name, help=helptext)
        dsub = p.add_subparsers(dest="design", metavar="DESIGN")
        for design in DESIGNS:
            q = dsub.add_parser(design, parents=[common], help=f"{design} design")
            q.add_argument("--n", type=int, help="n in group 1 (per group / pairs / total for corr)")
            if design in ("means", "props"):
                q.add_argument("--n2", type=int, help="n in group 2 (default ratio * n)")
                add_ratio(q)
            if design == "means":
                add_d(q)
            elif design == "props":
                add_props(q, need_p2=(name == "power"))
                if name == "mde":
                    q.add_argument("--direction", choices=("up", "down"), default="up",
                                   help="detect an increase (default) or a decrease from p1")
            elif design in ("one-mean", "paired"):
                add_d(q, "--sd" if design == "one-mean" else "--sd-diff")
            else:
                add_r(q)

    p = sub.add_parser("duration", parents=[common], help="days needed to enrol n_total units")
    p.add_argument("--n-total", type=float, required=True, help="total units across all arms")
    p.add_argument("--per-day", type=float, required=True, help="eligible units per day")
    p.add_argument("--allocation", type=float, default=1.0,
                   help="fraction of eligible traffic enrolled (default 1.0)")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo:
        return run_demo(args.json)
    if not args.command:
        parser.error("choose a command: n-means | n-props | n-one-mean | n-paired | n-corr | power | mde | duration "
                     "(or --demo / --selftest)")
    if not hasattr(args, "json"):
        args.json = False
    cmd = args.command
    if cmd in ("n-means", "means"):
        cmd_n_means(args)
    elif cmd in ("n-props", "props"):
        cmd_n_props(args)
    elif cmd == "n-one-mean":
        cmd_n_single(args, "one-mean")
    elif cmd == "n-paired":
        cmd_n_single(args, "paired")
    elif cmd == "n-corr":
        cmd_n_corr(args)
    elif cmd in ("power", "mde"):
        if not args.design:
            parser.error(f"{cmd} needs a design: " + " | ".join(DESIGNS))
        (cmd_power if cmd == "power" else cmd_mde)(args)
    else:
        cmd_duration(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
