#!/usr/bin/env python3
"""momentum.py — companion tool for the `assess-research-momentum` skill.

Quantifies research momentum from two small CSV series:

  fit       year,count     -> logistic S-curve fit, K / (1 + e^{-r(t - t0)}),
                              found by coarse grid search over (K, r, t0)
                              minimizing SSE, then pattern-search refinement.
                              Reports K, r, t0, R^2, current %-of-K, doubling
                              time, and phase (emergent / growth / mature).
  velocity  year,citations -> YoY growth, window CAGR, and acceleration sign
                              (recent-half vs early-half mean YoY growth).
  --selftest               -> built-in checks against a noiseless logistic
                              series with known parameters plus hand-verified
                              velocity arithmetic. Exit 0 on success.

CSV format: one `year,value` pair per line; an optional header row, blank
lines, and '#' comments are tolerated; rows may be unsorted.

Phase thresholds (fraction of K reached at the last observed year):
< 20% emergent, 20-80% growth, > 80% mature. Python 3.9+, stdlib only.
"""

import argparse
import math
import sys

PHASE_EMERGENT_MAX = 0.20   # below this fraction of K -> "emergent"
PHASE_GROWTH_MAX = 0.80     # below this (and >= above) -> "growth"
ACCEL_STEADY_TOL = 0.01     # |late-half - early-half mean YoY| below this -> "steady"


# --- input parsing -----------------------------------------------------------

def parse_series_lines(lines):
    """Parse `year,value` lines into a sorted [(year:int, value:float)] list.

    Skips blank lines, '#' comments, and one optional non-numeric header row.
    """
    rows = []
    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 2:
            raise ValueError(f"line {lineno}: expected 'year,value', got {line!r}")
        try:
            rows.append((int(parts[0]), float(parts[1])))
        except ValueError:
            if not rows:  # tolerate a single header row like "year,count"
                continue
            raise ValueError(f"line {lineno}: non-numeric row {line!r}")
    if len(rows) < 2:
        raise ValueError("need at least 2 data rows")
    rows.sort(key=lambda r: r[0])
    return rows


def read_series(path):
    with open(path, "r", encoding="utf-8") as fh:
        return parse_series_lines(fh)


# --- logistic S-curve fitting ------------------------------------------------

def logistic(t, K, r, t0):
    """Logistic level K / (1 + e^{-r(t - t0)}), overflow-safe."""
    z = -r * (t - t0)
    if z > 700.0:
        return 0.0
    if z < -700.0:
        return K
    return K / (1.0 + math.exp(z))


def sse(data, K, r, t0):
    """Sum of squared errors of the logistic model against (year, count) data."""
    if K <= 0.0 or r <= 0.0:
        return float("inf")
    return sum((y - logistic(t, K, r, t0)) ** 2 for t, y in data)


def fit_logistic(data):
    """Fit (K, r, t0) by coarse grid search + pattern-search refinement.

    The grid gives a deterministic starting point; the pattern search (try
    +-step per parameter, halve steps when no move improves SSE) polishes it.
    Caveat: data covering only the early near-exponential part of the curve
    leave K and t0 weakly identifiable (only K*e^{-r*t0} is pinned down) —
    treat such fits with caution, per the skill's confidence guidance.
    """
    years = [t for t, _ in data]
    t_min, t_max = min(years), max(years)
    y_max = max(y for _, y in data)
    if y_max <= 0.0:
        raise ValueError("all counts are zero — no curve to fit")

    # Coarse grid. K: log-spaced from half the max count to 15x it (a logistic
    # can sit below noisy data, and a young field can be far from K).
    # r: plausible annual growth rates. t0: midpoint well outside the window.
    ks = [y_max * 0.5 * (30.0 ** (i / 39.0)) for i in range(40)]
    rs = [0.02 + (2.0 - 0.02) * i / 39.0 for i in range(40)]
    t0_lo, t0_hi = t_min - 20.0, t_max + 30.0
    t0s = [t0_lo + (t0_hi - t0_lo) * i / 50.0 for i in range(51)]
    best_err, K, r, t0 = float("inf"), None, None, None
    for k_ in ks:
        for r_ in rs:
            for t0_ in t0s:
                err = sse(data, k_, r_, t0_)
                if err < best_err:
                    best_err, K, r, t0 = err, k_, r_, t0_

    # Pattern-search refinement.
    step_k, step_r, step_t0 = y_max * 0.25, 0.05, 1.0
    for _ in range(500):
        improved = False
        for dk in (-1.0, 0.0, 1.0):
            for dr in (-1.0, 0.0, 1.0):
                for dt in (-1.0, 0.0, 1.0):
                    if dk == dr == dt == 0.0:
                        continue
                    err = sse(data, K + dk * step_k, r + dr * step_r, t0 + dt * step_t0)
                    if err < best_err:
                        best_err = err
                        K += dk * step_k
                        r += dr * step_r
                        t0 += dt * step_t0
                        improved = True
        if not improved:
            step_k *= 0.5
            step_r *= 0.5
            step_t0 *= 0.5
            if step_k < y_max * 1e-5 and step_r < 1e-5 and step_t0 < 1e-4:
                break
    return K, r, t0, best_err


def r_squared(data, K, r, t0, fit_sse=None):
    """Coefficient of determination, 1 - SSE/SST."""
    ys = [y for _, y in data]
    mean = sum(ys) / len(ys)
    sst = sum((y - mean) ** 2 for y in ys)
    if sst == 0.0:
        return 1.0
    err = fit_sse if fit_sse is not None else sse(data, K, r, t0)
    return 1.0 - err / sst


def classify_phase(fraction_of_k):
    """Phase from the fraction of carrying capacity reached at the last year."""
    if fraction_of_k < PHASE_EMERGENT_MAX:
        return "emergent"
    if fraction_of_k <= PHASE_GROWTH_MAX:
        return "growth"
    return "mature"


def doubling_time(K, r, t0, t_now):
    """Years for the logistic level at t_now to double; None if past K/2.

    With y = L(t_now), the level 2y is reached after
    dt = ln( 2(K - y) / (K - 2y) ) / r. If 2y >= K the model never doubles
    again (the curve is past its inflection point).
    """
    y = logistic(t_now, K, r, t0)
    if y <= 0.0 or 2.0 * y >= K:
        return None
    return math.log(2.0 * (K - y) / (K - 2.0 * y)) / r


# --- citation velocity -------------------------------------------------------

def yoy_growth(series):
    """[(year, growth)] for consecutive rows; growth None when prior year is 0."""
    return [(t1, None if c0 == 0 else c1 / c0 - 1.0)
            for (t0, c0), (t1, c1) in zip(series, series[1:])]


def cagr(series):
    """Compound annual growth rate across the window; None if undefined."""
    (t_first, c_first), (t_last, c_last) = series[0], series[-1]
    n = t_last - t_first
    if n <= 0 or c_first <= 0:
        return None
    return (c_last / c_first) ** (1.0 / n) - 1.0


def acceleration(rates):
    """Compare recent-half vs early-half mean YoY growth.

    Returns (label, diff), diff = late_mean - early_mean (None when fewer
    than 2 rates). |diff| < ACCEL_STEADY_TOL counts as "steady".
    """
    if len(rates) < 2:
        return "insufficient data", None
    h = len(rates) // 2
    diff = sum(rates[-h:]) / h - sum(rates[:h]) / h
    if abs(diff) < ACCEL_STEADY_TOL:
        return "steady", diff
    return ("accelerating" if diff > 0 else "decelerating"), diff


# --- CLI commands ------------------------------------------------------------

def cmd_fit(path):
    try:
        data = read_series(path)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if len(data) < 4:
        print("error: need at least 4 yearly buckets for an S-curve fit "
              "(the skill itself wants >= 3 years before calling a trend)",
              file=sys.stderr)
        return 2
    K, r, t0, fit_sse = fit_logistic(data)
    r2 = r_squared(data, K, r, t0, fit_sse)
    t_last = data[-1][0]
    level = logistic(t_last, K, r, t0)
    frac = level / K
    dt = doubling_time(K, r, t0, t_last)
    print(f"Logistic S-curve fit — {path}")
    print(f"  data:            {len(data)} points, {data[0][0]}–{t_last}")
    print(f"  K (capacity):    {K:.1f} papers/year")
    print(f"  r (growth rate): {r:.4f} /year")
    print(f"  t0 (midpoint):   {t0:.1f}")
    print(f"  R²:              {r2:.4f}")
    print(f"  current level:   {level:.1f} = {frac * 100:.1f}% of K (year {t_last})")
    if dt is None:
        print("  doubling time:   n/a (past inflection — level already exceeds K/2)")
    else:
        print(f"  doubling time:   {dt:.2f} years at current level")
    print(f"  phase:           {classify_phase(frac)} "
          f"(<20% of K = emergent, 20–80% = growth, >80% = mature)")
    return 0


def cmd_velocity(path):
    try:
        data = read_series(path)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    yoy = yoy_growth(data)
    window_cagr = cagr(data)
    label, diff = acceleration([g for _, g in yoy if g is not None])
    print(f"Citation velocity — {path}")
    print(f"  data:   {len(data)} points, {data[0][0]}–{data[-1][0]}")
    print("  YoY:    " + ", ".join(
        f"{yr} {'n/a' if g is None else f'{g * 100:+.1f}%'}" for yr, g in yoy))
    if window_cagr is None:
        print("  CAGR:   n/a (undefined — zero/negative base or single-year window)")
    else:
        print(f"  CAGR:   {window_cagr * 100:+.1f}% per year ({data[0][0]}–{data[-1][0]})")
    if diff is None:
        print("  signal: insufficient data for an acceleration read")
    else:
        print(f"  signal: {label} "
              f"(recent-half mean YoY − early-half = {diff * 100:+.1f} pp)")
    return 0


# --- self-test ---------------------------------------------------------------

def selftest():
    """Built-in checks. Expected values are hand-computed, not self-referential:

    * Fit recovery: a noiseless series with K=1000, r=0.6, t0=2015 must be
      recovered within tolerance, with R² ~ 1 and a "mature" end phase
      (f(2025) = 1/(1+e^{-6}) = 0.9975).
    * Doubling time at t=2010 for the same curve: y = 1000/(1+e^3) = 47.4259,
      so dt = ln(2*(1000-47.4259)/(1000-94.8517))/0.6 = 1.2404 years.
    * Velocity: 100 -> 150 -> 225 -> 337.5 is exactly +50% each year, and
      337.5/100 = 27/8, so CAGR = (27/8)^{1/3} - 1 = 0.5 exactly.
    * Accelerating series 100,100,150,300 has CAGR = 3^{1/3} - 1 = 0.44225.
    """
    checks = []

    def check(name, ok, detail=""):
        checks.append(bool(ok))
        print(f"{'PASS' if ok else 'FAIL'}: {name}" + (f" ({detail})" if detail else ""))

    # Parsing: header, comments, blank lines, unsorted rows.
    rows = parse_series_lines([
        "year,count\n", "# comment line\n", "\n", "2010, 5\n", "2008, 1\n", "2009, 2\n"])
    check("CSV parser handles header/comments/blanks and sorts by year",
          rows == [(2008, 1.0), (2009, 2.0), (2010, 5.0)], f"rows={rows}")

    # Logistic fit recovers known parameters.
    TRUE_K, TRUE_R, TRUE_T0 = 1000.0, 0.6, 2015.0
    series = [(yr, logistic(yr, TRUE_K, TRUE_R, TRUE_T0)) for yr in range(2005, 2026)]
    K, r, t0, fit_sse = fit_logistic(series)
    r2 = r_squared(series, K, r, t0, fit_sse)
    check("fit recovers K within 5%",
          abs(K - TRUE_K) <= 0.05 * TRUE_K, f"fit={K:.2f}, true=1000")
    check("fit recovers r within 0.03",
          abs(r - TRUE_R) <= 0.03, f"fit={r:.4f}, true=0.6")
    check("fit recovers t0 within 0.3 years",
          abs(t0 - TRUE_T0) <= 0.3, f"fit={t0:.3f}, true=2015")
    check("noiseless fit achieves R² >= 0.999", r2 >= 0.999, f"R²={r2:.5f}")

    # Phase of the fitted series: f(2025) = 1/(1+e^-6) = 0.9975 -> mature.
    frac = logistic(2025, K, r, t0) / K
    check("fitted series ending at 99.75% of K classifies as mature",
          classify_phase(frac) == "mature", f"fraction={frac:.4f}")
    check("doubling time is n/a once past the inflection point",
          doubling_time(K, r, t0, 2025) is None)

    # Fit of a series ending at its midpoint -> growth phase (~50% of K).
    mid_series = [(yr, logistic(yr, TRUE_K, TRUE_R, TRUE_T0)) for yr in range(2000, 2016)]
    K2, r2_, t02, _ = fit_logistic(mid_series)
    frac2 = logistic(2015, K2, r2_, t02) / K2
    check("series ending at its midpoint (50% of K) classifies as growth",
          classify_phase(frac2) == "growth" and 0.45 <= frac2 <= 0.55,
          f"fraction={frac2:.4f}")

    # Phase boundary unit checks.
    check("phase thresholds: 10% emergent, 20%/50%/80% growth, 95% mature",
          classify_phase(0.10) == "emergent" and classify_phase(0.20) == "growth"
          and classify_phase(0.50) == "growth" and classify_phase(0.80) == "growth"
          and classify_phase(0.95) == "mature")

    # Doubling time, hand-computed: ln(2*952.5741/905.1483)/0.6 = 1.2404.
    dt = doubling_time(TRUE_K, TRUE_R, TRUE_T0, 2010)
    check("doubling time at t=2010 matches hand-computed 1.2404 years",
          dt is not None and abs(dt - 1.2404) < 0.001,
          f"dt={dt:.4f}" if dt is not None else "dt=None")

    # Velocity: exact +50%/year series.
    steady_series = [(2019, 100.0), (2020, 150.0), (2021, 225.0), (2022, 337.5)]
    yoy = yoy_growth(steady_series)
    check("YoY growth of 100→150→225→337.5 is exactly +50% each year",
          all(g is not None and abs(g - 0.5) < 1e-12 for _, g in yoy),
          f"rates={[round(g, 4) for _, g in yoy]}")
    check("CAGR of 100→337.5 over 3 years is exactly 50% (27/8)^(1/3)−1",
          abs(cagr(steady_series) - 0.5) < 1e-12, f"cagr={cagr(steady_series):.6f}")
    label, diff = acceleration([g for _, g in yoy])
    check("constant +50%/year reads as steady (diff 0.0)",
          label == "steady" and abs(diff) < 1e-12, f"label={label}, diff={diff:.4f}")

    # Acceleration / deceleration sign.
    accel_series = [(2018, 100.0), (2019, 100.0), (2020, 150.0), (2021, 300.0)]
    label_a, diff_a = acceleration([g for _, g in yoy_growth(accel_series)])
    check("0%→50%→100% YoY reads as accelerating (diff +1.0)",
          label_a == "accelerating" and abs(diff_a - 1.0) < 1e-12,
          f"label={label_a}, diff={diff_a:.4f}")
    check("CAGR of 100→300 over 3 years is 3^(1/3)−1 = 0.44225",
          abs(cagr(accel_series) - 0.44225) < 1e-4, f"cagr={cagr(accel_series):.6f}")
    decel_series = [(2018, 100.0), (2019, 300.0), (2020, 450.0), (2021, 550.0)]
    label_d, diff_d = acceleration([g for _, g in yoy_growth(decel_series)])
    check("200%→50%→22% YoY reads as decelerating",
          label_d == "decelerating", f"label={label_d}, diff={diff_d:.4f}")

    print(f"selftest: {sum(checks)}/{len(checks)} checks passed")
    return 0 if all(checks) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Companion tool for the assess-research-momentum skill: "
                    "logistic S-curve fits and citation velocity.")
    parser.add_argument("--selftest", action="store_true",
                        help="run built-in checks and exit")
    sub = parser.add_subparsers(dest="command")
    p_fit = sub.add_parser("fit", help="logistic S-curve fit of a year,count CSV")
    p_fit.add_argument("--file", required=True, help="CSV with year,count rows")
    p_vel = sub.add_parser("velocity", help="citation velocity of a year,citations CSV")
    p_vel.add_argument("--file", required=True, help="CSV with year,citations rows")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.command == "fit":
        return cmd_fit(args.file)
    if args.command == "velocity":
        return cmd_velocity(args.file)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
