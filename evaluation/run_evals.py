#!/usr/bin/env python3
"""Model-based paired evals (optional; NOT part of the deterministic score).

For each positive/edge case in `skills/<name>/evals/evals.json`, run two arms in a
headless Claude Code session (`claude -p`):

  with-skill    : the SKILL.md body is appended to the system prompt
  without-skill : the bare prompt

then ask a judge model whether each canonical `expectations` assertion holds in the
answer.

Cases flagged `"requires_input": true` presuppose an artifact the user would attach
(a draft, a reference list, a changelog) that the case does not carry. They are valid
trigger phrasings but not runnable behavioural cases — both arms answer "send me the
document" and score zero — so they are skipped unless --include-input-cases is passed. Reports per-case pass fractions for both arms and the delta — the
"does the skill actually change behaviour?" question the deterministic scorer
cannot answer. Mirrors the anthropics/skills skill-creator loop and the
`--ablation with-without` mode of `claude plugin eval`.

Costs money and is non-deterministic (model outputs). Defaults are frugal:
haiku for both arms and the judge, one run per case, text-only answers.

Usage:
  python3 evaluation/run_evals.py --skill analysis-of-competing-hypotheses
  python3 evaluation/run_evals.py --skills a,b,c --model sonnet --judge-model haiku
  python3 evaluation/run_evals.py --all --max-cases 1 --out evaluation/scores/behavioral.json

Requires the `claude` CLI on PATH and an authenticated session. Stdlib only.
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from score_skills import read, body_of  # noqa: E402
from eval_schema import load_eval_file  # noqa: E402

JUDGE_PROMPT = """You are grading an AI assistant's answer against a checklist.
Return ONLY a JSON object of the form {"results": [true, false, ...]} with one boolean per
checklist item, in order, true when the answer clearly exhibits that behaviour.

USER REQUEST:
%s

ASSISTANT ANSWER:
%s

CHECKLIST:
%s
"""


def claude(prompt, model, system_append=None, timeout=300):
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "text"]
    if system_append:
        cmd += ["--append-system-prompt", system_append]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip()[:300]
    return r.stdout.strip(), None


def judge(query, answer, expected, model):
    checklist = "\n".join("%d. %s" % (i + 1, e) for i, e in enumerate(expected))
    out, err = claude(JUDGE_PROMPT % (query, answer, checklist), model)
    if out is None:
        return None, err
    m = re.search(r"\{.*\}", out, re.S)
    try:
        res = json.loads(m.group(0))["results"]
        res = [bool(x) for x in res][: len(expected)]
        while len(res) < len(expected):
            res.append(False)
        return res, None
    except Exception:
        return None, "unparseable judge output: %s" % out[:200]


def run_case(root, skill, case, model, judge_model, runs):
    body = body_of(read(os.path.join(root, "skills", skill, "SKILL.md")))
    system = ("You have the following skill available. If it applies to the request, follow it "
              "faithfully — its procedure, output template and verification steps. Answer in text "
              "only; do not use tools.\n\n<skill name=\"%s\">\n%s\n</skill>" % (skill, body))
    query = case["prompt"] + "\n\n(Answer in text only; do not use tools.)"
    expected = case.get("expectations", [])
    out = {"id": case.get("case_id", case.get("id")), "kind": case.get("kind", "positive"), "n_expected": len(expected), "arms": {}}
    for arm, sysapp in (("with_skill", system), ("without_skill", None)):
        fracs, errors = [], []
        for _ in range(runs):
            ans, err = claude(query, model, sysapp)
            if ans is None:
                errors.append(err)
                continue
            res, jerr = judge(case["prompt"], ans, expected, judge_model)
            if res is None:
                errors.append(jerr)
                continue
            fracs.append(sum(res) / len(res) if res else 0.0)
        out["arms"][arm] = {"pass_fraction": round(sum(fracs) / len(fracs), 3) if fracs else None,
                            "runs": len(fracs), "errors": errors}
    w, wo = out["arms"]["with_skill"]["pass_fraction"], out["arms"]["without_skill"]["pass_fraction"]
    out["delta"] = round(w - wo, 3) if (w is not None and wo is not None) else None
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(HERE))
    ap.add_argument("--skill")
    ap.add_argument("--skills", help="comma-separated list")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--judge-model", default="haiku")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--max-cases", type=int, default=2, help="positive cases per skill")
    ap.add_argument("--include-input-cases", action="store_true",
                    help="also run cases flagged requires_input (they presuppose a user artifact "
                         "the case does not supply, so both arms typically ask for it and score 0)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--min-delta", type=float, default=None,
                    help="exit 1 if the mean with-minus-without delta falls below this")
    ap.add_argument("--min-with", type=float, default=None,
                    help="exit 1 if the mean with-skill pass fraction falls below this")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if args.skill:
        names = [args.skill]
    elif args.skills:
        names = [s.strip() for s in args.skills.split(",") if s.strip()]
    elif args.all:
        # Leading underscore = contributor scaffolding (skills/_TEMPLATE), not a skill.
        names = sorted(n for n in os.listdir(os.path.join(root, "skills"))
                       if not n.startswith("_")
                       and os.path.isfile(os.path.join(root, "skills", n, "evals", "evals.json")))
    else:
        ap.error("choose --skill, --skills or --all")
    report = {"model": args.model, "judge_model": args.judge_model, "runs": args.runs, "skills": {}}
    for n in names:
        ep = os.path.join(root, "skills", n, "evals", "evals.json")
        if not os.path.isfile(ep):
            print("%s: no evals.json — skipped" % n)
            continue
        _declared, loaded, _canonical = load_eval_file(ep, n)
        allcases = [c for c in loaded if c.get("kind", "positive") in ("positive", "edge")]
        runnable = [c for c in allcases if args.include_input_cases or not c.get("requires_input")]
        skipped = len(allcases) - len(runnable)
        if skipped:
            print("%s: skipped %d case(s) flagged requires_input" % (n, skipped))
        cases = runnable[: args.max_cases]
        results = [run_case(root, n, c, args.model, args.judge_model, args.runs) for c in cases]
        deltas = [r["delta"] for r in results if r["delta"] is not None]
        report["skills"][n] = {"cases": results, "mean_delta": round(sum(deltas) / len(deltas), 3) if deltas else None}
        for r in results:
            print("%-34s %-12s with %s  without %s  Δ %s" % (
                n, r["id"], r["arms"]["with_skill"]["pass_fraction"], r["arms"]["without_skill"]["pass_fraction"], r["delta"]))
    all_d = [s["mean_delta"] for s in report["skills"].values() if s["mean_delta"] is not None]
    report["mean_delta_all"] = round(sum(all_d) / len(all_d), 3) if all_d else None
    withs = [c["arms"]["with_skill"]["pass_fraction"]
             for s in report["skills"].values() for c in s["cases"]
             if c["arms"]["with_skill"]["pass_fraction"] is not None]
    report["mean_with_skill"] = round(sum(withs) / len(withs), 3) if withs else None
    report["cases_scored"] = len(withs)
    report["cases_flat_or_negative"] = sum(
        1 for s in report["skills"].values() for c in s["cases"]
        if c["delta"] is not None and c["delta"] <= 0)
    print("mean Δ (with − without) across %d skills: %s" % (len(all_d), report["mean_delta_all"]))
    print("mean with-skill pass fraction: %s over %d scored cases; %d case(s) flat or negative"
          % (report["mean_with_skill"], report["cases_scored"], report["cases_flat_or_negative"]))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=1, sort_keys=True)
            f.write("\n")
        print("wrote %s" % args.out)

    # A harness whose only return is 0 cannot report a regression. These gates
    # give it a failure path; without one, "the evals passed" means nothing.
    rc = 0
    if not withs:
        print("GATE FAIL: no case produced a score -- the harness ran nothing.")
        rc = 1
    if args.min_delta is not None and (report["mean_delta_all"] is None
                                       or report["mean_delta_all"] < args.min_delta):
        print("GATE FAIL: mean delta %s < %.3f" % (report["mean_delta_all"], args.min_delta))
        rc = 1
    if args.min_with is not None and (report["mean_with_skill"] is None
                                      or report["mean_with_skill"] < args.min_with):
        print("GATE FAIL: mean with-skill pass fraction %s < %.3f"
              % (report["mean_with_skill"], args.min_with))
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
