#!/usr/bin/env python3
"""rob2.py — Cochrane RoB 2 domain-level and overall risk-of-bias judgements.

Implements, mechanically, the published signalling-question -> judgement
algorithms of the revised Cochrane risk-of-bias tool for randomized trials
(RoB 2), for the *effect of assignment to intervention* (the intention-to-treat
effect), individually randomized parallel-group trials:

  Domain 1  Bias arising from the randomization process         SQ 1.1-1.3  Figure 1 / Table 4
  Domain 2  Bias due to deviations from intended interventions  SQ 2.1-2.7  Figure 2 / Table 6
  Domain 3  Bias due to missing outcome data                    SQ 3.1-3.4  Figure 4 / Table 10
  Domain 4  Bias in measurement of the outcome                  SQ 4.1-4.5  Figure 5 / Table 12
  Domain 5  Bias in selection of the reported result            SQ 5.1-5.3  Figure 7 / Table 14
  Overall   Table 1: Low if every domain is Low; Some concerns if >=1 domain
            is Some concerns and none is High; High if >=1 domain is High
            OR "some concerns for multiple domains in a way that substantially
            lowers confidence in the result".

The all-Low, Some-concerns and ">=1 High" rules are applied exactly. The
"multiple Some concerns" clause is a review-author judgement in RoB 2, not an
algorithm; this tool reports the count of Some-concerns domains and escalates to
High only when that count reaches --sc-high-threshold (default 3), saying so.

Signalling-question answers: Y / PY / PN / N / NI, plus NA for the conditional
questions (2.3-2.5, 2.7, 3.2-3.4, 4.3-4.5). Judgements: Low / Some concerns /
High. Optional per-domain and overall "direction" fields (NA / Favours
experimental / Favours comparator / Towards null / Away from null /
Unpredictable) are validated and passed through, never computed.

Source (algorithms, response options, Table 1 — wording NOT reproduced, see below):
  Higgins JPT, Savovic J, Page MJ, Sterne JAC (eds), on behalf of the RoB2
  Development Group. "Revised Cochrane risk-of-bias tool for randomized trials
  (RoB 2)" — full guidance document, version of 22 August 2019, and the short
  version (cribsheet) of the same date; both at
  https://www.riskofbias.info/welcome/rob-2-0-tool/current-version-of-rob-2
  Sterne JAC, Savovic J, Page MJ, et al. "RoB 2: a revised tool for assessing
  risk of bias in randomised trials." BMJ 2019;366:l4898.
  doi:10.1136/bmj.l4898

Licensing: RoB 2 is © its authors and is published under a Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International licence (CC BY-NC-ND
4.0). This file therefore does NOT reproduce the signalling-question wording.
What it keeps is the unprotectable method — the question IDs, the response-option
constraints and the published decision logic — with each question labelled by a
short topic descriptor written for this skill. Read the authoritative wording at
https://www.riskofbias.info/welcome/rob-2-0-tool and answer against that text,
not against the labels here. --sc-high-threshold is this skill's own addition and
is not part of the instrument.

Not implemented: the effect of *adhering* to intervention (Domain 2, Figure 3),
cluster-randomized (Domain 1b) and cross-over variants.

Input JSON (nested by domain; a flat {"1.1": "Y", ...} object is also accepted):
  {"study": "...", "outcome": "...", "effect": "assignment",
   "D1": {"1.1": "Y", "1.2": "PY", "1.3": "N", "direction": "NA"},
   "D2": {"2.1": "N", "2.2": "N", "2.6": "Y"},
   "D3": {"3.1": "N", "3.2": "N", "3.3": "Y", "3.4": "PN"},
   "D4": {"4.1": "N", "4.2": "N", "4.3": "Y", "4.4": "Y", "4.5": "PN"},
   "D5": {"5.1": "Y", "5.2": "N", "5.3": "N"}}
Full-word answers ("Probably yes", "No information") are accepted too.

Stdlib only. Python 3.9+. Offline. Deterministic.

Usage:
    python3 rob2.py judge --file answers.json [--json] [--sc-high-threshold 3]
    python3 rob2.py judge --demo                # SKILL.md worked example
    python3 rob2.py questions [--json | --template]   # IDs + topics + options
    python3 rob2.py --selftest
Exit codes: 0 judgement produced (whatever it is); 1 invalid input or usage.
"""

import argparse
import json
import sys
import textwrap

# --- the tool as published ---------------------------------------------------

SOURCE_TITLE = ("Revised Cochrane risk-of-bias tool for randomized trials (RoB 2) — "
                "full guidance document and cribsheet, version of 22 August 2019 "
                "(Higgins JPT, Savovic J, Page MJ, Sterne JAC, eds; RoB2 Development Group)")
SOURCE_URL = "https://www.riskofbias.info/welcome/rob-2-0-tool/current-version-of-rob-2"
SOURCE_PAPER = ("Sterne JAC et al. RoB 2: a revised tool for assessing risk of bias in "
                "randomised trials. BMJ 2019;366:l4898. doi:10.1136/bmj.l4898")
EFFECT = "effect of assignment to intervention (intention-to-treat effect)"

# The instrument's own text is under CC BY-NC-ND 4.0 and is not reproduced by
# this skill; every route into the tool points the assessor at the source.
WORDING_URL = "https://www.riskofbias.info/welcome/rob-2-0-tool"
QUESTION_LOCATOR = ("signalling-question boxes of the full guidance "
                    "(Boxes 4, 6, 8, 10 and 11; effect of assignment)")
WORDING_NOTICE = (
    "AUTHORITATIVE WORDING NOT REPRODUCED HERE. RoB 2 is © its authors and is licensed "
    "CC BY-NC-ND 4.0, so this skill carries only question IDs, response options and the "
    "published decision logic. The signalling questions must be read, in full, at "
    + WORDING_URL + " and answered against that text — the one-line topics below are "
    "signposts written for this skill, not the instrument."
)

LOW, SC, HIGH = "Low", "Some concerns", "High"
SEVERITY = {LOW: 0, SC: 1, HIGH: 2}
JUDGEMENT_LONG = {LOW: "Low risk of bias", SC: "Some concerns", HIGH: "High risk of bias"}

YES = ("Y", "PY")
NO = ("N", "PN")
FULL_OPTIONS = ("Y", "PY", "PN", "N", "NI")

# Accepted spellings (lower-cased) -> canonical code.
ANSWER_ALIASES = {
    "y": "Y", "yes": "Y",
    "py": "PY", "probably yes": "PY",
    "pn": "PN", "probably no": "PN",
    "n": "N", "no": "N",
    "ni": "NI", "no information": "NI", "no info": "NI",
    "na": "NA", "n/a": "NA", "not applicable": "NA",
}

DIRECTIONS = ("NA", "Favours experimental", "Favours comparator",
              "Towards null", "Away from null", "Unpredictable")

DOMAINS = [
    ("D1", "Bias arising from the randomization process", ("1.1", "1.2", "1.3")),
    ("D2", "Bias due to deviations from intended interventions",
     ("2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7")),
    ("D3", "Bias due to missing outcome data", ("3.1", "3.2", "3.3", "3.4")),
    ("D4", "Bias in measurement of the outcome", ("4.1", "4.2", "4.3", "4.4", "4.5")),
    ("D5", "Bias in selection of the reported result", ("5.1", "5.2", "5.3")),
]
DOMAIN_SHORT = {
    "D1": "randomization process", "D2": "deviations from intended interventions",
    "D3": "missing outcome data", "D4": "measurement of the outcome",
    "D5": "selection of the reported result",
}
DOMAIN_OF = {q: d for d, _, qs in DOMAINS for q in qs}

# Signalling-question inventory. The published wording is NOT reproduced here —
# RoB 2 is © its authors under CC BY-NC-ND 4.0 (see the licensing note in the
# module docstring). Each entry keeps only the unprotectable method: the
# question ID, the branching "condition" of the published algorithm (conditional
# questions also offer NA), and the published response-option set ("options";
# note 3.2 offers no "No information"). "topic" is a short descriptor written
# for this skill naming what the question is about — a signpost, never a
# substitute for the instrument's text. Read the exact wording at WORDING_URL
# (5.2 and 5.3 share one printed stem there) and answer against it.
QUESTIONS = {
    "1.1": dict(topic="allocation sequence random?", condition="", options=FULL_OPTIONS),
    "1.2": dict(topic="allocation concealed until enrolment and assignment?",
                condition="", options=FULL_OPTIONS),
    "1.3": dict(topic="baseline differences suggesting a randomization problem?",
                condition="", options=FULL_OPTIONS),
    "2.1": dict(topic="participant awareness of their own trial arm?",
                condition="", options=FULL_OPTIONS),
    "2.2": dict(topic="carers and intervention deliverers aware of the assignment?",
                condition="", options=FULL_OPTIONS),
    "2.3": dict(topic="departures from the intended intervention arising from the trial context?",
                condition="If Y/PY/NI to 2.1 or 2.2", options=("NA",) + FULL_OPTIONS),
    "2.4": dict(topic="outcome plausibly affected by those departures?",
                condition="If Y/PY to 2.3", options=("NA",) + FULL_OPTIONS),
    "2.5": dict(topic="those departures balanced across arms?",
                condition="If Y/PY/NI to 2.4", options=("NA",) + FULL_OPTIONS),
    "2.6": dict(topic="analysis appropriate for the effect of assignment (ITT)?",
                condition="", options=FULL_OPTIONS),
    "2.7": dict(topic="potential for substantial impact of not analysing as randomized?",
                condition="If N/PN/NI to 2.6", options=("NA",) + FULL_OPTIONS),
    "3.1": dict(topic="data available for all or nearly all randomized participants?",
                condition="", options=FULL_OPTIONS),
    "3.2": dict(topic="evidence against bias from the absent data?",
                condition="If N/PN/NI to 3.1", options=("NA", "Y", "PY", "PN", "N")),  # no NI
    "3.3": dict(topic="possible dependence of missingness on the true outcome value?",
                condition="If N/PN to 3.2", options=("NA",) + FULL_OPTIONS),
    "3.4": dict(topic="likely dependence of missingness on the true outcome value?",
                condition="If Y/PY/NI to 3.3", options=("NA",) + FULL_OPTIONS),
    "4.1": dict(topic="measurement method inappropriate?", condition="", options=FULL_OPTIONS),
    "4.2": dict(topic="measurement or ascertainment differing between arms?",
                condition="", options=FULL_OPTIONS),
    "4.3": dict(topic="assessor awareness of the arm a participant received?",
                condition="If N/PN/NI to 4.1 and 4.2", options=("NA",) + FULL_OPTIONS),
    "4.4": dict(topic="possible influence of that awareness on the assessment?",
                condition="If Y/PY/NI to 4.3", options=("NA",) + FULL_OPTIONS),
    "4.5": dict(topic="likely influence of that awareness on the assessment?",
                condition="If Y/PY/NI to 4.4", options=("NA",) + FULL_OPTIONS),
    "5.1": dict(topic="analysis followed a plan pre-specified before unblinded data?",
                condition="", options=FULL_OPTIONS),
    "5.2": dict(topic="result selected from multiple eligible outcome measurements?",
                condition="", options=FULL_OPTIONS),
    "5.3": dict(topic="result selected from multiple eligible analyses?",
                condition="", options=FULL_OPTIONS),
}

# Built-in example for --demo: the SKILL.md worked example (12-week mindfulness
# app vs waitlist, self-reported stress, n = 74). Answers are the assessor's
# reading of that illustrative report; the tool turns them into judgements.
DEMO = {
    "study": "Illustrative et al., 2025 — mindfulness app vs waitlist, n = 74",
    "outcome": "self-reported stress at 12 weeks",
    "effect": "assignment",
    "D1": {"1.1": "NI", "1.2": "NI", "1.3": "N",
           "support": "'randomly assigned' stated; no sequence-generation or concealment detail; "
                      "baseline table balanced"},
    "D2": {"2.1": "Y", "2.2": "Y", "2.3": "PN", "2.4": "NA", "2.5": "NA", "2.6": "PY", "2.7": "NA",
           "support": "waitlist control (unblinded); no co-intervention differences reported; "
                      "analysis by randomized group (mITT, missing outcomes excluded)"},
    "D3": {"3.1": "N", "3.2": "N", "3.3": "Y", "3.4": "Y",
           "support": "22% attrition in the app arm vs 4% in control; complete-case only; "
                      "dropout plausibly related to stress level; differential between arms",
           "direction": "Favours experimental"},
    "D4": {"4.1": "PN", "4.2": "N", "4.3": "Y", "4.4": "Y", "4.5": "PN",
           "support": "validated stress scale, same schedule in both arms; participants are the "
                      "assessors and unblinded; influence possible, not shown likely"},
    "D5": {"5.1": "N", "5.2": "Y", "5.3": "PN",
           "support": "no preregistered analysis plan; headline outcome differs from the registry's "
                      "primary outcome",
           "direction": "Favours experimental"},
}


# --- input parsing -----------------------------------------------------------


def parse_answer(qid, raw):
    """Canonicalize one signalling-question answer; ValueError if not an option."""
    if raw is None:
        return None
    s = str(raw).strip().lower()
    code = ANSWER_ALIASES.get(s)
    opts = QUESTIONS[qid]["options"]
    if code is None or code not in opts:
        raise ValueError(
            f"{DOMAIN_OF[qid]} {qid}: {raw!r} is not a RoB 2 response option; use one of "
            f"{'/'.join(opts)}" + (" (RoB 2 offers no 'NI' for 3.2)" if qid == "3.2" and code == "NI" else "")
        )
    return code


def parse_direction(where, raw):
    """Validate an optional direction-of-bias field against the RoB 2 options."""
    if raw is None:
        return None
    lowered = {d.lower(): d for d in DIRECTIONS}
    key = str(raw).strip().lower()
    if key not in lowered:
        raise ValueError(f"{where}: direction {raw!r} is not one of {' / '.join(DIRECTIONS)}")
    return lowered[key]


META_KEYS = ("study", "outcome", "result", "experimental", "comparator", "effect", "direction")


def parse_assessment(data):
    """Turn the input JSON object into a normalized assessment dict.

    Returns {"meta": {...}, "answers": {qid: code|None}, "direction": {...},
    "support": {...}}. Raises ValueError on unknown keys, invalid answers,
    unanswered mandatory questions, or an unsupported effect of interest.
    """
    if not isinstance(data, dict):
        raise ValueError("top level must be a JSON object")
    meta = {}
    answers = {}
    direction = {}
    support = {}
    domain_ids = {d for d, _, _ in DOMAINS}
    for key, value in data.items():
        if key.startswith("_"):
            continue  # comment fields
        up = key.upper()
        if up in domain_ids:
            if not isinstance(value, dict):
                raise ValueError(f"{up} must be an object of signalling-question answers")
            valid_q = {q for d, _, qs in DOMAINS if d == up for q in qs}
            for q, raw in value.items():
                if q.startswith("_"):
                    continue
                if q == "direction":
                    direction[up] = parse_direction(up, raw)
                elif q == "support":
                    support[up] = str(raw)
                elif q in valid_q:
                    answers[q] = parse_answer(q, raw)
                else:
                    raise ValueError(f"{up}: unknown key {q!r} (expected {', '.join(sorted(valid_q))}, direction, support)")
        elif key in QUESTIONS:
            answers[key] = parse_answer(key, value)
        elif key in META_KEYS:
            meta[key] = value
        else:
            raise ValueError(f"unknown top-level key {key!r}")
    effect = str(meta.get("effect", "assignment")).strip().lower()
    if effect not in ("assignment", "assignment to intervention", "itt", "intention-to-treat",
                      "intention to treat"):
        raise ValueError(
            f"effect {meta.get('effect')!r} not supported: only the effect of assignment to "
            "intervention (ITT) algorithms are implemented (adherence/per-protocol uses different "
            "Domain 2 questions and Figure 3)"
        )
    if "direction" in meta:
        meta["direction"] = parse_direction("overall", meta["direction"])
    # Mandatory (unconditional) questions must be answered with a non-NA option.
    for did, _, qs in DOMAINS:
        for q in qs:
            if "NA" in QUESTIONS[q]["options"]:
                continue  # conditional; the algorithm demands it only when reached
            if answers.get(q) in (None, "NA"):
                raise ValueError(f"{did}: signalling question {q} must be answered "
                                 f"({'/'.join(QUESTIONS[q]['options'])})")
    return {"meta": meta, "answers": answers, "direction": direction, "support": support}


def load_file(path):
    """Load the answers JSON from a path, or from stdin when path is '-'."""
    try:
        if path == "-":
            data = json.load(sys.stdin)
        else:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: not valid JSON ({exc})") from None
    return parse_assessment(data)


# --- the algorithms (Figures 1, 2, 4, 5, 7 of the guidance) -----------------


def klass(code):
    """Collapse an answer to the branch label used in the algorithm figures."""
    if code in YES:
        return "Y/PY"
    if code in NO:
        return "N/PN"
    return code  # "NI" or "NA"


class Needs:
    """Fetches answers for a domain and records which questions were consulted."""

    def __init__(self, did, answers):
        self.did = did
        self.answers = answers
        self.consulted = []

    def __call__(self, qid, because=""):
        code = self.answers.get(qid)
        if code in (None, "NA"):
            why = f" because {because}" if because else ""
            cond = QUESTIONS[qid]["condition"]
            hint = f" (RoB 2: '{cond}: ...')" if cond else ""
            raise ValueError(f"{self.did}: {qid} must be answered{why}{hint}; got {code or 'nothing'}")
        self.consulted.append(qid)
        return klass(code)


def judge_d1(need):
    """Figure 1 / Table 4: randomization process."""
    path = []
    k12 = need("1.2")
    if k12 == "N/PN":
        path.append("1.2=N/PN")
        return HIGH, path
    if k12 == "NI":
        path.append("1.2=NI")
        if need("1.3") == "Y/PY":
            path.append("1.3=Y/PY")
            return HIGH, path
        path.append("1.3=N/PN/NI")
        return SC, path
    path.append("1.2=Y/PY")
    if need("1.1") == "N/PN":
        path.append("1.1=N/PN")  # Figure 1; Table 3 'Some concerns' (i.1)+(i.2.1)
        return SC, path
    path.append("1.1=Y/PY/NI")
    if need("1.3") == "Y/PY":
        path.append("1.3=Y/PY")
        return SC, path
    path.append("1.3=N/PN/NI")
    return LOW, path


def judge_d2(need):
    """Figure 2 / Table 6: deviations from intended interventions (assignment).

    Part 1 (2.1-2.5) and Part 2 (2.6-2.7) are judged separately; the domain
    takes the more severe of the two (Table 5/6 'criteria for the domain').
    """
    p1 = []
    k21, k22 = need("2.1"), need("2.2")
    if k21 == "N/PN" and k22 == "N/PN":
        p1.append("2.1&2.2=N/PN")
        j1 = LOW
    else:
        p1.append("2.1|2.2=Y/PY/NI")
        k23 = need("2.3", "2.1 or 2.2 is Y/PY/NI")
        if k23 == "N/PN":
            p1.append("2.3=N/PN")
            j1 = LOW
        elif k23 == "NI":
            p1.append("2.3=NI")
            j1 = SC
        else:
            p1.append("2.3=Y/PY")
            if need("2.4", "2.3 is Y/PY") == "N/PN":
                p1.append("2.4=N/PN")
                j1 = SC
            else:
                p1.append("2.4=Y/PY/NI")
                if need("2.5", "2.4 is Y/PY/NI") == "Y/PY":
                    p1.append("2.5=Y/PY")
                    j1 = SC
                else:
                    p1.append("2.5=N/PN/NI")
                    j1 = HIGH
    p2 = []
    if need("2.6") == "Y/PY":
        p2.append("2.6=Y/PY")
        j2 = LOW
    else:
        p2.append("2.6=N/PN/NI")
        if need("2.7", "2.6 is N/PN/NI") == "N/PN":
            p2.append("2.7=N/PN")
            j2 = SC
        else:
            p2.append("2.7=Y/PY/NI")
            j2 = HIGH
    judgement = max(j1, j2, key=SEVERITY.get)
    path = ["Part 1: " + " → ".join(p1) + f" = {j1}", "Part 2: " + " → ".join(p2) + f" = {j2}"]
    return judgement, path


def judge_d3(need):
    """Figure 4 / Table 10: missing outcome data."""
    path = []
    if need("3.1") == "Y/PY":
        path.append("3.1=Y/PY")
        return LOW, path
    path.append("3.1=N/PN/NI")
    if need("3.2", "3.1 is N/PN/NI") == "Y/PY":
        path.append("3.2=Y/PY")
        return LOW, path
    path.append("3.2=N/PN")
    if need("3.3", "3.2 is N/PN") == "N/PN":
        path.append("3.3=N/PN")
        return LOW, path
    path.append("3.3=Y/PY/NI")
    if need("3.4", "3.3 is Y/PY/NI") == "N/PN":
        path.append("3.4=N/PN")
        return SC, path
    path.append("3.4=Y/PY/NI")
    return HIGH, path


def judge_d4(need):
    """Figure 5 / Table 12: measurement of the outcome."""
    path = []
    if need("4.1") == "Y/PY":
        path.append("4.1=Y/PY")
        return HIGH, path
    path.append("4.1=N/PN/NI")
    k42 = need("4.2")
    if k42 == "Y/PY":
        path.append("4.2=Y/PY")
        return HIGH, path
    # With 4.2 = N/PN the unaware / not-influenceable branches end at Low;
    # with 4.2 = NI the same branches end at Some concerns (Table 11 (ii)).
    floor = LOW if k42 == "N/PN" else SC
    path.append("4.2=" + k42)
    if need("4.3", "4.1 and 4.2 are not Y/PY") == "N/PN":
        path.append("4.3=N/PN")
        return floor, path
    path.append("4.3=Y/PY/NI")
    if need("4.4", "4.3 is Y/PY/NI") == "N/PN":
        path.append("4.4=N/PN")
        return floor, path
    path.append("4.4=Y/PY/NI")
    if need("4.5", "4.4 is Y/PY/NI") == "N/PN":
        path.append("4.5=N/PN")
        return SC, path
    path.append("4.5=Y/PY/NI")
    return HIGH, path


def judge_d5(need):
    """Figure 7 / Table 14: selection of the reported result."""
    path = []
    k52, k53 = need("5.2"), need("5.3")
    if k52 == "Y/PY" or k53 == "Y/PY":
        path.append("5.2|5.3=Y/PY")
        return HIGH, path
    if k52 == "NI" or k53 == "NI":
        path.append("5.2|5.3=NI (neither Y/PY)")
        return SC, path
    path.append("5.2&5.3=N/PN")
    if need("5.1") == "Y/PY":
        path.append("5.1=Y/PY")
        return LOW, path
    path.append("5.1=N/PN/NI")
    return SC, path


ALGORITHMS = {"D1": judge_d1, "D2": judge_d2, "D3": judge_d3, "D4": judge_d4, "D5": judge_d5}


def judge_domains(answers):
    """Run all five domain algorithms. Returns list of per-domain result dicts."""
    results = []
    for did, name, qs in DOMAINS:
        need = Needs(did, answers)
        judgement, path = ALGORITHMS[did](need)
        results.append({
            "id": did,
            "name": name,
            "answers": {q: (answers.get(q) or "NA") for q in qs},
            "consulted": list(need.consulted),
            "judgement": judgement,
            "path": path,
        })
    return results


def judge_overall(domain_results, sc_high_threshold):
    """Table 1 of the guidance. Returns dict with judgement, rule, counts."""
    highs = [r["id"] for r in domain_results if r["judgement"] == HIGH]
    scs = [r["id"] for r in domain_results if r["judgement"] == SC]
    escalated = False
    if highs:
        judgement = HIGH
        rule = f"at least one domain at High risk of bias ({', '.join(highs)})"
    elif not scs:
        judgement = LOW
        rule = "low risk of bias for all domains"
    elif len(scs) >= sc_high_threshold:
        judgement = HIGH
        escalated = True
        rule = (f"some concerns in {len(scs)} domains ({', '.join(scs)}) reaches "
                f"--sc-high-threshold {sc_high_threshold} — this skill's own mechanical stand-in "
                "for RoB 2's 'some concerns for multiple domains in a way that substantially lowers "
                "confidence in the result', which the instrument leaves to review-author judgement "
                "and does not threshold; lower/raise the threshold to override")
    else:
        judgement = SC
        rule = f"some concerns in at least one domain ({', '.join(scs)}), no domain at High risk"
    return {
        "judgement": judgement,
        "rule": rule,
        "high_domains": highs,
        "some_concerns_domains": scs,
        "some_concerns_count": len(scs),
        "sc_high_threshold": sc_high_threshold,
        "escalated_by_threshold": escalated,
    }


def assess(assessment, sc_high_threshold=3):
    """Full RoB 2 assessment from a parsed assessment dict."""
    domains = judge_domains(assessment["answers"])
    for r in domains:
        if r["id"] in assessment["direction"]:
            r["direction"] = assessment["direction"][r["id"]]
        if r["id"] in assessment["support"]:
            r["support"] = assessment["support"][r["id"]]
    overall = judge_overall(domains, sc_high_threshold)
    if "direction" in assessment["meta"]:
        overall["direction"] = assessment["meta"]["direction"]
    meta = {k: assessment["meta"][k] for k in META_KEYS if k in assessment["meta"] and k != "direction"}
    return {
        "tool": "RoB 2 (version 22 August 2019), " + EFFECT,
        "source": {"title": SOURCE_TITLE, "url": SOURCE_URL, "paper": SOURCE_PAPER},
        "meta": meta,
        "domains": domains,
        "overall": overall,
    }


# --- CLI ---------------------------------------------------------------------


def print_judgement(result):
    meta = result["meta"]
    print(f"RoB 2 judgement — {EFFECT}")
    if meta.get("study") or meta.get("outcome"):
        print(f"Study: {meta.get('study', '?')}   Outcome: {meta.get('outcome', '?')}")
    for extra in ("experimental", "comparator", "result"):
        if meta.get(extra):
            print(f"{extra.capitalize()}: {meta[extra]}")
    for r in result["domains"]:
        ans = " ".join(f"{q}={a}" for q, a in r["answers"].items())
        print(f"{r['id']}: {ans} → {r['judgement']}")
        joiner = " | " if r["id"] == "D2" else " → "
        print(f"    [{DOMAIN_SHORT[r['id']]}] via {joiner.join(r['path'])}")
        if r.get("direction"):
            print(f"    direction of bias (assessor-supplied): {r['direction']}")
    o = result["overall"]
    print(f"Overall: {JUDGEMENT_LONG[o['judgement']]}   (Table 1: {o['rule']})")
    n = o["some_concerns_count"]
    if n and not o["escalated_by_threshold"]:
        print(f"Some concerns in {n} domain(s): {', '.join(o['some_concerns_domains'])}. "
              "RoB 2 lets review authors judge multiple 'Some concerns' as High overall when they "
              f"substantially lower confidence; --sc-high-threshold={o['sc_high_threshold']} (this "
              "skill's addition, not part of RoB 2) not reached.")
    if o.get("direction"):
        print(f"Overall direction of bias (assessor-supplied): {o['direction']}")
    summary = " · ".join(f"{r['id']}={r['judgement']}" for r in result["domains"])
    print(f"Summary: {summary} → Overall {o['judgement']}")


def cmd_judge(args):
    if args.demo:
        assessment = parse_assessment(DEMO)
    elif args.file:
        assessment = load_file(args.file)
    else:
        raise ValueError("pass --file PATH (or '-' for stdin) or --demo")
    if args.sc_high_threshold < 2:
        raise ValueError("--sc-high-threshold must be >= 2 ('multiple domains'); use a value > 5 to disable")
    result = assess(assessment, args.sc_high_threshold)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_judgement(result)
    return 0


def questions_list():
    out = []
    for did, name, qs in DOMAINS:
        for q in qs:
            spec = QUESTIONS[q]
            out.append({"id": q, "domain": did, "domain_name": name,
                        "condition": spec["condition"], "topic": spec["topic"],
                        "options": "/".join(spec["options"]),
                        "wording": "not reproduced — read it at " + WORDING_URL})
    return out


def cmd_questions(args):
    if args.template:
        # "_"-prefixed keys are ignored by the parser, so the notice travels
        # with every answers.json produced from this template.
        template = {"_wording": WORDING_NOTICE,
                    "study": "", "outcome": "", "effect": "assignment"}
        for did, _, qs in DOMAINS:
            block = {q: "" for q in qs}
            block["direction"] = "NA"
            block["support"] = ""
            template[did] = block
        print(json.dumps(template, indent=2))
        return 0
    if args.json:
        print(json.dumps({"wording_notice": WORDING_NOTICE, "wording_url": WORDING_URL,
                          "source": {"title": SOURCE_TITLE, "url": SOURCE_URL, "paper": SOURCE_PAPER,
                                     "questions_located_in": QUESTION_LOCATOR},
                          "effect": EFFECT, "answers": "Y/PY/PN/N/NI (+NA for conditional questions)",
                          "judgements": [LOW, SC, HIGH], "directions": list(DIRECTIONS),
                          "questions": questions_list()}, indent=2, ensure_ascii=False))
        return 0
    print(f"RoB 2 signalling questions — {EFFECT}")
    print("=" * 96)
    print(textwrap.fill(WORDING_NOTICE, width=96))
    print("=" * 96)
    print(f"Source: {SOURCE_TITLE}")
    print(f"        questions: {QUESTION_LOCATOR} — {SOURCE_URL}")
    print(f"        {SOURCE_PAPER}")
    print("Answers: Y = Yes, PY = Probably yes, PN = Probably no, N = No, NI = No information; "
          "NA = Not applicable (conditional questions only)")
    print("Each line below: question ID, [branching condition], topic covered, response options.")
    for did, name, qs in DOMAINS:
        print()
        print(f"Domain {did[1]}: {name}")
        for q in qs:
            spec = QUESTIONS[q]
            cond = spec["condition"]
            head = f"  {q}  [{cond}] {spec['topic']}" if cond else f"  {q}  {spec['topic']}"
            body = textwrap.fill(head, width=96, subsequent_indent="       ")
            print(f"{body}  [{'/'.join(spec['options'])}]")
    print()
    print("5.2 and 5.3 share one printed stem in the source; read the two together there.")
    print("Optional per domain and overall — direction of bias: " + " / ".join(DIRECTIONS))
    print("Judgements: Low / Some concerns / High per domain and overall (Table 1).")
    print()
    print(textwrap.fill("Before answering: fetch " + WORDING_URL + " and work from the published "
                        "wording. Answers given against the topic labels above are not a RoB 2 "
                        "assessment.", width=96))
    return 0


# --- selftest ----------------------------------------------------------------


def _mk(**flat):
    """Build a complete assessment from flat answers, defaulting the rest to a
    Low-risk profile so a single domain can be exercised in isolation."""
    base = {"1.1": "Y", "1.2": "Y", "1.3": "N",
            "2.1": "N", "2.2": "N", "2.6": "Y",
            "3.1": "Y",
            "4.1": "N", "4.2": "N", "4.3": "N",
            "5.1": "Y", "5.2": "N", "5.3": "N"}
    base.update(flat)
    return parse_assessment(base)


def run_selftest():
    """Every expected judgement below is read off the published algorithm figures
    and mapping tables (Tables 4, 6, 10, 12, 14; Table 1) — not from memory."""
    checks = []

    def check(name, got, want):
        ok = got == want
        checks.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got!r}, expected {want!r}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    def dom(did, **flat):
        res = judge_domains(_mk(**flat)["answers"])
        return next(r["judgement"] for r in res if r["id"] == did)

    def rejects(name, fn):
        try:
            fn()
        except ValueError as exc:
            checks.append(True)
            print(f"PASS  {name}: rejected ({str(exc)[:60]}...)")
            return
        print(f"FAIL  {name}: accepted invalid input", file=sys.stderr)
        sys.exit(1)

    # Domain 1 — Table 4 rows + Figure 1 branch 1.1=N/PN (Table 3 'Some concerns' i)
    check("D1 Y,Y,N -> Low (T4 r1)", dom("D1", **{"1.1": "Y", "1.2": "Y", "1.3": "N"}), LOW)
    check("D1 NI,PY,PN -> Low (T4 r1)", dom("D1", **{"1.1": "NI", "1.2": "PY", "1.3": "PN"}), LOW)
    check("D1 Y,Y,Y -> Some concerns (T4 r2)", dom("D1", **{"1.1": "Y", "1.2": "Y", "1.3": "Y"}), SC)
    check("D1 N,Y,Y -> Some concerns (T4 r3)", dom("D1", **{"1.1": "N", "1.2": "Y", "1.3": "Y"}), SC)
    check("D1 N,Y,N -> Some concerns (Fig 1)", dom("D1", **{"1.1": "N", "1.2": "Y", "1.3": "N"}), SC)
    check("D1 NI,NI,N -> Some concerns (T4 r4)", dom("D1", **{"1.1": "NI", "1.2": "NI", "1.3": "N"}), SC)
    check("D1 Y,NI,Y -> High (T4 r5)", dom("D1", **{"1.1": "Y", "1.2": "NI", "1.3": "Y"}), HIGH)
    check("D1 N,N,N -> High (T4 r6)", dom("D1", **{"1.1": "N", "1.2": "N", "1.3": "N"}), HIGH)
    check("D1 Y,PN,N -> High (T4 r6)", dom("D1", **{"1.1": "Y", "1.2": "PN", "1.3": "N"}), HIGH)

    # Domain 2 — Table 6 (assignment): Part 1 rows, Part 2 rows, combination
    check("D2 both unaware, 2.6=Y -> Low (T6 P1 r1)", dom("D2", **{"2.1": "N", "2.2": "PN", "2.6": "Y"}), LOW)
    check("D2 aware, 2.3=N -> Low (T6 P1 r2)", dom("D2", **{"2.1": "Y", "2.2": "N", "2.3": "N", "2.6": "Y"}), LOW)
    check("D2 aware, 2.3=NI -> Some concerns (T6 P1 r3)", dom("D2", **{"2.1": "Y", "2.2": "Y", "2.3": "NI", "2.6": "Y"}), SC)
    check("D2 2.3=Y,2.4=N -> Some concerns (T6 P1 r4)", dom("D2", **{"2.1": "NI", "2.2": "N", "2.3": "Y", "2.4": "N", "2.6": "Y"}), SC)
    check("D2 2.3=Y,2.4=Y,2.5=Y -> Some concerns (T6 P1 r5)", dom("D2", **{"2.1": "Y", "2.2": "Y", "2.3": "Y", "2.4": "Y", "2.5": "Y", "2.6": "Y"}), SC)
    check("D2 2.3=Y,2.4=NI,2.5=N -> High (T6 P1 r6)", dom("D2", **{"2.1": "Y", "2.2": "Y", "2.3": "Y", "2.4": "NI", "2.5": "N", "2.6": "Y"}), HIGH)
    check("D2 2.6=N,2.7=N -> Some concerns (T6 P2 r2)", dom("D2", **{"2.1": "N", "2.2": "N", "2.6": "N", "2.7": "N"}), SC)
    check("D2 2.6=NI,2.7=NI -> High (T6 P2 r3)", dom("D2", **{"2.1": "N", "2.2": "N", "2.6": "NI", "2.7": "NI"}), HIGH)
    check("D2 P1 SC + P2 SC -> Some concerns", dom("D2", **{"2.1": "Y", "2.2": "Y", "2.3": "NI", "2.6": "N", "2.7": "N"}), SC)
    check("D2 P1 SC + P2 High -> High", dom("D2", **{"2.1": "Y", "2.2": "Y", "2.3": "NI", "2.6": "N", "2.7": "Y"}), HIGH)

    # Domain 3 — Table 10 rows
    check("D3 3.1=Y -> Low (T10 r1)", dom("D3", **{"3.1": "Y"}), LOW)
    check("D3 3.1=N,3.2=Y -> Low (T10 r2)", dom("D3", **{"3.1": "N", "3.2": "Y"}), LOW)
    check("D3 3.1=NI,3.2=N,3.3=N -> Low (T10 r3)", dom("D3", **{"3.1": "NI", "3.2": "N", "3.3": "N"}), LOW)
    check("D3 N,PN,NI,N -> Some concerns (T10 r4)", dom("D3", **{"3.1": "N", "3.2": "PN", "3.3": "NI", "3.4": "N"}), SC)
    check("D3 N,N,Y,Y -> High (T10 r5)", dom("D3", **{"3.1": "N", "3.2": "N", "3.3": "Y", "3.4": "Y"}), HIGH)
    check("D3 PN,N,Y,NI -> High (T10 r5)", dom("D3", **{"3.1": "PN", "3.2": "N", "3.3": "Y", "3.4": "NI"}), HIGH)

    # Domain 4 — Table 12 rows
    check("D4 N,N,N -> Low (T12 r1)", dom("D4", **{"4.1": "N", "4.2": "N", "4.3": "N"}), LOW)
    check("D4 NI,PN,Y,N -> Low (T12 r2)", dom("D4", **{"4.1": "NI", "4.2": "PN", "4.3": "Y", "4.4": "N"}), LOW)
    check("D4 N,N,Y,Y,N -> Some concerns (T12 r3)", dom("D4", **{"4.1": "N", "4.2": "N", "4.3": "Y", "4.4": "Y", "4.5": "N"}), SC)
    check("D4 N,N,NI,NI,NI -> High (T12 r4)", dom("D4", **{"4.1": "N", "4.2": "N", "4.3": "NI", "4.4": "NI", "4.5": "NI"}), HIGH)
    check("D4 N,NI,N -> Some concerns (T12 r5)", dom("D4", **{"4.1": "N", "4.2": "NI", "4.3": "N"}), SC)
    check("D4 N,NI,Y,N -> Some concerns (T12 r6)", dom("D4", **{"4.1": "N", "4.2": "NI", "4.3": "Y", "4.4": "N"}), SC)
    check("D4 N,NI,Y,Y,PN -> Some concerns (T12 r7)", dom("D4", **{"4.1": "N", "4.2": "NI", "4.3": "Y", "4.4": "Y", "4.5": "PN"}), SC)
    check("D4 N,NI,Y,Y,Y -> High (T12 r8)", dom("D4", **{"4.1": "N", "4.2": "NI", "4.3": "Y", "4.4": "Y", "4.5": "Y"}), HIGH)
    check("D4 4.1=Y -> High (T12 r9)", dom("D4", **{"4.1": "Y", "4.2": "N", "4.3": "N"}), HIGH)
    check("D4 4.2=Y -> High (T12 r10)", dom("D4", **{"4.1": "N", "4.2": "Y", "4.3": "N"}), HIGH)

    # Domain 5 — Table 14 rows
    check("D5 Y,N,N -> Low (T14 r1)", dom("D5", **{"5.1": "Y", "5.2": "N", "5.3": "N"}), LOW)
    check("D5 NI,N,PN -> Some concerns (T14 r2)", dom("D5", **{"5.1": "NI", "5.2": "N", "5.3": "PN"}), SC)
    check("D5 Y,N,NI -> Some concerns (T14 r3)", dom("D5", **{"5.1": "Y", "5.2": "N", "5.3": "NI"}), SC)
    check("D5 Y,NI,N -> Some concerns (T14 r4)", dom("D5", **{"5.1": "Y", "5.2": "NI", "5.3": "N"}), SC)
    check("D5 N,NI,NI -> Some concerns (T14 r5)", dom("D5", **{"5.1": "N", "5.2": "NI", "5.3": "NI"}), SC)
    check("D5 Y,Y,N -> High (T14 r6)", dom("D5", **{"5.1": "Y", "5.2": "Y", "5.3": "N"}), HIGH)
    check("D5 Y,N,PY -> High (T14 r6)", dom("D5", **{"5.1": "Y", "5.2": "N", "5.3": "PY"}), HIGH)

    # Overall — Table 1
    def overall(flat, threshold=3):
        return judge_overall(judge_domains(_mk(**flat)["answers"]), threshold)

    check("overall all Low -> Low", overall({})["judgement"], LOW)
    check("overall one SC -> Some concerns", overall({"5.1": "N"})["judgement"], SC)
    check("overall one High -> High", overall({"3.1": "N", "3.2": "N", "3.3": "Y", "3.4": "Y"})["judgement"], HIGH)
    three_sc = {"1.2": "NI", "5.1": "N", "4.2": "NI"}  # D1, D5, D4 at Some concerns
    check("overall 3x SC, threshold 3 -> High (escalated)", overall(three_sc)["judgement"], HIGH)
    check("overall 3x SC escalation flagged", overall(three_sc)["escalated_by_threshold"], True)
    check("overall 3x SC, threshold 4 -> Some concerns", overall(three_sc, 4)["judgement"], SC)
    check("overall 2x SC, threshold 3 -> Some concerns", overall({"1.2": "NI", "5.1": "N"})["judgement"], SC)
    check("overall SC count reported", overall(three_sc)["some_concerns_count"], 3)

    # Demo reproduces the SKILL.md worked example
    demo = assess(parse_assessment(DEMO))
    check("demo domain judgements", [r["judgement"] for r in demo["domains"]], [SC, LOW, HIGH, SC, HIGH])
    check("demo overall", demo["overall"]["judgement"], HIGH)
    check("demo D3 direction passed through", demo["domains"][2]["direction"], "Favours experimental")

    # Input handling
    check("full-word answers accepted", parse_answer("1.1", "Probably yes"), "PY")
    rejects("invalid token 'maybe'", lambda: _mk(**{"1.1": "maybe"}))
    rejects("3.2=NI (no such option)", lambda: _mk(**{"3.1": "N", "3.2": "NI"}))
    rejects("missing conditional 3.2 when 3.1=N", lambda: judge_domains(_mk(**{"3.1": "N"})["answers"]))
    rejects("missing mandatory 1.2", lambda: parse_assessment({"1.1": "Y", "1.3": "N", "2.1": "N", "2.2": "N",
                                                               "2.6": "Y", "3.1": "Y", "4.1": "N", "4.2": "N",
                                                               "4.3": "N", "5.1": "Y", "5.2": "N", "5.3": "N"}))
    rejects("effect 'adherence' unsupported", lambda: parse_assessment(dict(DEMO, effect="adherence")))
    rejects("unknown key", lambda: parse_assessment(dict(DEMO, D6={"6.1": "Y"})))
    rejects("bad direction", lambda: parse_assessment(dict(DEMO, direction="sideways")))

    # Question inventory and the licensing guard: IDs and response-option
    # constraints are kept; the instrument's wording is not reproduced. Assert on
    # IDs, options and judgements — never on question text.
    listed = questions_list()
    check("22 signalling question IDs listed", [q["id"] for q in listed],
          [q for _, _, qs in DOMAINS for q in qs])
    check("3.2 offers no 'No information'", "NI" in QUESTIONS["3.2"]["options"], False)
    check("every question carries a topic descriptor",
          sorted(q for q in QUESTIONS if not QUESTIONS[q].get("topic")), [])
    check("topics are short labels, not reproduced questions",
          max(len(QUESTIONS[q]["topic"]) for q in QUESTIONS) <= 80, True)
    check("no topic is an instrument question sentence",
          sorted({QUESTIONS[q]["topic"].split()[0].lower() for q in QUESTIONS}
                 & {"was", "were", "is", "are", "did", "could", "do", "does"}), [])
    check("every listed question points at the source",
          sorted({WORDING_URL in q["wording"] for q in listed}), [True])

    print(f"ALL {len(checks)} CHECKS PASSED")
    print("selftest OK")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Cochrane RoB 2 (22 Aug 2019) domain and overall risk-of-bias judgements "
        "from signalling-question answers — effect of assignment to intervention.",
    )
    parser.add_argument("--selftest", action="store_true", help="run built-in checks against the published algorithm tables and exit")
    parser.add_argument("--demo", dest="demo_top", action="store_true", help="same as: judge --demo")
    sub = parser.add_subparsers(dest="command")
    pj = sub.add_parser("judge", help="derive per-domain and overall judgements from answers")
    pj.add_argument("--file", help="JSON file of signalling-question answers ('-' = stdin)")
    pj.add_argument("--demo", action="store_true", help="use the built-in SKILL.md worked example")
    pj.add_argument("--json", action="store_true", help="emit JSON instead of text")
    pj.add_argument("--sc-high-threshold", type=int, default=3, metavar="N",
                    help="THIS SKILL'S ADDITION, not part of RoB 2: escalate overall to High when "
                         ">= N domains are 'Some concerns' and none is High (RoB 2 Table 1 leaves "
                         "the escalation to review-author judgement; default 3; > 5 disables)")
    pq = sub.add_parser("questions", help="print the signalling-question IDs, topics and response "
                                          "options (wording is not reproduced — read it at "
                                          + WORDING_URL + ")")
    pq.add_argument("--json", action="store_true", help="emit the questions as JSON")
    pq.add_argument("--template", action="store_true", help="emit an empty answers.json to fill in")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo_top and not args.command:
        args.command, args.demo, args.file, args.json, args.sc_high_threshold = "judge", True, None, False, 3
    if not args.command:
        parser.print_help()
        return 1
    try:
        if args.command == "judge":
            return cmd_judge(args)
        return cmd_questions(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
