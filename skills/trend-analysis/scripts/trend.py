#!/usr/bin/env python3
"""trend.py — quantify, fit and project a trend series (companion to ../SKILL.md).

Implements the arithmetic of SKILL.md steps 3–4 (quantify -> project) so the
agent never recomputes growth rates or curve fits in its head:

  describe  n, span, min/max, absolute and relative change, CAGR (endpoints and
            first->last non-zero), average change per period, mean period-over-
            period growth, doubling time, curvature read (accelerating / linear /
            saturating from the period gains), YoY table, largest single-period
            jump with a spike (outlier) check.
  fit       ordinary least squares linear fit; exponential (log-linear) fit;
            logistic S-curve fit; best model by R² with the diffusion-model caveat.
  project   projection per model to a target period, ± 2·RMSE band, horizon
            multiple, optional Trend Impact Analysis (TIA) event adjustment.

Definitions implemented:
  * CAGR            = (last / first) ** (1 / periods) - 1   (positive values only)
  * doubling time   = ln 2 / ln(1 + g)   (halving time = ln 0.5 / ln(1 + g), g < 0)
  * spike check     = modified z-score M = 0.6745 (x - median) / MAD of the
                      period-over-period changes; |M| > 3.5 marks an outlier
                      (Iglewicz & Hoaglin 1993, *How to Detect and Handle
                      Outliers*, ASQC Quality Press). A step is flagged as a
                      spike only when the rule fires on both the absolute change
                      and the relative change (absolute alone when values are not
                      all positive): a clean steep exponential has growing
                      increments but constant relative steps, and is not a spike.
                      When MAD = 0 the tool falls back to the mean absolute
                      deviation about the median with constant 0.7979 =
                      sqrt(2/pi); if that is 0 too, nothing is flagged.
  * linear          = OLS of y on t: y = a + b (t - t_first); R² = 1 - SSE/SST.
  * exponential     = OLS of ln y on t: y = A (1 + g) ** (t - t_first), growth
                      g = e**slope - 1; R² reported in log space (the regression's
                      own) and in y-space (comparable across models); requires
                      all values > 0.
  * logistic        = y = K / (1 + exp(-r (t - t0))). K by deterministic grid
                      search: 200 values evenly spaced in [1.05·max, 5·max], then
                      a 200-step refinement within one coarse step of the best K
                      (floor 1.001·max). For each K the Fisher–Pry linearisation
                      ln(y / (K - y)) = r (t - t0) is solved by OLS on the
                      positive observations (Fisher & Pry 1971, "A simple
                      substitution model of technological change", Technol.
                      Forecast. Soc. Change 3:75–88); the K minimising SSE in
                      y-space wins (first on ties). Reports r, t0 (inflection),
                      K (saturation), current fraction of K, R² in y-space.
                      Caveat: with data only on the lower half of the curve K is
                      poorly identified (Meade & Islam 2006, "Modelling and
                      forecasting the diffusion of innovation — a 25-year
                      review", Int. J. Forecasting 22:519–545).
  * naive           = last value + average change per period × periods ahead
                      (SKILL.md step 4 "naive extrapolation"); its RMSE is taken
                      about the line through the first and last observations.
  * ± 2·RMSE band   = point projection ± 2 × in-sample RMSE (sqrt(SSE / n)).
                      A rough spread, NOT a prediction interval: it ignores
                      parameter uncertainty and error growth with the horizon.
  * horizon multiple = (target - last observed) / (last - first observed);
                      > 1 means projecting further than the data's own span.
  * TIA adjustment  = baseline + sum(P_i × impact_i) over --event items
                      (Gordon 1994/2009, "Trend Impact Analysis", in Glenn &
                      Gordon, Futures Research Methodology, Millennium Project).

Periods may be years (2024), ISO dates (2024-06 or 2024-06-30, converted to
decimal years), quarters (2024Q3) or plain numbers (0, 1, 2 ...); rates are then
"per period" = per year for date-like periods. Stdlib only. Python 3.9+.

Usage:
    python3 trend.py describe --file series.csv          # columns: period,value
    python3 trend.py fit --series "2020:4,2021:9,2022:14,2023:18,2024:21"
    python3 trend.py project --file series.json --to 2030 --model auto
    python3 trend.py project --demo --to 2030 --model naive \\
        --event "subsidy rollback:0.5:-5" --event "charging bottlenecks:0.4:-4"
    python3 trend.py --demo        # reproduce the SKILL.md worked example
    python3 trend.py --selftest    # hand-verified checks; prints 'selftest OK'
Add --json to any command for machine-readable output.
"""

import argparse
import csv
import datetime
import json
import math
import re
import statistics
import sys

# --- constants ---------------------------------------------------------------

MIN_POINTS = 3           # fewer -> invalid input (exit 1)
SPARSE_POINTS = 5        # fewer -> warn (SKILL.md: "do not fit lines to three points")
OUTLIER_Z = 3.5          # Iglewicz & Hoaglin (1993) modified z-score cut-off
MAD_CONST = 0.6745       # makes MAD consistent with sigma under normality
MEANAD_CONST = 0.7979    # sqrt(2/pi): fallback constant when MAD == 0
K_GRID_LO = 1.05         # logistic K grid: lower bound as a multiple of max(y)
K_GRID_HI = 5.0          # upper bound as a multiple of max(y)
K_GRID_STEPS = 200       # evenly spaced K values, coarse pass and refinement
K_REFINE_FLOOR = 1.001   # refinement may approach max(y) down to this multiple
ROGERS_EARLY = 0.16      # S-curve position as a fraction of the fitted ceiling K:
ROGERS_LATE = 0.50       # < 16 % early, 16-50 % mid, > 50 % late. Rogers' adopter
                         # categories use the same cut-offs but on *cumulative*
                         # adoption; this is fraction of K, not a Rogers category.
CURVATURE_TOL = 0.05     # |gain trend| / mean|gain| below this -> "linear"
NEAR_TIE_R2 = 0.02       # top-two R² closer than this -> shapes not distinguishable
BAND_MULT = 2.0          # naive band = ± BAND_MULT × RMSE

# SKILL.md worked example: EV (BEV+PHEV) share of global new car sales, %,
# IEA Global EV Outlook series (approx.), 2020-2024, projected to 2030 by TIA.
DEMO_SERIES = "2020:4,2021:9,2022:14,2023:18,2024:21"
DEMO_TARGET = "2030"
DEMO_MODEL = "naive"
DEMO_EVENTS = [
    "subsidy rollback in a major market:0.5:-5",
    "charging bottlenecks:0.4:-4",
    "battery cost breakthrough:0.3:+3",
]

# Flexible column names for CSV headers / JSON object keys.
PERIOD_KEYS = ("period", "year", "date", "t", "x", "time")
VALUE_KEYS = ("value", "y", "count", "share", "level", "v")

MODEL_ORDER = ("naive", "linear", "exponential", "logistic")


# --- input parsing -----------------------------------------------------------


def parse_period(raw):
    """Return (label, t) for one period token.

    t is a float on a per-period axis: plain numbers as given; YYYY -> year;
    YYYY-MM and YYYY-MM-DD -> decimal year; YYYYQn -> year + (n - 1) / 4.
    """
    s = str(raw).strip()
    if not s:
        raise ValueError("empty period")
    m = re.fullmatch(r"(\d{4})-(\d{1,2})(?:-(\d{1,2}))?", s)
    if m:
        year, month = int(m.group(1)), int(m.group(2))
        if m.group(3) is None:
            if not 1 <= month <= 12:
                raise ValueError(f"bad month in period {s!r}")
            return s, year + (month - 1) / 12.0
        day = datetime.date(year, month, int(m.group(3)))  # ValueError if invalid
        days_in_year = (datetime.date(year + 1, 1, 1) - datetime.date(year, 1, 1)).days
        return s, year + (day - datetime.date(year, 1, 1)).days / days_in_year
    m = re.fullmatch(r"(\d{4})\s*-?\s*[Qq]([1-4])", s)
    if m:
        return s, int(m.group(1)) + (int(m.group(2)) - 1) / 4.0
    try:
        t = float(s)
    except ValueError:
        raise ValueError(
            f"unrecognised period {s!r} (use 2024, 2024-06, 2024-06-30, 2024Q3 or a number)"
        ) from None
    if not math.isfinite(t):
        raise ValueError(f"non-finite period {s!r}")
    return s, t


def parse_value(raw):
    """Parse a numeric value; tolerates thousands separators and a trailing %."""
    s = str(raw).strip().replace(",", "").rstrip("%").strip()
    try:
        y = float(s)
    except ValueError:
        raise ValueError(f"non-numeric value {raw!r}") from None
    if not math.isfinite(y):
        raise ValueError(f"non-finite value {raw!r}")
    return y


def build_series(pairs):
    """Turn (period, value) pairs into a sorted list of (label, t, y) triples."""
    rows = []
    for i, (p, v) in enumerate(pairs, start=1):
        try:
            label, t = parse_period(p)
            y = parse_value(v)
        except ValueError as exc:
            raise ValueError(f"row {i}: {exc}") from None
        rows.append((label, t, y))
    if len(rows) < MIN_POINTS:
        raise ValueError(f"need at least {MIN_POINTS} data points, got {len(rows)}")
    rows.sort(key=lambda r: r[1])
    for a, b in zip(rows, rows[1:]):
        if b[1] - a[1] <= 0:
            raise ValueError(f"duplicate period {a[0]!r} / {b[0]!r}")
    return rows


def parse_series_arg(text):
    """Parse an inline series: "2019:10,2020:14,2021:20"."""
    pairs = []
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" not in item:
            raise ValueError(f"item {item!r}: expected period:value")
        p, v = item.rsplit(":", 1)
        pairs.append((p, v))
    return build_series(pairs)


def _find_key(mapping, candidates):
    lowered = {str(k).strip().lower(): k for k in mapping}
    for cand in candidates:
        if cand in lowered:
            return lowered[cand]
    return None


def _json_pairs(data):
    """Accept {"series": [...]}, {period: value}, [[p, v], ...] or [{...}, ...]."""
    if isinstance(data, dict):
        if "series" in data:
            return _json_pairs(data["series"])
        return list(data.items())
    if not isinstance(data, list):
        raise ValueError("JSON must be a list of rows or an object of period: value")
    pairs = []
    for i, row in enumerate(data, start=1):
        if isinstance(row, dict):
            pk, vk = _find_key(row, PERIOD_KEYS), _find_key(row, VALUE_KEYS)
            if pk is None or vk is None:
                raise ValueError(
                    f"row {i}: need period {PERIOD_KEYS} and value {VALUE_KEYS} keys; got {list(row)}"
                )
            pairs.append((row[pk], row[vk]))
        elif isinstance(row, (list, tuple)) and len(row) >= 2:
            pairs.append((row[0], row[1]))
        else:
            raise ValueError(f"row {i}: expected [period, value] or an object")
    return pairs


def _is_data_row(row):
    try:
        parse_period(row[0])
        parse_value(row[1])
        return True
    except (ValueError, IndexError):
        return False


def _csv_pairs(lines):
    rows = [
        r for r in csv.reader(lines)
        if r and any(c.strip() for c in r) and not r[0].lstrip().startswith("#")
    ]
    if not rows:
        raise ValueError("no data rows")
    if _is_data_row(rows[0]):
        pi, vi, data = 0, 1, rows
    else:
        header = [c.strip().lower() for c in rows[0]]
        pi = next((i for i, h in enumerate(header) if h in PERIOD_KEYS), 0)
        vi = next((i for i, h in enumerate(header) if h in VALUE_KEYS and i != pi), 1 if pi != 1 else 0)
        data = rows[1:]
    pairs = []
    for r in data:
        if len(r) <= max(pi, vi):
            raise ValueError(f"row {r!r}: expected at least {max(pi, vi) + 1} columns")
        pairs.append((r[pi], r[vi]))
    return pairs


def load_file(path):
    """Load a series from CSV or JSON (by extension); '-' reads CSV/JSON from stdin."""
    if path == "-":
        text = sys.stdin.read()
        if text.lstrip().startswith(("[", "{")):
            return build_series(_json_pairs(json.loads(text)))
        return build_series(_csv_pairs(text.splitlines()))
    with open(path, newline="", encoding="utf-8") as fh:
        if path.lower().endswith(".json"):
            return build_series(_json_pairs(json.load(fh)))
        return build_series(_csv_pairs(fh.read().splitlines()))


# --- formatting --------------------------------------------------------------


def fmt_t(t):
    """Periods print as integers when whole (2024), else with two decimals."""
    if abs(t - round(t)) < 1e-9:
        return str(int(round(t)))
    return f"{t:.2f}"


def num(x, nd=2):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "n/a"
    if abs(x) >= 1e6:
        return f"{x:,.0f}"
    if abs(x) >= 1000:
        return f"{x:,.1f}"
    return f"{x:.{nd}f}"


def signed(x, nd=2):
    return "n/a" if x is None else ("+" if x >= 0 else "") + num(x, nd)


def pct(g, nd=1):
    return "n/a" if g is None else f"{100 * g:+.{nd}f}%"


def term(x, nd=2):
    """Signed term for formulas: '+ 4.25' / '− 4.25'."""
    return ("+ " if x >= 0 else "− ") + num(abs(x), nd)


def r2s(x):
    return "n/a" if x is None else f"{x:.4f}"


def _round(obj):
    if isinstance(obj, float):
        return round(obj, 6) if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_round(v) for v in obj]
    return obj


def emit_json(obj):
    print(json.dumps(_round(obj), indent=2, sort_keys=True, ensure_ascii=False))


# --- arithmetic --------------------------------------------------------------


def ols(xs, ys):
    """Ordinary least squares y = a + b x. Returns (a, b, r2, sse); r2 None if SST = 0."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        raise ValueError("all periods identical")
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    sse = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    sst = sum((y - my) ** 2 for y in ys)
    return a, b, (None if sst == 0 else 1.0 - sse / sst), sse


def r2_sse(ys, fitted):
    """R² = 1 - SSE/SST in y-space (None when SST = 0) and the SSE."""
    my = sum(ys) / len(ys)
    sst = sum((y - my) ** 2 for y in ys)
    sse = sum((y - f) ** 2 for y, f in zip(ys, fitted))
    return (None if sst == 0 else 1.0 - sse / sst), sse


def cagr(v0, v1, periods):
    """Compound growth per period between two positive values; None if undefined."""
    if v0 is None or v1 is None or v0 <= 0 or v1 <= 0 or periods <= 0:
        return None
    return (v1 / v0) ** (1.0 / periods) - 1.0


def doubling_time(g):
    """ln 2 / ln(1 + g) for g > 0 ('doubling'); ln 0.5 / ln(1 + g) for -1 < g < 0
    ('halving'). Returns (kind, periods) or (None, None) when undefined."""
    if g is None or g <= -1:
        return None, None
    if g > 0:
        return "doubling", math.log(2.0) / math.log(1.0 + g)
    if g < 0:
        return "halving", math.log(0.5) / math.log(1.0 + g)
    return None, None


def modified_z(values):
    """Iglewicz & Hoaglin (1993) modified z-scores, M = 0.6745 (x - median) / MAD.

    Falls back to 0.7979 (x - median) / MeanAD when MAD = 0; all zeros when
    both spreads vanish (identical values). Tiny spreads (floating-point noise
    relative to the data scale) count as zero.
    """
    med = statistics.median(values)
    dev = [abs(v - med) for v in values]
    scale = max(max(abs(v) for v in values), 1e-300)
    eps = 1e-9 * scale
    mad = statistics.median(dev)
    if mad > eps:
        return [MAD_CONST * (v - med) / mad for v in values]
    meanad = sum(dev) / len(dev)
    if meanad > eps:
        return [MEANAD_CONST * (v - med) / meanad for v in values]
    return [0.0 for _ in values]


def logistic_value(t, K, r, t0):
    x = -r * (t - t0)
    if x > 700:
        return 0.0
    return K / (1.0 + math.exp(x))


def curvature(series):
    """SKILL.md step 3 read: gains per period, then the OLS trend of those gains
    over time normalised by the mean |gain|. Growing gains = accelerating,
    shrinking = saturating, within ±CURVATURE_TOL = linear."""
    gains, mids = [], []
    for (_, t0, y0), (_, t1, y1) in zip(series, series[1:]):
        gains.append((y1 - y0) / (t1 - t0))
        mids.append((t0 + t1) / 2.0)
    mean_abs = sum(abs(g) for g in gains) / len(gains)
    if mean_abs == 0:
        return "flat", gains, 0.0
    _, slope, _, _ = ols(mids, gains)
    norm = slope / mean_abs
    rising = series[-1][2] >= series[0][2]
    if abs(norm) <= CURVATURE_TOL:
        label = "linear" if rising else "linear decline"
    elif rising:
        label = "accelerating" if norm > 0 else "saturating"
    else:
        label = "accelerating decline" if norm < 0 else "decelerating decline"
    return label, gains, norm


# --- models ------------------------------------------------------------------


def model_naive(series):
    """Naive extrapolation: last value + average change per period × periods ahead.
    Fit statistics are measured about the line through the first and last points."""
    (_, t0, y0), (_, tn, yn) = series[0], series[-1]
    avg = (yn - y0) / (tn - t0)
    ys = [y for _, _, y in series]
    fitted = [y0 + avg * (t - t0) for _, t, _ in series]
    r2, sse = r2_sse(ys, fitted)
    return {"model": "naive", "ok": True, "t_first": t0, "y_first": y0, "t_last": tn,
            "y_last": yn, "avg_change": avg, "r2": r2, "sse": sse,
            "rmse": math.sqrt(sse / len(ys))}


def fit_linear(series):
    t1 = series[0][1]
    xs = [t - t1 for _, t, _ in series]
    ys = [y for _, _, y in series]
    a, b, r2, sse = ols(xs, ys)
    return {"model": "linear", "ok": True, "t_first": t1, "intercept_first": a,
            "slope": b, "r2": r2, "sse": sse, "rmse": math.sqrt(sse / len(ys))}


def fit_exponential(series):
    ys = [y for _, _, y in series]
    if any(y <= 0 for y in ys):
        return {"model": "exponential", "ok": False,
                "reason": "log-linear fit requires all values > 0"}
    t1 = series[0][1]
    xs = [t - t1 for _, t, _ in series]
    c, k, r2_log, _ = ols(xs, [math.log(y) for y in ys])
    g, a = math.exp(k) - 1.0, math.exp(c)
    fitted = [a * math.exp(k * x) for x in xs]
    r2, sse = r2_sse(ys, fitted)
    kind, dt = doubling_time(g)
    return {"model": "exponential", "ok": True, "t_first": t1, "a": a, "growth": g,
            "r2_log": r2_log, "r2": r2, "sse": sse, "rmse": math.sqrt(sse / len(ys)),
            "doubling_kind": kind, "doubling_time": dt}


def _fisher_pry(series, K):
    """Fisher–Pry linearisation for a given K: OLS of ln(y / (K - y)) on t over the
    positive observations. Returns (sse_y, r, t0) or None when degenerate."""
    t1 = series[0][1]
    pts = [(t - t1, y) for _, t, y in series if 0 < y < K]
    if len(pts) < 3:
        return None
    c, r, _, _ = ols([x for x, _ in pts], [math.log(y / (K - y)) for _, y in pts])
    if abs(r) < 1e-12:
        return None
    t0 = t1 - c / r
    sse = sum((y - logistic_value(t, K, r, t0)) ** 2 for _, t, y in series)
    return sse, r, t0


def _scan_k(series, lo, hi, steps):
    """Evaluate `steps` evenly spaced K values in [lo, hi]; return the
    (K, sse, r, t0) with the smallest y-space SSE (first on ties)."""
    best = None
    for j in range(steps):
        K = lo + (hi - lo) * j / (steps - 1)
        res = _fisher_pry(series, K)
        if res is not None and (best is None or res[0] < best[1]):
            best = (K, res[0], res[1], res[2])
    return best


def fit_logistic(series, ceiling=None):
    ys = [y for _, _, y in series]
    ymax = max(ys)
    base = {"model": "logistic", "ok": False}
    if sum(1 for y in ys if y > 0) < 3:
        return dict(base, reason="needs at least 3 positive values")
    if ceiling is not None:
        if ceiling <= ymax:
            return dict(base, reason=f"--ceiling {num(ceiling)} must exceed the largest observation {num(ymax)}")
        res = _fisher_pry(series, ceiling)
        if res is None:
            return dict(base, reason="degenerate linearised fit at the given ceiling")
        K, (sse, r, t0) = ceiling, res
        k_fixed, k_at_bound = True, None
        search = f"K fixed at {num(K)} by --ceiling; r, t0 by Fisher–Pry OLS"
    else:
        lo, hi = K_GRID_LO * ymax, K_GRID_HI * ymax
        best = _scan_k(series, lo, hi, K_GRID_STEPS)
        if best is None:
            return dict(base, reason="no admissible K in the grid (linearised fit degenerate — constant series?)")
        step = (hi - lo) / (K_GRID_STEPS - 1)
        K1 = best[0]
        lo2 = K_REFINE_FLOOR * ymax if K1 <= lo else max(K_REFINE_FLOOR * ymax, K1 - step)
        best2 = _scan_k(series, lo2, K1 + step, K_GRID_STEPS)
        if best2 is not None and best2[1] < best[1]:
            best = best2
        K, sse, r, t0 = best
        k_fixed = False
        if K >= hi:
            k_at_bound = "upper"
        elif K <= K_REFINE_FLOOR * ymax * (1 + 1e-12):
            k_at_bound = "lower"
        else:
            k_at_bound = None
        search = (f"{K_GRID_STEPS}-step grid on [{K_GRID_LO}·max, {K_GRID_HI}·max] + "
                  f"{K_GRID_STEPS}-step refinement; per K, Fisher–Pry OLS on "
                  "ln(y/(K−y)) = r(t − t0); K minimising SSE in y-space")
    fitted = [logistic_value(t, K, r, t0) for _, t, _ in series]
    r2, _ = r2_sse(ys, fitted)
    frac = ys[-1] / K
    if r <= 0:
        position = "n/a (declining logistic)"
    elif frac < ROGERS_EARLY:
        position = "early (< 16% of K)"
    elif frac < ROGERS_LATE:
        position = "mid (16–50% of K)"
    else:
        position = "late (> 50% of K)"
    return {"model": "logistic", "ok": True, "K": K, "r": r, "t0": t0, "r2": r2,
            "sse": sse, "rmse": math.sqrt(sse / len(ys)), "fraction_of_k": frac,
            "position": position, "lower_half_only": frac < 0.5, "k_fixed": k_fixed,
            "k_at_bound": k_at_bound, "k_search": search}


def fit_all(series, ceiling=None):
    return [model_naive(series), fit_linear(series), fit_exponential(series),
            fit_logistic(series, ceiling)]


def predict(m, t):
    if m["model"] == "naive":
        return m["y_last"] + m["avg_change"] * (t - m["t_last"])
    if m["model"] == "linear":
        return m["intercept_first"] + m["slope"] * (t - m["t_first"])
    if m["model"] == "exponential":
        return m["a"] * (1.0 + m["growth"]) ** (t - m["t_first"])
    return logistic_value(t, m["K"], m["r"], m["t0"])


def formula(m):
    tf = fmt_t(m["t_first"]) if "t_first" in m else ""
    if m["model"] == "naive":
        return (f"y = {num(m['y_first'])} {term(m['avg_change'])}·(t − {tf}) — line through first "
                f"and last observations; average change {signed(m['avg_change'])} per period")
    if m["model"] == "linear":
        return (f"y = {num(m['intercept_first'])} {term(m['slope'])}·(t − {tf}) — OLS, "
                f"slope {signed(m['slope'])} per period")
    if m["model"] == "exponential":
        dt = (f"{m['doubling_kind']} time {num(m['doubling_time'])} periods"
              if m["doubling_kind"] else "no doubling (growth 0)")
        return (f"y = {num(m['a'])} × {num(1 + m['growth'], 4)}^(t − {tf}) — growth "
                f"{pct(m['growth'])} per period (log-linear OLS), {dt}, R²(log) {r2s(m['r2_log'])}")
    sign = "−" if m["r"] >= 0 else "+"
    head = (f"y = {num(m['K'])} / (1 + e^({sign}{num(abs(m['r']), 4)}·(t − {fmt_t(m['t0'])}))) — "
            f"K {num(m['K'])} (saturation), r {num(m['r'], 4)} per period, t0 {fmt_t(m['t0'])} "
            f"(inflection); last = {100 * m['fraction_of_k']:.1f}% of K")
    if m["r"] <= 0:
        return head + " — declining logistic (r ≤ 0): S-curve position not applicable"
    return head + f" → {m['position']} on the S-curve"


def recommend(fits):
    """Best fitted model (linear / exponential / logistic) by R² in y-space; first
    wins ties. Returns (name or None, sorted [(r2, name)], near_tie flag)."""
    ranked = [(m["r2"], m["model"]) for m in fits
              if m["ok"] and m["r2"] is not None and m["model"] != "naive"]
    best, best_r2 = None, None
    for r2, name in ranked:
        if best_r2 is None or r2 > best_r2:
            best, best_r2 = name, r2
    top = sorted(ranked, key=lambda x: (-x[0], MODEL_ORDER.index(x[1])))
    near_tie = len(top) >= 2 and (top[0][0] - top[1][0]) < NEAR_TIE_R2
    return best, top, near_tie


def logistic_caveat(m):
    frac = 100 * m["fraction_of_k"]
    if m["k_at_bound"] == "upper":
        return (f"Logistic: K ran to the top of the search grid ({K_GRID_HI:g}·max) — saturation is not "
                "identified by these data; the curve there is indistinguishable from an exponential "
                "(Meade & Islam 2006). Do not quote K; fix a ceiling with --ceiling if one is known.")
    if m["k_at_bound"] == "lower":
        return ("Logistic: K sits at the search floor just above the largest observation — the series "
                "reads as already saturated at its maximum; check whether that maximum is a real ceiling.")
    if m["k_fixed"]:
        return (f"Logistic: K = {num(m['K'])} is an assumed ceiling (--ceiling), not an estimate — "
                f"observations reach {frac:.0f}% of it, so r, t0 and the projection stand or fall "
                "with that assumption; state it on the assumption sheet (Meade & Islam 2006).")
    if m["lower_half_only"]:
        return (f"Logistic: observations reach only {frac:.0f}% of the fitted K — all on the lower "
                "half of the S-curve, where K (saturation) is poorly identified and can shift "
                "sharply with one more point (Meade & Islam 2006). Treat K and the logistic "
                "projection as provisional, or fix the ceiling with --ceiling.")
    return (f"Logistic: observations reach {frac:.0f}% of K, past the inflection, so K is "
            "identified by the data's own curvature — still a fitted assumption; cross-check "
            "against an external ceiling with --ceiling (Meade & Islam 2006).")


def sparse_warning(series):
    n = len(series)
    if n < SPARSE_POINTS:
        return [f"only {n} points — below the ~{SPARSE_POINTS}-observation floor in SKILL.md; "
                "too sparse to separate trend from noise, treat every number below as indicative"]
    return []


# --- describe ----------------------------------------------------------------


def describe(series):
    labels = [l for l, _, _ in series]
    ts = [t for _, t, _ in series]
    ys = [y for _, _, y in series]
    n = len(series)
    span = ts[-1] - ts[0]
    imin = min(range(n), key=lambda i: ys[i])
    imax = max(range(n), key=lambda i: ys[i])
    change = ys[-1] - ys[0]
    rel = change / ys[0] if ys[0] > 0 else None
    avg_change = change / span
    cagr_end = cagr(ys[0], ys[-1], span)
    nz = [i for i in range(n) if ys[i] > 0]
    if len(nz) >= 2:
        cagr_nz = cagr(ys[nz[0]], ys[nz[-1]], ts[nz[-1]] - ts[nz[0]])
        nz_from, nz_to = labels[nz[0]], labels[nz[-1]]
    else:
        cagr_nz, nz_from, nz_to = None, None, None
    steps = []
    for i in range(1, n):
        dt = ts[i] - ts[i - 1]
        dabs = ys[i] - ys[i - 1]
        rel_step = dabs / ys[i - 1] if ys[i - 1] > 0 else None
        ann = cagr(ys[i - 1], ys[i], dt) if ys[i - 1] > 0 and ys[i] > 0 else None
        steps.append({"from": labels[i - 1], "to": labels[i], "period": labels[i],
                      "value": ys[i], "dt": dt, "abs_change": dabs, "pct_change": rel_step,
                      "annualised_pct": ann})
    growth_steps = [s["annualised_pct"] for s in steps if s["annualised_pct"] is not None]
    mean_yoy = sum(growth_steps) / len(growth_steps) if growth_steps else None
    g = cagr_end if cagr_end is not None else cagr_nz
    dbl_basis = "endpoints" if cagr_end is not None else "first→last non-zero"
    dbl_kind, dbl = doubling_time(g)
    curv_label, gains, curv_norm = curvature(series)
    zs = modified_z([s["abs_change"] for s in steps])
    rel_steps = [s["pct_change"] for s in steps]
    zr = (modified_z(rel_steps) if all(r is not None for r in rel_steps)
          else [None] * len(steps))
    for s, z, z_rel in zip(steps, zs, zr):
        s["modified_z"] = z
        s["modified_z_rel"] = z_rel
        s["spike"] = abs(z) > OUTLIER_Z and (z_rel is None or abs(z_rel) > OUTLIER_Z)
    j = max(range(len(steps)), key=lambda i: abs(steps[i]["abs_change"]))
    return {
        "command": "describe", "n": n, "first": labels[0], "last": labels[-1], "span": span,
        "min": ys[imin], "min_period": labels[imin], "max": ys[imax], "max_period": labels[imax],
        "first_value": ys[0], "last_value": ys[-1], "change": change, "relative_change": rel,
        "avg_change_per_period": avg_change, "cagr_endpoints": cagr_end,
        "cagr_nonzero": cagr_nz, "cagr_nonzero_from": nz_from, "cagr_nonzero_to": nz_to,
        "mean_yoy_growth": mean_yoy, "doubling_kind": dbl_kind, "doubling_time": dbl,
        "doubling_basis": dbl_basis,
        "curvature": curv_label, "period_gains": gains, "gain_trend_normalised": curv_norm,
        "steps": steps,
        "largest_jump": {"abs_change": steps[j]["abs_change"], "from": steps[j]["from"],
                         "to": steps[j]["to"], "modified_z": steps[j]["modified_z"],
                         "modified_z_rel": steps[j]["modified_z_rel"], "spike": steps[j]["spike"]},
        "spikes": [f"{s['from']}→{s['to']}" for s in steps if s["spike"]],
        "warnings": sparse_warning(series),
    }


def render_describe(d):
    out = [f"Series: {d['n']} points, {d['first']} → {d['last']} (span {fmt_t(d['span'])} periods)"
           f"   min {num(d['min'])} ({d['min_period']})   max {num(d['max'])} ({d['max_period']})"]
    out.extend(f"WARNING: {w}" for w in d["warnings"])
    out.append(f"Change: {num(d['first_value'])} → {num(d['last_value'])} = {signed(d['change'])} "
               f"({pct(d['relative_change'])}) over {fmt_t(d['span'])} periods")
    out.append(f"Rate:   {signed(d['avg_change_per_period'])} per period (average absolute change)")
    nz = (f", {d['cagr_nonzero_from']}→{d['cagr_nonzero_to']}" if d["cagr_nonzero_from"] else "")
    out.append(f"        CAGR {pct(d['cagr_endpoints'])} per period (endpoints)   "
               f"CAGR {pct(d['cagr_nonzero'])} per period (first→last non-zero{nz})")
    out.append(f"        mean period-over-period growth {pct(d['mean_yoy_growth'])} "
               "(arithmetic mean of the Δ% column, annualised)")
    if d["doubling_kind"]:
        out.append(f"        {d['doubling_kind']} time {num(d['doubling_time'])} periods "
                   f"({'ln 0.5' if d['doubling_kind'] == 'halving' else 'ln 2'} / ln(1 + CAGR), "
                   f"CAGR {d['doubling_basis']})")
    else:
        out.append("        doubling time n/a (CAGR undefined or zero)")
    gains = ", ".join(signed(g) for g in d["period_gains"])
    out.append(f"Curvature: {d['curvature']} — period gains {gains} "
               f"(gain trend {100 * d['gain_trend_normalised']:+.1f}% of mean gain per period)")
    out.append("")
    out.append(f"{'period':<12}{'value':>12}{'Δt':>7}{'Δabs':>12}{'Δ%':>10}   spike?")
    out.append(f"{d['first']:<12}{num(d['first_value']):>12}{'–':>7}{'–':>12}{'–':>10}")
    for s in d["steps"]:
        out.append(f"{s['period']:<12}{num(s['value']):>12}{fmt_t(s['dt']):>7}"
                   f"{signed(s['abs_change']):>12}{pct(s['pct_change']):>10}   "
                   f"{'SPIKE' if s['spike'] else ''}".rstrip())
    j = d["largest_jump"]
    zr = "n/a" if j["modified_z_rel"] is None else f"{j['modified_z_rel']:.2f}"
    verdict = "SPIKE" if j["spike"] else "no spike"
    out.append(f"Largest single-period jump: {signed(j['abs_change'])} ({j['from']}→{j['to']}); "
               f"modified z {j['modified_z']:.2f} (absolute) / {zr} (relative) → {verdict} "
               f"(flag needs |z| > {OUTLIER_Z} on both scales; Iglewicz & Hoaglin 1993)")
    others = [p for p in d["spikes"] if p != f"{j['from']}→{j['to']}"]
    if others:
        out.append(f"Other spike-flagged steps: {', '.join(others)}")
    return "\n".join(out)


# --- fit ---------------------------------------------------------------------


def analyse_fits(series, ceiling=None):
    fits = fit_all(series, ceiling)
    best, ranked, near_tie = recommend(fits)
    caveats = []
    logi = fits[3]
    if logi["ok"]:
        caveats.append(logistic_caveat(logi))
    if near_tie:
        caveats.append(f"Near-tie: top two R² differ by < {NEAR_TIE_R2} ({ranked[0][1]} {r2s(ranked[0][0])} vs "
                       f"{ranked[1][1]} {r2s(ranked[1][0])}) — these data do not distinguish the shapes; "
                       "report both projections rather than picking the curve that gives the wanted answer.")
    return {"command": "fit", "n": len(series), "first": series[0][0], "last": series[-1][0],
            "fits": fits, "best_model": best, "ranking": [{"model": m, "r2": r} for r, m in ranked],
            "caveats": caveats, "warnings": sparse_warning(series)}


def render_fit(f):
    out = [f"Model fits — {f['n']} points, {f['first']} → {f['last']}"]
    out.extend(f"WARNING: {w}" for w in f["warnings"])
    out.append(f"  {'model':<12}{'R²(y)':>8}{'RMSE':>9}   parameters")
    for m in f["fits"]:
        if not m["ok"]:
            out.append(f"  {m['model']:<12}{'n/a':>8}{'n/a':>9}   not fitted: {m['reason']}")
            continue
        out.append(f"  {m['model']:<12}{r2s(m['r2']):>8}{num(m['rmse']):>9}   {formula(m)}")
        if m["model"] == "logistic":
            out.append(f"  {'':<12}{'':>8}{'':>9}   K search: {m['k_search']} (Fisher & Pry 1971)")
    if f["best_model"]:
        others = ", ".join(f"{r['model']} {r2s(r['r2'])}" for r in f["ranking"][1:])
        out.append(f"Best by R² (y-space, comparable across shapes): {f['best_model']} "
                   f"{r2s(f['ranking'][0]['r2'])}" + (f"  (then {others})" if others else ""))
    else:
        out.append("Best model: n/a (no fit has a defined R² — constant series?)")
    for c in f["caveats"]:
        out.append(f"Caveat — {c}")
    return "\n".join(out)


# --- project -----------------------------------------------------------------


def parse_event(text):
    """'label:probability:impact' -> dict; impact in the series' units, signed."""
    parts = text.rsplit(":", 2)
    if len(parts) != 3:
        raise ValueError(f"event {text!r}: expected LABEL:PROBABILITY:IMPACT")
    label, p, impact = parts[0].strip(), parts[1].strip(), parts[2].strip()
    try:
        p, impact = float(p), float(impact)
    except ValueError:
        raise ValueError(f"event {text!r}: probability and impact must be numbers") from None
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"event {text!r}: probability {p} outside [0, 1]")
    return {"label": label or "event", "probability": p, "impact": impact, "expected": p * impact}


def project(series, target_label, t_target, model_choice="auto", ceiling=None, events=()):
    t_first, t_last = series[0][1], series[-1][1]
    ahead = t_target - t_last
    span = t_last - t_first
    multiple = ahead / span
    fits = fit_all(series, ceiling)
    best, ranked, near_tie = recommend(fits)
    ymin = min(y for _, _, y in series)
    rows = []
    for m in fits:
        if not m["ok"]:
            rows.append({"model": m["model"], "ok": False, "reason": m["reason"]})
            continue
        p = predict(m, t_target)
        band = BAND_MULT * m["rmse"]
        notes = []
        if m["model"] == "naive":
            notes.append(f"{num(m['y_last'])} {term(m['avg_change'])} × {fmt_t(ahead)} "
                         "(last value + average change × periods ahead)")
        if m["model"] == "logistic":
            notes.append(f"bounded by K = {num(m['K'])} ({100 * p / m['K']:.1f}% of K at {target_label})")
        if p < 0 and ymin >= 0:
            notes.append("crosses zero — invalid for a non-negative quantity")
        if ceiling is not None and p > ceiling:
            notes.append(f"exceeds the assumed ceiling {num(ceiling)}")
        rows.append({"model": m["model"], "ok": True, "projection": p, "low": p - band,
                     "high": p + band, "rmse": m["rmse"], "r2": m["r2"], "notes": notes})
    selected = best if model_choice == "auto" else model_choice
    sel_row = next((r for r in rows if r["model"] == selected and r["ok"]), None)
    if sel_row is None:
        reason = next((r["reason"] for r in rows if r["model"] == selected and not r["ok"]),
                      "no fitted model has a defined R²")
        raise ValueError(f"model {selected!r} unavailable: {reason}")
    warnings = sparse_warning(series)
    if multiple > 1:
        warnings.append(f"horizon multiple {multiple:.2f} > 1 — projecting {fmt_t(ahead)} periods ahead "
                        f"on {fmt_t(span)} periods of data, further than the observed span; this is "
                        "extrapolation, not a forecast — attach the assumption sheet and signposts")
    caveats = []
    logi = fits[3]
    if logi["ok"] and (selected == "logistic" or model_choice == "auto"):
        caveats.append(logistic_caveat(logi))
    if near_tie and model_choice == "auto":
        caveats.append(f"Near-tie: {ranked[0][1]} {r2s(ranked[0][0])} vs {ranked[1][1]} {r2s(ranked[1][0])} — "
                       "the data do not distinguish these shapes; report both projections.")
    tia = None
    if events:
        adj = sum(e["expected"] for e in events)
        tia = {"baseline": sel_row["projection"], "events": list(events), "adjustment": adj,
               "adjusted": sel_row["projection"] + adj}
    if ceiling is not None:
        ceiling_note = f"{num(ceiling)} (--ceiling; logistic K fixed there)"
    elif logi["ok"]:
        ceiling_note = f"none assumed for naive/linear/exponential; logistic K = {num(logi['K'])} fitted"
    else:
        ceiling_note = "none assumed"
    return {"command": "project", "n": len(series), "first": series[0][0], "last": series[-1][0],
            "target": target_label, "t_target": t_target, "periods_ahead": ahead,
            "observed_span": span, "horizon_multiple": multiple, "horizon_warning": multiple > 1,
            "model_choice": model_choice, "selected": selected, "best_model": best,
            "projections": rows, "tia": tia, "ceiling": ceiling, "ceiling_note": ceiling_note,
            "band": f"± {BAND_MULT:g} × in-sample RMSE — a rough spread, NOT a prediction interval "
                    "(ignores parameter uncertainty and error growth with the horizon)",
            "caveats": caveats, "warnings": warnings}


def render_project(p):
    out = [f"Projection to {p['target']} — {fmt_t(p['periods_ahead'])} periods beyond {p['last']} "
           f"(observed span {fmt_t(p['observed_span'])}; horizon multiple {p['horizon_multiple']:.2f})"]
    out.extend(f"WARNING: {w}" for w in p["warnings"])
    out.append(f"  {'model':<12}{p['target']:>10}   {'± 2·RMSE band':<24}{'R²(y)':>7}   note")
    for r in p["projections"]:
        if not r["ok"]:
            out.append(f"  {r['model']:<12}{'n/a':>10}   {'':<24}{'':>7}   not fitted: {r['reason']}")
            continue
        band = f"[{num(r['low'])}, {num(r['high'])}]"
        out.append(f"  {r['model']:<12}{num(r['projection']):>10}   {band:<24}{r2s(r['r2']):>7}   "
                   f"{'; '.join(r['notes'])}".rstrip())
    sel = next(r for r in p["projections"] if r["model"] == p["selected"])
    how = "best R² in y-space" if p["model_choice"] == "auto" else "--model"
    out.append(f"Selected ({how}): {p['selected']} → {num(sel['projection'])} "
               f"[{num(sel['low'])}, {num(sel['high'])}]")
    if p["tia"]:
        t = p["tia"]
        out.append(f"TIA adjustment (Gordon): baseline {num(t['baseline'])}")
        width = max(len(e["label"]) for e in t["events"])
        for e in t["events"]:
            out.append(f"  {signed(e['expected']):>8}   {e['label']:<{width}}   "
                       f"(P {e['probability']:.2f} × {signed(e['impact'])})")
        out.append(f"  {'=':>8} {num(t['adjusted'])}   adjusted projection "
                   f"(net adjustment {signed(t['adjustment'])})")
    out.append(f"Band: {p['band']}")
    for c in p["caveats"]:
        out.append(f"Caveat — {c}")
    events = (", ".join(e["label"] for e in p["tia"]["events"]) if p["tia"]
              else "none modelled (add --event LABEL:P:IMPACT for TIA)")
    out.append(f"Assumption sheet: drivers persist unchanged; ceiling = {p['ceiling_note']}; "
               f"events considered = {events}")
    return "\n".join(out)


# --- demo --------------------------------------------------------------------


def run_demo(json_mode=False):
    series = parse_series_arg(DEMO_SERIES)
    label, t_target = parse_period(DEMO_TARGET)
    events = [parse_event(e) for e in DEMO_EVENTS]
    d = describe(series)
    f = analyse_fits(series)
    p = project(series, label, t_target, DEMO_MODEL, None, events)
    if json_mode:
        emit_json({"describe": d, "fit": f, "project": p})
        return 0
    ev = " ".join(f'--event "{e}"' for e in DEMO_EVENTS)
    print(f'$ python3 trend.py describe --series "{DEMO_SERIES}"')
    print(render_describe(d))
    print()
    print("$ python3 trend.py fit --demo")
    print(render_fit(f))
    print()
    print(f"$ python3 trend.py project --demo --to {DEMO_TARGET} --model {DEMO_MODEL} {ev}")
    print(render_project(p))
    return 0


# --- selftest ----------------------------------------------------------------


def run_selftest():
    """Hand-verified checks (known answers computed by hand or from exact synthetic
    series before being encoded here). Prints PASS lines and 'selftest OK'."""
    count = [0]

    def check(name, got, want, tol=1e-9):
        count[0] += 1
        if isinstance(want, bool) or isinstance(want, str):
            ok = got == want
            print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got!r}, expected {want!r}")
        else:
            ok = got is not None and abs(got - want) <= tol
            print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got}, expected {want} (tol {tol:g})")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    # Parsing: inline series, ISO month/day, quarter (2020 is a leap year: 1 Jul is day 182 of 366).
    s = parse_series_arg("2021:20, 2019:10,2020:14")
    check("series parses and sorts by period", s[0][1], 2019.0)
    check("series values", s[2][2], 20.0)
    check("ISO date 2020-07-01 -> decimal year", parse_period("2020-07-01")[1], 2020 + 182 / 366)
    check("ISO month 2020-07 -> 2020.5", parse_period("2020-07")[1], 2020.5)
    check("quarter 2024Q3 -> 2024.5", parse_period("2024Q3")[1], 2024.5)

    # CAGR by hand: (40/10)^(1/3) - 1 = 4^(1/3) - 1 = 0.587401... = 58.74 %.
    check("CAGR 10 -> 40 over 3 periods = 58.74 %", cagr(10, 40, 3), 0.5874, 5e-5)
    # Doubling time by hand: ln 2 / ln 1.2 = 0.693147 / 0.182322 = 3.8018 periods.
    check("doubling time at 20 % = 3.80 periods", doubling_time(0.20)[1], 3.80, 5e-3)
    check("doubling time identity ln2/ln1.2", doubling_time(0.20)[1], math.log(2) / math.log(1.2))
    check("halving time at -10 %", doubling_time(-0.10)[1], math.log(0.5) / math.log(0.9))

    # Modified z-score by hand: values 1,2,3,4,100 -> median 3, |dev| 2,1,0,1,97 -> MAD 1
    # -> M(100) = 0.6745 * 97 / 1 = 65.4265; M(1) = -1.349.
    z = modified_z([1, 2, 3, 4, 100])
    check("modified z of planted 100 = 0.6745*97", z[4], 65.4265, 1e-9)
    check("modified z of 1 = -1.349", z[0], -1.349, 1e-9)

    # Exact exponential 10 * 1.2^t, t = 0..7 -> growth 0.20, R² = 1 (log and y space).
    expo = build_series([(t, 10 * 1.2 ** t) for t in range(8)])
    fe = fit_exponential(expo)
    check("exponential fit recovers g = 0.20", fe["growth"], 0.20)
    check("exponential fit R² (log space) = 1", fe["r2_log"], 1.0)
    check("exponential fit R² (y space) = 1", fe["r2"], 1.0)
    check("exponential fit doubling time = ln2/ln1.2", fe["doubling_time"], math.log(2) / math.log(1.2))
    check("exponential refuses non-positive values",
          fit_exponential(build_series([(0, 0), (1, 2), (2, 4), (3, 6)]))["ok"], False)

    # Exact linear 3 + 2.5 t, t = 0..7 -> slope 2.5, intercept 3, R² = 1; projection at t=10 = 28.
    lin = build_series([(t, 3 + 2.5 * t) for t in range(8)])
    fl = fit_linear(lin)
    check("linear fit recovers slope 2.5", fl["slope"], 2.5)
    check("linear fit recovers intercept 3", fl["intercept_first"], 3.0)
    check("linear fit R² = 1", fl["r2"], 1.0)
    check("linear projection at t = 10 is 28", predict(fl, 10), 28.0)

    # Exact logistic K = 100, r = 0.8, t0 = 5, t = 0..10 -> grid + Fisher–Pry recovers
    # K within 5 %, t0 within 0.2 (spec tolerances; the fit is far tighter).
    logi = build_series([(t, 100 / (1 + math.exp(-0.8 * (t - 5)))) for t in range(11)])
    fg = fit_logistic(logi)
    check("logistic fit ok", fg["ok"], True)
    check("logistic K within 5 % of 100", fg["K"] / 100.0, 1.0, 0.05)
    check("logistic t0 within 0.2 of 5", fg["t0"], 5.0, 0.2)
    check("logistic r within 0.05 of 0.8", fg["r"], 0.8, 0.05)
    check("logistic R² > 0.999", fg["r2"] > 0.999, True)
    check("logistic position late (98 % of K)", fg["position"], "late (> 50% of K)")
    fk = fit_logistic(logi, ceiling=100.0)
    check("fixed-ceiling logistic recovers r = 0.8", fk["r"], 0.8, 1e-6)
    check("fixed-ceiling logistic recovers t0 = 5", fk["t0"], 5.0, 1e-6)
    lower = build_series([(t, 100 / (1 + math.exp(-0.8 * (t - 5)))) for t in range(4)])
    check("lower-half data triggers the Meade & Islam caveat", fit_logistic(lower)["lower_half_only"], True)

    # SKILL.md worked example: EV share 4 -> 21 over 2020-2024: +4.25 pp/period average
    # change; CAGR (21/4)^(1/4) - 1 = 0.5137; gains 5,5,4,3 shrink -> saturating; no spike.
    ev = parse_series_arg(DEMO_SERIES)
    d = describe(ev)
    check("EV average change +4.25 per period", d["avg_change_per_period"], 4.25)
    check("EV CAGR (21/4)^(1/4) - 1 = 51.37 %", d["cagr_endpoints"], 0.5137, 1e-4)
    check("EV curvature read = saturating", d["curvature"], "saturating")
    check("EV largest jump not a spike", d["largest_jump"]["spike"], False)
    check("EV series has no sparse warning", len(d["warnings"]), 0)

    # Planted spike: +44 then -41 among steps of 1-2 -> flagged by the MAD rule.
    spiked = parse_series_arg("0:10,1:11,2:13,3:14,4:16,5:60,6:19,7:21,8:22")
    ds = describe(spiked)
    check("planted spike: largest jump is +44", ds["largest_jump"]["abs_change"], 44.0)
    check("planted spike flagged as outlier", ds["largest_jump"]["spike"], True)
    check("planted spike: both steps flagged", len(ds["spikes"]), 2)
    steep = build_series([(2015 + t, 10 * 1.5 ** t) for t in range(10)])
    check("clean 50 %/period exponential is not flagged as a spike", len(describe(steep)["spikes"]), 0)

    # Projection: 2030 is 6 periods beyond 2024 on 4 periods of data -> multiple 1.5, warned;
    # naive baseline 21 + 6 × 4.25 = 46.5; TIA -2.5 -1.6 +0.9 -> 43.3 (SKILL.md worked example).
    events = [parse_event(e) for e in DEMO_EVENTS]
    p = project(ev, "2030", 2030.0, "naive", None, events)
    check("horizon multiple 6/4 = 1.5", p["horizon_multiple"], 1.5)
    check("horizon multiple > 1 raises the warning", p["horizon_warning"], True)
    check("horizon warning text present", any("horizon multiple" in w for w in p["warnings"]), True)
    check("naive baseline 21 + 6 × 4.25 = 46.5", p["tia"]["baseline"], 46.5)
    check("TIA adjusted 46.5 - 2.5 - 1.6 + 0.9 = 43.3", p["tia"]["adjusted"], 43.3)
    p2 = project(ev, "2026", 2026.0, "auto")
    check("horizon multiple 2/4 = 0.5 -> no warning", p2["horizon_warning"], False)
    check("auto selects the best-R² model", p2["selected"], p2["best_model"])
    check("naive band = ± 2 RMSE", p["projections"][0]["high"] - p["projections"][0]["projection"],
          2 * model_naive(ev)["rmse"])
    check("sparse series warns", len(describe(parse_series_arg("2020:1,2021:2,2022:4"))["warnings"]), 1)

    print(f"ALL {count[0]} CHECKS PASSED")
    print("selftest OK")
    return 0


# --- CLI ---------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(
        description="Quantify (describe), fit (linear / exponential / logistic S-curve) and "
                    "project a trend series with a naive ± 2·RMSE band, horizon multiple and "
                    "optional Trend Impact Analysis event adjustment.",
        epilog='Series input: --file series.csv|json (columns period,value; >= 3 points), '
               '--series "2019:10,2020:14,2021:20", or --demo (SKILL.md worked example).',
    )
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true",
                        help="reproduce the SKILL.md worked example (describe, fit, project --to 2030 with TIA events)")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    sub = parser.add_subparsers(dest="command", metavar="{describe,fit,project}")
    for name, helptext in [
        ("describe", "n, span, min/max, CAGR, average change, doubling time, YoY table, spike check"),
        ("fit", "linear, exponential (log-linear) and logistic S-curve fits with R²; best model + caveats"),
        ("project", "projection per model to --to PERIOD with ± 2·RMSE band, horizon multiple, TIA events"),
    ]:
        p = sub.add_parser(name, help=helptext, description=helptext)
        p.add_argument("--file", help="CSV or JSON series (period,value); '-' reads stdin")
        p.add_argument("--series", help='inline series "2019:10,2020:14,2021:20"')
        p.add_argument("--demo", action="store_true", default=argparse.SUPPRESS,
                       help="use the SKILL.md worked-example series (EV share 2020–2024)")
        p.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                       help="machine-readable JSON output")
        if name in ("fit", "project"):
            p.add_argument("--ceiling", type=float,
                           help="assumed saturation level K for the logistic fit (skips the K grid search)")
        if name == "project":
            p.add_argument("--to", required=True, metavar="PERIOD", help="target period, e.g. 2030 or 2030-06")
            p.add_argument("--model", choices=["auto"] + list(MODEL_ORDER), default="auto",
                           help="model to select (default auto = best R² in y-space)")
            p.add_argument("--event", action="append", default=[], metavar="LABEL:P:IMPACT",
                           help="TIA bending event, e.g. \"subsidy rollback:0.5:-5\" (repeatable)")
    return parser


def get_series(args, parser):
    demo = getattr(args, "demo", False)
    if sum(1 for x in (args.file, args.series, demo) if x) != 1:
        parser.error('pass exactly one of --file PATH, --series "p:v,...", or --demo')
    try:
        if demo:
            return parse_series_arg(DEMO_SERIES)
        if args.series:
            return parse_series_arg(args.series)
        return load_file(args.file)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(f"could not load series: {exc}")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    json_mode = getattr(args, "json", False)
    if not args.command:
        if getattr(args, "demo", False):
            return run_demo(json_mode)
        parser.error("choose a command: describe | fit | project  (or --demo / --selftest)")
    series = get_series(args, parser)
    if args.command == "describe":
        d = describe(series)
        emit_json(d) if json_mode else print(render_describe(d))
        return 0
    ceiling = args.ceiling
    if ceiling is not None and ceiling <= max(y for _, _, y in series):
        parser.error(f"--ceiling {num(ceiling)} must exceed the largest observation "
                     f"{num(max(y for _, _, y in series))}")
    if args.command == "fit":
        f = analyse_fits(series, ceiling)
        emit_json(f) if json_mode else print(render_fit(f))
        return 0
    try:
        label, t_target = parse_period(args.to)
        events = [parse_event(e) for e in args.event]
        if t_target <= series[-1][1]:
            raise ValueError(f"--to {args.to} is not beyond the last observation {series[-1][0]}")
        p = project(series, label, t_target, args.model, ceiling, events)
    except ValueError as exc:
        parser.error(str(exc))
    emit_json(p) if json_mode else print(render_project(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
