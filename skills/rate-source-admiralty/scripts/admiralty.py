#!/usr/bin/env python3
"""admiralty.py — NATO Admiralty (alphanumeric) grades: look-up, 6x6 matrix, aggregation.

Implements the two-axis source/information rating defined in NATO AJP-2.1, *Allied
Joint Doctrine for Intelligence Procedures*, and STANAG 2511, *Intelligence Reports*
(the "Admiralty System" / "NATO System"), reproduced in US Army FM 2-22.3, *Human
Intelligence Collector Operations* (Sept 2006), Appendix B, Tables B-1 and B-2:

  Reliability of the source (letter)
      A Completely reliable | B Usually reliable | C Fairly reliable |
      D Not usually reliable | E Unreliable | F Reliability cannot be judged
  Credibility of the information (digit)
      1 Confirmed by other sources | 2 Probably true | 3 Possibly true |
      4 Doubtful | 5 Improbable | 6 Truth cannot be judged

The explanatory sentences below are the standard's wording as printed in FM 2-22.3
App. B (Tables B-1/B-2); the labels are those of AJP-2.1 / STANAG 2511 (FM 2-22.3
prints A as "Reliable", 4 as "Doubtfully true" and F/6 as "Cannot be judged").

The standard defines two INDEPENDENT ordinal axes and no rule for combining them.
Everything this tool prints beyond the look-up is a documented heuristic:

  * `aggregate` counts grades per axis, reports the best/worst *judgeable* grade
    (neither F nor 6), lists F*/*6 items for a lateral check, and raises a CONFLICT
    flag when a well-graded (A/B, 1/2) source supports the claim while another
    well-graded source contradicts it — a re-grading prompt, not part of the standard.
  * `to-ordinal` returns reliability rank + credibility rank (A=1..E=5, F=6; 1..5, 6=6)
    for sorting only, and refuses to emit a "percentage confidence".

Stdlib only. Python 3.9+. Deterministic (sorted output, no clock, no randomness).

Usage:
    python3 admiralty.py grade B2 [--json]
    python3 admiralty.py matrix [--json]
    python3 admiralty.py aggregate --file sources.json [--json]   # .json | .csv | - (stdin JSON)
    python3 admiralty.py aggregate --demo
    python3 admiralty.py to-ordinal B2 [--json]
    python3 admiralty.py --demo
    python3 admiralty.py --selftest

sources.json: a list (or {"sources": [...]}) of rows about ONE claim:
    {"source": "Wire-service report", "grade": "B2",
     "claim_polarity": "supports" | "contradicts" | "neutral", "note": "free text"}
"""

import argparse
import contextlib
import csv
import io
import json
import re
import sys

CITATION = (
    "NATO AJP-2.1 (Allied Joint Doctrine for Intelligence Procedures) / STANAG 2511 "
    "(Intelligence Reports); reproduced in US Army FM 2-22.3 (2006), Appendix B, "
    "Tables B-1 and B-2"
)
CITATION_SHORT = "NATO AJP-2.1 / STANAG 2511; FM 2-22.3 (2006) App. B, Tables B-1/B-2"

# --- the standard (verbatim wording) -----------------------------------------

# letter: (label, explanation)  — Table B-1 "Evaluation of Source Reliability"
RELIABILITY = {
    "A": ("Completely reliable",
          "No doubt of authenticity, trustworthiness, or competency; "
          "has a history of complete reliability"),
    "B": ("Usually reliable",
          "Minor doubt about authenticity, trustworthiness, or competency; "
          "has a history of valid information most of the time"),
    "C": ("Fairly reliable",
          "Doubt of authenticity, trustworthiness, or competency but has provided "
          "valid information in the past"),
    "D": ("Not usually reliable",
          "Significant doubt about authenticity, trustworthiness, or competency but "
          "has provided valid information in the past"),
    "E": ("Unreliable",
          "Lacking in authenticity, trustworthiness, and competency; "
          "history of invalid information"),
    "F": ("Reliability cannot be judged",
          "No basis exists for evaluating the reliability of the source"),
}

# digit: (label, explanation)  — Table B-2 "Evaluation of Information Content"
CREDIBILITY = {
    1: ("Confirmed by other sources",
        "Confirmed by other independent sources; logical in itself; "
        "consistent with other information on the subject"),
    2: ("Probably true",
        "Not confirmed; logical in itself; consistent with other information on the subject"),
    3: ("Possibly true",
        "Not confirmed; reasonably logical in itself; "
        "agrees with some other information on the subject"),
    4: ("Doubtful",
        "Not confirmed; possible but not logical; no other information on the subject"),
    5: ("Improbable",
        "Not confirmed; not logical in itself; contradicted by other information on the subject"),
    6: ("Truth cannot be judged",
        "No basis exists for evaluating the validity of the information"),
}

LETTERS = "ABCDEF"
DIGITS = (1, 2, 3, 4, 5, 6)
POLARITIES = ("supports", "contradicts", "neutral")

# FM 2-22.3 paragraphs B-1 / B-2 on the two "cannot be judged" codes.
NOTE_F = ('An "F" rating does not necessarily mean that the source cannot be trusted, but '
          "that there is no reporting history and therefore no basis for making a "
          "determination (FM 2-22.3, para B-1).")
NOTE_6 = ('A rating of "6" does not necessarily mean false information, but is generally '
          "used to indicate that no determination can be made since the information is "
          "completely new (FM 2-22.3, para B-2).")

ORDINAL_NOTE = (
    "The ordinal (reliability rank + credibility rank) is NOT part of the NATO standard: "
    "AJP-2.1 / STANAG 2511 / FM 2-22.3 define two independent axes and no combination "
    "rule. Use it for sorting only, never as a score. F and 6 are ranked 6 so unjudged "
    "items sort last; that is a filing rule, not a judgement that they are worst."
)
PERCENT_NOTE = (
    "No percentage confidence is emitted. The standard keeps two axes on purpose: the "
    "letter says how far the source's record can be trusted, the digit how well this "
    "item fits everything else known. One number hides which axis is weak — a B5 "
    "(trusted source, contradicted claim) and an E2 (untrusted source, consistent claim) "
    "call for different follow-up — and F/6 mean 'no basis to judge', not 'low'."
)
CONFLICT_NOTE = (
    "Conflict flag = at least one well-graded (A or B, 1 or 2) source supports the claim "
    "AND at least one well-graded source contradicts it. Heuristic, not part of the "
    "standard: re-examine the credibility digits (1-2 mean 'consistent with other "
    "information on the subject') or record the claim as contested."
)

# Built-in example set for --demo (one claim: "AcmeCorp closed a $40M Series B").
DEMO = [
    {"source": "Form D filing (regulator database)", "grade": "A1", "claim_polarity": "supports",
     "note": "primary filing; amount matches the wire report"},
    {"source": "Wire-service report", "grade": "B2", "claim_polarity": "supports",
     "note": "editorial standards; not independently confirmed when graded"},
    {"source": "Trade-press article", "grade": "B2", "claim_polarity": "contradicts",
     "note": "reports $35M citing 'people familiar'"},
    {"source": "Founder's personal blog", "grade": "D3", "claim_polarity": "supports",
     "note": "interested party; agrees with the wire report"},
    {"source": "Vendor marketing page", "grade": "C6", "claim_polarity": "neutral",
     "note": "mentions the company, silent on the round"},
    {"source": "Anonymous forum post", "grade": "F6", "claim_polarity": "contradicts",
     "note": "no posting history; claims the round fell through"},
]

# --- grades ------------------------------------------------------------------

GRADE_RE = re.compile(r"^\s*([A-Fa-f])\s*[-/]?\s*([1-6])\s*$")


def parse_grade(text):
    """'B2' / 'b2' / 'B-2' -> ('B', 2). ValueError for anything outside A-F x 1-6."""
    m = GRADE_RE.match(str(text))
    if not m:
        raise ValueError(
            f"invalid Admiralty grade {text!r}: expected a letter A-F followed by a digit 1-6 (e.g. B2)"
        )
    return m.group(1).upper(), int(m.group(2))


def describe(letter, digit):
    """Full look-up for one grade: both labels, both explanations, notes, citation."""
    rl, rm = RELIABILITY[letter]
    cl, cm = CREDIBILITY[digit]
    notes = []
    if letter == "F":
        notes.append(NOTE_F)
    if digit == 6:
        notes.append(NOTE_6)
    return {
        "grade": f"{letter}{digit}",
        "reliability": {"code": letter, "label": rl, "meaning": rm},
        "credibility": {"code": digit, "label": cl, "meaning": cm},
        "cannot_be_judged": not judgeable(letter, digit),
        "notes": notes,
        "citation": CITATION,
    }


def reliability_rank(letter):
    """A=1 .. E=5, F=6 (F sorts last; see ORDINAL_NOTE)."""
    return LETTERS.index(letter) + 1


def credibility_rank(digit):
    """1 .. 5, 6=6 (6 sorts last; see ORDINAL_NOTE)."""
    return int(digit)


def ordinal(letter, digit):
    """Heuristic sort key: reliability rank + credibility rank (2 = A1 .. 12 = F6)."""
    return reliability_rank(letter) + credibility_rank(digit)


def judgeable(letter, digit):
    """Neither axis is 'cannot be judged' (F or 6)."""
    return letter != "F" and digit != 6


def well_graded(letter, digit):
    """A or B on reliability AND 1 or 2 on credibility (the conflict-flag threshold)."""
    return letter in ("A", "B") and digit in (1, 2)


def matrix():
    """The 6x6 grid: rows = reliability A-F, columns = credibility 1-6."""
    return {
        "rows": [{"code": L, "label": RELIABILITY[L][0]} for L in LETTERS],
        "columns": [{"code": d, "label": CREDIBILITY[d][0]} for d in DIGITS],
        "cells": [[f"{L}{d}" for d in DIGITS] for L in LETTERS],
        "citation": CITATION,
    }


# --- input parsing (aggregate) -----------------------------------------------


def parse_sources(rows):
    """Validate a list of {source, grade, claim_polarity, note} dicts (one claim)."""
    items = []
    for i, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"row {i}: expected an object with source/grade/claim_polarity/note")
        row = {str(k).strip().lower(): v for k, v in row.items()}
        source = str(row.get("source") or "").strip()
        if not source:
            raise ValueError(f"row {i}: 'source' is required")
        try:
            letter, digit = parse_grade(row.get("grade") or "")
        except ValueError as exc:
            raise ValueError(f"row {i} ({source}): {exc}") from None
        pol = str(row.get("claim_polarity") or "").strip().lower()
        if pol not in POLARITIES:
            raise ValueError(
                f"row {i} ({source}): claim_polarity must be one of {'|'.join(POLARITIES)}, got {pol!r}"
            )
        items.append(
            {
                "source": source,
                "grade": f"{letter}{digit}",
                "letter": letter,
                "digit": digit,
                "claim_polarity": pol,
                "note": str(row.get("note") or "").strip(),
            }
        )
    return items


def load_file(path):
    """Load source rows from JSON (list or {"sources": [...]}), CSV, or '-' (stdin JSON)."""
    if path == "-":
        data = json.load(sys.stdin)
    elif path.lower().endswith(".csv"):
        with open(path, newline="", encoding="utf-8") as fh:
            return parse_sources(list(csv.DictReader(fh)))
    else:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    if isinstance(data, dict):
        data = data.get("sources", [])
    if not isinstance(data, list):
        raise ValueError("expected a JSON list of rows or an object with a 'sources' list")
    return parse_sources(data)


# --- aggregation (documented heuristics) -------------------------------------


def sort_key(item):
    """Deterministic order: heuristic ordinal, then letter, digit, source name, polarity, note."""
    return (
        ordinal(item["letter"], item["digit"]),
        item["letter"],
        item["digit"],
        item["source"],
        item["claim_polarity"],
        item["note"],
    )


def aggregate(items):
    """Summarise graded sources about one claim. Returns a JSON-able dict."""
    rel = {L: 0 for L in LETTERS}
    cred = {str(d): 0 for d in DIGITS}
    pol = {p: 0 for p in POLARITIES}
    for it in items:
        rel[it["letter"]] += 1
        cred[str(it["digit"])] += 1
        pol[it["claim_polarity"]] += 1

    ordered = sorted(items, key=sort_key)
    judged = [it for it in ordered if judgeable(it["letter"], it["digit"])]
    lateral = [it for it in ordered if not judgeable(it["letter"], it["digit"])]
    strong_for = [it for it in ordered
                  if well_graded(it["letter"], it["digit"]) and it["claim_polarity"] == "supports"]
    strong_against = [it for it in ordered
                      if well_graded(it["letter"], it["digit"]) and it["claim_polarity"] == "contradicts"]

    def brief(it):
        return {"source": it["source"], "grade": it["grade"]}

    return {
        "n": len(items),
        "reliability": rel,
        "credibility": cred,
        "polarity": pol,
        "best": brief(judged[0]) if judged else None,
        "worst": brief(judged[-1]) if judged else None,
        "cannot_be_judged": len(lateral),
        "lateral_check": [brief(it) for it in lateral],
        "conflict": bool(strong_for) and bool(strong_against),
        "well_graded_supports": [brief(it) for it in strong_for],
        "well_graded_contradicts": [brief(it) for it in strong_against],
        "sorted": [
            {
                "ordinal": ordinal(it["letter"], it["digit"]),
                "grade": it["grade"],
                "claim_polarity": it["claim_polarity"],
                "source": it["source"],
                "note": it["note"],
            }
            for it in ordered
        ],
        "heuristics": {
            "best_worst": "min/max of the heuristic ordinal over judgeable grades only (neither F nor 6); "
                          "ties broken by letter, digit, source name",
            "conflict": CONFLICT_NOTE,
            "ordinal": ORDINAL_NOTE,
        },
        "citation": CITATION,
    }


# --- rendering ---------------------------------------------------------------


def render_grade(d):
    r, c = d["reliability"], d["credibility"]
    lines = [
        d["grade"],
        f"  Reliability  {r['code']} — {r['label']}: {r['meaning']}",
        f"  Credibility  {c['code']} — {c['label']}: {c['meaning']}",
    ]
    for note in d["notes"]:
        lines.append(f"  Note: {note}")
    lines.append(f"  Source: {CITATION_SHORT}")
    return "\n".join(lines)


def render_matrix(m):
    width = max(len(f"{r['code']} {r['label']}") for r in m["rows"]) + 2
    lines = ["NATO Admiralty 6x6 grid — rows: source reliability (A-F); columns: information credibility (1-6)"]
    lines.append(" " * (width + 2) + "".join(f"{c['code']:>6}" for c in m["columns"]))
    for r, cells in zip(m["rows"], m["cells"]):
        lines.append(f"  {r['code']} {r['label']:<{width - 2}}" + "".join(f"{cell:>6}" for cell in cells))
    lines.append("Columns: " + " | ".join(f"{c['code']} {c['label']}" for c in m["columns"]))
    lines.append("The two axes are independent; the standard defines no ordering across cells "
                 "(F and 6 mean 'no basis to judge', not 'lowest').")
    lines.append(f"Source: {CITATION_SHORT}")
    return "\n".join(lines)


def _fmt_item(it):
    return f"{it['grade']:<3} {it['source']}"


def render_aggregate(a):
    lines = [
        f"Admiralty aggregate — {a['n']} source{'' if a['n'] == 1 else 's'} on one claim "
        "(claim_polarity is relative to that claim)",
        "Reliability (A-F):   " + " | ".join(f"{L} {a['reliability'][L]}" for L in LETTERS),
        "Credibility (1-6):   " + " | ".join(f"{d} {a['credibility'][str(d)]}" for d in DIGITS),
        "Polarity:            " + " | ".join(f"{p} {a['polarity'][p]}" for p in POLARITIES),
    ]
    if a["best"]:
        lines.append(f"Best judged grade:   {_fmt_item(a['best'])}")
        lines.append(f"Worst judged grade:  {_fmt_item(a['worst'])}")
    else:
        lines.append("Best/worst judged grade: none (every grade carries an F or a 6)")
    lines.append(f"Cannot be judged (F or 6): {a['cannot_be_judged']} of {a['n']}"
                 + (" -> lateral check before use:" if a["lateral_check"] else ""))
    for it in a["lateral_check"]:
        lines.append(f"  {_fmt_item(it)}")
    if a["conflict"]:
        lines.append("Conflict flag (heuristic, not part of the standard): YES")
        for it in a["well_graded_supports"]:
            lines.append(f"  well-graded (A/B, 1/2) supports:    {_fmt_item(it)}")
        for it in a["well_graded_contradicts"]:
            lines.append(f"  well-graded (A/B, 1/2) contradicts: {_fmt_item(it)}")
        lines.append("  Two well-graded sources point opposite ways: re-examine the credibility digits "
                     "(1-2 mean 'consistent with other information on the subject') or record the claim as contested.")
    else:
        why = ""
        if a["polarity"]["supports"] and a["polarity"]["contradicts"]:
            why = " (sources disagree, but not two well-graded A/B, 1/2 sources on opposite sides)"
        lines.append(f"Conflict flag (heuristic, not part of the standard): no{why}")
    lines.append("Sorted by heuristic ordinal (reliability rank + credibility rank; sorting only, not a score):")
    for it in a["sorted"]:
        lines.append(f"  {it['ordinal']:>2}  {it['grade']}  {it['claim_polarity']:<12} {it['source']}")
    lines.append(f"Source: {CITATION_SHORT}")
    return "\n".join(lines)


def to_ordinal(letter, digit):
    """Heuristic sort key for one grade, explicitly flagged as not part of the standard."""
    return {
        "grade": f"{letter}{digit}",
        "ordinal": ordinal(letter, digit),
        "reliability_rank": reliability_rank(letter),
        "credibility_rank": credibility_rank(digit),
        "judgeable": judgeable(letter, digit),
        "part_of_standard": False,
        "purpose": "sorting only",
        "note": ORDINAL_NOTE,
        "percentage": None,
        "percentage_note": PERCENT_NOTE,
    }


def render_ordinal(o):
    lines = [
        f"{o['grade']} -> heuristic ordinal {o['ordinal']}  "
        f"(reliability rank {o['grade'][0]}={o['reliability_rank']} + "
        f"credibility rank {o['grade'][1]}={o['credibility_rank']}; lower sorts first)",
        f"  {ORDINAL_NOTE}",
        f"  {PERCENT_NOTE}",
    ]
    return "\n".join(lines)


def dump(obj):
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)


# --- selftest ----------------------------------------------------------------


def run_selftest():
    """Hand-verified checks: the standard's wording, validation, matrix, aggregation."""
    n = [0]

    def check(name, got, want):
        n[0] += 1
        ok = got == want
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got!r}, expected {want!r}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    # 1. Validation.
    check("parse B2", parse_grade("B2"), ("B", 2))
    check("parse lower-case / separator", (parse_grade("b2"), parse_grade("F-6")), (("B", 2), ("F", 6)))
    for bad in ("G1", "A7", "A0", "B", "2", "22", "AA", "1B", "", "B2X"):
        try:
            parse_grade(bad)
            check(f"reject {bad!r}", "accepted", "ValueError")
        except ValueError:
            check(f"reject {bad!r}", "ValueError", "ValueError")

    # 2. Standard wording (AJP-2.1 labels; FM 2-22.3 App. B explanations).
    check("labels A-F", [RELIABILITY[L][0] for L in LETTERS],
          ["Completely reliable", "Usually reliable", "Fairly reliable", "Not usually reliable",
           "Unreliable", "Reliability cannot be judged"])
    check("labels 1-6", [CREDIBILITY[d][0] for d in DIGITS],
          ["Confirmed by other sources", "Probably true", "Possibly true", "Doubtful", "Improbable",
           "Truth cannot be judged"])
    check("3 = reasonably logical / agrees with some", CREDIBILITY[3][1],
          "Not confirmed; reasonably logical in itself; agrees with some other information on the subject")
    check("4 = possible but not logical / no other info", CREDIBILITY[4][1],
          "Not confirmed; possible but not logical; no other information on the subject")
    check("F = no basis for the source", RELIABILITY["F"][1],
          "No basis exists for evaluating the reliability of the source")
    d = describe("B", 2)
    check("describe B2 labels", (d["reliability"]["label"], d["credibility"]["label"]),
          ("Usually reliable", "Probably true"))
    check("describe F6 flags cannot_be_judged + both notes",
          (describe("F", 6)["cannot_be_judged"], len(describe("F", 6)["notes"])), (True, 2))
    check("describe A1 is judgeable", describe("A", 1)["cannot_be_judged"], False)

    # 3. Matrix: 6 x 6 = 36 cells, A1 first, F6 last.
    m = matrix()
    check("matrix rows x cols", (len(m["rows"]), len(m["columns"])), (6, 6))
    check("matrix 36 cells", sum(len(r) for r in m["cells"]), 36)
    check("matrix corners", (m["cells"][0][0], m["cells"][5][5]), ("A1", "F6"))

    # 4. Ordinal heuristic: A1=2, B2=4, F6=12; F/6 not judgeable.
    check("ordinal A1/B2/F6", [ordinal(*parse_grade(g)) for g in ("A1", "B2", "F6")], [2, 4, 12])
    o = to_ordinal("A", 6)
    check("to-ordinal A6 unjudgeable, no percentage", (o["judgeable"], o["percentage"], o["part_of_standard"]),
          (False, None, False))

    # 5. Aggregate on the fixed demo set (counted by hand):
    #    grades A1 B2 B2 D3 C6 F6 -> A1 B2 C1 D1 E0 F1 ; 1:1 2:2 3:1 4:0 5:0 6:2
    #    polarity supports 3 / contradicts 2 / neutral 1 ; F-or-6 items: C6, F6
    #    judgeable sorted: A1(2) B2(4) B2(4) D3(7) -> best A1, worst D3
    a = aggregate(parse_sources(DEMO))
    check("demo n", a["n"], 6)
    check("demo reliability counts", [a["reliability"][L] for L in LETTERS], [1, 2, 1, 1, 0, 1])
    check("demo credibility counts", [a["credibility"][str(d)] for d in DIGITS], [1, 2, 1, 0, 0, 2])
    check("demo polarity counts", [a["polarity"][p] for p in POLARITIES], [3, 2, 1])
    check("demo best/worst judged", (a["best"]["grade"], a["worst"]["grade"]), ("A1", "D3"))
    check("demo cannot be judged", a["cannot_be_judged"], 2)
    check("demo lateral list", [x["grade"] for x in a["lateral_check"]], ["C6", "F6"])
    check("demo sorted order (ordinal, letter, digit, name)",
          [x["source"] for x in a["sorted"]],
          ["Form D filing (regulator database)", "Trade-press article", "Wire-service report",
           "Founder's personal blog", "Vendor marketing page", "Anonymous forum post"])
    check("demo conflict (B2 supports vs B2 contradicts)", a["conflict"], True)
    check("demo conflict parties (A1 + B2 support, B2 contradicts)",
          ([x["source"] for x in a["well_graded_supports"]], [x["source"] for x in a["well_graded_contradicts"]]),
          (["Form D filing (regulator database)", "Wire-service report"], ["Trade-press article"]))

    # 6. Conflict flag: false cases.
    def agg(rows):
        return aggregate(parse_sources(rows))

    check("no conflict: B2 supports vs C2 contradicts (C not well-graded)",
          agg([{"source": "x", "grade": "B2", "claim_polarity": "supports"},
               {"source": "y", "grade": "C2", "claim_polarity": "contradicts"}])["conflict"], False)
    check("no conflict: B2 supports vs B3 contradicts (3 not well-graded)",
          agg([{"source": "x", "grade": "B2", "claim_polarity": "supports"},
               {"source": "y", "grade": "B3", "claim_polarity": "contradicts"}])["conflict"], False)
    check("no conflict: two A1 supports, one A1 neutral",
          agg([{"source": "x", "grade": "A1", "claim_polarity": "supports"},
               {"source": "y", "grade": "A1", "claim_polarity": "supports"},
               {"source": "z", "grade": "A1", "claim_polarity": "neutral"}])["conflict"], False)
    check("conflict: A1 supports vs B2 contradicts",
          agg([{"source": "x", "grade": "A1", "claim_polarity": "supports"},
               {"source": "y", "grade": "B2", "claim_polarity": "contradicts"}])["conflict"], True)
    only_f6 = agg([{"source": "x", "grade": "F6", "claim_polarity": "supports"}])
    check("all-F6 set: no best/worst, 1 lateral", (only_f6["best"], only_f6["cannot_be_judged"]), (None, 1))

    # 7. Input validation.
    for bad in ([{"source": "x", "grade": "B9", "claim_polarity": "supports"}],
                [{"source": "", "grade": "B2", "claim_polarity": "supports"}],
                [{"source": "x", "grade": "B2", "claim_polarity": "maybe"}],
                [{"source": "x", "grade": "B2"}]):
        try:
            parse_sources(bad)
            check(f"reject row {bad[0]!r}", "accepted", "ValueError")
        except ValueError:
            check(f"reject row {bad[0]!r}", "ValueError", "ValueError")

    # 8. Rendering is stable and JSON round-trips (determinism guard).
    check("aggregate JSON identical across two runs", dump(agg(DEMO)) == dump(aggregate(parse_sources(DEMO))), True)
    check("grade text names both labels",
          all(s in render_grade(describe("B", 2)) for s in ("Usually reliable", "Probably true", "FM 2-22.3")), True)
    with contextlib.redirect_stderr(io.StringIO()):
        percent_rc = main(["to-ordinal", "B2", "--percent"])
        invalid_rc = main(["grade", "Z9"])
    check("--percent is refused (exit 2: unusable request)", percent_rc, 2)
    check("invalid grade code exits 2 (unusable input)", invalid_rc, 2)

    print(f"{n[0]} checks passed")
    print("selftest OK")
    return 0


# --- CLI ---------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(
        description="NATO Admiralty (A-F / 1-6) grade look-up, 6x6 matrix and multi-source aggregation "
        "(AJP-2.1 / STANAG 2511; FM 2-22.3 App. B)."
    )
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true",
                        help="aggregate the built-in example set (same as `aggregate --demo`)")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("grade", help="validate a code such as B2; print both labels, definitions, citation")
    p.add_argument("code", help="letter A-F + digit 1-6, e.g. B2")
    p.add_argument("--json", action="store_true", help="JSON output")

    p = sub.add_parser("matrix", help="print the 6x6 grid with row/column labels")
    p.add_argument("--json", action="store_true", help="JSON output")

    p = sub.add_parser("aggregate", help="summarise graded sources about one claim "
                       "(distribution, best/worst, F/6, conflict flag)")
    p.add_argument("--file", help="JSON or CSV of rows {source, grade, claim_polarity, note}; "
                   "'-' reads JSON from stdin")
    p.add_argument("--demo", action="store_true", help="use the built-in example set")
    p.add_argument("--json", action="store_true", help="JSON output")

    p = sub.add_parser("to-ordinal", help="heuristic sort key (reliability rank + credibility rank); "
                       "NOT part of the standard")
    p.add_argument("code", help="letter A-F + digit 1-6, e.g. B2")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--percent", "--confidence", action="store_true", dest="percent",
                   help="request a percentage confidence (refused, with the reason; exit 1)")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo and not args.command:
        print(render_aggregate(aggregate(parse_sources(DEMO))))
        return 0
    if not args.command:
        parser.error("choose a command: grade | matrix | aggregate | to-ordinal  (or --demo / --selftest)")

    if args.command in ("grade", "to-ordinal"):
        try:
            letter, digit = parse_grade(args.code)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.command == "grade":
            d = describe(letter, digit)
            print(dump(d) if args.json else render_grade(d))
            return 0
        if args.percent:
            print(f"refused: {letter}{digit} is not converted into a percentage confidence.", file=sys.stderr)
            print(PERCENT_NOTE, file=sys.stderr)
            return 2
        o = to_ordinal(letter, digit)
        print(dump(o) if args.json else render_ordinal(o))
        return 0

    if args.command == "matrix":
        m = matrix()
        print(dump(m) if args.json else render_matrix(m))
        return 0

    # aggregate
    if args.demo:
        items = parse_sources(DEMO)
    elif args.file:
        try:
            items = load_file(args.file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: could not load {args.file}: {exc}", file=sys.stderr)
            return 2
    else:
        parser.error("aggregate needs --file PATH or --demo")
    if not items:
        print("error: no source rows to aggregate", file=sys.stderr)
        return 2
    a = aggregate(items)
    print(dump(a) if args.json else render_aggregate(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
