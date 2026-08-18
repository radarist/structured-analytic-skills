#!/usr/bin/env python3
"""Deterministic multidimensional scorer for the skill library.

Every check is mechanical (regex / file-system / subprocess) — no model, no
human judgment — so two runs on the same tree produce byte-identical scores
and every lost point maps to a named, fixable check.

Twelve dimensions per skill (weights sum to 100):

  D1  spec            Agent Skills spec compliance (frontmatter, name, size)
  D2  discoverability description triggers, third person, discriminability
  D3  procedure       numbered, substantive, ordered steps
  D4  output          copy-ready output template / schema
  D5  boundaries      explicit do-not-invoke cases with sibling routing
  D6  crosslinks      pair-with section, resolving refs, methodology link
  D7  example         concrete worked example (numbers, names, output)
  D8  verification    how the output gets checked before it ships
  D9  provenance      reference section with dated, attributable sources
  D10 tooling         companion script quality (selftest, help, determinism)
  D11 efficiency      token budget / progressive disclosure
  D12 hygiene         self-containment, links, headings, no placeholders

Library score = 0.85 x mean(skill totals) + 0.15 x repo-hygiene score.

Usage:
  python3 evaluation/score_skills.py                 # score, write scores/latest.{json,md}
  python3 evaluation/score_skills.py --skill NAME    # detailed per-check report for one skill
  python3 evaluation/score_skills.py --baseline evaluation/scores/baseline.json
  python3 evaluation/score_skills.py --min-score 90 --min-library 90   # CI gate (exit 1 below)
  python3 evaluation/score_skills.py --no-exec       # skip subprocess checks (tooling scored from static evidence only)

Stdlib only. Python 3.9+.
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_repo  # noqa: E402  (shared denylists / regexes)

# --------------------------------------------------------------------------
# Configuration (all of it is visible here — no hidden knobs)
# --------------------------------------------------------------------------

WEIGHTS = {
    "D1_spec": 10, "D2_discoverability": 12, "D3_procedure": 12, "D4_output": 10,
    "D5_boundaries": 8, "D6_crosslinks": 8, "D7_example": 10, "D8_verification": 8,
    "D9_provenance": 8, "D10_tooling": 8, "D11_efficiency": 3, "D12_hygiene": 3,
}
assert sum(WEIGHTS.values()) == 100

# Frontmatter keys permitted by the Agent Skills specification (agentskills.io).
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "compatibility",
                            "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024
BODY_MAX_LINES = 500          # Anthropic authoring guidance: keep SKILL.md under 500 lines
BODY_WORDS_FULL = 1600        # full efficiency credit at or below this
BODY_WORDS_ZERO = 3200        # zero efficiency credit above this (unless references/ used)

# Skills whose method contains real arithmetic; a companion tool is expected.
# Everything else is language/judgment work where a script adds nothing, and
# D10 scores N/A (= full credit) for them. Kept explicit so it can be audited.
COMPUTATIONAL_SKILLS = {
    "analysis-of-competing-hypotheses", "assess-research-momentum", "bayesian-update",
    "brier-score-calibration", "cross-impact-analysis", "delphi-method",
    "estimate-market-size", "meta-analysis", "quantitative-sanity-check",
    "smiles-sanity-check", "systematic-review", "test-significance",
    "chemistry-claim-check", "verify-citations", "assess-study-bias",
    "evidence-appraisal", "experimental-design", "cite-ieee", "read-patent-landscape",
    "analyze-patent-claims", "detect-funding-round", "detect-ma-event",
    "score-technology-readiness", "rate-source-admiralty", "oss-project-health",
    "trend-analysis", "analyze-release-notes", "position-competitor",
    # added in the 2026-08 coverage pass
    "estimative-language", "reference-class-forecasting", "indicators-validation",
    "decision-matrix-mcda", "expected-value-decision-tree", "morphological-analysis",
    "amstar2-review-appraisal", "value-intellectual-property",
}

# Origin-system jargon that must not leak into a self-contained skill.
JARGON = [
    "landscape report", "Signal of type", "the mission", "mission report",
    "entity graph", "knowledge graph", "the graph yet", "auto-apply",
    "signal for triage", "approved for import", "trust ledger", "proposal evidence",
    "relationship claim", "radar report", "the Curator", "the Strategist",
    "sourceUrl", "needs_review", "in the graph",
]

STOPWORDS = set("""a an the and or of to in for on with by at from as is are be this that these those
it its into when use used using before after any all each per than then so if not no do does
their there which who whom what where why how can could should would will may might must
also more most less least such via vs versus i you we they them he she your our one two
""".split())

PRODUCTION_VERBS = re.compile(
    r"\b(produc\w*|emit\w*|return\w*|output\w*|scor\w*|grad\w*|rank\w*|classif\w*|comput\w*|"
    r"check\w*|draft\w*|writ\w*|map\w*|estimat\w*|detect\w*|pars\w*|rate\w*|revis\w*|"
    r"generat\w*|build\w*|assess\w*|test\w*|verif\w*|decompos\w*|pool\w*|convert\w*|"
    r"turn\w* .{0,40} into|deliver\w*|report\w*|place\w*|tag\w*|flag\w*|surface\w*)\b", re.I)

BOUNDARY_RE = re.compile(
    r"(do not invoke|don'?t invoke|do not use (this|it|when|for)|not for\b|skip (for|when|if|this)|"
    r"when not to (use|invoke|run)|do not run|route\w* .{0,80}? to|out of scope|instead\.)", re.I)
VERIFY_HEAD_RE = re.compile(r"^##+\s+.*(verif|self-check|self check|quality gate|checks?\b|before (emitting|reporting|shipping|you emit)|validation)", re.I | re.M)
VERIFY_SENT_RE = re.compile(r"\b(verify|recompute|re-compute|check that|must resolve|cross-check|re-run|rerun|assert|confirm that|reconcile|must sum|must equal|must agree)\b", re.I)
EXAMPLE_HEAD_RE = re.compile(r"^##+\s+.*(example|worked|illustrat|walk-?through)", re.I | re.M)
OUTPUT_HEAD_RE = re.compile(r"^##+\s+.*(output|emit|template|schema|format|deliverable|report shape|result)", re.I | re.M)
PAIR_HEAD_RE = re.compile(r"^##+\s+.*(pair(s|ed)? with|working with other|related skills|adjacent skills|see also|companion skills)", re.I | re.M)
REF_HEAD_RE = re.compile(r"^##+\s+.*(reference|sources|further reading|bibliography|citations)", re.I | re.M)
STEP_HEAD_RE = re.compile(r"^#{2,4}\s+(?:step\s*)?(\d+)\s*[—–\-\.:)]", re.I | re.M)
ORDERED_ITEM_RE = re.compile(r"^\s{0,3}(\d+)[.)]\s+\S", re.M)
FENCE_RE = re.compile(r"^```[^\n]*\n(.*?)^```", re.M | re.S)
YEAR_RE = re.compile(r"\b(1[89]\d{2}|20[0-2]\d)\b")
AUTHOR_RE = re.compile(r"(\b[A-Z]\.\s?[A-Z]?\.?\s?[A-Z][a-z]+\b|\b[A-Z][a-z]+,\s[A-Z]\.|\b[A-Z][a-z]+ (and|&) [A-Z][a-z]+\b|\bet al\.)")
LOCATOR_RE = re.compile(r"(doi\.org/|\bdoi:|arXiv:|\bISBN\b|https?://|\bvol\.|\bpp\.|\bno\.)", re.I)
BACKTICK_KEBAB_RE = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`")
PLACEHOLDER_RE = re.compile(r"\b(TODO|FIXME|XXX|TBD|lorem ipsum)\b")
QUOTED_RE = re.compile(r"[\"“”‘’']([^\"“”‘’']{3,80})[\"“”‘’']|`([^`]{2,60})`")

# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def parse_frontmatter(text):
    """Minimal YAML-subset parser: `key: value`, quoted scalars, `>`/`|` blocks,
    inline lists, and one level of nested mapping. Returns (dict, problems)."""
    problems = []
    if not text.startswith("---\n"):
        return {}, ["frontmatter must start with '---' on line 1"]
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, ["frontmatter closing '---' not found"]
    block = text[4:end].split("\n")
    data, seen = {}, set()
    i = 0
    while i < len(block):
        line = block[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            problems.append("unparseable frontmatter line: %r" % line[:60])
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if key in seen:
            problems.append("duplicate frontmatter key: %s" % key)
        seen.add(key)
        if val in (">", "|", ">-", "|-"):
            buf = []
            i += 1
            while i < len(block) and (block[i].startswith("  ") or not block[i].strip()):
                buf.append(block[i].strip())
                i += 1
            data[key] = " ".join(b for b in buf if b) if val.startswith(">") else "\n".join(buf)
            continue
        if val == "":
            sub = {}
            i += 1
            while i < len(block) and (block[i].startswith("  ") or not block[i].strip()):
                sm = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", block[i])
                if sm:
                    sub[sm.group(1)] = sm.group(2).strip().strip("'\"")
                elif block[i].strip():
                    problems.append("unparseable nested line: %r" % block[i][:60])
                i += 1
            data[key] = sub
            continue
        if val.startswith("[") and val.endswith("]"):
            data[key] = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
        else:
            if val.startswith('"') and val.endswith('"'):
                try:
                    val = json.loads(val)
                except ValueError:
                    problems.append("invalid JSON-quoted scalar for %s" % key)
                    val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1].replace("''", "'")
            data[key] = val
        i += 1
    return data, problems


def body_of(text):
    end = text.find("\n---\n", 4)
    return text[end + 5:] if text.startswith("---\n") and end >= 0 else text


def mask_fences(text):
    """Return text of identical length where every '#' inside a fenced code
    block is replaced by '\u00a7', so heading regexes ignore code blocks."""
    out, inside = [], False
    for line in text.split("\n"):
        if line.startswith("```"):
            inside = not inside
            out.append(line)
        elif inside:
            out.append(line.replace("#", "\u00a7"))
        else:
            out.append(line)
    return "\n".join(out)


def sections(text, head_re):
    """Every section whose heading matches head_re, in document order.

    A section runs from its heading to the next heading of the same or higher
    level. Headings inside fenced code blocks are ignored. Checks are evaluated
    across ALL matching sections and the best result is taken: the question a
    check asks is "does this skill contain a copy-ready output template / a
    verification checklist / a worked example at all", not "does the first
    heading that happens to contain the word 'format' contain one".
    """
    masked = mask_fences(text)
    out = []
    for m in head_re.finditer(masked):
        level = len(re.match(r"#+", masked[m.start():]).group(0))
        nxt = re.compile(r"^#{1,%d}\s" % level, re.M).search(masked, m.end())
        out.append(text[m.start(): nxt.start() if nxt else len(text)])
    return out


def section(text, head_re):
    """The shallowest matching section (earliest on ties), or ''."""
    masked = mask_fences(text)
    best = None
    for m in head_re.finditer(masked):
        level = len(re.match(r"#+", masked[m.start():]).group(0))
        if best is None or level < best[0]:
            best = (level, m)
    if not best:
        return ""
    level, m = best
    nxt = re.compile(r"^#{1,%d}\s" % level, re.M).search(masked, m.end())
    return text[m.start(): nxt.start() if nxt else len(text)]


def tokens(s):
    return [t for t in re.findall(r"[a-z][a-z0-9]+", s.lower()) if t not in STOPWORDS and len(t) > 2]


def cosine(a, b):
    num = sum(a[k] * b.get(k, 0.0) for k in a)
    da = math.sqrt(sum(v * v for v in a.values())); db = math.sqrt(sum(v * v for v in b.values()))
    return num / (da * db) if da and db else 0.0


def tfidf(descs):
    """descs: {name: text} -> {name: {token: weight}} (log-scaled tf-idf)."""
    df = Counter()
    toks = {n: tokens(d) for n, d in descs.items()}
    for n, ts in toks.items():
        df.update(set(ts))
    N = len(descs)
    vecs = {}
    for n, ts in toks.items():
        tf = Counter(ts)
        vecs[n] = {t: (1 + math.log(c)) * math.log((N + 1) / (df[t] + 1)) for t, c in tf.items()}
    return vecs


def words(s):
    return len(re.findall(r"\S+", s))


class Checks:
    """Accumulates (id, passed, points, max_points, note) for one dimension."""

    def __init__(self):
        self.items = []
        self.not_applicable = False

    def add(self, cid, ok, pts, note=""):
        self.items.append({"id": cid, "pass": bool(ok), "points": pts if ok else 0,
                           "max": pts, "note": note})

    def score(self):
        mx = sum(i["max"] for i in self.items)
        got = sum(i["points"] for i in self.items)
        return round(100.0 * got / mx, 1) if mx else 100.0


# --------------------------------------------------------------------------
# Per-dimension scoring
# --------------------------------------------------------------------------

def d1_spec(name, text, fm, fm_problems, body):
    c = Checks()
    c.add("D1.frontmatter-parses", not fm_problems, 3, "; ".join(fm_problems)[:200])
    c.add("D1.name-present", bool(fm.get("name")), 2)
    nm = str(fm.get("name", ""))
    c.add("D1.name-matches-dir", nm == name, 2, "name=%r dir=%r" % (nm, name))
    c.add("D1.name-format", bool(NAME_RE.match(nm)) and len(nm) <= NAME_MAX, 2,
          "lowercase letters/digits/hyphens, <=64 chars")
    desc = str(fm.get("description", ""))
    c.add("D1.description-present", bool(desc.strip()), 3)
    c.add("D1.description-length", 0 < len(desc) <= DESCRIPTION_MAX, 2, "%d chars (max %d)" % (len(desc), DESCRIPTION_MAX))
    unknown = sorted(set(fm) - ALLOWED_FRONTMATTER_KEYS)
    c.add("D1.no-unknown-keys", not unknown, 2, "unknown: %s" % ", ".join(unknown))
    lines = body.count("\n") + 1
    c.add("D1.body-under-500-lines", lines <= BODY_MAX_LINES, 2, "%d lines" % lines)
    c.add("D1.has-h1-title", bool(re.search(r"^# \S", body, re.M)), 1)
    c.add("D1.no-crlf-tabs", ("\r" not in text) and ("\t" not in body), 1)
    return c


def d2_discoverability(name, fm, vecs, all_names, trig=None):
    c = Checks()
    desc = str(fm.get("description", ""))
    c.add("D2.trigger-clause", bool(re.search(r"\b(Use|Invoke|Run|Apply) (it |this |the skill )?(when|whenever|before|after|for|if|to)\b", desc)), 3,
          "description should contain an explicit 'Use when …' triggering clause")
    c.add("D2.third-person", not re.search(r"\b(I|I'm|I'll|you|your|you're|we|our|let's)\b", desc), 3,
          "no first/second person in description")
    quoted = [q for q in QUOTED_RE.findall(desc)]
    c.add("D2.concrete-triggers", len(quoted) >= 2, 3, "%d quoted/backticked trigger phrases (need >=2)" % len(quoted))
    c.add("D2.states-output", bool(PRODUCTION_VERBS.search(desc)), 2, "should say what it produces")
    c.add("D2.length-band", 200 <= len(desc) <= 700, 2, "%d chars (target 200-700; listing budget)" % len(desc))
    c.add("D2.exclusion-clause", bool(re.search(r"\b(not for|do not use (for|when)|don't use for|use `[a-z0-9-]+` (instead|for)|instead of|rather than)\b", desc, re.I)), 1,
          "names a near-miss it does NOT cover (anti-trigger)")
    # discriminability: nearest-neighbour cosine similarity among all descriptions
    me = vecs.get(name, {})
    best, best_name = 0.0, ""
    for other in all_names:
        if other == name:
            continue
        s = cosine(me, vecs[other])
        if s > best:
            best, best_name = s, other
    c.add("D2.discriminable", best < 0.45, 3, "nearest=%s sim=%.2f (need <0.45)" % (best_name, best))
    c.add("D2.name-not-generic", not re.search(r"(^|-)(helper|utils?|tools?|misc|general|generic|stuff|things|skill)($|-)", name) and len(name.split("-")) <= 5, 1,
          "no generic words; at most five hyphenated words")
    ps = (trig or {}).get("per_skill", {}).get(name)
    n_pos = ps["positive"] if ps else 0
    n_neg = ps["negative"] if ps else 0
    c.add("D2.eval-cases-present", n_pos >= 3 and n_neg >= 1, 2, "evals/evals.json: %d positive, %d negative (need >=3 / >=1)" % (n_pos, n_neg))
    ok = bool(ps) and ps["positive_rank1"] == ps["positive"] and ps["negative_ok"] == ps["negative"] and n_pos > 0
    c.add("D2.trigger-rank1", ok, 3, ("; ".join(ps["failures"])[:160] if ps and ps["failures"] else ("no eval cases" if not ps else "")))
    return c


def d3_procedure(body):
    c = Checks()
    step_heads = STEP_HEAD_RE.findall(mask_fences(body))
    n_steps = len(step_heads)
    if n_steps < 3:
        # fall back to an ordered list of substantive items
        items = ORDERED_ITEM_RE.findall(body)
        n_steps = max(n_steps, len(items) if len(items) >= 3 else 0)
    c.add("D3.has-3plus-steps", n_steps >= 3, 4, "%d steps found" % n_steps)
    # ordering: step numbers strictly increasing where headings are used
    nums = [int(x) for x in step_heads]
    ordered = all(b == a + 1 for a, b in zip(nums, nums[1:])) if nums else n_steps >= 3
    c.add("D3.steps-ordered", ordered, 2, "numbering must be consecutive")
    # substance: mean words per step section
    if step_heads:
        parts = STEP_HEAD_RE.split(mask_fences(body))
        # split leaves [pre, num, text, num, text, ...]
        texts = parts[2::2]
        mean_words = sum(words(t) for t in texts) / max(1, len(texts))
        min_words = min(words(t) for t in texts) if texts else 0
    else:
        mean_words, min_words = (40, 20) if n_steps >= 3 else (0, 0)
    c.add("D3.steps-substantive", mean_words >= 30, 3, "mean %.0f words/step (need >=30)" % mean_words)
    c.add("D3.no-empty-steps", min_words >= 8, 1, "shortest step %d words" % min_words)
    c.add("D3.procedure-heading", bool(re.search(r"^##\s+.*(procedure|steps|method|how to|process|the .{0,30}(steps|moves|questions|axes|domains|forces|horizons)|run it|do this)", body, re.I | re.M)), 2,
          "a heading that names the procedure")
    return c


def d4_output(body):
    c = Checks()
    secs = sections(body, OUTPUT_HEAD_RE)
    c.add("D4.output-section", bool(secs), 3, "heading naming the output/template/schema")
    good = [f for sec in secs for f in FENCE_RE.findall(sec) if f.count("\n") >= 2]
    c.add("D4.fenced-template", bool(good), 4, "fenced block (>=3 lines) inside an output section")
    tmpl = "\n".join(good) if good else "\n".join(f for f in FENCE_RE.findall(body) if "{" in f or "<" in f)
    c.add("D4.placeholders-or-schema", bool(re.search(r"\{[^}\n]{1,60}\}|<[a-z_ ]{2,40}>|\"[a-z_]+\":", tmpl)), 2,
          "template uses {placeholders}, <slots> or JSON keys")
    joined = "\n".join(secs) if secs else body
    c.add("D4.mandatory-fields-named", bool(re.search(r"(mandatory|required|must (include|contain|state|appear|carry)|every .{0,60} must)", joined, re.I)), 1,
          "the template says which fields are mandatory")
    return c


def d5_boundaries(body, skill_names):
    c = Checks()
    m = BOUNDARY_RE.search(body)
    c.add("D5.negative-triggers", bool(m), 4, "explicit do-not-invoke / skip-for cases")
    routed = False
    if m:
        # any resolving sibling within a window around the first boundary sentence,
        # or anywhere inside a 'When (not) to invoke' section
        window = body[max(0, m.start() - 200): m.end() + 900]
        sec = "\n".join(sections(body, re.compile(r"^##+\s+.*(when to invoke|when not|when to use|scope|boundaries|do not invoke)", re.I | re.M)))
        cands = set(BACKTICK_KEBAB_RE.findall(window)) | set(BACKTICK_KEBAB_RE.findall(sec))
        routed = any(t in skill_names for t in cands)
    c.add("D5.sibling-routing", routed, 4, "names a sibling skill to route out-of-scope cases to")
    return c


# A skill may point at its methodology counterpart either by absolute repository
# URL (canonical: survives `cp -R skills/* .agents/skills/`) or by the legacy
# `../../methodologies/...` relative path. Both capture the repo-relative path.
METHODOLOGY_LINK_RE = re.compile(
    r"\]\((?:\.\./\.\./|https://github\.com/radarist/structured-analytic-skills/blob/main/)"
    r"(methodologies/[^)#\s]+)"
)


def skill_root(path):
    """Repository root for skills/<name>/SKILL.md."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(path))))


def d6_crosslinks(name, path, body, skill_names, meth_index):
    c = Checks()
    secs = sections(body, PAIR_HEAD_RE)
    refs = [t for sec in secs for t in BACKTICK_KEBAB_RE.findall(sec) if t in skill_names and t != name]
    c.add("D6.pair-with-section", bool(secs), 2)
    c.add("D6.two-plus-siblings", len(set(refs)) >= 2, 3, "%d resolving sibling refs" % len(set(refs)))
    all_refs = set(BACKTICK_KEBAB_RE.findall(body))
    dangling = sorted(t for t in all_refs if t not in skill_names and t not in check_repo.SKILL_REF_ALLOWLIST
                      and re.search(r"(?:use|invoke|run|see|pair\w* with|via|route\w* to|escalate to)\s+`%s`" % re.escape(t), body))
    c.add("D6.no-dangling-skill-refs", not dangling, 1, "dangling: %s" % ", ".join(dangling))
    # methodology counterpart. Skills are copied out of the repo one directory at
    # a time, so the canonical link form is the absolute repository URL; the older
    # `../../methodologies/...` relative form is still accepted for compatibility.
    links = [os.path.join(skill_root(path), rel) for rel in METHODOLOGY_LINK_RE.findall(body)]
    resolving = [l for l in links if os.path.exists(os.path.normpath(l))]
    has_counterpart = name in meth_index
    if has_counterpart:
        c.add("D6.methodology-link", bool(resolving), 1, "counterpart exists: %s" % meth_index[name])
        back = any(("skills/%s" % name) in read(l) for l in resolving) if resolving else False
        c.add("D6.methodology-backlink", back, 1, "methodology file should link back to skills/%s" % name)
    else:
        c.add("D6.methodology-link", True, 1, "no methodology counterpart (N/A)")
        c.add("D6.methodology-backlink", True, 1, "N/A")
    return c


def d7_example(body, has_tool):
    c = Checks()
    secs = sections(body, EXAMPLE_HEAD_RE)
    c.add("D7.example-section", bool(secs), 3)
    nums = max((len(re.findall(r"\d", sec)) for sec in secs), default=0)
    c.add("D7.concrete-numbers", nums >= 12, 2, "%d digits in the richest example (need >=12)" % nums)
    caps = max((len(set(re.findall(r"\b[A-Z][a-z]{2,}\b", sec))) for sec in secs), default=0)
    c.add("D7.named-entities", caps >= 6, 1, "%d distinct capitalised names" % caps)
    wds = max((words(sec) for sec in secs), default=0)
    c.add("D7.example-substantive", wds >= 120, 2, "%d words (need >=120)" % wds)
    c.add("D7.structured-example", any(FENCE_RE.search(sec) or re.search(r"^\|.*\|\s*$", sec, re.M) for sec in secs), 1,
          "example shows a table or fenced output")
    if has_tool:
        hay = "\n".join(secs) + "\n".join(sections(body, re.compile(r"^##+\s+.*companion tool", re.I | re.M)))
        c.add("D7.tool-verified", bool(re.search(r"scripts/\w+\.py|--selftest|--demo|reproduc", hay, re.I)), 1,
              "example numbers reproduced with the companion tool")
    else:
        c.add("D7.tool-verified", True, 1, "N/A (no tool)")
    return c


def d8_verification(body):
    c = Checks()
    secs = sections(body, VERIFY_HEAD_RE)
    c.add("D8.verification-section", bool(secs), 4, "a section on how the output is checked")
    items = max((len(re.findall(r"^\s*(?:- \[ \]|- |\d+\.)\s+\S", sec, re.M)) for sec in secs), default=0)
    sents = max((len(VERIFY_SENT_RE.findall(sec)) for sec in secs), default=len(VERIFY_SENT_RE.findall(body)))
    c.add("D8.concrete-checks", max(items, sents) >= 3, 3,
          "%d checklist items / %d verification sentences (need >=3)" % (items, sents))
    c.add("D8.checklist-form", items >= 3, 1, "verification expressed as a checklist")
    return c


def d9_provenance(body):
    c = Checks()
    secs = sections(body, REF_HEAD_RE)
    c.add("D9.reference-section", bool(secs), 3)
    entries = [l for sec in secs for l in sec.splitlines() if re.match(r"^\s*(-|\d+\.|\[\d+\])\s", l)]
    c.add("D9.dated-entry", any(YEAR_RE.search(e) for e in entries), 2, "at least one entry carries a year")
    c.add("D9.attributable-entry", any(AUTHOR_RE.search(e) for e in entries), 1, "author/organisation named")
    c.add("D9.locator", any(LOCATOR_RE.search(e) for e in entries), 1, "venue/DOI/ISBN/URL/vol/pp locator")
    head = body[: min([body.find(h) for h in ("## Reference", "## Sources", "## Further reading") if h in body] or [len(body)])]
    c.add("D9.originator-in-body", bool(YEAR_RE.search(head)), 1,
          "the method's origin is dated in the body, not only in the reference list")
    return c


def d10_tooling(name, skill_dir, body, exec_checks):
    c = Checks()
    scripts_dir = os.path.join(skill_dir, "scripts")
    scripts = sorted(f for f in os.listdir(scripts_dir) if f.endswith(".py")) if os.path.isdir(scripts_dir) else []
    computational = name in COMPUTATIONAL_SKILLS
    if not computational and not scripts:
        # Not applicable -- and NOT the same as scoring full marks. Awarding 8/8
        # for shipping no tooling gave 33 of 69 skills 264 of the 552 available
        # D10 points for free, which inflates every aggregate. The dimension is
        # flagged N/A and its weight is removed from this skill's denominator
        # instead (see score_skill).
        c.not_applicable = True
        c.add("D10.not-applicable", True, 0, "non-computational skill: N/A (weight redistributed)")
        return c
    c.add("D10.tool-present", bool(scripts), 2, "computational skill should ship scripts/*.py")
    if not scripts:
        for cid in ("D10.selftest", "D10.help", "D10.deterministic", "D10.documented", "D10.stdlib-only", "D10.docstring"):
            c.add(cid, False, 1)
        return c
    ok_self = ok_help = ok_det = ok_std = ok_doc = True
    for f in scripts:
        sp = os.path.join(scripts_dir, f)
        src = read(sp)
        if not re.match(r'\s*(#![^\n]*\n)?\s*(""")', src):
            ok_doc = False
        imports = set(re.findall(r"^\s*(?:import|from)\s+([A-Za-z_][\w]*)", src, re.M))
        non_std = imports - STDLIB
        if non_std:
            ok_std = False
        if exec_checks:
            r1 = run([sys.executable, sp, "--selftest"])
            r2 = run([sys.executable, sp, "--selftest"])
            if r1 is None or r1[0] != 0:
                ok_self = False
            if r1 is None or r2 is None or r1[1] != r2[1]:
                ok_det = False
            rh = run([sys.executable, sp, "--help"])
            if rh is None or rh[0] != 0 or "usage" not in rh[1].lower():
                ok_help = False
    documented = all(("scripts/%s" % f) in body for f in scripts)
    c.add("D10.selftest", ok_self, 2, "each script exits 0 on --selftest" + ("" if exec_checks else " (not executed: --no-exec)"))
    c.add("D10.help", ok_help, 1, "--help exits 0 and prints usage")
    c.add("D10.deterministic", ok_det, 1, "two --selftest runs produce identical output")
    c.add("D10.documented", documented, 1, "every script is referenced from SKILL.md")
    c.add("D10.stdlib-only", ok_std, 0.5, "imports only the standard library")
    c.add("D10.docstring", ok_doc, 0.5, "module docstring states purpose/usage")
    return c


def d11_efficiency(body, skill_dir):
    c = Checks()
    w = words(body)
    lines = body.count("\n") + 1
    has_refs_dir = os.path.isdir(os.path.join(skill_dir, "references"))
    if w <= BODY_WORDS_FULL:
        pts = 3
    elif w <= (BODY_WORDS_FULL + BODY_WORDS_ZERO) / 2:
        pts = 2
    elif w <= BODY_WORDS_ZERO:
        pts = 1
    else:
        pts = 0
    if has_refs_dir and pts < 3:
        pts = min(3, pts + 1)  # progressive disclosure credit
    c.add("D11.word-budget", pts == 3, 3, "%d words (full credit <=%d; references/ dir earns +1)" % (w, BODY_WORDS_FULL))
    if pts in (1, 2):
        c.items[-1]["points"] = pts
    heads = [h.strip().lower() for h in re.findall(r"^#{1,6}\s+(.*)$", mask_fences(body), re.M)]
    dups = [h for h, n in Counter(heads).items() if n > 1]
    c.add("D11.no-duplicate-headings", not dups, 1, "dups: %s" % ", ".join(dups)[:100])
    c.add("D11.line-budget", lines <= BODY_MAX_LINES, 1, "%d lines" % lines)
    return c


def d12_hygiene(path, text, body, skill_names):
    c = Checks()
    problems = check_repo.check_self_containment(text, skill_names, check_personas=True)
    c.add("D12.self-contained", not problems, 3, "; ".join(problems)[:200])
    jarg = [j for j in JARGON if j.lower() in text.lower()]
    c.add("D12.no-origin-jargon", not jarg, 2, "found: %s" % ", ".join(jarg))
    broken = check_repo.check_links(path, text)
    c.add("D12.links-resolve", not broken, 2, "; ".join(broken)[:200])
    levels = [len(h) for h in re.findall(r"^(#{1,6})\s", mask_fences(body), re.M)]
    jumps = any(b - a > 1 for a, b in zip(levels, levels[1:]))
    c.add("D12.heading-hierarchy", not jumps, 1, "no heading level skips (## -> ####)")
    c.add("D12.no-placeholders", not PLACEHOLDER_RE.search(body), 1, "no TODO/FIXME/TBD/lorem")
    fences = body.count("```")
    c.add("D12.fences-balanced", fences % 2 == 0, 1, "%d fence markers" % fences)
    return c


# stdlib module names sufficient for our scripts (Python 3.9 has no sys.stdlib_module_names)
STDLIB = set("""abc argparse ast base64 bisect builtins calendar cmath collections contextlib copy csv
dataclasses datetime decimal difflib doctest enum errno fnmatch fractions functools glob gzip hashlib
heapq hmac html http io itertools json logging math numbers operator os pathlib pickle platform pprint
queue random re shlex shutil signal socket sqlite3 statistics string struct subprocess sys tempfile
textwrap threading time timeit traceback types typing unicodedata unittest urllib uuid warnings
weakref xml zipfile zlib __future__ ssl select email mimetypes locale getpass secrets configparser
""".split())


def run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout + r.stderr
    except (subprocess.TimeoutExpired, OSError):
        return None


# --------------------------------------------------------------------------
# Repository-level hygiene
# --------------------------------------------------------------------------

def repo_hygiene(root, skill_names, exec_checks):
    c = Checks()
    readme = read(os.path.join(root, "README.md")) if os.path.isfile(os.path.join(root, "README.md")) else ""
    missing = [n for n in skill_names if ("`%s`" % n) not in readme]
    c.add("R.readme-catalog-complete", not missing, 3, "missing: %s" % ", ".join(missing)[:150])
    for fn, pts in (("LICENSE", 1), ("CONTRIBUTING.md", 1), ("CHANGELOG.md", 1), ("CITATION.cff", 1), ("SECURITY.md", 0.5), ("CODE_OF_CONDUCT.md", 0.5)):
        c.add("R.%s" % fn.lower().replace(".", "-"), os.path.isfile(os.path.join(root, fn)), pts)
    wf = os.path.join(root, ".github", "workflows")
    c.add("R.ci-workflow", os.path.isdir(wf) and any(f.endswith((".yml", ".yaml")) for f in os.listdir(wf)), 2)
    # every skill must declare metadata.category from the catalog's known set
    known_cats = {"decision-strategy", "foresight", "technology-assessment",
                  "evidence-verification", "quantitative", "domain", "writing"}
    bad_cat = []
    for n in skill_names:
        fm, _ = parse_frontmatter(read(os.path.join(root, "skills", n, "SKILL.md")))
        meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
        if meta.get("category") not in known_cats:
            bad_cat.append(n)
    c.add("R.skill-categories", not bad_cat, 2,
          "missing/unknown metadata.category: %s" % ", ".join(bad_cat)[:150])
    idx = os.path.join(root, "index.json")
    ok_idx = False
    if os.path.isfile(idx):
        try:
            data = json.loads(read(idx))
            listed = {s["name"] for s in data.get("skills", [])}
            ok_idx = listed == set(skill_names)
        except Exception:
            ok_idx = False
    c.add("R.machine-index", ok_idx, 2, "index.json lists exactly the skills on disk")
    plugin = os.path.join(root, ".claude-plugin", "plugin.json")
    c.add("R.plugin-manifest", os.path.isfile(plugin), 1, ".claude-plugin/plugin.json present")
    c.add("R.gitignore", os.path.isfile(os.path.join(root, ".gitignore")) and ".DS_Store" in read(os.path.join(root, ".gitignore")), 0.5)
    junk = []
    for dp, dn, fns in os.walk(root):
        if ".git" in dp.split(os.sep):
            continue
        junk += [os.path.join(dp, f) for f in fns if f in (".DS_Store", "Thumbs.db") or f.endswith((".pyc",))]
        junk += [os.path.join(dp, d) for d in dn if d == "__pycache__"]
    c.add("R.no-junk-files", not junk, 1, "; ".join(os.path.relpath(j, root) for j in junk)[:150])
    if exec_checks:
        r = run([sys.executable, os.path.join(root, "evaluation", "check_repo.py"), "--root", root], timeout=600)
        c.add("R.check-repo-passes", r is not None and r[0] == 0, 3, (r[1].strip().splitlines()[-1] if r else "not run")[:150])
    else:
        c.add("R.check-repo-passes", True, 3, "not executed (--no-exec)")
    c.add("R.evaluation-docs", os.path.isfile(os.path.join(root, "evaluation", "rubric.md")), 0.5)
    return c


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def methodology_index(root):
    """Map skill name -> methodology file path where a same-named counterpart exists,
    or where a methodology file explicitly links to the skill."""
    idx = {}
    mdir = os.path.join(root, "methodologies")
    files = []
    for cat in sorted(os.listdir(mdir)):
        cd = os.path.join(mdir, cat)
        if os.path.isdir(cd):
            files += [os.path.join(cd, f) for f in sorted(os.listdir(cd)) if f.endswith(".md")]
    for f in files:
        stem = os.path.splitext(os.path.basename(f))[0]
        idx[stem] = os.path.relpath(f, root)
    return idx, files


def score_skill(root, name, vecs, all_names, skill_names, meth_index, exec_checks, trig=None):
    skill_dir = os.path.join(root, "skills", name)
    path = os.path.join(skill_dir, "SKILL.md")
    text = read(path)
    fm, fm_problems = parse_frontmatter(text)
    body = body_of(text)
    has_tool = os.path.isdir(os.path.join(skill_dir, "scripts"))
    dims = {
        "D1_spec": d1_spec(name, text, fm, fm_problems, body),
        "D2_discoverability": d2_discoverability(name, fm, vecs, all_names, trig),
        "D3_procedure": d3_procedure(body),
        "D4_output": d4_output(body),
        "D5_boundaries": d5_boundaries(body, skill_names),
        "D6_crosslinks": d6_crosslinks(name, path, body, skill_names, meth_index),
        "D7_example": d7_example(body, has_tool),
        "D8_verification": d8_verification(body),
        "D9_provenance": d9_provenance(body),
        "D10_tooling": d10_tooling(name, skill_dir, body, exec_checks),
        "D11_efficiency": d11_efficiency(body, skill_dir),
        "D12_hygiene": d12_hygiene(path, text, body, skill_names),
    }
    scores = {k: v.score() for k, v in dims.items()}
    # Dimensions that do not apply to this skill are excluded from the total and
    # their weight is redistributed proportionally across the rest, so a skill is
    # never rewarded for lacking something.
    applicable = [k for k in WEIGHTS if not dims[k].not_applicable]
    wsum = sum(WEIGHTS[k] for k in applicable)
    total = round(sum(scores[k] * WEIGHTS[k] / wsum for k in applicable), 1)
    failed = [i for k, v in dims.items() for i in v.items if not i["pass"]]
    return {
        "name": name, "total": total, "dimensions": scores,
        "not_applicable": [k for k in WEIGHTS if dims[k].not_applicable],
        "words": words(body), "lines": body.count("\n") + 1,
        "description_chars": len(str(fm.get("description", ""))),
        "has_tool": has_tool,
        "checks": {k: v.items for k, v in dims.items()},
        "failed": ["%s — %s" % (i["id"], i["note"]) if i["note"] else i["id"] for i in failed],
    }


def load_descriptions(root, skill_names):
    descs = {}
    for n in skill_names:
        fm, _ = parse_frontmatter(read(os.path.join(root, "skills", n, "SKILL.md")))
        descs[n] = "%s %s" % (n.replace("-", " "), fm.get("description", ""))
    return descs


def render_md(result, baseline=None):
    out = []
    out.append("# Deterministic scorecard — skill library\n")
    out.append("Generated by `evaluation/score_skills.py` (mechanical checks only; no model judgment). "
               "Weights: " + ", ".join("%s %d" % (k, v) for k, v in WEIGHTS.items()) + ".\n")
    lib = result["library"]
    out.append("## Headline\n")
    out.append("| Metric | Value |%s" % (" Baseline | Δ |" if baseline else ""))
    out.append("|---|---|%s" % ("---|---|" if baseline else ""))

    def row(label, key, fmt="%.1f"):
        v = lib[key]
        if baseline:
            b = baseline["library"].get(key)
            d = (v - b) if isinstance(b, (int, float)) else None
            out.append("| %s | %s | %s | %s |" % (label, fmt % v, (fmt % b) if b is not None else "—", ("%+.1f" % d) if d is not None else "—"))
        else:
            out.append("| %s | %s |" % (label, fmt % v))
    row("Library score (0–100)", "library_score")
    row("Mean skill score", "mean_skill_score")
    row("Median skill score", "median_skill_score")
    row("Minimum skill score", "min_skill_score")
    row("Repo hygiene score", "repo_hygiene_score")
    row("Trigger eval rank-1 rate (positives)", "trigger_rank1_rate", "%.3f")
    row("Trigger eval MRR", "trigger_mrr", "%.3f")
    row("Trigger eval negatives not triggered", "trigger_negative_rate", "%.3f")
    out.append("| Skills scored | %d |%s" % (lib["n_skills"], (" %d | |" % baseline["library"]["n_skills"]) if baseline else ""))
    out.append("| Checks passed / total | %d / %d |%s" % (lib["checks_passed"], lib["checks_total"],
               (" %d / %d | |" % (baseline["library"]["checks_passed"], baseline["library"]["checks_total"])) if baseline else ""))
    out.append("\n## Dimension means (all skills)\n")
    out.append("| Dimension | Weight | Mean |%s" % (" Baseline | Δ |" if baseline else ""))
    out.append("|---|---|---|%s" % ("---|---|" if baseline else ""))
    for k in WEIGHTS:
        v = lib["dimension_means"][k]
        if baseline:
            b = baseline["library"]["dimension_means"].get(k)
            out.append("| %s | %d | %.1f | %s | %s |" % (k, WEIGHTS[k], v, ("%.1f" % b) if b is not None else "—", ("%+.1f" % (v - b)) if b is not None else "—"))
        else:
            out.append("| %s | %d | %.1f |" % (k, WEIGHTS[k], v))
    out.append("\n## Most-failed checks\n")
    out.append("| Check | Skills failing |")
    out.append("|---|---|")
    for cid, n in lib["failed_check_counts"][:25]:
        out.append("| `%s` | %d |" % (cid, n))
    out.append("\n## Per-skill scores\n")
    out.append("| Skill | Total | " + " | ".join(k.split("_")[0] for k in WEIGHTS) + " | Words | Gaps |")
    out.append("|---|---|" + "---|" * len(WEIGHTS) + "---|---|")
    for s in sorted(result["skills"], key=lambda s: (s["total"], s["name"])):
        out.append("| `%s` | **%.1f** | %s | %d | %s |" % (
            s["name"], s["total"], " | ".join("%.0f" % s["dimensions"][k] for k in WEIGHTS), s["words"],
            "; ".join(f.split(" — ")[0] for f in s["failed"][:6]) + (" …" if len(s["failed"]) > 6 else "")))
    out.append("\n## Repository hygiene checks\n")
    out.append("| Check | Pass | Note |")
    out.append("|---|---|---|")
    for i in result["repo_checks"]:
        out.append("| `%s` | %s | %s |" % (i["id"], "✓" if i["pass"] else "✗", i["note"]))
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(HERE))
    ap.add_argument("--skill", help="detailed report for one skill")
    ap.add_argument("--baseline", help="previous JSON output to diff against")
    ap.add_argument("--json", dest="json_out", default=None, help="JSON output path (default evaluation/scores/latest.json)")
    ap.add_argument("--md", dest="md_out", default=None, help="Markdown output path (default evaluation/scores/latest.md)")
    ap.add_argument("--min-score", type=float, default=None, help="exit 1 if any skill scores below this")
    ap.add_argument("--min-library", type=float, default=None, help="exit 1 if the library score is below this")
    ap.add_argument("--no-exec", action="store_true", help="skip subprocess checks")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--list-checks", action="store_true", help="print the check catalogue (ids, points) as markdown and exit")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    exec_checks = not args.no_exec

    skills_dir = os.path.join(root, "skills")
    # Leading underscore = contributor scaffolding (skills/_TEMPLATE), not a skill.
    skill_names = sorted(n for n in os.listdir(skills_dir)
                         if not n.startswith("_")
                         and os.path.isfile(os.path.join(skills_dir, n, "SKILL.md")))
    meth_index, _ = methodology_index(root)
    vecs = tfidf(load_descriptions(root, skill_names))
    import trigger_eval  # local import: trigger_eval imports helpers from this module
    trig = trigger_eval.evaluate(root)

    if args.list_checks:
        ref = "analysis-of-competing-hypotheses" if "analysis-of-competing-hypotheses" in skill_names else skill_names[0]
        s = score_skill(root, ref, vecs, skill_names, skill_names, meth_index, False, trig)
        print("| Dimension | Weight | Check | Points |")
        print("|---|---|---|---|")
        for k in WEIGHTS:
            for i in s["checks"][k]:
                print("| %s | %d | `%s` | %g |" % (k, WEIGHTS[k], i["id"], i["max"]))
        return 0
    if args.skill:
        s = score_skill(root, args.skill, vecs, skill_names, skill_names, meth_index, exec_checks, trig)
        print("%s — total %.1f" % (s["name"], s["total"]))
        for k in WEIGHTS:
            print("  %-20s %5.1f  (weight %d)" % (k, s["dimensions"][k], WEIGHTS[k]))
            for i in s["checks"][k]:
                print("     %s %-32s %s" % ("✓" if i["pass"] else "✗", i["id"], i["note"] if not i["pass"] else ""))
        return 0

    if not skill_names:
        print("FAIL: inspected zero skills -- expected at least one. Is skills/ present?")
        return 1
    results = [score_skill(root, n, vecs, skill_names, skill_names, meth_index, exec_checks, trig) for n in skill_names]
    hyg = repo_hygiene(root, skill_names, exec_checks)
    totals = [r["total"] for r in results]
    mean_skill = sum(totals) / len(totals)
    srt = sorted(totals)
    median = srt[len(srt) // 2] if len(srt) % 2 else (srt[len(srt) // 2 - 1] + srt[len(srt) // 2]) / 2
    dim_means = {k: round(sum(r["dimensions"][k] for r in results) / len(results), 1) for k in WEIGHTS}
    fail_counts = Counter(i["id"] for r in results for k in WEIGHTS for i in r["checks"][k] if not i["pass"])
    checks_total = sum(len(r["checks"][k]) for r in results for k in WEIGHTS)
    checks_passed = checks_total - sum(fail_counts.values())
    hyg_score = hyg.score()
    library_score = round(0.85 * mean_skill + 0.15 * hyg_score, 1)
    result = {
        "schema": "skill-library-scorecard/2",
        "weights": WEIGHTS,
        "library": {
            "library_score": library_score, "mean_skill_score": round(mean_skill, 1),
            "median_skill_score": round(median, 1), "min_skill_score": min(totals),
            "max_skill_score": max(totals), "repo_hygiene_score": hyg_score,
            "n_skills": len(results), "dimension_means": dim_means,
            "checks_passed": checks_passed, "checks_total": checks_total,
            "failed_check_counts": fail_counts.most_common(),
            "trigger_rank1_rate": trig["rank1_rate"], "trigger_mrr": trig["mrr"],
            "trigger_negative_rate": trig["negative_rate"], "trigger_cases": trig["n_cases"],
        },
        "repo_checks": hyg.items,
        "skills": results,
    }
    baseline = json.loads(read(args.baseline)) if args.baseline else None
    json_out = args.json_out or os.path.join(HERE, "scores", "latest.json")
    md_out = args.md_out or os.path.join(HERE, "scores", "latest.md")
    os.makedirs(os.path.dirname(json_out), exist_ok=True)
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    with open(md_out, "w", encoding="utf-8") as f:
        f.write(render_md(result, baseline))
    if not args.quiet:
        print("Library score %.1f | mean skill %.1f | median %.1f | min %.1f | hygiene %.1f | checks %d/%d" % (
            library_score, mean_skill, median, min(totals), hyg_score, checks_passed, checks_total))
        print("Dimension means: " + ", ".join("%s=%.0f" % (k.split("_")[0], v) for k, v in dim_means.items()))
        print("Trigger eval: rank-1 %.1f%% | MRR %.3f | negatives held %.1f%% | %d cases" % (
            100 * trig["rank1_rate"], trig["mrr"], 100 * trig["negative_rate"], trig["n_cases"]))
        if baseline:
            print("Δ vs baseline: library %+.1f, mean skill %+.1f" % (
                library_score - baseline["library"]["library_score"], mean_skill - baseline["library"]["mean_skill_score"]))
        print("wrote %s and %s" % (os.path.relpath(json_out, root), os.path.relpath(md_out, root)))
    rc = 0
    if args.min_score is not None and min(totals) < args.min_score:
        print("GATE FAIL: min skill score %.1f < %.1f" % (min(totals), args.min_score)); rc = 1
    if args.min_library is not None and library_score < args.min_library:
        print("GATE FAIL: library score %.1f < %.1f" % (library_score, args.min_library)); rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
