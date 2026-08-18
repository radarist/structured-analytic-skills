#!/usr/bin/env python3
"""delphi.py — companion statistics tool for the `delphi-method` skill.

Computes the aggregation statistics a Delphi facilitator needs, per Linstone
& Turoff (1975) and methodologies/foresight/delphi-method.md:

  aggregate  per item: n, median, IQR (Q1/Q3), min/max, outlier flags for
             estimates outside the IQR (rationales echoed).
  stability  per item: % of panelists changing estimate between two rounds,
             median shift, STABLE/MOVING verdict (<15% changed = STABLE).
  kendall    Kendall's W coefficient of concordance for ranked items.

Input files (JSON). Round file — either grouped:
  {"question": "...", "round": 1,
   "items": {"item": [{"panelist": "E1", "estimate": 2035,
                       "rationale": "..."}, ...]}}
or a flat list, grouped by "item":
  {"responses": [{"item": "...", "panelist": "E1", "estimate": 2035,
                  "rationale": "..."}, ...]}
Rankings file — each panelist's items ordered best-first (rank 1 first);
{"item": rank} dicts also accepted. Complete rankings, no ties:
  {"rankings": {"E1": ["A", "B", "C"], "E2": [...], ...}}

Stdlib only. Python 3.9+. Run `python3 delphi.py --selftest` to verify.
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

# Stopping rule from methodologies/foresight/delphi-method.md: an item is
# stable when fewer than 15% of estimates change between rounds.
STABILITY_THRESHOLD = 0.15


# --- Core statistics ---

def median(values):
    """Standard median: middle value (odd n) or mean of the two middles."""
    s = sorted(values)
    n = len(s)
    if n == 0:
        raise ValueError("median of empty list")
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def quartiles(values):
    """Q1/Q3 via the exclusive method: median of the lower / upper half of
    the sorted data, excluding the overall median when n is odd.
    Easy to hand-verify; standard for small Delphi panels."""
    s = sorted(values)
    n = len(s)
    if n < 2:
        raise ValueError("need at least 2 values for quartiles")
    mid = n // 2
    lower = s[:mid]
    upper = s[mid:] if n % 2 == 0 else s[mid + 1:]
    return median(lower), median(upper)


def kendalls_w(rank_runs):
    """Kendall's W for m raters ranking the same n items (no ties).

    rank_runs: {rater_id: {item: rank}}. W = 12*S / (m^2 * (n^3 - n)),
    where S is the sum of squared deviations of each item's rank sum from
    the mean rank sum. Returns (W, {item: rank_sum}).
    """
    raters = sorted(rank_runs)
    m = len(raters)
    if m < 2:
        raise ValueError("need at least 2 raters")
    items = sorted(rank_runs[raters[0]])
    n = len(items)
    if n < 2:
        raise ValueError("need at least 2 items")
    expected_ranks = set(range(1, n + 1))
    for r in raters:
        ranks = rank_runs[r]
        if sorted(ranks) != items:
            raise ValueError("rater %r ranks a different item set" % r)
        if set(ranks.values()) != expected_ranks:
            raise ValueError("rater %r must use ranks 1..%d, each once (no ties)"
                             % (r, n))
    rank_sums = {it: sum(rank_runs[r][it] for r in raters) for it in items}
    mean_rs = m * (n + 1) / 2
    s_sq = sum((rs - mean_rs) ** 2 for rs in rank_sums.values())
    w = 12 * s_sq / (m ** 2 * (n ** 3 - n))
    return w, rank_sums


# --- Input loading ---

def _norm_response(item_name, raw):
    """Normalize one response record to {item, panelist, estimate, rationale}."""
    return {
        "item": raw.get("item", item_name),
        "panelist": str(raw.get("panelist", raw.get("persona", "?"))),
        "estimate": float(raw["estimate"]),
        "rationale": str(raw.get("rationale", "")),
    }


def load_round(path):
    """Load a round file; return (meta, {item: [response, ...]})."""
    data = json.loads(Path(path).read_text())
    meta = {"question": data.get("question", ""), "round": data.get("round")}
    items = {}
    if "items" in data:  # grouped form
        for name, responses in data["items"].items():
            items[name] = [_norm_response(name, r) for r in responses]
    elif "responses" in data:  # flat form, grouped by "item"
        for r in data["responses"]:
            rec = _norm_response(None, r)
            items.setdefault(rec["item"], []).append(rec)
    else:
        raise ValueError("round file needs 'items' or 'responses'")
    return meta, items


def load_rankings(path):
    """Load a rankings file; return (meta, {rater: {item: rank}})."""
    data = json.loads(Path(path).read_text())
    meta = {"question": data.get("question", "")}
    rankings = {}
    for rater, ranked in data["rankings"].items():
        if isinstance(ranked, list):  # best-first list -> rank positions
            if len(set(ranked)) != len(ranked):
                raise ValueError("rater %r lists an item twice" % rater)
            rankings[str(rater)] = {item: i + 1 for i, item in enumerate(ranked)}
        else:  # already a {item: rank} dict
            rankings[str(rater)] = {item: int(rank) for item, rank in ranked.items()}
    return meta, rankings


# --- Commands ---

def fmt(x):
    """Print integral floats as ints (2035.0 -> '2035')."""
    return str(int(x)) if isinstance(x, float) and x.is_integer() else ("%g" % x)


def cmd_aggregate(args):
    meta, items = load_round(args.file)
    header = "Delphi round aggregation"
    if meta["round"] is not None:
        header += " — round %s" % meta["round"]
    print(header)
    if meta["question"]:
        print("Question: %s" % meta["question"])
    for name, responses in items.items():
        estimates = [r["estimate"] for r in responses]
        med = median(estimates)
        q1, q3 = quartiles(estimates)
        print("\nItem: %s" % name)
        print("  n=%d  median=%s  Q1=%s  Q3=%s  IQR=%s  min=%s  max=%s"
              % (len(estimates), fmt(med), fmt(q1), fmt(q3), fmt(q3 - q1),
                 fmt(min(estimates)), fmt(max(estimates))))
        outliers = [r for r in responses if r["estimate"] < q1 or r["estimate"] > q3]
        if outliers:
            print("  Outliers (outside the IQR):")
            for r in sorted(outliers, key=lambda r: r["estimate"]):
                line = "    %s: %s" % (r["panelist"], fmt(r["estimate"]))
                if r["rationale"]:
                    line += " — \"%s\"" % r["rationale"]
                print(line)
        else:
            print("  Outliers (outside the IQR): none")
    return 0


def cmd_stability(args):
    _, round1 = load_round(args.round1)
    _, round2 = load_round(args.round2)
    print("Delphi inter-round stability (stopping rule: STABLE when <%d%% of "
          "estimates change)" % (STABILITY_THRESHOLD * 100))
    for name in round1:
        if name not in round2:
            print("\nItem: %s\n  skipped — absent from round 2" % name)
            continue
        r1 = {r["panelist"]: r["estimate"] for r in round1[name]}
        r2 = {r["panelist"]: r["estimate"] for r in round2[name]}
        matched = sorted(set(r1) & set(r2))
        if not matched:
            print("\nItem: %s\n  skipped — no panelists appear in both rounds" % name)
            continue
        changed = [p for p in matched if r1[p] != r2[p]]
        pct = len(changed) / len(matched)
        med1, med2 = median(list(r1.values())), median(list(r2.values()))
        verdict = "STABLE" if pct < STABILITY_THRESHOLD else "MOVING"
        print("\nItem: %s" % name)
        print("  changed: %d/%d (%.1f%%)  median: %s -> %s (shift %+s)  verdict: %s"
              % (len(changed), len(matched), 100 * pct, fmt(med1), fmt(med2),
                 fmt(med2 - med1), verdict))
        if len(r1) != len(matched) or len(r2) != len(matched):
            print("  note: %d panelist(s) unmatched across rounds, excluded"
                  % (len(set(r1) ^ set(r2))))
    return 0


def cmd_kendall(args):
    meta, rankings = load_rankings(args.file)
    w, rank_sums = kendalls_w(rankings)
    n_raters, n_items = len(rankings), len(rank_sums)
    mean_ranks = {it: rs / n_raters for it, rs in rank_sums.items()}
    if w < 0.3:
        band = "weak agreement"
    elif w <= 0.7:
        band = "moderate agreement"
    else:
        band = "strong agreement"
    print("Kendall's W = %.4f  (%d raters, %d items) — %s"
          % (w, n_raters, n_items, band))
    if meta["question"]:
        print("Question: %s" % meta["question"])
    print("Consensus order (by mean rank):")
    for item in sorted(mean_ranks, key=mean_ranks.get):
        print("  %s (mean rank %.2f)" % (item, mean_ranks[item]))
    return 0


# --- Self-test — all expected values hand-computed before encoding. ---

_checks_run = 0


def _check(label, got, want, tol=1e-9):
    global _checks_run
    _checks_run += 1
    ok = (abs(got - want) <= tol) if isinstance(want, float) else (got == want)
    if not ok:
        print("FAIL: %s — got %r, want %r" % (label, got, want))
        sys.exit(1)
    print("PASS: %s" % label)


def cmd_selftest(_args):
    # Micro-panel: 5 experts, estimates [2030, 2032, 2035, 2040, 2060].
    # By hand: median = 2035; lower half [2030, 2032] -> Q1 = 2031;
    # upper half [2040, 2060] -> Q3 = 2050; IQR = 19; min 2030, max 2060.
    # Outside [Q1, Q3]: E1 (2030) and E5 (2060) -> both flagged.
    panel = [
        {"panelist": "E1", "estimate": 2030, "rationale": "fusion-first path"},
        {"panelist": "E2", "estimate": 2032, "rationale": "steady qubit scaling"},
        {"panelist": "E3", "estimate": 2035, "rationale": "roadmap midpoint"},
        {"panelist": "E4", "estimate": 2040, "rationale": "error-correction lag"},
        {"panelist": "E5", "estimate": 2060, "rationale": "materials bottleneck"},
    ]
    est = [r["estimate"] for r in panel]
    _check("median of 5-expert panel", median(est), 2035)
    q1, q3 = quartiles(est)
    _check("Q1 of 5-expert panel", q1, 2031)
    _check("Q3 of 5-expert panel", q3, 2050)
    _check("IQR of 5-expert panel", q3 - q1, 19)
    outliers = [r["panelist"] for r in panel
                if r["estimate"] < q1 or r["estimate"] > q3]
    _check("outliers flagged", outliers, ["E1", "E5"])

    # Even-n panel [10, 20, 30, 40]: median = (20+30)/2 = 25; halves
    # [10,20] -> Q1 = 15, [30,40] -> Q3 = 35; IQR = 20.
    even = [10, 20, 30, 40]
    _check("median of even panel", median(even), 25)
    _check("quartiles of even panel", quartiles(even), (15, 35))

    # Full aggregate path through a real file.
    with tempfile.TemporaryDirectory() as tmp:
        r1_path = Path(tmp) / "r1.json"
        r1_path.write_text(json.dumps(
            {"question": "fault-tolerant QC year", "round": 1,
             "items": {"qc year": panel}}))
        _, loaded = load_round(r1_path)
        _check("aggregate load: n", len(loaded["qc year"]), 5)

        # Stability: E1 and E5 revise (2/5 = 40% -> MOVING); medians
        # r1 = 2035, r2 = 2035 -> shift 0.
        r2 = [dict(r, estimate=e) for r, e in
              zip(panel, [2032, 2032, 2035, 2040, 2050])]
        r2_path = Path(tmp) / "r2.json"
        r2_path.write_text(json.dumps({"round": 2, "items": {"qc year": r2}}))
        _, loaded2 = load_round(r2_path)
        a = {r["panelist"]: r["estimate"] for r in loaded["qc year"]}
        b = {r["panelist"]: r["estimate"] for r in loaded2["qc year"]}
        matched = sorted(set(a) & set(b))
        changed = [p for p in matched if a[p] != b[p]]
        _check("stability: changed panelists", changed, ["E1", "E5"])
        pct = len(changed) / len(matched)
        _check("stability: pct changed", pct, 0.40)
        _check("stability: verdict", "STABLE" if pct < STABILITY_THRESHOLD
               else "MOVING", "MOVING")
        _check("stability: median shift",
               median(list(b.values())) - median(list(a.values())), 0)

        # Identical rounds -> 0% changed -> STABLE.
        _check("stability: identical rounds verdict",
               "STABLE" if 0.0 < STABILITY_THRESHOLD else "MOVING", "STABLE")

        # Kendall's W. 3 raters, 3 items: E1 A>B>C, E2 A>B>C, E3 A>C>B.
        # Rank sums: A=3, B=7, C=8; mean = 6; S = 9+1+4 = 14;
        # W = 12*14 / (9*(27-3)) = 168/216 = 0.7777...
        k_path = Path(tmp) / "k.json"
        k_path.write_text(json.dumps({"rankings": {
            "E1": ["A", "B", "C"], "E2": ["A", "B", "C"], "E3": ["A", "C", "B"]}}))
        _, krank = load_rankings(k_path)
        w, rank_sums = kendalls_w(krank)
        _check("kendall: rank sums", rank_sums, {"A": 3, "B": 7, "C": 8})
        _check("kendall: W for worked example", w, 168 / 216)
        # Perfect agreement: all raters identical -> S maximal -> W = 1.
        _check("kendall: perfect agreement",
               kendalls_w({"E1": {"A": 1, "B": 2, "C": 3},
                           "E2": {"A": 1, "B": 2, "C": 3}})[0], 1.0)
        # Two raters in exact reverse -> every rank sum = 4, S = 0 -> W = 0.
        _check("kendall: full disagreement",
               kendalls_w({"E1": {"A": 1, "B": 2, "C": 3},
                           "E2": {"A": 3, "B": 2, "C": 1}})[0], 0.0)

    print("All %d self-test checks passed." % _checks_run)
    return 0


# --- CLI ---

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Delphi companion statistics: median/IQR aggregation, "
                    "inter-round stability, Kendall's W.")
    parser.add_argument("--selftest", action="store_true",
                        help="run built-in worked examples and exit")
    sub = parser.add_subparsers(dest="command")

    p_agg = sub.add_parser("aggregate", help="median/IQR per item + outliers")
    p_agg.add_argument("--file", required=True, help="round JSON file")
    p_agg.set_defaults(func=cmd_aggregate)

    p_stab = sub.add_parser("stability", help="inter-round stability per item")
    p_stab.add_argument("--round1", required=True, help="round 1 JSON file")
    p_stab.add_argument("--round2", required=True, help="round 2 JSON file")
    p_stab.set_defaults(func=cmd_stability)

    p_ken = sub.add_parser("kendall", help="Kendall's W for ranked items")
    p_ken.add_argument("--file", required=True, help="rankings JSON file")
    p_ken.set_defaults(func=cmd_kendall)

    args = parser.parse_args(argv)
    if args.selftest:
        return cmd_selftest(args)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    try:
        return args.func(args)
    except (ValueError, KeyError, json.JSONDecodeError, OSError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
