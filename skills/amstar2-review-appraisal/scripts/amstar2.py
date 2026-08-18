#!/usr/bin/env python3
"""amstar2.py — AMSTAR 2 item recording and overall confidence rating for systematic reviews.

Implements, mechanically, the published AMSTAR 2 instrument (Shea et al., BMJ 2017):

  * the 16 items and their response options — Yes / No for every item; "Partial Yes"
    only for items 2, 4, 7, 8, 9; "No meta-analysis conducted" only for items 11, 12, 15
    (checklist, amstar.ca);
  * the seven critical domains — items 2, 4, 7, 9, 11, 13, 15 (Box 1) — which the
    appraiser may add to or substitute (`critical_override`; paper: "appraisers may add
    or substitute other critical domains");
  * the overall confidence rating scheme (Box 2):
        High            at most one non-critical weakness, and no critical flaw
        Moderate        two or more non-critical weaknesses, still no critical flaw
        Low             exactly one critical flaw, whatever the weakness count
        Critically low  two or more critical flaws, whatever the weakness count
    The Box 2 footnote — accumulating non-critical weaknesses may warrant moving Moderate
    down to Low — is advisory; it applies only when --moderate-to-low N is given, and says so.

Response -> flaw/weakness mapping. A "No" is unambiguous in the paper ("a 'Yes' answer
denotes a positive result"; missing information "should be rated as a 'No'"): a No in a
critical domain is a critical flaw, a No elsewhere is a non-critical weakness. "No
meta-analysis conducted" is not a weakness — the item does not apply ("If a meta-analysis
was not performed, the item covering ... meta-analytical methods (item 11) will not apply").
The paper introduces "Partial Yes" "to identify partial adherence to the standard" but does
not state how it counts towards Box 2 — De Santis et al. (2023) list this as a decision the
appraisal team must pre-specify. The tool therefore prints the convention with every
rating and lets you choose it:
    --partial-yes weakness   (default) a Partial Yes is a non-critical weakness wherever it is
    --partial-yes flaw       a Partial Yes in a critical domain is a critical flaw (strict)
    --partial-yes met        a Partial Yes counts as adherence (lenient; only to reproduce
                             ratings made under that convention — always report it)
AMSTAR 2 is not a score: item ratings are never summed ("We strongly recommend that
individual item ratings are not combined to create an overall score").

Sources and licence:
  Shea BJ, Reeves BC, Wells G, Thuku M, Hamel C, Moran J, Moher D, Tugwell P, Welch V,
  Kristjansson E, Henry DA. AMSTAR 2: a critical appraisal tool for systematic reviews that
  include randomised or non-randomised studies of healthcare interventions, or both.
  BMJ 2017;358:j4008. doi:10.1136/bmj.j4008 — licensed CC BY 4.0,
  https://creativecommons.org/licenses/by/4.0/. The 16 item questions and the Box 1
  critical-domain list are reused from that paper under CC BY 4.0 and have been MODIFIED:
  condensed and reformatted, with short labels and the Y/PY/N/NMA response codes added here.
  The "For Yes"/"For Partial Yes" criteria and the overall-confidence descriptions below are
  NOT reproduced from the separately copyrighted AMSTAR 2 checklist
  (https://amstar.ca/Amstar_Checklist.php, https://amstar.ca/docs/AMSTAR-2.pdf); they are
  restatements, written for this tool, of the same operational requirements. Consult the
  checklist itself when an appraisal must be defended verbatim. Neither the AMSTAR 2 authors
  nor BMJ endorse this tool.
  De Santis K, Pieper D, Lorenz R, Wegewitz U, Siemens W, Matthias K. User experience of
  applying AMSTAR 2 to appraise systematic reviews of healthcare interventions: a commentary.
  BMC Med Res Methodol 2023;23:63. doi:10.1186/s12874-023-01879-8  (Partial Yes weighting is
  undefined)

Input JSON (rate --file):
  {"review": "...", "question": "P ... | I ... | C ... | O ...",
   "items": {"1": "Y", "2": "PY", "3": "N", ..., "11": "NMA", ..., "16": "Y"},   # all 16
   "notes": {"2": "where the evidence is (section / quote)", ...},               # optional
   "critical_override": [2, 3, 4, 7, 9, 11, 13, 15],   # optional: the full list to use
   "partial_yes": "weakness"}                            # optional: weakness | flaw | met
  An item value may also be {"response": "PY", "note": "..."}; items 9 and 11 may be given
  per design, {"RCT": "Y", "NRSI": "PY"} — the item takes the weaker applicable panel.
  Long forms are accepted: "Yes", "Partial Yes", "No", "No meta-analysis conducted".

Stdlib only. Python 3.9+. Offline. Deterministic.

Usage:
    python3 amstar2.py rate --file answers.json [--json] [--partial-yes weakness|flaw|met]
                            [--critical 2,4,7,9,11,13,15] [--moderate-to-low N]
    python3 amstar2.py rate --demo                 # SKILL.md worked example
    python3 amstar2.py items [--json | --template] # 16 items, options, criteria, citation
    python3 amstar2.py --selftest
Exit codes: 0 rating produced (whatever it is); 1 invalid input or usage.
"""

import argparse
import json
import sys
import textwrap

# --- the instrument as published --------------------------------------------

SOURCE_PAPER = ("Shea BJ, Reeves BC, Wells G, et al. AMSTAR 2: a critical appraisal tool for "
                "systematic reviews that include randomised or non-randomised studies of "
                "healthcare interventions, or both. BMJ 2017;358:j4008. doi:10.1136/bmj.j4008")
SOURCE_LICENCE = ("Item questions and Box 1 reused from the paper under CC BY 4.0 "
                  "(https://creativecommons.org/licenses/by/4.0/), modified: condensed and "
                  "reformatted, labels and response codes added. Criteria and rating "
                  "descriptions are this tool's own restatements, not the checklist's wording.")
SOURCE_CHECKLIST = ("AMSTAR 2 checklist (authoritative wording; separately copyrighted) — "
                    "https://amstar.ca/Amstar_Checklist.php (PDF: https://amstar.ca/docs/AMSTAR-2.pdf)")
SOURCE_PARTIAL = ("De Santis K, Pieper D, Lorenz R, Wegewitz U, Siemens W, Matthias K. User experience "
                  "of applying AMSTAR 2 ...: a commentary. BMC Med Res Methodol 2023;23:63. "
                  "doi:10.1186/s12874-023-01879-8")

Y, PY, N, NMA = "Y", "PY", "N", "NMA"
LABEL = {Y: "Yes", PY: "Partial Yes", N: "No", NMA: "No meta-analysis conducted"}
# Worst-first order used when several design panels answer one item.
SEVERITY = {N: 0, PY: 1, Y: 2, NMA: 3}

DEFAULT_CRITICAL = (2, 4, 7, 9, 11, 13, 15)          # Box 1
PARTIAL_YES_ITEMS = (2, 4, 7, 8, 9)                   # checklist response options
NMA_ITEMS = (11, 12, 15)                              # checklist response options
CONVENTIONS = ("weakness", "flaw", "met")

HIGH, MODERATE, LOW, CRIT_LOW = "High", "Moderate", "Low", "Critically low"
# Rule text and reading of each rating, restated in this tool's own words (see SOURCE_LICENCE).
BOX2 = {
    HIGH: ("At most one non-critical weakness, and no critical flaw",
           "the review can be read as a dependable and complete account of what the available "
           "studies bearing on the question actually found"),
    MODERATE: ("Two or more non-critical weaknesses, still no critical flaw",
               "the review carries more than one weakness but nothing critical, so its account of "
               "the studies it did include may still be dependable"),
    LOW: ("Exactly one critical flaw, whatever the number of non-critical weaknesses",
          "one critical flaw is present, so the review may fail to account dependably or "
          "completely for the available studies bearing on the question"),
    CRIT_LOW: ("Two or more critical flaws, whatever the number of non-critical weaknesses",
               "two or more critical flaws are present, so the review must not be leaned on as a "
               "dependable or complete account of the available studies"),
}
BOX2_FOOTNOTE = ("Box 2 footnote: where non-critical weaknesses accumulate they may erode confidence "
                 "far enough to warrant moving the overall appraisal down from Moderate to Low")

# (number, short label, full item question, criteria text). The item questions are reused from
# the BMJ paper under CC BY 4.0, condensed (see SOURCE_LICENCE); the criteria text restates the
# checklist's "For Partial Yes" / "For Yes" requirements in this tool's own words.
ITEMS = [
    (1, "Research question and inclusion criteria include PICO",
     "Did the research questions and inclusion criteria for the review include the components of PICO?",
     "Yes requires all four PICO elements to be stated: who was studied, what was done to them, what "
     "that was compared against, and which outcomes were measured. Naming the follow-up window as well "
     "is encouraged but not required."),
    (2, "Protocol established before conduct; deviations justified",
     "Did the report of the review contain an explicit statement that the review methods were established "
     "prior to the conduct of the review and did the report justify any significant deviations from the protocol?",
     "Partial Yes requires the report to say a written protocol or plan existed beforehand and to show it "
     "covered every one of: the review question(s); how the literature would be searched; what would be "
     "included and excluded; how risk of bias would be judged. Yes requires all of that, plus the protocol "
     "to have been registered and to have additionally specified how results would be pooled or synthesised "
     "where that applies, how the causes of heterogeneity would be explored, and any departure from the plan "
     "to be explained."),
    (3, "Selection of study designs explained",
     "Did the review authors explain their selection of the study designs for inclusion in the review?",
     "Yes requires a stated reason for whichever design choice was made — admitting randomised trials only, "
     "admitting non-randomised studies only, or admitting both."),
    (4, "Comprehensive literature search strategy",
     "Did the review authors use a comprehensive literature search strategy?",
     "Partial Yes requires all three of: two or more databases suited to the question were searched; the search "
     "terms or the full strategy are reported; and any restriction on what could be retrieved (language, date, "
     "publication status) is defended. Yes requires those three and all of the following as well: the "
     "bibliographies of the included papers were checked; trial or study registers were queried; subject-matter "
     "experts were consulted; grey literature was sought wherever it is pertinent; and no more than 24 months "
     "separate the search from the finished review."),
    (5, "Study selection in duplicate",
     "Did the review authors perform study selection in duplicate?",
     "Yes by either route: two or more reviewers screened eligibility independently and then settled on a common "
     "include list; or two reviewers screened a subset, concurred on at least 80 percent of it, and a single "
     "reviewer handled the remainder."),
    (6, "Data extraction in duplicate",
     "Did the review authors perform data extraction in duplicate?",
     "Yes by either route: two or more reviewers reached agreement on the data pulled from the included studies; "
     "or two reviewers extracted from a subset with at least 80 percent concordance and one reviewer extracted "
     "the remainder."),
    (7, "Excluded studies listed and exclusions justified",
     "Did the review authors provide a list of excluded studies and justify the exclusions?",
     "Partial Yes requires the report to name every candidate study that was read at full text and then "
     "rejected. Yes additionally requires a stated reason for rejecting each of those studies; counts alone in "
     "a flow diagram do not reach either level."),
    (8, "Included studies described in adequate detail",
     "Did the review authors describe the included studies in adequate detail?",
     "Partial Yes requires every included study to be characterised on all of: population, intervention, "
     "comparator, outcomes and research design. Yes requires that characterisation to go further on all counts "
     "— population, intervention and comparator described in depth (dose or intensity wherever that matters), "
     "plus the setting in which the study ran and how long participants were followed."),
    (9, "Satisfactory technique for assessing risk of bias (RoB) in included studies",
     "Did the review authors use a satisfactory technique for assessing the risk of bias (RoB) in individual "
     "studies that were included in the review?",
     "RCTs — Partial Yes requires the review to have appraised at least whether allocation was concealed and "
     "whether patients and outcome assessors were blinded (blinding may be waived for outcomes that knowledge "
     "of the arm cannot sway, such as death from any cause). Yes requires two further sources of bias to have "
     "been appraised as well: whether the allocation sequence was genuinely random, and whether the reported "
     "result was picked out of several measurements or analyses of one specified outcome. NRSI — Partial Yes "
     "requires appraisal of confounding and of how participants came to be in the study. Yes requires two "
     "more: how exposures and outcomes were ascertained, and whether the reported result was picked out of "
     "several measurements or analyses of one specified outcome. A panel covering a design the review did not "
     "include is left unrated rather than counted."),
    (10, "Sources of funding of included studies reported",
     "Did the review authors report on the sources of funding for the studies included in the review?",
     "Yes requires the funding behind each individual included study to be reported. Stating that the reviewers "
     "went looking and the original authors had not disclosed it also earns Yes."),
    (11, "Appropriate methods for statistical combination (if meta-analysis)",
     "If meta-analysis was performed did the review authors use appropriate methods for statistical combination "
     "of results?",
     "RCTs — Yes requires all of: a stated rationale for pooling at all; a suitable weighted estimator, "
     "accommodating heterogeneity where it exists; and an inquiry into what drove any heterogeneity. NRSI — Yes "
     "requires all of: a stated rationale for pooling; a suitable weighted estimator accommodating heterogeneity "
     "where it exists; pooling of confounding-adjusted effect estimates rather than of unadjusted raw data (or "
     "an argument for using raw data where adjusted estimates did not exist); and, when both designs were "
     "included, pooled estimates reported separately for randomised and non-randomised evidence."),
    (12, "Impact of RoB on the synthesis assessed (if meta-analysis)",
     "If meta-analysis was performed, did the review authors assess the potential impact of RoB in individual "
     "studies on the results of the meta-analysis or other evidence synthesis?",
     "Yes by either route: the synthesis drew only on randomised trials judged at low risk of bias; or, where "
     "the pooled RCTs and/or NRSI varied in risk of bias, the reviewers ran analyses testing how far that "
     "variation moved the summary effect."),
    (13, "RoB accounted for when interpreting/discussing results",
     "Did the review authors account for RoB in individual studies when interpreting/discussing the results of "
     "the review?",
     "Yes by either route: only low-risk-of-bias randomised trials were included; or, where RCTs at moderate or "
     "high risk of bias or NRSI were included, the review works through what that risk of bias probably does to "
     "the findings."),
    (14, "Heterogeneity satisfactorily explained and discussed",
     "Did the review authors provide a satisfactory explanation for, and discussion of, any heterogeneity "
     "observed in the results of the review?",
     "Yes by either route: the results showed no material heterogeneity; or heterogeneity was present and the "
     "reviewers both traced where it came from and spelled out what it means for the review's results."),
    (15, "Publication bias investigated and its impact discussed (if quantitative synthesis)",
     "If they performed quantitative synthesis did the review authors carry out an adequate investigation of "
     "publication bias (small study bias) and discuss its likely impact on the results of the review?",
     "Yes requires both halves: a graphical or statistical examination for publication bias, and a discussion "
     "of how likely such bias is and how large a distortion it could have produced in the review's results."),
    (16, "Conflicts of interest and review funding reported",
     "Did the review authors report any potential sources of conflict of interest, including any funding they "
     "received for conducting the review?",
     "Yes by either route: the review authors declare that they hold no competing interests; or they name who "
     "funded the review and explain how any resulting conflicts were handled."),
]
SHORT = {n: s for n, s, _, _ in ITEMS}
WORDING = {n: w for n, _, w, _ in ITEMS}
CRITERIA = {n: c for n, _, _, c in ITEMS}


def options_for(num):
    opts = [Y]
    if num in PARTIAL_YES_ITEMS:
        opts.append(PY)
    opts.append(N)
    if num in NMA_ITEMS:
        opts.append(NMA)
    return opts


# --- built-in worked example (SKILL.md) --------------------------------------

DEMO = {
    "review": "Illustrative — 'Digital cognitive behavioural therapy for insomnia in adults: systematic "
              "review and meta-analysis of 12 randomised trials' (2024)",
    "question": "P adults with chronic insomnia | I app- or web-delivered CBT-I | C sleep-hygiene education "
                "or waitlist | O sleep-onset latency; Insomnia Severity Index",
    "items": {
        "1": {"response": "Y", "note": "Methods 2.1 states population, intervention, comparators and outcomes"},
        "2": {"response": "PY", "note": "'The protocol was agreed by the team before searching' (Methods 2.0); "
                                        "not registered; deviations not discussed"},
        "3": {"response": "Y", "note": "'Only RCTs were eligible because more than ten trials were available' (Methods 2.2)"},
        "4": {"response": "PY", "note": "MEDLINE, Embase, PsycINFO, CENTRAL to Jan 2022; strategy in Appendix A; "
                                        "English-only justified; no reference-list, registry or grey-literature "
                                        "search; searched 30 months before publication"},
        "5": {"response": "Y", "note": "'Two reviewers screened titles, abstracts and full texts independently' (Methods 2.3)"},
        "6": {"response": "N", "note": "'Data were extracted by one reviewer' (Methods 2.4)"},
        "7": {"response": "N", "note": "PRISMA flow gives counts only; no list of excluded full-text studies or reasons"},
        "8": {"response": "Y", "note": "Table 1: population, intervention (platform, sessions), comparator, setting, follow-up"},
        "9": {"response": "Y", "note": "Cochrane RoB 2, all five domains, per outcome (Table 2)"},
        "10": {"response": "N", "note": "Funding of the included trials neither reported nor sought"},
        "11": {"response": "Y", "note": "Random-effects model after stating comparability; heterogeneity explored (Methods 2.6)"},
        "12": {"response": "Y", "note": "Sensitivity analysis excluding three high-RoB trials (Results 3.4)"},
        "13": {"response": "Y", "note": "Discussion 4.2 weighs the pooled effect against RoB in the smaller trials"},
        "14": {"response": "Y", "note": "I2 = 62%; explored by delivery format and therapist support (Results 3.3)"},
        "15": {"response": "N", "note": "No funnel plot or test; 'publication bias cannot be excluded' stated without investigation"},
        "16": {"response": "Y", "note": "'The authors declare no competing interests'; funded by a national research council"},
    },
}

# --- input parsing -------------------------------------------------------------

ALIASES = {
    Y: {"y", "yes"},
    PY: {"py", "partial yes", "partial-yes", "partial_yes", "partial", "partially yes"},
    N: {"n", "no"},
    NMA: {"nma", "no meta-analysis conducted", "no meta-analysis", "no meta analysis", "no metaanalysis",
          "no ma", "n/a (no meta-analysis)"},
}


def normalise_response(num, raw):
    """Map a raw response to Y / PY / N / NMA and check it is allowed for this item."""
    s = " ".join(str(raw).strip().lower().replace(".", "").split())
    code = None
    for c, names in ALIASES.items():
        if s in names:
            code = c
            break
    if code is None:
        raise ValueError(f"item {num}: unrecognised response {raw!r} (use Y / PY / N / NMA)")
    if code == PY and num not in PARTIAL_YES_ITEMS:
        raise ValueError(f"item {num}: 'Partial Yes' is not a response option for this item "
                         f"(only items {', '.join(map(str, PARTIAL_YES_ITEMS))})")
    if code == NMA and num not in NMA_ITEMS:
        raise ValueError(f"item {num}: 'No meta-analysis conducted' is not a response option for this item "
                         f"(only items {', '.join(map(str, NMA_ITEMS))})")
    return code


def _item_number(key):
    try:
        num = int(str(key).strip().lower().replace("item", "").strip())
    except ValueError:
        raise ValueError(f"item key {key!r} is not an item number 1-16")
    if not 1 <= num <= 16:
        raise ValueError(f"item key {key!r} is outside 1-16")
    return num


def parse_item(num, raw):
    """Return (response_code, note, detail) for one item value.

    raw may be a string, {"response": ..., "note": ...}, or for items 9 and 11 a
    per-design object {"RCT": ..., "NRSI": ...} whose weaker applicable panel wins.
    """
    if isinstance(raw, dict):
        note = str(raw.get("note", "") or "").strip()
        if "response" in raw or "answer" in raw:
            return normalise_response(num, raw.get("response", raw.get("answer"))), note, ""
        panels = {str(k).upper(): v for k, v in raw.items() if str(k).upper() in ("RCT", "RCTS", "NRSI")}
        if panels:
            if num not in (9, 11):
                raise ValueError(f"item {num}: per-design (RCT/NRSI) answers are only defined for items 9 and 11")
            codes = {k: normalise_response(num, v) for k, v in sorted(panels.items())}
            applicable = [c for c in codes.values() if c != NMA] or list(codes.values())
            code = min(applicable, key=lambda c: SEVERITY[c])
            detail = "; ".join(f"{k} {LABEL[c]}" for k, c in codes.items()) + " -> weaker applicable panel"
            return code, note, detail
        raise ValueError(f"item {num}: object must have a 'response' key or RCT/NRSI panel keys")
    return normalise_response(num, raw), "", ""


def parse_assessment(data):
    """Validate a raw JSON object; return a normalised assessment dict."""
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object with an 'items' key")
    items_raw = data.get("items")
    if not isinstance(items_raw, dict) or not items_raw:
        raise ValueError("'items' must be an object mapping item numbers 1-16 to responses")
    responses, notes, details = {}, {}, {}
    for key, raw in items_raw.items():
        num = _item_number(key)
        if num in responses:
            raise ValueError(f"item {num} given twice")
        responses[num], notes[num], details[num] = parse_item(num, raw)
    missing = [n for n in range(1, 17) if n not in responses]
    if missing:
        raise ValueError("every AMSTAR 2 item needs a response (there is no 'not applicable'; rate a "
                         f"non-reported item 'No'); missing: {', '.join(map(str, missing))}")
    for key, note in (data.get("notes") or {}).items():
        num = _item_number(key)
        if note and not notes.get(num):
            notes[num] = str(note).strip()
    critical = None
    if data.get("critical_override") is not None:
        critical = parse_critical(data["critical_override"])
    convention = data.get("partial_yes")
    if convention is not None:
        convention = str(convention).strip().lower()
        if convention not in CONVENTIONS:
            raise ValueError(f"partial_yes must be one of {', '.join(CONVENTIONS)}; got {convention!r}")
    return {
        "review": str(data.get("review", "") or "").strip(),
        "question": str(data.get("question", "") or "").strip(),
        "responses": responses, "notes": notes, "details": details,
        "critical_override": critical, "partial_yes": convention,
    }


def parse_critical(value):
    """A full list of item numbers to treat as critical (replaces Box 1)."""
    if isinstance(value, str):
        value = [v for v in value.replace(";", ",").split(",") if v.strip()]
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError("critical domains must be a non-empty list of item numbers 1-16")
    nums = sorted({_item_number(v) for v in value})
    return tuple(nums)


def load_file(path):
    fh = sys.stdin if path == "-" else open(path, encoding="utf-8")
    try:
        return parse_assessment(json.load(fh))
    finally:
        if fh is not sys.stdin:
            fh.close()


# --- the rating (Box 1 + Box 2) --------------------------------------------------

def classify(code, is_critical, convention):
    """Status of one item under the stated Partial Yes convention."""
    if code == Y:
        return "met"
    if code == NMA:
        return "not applicable"
    if code == N:
        return "critical flaw" if is_critical else "non-critical weakness"
    # Partial Yes
    if convention == "met":
        return "met (partial adherence)"
    if convention == "flaw" and is_critical:
        return "critical flaw"
    return "non-critical weakness"


def rate(assessment, convention=None, critical=None, moderate_to_low=None):
    """Derive the overall confidence rating. Returns a JSON-serialisable dict."""
    convention = convention or assessment.get("partial_yes") or "weakness"
    if convention not in CONVENTIONS:
        raise ValueError(f"partial_yes convention must be one of {', '.join(CONVENTIONS)}")
    if critical is None:
        critical = assessment.get("critical_override")
    overridden = critical is not None
    critical = tuple(critical) if overridden else DEFAULT_CRITICAL
    if moderate_to_low is not None and moderate_to_low < 2:
        raise ValueError("--moderate-to-low must be >= 2 (Moderate already means more than one weakness)")

    rows, flaws, weak, na, warnings = [], [], [], [], []
    for num in range(1, 17):
        code = assessment["responses"][num]
        is_crit = num in critical
        status = classify(code, is_crit, convention)
        if status == "critical flaw":
            flaws.append(num)
        elif status == "non-critical weakness":
            weak.append(num)
        elif status == "not applicable":
            na.append(num)
        rows.append({"item": num, "short": SHORT[num], "response": code, "response_label": LABEL[code],
                     "critical": is_crit, "status": status,
                     "note": assessment["notes"].get(num, ""), "detail": assessment["details"].get(num, "")})

    nma_flags = {n: assessment["responses"][n] == NMA for n in NMA_ITEMS}
    if any(nma_flags.values()) and not all(nma_flags.values()):
        warnings.append("items 11/12/15 disagree on whether a meta-analysis was conducted ("
                        + ", ".join(f"{n}={LABEL[assessment['responses'][n]]}" for n in NMA_ITEMS)
                        + ") — check; a review either pooled or did not")
    if convention == "met" and any(assessment["responses"][n] == PY for n in range(1, 17)):
        warnings.append("Partial Yes counted as adherence ('met' convention) — report this; the default "
                        "treats partial adherence as a weakness")

    n_flaws, n_weak = len(flaws), len(weak)
    trace = [f"critical domains: {', '.join(map(str, critical))} "
             + ("(reviewer override; Box 1 default is 2, 4, 7, 9, 11, 13, 15)" if overridden else "(AMSTAR 2 Box 1)"),
             f"Partial Yes convention: {convention}",
             f"critical flaws = {n_flaws}" + (f" (items {', '.join(map(str, flaws))})" if flaws else ""),
             f"non-critical weaknesses = {n_weak}" + (f" (items {', '.join(map(str, weak))})" if weak else "")]
    if n_flaws > 1:
        rating = CRIT_LOW
        trace.append(f"critical flaws {n_flaws} > 1 -> {CRIT_LOW}")
    elif n_flaws == 1:
        rating = LOW
        trace.append(f"critical flaws = 1 -> {LOW}")
    elif n_weak > 1:
        rating = MODERATE
        trace.append(f"no critical flaw; non-critical weaknesses {n_weak} > 1 -> {MODERATE}")
        if moderate_to_low is not None and n_weak >= moderate_to_low:
            rating = LOW
            trace.append(f"{BOX2_FOOTNOTE} — applied: {n_weak} >= --moderate-to-low {moderate_to_low} -> {LOW}")
        else:
            trace.append(BOX2_FOOTNOTE + " (advisory; not applied)")
    else:
        rating = HIGH
        trace.append(f"no critical flaw; non-critical weaknesses {n_weak} <= 1 -> {HIGH}")

    return {
        "review": assessment["review"], "question": assessment["question"],
        "convention": {"partial_yes": convention, "critical_domains": list(critical),
                       "critical_source": "reviewer override" if overridden else "AMSTAR 2 Box 1",
                       "moderate_to_low_threshold": moderate_to_low},
        "items": rows,
        "critical_flaws": flaws, "non_critical_weaknesses": weak, "not_applicable": na,
        "counts": {"critical_flaws": n_flaws, "non_critical_weaknesses": n_weak,
                   "met": 16 - n_flaws - n_weak - len(na), "not_applicable": len(na)},
        "rating": rating, "rule": BOX2[rating][0], "interpretation": BOX2[rating][1],
        "trace": trace, "warnings": warnings,
        "source": {"paper": SOURCE_PAPER, "licence": SOURCE_LICENCE, "checklist": SOURCE_CHECKLIST,
                   "partial_yes": SOURCE_PARTIAL},
    }


# --- output ------------------------------------------------------------------

def print_rating(res):
    print(f"AMSTAR 2 appraisal — {res['review'] or '(review not named)'}")
    if res["question"]:
        print(f"Question (PICO): {res['question']}")
    conv = res["convention"]
    print(f"Critical domains: {', '.join(map(str, conv['critical_domains']))} ({conv['critical_source']}); "
          f"Partial Yes = {conv['partial_yes']}")
    print()
    print(f"{'Item':<5}{'Response':<15}{'Critical':<10}{'Counts as':<24}Item (short)")
    for r in res["items"]:
        crit = "CRITICAL" if r["critical"] else "-"
        counts = "-" if r["status"].startswith("met") or r["status"] == "not applicable" else r["status"]
        if r["status"] == "not applicable":
            counts = "n/a (no meta-analysis)"
        elif r["status"] == "met (partial adherence)":
            counts = "met (partial)"
        print(f"{r['item']:<5}{r['response_label']:<15}{crit:<10}{counts:<24}{r['short']}")
    print()
    c = res["counts"]
    print(f"Critical flaws ({c['critical_flaws']}): "
          + (", ".join(f"item {n}" for n in res["critical_flaws"]) or "none"))
    print(f"Non-critical weaknesses ({c['non_critical_weaknesses']}): "
          + (", ".join(f"item {n}" for n in res["non_critical_weaknesses"]) or "none"))
    if res["not_applicable"]:
        print(f"Not applicable (no meta-analysis): " + ", ".join(f"item {n}" for n in res["not_applicable"]))
    print()
    print("Rule trace (Box 2, Shea et al. 2017):")
    for line in res["trace"]:
        print("  " + line)
    print()
    print(f"Overall confidence: {res['rating'].upper()} — {res['rule']}: {res['interpretation']}.")
    for w in res["warnings"]:
        print(f"WARNING: {w}")
    notes = [r for r in res["items"] if r["note"] or r["detail"]]
    if notes:
        print()
        print("Evidence recorded per item:")
        for r in notes:
            txt = "; ".join(x for x in (r["detail"], r["note"]) if x)
            print(textwrap.fill(f"{r['item']:>3}. {txt}", width=100, subsequent_indent="       "))


def cmd_rate(args):
    if args.demo:
        assessment = parse_assessment(DEMO)
    elif args.file:
        assessment = load_file(args.file)
    else:
        raise ValueError("pass --file PATH (or '-' for stdin) or --demo")
    critical = parse_critical(args.critical) if args.critical else None
    res = rate(assessment, convention=args.partial_yes, critical=critical, moderate_to_low=args.moderate_to_low)
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print_rating(res)
    return 0


def cmd_items(args):
    if args.template:
        template = {"review": "", "question": "P ... | I ... | C ... | O ...",
                    "items": {str(n): {"response": "", "note": ""} for n in range(1, 17)},
                    "critical_override": list(DEFAULT_CRITICAL), "partial_yes": "weakness"}
        print(json.dumps(template, indent=2))
        return 0
    if args.json:
        print(json.dumps({"source": {"paper": SOURCE_PAPER, "licence": SOURCE_LICENCE,
                                     "checklist": SOURCE_CHECKLIST},
                          "responses": LABEL, "critical_domains": list(DEFAULT_CRITICAL),
                          "ratings": {k: v[0] for k, v in BOX2.items()},
                          "items": [{"item": n, "short": SHORT[n], "text": WORDING[n], "critical": n in DEFAULT_CRITICAL,
                                     "options": [LABEL[o] for o in options_for(n)], "criteria": CRITERIA[n]}
                                    for n in range(1, 17)]}, indent=2, ensure_ascii=False))
        return 0
    print("AMSTAR 2 — the 16 items, response options and rating criteria")
    print(f"Source: {SOURCE_PAPER}")
    print(textwrap.fill(SOURCE_LICENCE, width=100, initial_indent="        ", subsequent_indent="        "))
    print(textwrap.fill(SOURCE_CHECKLIST, width=100, initial_indent="        ", subsequent_indent="        "))
    print("Responses: Y = Yes, PY = Partial Yes (items 2, 4, 7, 8, 9 only), N = No, "
          "NMA = No meta-analysis conducted (items 11, 12, 15 only). No 'not applicable' / 'cannot answer': "
          "if the report gives no information, rate the item No.")
    print(f"Critical domains (Box 1): {', '.join(map(str, DEFAULT_CRITICAL))} — appraisers may add or substitute.")
    for n in range(1, 17):
        print()
        head = f"{n:>2}. {'[CRITICAL] ' if n in DEFAULT_CRITICAL else ''}{WORDING[n]}"
        print(textwrap.fill(head, width=100, subsequent_indent="    "))
        print(f"    Options: {' / '.join(LABEL[o] for o in options_for(n))}")
        print(textwrap.fill(CRITERIA[n], width=100, initial_indent="    ", subsequent_indent="    "))
    print()
    print("Overall confidence (Box 2): " + "; ".join(f"{k} = {v[0].lower()}" for k, v in BOX2.items()) + ".")
    print("Item ratings are never summed into a score.")
    return 0


# --- selftest --------------------------------------------------------------------

def _mk(**over):
    """A complete all-Yes assessment with selected items overridden (keys 'i2', 'i15', ...)."""
    items = {str(n): "Y" for n in range(1, 17)}
    for k, v in over.items():
        items[k[1:]] = v
    return parse_assessment({"review": "t", "items": items})


def run_selftest():
    """Expected values are read off Box 1 / Box 2 of Shea et al. 2017 and the checklist's
    response options — not from memory of other implementations."""
    checks = []

    def check(name, got, want):
        ok = got == want
        checks.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got!r}, expected {want!r}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    def rejects(name, fn):
        try:
            fn()
        except ValueError as exc:
            checks.append(True)
            print(f"PASS  {name}: rejected ({str(exc)[:70]})")
            return
        print(f"FAIL  {name}: accepted invalid input", file=sys.stderr)
        sys.exit(1)

    # Box 2 — the four outcomes
    check("all Yes -> High", rate(_mk())["rating"], HIGH)
    check("one non-critical No (item 10) -> High ('no or one non-critical weakness')",
          rate(_mk(i10="N"))["rating"], HIGH)
    r = rate(_mk(i10="N", i16="N"))
    check("two non-critical No (10, 16) -> Moderate", r["rating"], MODERATE)
    check("  ... weaknesses listed", r["non_critical_weaknesses"], [10, 16])
    r = rate(_mk(i7="N"))
    check("one critical No (item 7) -> Low", r["rating"], LOW)
    check("  ... flaw listed", r["critical_flaws"], [7])
    check("one critical No + three non-critical No -> Low (weaknesses do not add up to Critically low)",
          rate(_mk(i7="N", i5="N", i6="N", i10="N"))["rating"], LOW)
    r = rate(_mk(i2="N", i15="N"))
    check("two critical No (2, 15) -> Critically low", r["rating"], CRIT_LOW)
    check("  ... both flaws listed, no weaknesses", (r["critical_flaws"], r["non_critical_weaknesses"]), ([2, 15], []))
    check("  ... every rating carries a rule and a reading",
          all(bool(BOX2[k][0].strip()) and bool(BOX2[k][1].strip()) for k in (HIGH, MODERATE, LOW, CRIT_LOW)), True)
    check("all sixteen No -> Critically low with 7 flaws / 9 weaknesses",
          (lambda x: (x["rating"], x["counts"]["critical_flaws"], x["counts"]["non_critical_weaknesses"]))(
              rate(_mk(**{f"i{n}": "N" for n in range(1, 17)}))), (CRIT_LOW, 7, 9))

    # Partial Yes conventions (the paper leaves the weight open; default = non-critical weakness)
    r = rate(_mk(i2="PY", i4="PY"))
    check("PY on critical items 2, 4 -> default: two non-critical weaknesses -> Moderate", r["rating"], MODERATE)
    check("  ... convention recorded", r["convention"]["partial_yes"], "weakness")
    check("PY on 2, 4 with --partial-yes flaw -> two critical flaws -> Critically low",
          rate(_mk(i2="PY", i4="PY"), convention="flaw")["rating"], CRIT_LOW)
    check("PY on 2, 4 with --partial-yes met -> High", rate(_mk(i2="PY", i4="PY"), convention="met")["rating"], HIGH)
    check("PY on non-critical item 8 is a weakness under 'flaw' too",
          rate(_mk(i8="PY", i10="N"), convention="flaw")["rating"], MODERATE)
    check("single PY on item 8 -> High (one non-critical weakness)", rate(_mk(i8="PY"))["rating"], HIGH)
    check("file-level partial_yes honoured",
          rate(parse_assessment({"items": {**{str(n): "Y" for n in range(1, 17)}, "2": "PY", "4": "PY"},
                                 "partial_yes": "flaw"}))["rating"], CRIT_LOW)

    # No meta-analysis conducted
    r = rate(_mk(i11="NMA", i12="NMA", i15="NMA"))
    check("11/12/15 NMA, rest Yes -> High (NMA is not a weakness)", r["rating"], HIGH)
    check("  ... listed as not applicable", r["not_applicable"], [11, 12, 15])
    check("  ... no warning when consistent", r["warnings"], [])
    check("meta-analysis done, item 15 No -> Low", rate(_mk(i15="N"))["rating"], LOW)
    r = rate(_mk(i11="NMA", i12="Y", i15="N"))
    check("mixed 11=NMA / 15=No -> warning issued", len(r["warnings"]), 1)

    # Reviewer-defined critical domains
    check("item 3 No, default domains -> High", rate(_mk(i3="N"))["rating"], HIGH)
    r = rate(_mk(i3="N"), critical=(2, 3, 4, 7, 9, 11, 13, 15))
    check("item 3 No with item 3 added as critical -> Low", r["rating"], LOW)
    check("  ... source says override", r["convention"]["critical_source"], "reviewer override")
    check("item 15 No with 15 removed from the critical set -> High",
          rate(_mk(i15="N"), critical=(2, 4, 7, 9, 11, 13))["rating"], HIGH)
    check("critical_override in file honoured",
          rate(parse_assessment({"items": {**{str(n): "Y" for n in range(1, 17)}, "14": "N"},
                                 "critical_override": [2, 4, 7, 9, 11, 13, 14, 15]}))["rating"], LOW)

    # Box 2 footnote (advisory) applied only on request
    check("four non-critical weaknesses, footnote off -> Moderate", rate(_mk(i5="N", i6="N", i10="N", i16="N"))["rating"], MODERATE)
    check("four non-critical weaknesses, --moderate-to-low 4 -> Low",
          rate(_mk(i5="N", i6="N", i10="N", i16="N"), moderate_to_low=4)["rating"], LOW)

    # Long-form answers and per-design panels
    a = parse_assessment({"items": {**{str(n): "Yes" for n in range(1, 17)}, "2": "Partial Yes",
                                    "11": "No meta-analysis conducted", "12": "no meta-analysis", "15": "NMA"}})
    check("long forms accepted", (a["responses"][2], a["responses"][11], a["responses"][15]), (PY, NMA, NMA))
    a = parse_assessment({"items": {**{str(n): "Y" for n in range(1, 17)}, "9": {"RCT": "Y", "NRSI": "PY"},
                                    "11": {"RCT": "Y", "NRSI": "N"}}})
    check("item 9 per design -> weaker panel (PY)", a["responses"][9], PY)
    check("item 11 per design -> weaker panel (N)", a["responses"][11], N)
    a = parse_assessment({"items": {**{str(n): "Y" for n in range(1, 17)}, "11": {"RCT": "NMA", "NRSI": "NMA"}}})
    check("item 11 both panels NMA -> NMA", a["responses"][11], NMA)

    # Invalid input is rejected (exit 1 at the CLI)
    rejects("Partial Yes on item 1 (not an option)", lambda: _mk(i1="PY"))
    rejects("Partial Yes on item 13 (critical, but Yes/No only)", lambda: _mk(i13="PY"))
    rejects("NMA on item 5", lambda: _mk(i5="NMA"))
    rejects("unknown response 'maybe'", lambda: _mk(i3="maybe"))
    rejects("missing item 16", lambda: parse_assessment({"items": {str(n): "Y" for n in range(1, 16)}}))
    rejects("item 17", lambda: parse_assessment({"items": {**{str(n): "Y" for n in range(1, 17)}, "17": "Y"}}))
    rejects("critical_override with 0", lambda: parse_critical([0, 2]))
    rejects("empty critical_override", lambda: parse_critical([]))
    rejects("unknown partial_yes convention", lambda: parse_assessment({"items": {str(n): "Y" for n in range(1, 17)}, "partial_yes": "ignore"}))
    rejects("per-design answers on item 4", lambda: parse_assessment({"items": {**{str(n): "Y" for n in range(1, 17)}, "4": {"RCT": "Y", "NRSI": "N"}}}))
    rejects("--moderate-to-low 1", lambda: rate(_mk(), moderate_to_low=1))

    # Instrument facts
    check("Partial Yes items are 2, 4, 7, 8, 9", tuple(n for n in range(1, 17) if PY in options_for(n)), (2, 4, 7, 8, 9))
    check("NMA items are 11, 12, 15", tuple(n for n in range(1, 17) if NMA in options_for(n)), (11, 12, 15))
    check("Box 1 critical domains", DEFAULT_CRITICAL, (2, 4, 7, 9, 11, 13, 15))

    # Worked example (SKILL.md) — 2 critical flaws (7, 15), 4 non-critical weaknesses (2, 4, 6, 10)
    r = rate(parse_assessment(DEMO))
    check("demo -> Critically low", r["rating"], CRIT_LOW)
    check("demo critical flaws", r["critical_flaws"], [7, 15])
    check("demo non-critical weaknesses", r["non_critical_weaknesses"], [2, 4, 6, 10])
    check("demo under 'flaw' convention -> still Critically low (4 flaws)",
          (lambda x: (x["rating"], x["counts"]["critical_flaws"]))(rate(parse_assessment(DEMO), convention="flaw")), (CRIT_LOW, 4))

    print(f"ALL {len(checks)} CHECKS PASSED")
    print("selftest OK")
    return 0


# --- CLI ---------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(
        description="AMSTAR 2 (Shea et al., BMJ 2017) — record the 16 item responses of a systematic-review "
                    "appraisal and derive the overall confidence rating (High / Moderate / Low / Critically low) "
                    "from the critical-domain scheme of Box 2. Never a summed score.")
    parser.add_argument("--selftest", action="store_true", help="run built-in checks against Box 1 / Box 2 and the checklist and exit")
    parser.add_argument("--demo", dest="demo_top", action="store_true", help="same as: rate --demo")
    sub = parser.add_subparsers(dest="command")
    pr = sub.add_parser("rate", help="derive the overall confidence rating from item responses")
    pr.add_argument("--file", help="JSON file of item responses ('-' = stdin)")
    pr.add_argument("--demo", action="store_true", help="use the built-in SKILL.md worked example")
    pr.add_argument("--json", action="store_true", help="emit JSON instead of text")
    pr.add_argument("--partial-yes", choices=CONVENTIONS, default=None,
                    help="how a Partial Yes counts: weakness (default; non-critical weakness anywhere), "
                         "flaw (critical flaw in a critical domain), met (adherence — report if used)")
    pr.add_argument("--critical", metavar="LIST", default=None,
                    help="comma-separated item numbers to treat as critical (replaces Box 1: 2,4,7,9,11,13,15)")
    pr.add_argument("--moderate-to-low", type=int, metavar="N", default=None,
                    help="apply the Box 2 footnote: move Moderate down to Low when >= N non-critical weaknesses "
                         "(off by default; the paper calls this advisory)")
    pi = sub.add_parser("items", help="print the 16 items, response options and criteria (exact wording)")
    pi.add_argument("--json", action="store_true", help="emit the items as JSON")
    pi.add_argument("--template", action="store_true", help="emit an empty answers.json to fill in")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo_top and not args.command:
        args.command, args.demo, args.file, args.json = "rate", True, None, False
        args.partial_yes, args.critical, args.moderate_to_low = None, None, None
    if not args.command:
        parser.print_help()
        return 1
    try:
        if args.command == "rate":
            return cmd_rate(args)
        return cmd_items(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
