#!/usr/bin/env python3
"""ieee.py — check, renumber and format IEEE numbered-bracket citations.

Implements the reference rules of the IEEE Reference Guide (IEEE Publication
Operations, Piscataway, NJ, USA, V 3.28.2025, formerly at
ieeeauthorcenter.ieee.org/wp-content/uploads/IEEE-Reference-Guide.pdf; earlier
edition V 11.12.2018), §I "Citing References", §II "Style", §III "Notes About
Online References", together with the "References" section of the IEEE
Editorial Style Manual for Authors (IEEE Publishing Operations, updated
29 July 2024), as simplified in ../SKILL.md:

  * In-text citations are numbers in square brackets, on the line, inside the
    punctuation. The guide cites several sources as separate brackets --
    "as shown by Brown [4], [5]; as mentioned earlier [2], [4]-[7], [9]"
    (Guide, I.A) -- and reserves the comma inside a bracket for a locator:
    [3, pp. 5-10], [3, Fig. 1] (Guide, I.B). `check` also accepts the house
    forms [1, 4], [2]-[5], [2]–[5], [2–5], [7, pp. 12–14]; ranges are expanded
    ([2]–[5] = 2, 3, 4, 5).
  * "Do not combine references. There must be only one reference with each
    number" (Guide §II); numbers run 1, 2, 3, ... in order of first citation
    (Style Manual, "References"), so: every listed number is cited, every cited
    number is listed, no gaps, no duplicates, no source cited before a lower
    number first appears.
  * Entry lint (warnings): "All references, except those ending with URLs, will
    end with a period, including those with a DOI" (Guide §II); every reference
    carries at least a year (§II); article titles are quoted and followed by
    the periodical / book / venue name; online sources carry
    "Accessed: Mon. D, YYYY." and "[Online]. Available: URL" (§III).
  * `format` reproduces the guide's "Basic Format" lines: up to six authors are
    listed, seven or more become "First Author et al." (§II); given names are
    initials before the surname, no commas around Jr./Sr./III (§II); months are
    Jan. Feb. Mar. Apr. May Jun. Jul. Aug. Sep. Oct. Nov. Dec.; page ranges use
    an en dash; e.g. journal article (Guide §II-M "Periodicals"):
        J. K. Author, "Name of paper," Abbrev. Title of Periodical, vol. x,
        no. x, pp. xxx-xxx, Abbrev. Month, year, doi: xxx.

Note: the 2018 guide shows in-text ranges as "[2], [4]–[7]"; the 2025 guide
writes them out ("[1], [2], [3], [4]"); a compressed "[2–5]" is a house
variant. `check` accepts all three; `renumber` emits the guide's form -- one
number per bracket, ranges written out. The guide's arXiv format is "year, arXiv:ID." (§II-S), which `format`
follows.

Stdlib only. Python 3.9+. Deterministic (no clock, no randomness).

Usage:
    python3 ieee.py check    --file report.md [--json]
    python3 ieee.py renumber --file report.md [--write out.md]
    python3 ieee.py format   --file refs.json [--md] [--json]
    python3 ieee.py --demo
    python3 ieee.py --selftest

Exit codes: 0 clean (warnings allowed) · 1 usage / unreadable input · 2 `check`
found at least one error-level problem.
"""

import argparse
import json
import re
import sys

EN_DASH = "–"
MONTHS = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "Jun.", "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."]
MONTH_FULL = ["january", "february", "march", "april", "may", "june", "july", "august",
              "september", "october", "november", "december"]
MONTH_LOOKUP = {}
for _i, _full in enumerate(MONTH_FULL):
    MONTH_LOOKUP[_full] = _i
    MONTH_LOOKUP[_full[:3]] = _i
    MONTH_LOOKUP[str(_i + 1)] = _i
    MONTH_LOOKUP["%02d" % (_i + 1)] = _i
MONTH_LOOKUP["sept"] = 8
MONTH_WORD_RE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December"
    r"|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\.?(?=[\s,]|$)")
YEAR_RE = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")
FULL_DATE_RE = re.compile(
    r"\b(Jan\.|Feb\.|Mar\.|Apr\.|May|Jun\.|Jul\.|Aug\.|Sep\.|Sept\.|Oct\.|Nov\.|Dec\."
    r"|January|February|March|April|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},\s+\d{4}")
URL_RE = re.compile(r"(?:https?://|www\.)\S+")
DOI_URL_RE = re.compile(r"https?://(?:dx\.)?doi\.org/(10\.\S+)", re.I)

# --- document parsing --------------------------------------------------------

# A reference-list entry: optional indent / list marker, then "[n]" and text.
ENTRY_RE = re.compile(r"^(\s*(?:[-*+]\s+)?)\[(\d+)\]\s*(.*)$")
ATX_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
REF_HEADING_WORDS = ("references", "reference list", "bibliography", "works cited")
BRACKET_RE = re.compile(r"\[([^\[\]\n]*)\]")
NUM_RANGE_RE = re.compile(r"^(\d+)\s*[-–—]\s*(\d+)$")
BRACKET_RANGE_RE = re.compile(r"\s?[-–—]\s?\[(\d+)\]")
ADJACENT_RE = re.compile(r"\s?\[(\d+)\]")


def find_reference_heading(lines):
    """Index of the heading that opens the reference list, or None.

    Accepts an ATX markdown heading ("## References", "## 7. References") or a
    bare line consisting only of the word (optionally bold, numbered, colon,
    HTML tags). An exact "References"/"Bibliography" wins over a heading that
    merely contains the word.
    """
    fallback = None
    for i, raw in enumerate(lines):
        stripped = re.sub(r"<[^>]+>", "", raw).strip()
        m = ATX_HEADING_RE.match(stripped)
        text = m.group(2) if m else stripped
        text = text.strip().strip("*_").strip().rstrip(":").strip()
        text = re.sub(r"^(?:\d+|[ivxlc]+)[.)]?\s+", "", text, flags=re.I)
        low = text.lower()
        if low in REF_HEADING_WORDS:
            return i
        if m and fallback is None and "references" in low:
            fallback = i
    return fallback


def collect_entries(lines, start, end, stop_at_other):
    """Collect [n] entries in lines[start:end].

    Lines immediately following an entry (no blank line between) are wrapped
    continuation lines of that entry. In fallback mode (no heading found,
    stop_at_other=True) the first other non-blank line ends the list.
    Returns (entries, end_index).
    """
    entries, cur = [], None
    for j in range(start, end):
        raw = lines[j]
        m = ENTRY_RE.match(raw)
        if m:
            cur = {"n": int(m.group(2)), "line": j + 1, "first": j, "last": j,
                   "prefix": m.group(1), "text": m.group(3).strip(), "lines": [raw]}
            entries.append(cur)
        elif not raw.strip():
            cur = None
        elif cur is not None:
            cur["last"] = j
            cur["lines"].append(raw)
            cur["text"] = (cur["text"] + " " + raw.strip()).strip()
        elif stop_at_other:
            return entries, j
    return entries, end


def parse_document(text):
    """Split a markdown / plain-text document into body lines and reference list."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    head = find_reference_heading(lines)
    entries, zone_start, zone_end = [], None, None
    if head is not None:
        zone_start, zone_end = head + 1, len(lines)
        for j in range(head + 1, len(lines)):
            if ATX_HEADING_RE.match(lines[j]):
                zone_end = j
                break
        entries, _ = collect_entries(lines, zone_start, zone_end, stop_at_other=False)
    else:
        for j, raw in enumerate(lines):
            if ENTRY_RE.match(raw):
                zone_start = j
                break
        if zone_start is not None:
            entries, zone_end = collect_entries(lines, zone_start, len(lines), stop_at_other=True)
    body_idx = [i for i in range(len(lines))
                if zone_start is None or not (zone_start <= i < zone_end)]
    if head is not None:
        body_idx = [i for i in body_idx if i != head]
    return {"lines": lines, "heading": head, "zone": (zone_start, zone_end),
            "entries": entries, "body_idx": body_idx}


def parse_bracket(content):
    """Parse the inside of one bracket. Returns (numbers, locator, error) or None
    when the bracket is not a numeric citation ([Online], [sic], [^1], ...)."""
    tokens = [t.strip() for t in content.split(",")]
    if not tokens or not tokens[0]:
        return None
    numbers, locator, error = [], None, None
    for k, tok in enumerate(tokens):
        if re.fullmatch(r"\d+", tok):
            numbers.append(int(tok))
            continue
        m = NUM_RANGE_RE.match(tok)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if b < a:
                error = "descending range %s" % tok
            numbers.extend(range(a, b + 1) if b >= a else [a, b])
            continue
        if k == 0:
            return None
        locator = ", ".join(tokens[k:])
        break
    if 0 in numbers:
        return None
    return numbers, locator, error


def strip_code(line):
    """Blank out inline code spans so brackets inside them are not citations."""
    return re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)


def scan_citations(doc):
    """Find every in-text citation group in the body. Returns (citations, problems).

    A group is one bracket, or a bracket range "[a]–[b]". Fenced code blocks
    and inline code are skipped; "[n](" (markdown link) is skipped.
    """
    cits, problems = [], []
    in_fence = False
    for i in doc["body_idx"]:
        raw = doc["lines"][i]
        if raw.lstrip().startswith("```") or raw.lstrip().startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = strip_code(raw)
        pos = 0
        while True:
            m = BRACKET_RE.search(line, pos)
            if not m:
                break
            pos = m.end()
            if line[m.end():m.end() + 1] == "(":
                continue
            parsed = parse_bracket(m.group(1))
            if parsed is None:
                continue
            numbers, locator, error = parsed
            start, end, kind = m.start(), m.end(), "single" if len(numbers) == 1 else "list"
            if len(numbers) == 1 and locator is None:
                r = BRACKET_RANGE_RE.match(line, end)
                if r:
                    b = int(r.group(1))
                    if b < numbers[0]:
                        error = "descending range [%d]-[%d]" % (numbers[0], b)
                        numbers = [numbers[0], b]
                    else:
                        numbers = list(range(numbers[0], b + 1))
                    end, kind = r.end(), "bracket-range"
                    pos = end
            if locator is not None:
                kind = "locator"
            adj = ADJACENT_RE.match(line, end)              # "[1][2]" / "[1] [2]" — the guide wants "[1], [2]"
            if adj and kind != "bracket-range" and not BRACKET_RANGE_RE.match(line, end):
                separated = ", ".join("[%d]" % x for x in numbers + [int(adj.group(1))])
                problems.append(_p("warning", "adjacent", i + 1, numbers[0],
                                   "adjacent bracket groups %s%s; separate with commas as %s"
                                   % (line[start:end], adj.group(0).strip(), separated)))
            if error:
                problems.append(_p("error", "range", i + 1, numbers[0], error + " in " + line[start:end]))
            cits.append({"line": i + 1, "start": start, "end": end, "text": line[start:end],
                         "numbers": numbers, "locator": locator, "kind": kind})
    return cits, problems


def _p(severity, code, line, ref, message):
    return {"severity": severity, "code": code, "line": line, "ref": ref, "message": message}


def first_cited_order(cits):
    order = []
    for c in cits:
        for n in c["numbers"]:
            if n not in order:
                order.append(n)
    return order


def _compress(nums):
    """[3,4,5,9] -> '[3]–[5], [9]' for messages."""
    out, i = [], 0
    nums = sorted(set(nums))
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j - i >= 2:
            out.append("[%d]%s[%d]" % (nums[i], EN_DASH, nums[j]))
        else:
            out.extend("[%d]" % x for x in nums[i:j + 1])
        i = j + 1
    return ", ".join(out)


# --- the checks ---------------------------------------------------------------


def lint_entry(e):
    """Warning-level style checks on one reference entry (Guide §II, §III)."""
    t, n, line, out = re.sub(r"<!--.*?-->", " ", e["text"]).strip(), e["n"], e["line"], []
    if not t:
        out.append(_p("warning", "empty", line, n, "[%d] has no text (placeholder?)" % n))
        return out
    last = t.split()[-1]
    urls = [u for u in URL_RE.findall(t) if not DOI_URL_RE.match(u)]
    doi_urls = DOI_URL_RE.findall(t)
    ends_with_url = bool(re.match(r"(https?://|www\.)", last))
    if ends_with_url:
        if last.endswith("."):
            out.append(_p("warning", "url-period", line, n,
                          "entries that end with a URL take no final period (Guide §II)"))
    elif not t.endswith("."):
        out.append(_p("warning", "no-period", line, n, "entry should end with a period"))
    if not YEAR_RE.search(t) and "n.d." not in t:
        out.append(_p("warning", "no-year", line, n, "no year found (use the year or \"(n.d.)\")"))
    quoted = re.search(r'["“]([^"“”]{3,}?)[,.?!]?["”]', t)
    italic = re.search(r"(?<!\*)\*[^*\n]{3,}\*(?!\*)|(?<!\w)_[^_\n]{3,}_(?!\w)", t)
    book_like = re.search(r":\s*[^,:]+,\s*(?:1[5-9]\d\d|20\d\d)\b", t)
    standard_like = re.search(r"\b(?:Standard|Std\.|Rec\.\s+ITU|ISO/IEC|ISO|IEC|ANSI|NERC)\b", t)
    if not quoted and not italic and not book_like and not standard_like:
        out.append(_p("warning", "no-title", line, n,
                      "no quoted article title (or italic book/journal title) found"))
    if quoted:
        after = t[quoted.end():]
        after = re.sub(r"https?://\S+|www\.\S+", " ", after)
        after = re.sub(r"(?i)\bdoi:\s*\S+|\[Online\]|\bAvailable:|\bAccessed:[^.]*", " ", after)
        after = re.sub(r"\b(?:vol|no|pp?|Art|ed|ch|sect?)\.\s*", " ", after)
        after = MONTH_WORD_RE.sub(" ", after)
        if len(re.findall(r"[A-Za-z]", after)) < 2:
            out.append(_p("warning", "no-venue", line, n,
                          "no journal / book / venue name after the title"))
    if doi_urls:
        out.append(_p("warning", "doi-url", line, n,
                      "write the DOI as \"doi: %s\" rather than a URL" % doi_urls[0].rstrip(".")))
    if urls:
        if "available:" not in t.lower():
            out.append(_p("warning", "no-available", line, n,
                          "URL should be introduced by \"[Online]. Available:\""))
        if "accessed" not in t.lower() and not FULL_DATE_RE.search(t):
            out.append(_p("warning", "no-accessed", line, n,
                          "URL without an access date; add \"Accessed: Mon. D, YYYY.\" before \"[Online]. Available:\""))
    return out


def analyse(text):
    """Run every check. Returns a report dict (see cmd_check for the shape)."""
    doc = parse_document(text)
    cits, problems = scan_citations(doc)
    entries = doc["entries"]
    order = first_cited_order(cits)
    listed = [e["n"] for e in entries]
    listed_set = set(listed)
    cited_set = set(order)
    first_line = {}
    for c in cits:
        for n in c["numbers"]:
            first_line.setdefault(n, c["line"])

    if not cits and not entries:
        problems.append(_p("warning", "nothing", 0, None, "no in-text citations and no reference list found"))
    if cits and not entries:
        problems.append(_p("error", "no-list", doc["heading"] + 1 if doc["heading"] is not None else 0, None,
                           "no bracket-numbered reference list found; entries must start with [n] (%d source%s cited: %s)"
                           % (len(order), "" if len(order) == 1 else "s", _compress(order))))

    # (5) a source cited before a lower number first appears
    for idx, n in enumerate(order):
        later_lower = [m for m in order[idx + 1:] if m < n]
        if later_lower:
            shown = ", ".join("[%d]" % m for m in later_lower[:4])
            if len(later_lower) > 4:
                shown += " and %d more" % (len(later_lower) - 4)
            problems.append(_p("error", "order", first_line[n], n,
                               "[%d] is first cited before %s first appear%s"
                               % (n, shown, "s" if len(later_lower) == 1 else "")))
    # (1) numbering must run 1, 2, 3, ... in order of first citation
    expected = list(range(1, len(order) + 1))
    if order and order != expected:
        k = next(i for i, (a, b) in enumerate(zip(order, expected)) if a != b)
        changes = ["[%d]->[%d]" % (a, b) for a, b in zip(order, expected) if a != b]
        shown = ", ".join(changes[:6]) + (", ..." if len(changes) > 6 else "")
        problems.append(_p("error", "sequence", first_line[order[k]], order[k],
                           "cited in the order %s; IEEE numbers sources 1, 2, 3, ... by first citation (renumber: %s)"
                           % (", ".join("[%d]" % n for n in order), shown)))
    # (2) no gaps or duplicates in the list; list ascending
    seen = {}
    for e in entries:
        if e["n"] in seen:
            problems.append(_p("error", "list-duplicate", e["line"], e["n"],
                               "duplicate entry [%d] (first listed at line %d)" % (e["n"], seen[e["n"]])))
        else:
            seen[e["n"]] = e["line"]
    prev = None
    for e in entries:
        if prev is not None and e["n"] < prev["n"]:
            problems.append(_p("error", "list-order", e["line"], e["n"],
                               "[%d] is listed after [%d]; the list must ascend 1, 2, 3, ..." % (e["n"], prev["n"])))
        prev = e
    if listed:
        missing = sorted(set(range(1, max(listed) + 1)) - listed_set)
        if missing:
            nxt = next(e for e in entries if e["n"] > missing[0])
            problems.append(_p("error", "list-gap", nxt["line"], missing[0],
                               "gap in the reference list: no entry for %s" % _compress(missing)))
    # (3) every listed reference is cited
    for e in entries:
        if e["n"] not in cited_set:
            problems.append(_p("error", "uncited", e["line"], e["n"],
                               "[%d] is listed but never cited in the text" % e["n"]))
    # (4) every cited number has an entry
    if entries:
        for n in order:
            if n not in listed_set:
                problems.append(_p("error", "no-entry", first_line[n], n,
                                   "[%d] is cited but has no entry in the reference list" % n))
    # entry lint (warnings)
    for e in entries:
        problems.extend(lint_entry(e))

    sev_rank = {"error": 0, "warning": 1}
    problems.sort(key=lambda p: (p["line"], sev_rank[p["severity"]], p["code"], p["ref"] or 0))
    errors = sum(1 for p in problems if p["severity"] == "error")
    warnings = sum(1 for p in problems if p["severity"] == "warning")
    return {
        "citations": cits, "first_cited_order": order, "entries": entries, "doc": doc,
        "problems": problems,
        "summary": {"citations": len(cits), "distinct_cited": len(order), "entries": len(entries),
                    "errors": errors, "warnings": warnings},
        "ok": errors == 0,
    }


# --- renumber -----------------------------------------------------------------


def canonical_group(new_numbers, locator):
    """Emit one citation group in the guide's form: ascending, one number per
    bracket, ranges written out, locator inside its own bracket --
    [1], [3], [5], [6] and [3, pp. 5-10] (Guide, I.A and I.B)."""
    nums = sorted(set(new_numbers))
    if locator:
        return ", ".join("[%d, %s]" % (n, locator) for n in nums)
    return ", ".join("[%d]" % n for n in nums)


def renumber(text):
    """Renumber citations by first appearance and reorder the reference list.

    Returns (new_text, mapping, notes). Entry text is preserved verbatim; the
    slots of the original list are refilled in the new order, uncited entries
    go last (flagged), and cited numbers without an entry get a flagged
    placeholder so the output list is 1..N.
    """
    rep = analyse(text)
    doc, cits, entries = rep["doc"], rep["citations"], rep["entries"]
    lines = list(doc["lines"])
    eol = "\r\n" if "\r\n" in text else "\n"
    order = rep["first_cited_order"]
    mapping = {n: i + 1 for i, n in enumerate(order)}
    listed = {}
    for e in entries:
        listed.setdefault(e["n"], e)
    uncited = [e for e in entries if e["n"] not in mapping and listed[e["n"]] is e]
    duplicates = [e for e in entries if listed[e["n"]] is not e]
    nxt = len(order)
    for e in uncited:
        nxt += 1
        mapping[e["n"]] = nxt
    dup_numbers = {}
    for e in duplicates:
        nxt += 1
        dup_numbers[id(e)] = nxt
    notes = []

    # 1. body: rewrite each group right-to-left so offsets stay valid
    by_line = {}
    for c in cits:
        by_line.setdefault(c["line"] - 1, []).append(c)
    for i, groups in by_line.items():
        line = lines[i]
        for c in sorted(groups, key=lambda g: g["start"], reverse=True):
            new = canonical_group([mapping[n] for n in c["numbers"]], c["locator"])
            line = line[:c["start"]] + new + line[c["end"]:]
        lines[i] = line

    # 2. reference list: refill the original slots in the new order
    if entries:
        slots = sorted(entries, key=lambda e: e["first"])
        prefix = slots[0]["prefix"]
        blocks = []
        for n in order:                                   # cited sources, first-appearance order
            if n in listed:
                e = listed[n]
                block = list(e["lines"])
                block[0] = ENTRY_RE.sub(lambda m, k=mapping[n]: "%s[%d] %s" % (m.group(1), k, m.group(3)), block[0], count=1)
                blocks.append(block)
            else:
                blocks.append(["%s[%d] <!-- MISSING ENTRY: [%d] is cited in the text but has no reference entry -->"
                               % (prefix, mapping[n], n)])
                notes.append("[%d] -> [%d]  MISSING entry: placeholder inserted" % (n, mapping[n]))
        for e in uncited:                                 # then the uncited ones, flagged
            block = list(e["lines"])
            block[0] = ENTRY_RE.sub(lambda m, k=mapping[e["n"]]: "%s[%d] %s" % (m.group(1), k, m.group(3)), block[0], count=1)
            block[-1] = block[-1].rstrip() + " <!-- UNCITED: not cited in the text -->"
            blocks.append(block)
            notes.append("[%d] -> [%d]  UNCITED entry moved to the end" % (e["n"], mapping[e["n"]]))
        for e in duplicates:                              # duplicate numbers: kept, renumbered, flagged
            k = dup_numbers[id(e)]
            block = list(e["lines"])
            block[0] = ENTRY_RE.sub(lambda m, k=k: "%s[%d] %s" % (m.group(1), k, m.group(3)), block[0], count=1)
            block[-1] = block[-1].rstrip() + " <!-- DUPLICATE: was also numbered [%d]; merge or delete -->" % e["n"]
            blocks.append(block)
            notes.append("[%d] -> [%d]  DUPLICATE number kept as a separate flagged entry" % (e["n"], k))
        out, cursor = [], slots[0]["first"]
        for i, block in enumerate(blocks):
            if i < len(slots):                            # keep whatever sat between the original slots
                out.extend(lines[cursor:slots[i]["first"]])
                cursor = slots[i]["last"] + 1
            out.extend(block)
        cursor = max(cursor, slots[-1]["last"] + 1)
        lines = lines[:slots[0]["first"]] + out + lines[cursor:]
    else:
        notes.append("no reference list found; only in-text citations were renumbered")
    notes = ["[%d] -> [%d]" % (n, mapping[n]) for n in order if n in listed and mapping[n] != n] + notes
    return eol.join(lines), mapping, notes


# --- format -------------------------------------------------------------------

TYPE_ALIASES = {
    "journal": "journal", "article": "journal", "periodical": "journal", "journal_article": "journal",
    "conference": "conference", "inproceedings": "conference", "proceedings": "conference",
    "conference_paper": "conference",
    "book": "book", "monograph": "book",
    "chapter": "chapter", "incollection": "chapter", "inbook": "chapter", "book_chapter": "chapter",
    "website": "website", "web": "website", "webpage": "website", "online": "website",
    "news": "news", "blog": "news", "newspaper": "news", "magazine": "news", "news_article": "news",
    "arxiv": "arxiv", "preprint": "arxiv", "eprint": "arxiv",
    "patent": "patent",
    "standard": "standard",
    "thesis": "thesis", "mastersthesis": "thesis", "msthesis": "thesis",
    "dissertation": "dissertation", "phdthesis": "dissertation",
    "report": "report", "techreport": "report", "tech_report": "report", "whitepaper": "report",
    "filing": "report", "white_paper": "report",
}
PARTICLES = {"van", "von", "de", "der", "den", "del", "della", "di", "da", "do", "dos", "das",
             "la", "le", "du", "ter", "ten", "af", "av", "bin", "ibn", "el", "al", "y"}
SUFFIXES = {"jr": "Jr.", "sr": "Sr.", "ii": "II", "iii": "III", "iv": "IV"}
ORG_WORDS = {"inc", "corp", "corporation", "ltd", "llc", "gmbh", "co", "company", "univ", "university",
             "institute", "inst", "association", "assoc", "committee", "consortium", "group", "laboratory",
             "lab", "labs", "agency", "organization", "organisation", "foundation", "council", "society",
             "soc", "department", "dept", "bureau", "ministry", "office", "commission", "administration",
             "board", "center", "centre", "authority", "operations", "publications", "and", "&", "of",
             "the", "for", "team", "project", "working", "staff", "division", "div"}


def initials(given):
    parts = []
    for tok in given.replace(".", ". ").split():
        tok = tok.strip(".")
        if not tok:
            continue
        if "-" in tok:
            parts.append("-".join(p[0] + "." for p in tok.split("-") if p))
        else:
            parts.append(tok[0] + ".")
    return " ".join(parts)


def format_person(name):
    """'Jane K. Author' / 'Author, Jane K.' / {'given','family'} -> 'J. K. Author'.
    Corporate names ({'literal': ...} or containing Inc./Univ./of/...) are kept."""
    if isinstance(name, dict):
        if name.get("literal"):
            return " ".join(str(name["literal"]).split())
        given = " ".join(str(name.get("given", "")).split())
        family = " ".join(str(name.get("family", "")).split())
        suffix = SUFFIXES.get(str(name.get("suffix", "")).strip(". ").lower(), str(name.get("suffix", "")).strip())
        if not given:
            return (family + (" " + suffix if suffix else "")).strip()
        return (initials(given) + " " + family + (" " + suffix if suffix else "")).strip()
    s = " ".join(str(name).split())
    if not s:
        return ""
    if any(w.strip(".,").lower() in ORG_WORDS for w in s.split()):
        return s
    suffix = ""
    toks = [t for t in re.split(r"\s+", s.replace(",", " , ")) if t]
    kept = []
    for t in toks:
        key = t.strip(".").lower()
        if key in SUFFIXES and len(toks) > 2:
            suffix = SUFFIXES[key]
        else:
            kept.append(t)
    s = " ".join(kept).replace(" , ", ", ").strip(" ,")
    if "," in s:
        family, given = [p.strip() for p in s.split(",", 1)]
    else:
        toks = s.split()
        if len(toks) == 1:
            return (s + (" " + suffix if suffix else "")).strip()
        given_toks, fam_toks = toks[:-1], [toks[-1]]
        while len(given_toks) > 1 and given_toks[-1].lower() in PARTICLES:
            fam_toks.insert(0, given_toks.pop())
        given, family = " ".join(given_toks), " ".join(fam_toks)
    out = (initials(given) + " " + family).strip()
    return out + (" " + suffix if suffix else "")


def join_names(names):
    names = [n for n in names if n]
    if len(names) <= 1:
        return "".join(names)
    if len(names) == 2:
        return "%s and %s" % (names[0], names[1])
    return ", ".join(names[:-1]) + ", and " + names[-1]


def authors_string(value, max_authors=6, force_et_al=False):
    """Guide §II: list up to six names; more than six -> 'First Author et al.'"""
    if value is None:
        return ""
    if isinstance(value, str):
        value = [v.strip() for v in re.split(r";|\band\b", value) if v.strip()] if (";" in value or " and " in value) else [value]
    names = [format_person(v) for v in value if v]
    if not names:
        return ""
    if force_et_al or len(names) > max_authors:
        return names[0] + " et al."
    return join_names(names)


def norm_month(value):
    if value is None or str(value).strip() == "":
        return ""
    s = str(value).strip()
    if "/" in s:  # "Jul./Aug." two-month issue
        return "/".join(norm_month(p) for p in s.split("/"))
    key = s.rstrip(".").lower()
    if key in MONTH_LOOKUP:
        return MONTHS[MONTH_LOOKUP[key]]
    return s


def fmt_date(value):
    """ISO 2009-02-01 -> 'Feb. 1, 2009'; 2009-02 -> 'Feb. 2009'; otherwise
    normalise month words ('September 23, 2024' -> 'Sep. 23, 2024')."""
    if value is None:
        return ""
    s = str(value).strip()
    m = re.fullmatch(r"(\d{4})-(\d{1,2})(?:-(\d{1,2}))?", s)
    if m:
        y, mo, d = m.group(1), norm_month(m.group(2)), m.group(3)
        return "%s %d, %s" % (mo, int(d), y) if d else "%s %s" % (mo, y)
    return MONTH_WORD_RE.sub(lambda mm: norm_month(mm.group(1)), s)


def get(ref, *keys):
    for k in keys:
        v = ref.get(k)
        if v is None:
            continue
        if isinstance(v, (list, dict)):
            return v
        v = str(v).strip()
        if v:
            return v
    return ""


def date_string(ref):
    d = get(ref, "date")
    if d:
        return fmt_date(d)
    y, mo, day = get(ref, "year"), norm_month(get(ref, "month")), get(ref, "day")
    if mo and day and y:
        return "%s %s, %s" % (mo, day, y)
    if mo and y:
        return "%s %s" % (mo, y)
    return y


def pages(pp):
    if not pp:
        return ""
    s = str(pp).strip()
    s = re.sub(r"^(?:pp?\.)\s*", "", s, flags=re.I)
    s = re.sub(r"\s*(?:-{1,2}|–|—)\s*", EN_DASH, s)
    return ("pp. " if EN_DASH in s or "," in s else "p. ") + s


def _dot(s):
    """Append the closing period unless the text already ends in one."""
    if not s or s.endswith((".", '."', '?"', '!"')):
        return s
    return s + "."


def quoted(title, closer=","):
    """'"Title," ' — comma inside the closing quote; none after ? or !."""
    if not title:
        return ""
    t = str(title).strip()
    if closer and t[-1] in "?!":
        return '"%s"' % t
    return '"%s%s"' % (t, closer)


def render_reference(ref, md=False):
    """Render one reference dict as an IEEE entry. Returns (text, warnings)."""
    warns = []
    kind = TYPE_ALIASES.get(str(get(ref, "type", "kind", "entry_type")).lower().replace("-", "_").replace(" ", "_"))
    if kind is None:
        if get(ref, "journal"):
            kind = "journal"
        elif get(ref, "booktitle", "conference", "proceedings"):
            kind = "conference" if get(ref, "conference", "proceedings") or not get(ref, "publisher") else "chapter"
        elif get(ref, "arxiv", "eprint", "arxiv_id"):
            kind = "arxiv"
        elif get(ref, "patent", "patent_number"):
            kind = "patent"
        elif get(ref, "school", "university", "degree"):
            kind = "thesis"
        elif get(ref, "institution", "organization", "report_number"):
            kind = "report"
        elif get(ref, "publisher"):
            kind = "book"
        elif get(ref, "url"):
            kind = "website"
        else:
            kind = "journal"
        warns.append("no recognised type; treated as %s" % kind)

    def ital(s):
        return "*%s*" % s if (md and s) else s

    def join(parts):
        return ", ".join(p for p in parts if p)

    authors = authors_string(get(ref, "authors", "author"), force_et_al=bool(ref.get("et_al")))
    editors_raw = get(ref, "editors", "editor")
    editors = ""
    if editors_raw:
        eds = authors_string(editors_raw)
        n_eds = len(editors_raw) if isinstance(editors_raw, list) else (2 if " and " in eds else 1)
        editors = "%s, %s" % (eds, "Ed." if n_eds == 1 else "Eds.")
    title = get(ref, "title")
    year = get(ref, "year")
    doi = get(ref, "doi")
    url = get(ref, "url", "link")
    if url and DOI_URL_RE.match(url):
        doi = doi or DOI_URL_RE.match(url).group(1)
        url = ""
    accessed = fmt_date(get(ref, "accessed", "access_date", "retrieved"))
    address = get(ref, "address", "location") or join([get(ref, "city"), get(ref, "state"), get(ref, "country")])
    vol, no, pp = get(ref, "vol", "volume"), get(ref, "no", "number", "issue"), pages(get(ref, "pp", "pages"))
    vol_s, no_s = ("vol. %s" % vol if vol else ""), ("no. %s" % no if no else "")
    ch, sect = get(ref, "chapter", "ch"), get(ref, "section", "sect")
    ch_s, sect_s = ("ch. %s" % ch if ch else ""), ("sect. %s" % sect if sect else "")
    edition = get(ref, "edition")
    doi_s = "doi: %s" % doi if doi else ""
    date = date_string(ref)
    head = authors + ", " if authors else ""
    if kind not in ("standard", "website", "news", "report") and not authors:
        warns.append("no authors")
    if kind != "standard" and not title:
        warns.append("no title")

    def titled(body, closer=","):
        """authors, "Title," body — or "Title." when nothing follows the title."""
        if not body:
            return head + quoted(title, ".")
        return head + quoted(title, closer) + (" " if title else "") + body

    if kind == "journal":
        journal = get(ref, "journal", "periodical", "container")
        if not journal:
            warns.append("no journal name")
        art = get(ref, "art_no", "article_number", "article_no")
        main = titled(join([ital(journal), vol_s, no_s, pp, date, "Art. no. %s" % art if art else "", doi_s]))
    elif kind == "conference":
        booktitle = get(ref, "booktitle", "conference", "proceedings", "container")
        if not booktitle:
            warns.append("no conference / proceedings name")
        loc = get(ref, "location", "address") or join([get(ref, "city"), get(ref, "state"), get(ref, "country")])
        bt = booktitle if booktitle.lower().startswith("in ") else ital(booktitle)
        inner = join([bt, loc, date, pp, doi_s])
        main = titled(("in " + inner) if booktitle else inner)
    elif kind == "book":
        publisher = get(ref, "publisher")
        if not publisher:
            warns.append("no publisher")
        series = get(ref, "series")
        if not authors and editors:
            head = editors + " "
        lead = head + ital(title) + (" (%s)" % series if series else "") + (", vol. %s" % vol if vol else "")
        pub = ("%s: %s" % (address, publisher)) if (address and publisher) else (publisher or address)
        rest = join([pub, date or year, ch_s, sect_s, pp])
        if edition:
            lead += ", %s ed." % edition
        elif rest:
            lead = _dot(lead)
        main = lead + (" " + rest if rest else "")
    elif kind == "chapter":
        booktitle = get(ref, "booktitle", "book", "container")
        if not booktitle:
            warns.append("no book title")
        publisher = get(ref, "publisher")
        s = ("in " + ital(booktitle) if booktitle else "") + (", vol. %s" % vol if vol and booktitle else "")
        if editors:
            s = (s + ", " + editors) if s else editors
        if edition:
            s += ", %s ed." % edition
        pub = ("%s: %s" % (address, publisher)) if (address and publisher) else (publisher or address)
        rest = join([pub, date or year, ch_s, sect_s, pp])
        if rest and edition:
            s += " " + rest
        elif rest and editors:
            s += ", " + rest
        elif rest:
            s = (_dot(s) + " " + rest) if s else rest
        main = titled(s)
    elif kind in ("website", "news"):
        site = get(ref, "website", "site", "publication", "newspaper", "journal", "container", "publisher")
        if kind == "website" and not date:
            # Guide §II-T: J. Smith. "Page Title." Website Title. Accessed: Feb. 1, 2009. [Online]. Available: URL
            if not accessed:
                warns.append("website without accessed date")
            main = ((authors + ". ") if authors else "") + quoted(title, ".") + ((" " + _dot(site)) if site else "")
        else:
            # Guide §II-A / §II-J: J. K. Author, "Title," Title of the News Source, Month, Day, Year.
            if not date:
                warns.append("no date")
            main = titled(join([ital(site), date]))
        if not url:
            warns.append("no URL")
    elif kind == "arxiv":
        eid = re.sub(r"^arxiv:\s*", "", get(ref, "arxiv", "eprint", "arxiv_id", "id"), flags=re.I)
        if not eid:
            warns.append("no arXiv identifier")
        main = titled(join([year, "arXiv:%s" % eid if eid else "", doi_s]))
    elif kind == "patent":
        num = get(ref, "patent", "patent_number", "number")
        if not num:
            warns.append("no patent number")
        pat = num if re.search(r"\bpatent\b", num, re.I) else "%s Patent %s" % (get(ref, "country") or "U.S.", num)
        main = titled(join([pat if num else "", date]))
    elif kind == "standard":
        num = get(ref, "standard", "standard_number", "number")
        if not num:
            warns.append("no standard number")
        main = join([ital(title), num, get(ref, "organization", "org", "institution", "publisher"), address, date])
    elif kind in ("thesis", "dissertation"):
        degree = get(ref, "degree") or ("Ph.D. dissertation" if kind == "dissertation" else "M.S. thesis")
        school = get(ref, "school", "university", "institution")
        if not school:
            warns.append("no university")
        main = titled(join([degree, get(ref, "department", "dept"), school, address, year]))
    else:  # report
        inst = get(ref, "institution", "organization", "org", "company", "publisher")
        num = get(ref, "report_number", "number", "rep")
        if num and not re.match(r"(?i)^(tech|rep|memo|sci|final|contract|white|form|paper|version|doc|publ|r\b)", num):
            num = "Rep. %s" % num
        main = titled(join([inst, address, num, date]))
    if not year and not date and kind != "website":
        warns.append("no year")
    main = _dot(re.sub(r"\s+", " ", main).strip())
    tail = ""
    if accessed:
        tail += " Accessed: %s." % accessed
    if url:
        tail += " [Online]. Available: %s" % url
    return main + tail, warns


def load_refs(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        data = data.get("references", data.get("refs", []))
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise ValueError("expected a JSON list of reference objects (or {\"references\": [...]})")
    return data


# --- demo material --------------------------------------------------------------

# The SKILL.md worked example (clean).
DEMO_DOC = """# Report excerpt

Chain-of-Verification reduces hallucination by verifying each draft claim [1], and the Transformer architecture [2] underlies the models we benchmark. Reporting follows the PRISMA guideline [3].

## References

[1] S. Dhuliawala et al., "Chain-of-Verification reduces hallucination in large language models," arXiv:2309.11495, 2023.
[2] A. Vaswani et al., "Attention is all you need," in Proc. Adv. Neural Inf. Process. Syst. (NeurIPS), 2017, pp. 5998–6008.
[3] M. J. Page et al., "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews," BMJ, vol. 372, n71, 2021.
"""

# A draft with the classic problems: out-of-order first citation, gap, uncited
# entry, cited number without an entry, a range, a locator, a URL lint.
DEMO_BROKEN = """# Draft

Chain-of-Verification reduces hallucination [3], and the Transformer [1] underlies our models [1, 3]. Reporting follows PRISMA [2]-[4] and the IEEE guide [7, pp. 12–14].

## References

[1] A. Vaswani et al., "Attention is all you need," in Proc. Adv. Neural Inf. Process. Syst. (NeurIPS), 2017, pp. 5998–6008.
[2] M. J. Page et al., "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews," BMJ, vol. 372, n71, 2021.
[3] S. Dhuliawala et al., "Chain-of-Verification reduces hallucination in large language models," arXiv:2309.11495, 2023.
[4] IEEE Publication Operations, "IEEE Reference Guide," Piscataway, NJ, USA, 2025. [Online]. Available: https://ieeeauthorcenter.ieee.org/wp-content/uploads/IEEE-Reference-Guide.pdf
[6] W. Knight, "The most capable open source AI model yet could supercharge AI agents," Wired, Sep. 25, 2024. [Online]. Available: https://www.wired.com/story/molmo-open-source-multimodal-ai-model-allen-institute-agents/
"""

DEMO_REFS = [
    {"type": "arxiv", "authors": ["Shehzaad Dhuliawala", "Mojtaba Komeili", "Jing Xu", "Roberta Raileanu",
                                  "Xian Li", "Asli Celikyilmaz", "Jason Weston"],
     "title": "Chain-of-Verification reduces hallucination in large language models", "year": 2023,
     "arxiv": "2309.11495"},
    {"type": "conference", "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit",
                                       "Llion Jones", "Aidan N. Gomez", "Lukasz Kaiser", "Illia Polosukhin"],
     "title": "Attention is all you need", "booktitle": "Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)",
     "year": 2017, "pp": "5998-6008"},
    {"type": "journal", "authors": ["Matthew J. Page", "Joanne E. McKenzie", "Patrick M. Bossuyt", "Isabelle Boutron",
                                    "Tammy C. Hoffmann", "Cynthia D. Mulrow", "Larissa Shamseer"],
     "title": "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews",
     "journal": "BMJ", "vol": 372, "art_no": "n71", "year": 2021, "doi": "10.1136/bmj.n71"},
]


# --- CLI ------------------------------------------------------------------------


def read_text(path, parser):
    try:
        with open(path, encoding="utf-8", newline="") as fh:   # keep CRLF as-is
            return fh.read()
    except OSError as exc:
        parser.error("could not read %s: %s" % (path, exc))


def print_report(rep, label):
    s = rep["summary"]
    doc = rep["doc"]
    where = ""
    if rep["entries"]:
        lo, hi = rep["entries"][0]["line"], rep["entries"][-1]["line"]
        where = " (line %d" % lo if lo == hi else " (lines %d%s%d" % (lo, EN_DASH, hi)
        where += ", heading at line %d)" % (doc["heading"] + 1) if doc["heading"] is not None else ", no heading)"
    print("%s: %d in-text citation group%s (%d distinct source%s); reference list: %d entr%s%s"
          % (label, s["citations"], "" if s["citations"] == 1 else "s", s["distinct_cited"],
             "" if s["distinct_cited"] == 1 else "s", s["entries"], "y" if s["entries"] == 1 else "ies", where))
    if rep["problems"]:
        print()
        print("%5s  %-7s  %-14s  %-5s  %s" % ("line", "level", "code", "ref", "problem"))
        for p in rep["problems"]:
            print("%5s  %-7s  %-14s  %-5s  %s" % (p["line"] or "-", p["severity"].upper(), p["code"],
                                                  "[%d]" % p["ref"] if p["ref"] else "-", p["message"]))
    print()
    print("%d error%s, %d warning%s — %s" % (s["errors"], "" if s["errors"] == 1 else "s", s["warnings"],
                                             "" if s["warnings"] == 1 else "s", "OK" if rep["ok"] else "FAIL"))


def report_json(rep, label):
    return {
        "file": label,
        "citations": [{"line": c["line"], "text": c["text"], "numbers": c["numbers"], "locator": c["locator"]}
                      for c in rep["citations"]],
        "first_cited_order": rep["first_cited_order"],
        "references": [{"n": e["n"], "line": e["line"], "text": e["text"]} for e in rep["entries"]],
        "problems": rep["problems"],
        "summary": rep["summary"],
        "ok": rep["ok"],
    }


def cmd_check(args, parser):
    if args.demo:
        text, label = DEMO_BROKEN, "demo"
    elif args.file:
        text, label = read_text(args.file, parser), args.file
    else:
        parser.error("pass --file PATH (or --demo)")
    rep = analyse(text)
    if args.json:
        print(json.dumps(report_json(rep, label), indent=2, ensure_ascii=False))
    else:
        print_report(rep, label)
    return 0 if rep["ok"] else 1


def cmd_renumber(args, parser):
    if args.demo:
        text = DEMO_BROKEN
    elif args.file:
        text = read_text(args.file, parser)
    else:
        parser.error("pass --file PATH (or --demo)")
    new_text, mapping, notes = renumber(text)
    for n in notes:
        print("renumber: " + n, file=sys.stderr)
    if args.write:
        with open(args.write, "w", encoding="utf-8", newline="") as fh:
            fh.write(new_text)
        print("wrote %s" % args.write, file=sys.stderr)
    else:
        sys.stdout.write(new_text)
        if not new_text.endswith("\n"):
            sys.stdout.write("\n")
    return 0


def cmd_format(args, parser):
    if args.demo:
        refs = DEMO_REFS
    elif args.file:
        try:
            refs = load_refs(args.file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error("could not load %s: %s" % (args.file, exc))
    else:
        parser.error("pass --file refs.json (or --demo)")
    rendered = []
    for i, ref in enumerate(refs, start=1):
        text, warns = render_reference(ref, md=args.md)
        rendered.append({"n": i, "type": TYPE_ALIASES.get(str(get(ref, "type", "kind", "entry_type")).lower(), "inferred"), "text": text})
        for w in warns:
            print("format: ref %d: %s" % (i, w), file=sys.stderr)
    if args.json:
        print(json.dumps(rendered, indent=2, ensure_ascii=False))
    else:
        for r in rendered:
            print("[%d] %s" % (r["n"], r["text"]))
    return 0


def run_demo():
    print("=== check: SKILL.md worked example (clean) ===")
    print_report(analyse(DEMO_DOC), "worked-example.md")
    print()
    print("=== check: broken draft ===")
    print_report(analyse(DEMO_BROKEN), "draft.md")
    print()
    print("=== renumber: broken draft ===")
    new_text, _, notes = renumber(DEMO_BROKEN)
    for n in notes:
        print("renumber: " + n)
    print("---")
    print(new_text.rstrip("\n"))
    print("---")
    print()
    print("=== format: worked-example sources from structured fields ===")
    for i, ref in enumerate(DEMO_REFS, start=1):
        print("[%d] %s" % (i, render_reference(ref)[0]))
    return 0


# --- selftest -------------------------------------------------------------------


def run_selftest():
    """Hand-verified cases: the SKILL.md worked example, small synthetic
    documents with one planted fault each, and the IEEE Reference Guide's own
    examples (V 3.28.2025) as expected renderings."""
    checks = []

    def check(name, ok, detail=""):
        checks.append(bool(ok))
        print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -> " + str(detail)) if (detail and not ok) else ""))
        if not ok:
            print("SELFTEST FAILED at: %s" % name, file=sys.stderr)
            sys.exit(1)

    def codes(rep, severity=None):
        return sorted(p["code"] for p in rep["problems"] if severity is None or p["severity"] == severity)

    # 1. The worked example is clean: 3 citations, 3 entries, no problems, ok.
    rep = analyse(DEMO_DOC)
    check("worked example: 3 citation groups, 3 entries", rep["summary"]["citations"] == 3 and rep["summary"]["entries"] == 3)
    check("worked example: first-cited order 1, 2, 3", rep["first_cited_order"] == [1, 2, 3])
    check("worked example: no errors, no warnings, ok", rep["ok"] and not rep["problems"], rep["problems"])

    # 2. Out-of-order first citation: [2] before [1] -> order + sequence errors.
    doc = "Text [2] then [1].\n\n## References\n\n[1] A. One, \"First,\" J. A, vol. 1, no. 1, pp. 1–2, Jan. 2020.\n[2] B. Two, \"Second,\" J. B, vol. 2, no. 2, pp. 3–4, Feb. 2021.\n"
    rep = analyse(doc)
    check("out-of-order: detected as error", not rep["ok"] and codes(rep, "error") == ["order", "sequence"], codes(rep))
    order_p = [p for p in rep["problems"] if p["code"] == "order"][0]
    check("out-of-order: names [2] on line 1", order_p["ref"] == 2 and order_p["line"] == 1
          and order_p["message"].startswith("[2] is first cited before [1]"), order_p)

    # 3. Gap in the reference list: [1], [2], [4] with [3] cited -> list-gap + no-entry.
    doc = "Text [1], [2], [3].\n\nReferences\n\n[1] A. One, \"First,\" J. A, vol. 1, no. 1, pp. 1–2, Jan. 2020.\n[2] B. Two, \"Second,\" J. B, vol. 2, no. 2, pp. 3–4, Feb. 2021.\n[4] D. Four, \"Fourth,\" J. D, vol. 4, no. 4, pp. 7–8, Apr. 2023.\n"
    rep = analyse(doc)
    check("gap: list-gap, no-entry, uncited errors", codes(rep, "error") == ["list-gap", "no-entry", "uncited"], codes(rep))
    gap = [p for p in rep["problems"] if p["code"] == "list-gap"][0]
    check("gap: message names [3] at the line of [4]", "[3]" in gap["message"] and gap["line"] == 7, gap)
    check("gap: bare 'References' line accepted as heading", rep["doc"]["heading"] == 2)

    # 4. Uncited entry: [3] listed, never cited.
    doc = "Text [1] and [2].\n\n## References\n[1] A. One, \"First,\" J. A, vol. 1, no. 1, pp. 1–2, Jan. 2020.\n[2] B. Two, \"Second,\" J. B, vol. 2, no. 2, pp. 3–4, Feb. 2021.\n[3] C. Three, \"Third,\" J. C, vol. 3, no. 3, pp. 5–6, Mar. 2022.\n"
    rep = analyse(doc)
    check("uncited: exactly one error, code uncited, ref [3] line 6",
          codes(rep, "error") == ["uncited"] and rep["problems"][0]["ref"] == 3 and rep["problems"][0]["line"] == 6, rep["problems"])

    # 5. Ranges and locators expand: [2]–[4], [2]-[4], [2–4], [7, pp. 12–14], [1, 4].
    doc = "A [1] b [2]–[4] c [2]-[4] d [2–4] e [7, pp. 12–14] f [1, 4] g [1][2] h `x[9]` i [3](http://x) j [Online]."
    cits, probs = scan_citations(parse_document(doc))
    check("ranges: eight citation groups found (code span, link, [Online] skipped)", len(cits) == 8, [c["text"] for c in cits])
    check("range [2]–[4] expands to 2, 3, 4", cits[1]["numbers"] == [2, 3, 4] and cits[1]["kind"] == "bracket-range")
    check("range [2]-[4] (hyphen) expands to 2, 3, 4", cits[2]["numbers"] == [2, 3, 4])
    check("range [2–4] (in-bracket) expands to 2, 3, 4", cits[3]["numbers"] == [2, 3, 4])
    check("locator [7, pp. 12–14] -> number 7, locator kept", cits[4]["numbers"] == [7] and cits[4]["locator"] == "pp. 12–14")
    check("list [1, 4] -> 1, 4", cits[5]["numbers"] == [1, 4])
    check("adjacent [1][2] flagged as warning", [p["code"] for p in probs] == ["adjacent"])
    check("first-cited order across the line", first_cited_order(cits) == [1, 2, 3, 4, 7])
    check("descending range [5]–[2] is an error", any(p["code"] == "range" for p in scan_citations(parse_document("x [5]–[2] y"))[1]))

    # 6. Renumber: expected text worked out by hand.
    doc = ("Intro cites [3] first, then [1], and both again [1, 3]. Later [2]–[4] and [7, pp. 12–14].\n"
           "\n## References\n\n"
           "[1] A. One, \"First,\" J. A, vol. 1, no. 1, pp. 1–2, Jan. 2020.\n"
           "[2] B. Two, \"Second,\" J. B, vol. 2, no. 2, pp. 3–4, Feb. 2021.\n"
           "[3] C. Three, \"Third,\" J. C, vol. 3, no. 3, pp. 5–6, Mar. 2022.\n"
           "[4] D. Four, \"Fourth,\" J. D, vol. 4, no. 4, pp. 7–8, Apr. 2023.\n"
           "[5] E. Five, \"Fifth,\" J. E, vol. 5, no. 5, pp. 9–10, May 2024.\n")
    want = ("Intro cites [1] first, then [2], and both again [1], [2]. Later [1], [3], [4] and [5, pp. 12–14].\n"
            "\n## References\n\n"
            "[1] C. Three, \"Third,\" J. C, vol. 3, no. 3, pp. 5–6, Mar. 2022.\n"
            "[2] A. One, \"First,\" J. A, vol. 1, no. 1, pp. 1–2, Jan. 2020.\n"
            "[3] B. Two, \"Second,\" J. B, vol. 2, no. 2, pp. 3–4, Feb. 2021.\n"
            "[4] D. Four, \"Fourth,\" J. D, vol. 4, no. 4, pp. 7–8, Apr. 2023.\n"
            "[5] <!-- MISSING ENTRY: [7] is cited in the text but has no reference entry -->\n"
            "[6] E. Five, \"Fifth,\" J. E, vol. 5, no. 5, pp. 9–10, May 2024. <!-- UNCITED: not cited in the text -->\n")
    got, mapping, notes = renumber(doc)
    check("renumber: mapping 3->1, 1->2, 2->3, 4->4, 7->5, 5->6", mapping == {3: 1, 1: 2, 2: 3, 4: 4, 7: 5, 5: 6}, mapping)
    check("renumber: output text matches the hand-worked expectation", got == want, got)
    check("renumber: result passes the order/gap checks", codes(analyse(got), "error") == ["uncited"], codes(analyse(got)))
    check("renumber: a clean document is unchanged", renumber(DEMO_DOC)[0] == DEMO_DOC)
    check("canonical group: guide form, one number per bracket",
          canonical_group([12, 8, 7, 6, 5, 3, 1], None) == "[1], [3], [5], [6], [7], [8], [12]",
          canonical_group([12, 8, 7, 6, 5, 3, 1], None))
    check("canonical group: locator stays inside its own bracket",
          canonical_group([3], "pp. 5–10") == "[3, pp. 5–10]", canonical_group([3], "pp. 5–10"))

    # 7. Entry lint (warnings): period, year, quoted title, venue, accessed.
    doc = ("See [1], [2], [3], [4].\n\n## References\n"
           "[1] A. One, \"First,\" J. A, vol. 1, no. 1, pp. 1–2, Jan. 2020\n"
           "[2] B. Two, \"Second,\" J. B, vol. 2, no. 2, pp. 3–4.\n"
           "[3] C. Three, Third thoughts, 2022.\n"
           "[4] D. Four, \"Fourth,\" 2023. [Online]. Available: https://example.org/four\n")
    rep = analyse(doc)
    by_ref = {}
    for p in rep["problems"]:
        by_ref.setdefault(p["ref"], []).append(p["code"])
    check("lint: no errors, only warnings", rep["ok"] and rep["summary"]["warnings"] > 0)
    check("lint: [1] missing final period", by_ref.get(1) == ["no-period"], by_ref.get(1))
    check("lint: [2] missing year", by_ref.get(2) == ["no-year"], by_ref.get(2))
    check("lint: [3] no quoted title", by_ref.get(3) == ["no-title"], by_ref.get(3))
    check("lint: [4] no venue + URL without Accessed", sorted(by_ref.get(4, [])) == ["no-accessed", "no-venue"], by_ref.get(4))

    # 8. format: the guide's own examples rendered from fields (straight quotes, en dash).
    r = {"type": "journal", "authors": ["M. M. Chiampi", "L. L. Zilberti"],
         "title": "Induction of electric field in human bodies moving near MRI: An efficient BEM computational procedure",
         "journal": "IEEE Trans. Biomed. Eng.", "vol": 58, "no": 10, "pp": "2787-2793", "month": "Oct", "year": 2011,
         "doi": "10.1109/TBME.2011.2158315"}
    want = ('M. M. Chiampi and L. L. Zilberti, "Induction of electric field in human bodies moving near MRI: '
            'An efficient BEM computational procedure," IEEE Trans. Biomed. Eng., vol. 58, no. 10, pp. 2787–2793, '
            'Oct. 2011, doi: 10.1109/TBME.2011.2158315.')
    check("format journal = Guide §II-M 'Periodical With DOI' example", render_reference(r)[0] == want, render_reference(r)[0])
    check("format journal --md italicises the periodical", "*IEEE Trans. Biomed. Eng.*" in render_reference(r, md=True)[0])
    r = {"type": "conference", "authors": ["G. Veruggio"], "title": "The EURON roboethics roadmap",
         "booktitle": "Proc. Humanoids '06: 6th IEEE-RAS Int. Conf. Humanoid Robots", "year": 2006, "pp": "612–617",
         "doi": "10.1109/ICHR.2006.321337"}
    check("format conference = Guide 'Conference Proceedings With DOI' example",
          render_reference(r)[0] == 'G. Veruggio, "The EURON roboethics roadmap," in Proc. Humanoids \'06: 6th IEEE-RAS Int. Conf. Humanoid Robots, 2006, pp. 612–617, doi: 10.1109/ICHR.2006.321337.',
          render_reference(r)[0])
    r = {"type": "book", "authors": ["B. Klaus", "P. Horn"], "title": "Robot Vision", "address": "Cambridge, MA, USA",
         "publisher": "MIT Press", "year": 1986}
    check("format book = Guide 'Book' example", render_reference(r)[0] == "B. Klaus and P. Horn, Robot Vision. Cambridge, MA, USA: MIT Press, 1986.", render_reference(r)[0])
    r = {"type": "chapter", "authors": ["L. Stein"], "title": "Random patterns", "booktitle": "Computers and You",
         "editors": ["J. S. Brake"], "address": "New York, NY, USA", "publisher": "Wiley", "year": 1994, "pp": "55-70"}
    check("format chapter = Guide 'Book With Editor(s)' example",
          render_reference(r)[0] == 'L. Stein, "Random patterns," in Computers and You, J. S. Brake, Ed., New York, NY, USA: Wiley, 1994, pp. 55–70.', render_reference(r)[0])
    r = {"type": "patent", "authors": ["J. P. Wilkinson"], "title": "Nonlinear resonant circuit devices", "number": "3 624 125",
         "month": "July", "day": 16, "year": 1990}
    check("format patent = Guide 'Patent' example",
          render_reference(r)[0] == 'J. P. Wilkinson, "Nonlinear resonant circuit devices," U.S. Patent 3 624 125, Jul. 16, 1990.', render_reference(r)[0])
    r = {"type": "standard", "title": "IEEE Criteria for Class IE Electric Systems", "number": "IEEE Standard 308", "year": 1969}
    check("format standard = Guide 'Standards' example",
          render_reference(r)[0] == "IEEE Criteria for Class IE Electric Systems, IEEE Standard 308, 1969.", render_reference(r)[0])
    r = {"type": "phdthesis", "authors": ["J. O. Williams"], "title": "Narrow-band analyzer", "department": "Dept. Elect. Eng.",
         "school": "Harvard Univ.", "address": "Cambridge, MA, USA", "year": 1993}
    check("format thesis = Guide 'Theses and Dissertations' example",
          render_reference(r)[0] == 'J. O. Williams, "Narrow-band analyzer," Ph.D. dissertation, Dept. Elect. Eng., Harvard Univ., Cambridge, MA, USA, 1993.', render_reference(r)[0])
    r = {"type": "report", "authors": ["E. E. Reber", "R. L. Michell", "C. J. Carter"], "title": "Oxygen absorption in the Earth's atmosphere",
         "institution": "Aerospace Corp.", "address": "Los Angeles, CA, USA", "number": "Tech. Rep. TR-0200 (4230-46)-3",
         "month": 11, "year": 1988}
    check("format report = Guide 'Reports' example",
          render_reference(r)[0] == 'E. E. Reber, R. L. Michell, and C. J. Carter, "Oxygen absorption in the Earth\'s atmosphere," Aerospace Corp., Los Angeles, CA, USA, Tech. Rep. TR-0200 (4230-46)-3, Nov. 1988.', render_reference(r)[0])
    r = {"type": "arxiv", "authors": ["S. Urazhdin", "N. O. Birge", {"given": "William P.", "family": "Pratt", "suffix": "Jr."}, "J. Bass"],
         "title": "Current-driven magnetic excitations in permalloy-based multilayer nanopillars", "year": 2003, "arxiv": "arXiv:0303149"}
    check("format arXiv = Guide 'Preprint arXiv' example (year, arXiv:ID)",
          render_reference(r)[0] == 'S. Urazhdin, N. O. Birge, W. P. Pratt Jr., and J. Bass, "Current-driven magnetic excitations in permalloy-based multilayer nanopillars," 2003, arXiv:0303149.', render_reference(r)[0])
    r = {"type": "website", "authors": ["J. Smith"], "title": "Obama inaugurated as President", "website": "CNN.com",
         "accessed": "2009-02-01", "url": "http://www.cnn.com/POLITICS/01/21/obama_inaugurated/index.html"}
    check("format website = Guide §II-T example (Accessed:, no final period after URL)",
          render_reference(r)[0] == 'J. Smith. "Obama inaugurated as President." CNN.com. Accessed: Feb. 1, 2009. [Online]. Available: http://www.cnn.com/POLITICS/01/21/obama_inaugurated/index.html', render_reference(r)[0])
    r = {"type": "news", "authors": ["A. Clark"], "title": "A new AI tool creates hyperrealistic photos. Can you tell the difference?",
         "publication": "CBS News", "date": "2024-08-30", "url": "https://www.cbsnews.com/news/can-you-tell-real-image-from-ai-flux/"}
    check("format news = Guide 'News Article (Online)' example (no comma after ?)",
          render_reference(r)[0] == 'A. Clark, "A new AI tool creates hyperrealistic photos. Can you tell the difference?" CBS News, Aug. 30, 2024. [Online]. Available: https://www.cbsnews.com/news/can-you-tell-real-image-from-ai-flux/', render_reference(r)[0])

    # 9. Authors: initials, particles, suffixes, hyphens, corporate names, et al. after six.
    check("person: 'Jane K. Author' -> 'J. K. Author'", format_person("Jane K. Author") == "J. K. Author")
    check("person: 'Author, Jane K.' -> 'J. K. Author'", format_person("Author, Jane K.") == "J. K. Author")
    check("person: 'Jean-Luc Dessalles' -> 'J.-L. Dessalles'", format_person("Jean-Luc Dessalles") == "J.-L. Dessalles")
    check("person: 'Jan van Etten' -> 'J. van Etten'", format_person("Jan van Etten") == "J. van Etten")
    check("person: 'William P. Pratt Jr.' -> 'W. P. Pratt Jr.' (no comma, Guide §II)", format_person("William P. Pratt Jr.") == "W. P. Pratt Jr.")
    check("person: corporate author kept verbatim", format_person("Bureau of Meteorology") == "Bureau of Meteorology"
          and format_person({"literal": "Nvidia Corporation"}) == "Nvidia Corporation")
    six = ["A. One", "B. Two", "C. Three", "D. Four", "E. Five", "F. Six"]
    check("authors: six names all listed", authors_string(six) == "A. One, B. Two, C. Three, D. Four, E. Five, and F. Six")
    check("authors: seven names -> 'A. One et al.'", authors_string(six + ["G. Seven"]) == "A. One et al.")
    check("authors: two names joined with 'and'", authors_string(["A. One", "B. Two"]) == "A. One and B. Two")
    check("dates: 'September 23, 2024' -> 'Sep. 23, 2024'; '2011-10' -> 'Oct. 2011'",
          fmt_date("September 23, 2024") == "Sep. 23, 2024" and fmt_date("2011-10") == "Oct. 2011")
    check("pages: '123-145' -> 'pp. 123–145'; '475' -> 'p. 475'", pages("123-145") == "pp. 123–145" and pages("475") == "p. 475")

    # 10. The demo material behaves as documented.
    rep = analyse(DEMO_BROKEN)
    check("demo draft: order, sequence, list-gap, uncited, no-entry errors",
          codes(rep, "error") == ["list-gap", "no-entry", "order", "sequence", "uncited"], codes(rep, "error"))
    check("demo draft: exactly one warning (no-accessed on [4])",
          [(p["code"], p["ref"]) for p in rep["problems"] if p["severity"] == "warning"] == [("no-accessed", 4)])
    check("demo refs: journal with Art. no. renders per Guide 'Periodical With Article ID'",
          render_reference(DEMO_REFS[2])[0] == 'M. J. Page et al., "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews," BMJ, vol. 372, 2021, Art. no. n71, doi: 10.1136/bmj.n71.', render_reference(DEMO_REFS[2])[0])

    print("selftest OK (%d checks passed)" % len(checks))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Check, renumber and format IEEE numbered-bracket citations (IEEE Reference Guide).")
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", dest="demo_all", action="store_true",
                        help="run check / renumber / format on the built-in sample documents and exit")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("check", help="verify citation order, list completeness and entry style; exit 1 on errors")
    p.add_argument("--file", help="markdown or plain-text document")
    p.add_argument("--demo", action="store_true", help="check the built-in broken sample instead of --file")
    p.add_argument("--json", action="store_true", help="machine-readable report")
    p = sub.add_parser("renumber", help="renumber citations by first appearance and reorder the reference list")
    p.add_argument("--file", help="markdown or plain-text document")
    p.add_argument("--demo", action="store_true", help="renumber the built-in broken sample")
    p.add_argument("--write", metavar="OUT", help="write the result to OUT instead of stdout")
    p = sub.add_parser("format", help="render structured references (JSON list) as IEEE entries")
    p.add_argument("--file", help="JSON: list of objects with type, authors, title, journal, vol, no, pp, month, year, doi, url, accessed, ...")
    p.add_argument("--demo", action="store_true", help="render the built-in sample references")
    p.add_argument("--md", action="store_true", help="markdown output: italicise periodical / book titles")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo_all:
        return run_demo()
    if not args.command:
        parser.error("choose a command: check | renumber | format  (or --demo / --selftest)")
    if args.command == "check":
        return cmd_check(args, parser)
    if args.command == "renumber":
        return cmd_renumber(args, parser)
    return cmd_format(args, parser)


if __name__ == "__main__":
    sys.exit(main())
