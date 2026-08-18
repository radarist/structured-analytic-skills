#!/usr/bin/env python3
"""Generate the machine-readable catalog `index.json` and the README catalog
tables from skill frontmatter.

Never hand-edit either — regenerate them. The README tables live between the
`<!-- CATALOG:BEGIN -->` and `<!-- CATALOG:END -->` markers and are rebuilt from
each skill's `metadata.category` / `metadata.method`, so the catalog cannot drift
from what is on disk. CI runs `--check` to fail when either is stale.
Deterministic: sorted keys, no timestamps.

Usage:
  python3 evaluation/build_index.py            # write index.json + README catalog
  python3 evaluation/build_index.py --check    # exit 1 if either is stale
  python3 evaluation/build_index.py --print    # print index.json to stdout only

Stdlib only. Python 3.9+.
"""

import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from score_skills import parse_frontmatter, read, body_of, words  # noqa: E402

SCHEMA = "https://github.com/radarist/structured-analytic-skills/index.schema/1"
GENERATOR = "python3 evaluation/build_index.py — do not edit by hand"

# Display order and headings for the README catalog. A skill whose
# metadata.category is not listed here lands in "Uncategorised", which the
# repo-hygiene check treats as a failure — every skill must declare one.
CATEGORY_ORDER = [
    ("decision-strategy", "Decision & strategy",
     "Choosing between options, ranking explanations, and stress-testing a decision before it is made."),
    ("foresight", "Foresight",
     "Looking further out: weak signals, alternative futures, and the indicators that tell you which one is arriving."),
    ("technology-assessment", "Technology assessment",
     "Reading the maturity, momentum and competitive position of a technology or the organisations building it."),
    ("evidence-verification", "Evidence & verification",
     "Establishing what is actually known, how well it is sourced, and where a conclusion would break."),
    ("quantitative", "Quantitative checks",
     "The arithmetic behind a claim: significance, power, pooling, calibration, base rates."),
    ("domain", "Domain-specific",
     "Checks that need a field's own rules."),
    ("writing", "Writing",
     "Getting the finished analysis in front of a reader in a form they can act on."),
]
MARK_BEGIN = "<!-- CATALOG:BEGIN -->"
MARK_END = "<!-- CATALOG:END -->"


def build(root):
    sdir = os.path.join(root, "skills")
    plugin = os.path.join(root, ".claude-plugin", "plugin.json")
    lib_version = None
    if os.path.isfile(plugin):
        try:
            lib_version = json.loads(read(plugin)).get("version")
        except ValueError:
            lib_version = None
    skills = []
    for name in sorted(os.listdir(sdir)):
        # A leading underscore marks contributor scaffolding (skills/_TEMPLATE),
        # which must never reach the catalog or index.
        p = os.path.join(sdir, name, "SKILL.md")
        if name.startswith("_") or not os.path.isfile(p):
            continue
        text = read(p)
        fm, _ = parse_frontmatter(text)
        meta = fm.get("metadata", {}) if isinstance(fm.get("metadata"), dict) else {}
        scripts_dir = os.path.join(sdir, name, "scripts")
        scripts = sorted(f for f in os.listdir(scripts_dir) if f.endswith(".py")) if os.path.isdir(scripts_dir) else []
        refs_dir = os.path.join(sdir, name, "references")
        refs = sorted(os.listdir(refs_dir)) if os.path.isdir(refs_dir) else []
        entry = {
            "name": name,
            "description": fm.get("description", ""),
            "category": meta.get("category", ""),
            "method": meta.get("method", ""),
            "origin": meta.get("origin", ""),
            "version": meta.get("version", ""),
            "license": fm.get("license", ""),
            "path": "skills/%s/SKILL.md" % name,
            "scripts": ["skills/%s/scripts/%s" % (name, f) for f in scripts],
            "references": ["skills/%s/references/%s" % (name, f) for f in refs],
            "has_evals": os.path.isfile(os.path.join(sdir, name, "evals", "evals.json")),
            "words": words(body_of(text)),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        }
        skills.append(entry)
    cats = {}
    for s in skills:
        cats[s["category"] or "(uncategorised)"] = cats.get(s["category"] or "(uncategorised)", 0) + 1
    return {
        "$schema": SCHEMA,
        # Marker for humans and tools: this file has no hand-written content.
        "_generated_by": GENERATOR,
        "name": "structured-analytic-skills",
        "version": lib_version or "",
        "spec": "https://agentskills.io/specification",
        "skill_count": len(skills),
        "categories": dict(sorted(cats.items())),
        "with_scripts": sum(1 for s in skills if s["scripts"]),
        "with_evals": sum(1 for s in skills if s["has_evals"]),
        "skills": skills,
    }


def dumps(obj):
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def readme_catalog(data):
    """Render the README catalog tables from the index data."""
    by_cat = {}
    for s in data["skills"]:
        by_cat.setdefault(s["category"] or "", []).append(s)
    out = [MARK_BEGIN, "",
           "<!-- Generated by evaluation/build_index.py — do not edit by hand. -->", ""]
    known = {k for k, _, _ in CATEGORY_ORDER}
    for key, heading, blurb in CATEGORY_ORDER:
        items = sorted(by_cat.get(key, []), key=lambda s: s["name"])
        if not items:
            continue
        out.append("### %s" % heading)
        out.append("")
        out.append(blurb)
        out.append("")
        out.append("| Skill | Method | Tool |")
        out.append("| --- | --- | --- |")
        for s in items:
            tool = ", ".join("`%s`" % os.path.basename(p) for p in s["scripts"]) or "—"
            out.append("| [`%s`](%s) | %s | %s |" % (s["name"], s["path"], s["method"] or "—", tool))
        out.append("")
    leftover = sorted((s for k, v in by_cat.items() if k not in known for s in v), key=lambda s: s["name"])
    if leftover:
        out.append("### Uncategorised")
        out.append("")
        out.append("| Skill | Method | Tool |")
        out.append("| --- | --- | --- |")
        for s in leftover:
            tool = ", ".join("`%s`" % os.path.basename(p) for p in s["scripts"]) or "—"
            out.append("| [`%s`](%s) | %s | %s |" % (s["name"], s["path"], s["method"] or "—", tool))
        out.append("")
    out.append(MARK_END)
    return "\n".join(out)


def render_readme(root, data):
    """Return the README text with the catalog block replaced, or None if the
    markers are absent."""
    path = os.path.join(root, "README.md")
    if not os.path.isfile(path):
        return None, None
    text = read(path)
    if MARK_BEGIN not in text or MARK_END not in text:
        return path, None
    start = text.index(MARK_BEGIN)
    end = text.index(MARK_END) + len(MARK_END)
    return path, text[:start] + readme_catalog(data) + text[end:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(HERE))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--print", dest="do_print", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    data = build(root)
    out = dumps(data)
    target = os.path.join(root, "index.json")
    readme_path, readme_new = render_readme(root, data)
    if args.do_print:
        sys.stdout.write(out)
        return 0
    if args.check:
        rc = 0
        current = read(target) if os.path.isfile(target) else ""
        if current != out:
            print("index.json is stale — run: python3 evaluation/build_index.py")
            rc = 1
        if readme_new is not None and read(readme_path) != readme_new:
            print("README.md catalog is stale — run: python3 evaluation/build_index.py")
            rc = 1
        if rc == 0:
            print("index.json and README catalog are current")
        return rc
    with open(target, "w", encoding="utf-8") as f:
        f.write(out)
    msg = "wrote index.json (%d skills)" % len(data["skills"])
    if readme_new is not None:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_new)
        msg += " and regenerated the README catalog"
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
