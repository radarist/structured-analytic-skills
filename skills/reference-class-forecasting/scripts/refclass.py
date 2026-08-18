#!/usr/bin/env python3
"""refclass.py — reference class forecasting: outcome distribution, position, uplift.

Implements the three steps of reference class forecasting exactly as ../SKILL.md
states them (Flyvbjerg 2006, after Kahneman & Tversky 1979 and Lovallo &
Kahneman 2003):

  describe  step 2 — the reference class's outcome distribution: n, min/max,
            P10 / P25 / P50 / P75 / P80 / P90, mean, sd, and a skew note.
  position  step 3 — where the inside-view estimate falls in that distribution:
            percentile rank as a band [share strictly below, share at-or-below]
            plus an interpolated point, with an interpretation string.
  uplift    step 3 — the multiplier / additive uplift that moves the inside
            estimate to the target percentile (default P80, the level the UK
            Department for Transport adopted; Flyvbjerg 2006), the residual
            inside-view adjustment (only with a stated reason) and the final
            forecast.
  report    every section above, in the SKILL.md output-template order.

Definitions
  * Quantiles: Hyndman & Fan (1996) definition 7 — linear interpolation between
    order statistics; the default of NumPy, R and Excel PERCENTILE.INC. With the
    sorted sample x[1..n] and h = (n - 1) p + 1:
        Q(p) = x[floor h] + (h - floor h) * (x[floor h + 1] - x[floor h])
  * Percentile rank of the inside estimate v: the band
        [100 * #(x < v) / n , 100 * #(x <= v) / n]
    and the interpolated point Q^-1(v) under the same type-7 definition.
  * Uplift to target percentile p (Flyvbjerg 2006; HM Treasury Green Book
    supplementary guidance on optimism bias):
        multiplier  m = Q(p) / inside        additive  a = Q(p) - inside
        forecast(p) = base * m               (base = the absolute figure the inside
                                              estimate stands for; base = inside
                                              when the class is in absolute units)
  * Residual inside-view adjustment k (must come with --reason):
        final = forecast(p) * k
    If final falls below the class-median forecast, the tool reports the
    "adjusting away the base rate" verdict and exits 2.
  * Sample size: n < 3 is refused (exit 1); n < 8 prints a
    "reference class too small" warning.
  * Skew: g1 = m3 / m2^1.5 (moment coefficient); the note compares mean and
    median so a right-skewed class is never summarised by its mean.

Stdlib only. Python 3.9+. Deterministic: no randomness, no wall clock.

Usage:
    python3 refclass.py describe --file class.json
    python3 refclass.py position --file class.csv --inside 1.0
    python3 refclass.py uplift   --file class.json --inside 1.0 --base 9 --target-percentile 80
    python3 refclass.py report   --file class.json --inside 1.0 --base 9 --adjust 0.9 --reason "..."
    python3 refclass.py report   --demo            # the SKILL.md worked example
    python3 refclass.py --selftest
"""

import argparse
import contextlib
import csv
import io
import json
import math
import sys

MIN_N = 3          # below this a distribution cannot be described -> refuse
SMALL_N = 8        # below this percentiles are only indicative -> warn
DEFAULT_TARGET = 80.0

VALUE_KEYS = ("value", "outcome", "ratio", "overrun", "actual_over_estimate", "result", "x")
NAME_KEYS = ("name", "project", "case", "id", "label")
SOURCE_KEYS = ("source", "src", "reference", "ref")

# The SKILL.md worked example: ten *illustrative* internal R&D / software
# projects, outcome = actual / planned duration. Inside view = plan as stated
# (ratio 1.0) for a 9-month plan; target P80; a small evidenced adjustment.
DEMO = {
    "quantity": "delivery schedule of Feature X (planned 9 months)",
    "kind": "ratio",
    "unit": "actual / planned duration",
    "class": "internal ML/R&D features 2019-2025, >= 3 engineers, novel model "
             "component, planned >= 6 months (illustrative)",
    "outcomes": [
        {"name": "Project Alder", "value": 1.0, "source": "PMO schedule log (illustrative)"},
        {"name": "Project Birch", "value": 1.1, "source": "PMO schedule log (illustrative)"},
        {"name": "Project Cedar", "value": 1.2, "source": "PMO schedule log (illustrative)"},
        {"name": "Project Dogwood", "value": 1.3, "source": "PMO schedule log (illustrative)"},
        {"name": "Project Elm", "value": 1.5, "source": "PMO schedule log (illustrative)"},
        {"name": "Project Fir", "value": 1.6, "source": "PMO schedule log (illustrative)"},
        {"name": "Project Ginkgo", "value": 1.8, "source": "PMO schedule log (illustrative)"},
        {"name": "Project Hazel", "value": 2.0, "source": "PMO schedule log (illustrative)"},
        {"name": "Project Ironwood", "value": 2.4, "source": "PMO schedule log (illustrative)"},
        {"name": "Project Juniper", "value": 3.0, "source": "PMO schedule log (illustrative)"},
    ],
}
DEMO_ARGS = {
    "inside": 1.0,
    "base": 9.0,
    "base_unit": "months",
    "target": 80.0,
    "adjust": 0.9,
    "reason": "the same team's last four comparable features finished at a median "
              "ratio of 1.3 (PMO log) against the class median 1.55 - evidence of "
              "better-than-class estimating, not a feeling",
}


# --- input -------------------------------------------------------------------

def _find_key(mapping, candidates):
    lowered = {str(k).strip().lower(): k for k in mapping}
    for cand in candidates:
        if cand in lowered:
            return lowered[cand]
    return None


def parse_outcomes(raw):
    """Normalise a list of numbers or row-dicts into [(name, value, source)]."""
    out = []
    for i, row in enumerate(raw, start=1):
        if isinstance(row, dict):
            vkey = _find_key(row, VALUE_KEYS)
            if vkey is None:
                raise ValueError(f"row {i}: no value column {VALUE_KEYS}; got keys {list(row)}")
            value = float(row[vkey])
            nkey = _find_key(row, NAME_KEYS)
            skey = _find_key(row, SOURCE_KEYS)
            name = str(row[nkey]).strip() if nkey is not None else f"case {i}"
            source = str(row[skey]).strip() if skey is not None else ""
        else:
            value = float(row)
            name, source = f"case {i}", ""
        if not math.isfinite(value):
            raise ValueError(f"row {i}: value {value!r} is not finite")
        out.append((name, value, source))
    return out


def load_class(path):
    """Load a reference class from CSV or JSON (chosen by extension).

    CSV : header row with a value column (value|outcome|ratio|...) and optional
          name / source columns.
    JSON: a list of numbers, a list of {name, value, source} objects, or an object
          {"quantity", "kind": "ratio"|"absolute", "unit", "class", "sources",
           "outcomes": [...]}.
    """
    meta = {"quantity": "", "kind": "", "unit": "", "class": "", "sources": []}
    with open(path, newline="", encoding="utf-8") as fh:
        if path.lower().endswith(".json"):
            data = json.load(fh)
            if isinstance(data, dict):
                for k in ("quantity", "kind", "unit", "class"):
                    if data.get(k):
                        meta[k] = str(data[k])
                srcs = data.get("sources", [])
                meta["sources"] = [str(s) for s in srcs] if isinstance(srcs, list) else [str(srcs)]
                data = data.get("outcomes", [])
            return parse_outcomes(data), meta
        return parse_outcomes(list(csv.DictReader(fh))), meta


# --- the math (SKILL.md steps 2-3) --------------------------------------------

def quantile7(values, p):
    """Hyndman & Fan definition 7 (NumPy / R default) for 0 <= p <= 1."""
    s = sorted(values)
    n = len(s)
    if n == 0:
        raise ValueError("empty sample")
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"p={p} outside [0, 1]")
    h = (n - 1) * p
    lo = int(math.floor(h))
    if lo >= n - 1:
        return float(s[-1])
    return s[lo] + (h - lo) * (s[lo + 1] - s[lo])


def inverse_quantile7(values, v):
    """Interpolated percentile (0..1) of v under the type-7 definition; the
    inverse of quantile7 on [min, max], clamped outside."""
    s = sorted(values)
    n = len(s)
    if v <= s[0]:
        return 0.0
    if v >= s[-1]:
        return 1.0
    for k in range(n - 1):
        if s[k] <= v < s[k + 1]:
            return (k + (v - s[k]) / (s[k + 1] - s[k])) / (n - 1)
    return 1.0  # unreachable


def describe(values):
    """n, min, P10/P25/P50/P75/P80/P90, max, mean, sd (n-1), skew g1, notes."""
    n = len(values)
    mean = sum(values) / n
    ss = sum((x - mean) ** 2 for x in values)
    sd = math.sqrt(ss / (n - 1)) if n > 1 else 0.0
    m2 = ss / n
    m3 = sum((x - mean) ** 3 for x in values) / n
    skew = m3 / (m2 ** 1.5) if m2 > 0 else 0.0
    q = {p: quantile7(values, p / 100.0) for p in (10, 25, 50, 75, 80, 90)}
    if mean > q[50] * 1.02:
        skew_note = "right-skewed (mean > median): summarise with percentiles, not the mean"
    elif mean < q[50] * 0.98:
        skew_note = "left-skewed (mean < median): summarise with percentiles, not the mean"
    else:
        skew_note = "roughly symmetric (mean ~ median)"
    warnings = []
    if n < SMALL_N:
        warnings.append(f"reference class too small (n = {n} < {SMALL_N}): P10/P90 are "
                        "extrapolations of the extremes; treat every percentile as indicative "
                        "and widen the class or say so in the report")
    return {"n": n, "min": min(values), "max": max(values), "quantiles": q, "mean": mean,
            "sd": sd, "skew": skew, "skew_note": skew_note, "warnings": warnings}


def position(values, inside):
    """Percentile rank of the inside estimate: band + interpolated point."""
    n = len(values)
    below = sum(1 for x in values if x < inside)
    at_or_below = sum(1 for x in values if x <= inside)
    lo = 100.0 * below / n
    hi = 100.0 * at_or_below / n
    point = 100.0 * inverse_quantile7(values, inside)
    if hi <= 10.0 or point < 10.0:
        interp = ("more optimistic than at least 90 % of the reference class - the classic "
                  "planning-fallacy signature; treat the inside estimate as a lower bound, not a forecast")
    elif point < 50.0:
        interp = ("more optimistic than the class median - expect the outside view to pull the "
                  "forecast up; ask what specific evidence justifies beating the median")
    elif point <= 80.0:
        interp = ("at or above the class median - the inside view already carries contingency; "
                  "check it is not being padded a second time by the uplift")
    else:
        interp = ("more conservative than 80 % of the class - either the estimate is sandbagged or "
                  "the reference class is too easy; re-check the class definition")
    return {"below": below, "at_or_below": at_or_below, "pct_low": lo, "pct_high": hi,
            "pct_point": point, "interpretation": interp}


def uplift(values, inside, target_pct, base=None, adjust=1.0):
    """Multiplier / additive uplift to the target percentile, forecasts, and the
    residual-adjustment check. base defaults to inside (absolute classes)."""
    if inside <= 0:
        raise ValueError("inside estimate must be > 0 for a multiplicative uplift")
    q_t = quantile7(values, target_pct / 100.0)
    q_50 = quantile7(values, 0.5)
    base_v = inside if base is None else base
    mult = q_t / inside
    add = q_t - inside
    f_target = base_v * mult
    f_50 = base_v * q_50 / inside
    final = f_target * adjust
    notes = []
    verdict_ok = True
    if target_pct < 50.0:
        notes.append(f"target P{target_pct:g} is below the class median - defensible only for a "
                     "portfolio owner who can net overruns against underruns (Flyvbjerg 2006)")
    if adjust != 1.0:
        if target_pct >= 50.0 and final < f_50:
            verdict_ok = False
            notes.append(f"adjustment x{adjust:g} pulls the forecast ({final:.4g}) below the class-median "
                         f"forecast ({f_50:.4g}) - this is adjusting away the base rate; only exceptional, "
                         "documented evidence of better-than-class estimating justifies it")
        else:
            notes.append(f"adjusted forecast {final:.4g} stays at or above the class-median forecast "
                         f"{f_50:.4g} - the adjustment does not erase the base rate")
    return {"target_pct": target_pct, "q_target": q_t, "q_50": q_50, "multiplier": mult,
            "additive": add, "base": base_v, "forecast_target": f_target, "forecast_50": f_50,
            "adjust": adjust, "final": final, "notes": notes, "verdict_ok": verdict_ok}


# --- rendering ---------------------------------------------------------------

def _rounded(obj, ndigits=10):
    """Round floats (recursively) so JSON output is free of binary noise."""
    if isinstance(obj, float):
        return round(obj, ndigits)
    if isinstance(obj, dict):
        return {k: _rounded(v, ndigits) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_rounded(v, ndigits) for v in obj]
    return obj


def fmt(x):
    """Compact, stable number formatting: 4 significant digits, whole numbers as 1.00."""
    if abs(x) >= 1000:
        return f"{x:,.0f}"
    if float(x).is_integer():
        return f"{x:.2f}"
    return f"{x:.4g}"


def render_describe(d, meta, unit_label):
    lines = []
    cls = meta.get("class") or "(class not described - state it in the report)"
    lines.append(f"Reference class: {cls}")
    lines.append(f"Outcome measure: {unit_label}")
    if meta.get("sources"):
        lines.append("Sources: " + "; ".join(meta["sources"]))
    q = d["quantiles"]
    lines.append(f"n {d['n']}   min {fmt(d['min'])}   P10 {fmt(q[10])}   P25 {fmt(q[25])}   "
                 f"P50 {fmt(q[50])}   P75 {fmt(q[75])}   P80 {fmt(q[80])}   P90 {fmt(q[90])}   max {fmt(d['max'])}")
    lines.append(f"mean {fmt(d['mean'])}   sd {fmt(d['sd'])}   skew g1 {d['skew']:+.2f} - {d['skew_note']}")
    lines.append("(quantiles: Hyndman & Fan type 7, linear interpolation - NumPy/R default)")
    for w in d["warnings"]:
        lines.append(f"WARNING: {w}")
    return lines


def render_position(p, inside, d, unit_label):
    lines = []
    lines.append(f"Inside-view estimate: {fmt(inside)} ({unit_label})")
    lines.append(f"outcomes below it: {p['below']}/{d['n']} ({p['pct_low']:.0f} %)   "
                 f"at or below: {p['at_or_below']}/{d['n']} ({p['pct_high']:.0f} %)   "
                 f"percentile rank: {p['pct_low']:.0f}-{p['pct_high']:.0f} % "
                 f"(interpolated {p['pct_point']:.1f} %)")
    lines.append(f"Interpretation: {p['interpretation']}")
    return lines


def render_uplift(u, inside, base_unit):
    t = u["target_pct"]
    lines = []
    lines.append(f"multiplier = Q(P{t:g}) / inside = {fmt(u['q_target'])} / {fmt(inside)} = "
                 f"x{u['multiplier']:.2f} ({100 * (u['multiplier'] - 1):+.0f} %)")
    lines.append(f"additive   = Q(P{t:g}) - inside = {u['additive']:+.4g}")
    bu = f" {base_unit}" if base_unit else ""
    lines.append(f"base {fmt(u['base'])}{bu} -> P50 forecast {fmt(u['forecast_50'])}{bu} -> "
                 f"P{t:g} forecast {fmt(u['forecast_target'])}{bu}")
    return lines


def render_adjust(u, reason, base_unit):
    bu = f" {base_unit}" if base_unit else ""
    lines = []
    if u["adjust"] == 1.0:
        lines.append("none (x1.00) - no specific, evidenced reason to depart from the class")
        lines.append(f"final forecast: {fmt(u['final'])}{bu} at P{u['target_pct']:g}")
    else:
        lines.append(f"x{u['adjust']:g} - reason: {reason}")
        lines.append(f"final forecast: {fmt(u['forecast_target'])}{bu} x {u['adjust']:g} = "
                     f"{fmt(u['final'])}{bu} at P{u['target_pct']:g}")
    for n in u["notes"]:
        lines.append(("CHECK FAILED: " if not u["verdict_ok"] and "adjusting away" in n else "note: ") + n)
    return lines


# --- CLI ---------------------------------------------------------------------

def validate_class(values):
    """Refuse a class too small to describe a distribution (n < MIN_N)."""
    n = len(values)
    if n < MIN_N:
        raise ValueError(f"reference class of n = {n} is too small to describe a distribution "
                         f"(need >= {MIN_N}; >= {SMALL_N} to trust percentiles; Flyvbjerg's road class had 172)")
    return n


def build_parser():
    parser = argparse.ArgumentParser(
        description="Reference class forecasting: describe a reference class's outcome "
                    "distribution, position an inside-view estimate in it, and compute the "
                    "uplift to a target percentile (Flyvbjerg 2006; Kahneman & Tversky 1979).")
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    sub = parser.add_subparsers(dest="command")
    for name, helptext in [
        ("describe", "n, min, P10/P25/P50/P75/P80/P90, max, mean, sd, skew note"),
        ("position", "percentile rank of the inside estimate within the class + interpretation"),
        ("uplift", "multiplier / additive uplift to the target percentile, forecasts, adjustment check"),
        ("report", "all sections in the SKILL.md output order"),
    ]:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--file", help="CSV or JSON reference class (see module docstring)")
        p.add_argument("--demo", action="store_true", help="use the SKILL.md worked example")
        p.add_argument("--kind", choices=["ratio", "absolute"],
                       help="outcomes are actual/estimate ratios (default) or absolute values")
        p.add_argument("--json", action="store_true", help="JSON output")
        if name != "describe":
            p.add_argument("--inside", type=float, help="inside-view estimate in class units "
                           "(ratio classes default to 1.0 = the plan as stated)")
            p.add_argument("--base", type=float, help="absolute figure the inside estimate stands "
                           "for (ratio classes), e.g. 9 for a 9-month plan")
            p.add_argument("--base-unit", default="", help="label for the base figure, e.g. months")
        if name in ("uplift", "report"):
            p.add_argument("--target-percentile", type=float, default=DEFAULT_TARGET,
                           help="target confidence percentile (default 80)")
            p.add_argument("--adjust", type=float, default=1.0,
                           help="residual inside-view adjustment multiplier (needs --reason)")
            p.add_argument("--reason", default="", help="the specific, evidenced reason for --adjust")
    return parser


def get_class(args, parser):
    if args.demo:
        return parse_outcomes(DEMO["outcomes"]), dict(DEMO, sources=[])
    if args.file:
        try:
            return load_class(args.file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(f"could not load {args.file}: {exc}")
    parser.error("pass --file PATH or --demo")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.command:
        parser.error("choose a command: describe | position | uplift | report  (or --selftest)")
    rows, meta = get_class(args, parser)
    values = [v for _, v, _ in rows]
    try:
        validate_class(values)
    except ValueError as exc:
        parser.error(str(exc))
    kind = args.kind or meta.get("kind") or "ratio"
    unit_label = meta.get("unit") or ("actual / estimate ratio" if kind == "ratio" else "absolute units")
    d = describe(values)

    inside = base = None
    base_unit = ""
    if args.command != "describe":
        inside = args.inside
        base = args.base
        base_unit = args.base_unit
        if args.demo and inside is None and base is None:
            inside, base, base_unit = DEMO_ARGS["inside"], DEMO_ARGS["base"], DEMO_ARGS["base_unit"]
        if inside is None:
            if kind == "ratio":
                inside = 1.0
            else:
                parser.error("--inside is required for an absolute-valued class")
        if inside <= 0:
            parser.error("--inside must be > 0")
        if base is not None and base <= 0:
            parser.error("--base must be > 0")

    out = {"quantity": meta.get("quantity", ""), "class": meta.get("class", ""), "kind": kind,
           "unit": unit_label, "sources": meta.get("sources", []), "distribution": d}
    exit_code = 0
    text = []
    if args.command == "describe":
        text += render_describe(d, meta, unit_label)
    elif args.command == "position":
        p = position(values, inside)
        out.update(inside=inside, position=p)
        text += render_position(p, inside, d, unit_label)
        for w in d["warnings"]:
            text.append(f"WARNING: {w}")
    else:
        t = args.target_percentile
        if not 0.0 < t < 100.0:
            parser.error("--target-percentile must be strictly between 0 and 100")
        adjust, reason = args.adjust, args.reason
        if args.demo and adjust == 1.0 and not reason and args.inside is None:
            adjust, reason = DEMO_ARGS["adjust"], DEMO_ARGS["reason"]
        if adjust <= 0:
            parser.error("--adjust must be > 0")
        if adjust != 1.0 and not reason.strip():
            parser.error("--adjust requires --reason: adjust the inside view only with a specific, "
                         "evidenced reason (what makes this case different)")
        p = position(values, inside)
        u = uplift(values, inside, t, base, adjust)
        out.update(inside=inside, position=p, uplift=u, reason=reason, base_unit=base_unit)
        if not u["verdict_ok"]:
            exit_code = 1
        if args.command == "uplift":
            text += render_uplift(u, inside, base_unit)
            text += ["Residual inside-view adjustment:"] + ["  " + s for s in render_adjust(u, reason, base_unit)]
            for w in d["warnings"]:
                text.append(f"WARNING: {w}")
        else:
            q = meta.get("quantity") or "(forecast quantity not stated - state it)"
            text.append(f"Reference class forecast - {q}")
            text.append("")
            text.append("1. Reference class and its outcome distribution")
            text += ["   " + s for s in render_describe(d, meta, unit_label)]
            text.append("")
            text.append("2. Position of the inside view")
            text += ["   " + s for s in render_position(p, inside, d, unit_label)]
            text.append("")
            text.append(f"3. Uplift to the target percentile (P{t:g})")
            text += ["   " + s for s in render_uplift(u, inside, base_unit)]
            text.append("")
            text.append("4. Residual inside-view adjustment")
            text += ["   " + s for s in render_adjust(u, reason, base_unit)]
            text.append("")
            bu = f" {base_unit}" if base_unit else ""
            text.append(f"Forecast: {fmt(u['final'])}{bu} at P{t:g}  (class P50 {fmt(u['forecast_50'])}{bu}; "
                        f"inside view {fmt(u['base'])}{bu} sat at the {p['pct_low']:.0f}-{p['pct_high']:.0f} % "
                        f"point of the class)")
            text.append("Verdict: " + ("OK - forecast rests on the reference class; adjustment stated with reason"
                                       if u["verdict_ok"] else
                                       "FAIL - the adjustment erases the base rate (see CHECK FAILED above)"))
    if args.json:
        out["exit_code"] = exit_code
        print(json.dumps(_rounded(out), indent=1, sort_keys=True))
    else:
        print("\n".join(text))
    return exit_code


# --- selftest ----------------------------------------------------------------

def run_selftest():
    """Hand-verified checks. Every expected value was computed by hand from the
    definitions in the module docstring before being encoded here."""
    checks = []

    def check(name, got, want, tol=1e-9):
        ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and not isinstance(want, bool) \
            else (got == want)
        checks.append(ok)
        shown = f"got {got:.6f}, expected {want:.6f}" if isinstance(want, float) else f"got {got!r}, expected {want!r}"
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {shown}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    # Class A (ratios, n = 10, sorted): 1.0 1.1 1.2 1.3 1.5 1.6 1.8 2.0 2.4 3.0
    # Type 7: h = 9p + 1 (1-indexed).
    #   P10: h = 1.9  -> 1.0 + 0.9 (0.1) = 1.09
    #   P25: h = 3.25 -> 1.2 + 0.25(0.1) = 1.225
    #   P50: h = 5.5  -> 1.5 + 0.5 (0.1) = 1.55
    #   P75: h = 7.75 -> 1.8 + 0.75(0.2) = 1.95
    #   P80: h = 8.2  -> 2.0 + 0.2 (0.4) = 2.08
    #   P90: h = 9.1  -> 2.4 + 0.1 (0.6) = 2.46
    a = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.4, 3.0]
    check("type-7 P10 = 1.09", quantile7(a, 0.10), 1.09)
    check("type-7 P25 = 1.225", quantile7(a, 0.25), 1.225)
    check("type-7 P50 = 1.55", quantile7(a, 0.50), 1.55)
    check("type-7 P75 = 1.95", quantile7(a, 0.75), 1.95)
    check("type-7 P80 = 2.08", quantile7(a, 0.80), 2.08)
    check("type-7 P90 = 2.46", quantile7(a, 0.90), 2.46)
    check("type-7 P0 = min", quantile7(a, 0.0), 1.0)
    check("type-7 P100 = max", quantile7(a, 1.0), 3.0)
    # unsorted input must give the same answer
    check("type-7 order-independent", quantile7(list(reversed(a)), 0.80), 2.08)

    # mean = 16.9/10 = 1.69; sum of squared deviations = 3.589; sd = sqrt(3.589/9)
    d = describe(a)
    check("mean = 1.69", d["mean"], 1.69)
    check("sd (n-1) = sqrt(3.589/9)", d["sd"], math.sqrt(3.589 / 9))
    # skew g1 = m3/m2^1.5 with m2 = 0.3589, m3 = 0.191868 -> 0.89236 (right-skewed)
    check("skew g1 = 0.191868/0.3589^1.5", d["skew"], 0.191868 / (0.3589 ** 1.5), tol=1e-9)
    check("skew note flags right skew", "right-skewed" in d["skew_note"], True)
    check("n = 10 -> no small-n warning", len(d["warnings"]), 0)

    # position of the inside view 1.0 (the plan as stated): 0 below, 1 at-or-below -> 0-10 %
    p = position(a, 1.0)
    check("position 1.0: pct_low = 0", p["pct_low"], 0.0)
    check("position 1.0: pct_high = 10", p["pct_high"], 10.0)
    check("position 1.0: interpolated = 0", p["pct_point"], 0.0)
    check("position 1.0: planning-fallacy interpretation", "planning-fallacy" in p["interpretation"], True)
    # inside 1.4 lies between x4 = 1.3 and x5 = 1.5 -> k = 3 (0-based) + 0.5 -> 3.5/9 = 38.9 %
    p14 = position(a, 1.4)
    check("position 1.4: 4 below, 4 at-or-below (40-40 %)", (p14["pct_low"], p14["pct_high"]), (40.0, 40.0))
    check("position 1.4: interpolated 3.5/9", p14["pct_point"], 100 * 3.5 / 9)
    check("inverse of Q: 2.08 -> 80 %", 100 * inverse_quantile7(a, 2.08), 80.0, tol=1e-9)
    check("position 3.0 (max): 100 %", position(a, 3.0)["pct_point"], 100.0)

    # uplift to P80 for inside 1.0: multiplier 2.08/1.0 = x2.08, additive +1.08;
    # base 9 months -> P50 forecast 9*1.55 = 13.95, P80 forecast 9*2.08 = 18.72
    u = uplift(a, 1.0, 80.0, base=9.0)
    check("uplift P80 multiplier = x2.08", u["multiplier"], 2.08)
    check("uplift P80 additive = +1.08", u["additive"], 1.08)
    check("P50 forecast = 13.95", u["forecast_50"], 13.95)
    check("P80 forecast = 18.72", u["forecast_target"], 18.72)
    check("no adjustment -> final = P80 forecast", u["final"], 18.72)
    check("no adjustment -> verdict OK", u["verdict_ok"], True)
    # inside 1.3 (plan already carries 30 % contingency): multiplier 2.08/1.3 = 1.6
    check("uplift for inside 1.3 = 2.08/1.3", uplift(a, 1.3, 80.0)["multiplier"], 2.08 / 1.3)
    # residual adjustment x0.9 -> 16.848 >= 13.95 -> OK; x0.7 -> 13.104 < 13.95 -> FAIL
    ok = uplift(a, 1.0, 80.0, base=9.0, adjust=0.9)
    check("adjust x0.9 -> 16.848", ok["final"], 16.848)
    check("adjust x0.9 stays above P50 -> OK", ok["verdict_ok"], True)
    bad = uplift(a, 1.0, 80.0, base=9.0, adjust=0.7)
    check("adjust x0.7 -> 13.104", bad["final"], 13.104)
    check("adjust x0.7 falls below P50 -> verdict FAIL", bad["verdict_ok"], False)
    # base defaults to inside for absolute classes
    check("base defaults to inside", uplift(a, 1.0, 80.0)["forecast_target"], 2.08)

    # Class B (absolute months, n = 10, sorted): 6 7 8 9 10 12 14 16 18 24
    #   P80: h = 8.2 -> 16 + 0.2 (2) = 16.4;  inside 9 -> x16.4/9, +7.4
    #   position of 9: below 3 (6,7,8), at-or-below 4 -> 30-40 %; interpolated 3/9 = 33.3 %
    b = [6, 7, 8, 9, 10, 12, 14, 16, 18, 24]
    check("class B: P80 = 16.4", quantile7(b, 0.80), 16.4)
    ub = uplift(b, 9.0, 80.0)
    check("class B: multiplier 16.4/9", ub["multiplier"], 16.4 / 9)
    check("class B: additive +7.4", ub["additive"], 7.4)
    pb = position(b, 9.0)
    check("class B: position 9 -> 30-40 %", (pb["pct_low"], pb["pct_high"]), (30.0, 40.0))
    check("class B: interpolated 3/9", pb["pct_point"], 100 * 3 / 9)

    # small-n handling: n = 5 warns; n = 2 is refused (ValueError -> CLI exit 1)
    check("n = 5 -> small-n warning", "too small" in " ".join(describe([1.0, 1.2, 1.5, 2.0, 2.5])["warnings"]), True)
    check("n = 8 -> no small-n warning", len(describe([1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0])["warnings"]), 0)
    refused = False
    try:
        validate_class([1.0, 2.0])
    except ValueError:
        refused = True
    check("n = 2 -> refused", refused, True)
    check("n = 3 -> accepted", validate_class([1.0, 2.0, 3.0]), 3)

    # CLI exit codes: 0 pass, 1 failing analytic verdict, 2 usage / unusable input
    def exit_code_of(argv):
        sink = io.StringIO()
        try:
            with contextlib.redirect_stderr(sink), contextlib.redirect_stdout(sink):
                return main(argv)
        except SystemExit as exc:
            return exc.code
    check("unreadable file -> exit 2", exit_code_of(["describe", "--file", "/dev/null/nonexistent.json"]), 2)
    check("--adjust without --reason -> exit 2", exit_code_of(["uplift", "--demo", "--adjust", "0.9"]), 2)
    check("--inside must be > 0 -> exit 2", exit_code_of(["position", "--demo", "--inside", "0"]), 2)
    # parse helpers
    rows = parse_outcomes([{"Name": "P1", "Value": "1.5", "Source": "log"}, 2.0])
    check("parse_outcomes: dict + number rows", [(r[0], r[1]) for r in rows], [("P1", 1.5), ("case 2", 2.0)])
    # demo reproduces the SKILL.md worked example
    dv = [v for _, v, _ in parse_outcomes(DEMO["outcomes"])]
    check("demo class == class A", sorted(dv), a)
    du = uplift(dv, DEMO_ARGS["inside"], DEMO_ARGS["target"], DEMO_ARGS["base"], DEMO_ARGS["adjust"])
    check("demo: P80 forecast 18.72 months", du["forecast_target"], 18.72)
    check("demo: adjusted forecast 16.848 months", du["final"], 16.848)
    check("demo: verdict OK", du["verdict_ok"], True)

    print(f"ALL {len(checks)} CHECKS PASSED")
    print("selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
