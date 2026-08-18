#!/usr/bin/env python3
"""Deterministic trigger (discoverability) evaluation for the skill library.

An agent chooses a skill from its `name` + `description` alone, so those two
fields must route real user requests to the right skill and keep near-miss
requests away from it. This script measures that with a lexical retriever
(BM25 over name+description) — a deterministic proxy for model routing that
runs in milliseconds, in CI, with no API key. It is a proxy: a skill whose
positive queries do not even lexically retrieve it is unlikely to be chosen by
a model either, and confusion pairs surface descriptions that overlap.

Cases live with each skill in `skills/<name>/evals/evals.json` using the
anthropics/skills `skill-creator` envelope plus routing extensions:

  {"skill_name": "analysis-of-competing-hypotheses", "evals": [{
    "id": 1, "case_id": "ach-pos-1", "kind": "positive",
    "prompt": "the user request, as a user would phrase it",
    "expected_output": "human-readable success description", "files": [],
    "expectations": ["verifiable check 1", "verifiable check 2"]
  }]}

Scoring rules
  positive/edge : the owning skill must rank 1 for the query
  negative      : the owning skill must NOT rank 1; if `skills` names a sibling,
                  we also report whether that sibling ranked 1 (routing)

Usage:
  python3 evaluation/trigger_eval.py                 # summary
  python3 evaluation/trigger_eval.py --skill NAME    # per-query detail
  python3 evaluation/trigger_eval.py --json out.json
  python3 evaluation/trigger_eval.py --min-rank1 0.80 --min-negative 0.80   # CI gate

Stdlib only. Python 3.9+.
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from score_skills import parse_frontmatter, read, STOPWORDS  # noqa: E402
from eval_schema import load_eval_file  # noqa: E402

K1, B = 1.5, 0.75


def stem(t):
    for suf in ("ings", "ing", "edly", "ed", "es", "s", "ly"):
        if len(t) > 4 and t.endswith(suf):
            return t[: -len(suf)]
    return t


def toks(s):
    out = []
    for t in re.findall(r"[a-z][a-z0-9]+", s.lower()):
        if t in STOPWORDS or len(t) < 3:
            continue
        out.append(stem(t))
    return out


class BM25:
    def __init__(self, docs):
        self.names = sorted(docs)
        self.tf = {n: Counter(toks(docs[n])) for n in self.names}
        self.len = {n: sum(self.tf[n].values()) for n in self.names}
        self.avg = sum(self.len.values()) / max(1, len(self.names))
        df = Counter()
        for n in self.names:
            df.update(set(self.tf[n]))
        N = len(self.names)
        self.idf = {t: math.log(1 + (N - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def score(self, query):
        q = toks(query)
        res = []
        for n in self.names:
            s = 0.0
            for t in q:
                f = self.tf[n].get(t, 0)
                if not f:
                    continue
                s += self.idf[t] * f * (K1 + 1) / (f + K1 * (1 - B + B * self.len[n] / self.avg))
            res.append((round(s, 6), n))
        # deterministic: score desc, then name asc
        res.sort(key=lambda x: (-x[0], x[1]))
        return res


def load_library(root):
    docs, cases = {}, []
    sdir = os.path.join(root, "skills")
    for name in sorted(os.listdir(sdir)):
        # Leading underscore = contributor scaffolding (skills/_TEMPLATE), not a skill.
        p = os.path.join(sdir, name, "SKILL.md")
        if name.startswith("_") or not os.path.isfile(p):
            continue
        fm, _ = parse_frontmatter(read(p))
        desc = str(fm.get("description", ""))
        # Method acronyms (ACH, TRL, GRADE, SIFT ...) are how users name a method;
        # repeat them so an acronym in the query is a strong signal (documented boost).
        acronyms = " ".join(a for a in re.findall(r"\b[A-Z][A-Z0-9-]{1,7}\b", desc) for _ in range(3))
        docs[name] = "%s %s %s %s" % (name.replace("-", " "), name.replace("-", " "), desc, acronyms)
        ep = os.path.join(sdir, name, "evals", "evals.json")
        if os.path.isfile(ep):
            try:
                _declared, loaded, _canonical = load_eval_file(ep, name)
                for c in loaded:
                    c = dict(c)
                    c["owner"] = name
                    cases.append(c)
            except ValueError as e:
                cases.append({"owner": name, "id": "PARSE-ERROR", "kind": "invalid", "query": "", "error": str(e)})
    return docs, cases


def evaluate(root):
    docs, cases = load_library(root)
    bm = BM25(docs)
    per_skill = defaultdict(lambda: {"positive": 0, "positive_rank1": 0, "negative": 0, "negative_ok": 0,
                                     "negative_routed": 0, "rr_sum": 0.0, "failures": []})
    confusion = Counter()
    invalid = []
    for c in cases:
        owner = c["owner"]
        kind = c.get("kind", "positive")
        q = c.get("prompt", "")
        if kind == "invalid" or not q:
            invalid.append("%s: %s" % (owner, c.get("error", "missing query")))
            continue
        ranked = bm.score(q)
        names = [n for _, n in ranked]
        top = names[0] if names else ""
        rank = names.index(owner) + 1 if owner in names else 0
        ps = per_skill[owner]
        if kind in ("positive", "edge"):
            ps["positive"] += 1
            ps["rr_sum"] += (1.0 / rank) if rank else 0.0
            if top == owner:
                ps["positive_rank1"] += 1
            else:
                ps["failures"].append("%s [%s] → rank %d, top=%s" % (c.get("case_id", c.get("id", "?")), kind, rank, top))
                confusion[(owner, top)] += 1
        elif kind == "negative":
            ps["negative"] += 1
            if top != owner:
                ps["negative_ok"] += 1
                if c.get("skills") and top in c.get("skills", []):
                    ps["negative_routed"] += 1
            else:
                ps["failures"].append("%s [negative] → owner ranked 1 (should not); expected %s" % (c.get("case_id", c.get("id", "?")), ",".join(c.get("skills", []))))
    tot_pos = sum(v["positive"] for v in per_skill.values())
    tot_pos_ok = sum(v["positive_rank1"] for v in per_skill.values())
    tot_neg = sum(v["negative"] for v in per_skill.values())
    tot_neg_ok = sum(v["negative_ok"] for v in per_skill.values())
    tot_neg_routed = sum(v["negative_routed"] for v in per_skill.values())
    mrr = sum(v["rr_sum"] for v in per_skill.values()) / tot_pos if tot_pos else 0.0
    skills_without_cases = [n for n in docs if n not in per_skill]
    return {
        "n_skills": len(docs), "n_cases": len(cases), "skills_with_cases": len(per_skill),
        "skills_without_cases": skills_without_cases,
        "positive_cases": tot_pos, "positive_rank1": tot_pos_ok,
        "rank1_rate": round(tot_pos_ok / tot_pos, 4) if tot_pos else 0.0,
        "mrr": round(mrr, 4),
        "negative_cases": tot_neg, "negative_not_triggered": tot_neg_ok,
        "negative_rate": round(tot_neg_ok / tot_neg, 4) if tot_neg else 0.0,
        "negative_routed_to_named_sibling": tot_neg_routed,
        "invalid_cases": invalid,
        "confusion_pairs": [{"owner": a, "retrieved": b, "count": n} for (a, b), n in sorted(confusion.items(), key=lambda kv: (-kv[1], kv[0]))],
        "per_skill": {k: dict(v) for k, v in sorted(per_skill.items())},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(HERE))
    ap.add_argument("--skill")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--min-rank1", type=float)
    ap.add_argument("--min-negative", type=float)
    ap.add_argument("--min-cases", type=int, default=None, help="exit 1 if any skill has fewer positive cases")
    ap.add_argument("--min-routed", type=float, default=None,
                    help="exit 1 if the share of negative cases retrieved by the sibling "
                         "their `skills` field names falls below this. Without it the "
                         "negative gate is nearly free: a retriever that scores every "
                         "document 0.0 still 'holds' ~99%% of negatives, because holding "
                         "only requires that the owner not rank first.")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if args.skill:
        docs, cases = load_library(root)
        bm = BM25(docs)
        for c in cases:
            if c["owner"] != args.skill:
                continue
            ranked = bm.score(c.get("prompt", ""))[:3]
            print("%-14s %-9s %s" % (c.get("case_id", c.get("id", "?")), c.get("kind", "positive"), c.get("prompt", "")[:100]))
            for s, n in ranked:
                print("      %6.2f  %s" % (s, n))
        return 0
    r = evaluate(root)
    if r["n_skills"] == 0 or r["n_cases"] == 0:
        print("FAIL: inspected %d skills and %d eval cases -- a run that scores nothing is "
              "not a pass." % (r["n_skills"], r["n_cases"]))
        return 1
    print("Trigger eval: %d skills, %d cases (%d skills without cases)" % (r["n_skills"], r["n_cases"], len(r["skills_without_cases"])))
    print("  positive rank-1 rate: %.1f%% (%d/%d)   MRR %.3f" % (100 * r["rank1_rate"], r["positive_rank1"], r["positive_cases"], r["mrr"]))
    print("  negative not-triggered: %.1f%% (%d/%d); routed to named sibling: %d" % (100 * r["negative_rate"], r["negative_not_triggered"], r["negative_cases"], r["negative_routed_to_named_sibling"]))
    if r["invalid_cases"]:
        print("  INVALID: " + "; ".join(r["invalid_cases"]))
    if r["confusion_pairs"]:
        print("  top confusions: " + "; ".join("%s→%s×%d" % (c["owner"], c["retrieved"], c["count"]) for c in r["confusion_pairs"][:8]))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=1, sort_keys=True)
            f.write("\n")
    rc = 0
    if args.min_rank1 is not None and r["rank1_rate"] < args.min_rank1:
        print("GATE FAIL: rank-1 %.3f < %.3f" % (r["rank1_rate"], args.min_rank1)); rc = 1
    if args.min_negative is not None and r["negative_rate"] < args.min_negative:
        print("GATE FAIL: negative %.3f < %.3f" % (r["negative_rate"], args.min_negative)); rc = 1
    # Sanity: the negative gate is satisfiable by a broken retriever, so verify the
    # retriever discriminates at all before trusting any of these numbers.
    if r["positive_cases"] and r["rank1_rate"] < 0.5:
        print("WARNING: positive rank-1 rate %.1f%% is near or below chance -- the retriever "
              "may be broken, which would also make the negative rate meaningless."
              % (100 * r["rank1_rate"]))
    if args.min_routed is not None:
        routed = (r["negative_routed_to_named_sibling"] / r["negative_cases"]) if r["negative_cases"] else 0.0
        if routed < args.min_routed:
            print("GATE FAIL: negatives routed to their named sibling %.3f < %.3f" % (routed, args.min_routed))
            rc = 1
    if args.min_cases is not None:
        short = [n for n in sorted(set(list(r["per_skill"]) + r["skills_without_cases"])) if r["per_skill"].get(n, {}).get("positive", 0) < args.min_cases]
        if short:
            print("GATE FAIL: skills with < %d positive cases: %s" % (args.min_cases, ", ".join(short))); rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
