#!/usr/bin/env python3
"""citecheck.py — offline syntax + checksum validation of scholarly identifiers.

Companion tool for ../SKILL.md (verify-citations). It extracts every DOI,
arXiv identifier, ISBN-10/13, PMID, PMCID, ORCID iD and URL from a reference
list and checks each one against the published format rules of its scheme,
WITHOUT touching the network. `resolve` is the only networked subcommand and
it stays offline (dry run) unless `--online` is passed; `--selftest` and
`--demo` never open a socket.

Definitions implemented (the check digits are the algorithms in the standards,
not approximations):

  * DOI    ISO 26324:2022, Information and documentation - Digital object
           identifier system; DOI Handbook ch. 2 "Numbering" (doi:10.1000/182).
           prefix "10." + registrant code, "/", opaque suffix; DOI names are
           case-insensitive (ASCII case folding), so the normal form here is
           lower-case. Matcher: 10\\.\\d{4,9}(\\.\\d+)*/[^\\s"\\x00]+ with
           trailing punctuation stripped. Registrant codes outside
           10.1000-10.99999, truncated-looking or placeholder suffixes are
           flagged for REVIEW.
           NOTE ON SCOPE: the DOI Handbook (normative for ISO 26324) permits any
           Unicode Graphic character in the suffix -- including angle brackets,
           semicolons and spaces -- and sets no length or digit limit on the
           registrant code. The 4-9 digit prefix and the no-whitespace rule
           applied here are CROSSREF corpus heuristics, not ISO requirements,
           and are reported as such. Angle brackets are accepted so that the
           legacy AMS/AGU/GSA SICI-style DOIs validate, e.g.
           10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2 (Brier 1950).
  * arXiv  arXiv identifier scheme, https://info.arxiv.org/help/arxiv_identifier.html
           new scheme (0704 onwards): YYMM.NNNN for 0704-1412, YYMM.NNNNN from
           1501, optional vN; old scheme (9107-0703): archive[.subject]/YYMMNNN.
           MM must be 01-12. Era checks compare against these fixed scheme
           boundaries only - the wall clock is never consulted.
  * ISBN   ISO 2108:2017; ISBN Users' Manual, International ISBN Agency,
           7th ed. (2017), sec. 5 "Check digit". ISBN-13: GS1 prefix 978/979,
           weights 1,3,1,3,... over 12 digits, check = (10 - sum mod 10) mod 10.
           ISBN-10: weights 10,9,...,2 over 9 digits, check = (11 - sum mod 11)
           mod 11, value 10 written "X".
  * ORCID  ORCID iD = 16 characters whose last is an ISO/IEC 7064:2003
           MOD 11-2 check character ("Structure of the ORCID Identifier",
           ORCID support documentation): total = (total + digit) * 2 over the
           15 base digits; check = (12 - total mod 11) mod 11, 10 -> "X".
  * PMID   PubMed identifier: positive integer of 1-8 digits (values below 100
           flagged for REVIEW). PMCID: "PMC" + digits.
  * URL    RFC 3986 generic syntax: scheme (http/https/ftp) + host required;
           reserved example/placeholder domains (RFC 2606, RFC 6761) flagged.

Verdicts follow SKILL.md: PASS / REVIEW (valid syntax but suspicious) / FAIL
(syntax or checksum error). Exit code 2 when any identifier FAILs, else 0;
1 = usage or input error. Deterministic: no wall clock, no randomness.

Stdlib only. Python 3.9+.

Usage:
    python3 citecheck.py validate --file refs.txt            # free text, or .json list of strings
    python3 citecheck.py validate --text "doi: 10.1038/nature14539" --json
    cat refs.txt | python3 citecheck.py validate
    python3 citecheck.py resolve  --file refs.txt            # dry run: prints planned lookups
    python3 citecheck.py resolve  --file refs.txt --online   # DOI handle API, arXiv API, Open Library
    python3 citecheck.py --demo
    python3 citecheck.py --selftest
"""

import argparse
import http.client
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# --- patterns ----------------------------------------------------------------

# Consumed spans are overwritten with MASK so later passes cannot re-match
# inside them (a DOI inside a doi.org URL, an arXiv number inside a DOI, ...).
# MASK is neither whitespace nor a word character, so every token class below
# stops at it.
MASK = "\x00"
NS = r"[^\s\x00]"  # one non-space, non-mask character

URL_RE = re.compile(r"\b(?:https?|ftp)://[^\s<>\"'`\x00]+", re.I)

DOI_FULL_RE = re.compile(r"^10\.(\d{4,9})((?:\.\d+)*)/([^\s\"\x00]+)$")
BARE_DOI_RE = re.compile(r"(?<![\w.])10\.\d{4,9}(?:\.\d+)*/[^\s\"\x00]+")
LABEL_DOI_RE = re.compile(
    r"\bdoi\s*:\s*(" + NS + r"+)|\b(?:www\.)?(?:dx\.)?doi\.org/(" + NS + r"*)", re.I
)
DOI_PLACEHOLDER_RE = re.compile(r"^(?:[x]+|[n]+|0+|\?+|xyz|abc|1234(?:5(?:6)?)?)$|xxxx", re.I)

ARXIV_NEW_RE = re.compile(r"^(\d{2})(\d{2})\.(\d{4,5})(v\d+)?$")
ARXIV_OLD_RE = re.compile(
    r"^([a-z]+(?:-[a-z]+)*)(?:\.([A-Za-z]{2}|[a-z]{2,}(?:-[a-z]{2,})*))?/(\d{2})(\d{2})(\d{3})(v\d+)?$"
)
LABEL_ARXIV_RE = re.compile(r"\barxiv\s*:\s*(" + NS + r"+)", re.I)
BARE_ARXIV_NEW_RE = re.compile(r"(?<![\w./:-])\d{4}\.\d{4,5}(?:v\d+)?(?![\w/-])(?!\.\d)")
# Archives that issued old-scheme identifiers (arXiv archive list incl. the
# subsumed archives). Used to recognise bare old-scheme ids in prose and to
# flag unknown archives in labelled ones.
OLD_ARCHIVES = (
    "acc-phys", "adap-org", "alg-geom", "ao-sci", "astro-ph", "atom-ph", "bayes-an",
    "chao-dyn", "chem-ph", "cmp-lg", "comp-gas", "cond-mat", "cs", "dg-ga", "funct-an",
    "gr-qc", "hep-ex", "hep-lat", "hep-ph", "hep-th", "math", "math-ph", "mtrl-th",
    "nlin", "nucl-ex", "nucl-th", "patt-sol", "physics", "plasm-ph", "q-alg", "q-bio",
    "quant-ph", "solv-int", "supr-con",
)
BARE_ARXIV_OLD_RE = re.compile(
    r"(?<![\w./:-])(?:" + "|".join(re.escape(a) for a in sorted(OLD_ARCHIVES, key=lambda a: (-len(a), a)))
    + r")(?:\.(?:[A-Za-z]{2}|[a-z]{2,}(?:-[a-z]{2,})*))?/\d{7}(?:v\d+)?(?![\w/-])(?!\.\d)"
)

LABEL_ISBN_RE = re.compile(r"\bISBN(?:[- ]?1[03](?=[\s:]))?\s*:?\s*([0-9Xx][0-9Xx\- ]{7,}[0-9Xx])", re.I)
BARE_ISBN13_RE = re.compile(r"(?<![\w-])97[89](?:[- ]?\d){9}[- ]?\d(?![\w-])")
BARE_ISBN10_RE = re.compile(r"(?<![\w-])\d{1,5}-\d{1,7}-\d{1,7}-[\dXx](?![\w-])")

ORCID_SHAPE = r"\d{4}-\d{4}-\d{4}-\d{3}[\dXx]"
LABEL_ORCID_RE = re.compile(
    r"\bORCID(?:\s*iD)?\s*:?\s*(?:https?://(?:www\.)?orcid\.org/)?(" + ORCID_SHAPE + r")", re.I
)
BARE_ORCID_RE = re.compile(r"(?<![\w-])" + ORCID_SHAPE + r"(?![\w-])")

LABEL_PMID_RE = re.compile(r"\bPMID\s*:?\s*(\d+)", re.I)
LABEL_PMCID_RE = re.compile(r"\bPMCID\s*:?\s*(?:PMC)?(\d+)", re.I)
BARE_PMC_RE = re.compile(r"\bPMC(\d+)\b")

AVAILABLE_RE = re.compile(r"\bAvailable\s*:\s*(" + NS + r"+)", re.I)
BARE_WWW_RE = re.compile(r"(?<![\w@./])www\.[^\s<>\"'`\x00]+", re.I)
URLISH_RE = re.compile(r"^[\w.-]+\.[a-z]{2,}(?:[/:?#].*)?$", re.I)

HOST_RE = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{1,62}$")
IPV4_RE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
# RFC 2606 / RFC 6761 reserved names plus the usual filler words.
PLACEHOLDER_HOST_RE = re.compile(
    r"(?:^|\.)example\.(?:com|net|org|edu)$|(?:^|\.)(?:example|test|invalid|localhost)$"
    r"|lorem|ipsum|placeholder|your-?domain|(?:^|\.)domain\.com$"
)

ENTRY_MARK_RE = re.compile(r"(?m)^[ \t]*\[(\d+)\][ \t]*")
PREVIEW_LEN = 48

# --- generic helpers ---------------------------------------------------------

_TRAIL = ".,;:!?'\""
_PAIRS = {")": "(", "]": "[", "}": "{", ">": "<"}


def strip_trailing(token):
    """Drop sentence punctuation glued to the end of a token. An opening
    bracket at the end is always dropped (markdown '[10.1000/182](' ...); a
    closing bracket only when it is unbalanced (10.1016/S0140-6736(20)30183-5
    keeps its parentheses, '(doi:10.1000/182)' loses the outer one)."""
    while token:
        last = token[-1]
        if last in _TRAIL or last in "([{":
            token = token[:-1]
            continue
        if last in _PAIRS and token.count(last) > token.count(_PAIRS[last]):
            token = token[:-1]
            continue
        break
    return token


def make_item(kind, raw, normalised, entry_label, checksum=None):
    return {
        "entry": entry_label,
        "type": kind,
        "raw": raw,
        "normalised": normalised,
        "syntax_ok": True,
        "checksum_ok": checksum,
        "verdict": "PASS",
        "errors": [],
        "warnings": [],
        "notes": [],
    }


def syntax_error(item, msg):
    item["syntax_ok"] = False
    item["errors"].append(msg)


def finalise(item):
    """FAIL on any error (syntax or checksum), REVIEW on any warning, else PASS."""
    if item["errors"]:
        item["verdict"] = "FAIL"
    elif item["warnings"]:
        item["verdict"] = "REVIEW"
    else:
        item["verdict"] = "PASS"
    return item


# --- check digits (ISO 2108 / ISO 7064) -------------------------------------


def isbn13_check_digit(first12):
    """ISBN-13 (ISO 2108:2017; ISBN Users' Manual 7th ed. sec. 5): weights
    1,3,1,3,... over the first 12 digits; check = (10 - sum mod 10) mod 10."""
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(first12))
    return str((10 - total % 10) % 10)


def isbn10_check_digit(first9):
    """ISBN-10 (ISO 2108): weights 10,9,...,2 over the first 9 digits;
    check = (11 - sum mod 11) mod 11; the value 10 is written 'X'."""
    total = sum(int(d) * (10 - i) for i, d in enumerate(first9))
    r = (11 - total % 11) % 11
    return "X" if r == 10 else str(r)


def orcid_check_char(base15):
    """ISO/IEC 7064:2003 MOD 11-2 as specified for ORCID iDs: total =
    (total + digit) * 2 over the 15 base digits; check = (12 - total mod 11)
    mod 11; 10 -> 'X'."""
    total = 0
    for d in base15:
        total = (total + int(d)) * 2
    result = (12 - total % 11) % 11
    return "X" if result == 10 else str(result)


# --- per-scheme checkers -----------------------------------------------------


def check_doi(candidate, raw, label):
    item = make_item("doi", raw, candidate.lower(), label)
    m = DOI_FULL_RE.match(candidate)
    if not m:
        if not candidate:
            syntax_error(item, "empty DOI (nothing after the doi: label / doi.org/)")
        else:
            syntax_error(item, "does not match 10.NNNN/suffix (Crossref pattern; ISO 26324 itself sets no digit limit on the registrant code)")
        return item
    registrant, subdivision, suffix = m.groups()
    if not 1000 <= int(registrant) <= 99999:
        item["warnings"].append(
            "registrant code 10.%s lies outside the 10.1000-10.99999 range in use" % registrant
        )
    if subdivision:
        item["notes"].append("prefix carries a sub-registrant subdivision (%s); rare but allowed" % subdivision)
    truncated = None
    if suffix[-1] in "-_/.(,[":
        truncated = "ends with %r" % suffix[-1]
    elif "..." in suffix:
        truncated = "contains an ellipsis"
    elif suffix.count("(") != suffix.count(")") or suffix.count("[") != suffix.count("]"):
        truncated = "unbalanced brackets"
    if truncated:
        item["warnings"].append("suffix looks truncated (%s)" % truncated)
    if DOI_PLACEHOLDER_RE.search(suffix):
        item["warnings"].append("suffix looks like a placeholder")
    return item


def _arxiv_year(yy):
    """Two-digit year -> absolute year using the scheme's fixed 1991 start
    (91-99 -> 1991-1999, 00-90 -> 2000-2090). Not a wall-clock check."""
    y = int(yy)
    return 1900 + y if y >= 91 else 2000 + y


def check_arxiv(candidate, raw, label):
    cand = candidate.strip()
    item = make_item("arxiv", raw, cand, label)
    m_new = ARXIV_NEW_RE.match(cand)
    m_old = ARXIV_OLD_RE.match(cand)
    if m_new:
        yy, mm, num, ver = m_new.groups()
        year, month = _arxiv_year(yy), int(mm)
        item["normalised"] = "%s%s.%s%s" % (yy, mm, num, ver or "")
        if not 1 <= month <= 12:
            syntax_error(item, "month %s is not 01-12" % mm)
        elif (year, month) < (2007, 4):
            syntax_error(item, "new-scheme identifiers (YYMM.NNNNN) begin at 0704")
        elif (year, month) < (2015, 1) and len(num) != 4:
            syntax_error(item, "identifiers before 1501 carry a 4-digit sequence number (found %d)" % len(num))
        elif (year, month) >= (2015, 1) and len(num) != 5:
            syntax_error(item, "identifiers from 1501 on carry a 5-digit sequence number (found %d)" % len(num))
        else:
            item["notes"].append("new scheme, %d-digit era (%04d-%02d)" % (len(num), year, month))
        if ver:
            item["notes"].append("version %s pinned" % ver)
        return item
    if m_old:
        archive, subject, yy, mm, num, ver = m_old.groups()
        year, month = _arxiv_year(yy), int(mm)
        item["normalised"] = "%s%s/%s%s%s%s" % (
            archive.lower(), "." + subject if subject else "", yy, mm, num, ver or ""
        )
        if not 1 <= month <= 12:
            syntax_error(item, "month %s is not 01-12" % mm)
        elif not (1991, 7) <= (year, month) <= (2007, 3):
            syntax_error(item, "old-scheme identifiers (archive/YYMMNNN) run 9107-0703")
        else:
            item["notes"].append("old scheme (%04d-%02d)" % (year, month))
        if archive.lower() not in OLD_ARCHIVES:
            item["warnings"].append("unrecognised old-scheme archive %r" % archive)
        if ver:
            item["notes"].append("version %s pinned" % ver)
        return item
    syntax_error(item, "not an arXiv identifier (new YYMM.NNNNN or old archive/YYMMNNN)")
    return item


def check_isbn(token, raw, label):
    compact = re.sub(r"[-\s]", "", token).upper()
    item = make_item("isbn", raw, compact, label)
    if len(compact) == 13:
        item["type"] = "isbn13"
        if not compact.isdigit():
            syntax_error(item, "ISBN-13 must be all digits")
            return item
        if compact[:3] not in ("978", "979"):
            syntax_error(item, "ISBN-13 must start 978 or 979 (GS1 prefix)")
        want = isbn13_check_digit(compact[:12])
        item["checksum_ok"] = want == compact[12]
        if not item["checksum_ok"]:
            item["errors"].append("check digit mismatch: computed %s, found %s" % (want, compact[12]))
        elif compact[:3] == "978":
            item["notes"].append("ISBN-10 equivalent %s%s" % (compact[3:12], isbn10_check_digit(compact[3:12])))
        elif compact[:3] == "979":
            item["notes"].append("979 prefix: no ISBN-10 equivalent")
        return item
    if len(compact) == 10:
        item["type"] = "isbn10"
        if not re.fullmatch(r"\d{9}[\dX]", compact):
            syntax_error(item, "ISBN-10 must be 9 digits plus a digit/X check character")
            return item
        want = isbn10_check_digit(compact[:9])
        item["checksum_ok"] = want == compact[9]
        if not item["checksum_ok"]:
            item["errors"].append("check digit mismatch: computed %s, found %s" % (want, compact[9]))
        else:
            item["notes"].append("ISBN-13 equivalent 978%s%s" % (compact[:9], isbn13_check_digit("978" + compact[:9])))
        return item
    syntax_error(item, "ISBN must have 10 or 13 characters (found %d)" % len(compact))
    return item


def check_orcid(token, raw, label):
    compact = token.replace("-", "").upper()
    item = make_item("orcid", raw, token.upper(), label)
    if not re.fullmatch(r"\d{15}[\dX]", compact):
        syntax_error(item, "ORCID iD must be 16 characters 0000-0000-0000-000X")
        return item
    item["normalised"] = "-".join(compact[i:i + 4] for i in range(0, 16, 4))
    want = orcid_check_char(compact[:15])
    item["checksum_ok"] = want == compact[15]
    if not item["checksum_ok"]:
        item["errors"].append("ISO 7064 MOD 11-2 check character mismatch: computed %s, found %s" % (want, compact[15]))
    return item


def check_pmid(digits, raw, label):
    item = make_item("pmid", raw, digits, label)
    if not digits.isdigit():
        syntax_error(item, "PMID must be digits only")
        return item
    value = int(digits)
    item["normalised"] = str(value)
    if len(digits) > 8:
        syntax_error(item, "PMID has %d digits (PubMed IDs are 1-8 digits)" % len(digits))
    elif value == 0:
        syntax_error(item, "PMID must be a positive integer")
    elif value < 100:
        item["warnings"].append("PMID below 100 is suspicious (earliest PubMed records)")
    if digits != str(value) and item["syntax_ok"]:
        item["notes"].append("leading zeros dropped")
    return item


def check_pmcid(digits, raw, label):
    item = make_item("pmcid", raw, "PMC" + digits, label)
    if not digits.isdigit() or int(digits) == 0:
        syntax_error(item, "PMCID must be PMC followed by a positive integer")
    elif len(digits) > 8:
        item["warnings"].append("PMCID has %d digits; current PMCIDs have at most 8" % len(digits))
    return item


def check_url(raw, label):
    item = make_item("url", raw, raw, label)
    try:
        parts = urllib.parse.urlsplit(raw)
    except ValueError as exc:
        syntax_error(item, "unparseable URL (%s)" % exc)
        return item
    scheme = parts.scheme.lower()
    if scheme not in ("http", "https", "ftp"):
        syntax_error(item, "missing or unsupported scheme (expected http(s):// or ftp://)")
    host = parts.hostname or ""
    if not host:
        syntax_error(item, "missing host")
    elif ":" in host or host == "localhost" or IPV4_RE.match(host):
        pass  # IPv6 literal, localhost, or IPv4 address
    elif not host.isascii():
        item["notes"].append("internationalised host name (not validated)")
    elif not HOST_RE.match(host):
        syntax_error(item, "malformed host %r" % host)
    if any(ch.isspace() for ch in raw):
        syntax_error(item, "whitespace inside URL")
    if "//" in parts.path:
        item["warnings"].append("consecutive slashes in the path (often a copy-paste error)")
    if PLACEHOLDER_HOST_RE.search(host):
        item["warnings"].append("reserved example domain (RFC 2606) - looks like a placeholder")
    if scheme == "http":
        item["notes"].append("plain http (not https)")
    head = len(parts.scheme) + 3 + len(parts.netloc)
    item["normalised"] = raw[:head].lower() + raw[head:]
    return item


def missing_scheme_url(token, label):
    item = make_item("url", token, token, label)
    syntax_error(item, "missing scheme (expected https:// or http://)")
    return item


# --- extraction --------------------------------------------------------------


def classify_url(raw, label):
    """A URL that merely wraps another identifier (doi.org, arxiv.org, orcid.org,
    PubMed/PMC) is reported as that identifier, not as a URL."""
    parts = urllib.parse.urlsplit(raw)
    host = (parts.hostname or "").lower()
    path = parts.path
    if host in ("doi.org", "dx.doi.org", "www.doi.org"):
        cand = urllib.parse.unquote(path.lstrip("/"))
        if cand.lower().startswith("doi:"):
            cand = cand[4:]
        item = check_doi(strip_trailing(cand), raw, label)
        item["notes"].insert(0, "embedded in a doi.org URL (URL not counted separately)")
        if host == "dx.doi.org":
            item["notes"].append("legacy dx.doi.org host; current form is https://doi.org/<doi>")
        if parts.scheme.lower() == "http":
            item["notes"].append("http scheme; https://doi.org/<doi> is the recommended form")
        return item
    if host in ("arxiv.org", "www.arxiv.org", "export.arxiv.org"):
        m = re.match(r"^/(?:abs|pdf|html|ps|format|src)/(.+?)(?:\.pdf)?/?$", path)
        if m:
            item = check_arxiv(m.group(1), raw, label)
            item["notes"].insert(0, "embedded in an arxiv.org URL")
            return item
    if host in ("orcid.org", "www.orcid.org"):
        m = re.match(r"^/(" + ORCID_SHAPE + r")/?$", path)
        if m:
            item = check_orcid(m.group(1), raw, label)
            item["notes"].insert(0, "embedded in an orcid.org URL")
            return item
    if host in ("pubmed.ncbi.nlm.nih.gov", "www.ncbi.nlm.nih.gov"):
        m = re.match(r"^/(?:pubmed/)?(\d+)/?$", path)
        if m:
            item = check_pmid(m.group(1), raw, label)
            item["notes"].insert(0, "embedded in a PubMed URL")
            return item
    if host in ("pmc.ncbi.nlm.nih.gov", "www.ncbi.nlm.nih.gov"):
        m = re.match(r"^/(?:pmc/)?articles/PMC(\d+)/?", path, re.I)
        if m:
            item = check_pmcid(m.group(1), raw, label)
            item["notes"].insert(0, "embedded in a PMC URL")
            return item
    return check_url(raw, label)


def _isbn_token(token):
    """Trim space-separated groups that are not part of the ISBN
    ('0-306-40615-2 2004' -> '0-306-40615-2')."""
    groups = token.split(" ")
    for k in range(1, len(groups) + 1):
        cand = " ".join(groups[:k])
        if sum(ch.isalnum() for ch in cand) in (10, 13):
            return cand
    return token


def extract_identifiers(text, label):
    """Return the identifier items found in one reference entry, in order of
    appearance. Passes: A) scheme'd URLs, B) labelled ids, C) bare ids,
    D) scheme-less URL tokens. Each match is masked before the next pass."""
    found = []
    buf = text

    def take(start, end):
        nonlocal buf
        buf = buf[:start] + MASK * (end - start) + buf[end:]

    def add(start, item, end):
        found.append((start, item))
        take(start, end)

    # A. URLs (may wrap DOI / arXiv / ORCID / PubMed identifiers)
    for m in list(URL_RE.finditer(buf)):
        raw = strip_trailing(m.group(0))
        if raw:
            add(m.start(), classify_url(raw, label), m.start() + len(raw))

    # B. labelled identifiers
    for m in list(LABEL_DOI_RE.finditer(buf)):
        if m.group(1) is not None:
            token = strip_trailing(m.group(1))
            add(m.start(), check_doi(token, token, label), m.start(1) + len(token))
        else:
            token = strip_trailing(urllib.parse.unquote(m.group(2)))
            item = check_doi(token, m.group(0)[: len(m.group(0)) - len(m.group(2)) + len(token)], label)
            item["notes"].insert(0, "embedded in a doi.org URL (URL not counted separately)")
            add(m.start(), item, m.start(2) + len(token))
    for m in list(LABEL_ARXIV_RE.finditer(buf)):
        token = strip_trailing(m.group(1))
        add(m.start(), check_arxiv(token, token, label), m.start(1) + len(token))
    for m in list(LABEL_ISBN_RE.finditer(buf)):
        token = _isbn_token(m.group(1)).rstrip()
        add(m.start(), check_isbn(token, token, label), m.start(1) + len(token))
    for m in list(LABEL_ORCID_RE.finditer(buf)):
        add(m.start(), check_orcid(m.group(1), m.group(1), label), m.end())
    for m in list(LABEL_PMID_RE.finditer(buf)):
        add(m.start(), check_pmid(m.group(1), m.group(0), label), m.end())
    for m in list(LABEL_PMCID_RE.finditer(buf)):
        add(m.start(), check_pmcid(m.group(1), m.group(0), label), m.end())

    # C. bare identifiers
    for m in list(BARE_DOI_RE.finditer(buf)):
        token = strip_trailing(m.group(0))
        add(m.start(), check_doi(token, token, label), m.start() + len(token))
    for m in list(BARE_ORCID_RE.finditer(buf)):
        add(m.start(), check_orcid(m.group(0), m.group(0), label), m.end())
    for m in list(BARE_ISBN13_RE.finditer(buf)):
        add(m.start(), check_isbn(m.group(0), m.group(0), label), m.end())
    for m in list(BARE_ISBN10_RE.finditer(buf)):
        if sum(ch.isalnum() for ch in m.group(0)) == 10:
            add(m.start(), check_isbn(m.group(0), m.group(0), label), m.end())
    for m in list(BARE_ARXIV_OLD_RE.finditer(buf)):
        add(m.start(), check_arxiv(m.group(0), m.group(0), label), m.end())
    for m in list(BARE_ARXIV_NEW_RE.finditer(buf)):
        # A bare YYMM.NNNNN with an impossible month is almost certainly a
        # number, not an arXiv id: leave it alone (labelled ids are always kept).
        if 1 <= int(m.group(0)[2:4]) <= 12:
            add(m.start(), check_arxiv(m.group(0), m.group(0), label), m.end())
    for m in list(BARE_PMC_RE.finditer(buf)):
        add(m.start(), check_pmcid(m.group(1), m.group(0), label), m.end())

    # D. scheme-less URL tokens (IEEE "Available:" or bare www.)
    for m in list(AVAILABLE_RE.finditer(buf)):
        token = strip_trailing(m.group(1))
        if token and URLISH_RE.match(token):
            add(m.start(1), missing_scheme_url(token, label), m.start(1) + len(token))
    for m in list(BARE_WWW_RE.finditer(buf)):
        token = strip_trailing(m.group(0))
        if token:
            add(m.start(), missing_scheme_url(token, label), m.start() + len(token))

    found.sort(key=lambda pair: pair[0])
    # The same identifier written twice in one entry (label + URL, markdown
    # link text + target) is one identifier: keep the first, merge the notes.
    merged, seen = [], {}
    for _, item in found:
        key = (item["type"], item["normalised"])
        if key in seen:
            keep = seen[key]
            for field in ("errors", "warnings", "notes"):
                for msg in item[field]:
                    if msg not in keep[field]:
                        keep[field].append(msg)
            continue
        seen[key] = item
        merged.append(item)
    return [finalise(item) for item in merged]


# --- input -------------------------------------------------------------------


def _clean(text):
    return re.sub(r"\s+", " ", text).strip()


def split_entries(text):
    """Split free text into reference entries: IEEE-style '[N] ...' blocks when
    present (wrapped lines are re-joined), otherwise one entry per non-blank
    line. Returns [(label, text)]."""
    text = text.replace("\r\n", "\n")
    marks = list(ENTRY_MARK_RE.finditer(text))
    if marks:
        entries = []
        pre = _clean(text[: marks[0].start()])
        if pre:
            entries.append(("(pre)", pre))
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
            entries.append(("[%s]" % m.group(1), _clean(text[m.end():end])))
        return entries
    lines = [_clean(ln) for ln in text.split("\n") if ln.strip()]
    return [("L%d" % i, ln) for i, ln in enumerate(lines, start=1)]


def entries_from_json(data):
    """JSON input: a list of strings, a list of objects with a text-like key,
    or {"references": [...]}."""
    if isinstance(data, dict):
        data = data.get("references", data.get("items", []))
    if not isinstance(data, list):
        raise ValueError("JSON input must be a list of strings (or {\"references\": [...]})")
    entries = []
    for i, ref in enumerate(data, start=1):
        if isinstance(ref, dict):
            for key in ("reference", "citation", "raw", "text"):
                if isinstance(ref.get(key), str):
                    ref = ref[key]
                    break
            else:
                raise ValueError("item %d: object has no reference/citation/raw/text string" % i)
        if not isinstance(ref, str):
            raise ValueError("item %d: expected a string, got %s" % (i, type(ref).__name__))
        m = ENTRY_MARK_RE.match(ref)
        label = "[%s]" % m.group(1) if m else "#%d" % i
        entries.append((label, _clean(ref[m.end():] if m else ref)))
    return entries


def load_entries(args, parser):
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                content = fh.read()
            if args.file.lower().endswith(".json"):
                return entries_from_json(json.loads(content))
            return split_entries(content)
        except (OSError, ValueError) as exc:
            parser.error("could not load %s: %s" % (args.file, exc))
    if args.text is not None:
        return split_entries(args.text)
    if sys.stdin is not None and not sys.stdin.isatty():
        return split_entries(sys.stdin.read())
    parser.error("pass --file PATH, --text '...', or pipe references on stdin")


# --- report ------------------------------------------------------------------


def preview(text):
    return text if len(text) <= PREVIEW_LEN else text[: PREVIEW_LEN - 3].rstrip() + "..."


def build_report(entries, command="validate"):
    items, rows = [], []
    for label, body in entries:
        idx = []
        for item in extract_identifiers(body, label):
            idx.append(len(items))
            items.append(item)
        rows.append({"label": label, "text": body, "preview": preview(body), "identifiers": idx})
    report = {"tool": "citecheck", "command": command, "entries": rows, "items": items}
    summarise(report)
    return report


def summarise(report):
    items = report["items"]
    counts = {"PASS": 0, "REVIEW": 0, "FAIL": 0}
    by_type = {}
    for item in items:
        counts[item["verdict"]] += 1
        by_type[item["type"]] = by_type.get(item["type"], 0) + 1
    overall = "FAIL" if counts["FAIL"] else ("REVIEW" if counts["REVIEW"] else "PASS")
    report["summary"] = {
        "entries": len(report["entries"]),
        "entries_without_identifiers": sum(1 for e in report["entries"] if not e["identifiers"]),
        "identifiers": len(items),
        "pass": counts["PASS"],
        "review": counts["REVIEW"],
        "fail": counts["FAIL"],
        "by_type": dict(sorted(by_type.items())),
        "verdict": overall,
    }
    report["exit_code"] = 1 if counts["FAIL"] else 0
    return report


def validate_text(text):
    return build_report(split_entries(text))


def render_text(report):
    s = report["summary"]
    mode = report["command"]
    if report.get("online") is True:
        mode += " (online)"
    elif report.get("online") is False:
        mode += " (dry run, no network)"
    lines = ["citecheck %s: %d entries, %d identifiers" % (mode, s["entries"], s["identifiers"])]
    for entry in report["entries"]:
        lines.append("")
        lines.append("%s %s" % (entry["label"], entry["preview"]))
        if not entry["identifiers"]:
            lines.append("    (no identifiers found)")
        for i in entry["identifiers"]:
            item = report["items"][i]
            lines.append("    %-7s %-7s %s" % (item["verdict"], item["type"], item["normalised"]))
            for e in item["errors"]:
                lines.append("            error: %s" % e)
            for w in item["warnings"]:
                lines.append("            warn:  %s" % w)
            for n in item["notes"]:
                lines.append("            note:  %s" % n)
    lines.append("")
    lines.append(
        "Summary: %d identifiers in %d entries -- PASS %d, REVIEW %d, FAIL %d"
        % (s["identifiers"], s["entries"], s["pass"], s["review"], s["fail"])
    )
    if s["entries_without_identifiers"]:
        lines.append("%d entries carry no identifier at all (check them by hand)." % s["entries_without_identifiers"])
    lines.append("Verdict: %s -> exit %d" % (s["verdict"], report["exit_code"]))
    return "\n".join(lines)


def render_json(report):
    return json.dumps(report, indent=2, ensure_ascii=False)


# --- resolve (the only networked command) ------------------------------------

DEFAULT_UA = "citecheck/1.0 (verify-citations companion tool; stdlib urllib)"


def plan_lookup(item):
    """The URL `resolve --online` would query for this item, or None."""
    if item["verdict"] == "FAIL":
        return None
    kind, ident = item["type"], item["normalised"]
    if kind == "doi":
        return "https://doi.org/api/handles/" + urllib.parse.quote(ident, safe="/:;()")
    if kind == "arxiv":
        return "https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(ident, safe="/")
    if kind in ("isbn10", "isbn13"):
        return "https://openlibrary.org/isbn/%s.json" % ident
    return None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # surfaces 3xx as HTTPError so the caller can read the code


def http_fetch(url, user_agent, timeout, follow_redirects=True, method="GET"):
    """Return (status, body_bytes, headers, error_message)."""
    req = urllib.request.Request(
        url, method=method,
        headers={"User-Agent": user_agent, "Accept": "application/json, application/atom+xml;q=0.9, */*;q=0.5"},
    )
    opener = urllib.request.build_opener() if follow_redirects else urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = b"" if method == "HEAD" else resp.read()
            return resp.status, body, resp.headers, None
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read()
        except Exception:  # noqa: BLE001 - any read failure just means "no body"
            body = b""
        return exc.code, body, exc.headers, None
    except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        return None, b"", None, "%s: %s" % (type(exc).__name__, reason)


def _result(status, detail, target=None):
    return {"status": status, "detail": detail, "target": target}


def resolve_doi(doi, args):
    api = plan_lookup({"verdict": "PASS", "type": "doi", "normalised": doi})
    status, body, _, err = http_fetch(api, args.user_agent, args.timeout)
    if err is None and body:
        try:
            data = json.loads(body.decode("utf-8", "replace"))
        except ValueError:
            data = None
        if isinstance(data, dict) and "responseCode" in data:
            rc = data.get("responseCode")
            if rc == 1:
                target = None
                for v in data.get("values", []):
                    if v.get("type") == "URL":
                        target = v.get("data", {}).get("value")
                        break
                return _result("resolves", "resolves via handle API -> %s" % (target or "(no URL value)"), target)
            if rc == 100:
                return _result("not-found", "handle API: DOI not registered (responseCode 100)")
            return _result("error", "handle API responseCode %s" % rc)
    # Fallback: HEAD https://doi.org/<doi> without following the redirect.
    head_url = "https://doi.org/" + urllib.parse.quote(doi, safe="/:;()")
    status, _, headers, err = http_fetch(head_url, args.user_agent, args.timeout, follow_redirects=False, method="HEAD")
    if err:
        return _result("error", "lookup failed (%s)" % err)
    if status in (200, 301, 302, 303, 307, 308):
        location = headers.get("Location") if headers is not None else None
        return _result("resolves", "HTTP %d from doi.org%s" % (status, " -> " + location if location else ""), location)
    if status == 404:
        return _result("not-found", "HTTP 404 from doi.org")
    return _result("error", "HTTP %s from doi.org" % status)


def resolve_arxiv(aid, args):
    url = plan_lookup({"verdict": "PASS", "type": "arxiv", "normalised": aid})
    status, body, _, err = http_fetch(url, args.user_agent, args.timeout)
    if err:
        return _result("error", "lookup failed (%s)" % err)
    if status != 200:
        return _result("error", "arXiv API HTTP %s" % status)
    try:
        root = ET.fromstring(body)
    except ET.ParseError as exc:
        return _result("error", "arXiv API returned an unparseable feed (%s)" % exc)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entries = root.findall("a:entry", ns)
    if not entries:
        return _result("not-found", "arXiv API returned no entry for this id")
    title = " ".join((entries[0].findtext("a:title", default="", namespaces=ns)).split())
    eid = entries[0].findtext("a:id", default="", namespaces=ns)
    if title == "Error" or "api/errors" in eid:
        summary = " ".join((entries[0].findtext("a:summary", default="", namespaces=ns)).split())
        return _result("not-found", "arXiv API error: %s" % (summary or "unknown id"))
    return _result("resolves", 'arXiv title: "%s"' % title, eid or None)


def resolve_isbn(isbn, args):
    url = plan_lookup({"verdict": "PASS", "type": "isbn13", "normalised": isbn})
    status, body, _, err = http_fetch(url, args.user_agent, args.timeout)
    if err:
        return _result("error", "lookup failed (%s)" % err)
    if status == 404:
        return _result("not-found", "Open Library has no record for this ISBN")
    if status != 200:
        return _result("error", "Open Library HTTP %s" % status)
    try:
        data = json.loads(body.decode("utf-8", "replace"))
    except ValueError:
        return _result("error", "Open Library returned non-JSON")
    title = data.get("title") if isinstance(data, dict) else None
    return _result("resolves", 'Open Library title: "%s"' % (title or "(untitled record)"), url)


def apply_resolution(item, res):
    item["resolution"] = res
    if res["status"] == "resolves":
        item["notes"].append("lookup: " + res["detail"])
    elif res["status"] == "not-found":
        item["errors"].append("lookup: " + res["detail"])
    elif res["status"] == "error":
        item["warnings"].append("lookup: " + res["detail"])
    else:
        item["notes"].append("lookup: " + res["detail"])
    finalise(item)


def cmd_resolve(report, args):
    report["command"] = "resolve"
    report["online"] = bool(args.online)
    first = True
    for item in report["items"]:
        url = plan_lookup(item)
        if url is None:
            reason = "fails syntax/checksum" if item["verdict"] == "FAIL" else "no resolver for type %s" % item["type"]
            apply_resolution(item, _result("skipped", "not looked up (%s)" % reason))
            continue
        if not args.online:
            apply_resolution(item, _result("skipped", "dry run; --online would GET " + url))
            continue
        if not first and args.delay > 0:
            time.sleep(args.delay)
        first = False
        if item["type"] == "doi":
            res = resolve_doi(item["normalised"], args)
        elif item["type"] == "arxiv":
            res = resolve_arxiv(item["normalised"], args)
        else:
            res = resolve_isbn(item["normalised"], args)
        apply_resolution(item, res)
    summarise(report)
    return report


# --- demo --------------------------------------------------------------------

# The worked example in SKILL.md: the three references from the procedure's
# report format plus one book, so every verdict appears once.
DEMO_TEXT = """\
[1] S. Dhuliawala et al., "Chain-of-Verification Reduces Hallucination in Large Language Models," arXiv:2309.11495, 2023.
[2] S. Reporter, "Article," Publication, 2024. [Online]. Available: https://example.com/article
[3] J. Smith, "Paper," Journal, vol. 5, no. 2, 2024. doi: 10.invalid-fake
[4] C. M. Bishop, Pattern Recognition and Machine Learning. New York, NY, USA: Springer, 2006. ISBN 978-0-387-31073-2.
"""


# --- selftest ----------------------------------------------------------------


def run_selftest():
    """Known-good and known-bad cases. Every expected value was checked by hand
    against the scheme documentation (see module docstring) before being
    encoded here. No network access."""
    results = []

    def check(name, cond, detail=""):
        ok = bool(cond)
        results.append(ok)
        print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok or not detail else "  [%s]" % detail))

    def first(text, kind=None):
        items = validate_text(text)["items"]
        if kind:
            items = [i for i in items if i["type"] == kind]
        return items[0] if items else None

    def count(text):
        return len(validate_text(text)["items"])

    # -- DOI (ISO 26324) --
    it = first("doi: 10.1038/nature14539")
    check("DOI 10.1038/nature14539: syntax valid, PASS", it and it["type"] == "doi" and it["syntax_ok"] and it["verdict"] == "PASS")

    # Regression: legacy AMS/AGU/GSA SICI-style DOIs contain angle brackets and
    # semicolons. The DOI Handbook permits any Unicode Graphic in the suffix, so
    # these are valid and resolvable -- these two are Brier (1950) and Murphy
    # (1973), the founding citations of the brier-score-calibration skill.
    it = first("doi: 10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2")
    check("legacy SICI DOI (Brier 1950) passes",
          it and it["type"] == "doi" and it["syntax_ok"] and it["verdict"] == "PASS")
    it = first("doi: 10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2")
    check("legacy SICI DOI (Murphy 1973) passes",
          it and it["type"] == "doi" and it["syntax_ok"] and it["verdict"] == "PASS")
    it = first("doi:10.1038/NATURE14539.")
    check("DOI trailing period stripped, normalised lower-case", it and it["normalised"] == "10.1038/nature14539" and it["raw"] == "10.1038/NATURE14539", str(it))
    it = first("(doi:10.1000/182)")
    check("DOI unbalanced closing paren stripped", it and it["normalised"] == "10.1000/182", str(it))
    it = first("10.1016/S0140-6736(20)30183-5.")
    check("DOI balanced parentheses kept", it and it["normalised"] == "10.1016/s0140-6736(20)30183-5", str(it))
    rep = validate_text("https://doi.org/10.1038/nature14539")
    check("doi.org URL -> one DOI item, URL not double-counted",
          len(rep["items"]) == 1 and rep["items"][0]["type"] == "doi" and any("embedded" in n for n in rep["items"][0]["notes"]))
    it = first("http://dx.doi.org/10.1038/nature14539,")
    check("dx.doi.org legacy host noted, comma stripped", it and it["normalised"] == "10.1038/nature14539" and any("dx.doi.org" in n for n in it["notes"]))
    it = first("doi: 10.invalid-fake")
    check("fabricated DOI 10.invalid-fake -> FAIL", it and it["type"] == "doi" and not it["syntax_ok"] and it["verdict"] == "FAIL")
    it = first("doi:10.123456/abc")
    check("registrant code outside 10.1000-10.99999 -> REVIEW", it and it["syntax_ok"] and it["verdict"] == "REVIEW")
    it = first("doi:10.1038/s41586-023-")
    check("truncated-looking suffix -> REVIEW", it and it["verdict"] == "REVIEW" and any("truncated" in w for w in it["warnings"]))
    it = first("doi:10.1000/xxxxx")
    check("placeholder suffix -> REVIEW", it and it["verdict"] == "REVIEW")
    check("bare DOI in prose is found", count("see 10.1038/nature14539 for details") == 1)

    # -- arXiv --
    it = first("arXiv:2309.11495")
    check("arXiv 2309.11495: new scheme, 5-digit era, PASS", it and it["verdict"] == "PASS" and it["normalised"] == "2309.11495" and any("5-digit" in n for n in it["notes"]))
    it = first("arXiv:0704.0001")
    check("arXiv 0704.0001: 4-digit era, PASS", it and it["verdict"] == "PASS" and any("4-digit" in n for n in it["notes"]))
    it = first("arXiv:hep-th/9901001")
    check("arXiv hep-th/9901001: old scheme, PASS", it and it["verdict"] == "PASS" and it["normalised"] == "hep-th/9901001" and any("old scheme" in n for n in it["notes"]))
    it = first("arXiv:math.GT/0309136")
    check("arXiv math.GT/0309136: old scheme with subject class, PASS", it and it["verdict"] == "PASS" and it["normalised"] == "math.GT/0309136")
    it = first("arXiv:2309.11495v2")
    check("arXiv version suffix kept and noted", it and it["normalised"] == "2309.11495v2" and any("v2" in n for n in it["notes"]))
    it = first("arXiv:2309.1149")
    check("arXiv 4-digit number in the 5-digit era -> FAIL", it and it["verdict"] == "FAIL")
    it = first("arXiv:0704.00001")
    check("arXiv 5-digit number in the 4-digit era -> FAIL", it and it["verdict"] == "FAIL")
    it = first("arXiv:2313.11495")
    check("arXiv month 13 -> FAIL", it and it["verdict"] == "FAIL")
    it = first("arXiv:0612.1234")
    check("arXiv new-scheme id before 0704 -> FAIL", it and it["verdict"] == "FAIL")
    it = first("arXiv:hep-th/0801001")
    check("arXiv old-scheme id after 0703 -> FAIL", it and it["verdict"] == "FAIL")
    it = first("arXiv:foo-bar/9901001")
    check("arXiv unknown old archive -> REVIEW", it and it["verdict"] == "REVIEW")
    check("bare arXiv ids (new + old) found in prose", count("see 2309.11495 and hep-th/9901001") == 2)
    it = first("arXiv:2309.11495 [cs.CL]")
    check("arXiv category tag not swallowed", it and it["normalised"] == "2309.11495")
    it = first("https://arxiv.org/pdf/2309.11495v1.pdf")
    check("arxiv.org PDF URL -> arXiv item", it and it["type"] == "arxiv" and it["normalised"] == "2309.11495v1")
    check("bare number with impossible month is not an arXiv id", count("total 1998.4567 units") == 0)

    # -- ISBN (ISO 2108) --
    check("ISBN-13 check digit for 978030640615 is 7", isbn13_check_digit("978030640615") == "7")
    check("ISBN-10 check digit for 030640615 is 2", isbn10_check_digit("030640615") == "2")
    check("ISBN-10 check digit for 080442957 is X", isbn10_check_digit("080442957") == "X")
    it = first("ISBN 978-0-306-40615-7")
    check("ISBN-13 978-0-306-40615-7 valid", it and it["type"] == "isbn13" and it["checksum_ok"] is True and it["verdict"] == "PASS" and it["normalised"] == "9780306406157")
    it = first("ISBN 978-0-306-40615-8")
    check("ISBN-13 978-0-306-40615-8 bad check digit -> FAIL", it and it["checksum_ok"] is False and it["verdict"] == "FAIL")
    it = first("ISBN 0-306-40615-2")
    check("ISBN-10 0-306-40615-2 valid, ISBN-13 equivalent noted", it and it["type"] == "isbn10" and it["checksum_ok"] is True and any("9780306406157" in n for n in it["notes"]))
    it = first("ISBN 0-8044-2957-X")
    check("ISBN-10 0-8044-2957-X valid (X check character)", it and it["checksum_ok"] is True and it["verdict"] == "PASS")
    it = first("ISBN 0-8044-2957-0")
    check("ISBN-10 0-8044-2957-0 bad check digit -> FAIL", it and it["checksum_ok"] is False)
    it = first("ISBN 978 0 306 40615 7")
    check("ISBN with space separators accepted", it and it["checksum_ok"] is True)
    it = first("ISBN 0-306-40615-2 2004")
    check("ISBN token trimmed at group boundary (year not swallowed)", it and it["normalised"] == "0306406152" and it["checksum_ok"] is True)
    it = first("ISBN: 123-4-56-789012-3")
    check("ISBN-13 not starting 978/979 -> FAIL", it and it["verdict"] == "FAIL")
    it = first("ISBN 0-306-40615")
    check("ISBN with 9 characters -> FAIL", it and it["verdict"] == "FAIL")
    check("bare hyphenated ISBN-13 found", first("978-0-306-40615-7", "isbn13") is not None)
    check("bare hyphenated ISBN-10 found", first("0-306-40615-2", "isbn10") is not None)

    # -- ORCID (ISO/IEC 7064 MOD 11-2) --
    check("ORCID check char for 000000021825009 is 7", orcid_check_char("000000021825009") == "7")
    check("ORCID check char for 000000029079593 is X", orcid_check_char("000000029079593") == "X")
    it = first("ORCID: 0000-0002-1825-0097")
    check("ORCID 0000-0002-1825-0097 valid", it and it["type"] == "orcid" and it["checksum_ok"] is True and it["verdict"] == "PASS")
    it = first("0000-0002-1825-0098")
    check("ORCID 0000-0002-1825-0098 invalid -> FAIL", it and it["type"] == "orcid" and it["checksum_ok"] is False and it["verdict"] == "FAIL")
    it = first("https://orcid.org/0000-0002-1825-0097")
    check("orcid.org URL -> ORCID item", it and it["type"] == "orcid" and it["normalised"] == "0000-0002-1825-0097")

    # -- PMID / PMCID --
    it = first("PMID: 12345678")
    check("PMID 12345678 valid", it and it["type"] == "pmid" and it["verdict"] == "PASS" and it["normalised"] == "12345678")
    it = first("PMID: 123456789")
    check("PMID with 9 digits -> FAIL", it and it["verdict"] == "FAIL")
    it = first("PMID: 42")
    check("PMID below 100 -> REVIEW", it and it["verdict"] == "REVIEW")
    it = first("https://pubmed.ncbi.nlm.nih.gov/12345678/")
    check("PubMed URL -> PMID item", it and it["type"] == "pmid" and it["normalised"] == "12345678")
    it = first("PMC1234567")
    check("PMCID PMC1234567 valid", it and it["type"] == "pmcid" and it["verdict"] == "PASS")
    check("PMCID label + PMC token counted once", count("PMCID: PMC1234567") == 1)

    # -- URL (RFC 3986 / RFC 2606) --
    it = first("https://example.com/article")
    check("example.com URL -> REVIEW (placeholder domain)", it and it["type"] == "url" and it["syntax_ok"] and it["verdict"] == "REVIEW")
    it = first("http://www.nature.com/articles/nature14539")
    check("plain-http URL passes with a note", it and it["verdict"] == "PASS" and any("http" in n for n in it["notes"]))
    it = first("(see https://www.nature.com/articles/nature14539).")
    check("URL trailing ').' stripped", it and it["normalised"] == "https://www.nature.com/articles/nature14539")
    it = first("https://en.wikipedia.org/wiki/Foo_(bar)")
    check("URL balanced parentheses kept", it and it["normalised"].endswith("Foo_(bar)"))
    it = first("[Online]. Available: www.nature.com/articles/nature14539")
    check("scheme-less URL after Available: -> FAIL", it and it["type"] == "url" and not it["syntax_ok"])
    it = first("https://nature..com/x")
    check("malformed host -> FAIL", it and it["verdict"] == "FAIL")
    it = first("https://www.nature.com//articles/x")
    check("double slash in path -> REVIEW", it and it["verdict"] == "REVIEW")
    it = first("https://doi.org/")
    check("empty doi.org URL -> DOI FAIL", it and it["type"] == "doi" and it["verdict"] == "FAIL")
    check("'Available: on request' is not a URL", count("Available: on request") == 0)

    check("markdown link text + target -> one DOI item, PASS",
          [(i["type"], i["verdict"]) for i in validate_text("[10.1038/nature14539](https://doi.org/10.1038/nature14539)")["items"]] == [("doi", "PASS")])
    check("label + URL of the same arXiv id merged into one item",
          count("arXiv:1706.03762 [Online]. Available: https://arxiv.org/abs/1706.03762") == 1)
    it = first("ISBN 1301234567")
    check("ISBN designator never eats leading digits (1301234567 is an ISBN-10)", it and it["type"] == "isbn10" and it["normalised"] == "1301234567")

    # -- entries, exit codes, JSON input, determinism --
    rep = validate_text("[1] doi: 10.1038/nature14539\n[2] arXiv:2309.11495")
    check("numbered entries split and labelled", [e["label"] for e in rep["entries"]] == ["[1]", "[2]"] and rep["exit_code"] == 0)
    rep = validate_text("[1] doi: 10.1038/nature14539\n[2] doi: 10.fake/xyz")
    check("any FAIL -> exit code 1", rep["exit_code"] == 1 and rep["summary"]["fail"] == 1)
    rep = build_report(entries_from_json(["doi: 10.1038/nature14539", "arXiv:2309.11495"]))
    check("JSON list input -> one entry per string", rep["summary"]["entries"] == 2 and rep["summary"]["identifiers"] == 2)
    check("wrapped reference lines re-joined under one [N] entry",
          validate_text("[1] A. Author, Title,\n    doi: 10.1038/nature14539.")["summary"]["entries"] == 1)
    a = render_json(validate_text(DEMO_TEXT))
    b = render_json(validate_text(DEMO_TEXT))
    check("two runs are byte-identical", a == b)
    demo = validate_text(DEMO_TEXT)
    check("demo: verdicts PASS/REVIEW/FAIL/PASS, exit 2",
          [i["verdict"] for i in demo["items"]] == ["PASS", "REVIEW", "FAIL", "PASS"] and demo["exit_code"] == 1)
    check("resolve dry-run plans the handle API URL",
          plan_lookup({"verdict": "PASS", "type": "doi", "normalised": "10.1038/nature14539"}) == "https://doi.org/api/handles/10.1038/nature14539")
    check("resolve never plans a lookup for a FAILing item",
          plan_lookup({"verdict": "FAIL", "type": "doi", "normalised": "10.invalid-fake"}) is None)

    failed = results.count(False)
    if failed:
        print("SELFTEST FAILED: %d of %d checks" % (failed, len(results)), file=sys.stderr)
        return 1
    print("ALL %d CHECKS PASSED" % len(results))
    print("selftest OK")
    return 0


# --- CLI ---------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(
        description="Offline syntax + checksum validation of DOIs, arXiv ids, ISBNs, "
        "PMIDs/PMCIDs, ORCID iDs and URLs in a reference list (verify-citations companion)."
    )
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true", help="validate the SKILL.md worked example and exit")
    sub = parser.add_subparsers(dest="command")
    for name, helptext in [
        ("validate", "extract identifiers and check syntax + check digits (offline)"),
        ("resolve", "validate, then look DOIs / arXiv ids / ISBNs up online (needs --online)"),
    ]:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--file", help="reference list: free text, or .json list of strings")
        p.add_argument("--text", help="reference text passed inline")
        p.add_argument("--json", action="store_true", help="emit the report as JSON")
        if name == "resolve":
            p.add_argument("--online", action="store_true", help="actually query doi.org, export.arxiv.org and openlibrary.org")
            p.add_argument("--timeout", type=float, default=10.0, help="per-request timeout in seconds (default 10)")
            p.add_argument("--delay", type=float, default=3.0,
                           help="pause between requests in seconds (default 3.0; arXiv's terms "
                                "require no more than one request every three seconds)")
            p.add_argument("--user-agent", default=DEFAULT_UA, help="User-Agent header for lookups")
    return parser


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo:
        report = validate_text(DEMO_TEXT)
        print(render_text(report))
        return report["exit_code"]
    if not args.command:
        parser.error("choose a command: validate | resolve  (or --selftest / --demo)")
    entries = load_entries(args, parser)
    report = build_report(entries)
    if args.command == "resolve":
        cmd_resolve(report, args)
    print(render_json(report) if args.json else render_text(report))
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
