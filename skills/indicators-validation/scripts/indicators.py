#!/usr/bin/env python3
"""indicators.py -- validate a scenario indicator list (Indicators Validator).

Implements the Indicators Validator matrix of Heuer & Pherson, *Structured
Analytic Techniques for Intelligence Analysis* (2nd ed. CQ Press 2014, ch. 6
"Scenarios and Indicators"; 3rd ed. 2019, sec. 9.11 "Indicators Generation,
Validation, and Evaluation"), developed by Pherson Associates in 2008: every
indicator is rated, for every scenario, on how likely it is to be observed if
that scenario were unfolding --

    HL  Highly Likely to appear   +2
    L   Likely                    +1
    C   Could appear               0
    U   Unlikely                  -1
    HU  Highly Unlikely           -2

An indicator that would appear under every scenario discriminates nothing;
the ideal indicator is highly likely in the world it belongs to and highly
unlikely in every other world. Definitions computed here:

  * spread   = max rating - min rating across scenarios (0..4)
  * pairs    = number of scenario pairs whose ratings differ by >= 2 steps
  * verdict  = keep (spread >= 3) | weak (spread == 2) | drop (spread <= 1,
               i.e. identical or near-identical ratings)
  * for      = scenarios rated L or HL (the indicator is expected there);
               an indicator is UNIQUE to a scenario when it is expected in
               that scenario only
  * against  = scenarios rated U or HU (its appearance argues against them)
  * coverage = kept indicators unique to each scenario; a scenario with
               fewer than 3 is flagged (generate more before the plan ships)

Stdlib only. Python 3.9+. Deterministic (no clock, sorted iteration).

Usage:
    python3 indicators.py validate --file indicators.json [--json]
    python3 indicators.py matrix   --file indicators.json [--json]
    python3 indicators.py plan     --file indicators.json [--json]
    python3 indicators.py validate --demo          # built-in worked example
    python3 indicators.py --demo                   # same as: validate --demo
    python3 indicators.py --selftest

Exit codes: 0 ok | 1 invalid input or usage | 2 validate: at least one
scenario has fewer than 3 unique kept indicators.

Case file:
  {"question": str (optional), "revalidate": "YYYY-MM-DD" (optional),
   "scenarios": ["S1: label", ...]  or  [{"id": "S1", "label": "...",
                                          "description": "..."}, ...],
   "indicators": [{"id": "I1", "text": "observable, dated statement",
                   "ratings": {"S1": "HL", "S2": "U", "S3": "HU"},
                   "source": "...", "threshold": "...", "cadence": "...",
                   "owner": "..."}, ...]}
Ratings accept HL/L/C/U/HU, the full phrases ("highly likely", "could
appear", ...) or the integers 2/1/0/-1/-2. Every indicator needs a rating
for every scenario. source/threshold/cadence/owner are optional and feed
the monitoring plan (missing values print as {placeholders}).
"""

import argparse
import json
import re
import sys

# --- the rating scale (Pherson's Indicators Validator) -----------------------

RATING_VALUE = {"HL": 2, "L": 1, "C": 0, "U": -1, "HU": -2}
VALUE_RATING = {v: k for k, v in RATING_VALUE.items()}
RATING_PHRASE = {
    "highly likely": "HL", "likely": "L", "could": "C", "could appear": "C",
    "unlikely": "U", "highly unlikely": "HU",
}
SCALE_LEGEND = "HL highly likely | L likely | C could | U unlikely | HU highly unlikely (to be observed if the scenario were unfolding)"

# --- verdict thresholds (documented in SKILL.md; override by judgment) --------

KEEP_MIN_SPREAD = 3     # spread >= 3: at least one pair separated by HL/U or L/HU
DROP_MAX_SPREAD = 1     # spread <= 1: identical or near-identical ratings
PAIR_MIN_GAP = 2        # a scenario pair counts as discriminated at >= 2 steps
MIN_UNIQUE = 3          # unique kept indicators required per scenario
EXPECTED_MIN = 1        # rating >= L: the indicator is expected in the scenario
AGAINST_MAX = -1        # rating <= U: its appearance argues against the scenario


class CaseError(ValueError):
    """Raised when the input case file is malformed."""


# --- parsing -----------------------------------------------------------------


def parse_rating(raw):
    """Map HL/L/C/U/HU, a phrase, or an integer -2..2 to a rating code."""
    if isinstance(raw, bool):
        raise CaseError(f"bad rating {raw!r}")
    if isinstance(raw, (int, float)):
        if float(raw).is_integer() and int(raw) in VALUE_RATING:
            return VALUE_RATING[int(raw)]
        raise CaseError(f"bad rating {raw!r}; use 2/1/0/-1/-2 or HL/L/C/U/HU")
    s = str(raw).strip()
    if re.fullmatch(r"[+-]?\d+", s) and int(s) in VALUE_RATING:
        return VALUE_RATING[int(s)]
    code = s.upper().replace(" ", "")
    if code in RATING_VALUE:
        return code
    phrase = re.sub(r"\s+", " ", s.lower())
    phrase = re.sub(r"\s+to (appear|be observed|occur)$", "", phrase)
    if phrase in RATING_PHRASE:
        return RATING_PHRASE[phrase]
    raise CaseError(f"bad rating {raw!r}; use HL/L/C/U/HU, a phrase, or 2/1/0/-1/-2")


def natural_key(text):
    """Sort key so that I2 < I10 (digits compared numerically)."""
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", str(text))]


def parse_case(data):
    """Validate a case description; return (question, scenarios, indicators, meta).

    scenarios:  list of {"id", "label", "description"}
    indicators: list of {"id", "text", "ratings" {sid: code}, "source",
                "threshold", "cadence", "owner"}
    """
    if not isinstance(data, dict):
        raise CaseError("top level must be a JSON object")
    raw_sc = data.get("scenarios")
    if not isinstance(raw_sc, list) or len(raw_sc) < 2:
        raise CaseError("'scenarios' must be a list of at least 2 entries")
    scenarios, seen = [], set()
    for i, entry in enumerate(raw_sc, 1):
        if isinstance(entry, str):
            sid, _, label = entry.partition(":")
            sid, label, desc = sid.strip(), label.strip(), ""
        elif isinstance(entry, dict):
            sid = str(entry.get("id", "")).strip()
            label = str(entry.get("label", "")).strip()
            desc = str(entry.get("description", "")).strip()
        else:
            raise CaseError(f"scenario #{i} must be a string or an object")
        if not sid:
            sid = f"S{i}"
        if sid in seen:
            raise CaseError(f"duplicate scenario id {sid!r}")
        seen.add(sid)
        scenarios.append({"id": sid, "label": label or sid, "description": desc})
    sids = [s["id"] for s in scenarios]

    raw_ind = data.get("indicators")
    if not isinstance(raw_ind, list) or not raw_ind:
        raise CaseError("'indicators' must be a non-empty list")
    indicators, seen = [], set()
    for i, ind in enumerate(raw_ind, 1):
        if not isinstance(ind, dict):
            raise CaseError(f"indicator #{i} must be an object")
        iid = str(ind.get("id", f"I{i}")).strip() or f"I{i}"
        if iid in seen:
            raise CaseError(f"duplicate indicator id {iid!r}")
        seen.add(iid)
        ratings = ind.get("ratings")
        if not isinstance(ratings, dict):
            raise CaseError(f"indicator {iid}: 'ratings' must be an object")
        unknown = sorted(set(ratings) - set(sids), key=natural_key)
        if unknown:
            raise CaseError(f"indicator {iid}: ratings for unknown scenarios {unknown}")
        missing = [sid for sid in sids if sid not in ratings]
        if missing:
            raise CaseError(f"indicator {iid}: missing ratings for {missing}")
        norm = {}
        for sid in sids:
            try:
                norm[sid] = parse_rating(ratings[sid])
            except CaseError as exc:
                raise CaseError(f"indicator {iid}, scenario {sid}: {exc}") from None
        indicators.append({
            "id": iid,
            "text": str(ind.get("text", ind.get("description", ""))).strip(),
            "ratings": norm,
            "source": str(ind.get("source", "")).strip(),
            "threshold": str(ind.get("threshold", "")).strip(),
            "cadence": str(ind.get("cadence", "")).strip(),
            "owner": str(ind.get("owner", "")).strip(),
        })
    meta = {"revalidate": str(data.get("revalidate", "")).strip()}
    return str(data.get("question", "")).strip(), scenarios, indicators, meta


def load_case(path):
    """Read and validate a JSON case file; exit 1 with a message on failure."""
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


# --- diagnosticity -----------------------------------------------------------


def values(ind, sids):
    return [RATING_VALUE[ind["ratings"][sid]] for sid in sids]


def spread(ind, sids):
    """max - min rating value across scenarios (0 = cannot discriminate)."""
    v = values(ind, sids)
    return max(v) - min(v)


def pairs_discriminated(ind, sids):
    """(n_pairs_separated_by_>=PAIR_MIN_GAP, n_pairs)."""
    v = values(ind, sids)
    n_ok = n_all = 0
    for a in range(len(v)):
        for b in range(a + 1, len(v)):
            n_all += 1
            if abs(v[a] - v[b]) >= PAIR_MIN_GAP:
                n_ok += 1
    return n_ok, n_all


def verdict(sp):
    if sp >= KEEP_MIN_SPREAD:
        return "keep"
    if sp <= DROP_MAX_SPREAD:
        return "drop"
    return "weak"


def points_for(ind, sids):
    """Scenarios in which the indicator is expected (rated L or HL)."""
    return [sid for sid in sids if RATING_VALUE[ind["ratings"][sid]] >= EXPECTED_MIN]


def points_against(ind, sids):
    """Scenarios the indicator's appearance argues against (rated U or HU)."""
    return [sid for sid in sids if RATING_VALUE[ind["ratings"][sid]] <= AGAINST_MAX]


def unique_to(ind, sids):
    """The single scenario the indicator is expected in, else None."""
    f = points_for(ind, sids)
    return f[0] if len(f) == 1 else None


def assess(ind, sids):
    """All per-indicator diagnosticity fields as a dict."""
    sp = spread(ind, sids)
    n_ok, n_all = pairs_discriminated(ind, sids)
    return {
        "id": ind["id"], "text": ind["text"], "ratings": dict(ind["ratings"]),
        "spread": sp, "pairs": n_ok, "pairs_total": n_all, "verdict": verdict(sp),
        "for": points_for(ind, sids), "against": points_against(ind, sids),
        "unique_to": unique_to(ind, sids),
        "source": ind["source"], "threshold": ind["threshold"],
        "cadence": ind["cadence"], "owner": ind["owner"],
    }


def rank(assessed):
    """Most diagnostic first: spread desc, pairs desc, then natural id order."""
    return sorted(assessed, key=lambda a: (-a["spread"], -a["pairs"], natural_key(a["id"])))


def coverage(assessed, scenarios):
    """Per scenario: kept indicators unique to it (+ weak reserve) and a warning
    when the kept count is below MIN_UNIQUE."""
    out = []
    for sc in scenarios:
        by_id = sorted(assessed, key=lambda a: natural_key(a["id"]))
        kept = [a["id"] for a in by_id if a["verdict"] == "keep" and a["unique_to"] == sc["id"]]
        weak = [a["id"] for a in by_id if a["verdict"] == "weak" and a["unique_to"] == sc["id"]]
        warn = None
        if len(kept) < MIN_UNIQUE:
            warn = (f"only {len(kept)} unique kept indicator(s) (need >= {MIN_UNIQUE}) -- "
                    "generate more, or tighten a weak one until its spread reaches "
                    f"{KEEP_MIN_SPREAD}")
        out.append({"id": sc["id"], "label": sc["label"], "unique_kept": kept,
                    "unique_weak": weak, "warning": warn})
    return out


def analyse(question, scenarios, indicators, meta):
    sids = [s["id"] for s in scenarios]
    assessed = []
    for n, ind in enumerate(indicators):
        a = assess(ind, sids)
        a["order"] = n          # position in the case file (matrix keeps it)
        assessed.append(a)
    ranked = rank(assessed)
    cov = coverage(assessed, scenarios)
    counts = {v: sum(1 for a in assessed if a["verdict"] == v) for v in ("keep", "weak", "drop")}
    return {
        "question": question, "revalidate": meta.get("revalidate", ""),
        "scenarios": scenarios, "indicators": ranked, "ranking": [a["id"] for a in ranked],
        "counts": counts, "coverage": cov,
        "warnings": [f"{c['id']} {c['label']}: {c['warning']}" for c in cov if c["warning"]],
        "thresholds": {"keep_min_spread": KEEP_MIN_SPREAD, "drop_max_spread": DROP_MAX_SPREAD,
                       "pair_min_gap": PAIR_MIN_GAP, "min_unique_per_scenario": MIN_UNIQUE},
    }


# --- text output -------------------------------------------------------------


def _clip(text, width):
    return text if len(text) <= width else text[: width - 3] + "..."


def _header(result):
    if result["question"]:
        print(f"Question: {result['question']}")
    print("Scenarios: " + " | ".join(f"{s['id']} {s['label']}" for s in result["scenarios"]))
    print(f"Scale: {SCALE_LEGEND}")
    print()


def print_validate(result):
    _header(result)
    sids = [s["id"] for s in result["scenarios"]]
    tw = 44
    print("Indicators ranked by diagnosticity (spread = max - min; pairs = scenario pairs "
          f"separated by >= {PAIR_MIN_GAP} steps):")
    head = f"{'ID':<5} {'Indicator':<{tw}} " + " ".join(f"{s:>4}" for s in sids) + \
        f"  {'Spread':>6} {'Pairs':>5}  {'Verdict':<7} {'For':<9} Against"
    print(head)
    print("-" * len(head))
    for a in result["indicators"]:
        cells = " ".join(f"{a['ratings'][s]:>4}" for s in sids)
        for_txt = ",".join(a["for"]) or "-"
        ag_txt = ",".join(a["against"]) or "-"
        if a["unique_to"]:
            for_txt += "*"
        pairs = f"{a['pairs']}/{a['pairs_total']}"
        print(f"{a['id']:<5} {_clip(a['text'], tw):<{tw}} {cells}  {a['spread']:>6} {pairs:>5}  "
              f"{a['verdict']:<7} {for_txt:<9} {ag_txt}")
    print("-" * len(head))
    print(f"Verdict rule: keep spread >= {KEEP_MIN_SPREAD} | weak spread == {KEEP_MIN_SPREAD - 1} | "
          f"drop spread <= {DROP_MAX_SPREAD} (identical or near-identical ratings cannot discriminate). "
          "* = unique to that scenario.")
    c = result["counts"]
    print(f"Kept {c['keep']} | weak {c['weak']} | dropped {c['drop']} (of {len(result['indicators'])})")
    print()
    print(f"Coverage (kept indicators unique to one scenario; need >= {MIN_UNIQUE} each):")
    for cov in result["coverage"]:
        reserve = f" + {len(cov['unique_weak'])} weak reserve ({', '.join(cov['unique_weak'])})" if cov["unique_weak"] else ""
        status = "ok" if not cov["warning"] else "WARNING: " + cov["warning"]
        ids = ", ".join(cov["unique_kept"]) or "none"
        print(f"  {cov['id']:<4} {_clip(cov['label'], 24):<24} {len(cov['unique_kept'])}  ({ids}){reserve}   {status}")
    if result["revalidate"]:
        print(f"\nRe-validate the list by: {result['revalidate']}")


def print_matrix(result):
    _header(result)
    sids = [s["id"] for s in result["scenarios"]]
    tw = 60
    head = f"{'ID':<5} {'Indicator':<{tw}} " + " ".join(f"{s:>4}" for s in sids) + f"  {'Spread':>6}"
    print("Indicators Validator matrix (file order):")
    print(head)
    print("-" * len(head))
    for a in sorted(result["indicators"], key=lambda a: a["order"]):
        cells = " ".join(f"{a['ratings'][s]:>4}" for s in sids)
        print(f"{a['id']:<5} {_clip(a['text'], tw):<{tw}} {cells}  {a['spread']:>6}")
    print("-" * len(head))
    print("\nScenarios:")
    for s in result["scenarios"]:
        desc = f" -- {s['description']}" if s["description"] else ""
        print(f"  {s['id']}  {s['label']}{desc}")


def plan_rows(result):
    """Monitoring-plan rows for kept indicators, most diagnostic first."""
    rows = []
    for a in result["indicators"]:
        if a["verdict"] != "keep":
            continue
        rows.append({
            "id": a["id"], "indicator": a["text"],
            "for": ",".join(a["for"]) or "-", "against": ",".join(a["against"]) or "-",
            "source": a["source"] or "{source}",
            "threshold": a["threshold"] or "{threshold}",
            "cadence": a["cadence"] or "{cadence}",
            "owner": a["owner"] or "{owner}",
        })
    return rows


def print_plan(result):
    _header(result)
    rows = plan_rows(result)
    print(f"Monitoring plan -- {len(rows)} kept indicators (most diagnostic first). "
          "Fill every {placeholder} before the plan ships.")
    cols = [("id", "ID", 4), ("indicator", "Indicator", 38), ("for", "For", 5),
            ("source", "Source", 30), ("threshold", "Threshold", 30), ("cadence", "Cadence", 11), ("owner", "Owner", 18)]
    head = " ".join(f"{title:<{w}}" for _, title, w in cols)
    print(head)
    print("-" * len(head))
    for r in rows:
        print(" ".join(f"{_clip(r[key], w):<{w}}" for key, _, w in cols).rstrip())
    print("-" * len(head))
    print(f"Re-validate the whole list by: {result['revalidate'] or '{YYYY-MM-DD}'} "
          "(re-rate every indicator; retire indicators the target has learned to fake).")
    print("Log absence too: an expected indicator that fails to appear by its date is evidence against its scenario.")


# --- built-in worked example (SKILL.md) --------------------------------------

DEMO = {
    "question": "Which grid-storage battery scenario is unfolding by 2030?",
    "revalidate": "2027-01-31",
    "scenarios": [
        {"id": "S1", "label": "Lithium Lock-in",
         "description": "LFP lithium-ion keeps >= 85% of new grid-storage GWh through 2030"},
        {"id": "S2", "label": "Sodium Surge",
         "description": "sodium-ion takes >= 25% of new stationary-storage GWh by 2030"},
        {"id": "S3", "label": "Long-Duration Leap",
         "description": "non-lithium 8-hour-plus technologies take >= 25% of new grid-storage capacity by 2030"},
    ],
    "indicators": [
        {"id": "I1", "text": "Sodium-ion cells quoted at or below $50/kWh at GWh volume by at least two suppliers",
         "ratings": {"S1": "U", "S2": "HL", "S3": "C"},
         "source": "supplier price sheets; battery price surveys", "threshold": "<= $50/kWh from >= 2 suppliers",
         "cadence": "quarterly", "owner": "cell-market analyst"},
        {"id": "I2", "text": "At least 30% of MW awarded in US/EU/China utility storage tenders in a year specifies 8-hour-plus duration",
         "ratings": {"S1": "U", "S2": "U", "S3": "HL"},
         "source": "public tender awards (DOE, EU TSOs, NEA)", "threshold": ">= 30% of awarded MW at >= 8 h",
         "cadence": "semi-annual", "owner": "policy analyst"},
        {"id": "I3", "text": "Lithium carbonate spot price stays below $15/kg for four consecutive quarters",
         "ratings": {"S1": "HL", "S2": "U", "S3": "C"},
         "source": "lithium carbonate spot index", "threshold": "< $15/kg for 4 consecutive quarters",
         "cadence": "quarterly", "owner": "commodities analyst"},
        {"id": "I4", "text": "Global grid-storage installations exceed 100 GWh in a calendar year",
         "ratings": {"S1": "HL", "S2": "HL", "S3": "L"},
         "source": "annual market reports", "threshold": "> 100 GWh/yr", "cadence": "annual", "owner": ""},
        {"id": "I5", "text": "A top-5 cell maker commissions a sodium-ion line of 10 GWh/yr or more dedicated to stationary storage",
         "ratings": {"S1": "HU", "S2": "HL", "S3": "C"},
         "source": "company filings and press releases", "threshold": ">= 10 GWh/yr line commissioned",
         "cadence": "quarterly", "owner": "cell-market analyst"},
        {"id": "I6", "text": "A major market adopts capacity-market rules that pay duration-weighted credit beyond 4 hours",
         "ratings": {"S1": "C", "S2": "C", "S3": "HL"},
         "source": "regulator rulemaking dockets", "threshold": "final rule adopted", "cadence": "semi-annual",
         "owner": "policy analyst"},
        {"id": "I7", "text": "An iron-air or flow-battery project of 100 MW or more reaches commercial operation with published round-trip efficiency and availability",
         "ratings": {"S1": "HU", "S2": "U", "S3": "HL"},
         "source": "developer releases; grid-operator commissioning notices", "threshold": ">= 100 MW in operation with published data",
         "cadence": "semi-annual", "owner": "technology analyst"},
        {"id": "I8", "text": "Government storage subsidies and mandates continue in the major markets",
         "ratings": {"S1": "L", "S2": "L", "S3": "L"},
         "source": "policy trackers", "threshold": "n/a", "cadence": "annual", "owner": ""},
        {"id": "I9", "text": "At least two announced sodium-ion gigafactories are cancelled or delayed by more than 12 months",
         "ratings": {"S1": "HL", "S2": "HU", "S3": "C"},
         "source": "trade press; company filings", "threshold": ">= 2 cancellations or > 12-month delays",
         "cadence": "quarterly", "owner": "cell-market analyst"},
        {"id": "I10", "text": "Sodium-ion exceeds 10% of new stationary-storage GWh in China in a calendar year (industry-association data)",
         "ratings": {"S1": "U", "S2": "HL", "S3": "U"},
         "source": "industry-association annual statistics", "threshold": "> 10% of new stationary GWh",
         "cadence": "annual", "owner": "cell-market analyst"},
        {"id": "I11", "text": "At least two long-duration projects above 100 MW are cancelled or re-scoped to 4-hour lithium",
         "ratings": {"S1": "L", "S2": "C", "S3": "HU"},
         "source": "trade press; regulator project registers", "threshold": ">= 2 projects > 100 MW cancelled or re-scoped",
         "cadence": "semi-annual", "owner": "technology analyst"},
        {"id": "I12", "text": "More than 3 GW of 8-hour-plus storage holds signed offtake contracts in a single market's interconnection queue",
         "ratings": {"S1": "U", "S2": "C", "S3": "HL"},
         "source": "interconnection-queue data (e.g. CAISO, ERCOT, PJM)", "threshold": "> 3 GW at >= 8 h with signed offtake",
         "cadence": "quarterly", "owner": "policy analyst"},
    ],
}


# --- selftest ----------------------------------------------------------------


def selftest():
    """Hand-verified checks (values computed by hand from the definitions in
    the module docstring before being encoded here)."""
    checks = []

    def check(name, ok):
        checks.append(bool(ok))
        print(f"{'PASS' if ok else 'FAIL'} -- {name}")

    def ind(*codes):
        return {"id": "X", "text": "", "ratings": {f"S{i}": c for i, c in enumerate(codes, 1)},
                "source": "", "threshold": "", "cadence": "", "owner": ""}

    sids = ["S1", "S2", "S3"]

    # 1. rating parsing: codes, phrases, integers, numeric strings
    check("parse ratings: HL, 'highly unlikely', 'Could', 1, '-1', 'Likely to appear'",
          [parse_rating(x) for x in ("HL", "highly unlikely", "Could", 1, "-1", "Likely to appear")]
          == ["HL", "HU", "C", "L", "U", "L"])

    # 2. spread = max - min: (HL,U,HU) = 2-(-2) = 4; (L,C,C) = 1; (C,C,C) = 0
    check("spread (HL,U,HU)=4, (L,C,C)=1, (C,C,C)=0",
          [spread(ind(*r), sids) for r in (("HL", "U", "HU"), ("L", "C", "C"), ("C", "C", "C"))] == [4, 1, 0])

    # 3. verdicts by spread: 4,3 keep | 2 weak | 1,0 drop (uniform rows dropped)
    check("verdict spread 4/3 keep, 2 weak, 1/0 drop",
          [verdict(s) for s in (4, 3, 2, 1, 0)] == ["keep", "keep", "weak", "drop", "drop"])
    check("uniform row (L,L,L) is dropped; near-uniform (HL,HL,L) is dropped",
          verdict(spread(ind("L", "L", "L"), sids)) == "drop"
          and verdict(spread(ind("HL", "HL", "L"), sids)) == "drop")

    # 4. pairwise discrimination (gap >= 2): (HL,C,HU): 2,4,2 -> 3/3;
    #    (HL,L,U): 1,3,2 -> 2/3; (L,L,L): 0/3
    check("pairs (HL,C,HU)=3/3, (HL,L,U)=2/3, (L,L,L)=0/3",
          [pairs_discriminated(ind(*r), sids) for r in (("HL", "C", "HU"), ("HL", "L", "U"), ("L", "L", "L"))]
          == [(3, 3), (2, 3), (0, 3)])

    # 5. uniqueness: expected (>= L) in exactly one scenario
    check("unique: (HL,C,U)->S1; (L,L,U)->None; (HL,L,HU)->None; (HU,L,L)->None",
          [unique_to(ind(*r), sids) for r in (("HL", "C", "U"), ("L", "L", "U"), ("HL", "L", "HU"), ("HU", "L", "L"))]
          == ["S1", None, None, None])
    check("for/against: (HL,C,HU) -> for [S1], against [S3]",
          points_for(ind("HL", "C", "HU"), sids) == ["S1"] and points_against(ind("HL", "C", "HU"), sids) == ["S3"])

    # 6. coverage warning: S1 has 3 unique kept, S2 has 1, S3 has 0
    tiny = {"scenarios": ["S1: a", "S2: b", "S3: c"], "indicators": [
        {"id": "A", "ratings": {"S1": "HL", "S2": "U", "S3": "HU"}},
        {"id": "B", "ratings": {"S1": "HL", "S2": "HU", "S3": "U"}},
        {"id": "C", "ratings": {"S1": "L", "S2": "HU", "S3": "U"}},
        {"id": "D", "ratings": {"S1": "U", "S2": "HL", "S3": "U"}},
        {"id": "E", "ratings": {"S1": "C", "S2": "C", "S3": "HL"}},   # weak reserve for S3
    ]}
    res = analyse(*parse_case(tiny))
    cov = {c["id"]: c for c in res["coverage"]}
    check("coverage counts S1=3 (A,B,C), S2=1 (D), S3=0 with weak reserve E",
          cov["S1"]["unique_kept"] == ["A", "B", "C"] and cov["S2"]["unique_kept"] == ["D"]
          and cov["S3"]["unique_kept"] == [] and cov["S3"]["unique_weak"] == ["E"])
    check("coverage warning fires for S2 and S3 only",
          [c["id"] for c in res["coverage"] if c["warning"]] == ["S2", "S3"] and len(res["warnings"]) == 2)

    # 7. invalid input rejected
    def rejects(case, why):
        try:
            parse_case(case)
        except CaseError:
            return True
        print(f"      (accepted but should reject: {why})")
        return False
    base = {"scenarios": ["S1: a", "S2: b"]}
    check("invalid rating 'maybe' rejected",
          rejects({**base, "indicators": [{"ratings": {"S1": "maybe", "S2": "C"}}]}, "maybe"))
    check("out-of-range numeric rating 3 rejected",
          rejects({**base, "indicators": [{"ratings": {"S1": 3, "S2": "C"}}]}, "3"))
    check("missing scenario rating rejected",
          rejects({**base, "indicators": [{"ratings": {"S1": "HL"}}]}, "missing S2"))
    check("rating for unknown scenario rejected",
          rejects({**base, "indicators": [{"ratings": {"S1": "HL", "S2": "C", "S9": "U"}}]}, "S9"))
    check("fewer than 2 scenarios rejected",
          rejects({"scenarios": ["S1: a"], "indicators": [{"ratings": {"S1": "HL"}}]}, "1 scenario"))
    check("duplicate indicator id rejected",
          rejects({**base, "indicators": [{"id": "I1", "ratings": {"S1": "HL", "S2": "U"}},
                                          {"id": "I1", "ratings": {"S1": "U", "S2": "HL"}}]}, "dup id"))

    # 8. worked example (SKILL.md): 9 keep, 1 weak, 2 drop; ranking; full coverage
    demo = analyse(*parse_case(DEMO))
    check("demo counts keep 9 / weak 1 / drop 2",
          demo["counts"] == {"keep": 9, "weak": 1, "drop": 2})
    check("demo ranking I5, I9, I7, I1, I2, I3, I10, I11, I12, I6, I4, I8",
          demo["ranking"] == ["I5", "I9", "I7", "I1", "I2", "I3", "I10", "I11", "I12", "I6", "I4", "I8"])
    by_id = {a["id"]: a for a in demo["indicators"]}
    check("demo I5 spread 4 pairs 3/3 unique S2; I7 spread 4 pairs 2/3 unique S3; I6 weak spread 2",
          (by_id["I5"]["spread"], by_id["I5"]["pairs"], by_id["I5"]["unique_to"]) == (4, 3, "S2")
          and (by_id["I7"]["spread"], by_id["I7"]["pairs"], by_id["I7"]["unique_to"]) == (4, 2, "S3")
          and (by_id["I6"]["verdict"], by_id["I6"]["spread"]) == ("weak", 2))
    check("demo coverage 3/3/3, no warnings",
          [len(c["unique_kept"]) for c in demo["coverage"]] == [3, 3, 3] and demo["warnings"] == [])
    check("demo plan lists exactly the 9 kept indicators, most diagnostic first",
          [r["id"] for r in plan_rows(demo)] == ["I5", "I9", "I7", "I1", "I2", "I3", "I10", "I11", "I12"])

    passed = sum(checks)
    print(f"\nSELFTEST {'PASSED' if passed == len(checks) else 'FAILED'} ({passed}/{len(checks)} checks)")
    if passed == len(checks):
        print("selftest OK")
        return 0
    return 1


# --- CLI ---------------------------------------------------------------------


def get_result(args):
    if args.demo:
        return analyse(*parse_case(DEMO))
    if args.file:
        return analyse(*load_case(args.file))
    raise SystemExit("error: pass --file PATH or --demo")


def cmd_validate(args):
    result = get_result(args)
    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    else:
        print_validate(result)
    return 1 if result["warnings"] else 0


def cmd_matrix(args):
    result = get_result(args)
    if args.json:
        grid = {"question": result["question"], "scenarios": result["scenarios"],
                "matrix": [{"id": a["id"], "text": a["text"], "ratings": a["ratings"], "spread": a["spread"]}
                           for a in sorted(result["indicators"], key=lambda a: a["order"])]}
        print(json.dumps(grid, indent=1, sort_keys=True))
    else:
        print_matrix(result)
    return 0


def cmd_plan(args):
    result = get_result(args)
    if args.json:
        print(json.dumps({"question": result["question"], "revalidate": result["revalidate"],
                          "plan": plan_rows(result)}, indent=1, sort_keys=True))
    else:
        print_plan(result)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Indicators Validator: rate indicators against scenarios, compute "
                    "diagnosticity (spread, pairwise discrimination), keep/weak/drop verdicts, "
                    "per-scenario coverage, and a monitoring-plan skeleton.")
    parser.add_argument("--selftest", action="store_true", help="run hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true", help="shortcut for: validate --demo")
    sub = parser.add_subparsers(dest="command")
    for name, helptext in (
            ("validate", "ranked diagnosticity table, verdicts and per-scenario coverage (exit 2 on coverage warning)"),
            ("matrix", "print the indicator x scenario rating grid"),
            ("plan", "monitoring-plan skeleton for kept indicators (source / threshold / cadence / owner)")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--file", help="JSON case file (see module docstring)")
        p.add_argument("--demo", action="store_true", help="use the built-in worked example")
        p.add_argument("--json", action="store_true", help="JSON output instead of text")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.command:
        if args.demo:
            args.command, args.file, args.json = "validate", None, False
            return cmd_validate(args)
        parser.print_help()
        return 1
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "matrix":
        return cmd_matrix(args)
    return cmd_plan(args)


if __name__ == "__main__":
    sys.exit(main())
