#!/usr/bin/env python3
"""landscape.py — assignee concentration, filing velocity, CPC white-space and
entrant/dormant reads over a set of patent FAMILIES (companion to ../SKILL.md).

Input: one row per patent family (dedupe by family first — SKILL.md anti-pattern 4):
    assignee, priority_year, cpc            (cpc = 'H01M10/052;H01M4/58', ';'-separated)
    optional: jurisdictions ('US;EP;CN'), family_size, citations
CSV with a header row, or JSON (a list of objects, or {"families": [...]}).
`--file -` reads stdin. Column names are matched case-insensitively with a few
aliases (applicant/owner, year/filing_year, ipc, countries, cited_by, ...).

Definitions implemented
  * Herfindahl-Hirschman Index (HHI, SKILL.md step 2) = sum over assignees of
    (percentage share)^2; 0-10,000, a single holder = 10,000. Bands as published
    by the US DOJ and FTC and printed side by side:
      - Horizontal Merger Guidelines (19 Aug 2010) §5.3: < 1,500 unconcentrated;
        1,500-2,500 moderately concentrated; > 2,500 highly concentrated.
      - Merger Guidelines (18 Dec 2023), Guideline 1 / §2.1: > 1,800 highly
        concentrated (a change of > 100 is significant). The DOJ Antitrust
        Division's HHI explainer (justice.gov/atr/herfindahl-hirschman-index)
        states the accompanying lower bands: 1,000-1,800 moderately concentrated,
        < 1,000 unconcentrated (the 1982/1992 bands the 2023 Guidelines revert to).
    These are merger-review yardsticks applied here to family shares as a
    descriptive scale — not an antitrust finding.
  * CR4 = summed share of the four largest assignees (top-4 concentration ratio).
  * Numbers-equivalent = 10,000 / HHI (how many equal-sized holders give the same HHI).
  * Long tail = assignees holding exactly one family.
  * Filing velocity (SKILL.md step 3): families per priority year, year-over-year
    growth, CAGR = (last/first)^(1/years) - 1 between the first and last non-zero
    years, trailing 3-year rolling mean, peak year, share of families in the last
    N years, and a trend label (mean of the last N years vs the mean of the N
    years before: ratio >= 1.25 accelerating, <= 0.80 declining, else flat).
  * White-space (SKILL.md steps 4-5): CPC (top-K) x assignee (top-M) matrix;
    empty (0) and low (<= --low) cells are candidate white space; CPC
    co-occurrence pairs (families carrying both codes); per-assignee CPC breadth.
  * Entry (an assignee-level read of step 3): first/last priority year per
    assignee; entrant = first year within the last --recent years; dormant = no
    family in the last --dormant years; otherwise established.
  * WIPO, Guidelines for Preparing Patent Landscape Reports (WIPO Publication
    946E, ISBN 978-92-805-2529-8, 2015; prepared by A. Trippe, Patinformatics LLC;
    doi:10.34667/tind.28858): count by family (§8.3.2), families by year (§8.4.1),
    top applicants/assignees (§8.4.6), top IPC/CPC (§8.4.4), lists and
    co-occurrence matrices (§6.2-6.3), and the dip in the most recent years
    caused by the 18-month publication delay (§8.3.4) — the warning this tool
    prints with every velocity read.

"Last N years" always means the N calendar years ending at the reference year
(--asof; default = the latest priority year in the data). No wall clock is used,
so two runs on the same file are byte-identical.

Exit codes: 0 ok; 1 usage/input error; 2 cluster smaller than --min-families
(default 5: SKILL.md says say so rather than force a landscape read).

Usage:
    python3 landscape.py report      --file families.csv [--scope TEXT] [--recent 3] [--dormant 4] [--json]
    python3 landscape.py concentrate --file families.csv [--top 10]
    python3 landscape.py velocity    --file families.json [--recent 3] [--asof 2025]
    python3 landscape.py whitespace  --file families.csv [--cpc 8] [--assignees 6] [--low 1] [--level full|group|subclass]
    python3 landscape.py entry       --file families.csv [--recent 3] [--dormant 4]
    python3 landscape.py report --demo          # synthetic 42-family cluster from the SKILL.md worked example
    python3 landscape.py --selftest
"""

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter

# --- constants ---------------------------------------------------------------

# HHI bands: (lower bound of "moderately concentrated", lower bound of "highly").
HHI_BANDS = {
    "2023": (1000.0, 1800.0),   # 2023 Merger Guidelines G1 / DOJ HHI explainer
    "2010": (1500.0, 2500.0),   # 2010 Horizontal Merger Guidelines §5.3
}
HHI_BAND_LABEL = {
    "2023": "2023 Merger Guidelines, Guideline 1 (<1,000 / 1,000-1,800 / >1,800)",
    "2010": "2010 Horizontal Merger Guidelines s5.3 (<1,500 / 1,500-2,500 / >2,500)",
}
TOP_SHARE_CONCENTRATED = 25.0   # SKILL.md step 2: no single holder above ~20-25% = crowded/open
TREND_ACCEL = 1.25              # recent-mean / prior-mean at or above this = accelerating
TREND_DECLINE = 0.80            # ... at or below this = declining
LAG_MONTHS = 24                 # years within this many months of the reference year are flagged
LAG_WARNING = (
    "WARNING: publication lag -- applications publish ~18 months after priority "
    "(WIPO 2015 s8.3.4) and family/CPC data lag further, so the last 18-36 months "
    "are under-counted; a flat or declining tail may be an artefact, not a cooling race."
)
LEVELS = ("full", "group", "subclass")

# Flexible column names for CSV headers / JSON keys (matched lower-cased).
ASSIGNEE_KEYS = ("assignee", "applicant", "owner", "holder", "assignees", "applicants", "current_assignee",
                 "owners", "company")
YEAR_KEYS = ("priority_year", "year", "priority", "filing_year", "priority_date", "filing_date",
             "earliest_priority_year", "earliest_priority_date", "first_priority_year")
CPC_KEYS = ("cpc", "ipc", "cpc_codes", "ipc_codes", "cpcs", "cpc_classifications", "ipc_classifications",
            "ipcr_classifications", "classes", "classification", "classifications")
JURIS_KEYS = ("jurisdictions", "jurisdiction", "countries", "country", "authorities", "offices")
SIZE_KEYS = ("family_size", "size", "members", "family_members", "n_members")
CITE_KEYS = ("citations", "cited_by", "forward_citations", "cites", "citation_count")

UNKNOWN = "(unknown)"

# Synthetic 42-family cluster reproducing the SKILL.md worked example
# ("solid-state battery manufacturing"): 3 -> 5 -> 9 -> 14 -> 11 families per
# priority year 2019-2023; Incumbent A 9, Incumbent B 7, Startup C 5 (top-3 =
# 21 of 42); H01M10/0562 on 26 families, H01M4/04 on 4, H01M4/366 on 1.
# Columns: assignee, priority_year, cpc, jurisdictions, family_size, citations.
DEMO = [
    ("Incumbent A", 2020, "H01M10/0562;H01M10/0525", "US;EP;CN;JP;KR", 12, 18),
    ("Incumbent A", 2020, "H01M10/0525", "US;EP;JP", 9, 11),
    ("Incumbent A", 2021, "H01M10/0562;H01M4/13", "US;EP;CN;JP;KR", 14, 9),
    ("Incumbent A", 2021, "H01M10/0562;H01M10/058", "US;EP;CN;JP", 10, 7),
    ("Incumbent A", 2022, "H01M10/0562;H01M4/04", "US;EP;CN;JP;KR", 11, 4),
    ("Incumbent A", 2022, "H01M10/0562;H01M4/62", "US;EP;JP", 8, 3),
    ("Incumbent A", 2022, "H01M10/0525;H01M4/13", "US;JP", 6, 2),
    ("Incumbent A", 2023, "H01M10/0562;H01M10/058", "US;EP;CN;JP;KR", 9, 1),
    ("Incumbent A", 2023, "H01M10/0562;H01M4/04", "US;EP;JP", 7, 0),
    ("Incumbent B", 2019, "H01M10/0525", "US;EP;JP;KR", 10, 21),
    ("Incumbent B", 2020, "H01M10/0562;H01M10/0525", "US;EP;CN;JP;KR", 13, 15),
    ("Incumbent B", 2021, "H01M10/0562;H01M10/058", "US;EP;KR", 8, 8),
    ("Incumbent B", 2022, "H01M10/0562;H01M4/13", "US;EP;CN;KR", 9, 3),
    ("Incumbent B", 2022, "H01M4/13;H01M10/0525", "US;KR", 5, 2),
    ("Incumbent B", 2023, "H01M10/0562;H01M4/04", "US;EP;CN;JP;KR", 11, 1),
    ("Incumbent B", 2023, "H01M10/0562;H01M10/058", "US;KR", 6, 0),
    ("Startup C", 2021, "H01M10/0562;H01M4/62", "US;EP", 4, 6),
    ("Startup C", 2021, "H01M10/058", "US", 2, 3),
    ("Startup C", 2022, "H01M10/0562;H01M4/62", "US;EP;JP", 5, 2),
    ("Startup C", 2022, "H01M10/0525;H01M4/13", "US", 2, 1),
    ("Startup C", 2023, "H01M10/0562;H01M10/058", "US;EP", 3, 0),
    ("Incumbent D", 2019, "H01M10/0525", "US;EP;JP", 9, 14),
    ("Incumbent D", 2019, "H01M10/0562;H01M4/62", "US;JP", 6, 10),
    ("Incumbent E", 2020, "H01M10/0525", "EP;DE;US", 7, 9),
    ("Incumbent E", 2023, "H01M10/0562;H01M4/13", "EP;US;CN", 8, 0),
    ("Startup F", 2022, "H01M4/13", "US", 2, 1),
    ("Startup F", 2023, "H01M10/0562;H01M4/04", "US;EP", 3, 0),
    ("Startup G", 2022, "H01M10/0525;H01M4/13", "US;KR", 3, 2),
    ("Startup G", 2023, "H01M10/0562", "US", 1, 0),
    ("University H", 2020, "H01M10/0562;H01M4/62", "US", 2, 12),
    ("University H", 2021, "H01M10/0525", "US;EP", 3, 5),
    ("Supplier I", 2021, "H01M10/0525", "JP;US", 4, 4),
    ("Supplier I", 2022, "H01M10/0562;H01M4/13", "JP;US;EP", 5, 2),
    ("Startup J", 2021, "H01M10/0562", "US", 1, 3),
    ("Startup K", 2022, "H01M10/0525", "US;EP", 2, 1),
    ("Startup L", 2022, "H01M10/0562;H01M4/366", "US", 1, 2),
    ("University M", 2022, "H01M10/0525", "US", 1, 1),
    ("Startup N", 2023, "H01M10/0562", "US;EP", 2, 0),
    ("University O", 2023, "H01M10/058", "US", 1, 0),
    ("Startup P", 2023, "H01M10/0562", "US", 1, 0),
    ("Supplier Q", 2022, "H01M10/0525", "JP", 2, 1),
    ("Startup R", 2021, "H01M10/0562", "US;CN", 2, 4),
]


def demo_rows():
    keys = ("assignee", "priority_year", "cpc", "jurisdictions", "family_size", "citations")
    return [dict(zip(keys, row)) for row in DEMO]


# --- input parsing -----------------------------------------------------------


def _find_key(mapping, candidates):
    """Return the actual key in `mapping` matching one of `candidates`
    (case-insensitive; spaces, hyphens and slashes count as underscores, so
    'Priority Date' matches 'priority_date')."""
    lowered = {re.sub(r"[\s\-/]+", "_", str(k).strip().lower()): k for k in mapping}
    for cand in candidates:
        if cand in lowered:
            return lowered[cand]
    return None


def split_multi(raw):
    """'A; B;C' (or '|'-separated, or a JSON list) -> sorted tuple of unique tokens.
    A cell without a separator is one token even if it contains spaces
    ('H01M 10/0562' is a single CPC code)."""
    if raw is None:
        return ()
    if isinstance(raw, (list, tuple)):
        parts = [str(p) for p in raw]
    else:
        s = str(raw).strip()
        if not s:
            return ()
        sep = ";" if ";" in s else ("|" if "|" in s else None)
        parts = s.split(sep) if sep else [s]
    return tuple(sorted({p.strip() for p in parts if p.strip()}))


def normalize_cpc(code):
    """Upper-case and drop internal whitespace: 'h01m 10/0562' -> 'H01M10/0562'."""
    return re.sub(r"\s+", "", str(code)).upper()


def cpc_level(code, level):
    """Roll a normalized CPC code up: subclass 'H01M', main group 'H01M10', or full."""
    if level == "subclass":
        return code[:4]
    if level == "group":
        return code.split("/", 1)[0]
    return code


def parse_year(raw):
    """First 4-digit year (1800-2100) in the cell; None if absent. Accepts
    '2021', '2021.0' and dates such as '2021-03-04'."""
    if raw is None:
        return None
    m = re.search(r"(?<!\d)(1[89]\d\d|20\d\d|2100)(?!\d)", str(raw))
    return int(m.group(1)) if m else None


def parse_int(raw):
    """Non-negative integer or None (blank / non-numeric)."""
    s = "" if raw is None else str(raw).strip()
    if not s:
        return None
    try:
        v = int(float(s))
    except ValueError:
        return None
    return v if v >= 0 else None


def parse_rows(dicts):
    """Raw row-dicts -> list of family dicts:
    {assignee, year, cpcs (normalized tuple), jurisdictions, family_size, citations}.
    Missing assignee -> '(unknown)'; unparsable year/size/citations -> None."""
    fams = []
    for i, row in enumerate(dicts, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"row {i}: expected an object/dict, got {type(row).__name__}")
        akey = _find_key(row, ASSIGNEE_KEYS)
        ykey = _find_key(row, YEAR_KEYS)
        ckey = _find_key(row, CPC_KEYS)
        if akey is None or ykey is None or ckey is None:
            raise ValueError(
                f"row {i}: need columns assignee {ASSIGNEE_KEYS[:3]}, priority_year "
                f"{YEAR_KEYS[:3]} and cpc {CPC_KEYS[:2]}; got keys {sorted(map(str, row))}"
            )
        name = " ".join(str(row[akey] or "").split()) or UNKNOWN
        jkey = _find_key(row, JURIS_KEYS)
        skey = _find_key(row, SIZE_KEYS)
        tkey = _find_key(row, CITE_KEYS)
        fams.append({
            "assignee": name,
            "year": parse_year(row[ykey]),
            "cpcs": tuple(sorted({normalize_cpc(c) for c in split_multi(row[ckey])})),
            "jurisdictions": tuple(sorted({j.upper() for j in split_multi(row[jkey])})) if jkey else (),
            "family_size": parse_int(row[skey]) if skey else None,
            "citations": parse_int(row[tkey]) if tkey else None,
        })
    if not fams:
        raise ValueError("no family rows found")
    return fams


def parse_text(text, is_json):
    if is_json:
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("families", data.get("rows", []))
        return parse_rows(data)
    return parse_rows(list(csv.DictReader(io.StringIO(text))))


def load_file(path):
    """Load families from CSV or JSON (by extension; '-' = stdin, sniffed)."""
    if path == "-":
        text = sys.stdin.read()
        return parse_text(text, text.lstrip().startswith(("[", "{")))
    with open(path, newline="", encoding="utf-8") as fh:
        return parse_text(fh.read(), path.lower().endswith(".json"))


# --- helpers -----------------------------------------------------------------


def sorted_counts(counter):
    """Counter -> [(name, count)] sorted count desc, then name asc (deterministic)."""
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))


def pct(part, whole):
    return 100.0 * part / whole if whole else 0.0


def r4(x):
    return None if x is None else round(x, 4)


def reference_year(fams, asof=None):
    years = [f["year"] for f in fams if f["year"] is not None]
    if asof is not None:
        return asof
    return max(years) if years else None


# --- concentration (SKILL.md step 2) -----------------------------------------


def hhi(counts):
    """HHI = sum of squared percentage shares (0-10,000)."""
    total = sum(counts)
    return sum((100.0 * c / total) ** 2 for c in counts) if total else 0.0


def cr(counts, k=4):
    """Top-k concentration ratio in percent (counts need not be sorted)."""
    total = sum(counts)
    return pct(sum(sorted(counts, reverse=True)[:k]), total)


def hhi_band(h, scheme):
    lo, hi = HHI_BANDS[scheme]
    if h > hi:
        return "highly concentrated"
    if h >= lo:
        return "moderately concentrated"
    return "unconcentrated"


def concentration_verdict(h, top_share):
    """SKILL.md step 2 read: 'concentrated' when the 2023 band is highly
    concentrated or one holder has >= 25%; else the 2023 band, 'crowded / open'
    for unconcentrated."""
    band = hhi_band(h, "2023")
    if band == "highly concentrated" or top_share >= TOP_SHARE_CONCENTRATED:
        return "concentrated"
    if band == "moderately concentrated":
        return "moderately concentrated"
    return "crowded / open"


def concentration(fams, top=10):
    n = len(fams)
    counts = sorted_counts(Counter(f["assignee"] for f in fams))
    values = [c for _, c in counts]
    h = hhi(values)
    top_share = pct(values[0], n) if values else 0.0
    singles = [name for name, c in counts if c == 1]
    sizes = [f["family_size"] for f in fams if f["family_size"] is not None]
    cites = [f["citations"] for f in fams if f["citations"] is not None]
    rows, cum = [], 0.0
    for rank, (name, c) in enumerate(counts[:top], start=1):
        cum += pct(c, n)
        own = [f for f in fams if f["assignee"] == name]
        own_sizes = [f["family_size"] for f in own if f["family_size"] is not None]
        own_cites = [f["citations"] for f in own if f["citations"] is not None]
        rows.append({
            "rank": rank, "assignee": name, "families": c,
            "share_pct": r4(pct(c, n)), "cum_share_pct": r4(cum),
            "mean_family_size": r4(sum(own_sizes) / len(own_sizes)) if own_sizes else None,
            "citations_per_family": r4(sum(own_cites) / len(own_cites)) if own_cites else None,
        })
    return {
        "families": n,
        "assignees": len(counts),
        "hhi": r4(h),
        "hhi_band_2023": hhi_band(h, "2023"),
        "hhi_band_2010": hhi_band(h, "2010"),
        "numbers_equivalent": r4(10000.0 / h) if h else None,
        "cr4_pct": r4(cr(values, 4)),
        "top_share_pct": r4(top_share),
        "top_assignee": counts[0][0] if counts else None,
        "single_family_assignees": len(singles),
        "single_family_share_pct": r4(pct(len(singles), n)),
        "verdict": concentration_verdict(h, top_share),
        "has_family_size": bool(sizes),
        "has_citations": bool(cites),
        "top": rows,
    }


def _num(x, fmt="{:.1f}"):
    return "-" if x is None else fmt.format(x)


def _fam(n):
    return f"{n} family" if n == 1 else f"{n} families"


def fmt_concentration(res):
    out = [f"Assignee concentration (N = {res['families']} families, {res['assignees']} assignees)"]
    out.append(f"  HHI: {res['hhi']:,.0f}  (sum of squared % shares; 0-10,000)")
    out.append(f"    {HHI_BAND_LABEL['2023']}: {res['hhi_band_2023']}")
    out.append(f"    {HHI_BAND_LABEL['2010']}: {res['hhi_band_2010']}")
    if res["numbers_equivalent"] is not None:
        out.append(f"    numbers-equivalent (10,000 / HHI): {res['numbers_equivalent']:.1f} equal-sized holders")
    out.append(f"  CR4 (top-4 share): {res['cr4_pct']:.1f}%   top holder: {res['top_assignee']} {res['top_share_pct']:.1f}%")
    out.append(f"  Long tail: {res['single_family_assignees']} of {res['assignees']} assignees hold a single family "
               f"({res['single_family_share_pct']:.1f}% of families)")
    out.append(f"  Read (SKILL.md step 2): {res['verdict']} -- HHI bands are merger-review yardsticks used "
               "descriptively; concentrated = 2023 band highly concentrated or one holder >= 25%")
    hdr = f"  {'rank':>4}  {'assignee':<28}{'families':>9}{'share':>8}{'cum.':>8}"
    if res["has_family_size"]:
        hdr += f"{'fam.size':>10}"
    if res["has_citations"]:
        hdr += f"{'cites/fam':>11}"
    out.append(hdr)
    for r in res["top"]:
        line = f"  {r['rank']:>4}  {r['assignee'][:28]:<28}{r['families']:>9}{r['share_pct']:>7.1f}%{r['cum_share_pct']:>7.1f}%"
        if res["has_family_size"]:
            line += f"{_num(r['mean_family_size']):>10}"
        if res["has_citations"]:
            line += f"{_num(r['citations_per_family']):>11}"
        out.append(line)
    if res["assignees"] > len(res["top"]):
        out.append(f"  ({res['assignees'] - len(res['top'])} more assignees not shown)")
    return out


# --- filing velocity (SKILL.md step 3) ---------------------------------------


def year_series(fams, asof=None):
    """Contiguous [(year, families)] from the earliest priority year to max(asof, latest)."""
    years = [f["year"] for f in fams if f["year"] is not None]
    if not years:
        return []
    c = Counter(years)
    last = max(years) if asof is None else max(asof, max(years))
    return [(y, c.get(y, 0)) for y in range(min(years), last + 1)]


def yoy(series):
    """Year-over-year growth in % per year (None where the previous year is 0 / absent)."""
    out = [None]
    for (_, prev), (_, cur) in zip(series, series[1:]):
        out.append(pct(cur - prev, prev) if prev else None)
    return out


def cagr(series):
    """CAGR between the first and last non-zero years: (last/first)^(1/years) - 1.
    Returns dict(first_year, first, last_year, last, years, cagr_pct) or None."""
    nz = [(y, c) for y, c in series if c > 0]
    if len(nz) < 2:
        return None
    (y0, c0), (y1, c1) = nz[0], nz[-1]
    span = y1 - y0
    return {"first_year": y0, "first": c0, "last_year": y1, "last": c1, "years": span,
            "cagr_pct": r4(((c1 / c0) ** (1.0 / span) - 1.0) * 100.0)}


def rolling_mean(series, window=3):
    """Trailing rolling mean; None until the window is full."""
    vals = [c for _, c in series]
    return [None if i + 1 < window else sum(vals[i + 1 - window:i + 1]) / window
            for i in range(len(vals))]


def trend_label(series, asof, recent):
    """Mean families/yr in the last `recent` years vs the (up to) `recent` observed
    years before them. Returns (label, detail dict)."""
    d = dict(series)
    win = [y for y in range(asof - recent + 1, asof + 1)]
    prior = [y for y in range(asof - 2 * recent + 1, asof - recent + 1) if y in d]
    mean_recent = sum(d.get(y, 0) for y in win) / recent
    if not prior:
        return "n/a (too few years)", {"recent_mean": r4(mean_recent), "prior_mean": None, "ratio": None}
    if mean_recent == 0 and max(y for y, c in series if c > 0) < win[0]:
        return (f"n/a (no dated families in {win[0]}-{win[-1]}; latest dated year is before the window -- "
                "check --asof and the publication lag)"), {"recent_mean": 0.0, "prior_mean": None, "ratio": None}
    mean_prior = sum(d[y] for y in prior) / len(prior)
    if mean_prior == 0:
        label = "accelerating (from zero)" if mean_recent > 0 else "flat (no filings)"
        ratio = None
    else:
        ratio = mean_recent / mean_prior
        label = "accelerating" if ratio >= TREND_ACCEL else ("declining" if ratio <= TREND_DECLINE else "flat")
    return label, {"recent_years": [win[0], win[-1]], "prior_years": [prior[0], prior[-1]],
                   "recent_mean": r4(mean_recent), "prior_mean": r4(mean_prior), "ratio": r4(ratio)}


def velocity(fams, recent=3, asof=None):
    dated = [f for f in fams if f["year"] is not None]
    ref = reference_year(fams, asof)
    series = year_series(fams, asof)
    res = {"families_dated": len(dated), "families_undated": len(fams) - len(dated),
           "reference_year": ref, "recent_window": recent, "warning": LAG_WARNING}
    if not series:
        res.update({"years": [], "cagr": None, "peak": None, "recent": None, "trend": "n/a (no dated families)"})
        return res
    growth, roll = yoy(series), rolling_mean(series, 3)
    lag_years = LAG_MONTHS // 12
    rows = [{"year": y, "families": c, "yoy_pct": r4(g), "rolling3": r4(m),
             "lag_flag": y > ref - lag_years}
            for (y, c), g, m in zip(series, growth, roll)]
    peak = max(series, key=lambda yc: (yc[1], -yc[0]))
    win_lo = ref - recent + 1
    n_recent = sum(c for y, c in series if win_lo <= y <= ref)
    label, detail = trend_label(series, ref, recent)
    res.update({
        "years": rows,
        "cagr": cagr(series),
        "peak": {"year": peak[0], "families": peak[1]},
        "recent": {"years": [win_lo, ref], "families": n_recent, "share_pct": r4(pct(n_recent, len(dated)))},
        "trend": label, "trend_detail": detail,
        "last_yoy_pct": rows[-1]["yoy_pct"],
    })
    return res


def fmt_velocity(res):
    out = [f"Filing velocity by priority year ({res['families_dated']} dated families, "
           f"{res['families_undated']} undated; reference year {res['reference_year']})"]
    if not res["years"]:
        out.append("  no dated families")
        out.append("  " + LAG_WARNING)
        return out
    out.append(f"  {'year':<7}{'families':>9}{'YoY':>9}{'3-yr mean':>11}")
    for r in res["years"]:
        y = f"{r['year']}{'*' if r['lag_flag'] else ''}"
        g = "n/a" if r["yoy_pct"] is None else f"{r['yoy_pct']:+.1f}%"
        m = "-" if r["rolling3"] is None else f"{r['rolling3']:.1f}"
        out.append(f"  {y:<7}{r['families']:>9}{g:>9}{m:>11}")
    out.append(f"  * within {LAG_MONTHS} months of the reference year: likely under-counted (see warning)")
    out.append(f"  Peak year: {res['peak']['year']} ({_fam(res['peak']['families'])})")
    c = res["cagr"]
    if c is None:
        out.append("  CAGR: n/a (fewer than two non-zero years)")
    else:
        out.append(f"  CAGR {c['first_year']}->{c['last_year']} ({c['first']} -> {c['last']} over {c['years']} years): "
                   f"{c['cagr_pct']:+.1f}%/yr")
    rc = res["recent"]
    out.append(f"  Last {res['recent_window']} years ({rc['years'][0]}-{rc['years'][1]}): {rc['families']} of "
               f"{res['families_dated']} dated families = {rc['share_pct']:.1f}%")
    d = res["trend_detail"]
    if d.get("prior_mean") is None:
        out.append(f"  Trend: {res['trend']}")
    else:
        ratio = "n/a" if d["ratio"] is None else f"{d['ratio']:.2f}"
        out.append(f"  Trend: {res['trend']} (mean {d['recent_mean']:.1f}/yr in {d['recent_years'][0]}-{d['recent_years'][1]}"
                   f" vs {d['prior_mean']:.1f}/yr in {d['prior_years'][0]}-{d['prior_years'][1]}; ratio {ratio}; "
                   f">={TREND_ACCEL:.2f} accelerating, <={TREND_DECLINE:.2f} declining)")
    if res["last_yoy_pct"] is not None:
        out.append(f"  Latest year-over-year: {res['last_yoy_pct']:+.1f}%")
    out.append("  " + LAG_WARNING)
    return out


# --- CPC clustering + white-space (SKILL.md steps 4-5) -----------------------


def family_cpcs(fam, level):
    return tuple(sorted({cpc_level(c, level) for c in fam["cpcs"]}))


def cpc_counts(fams, level="full"):
    c = Counter()
    for f in fams:
        c.update(family_cpcs(f, level))
    return sorted_counts(c)


def whitespace(fams, level="full", k=8, m=6, low=1, pairs=10):
    n = len(fams)
    counts = cpc_counts(fams, level)
    coded = [f for f in fams if f["cpcs"]]
    top_cpcs = [c for c, _ in counts[:k]]
    top_assg = [a for a, _ in sorted_counts(Counter(f["assignee"] for f in fams))[:m]]
    cells = {(c, a): 0 for c in top_cpcs for a in top_assg}
    for f in fams:
        if f["assignee"] in top_assg:
            for c in family_cpcs(f, level):
                if (c, f["assignee"]) in cells:
                    cells[(c, f["assignee"])] += 1
    cpc_total = dict(counts)
    assg_total = Counter(f["assignee"] for f in fams)
    matrix = [[cells[(c, a)] for a in top_assg] for c in top_cpcs]
    empty, lowc = [], []
    for c in top_cpcs:
        for a in top_assg:
            v = cells[(c, a)]
            entry = {"cpc": c, "cpc_families": cpc_total[c], "assignee": a,
                     "assignee_families": assg_total[a], "families": v}
            if v == 0:
                empty.append(entry)
            elif v <= low:
                lowc.append(entry)
    def cell_key(e):   # densest CPC first, then largest assignee, then names
        return (-e["cpc_families"], -e["assignee_families"], e["cpc"], e["assignee"])
    empty.sort(key=cell_key)
    lowc.sort(key=cell_key)
    sparse = [{"cpc": c, "families": v, "assignees": sorted({f["assignee"] for f in fams if c in family_cpcs(f, level)})}
              for c, v in counts if v <= low]
    pair_counter = Counter()
    for f in fams:
        cs = family_cpcs(f, level)
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                pair_counter[(cs[i], cs[j])] += 1
    co = [{"pair": list(p), "families": v} for p, v in
          sorted(pair_counter.items(), key=lambda kv: (-kv[1], kv[0]))[:pairs]]
    breadth = Counter()
    seen = {}
    for f in fams:
        seen.setdefault(f["assignee"], set()).update(family_cpcs(f, level))
    for a, s in seen.items():
        breadth[a] = len(s)
    breadth_rows = [{"assignee": a, "distinct_cpcs": breadth[a], "families": assg_total[a]} for a in top_assg]
    return {
        "level": level, "families": n, "families_with_cpc": len(coded),
        "distinct_cpcs": len(counts),
        "cpc_counts": [{"cpc": c, "families": v, "share_pct": r4(pct(v, n))} for c, v in counts[:k]],
        "matrix": {"cpcs": top_cpcs, "assignees": top_assg, "cells": matrix},
        "empty_cells": empty, "low_cells": lowc, "low_threshold": low,
        "sparse_cpcs": sparse,
        "co_occurrence": co,
        "breadth": breadth_rows,
        "breadth_all": [{"assignee": a, "distinct_cpcs": breadth[a]} for a, _ in sorted_counts(assg_total)],
    }


def fmt_cpc_counts(res):
    out = [f"Dense sub-areas (CPC/IPC, level {res['level']}; {res['families_with_cpc']} of {res['families']} "
           f"families carry codes; {res['distinct_cpcs']} distinct)"]
    for r in res["cpc_counts"]:
        out.append(f"  {r['cpc']:<16}{r['families']:>6}  ({r['share_pct']:.1f}% of families)")
    if res["distinct_cpcs"] > len(res["cpc_counts"]):
        out.append(f"  ({res['distinct_cpcs'] - len(res['cpc_counts'])} more codes not shown)")
    return out


def _abbrev(name, width):
    return name if len(name) <= width else name[:width - 1] + "~"


def fmt_whitespace(res):
    mx = res["matrix"]
    out = [f"CPC x assignee matrix (top {len(mx['cpcs'])} CPCs by families x top {len(mx['assignees'])} assignees; "
           "cell = families of that assignee carrying that code)"]
    w = 12
    hdr = f"  {'CPC':<16}{'total':>6} |" + "".join(f"{_abbrev(a, w):>{w + 1}}" for a in mx["assignees"])
    out.append(hdr)
    totals = {r["cpc"]: r["families"] for r in res["cpc_counts"]}
    for c, row in zip(mx["cpcs"], mx["cells"]):
        out.append(f"  {c:<16}{totals[c]:>6} |" + "".join(f"{v:>{w + 1}}" for v in row))
    if any(len(a) > w for a in mx["assignees"]):
        out.append("  columns: " + "; ".join(f"{_abbrev(a, w)} = {a}" for a in mx["assignees"] if len(a) > w))
    out.append("Candidate white space (SKILL.md step 5 -- pair with a demand signal before calling it an opportunity):")
    by_cpc = {}
    for e in res["empty_cells"]:
        by_cpc.setdefault(e["cpc"], ([], []))[0].append(e["assignee"])
    for e in res["low_cells"]:
        by_cpc.setdefault(e["cpc"], ([], []))[1].append(e["assignee"])
    if not by_cpc:
        out.append("  none: every top assignee holds > "
                   f"{res['low_threshold']} families in every top CPC")
    for c in mx["cpcs"]:
        if c not in by_cpc:
            continue
        emp, lo = by_cpc[c]
        parts = []
        if emp:
            parts.append("empty for " + ", ".join(emp))
        if lo:
            parts.append(f"<= {res['low_threshold']} for " + ", ".join(lo))
        out.append(f"  {c} ({_fam(totals[c])}): " + "; ".join(parts))
    if res["sparse_cpcs"]:
        out.append(f"Sparse codes overall (<= {_fam(res['low_threshold'])}; adjacent near-empty classes):")
        for s in res["sparse_cpcs"][:10]:
            out.append(f"  {s['cpc']}: {s['families']} ({', '.join(s['assignees'])})")
        if len(res["sparse_cpcs"]) > 10:
            out.append(f"  ({len(res['sparse_cpcs']) - 10} more sparse codes not shown)")
    out.append("CPC co-occurrence (families carrying both codes; top pairs):")
    if not res["co_occurrence"]:
        out.append("  none (no family carries two or more codes)")
    for p in res["co_occurrence"]:
        out.append(f"  {p['pair'][0]} + {p['pair'][1]}: {p['families']}")
    out.append("CPC breadth (distinct codes per assignee, top assignees):")
    for b in res["breadth"]:
        out.append(f"  {b['assignee']:<28}{b['distinct_cpcs']:>4} codes over {b['families']} families")
    return out


# --- entrants / dormant assignees ------------------------------------------


def entry(fams, recent=3, dormant=4, asof=None):
    ref = reference_year(fams, asof)
    per = {}
    for f in fams:
        d = per.setdefault(f["assignee"], {"families": 0, "years": []})
        d["families"] += 1
        if f["year"] is not None:
            d["years"].append(f["year"])
    rows = []
    for name in sorted(per, key=lambda a: (-per[a]["families"], a)):
        d = per[name]
        first = min(d["years"]) if d["years"] else None
        last = max(d["years"]) if d["years"] else None
        if ref is None or first is None:
            status = "unknown"
        elif last <= ref - dormant:
            status = "dormant"
        elif first >= ref - recent + 1:
            status = "entrant"
        else:
            status = "established"
        rows.append({"assignee": name, "families": d["families"], "first_year": first,
                     "last_year": last, "status": status})
    summary = Counter(r["status"] for r in rows)
    return {
        "reference_year": ref, "recent_window": recent, "dormant_window": dormant,
        "entrant_from_year": None if ref is None else ref - recent + 1,
        "dormant_last_year_at_most": None if ref is None else ref - dormant,
        "assignees": rows,
        "counts": {s: summary.get(s, 0) for s in ("entrant", "established", "dormant", "unknown")},
        "entrants": [r["assignee"] for r in rows if r["status"] == "entrant"],
        "dormant": [r["assignee"] for r in rows if r["status"] == "dormant"],
    }


def fmt_entry(res, top=None):
    ref = res["reference_year"]
    out = [f"Assignee entry / dormancy (reference year {ref}; entrant = first priority year >= "
           f"{res['entrant_from_year']}, i.e. within the last {res['recent_window']} years; dormant = no family "
           f"since {res['dormant_last_year_at_most']}, i.e. none in the last {res['dormant_window']} years)"]
    c = res["counts"]
    out.append(f"  entrants {c['entrant']} | established {c['established']} | dormant {c['dormant']}"
               + (f" | undated {c['unknown']}" if c["unknown"] else ""))
    out.append(f"  {'assignee':<28}{'families':>9}{'first':>7}{'last':>6}  status")
    rows = res["assignees"] if top is None else res["assignees"][:top]
    for r in rows:
        f0 = "-" if r["first_year"] is None else str(r["first_year"])
        f1 = "-" if r["last_year"] is None else str(r["last_year"])
        out.append(f"  {r['assignee'][:28]:<28}{r['families']:>9}{f0:>7}{f1:>6}  {r['status']}")
    if top is not None and len(res["assignees"]) > top:
        out.append(f"  ({len(res['assignees']) - top} more assignees not shown)")
    if res["entrants"]:
        out.append("  Entrants: " + ", ".join(res["entrants"]))
    if res["dormant"]:
        out.append("  Dormant: " + ", ".join(res["dormant"]))
    return out


# --- cluster summary + data completeness -------------------------------------


def _dup_key(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def cluster_summary(fams, level="full"):
    years = [f["year"] for f in fams if f["year"] is not None]
    jur = Counter()
    for f in fams:
        jur.update(f["jurisdictions"])
    sizes = [f["family_size"] for f in fams if f["family_size"] is not None]
    cites = [f["citations"] for f in fams if f["citations"] is not None]
    spell = {}
    for f in fams:
        spell.setdefault(_dup_key(f["assignee"]), set()).add(f["assignee"])
    dups = [sorted(v) for k, v in sorted(spell.items()) if len(v) > 1]
    return {
        "families": len(fams),
        "assignees": len({f["assignee"] for f in fams}),
        "years": [min(years), max(years)] if years else None,
        "distinct_cpcs": len(cpc_counts(fams, level)),
        "cpc_level": level,
        "jurisdictions": [{"code": c, "families": v} for c, v in sorted_counts(jur)],
        "family_size_mean": r4(sum(sizes) / len(sizes)) if sizes else None,
        "citations_mean": r4(sum(cites) / len(cites)) if cites else None,
        "completeness": {
            "dated": len(years), "with_cpc": sum(1 for f in fams if f["cpcs"]),
            "with_jurisdictions": sum(1 for f in fams if f["jurisdictions"]),
            "with_family_size": len(sizes), "with_citations": len(cites),
            "unknown_assignee": sum(1 for f in fams if f["assignee"] == UNKNOWN),
            "possible_duplicate_spellings": dups,
        },
    }


def fmt_cluster(res):
    yrs = "no dated families" if res["years"] is None else f"priority years {res['years'][0]}-{res['years'][1]}"
    out = [f"  {res['families']} families | {res['assignees']} assignees | {yrs} | "
           f"{res['distinct_cpcs']} distinct CPC codes (level {res['cpc_level']})"]
    if res["jurisdictions"]:
        out.append("  jurisdictions (families filed in): " +
                   ", ".join(f"{j['code']} {j['families']}" for j in res["jurisdictions"][:10]))
    extras = []
    if res["family_size_mean"] is not None:
        extras.append(f"mean family size {res['family_size_mean']:.1f}")
    if res["citations_mean"] is not None:
        extras.append(f"mean forward citations {res['citations_mean']:.1f}")
    if extras:
        out.append("  " + " | ".join(extras))
    return out


def fmt_completeness(res):
    n, c = res["families"], res["completeness"]
    out = [f"  dated {c['dated']}/{n} | with CPC {c['with_cpc']}/{n} | with jurisdictions {c['with_jurisdictions']}/{n}"
           f" | family_size {c['with_family_size']}/{n} | citations {c['with_citations']}/{n}"
           f" | unknown assignee {c['unknown_assignee']}"]
    if c["possible_duplicate_spellings"]:
        out.append("  possible duplicate assignee spellings (clean/group before trusting shares, WIPO 2015 s8.3.1): "
                   + "; ".join(" / ".join(g) for g in c["possible_duplicate_spellings"]))
    else:
        out.append("  possible duplicate assignee spellings: none detected")
    out.append("  Confidence itself is the analyst's call (SKILL.md step 6): how the cluster was assembled and "
               "how complete CPC coverage of recent filings is.")
    return out


# --- report ------------------------------------------------------------------


def report(fams, scope=None, recent=3, dormant=4, asof=None, top=10, level="full", k=8, m=6, low=1, pairs=10):
    return {
        "scope": scope,
        "cluster": cluster_summary(fams, level),
        "concentration": concentration(fams, top),
        "velocity": velocity(fams, recent, asof),
        "entry": entry(fams, recent, dormant, asof),
        "whitespace": whitespace(fams, level, k, m, low, pairs),
    }


def fmt_report(res):
    out = [f"Patent landscape read -- {res['scope'] or 'cluster'} (numbers for the SKILL.md output template)"]
    out.append("== Cluster ==")
    out += fmt_cluster(res["cluster"])
    out.append("== Top assignees ==")
    out += fmt_concentration(res["concentration"])
    out.append("== Filing velocity ==")
    out += fmt_velocity(res["velocity"])
    out.append("== Entrants and dormant assignees ==")
    out += fmt_entry(res["entry"], top=len(res["concentration"]["top"]))
    out.append("== Dense sub-areas (CPC/IPC) ==")
    out += fmt_cpc_counts(res["whitespace"])
    out.append("== White-space ==")
    out += fmt_whitespace(res["whitespace"])
    out.append("== Confidence inputs (data completeness) ==")
    out += fmt_completeness(res["cluster"])
    return out


# --- CLI ---------------------------------------------------------------------


def get_data(args, parser):
    if getattr(args, "demo", False):
        return parse_rows(demo_rows())
    if getattr(args, "file", None):
        try:
            return load_file(args.file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(f"could not load {args.file}: {exc}")
    parser.error("pass --file PATH (or '-' for stdin) or --demo")


def emit(result, lines, as_json):
    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("\n".join(lines))


def build_parser():
    parser = argparse.ArgumentParser(
        description="Patent-landscape arithmetic over one row per patent family: assignee "
        "concentration (HHI, CR4), filing velocity (YoY, CAGR), CPC x assignee white-space "
        "matrix, and entrant/dormant assignees. Stdlib only, deterministic."
    )
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", dest="demo_report", action="store_true",
                        help="shortcut for 'report --demo' (synthetic 42-family cluster)")
    sub = parser.add_subparsers(dest="command")

    def common(p, *groups):
        p.add_argument("--file", help="CSV or JSON of families (assignee, priority_year, cpc, ...); '-' = stdin")
        p.add_argument("--demo", action="store_true", help="use the built-in synthetic cluster")
        p.add_argument("--json", action="store_true", help="emit the result as JSON")
        p.add_argument("--min-families", type=int, default=5,
                       help="refuse (exit 2) below this many families (default 5, SKILL.md); 0 disables")
        if "time" in groups:
            p.add_argument("--recent", type=int, default=3, help="window in years for 'recent' (default 3)")
            p.add_argument("--asof", type=int, help="reference year (default: latest priority year in the data)")
        if "entry" in groups:
            p.add_argument("--dormant", type=int, default=4,
                           help="dormant = no family in the last N years (default 4)")
        if "conc" in groups:
            p.add_argument("--top", type=int, default=10, help="rows in the top-assignee table (default 10)")
        if "ws" in groups:
            p.add_argument("--cpc", type=int, default=8, help="top-K CPC codes in the matrix (default 8)")
            p.add_argument("--assignees", type=int, default=6, help="top-M assignees in the matrix (default 6)")
            p.add_argument("--low", type=int, default=1, help="cells with <= this many families are 'low' (default 1)")
            p.add_argument("--pairs", type=int, default=10, help="co-occurrence pairs to list (default 10)")
            p.add_argument("--level", choices=LEVELS, default="full",
                           help="CPC roll-up: full code, main group (H01M10) or subclass (H01M)")

    common(sub.add_parser("concentrate", help="assignee shares, HHI (2010 + 2023 bands), CR4, long tail"), "conc")
    common(sub.add_parser("velocity", help="families per priority year, YoY, CAGR, rolling mean, peak, recent share"), "time")
    common(sub.add_parser("whitespace", help="CPC x assignee matrix, empty/low cells, co-occurrence, breadth"), "ws")
    common(sub.add_parser("entry", help="first/last priority year per assignee -> entrant / established / dormant"),
           "time", "entry")
    p = sub.add_parser("report", help="all of the above in the SKILL.md output-template order")
    common(p, "time", "entry", "conc", "ws")
    p.add_argument("--scope", help="cluster label printed in the report header")
    return parser


def _validate(args, parser):
    for name in ("recent", "dormant", "top", "cpc", "assignees", "pairs"):
        if getattr(args, name, 1) < 1:
            parser.error(f"--{name} must be >= 1")
    if getattr(args, "low", 0) < 0 or args.min_families < 0:
        parser.error("--low and --min-families must be >= 0")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo_report and not args.command:
        args = parser.parse_args(["report", "--demo"])
    if not args.command:
        parser.error("choose a command: report | concentrate | velocity | whitespace | entry  (or --selftest)")
    _validate(args, parser)
    fams = get_data(args, parser)
    if len(fams) < args.min_families:
        print(f"cluster too small: {len(fams)} families (< {args.min_families}). SKILL.md: say so rather than "
              "force a landscape read; use analyze-patent-claims per filing (override with --min-families 0).")
        return 2
    if args.command == "concentrate":
        res = concentration(fams, args.top)
        emit(res, fmt_concentration(res), args.json)
    elif args.command == "velocity":
        res = velocity(fams, args.recent, args.asof)
        emit(res, fmt_velocity(res), args.json)
    elif args.command == "whitespace":
        res = whitespace(fams, args.level, args.cpc, args.assignees, args.low, args.pairs)
        emit(res, fmt_cpc_counts(res) + fmt_whitespace(res), args.json)
    elif args.command == "entry":
        res = entry(fams, args.recent, args.dormant, args.asof)
        emit(res, fmt_entry(res), args.json)
    else:
        res = report(fams, args.scope, args.recent, args.dormant, args.asof, args.top,
                     args.level, args.cpc, args.assignees, args.low, args.pairs)
        emit(res, fmt_report(res), args.json)
    return 0


# --- selftest ----------------------------------------------------------------


def run_selftest():
    """Hand-verified checks: every expected value below was worked out by hand,
    using the definitions in the module docstring, before being encoded here."""
    checks = []

    def check(name, ok, detail=""):
        checks.append(bool(ok))
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    # 1. HHI of shares 50/30/20: 2500 + 900 + 400 = 3,800 (highly concentrated in both schemes).
    check("HHI of shares 50/30/20 = 3,800", abs(hhi([5, 3, 2]) - 3800.0) < 1e-9, f"{hhi([5, 3, 2]):.1f}")
    check("HHI single holder = 10,000", hhi([7]) == 10000.0)
    check("HHI 3,800 -> highly concentrated (2023 and 2010)",
          hhi_band(3800, "2023") == "highly concentrated" and hhi_band(3800, "2010") == "highly concentrated")
    # 2. Counts 4,3,2,1,1,1 (N=12): shares 33.33/25/16.67/8.33x3 -> HHI 1111.1+625+277.8+208.3 = 2,222.2;
    #    CR4 = (4+3+2+1)/12 = 83.3%. Bands diverge: 2023 highly (>1,800), 2010 moderately (1,500-2,500).
    h6 = hhi([4, 3, 2, 1, 1, 1])
    check("HHI of 4/3/2/1/1/1 = 2,222.2", abs(h6 - 2222.2222) < 1e-3, f"{h6:.4f}")
    check("CR4 of 4/3/2/1/1/1 = 83.3%", abs(cr([1, 4, 1, 3, 2, 1], 4) - 83.3333) < 1e-3)
    check("HHI 2,222 -> 2023 highly / 2010 moderately",
          hhi_band(h6, "2023") == "highly concentrated" and hhi_band(h6, "2010") == "moderately concentrated")
    check("band edges: 1,000 and 1,800 are 'moderately' (2023); 1,500 and 2,500 'moderately' (2010); 999 unconcentrated",
          hhi_band(1000, "2023") == "moderately concentrated" and hhi_band(1800, "2023") == "moderately concentrated"
          and hhi_band(1500, "2010") == "moderately concentrated" and hhi_band(2500, "2010") == "moderately concentrated"
          and hhi_band(999, "2023") == "unconcentrated" and hhi_band(1499, "2010") == "unconcentrated")
    check("verdict: top holder 25% forces 'concentrated' even at HHI 1,750",
          concentration_verdict(1750, 25.0) == "concentrated"
          and concentration_verdict(1750, 20.0) == "moderately concentrated"
          and concentration_verdict(900, 20.0) == "crowded / open")

    # 3. CAGR 10 -> 40 over 3 years = 4^(1/3) - 1 = 58.74%; leading/trailing zero years ignored.
    series = [(2019, 0), (2020, 10), (2021, 20), (2022, 25), (2023, 40), (2024, 0)]
    c = cagr(series)
    check("CAGR of 10 -> 40 over 3 years = 58.7%", c["years"] == 3 and abs(c["cagr_pct"] - 58.74) < 0.01,
          f"{c['cagr_pct']:.2f}% ({c['first_year']}-{c['last_year']})")
    check("YoY: 2021 +100%, 2022 +25%, 2023 +60%; 2020 n/a (previous year 0)",
          [None if g is None else round(g, 6) for g in yoy(series)] == [None, None, 100.0, 25.0, 60.0, -100.0])
    rm = rolling_mean(series, 3)
    check("3-yr rolling mean: 2022 = 18.33, 2023 = 28.33", abs(rm[3] - 55 / 3) < 1e-9 and abs(rm[4] - 85 / 3) < 1e-9
          and rm[0] is None and rm[1] is None)
    check("CAGR undefined with < 2 non-zero years", cagr([(2020, 0), (2021, 5)]) is None)

    # 4. Pipeline on a 12-family mini set (built by hand):
    #    Alpha 5 (2019-2023), Beta 3 (2020, 2021, 2023), Gamma 2 (2023, 2023), Delta 1 (2018), Epsilon 1 (2019).
    mini = [
        {"assignee": "Alpha", "priority_year": 2019, "cpc": "H01M10/0562"},
        {"assignee": "Alpha", "priority_year": 2020, "cpc": "H01M10/0562;H01M4/04"},
        {"assignee": "Alpha", "priority_year": 2021, "cpc": "H01M10/0562"},
        {"assignee": "Alpha", "priority_year": 2022, "cpc": "H01M10/0562;H01M4/04"},
        {"assignee": "Alpha", "priority_year": 2023, "cpc": "h01m 10/0562"},          # normalized
        {"assignee": "Beta", "priority_year": 2020, "cpc": "H01M10/0562"},
        {"assignee": "Beta", "priority_year": 2021, "cpc": "H01M10/0562;H01M4/366"},
        {"assignee": "Beta", "priority_year": "2023-05-01", "cpc": "H01M10/0562"},     # date -> year
        {"assignee": "Gamma", "priority_year": 2023, "cpc": "H01M4/04"},
        {"assignee": " Gamma ", "priority_year": 2023, "cpc": "H01M4/04"},              # trimmed
        {"assignee": "Delta", "priority_year": 2018, "cpc": "H01M10/0562"},
        {"assignee": "Epsilon", "priority_year": 2019, "cpc": ""},                       # no CPC
    ]
    fams = parse_rows(mini)
    check("parse: 12 families, 5 assignees, 'h01m 10/0562' normalized, date parsed",
          len(fams) == 12 and len({f["assignee"] for f in fams}) == 5
          and fams[4]["cpcs"] == ("H01M10/0562",) and fams[7]["year"] == 2023 and fams[11]["cpcs"] == ())
    conc = concentration(fams, top=3)
    # shares: 41.67, 25, 16.67, 8.33, 8.33 -> HHI 1736.1+625+277.8+69.4+69.4 = 2,777.8; CR4 = 11/12 = 91.7%
    check("mini: HHI 2,777.8, CR4 91.7%, 2 single-family assignees, top holder Alpha 41.7% -> concentrated",
          abs(conc["hhi"] - 2777.7778) < 1e-3 and abs(conc["cr4_pct"] - 91.6667) < 1e-3
          and conc["single_family_assignees"] == 2 and conc["top_assignee"] == "Alpha"
          and conc["verdict"] == "concentrated" and conc["top"][0]["cum_share_pct"] == round(500 / 12, 4))
    check("sorting: equal counts (Delta 1, Epsilon 1) ordered by name",
          [r["assignee"] for r in concentration(fams, top=10)["top"]] == ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"])

    # 5. Velocity on the mini set: 2018:1 2019:2 2020:2 2021:2 2022:1 2023:4; peak 2023; CAGR 1->4 over 5y = 31.95%;
    #    last 3 years (2021-2023) = 7 of 12 = 58.3%; trend: mean 7/3 = 2.33 vs 2018-2020 mean 5/3 = 1.67 -> 1.40 accelerating.
    vel = velocity(fams, recent=3)
    check("velocity: series 1,2,2,2,1,4 with reference year 2023",
          [r["families"] for r in vel["years"]] == [1, 2, 2, 2, 1, 4] and vel["reference_year"] == 2023)
    check("velocity: peak 2023 (4), CAGR 2018->2023 = +31.95%",
          vel["peak"] == {"year": 2023, "families": 4} and abs(vel["cagr"]["cagr_pct"] - 31.9508) < 1e-3)
    check("velocity: last 3 years 7/12 = 58.3%; trend accelerating (ratio 1.40)",
          vel["recent"]["families"] == 7 and abs(vel["recent"]["share_pct"] - 58.3333) < 1e-3
          and vel["trend"] == "accelerating" and abs(vel["trend_detail"]["ratio"] - 1.4) < 1e-9)
    check("velocity: 2022 and 2023 flagged as within the publication-lag window",
          [r["year"] for r in vel["years"] if r["lag_flag"]] == [2022, 2023])
    text = "\n".join(fmt_velocity(vel))
    check("publication-lag warning is always printed", LAG_WARNING in text and "publication lag" in text)
    check("--asof extends the series and moves the window: asof 2025 -> last 3 years 2023-2025 = 4 families",
          velocity(fams, recent=3, asof=2025)["recent"] == {"years": [2023, 2025], "families": 4,
                                                            "share_pct": round(400 / 12, 4)})

    # 6. White space on the mini set (top-3 CPC x top-3 assignees):
    #    H01M10/0562: Alpha 5, Beta 3, Gamma 0 | H01M4/04: Alpha 2, Beta 0, Gamma 2 | H01M4/366: Alpha 0, Beta 1, Gamma 0
    ws = whitespace(fams, "full", k=3, m=3, low=1)
    check("cpc counts: H01M10/0562 9, H01M4/04 4, H01M4/366 1",
          [(r["cpc"], r["families"]) for r in ws["cpc_counts"]] == [("H01M10/0562", 9), ("H01M4/04", 4), ("H01M4/366", 1)])
    check("matrix cells as hand-counted",
          ws["matrix"]["assignees"] == ["Alpha", "Beta", "Gamma"] and ws["matrix"]["cells"] == [[5, 3, 0], [2, 0, 2], [0, 1, 0]])
    empties = [(e["cpc"], e["assignee"]) for e in ws["empty_cells"]]
    check("white-space cells: 4 empty, ordered by CPC density; Beta x H01M4/366 is the one low (=1) cell",
          empties == [("H01M10/0562", "Gamma"), ("H01M4/04", "Beta"), ("H01M4/366", "Alpha"), ("H01M4/366", "Gamma")]
          and [(e["cpc"], e["assignee"]) for e in ws["low_cells"]] == [("H01M4/366", "Beta")])
    check("sparse codes overall: H01M4/366 (1 family, Beta)",
          ws["sparse_cpcs"] == [{"cpc": "H01M4/366", "families": 1, "assignees": ["Beta"]}])
    check("co-occurrence: (0562, 4/04) 2, (0562, 4/366) 1; breadth Alpha 2, Beta 2, Gamma 1",
          [(tuple(p["pair"]), p["families"]) for p in ws["co_occurrence"]]
          == [(("H01M10/0562", "H01M4/04"), 2), (("H01M10/0562", "H01M4/366"), 1)]
          and [(b["assignee"], b["distinct_cpcs"]) for b in ws["breadth"]] == [("Alpha", 2), ("Beta", 2), ("Gamma", 1)])
    check("CPC roll-up: group level merges H01M4/04 + H01M4/366 into H01M4 (5 families); subclass -> H01M (11)",
          cpc_counts(fams, "group") == [("H01M10", 9), ("H01M4", 5)] and cpc_counts(fams, "subclass") == [("H01M", 11)])

    # 7. Entry (reference year 2023, recent 3 -> entrant if first >= 2021; dormant 4 -> dormant if last <= 2019).
    en = entry(fams, recent=3, dormant=4)
    status = {r["assignee"]: r["status"] for r in en["assignees"]}
    check("entry: Gamma entrant (first 2023); Alpha, Beta established",
          status["Gamma"] == "entrant" and status["Alpha"] == "established" and status["Beta"] == "established")
    check("entry: Delta (last 2018) and Epsilon (last 2019 = boundary) dormant; with --dormant 5 only Delta is",
          status["Delta"] == "dormant" and status["Epsilon"] == "dormant"
          and entry(fams, recent=3, dormant=5)["dormant"] == ["Delta"])
    check("entry: counts entrant 1 / established 2 / dormant 2",
          en["counts"] == {"entrant": 1, "established": 2, "dormant": 2, "unknown": 0})

    # 8. Demo reproduces the SKILL.md worked example; report is deterministic and JSON-serialisable.
    demo = parse_rows(demo_rows())
    dc = concentration(demo, top=3)
    dv = velocity(demo, recent=3)
    dw = whitespace(demo, "full", 8, 6, 1)
    check("demo: 42 families, 18 assignees, top-3 = Incumbent A 9 / Incumbent B 7 / Startup C 5",
          dc["families"] == 42 and dc["assignees"] == 18
          and [(r["assignee"], r["families"]) for r in dc["top"]] == [("Incumbent A", 9), ("Incumbent B", 7), ("Startup C", 5)])
    check("demo: velocity 3 -> 5 -> 9 -> 14 -> 11, peak 2022, CAGR +38.4% ((11/3)^(1/4) - 1)",
          [r["families"] for r in dv["years"]] == [3, 5, 9, 14, 11] and dv["peak"]["year"] == 2022
          and abs(dv["cagr"]["cagr_pct"] - 38.38) < 0.01)
    check("demo: H01M10/0562 on 26 families, H01M4/04 on 4, H01M4/366 on 1",
          dict((r["cpc"], r["families"]) for r in dw["cpc_counts"]).get("H01M10/0562") == 26
          and dict((r["cpc"], r["families"]) for r in dw["cpc_counts"]).get("H01M4/04") == 4
          and dw["sparse_cpcs"][0]["cpc"] == "H01M4/366")
    check("demo: HHI 1,065.8 -> 2023 moderately / 2010 unconcentrated; CR4 54.8%",
          abs(dc["hhi"] - 1065.76) < 0.01 and dc["hhi_band_2023"] == "moderately concentrated"
          and dc["hhi_band_2010"] == "unconcentrated" and abs(dc["cr4_pct"] - 54.7619) < 1e-3)
    de = entry(demo, 3, 4)
    check("demo: 13 entrants, 4 established, Incumbent D dormant",
          de["counts"] == {"entrant": 13, "established": 4, "dormant": 1, "unknown": 0} and de["dormant"] == ["Incumbent D"])
    r1 = "\n".join(fmt_report(report(demo, "demo")))
    r2 = "\n".join(fmt_report(report(demo, "demo")))
    check("report: two runs byte-identical and JSON-serialisable",
          r1 == r2 and json.dumps(report(demo, "demo")) == json.dumps(report(demo, "demo")))

    # 9. CSV / stdin round trip and CLI exit codes.
    csv_text = ("assignee,priority_year,cpc,jurisdictions,family_size,citations\n"
                "Alpha,2021,H01M10/0562;H01M4/04,US;EP,4,2\n"
                "Beta,2022,H01M10/0562,US,1,\n"
                "Gamma,2023,,,,\n")
    fc = parse_text(csv_text, is_json=False)
    check("CSV parse: 3 families, jurisdictions upper-cased and sorted, blanks -> None/()",
          len(fc) == 3 and fc[0]["jurisdictions"] == ("EP", "US") and fc[1]["citations"] is None
          and fc[2]["cpcs"] == () and fc[2]["year"] == 2023 and fc[0]["family_size"] == 4)
    fj = parse_text(json.dumps({"families": [{"Assignee": "A", "Year": "2020", "IPC": ["H01M4/04", "h01m 4/04"]}]}), True)
    check("JSON parse: aliased keys, list-valued CPC de-duplicated after normalization",
          fj[0]["assignee"] == "A" and fj[0]["year"] == 2020 and fj[0]["cpcs"] == ("H01M4/04",))
    buf, old_stdin, old_stdout = io.StringIO(), sys.stdin, sys.stdout
    try:
        sys.stdin, sys.stdout = io.StringIO(csv_text), buf
        rc = main(["concentrate", "--file", "-"])
    finally:
        sys.stdin, sys.stdout = old_stdin, old_stdout
    check("CLI: 3 families < --min-families 5 -> exit 2 with the SKILL.md too-small message",
          rc == 2 and "cluster too small" in buf.getvalue())
    buf = io.StringIO()
    try:
        sys.stdin, sys.stdout = io.StringIO(csv_text), buf
        rc = main(["concentrate", "--file", "-", "--min-families", "0", "--json"])
    finally:
        sys.stdin, sys.stdout = old_stdin, old_stdout
    check("CLI: --min-families 0 --json -> exit 0 and valid JSON with hhi 3,333.3",
          rc == 0 and abs(json.loads(buf.getvalue())["hhi"] - 3333.3333) < 1e-3)
    old_stderr = sys.stderr
    try:
        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        try:
            main(["velocity", "--demo", "--recent", "0"])
            rc = 0
        except SystemExit as exc:
            rc = exc.code
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
    check("CLI: invalid option value exits 2 (usage error)", rc == 2)

    print(f"selftest OK ({len(checks)} checks passed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
