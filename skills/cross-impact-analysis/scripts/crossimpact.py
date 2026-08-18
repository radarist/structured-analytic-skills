#!/usr/bin/env python3
"""crossimpact.py — cross-impact analysis: MICMAC-style influence/dependence ranking.

Reads a JSON file describing a set of events (or variables) and their pairwise
cross-impact matrix, then computes per-event influence (row totals) and
dependence (column totals) in the MICMAC tradition (Godet), ranks both,
classifies events into the four MICMAC quadrants, and flags asymmetric pairs
whose two directional ratings diverge beyond a threshold.

SCOPE: this is MICMAC's DIRECT stage only. Full MICMAC raises the matrix to
successive powers to capture indirect influence (Godet; Arcade et al. 2009);
that powering is deliberately not implemented, so rankings here reflect
first-order influence and dependence alone.

Input JSON format (--file):

    {
      "title":  "optional title",
      "mode":   "impact" | "probability",        # default "impact"
      "events": ["event 1", "event 2", ...],
      "matrix": [[0, 2, ...], [0, 0, ...], ...]  # N x N, diagonal must be 0
    }

Two matrix modes are supported; "mode" selects one (default "impact"):

  impact       cell (i,j) = direct impact of event i on event j, in -3..+3
               (signed MICMAC-style rating; 0 = none, sign = direction).
               Totals use |value| so opposing impacts do not cancel out.
  probability  cell (i,j) = conditional probability P(j | i), in 0..1
               (Gordon-Helmer cross-impact). Totals are plain sums (values
               are non-negative, so this is the same code path).

Usage:
    python3 crossimpact.py --file matrix.json [--asym 2]
    python3 crossimpact.py --selftest

Stdlib only. Python 3.9+.
"""

import argparse
import json
import sys

# Valid cell range per mode. Out-of-bounds values are rejected at load time.
BOUNDS = {"impact": (-3.0, 3.0), "probability": (0.0, 1.0)}

# Default asymmetry threshold per mode, in matrix units: a pair (i, j) is
# flagged when |m[i][j] - m[j][i]| exceeds it (strong one-way influence with
# no reciprocity deserves an explicit story — or a re-rating).
DEFAULT_ASYM = {"impact": 2.0, "probability": 0.5}

# Methodological guardrail from the literature: matrices grow as N^2 and
# rating quality collapses with fatigue. Warn above this size, don't refuse.
MAX_RECOMMENDED_N = 25

QUADRANTS = (
    (True, False, "determinant (high influence, low dependence - strategic lever)"),
    (True, True, "relay (high influence, high dependence - unstable amplifier)"),
    (False, True, "dependent (low influence, high dependence - indicator)"),
    (False, False, "excluded (low influence, low dependence - autonomous)"),
)


def validate(payload):
    """Return a list of structural/bounds errors in the input payload (empty = OK)."""
    errors = []
    events = payload.get("events")
    matrix = payload.get("matrix")
    mode = payload.get("mode", "impact")

    if mode not in BOUNDS:
        errors.append('unknown mode %r (expected "impact" or "probability")' % mode)
        return errors  # cannot bounds-check without a valid mode
    if not isinstance(events, list) or len(events) < 2:
        errors.append('"events" must be a list of at least 2 names')
        return errors
    if not all(isinstance(e, str) and e.strip() for e in events):
        errors.append("every event name must be a non-empty string")
    if len(set(events)) != len(events):
        errors.append("event names must be unique")
    if not isinstance(matrix, list) or len(matrix) != len(events):
        errors.append('"matrix" must have exactly one row per event')
        return errors

    lo, hi = BOUNDS[mode]
    for i, row in enumerate(matrix):
        if not isinstance(row, list) or len(row) != len(events):
            errors.append("matrix row %d must have exactly %d cells" % (i, len(events)))
            continue
        for j, cell in enumerate(row):
            if isinstance(cell, bool) or not isinstance(cell, (int, float)):
                errors.append("cell (%d,%d) is not a number: %r" % (i, j, cell))
            elif i == j and cell != 0:
                errors.append("diagonal cell (%d,%d) must be 0, got %g" % (i, j, cell))
            elif i != j and not (lo <= cell <= hi):
                errors.append(
                    "cell (%d,%d) = %g is out of bounds for %s mode [%g, %g]"
                    % (i, j, cell, mode, lo, hi)
                )
    return errors


def analyze(events, matrix, asym_threshold):
    """Compute MICMAC-style scores, rankings, classification, asymmetric pairs.

    influence[i]  = sum_j |m[i][j]|  (total impact event i exerts on others)
    dependence[j] = sum_i |m[i][j]|  (total impact event j absorbs)
    net[i]        = sum_j  m[i][j]   (signed; positive = net promoter)
    """
    n = len(events)
    influence = [sum(abs(matrix[i][j]) for j in range(n) if j != i) for i in range(n)]
    dependence = [sum(abs(matrix[i][j]) for i in range(n) if i != j) for j in range(n)]
    net = [sum(matrix[i][j] for j in range(n) if j != i) for i in range(n)]

    # Rankings: highest score first; ties broken alphabetically for determinism.
    influence_rank = sorted(range(n), key=lambda i: (-influence[i], events[i]))
    dependence_rank = sorted(range(n), key=lambda i: (-dependence[i], events[i]))

    # MICMAC quadrant classification, split at the mean of each axis.
    mean_infl = sum(influence) / n
    mean_dep = sum(dependence) / n
    classification = {}
    for i in range(n):
        high_infl = influence[i] > mean_infl
        high_dep = dependence[i] > mean_dep
        for hi_flag, dep_flag, label in QUADRANTS:
            if high_infl == hi_flag and high_dep == dep_flag:
                classification[events[i]] = label
                break

    # Asymmetric pairs: unordered pairs whose two directions diverge.
    asymmetric = []
    for i in range(n):
        for j in range(i + 1, n):
            if abs(matrix[i][j] - matrix[j][i]) >= asym_threshold:
                asymmetric.append((events[i], events[j], matrix[i][j], matrix[j][i]))

    return {
        "influence": influence,
        "dependence": dependence,
        "net": net,
        "influence_rank": influence_rank,
        "dependence_rank": dependence_rank,
        "mean_infl": mean_infl,
        "mean_dep": mean_dep,
        "classification": classification,
        "asymmetric": asymmetric,
    }


def fmt(x):
    """Compact number formatting: 5 not 5.0; 0.77 for messy floats."""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return "%.2f" % x


def signed(x):
    return ("+" if x > 0 else "") + fmt(x)


def render(title, mode, events, matrix, result, asym_threshold):
    """Format the full report as plain text."""
    n = len(events)
    width = max(len(e) for e in events)
    lines = []
    header = "Cross-impact analysis - %s" % title if title else "Cross-impact analysis"
    lines.append("%s (mode: %s, %d events)" % (header, mode, n))
    if n > MAX_RECOMMENDED_N:
        lines.append(
            "WARNING: N=%d exceeds the recommended maximum of %d - cluster or merge "
            "events before trusting these ratings." % (n, MAX_RECOMMENDED_N)
        )

    lines.append("")
    lines.append("Influence ranking (total impact exerted, row totals of |rating|):")
    for rank, i in enumerate(result["influence_rank"], 1):
        lines.append(
            "  %d. %-*s  influence %s   net %s"
            % (rank, width, events[i], fmt(result["influence"][i]), signed(result["net"][i]))
        )

    lines.append("")
    lines.append("Dependence ranking (total impact absorbed, column totals):")
    for rank, i in enumerate(result["dependence_rank"], 1):
        lines.append(
            "  %d. %-*s  dependence %s" % (rank, width, events[i], fmt(result["dependence"][i]))
        )

    lines.append("")
    lines.append(
        "Direct-stage MICMAC classification (no indirect powering; mean split: influence %s, dependence %s):"
        % (fmt(result["mean_infl"]), fmt(result["mean_dep"]))
    )
    for _, _, label in QUADRANTS:
        members = [e for e in events if result["classification"][e] == label]
        lines.append("  %s: %s" % (label, "; ".join(members) if members else "-"))

    lines.append("")
    if result["asymmetric"]:
        lines.append(
            "Asymmetric pairs (|i->j - j->i| >= %s) - give each a one-line story or re-rate:"
            % fmt(asym_threshold)
        )
        for ei, ej, vij, vji in result["asymmetric"]:
            lines.append("  %s -> %s: %s vs %s" % (ei, ej, signed(vij), signed(vji)))
    else:
        lines.append("Asymmetric pairs (threshold %s): none." % fmt(asym_threshold))

    lines.append("")
    lines.append(
        "Reminder: ratings are structured judgment, not measurement - report "
        "classifications and ranges, not decimal authority."
    )
    return "\n".join(lines)


def selftest():
    """Run hand-verified checks. Print one PASS line per check; exit non-zero on failure."""
    failures = []

    def check(name, cond):
        if cond:
            print("PASS: %s" % name)
        else:
            print("FAIL: %s" % name)
            failures.append(name)

    # --- Case 1: 4-event impact matrix (energy transition). ---
    # Hand-verified sums:
    #   row|abs totals: E1=5, E2=3, E3=2, E4=6  (net: 5, 3, 0, 6)
    #   col|abs totals: E1=3, E2=4, E3=8, E4=1  (both means = 4.0)
    events = ["E1", "E2", "E3", "E4"]
    matrix = [
        [0, 2, 2, 1],
        [0, 0, 3, 0],
        [-1, 1, 0, 0],
        [2, 1, 3, 0],
    ]
    r = analyze(events, matrix, asym_threshold=2)

    check("impact: influence totals", [r["influence"][i] for i in range(4)] == [5, 3, 2, 6])
    check("impact: dependence totals", [r["dependence"][i] for i in range(4)] == [3, 4, 8, 1])
    check("impact: net signed totals", [r["net"][i] for i in range(4)] == [5, 3, 0, 6])
    check(
        "impact: influence ranking E4>E1>E2>E3",
        [events[i] for i in r["influence_rank"]] == ["E4", "E1", "E2", "E3"],
    )
    check(
        "impact: dependence ranking E3>E2>E1>E4",
        [events[i] for i in r["dependence_rank"]] == ["E3", "E2", "E1", "E4"],
    )
    check(
        "impact: MICMAC classification",
        r["classification"]["E1"].startswith("determinant")
        and r["classification"]["E2"].startswith("excluded")
        and r["classification"]["E3"].startswith("dependent")
        and r["classification"]["E4"].startswith("determinant"),
    )
    check(
        "impact: asymmetric pairs at threshold 2",
        [(a, b) for a, b, _, _ in r["asymmetric"]]
        == [("E1", "E2"), ("E1", "E3"), ("E2", "E3"), ("E3", "E4")],
    )
    check("impact: clean matrix validates", validate({"events": events, "matrix": matrix}) == [])

    # --- Case 2: 3-event conditional-probability matrix. ---
    # Hand-verified sums: rows A=1.1, B=0.7, C=0.5; cols A=0.3, B=1.2, C=0.8.
    pevents = ["A", "B", "C"]
    pmatrix = [
        [0.0, 0.8, 0.3],
        [0.2, 0.0, 0.5],
        [0.1, 0.4, 0.0],
    ]
    pr = analyze(pevents, pmatrix, asym_threshold=0.5)
    close = lambda xs, ys: all(abs(x - y) < 1e-9 for x, y in zip(xs, ys))

    check("probability: influence totals", close(pr["influence"], [1.1, 0.7, 0.5]))
    check("probability: dependence totals", close(pr["dependence"], [0.3, 1.2, 0.8]))
    check(
        "probability: rankings",
        [pevents[i] for i in pr["influence_rank"]] == ["A", "B", "C"]
        and [pevents[i] for i in pr["dependence_rank"]] == ["B", "C", "A"],
    )
    check(
        "probability: asymmetric pair A<->B at threshold 0.5",
        [(a, b) for a, b, _, _ in pr["asymmetric"]] == [("A", "B")],
    )
    check(
        "probability: valid matrix validates",
        validate({"mode": "probability", "events": pevents, "matrix": pmatrix}) == [],
    )

    # --- Case 3: out-of-bounds detection. ---
    bad_prob = {"mode": "probability", "events": pevents,
                "matrix": [[0.0, 1.5, 0.3], [0.2, 0.0, 0.5], [0.1, 0.4, 0.0]]}
    errs = validate(bad_prob)
    check("probability: 1.5 flagged out of bounds", len(errs) == 1 and "out of bounds" in errs[0])

    bad_impact = {"events": events,
                  "matrix": [[0, 4, 2, 1], [0, 0, 3, 0], [-1, 1, 0, 0], [2, 1, 3, 0]]}
    errs = validate(bad_impact)
    check("impact: +4 flagged out of bounds", len(errs) == 1 and "out of bounds" in errs[0])

    bad_diag = {"events": ["X", "Y"], "matrix": [[1, 2], [0, 0]]}
    errs = validate(bad_diag)
    check("non-zero diagonal flagged", len(errs) == 1 and "diagonal" in errs[0])

    if failures:
        print("SELFTEST FAILED: %d check(s) failed." % len(failures))
        sys.exit(1)
    print("SELFTEST OK: all checks passed.")
    sys.exit(0)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Cross-impact analysis: direct-stage MICMAC influence/dependence ranking."
    )
    parser.add_argument("--file", help="JSON input: events + pairwise matrix (see module docstring).")
    parser.add_argument(
        "--asym",
        type=float,
        default=None,
        help="asymmetry flag threshold, in matrix units "
        "(default: 2 for impact mode, 0.5 for probability mode).",
    )
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks.")
    args = parser.parse_args(argv)

    if args.selftest:
        selftest()
    if not args.file:
        parser.error("--file is required (or use --selftest)")

    with open(args.file, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    errors = validate(payload)
    if errors:
        for e in errors:
            print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(2)

    mode = payload.get("mode", "impact")
    threshold = args.asym if args.asym is not None else DEFAULT_ASYM[mode]
    events, matrix = payload["events"], payload["matrix"]
    result = analyze(events, matrix, threshold)
    print(render(payload.get("title", ""), mode, events, matrix, result, threshold))
    return 0


if __name__ == "__main__":
    sys.exit(main())
