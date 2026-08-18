#!/usr/bin/env python3
"""Repo consistency checker for the skill-library.

Stdlib-only. Checks:
  1. Every skills/*/SKILL.md has YAML frontmatter with `name` and a strict,
     JSON-quoted `description` accepted by cross-client validators.
  2. Every methodologies/<cat>/*.md has valid schema-shaped YAML frontmatter,
     the 12 template sections and the 8 Agent Adaptation subsections required
     by methodologies/_TEMPLATE.md.
  3. Every relative Markdown link and frontmatter `related:` entry resolves
     to a file that exists, and no skills/*/SKILL.md link escapes its own
     directory with a leading `../` (those dangle after the documented
     copy-out install).
  4. Every skills/*/scripts/*.py runs `--selftest` with exit code 0.
  5. Self-containment: no references to origin-system internals (phantom tools,
     phantom skills, agent personas, origin file paths) — see PHANTOM_SUBSTRINGS
     and PERSONA_RE.
  6. Skill-ref integrity: a backticked kebab-case token appearing after a cue
     word ("use `x`", "invoke `x`", "`x` skill", ...) must be an existing skill
     directory or explicitly allowlisted.
  7. Catalog coverage: every skills/*/SKILL.md is listed in README.md; every
     methodologies/<cat>/*.md is linked from methodologies/README.md. Every
     skills/<name>/ directory contains a SKILL.md.
  8. Every evals/evals.json uses the canonical skill-creator envelope and its
     declared fixtures resolve.
  9. Every skill has current generated `agents/openai.yaml` UI metadata.

Usage: python3 evaluation/check_repo.py [--root PATH] [--no-selftest]
Exit code 0 = all checks pass; 1 = failures found (printed to stdout).
"""

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_schema import validate_eval_file  # noqa: E402
from build_openai_metadata import generated_text  # noqa: E402

METHODOLOGY_SECTIONS = [
    "## Overview",
    "## Origin & History",
    "## Core Concepts & Key Terms",
    "## When to Use / When Not to Use",
    "## Process & Steps",
    "## Techniques, Tools & Deliverables",
    "## Strengths & Limitations",
    "## Worked Examples & Case Studies",
    "## Variants & Related Methodologies",
    "## Agent Adaptation",
    "## References & Further Reading",
]

AGENT_SUBSECTIONS = [
    "suitability for agent execution",
    "recommended multi-agent workflow",
    "agent pipeline",
    "prompt templates",
    "tools & data requirements",
    "quality checks, failure modes & mitigations",
    "human-in-the-loop checkpoints",
    "inputs & outputs",
]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)[^)]*\)")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

# --- Self-containment (checks 5 & 6) -----------------------------------------
# Substrings that must never appear in skill/methodology prose: tools, skills,
# config constants, and file paths of the origin system these files were
# extracted from. Plain substring match, applied everywhere.
PHANTOM_SUBSTRINGS = [
    # origin-system tools / APIs
    "searchOssHealth", "searchPapers", "searchPatents", "searchEntities",
    "webSearch", "webScrape", "firecrawl", "recordKnowledgeGap",
    "approveSignalForImport", "search_with_grounding", "checkCreator",
    "admiralty_to_confidence", "SIGNAL_AUTO_APPROVE_THRESHOLD",
    "mission-quality.ts",
    # skills that existed only in the origin system
    "generate-radar-report", "research-technology", "web-research",
    "resolve-citations",
    # origin codebase paths
    "public/ihe-", "public/css/report-",
    # origin system docs
    "CLAUDE.md", "Relation Write Contract",
    # origin project name (provenance belongs in the root README only)
    "Radarist",
]

# Origin-system agent personas, capitalized as system roles. Skills only —
# methodologies/agent-playbook.md deliberately defines its own generic role
# catalog (Scout, Analyst, ...) for multi-agent pipelines.
PERSONA_RE = re.compile(
    r"\bthe (Strategist|Curator|Creator|Scout)\b"
    r"|\b(Strategist|Curator|Creator|Scout) agents?\b"
    r"|\b(Strategist|Curator|Creator|Scout)'s\b"
)

# A backticked kebab-case token near a routing cue must resolve to a real
# skill directory. Catches dangling references to skills that were not ported.
SKILL_REF_CUE_RE = re.compile(
    r"\b(?:use|invoke|run|see|pairs? with|paired with|via)\s+`([a-z][a-z0-9]*-[a-z0-9-]*)`"
    r"|`([a-z][a-z0-9]*-[a-z0-9-]*)`\s+(?:skill|territory|instead|directly)"
)

# Non-skill tokens that legitimately appear after a cue word. Keep empty;
# add only with a comment explaining why the token is not a skill reference.
SKILL_REF_ALLOWLIST: dict[str, str] = {}


# --- Copy-out safety (check 3) -----------------------------------------------
# A skill is installed by copying its own directory out of this repo
# (`cp -R skills/* .agents/skills/`), so any link that walks above the skill
# directory resolves here and dangles for every installed user. Targets outside
# the skill must be absolute URLs to the canonical repository path.
RELATIVE_ESCAPE_RE = re.compile(r"\]\((\.\./[^)\s]*)")
REPO_URL_BASE = "https://github.com/radarist/structured-analytic-skills/blob/main/"

# Skills whose escaping links have not been migrated yet. Entries are reported
# as warnings instead of failures so an in-flight migration cannot block CI.
# Delete an entry once that skill is clean — an entry that is already clean is
# harmless, so the list can be emptied at any time. Target: empty.
RELATIVE_LINK_MIGRATION = {
    "amstar2-review-appraisal",
    "analysis-of-competing-hypotheses",
    "assess-study-bias",
    "bayesian-update",
    "futures-wheel",
    "indicators-validation",
    "meta-analysis",
    "quality-of-information-check",
    "trend-analysis",
    "triangulate-sources",
}


def check_relative_escapes(text):
    """Return list of links that walk above the skill directory."""
    return [
        "link escapes the skill directory and dangles after the documented "
        "copy-out install: %s — use %s<path>" % (t, REPO_URL_BASE)
        for t in RELATIVE_ESCAPE_RE.findall(text)
    ]


def is_scaffolding(name):
    """True for a skills/ entry that is contributor scaffolding, not a skill.

    A leading underscore (skills/_TEMPLATE) marks a directory that must stay out
    of the catalog, the scorecard and every validator. Shared convention across
    build_index.py, score_skills.py, build_openai_metadata.py, eval_schema.py,
    trigger_eval.py and run_evals.py.
    """
    return name.startswith("_")


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def check_frontmatter(path, text, required_keys):
    """Return frontmatter problems detectable with the repository schema."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return ["missing YAML frontmatter"]
    body = m.group(1)
    problems = []
    for key in required_keys:
        if not re.search(rf"^{re.escape(key)}:\s*\S", body, re.MULTILINE):
            problems.append(f"frontmatter missing `{key}:`")
    for line_number, line in enumerate(body.splitlines(), start=2):
        field = re.match(r"^[A-Za-z_][A-Za-z0-9_-]*:\s*(.*)$", line)
        if not field:
            continue
        value = field.group(1).strip()
        if value.startswith(('"', "'", "[", "{", "|", ">")):
            continue
        if re.search(r":(?:[ \t]|$)", value):
            problems.append(
                "invalid YAML plain scalar on line %d: quote values containing ': '"
                % line_number
            )
    description = re.search(r"^description:\s*(\S.*)$", body, re.MULTILINE)
    if description:
        raw = description.group(1).strip()
        try:
            parsed = json.loads(raw)
        except ValueError:
            problems.append("description must be a JSON-quoted YAML scalar")
        else:
            if not isinstance(parsed, str) or not parsed.strip():
                problems.append("description must be a non-empty string")
            if "<" in parsed or ">" in parsed:
                problems.append("description cannot contain angle brackets")
    return problems


def frontmatter_related(text):
    """Extract entries of an inline `related: [a, b, c]` frontmatter list."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return []
    rm = re.search(r"^related:\s*\[(.*)\]\s*$", m.group(1), re.MULTILINE)
    if not rm:
        return []
    return [e.strip().strip("'\"") for e in rm.group(1).split(",") if e.strip()]


def check_links(path, text):
    """Return list of broken relative links (markdown links + related: entries)."""
    problems = []
    base = os.path.dirname(path)
    targets = list(LINK_RE.findall(text)) + frontmatter_related(text)
    for t in targets:
        if re.match(r"^[a-z]+://", t) or t.startswith("#") or t.startswith("mailto:"):
            continue
        target = t.split("#", 1)[0]
        if not target:
            continue
        if "{{" in target:  # prompt-template placeholder, not a real path
            continue
        resolved = os.path.normpath(os.path.join(base, target))
        if not os.path.exists(resolved):
            problems.append(f"broken link: {t}")
    return problems


def check_self_containment(text, skill_names, check_personas):
    """Return list of origin-system references (phantoms, personas, dangling skill refs)."""
    problems = []
    for needle in PHANTOM_SUBSTRINGS:
        if needle in text:
            problems.append(f"origin-system reference: {needle!r}")
    if check_personas:
        for m in PERSONA_RE.finditer(text):
            problems.append(f"origin-system agent persona: {m.group(0)!r}")
    for m in SKILL_REF_CUE_RE.finditer(text):
        token = m.group(1) or m.group(2)
        if token not in skill_names and token not in SKILL_REF_ALLOWLIST:
            problems.append(f"dangling skill reference: `{token}` (not a skill in skills/)")
    return problems


def check_catalog_coverage(root, skill_names, meth_files):
    """Return list of files missing from the README catalogs."""
    problems = []
    readme = read(os.path.join(root, "README.md")) if os.path.isfile(os.path.join(root, "README.md")) else ""
    for name in skill_names:
        if f"`{name}`" not in readme:
            problems.append(f"skills/{name}/SKILL.md not listed in README.md catalog")
    meth_readme_path = os.path.join(root, "methodologies", "README.md")
    meth_readme = read(meth_readme_path) if os.path.isfile(meth_readme_path) else ""
    for cat, fn in meth_files:
        if f"({cat}/{fn})" not in meth_readme:
            problems.append(f"methodologies/{cat}/{fn} not linked from methodologies/README.md")
    return problems


def check_methodology_sections(text):
    problems = []
    for sec in METHODOLOGY_SECTIONS:
        if sec.lower() not in text.lower():
            problems.append(f"missing section `{sec}`")
    if "> **Essence:**" not in text:
        problems.append("missing `> **Essence:**` blockquote")
    lowered = text.lower()
    for sub in AGENT_SUBSECTIONS:
        if sub not in lowered:
            problems.append(f"missing Agent Adaptation subsection `{sub}`")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--no-selftest", action="store_true")
    args = ap.parse_args()
    root = args.root

    failures = 0
    skills_dir = os.path.join(root, "skills")
    meth_dir = os.path.join(root, "methodologies")

    # 0. Skill inventory: every skills/<name>/ directory must contain a SKILL.md
    #    (catches orphan dirs such as a scripts/-only folder).
    skill_names = []
    for name in sorted(os.listdir(skills_dir)):
        if not os.path.isdir(os.path.join(skills_dir, name)) or is_scaffolding(name):
            continue
        skill_names.append(name)
        if not os.path.isfile(os.path.join(skills_dir, name, "SKILL.md")):
            failures += 1
            print(f"FAIL skills/{name}/: directory has no SKILL.md")

    # 1. Skills: frontmatter + links + self-containment
    for name in skill_names:
        path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(path):
            continue
        text = read(path)
        problems = check_frontmatter(path, text, ["name", "description"])
        problems += check_links(path, text)
        problems += check_self_containment(text, skill_names, check_personas=True)
        escapes = check_relative_escapes(text)
        if escapes and name in RELATIVE_LINK_MIGRATION:
            for p in escapes:
                print("WARN skills/%s/SKILL.md: %s (migration pending)" % (name, p))
        else:
            problems += escapes
        for p in problems:
            failures += 1
            print(f"FAIL skills/{name}/SKILL.md: {p}")

    # 2. Methodologies: sections + links + self-containment (personas excluded:
    #    agent-playbook.md defines its own generic role catalog)
    meth_files = []
    for cat in sorted(os.listdir(meth_dir)):
        cat_dir = os.path.join(meth_dir, cat)
        if not os.path.isdir(cat_dir):
            continue
        for fn in sorted(os.listdir(cat_dir)):
            if not fn.endswith(".md"):
                continue
            meth_files.append((cat, fn))
            path = os.path.join(cat_dir, fn)
            text = read(path)
            problems = check_frontmatter(
                path,
                text,
                ["name", "category", "origin", "agent_suitability", "tags", "related"],
            )
            problems += check_methodology_sections(text)
            problems += check_links(path, text)
            problems += check_self_containment(text, skill_names, check_personas=False)
            for p in problems:
                failures += 1
                print(f"FAIL methodologies/{cat}/{fn}: {p}")

    # 3. Top-level methodology docs: links only
    for fn in ("README.md", "agent-playbook.md", "_TEMPLATE.md"):
        path = os.path.join(meth_dir, fn)
        if os.path.isfile(path):
            for p in check_links(path, read(path)):
                failures += 1
                print(f"FAIL methodologies/{fn}: {p}")

    # 4. Catalog coverage: README.md lists every skill; methodologies/README.md
    #    links every methodology file
    for p in check_catalog_coverage(root, skill_names, meth_files):
        failures += 1
        print(f"FAIL catalog: {p}")

    # 5. Canonical eval schema and fixture paths
    for name in skill_names:
        ep = os.path.join(skills_dir, name, "evals", "evals.json")
        if not os.path.isfile(ep):
            failures += 1
            print(f"FAIL skills/{name}/: missing evals/evals.json")
            continue
        for problem in validate_eval_file(ep, name):
            failures += 1
            print(f"FAIL skills/{name}/evals/evals.json: {problem}")

    # 6. Codex / ChatGPT UI metadata is present and derived from each skill.
    for name in skill_names:
        skill_dir = os.path.join(skills_dir, name)
        op = os.path.join(skill_dir, "agents", "openai.yaml")
        if not os.path.isfile(op):
            failures += 1
            print(f"FAIL skills/{name}/: missing agents/openai.yaml")
        elif read(op) != generated_text(skill_dir):
            failures += 1
            print(f"FAIL skills/{name}/agents/openai.yaml: generated metadata is stale")

    # 7. Tool selftests
    if not args.no_selftest:
        for name in sorted(os.listdir(skills_dir)):
            scripts = os.path.join(skills_dir, name, "scripts")
            if is_scaffolding(name) or not os.path.isdir(scripts):
                continue
            for fn in sorted(os.listdir(scripts)):
                if not fn.endswith(".py"):
                    continue
                sp = os.path.join(scripts, fn)
                try:
                    r = subprocess.run(
                        [sys.executable, sp, "--selftest"],
                        capture_output=True, text=True, timeout=120,
                    )
                    if r.returncode != 0:
                        failures += 1
                        tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
                        print(f"FAIL skills/{name}/scripts/{fn} --selftest: " + " | ".join(tail))
                except subprocess.TimeoutExpired:
                    failures += 1
                    print(f"FAIL skills/{name}/scripts/{fn} --selftest: timed out")

    if failures == 0:
        print("OK: all checks passed")
        return 0
    print(f"\n{failures} check(s) failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
