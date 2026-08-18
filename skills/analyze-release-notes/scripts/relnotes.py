#!/usr/bin/env python3
"""relnotes.py — semver arithmetic and cue-based tagging for release notes.

Deterministic companion to ../SKILL.md (analyze-release-notes). It does the two
things a reader gets wrong under time pressure — version arithmetic and consistent
category tagging — and emits the ReleaseEvent JSON defined in SKILL.md
("Output schema"). It does NOT grade the source (that is `rate-source-admiralty`)
and it never paraphrases: every listed change is the verbatim entry text.

Definitions implemented
  * Semantic Versioning 2.0.0 (Preston-Werner), https://semver.org/spec/v2.0.0.html
      §2 core MAJOR.MINOR.PATCH, §9 pre-release identifiers, §10 build metadata,
      §11 precedence: 11.2 numeric core, 11.3 pre-release < normal, 11.4.1 numeric
      identifiers compared numerically, 11.4.2 alphanumeric compared in ASCII order,
      11.4.3 numeric < alphanumeric, 11.4.4 more fields wins when a prefix is equal.
      Build metadata is ignored for precedence (§10). Parser = the spec's own regex.
      `bump` = first differing core component (major | minor | patch), "prerelease"
      when only the pre-release part differs (e.g. 1.0.0-rc.1 -> 1.0.0), "none" when
      precedence-equal, "downgrade" when TO < FROM, "calver" when either side looks
      like calendar versioning (SKILL.md step 1). A leading "v" is tolerated; loose
      forms ("3.0", "1.2.3.4", leading zeros) parse with a note.
  * Conventional Commits 1.0.0, https://www.conventionalcommits.org/en/v1.0.0/
      rule 12/16: an uppercase `BREAKING CHANGE:` / `BREAKING-CHANGE:` footer token;
      rule 13: `type(scope)!:` — a `!` before the colon marks a breaking change;
      types feat -> new feature, fix -> bug fix, perf -> performance, docs -> docs,
      build/chore with a `deps` scope -> dependency bump, other types -> other.
  * Keep a Changelog 1.1.0, https://keepachangelog.com/en/1.1.0/
      section names Added / Changed / Deprecated / Removed / Fixed / Security,
      version headings `## [1.1.1] - 2023-03-05`, `## [Unreleased]`, `[YANKED]`,
      ISO 8601 dates ("Month D, YYYY" and "D Month YYYY" are also recognised).
  * CVE ids `CVE-\\d{4}-\\d{4,}` (cve.mitre.org) and GitHub advisories `GHSA-xxxx-xxxx-xxxx`.

Categories (SKILL.md vocabulary, fixed order):
  breaking change | deprecation | removal | new feature | enhancement | bug fix |
  security fix | performance | docs | dependency bump | other
Mapping to the ReleaseEvent schema: breaking change + removal -> breaking_changes[]
(SemVer §8: removing public functionality is backwards-incompatible), new feature ->
new_features[], deprecation -> deprecations[], bug fix -> bug_fixes (int; an entry
that says "N fixes" counts N, otherwise 1), CVE/GHSA ids -> security_advisories[].

Entries are top-level bullets (nested bullets elaborate their parent and are merged
into it, unless the parent is a <= 2-word group label such as "- Core" or "- Breaking
changes:", whose children are then the entries) or the sentences of prose paragraphs.
Lines under Contributors / Known issues / Full Changelog headings are not entries.

Classification precedence per entry, first hit wins:
  1. explicit markers: `type!:` / uppercase BREAKING CHANGE token -> breaking change;
     CVE/GHSA id -> security fix
  2. author structure: a *final* section heading (Breaking, Deprecated, Removed,
     Fixed, Security, Performance, Docs, Dependencies) or a Conventional Commits type
     fix/perf/docs/build(deps)/chore(deps)/security; then a non-final label
     (Added/Features/Changed/Improvements headings, `feat:`/`chore:`/`refactor:` types)
     that the high-priority phrases below may override
  3. phrase cues, in this order: deprecation ("deprecated", "will be removed in",
     "sunset"), removal ("removed", "dropped support", entry starts with remove/drop),
     breaking ("breaking change", "backwards-incompatible", "renamed", "dropped support",
     "migration guide", "now requires", "no longer" unless a bug-fix cue is present),
     security words (vulnerability, advisory, XSS, RCE, ...), docs, dependency bump,
     performance, bug fix, new feature, enhancement; else other.

Semver-consistency flag (SKILL.md anti-pattern "do not skip the prior-version
comparison"): raised when breaking-change entries exist but the bump is not major
(0.x minor bumps and pre-release bumps are reported at "info" severity — SemVer §4/§9),
or when the bump is major but no breaking-change entry was found (0.x -> 1.0.0 at
"info": may be a stabilisation release, SemVer §5).

Parse confidence (integer 0-100; the trace is printed with every scan):
  40 base; +20 version from a heading in the text (+15 if only from --to);
  +10 release date found; +10 prior version given/linked/"since" (+5 when it is
  inferred via the next-lower changelog heading); +10 a recognised section heading;
  +5 an explicit machine marker; -25 no version; -10 no entries;
  -floor(20 * other / entries); -15 consistency flag at warn (-5 at info); clamp 0-100.

Stdlib only. Python 3.9+. Offline. Deterministic (no clock, sorted iteration).
Exit codes: 0 ok; 1 invalid input/usage; 2 scan raised the consistency flag at warn.

Usage:
    python3 relnotes.py semver parse v2.3.1-beta.2+build.5
    python3 relnotes.py semver compare 1.0.0-rc.1 1.0.0
    python3 relnotes.py semver bump 1.4.2 2.0.0 [--json]
    python3 relnotes.py scan --file CHANGELOG.md [--from 1.4.2 --to 2.0.0] [--report]
    python3 relnotes.py scan --text "..." [--project NAME --source-url URL --source-grade A1]
    python3 relnotes.py --demo          # reproduces the SKILL.md worked example
    python3 relnotes.py --selftest      # semver §11 ordering example, bumps, sample scan
"""

import argparse
import functools
import json
import re
import sys

# --- semver ------------------------------------------------------------------

# The regular expression suggested by semver.org (FAQ), named-group form.
SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)
# Tolerant form: 1-4 numeric components (leading zeros allowed), optional -pre, +build.
LOOSE_RE = re.compile(
    r"^(?P<a>\d+)(?:\.(?P<b>\d+))?(?:\.(?P<c>\d+))?(?P<extra>(?:\.\d+)*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?(?:\+(?P<build>[0-9A-Za-z.-]+))?$"
)


def _ident(s):
    """Pre-release identifier: int when all digits (SemVer §11.4.1), else str."""
    return int(s) if s.isdigit() else s


def parse_version(raw):
    """Parse a version string. Never raises; scheme tells you what it found.

    scheme: "semver" (strict 2.0.0), "semver-loose" (leading v, missing/extra
    components, leading zeros), "calver?" (first component is a year, or a
    zero-padded YY.MM), "invalid".
    """
    text = str(raw).strip()
    notes = []
    core = text
    if core[:1] in ("v", "V"):
        core = core[1:]
        notes.append("leading 'v' stripped")
    if core[:1] == "=":
        core = core[1:]
    out = {"input": text, "normalized": None, "scheme": "invalid", "major": None,
           "minor": None, "patch": None, "extra": [], "prerelease": [], "build": [],
           "notes": notes}
    m = SEMVER_RE.match(core)
    if m:
        out.update(major=int(m.group("major")), minor=int(m.group("minor")),
                   patch=int(m.group("patch")),
                   prerelease=[_ident(p) for p in (m.group("prerelease") or "").split(".") if p],
                   build=[b for b in (m.group("buildmetadata") or "").split(".") if b])
        out["scheme"] = "semver-loose" if notes else "semver"
    else:
        lm = LOOSE_RE.match(core)
        if not lm:
            return out
        b, c = lm.group("b"), lm.group("c")
        if b is None or c is None:
            notes.append("missing components padded with 0")
        extra = [int(x) for x in lm.group("extra").split(".") if x]
        if extra:
            notes.append("extra numeric components kept for ordering (not SemVer)")
        if any(len(x) > 1 and x[0] == "0" for x in (lm.group("a"), b or "", c or "")):
            notes.append("leading zeros (invalid in SemVer 2.0.0 §2)")
        out.update(major=int(lm.group("a")), minor=int(b or 0), patch=int(c or 0), extra=extra,
                   prerelease=[_ident(p) for p in (lm.group("prerelease") or "").split(".") if p],
                   build=[x for x in (lm.group("build") or "").split(".") if x])
        out["scheme"] = "semver-loose"
        if b is not None and len(b) == 2 and b[0] == "0" and len(lm.group("a")) == 2:
            out["scheme"] = "calver?"  # e.g. 24.04
    if out["major"] is not None and 1900 <= out["major"] <= 2199:
        out["scheme"] = "calver?"  # e.g. 2026.4.1 / 2026.04.01
        notes.append("first component looks like a year")
    # CalVer keeps its zero padding (2026.04.01 is the name, not a number).
    out["normalized"] = core if out["scheme"] == "calver?" else format_version(out)
    return out


def format_version(v):
    s = "%d.%d.%d" % (v["major"], v["minor"], v["patch"])
    if v["extra"]:
        s += "".join(".%d" % x for x in v["extra"])
    if v["prerelease"]:
        s += "-" + ".".join(str(p) for p in v["prerelease"])
    if v["build"]:
        s += "+" + ".".join(v["build"])
    return s


def _cmp(a, b):
    return (a > b) - (a < b)


def compare_explain(a, b):
    """Return (cmp, rule) for parsed versions a, b; cmp in {-1, 0, 1}.

    Implements SemVer 2.0.0 §11 exactly; the rule names the deciding clause.
    """
    for key, rule in (("major", "§11.2 major compared numerically"),
                      ("minor", "§11.2 minor compared numerically"),
                      ("patch", "§11.2 patch compared numerically")):
        c = _cmp(a[key], b[key])
        if c:
            return c, rule
    c = _cmp(a["extra"], b["extra"])
    if c:
        return c, "(not SemVer) extra numeric components compared numerically"
    pa, pb = a["prerelease"], b["prerelease"]
    if not pa and not pb:
        return 0, "§10 equal precedence (build metadata is ignored)"
    if not pa:
        return 1, "§11.3 a pre-release version has lower precedence than the normal version"
    if not pb:
        return -1, "§11.3 a pre-release version has lower precedence than the normal version"
    for x, y in zip(pa, pb):
        if x == y:
            continue
        xi, yi = isinstance(x, int), isinstance(y, int)
        if xi and yi:
            return _cmp(x, y), "§11.4.1 numeric identifiers are compared numerically"
        if xi != yi:
            return (-1 if xi else 1), "§11.4.3 numeric identifiers have lower precedence than alphanumeric"
        return _cmp(x, y), "§11.4.2 alphanumeric identifiers compared lexically in ASCII order"
    if len(pa) != len(pb):
        return _cmp(len(pa), len(pb)), "§11.4.4 a larger set of pre-release fields has higher precedence"
    return 0, "§10 equal precedence (build metadata is ignored)"


def compare_versions(a, b):
    return compare_explain(parse_version(a), parse_version(b))[0]


def classify_bump(v_from, v_to):
    """Bump kind between two parsed versions (see module docstring)."""
    if v_from["scheme"] == "invalid" or v_to["scheme"] == "invalid":
        return None
    if "calver?" in (v_from["scheme"], v_to["scheme"]):
        return "calver"
    c, _ = compare_explain(v_from, v_to)
    if c == 0:
        return "none"
    if c > 0:
        return "downgrade"
    for key in ("major", "minor", "patch"):
        if v_from[key] != v_to[key]:
            return key
    if v_from["extra"] != v_to["extra"]:
        return "patch"
    return "prerelease"


# --- release-note scanning: cue tables ---------------------------------------

CATEGORIES = ["breaking change", "deprecation", "removal", "new feature", "enhancement",
              "bug fix", "security fix", "performance", "docs", "dependency bump", "other"]
# Used to break ties when a heading names several categories ("Fixes and improvements").
CATEGORY_PRIORITY = ["breaking change", "security fix", "removal", "deprecation", "bug fix",
                     "performance", "docs", "dependency bump", "new feature", "enhancement", "other"]

# Normalised heading text -> (category, final). Final headings are not overridden by
# phrase cues; non-final ones (Added/Changed/...) yield to deprecation/removal/breaking/
# security phrases found in the entry itself.
HEADING_MAP = {}
for _keys, _cat, _final in (
    (("breaking", "breaking changes", "breaking change", "incompatible changes",
      "backwards incompatible changes", "backward incompatible changes"), "breaking change", True),
    (("deprecated", "deprecations", "deprecation"), "deprecation", True),
    (("removed", "removals", "removal"), "removal", True),
    (("fixed", "fixes", "bug fixes", "bugfixes", "bug fix", "bugs", "fixed bugs"), "bug fix", True),
    (("security", "security fixes", "security fix", "security advisories", "security updates",
      "vulnerabilities", "vulnerability fixes"), "security fix", True),
    (("performance", "perf", "performance improvements"), "performance", True),
    (("documentation", "docs", "doc"), "docs", True),
    (("dependencies", "dependency updates", "dependency bumps", "deps", "dependency"), "dependency bump", True),
    (("added", "features", "new features", "new", "whats new", "feature", "additions",
      "highlights"), "new feature", False),
    (("changed", "changes", "improvements", "enhancements", "improved", "enhancement",
      "improvement"), "enhancement", False),
    (("other", "other changes", "miscellaneous", "misc", "internal", "chores", "chore",
      "maintenance", "refactoring", "refactor", "build", "ci", "tests", "testing", "style",
      "housekeeping"), "other", False),
):
    for _k in _keys:
        HEADING_MAP[_k] = (_cat, _final)
# Headings that carry no category: entries beneath them are classified by their own cues.
TRANSPARENT_HEADINGS = {"whats changed", "unreleased", "notes", "release notes", "summary",
                        "overview", "upgrade notes", "upgrading", "migration", "migration guide",
                        "details", "changelog", "change log", "what changed"}
# Headings whose lines are not change entries at all.
IGNORE_HEADINGS = {"contributors", "new contributors", "thanks", "credits", "acknowledgements",
                   "acknowledgments", "known issues", "full changelog", "checksums", "assets",
                   "downloads", "sha256", "sha256 checksums"}

CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,}\b", re.I)
GHSA_RE = re.compile(r"\bGHSA(?:-[23456789cfghjmpqrvwx]{4}){3}\b", re.I)
# Conventional Commits 1.0.0: type(scope)!: subject
CC_RE = re.compile(r"^(?P<type>[A-Za-z]+)(?:\((?P<scope>[^)]*)\))?(?P<bang>!)?:\s+(?P<subject>\S.*)$")
CC_TYPES = {"feat": ("new feature", False), "fix": ("bug fix", True), "perf": ("performance", True),
            "docs": ("docs", True), "security": ("security fix", True),
            "refactor": ("other", False), "style": ("other", False), "test": ("other", False),
            "tests": ("other", False), "ci": ("other", False), "chore": ("other", False),
            "build": ("other", False), "revert": ("other", False)}
# Tier-1 breaking markers (Conventional Commits rules 12, 13, 16; uppercase is required
# for the footer token, so these are case-sensitive except the "Breaking:" lead-in).
BREAKING_STRONG = [
    ("marker:BREAKING CHANGE token", re.compile(r"\bBREAKING[ -]CHANGES?\b")),
    ("marker:BREAKING token", re.compile(r"\bBREAKING\b")),
    ("marker:'Breaking:' lead-in", re.compile(r"^\W*breaking(?: changes?)?\s*[:—–-]", re.I)),
]
BUGFIX_WORDS = re.compile(r"\b(?:fix(?:es|ed|ing)?|bugs?|crash\w*|regression|hotfix|resolv(?:e|es|ed)|"
                          r"incorrect\w*|correct(?:s|ed|ly)?|issues?|leak|hang)\b", re.I)
# Tier-3 phrase cues. HIGH cues may override non-final labels; LOW cues only fill gaps.
HIGH_CUES = [
    ("phrase:future removal", re.compile(
        r"\b(?:will be|to be|going to be|scheduled for|slated for|planned for|pending)\s+"
        r"(?:removed|removal|dropped|deleted)\b", re.I), "deprecation"),
    ("phrase:removed/dropped", re.compile(
        r"\b(?:removed|dropped|deleted)\b|\b(?:drop(?:s|ped)?|remov(?:e|es|ed))\s+support\b|"
        r"\bno longer\s+(?:supported|available|shipped|bundled|included|maintained)\b|"
        r"^\W*(?:[a-z]+(?:\([^)]*\))?!?:\s*)?(?:remove|drop|delete)\b", re.I), "removal"),
    ("phrase:deprecated", re.compile(r"\bdeprecat(?:e|es|ed|ion|ions|ing)\b|\bsunset(?:s|ted|ting)?\b", re.I),
     "deprecation"),
    ("phrase:breaking wording", re.compile(
        r"\bbreaking[ -]changes?\b|\bbackwards?[ -]incompatib\w*|\bnot backwards?[ -]compatible\b|"
        r"\brenam(?:e|es|ed|ing)\b|\bmigration guide\b|\bmust migrate\b|\brequires migration\b|"
        r"\bnow requires?\b|\bminimum (?:supported |required )?(?:version|python|node|java|go|ruby|php)\b",
        re.I), "breaking change"),
    ("phrase:'no longer' (no bug-fix cue)", None, "breaking change"),  # handled specially
    ("phrase:security wording", re.compile(
        r"\bsecurity\b|\bvulnerab\w*|\badvisor(?:y|ies)\b|\bexploit\w*|\bXSS\b|\bCSRF\b|\bSSRF\b|"
        r"\bRCE\b|\bDoS\b|\bdenial of service\b|\binjection\b|\bprivilege escalation\b|"
        r"\bpath traversal\b|\bhardening\b", re.I), "security fix"),
]
NO_LONGER_RE = re.compile(r"\bno longer\b", re.I)
LOW_CUES = [
    ("phrase:docs wording", re.compile(
        r"\bdocs?\b|\bdocumentation\b|\breadme\b|\btypos?\b|\bdocstrings?\b|\bchangelog\b|\bspelling\b",
        re.I), "docs"),
    ("phrase:dependency wording", re.compile(
        r"\bbump(?:s|ed)?\b|\bdependenc(?:y|ies)\b|\bdeps\b|\bdependabot\b|\brenovate\b|\block ?file\b|"
        r"\b(?:upgrade|update)[sd]?\s+\S+(?:\s+\S+){0,3}?\s+(?:to|from)\s+v?\d", re.I), "dependency bump"),
    ("phrase:performance wording", re.compile(
        r"\bperformance\b|\bperf\b|\bfaster\b|\bspeed(?:s|ed)?[ -]?up\b|\bspeedup\b|\blatency\b|"
        r"\bthroughput\b|\bmemory (?:usage|footprint|consumption)\b|\boptimi[sz]\w*", re.I), "performance"),
    ("phrase:bug-fix wording", BUGFIX_WORDS, "bug fix"),
    ("phrase:feature wording", re.compile(
        r"\badd(?:s|ed|ing)?\b|\bnew\b|\bintroduc(?:e|es|ed|ing)\b|\bsupport for\b|\bnow supports?\b|"
        r"\bimplement(?:s|ed)?\b|\bfeature\b|\bability to\b", re.I), "new feature"),
    ("phrase:enhancement wording", re.compile(
        r"\bimprov(?:e|es|ed|ement|ements|ing)\b|\benhanc\w*|\bupdate[sd]?\b|\bupgrade[sd]?\b|\bbetter\b|"
        r"\ballow(?:s|ed)?\b|\bextend(?:s|ed)?\b|\boption(?:al|s)?\b|\bconfigurable\b|\brefactor\w*|"
        r"\bchang(?:e|es|ed)\b|\btweak\w*|\bsimplif\w*|\bclean ?up\b|\bincrease[sd]?\b|\breduce[sd]?\b",
        re.I), "enhancement"),
]
FIX_COUNT_RE = re.compile(r"\b(\d+)\s+(?:bug[- ]?)?fix(?:es)?\b", re.I)
# Phrase cues are matched on text without URLs and without "see the docs"-style tails,
# so a link or a pointer to documentation does not decide the category.
URL_RE = re.compile(r"https?://\S+|\bwww\.\S+", re.I)
DOC_POINTER_RE = re.compile(r"\b(?:see|read|check|refer to|more in|details in)\s+(?:the\s+|our\s+)?"
                            r"(?:docs?|documentation|readme|guide|wiki|manual)\b.*$", re.I)
REMOVAL_VERSION_RES = [
    re.compile(r"\b(?:removed|removal|dropped|deleted|go away)\s+(?:in|by|with|as of|from)\s+(?:the\s+)?"
               r"(?:v(?:ersion)?\.?\s*)?(?P<ver>\d+(?:\.\d+)*|next (?:major|minor)(?: (?:version|release))?)", re.I),
    re.compile(r"\b(?:until|before)\s+(?:v(?:ersion)?\.?\s*)?(?P<ver>\d+(?:\.\d+)+)\b", re.I),
]

# Version headings and dates.
# A version token as dot-separated identifiers (no trailing dot can be captured).
VER_TOKEN = r"v?\d+(?:\.\d+)+(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
MONTHS = ("january|february|march|april|may|june|july|august|september|october|november|december|"
          "jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec")
MONTH_NUM = {m: i % 12 + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august", "september",
     "october", "november", "december"])}
DATE_ISO_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
DATE_MDY_RE = re.compile(r"\b(%s)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b" % MONTHS, re.I)
DATE_DMY_RE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(%s)\.?,?\s+(\d{4})\b" % MONTHS, re.I)
VERSION_LINE_RE = re.compile(
    r"^(?P<lead>(?:[A-Za-z][\w.'-]*\s+){0,3})\[?(?P<ver>%s)\]?(?P<rest>.*)$" % VER_TOKEN)
LEAD_STOPWORDS = {"in", "since", "from", "to", "the", "a", "an", "of", "on", "at", "by", "than",
                  "before", "after", "until", "into", "with", "requires", "require", "required",
                  "removed", "deprecated", "will", "be", "is", "are", "was", "were", "as", "and",
                  "or", "supports", "support", "targets", "target", "needs", "need", "minimum",
                  "min", "under", "over", "above", "below", "up", "down", "use", "using", "via"}
REST_OK_RE = re.compile(r"^\s*(?:$|[-–—:(\[,]|released\b|is (?:now )?(?:out|available)\b|available\b|"
                        r"\d{4}-\d{2}-\d{2}|(?:%s)\b|\d{1,2}(?:st|nd|rd|th)?\s+(?:%s)\b)" % (MONTHS, MONTHS), re.I)
UNRELEASED_RE = re.compile(r"^\W*unreleased\W*$", re.I)
COMPARE_LINK_RE = re.compile(r"compare/(?P<a>%s)\.{2,3}(?P<b>%s)" % (VER_TOKEN, VER_TOKEN))
SINCE_RE = re.compile(r"\b(?:since|upgrading from|upgrade from|changes since|changes from)\s+v?(?P<a>\d+\.\d+(?:\.\d+)?)\b", re.I)
BULLET_RE = re.compile(r"^(?P<indent>[ \t]*)(?:[-*+•]|\d+[.)])\s+(?P<text>\S.*)$")
RULE_LINE_RE = re.compile(r"^\s*([-=*_~])\1{2,}\s*$")
# Prose paragraphs are split into sentences (one entry each); bullets are never split.
SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z`\"'(])")
ABBREVIATIONS = ("e.g.", "i.e.", "etc.", "vs.", "approx.", "cf.", "no.", "fig.")


def split_sentences(text):
    parts, buf = [], ""
    for piece in SENTENCE_END_RE.split(text):
        buf = (buf + " " + piece).strip() if buf else piece
        if not buf.lower().endswith(ABBREVIATIONS):
            parts.append(buf)
            buf = ""
    if buf:
        parts.append(buf)
    return parts
FULL_CHANGELOG_RE = re.compile(r"^\W*full changelog\b", re.I)


def normalize_heading(text):
    t = re.sub(r"[’']", "", text.lower())
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def classify_heading(text):
    """Return ('ignore'|'transparent'|category, final) or None for unknown headings."""
    n = normalize_heading(text)
    if not n:
        return None
    if n in IGNORE_HEADINGS:
        return ("ignore", True)
    if n in TRANSPARENT_HEADINGS:
        return ("transparent", True)
    if n in HEADING_MAP:
        return HEADING_MAP[n]
    if len(n.split()) <= 6:
        found = {HEADING_MAP[k][0] for k in HEADING_MAP if re.search(r"\b%s\b" % re.escape(k), n)}
        if found:
            best = min(found, key=CATEGORY_PRIORITY.index)
            return (best, False)
    return None


def to_iso_date(text):
    """First recognisable date in text as YYYY-MM-DD, or None."""
    m = DATE_ISO_RE.search(text)
    if m:
        return "%s-%s-%s" % m.groups()
    m = DATE_MDY_RE.search(text)
    if m:
        mon, day, year = m.groups()
    else:
        m = DATE_DMY_RE.search(text)
        if not m:
            return None
        day, mon, year = m.groups()
    mon = mon.lower()[:3]
    num = next(v for k, v in MONTH_NUM.items() if k.startswith(mon))
    return "%s-%02d-%02d" % (year, num, int(day))


def parse_version_heading(line):
    """Recognise a version heading line; return dict or None.

    Accepts `## [2.0.0] - 2026-03-14`, `## v2.0.0 (March 14, 2026)`, `# Release 2.0.0`,
    `## [Unreleased]`, `## [0.0.5] - 2014-12-13 [YANKED]`, plain `v2.0.0`.
    """
    s = line.strip()
    is_md = s.startswith("#")
    body = s.lstrip("#").strip().strip("*_ ").strip()
    if not body or BULLET_RE.match(line):
        return None
    if UNRELEASED_RE.match(body):
        return {"version": None, "date": None, "yanked": False, "unreleased": True}
    m = VERSION_LINE_RE.match(body)
    if not m:
        return None
    lead = m.group("lead").strip().lower().split()
    if lead:
        if any(w in LEAD_STOPWORDS for w in lead):
            return None
        if not is_md and lead[0] not in ("release", "version", "v", "tag") and len(lead) > 2:
            return None
    rest = m.group("rest")
    if not REST_OK_RE.match(rest):
        return None
    ver = m.group("ver")
    if parse_version(ver)["scheme"] == "invalid":
        return None
    return {"version": ver[1:] if ver[:1] in "vV" else ver, "date": to_iso_date(rest),
            "yanked": "yanked" in rest.lower(), "unreleased": False}


def _all_ids(text):
    ids = {m.group(0).upper() for m in CVE_RE.finditer(text)}
    ids |= {"GHSA-" + m.group(0)[5:].lower() for m in GHSA_RE.finditer(text)}
    return sorted(ids)


def _phrase_text(text):
    return DOC_POINTER_RE.sub("", URL_RE.sub(" ", text)).strip()


def classify_entry(text, heading):
    """Return (category, cue) for one entry; heading is (category, final, name) or None."""
    for cue, rx in BREAKING_STRONG:
        if rx.search(text):
            return "breaking change", cue
    cc = CC_RE.match(text)
    if cc and cc.group("bang"):
        return "breaking change", "marker:type! (Conventional Commits rule 13)"
    if CVE_RE.search(text) or GHSA_RE.search(text):
        return "security fix", "marker:CVE/GHSA id"
    label = None
    if heading and heading[1]:
        return heading[0], "section:%s" % heading[2]
    if cc and cc.group("type").lower() in CC_TYPES:
        ctype = cc.group("type").lower()
        cat, final = CC_TYPES[ctype]
        scope = (cc.group("scope") or "").lower()
        if ctype in ("build", "chore") and "dep" in scope:
            cat, final = "dependency bump", True
        if final:
            return cat, "type:%s" % ctype
        label = (cat, "type:%s" % ctype)
    elif heading:
        label = (heading[0], "section:%s" % heading[2])
    ptext = _phrase_text(text)
    for cue, rx, cat in HIGH_CUES:
        if rx is None:
            if NO_LONGER_RE.search(ptext) and not BUGFIX_WORDS.search(ptext):
                return cat, cue
        elif rx.search(ptext):
            return cat, cue
    if label:
        return label
    for cue, rx, cat in LOW_CUES:
        if rx.search(ptext):
            return cat, cue
    return "other", None


def _heading_tuple(text, used_headings):
    """Turn heading text into the state used by extract_entries.

    Returns "ignore", None (transparent or unknown), or (category, final, normalised name).
    """
    h = classify_heading(text)
    if h is None or h[0] == "transparent":
        return None
    if h[0] == "ignore":
        return "ignore"
    norm = normalize_heading(text)
    used_headings.append(norm)
    return (h[0], h[1], norm)


def _indent_of(raw):
    return len(re.match(r"[ \t]*", raw).group(0).expandtabs(4))


def _strip_decor(text):
    return text.lstrip("#").strip().strip("*_:").strip()


def extract_entries(lines, start, end):
    """Split lines[start:end] (0-based, end exclusive) into entries with headings applied.

    Entries are bullets or paragraph sentences. Nested bullets are merged into their parent
    (they elaborate it) unless the parent is a short group label (<= 2 words, or an
    exact heading word such as "- Breaking changes:"), in which case the children are
    the entries and a recognised label acts as their section heading. Headings are
    Markdown `#` lines, or short bold/colon lines that name a known section.
    """
    entries = []
    used_headings = []
    heading = None          # None | "ignore" | (category, final, normalised name)
    last_kind = None        # "bullet" | "para" | None
    base_indent = None      # indent of the current top-level bullet
    top = None              # entry dict of the current top-level bullet
    label = None            # None undecided | False merge mode | True label mode
    label_heading = None
    child_indent = None

    def reset_bullets():
        nonlocal base_indent, top, label, label_heading, child_indent
        base_indent, top, label, label_heading, child_indent = None, None, None, None, None

    for idx in range(start, end):
        raw = lines[idx]
        s = raw.strip()
        if not s or RULE_LINE_RE.match(s) or FULL_CHANGELOG_RE.match(s):
            last_kind = None
            continue
        if parse_version_heading(raw):
            heading, last_kind = None, None
            reset_bullets()
            continue
        bm = BULLET_RE.match(raw)
        if bm:
            indent = _indent_of(raw)
            text = bm.group("text").strip()
            if base_indent is None or indent <= base_indent or top is None:
                reset_bullets()
                base_indent = indent
                if heading != "ignore":
                    top = {"line": idx + 1, "text": text, "heading": heading}
                    entries.append(top)
                last_kind = "bullet"
                continue
            if label is None:  # first child decides whether the parent is a group label
                h = classify_heading(_strip_decor(top["text"]))
                exact = h is not None and normalize_heading(_strip_decor(top["text"])) in (
                    set(HEADING_MAP) | TRANSPARENT_HEADINGS | IGNORE_HEADINGS)
                if exact or len(_strip_decor(top["text"]).split()) <= 2:
                    label = True
                    if top in entries:
                        entries.remove(top)
                    label_heading = _heading_tuple(_strip_decor(top["text"]), used_headings) if h else heading
                else:
                    label = False
            if label:
                if child_indent is not None and indent > child_indent and entries:
                    entries[-1]["text"] += " " + text
                else:
                    child_indent = indent
                    if label_heading != "ignore":
                        entries.append({"line": idx + 1, "text": text, "heading": label_heading})
            else:
                top["text"] += " " + text
            last_kind = "bullet"
            continue
        indented = raw.startswith("  ") or raw.startswith("\t")
        if s.startswith("#"):
            heading, last_kind = _heading_tuple(_strip_decor(s), used_headings), None
            reset_bullets()
            continue
        if not indented and len(_strip_decor(s).split()) <= 5 and classify_heading(_strip_decor(s)):
            heading, last_kind = _heading_tuple(_strip_decor(s), used_headings), None
            reset_bullets()
            continue
        if last_kind == "bullet" and entries:  # indented or lazy continuation of a bullet
            entries[-1]["text"] += " " + s
            continue
        if last_kind == "para" and entries and entries[-1].get("_para"):
            entries[-1]["text"] += " " + s
            continue
        reset_bullets()
        last_kind = "para"
        if heading != "ignore":
            entries.append({"line": idx + 1, "text": s, "heading": heading, "_para": True})
    out = []
    for e in entries:
        if e.pop("_para", None):
            for sent in split_sentences(e["text"]):
                if sent.strip():
                    out.append({"line": e["line"], "text": sent.strip(), "heading": e["heading"]})
        else:
            out.append(e)
    return out, used_headings


def scan(text, v_from=None, v_to=None, project=None, source_url=None, source_grade=None):
    """Full pipeline: version/section selection, entry tagging, schema + consistency + confidence."""
    lines = text.splitlines()
    trace = []
    headings = []
    for i, line in enumerate(lines):
        if BULLET_RE.match(line):
            continue
        vh = parse_version_heading(line)
        if vh:
            vh["line"] = i + 1
            headings.append(vh)
    versioned = [h for h in headings if h["version"]]

    # -- which section is "this release"?
    current = None
    if v_to:
        want = parse_version(v_to)
        for h in versioned:
            if want["scheme"] != "invalid" and compare_explain(parse_version(h["version"]), want)[0] == 0:
                current = h
                break
        version = want["normalized"] if want["scheme"] != "invalid" else v_to.strip()
        if current:
            trace.append("version %s from --to; matching heading at line %d" % (version, current["line"]))
        else:
            trace.append("version %s from --to; no matching heading, whole text scanned" % version)
    elif versioned:
        current = versioned[0]
        for h in versioned[1:]:
            if compare_explain(parse_version(h["version"]), parse_version(current["version"]))[0] > 0:
                current = h
        version = parse_version(current["version"])["normalized"]
        trace.append("version %s from heading at line %d (highest of %d version headings)"
                     % (version, current["line"], len(versioned)))
    else:
        version = None
        trace.append("no version heading found and no --to given")
    if current:
        start = current["line"]  # 0-based index of the line after the heading
        later = [h["line"] for h in headings if h["line"] > current["line"]]
        end = (min(later) - 1) if later else len(lines)
        section_src = "heading"
    else:
        start, end, section_src = 0, len(lines), "whole text"
    section_lines = lines[start:end]
    section_text = "\n".join(section_lines)

    # -- date
    released = current["date"] if current else None
    date_src = "version heading" if released else None
    if not released:
        for ln in section_lines:
            if not BULLET_RE.match(ln) and re.search(r"\breleas|\bdate\b", ln, re.I):
                released = to_iso_date(ln)
                if released:
                    date_src = "release line"
                    break
    trace.append("date %s (%s)" % (released, date_src) if released else "no release date found")

    # -- prior version
    prior, prior_src, prior_inferred = None, None, False
    if v_from:
        pv = parse_version(v_from)
        prior = pv["normalized"] if pv["scheme"] != "invalid" else v_from.strip()
        prior_src = "--from"
    else:
        cm = COMPARE_LINK_RE.search(section_text)
        sm = SINCE_RE.search(section_text)
        if cm and version and compare_explain(parse_version(cm.group("b")), parse_version(version))[0] == 0 \
                and parse_version(cm.group("a"))["scheme"] != "invalid":
            prior, prior_src = parse_version(cm.group("a"))["normalized"], "compare link"
        elif sm and parse_version(sm.group("a"))["scheme"] != "invalid":
            prior, prior_src = parse_version(sm.group("a"))["normalized"], "'since' phrase"
        elif current and version:
            lower = [h for h in versioned
                     if compare_explain(parse_version(h["version"]), parse_version(version))[0] < 0]
            if lower:
                best = lower[0]
                for h in lower[1:]:
                    if compare_explain(parse_version(h["version"]), parse_version(best["version"]))[0] > 0:
                        best = h
                prior, prior_src, prior_inferred = parse_version(best["version"])["normalized"], \
                    "next-lower heading (line %d)" % best["line"], True
    trace.append("prior version %s (%s)" % (prior, prior_src) if prior else "prior version unknown")

    # -- bump
    bump = None
    if prior and version:
        bump = classify_bump(parse_version(prior), parse_version(version))
    scheme = parse_version(version)["scheme"] if version else None

    # -- entries
    entries, used_headings = extract_entries(lines, start, end)
    for e in entries:
        cat, cue = classify_entry(e["text"], e["heading"])
        e["category"], e["cue"] = cat, cue
        e.pop("heading", None)
    counts = {c: 0 for c in CATEGORIES}
    for e in entries:
        counts[e["category"]] += 1
    breaking = [e for e in entries if e["category"] in ("breaking change", "removal")]
    deprecations = []
    for e in entries:
        if e["category"] != "deprecation":
            continue
        rv = None
        for rx in REMOVAL_VERSION_RES:
            m = rx.search(e["text"])
            if m:
                rv = m.group("ver")
                break
        deprecations.append({"line": e["line"], "cue": e["cue"], "text": e["text"], "removal_version": rv})
    security = [{"line": e["line"], "cue": e["cue"], "text": e["text"], "ids": _all_ids(e["text"])}
                for e in entries if e["category"] == "security fix"]
    advisories = _all_ids(section_text)
    bug_fixes = 0
    for e in entries:
        if e["category"] == "bug fix":
            m = FIX_COUNT_RE.search(e["text"])
            bug_fixes += int(m.group(1)) if m else 1

    # -- semver consistency
    to_major = parse_version(version)["major"] if version else None
    from_major = parse_version(prior)["major"] if prior else None
    cons = {"checked": False, "flag": False, "severity": None, "reason": None}
    if bump is None:
        cons["reason"] = "not checked: prior or current version unknown"
    elif bump in ("calver", "downgrade"):
        cons["reason"] = "not checked: bump is %s" % bump
    else:
        cons["checked"] = True
        n_rm = sum(1 for e in breaking if e["category"] == "removal")
        if breaking and bump != "major":
            cons["flag"] = True
            if bump == "prerelease":
                cons["severity"] = "info"
                cons["reason"] = ("%d breaking-change entries (%d removals) on a pre-release bump %s -> %s; "
                                  "SemVer §9: pre-release versions need not satisfy compatibility"
                                  % (len(breaking), n_rm, prior, version))
            elif to_major == 0 and bump == "minor":
                cons["severity"] = "info"
                cons["reason"] = ("%d breaking-change entries (%d removals) on a 0.x minor bump %s -> %s; "
                                  "SemVer §4: major version zero, anything MAY change (0.x caveat)"
                                  % (len(breaking), n_rm, prior, version))
            else:
                cons["severity"] = "warn"
                cons["reason"] = ("%d breaking-change entries (%d removals) but the bump %s -> %s is %s; "
                                  "SemVer §8 requires a MAJOR bump" % (len(breaking), n_rm, prior, version, bump))
        elif bump == "major" and not breaking:
            cons["flag"] = True
            if from_major == 0:
                cons["severity"] = "info"
                cons["reason"] = ("major bump %s -> %s with no breaking-change entries; 0.x -> 1.0.0 may be a "
                                  "stabilisation release (SemVer §5) — check for unmarked breaking changes"
                                  % (prior, version))
            else:
                cons["severity"] = "warn"
                cons["reason"] = ("major bump %s -> %s but no breaking-change entries were found; check the "
                                  "note for unmarked breaking changes" % (prior, version))
        else:
            cons["reason"] = "consistent: bump %s -> %s is %s with %d breaking-change entries" % (
                prior, version, bump, len(breaking))

    # -- signal strength (SKILL.md rubric)
    if bump == "major" or breaking or advisories or security:
        signal = "high"
    elif counts["new feature"] and bump in ("minor", None, "prerelease", "calver"):
        signal = "medium"
    else:
        signal = "low"

    # -- confidence
    conf, ctrace = 40, ["+40 base"]

    def add(points, why):
        nonlocal conf
        conf += points
        ctrace.append("%+d %s" % (points, why))

    if current and not v_to:
        add(20, "version from a heading in the text")
    elif v_to and current:
        add(20, "version from --to confirmed by a heading")
    elif v_to:
        add(15, "version from --to only (no matching heading)")
    else:
        add(-25, "no version identified")
    if released:
        add(10, "release date found (%s)" % date_src)
    if prior:
        add(5 if prior_inferred else 10, "prior version via %s" % prior_src)
    if used_headings:
        add(10, "recognised section heading(s): %s" % ", ".join(sorted(set(used_headings))))
    markers = sorted({e["cue"] for e in entries if e["cue"] and e["cue"].startswith("marker:")})
    if markers:
        add(5, "explicit marker(s): %s" % ", ".join(markers))
    if not entries:
        add(-10, "no entries found")
    elif counts["other"]:
        add(-(20 * counts["other"] // len(entries)),
            "%d of %d entries unclassified (other)" % (counts["other"], len(entries)))
    if cons["flag"]:
        add(-15 if cons["severity"] == "warn" else -5, "semver-consistency flag (%s)" % cons["severity"])
    conf = max(0, min(100, conf))
    ctrace.append("= %d" % conf)

    event = {
        "event_type": "release",
        "project_name": project,
        "version": version,
        "prior_version": prior,
        "semver_bump": bump,
        "released_date": released,
        "breaking_changes": [e["text"] for e in breaking],
        "new_features": [e["text"] for e in entries if e["category"] == "new feature"],
        "deprecations": [d["text"] for d in deprecations],
        "bug_fixes": bug_fixes,
        "security_advisories": advisories,
        "source_url": source_url,
        "source_grade": source_grade,
        "signal_strength": signal,
        "scheme": scheme,
        "yanked": bool(current and current.get("yanked")),
        "category_counts": counts,
        "entries_total": len(entries),
        "breaking_change_details": [{"line": e["line"], "category": e["category"], "cue": e["cue"],
                                     "text": e["text"]} for e in breaking],
        "deprecation_details": deprecations,
        "security_fix_details": security,
        "semver_consistency": cons,
        "confidence": conf,
        "confidence_trace": ctrace,
        "version_headings": [{"line": h["line"], "version": h["version"], "date": h["date"],
                              "yanked": h["yanked"]} for h in headings],
        "section": {"source": section_src, "start_line": start + 1, "end_line": end},
        "parse_trace": trace,
        "entries": [{"line": e["line"], "category": e["category"], "cue": e["cue"], "text": e["text"]}
                    for e in entries],
    }
    return event


# --- output helpers ----------------------------------------------------------


def dump(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def print_report(ev):
    print("Release: %s%s  (prior %s, bump %s, released %s, scheme %s%s)" % (
        (ev["project_name"] + " ") if ev["project_name"] else "", ev["version"], ev["prior_version"],
        ev["semver_bump"], ev["released_date"], ev["scheme"], ", YANKED" if ev["yanked"] else ""))
    print("Signal strength: %s" % ev["signal_strength"])
    parts = ["%s %d" % (c, n) for c, n in ev["category_counts"].items() if n]
    print("Entries: %d — %s  (bug_fixes=%d)" % (ev["entries_total"], ", ".join(parts) or "none", ev["bug_fixes"]))
    print("Breaking changes (%d):" % len(ev["breaking_change_details"]))
    for d in ev["breaking_change_details"]:
        print("  L%-4d [%s] %s" % (d["line"], d["cue"], d["text"]))
    print("Deprecations (%d):" % len(ev["deprecation_details"]))
    for d in ev["deprecation_details"]:
        print("  L%-4d [%s] %s  -> removal: %s" % (d["line"], d["cue"], d["text"], d["removal_version"] or "not stated"))
    print("Security fixes (%d), advisories: %s" % (len(ev["security_fix_details"]),
                                                    ", ".join(ev["security_advisories"]) or "none"))
    for d in ev["security_fix_details"]:
        print("  L%-4d [%s] %s" % (d["line"], d["cue"], d["text"]))
    c = ev["semver_consistency"]
    print("Semver consistency: %s — %s" % ("FLAG (%s)" % c["severity"] if c["flag"] else "ok", c["reason"]))
    print("Parse trace: " + "; ".join(ev["parse_trace"]))
    print("Confidence: %d/100" % ev["confidence"])
    for t in ev["confidence_trace"]:
        print("  " + t)


def describe_version(v):
    print("input:      %s" % v["input"])
    print("scheme:     %s%s" % (v["scheme"], (" (" + "; ".join(v["notes"]) + ")") if v["notes"] else ""))
    if v["scheme"] == "invalid":
        return
    print("normalized: %s" % v["normalized"])
    print("major:      %d" % v["major"])
    print("minor:      %d" % v["minor"])
    print("patch:      %d" % v["patch"])
    if v["extra"]:
        print("extra:      %s" % ".".join(str(x) for x in v["extra"]))
    kinds = ", ".join("%s %s" % ("numeric" if isinstance(p, int) else "alphanumeric", repr(p)) for p in v["prerelease"])
    print("prerelease: %s" % ((".".join(str(p) for p in v["prerelease"]) + "  [" + kinds + "]") if v["prerelease"] else "(none)"))
    print("build:      %s" % ((".".join(v["build"]) + "  (ignored for precedence, SemVer §10)") if v["build"] else "(none)"))


# --- demo / selftest -----------------------------------------------------------

DEMO_TEXT = """## [2.0.0] - 2026-03-14
### Breaking
- Dropped Python 3.8 support; minimum is now 3.10
- query() now returns a Result object instead of a plain dict
### Added
- Hybrid search (BM25 + vector fusion)
### Deprecated
- search() — use query(); will be removed in 3.0
### Fixed
- 7 fixes, including index corruption on concurrent writes
"""

SELFTEST_TEXT = """## [1.4.3] - 2026-05-02
### Removed
- Removed the legacy `--legacy-auth` flag (see the migration guide)
### Changed
- feat!: `Client.connect()` now returns a `Session` object instead of a tuple
- The `retries` option is deprecated and will be removed in 3.0; use `retry_policy`
- Improved error messages for timeouts
### Fixed
- Fixed a race in the connection pool (#412)
- 3 fixes to CLI argument parsing
### Security
- Patched a header-injection vulnerability (CVE-2026-1234)

BREAKING CHANGE: configuration files must now be TOML; JSON configs are rejected

## [1.4.2] - 2026-04-20
### Fixed
- Fixed a typo in the README
"""


def run_selftest():
    """Hand-verified checks: SemVer 2.0.0 §11 ordering example, bump kinds, sample scan."""
    n = [0]

    def check(name, got, want):
        n[0] += 1
        ok = got == want
        print("%s  %s: got %r, expected %r" % ("PASS" if ok else "FAIL", name, got, want))
        if not ok:
            print("SELFTEST FAILED at: %s" % name, file=sys.stderr)
            sys.exit(1)

    # SemVer 2.0.0 §11.4 ordering example (verbatim chain from the spec).
    chain = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta", "1.0.0-beta.2",
             "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]
    for a, b in zip(chain, chain[1:]):
        check("§11.4 %s < %s" % (a, b), compare_versions(a, b), -1)
        check("§11.4 %s > %s" % (b, a), compare_versions(b, a), 1)
    shuffled = ["1.0.0", "1.0.0-beta.11", "1.0.0-alpha.1", "1.0.0-rc.1", "1.0.0-beta.2",
                "1.0.0-alpha.beta", "1.0.0-beta", "1.0.0-alpha"]
    check("§11.4 sort reproduces the spec chain",
          sorted(shuffled, key=functools.cmp_to_key(compare_versions)), chain)
    # §11.2 core numeric ordering, §10 build metadata ignored, §11.4.1/§11.4.3 details.
    core = ["1.0.0", "2.0.0", "2.1.0", "2.1.1"]
    for a, b in zip(core, core[1:]):
        check("§11.2 %s < %s" % (a, b), compare_versions(a, b), -1)
    check("§10 build metadata ignored", compare_versions("1.0.0+20130313144700", "1.0.0"), 0)
    check("§10 build metadata ignored (pre-release)", compare_versions("1.0.0-alpha+001", "1.0.0-alpha"), 0)
    check("§11.4.1 numeric identifiers compare numerically (2 < 10)", compare_versions("1.0.0-alpha.2", "1.0.0-alpha.10"), -1)
    check("§11.4.3 numeric < alphanumeric", compare_versions("1.0.0-1", "1.0.0-a"), -1)
    check("§11.4.3 rule name", compare_explain(parse_version("1.0.0-1"), parse_version("1.0.0-a"))[1][:7], "§11.4.3")
    check("§9 numeric identifier with leading zero is not strict semver", parse_version("1.0.0-01")["scheme"], "semver-loose")
    check("§2 leading zeros invalid -> loose", parse_version("1.01.0")["scheme"], "semver-loose")
    # parse
    p = parse_version("v2.3.1-beta.2+build.5")
    check("parse major/minor/patch", (p["major"], p["minor"], p["patch"]), (2, 3, 1))
    check("parse pre-release identifiers (numeric typed)", p["prerelease"], ["beta", 2])
    check("parse build metadata", p["build"], ["build", "5"])
    check("parse leading v -> semver-loose with note", (p["scheme"], p["notes"]), ("semver-loose", ["leading 'v' stripped"]))
    check("parse strict", parse_version("1.0.0-alpha")["scheme"], "semver")
    check("parse invalid", parse_version("banana")["scheme"], "invalid")
    check("parse calver 2026.04.01", parse_version("2026.04.01")["scheme"], "calver?")
    check("parse calver 24.04", parse_version("24.04")["scheme"], "calver?")
    check("parse two-component 3.0 padded", (parse_version("3.0")["scheme"], parse_version("3.0")["normalized"]), ("semver-loose", "3.0.0"))
    # bump
    for a, b, want in [("1.4.2", "2.0.0", "major"), ("1.4.2", "1.5.0", "minor"), ("1.4.2", "1.4.3", "patch"),
                       ("1.0.0-rc.1", "1.0.0", "prerelease"), ("1.0.0-alpha", "1.0.0-beta", "prerelease"),
                       ("1.0.0", "1.0.0", "none"), ("v1.2.3", "1.2.3+build.9", "none"),
                       ("2.0.0", "1.9.3", "downgrade"), ("2026.04.01", "2026.05.01", "calver"),
                       ("0.2.17", "0.3.0", "minor"), ("1.9.3", "2.0.0-rc.1", "major")]:
        check("bump %s -> %s" % (a, b), classify_bump(parse_version(a), parse_version(b)), want)
    # dates and headings
    check("date Month D, YYYY", to_iso_date("March 14, 2026"), "2026-03-14")
    check("date D Month YYYY", to_iso_date("released 14 March 2026"), "2026-03-14")
    check("date ISO", to_iso_date("## [2.0.0] - 2026-03-14"), "2026-03-14")
    vh = parse_version_heading("## v2.0.0 (March 14, 2026)")
    check("version heading with parenthesised date", (vh["version"], vh["date"]), ("2.0.0", "2026-03-14"))
    vh = parse_version_heading("## [0.0.5] - 2014-12-13 [YANKED]")
    check("yanked heading", (vh["version"], vh["yanked"]), ("0.0.5", True))
    check("unreleased heading", parse_version_heading("## [Unreleased]")["unreleased"], True)
    check("sentence with a version is not a heading", parse_version_heading("Requires Python 3.10 or later"), None)
    check("'will be removed in 3.0' is not a heading", parse_version_heading("will be removed in 3.0"), None)
    check("heading map: emoji stripped", classify_heading("🐛 Bug Fixes"), ("bug fix", True))
    check("heading map: KaC Removed", classify_heading("Removed"), ("removal", True))
    check("heading map: mixed heading is non-final", classify_heading("Fixes and improvements"), ("bug fix", False))
    # entry classification
    for text, heading, want in [
        ("feat!: drop node 14", None, ("breaking change", "marker:type! (Conventional Commits rule 13)")),
        ("BREAKING CHANGE: config is now TOML", ("bug fix", True, "fixed"), ("breaking change", "marker:BREAKING CHANGE token")),
        ("Fixed XSS in templates (CVE-2026-0001)", ("bug fix", True, "fixed"), ("security fix", "marker:CVE/GHSA id")),
        ("Renamed `foo` to `bar`", ("enhancement", False, "changed"), ("breaking change", "phrase:breaking wording")),
        ("Removed deprecated ConversationalRetrievalChain; use RunnableWithMessageHistory", None, ("removal", "phrase:removed/dropped")),
        ("initialize_agent is deprecated; will be removed in 0.4", ("new feature", False, "added"), ("deprecation", "phrase:future removal")),
        ("fix: no longer crashes on empty input", None, ("bug fix", "type:fix")),
        ("The parser no longer crashes on empty input", ("bug fix", True, "fixed"), ("bug fix", "section:fixed")),
        ("Bump lodash from 4.17.20 to 4.17.21", None, ("dependency bump", "phrase:dependency wording")),
        ("chore(deps): bump lodash", None, ("dependency bump", "type:chore")),
        ("Improve query latency by 30%", None, ("performance", "phrase:performance wording")),
        ("Fixed a typo in the README", None, ("docs", "phrase:docs wording")),
        ("Add support for Python 3.13", None, ("new feature", "phrase:feature wording")),
        ("Hybrid search (BM25 + vector fusion)", ("new feature", False, "added"), ("new feature", "section:added")),
        ("Patched GHSA-jfh8-c2jp-5v3q", None, ("security fix", "marker:CVE/GHSA id")),
        ("Rewrote the build script", None, ("other", None)),
    ]:
        check("classify %r" % text[:40], classify_entry(text, heading), want)
    check("classify: URL/doc pointer does not decide", classify_entry("New export button (see the docs: https://x.io/docs/export)", None)[0], "new feature")
    ents, _ = extract_entries(["- Core", "  - Added X", "  - Fixed Y", "    (details of Y)", "- Breaking changes:",
                               "  - Renamed foo to bar", "- New export button", "  - supports CSV", "**Bug fixes**",
                               "- Fixed export crash", "Deprecated:", "- The `legacy` flag"], 0, 12)
    check("nesting: group label children are entries, elaborations merge, bold/colon headings apply",
          [(e["text"], e["heading"][0] if e["heading"] else None) for e in ents],
          [("Added X", None), ("Fixed Y (details of Y)", None), ("Renamed foo to bar", "breaking change"),
           ("New export button supports CSV", None), ("Fixed export crash", "bug fix"), ("The `legacy` flag", "deprecation")])
    check("advisory ids sorted+normalised", _all_ids("cve-2026-2 fix, CVE-2026-1234, ghsa-JFH8-C2JP-5V3Q"),
          ["CVE-2026-1234", "GHSA-jfh8-c2jp-5v3q"])

    # SKILL.md worked example (--demo) must reproduce the JSON in SKILL.md.
    ev = scan(DEMO_TEXT, v_from="1.9.3", project="vectordb-lite", source_grade="B1")
    check("demo version/prior/bump", (ev["version"], ev["prior_version"], ev["semver_bump"]), ("2.0.0", "1.9.3", "major"))
    check("demo date", ev["released_date"], "2026-03-14")
    check("demo breaking changes verbatim", ev["breaking_changes"],
          ["Dropped Python 3.8 support; minimum is now 3.10", "query() now returns a Result object instead of a plain dict"])
    check("demo new features", ev["new_features"], ["Hybrid search (BM25 + vector fusion)"])
    check("demo deprecations", ev["deprecations"], ["search() — use query(); will be removed in 3.0"])
    check("demo removal horizon", ev["deprecation_details"][0]["removal_version"], "3.0")
    check("demo bug_fixes counts '7 fixes'", ev["bug_fixes"], 7)
    check("demo no advisories", ev["security_advisories"], [])
    check("demo signal high", ev["signal_strength"], "high")
    check("demo consistency ok", ev["semver_consistency"]["flag"], False)
    # 40 base +20 heading +10 date +10 --from +10 recognised headings (no markers) = 90
    check("demo confidence", ev["confidence"], 90)

    # Sample changelog: BREAKING CHANGE footer, feat!:, deprecation w/ horizon, CVE, KaC Removed.
    ev = scan(SELFTEST_TEXT)
    check("sample version from highest heading", ev["version"], "1.4.3")
    check("sample prior inferred from next-lower heading", ev["prior_version"], "1.4.2")
    check("sample bump patch", ev["semver_bump"], "patch")
    check("sample section excludes the 1.4.2 block", ev["section"], {"source": "heading", "start_line": 2, "end_line": 15})
    check("sample counts", ev["category_counts"],
          {"breaking change": 2, "deprecation": 1, "removal": 1, "new feature": 0, "enhancement": 1,
           "bug fix": 2, "security fix": 1, "performance": 0, "docs": 0, "dependency bump": 0, "other": 0})
    check("sample breaking cues", [d["cue"] for d in ev["breaking_change_details"]],
          ["section:removed", "marker:type! (Conventional Commits rule 13)", "marker:BREAKING CHANGE token"])
    check("sample breaking list incl. removal (SemVer §8)", len(ev["breaking_changes"]), 3)
    check("sample deprecation horizon", ev["deprecation_details"][0]["removal_version"], "3.0")
    check("sample CVE captured", ev["security_advisories"], ["CVE-2026-1234"])
    check("sample bug_fixes = 1 + 3", ev["bug_fixes"], 4)
    check("sample consistency flag fires (patch bump with breaking changes)",
          (ev["semver_consistency"]["flag"], ev["semver_consistency"]["severity"]), (True, "warn"))
    check("sample signal high", ev["signal_strength"], "high")
    # 40 base +20 heading +10 date +5 inferred prior +10 headings +5 markers -15 warn flag = 75
    check("sample confidence", ev["confidence"], 75)
    check("sample exit code would be 1", exit_code_for(ev), 1)
    # Flag also fires the other way round, and 0.x is only informational.
    ev = scan("## 2.0.0 - 2026-01-01\n### Added\n- New dashboard\n", v_from="1.9.0")
    check("major bump without breaking entries -> warn", (ev["semver_consistency"]["flag"], ev["semver_consistency"]["severity"]), (True, "warn"))
    ev = scan("## 0.3.0 - 2026-01-01\n### Removed\n- Removed the beta API\n", v_from="0.2.17")
    check("0.x minor bump with breaking -> info", (ev["semver_consistency"]["flag"], ev["semver_consistency"]["severity"]), (True, "info"))
    check("0.x info flag exits 0", exit_code_for(ev), 0)
    ev = scan("## v0.3.0\n- feat: x\n\n**Full Changelog**: https://example.com/compare/v0.2.17...v0.3.0\n")
    check("prior version from compare link", (ev["prior_version"], ev["semver_bump"]), ("0.2.17", "minor"))
    ev = scan("## v0.3.0\nChanges since 0.2.17:\n- feat: x\n")
    check("prior version from 'since' phrase", ev["prior_version"], "0.2.17")
    ev = scan("This release drops support for Node 14. It also fixes CVE-2026-4242 in the parser.", v_from="4.8.1", v_to="5.0.0")
    check("prose: sentences are separate entries", [e["category"] for e in ev["entries"]], ["removal", "security fix"])
    check("prose: major bump with a removal is consistent", ev["semver_consistency"]["flag"], False)
    ev = scan("- Fixed a crash\n- Fixed a leak\n")
    check("no version: bump unknown, consistency unchecked, low signal",
          (ev["version"], ev["semver_bump"], ev["semver_consistency"]["checked"], ev["signal_strength"]), (None, None, False, "low"))
    check("no version: confidence (40 - 25)", ev["confidence"], 15)
    # Determinism: two scans of the same text are identical.
    check("deterministic output (two scans byte-identical)",
          json.dumps(scan(SELFTEST_TEXT)) == json.dumps(scan(SELFTEST_TEXT)), True)
    print("selftest OK (%d checks)" % n[0])
    return 0


def exit_code_for(ev):
    c = ev["semver_consistency"]
    return 1 if c["flag"] and c["severity"] == "warn" else 0


# --- CLI ---------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(description="SemVer 2.0.0 arithmetic and cue-based release-note tagging "
                                "(ReleaseEvent JSON per SKILL.md).")
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true", help="scan the SKILL.md worked example and print its ReleaseEvent")
    sub = parser.add_subparsers(dest="command")
    sv = sub.add_parser("semver", help="parse | compare | bump (Semantic Versioning 2.0.0)")
    svs = sv.add_subparsers(dest="semver_command")
    p = svs.add_parser("parse", help="split a version into its components")
    p.add_argument("version")
    p.add_argument("--json", action="store_true")
    p = svs.add_parser("compare", help="precedence of A vs B (§11); prints <, = or >")
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--json", action="store_true")
    p = svs.add_parser("bump", help="major | minor | patch | prerelease | none (| downgrade | calver)")
    p.add_argument("from_version", metavar="FROM")
    p.add_argument("to_version", metavar="TO")
    p.add_argument("--json", action="store_true")
    s = sub.add_parser("scan", help="tag a release note / changelog and emit the ReleaseEvent JSON")
    s.add_argument("--file", help="path to the note (Markdown/plain text); '-' reads stdin")
    s.add_argument("--text", help="the note as a string")
    s.add_argument("--from", dest="v_from", metavar="VERSION", help="prior version (else inferred)")
    s.add_argument("--to", dest="v_to", metavar="VERSION", help="this release's version (else from headings)")
    s.add_argument("--project", help="project_name for the ReleaseEvent")
    s.add_argument("--source-url", help="source_url for the ReleaseEvent")
    s.add_argument("--source-grade", help="Admiralty grade from rate-source-admiralty (pass-through)")
    s.add_argument("--json", action="store_true", help="JSON output (the default)")
    s.add_argument("--report", action="store_true", help="human-readable report instead of JSON")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo:
        dump(scan(DEMO_TEXT, v_from="1.9.3", project="vectordb-lite", source_grade="B1"))
        return 0
    if args.command == "semver":
        if not args.semver_command:
            parser.error("choose: semver parse | compare | bump")
        if args.semver_command == "parse":
            v = parse_version(args.version)
            if args.json:
                dump(v)
            else:
                describe_version(v)
            return 0 if v["scheme"] != "invalid" else 1
        if args.semver_command == "compare":
            a, b = parse_version(args.a), parse_version(args.b)
            if "invalid" in (a["scheme"], b["scheme"]):
                parser.error("cannot parse %r" % (args.a if a["scheme"] == "invalid" else args.b))
            c, rule = compare_explain(a, b)
            sym = {-1: "<", 0: "=", 1: ">"}[c]
            if args.json:
                dump({"a": a["normalized"], "b": b["normalized"], "result": sym, "cmp": c, "rule": rule,
                      "scheme_a": a["scheme"], "scheme_b": b["scheme"]})
            else:
                print("%s %s %s   (SemVer 2.0.0 %s)" % (a["normalized"], sym, b["normalized"], rule))
            return 0
        a, b = parse_version(args.from_version), parse_version(args.to_version)
        if "invalid" in (a["scheme"], b["scheme"]):
            parser.error("cannot parse %r" % (args.from_version if a["scheme"] == "invalid" else args.to_version))
        kind = classify_bump(a, b)
        notes = ["from: " + n for n in a["notes"]] + ["to: " + n for n in b["notes"]]
        if args.json:
            dump({"from": a["normalized"], "to": b["normalized"], "bump": kind,
                  "scheme_from": a["scheme"], "scheme_to": b["scheme"], "notes": notes})
        else:
            print("%s -> %s: %s   (scheme %s -> %s%s)" % (a["normalized"], b["normalized"], kind, a["scheme"],
                                                          b["scheme"], ("; " + "; ".join(notes)) if notes else ""))
        return 0
    if args.command == "scan":
        if args.text is not None:
            text = args.text
        elif args.file == "-":
            text = sys.stdin.read()
        elif args.file:
            try:
                with open(args.file, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError as exc:
                parser.error("could not read %s: %s" % (args.file, exc))
        else:
            parser.error("pass --file PATH (or '-') or --text STRING")
        for flag, val in (("--from", args.v_from), ("--to", args.v_to)):
            if val and parse_version(val)["scheme"] == "invalid":
                parser.error("%s: cannot parse version %r" % (flag, val))
        ev = scan(text, v_from=args.v_from, v_to=args.v_to, project=args.project,
                  source_url=args.source_url, source_grade=args.source_grade)
        if args.report:
            print_report(ev)
        else:
            dump(ev)
        return exit_code_for(ev)
    parser.error("choose a command: semver | scan  (or --selftest / --demo)")


if __name__ == "__main__":
    sys.exit(main())
