#!/usr/bin/env python3
"""funding.py — deterministic parser for funding-round announcements.

Implements the normalisation rules of ../SKILL.md so that the arithmetic and
the round vocabulary are never re-derived by hand:

  * amount   money strings -> {value, currency, notes, confidence_penalty}.
             A range collapses to its MIDPOINT, "up to X" is a CAP, and a bare
             "$" stays ambiguous ("USD?") because $ is also CAD/AUD/SGD/HKD.
             No FX conversion is ever applied: the value stays in the currency
             the source used and the currency is reported beside it.
  * stage    round phrasing -> the canonical stage vocabulary (Pre-seed, Seed,
             Series A..Z with optional -n, Bridge, Growth, Secondary,
             Public (IPO) / Public (Direct) / Public (SPAC)). Phrasing that
             names no stage ("its latest round") stays blank, never guessed.
  * extract  rule-based pass over an article -> the FundingEvent record of
             ../SKILL.md plus the confidence trace that produced its score.

Confidence (0-100 scale, SKILL.md "Emit the record"):

    base                          60
    + explicit stage             +15
    + explicit lead investor     +10
    + exact single amount        +10   (one raise amount, not a range/cap/approx)
    - range or "up to"           -15
    - ambiguous currency         -10   (a bare "$" with no US$/USD marker)
    then clamped to [0, 100].

Fields the text does not state are omitted, never invented; a valuation is
never written into the amount field.

Offline, deterministic, standard library only. Python 3.9+.

Usage:
    python3 funding.py amount  "$47M to $50M"
    python3 funding.py amount  "up to EUR 50 million" --json
    python3 funding.py stage   "closed its Series B-2 financing"
    python3 funding.py extract --text "Acme raised $47M in Series B funding ..."
    python3 funding.py extract --file article.txt --source-url URL --source-grade B2
    python3 funding.py extract --demo        # the SKILL.md worked example
    python3 funding.py --selftest            # hand-checked cases; prints "selftest OK"

Exit codes: 0 success, 1 invalid input / nothing parseable.
"""

import argparse
import json
import re
import sys
from collections import OrderedDict

# --------------------------------------------------------------------------
# 1 - Money normalisation (SKILL.md step 1 "Normalize the amount")
# --------------------------------------------------------------------------

# Prefix markers, longest-first at match time. "$" is deliberately last and
# deliberately ambiguous: USD, CAD, AUD, SGD, HKD, NZD all write it "$".
CURRENCY_PREFIXES = [
    ("US$", "USD"), ("U.S.$", "USD"), ("USD", "USD"),
    ("CA$", "CAD"), ("C$", "CAD"), ("CAD", "CAD"),
    ("AU$", "AUD"), ("A$", "AUD"), ("AUD", "AUD"),
    ("S$", "SGD"), ("SGD", "SGD"),
    ("HK$", "HKD"), ("HKD", "HKD"),
    ("NZ$", "NZD"), ("NZD", "NZD"),
    ("R$", "BRL"), ("BRL", "BRL"),
    ("EUR", "EUR"), ("€", "EUR"),
    ("GBP", "GBP"), ("£", "GBP"),
    ("CN¥", "CNY"), ("CNY", "CNY"), ("RMB", "CNY"),
    ("JPY", "JPY"), ("¥", "JPY"),
    ("INR", "INR"), ("₹", "INR"), ("Rs.", "INR"), ("Rs", "INR"),
    ("KRW", "KRW"), ("₩", "KRW"),
    ("ILS", "ILS"), ("₪", "ILS"),
    ("CHF", "CHF"), ("SEK", "SEK"), ("NOK", "NOK"), ("DKK", "DKK"),
    ("$", "USD?"),
]

# Suffix words ("10 million euros"). "dollars" alone is as ambiguous as "$".
CURRENCY_WORDS = [
    ("U.S. dollars", "USD"), ("US dollars", "USD"),
    ("Canadian dollars", "CAD"), ("Australian dollars", "AUD"),
    ("Singapore dollars", "SGD"), ("Hong Kong dollars", "HKD"),
    ("dollars", "USD?"), ("dollar", "USD?"),
    ("euros", "EUR"), ("euro", "EUR"),
    ("pounds sterling", "GBP"), ("pounds", "GBP"), ("sterling", "GBP"),
    ("yen", "JPY"), ("rupees", "INR"), ("rupee", "INR"),
    ("yuan", "CNY"), ("renminbi", "CNY"), ("won", "KRW"),
    ("francs", "CHF"), ("shekels", "ILS"), ("reais", "BRL"),
]

# South-Asian scale words are part of the grammar: 1 crore = 10^7, 1 lakh = 10^5.
UNIT_MULT = {
    "thousand": 1e3, "k": 1e3,
    "million": 1e6, "m": 1e6, "mm": 1e6,
    "billion": 1e9, "b": 1e9, "bn": 1e9,
    "trillion": 1e12, "t": 1e12,
    "crore": 1e7, "lakh": 1e5,
}

# Modifiers that sit in front of the figure. A cap is a hard ceiling (SKILL.md:
# treat "up to $X" as the cap and lower the confidence); the rest only tell us
# the figure is not exact, so they forfeit the exact-amount bonus.
CAP_WORDS = ["up to", "as much as", "no more than", "a maximum of", "at most"]
FLOOR_WORDS = ["over", "more than", "north of", "at least", "in excess of",
               "upwards of", "just over"]
APPROX_WORDS = ["nearly", "almost", "approximately", "about", "roughly",
                "around", "circa", "just under", "some", "~"]

SYMBOL_CAVEAT = {
    "¥": "'¥' read as JPY; CNY also uses ¥ - confirm from the source",
    "$": "'$' is ambiguous (USD/CAD/AUD/SGD/HKD/NZD); no US$/USD marker in the text",
}


def _alt(strings):
    """Regex alternation, longest literal first so 'US$' beats '$'."""
    return "|".join(re.escape(s) for s in sorted(set(strings), key=len, reverse=True))


_CUR_ALT = _alt([c for c, _ in CURRENCY_PREFIXES])
_CURW_ALT = _alt([w for w, _ in CURRENCY_WORDS])
_UNIT_ALT = "thousands?|millions?|billions?|trillions?|crores?|lakhs?|bn|mm|k|m|b|t"
_NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"

RAW_MONEY_RE = re.compile(
    r"(?:(?P<cur>" + _CUR_ALT + r")\s?)?"
    r"(?P<num>" + _NUM + r")"
    r"(?:[\s\-]?(?P<unit>" + _UNIT_ALT + r")\b)?"
    r"(?:\s+(?P<curw>" + _CURW_ALT + r")\b)?",
    re.IGNORECASE,
)

_CUR_LOOKUP = {k.lower(): v for k, v in CURRENCY_PREFIXES}
_CURW_LOOKUP = {k.lower(): v for k, v in CURRENCY_WORDS}

# A range connector. "and" only counts after "between", so that
# "raised $10M and $5M in debt" is not silently averaged.
CONNECTOR_RE = re.compile(r"\s*(-|–|—|to\b|through\b|and\b)\s*", re.IGNORECASE)


def _scale(num_s, unit_s):
    v = float(num_s.replace(",", ""))
    if unit_s:
        u = unit_s.lower()
        if u.endswith("s") and u[:-1] in UNIT_MULT:
            u = u[:-1]
        v *= UNIT_MULT[u]
    return v


def _tidy(v):
    """Integral values print as integers; everything else keeps its float."""
    r = round(v)
    return int(r) if abs(v - r) < 1e-6 else v


def money_str(value, currency):
    if isinstance(value, int):
        return "%s %s" % (format(value, ","), currency)
    return "%s %s" % (format(value, ",.2f"), currency)


def _raw_mentions(text):
    out = []
    for m in RAW_MONEY_RE.finditer(text):
        cur, curw, unit = m.group("cur"), m.group("curw"), m.group("unit")
        out.append({
            "start": m.start(), "end": m.end(), "text": m.group(0),
            "cur": cur, "curw": curw, "unit": unit, "num": m.group("num"),
            "is_money": bool(cur or curw),
        })
    return out


def _range_partner(text, raws, i):
    """Index of the figure that closes a range opened by raws[i], else None."""
    a = raws[i]
    m = CONNECTOR_RE.match(text, a["end"])
    if not m or m.end() == m.start():
        return None
    conn = m.group(1).lower()
    if conn == "and":
        before = text[max(0, a["start"] - 14):a["start"]].lower()
        if "between" not in before:
            return None
    for j in range(i + 1, len(raws)):
        if raws[j]["start"] == m.end():
            return j
        if raws[j]["start"] > m.end():
            break
    return None


def _currency_of(a, b, assume_usd):
    notes = []
    sym = a["cur"] or (b or {}).get("cur")
    word = a["curw"] or (b or {}).get("curw")
    code = None
    if sym:
        code = _CUR_LOOKUP[sym.lower()]
    elif word:
        code = _CURW_LOOKUP[word.lower()]
    if code is None:
        return None, notes
    caveat = SYMBOL_CAVEAT.get(sym) if sym else None
    if code == "USD?":
        if assume_usd:
            code = "USD"
            notes.append("bare '$' read as USD (--assume-usd)")
        elif caveat:
            notes.append(caveat)
        else:
            notes.append("'dollars' is ambiguous (USD/CAD/AUD/SGD); no country marker")
    elif caveat:
        notes.append(caveat)
    return code, notes


def _modifier(text, start):
    """Cap / floor / approximation word immediately in front of the figure."""
    window = text[max(0, start - 26):start].lower()
    for kind, words in (("cap", CAP_WORDS), ("floor", FLOOR_WORDS), ("approx", APPROX_WORDS)):
        for w in words:
            if re.search(re.escape(w) + r"\s*$", window):
                return kind, w
    return None, None


def scan_money(text, assume_usd=False):
    """All money figures in `text`, ranges already collapsed to midpoints.

    Each mention is a dict: start, end, text, value, currency, notes,
    confidence_penalty, exact (False once a range/cap/approximation is in play).
    """
    raws = _raw_mentions(text)
    consumed = set()
    out = []
    for i, a in enumerate(raws):
        if i in consumed or not a["is_money"]:
            continue
        j = _range_partner(text, raws, i)
        b = raws[j] if j is not None else None
        if b is not None:
            consumed.add(j)
        code, notes = _currency_of(a, b, assume_usd)
        penalty = 0
        exact = True
        if b is None:
            value = _scale(a["num"], a["unit"])
        else:
            ua = a["unit"] or b["unit"]
            ub = b["unit"] or a["unit"]
            lo, hi = sorted((_scale(a["num"], ua), _scale(b["num"], ub)))
            value = (lo + hi) / 2.0
            notes.append("range %s to %s -> midpoint (SKILL.md step 1)"
                         % (format(_tidy(lo), ","), format(_tidy(hi), ",")))
            penalty += 15
            exact = False
        kind, word = _modifier(text, a["start"])
        if kind == "cap":
            notes.append("cap ('%s') - the figure is a ceiling, not the amount raised" % word)
            penalty += 15
            exact = False
        elif kind == "floor":
            notes.append("lower bound ('%s') - the true figure may be higher" % word)
            exact = False
        elif kind == "approx":
            notes.append("approximate ('%s') - stated figure kept as-is" % word)
            exact = False
        if code and code.endswith("?"):
            penalty += 10
        elif code and code != "USD":
            notes.append("stated in %s; no FX conversion applied" % code)
        end = b["end"] if b is not None else a["end"]
        out.append({
            "start": a["start"], "end": end, "text": text[a["start"]:end],
            "value": _tidy(value), "currency": code or "unknown",
            "notes": notes, "confidence_penalty": penalty, "exact": exact,
        })
    return out


def normalise_amount(text, assume_usd=False):
    """First money figure in `text` (the `amount` subcommand), or None."""
    found = scan_money(text, assume_usd=assume_usd)
    return found[0] if found else None


# --------------------------------------------------------------------------
# 2 - Stage vocabulary (SKILL.md step 2 "Identify the stage")
# --------------------------------------------------------------------------

# Ordered: the first pattern that matches earliest in the string wins, so the
# narrow spellings (pre-seed, pre-Series A) are written to exclude the wide
# ones. `None` as the stage means "recognised phrasing, but not a stage" -
# the field is left blank rather than guessed.
STAGE_RULES = [
    (r"\bpre[\s-]?seed\b", "Pre-seed", ""),
    (r"\bpre[\s-]?series\s+[A-Z]\b", None,
     "'pre-Series A' names no canonical stage (usually a bridge) - confirm before filling"),
    (r"\bseries\s+([A-Z])[\s-]?(\d)\b", "Series", ""),
    (r"\bseries\s+([A-Z])\b", "Series", ""),
    (r"(?<!pre-)(?<!pre )\bseed\b", "Seed", ""),
    (r"\b(bridge|extension)\s+(round|financing|note)\b", "Bridge", ""),
    (r"\bbridge\b", "Bridge", ""),
    (r"\b(tender offer|secondary (sale|round|transaction|offering))\b", "Secondary", ""),
    (r"\bsecondary\b", "Secondary", ""),
    (r"\b(growth (equity|round|financing|capital)|late[\s-]stage|crossover|mezzanine|pre[\s-]?IPO)\b",
     "Growth", ""),
    (r"\b(initial public offering|IPO)\b", "Public (IPO)", ""),
    (r"\bdirect listing\b", "Public (Direct)", ""),
    (r"\b(SPAC|blank[\s-]cheque|blank[\s-]check|de[\s-]SPAC)\b", "Public (SPAC)", ""),
    (r"\b(venture debt|debt financing|credit facility|term loan|revenue[\s-]based financing)\b", None,
     "debt, not a priced equity round - stage left blank (SKILL.md: do not guess the stage)"),
    (r"\b(grant|non[\s-]dilutive award)\b", None,
     "non-dilutive grant, not a venture round - stage left blank"),
]

NO_STAGE_NOTE = ("no canonical stage named (e.g. 'its latest round') - "
                 "left blank per SKILL.md step 2; rely on amount + date")


def map_stage(text):
    """Canonical stage for a phrase. Returns (stage, notes); stage '' = unknown."""
    best = None
    for pattern, stage, note in STAGE_RULES:
        m = re.search(pattern, text, re.IGNORECASE)
        if not m:
            continue
        if best is None or m.start() < best[0]:
            best = (m.start(), m, stage, note)
    if best is None:
        return "", [NO_STAGE_NOTE]
    _, m, stage, note = best
    notes = [note] if note else []
    if stage is None:
        return "", notes
    if stage == "Series":
        letter = m.group(1).upper()
        stage = "Series %s" % letter
        if m.lastindex and m.lastindex >= 2 and m.group(2):
            stage = "%s-%s" % (stage, m.group(2))
    return stage, notes


# --------------------------------------------------------------------------
# 3 - Article extraction (SKILL.md steps 1-7)
# --------------------------------------------------------------------------

RAISE_VERB_RE = re.compile(
    r"\b(raised|raises|raising|closed|closes|has closed|secured|secures|landed|"
    r"announced|announces|banked|netted|nets|completed|completes|picked up|"
    r"pulled in|brought in)\b", re.IGNORECASE)

ROUND_NOUN_RE = re.compile(
    r"\b(round|funding|financing|investment|raise|capital injection|equity)\b", re.IGNORECASE)

# Figures that are never the amount raised. Cues are split by where they sit
# relative to the figure, because "raised $12M, bringing its total funding to
# $85M" disqualifies the $85M and not the $12M.
NOT_AMOUNT_BACK_RE = re.compile(
    r"\b(total (funding|raised|capital|investment)|raised a total|to date|"
    r"revenues? of|ARR of|sales of|market (size|of)|TAM of|acquisition of|"
    r"acquired for|bought for|salary of|payroll of|debt facility of|"
    r"credit facility of|worth)\b", re.IGNORECASE)
NOT_AMOUNT_FWD_RE = re.compile(
    r"^\W{0,4}(in )?(ARR|annual recurring revenue|revenue|sales|market cap|"
    r"of (revenue|ARR)|customers|users|employees)\b", re.IGNORECASE)

VALUATION_POST_RE = re.compile(r"post[\s-]?money", re.IGNORECASE)
VALUATION_PRE_RE = re.compile(r"pre[\s-]?money", re.IGNORECASE)
VALUATION_ANY_RE = re.compile(r"\b(valuation|valuing|valued|values|worth)\b", re.IGNORECASE)

# Proper-noun run: an initial-capital word, then further capitalised words or the
# lowercase connectives that appear inside firm names ("Bank of the West",
# "de Vries Capital").
#
# SECURITY: this pattern MUST NOT be compiled with re.IGNORECASE. Under
# IGNORECASE the `[A-Z]…` branch also matches `de|van|von|of|and`, so the
# alternation inside the unbounded `(?:…)*` becomes ambiguous and the engine
# explores 2^k parses. A 146-byte input then takes ~22 s. Patterns that embed
# NAME therefore stay case-sensitive and scope case-insensitivity to their
# literal parts with inline `(?i:...)` groups.
NAME = r"[A-Z][\w&.'’-]*(?:\s+(?:[A-Z][\w&.'’-]*|de|van|von|of|and\s+[A-Z][\w&.'’-]*))*"
LIST_STOP = (r"(?=[.;:]|,?\s+(?:with|alongside|joined|which|who|in\s+a|at\s+a|"
             r"and\s+existing|and\s+returning|bringing|valuing|according|as\s+part|"
             r"the\s+(?:company|round|deal|startup|firm|financing))\b|$)")

LEAD_PATTERNS = [
    re.compile(r"\bco-led by\s+(?P<names>.+?)" + LIST_STOP, re.IGNORECASE),
    re.compile(r"\bled by\s+(?P<names>.+?)" + LIST_STOP, re.IGNORECASE),
    re.compile(r"(?P<names>" + NAME + r")\s+(?i:(?:co-)?led the (?:round|financing|investment|deal))"),
    re.compile(r"(?P<names>" + NAME + r")\s+(?i:priced the round)"),
]

PARTICIPANT_PATTERNS = [
    re.compile(r"\b(?:with|and)\s+participation\s+(?:from|by|of)\s+(?P<names>.+?)" + LIST_STOP,
               re.IGNORECASE),
    re.compile(r"\bjoined by\s+(?P<names>.+?)" + LIST_STOP, re.IGNORECASE),
    re.compile(r"\balongside\s+(?P<names>.+?)" + LIST_STOP, re.IGNORECASE),
    re.compile(r"\bwith (?:additional )?(?:support|backing) from\s+(?P<names>.+?)" + LIST_STOP,
               re.IGNORECASE),
    re.compile(r"(?P<names>" + NAME + r"(?:\s*,\s*" + NAME + r")*(?:\s+and\s+" + NAME + r")?)"
               r"\s+(?i:(?:also\s+)?participat(?:ed|ing))\b"),
]

INVESTOR_PREFIX_RE = re.compile(
    r"^(?:existing|returning|current|new|other|both|several|the)\s+"
    r"(?:investors?|backers?|shareholders?)?\s*", re.IGNORECASE)

PROCEEDS_PATTERNS = [
    re.compile(r"\b(?:will|plans? to|intends? to|says? it will)\s+use\s+(?:the\s+)?"
               r"(?:funds|proceeds|money|capital|financing|investment)\s+to\s+(?P<use>[^.;]+)",
               re.IGNORECASE),
    re.compile(r"\b(?:funds|proceeds|money|capital|round|financing|investment)\s+will\s+be\s+"
               r"(?:used|deployed)\s+to\s+(?P<use>[^.;]+)", re.IGNORECASE),
    re.compile(r"\bto\s+(?P<use>(?:accelerate|expand|scale|hire|build|fund|grow|launch|"
               r"develop|invest|double|open|commercialis|commercializ|advance|support|"
               r"deploy|broaden|extend|ramp)[^.;]+)", re.IGNORECASE),
]

MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"])}
MONTHS.update({m[:3]: i + 1 for i, m in enumerate(sorted(MONTHS, key=lambda k: MONTHS[k]))})
_MONTH_ALT = _alt(list(MONTHS))

DATE_PATTERNS = [
    re.compile(r"\b(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})\b"),
    re.compile(r"\b(?P<mon>" + _MONTH_ALT + r")\.?\s+(?P<d>\d{1,2})(?:st|nd|rd|th)?,?\s+(?P<y>\d{4})\b",
               re.IGNORECASE),
    re.compile(r"\b(?P<d>\d{1,2})(?:st|nd|rd|th)?\s+(?P<mon>" + _MONTH_ALT + r")\.?\s+(?P<y>\d{4})\b",
               re.IGNORECASE),
]

URL_RE = re.compile(r"https?://[^\s<>\"')]+")

SENTENCE_ABBR = {"inc", "ltd", "llc", "corp", "co", "plc", "gmbh", "sa", "bv", "u.s", "mr",
                 "ms", "dr", "no", "vs", "st", "approx", "jan", "feb", "mar", "apr", "jun",
                 "jul", "aug", "sep", "sept", "oct", "nov", "dec"}

GENERIC_LEAD_TOKENS = {"The", "A", "An", "On", "In", "Today", "Yesterday", "This", "That",
                       "After", "Following", "Meanwhile", "It", "Its", "Last", "Earlier"}
SUBJECT_STOP = {"based", "startup", "company", "firm", "maker", "developer", "provider",
                "platform", "business", "group", "unicorn", "venture", "scale-up", "which",
                "that", "said", "announced", "today", "reported", "and"}


def normalise_text(raw):
    """Collapse whitespace so character offsets and windows behave predictably."""
    return re.sub(r"\s+", " ", raw).strip()


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = []
    for p in parts:
        if out:
            tail = re.search(r"([A-Za-z.]+)\.$", out[-1].strip())
            if tail and tail.group(1).lower().strip(".") in SENTENCE_ABBR:
                out[-1] = out[-1] + " " + p
                continue
        out.append(p)
    return [s for s in (p.strip() for p in out) if s]


def sentence_spans(text):
    spans, cursor = [], 0
    for s in split_sentences(text):
        i = text.find(s, cursor)
        if i < 0:
            i = cursor
        spans.append((i, i + len(s), s))
        cursor = i + len(s)
    return spans


def sentence_of(spans, pos):
    for start, end, s in spans:
        if start <= pos < end:
            return start, s
    return (0, spans[0][2]) if spans else (0, "")


def split_names(blob):
    """Split an investor list into names; drop qualifiers, keep '&' inside names."""
    blob = re.sub(r"\s+", " ", blob).strip().strip(",;:. ")
    if not blob:
        return []
    parts = re.split(r",\s*and\s+|,\s*|\s+and\s+|\s*;\s*", blob)
    names = []
    for p in parts:
        p = INVESTOR_PREFIX_RE.sub("", p).strip().strip(",;:. ")
        p = re.sub(r"^(?:investors?|backers?|funds?)\s+", "", p, flags=re.IGNORECASE).strip()
        if not p or not p[0].isupper():
            continue
        if p not in names:
            names.append(p)
    return names


def find_investors(text):
    """(leads, participants) - explicit statements only; nothing inferred."""
    leads, participants = [], []
    for pat in LEAD_PATTERNS:
        for m in pat.finditer(text):
            for n in split_names(m.group("names")):
                if n not in leads:
                    leads.append(n)
        if leads:
            break
    for pat in PARTICIPANT_PATTERNS:
        for m in pat.finditer(text):
            for n in split_names(m.group("names")):
                if n not in participants and n not in leads:
                    participants.append(n)
    return leads, participants


def find_company(text, spans):
    """Subject in front of the first raise verb. Heuristic - always flagged."""
    m = RAISE_VERB_RE.search(text)
    if not m:
        return "", ["no raise verb found; company_name could not be read from the text"]
    start, sentence = sentence_of(spans, m.start())
    prefix = text[start:m.start()].strip()
    runs, current = [], []
    for tok in prefix.split(" "):
        bare = tok.strip(",;:.()\"'")
        if bare and bare[0].isupper():
            current.append(bare)
            continue
        if bare.lower() in ("de", "van", "von", "of") and current:
            current.append(bare)
            continue
        if current:
            runs.append(current)
            current = []
    trailing = bool(current)
    if current:
        runs.append(current)
    cleaned = []
    for run in runs:
        while run and run[0] in GENERIC_LEAD_TOKENS:
            run = run[1:]
        while run and run[-1].lower() in SUBJECT_STOP:
            run = run[:-1]
        if run:
            cleaned.append(" ".join(run))
    if not cleaned:
        return "", ["no capitalised subject in front of the raise verb; company_name omitted"]
    name = cleaned[-1] if trailing else cleaned[0]
    return name, ["company_name '%s' is a heuristic read of the subject in front of "
                  "'%s' - verify against the source" % (name, m.group(0).lower())]


def find_dates(text):
    """(announced_date, close_date) in ISO form, from what the text states."""
    found = []
    for pat in DATE_PATTERNS:
        for m in pat.finditer(text):
            if m.group("y") and "mon" in m.groupdict() and m.groupdict().get("mon"):
                mon = MONTHS[m.group("mon").lower().rstrip(".")[:3]] \
                    if m.group("mon").lower().rstrip(".")[:3] in MONTHS \
                    else MONTHS[m.group("mon").lower().rstrip(".")]
                iso = "%s-%02d-%02d" % (m.group("y"), mon, int(m.group("d")))
            else:
                iso = "%s-%s-%s" % (m.group("y"), m.group("m"), m.group("d"))
            found.append((m.start(), iso))
    found.sort()
    announced = close = None
    for pos, iso in found:
        window = text[max(0, pos - 60):pos].lower()
        if re.search(r"\bclos(e|ed|es|ing)\b", window):
            if close is None:
                close = iso
        elif announced is None:
            announced = iso
    return announced, close


def find_use_of_proceeds(text):
    for pat in PROCEEDS_PATTERNS:
        m = pat.search(text)
        if m:
            use = re.sub(r"\s+", " ", m.group("use")).strip().strip(",;: ")
            return use
    return None


def classify_amounts(text, spans, mentions):
    """Split money figures into capital raised vs valuation (SKILL.md step 3).

    Each figure is judged on the text between it and its neighbours only, so a
    valuation sitting later in the sentence never captures the round amount and
    a cumulative "total funding to date" never displaces it.
    """
    raises, valuations = [], []
    for idx, men in enumerate(mentions):
        s_start, sentence = sentence_of(spans, men["start"])
        s_end = s_start + len(sentence)
        left = s_start
        right = s_end
        if idx > 0 and mentions[idx - 1]["end"] > left:
            left = mentions[idx - 1]["end"]
        if idx + 1 < len(mentions) and mentions[idx + 1]["start"] < right:
            right = mentions[idx + 1]["start"]
        back = text[max(left, men["start"] - 80):men["start"]]
        fwd = text[men["end"]:min(right, men["end"] + 45)]
        near = back + " || " + fwd
        if VALUATION_PRE_RE.search(near):
            valuations.append((men, "pre_money"))
        elif VALUATION_POST_RE.search(near):
            valuations.append((men, "post_money"))
        elif VALUATION_ANY_RE.search(near):
            valuations.append((men, "post_money_default"))
        elif NOT_AMOUNT_BACK_RE.search(back) or NOT_AMOUNT_FWD_RE.search(fwd):
            continue
        elif RAISE_VERB_RE.search(sentence) or ROUND_NOUN_RE.search(fwd):
            raises.append(men)
    return raises, valuations


# The SKILL.md worked example. Illustrative text: the company and the funds are
# invented so the example is reproducible offline and cites nothing real.
DEMO_ARTICLE = (
    "Helion Diagnostics, a Cambridge-based cancer-screening company, raised $47 million "
    "in Series B funding, the company announced on 2025-03-03. The round was led by "
    "Northgate Ventures, with participation from Baseline Capital, Kestrel Partners and "
    "Orion Growth Fund. The financing, which closed on 2025-02-18, values Helion at "
    "$400 million post-money. Helion will use the funds to expand its clinical trial "
    "programme and open a manufacturing site in Basel."
)

# SKILL.md order; the record is emitted in exactly this order every run.
FIELD_ORDER = [
    "event_type", "company_name", "stage", "amount_usd", "amount_currency",
    "announced_date", "close_date", "post_money_valuation_usd",
    "pre_money_valuation_usd", "lead_investors", "participating_investors",
    "use_of_proceeds", "source_url", "source_grade", "confidence",
]


def extract_event(raw_text, assume_usd=False, source_url=None, source_grade=None):
    """Rule-based FundingEvent. Returns (event, notes, trace)."""
    text = normalise_text(raw_text)
    spans = sentence_spans(text)
    notes, trace = [], []
    event = OrderedDict()
    event["event_type"] = "funding_round"

    company, cnotes = find_company(text, spans)
    notes.extend(cnotes)
    if company:
        event["company_name"] = company

    stage, snotes = map_stage(text)
    notes.extend(n for n in snotes if n)
    if stage:
        event["stage"] = stage

    mentions = scan_money(text, assume_usd=assume_usd)
    raises, valuations = classify_amounts(text, spans, mentions)
    amount = None
    if raises:
        amount = sorted(raises, key=lambda m: (-m["value"], m["start"]))[0]
        event["amount_usd"] = amount["value"]
        event["amount_currency"] = amount["currency"]
        notes.extend(amount["notes"])
        if len(raises) > 1:
            notes.append("%d capital-raise figures in the text; the largest (%s) kept - "
                         "check the others are not tranches"
                         % (len(raises), money_str(amount["value"], amount["currency"])))
    else:
        notes.append("no capital-raise amount found near a raise verb; amount omitted")

    announced, close = find_dates(text)
    if announced:
        event["announced_date"] = announced
    if close:
        event["close_date"] = close

    for men, kind in valuations:
        if kind == "pre_money" and "pre_money_valuation_usd" not in event:
            event["pre_money_valuation_usd"] = men["value"]
            notes.append("valuation %s recorded as pre-money, kept out of the amount "
                         "(SKILL.md step 3)" % money_str(men["value"], men["currency"]))
        elif kind in ("post_money", "post_money_default") and "post_money_valuation_usd" not in event:
            event["post_money_valuation_usd"] = men["value"]
            if kind == "post_money_default":
                notes.append("valuation %s stated without a pre/post qualifier - recorded as "
                             "post-money per SKILL.md step 3; ambiguity is real"
                             % money_str(men["value"], men["currency"]))
            else:
                notes.append("valuation %s recorded as post-money, kept out of the amount "
                             "(SKILL.md step 3)" % money_str(men["value"], men["currency"]))

    leads, participants = find_investors(text)
    event["lead_investors"] = leads          # [] is meaningful: no lead was named
    if not leads:
        notes.append("no investor is stated to have led; lead_investors left empty, not guessed")
    if participants:
        event["participating_investors"] = participants

    use = find_use_of_proceeds(text)
    if use:
        event["use_of_proceeds"] = use

    url = source_url or (URL_RE.search(text).group(0).rstrip(".,);") if URL_RE.search(text) else None)
    if url:
        event["source_url"] = url
    else:
        notes.append("source_url is required by the schema and is not in the text - "
                     "supply it with --source-url before the record ships")
    if source_grade:
        event["source_grade"] = source_grade
    else:
        notes.append("source_grade not set: grade the source with rate-source-admiralty "
                     "and pass --source-grade")

    event["confidence"] = score_confidence(event, amount, trace)
    return OrderedDict((k, event[k]) for k in FIELD_ORDER if k in event), notes, trace


def score_confidence(event, amount, trace):
    """0-100 confidence from explicit rules only; every step is traced."""
    score = 60
    trace.append(("base", 60, "starting point for a single-source parse"))
    if event.get("stage"):
        score += 15
        trace.append(("+ explicit stage", 15, event["stage"]))
    if event.get("lead_investors"):
        score += 10
        trace.append(("+ explicit lead investor", 10, ", ".join(event["lead_investors"])))
    if amount is not None and amount["exact"]:
        score += 10
        trace.append(("+ exact single amount", 10, money_str(amount["value"], amount["currency"])))
    if amount is not None:
        for note in amount["notes"]:
            if note.startswith("range"):
                score -= 15
                trace.append(("- range (midpoint used)", -15, note))
            elif note.startswith("cap"):
                score -= 15
                trace.append(("- 'up to' cap", -15, note))
        if amount["currency"].endswith("?"):
            score -= 10
            trace.append(("- ambiguous currency", -10, amount["currency"]))
    clamped = max(0, min(100, score))
    if clamped != score:
        trace.append(("clamped to 0-100", clamped - score, "raw score %d" % score))
    trace.append(("= confidence", clamped, "the SKILL.md review threshold is 75"))
    return clamped


# --------------------------------------------------------------------------
# 4 - CLI
# --------------------------------------------------------------------------

def print_trace(notes, trace, stream):
    stream.write("confidence trace (SKILL.md scoring rules):\n")
    for label, delta, why in trace:
        fmt = "  %-28s %5d   %s\n" if label == "= confidence" else "  %-28s %+5d   %s\n"
        stream.write(fmt % (label, delta, why))
    if notes:
        stream.write("notes:\n")
        for n in notes:
            stream.write("  - %s\n" % n)


def cmd_amount(args, parser):
    res = normalise_amount(args.text, assume_usd=args.assume_usd)
    if res is None:
        parser.error("no money figure found in %r" % args.text)
    payload = OrderedDict([
        ("value", res["value"]), ("currency", res["currency"]),
        ("notes", res["notes"]), ("confidence_penalty", res["confidence_penalty"]),
    ])
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("value:              %s" % format(res["value"], ","))
        print("currency:           %s" % res["currency"])
        print("confidence_penalty: -%d" % res["confidence_penalty"])
        for n in res["notes"]:
            print("note:               %s" % n)
    return 0


def cmd_stage(args, parser):
    stage, notes = map_stage(args.text)
    if args.json:
        print(json.dumps(OrderedDict([("stage", stage), ("notes", notes)]),
                         ensure_ascii=False, indent=2))
    else:
        print("stage:  %s" % (stage if stage else "(blank - not stated)"))
        for n in notes:
            print("note:   %s" % n)
    return 0


def cmd_extract(args, parser):
    if args.demo:
        raw = DEMO_ARTICLE
    elif args.text:
        raw = args.text
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                raw = fh.read()
        except OSError as exc:
            parser.error("could not read %s: %s" % (args.file, exc))
    else:
        parser.error("pass --file PATH, --text STRING or --demo")
    event, notes, trace = extract_event(raw, assume_usd=args.assume_usd,
                                        source_url=args.source_url,
                                        source_grade=args.source_grade)
    print(json.dumps(event, ensure_ascii=False, indent=2))
    if not args.quiet:
        print_trace(notes, trace, sys.stderr)
    return 0


def cmd_demo():
    print("Worked example article (illustrative text; the company and funds are invented):")
    print()
    for line in re.findall(r".{1,76}(?:\s|$)", DEMO_ARTICLE):
        print("  " + line.rstrip())
    print()
    print("$ python3 funding.py extract --demo")
    event, notes, trace = extract_event(DEMO_ARTICLE)
    print(json.dumps(event, ensure_ascii=False, indent=2))
    print_trace(notes, trace, sys.stdout)
    return 0


# --------------------------------------------------------------------------
# 5 - selftest: hand-checked cases for every rule in SKILL.md steps 1-7
# --------------------------------------------------------------------------

def run_selftest():
    failures = [0]
    count = [0]

    def check(name, got, want):
        count[0] += 1
        ok = got == want
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
        if not ok:
            failures[0] += 1
            print("      got:      %r" % (got,))
            print("      expected: %r" % (want,))

    def amt(s, assume_usd=False):
        r = normalise_amount(s, assume_usd=assume_usd)
        return None if r is None else (r["value"], r["currency"], r["confidence_penalty"])

    # --- step 1: money grammar (values computed by hand) -------------------
    check("amount $47M", amt("$47M"), (47000000, "USD?", 10))
    check("amount $1.2B", amt("$1.2B"), (1200000000, "USD?", 10))
    check("amount US$3.5 billion is unambiguous USD", amt("US$3.5 billion"), (3500000000, "USD", 0))
    check("amount EUR symbol", amt("€10 million"), (10000000, "EUR", 0))
    check("amount GBP thousands", amt("£500k"), (500000, "GBP", 0))
    check("amount CAD code", amt("CAD 20M"), (20000000, "CAD", 0))
    check("amount A$ is AUD", amt("A$15m"), (15000000, "AUD", 0))
    check("amount yen", amt("¥1.2 billion"), (1200000000, "JPY", 0))
    check("amount INR crore = 10^7", amt("INR 400 crore"), (4000000000, "INR", 0))
    check("amount suffix word", amt("10 million euros"), (10000000, "EUR", 0))
    # 47M and 50M -> (47 + 50)/2 = 48.5M, and the range costs 15.
    check("range with hyphen -> midpoint", amt("$47M-$50M"), (48500000, "USD?", 25))
    check("range with 'to' -> midpoint", amt("$47M to $50M"), (48500000, "USD?", 25))
    check("range 'between X and Y' -> midpoint",
          amt("between $47 million and $50 million"), (48500000, "USD?", 25))
    check("range shorthand $47-50M", amt("$47-50M"), (48500000, "USD?", 25))
    check("'up to' is a cap, not the amount", amt("up to $50 million"), (50000000, "USD?", 25))
    check("'nearly' keeps the figure, forfeits exactness", amt("nearly $10M"), (10000000, "USD?", 10))
    check("'over' is a lower bound", amt("over $100M"), (100000000, "USD?", 10))
    check("--assume-usd resolves the bare $", amt("$47M", assume_usd=True), (47000000, "USD", 0))
    check("'and' outside 'between' is not a range",
          amt("raised $10M and $5M in debt"), (10000000, "USD?", 10))
    check("no money in the string", amt("hired 60 people in 2025"), None)
    check("'up to' is not exact", normalise_amount("up to $50 million")["exact"], False)

    # --- step 2: stage vocabulary ------------------------------------------
    check("stage Series B", map_stage("raised $47M in Series B funding")[0], "Series B")
    check("stage Series B-2", map_stage("closed its Series B-2 financing")[0], "Series B-2")
    check("stage seed financing", map_stage("a seed financing round")[0], "Seed")
    check("stage pre-seed beats seed", map_stage("closed a pre-seed round")[0], "Pre-seed")
    check("stage bridge", map_stage("an internal bridge round")[0], "Bridge")
    check("stage growth equity", map_stage("a growth equity investment")[0], "Growth")
    check("stage late-stage -> Growth", map_stage("a late-stage round")[0], "Growth")
    check("stage tender offer -> Secondary", map_stage("employee tender offer")[0], "Secondary")
    check("stage IPO", map_stage("priced its IPO on Nasdaq")[0], "Public (IPO)")
    check("stage direct listing", map_stage("went public via a direct listing")[0], "Public (Direct)")
    check("stage SPAC", map_stage("merging with a SPAC")[0], "Public (SPAC)")
    check("stage blank when unnamed", map_stage("closed its latest round")[0], "")
    check("stage blank note explains why",
          NO_STAGE_NOTE in map_stage("closed its latest round")[1], True)
    check("venture debt is not a stage", map_stage("raised venture debt")[0], "")

    # --- steps 3-7: whole-sentence extraction ------------------------------
    s1 = ("Acme raised $47M in Series B funding led by Foo Ventures with participation "
          "from Bar Capital and Baz Partners, valuing the company at $400M post-money.")
    e1, n1, t1 = extract_event(s1)
    check("s1 company", e1.get("company_name"), "Acme")
    check("s1 stage", e1.get("stage"), "Series B")
    check("s1 amount", e1.get("amount_usd"), 47000000)
    check("s1 currency stays ambiguous", e1.get("amount_currency"), "USD?")
    check("s1 lead", e1.get("lead_investors"), ["Foo Ventures"])
    check("s1 participants", e1.get("participating_investors"), ["Bar Capital", "Baz Partners"])
    check("s1 valuation is separate from the amount",
          e1.get("post_money_valuation_usd"), 400000000)
    # 60 base +15 stage +10 lead +10 exact amount -10 ambiguous currency = 85
    check("s1 confidence = 60+15+10+10-10", e1.get("confidence"), 85)
    check("s1 omits what the text never says", "use_of_proceeds" in e1, False)

    s2 = ("Bolt Fusion closed a Series A round of up to $50 million, the company said, "
          "with participation from Delta Capital.")
    e2, _, _ = extract_event(s2)
    check("s2 cap amount", e2.get("amount_usd"), 50000000)
    check("s2 no lead named -> empty list", e2.get("lead_investors"), [])
    # 60 base +15 stage -15 cap -10 ambiguous currency = 50
    check("s2 confidence = 60+15-15-10", e2.get("confidence"), 50)

    s3 = ("Vantage Bio raised €10 million to €12 million in seed financing co-led by "
          "Alpha Fund and Beta Ventures.")
    e3, _, _ = extract_event(s3)
    check("s3 EUR midpoint", e3.get("amount_usd"), 11000000)
    check("s3 currency", e3.get("amount_currency"), "EUR")
    check("s3 co-leads", e3.get("lead_investors"), ["Alpha Fund", "Beta Ventures"])
    # 60 base +15 stage +10 lead -15 range = 70 (EUR is explicit: no currency penalty)
    check("s3 confidence = 60+15+10-15", e3.get("confidence"), 70)

    s4 = "Northwind Labs announced its latest round. Terms were not disclosed."
    e4, _, _ = extract_event(s4)
    check("s4 no stage guessed", "stage" in e4, False)
    check("s4 no amount invented", "amount_usd" in e4, False)
    check("s4 confidence = base only", e4.get("confidence"), 60)

    s5 = ("Orbital Freight raised US$3.5 billion in a Series E led by Lightspeed, "
          "which closed on 2025-02-18 at a US$61.5 billion post-money valuation. "
          "Orbital will use the funds to expand its fleet.")
    e5, _, _ = extract_event(s5)
    check("s5 amount is not the valuation", e5.get("amount_usd"), 3500000000)
    check("s5 valuation", e5.get("post_money_valuation_usd"), 61500000000)
    check("s5 close date", e5.get("close_date"), "2025-02-18")
    check("s5 use of proceeds", e5.get("use_of_proceeds"), "expand its fleet")
    # 60 +15 stage +10 lead +10 exact amount = 95 (US$ is explicit)
    check("s5 confidence = 60+15+10+10", e5.get("confidence"), 95)

    s6 = ("Kite Robotics, a Toronto-based warehouse automation startup, raised CAD 20M "
          "in a Series A on March 3, 2025. Maple Ventures led the round, joined by "
          "existing investors Northern Fund and Lakeshore Capital.")
    e6, _, _ = extract_event(s6)
    check("s6 company from a longer subject", e6.get("company_name"), "Kite Robotics")
    check("s6 CAD kept, no FX conversion", (e6.get("amount_usd"), e6.get("amount_currency")),
          (20000000, "CAD"))
    check("s6 'X led the round'", e6.get("lead_investors"), ["Maple Ventures"])
    check("s6 'joined by' participants",
          e6.get("participating_investors"), ["Northern Fund", "Lakeshore Capital"])
    check("s6 US date -> ISO", e6.get("announced_date"), "2025-03-03")

    s7 = ("Helios Bio raised $12 million, bringing its total funding to $85 million, "
          "in a seed round.")
    e7, _, _ = extract_event(s7)
    check("s7 cumulative total is not the round", e7.get("amount_usd"), 12000000)

    s8 = "Nimbus AI raised $30 million at a $250 million valuation."
    e8, n8, _ = extract_event(s8)
    check("s8 amount survives a later valuation", e8.get("amount_usd"), 30000000)
    check("s8 unqualified valuation -> post-money", e8.get("post_money_valuation_usd"), 250000000)
    check("s8 ambiguity is noted",
          any("without a pre/post qualifier" in n for n in n8), True)

    s9 = "Zephyr Grid raised $80 million at a $600 million pre-money valuation."
    e9, _, _ = extract_event(s9)
    check("s9 pre-money kept in its own field", e9.get("pre_money_valuation_usd"), 600000000)
    check("s9 pre-money is not post-money", "post_money_valuation_usd" in e9, False)

    s10 = ("Cormorant Health raised $47 million, the company said, with the round "
           "detailed at https://example.com/press/cormorant-series-b.")
    e10, _, _ = extract_event(s10, source_grade="B2")
    check("s10 source_url read from the text",
          e10.get("source_url"), "https://example.com/press/cormorant-series-b")
    check("s10 source_grade only when supplied", e10.get("source_grade"), "B2")

    # --- the demo article reproduces the SKILL.md worked example -----------
    ed, _, _ = extract_event(DEMO_ARTICLE)
    check("demo company", ed.get("company_name"), "Helion Diagnostics")
    check("demo stage", ed.get("stage"), "Series B")
    check("demo amount", ed.get("amount_usd"), 47000000)
    check("demo valuation", ed.get("post_money_valuation_usd"), 400000000)
    check("demo lead", ed.get("lead_investors"), ["Northgate Ventures"])
    check("demo participants", ed.get("participating_investors"),
          ["Baseline Capital", "Kestrel Partners", "Orion Growth Fund"])
    check("demo announced date", ed.get("announced_date"), "2025-03-03")
    check("demo close date", ed.get("close_date"), "2025-02-18")
    check("demo confidence", ed.get("confidence"), 85)
    check("demo field order is the schema order",
          list(ed), [k for k in FIELD_ORDER if k in ed])

    # --- determinism -------------------------------------------------------
    check("two extractions are identical",
          json.dumps(extract_event(DEMO_ARTICLE)[0]), json.dumps(extract_event(DEMO_ARTICLE)[0]))

    print()
    if failures[0]:
        print("selftest FAILED: %d of %d checks" % (failures[0], count[0]))
        return 1
    print("ALL %d CHECKS PASSED" % count[0])
    print("selftest OK")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="funding.py",
        description="Normalise funding-announcement text into the FundingEvent record of "
                    "SKILL.md: money grammar, stage vocabulary, investors, confidence.")
    parser.add_argument("--selftest", action="store_true",
                        help="run the built-in hand-checked cases and exit")
    parser.add_argument("--demo", action="store_true",
                        help="print the SKILL.md worked example and its parse")
    sub = parser.add_subparsers(dest="command")

    a = sub.add_parser("amount", help="normalise a money string (ranges, caps, currency)")
    a.add_argument("text", help='the money string, e.g. "$47M to $50M"')
    a.add_argument("--assume-usd", action="store_true",
                   help="read a bare '$' as USD instead of leaving it ambiguous")
    a.add_argument("--json", action="store_true", help="emit JSON")

    s = sub.add_parser("stage", help="map round phrasing to the canonical stage")
    s.add_argument("text", help='the phrase, e.g. "closed its Series B-2 financing"')
    s.add_argument("--json", action="store_true", help="emit JSON")

    e = sub.add_parser("extract", help="parse an article into the FundingEvent JSON")
    e.add_argument("--file", help="path to a UTF-8 text file holding the article")
    e.add_argument("--text", help="the article text as a string")
    e.add_argument("--demo", action="store_true", help="use the built-in worked example")
    e.add_argument("--assume-usd", action="store_true",
                   help="read a bare '$' as USD instead of leaving it ambiguous")
    e.add_argument("--source-url", help="source URL to record (the schema requires one)")
    e.add_argument("--source-grade", help="Admiralty grade from rate-source-admiralty, e.g. B2")
    e.add_argument("--json", action="store_true",
                   help="emit JSON (already the default for extract)")
    e.add_argument("--quiet", action="store_true",
                   help="suppress the confidence trace and notes on stderr")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.command:
        if args.demo:
            return cmd_demo()
        parser.error("choose a command: amount | stage | extract  (or --selftest / --demo)")
    if args.command == "amount":
        return cmd_amount(args, parser)
    if args.command == "stage":
        return cmd_stage(args, parser)
    return cmd_extract(args, parser)


if __name__ == "__main__":
    sys.exit(main())
