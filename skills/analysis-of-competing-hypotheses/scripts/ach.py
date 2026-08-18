#!/usr/bin/env python3
"""ach.py -- score an Analysis of Competing Hypotheses (ACH) matrix.

Implements the scoring half of Richards J. Heuer Jr.'s ACH (Psychology of
Intelligence Analysis, CIA, 1999, ch. 8). Every evidence item carries a
weight (credibility x relevance); every evidence/hypothesis cell carries a
consistency mark: CC/C (consistent), N (neutral), I/II (inconsistent),
NA (not applicable). Hypotheses are ranked by WEIGHTED INCONSISTENCY total
-- fewest wins (counting consistencies would reward confirmation bias; ACH
disconfirms). Evidence diagnosticity = spread of its marks across
hypotheses; a row with the same mark everywhere cannot discriminate
(Heuer step 4). Stdlib only, Python 3.9+.

Usage:
    python3 ach.py score --file case.json
    python3 ach.py diagnosticity --file case.json
    python3 ach.py --selftest

Case file: {"question": str (optional),
  "hypotheses": ["H1: label", ...],
  "evidence": [{"id": "E1", "description": "...", "weight": 0.9,
                "credibility": 0.9, "relevance": 1.0,
                "marks": {"H1": "C", "H2": "I", ...}}]}
Effective evidence weight = weight x credibility x relevance (all optional,
default 1.0); id/description are optional; every hypothesis needs a mark.
"""

import argparse
import json
import sys

# Numeric value of each mark on the consistency scale, used for the
# diagnosticity spread. NA has no value: the cell does not bear on the
# hypothesis and is excluded from both scoring and spread.
MARK_VALUE = {"CC": -2, "C": -1, "N": 0, "I": 1, "II": 2}
VALID_MARKS = frozenset(MARK_VALUE) | {"NA"}

# Heuer: prefer the hypothesis with the FEWEST inconsistencies.
# II ("strongly inconsistent") penalises double.
INCONSISTENCY_PENALTY = {"I": 1.0, "II": 2.0}

EPS = 1e-9  # float tolerance for totals and tie detection


class CaseError(ValueError):
    """Raised when the input case file is malformed."""


def _factor(ev, key, index):
    """Read an optional non-negative numeric multiplier from an evidence item."""
    value = ev.get(key, 1.0)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise CaseError(f"evidence #{index}: {key!r} must be a non-negative number")
    return float(value)


def parse_case(data):
    """Validate the JSON case description and normalise it.

    Returns (question, hypotheses, evidence): hypotheses is a list of
    (hid, label) tuples; evidence is a list of dicts with keys
    id, description, weight (effective), marks ({hid: mark}).
    """
    if not isinstance(data, dict):
        raise CaseError("top level must be a JSON object")
    raw_hyps = data.get("hypotheses")
    if not isinstance(raw_hyps, list) or len(raw_hyps) < 2:
        raise CaseError("'hypotheses' must be a list of at least 2 entries")

    hypotheses = []
    seen = set()
    for i, entry in enumerate(raw_hyps, 1):
        if not isinstance(entry, str):
            raise CaseError(f"hypothesis #{i} must be a string")
        hid, _, label = entry.partition(":")
        hid, label = hid.strip(), label.strip()
        if not hid:
            hid = f"H{i}"
        if hid in seen:
            raise CaseError(f"duplicate hypothesis id {hid!r}")
        seen.add(hid)
        hypotheses.append((hid, label or hid))

    raw_ev = data.get("evidence")
    if not isinstance(raw_ev, list) or not raw_ev:
        raise CaseError("'evidence' must be a non-empty list")
    hyp_ids = [hid for hid, _ in hypotheses]
    evidence = []
    for i, ev in enumerate(raw_ev, 1):
        if not isinstance(ev, dict):
            raise CaseError(f"evidence #{i} must be an object")
        marks = ev.get("marks")
        if not isinstance(marks, dict):
            raise CaseError(f"evidence #{i}: 'marks' must be an object")
        unknown = sorted(set(marks) - set(hyp_ids))
        if unknown:
            raise CaseError(f"evidence #{i}: marks for unknown hypotheses {unknown}")
        missing = [hid for hid in hyp_ids if hid not in marks]
        if missing:
            raise CaseError(f"evidence #{i}: missing marks for {missing}")
        norm = {}
        for hid, mark in marks.items():
            mark = str(mark).strip().upper()
            if mark not in VALID_MARKS:
                raise CaseError(
                    f"evidence #{i}: bad mark {mark!r} for {hid}; use CC/C/N/I/II/NA")
            norm[hid] = mark
        weight = (_factor(ev, "weight", i)
                  * _factor(ev, "credibility", i)
                  * _factor(ev, "relevance", i))
        evidence.append({
            "id": str(ev.get("id", f"E{i}")),
            "description": str(ev.get("description", "")).strip(),
            "weight": weight,
            "marks": norm,
        })
    return str(data.get("question", "")).strip(), hypotheses, evidence


def load_case(path):
    """Read and validate a JSON case file; exit with a message on failure."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as exc:
        raise SystemExit(f"error: cannot read {path}: {exc}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON: {exc}")
    try:
        return parse_case(data)
    except CaseError as exc:
        raise SystemExit(f"error: {path}: {exc}")


def inconsistency_totals(hypotheses, evidence):
    """Per hypothesis: (weighted inconsistency total, raw I-count).

    Weighted total = sum over evidence of weight x penalty(mark);
    raw count treats I as 1 and II as 2, ignoring weights.
    """
    totals = {}
    for hid, _ in hypotheses:
        weighted, raw = 0.0, 0
        for ev in evidence:
            penalty = INCONSISTENCY_PENALTY.get(ev["marks"][hid], 0.0)
            weighted += ev["weight"] * penalty
            raw += int(penalty)
        totals[hid] = (weighted, raw)
    return totals


def rank_hypotheses(hypotheses, totals):
    """Fewest weighted inconsistencies first (Heuer); ties broken by raw
    I-count, then by id for determinism."""
    return sorted(hypotheses,
                  key=lambda hl: (totals[hl[0]][0], totals[hl[0]][1], hl[0]))


def mark_spread(ev, hyp_ids):
    """Diagnosticity of one evidence row: spread = max - min of mark values
    across hypotheses, NA cells excluded. Spread 0 (or a single applicable
    cell) means the evidence cannot discriminate between hypotheses."""
    values = [MARK_VALUE[ev["marks"][hid]]
              for hid in hyp_ids if ev["marks"][hid] != "NA"]
    if not values:
        return 0
    return max(values) - min(values)


def diagnosticity_flag(ev, hyp_ids):
    """Heuer step-4 verdict for one evidence row, or None if it discriminates."""
    applicable = [ev["marks"][hid] for hid in hyp_ids if ev["marks"][hid] != "NA"]
    if not applicable:
        return "bears on no hypothesis (all NA) -- drop"
    if len(set(applicable)) == 1:
        mark = applicable[0]
        if mark in ("C", "CC"):
            return "consistent with every hypothesis -- no diagnostic value, consider dropping"
        if mark == "N":
            return "neutral for every hypothesis -- no diagnostic value, drop"
        return ("inconsistent with every hypothesis -- challenge the evidence "
                "or add a missing hypothesis")
    return None


def most_diagnostic(evidence, hyp_ids):
    """Ids of the discriminating evidence rows with the largest spread."""
    best, best_spread = [], -1
    for ev in evidence:
        if diagnosticity_flag(ev, hyp_ids) is not None:
            continue
        spread = mark_spread(ev, hyp_ids)
        if spread > best_spread:
            best, best_spread = [ev["id"]], spread
        elif spread == best_spread:
            best.append(ev["id"])
    return best, best_spread


def print_matrix(hypotheses, evidence, totals):
    """Print the full ACH matrix as a fixed-width text table."""
    hyp_ids = [hid for hid, _ in hypotheses]

    def label(ev):
        return f"{ev['id']} {ev['description']}".strip()

    ev_w = min(max([len(label(ev)) for ev in evidence] + [7]), 46)
    col_w = [max(len(hid), 4) + 1 for hid in hyp_ids]

    def row(cells):
        parts = [cells[0].ljust(ev_w), cells[1].rjust(5)]
        parts += [c.rjust(w) for c, w in zip(cells[2:-1], col_w)]
        parts.append(cells[-1].rjust(4))
        print("  ".join(parts))

    row(["Evidence", "W"] + hyp_ids + ["Diag"])
    rule = ["-" * ev_w, "-" * 5] + ["-" * w for w in col_w] + ["-" * 4]
    print("  ".join(rule))
    for ev in evidence:
        text = label(ev)
        if len(text) > ev_w:
            text = text[: ev_w - 3] + "..."
        row([text, f"{ev['weight']:.2f}"]
            + [ev["marks"][hid] for hid in hyp_ids]
            + [str(mark_spread(ev, hyp_ids))])
    print("  ".join(rule))
    row(["Weighted inconsistency", ""] + [f"{totals[h][0]:.2f}" for h in hyp_ids] + [""])
    row(["Raw I count (I=1, II=2)", ""] + [str(totals[h][1]) for h in hyp_ids] + [""])
    print("\nHypotheses:")
    for hid, text in hypotheses:
        print(f"  {hid}  {text}")


def print_ranking(hypotheses, totals):
    """Print hypotheses ranked by weighted inconsistency; flag exact ties."""
    order = rank_hypotheses(hypotheses, totals)
    counts = {}
    for hid, _ in hypotheses:
        key = round(totals[hid][0], 9)
        counts[key] = counts.get(key, 0) + 1
    print("\nRanking (fewest weighted inconsistencies = leading hypothesis, per Heuer):")
    for n, (hid, text) in enumerate(order, 1):
        weighted, raw = totals[hid]
        tie = ("   [tie: weigh which inconsistencies are most damaging]"
               if counts[round(weighted, 9)] > 1 else "")
        print(f"  {n}. {hid}  {text:<42.42}  weighted-I {weighted:5.2f}   raw-I {raw}{tie}")
    return order


def cmd_score(args):
    question, hypotheses, evidence = load_case(args.file)
    hyp_ids = [hid for hid, _ in hypotheses]
    totals = inconsistency_totals(hypotheses, evidence)
    if question:
        print(f"Question: {question}\n")
    print_matrix(hypotheses, evidence, totals)
    print_ranking(hypotheses, totals)
    notes = [(ev["id"], diagnosticity_flag(ev, hyp_ids)) for ev in evidence]
    notes = [(eid, flag) for eid, flag in notes if flag]
    if notes:
        print("\nNon-diagnostic evidence (Heuer step 4 -- consider dropping or re-sourcing):")
        for eid, flag in notes:
            print(f"  {eid}: {flag}")
    return 0


def cmd_diagnosticity(args):
    question, hypotheses, evidence = load_case(args.file)
    hyp_ids = [hid for hid, _ in hypotheses]
    if question:
        print(f"Question: {question}\n")
    print("Evidence diagnosticity (spread of marks across hypotheses; 0 = cannot discriminate):\n")
    for ev in evidence:
        marks = "  ".join(f"{hid}={ev['marks'][hid]}" for hid in hyp_ids)
        print(f"  {ev['id']:<4} spread {mark_spread(ev, hyp_ids)}   {marks}")
        flag = diagnosticity_flag(ev, hyp_ids)
        if flag:
            print(f"       ^ NON-DIAGNOSTIC: {flag}")
    best, spread = most_diagnostic(evidence, hyp_ids)
    print(f"\nMost diagnostic evidence: {', '.join(best)} (spread {spread})")
    return 0


# --------------------------------------------------------------------------
# Selftest: 3 hypotheses x 5 evidence, all expected values hand-verified.
#
# Effective weights: E1=0.9, E2=0.8, E3=0.75x0.8=0.6, E4=0.5, E5=0.4.
# Weighted inconsistency (penalty I=1, II=2):
#   H1 = 0.6 (E3)                 = 0.6
#   H2 = 0.5 (E4)                 = 0.5
#   H3 = 0.9x2 (E1) + 0.8 (E2)    = 2.6
# Raw I-counts: H1=1, H2=1, H3=3 -> ranking H2, H1, H3 (weights break the
# raw-count tie between H1 and H2).
# Spreads (CC=-2..II=+2): E1: -1,-1,+2 -> 3; E2: -1,0,+1 -> 2;
#   E3: +1,-1,0 -> 2; E4: -1,+1,-2 -> 3; E5: 0,NA,0 -> 0 (NA excluded,
#   uniform N -> flagged non-diagnostic). Most diagnostic: E1 and E4.
# --------------------------------------------------------------------------
SELFTEST_CASE = {
    "question": "Why did enterprise adoption of the platform stall in Q4?",
    "hypotheses": [
        "H1: Adoption is genuinely slow",
        "H2: Pivot to a different segment",
        "H3: Null -- market noise",
    ],
    "evidence": [
        {"id": "E1", "description": "Q4 revenue -8% YoY", "weight": 0.9,
         "marks": {"H1": "C", "H2": "C", "H3": "II"}},
        {"id": "E2", "description": "No new customers in roadmap-aligned ICP",
         "weight": 0.8,
         "marks": {"H1": "C", "H2": "N", "H3": "I"}},
        {"id": "E3", "description": "CEO 're-evaluating market fit' quote on earnings call",
         "credibility": 0.75, "relevance": 0.8,
         "marks": {"H1": "I", "H2": "C", "H3": "N"}},
        {"id": "E4", "description": "Headcount flat for three quarters", "weight": 0.5,
         "marks": {"H1": "C", "H2": "I", "H3": "CC"}},
        {"id": "E5", "description": "Support ticket volume steady", "weight": 0.4,
         "marks": {"H1": "N", "H2": "NA", "H3": "N"}},
    ],
}


def selftest():
    checks = []

    def check(name, ok):
        checks.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} -- {name}")

    question, hypotheses, evidence = parse_case(SELFTEST_CASE)
    hyp_ids = [hid for hid, _ in hypotheses]
    totals = inconsistency_totals(hypotheses, evidence)

    check("E3 effective weight = credibility x relevance = 0.6",
          abs(evidence[2]["weight"] - 0.6) < EPS)
    check("weighted inconsistency H1=0.6, H2=0.5, H3=2.6",
          abs(totals["H1"][0] - 0.6) < EPS
          and abs(totals["H2"][0] - 0.5) < EPS
          and abs(totals["H3"][0] - 2.6) < EPS)
    check("raw I-counts H1=1, H2=1, H3=3",
          totals["H1"][1] == 1 and totals["H2"][1] == 1 and totals["H3"][1] == 3)
    check("ranking is H2 (leading), H1, H3",
          [hid for hid, _ in rank_hypotheses(hypotheses, totals)] == ["H2", "H1", "H3"])
    check("spreads E1=3, E2=2, E3=2, E4=3, E5=0",
          [mark_spread(ev, hyp_ids) for ev in evidence] == [3, 2, 2, 3, 0])
    check("E5 flagged non-diagnostic (uniform N over applicable cells)",
          diagnosticity_flag(evidence[4], hyp_ids) is not None
          and "neutral" in diagnosticity_flag(evidence[4], hyp_ids))
    check("most diagnostic evidence = E1 and E4 (spread 3)",
          most_diagnostic(evidence, hyp_ids) == (["E1", "E4"], 3))
    check("NA excluded from spread: {I, NA, II} -> spread 1, not 2",
          mark_spread({"marks": {"H1": "I", "H2": "NA", "H3": "II"}}, hyp_ids) == 1)
    try:
        parse_case({"hypotheses": ["H1: a", "H2: b"],
                    "evidence": [{"marks": {"H1": "X", "H2": "C"}}]})
        check("invalid mark rejected by validation", False)
    except CaseError:
        check("invalid mark rejected by validation", True)

    passed = sum(checks)
    print(f"\nSELFTEST {'PASSED' if passed == len(checks) else 'FAILED'} "
          f"({passed}/{len(checks)} checks)")
    return 0 if passed == len(checks) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Score a Heuer ACH matrix: weighted inconsistencies, "
                    "hypothesis ranking, evidence diagnosticity.")
    parser.add_argument("--selftest", action="store_true",
                        help="run the built-in worked example and verify expected outputs")
    sub = parser.add_subparsers(dest="command")
    for name, helptext in (
            ("score", "print the matrix and rank hypotheses by weighted inconsistency"),
            ("diagnosticity", "report per-evidence diagnosticity and flag "
                              "non-discriminating rows")):
        subp = sub.add_parser(name, help=helptext)
        subp.add_argument("--file", required=True, help="JSON case file (see module docstring)")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.command == "score":
        return cmd_score(args)
    if args.command == "diagnosticity":
        return cmd_diagnosticity(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
