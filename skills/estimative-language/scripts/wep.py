#!/usr/bin/env python3
"""wep.py — words of estimative probability: map, look up, and lint.

Implements the calibrated-language tables in ../SKILL.md exactly as published:

  * ODNI ICD 203 "Analytic Standards" (2 Jan 2015; technical amendment
    21 Dec 2022), section D.6.e(2): seven likelihood bands with two synonym
    rows (almost no chance / remote 01-05% ... almost certain(ly) / nearly
    certain 95-99%), plus rule (b): a product "must not combine a confidence
    level and a degree of likelihood ... in the same sentence".
  * UK PHIA Probability Yardstick, "Explaining Uncertainty in UK
    Intelligence Assessment" (gov.uk, 24 Mar 2025): seven ranges with
    deliberate gaps between them (remote chance >0-~5% ... almost certain
    ~95-<100%); "the scale is not continuous to avoid a false impression of
    accuracy" (MoD Defence Intelligence, 17 Feb 2023).
  * IPCC AR5 Guidance Note (Mastrandrea et al., 2010), Table 1: nested
    likelihood bands (virtually certain 99-100% ... exceptionally unlikely
    0-1%) plus the AR4 additional terms allowed "when appropriate"; five
    confidence qualifiers derived from evidence x agreement.

Commands
  term   probability -> the standard's term(s); reports boundaries, gaps
         (PHIA) and nested matches (IPCC) instead of guessing
  prob   term -> the standard's range (all standards if none is given)
  lint   per sentence, with line:col — vague-likelihood (possible, may,
         could, significant chance, ...), mixed-confidence-likelihood
         (confidence phrase + likelihood term/number in one sentence),
         bare-number (a probability with no term), numeric-confidence
         ("80 % confident"), hedged-term ("quite likely"), foreign-term
         (a term from another standard than the one declared) and, per
         document, mixed-standards; exit 2 if any error-level finding
  table  print a standard's table with its citation

Stdlib only. Python 3.9+. Deterministic (no randomness, no clock).

Usage:
    python3 wep.py term  --p 0.7 [--standard icd203|phia|ipcc] [--json]
    python3 wep.py prob  --term "likely" [--standard phia] [--json]
    python3 wep.py lint  --file doc.md | --text "..." [--standard auto|icd203|phia|ipcc]
                         [--numbers require-term|allow] [--json]
    python3 wep.py table [--standard icd203|phia|ipcc]
    python3 wep.py --demo        # the SKILL.md worked example
    python3 wep.py --selftest    # hand-verified checks; prints 'selftest OK'
"""

import argparse
import json
import re
import sys

# ---------------------------------------------------------------------------
# The published tables (verbatim ranges; boundaries flagged inclusive/exclusive)
# ---------------------------------------------------------------------------

# Each band: term, synonyms (the standard's own alternates), lo, hi,
# lo_incl, hi_incl, and the range string exactly as the standard prints it.
STANDARDS = {
    "icd203": {
        "title": "ODNI ICD 203 Analytic Standards — likelihood terms (D.6.e(2)(a))",
        "citation": (
            "Office of the Director of National Intelligence, Intelligence Community "
            "Directive 203, Analytic Standards, 2 January 2015 (technical amendment "
            "21 December 2022), section D.6.e(2). "
            "https://www.dni.gov/files/documents/ICD/ICD-203-TA-Analytic-Standards-21-Dec-2022.pdf"
        ),
        "shape": "contiguous — adjacent bands share a boundary; the table runs 01-99 %",
        "confidence": {
            "levels": ["high", "moderate", "low"],
            "basis": (
                "the logic and evidentiary base that underpin the judgment, including the "
                "quantity and quality of source material, and the analyst's understanding of "
                "the topic (ICD 203); high = high-quality information and/or an issue that "
                "allows a solid judgment; moderate = credibly sourced and plausible but not "
                "of sufficient quality or corroboration; low = questionable credibility or "
                "plausibility, fragmented or poorly corroborated (NIC, 'What We Mean When We "
                "Say', 2007)"
            ),
            "rule": "must not combine a confidence level and a degree of likelihood in the same sentence",
        },
        "bands": [
            dict(term="almost no chance", synonyms=["remote"], lo=0.01, hi=0.05, lo_incl=True, hi_incl=True, range="01-05%"),
            dict(term="very unlikely", synonyms=["highly improbable"], lo=0.05, hi=0.20, lo_incl=True, hi_incl=True, range="05-20%"),
            dict(term="unlikely", synonyms=["improbable", "improbably"], lo=0.20, hi=0.45, lo_incl=True, hi_incl=True, range="20-45%"),
            dict(term="roughly even chance", synonyms=["roughly even odds"], lo=0.45, hi=0.55, lo_incl=True, hi_incl=True, range="45-55%"),
            dict(term="likely", synonyms=["probable", "probably"], lo=0.55, hi=0.80, lo_incl=True, hi_incl=True, range="55-80%"),
            dict(term="very likely", synonyms=["highly probable"], lo=0.80, hi=0.95, lo_incl=True, hi_incl=True, range="80-95%"),
            dict(term="almost certain", synonyms=["almost certainly", "nearly certain"], lo=0.95, hi=0.99, lo_incl=True, hi_incl=True, range="95-99%"),
        ],
    },
    "phia": {
        "title": "UK PHIA Probability Yardstick",
        "citation": (
            "Professional Head of Intelligence Assessment (PHIA), 'Explaining Uncertainty in UK "
            "Intelligence Assessment', GOV.UK guidance, published 24 March 2025. "
            "https://www.gov.uk/government/publications/explaining-uncertainty-in-uk-intelligence-assessment/"
            "explaining-uncertainty-in-uk-intelligence-assessment — gaps are deliberate: 'The scale is "
            "not continuous to avoid a false impression of accuracy' (Ministry of Defence, Defence "
            "Intelligence: communicating probability, 17 February 2023)."
        ),
        "shape": "seven ranges with deliberate gaps (5-10, 20-25, 35-40, 50-55, 75-80, 90-95 %); '≈' marks approximate edges",
        "confidence": {
            "levels": ["high", "moderate", "low"],
            "basis": (
                "Analytical Confidence Rating (AnCR) — High, Moderate or Low — evaluated against "
                "Information Base, Analytical Rigour, and Complexity & Volatility; stated in a "
                "separate AnCR statement"
            ),
            "rule": "probability and confidence are two frameworks; give the AnCR as its own rating/statement",
        },
        "bands": [
            dict(term="remote chance", synonyms=[], lo=0.0, hi=0.05, lo_incl=False, hi_incl=True, range=">0% - ≈5%"),
            dict(term="highly unlikely", synonyms=[], lo=0.10, hi=0.20, lo_incl=True, hi_incl=True, range="≈10% - ≈20%"),
            dict(term="unlikely", synonyms=[], lo=0.25, hi=0.35, lo_incl=True, hi_incl=True, range="≈25% - ≈35%"),
            dict(term="realistic possibility", synonyms=[], lo=0.40, hi=0.50, lo_incl=True, hi_incl=False, range="≈40% - <50%"),
            dict(term="likely", synonyms=["probable", "probably"], lo=0.55, hi=0.75, lo_incl=True, hi_incl=True, range="≈55% - ≈75%"),
            dict(term="highly likely", synonyms=[], lo=0.80, hi=0.90, lo_incl=True, hi_incl=True, range="≈80% - ≈90%"),
            dict(term="almost certain", synonyms=["almost certainly"], lo=0.95, hi=1.0, lo_incl=True, hi_incl=False, range="≈95% - <100%"),
        ],
    },
    "ipcc": {
        "title": "IPCC AR5 Guidance Note — Table 1 Likelihood Scale",
        "citation": (
            "M. D. Mastrandrea, C. B. Field, T. F. Stocker, O. Edenhofer, K. L. Ebi, D. J. Frame, "
            "H. Held, E. Kriegler, K. J. Mach, P. R. Matschoss, G.-K. Plattner, G. W. Yohe and "
            "F. W. Zwiers, 'Guidance Note for Lead Authors of the IPCC Fifth Assessment Report on "
            "Consistent Treatment of Uncertainties', IPCC, 2010, Table 1 and paras 8-10. "
            "https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf"
        ),
        "shape": "nested bands with 'fuzzy' boundaries — several terms can be true at once; report the narrowest",
        "confidence": {
            "levels": ["very high", "high", "medium", "low", "very low"],
            "basis": (
                "evidence (limited / medium / robust) x agreement (low / medium / high); "
                "'Confidence should not be interpreted probabilistically'"
            ),
            "rule": "a finding with a likelihood term may carry a confidence qualifier; it is not required when confidence is high or very high",
        },
        "bands": [
            dict(term="virtually certain", synonyms=[], lo=0.99, hi=1.0, lo_incl=True, hi_incl=True, range="99-100% probability"),
            dict(term="very likely", synonyms=[], lo=0.90, hi=1.0, lo_incl=True, hi_incl=True, range="90-100% probability"),
            dict(term="likely", synonyms=[], lo=0.66, hi=1.0, lo_incl=True, hi_incl=True, range="66-100% probability"),
            dict(term="about as likely as not", synonyms=[], lo=0.33, hi=0.66, lo_incl=True, hi_incl=True, range="33 to 66% probability"),
            dict(term="unlikely", synonyms=[], lo=0.0, hi=0.33, lo_incl=True, hi_incl=True, range="0-33% probability"),
            dict(term="very unlikely", synonyms=[], lo=0.0, hi=0.10, lo_incl=True, hi_incl=True, range="0-10% probability"),
            dict(term="exceptionally unlikely", synonyms=[], lo=0.0, hi=0.01, lo_incl=True, hi_incl=True, range="0-1% probability"),
            # AR4 additional terms "may also be used in the AR5 when appropriate" (Table 1 footnote)
            dict(term="extremely likely", synonyms=[], lo=0.95, hi=1.0, lo_incl=True, hi_incl=True, range="95-100% probability", extra=True),
            dict(term="more likely than not", synonyms=[], lo=0.50, hi=1.0, lo_incl=False, hi_incl=True, range=">50-100% probability", extra=True),
            dict(term="extremely unlikely", synonyms=[], lo=0.0, hi=0.05, lo_incl=True, hi_incl=True, range="0-5% probability", extra=True),
        ],
    },
}
STANDARD_ORDER = ("icd203", "phia", "ipcc")
LABEL = {"icd203": "ICD 203", "phia": "PHIA yardstick", "ipcc": "IPCC AR5"}

# ---------------------------------------------------------------------------
# Probability <-> term
# ---------------------------------------------------------------------------


def in_band(p, band):
    """True when p lies inside the band, honouring inclusive/exclusive edges."""
    lo_ok = p >= band["lo"] if band["lo_incl"] else p > band["lo"]
    hi_ok = p <= band["hi"] if band["hi_incl"] else p < band["hi"]
    return lo_ok and hi_ok


def width(band):
    return band["hi"] - band["lo"]


def term_for(p, standard):
    """Return a dict describing every band of `standard` that contains p.

    kind: 'term' (exactly one band), 'boundary' (two contiguous bands share
    the point), 'nested' (IPCC: several overlapping bands), 'gap' (PHIA: p
    falls between bands) or 'outside' (beyond the table's ends).
    """
    std = STANDARDS[standard]
    bands = std["bands"]
    hits = [b for b in bands if in_band(p, b)]
    core = [b for b in hits if not b.get("extra")]
    result = {"standard": standard, "p": p, "matches": [], "extra": [], "kind": None, "gap_between": None}
    for b in sorted(hits, key=lambda b: (width(b), b["term"])):
        entry = {"term": b["term"], "synonyms": list(b["synonyms"]), "range": b["range"]}
        (result["extra"] if b.get("extra") else result["matches"]).append(entry)
    if core:
        if len(core) == 1:
            result["kind"] = "term"
        elif standard == "ipcc":
            result["kind"] = "nested"
        else:
            result["kind"] = "boundary"
        return result
    lo_end = min(b["lo"] for b in bands)
    hi_end = max(b["hi"] for b in bands)
    if p < lo_end or p > hi_end or (p == lo_end and not any(b["lo_incl"] for b in bands if b["lo"] == lo_end)) \
            or (p == hi_end and not any(b["hi_incl"] for b in bands if b["hi"] == hi_end)):
        result["kind"] = "outside"
        return result
    result["kind"] = "gap"
    below = max((b for b in bands if not b.get("extra") and b["hi"] <= p), key=lambda b: b["hi"])
    above = min((b for b in bands if not b.get("extra") and b["lo"] >= p), key=lambda b: b["lo"])
    result["gap_between"] = [
        {"term": below["term"], "range": below["range"]},
        {"term": above["term"], "range": above["range"]},
    ]
    return result


def fmt_pct(p):
    s = ("%.4f" % (100 * p)).rstrip("0").rstrip(".")
    return s + " %"


def render_term(res):
    std = res["standard"]
    p = res["p"]
    lines = ["p = %s  (%s)   standard: %s" % (("%g" % p), fmt_pct(p), STANDARDS[std]["title"])]
    kind = res["kind"]
    if kind == "term":
        m = res["matches"][0]
        syn = ("  — synonyms: " + ", ".join(m["synonyms"])) if m["synonyms"] else ""
        lines.append("  term: %s (%s)%s" % (m["term"], m["range"], syn))
        lines.append('  write: "%s (%s)" — keep the number when the reader will act on it' % (m["term"], fmt_pct(p)))
    elif kind == "boundary":
        lines.append("  boundary: %s shared by %s — pick one and attach the number" % (
            fmt_pct(p), " / ".join("%s (%s)" % (m["term"], m["range"]) for m in res["matches"])))
    elif kind == "nested":
        lines.append("  narrowest term: %s (%s)" % (res["matches"][0]["term"], res["matches"][0]["range"]))
        if len(res["matches"]) > 1:
            lines.append("  also true (wider bands): " + "; ".join(
                "%s (%s)" % (m["term"], m["range"]) for m in res["matches"][1:]))
    elif kind == "gap":
        lo, hi = res["gap_between"]
        lines.append("  no term: %s falls in a deliberate gap between '%s' (%s) and '%s' (%s)" % (
            fmt_pct(p), lo["term"], lo["range"], hi["term"], hi["range"]))
        lines.append("  action: state the number, or move the judgment into a band — the yardstick "
                     "'is not continuous to avoid a false impression of accuracy'")
    else:  # outside
        lines.append("  no term: %s lies outside the %s table — say 'certain' / 'no chance' or give the number, "
                     "not an estimative term" % (fmt_pct(p), LABEL[std]))
    if res["extra"]:
        lines.append("  AR4 additional terms (permitted 'when appropriate'): " + "; ".join(
            "%s (%s)" % (m["term"], m["range"]) for m in res["extra"]))
    return "\n".join(lines)


def prob_for(term, standard=None):
    """Return [(standard, band)] whose term or synonym equals `term` (case-insensitive)."""
    t = normalize_term(term)
    out = []
    for std in STANDARD_ORDER if standard is None else (standard,):
        for b in STANDARDS[std]["bands"]:
            names = [b["term"]] + b["synonyms"]
            if t in [normalize_term(n) for n in names]:
                out.append((std, b))
    return out


def normalize_term(s):
    s = s.strip().lower().replace("’", "'")
    s = re.sub(r"\s+", " ", s)
    s = s.replace("almost certain(ly)", "almost certain")
    return s


def render_prob(term, hits, standard):
    if not hits:
        where = "any supported standard" if standard is None else LABEL[standard]
        msg = ["'%s' is not a term in %s" % (term, where)]
        if standard is not None:
            elsewhere = prob_for(term)
            if elsewhere:
                msg.append("  it is a %s term: %s" % (
                    ", ".join(sorted({LABEL[s] for s, _ in elsewhere})),
                    "; ".join("%s (%s, %s)" % (b["term"], b["range"], LABEL[s]) for s, b in elsewhere)))
            msg.append("  %s terms: %s" % (LABEL[standard], ", ".join(b["term"] for b in STANDARDS[standard]["bands"] if not b.get("extra"))))
        return "\n".join(msg)
    lines = []
    for std, b in hits:
        syn = ("  — synonyms: " + ", ".join(b["synonyms"])) if b["synonyms"] else ""
        extra = "  [AR4 additional term]" if b.get("extra") else ""
        lines.append("%s: %s = %s%s%s" % (LABEL[std], b["term"], b["range"], syn, extra))
    return "\n".join(lines)


def render_table(standard):
    std = STANDARDS[standard]
    lines = [std["title"], "=" * len(std["title"])]
    w = max(len(b["term"]) for b in std["bands"])
    for b in std["bands"]:
        syn = ("   [" + ", ".join(b["synonyms"]) + "]") if b["synonyms"] else ""
        extra = "   (AR4 additional term, 'when appropriate')" if b.get("extra") else ""
        lines.append("  %-*s  %s%s%s" % (w, b["term"], b["range"], syn, extra))
    lines.append("shape: " + std["shape"])
    conf = std["confidence"]
    lines.append("confidence levels: %s — %s" % (" / ".join(conf["levels"]), conf["basis"]))
    lines.append("rule: " + conf["rule"])
    lines.append("source: " + std["citation"])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Lint
# ---------------------------------------------------------------------------

# Every recognised likelihood phrase -> set of standards that own it.
# Longest phrase wins during matching (so 'remote chance' beats 'remote').
def _build_term_index():
    idx = {}
    for std in STANDARD_ORDER:
        for b in STANDARDS[std]["bands"]:
            for name in [b["term"]] + b["synonyms"]:
                idx.setdefault(name, set()).add(std)
    # 'remote chance' is PHIA's term, but 'remote' is ICD 203's word; a
    # writer under ICD 203 saying 'a remote chance' is not switching standard.
    idx["remote chance"].add("icd203")
    return idx


TERM_INDEX = _build_term_index()
TERM_RE = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in sorted(TERM_INDEX, key=lambda s: (-len(s), s))) + r")\b",
    re.I,
)

# Modifiers that push a term off its scale ("quite likely", "somewhat unlikely").
HEDGE_RE = re.compile(
    r"\b(quite|fairly|somewhat|rather|pretty|reasonably|moderately|not)\s+"
    r"(likely|unlikely|probable|improbable|certain)\b", re.I)

# Vague likelihood words and phrases (Kent's 'serious possibility' problem).
VAGUE_PHRASES = [
    "significant chance", "real chance", "good chance", "fair chance", "small chance",
    "slim chance", "outside chance", "strong chance", "reasonable chance", "some chance",
    "every chance", "serious possibility", "real possibility", "distinct possibility",
    "strong possibility", "very real possibility", "cannot rule out", "can't rule out",
    "cannot be ruled out", "can not rule out", "cannot exclude", "cannot discount",
    "cannot dismiss", "not impossible", "even chance", "even odds", "50-50", "50/50",
    "fifty-fifty", "possible", "possibly", "potentially", "perhaps", "maybe", "conceivable",
    "conceivably", "might", "could", "may",
]
VAGUE_RE = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in sorted(VAGUE_PHRASES, key=lambda s: (-len(s), s))) + r")\b",
    re.I,
)
# The 2007 NIE explainer names these as *correct* usage, not vagueness: they
# "reflect an unlikely, improbable, or remote event whose consequences are such
# that it warrants mentioning" (NIC, Iran NIE, Nov 2007). Reported as a note.
CONSEQUENCE_FLAGS = {
    "cannot rule out", "can't rule out", "cannot be ruled out", "can not rule out",
    "cannot discount", "cannot dismiss",
}
_CONSEQUENCE_HINT = ("NIC 2007 uses this for an unlikely-but-consequential event that warrants "
                     "mentioning; keep it only in that sense, and give the event its own term")
VAGUE_HINT = {
    "even chance": "'roughly even chance' (ICD 203, 45-55%) or 'about as likely as not' (IPCC, 33-66%)",
    "even odds": "'roughly even odds' (ICD 203, 45-55%)",
    "50-50": "'roughly even chance' (ICD 203, 45-55%)",
    "50/50": "'roughly even chance' (ICD 203, 45-55%)",
    "fifty-fifty": "'roughly even chance' (ICD 203, 45-55%)",
    "could": "capability or likelihood? if likelihood, pick a term",
    "may": "unable to assess, or a likelihood you have not stated? (NIC 2007: 'might'/'may' = unable to assess)",
    "might": "unable to assess, or a likelihood you have not stated? (NIC 2007: 'might'/'may' = unable to assess)",
}
VAGUE_HINT.update({t: _CONSEQUENCE_HINT for t in CONSEQUENCE_FLAGS})
MONTH_PREPS = {"in", "of", "since", "until", "till", "by", "from", "on", "last", "next", "this",
               "early", "mid", "late", "to", "through", "before", "after", "during", "between", "and"}

CONF_RE = re.compile(
    r"\b(?:(very high|high|moderate|medium|low|very low)[- ]confidence"
    r"|confidence (?:level|rating)s?"
    r"|(?:high|moderate|medium|low)\s+analytical confidence"
    r"|AnCR)\b", re.I)
NUM_CONF_RE = re.compile(
    r"\b(\d{1,3}(?:\.\d+)?)\s?(?:%|percent|per cent)\s+(?:confiden(?:t|ce)\b)(?!\s+interval)"
    r"|\b(?:confidence|confident)\s+(?:of|at|is|=|:)\s*(\d{1,3}(?:\.\d+)?)\s?(?:%|percent|per cent)", re.I)
# A percentage counts as a *probability* only when a probability cue sits next
# to it ("a 70 % chance", "probability of about 35 %"); "yields below 60 %" or
# "revenue fell 8 %" are quantities, not likelihoods.
_CUE = r"(?:chance|chances|probability|probabilities|likelihood|odds|risk|likely|probable|certain)"
_PCT = r"(\d{1,3}(?:\.\d+)?)\s?(?:%|percent|per cent)"
PROB_PCT_RE = re.compile(
    r"(?<![\w.])" + _PCT + r"\s+(?:-|–)?\s*" + _CUE + r"\b"                       # 70 % chance / 70 % likely
    r"|\b" + _CUE + r"\s+(?:of|at|is|=|:|near|about|around|roughly|approximately)?\s*"
    r"(?:(?:a|an|about|roughly|around|approximately|some|only|just|at least|at most)\s+)*" + _PCT,  # chance of about 35 %
    re.I)
DEC_RE = re.compile(
    r"\bp\s*=\s*(0?\.\d+|1\.0+)(?![\d.%])"                                            # p = 0.35
    r"|\b(?:probability|probabilities|chance|chances|likelihood|odds)\b[^.;:\n]{0,40}?"
    r"(?<![\d.])(0?\.\d+|1\.0+)(?![\d.%])",                                             # probability of default is 0.35
    re.I)
_SMALL = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|twenty|fifty|hundred|thousand|million)"
ODDS_RE = re.compile(r"\b" + _SMALL + r"[- ]in[- ]" + _SMALL + r"\b(?=[^.;\n]{0,30}\b(?:chance|chances|odds|likelihood|probability)\b)"
                     r"|\b(?:chance|chances|odds|likelihood|probability)\b[^.;\n]{0,30}?\b" + _SMALL + r"[- ]in[- ]" + _SMALL + r"\b", re.I)
# "possible" used enumeratively ("possible outcomes", "as soon as possible") is not a likelihood claim.
POSSIBLE_SKIP_BEFORE = re.compile(r"(?:\bas\s+\w+\s+as|\bwhere(?:ver)?|\bif|\bwhen(?:ever)?|\bwhere)\s*$", re.I)
POSSIBLE_SKIP_AFTER = re.compile(
    r"^\s+(?:outcomes?|options?|explanations?|scenarios?|values?|ranges?|causes?|reasons?|alternatives?|"
    r"hypotheses|hypothesis|futures?|actions?|responses?|courses?|routes?|paths?|worlds?|states?|"
    r"combinations?|configurations?|solutions?|answers?|interpretations?|sources?)\b", re.I)

SENT_SPLIT_RE = re.compile(r"(?<=[.!?])[\"”’)\]]*\s+(?=[\"“(\[]?[A-Z0-9])|\n+")


def sentences(text):
    """Yield (start_offset, sentence_text) — split at sentence ends and newlines."""
    pos = 0
    for m in SENT_SPLIT_RE.finditer(text):
        chunk = text[pos:m.start()]
        if chunk.strip():
            yield pos, chunk
        pos = m.end()
    tail = text[pos:]
    if tail.strip():
        yield pos, tail


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def col_of(text, offset):
    return offset - (text.rfind("\n", 0, offset) + 1) + 1


def _is_month_may(sentence, m):
    """'May' the month, not the modal: capitalised and next to a date/preposition."""
    if sentence[m.start():m.end()] != "May":
        return False
    after = sentence[m.end():m.end() + 8]
    before = sentence[max(0, m.start() - 12):m.start()].strip().split(" ")
    if re.match(r"\s*\d", after):
        return True
    prev = before[-1].lower().strip(",;:()") if before and before[-1] else ""
    return prev in MONTH_PREPS


def lint(text, standard="auto", numbers="require-term"):
    """Return (findings, summary). Each finding: line, rule, severity, snippet, message."""
    findings = []
    seen_standards = {}  # std -> first (line, phrase) among distinctive terms
    strict_mix = standard in ("auto", "icd203", "phia")

    def add(start, m, **kw):
        off = start + (m.start() if m is not None else 0)
        findings.append(dict(line=line_of(text, off), col=col_of(text, off), pos=off, **kw))

    for start, sent in sentences(text):
        line = line_of(text, start)
        terms = [(m.group(1).lower(), m) for m in TERM_RE.finditer(sent)]
        confs = list(CONF_RE.finditer(sent))
        hedges = list(HEDGE_RE.finditer(sent))
        num_conf = list(NUM_CONF_RE.finditer(sent))
        nums = sorted(list(PROB_PCT_RE.finditer(sent)) + list(DEC_RE.finditer(sent)) + list(ODDS_RE.finditer(sent)),
                      key=lambda m: m.start())
        has_term = bool(terms)
        has_number = bool(nums)
        snippet = sent.strip()
        if len(snippet) > 110:
            snippet = snippet[:107].rstrip() + "..."

        # 1. standards bookkeeping (distinctive terms only) and foreign terms
        for phrase, m in terms:
            owners = TERM_INDEX[phrase]
            if standard != "auto" and standard not in owners:
                add(start, m, rule="foreign-term", severity="error", snippet=snippet,
                    message="'%s' is a %s term, not %s — the document declares %s" % (
                        m.group(0), "/".join(LABEL[o] for o in STANDARD_ORDER if o in owners),
                        LABEL[standard], LABEL[standard]))
            if len(owners) == 1:
                std = next(iter(owners))
                seen_standards.setdefault(std, (line, m.group(0)))

        # 2. hedged / modified terms
        for h in hedges:
            add(start, h, rule="hedged-term", severity="error", snippet=snippet,
                message="'%s' moves '%s' off its scale — drop the modifier or choose the neighbouring term" % (
                    h.group(0), h.group(2)))

        # 3. confidence + likelihood in the same sentence (ICD 203 D.6.e(2)(b))
        if confs and (has_term or has_number):
            sev = "error" if strict_mix else "info"
            what = terms[0][1].group(0) if terms else nums[0].group(0)
            note = ("ICD 203: 'must not combine a confidence level and a degree of likelihood ... in the same "
                    "sentence' — state confidence in its own sentence")
            if standard == "ipcc":
                note = ("IPCC AR5 permits a confidence qualifier next to a likelihood term (not required when "
                        "confidence is high/very high) — check it reads as evidence x agreement, not as a second probability")
            add(start, confs[0], rule="mixed-confidence-likelihood", severity=sev, snippet=snippet,
                message="confidence phrase '%s' and likelihood '%s' in one sentence — %s" % (
                    confs[0].group(0), what, note))

        # 4. numeric confidence ("80 % confident")
        for m in num_conf:
            n = m.group(1) or m.group(2)
            add(start, m, rule="numeric-confidence", severity="error", snippet=snippet,
                message="'%s' — confidence is a qualitative level (high / moderate / low), not a probability; "
                        "if %s %% is a likelihood, write the term with the number" % (m.group(0).strip(), n))

        # 5. vague likelihood words (a vague phrase inside a recognised term — 'even chance'
        #    inside 'roughly even chance' — is the term, not a hedge)
        term_spans = [(m.start(), m.end()) for _, m in terms]
        for m in VAGUE_RE.finditer(sent):
            word = m.group(1).lower()
            if any(a <= m.start() and m.end() <= b for a, b in term_spans):
                continue
            if word == "may" and _is_month_may(sent, m):
                continue
            if word == "possible" and (POSSIBLE_SKIP_BEFORE.search(sent[:m.start()]) or POSSIBLE_SKIP_AFTER.match(sent[m.end():])):
                continue
            if word == "could" and re.match(r"\s*(?:not\b|n't)", sent[m.end():]):
                continue
            mapped = has_term or has_number
            flagged = word in CONSEQUENCE_FLAGS
            hint = VAGUE_HINT.get(word, "map to a term of the declared standard, or delete")
            suffix = ""
            if mapped and not flagged:
                suffix = "; sentence also carries a term/number, check the mapping"
            add(start, m, rule="vague-likelihood",
                severity="info" if (mapped or flagged) else "error", snippet=snippet,
                message="'%s' — %s%s" % (m.group(0), hint, suffix))

        # 6. bare numeric probability without a term
        if numbers == "require-term" and has_number and not has_term:
            add(start, nums[0], rule="bare-number", severity="error", snippet=snippet,
                message="'%s' has no estimative term — write the standard's term and keep the number in parentheses"
                        % " ".join(nums[0].group(0).split()))

    # 7. terms from two different standards in one document
    if len(seen_standards) >= 2:
        parts = "; ".join("%s: '%s' (line %d)" % (LABEL[s], ph, ln) for s, (ln, ph) in sorted(seen_standards.items(), key=lambda kv: kv[1][0]))
        first_line = min(ln for ln, _ in seen_standards.values())
        findings.append(dict(line=first_line, col=0, pos=-1, rule="mixed-standards", severity="error", snippet="(document)",
                             message="terms from %d standards in one document — %s; declare one standard" % (len(seen_standards), parts)))

    findings.sort(key=lambda f: (f["line"], f["pos"], f["rule"], f["message"]))
    for f in findings:
        del f["pos"]
    errors = sum(1 for f in findings if f["severity"] == "error")
    infos = len(findings) - errors
    summary = {"errors": errors, "advisories": infos, "standard": standard,
               "standards_seen": sorted(seen_standards), "numbers": numbers}
    return findings, summary


def render_lint(findings, summary, source="<text>"):
    lines = []
    for f in findings:
        where = "%s:%d:%d" % (source, f["line"], f["col"]) if f["col"] else "%s:%d" % (source, f["line"])
        lines.append("%s: [%s] %s — %s" % (where, f["severity"], f["rule"], f["message"]))
        lines.append("    > %s" % f["snippet"])
    seen = ", ".join(LABEL[s] for s in summary["standards_seen"]) or "none distinctive"
    lines.append("lint: %d error(s), %d advisory; declared standard: %s; distinctive terms seen: %s" % (
        summary["errors"], summary["advisories"], summary["standard"], seen))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Demo (the SKILL.md worked example) and selftest
# ---------------------------------------------------------------------------

DEMO_BEFORE = (
    "We assess with high confidence that Vendor A will likely ship its 2 nm process node in 2027. "
    "There is a significant chance the second fab slips, and it is possible that yields stay below 60 %. "
    "We think there is roughly a 70 % chance that Vendor B loses its lead customer. "
    "A price war is a realistic possibility."
)

DEMO_AFTER = (
    "Vendor A will likely (about 70 %) ship its 2 nm process node in 2027. "
    "There is a roughly even chance (45-55 %) that the second fab slips by a quarter or more, "
    "and it is unlikely (20-45 %) that yields stay below 60 %. "
    "Vendor B will likely (70 %) lose its lead customer. "
    "A price war is unlikely (about 30 %). "
    "We have moderate confidence in these judgments: two corroborating supplier reports and one dated "
    "public filing; the fab-slip judgment rests on the assumption that tool deliveries stay on schedule. "
    "A slip in the lithography tool delivery date would move the fab-slip judgment to likely."
)


def run_demo():
    print("# BEFORE — lint --standard icd203")
    f, s = lint(DEMO_BEFORE, "icd203")
    print(render_lint(f, s, "before.md"))
    print()
    print("# AFTER — lint --standard icd203")
    f, s = lint(DEMO_AFTER, "icd203")
    print(render_lint(f, s, "after.md"))
    print()
    print("# term --p 0.7 --standard phia")
    print(render_term(term_for(0.7, "phia")))
    print()
    print("# term --p 0.5 --standard phia   (deliberate gap)")
    print(render_term(term_for(0.5, "phia")))
    print()
    print("# prob --term 'realistic possibility' --standard phia")
    print(render_prob("realistic possibility", prob_for("realistic possibility", "phia"), "phia"))
    return 0


def run_selftest():
    checks = []

    def check(name, cond, detail=""):
        checks.append(bool(cond))
        print("%s  %s%s" % ("PASS" if cond else "FAIL", name, (" — " + str(detail)) if detail and not cond else ""))
        if not cond:
            print("SELFTEST FAILED at: %s" % name, file=sys.stderr)
            sys.exit(1)

    # --- ICD 203 mapping (table verbatim: 01-05, 05-20, 20-45, 45-55, 55-80, 80-95, 95-99) ---
    r = term_for(0.70, "icd203")
    check("icd203 0.70 -> likely", r["kind"] == "term" and r["matches"][0]["term"] == "likely", r)
    check("icd203 likely synonyms probable/probably", r["matches"][0]["synonyms"] == ["probable", "probably"])
    r = term_for(0.03, "icd203")
    check("icd203 0.03 -> almost no chance", r["kind"] == "term" and r["matches"][0]["term"] == "almost no chance", r)
    r = term_for(0.50, "icd203")
    check("icd203 0.50 -> roughly even chance", r["kind"] == "term" and r["matches"][0]["term"] == "roughly even chance", r)
    r = term_for(0.97, "icd203")
    check("icd203 0.97 -> almost certain", r["kind"] == "term" and r["matches"][0]["term"] == "almost certain", r)
    r = term_for(0.20, "icd203")
    check("icd203 0.20 -> boundary very unlikely / unlikely",
          r["kind"] == "boundary" and [m["term"] for m in r["matches"]] == ["very unlikely", "unlikely"], r)
    r = term_for(0.005, "icd203")
    check("icd203 0.005 -> outside table (01-99%)", r["kind"] == "outside", r)
    r = term_for(0.995, "icd203")
    check("icd203 0.995 -> outside table (01-99%)", r["kind"] == "outside", r)

    # --- PHIA mapping (>0-~5, ~10-~20, ~25-~35, ~40-<50, ~55-~75, ~80-~90, ~95-<100) ---
    r = term_for(0.70, "phia")
    check("phia 0.70 -> likely", r["kind"] == "term" and r["matches"][0]["term"] == "likely", r)
    r = term_for(0.45, "phia")
    check("phia 0.45 -> realistic possibility", r["kind"] == "term" and r["matches"][0]["term"] == "realistic possibility", r)
    r = term_for(0.85, "phia")
    check("phia 0.85 -> highly likely", r["kind"] == "term" and r["matches"][0]["term"] == "highly likely", r)
    r = term_for(0.02, "phia")
    check("phia 0.02 -> remote chance", r["kind"] == "term" and r["matches"][0]["term"] == "remote chance", r)
    r = term_for(0.50, "phia")
    check("phia 0.50 -> gap (realistic possibility <50 | likely 55)",
          r["kind"] == "gap" and [g["term"] for g in r["gap_between"]] == ["realistic possibility", "likely"], r)
    r = term_for(0.78, "phia")
    check("phia 0.78 -> gap (likely 75 | highly likely 80)",
          r["kind"] == "gap" and [g["term"] for g in r["gap_between"]] == ["likely", "highly likely"], r)
    r = term_for(0.07, "phia")
    check("phia 0.07 -> gap (remote chance | highly unlikely)",
          r["kind"] == "gap" and [g["term"] for g in r["gap_between"]] == ["remote chance", "highly unlikely"], r)
    r = term_for(0.0, "phia")
    check("phia 0.0 -> outside (>0%)", r["kind"] == "outside", r)
    r = term_for(1.0, "phia")
    check("phia 1.0 -> outside (<100%)", r["kind"] == "outside", r)
    check("phia has no 'roughly even chance'", prob_for("roughly even chance", "phia") == [])

    # --- IPCC mapping (nested bands) ---
    r = term_for(0.70, "ipcc")
    check("ipcc 0.70 -> likely (only core band)", r["kind"] == "term" and r["matches"][0]["term"] == "likely", r)
    check("ipcc 0.70 -> also 'more likely than not' as AR4 extra", [e["term"] for e in r["extra"]] == ["more likely than not"], r)
    r = term_for(0.95, "ipcc")
    check("ipcc 0.95 -> nested: very likely then likely",
          r["kind"] == "nested" and [m["term"] for m in r["matches"]] == ["very likely", "likely"], r)
    check("ipcc 0.95 -> extras extremely likely, more likely than not",
          [e["term"] for e in r["extra"]] == ["extremely likely", "more likely than not"], r)
    r = term_for(0.995, "ipcc")
    check("ipcc 0.995 -> virtually certain narrowest",
          r["kind"] == "nested" and r["matches"][0]["term"] == "virtually certain", r)
    r = term_for(0.005, "ipcc")
    check("ipcc 0.005 -> exceptionally unlikely narrowest",
          r["kind"] == "nested" and r["matches"][0]["term"] == "exceptionally unlikely", r)
    r = term_for(0.50, "ipcc")
    check("ipcc 0.50 -> about as likely as not", r["kind"] == "term" and r["matches"][0]["term"] == "about as likely as not", r)

    # --- prob lookups ---
    hits = prob_for("realistic possibility", "phia")
    check("prob realistic possibility (phia) = ≈40% - <50%", len(hits) == 1 and hits[0][1]["range"] == "≈40% - <50%", hits)
    hits = prob_for("Highly Improbable", "icd203")
    check("prob highly improbable (icd203) -> very unlikely 05-20%", hits and hits[0][1]["term"] == "very unlikely" and hits[0][1]["range"] == "05-20%", hits)
    hits = prob_for("likely")
    check("prob likely across standards -> 3 hits", [s for s, _ in hits] == ["icd203", "phia", "ipcc"], hits)
    check("prob virtually certain (ipcc) = 99-100%", prob_for("virtually certain", "ipcc")[0][1]["range"] == "99-100% probability")
    check("prob 'realistic possibility' absent from icd203", prob_for("realistic possibility", "icd203") == [])

    # --- lint fixtures ---
    clean = ("Vendor A will likely (about 70 %) ship the node in 2027. "
             "It is unlikely (20-45 %) that yields stay below 60 %. "
             "We have moderate confidence in these judgments: two corroborating reports and one dated filing. "
             "Revenue fell 8 % in May 2026, and the board meets again in May.")
    f, s = lint(clean, "icd203")
    check("clean paragraph -> 0 errors", s["errors"] == 0, f)
    check("clean paragraph -> 0 advisories", s["advisories"] == 0, f)

    three = ("We assess with high confidence that the launch is likely in 2027. "
             "It is possible that the supplier defaults. "
             "There is a 70 % chance that the merger closes.")
    f, s = lint(three, "icd203")
    rules = [x["rule"] for x in f if x["severity"] == "error"]
    check("three-violation paragraph -> exactly 3 errors", s["errors"] == 3, f)
    check("three-violation rules", rules == ["mixed-confidence-likelihood", "vague-likelihood", "bare-number"], rules)
    check("three-violation lines 1,1,1 (single line)", [x["line"] for x in f] == [1, 1, 1], f)
    check("three-violation columns ascend", [x["col"] for x in f] == sorted(x["col"] for x in f) and f[0]["col"] == 16, f)

    mixed = "It is a realistic possibility that X.\nIt is a roughly even chance that Y."
    f, s = lint(mixed, "auto")
    check("mixed standards detected (phia + icd203)", any(x["rule"] == "mixed-standards" for x in f) and s["standards_seen"] == ["icd203", "phia"], f)
    check("mixed-standards finding sits on line 1", [x["line"] for x in f if x["rule"] == "mixed-standards"] == [1], f)
    f, s = lint("It is a realistic possibility that X.", "icd203")
    check("foreign term under declared icd203", [x["rule"] for x in f] == ["foreign-term"], f)
    f, s = lint("It is quite likely that X.", "icd203")
    check("hedged term flagged", [x["rule"] for x in f] == ["hedged-term"], f)
    f, s = lint("We are 80 % confident that X occurs.", "icd203")
    check("numeric confidence flagged", "numeric-confidence" in [x["rule"] for x in f], f)
    f, s = lint("It is likely (medium confidence) that X.", "ipcc")
    check("ipcc: confidence next to likelihood is advisory only", s["errors"] == 0 and s["advisories"] == 1, f)
    f, s = lint("There is a 70 % chance that X.", "icd203", numbers="allow")
    check("bare number allowed with --numbers allow", s["errors"] == 0, f)
    f, s = lint("Sales may reach 5 % in May 2027.", "icd203")
    check("'may' modal flagged, 'May' month skipped", [x["rule"] for x in f] == ["vague-likelihood"] and "'may'" in f[0]["message"], f)
    f, s = lint("Line one is fine.\nLine two: it could happen.", "icd203")
    check("line numbers reported", f and f[0]["line"] == 2, f)

    f, s = lint("It is possible that yields stay below 60 %.", "icd203")
    check("'60 %' yield is a quantity, not a bare probability", [x["rule"] for x in f] == ["vague-likelihood"], f)
    f, s = lint("We considered three possible explanations as soon as possible, and could not verify them.", "icd203")
    check("enumerative 'possible' and 'could not' are skipped", f == [], f)
    f, s = lint("There is a roughly even chance (45-55 %) that the fab slips.", "icd203")
    check("'even chance' inside 'roughly even chance' is the term, not a hedge", f == [], f)
    f, s = lint("The 95 % confidence interval is wide.", "icd203")
    check("'confidence interval' is not numeric confidence", f == [], f)
    f, s = lint("There is a 1-in-4 chance of a slip.", "icd203")
    check("odds form '1-in-4 chance' is a bare number", [x["rule"] for x in f] == ["bare-number"], f)
    f, s = lint("The probability of default is 0.35 this year.", "icd203")
    check("decimal probability without a term is a bare number", [x["rule"] for x in f] == ["bare-number"], f)
    f, s = lint("Sales rose 8 % in May 2026, and yields reached 60 %.", "icd203")
    check("plain percentages are not probabilities", f == [], f)

    # determinism of the report renderer
    a = render_lint(*lint(DEMO_BEFORE, "icd203"))
    b = render_lint(*lint(DEMO_BEFORE, "icd203"))
    check("render is deterministic", a == b)

    print("ALL %d CHECKS PASSED" % len(checks))
    print("selftest OK")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser():
    p = argparse.ArgumentParser(
        description="Words of estimative probability: map probabilities to the terms of ICD 203, "
                    "the UK PHIA yardstick or the IPCC AR5 scale, and lint prose for vague or mixed usage.")
    p.add_argument("--selftest", action="store_true", help="run hand-verified checks and exit 0")
    p.add_argument("--demo", action="store_true", help="print the SKILL.md worked example")
    sub = p.add_subparsers(dest="command")

    t = sub.add_parser("term", help="probability -> term(s) of a standard")
    t.add_argument("--p", type=float, required=True, help="probability in [0,1] (or 0-100 with %%)")
    t.add_argument("--standard", choices=STANDARD_ORDER, default="icd203")
    t.add_argument("--json", action="store_true")

    q = sub.add_parser("prob", help="term -> range")
    q.add_argument("--term", required=True)
    q.add_argument("--standard", choices=STANDARD_ORDER, default=None, help="default: search all standards")
    q.add_argument("--json", action="store_true")

    l = sub.add_parser("lint", help="flag vague / mixed / bare-number usage; exit 2 on any error")
    src = l.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="text or markdown file ('-' for stdin)")
    src.add_argument("--text", help="inline text")
    l.add_argument("--standard", choices=("auto",) + STANDARD_ORDER, default="auto",
                   help="declared standard; 'auto' only reports mixing (default)")
    l.add_argument("--numbers", choices=("require-term", "allow"), default="require-term",
                   help="require a term next to every numeric probability (default) or allow bare numbers")
    l.add_argument("--json", action="store_true")

    b = sub.add_parser("table", help="print a standard's table with its citation")
    b.add_argument("--standard", choices=STANDARD_ORDER, default=None, help="default: all three")
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo:
        return run_demo()
    if not args.command:
        parser.error("choose a command: term | prob | lint | table  (or --demo / --selftest)")

    if args.command == "term":
        p = args.p
        if p > 1.0 and p <= 100.0:
            p = p / 100.0
        if not 0.0 <= p <= 1.0:
            parser.error("--p must be a probability in [0, 1] (or a percentage up to 100)")
        res = term_for(p, args.standard)
        print(json.dumps(res, indent=1, sort_keys=True, ensure_ascii=False) if args.json else render_term(res))
        return 0

    if args.command == "prob":
        hits = prob_for(args.term, args.standard)
        if args.json:
            print(json.dumps([{"standard": s, **{k: v for k, v in b.items()}} for s, b in hits],
                             indent=1, sort_keys=True, ensure_ascii=False))
        else:
            print(render_prob(args.term, hits, args.standard))
        return 0 if hits else 1

    if args.command == "lint":
        if args.text is not None:
            text, source = args.text, "<text>"
        elif args.file == "-":
            text, source = sys.stdin.read(), "<stdin>"
        else:
            try:
                with open(args.file, encoding="utf-8") as fh:
                    text = fh.read()
            except OSError as exc:
                parser.error("could not read %s: %s" % (args.file, exc))
            source = args.file
        findings, summary = lint(text, args.standard, args.numbers)
        if args.json:
            print(json.dumps({"source": source, "summary": summary, "findings": findings},
                             indent=1, sort_keys=True, ensure_ascii=False))
        else:
            print(render_lint(findings, summary, source))
        return 1 if summary["errors"] else 0

    if args.command == "table":
        stds = (args.standard,) if args.standard else STANDARD_ORDER
        print("\n\n".join(render_table(s) for s in stds))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
