#!/usr/bin/env python3
"""metapool.py -- meta-analytic pooling of effect sizes (stdlib only).

Reads a JSON or CSV file of studies, each with an effect size and either a
standard error or a 95% CI (SE derived as width / (2*1.96)), and reports:
fixed-effect inverse-variance pooled estimate + 95% CI; DerSimonian-Laird
random-effects estimate + CI; Cochran's Q (with chi-square p), I^2, tau^2;
a text forest table; and Egger's regression test for funnel asymmetry.

JSON: [{"study": "A", "effect": 0.5, "se": 0.2}, ...]  (or {"studies": [...]})
      "ci_low"/"ci_high" may replace "se".
CSV:  study,effect,se          or          study,effect,ci_low,ci_high

Usage:  python3 metapool.py --file studies.json
        python3 metapool.py --selftest
"""

import argparse
import csv
import json
import math
import sys

Z95 = 1.959963984540054  # two-sided 95% normal quantile (1.96)


# --- Input loading -----------------------------------------------------------

def load_studies(path):
    """Load studies from JSON or CSV; return list of dicts with name/y/se."""
    with open(path, "r", newline="") as fh:
        text = fh.read()
    if path.lower().endswith(".json"):
        rows = _from_json(text)
    elif path.lower().endswith(".csv"):
        rows = _from_csv(text)
    else:  # sniff: try JSON first, then CSV
        try:
            rows = _from_json(text)
        except (ValueError, KeyError):
            rows = _from_csv(text)
    studies = []
    for i, row in enumerate(rows):
        name = str(row.get("study") or row.get("name") or "S%d" % (i + 1))
        y = float(row["effect"])
        if row.get("se") not in (None, ""):
            se = float(row["se"])
        elif row.get("ci_low") not in (None, "") and row.get("ci_high") not in (None, ""):
            se = (float(row["ci_high"]) - float(row["ci_low"])) / (2.0 * Z95)
        else:
            raise ValueError("study %r: need 'se' or 'ci_low'+'ci_high'" % name)
        if not math.isfinite(se):
            raise ValueError(
                "study %r: SE is %r. NaN and infinity are rejected at load: a NaN "
                "slips past every `se <= 0` guard (all NaN comparisons are False) "
                "and then launders itself into a finite-looking p-value downstream."
                % (name, se))
        if not math.isfinite(y):
            raise ValueError("study %r: effect is %r; NaN and infinity are rejected" % (name, y))
        if se <= 0:
            raise ValueError("study %r: SE must be positive" % name)
        studies.append({"name": name, "y": y, "se": se})
    if len(studies) < 2:
        raise ValueError("need at least 2 studies to pool")
    return studies


def _from_json(text):
    data = json.loads(text)
    if isinstance(data, dict):
        data = data["studies"]
    if not isinstance(data, list):
        raise ValueError("JSON must be a list of studies or {'studies': [...]}")
    return data


def _from_csv(text):
    return list(csv.DictReader(text.splitlines()))


# --- Special functions for p-values (Numerical Recipes style, stdlib math) ---

def gammaincc(a, x):
    """Regularized upper incomplete gamma Q(a, x) = Gamma(a,x)/Gamma(a)."""
    if x < 0 or a <= 0:
        raise ValueError("bad args to gammaincc")
    if x == 0:
        return 1.0
    tiny = 1e-300
    if x < a + 1.0:  # series for P(a,x), then Q = 1 - P
        ap, term, total = a, 1.0 / a, 1.0 / a
        for _ in range(1000):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return max(0.0, 1.0 - total * math.exp(-x + a * math.log(x) - math.lgamma(a)))
    b, c, d = x + 1.0 - a, 1.0 / tiny, 1.0 / (x + 1.0 - a)  # continued fraction for Q
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return max(0.0, math.exp(-x + a * math.log(x) - math.lgamma(a)) * h)


def _betacf(a, b, x):
    """Continued fraction for the incomplete beta function."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)),
                   -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1.0 + aa * d
            if abs(d) < tiny:
                d = tiny
            c = 1.0 + aa / c
            if abs(c) < tiny:
                c = tiny
            d = 1.0 / d
            h *= d * c
        if abs(d * c - 1.0) < 1e-15:
            break
    return h


def betainc(x, a, b):
    """Regularized incomplete beta I_x(a, b)."""
    if not 0.0 <= x <= 1.0:
        raise ValueError("bad x in betainc")
    if x == 0.0 or x == 1.0:
        return x
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                  + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def chi2_pvalue(q, df):
    """Survival function P(chi^2_df >= q)."""
    return gammaincc(df / 2.0, q / 2.0)


def t_pvalue_two_sided(t, df):
    """Two-sided p-value for a t statistic with df degrees of freedom."""
    return betainc(df / (df + t * t), df / 2.0, 0.5)


# --- Meta-analytic machinery -------------------------------------------------

def fixed_effect(y, v):
    """Inverse-variance pooled estimate. Returns (pooled, se, weights)."""
    w = [1.0 / vi for vi in v]
    sw = sum(w)
    pooled = sum(wi * yi for wi, yi in zip(w, y)) / sw
    return pooled, math.sqrt(1.0 / sw), w


def heterogeneity(y, w, pooled_fe, df):
    """Cochran's Q, I^2 (fraction), and DerSimonian-Laird tau^2."""
    q = sum(wi * (yi - pooled_fe) ** 2 for wi, yi in zip(w, y))
    i2 = max(0.0, (q - df) / q) if q > 0 else 0.0
    sw = sum(w)
    c = sw - sum(wi * wi for wi in w) / sw
    tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0
    return q, i2, tau2


def random_effects(y, v, tau2):
    """DL random-effects pooled estimate. Returns (pooled, se, weights)."""
    w = [1.0 / (vi + tau2) for vi in v]
    sw = sum(w)
    pooled = sum(wi * yi for wi, yi in zip(w, y)) / sw
    return pooled, math.sqrt(1.0 / sw), w


def eggers_test(y, se):
    """Egger's regression: standard normal deviate ~ precision.

    Returns (intercept, slope, t, df, p). An intercept departing from 0
    indicates funnel asymmetry (small-study effects / publication bias).
    Needs k >= 3; power is low unless k >= 10.
    """
    k = len(y)
    x = [1.0 / s for s in se]               # precision
    z = [yi / si for yi, si in zip(y, se)]  # standard normal deviate
    mx, mz = sum(x) / k, sum(z) / k
    sxx = sum((xi - mx) ** 2 for xi in x)
    sxz = sum((xi - mx) * (zi - mz) for xi, zi in zip(x, z))
    # Egger regresses the standard normal deviate on precision. If every study
    # has the same SE there is no spread in precision to regress on, sxx == 0,
    # and the test is undefined -- not "no asymmetry". This is a common real
    # case (equal-sized studies, or SEs rounded to two decimals), so it returns
    # None rather than dividing by zero or reporting a fabricated t.
    if sxx <= 0:
        return None
    slope = sxz / sxx
    intercept = mz - slope * mx
    resid = [zi - (intercept + slope * xi) for xi, zi in zip(x, z)]
    s2 = sum(r * r for r in resid) / (k - 2)
    se_int = math.sqrt(s2 * (1.0 / k + mx * mx / sxx))
    if se_int <= 0 or not math.isfinite(se_int):
        # Perfect fit: the points are exactly collinear, so the intercept has no
        # sampling variability to test against. Reporting t = 2e15, p = 0.0000
        # would present floating-point noise as decisive publication bias.
        return None
    t = intercept / se_int
    df = k - 2
    return intercept, slope, t, df, t_pvalue_two_sided(abs(t), df)


def analyze(studies):
    """Run the full battery; return a results dict."""
    y = [s["y"] for s in studies]
    v = [s["se"] ** 2 for s in studies]
    k, df = len(y), len(y) - 1
    fe, fe_se, w = fixed_effect(y, v)
    q, i2, tau2 = heterogeneity(y, w, fe, df)
    re, re_se, wr = random_effects(y, v, tau2)
    return {
        "k": k, "df": df, "w_fe": w, "w_re": wr,
        "fe": fe, "fe_se": fe_se, "fe_ci": (fe - Z95 * fe_se, fe + Z95 * fe_se),
        "re": re, "re_se": re_se, "re_ci": (re - Z95 * re_se, re + Z95 * re_se),
        "q": q, "q_p": chi2_pvalue(q, df), "i2": i2, "tau2": tau2,
        "egger": eggers_test(y, [s["se"] for s in studies]) if k >= 3 else None,
    }


def render(studies, res):
    """Plain-text report: forest table, pooled estimates, heterogeneity, Egger."""
    sw = sum(res["w_fe"])
    lines = ["Forest table (fixed-effect weights)",
             "%-16s %8s %8s %-20s %10s" % ("study", "effect", "SE", "95% CI", "weight %"),
             "-" * 66]
    for s, wi in zip(studies, res["w_fe"]):
        ci = "[%.3f, %.3f]" % (s["y"] - Z95 * s["se"], s["y"] + Z95 * s["se"])
        lines.append("%-16s %8.3f %8.3f %-20s %10.1f"
                     % (s["name"][:16], s["y"], s["se"], ci, 100.0 * wi / sw))
    lines += ["-" * 66,
              "Fixed-effect pooled:  %8.3f  SE %.4f  95%% CI [%.3f, %.3f]"
              % (res["fe"], res["fe_se"], res["fe_ci"][0], res["fe_ci"][1]),
              "Random-effects (DL):  %8.3f  SE %.4f  95%% CI [%.3f, %.3f]"
              % (res["re"], res["re_se"], res["re_ci"][0], res["re_ci"][1]),
              "",
              "Heterogeneity: Q = %.3f (df %d, p = %.4f);  I^2 = %.1f%%;  tau^2 = %.4f"
              % (res["q"], res["df"], res["q_p"], 100.0 * res["i2"], res["tau2"])]
    if res["egger"] is not None:
        a, b, t, df, p = res["egger"]
        lines.append("Egger's test: intercept = %.3f (slope %.3f), t(%d) = %.3f, p = %.4f"
                     % (a, b, df, t, p))
        if res["k"] < 10:
            lines.append("  note: k = %d < 10 -- Egger's test has low power; interpret with care."
                         % res["k"])
    elif res["k"] < 3:
        lines.append("Egger's test: not computed (needs at least 3 studies; k = %d)." % res["k"])
    else:
        lines.append("Egger's test: not computed -- every study has the same standard error, "
                     "so there is no spread in precision to regress the effect against. "
                     "This is undefined, NOT evidence of symmetry: a funnel plot with one "
                     "precision cannot show asymmetry either way.")
    return "\n".join(lines)


# --- Selftest ----------------------------------------------------------------
# Every expected value below was derived by hand from the data:
#   studies A(0.5, SE .2), B(0.3, SE .1), C(0.4, SE .2), D(0.7, SE .2)
#   weights 25/100/25/25, sum 175;  FE pooled = 70/175 = 0.4;  SE = sqrt(1/175)
#   Q = 25*.1^2 + 100*.1^2 + 0 + 25*.3^2 = 3.5, df = 3
#   chi2_3 p at 3.5 = erfc(sqrt(1.75)) + 2*sqrt(1.75)*e^-1.75/sqrt(pi) ~ 0.3208
#   I^2 = (3.5-3)/3.5 = 1/7;  C = 175 - 11875/175 = 750/7;  tau^2 = 0.5/C = 7/1500
#   RE weights 1500/67 (x3), 750/11;  pooled = (41475/737)/(99750/737) = 553/1330
#   RE SE = sqrt(737/99750)
#   Egger: precision (5,10,5,5), SND (2.5,3,2,3.5): slope 1/15, intercept 7/3,
#          SE(intercept) 7/6, t = 2.0, df = 2, p = 1 - sqrt(2/3) ~ 0.1835

SELFTEST_ROWS = [
    {"study": "A", "effect": 0.5, "se": 0.2},
    {"study": "B", "effect": 0.3, "se": 0.1},
    {"study": "C", "effect": 0.4, "se": 0.2},
    {"study": "D", "effect": 0.7, "se": 0.2},
]


def _check(label, got, want, tol=1e-9):
    ok = abs(got - want) <= tol
    print("%s %-44s got=%.10g want=%.10g" % ("PASS" if ok else "FAIL", label, got, want))
    return ok


def selftest():
    import os
    import tempfile
    all_ok = True

    # CLI loaders: JSON and CSV must yield identical studies
    with tempfile.TemporaryDirectory() as tmp:
        jpath, cpath = os.path.join(tmp, "s.json"), os.path.join(tmp, "s.csv")
        with open(jpath, "w") as fh:
            json.dump(SELFTEST_ROWS, fh)
        with open(cpath, "w") as fh:
            fh.write("study,effect,se\n" + "".join(
                "%s,%s,%s\n" % (r["study"], r["effect"], r["se"]) for r in SELFTEST_ROWS))
        sj, sc = load_studies(jpath), load_studies(cpath)
        ok = len(sj) == 4 and all(a == b for a, b in zip(sj, sc))
        print("%s %-44s (4 studies, JSON == CSV)" % ("PASS" if ok else "FAIL", "loaders JSON/CSV agree"))
        all_ok &= ok

    studies = [dict(name=r["study"], y=r["effect"], se=r["se"]) for r in SELFTEST_ROWS]
    res = analyze(studies)
    all_ok &= _check("FE pooled = 70/175", res["fe"], 0.4)
    all_ok &= _check("FE SE = sqrt(1/175)", res["fe_se"], math.sqrt(1.0 / 175.0))
    all_ok &= _check("FE CI lower", res["fe_ci"][0], 0.4 - Z95 * math.sqrt(1.0 / 175.0))
    all_ok &= _check("Cochran's Q", res["q"], 3.5)
    expected_qp = math.erfc(math.sqrt(1.75)) + 2.0 * math.sqrt(1.75) * math.exp(-1.75) / math.sqrt(math.pi)
    all_ok &= _check("Q p-value (chi2_3 closed form)", res["q_p"], expected_qp)
    all_ok &= _check("I^2 = 1/7", res["i2"], 1.0 / 7.0)
    all_ok &= _check("tau^2 = 7/1500", res["tau2"], 7.0 / 1500.0)
    all_ok &= _check("RE pooled = 553/1330", res["re"], 553.0 / 1330.0)
    all_ok &= _check("RE SE = sqrt(737/99750)", res["re_se"], math.sqrt(737.0 / 99750.0))

    a, b, t, df, p = res["egger"]
    all_ok &= _check("Egger intercept = 7/3", a, 7.0 / 3.0)
    all_ok &= _check("Egger slope = 1/15", b, 1.0 / 15.0)
    all_ok &= _check("Egger t = 2.0", t, 2.0)
    all_ok &= _check("Egger df = 2", df, 2, tol=0)
    all_ok &= _check("Egger p = 1 - sqrt(2/3)", p, 1.0 - math.sqrt(2.0 / 3.0))

    # SE derived from a 95% CI: [0.108, 0.892] -> 0.784/3.92 = 0.2 by hand
    # (hand check uses z = 1.96; the script uses the exact 1.959964, so the
    # result differs by ~4e-5 -- tolerance covers that convention gap)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "ci.json")
        with open(path, "w") as fh:
            json.dump([{"study": "X", "effect": 0.5, "ci_low": 0.108, "ci_high": 0.892},
                       {"study": "Y", "effect": 0.3, "se": 0.1}], fh)
        all_ok &= _check("SE from CI ~= 0.2", load_studies(path)[0]["se"], 0.2, tol=1e-3)

    text = render(studies, res)  # render smoke test
    ok = "Fixed-effect pooled" in text and "Egger" in text and "I^2 = 14.3%" in text
    print("%s %-44s" % ("PASS" if ok else "FAIL", "render contains pooled/heterogeneity/Egger"))
    all_ok &= ok

    print("SELFTEST %s" % ("PASSED" if all_ok else "FAILED"))
    return 0 if all_ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pool effect sizes: fixed-effect, "
                                     "DerSimonian-Laird random-effects, Q/I^2/tau^2, "
                                     "forest table, Egger's test.")
    ap.add_argument("--file", help="JSON or CSV study file (effect + se, or ci_low/ci_high)")
    ap.add_argument("--selftest", action="store_true", help="run built-in checks and exit")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.file:
        ap.error("--file is required (or use --selftest)")
    try:
        studies = load_studies(args.file)
        print(render(studies, analyze(studies)))
    except (ValueError, KeyError, OSError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
