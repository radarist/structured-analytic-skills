#!/usr/bin/env python3
"""Load, validate, and migrate skill evals to the skill-creator schema.

The canonical file shape follows anthropics/skills skill-creator:

  {"skill_name": "name", "evals": [{"id": 1, "prompt": "...",
    "expected_output": "...", "files": [], "expectations": ["..."]}]}

This library adds `kind`, `skills`, `case_id`, and `requires_input` as optional
extensions for routing negatives and non-runnable trigger cases.  The loader
also accepts the legacy list form so historical trees can still be scored.

Stdlib only. Python 3.9+.
"""

import argparse
import json
import os
import sys


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _expectations(case):
    values = case.get("expectations", case.get("expected_behavior", []))
    return values if isinstance(values, list) else []


def load_eval_file(path, expected_skill=None):
    """Return `(declared_skill, normalized_cases, is_canonical)`.

    Normalized cases use the canonical `prompt` and `expectations` keys while
    preserving routing extensions.  Validation is deliberately separate so a
    historical checkout can be loaded and re-scored before migration.
    """
    data = read_json(path)
    if isinstance(data, dict):
        declared = data.get("skill_name")
        raw_cases = data.get("evals", [])
        canonical = True
    elif isinstance(data, list):
        declared = expected_skill
        raw_cases = data
        canonical = False
    else:
        return expected_skill, [], False

    cases = []
    if not isinstance(raw_cases, list):
        return declared, [], canonical
    for case in raw_cases:
        if not isinstance(case, dict):
            continue
        normalized = dict(case)
        normalized["prompt"] = case.get("prompt", case.get("query", ""))
        normalized["expectations"] = _expectations(case)
        if "expected_output" not in normalized:
            normalized["expected_output"] = _expected_output(normalized["expectations"])
        if "files" not in normalized:
            normalized["files"] = []
        cases.append(normalized)
    return declared, cases, canonical


def _expected_output(expectations):
    if not expectations:
        return "A response that follows the skill's method and output contract."
    joined = "; ".join(str(item).rstrip(".") for item in expectations)
    return "A response that satisfies these checks: %s." % joined


def canonical_document(path, expected_skill):
    """Convert a canonical or legacy eval file to the canonical envelope."""
    _declared, cases, _canonical = load_eval_file(path, expected_skill)
    out = []
    for sequence, case in enumerate(cases, 1):
        old_id = case.get("case_id", case.get("id"))
        item = {
            "id": sequence,
            "case_id": str(old_id) if old_id is not None else "%s-%d" % (expected_skill, sequence),
            "kind": case.get("kind", "positive"),
            "prompt": str(case.get("prompt", "")),
            "expected_output": str(case.get("expected_output") or _expected_output(case.get("expectations", []))),
            "files": list(case.get("files", [])) if isinstance(case.get("files", []), list) else [],
            "expectations": list(case.get("expectations", [])),
        }
        if case.get("skills"):
            item["skills"] = list(case["skills"])
        if case.get("requires_input"):
            item["requires_input"] = True
        out.append(item)
    return {"skill_name": expected_skill, "evals": out}


def validate_eval_file(path, expected_skill):
    """Return schema and fixture problems for one canonical eval file."""
    problems = []
    try:
        data = read_json(path)
    except (OSError, ValueError) as exc:
        return ["invalid JSON: %s" % exc]
    if not isinstance(data, dict):
        return ["top level must be an object with skill_name and evals"]
    if data.get("skill_name") != expected_skill:
        problems.append("skill_name=%r does not match %r" % (data.get("skill_name"), expected_skill))
    cases = data.get("evals")
    if not isinstance(cases, list):
        return problems + ["evals must be a list"]
    seen_ids = set()
    seen_case_ids = set()
    skill_root = os.path.dirname(os.path.dirname(path))
    for index, case in enumerate(cases, 1):
        label = "evals[%d]" % (index - 1)
        if not isinstance(case, dict):
            problems.append("%s must be an object" % label)
            continue
        eid = case.get("id")
        if not isinstance(eid, int) or isinstance(eid, bool):
            problems.append("%s.id must be an integer" % label)
        elif eid in seen_ids:
            problems.append("%s.id duplicates %r" % (label, eid))
        seen_ids.add(eid)
        cid = case.get("case_id")
        if not isinstance(cid, str) or not cid.strip():
            problems.append("%s.case_id must be a non-empty string" % label)
        elif cid in seen_case_ids:
            problems.append("%s.case_id duplicates %r" % (label, cid))
        seen_case_ids.add(cid)
        if not isinstance(case.get("prompt"), str) or not case.get("prompt", "").strip():
            problems.append("%s.prompt must be a non-empty string" % label)
        if not isinstance(case.get("expected_output"), str) or not case.get("expected_output", "").strip():
            problems.append("%s.expected_output must be a non-empty string" % label)
        expectations = case.get("expectations")
        if not isinstance(expectations, list) or not expectations or not all(isinstance(x, str) and x.strip() for x in expectations):
            problems.append("%s.expectations must contain non-empty strings" % label)
        files = case.get("files")
        if not isinstance(files, list) or not all(isinstance(x, str) for x in files):
            problems.append("%s.files must be a list of paths" % label)
        else:
            for rel in files:
                if os.path.isabs(rel) or not os.path.isfile(os.path.normpath(os.path.join(skill_root, rel))):
                    problems.append("%s.files path does not resolve: %r" % (label, rel))
        if case.get("kind", "positive") not in ("positive", "negative", "edge"):
            problems.append("%s.kind must be positive, negative, or edge" % label)
    return problems


def iter_skill_evals(root):
    skills_dir = os.path.join(root, "skills")
    for name in sorted(os.listdir(skills_dir)):
        # Leading underscore = contributor scaffolding (skills/_TEMPLATE), not a skill.
        if name.startswith("_"):
            continue
        path = os.path.join(skills_dir, name, "evals", "evals.json")
        if os.path.isfile(path):
            yield name, path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="validate every eval file")
    mode.add_argument("--migrate", action="store_true", help="rewrite every eval file canonically")
    args = ap.parse_args()

    failures = 0
    count = 0
    for name, path in iter_skill_evals(os.path.abspath(args.root)):
        count += 1
        if args.migrate:
            document = canonical_document(path, name)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(document, f, indent=2, ensure_ascii=False)
                f.write("\n")
        for problem in validate_eval_file(path, name):
            failures += 1
            print("FAIL skills/%s/evals/evals.json: %s" % (name, problem))
    if failures:
        print("%d eval schema check(s) failed" % failures)
        return 1
    # A checker that inspects zero items must fail. Without this, an empty or
    # mis-pathed skills/ directory reports "OK: 0 ..." and exits 0, so a broken
    # CI checkout looks like a passing gate.
    if count == 0:
        print("FAIL: inspected zero eval files -- expected at least one. "
              "Is skills/ present and populated?")
        return 1

    print("OK: %d eval files use the canonical skill-creator schema" % count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
