#!/usr/bin/env python3
"""claims.py — deterministic structural analysis of a patent claim set.

Implements procedure step 2 of ../SKILL.md ("Parse the claims") as code, so the
claim counts, dependency tree, transition language and drafting flags that feed
a PatentEvent come from a tool rather than from an agent's mental bookkeeping.

What it computes (every rule is a documented heuristic over claim wording):

  * Splits raw claim text ("1. A method comprising: ...") into numbered claims.
    A claim begins with a capital letter and ends with a period (MPEP § 608.01(m));
    amendment status markers such as "(Canceled)" / "(Currently Amended)" are
    recognised and stripped.
  * Builds the dependency tree from reference phrases — "of claim 3", "according
    to claim 1", "as claimed in claim 2", "as recited in claim 4", "of any one of
    claims 1 to 3", "of any of claims 1-3", "of claim 1 or 2", "according to any
    one of the preceding claims" — and classifies each claim as independent,
    dependent or multiple dependent (35 U.S.C. § 112(c)–(e)).
  * Labels the statutory category from the preamble head noun — method/process,
    system/apparatus/device, composition/compound, computer-readable medium
    (CRM), use claim, product-by-process, kit, article — and maps it onto the
    four 35 U.S.C. § 101 categories (process, machine, manufacture, composition
    of matter; MPEP § 2106.03).  Product-by-process and "use of" wording are
    tested first; otherwise the earliest category keyword in the preamble wins.
  * For independent claims, splits preamble from body at the transitional phrase
    and states its scope per MPEP § 2111.03: "comprising" (synonyms "including",
    "containing", "characterized by") is OPEN — an accused product with the
    recited elements plus more still reads on the claim; "consisting of" is
    CLOSED — unrecited elements are excluded; "consisting essentially of" is
    PARTIALLY OPEN — only additions that do not materially affect the basic and
    novel characteristics are admitted; "having" / "composed of" are ambiguous
    and read in light of the specification.  Split preference: a phrase followed
    by ":" > any comprising/consisting/including phrase > "having"/"composed
    of"; earliest position breaks ties; the Jepson phrase "the improvement
    comprising" wins outright (37 CFR 1.75(e); MPEP § 2129).  "group consisting
    of" is a Markush group (MPEP § 2173.05(h)), never the transition.
  * Counts elements (";"-separated clauses, "(a)/(i)/(1)" enumerations, or the
    line-broken sub-paragraphs of 37 CFR 1.75(i)) and words.  Word count is a
    breadth proxy only: a shorter independent claim generally recites fewer
    limitations and is therefore generally broader (37 CFR 1.75(g) expects the
    least restrictive claim to be claim 1).
  * Per-claim flags: "means for" / "step for" (35 U.S.C. § 112(f); MPEP § 2181)
    and generic placeholders such as "module for" that may invoke it (MPEP § 2181,
    prong 1); relative terms — "about", "substantially", "approximately", ... —
    the indefiniteness watch-list of MPEP § 2173.05(b); exemplary language
    ("such as", "for example" — MPEP § 2173.05(d)); negative limitations ("free
    of", "without" — MPEP § 2173.05(i)); Markush groups; use claims (MPEP
    § 2173.05(q)); product-by-process claims (MPEP § 2113); a dependent claim in
    a different category than its parent (infringement test, MPEP § 608.01(n)).
  * Global flags: multiple dependent claims (count; they must refer to their
    parents in the alternative only, may not depend from another multiple
    dependent claim, and for USPTO fees count as the number of claims referenced
    plus the 37 CFR 1.16(j) surcharge — 35 U.S.C. § 112(e); 37 CFR 1.75(c); MPEP
    § 608.01(n)); a dependent claim referencing a later, non-existent or canceled
    claim (35 U.S.C. § 112(d) requires "a claim previously set forth"; MPEP
    § 608.01(n)); a dependent claim that adds no further limitation or duplicates
    a sibling (35 U.S.C. § 112(d); MPEP § 608.01(m) and (n)); gaps in the claim
    numbering (MPEP § 608.01(j)).

This is a first pass for the examiner-style read in SKILL.md — not claim
construction and not legal advice.  Stdlib only.  Python 3.9+.  Deterministic:
no randomness, no wall-clock, sorted iteration everywhere.

Usage:
    python3 claims.py parse --file claims.txt          # tree + table + flags
    python3 claims.py parse --file claims.txt --json   # structured output
    python3 claims.py parse --demo                     # built-in synthetic claim set
    python3 claims.py stats --file claims.txt          # counts only (--json ok)
    python3 claims.py --selftest

Exit codes: 0 ok; 1 usage / unparseable input; 2 the claim set carries an
error-level flag (forward or dangling reference, improper multiple dependency,
dependent claim with no further limitation).
"""

import argparse
import json
import re
import sys

# --- text normalisation ------------------------------------------------------

_TRANSLATE = {ord(ch): "-" for ch in "\u2010\u2011\u2012\u2013\u2014\u2212"}
_TRANSLATE.update({0x201C: '"', 0x201D: '"', 0x2018: "'", 0x2019: "'", 0x00A0: " ", 0x200B: None})


def normalize(text):
    """Unify line endings, dashes, quotes and non-breaking spaces; drop the BOM."""
    text = text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
    return text.translate(_TRANSLATE)


def flat(text):
    """Collapse all whitespace runs to single spaces."""
    return " ".join(text.split())


def norm_key(text):
    """Lower-case alphanumeric skeleton used to compare claim bodies."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


# --- claim splitting (MPEP § 608.01(m): capital letter ... period) ----------

STATUS_WORDS = (r"currently amended|previously presented|original|new|withdrawn|"
                r"canceled|cancelled|not entered|withdrawn\s*-\s*currently amended")
CLAIM_START_RE = re.compile(
    r"(?:^|(?<=\s))(?i:claim\s+)?(\d{1,3})\s*[.)]\s*"
    r"(?=(?i:\((?:" + STATUS_WORDS + r")\))|[A-Z(]|\d{1,3}[,\-]\S)",
    re.M,
)
STATUS_RE = re.compile(r"^\((" + STATUS_WORDS + r")\)\s*\.?\s*", re.I)


def split_claims(text):
    """Return [(number, raw_text)] in document order.

    A claim starts at 'N.' / 'N)' followed by a capital letter (or an amendment
    status marker).  Numbers must increase, so a stray 'N. Xyz' inside a claim
    body is ignored; if a candidate numbered 1 exists, parsing starts there
    (anything before it — 'What is claimed is:' — is dropped).
    """
    text = normalize(text)
    cands = [(int(m.group(1)), m.start(), m.end()) for m in CLAIM_START_RE.finditer(text)]
    first = next((i for i, c in enumerate(cands) if c[0] == 1), 0)
    starts, last = [], 0
    for n, s, e in cands[first:]:
        if n > last:
            starts.append((n, s, e))
            last = n
    claims = []
    for i, (n, _s, e) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(text)
        claims.append((n, text[e:end].strip()))
    return claims


def strip_status(raw):
    """Remove a leading amendment status marker; return (status or None, text)."""
    m = STATUS_RE.match(raw)
    if not m:
        return None, raw
    status = m.group(1).lower().replace("cancelled", "canceled")
    return status, raw[m.end():].strip()


# --- dependency phrases (35 U.S.C. § 112(d)-(e); MPEP § 608.01(n)) ----------

DEP_PREFIX = r"(?:any\s+(?:one\s+)?of\s+|one\s+of\s+|either\s+of\s+|either\s+|each\s+of\s+)"
_SEP = r"(?:,\s*(?:or\b|and/or\b|and\b)?|or\b|and/or\b|and\b|to\b|through\b|-)"
NUMLIST = r"\d{1,3}(?:\s*" + _SEP + r"\s*(?:claims?\s+)?\d{1,3})*"
DEP_RE = re.compile(r"\b(?P<prefix>" + DEP_PREFIX + r")?claims?\s+(?P<list>" + NUMLIST + r")", re.I)
PRECEDING_RE = re.compile(
    r"\b(?P<prefix>(?:any\s+(?:one\s+)?of\s+the\s+|any\s+of\s+the\s+|one\s+of\s+the\s+|"
    r"each\s+of\s+the\s+|any\s+(?:one\s+)?|the\s+))?"
    r"(?:preceding|previous|foregoing|aforementioned)\s+claim(?P<plural>s)?\b", re.I)
RANGE_RE = re.compile(r"(\d{1,3})\s*(?:to|through|-)\s*(\d{1,3})|(\d{1,3})", re.I)
HEAD_TAIL_RE = re.compile(
    r"\s*\b(?:of|according\s+to|as\s+(?:claimed|recited|defined|described|set\s+forth)\s+in|"
    r"as\s+in|in|per|under|to|by|from|with)\s*$", re.I)


def parse_numlist(s):
    """'1, 2, or 3' -> [1, 2, 3]; '1-3' -> [1, 2, 3]; '1 or claim 2' -> [1, 2]."""
    nums = set()
    for m in RANGE_RE.finditer(s):
        if m.group(3):
            nums.add(int(m.group(3)))
        else:
            a, b = int(m.group(1)), int(m.group(2))
            nums.update(range(a, b + 1) if a <= b else (a, b))
    return sorted(nums)


def alternative_form(prefix, numlist):
    """MPEP § 608.01(n): a multiple dependent claim must refer to its parents
    'in the alternative only'.  Acceptable: 'claim 3 or 4', 'either claim 1 or
    claim 2', 'any one of claims 1, 2, and 3', 'any of claims 1-3'.
    Unacceptable: 'claim 3 and 4', 'claims 1-3', 'claims 1-3 or 7-9', 'claims 1, 2, 3'."""
    if prefix:
        return True
    has_or = re.search(r"\bor\b", numlist, re.I) is not None
    has_and = re.search(r"\band\b", numlist, re.I) is not None
    has_range = re.search(r"\d\s*(?:to|through|-)\s*\d", numlist, re.I) is not None
    return has_or and not has_and and not has_range


def find_dependency(text, own, known):
    """Locate the first claim reference. Returns (refs, start, end, alternative) or None.

    `known` is the sorted list of live claim numbers (used for 'preceding claims')."""
    m1 = DEP_RE.search(text)
    m2 = PRECEDING_RE.search(text)
    m = min((x for x in (m1, m2) if x), key=lambda x: x.start(), default=None)
    if m is None:
        return None
    if m is m1:
        return parse_numlist(m.group("list")), m.start(), m.end(), alternative_form(m.group("prefix"), m.group("list"))
    prefix = (m.group("prefix") or "").strip().lower()
    plural = bool(m.group("plural"))
    preceding = [k for k in known if k < own]
    if prefix.startswith(("any", "one", "each")):
        return preceding, m.start(), m.end(), True          # "any one of the preceding claims"
    if not plural:
        return preceding[-1:], m.start(), m.end(), True     # "the preceding claim" = the one before
    return preceding, m.start(), m.end(), False             # "the preceding claims" = conjunctive


# --- statutory category (35 U.S.C. § 101; MPEP § 2106.03) --------------------

USE_RE = re.compile(r"^\W*(?:the\s+|a\s+|an\s+)?use\s+of\b", re.I)
PBP_RE = re.compile(
    r"\b(?:obtained|obtainable|produced|producible|prepared|made|manufactured|formed|synthesi[sz]ed)\s+"
    r"(?:by|according\s+to|using|through|via|with)\s+(?:the\s+|a\s+|an\s+)?(?:process|method)\b"
    r"|\bproduct\s+of\s+the\s+(?:process|method)\b", re.I)

CATEGORY_RULES = [  # (label, 35 U.S.C. § 101 class, regex) — earliest match in the preamble wins
    ("method", "process", r"\b(?:method|process|procedure)(?:es|s)?\b"),
    ("crm", "manufacture",
     r"\b(?:computer|machine|processor)[- ]readable\b|\bnon-transitory\b|\bstorage\s+(?:medium|media)\b|"
     r"\bprogram\s+products?\b|\bcomputer\s+programs?\b|\brecording\s+medi(?:um|a)\b|"
     r"\bmemory\s+(?:storing|having|comprising|encoded|containing)\b"),
    ("kit", "manufacture", r"\bkits?\b"),
    ("apparatus", "machine",
     r"\b(?:system|apparatus|apparatuses|device|assembly|assemblies|circuit|circuitry|engine|vehicle|"
     r"controller|sensor|module|unit|equipment|instrument|tool|arrangement|network|robot|drone|display|"
     r"server|terminal|node|actuator|pump|valve|motor|reactor|antenna|transceiver|receiver|transmitter|"
     r"camera|appliance|mechanism|batter(?:y|ies)|processor(?![- ](?:readable|implemented|executable))|"
     r"computer(?![- ](?:readable|implemented|executable|usable|program|storage))|"
     r"machine(?![- ]?(?:readable|learning|implemented|executable)))(?:s|es)?\b"),
    ("composition", "composition of matter",
     r"\b(?:composition|compound|formulation|mixture|blend|polymer|copolymer|alloy|resin|adhesive|"
     r"pharmaceutical|vaccine|antibod(?:y|ies)|antigen|peptide|polypeptide|protein|enzyme|nucleic\s+acid|"
     r"oligonucleotide|polynucleotide|molecule|solution|suspension|emulsion|dispersion|salt|crystal|"
     r"crystalline\s+form|drug|medicament|catalyst|electrolyte|ink|lubricant|fuel|solvent|surfactant|"
     r"ceramic|cement|hydrogel|foam|powder|paste|slurry|extract|conjugate|isomer|hydrate|solvate|prodrug|"
     r"reagent|substance|cell\s+line|microorganism|bacterium|bacteria|strain|plant|seed)(?:s|es)?\b"),
    ("article", "manufacture",
     r"\b(?:article|product|structure|garment|container|substrate|film|layer|fabric|textile|component|"
     r"element|member|body|sheet|package|packaging|panel|tube|tubing|fiber|fibre|implant|stent|catheter|"
     r"prosthesis|label|card|tire|tyre|blade|housing|frame|composite|laminate|filter|membrane|electrode|"
     r"wafer|chip|semiconductor|lens|coating|bottle|bag|box|cartridge|capsule|tablet|dosage\s+form|wire|"
     r"cable|connector|fastener|screw|bolt|hinge|seal|gasket|bearing|gear|shaft|spring|toy|footwear|shoe|"
     r"helmet|mask|glove)(?:s|es)?\b"),
]
CATEGORY_RULES = [(label, cls, re.compile(rx, re.I)) for label, cls, rx in CATEGORY_RULES]


def classify(head):
    """(category label, statutory class) from a preamble / claim head."""
    h = flat(head)
    if USE_RE.match(h):
        return "use", "process (use claim; see MPEP 2173.05(q))"
    if PBP_RE.search(h):
        return "product-by-process", "product (manufacture or composition of matter)"
    best = None
    for label, cls, rx in CATEGORY_RULES:
        m = rx.search(h)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), label, cls)
    return (best[1], best[2]) if best else ("unknown", "unknown")


# --- transitional phrase (MPEP § 2111.03) ------------------------------------

JEPSON_RE = re.compile(r"\b(?:wherein\s+)?the\s+improvement\s+compris(?:ing|es)\b", re.I)
TRANSITION_RULES = [  # (regex, canonical, scope, tier)  tier 3 = weakest evidence of a transition
    (re.compile(r"\bconsist(?:ing|s)\s+essentially\s+of\b", re.I), "consisting essentially of", "partially open", 1),
    (re.compile(r"(?<!group\s)\bconsist(?:ing|s)\s+of\b", re.I), "consisting of", "closed", 1),
    (re.compile(r"\bcompris(?:ing|es|e)\b", re.I), "comprising", "open", 1),
    (re.compile(r"\binclud(?:ing|es)\b", re.I), "including", "open", 2),
    (re.compile(r"\bcontain(?:ing|s)\b", re.I), "containing", "open", 2),
    (re.compile(r"\bcharacteri[sz]ed\s+(?:by|in\s+that)\b", re.I), "characterized by", "open", 2),
    (re.compile(r"\bcomposed\s+of\b", re.I), "composed of", "ambiguous", 3),
    (re.compile(r"\bhaving\b", re.I), "having", "ambiguous", 3),
]
SCOPE_NOTE = {
    "open": "covers anything with the recited elements plus more",
    "closed": "excludes any element not recited",
    "partially open": "admits only additions that do not materially affect the basic and novel characteristics",
    "ambiguous": "open or closed depending on the specification",
}


def find_transition(text):
    """Primary transitional phrase of an independent claim.

    Returns (start, end, canonical, scope, jepson, rule_index, occurrence) or None.
    Preference: Jepson phrase > phrase followed by ':' > tiers 1-2 over 'having' /
    'composed of' > earliest position."""
    m = JEPSON_RE.search(text)
    if m:
        return m.start(), m.end(), "the improvement comprising", "open", True, None, None
    best = None
    for i, (rx, canon, scope, tier) in enumerate(TRANSITION_RULES):
        for occ, m in enumerate(rx.finditer(text)):
            colon = 0 if text[m.end():m.end() + 2].lstrip(" ").startswith(":") else 1
            key = (colon, 1 if tier == 3 else 0, m.start())
            if best is None or key < best[0]:
                best = (key, m.start(), m.end(), canon, scope, i, occ)
    if best is None:
        return None
    _key, s, e, canon, scope, i, occ = best
    return s, e, canon, scope, False, i, occ


ENUM_RE = re.compile(r"\((?:[a-z]|[ivx]{1,4}|\d{1,2})\)\s")


def split_elements(body_flat, body_raw):
    """Elements: ';'-separated clauses > '(a)/(i)/(1)' enumerations > line-broken
    sub-paragraphs (37 CFR 1.75(i)) > the whole body as one element."""
    if ";" in body_flat:
        parts = body_flat.split(";")
    else:
        marks = [m.start() for m in ENUM_RE.finditer(body_flat)]
        if len(marks) >= 2:
            parts = [body_flat[a:b] for a, b in zip(marks, marks[1:] + [len(body_flat)])]
        else:
            lines = [ln for ln in body_raw.split("\n") if ln.strip()]
            parts = lines if len(lines) >= 2 else [body_flat]
    out = []
    for p in parts:
        p = flat(p).strip(" ,.:")
        p = re.sub(r"^(?:and|or)\s+", "", p, flags=re.I).strip(" ,.:")
        if p:
            out.append(p)
    return out


def gist_of(preamble, transition, elements, k=3):
    """Mechanical one-line gist: preamble + transition + first k words of each element."""
    parts = []
    for el in elements:
        w = el.split()
        parts.append(" ".join(w[:k]) + (" ..." if len(w) > k else ""))
    head = flat(preamble)
    if transition:
        head += " " + transition + ":"
    return head + (" " + "; ".join(parts) if parts else "")


# --- wording flags -----------------------------------------------------------

MPF_RE = re.compile(r"(?:\b[\w-]+\s+)?\bmeans\b(?:\s+for\s+[\w-]+)?|\bsteps?\s+for\s+[\w-]+", re.I)
NONCE_RE = re.compile(
    r"\b(?:mechanism|module|unit|component|element|member|device|logic)s?\s+"
    r"(?:for\s+[\w-]+|configured\s+to|adapted\s+to|operable\s+to|arranged\s+to)\b", re.I)
RELATIVE_TERMS = ("about", "approximately", "substantially", "essentially", "similar",
                  "generally", "relatively", "nearly", "roughly", "close to")
RELATIVE_RE = re.compile(r"\b(?:" + "|".join(t.replace(" ", r"\s+") for t in RELATIVE_TERMS) + r")\b", re.I)
EXEMPLARY_RE = re.compile(r"\bsuch\s+as\b|\bfor\s+example\b|\bfor\s+instance\b|\be\.g\.|\bpreferably\b", re.I)
NEGATIVE_RE = re.compile(
    r"\b(?:free\s+of|free\s+from|devoid\s+of|without|absent|in\s+the\s+absence\s+of|excluding|"
    r"other\s+than|except|lacking|does\s+not|do\s+not|is\s+not|are\s+not|"
    r"not\s+(?:compris\w*|contain\w*|includ\w*))\b", re.I)
MARKUSH_RE = re.compile(r"\bselected\s+from\s+(?:the\s+)?group\s+consisting\s+of\b", re.I)


def find_mpf(text):
    """'means for X' / 'step for X' / '<noun> means' snippets, excluding 'by means of'."""
    hits = set()
    for m in MPF_RE.finditer(text):
        s = flat(m.group(0)).lower()
        if s.startswith("by means"):
            continue
        if s.endswith("means") and re.match(r"\s+of\b", text[m.end():]):
            continue
        hits.add(s)
    return sorted(hits)


def find_terms(rx, text):
    return sorted({flat(m.group(0)).lower() for m in rx.finditer(text)})


# --- analysis ----------------------------------------------------------------

SEVERITY_RANK = {"error": 0, "warning": 1, "info": 2}


def _compatible(a, b):
    """Same statutory subject for the cross-category check; a product-by-process
    claim is a product claim, so it is compatible with article/composition heads."""
    if a == b or "unknown" in (a, b):
        return True
    return "product-by-process" in (a, b) and {a, b} <= {"product-by-process", "article", "composition"}


def _flag(claim, code, severity, detail):
    claim["_flags"].append({"code": code, "severity": severity, "detail": detail})


def analyze(text):
    """Parse a claim set and return the result dict (see docstring / --json)."""
    parsed = split_claims(text)
    if not parsed:
        raise ValueError("no claims found: each claim must start with its number, e.g. '1. A method ...'")

    claims = []
    for n, raw in parsed:
        status, body_raw = strip_status(raw)
        canceled = status == "canceled" or not body_raw
        claims.append({
            "id": n, "type": "canceled" if canceled else None, "status": status,
            "category": None, "statutory_class": None, "depends_on": [], "multiple_dependent": False,
            "depth": 0, "preamble": None, "transition": None, "transition_scope": None,
            "elements": 0, "element_list": [], "words": 0, "flags": [], "means_plus_function": False,
            "relative_terms": [], "negative_limitations": [], "gist": None,
            "text": flat(body_raw), "_raw": body_raw, "_flags": [], "_body_norm": "", "_alt": True,
            "_own_category": None,
        })
    by_id = {c["id"]: c for c in claims}
    live = sorted(c["id"] for c in claims if c["type"] != "canceled")

    # dependency, category, transition, elements
    for c in claims:
        if c["type"] == "canceled":
            c["category"], c["statutory_class"] = "-", "-"
            continue
        text_c = c["text"]
        c["words"] = len(text_c.split())
        dep = find_dependency(text_c, c["id"], live)
        if dep is None:
            c["type"] = "independent"
            tr = find_transition(text_c)
            if tr is None:
                c["preamble"], body_flat, body_raw = text_c, "", ""
                _flag(c, "NO-TRANS", "warning",
                      "no transitional phrase found; preamble/body split unavailable (MPEP 2111.03)")
            else:
                s, e, canon, scope, jepson, ri, occ = tr
                c["preamble"] = text_c[:s].strip(" ,;:")
                c["transition"], c["transition_scope"] = canon, scope
                body_flat = text_c[e:].strip(" ,;:")
                body_raw = body_flat
                if ri is not None:
                    raw_matches = list(TRANSITION_RULES[ri][0].finditer(c["_raw"]))
                    if occ < len(raw_matches):
                        body_raw = c["_raw"][raw_matches[occ].end():]
                if jepson:
                    _flag(c, "JEPSON", "info", "Jepson form: the preamble is an implied admission of prior art "
                                              "(37 CFR 1.75(e); MPEP 2129)")
                if scope == "closed":
                    _flag(c, "CLOSED", "info", "closed transition 'consisting of': " + SCOPE_NOTE["closed"] +
                          " (MPEP 2111.03)")
            c["category"], c["statutory_class"] = classify(c["preamble"])
            c["_own_category"] = c["category"]
            c["element_list"] = split_elements(body_flat, body_raw)
            c["elements"] = len(c["element_list"])
            c["gist"] = gist_of(c["preamble"], c["transition"], c["element_list"])
            c["_body_norm"] = norm_key(body_flat)
            scan_body = body_flat
        else:
            refs, s, e, alt = dep
            c["type"] = "dependent"
            c["depends_on"] = refs
            c["multiple_dependent"] = len(refs) > 1
            c["_alt"] = alt
            head = HEAD_TAIL_RE.sub("", text_c[:s]).strip(" ,;:")
            c["preamble"] = head
            c["category"], c["statutory_class"] = classify(head)
            c["_own_category"] = c["category"]
            limitation = text_c[e:].strip(" ,;:")
            c["element_list"] = split_elements(limitation, limitation)
            c["elements"] = len(c["element_list"])
            c["_body_norm"] = norm_key(limitation)
            scan_body = limitation
        # wording flags (whole claim for 112(f)/relative/negative; body only for nonce terms)
        mpf = find_mpf(text_c)
        if mpf:
            c["means_plus_function"] = True
            _flag(c, "112F", "info", "means-/step-plus-function language " + ", ".join('"%s"' % t for t in mpf) +
                  ": construed to cover the corresponding structure, material or acts in the specification and "
                  "equivalents (35 U.S.C. 112(f); MPEP 2181)")
        nonce = find_terms(NONCE_RE, scan_body)
        if nonce:
            _flag(c, "NONCE", "info", "generic placeholder + function " + ", ".join('"%s"' % t for t in nonce) +
                  ": may invoke 35 U.S.C. 112(f) if no structure is recited (MPEP 2181, prong 1)")
        rel_text = re.sub(r"consist(?:ing|s)\s+essentially\s+of", "consisting of", text_c, flags=re.I)
        c["relative_terms"] = find_terms(RELATIVE_RE, rel_text)
        if c["relative_terms"]:
            _flag(c, "REL", "info", "relative term(s) " + ", ".join('"%s"' % t for t in c["relative_terms"]) +
                  ": definiteness watch-list; check that the specification supplies a standard (MPEP 2173.05(b))")
        ex = find_terms(EXEMPLARY_RE, text_c)
        if ex:
            _flag(c, "EXAMPLE", "warning", "exemplary/preferential language " + ", ".join('"%s"' % t for t in ex) +
                  ": examples belong in the specification, not the claim (MPEP 2173.05(d))")
        c["negative_limitations"] = find_terms(NEGATIVE_RE, text_c)
        if c["negative_limitations"]:
            _flag(c, "NEG", "info", "negative limitation(s) " + ", ".join('"%s"' % t for t in c["negative_limitations"]) +
                  ": needs basis in the original disclosure (MPEP 2173.05(i))")
        markush = len(MARKUSH_RE.findall(text_c))
        if markush:
            _flag(c, "MARKUSH", "info", "%d Markush group(s) 'selected from the group consisting of': a closed list "
                                        "of alternatives (MPEP 2173.05(h))" % markush)
        if c["category"] == "use":
            _flag(c, "USE", "warning", "'use' claim: indefinite in US practice unless active steps are recited "
                                       "(35 U.S.C. 112(b); MPEP 2173.05(q)); accepted in some other jurisdictions")
        if c["category"] == "product-by-process":
            _flag(c, "PBP", "info", "product-by-process claim: patentability is judged on the product itself, "
                                    "not the recited process (MPEP 2113)")

    # dependency integrity, depth, further-limitation checks
    live_set = set(live)
    seen_bodies = {}
    for c in claims:
        if c["type"] != "dependent":
            continue
        n = c["id"]
        valid = [p for p in c["depends_on"] if p in live_set and p < n]
        fwd = [p for p in c["depends_on"] if p in live_set and p >= n]
        missing = [p for p in c["depends_on"] if p not in live_set]
        if fwd:
            _flag(c, "FWD-REF", "error", "refers to claim(s) %s which come(s) later: a dependent claim must refer "
                  "to 'a claim previously set forth' (35 U.S.C. 112(d); MPEP 608.01(n))" % ", ".join(map(str, fwd)))
        if missing:
            canc = [p for p in missing if p in by_id]
            what = "canceled" if canc and len(canc) == len(missing) else "non-existent or canceled"
            _flag(c, "NO-REF", "error", "refers to %s claim(s) %s: a claim dependent on a canceled base claim is "
                  "rejected as incomplete (MPEP 608.01(n))" % (what, ", ".join(map(str, missing))))
        if c["multiple_dependent"]:
            n_ref = len(c["depends_on"])
            _flag(c, "MULTI", "info", "multiple dependent claim referring to claims %s%s; for USPTO fees it counts "
                  "as %d claims and triggers the 37 CFR 1.16(j) surcharge; may not serve as a basis for another "
                  "multiple dependent claim (35 U.S.C. 112(e); 37 CFR 1.75(c); MPEP 608.01(n))"
                  % (", ".join(map(str, c["depends_on"])), "" if c["_alt"] else " (NOT in the alternative)", n_ref))
            if not c["_alt"]:
                _flag(c, "MULTI-AND", "error", "improper multiple dependent claim: parents must be referenced 'in the "
                      "alternative only' ('claim 1 or 2', 'any one of claims 1-3'), not conjunctively "
                      "(35 U.S.C. 112(e); 37 CFR 1.75(c); MPEP 608.01(n))")
            chained = [p for p in valid if by_id[p]["multiple_dependent"]]
            if chained:
                _flag(c, "MULTI-CHAIN", "error", "multiple dependent claim depending from multiple dependent claim(s) "
                      "%s: prohibited (35 U.S.C. 112(e); 37 CFR 1.75(c))" % ", ".join(map(str, chained)))
        c["depth"] = 1 + max(by_id[p]["depth"] for p in valid) if valid else 0
        # A head opening with "The"/"Said" restates the parent's subject; a head such as
        # "A film made by the process of claim 9" or "Use of the composition of claim 1"
        # is itself the further limitation (a different statutory subject).
        same_subject = re.match(r"(?:the|said)\b", c["preamble"] or "", re.I) is not None
        own = c["_own_category"]
        parent = by_id[valid[0]] if valid else None
        if parent is not None:
            if own == "unknown" and parent["category"] not in ("unknown", "-"):
                c["category"], c["statutory_class"] = parent["category"], parent["statutory_class"]
            elif not _compatible(own, parent["category"]):
                _flag(c, "X-CAT", "info", "category '%s' differs from parent claim %d ('%s'): proper only if it "
                      "cannot be infringed without infringing the parent (infringement test, MPEP 608.01(n))"
                      % (own, parent["id"], parent["category"]))
        empty = not c["_body_norm"]
        identical = (not empty) and any(c["_body_norm"] == by_id[p]["_body_norm"] for p in valid)
        restates = same_subject or own == "unknown" or (parent is not None and _compatible(own, parent["category"]))
        if identical or (empty and restates):
            _flag(c, "NO-LIMIT", "error", "adds no further limitation to the claim it depends on "
                                          "(35 U.S.C. 112(d); MPEP 608.01(n))")
        elif not empty:
            key = (tuple(c["depends_on"]), c["_body_norm"])
            if key in seen_bodies:
                _flag(c, "DUP", "warning", "substantial duplicate of claim %d (same parent, same limitation): "
                                           "objectionable (MPEP 608.01(m))" % seen_bodies[key])
            else:
                seen_bodies[key] = n

    # global checks
    global_flags = []
    ids = [c["id"] for c in claims]
    if ids[0] != 1:
        global_flags.append({"code": "NUMBERING", "severity": "warning",
                             "detail": "claim numbering starts at %d, not 1 (37 CFR 1.126; MPEP 608.01(j))" % ids[0]})
    gaps = [k for k in range(ids[0], ids[-1]) if k not in by_id]
    if gaps:
        global_flags.append({"code": "GAP", "severity": "warning",
                             "detail": "claim numbering gap(s): %s missing - claims are numbered consecutively "
                                       "(37 CFR 1.126; MPEP 608.01(j)); check for a lost claim or a canceled "
                                       "claim without a marker" % ", ".join(map(str, gaps))})
    multi = [c["id"] for c in claims if c["multiple_dependent"]]
    if multi:
        global_flags.append({"code": "MULTI-COUNT", "severity": "info",
                             "detail": "%d multiple dependent claim(s): %s - alternative form only, no chaining, "
                                       "extra fee (35 U.S.C. 112(e); 37 CFR 1.75(c), 1.16(j); MPEP 608.01(n))"
                                       % (len(multi), ", ".join(map(str, multi)))})
    indep = [c for c in claims if c["type"] == "independent"]
    if indep:
        broadest = min(indep, key=lambda c: (c["words"], c["id"]))
        if broadest["id"] != 1:
            global_flags.append({"code": "BREADTH", "severity": "info",
                                 "detail": "shortest independent claim is claim %d, not claim 1; 37 CFR 1.75(g) "
                                           "expects the least restrictive claim first - check which is really "
                                           "broader (word count is only a proxy)" % broadest["id"]})

    # assemble
    for c in claims:
        c["_flags"].sort(key=lambda f: (SEVERITY_RANK[f["severity"]], f["code"]))
        c["flags"] = [f["code"] for f in c["_flags"]]
    all_flags = [dict(claim=c["id"], **f) for c in claims for f in c["_flags"]]
    all_flags += [dict(claim=None, **g) for g in global_flags]
    all_flags.sort(key=lambda f: (SEVERITY_RANK[f["severity"]], f["claim"] if f["claim"] is not None else 10 ** 6, f["code"]))
    errors = sum(1 for f in all_flags if f["severity"] == "error")

    dependents = [c for c in claims if c["type"] == "dependent"]
    first_ind = by_id[1] if 1 in by_id and by_id[1]["type"] == "independent" else (indep[0] if indep else None)
    mean_words = round(sum(c["words"] for c in indep) / len(indep), 2) if indep else None
    result = {
        "claim_count": len(claims),
        "independent_claim_count": len(indep),
        "dependent_claim_count": len(dependents),
        "multiple_dependent_claim_count": len(multi),
        "canceled_claim_count": sum(1 for c in claims if c["type"] == "canceled"),
        "max_dependency_depth": max((c["depth"] for c in claims), default=0),
        "mean_words_independent": mean_words,
        "independent_claims": [c["id"] for c in indep],
        "broadest_independent_by_words": min(indep, key=lambda c: (c["words"], c["id"]))["id"] if indep else None,
        "claim_transition_language": first_ind["transition"] if first_ind else None,
        "independent_claim_1_gist": first_ind["gist"] if first_ind else None,
        "claims": [{k: v for k, v in c.items() if not k.startswith("_")} for c in claims],
        "flags": all_flags,
        "error_count": errors,
    }
    return result


# --- rendering ---------------------------------------------------------------

def _snip(s, n=70):
    s = flat(s or "")
    return s if len(s) <= n else s[: n - 3].rstrip() + "..."


def render_tree(result):
    claims = result["claims"]
    by_id = {c["id"]: c for c in claims}
    children, roots = {}, []
    for c in claims:
        valid = [p for p in c["depends_on"] if p in by_id and p < c["id"] and by_id[p]["type"] != "canceled"]
        if c["type"] == "dependent" and valid:
            children.setdefault(valid[0], []).append(c["id"])
        else:
            roots.append(c["id"])
    lines = []

    def emit(cid, level):
        c = by_id[cid]
        pad = "   " * level
        star = "*" if c["multiple_dependent"] else ""
        if c["type"] == "canceled":
            lines.append("%s%-3s CANCELED" % (pad, cid))
        elif c["type"] == "independent":
            tr = "%s, %s" % (c["transition"], c["transition_scope"]) if c["transition"] else "no transition"
            lines.append("%s%-3s IND %s [%s] %d elem, %d w  | %s%s" % (
                pad, cid, c["category"], tr, c["elements"], c["words"], _snip(c["preamble"]),
                ("   " + " ".join(c["flags"])) if c["flags"] else ""))
        else:
            deps = ",".join(map(str, c["depends_on"])) or "?"
            unresolved = "" if any(p in by_id and p < cid for p in c["depends_on"]) else " (unresolved)"
            body = c["element_list"][0] if c["element_list"] else (c["preamble"] or "")
            if len(c["element_list"]) > 1:
                body += " ; ..."
            lines.append("%s%-3s dep %s%s  | %s%s" % (
                pad, "%d%s" % (cid, star), deps, unresolved, _snip(body),
                ("   " + " ".join(c["flags"])) if c["flags"] else ""))
        for k in sorted(children.get(cid, [])):
            emit(k, level + 1)

    for r in sorted(roots):
        emit(r, 0)
    return lines


def render_table(result):
    rows = [("id", "type", "category", "depends_on", "elements", "words", "flags")]
    for c in result["claims"]:
        t = {"independent": "ind", "dependent": "dep*" if c["multiple_dependent"] else "dep", "canceled": "canc"}[c["type"]]
        rows.append((str(c["id"]), t, c["category"], ",".join(map(str, c["depends_on"])) or "-",
                     str(c["elements"]) if c["type"] != "canceled" else "-",
                     str(c["words"]) if c["type"] != "canceled" else "-", ",".join(c["flags"]) or "-"))
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    return ["  ".join(cell.ljust(widths[i]) for i, cell in enumerate(r)).rstrip() for r in rows]


def render_text(result):
    out = []
    n_multi = result["multiple_dependent_claim_count"]
    out.append("Claims parsed: %d (independent %d, dependent %d of which %d multiple dependent, canceled %d); "
               "max dependency depth %d" % (result["claim_count"], result["independent_claim_count"],
                                            result["dependent_claim_count"], n_multi,
                                            result["canceled_claim_count"], result["max_dependency_depth"]))
    indep = [c for c in result["claims"] if c["type"] == "independent"]
    if indep:
        ranked = sorted(indep, key=lambda c: (c["words"], c["id"]))
        out.append("Independent claims by word count (fewer words = fewer limitations = generally broader): "
                   + ", ".join("%d (%dw)" % (c["id"], c["words"]) for c in ranked))
    out.append("")
    out.append("CLAIM TREE  (indent = depends on the claim above; * = multiple dependent, shown under its first parent)")
    out.extend(render_tree(result))
    out.append("")
    out.append("SUMMARY TABLE")
    out.extend(render_table(result))
    if indep:
        out.append("")
        out.append("INDEPENDENT CLAIMS")
        for c in indep:
            if c["transition"]:
                tr = 'transition "%s" = %s: %s (MPEP 2111.03)' % (c["transition"], c["transition_scope"],
                                                                   SCOPE_NOTE[c["transition_scope"]])
            else:
                tr = "no transitional phrase found"
            out.append("Claim %d - %s (%s); %s" % (c["id"], c["category"], c["statutory_class"], tr))
            out.append("  preamble: %s" % c["preamble"])
            out.append("  elements (%d):" % c["elements"])
            for i, el in enumerate(c["element_list"], 1):
                out.append("    %d. %s" % (i, el))
            out.append("  gist: %s" % c["gist"])
    out.append("")
    out.append("FLAGS  (error > warning > info)")
    if result["flags"]:
        for f in result["flags"]:
            where = "claim %d" % f["claim"] if f["claim"] is not None else "claim set"
            out.append("  %-8s %-10s %-11s %s" % (f["severity"], where, f["code"], f["detail"]))
    else:
        out.append("  none")
    if result["error_count"]:
        out.append("  => %d error-level flag(s); exit code 2" % result["error_count"])
    else:
        out.append("  no error-level flags")
    return "\n".join(out)


def stats_of(result):
    keys = ("claim_count", "independent_claim_count", "dependent_claim_count", "multiple_dependent_claim_count",
            "canceled_claim_count", "max_dependency_depth", "mean_words_independent")
    return {k: result[k] for k in keys}


def render_stats(result):
    s = stats_of(result)
    mean = "n/a" if s["mean_words_independent"] is None else "%.1f" % s["mean_words_independent"]
    return "\n".join([
        "claims:                            %d" % s["claim_count"],
        "independent claims:                %d" % s["independent_claim_count"],
        "dependent claims:                  %d" % s["dependent_claim_count"],
        "multiple dependent claims:         %d" % s["multiple_dependent_claim_count"],
        "canceled claims:                   %d" % s["canceled_claim_count"],
        "max dependency depth:              %d" % s["max_dependency_depth"],
        "mean words per independent claim:  %s   (shorter = generally broader)" % mean,
    ])


# --- demo & selftest data ----------------------------------------------------

# Synthetic claim set. Claims 1-9 are the SKILL.md worked example (a neural
# ranking retrieval method with dependent claims 2, 5 and 8 as the narrowing
# positions); claims 10-12 add a system claim with "means for" language and a
# Beauregard (computer-readable medium) claim.
DEMO = """\
What is claimed is:

1. A method comprising:
receiving, at a retrieval service, a natural-language query;
generating, by a neural ranking model, a ranked set of document passages from an index; and
transmitting, to a client device, the ranked set with per-passage confidence scores.

2. The method of claim 1, wherein the neural ranking model is a cross-encoder.

3. The method of claim 2, wherein the cross-encoder is fine-tuned on click-through data.

4. The method of claim 1, wherein the natural-language query is received over an encrypted channel.

5. The method of claim 1, wherein the index is an approximate-nearest-neighbor index.

6. The method of claim 5, wherein the approximate-nearest-neighbor index is a hierarchical navigable small-world graph.

7. The method of claim 1 or claim 5, wherein each per-passage confidence score is calibrated to a probability.

8. The method of claim 1, further comprising rewriting the natural-language query before generating the ranked set.

9. The method of claim 8, wherein the rewriting is performed by a language model.

10. A retrieval system comprising:
a processor;
a memory storing an index of document passages;
means for receiving a natural-language query from a client device; and
a neural ranking model configured to generate, from the index, a ranked set of document passages with per-passage confidence scores that are substantially calibrated.

11. The retrieval system of claim 10, wherein the index is free of duplicate passages.

12. A non-transitory computer-readable medium comprising instructions that, when executed by a processor, cause the processor to perform operations comprising:
receiving a natural-language query;
generating, by a neural ranking model, a ranked set of document passages from an index; and
transmitting the ranked set with per-passage confidence scores to a client device.
"""

# Deliberately defective set for the selftest: forward reference (3 -> 4, 8 -> 9),
# no further limitation (4), conjunctive multiple dependency (5), use claim (7),
# product-by-process (8), closed transition (9), relative term (10),
# dangling reference (12 -> 15) and a numbering gap (11).
DEFECTIVE = """\
1. A composition consisting essentially of a polymer and a plasticizer.
2. The composition of claim 1, wherein the polymer is polyethylene.
3. The composition of claim 4, wherein the plasticizer is a phthalate.
4. The composition of claim 1.
5. The composition of claims 1 and 2, further comprising a dye.
6. A kit comprising a container and an adhesive composition consisting of an epoxy resin and a hardener.
7. Use of the composition of claim 1 as a coating.
8. A film made by the process of claim 9.
9. A process for making a film, the process consisting of: melting a polymer; and extruding the melt through a die.
10. The process of claim 9, wherein the die is heated to about 200 degrees C.
12. The film of claim 15, wherein the film is transparent.
"""

# One-line (inline-numbered) set exercising "preceding claim(s)" phrases.
INLINE = ("What is claimed is: 1. A widget comprising a frame. 2. The widget of claim 1, wherein the frame is "
          "steel. 3. The widget according to any one of the preceding claims, wherein the frame is painted. "
          "4. The widget as claimed in claim 3, wherein the paint is red. 5. The widget as recited in the "
          "preceding claim, wherein the paint is glossy.")

# Amendment-style listing with status markers and a canceled base claim.
AMENDED = """\
1. (Currently Amended) A method comprising: heating a sample; and cooling the sample.
2. (Canceled)
3. (Original) The method of claim 2, wherein the sample is water.
"""


def run_selftest():
    """Hand-verified checks: expected values were worked out by hand from the
    claim texts above (word counts, tree, categories) and from the MPEP rules."""
    n_checks = [0]

    def check(name, got, want):
        n_checks[0] += 1
        ok = got == want
        print("%s  %s: got %r, expected %r" % ("PASS" if ok else "FAIL", name, got, want))
        if not ok:
            print("SELFTEST FAILED at: %s" % name, file=sys.stderr)
            sys.exit(1)

    # -- number-list and alternative-form parsing (MPEP 608.01(n) examples)
    check("numlist '1, 2, or 3'", parse_numlist("1, 2, or 3"), [1, 2, 3])
    check("numlist '1-3'", parse_numlist("1-3"), [1, 2, 3])
    check("numlist '1 or claim 2'", parse_numlist("1 or claim 2"), [1, 2])
    check("alternative 'claim 3 or 4'", alternative_form(None, "3 or 4"), True)
    check("alternative 'any one of claims 1, 2, and 3'", alternative_form("any one of ", "1, 2, and 3"), True)
    check("conjunctive 'claim 3 and 4'", alternative_form(None, "3 and 4"), False)
    check("bare range 'claims 1-3' not alternative", alternative_form(None, "1-3"), False)
    check("'claims 1-3 or 7-9' not alternative", alternative_form(None, "1-3 or 7-9"), False)

    # -- DEMO: 3 independent claims + dependents, tree, categories, transitions
    r = analyze(DEMO)
    by = {c["id"]: c for c in r["claims"]}
    check("demo: claims parsed", r["claim_count"], 12)
    check("demo: independent claims", r["independent_claims"], [1, 10, 12])
    check("demo: independent_claim_count", r["independent_claim_count"], 3)
    check("demo: dependent_claim_count", r["dependent_claim_count"], 9)
    check("demo: multiple_dependent_claim_count", r["multiple_dependent_claim_count"], 1)
    check("demo: tree parents", {n: by[n]["depends_on"] for n in range(2, 13) if n not in (10, 12)},
          {2: [1], 3: [2], 4: [1], 5: [1], 6: [5], 7: [1, 5], 8: [1], 9: [8], 11: [10]})
    check("demo: depths (1->2->3, 1->5->6, 1->8->9)", (by[3]["depth"], by[6]["depth"], by[7]["depth"], by[9]["depth"]),
          (2, 2, 2, 2))
    check("demo: max dependency depth", r["max_dependency_depth"], 2)
    check("demo: claim 7 multiple dependent, in the alternative", (by[7]["multiple_dependent"], by[7]["flags"]),
          (True, ["MULTI"]))
    check("demo: categories", (by[1]["category"], by[2]["category"], by[10]["category"], by[11]["category"], by[12]["category"]),
          ("method", "method", "apparatus", "apparatus", "crm"))
    check("demo: statutory classes", (by[1]["statutory_class"], by[10]["statutory_class"], by[12]["statutory_class"]),
          ("process", "machine", "manufacture"))
    check("demo: claim 1 transition", (by[1]["transition"], by[1]["transition_scope"]), ("comprising", "open"))
    check("demo: claim 1 preamble", by[1]["preamble"], "A method")
    check("demo: claim 12 preamble split at 'comprising:'", by[12]["preamble"],
          "A non-transitory computer-readable medium comprising instructions that, when executed by a processor, "
          "cause the processor to perform operations")
    check("demo: claim 1 elements", by[1]["elements"], 3)
    check("demo: claim 10 elements (4 ';'-separated)", by[10]["elements"], 4)
    check("demo: claim 10 element list", by[10]["element_list"],
          ["a processor", "a memory storing an index of document passages",
           "means for receiving a natural-language query from a client device",
           "a neural ranking model configured to generate, from the index, a ranked set of document passages "
           "with per-passage confidence scores that are substantially calibrated"])
    check("demo: claim 12 elements", by[12]["elements"], 3)
    check("demo: word counts (hand-counted)", (by[1]["words"], by[10]["words"], by[12]["words"]), (39, 49, 51))
    check("demo: mean words of independent claims = 139/3", r["mean_words_independent"], 46.33)
    check("demo: broadest by word count", r["broadest_independent_by_words"], 1)
    check("demo: 112(f) flag on claim 10 only", [c["id"] for c in r["claims"] if c["means_plus_function"]], [10])
    check("demo: claim 10 flags", by[10]["flags"], ["112F", "REL"])
    check("demo: relative term", by[10]["relative_terms"], ["substantially"])
    check("demo: negative limitation on claim 11", by[11]["negative_limitations"], ["free of"])
    check("demo: SKILL.md schema fields", (r["claim_transition_language"], r["independent_claim_1_gist"]),
          ("comprising", "A method comprising: receiving, at a ...; generating, by a ...; transmitting, to a ..."))
    check("demo: no error-level flags", r["error_count"], 0)

    # -- DEFECTIVE: forward / dangling references, no further limitation, improper multiple dependency
    d = analyze(DEFECTIVE)
    by = {c["id"]: c for c in d["claims"]}
    check("defective: claims parsed", d["claim_count"], 11)
    check("defective: independent claims", d["independent_claims"], [1, 6, 9])
    check("defective: dependent count", d["dependent_claim_count"], 8)
    check("defective: claim 3 forward reference", by[3]["flags"], ["FWD-REF"])
    check("defective: claim 4 no further limitation", by[4]["flags"], ["NO-LIMIT"])
    check("defective: claim 5 conjunctive multiple dependency", by[5]["flags"], ["MULTI-AND", "MULTI"])
    check("defective: claim 12 dangling reference", by[12]["flags"], ["NO-REF"])
    check("defective: numbering gap 11", [f["code"] for f in d["flags"] if f["claim"] is None][:1], ["GAP"])
    check("defective: claim 1 'consisting essentially of' = partially open",
          (by[1]["category"], by[1]["transition"], by[1]["transition_scope"]),
          ("composition", "consisting essentially of", "partially open"))
    check("defective: claim 6 kit, open", (by[6]["category"], by[6]["transition"], by[6]["transition_scope"]),
          ("kit", "comprising", "open"))
    check("defective: claim 7 use claim, cross-category vs composition parent",
          (by[7]["category"], by[7]["flags"], by[7]["depends_on"]), ("use", ["USE", "X-CAT"], [1]))
    check("defective: claim 8 product-by-process + forward ref (head carries the limitation)",
          (by[8]["category"], by[8]["flags"]), ("product-by-process", ["FWD-REF", "PBP"]))
    check("defective: claim 9 'consisting of' = closed, 2 elements",
          (by[9]["category"], by[9]["transition_scope"], by[9]["elements"]), ("method", "closed", 2))
    check("defective: claim 10 relative term 'about'", by[10]["relative_terms"], ["about"])
    check("defective: error count (3, 4, 5, 8, 12)", d["error_count"], 5)

    # -- INLINE: one-line numbering and 'preceding claim(s)' phrases
    i = analyze(INLINE)
    by = {c["id"]: c for c in i["claims"]}
    check("inline: claims parsed", i["claim_count"], 5)
    check("inline: 'any one of the preceding claims'", (by[3]["depends_on"], by[3]["multiple_dependent"]), ([1, 2], True))
    check("inline: 'as claimed in claim 3'", by[4]["depends_on"], [3])
    check("inline: 'the preceding claim' = claim 4", by[5]["depends_on"], [4])
    check("inline: max depth 1->2->3->4->5", i["max_dependency_depth"], 4)

    # -- AMENDED: status markers and canceled base claim
    a = analyze(AMENDED)
    by = {c["id"]: c for c in a["claims"]}
    check("amended: status markers stripped", (by[1]["type"], by[1]["preamble"], by[2]["type"]),
          ("independent", "A method", "canceled"))
    check("amended: dependent on canceled claim", by[3]["flags"], ["NO-REF"])
    check("amended: counts", (a["independent_claim_count"], a["dependent_claim_count"], a["canceled_claim_count"]),
          (1, 1, 1))

    print("ALL %d CHECKS PASSED" % n_checks[0])
    print("selftest OK")
    return 0


# --- CLI ---------------------------------------------------------------------

def load_text(args, parser):
    if args.demo:
        return DEMO
    if args.file:
        try:
            if args.file == "-":
                return sys.stdin.read()
            with open(args.file, encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except OSError as exc:
            parser.error("could not read %s: %s" % (args.file, exc))
    parser.error("pass --file PATH (or '-' for stdin) or --demo")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Structural analysis of a patent claim set: dependency tree, statutory category, "
                    "transitional phrase and scope, element/word counts, and MPEP-cited drafting flags.")
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", dest="demo_top", action="store_true", help="shorthand for 'parse --demo'")
    sub = parser.add_subparsers(dest="command")
    for name, helptext in [
        ("parse", "dependency tree, summary table, independent-claim detail and flags"),
        ("stats", "counts only: independent / dependent / multiple dependent, max depth, mean words"),
    ]:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--file", help="claims text file as found in a patent ('-' = stdin)")
        p.add_argument("--demo", action="store_true", help="use the built-in synthetic claim set")
        p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.command:
        if args.demo_top:
            args.command, args.demo, args.file, args.json = "parse", True, None, False
        else:
            parser.error("choose a command: parse | stats  (or --selftest / --demo)")
    text = load_text(args, parser)
    try:
        result = analyze(text)
    except ValueError as exc:
        parser.error(str(exc))
    if args.command == "stats":
        print(json.dumps(stats_of(result), indent=2) if args.json else render_stats(result))
    else:
        print(json.dumps(result, indent=2) if args.json else render_text(result))
    return 1 if result["error_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
