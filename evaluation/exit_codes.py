#!/usr/bin/env python3
"""Enforce the companion-tool exit-code convention (CONTRIBUTING.md).

    0  the check passed
    1  the tool ran and its verdict is a failure
    2  usage error, or input the tool cannot analyse

This is the convention of grep, diff, flake8 and pytest, and the one argparse
already enforces -- ArgumentParser.error() exits 2. Any scheme that gives 2 a
different meaning needs an ArgumentParser subclass in *every* script, and fails
silently in the ones that forget; that is exactly how the two meanings came to
collide here, so this gate checks the real binaries rather than the docs.

Three layers:

  * universal   -- every script: `--help` and `--selftest` exit 0, an unknown
                   flag exits 2.
  * verdict     -- curated pass/fail pairs, so "exit 1 means the verdict failed"
                   is demonstrated rather than asserted.
  * static      -- no script may subclass ArgumentParser (that is how a script
                   would re-take 2 from argparse), and no script may return 2
                   for a verdict.

Usage:
    python3 evaluation/exit_codes.py            # report
    python3 evaluation/exit_codes.py --json     # machine-readable
    python3 evaluation/exit_codes.py --selftest # check this checker

Exit 0 when every case conforms, 1 when any case fails (this script follows the
convention it enforces), 2 on usage error or when there is nothing to inspect.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
PY = sys.executable or "python3"

UNKNOWN_FLAG = "--zzz-not-a-real-flag"

# Curated pass/fail pairs: (script, argv, expected, label).
# Every one of these was run by hand before being written down.
VERDICT_CASES = [
    ("smiles-sanity-check/scripts/smiles.py", ["check", "CCO"], 0, "valid SMILES"),
    ("smiles-sanity-check/scripts/smiles.py", ["check", "CO(C)C"], 1, "invalid valence"),
    ("chemistry-claim-check/scripts/chem.py",
     ["check", "--formula", "C6H6", "--mw", "78.11"], 0, "MW matches"),
    ("chemistry-claim-check/scripts/chem.py",
     ["check", "--formula", "C6H6", "--mw", "999"], 1, "MW does not match"),
    ("systematic-review/scripts/prisma.py",
     ["flow", "--identified", "100", "--deduped", "10", "--screened", "90",
      "--excluded-title", "50", "--fulltext", "40", "--excluded-fulltext", "15",
      "--included", "25"], 0, "PRISMA chain balances"),
    ("systematic-review/scripts/prisma.py",
     ["flow", "--identified", "100", "--deduped", "10", "--screened", "90",
      "--excluded-title", "50", "--fulltext", "30", "--excluded-fulltext", "5",
      "--included", "25"], 1, "PRISMA chain does not balance"),
    ("verify-citations/scripts/citecheck.py",
     ["validate", "--text", "doi:10.1136/bmj.n71"], 0, "resolvable DOI"),
    ("verify-citations/scripts/citecheck.py",
     ["validate", "--text", "doi:10.abc/xyz"], 1, "malformed DOI"),
    ("verify-citations/scripts/citecheck.py", ["--demo"], 1, "demo list contains a FAIL"),
    ("oss-project-health/scripts/osshealth.py", ["assess", "--demo"], 1, "at-risk verdict"),
    ("cite-ieee/scripts/ieee.py", ["check", "--demo"], 1, "broken sample document"),
    ("quantitative-sanity-check/scripts/sanity.py",
     ["cagr", "--start", "100", "--end", "200", "--years", "5", "--claim", "14.87"],
     0, "CAGR claim reproduces"),
    ("quantitative-sanity-check/scripts/sanity.py",
     ["cagr", "--start", "100", "--end", "200", "--years", "5", "--claim", "50"],
     1, "CAGR claim does not reproduce"),
    ("experimental-design/scripts/power.py",
     ["n-means", "--d", "0.5", "--alpha", "1.5"], 2, "alpha out of range is unusable input"),
]

SUBCLASS_RE = re.compile(r"^class\s+\w+\s*\(\s*argparse\.ArgumentParser\s*\)", re.M)
VERDICT_TWO_RE = re.compile(r"return[ \t]+2[ \t]+if|exit_code[ \t]*=[ \t]*2\b|exit_code\"\][ \t]*=[ \t]*2\b")


def scripts():
    out = []
    for name in sorted(os.listdir(SKILLS)):
        d = os.path.join(SKILLS, name, "scripts")
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".py"):
                out.append(os.path.join(d, f))
    return out


def run(path, argv, timeout=180):
    """Return the exit code of `python3 path *argv`, or None if it hung/crashed."""
    try:
        p = subprocess.run([PY, path] + list(argv), stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=timeout)
        return p.returncode
    except subprocess.TimeoutExpired:
        return None


def check_all():
    findings = []
    n = 0
    paths = scripts()
    for path in paths:
        rel = os.path.relpath(path, ROOT)
        for argv, want, label in (
            (["--help"], 0, "--help exits 0"),
            (["--selftest"], 0, "--selftest exits 0"),
            ([UNKNOWN_FLAG], 2, "unknown flag exits 2 (argparse usage error)"),
        ):
            n += 1
            got = run(path, argv)
            if got != want:
                findings.append({"file": rel, "argv": argv, "want": want,
                                 "got": got, "label": label})
        src = open(path, encoding="utf-8").read()
        n += 1
        if SUBCLASS_RE.search(src):
            findings.append({"file": rel, "argv": None, "want": "no ArgumentParser subclass",
                             "got": "subclass present", "label":
                             "subclassing ArgumentParser re-takes exit 2 from usage errors"})
        n += 1
        m = VERDICT_TWO_RE.search(src)
        if m:
            findings.append({"file": rel, "argv": None, "want": "verdict failure returns 1",
                             "got": m.group(0), "label": "exit 2 is usage error, not a verdict"})

    for rel_script, argv, want, label in VERDICT_CASES:
        path = os.path.join(SKILLS, rel_script)
        n += 1
        if not os.path.isfile(path):
            findings.append({"file": rel_script, "argv": argv, "want": want,
                             "got": "missing script", "label": label})
            continue
        got = run(path, argv)
        if got != want:
            findings.append({"file": rel_script, "argv": argv, "want": want,
                             "got": got, "label": label})
    return paths, n, findings


def selftest():
    """The checker must be able to fail. Prove each layer catches a planted defect."""
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))

    check("scripts() finds the companion tools", len(scripts()) >= 30)
    check("a real script exits 0 on --help",
          run(os.path.join(SKILLS, "smiles-sanity-check/scripts/smiles.py"), ["--help"]) == 0)
    check("a real script exits 2 on an unknown flag",
          run(os.path.join(SKILLS, "smiles-sanity-check/scripts/smiles.py"), [UNKNOWN_FLAG]) == 2)
    check("a failing verdict exits 1",
          run(os.path.join(SKILLS, "smiles-sanity-check/scripts/smiles.py"),
              ["check", "CO(C)C"]) == 1)
    check("static guard catches an ArgumentParser subclass",
          SUBCLASS_RE.search("class Parser(argparse.ArgumentParser):\n    pass\n") is not None)
    check("static guard ignores a plain instantiation",
          SUBCLASS_RE.search("p = argparse.ArgumentParser()\n") is None)
    check("static guard catches a verdict returning 2",
          VERDICT_TWO_RE.search('    return 2 if result["errors"] else 0') is not None)
    check("static guard catches exit_code = 2",
          VERDICT_TWO_RE.search("        exit_code = 2") is not None)
    check("verdict case table is populated", len(VERDICT_CASES) >= 10)
    check("verdict table covers all three codes",
          {c[2] for c in VERDICT_CASES} == {0, 1, 2})

    failed = [n for n, ok in checks if not ok]
    for name, ok in checks:
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
    if failed:
        print("\nSELFTEST FAILED: %d of %d" % (len(failed), len(checks)), file=sys.stderr)
        return 1
    print("\nselftest OK (%d checks passed)" % len(checks))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Enforce the companion-tool exit-code convention (CONTRIBUTING.md).")
    ap.add_argument("--json", action="store_true", help="emit the report as JSON")
    ap.add_argument("--selftest", action="store_true", help="check this checker and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    paths, n, findings = check_all()
    if not paths or not n:
        print("error: no companion tools inspected — refusing to report success",
              file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"scripts": len(paths), "cases": n,
                          "findings": findings}, indent=2, sort_keys=True))
    else:
        for f in findings:
            where = "%s %s" % (f["file"], " ".join(f["argv"]) if f["argv"] else "")
            print("FAIL  %-58s want %s, got %s  (%s)"
                  % (where.strip(), f["want"], f["got"], f["label"]))
        if findings:
            print("\n%d of %d exit-code cases violate the convention "
                  "(CONTRIBUTING.md: 0 pass, 1 failing verdict, 2 usage)."
                  % (len(findings), n), file=sys.stderr)
        else:
            print("OK: %d exit-code cases across %d companion tools conform "
                  "(0 pass, 1 failing verdict, 2 usage)." % (n, len(paths)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
