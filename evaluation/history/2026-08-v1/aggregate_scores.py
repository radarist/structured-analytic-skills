#!/usr/bin/env python3
"""Aggregate rubric scores from a TSV into a markdown scoresheet.

Usage: python3 evaluation/aggregate_scores.py <scores.tsv> <out.md> <title>

TSV format (header row: file<TAB>scores<TAB>gaps):
  repo-relative path <TAB> c1,...,c10 (raw 0/1/2, comma-joined) <TAB> free-text gaps

Weights follow evaluation/rubric.md (same for Rubric A and B):
  c1=10, c2=15, c3=15, c4=10, c5=10, c6=10, c7=10, c8=10, c9=5, c10=5
Weighted points per criterion = raw/2 * weight. Total out of 100.
"""

import sys
from collections import defaultdict

WEIGHTS = [10, 15, 15, 10, 10, 10, 10, 10, 5, 5]

SKILL_CATEGORIES = {
    "Decision & strategy": [
        "analysis-of-competing-hypotheses", "premortem-analysis", "scenario-planning",
        "cynefin-classification", "three-horizons", "five-forces-analysis",
        "wardley-map-drafting", "jtbd-framing", "cheapest-experiment", "foresight",
        "delphi-method", "decompose-research-question",
    ],
    "Foresight": [
        "horizon-scanning", "steep-pestle-analysis", "trend-analysis", "futures-wheel",
        "cross-impact-analysis", "backcasting", "causal-layered-analysis",
    ],
    "Technology assessment": [
        "score-technology-readiness", "apply-hype-cycle", "evolution-stage",
        "position-competitor", "estimate-market-size", "oss-project-health",
        "assess-research-momentum", "read-patent-landscape", "analyze-patent-claims",
        "analyze-release-notes", "detect-funding-round", "detect-ma-event",
    ],
    "Evidence & verification": [
        "rate-source-admiralty", "sift-source-check", "grounded-answer",
        "grounded-fact-check", "triangulate-sources", "verify-citations",
        "claim-provenance", "abstain-or-escalate", "key-assumptions-check",
        "steelman-argument", "red-team-claim", "critique-report",
        "evidence-appraisal", "meta-analysis",
    ],
    "Quantitative checks": [
        "quantitative-sanity-check", "test-significance", "bayesian-update",
        "brier-score-calibration", "assess-study-bias", "benchmark-model-claims",
        "systematic-review", "experimental-design",
    ],
    "Domain-specific": ["chemistry-claim-check", "smiles-sanity-check"],
    "Writing": ["write-imrad-report", "write-srl-brief", "pyramid-principle", "cite-ieee"],
}


def category_of(path):
    parts = path.split("/")
    if parts[0] == "skills":
        name = parts[1]
        for cat, names in SKILL_CATEGORIES.items():
            if name in names:
                return f"skills: {cat}"
        return "skills: (uncategorized/new)"
    return f"methodologies: {parts[1]}"


def main():
    tsv_path, out_path, title = sys.argv[1], sys.argv[2], sys.argv[3]
    rows = []
    with open(tsv_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("file\t"):
                continue
            path, scores, gaps = line.split("\t", 2)
            raw = [int(x) for x in scores.split(",")]
            assert len(raw) == 10, f"{path}: expected 10 scores"
            total = sum(r / 2 * w for r, w in zip(raw, WEIGHTS))
            rows.append((path, raw, total, gaps))

    cat_rows = defaultdict(list)
    for r in rows:
        cat_rows[category_of(r[0])].append(r)

    out = []
    out.append(f"# {title}\n")
    out.append(f"Scored with `evaluation/rubric.md`; {len(rows)} files. "
               "Raw scores 0/1/2 per criterion (order S1–S10 / M1–M10); "
               "weighted total out of 100.\n")

    out.append("## Per-category summary\n")
    out.append("| Category | Files | Mean total | Min | Max |")
    out.append("|---|---|---|---|---|")
    for cat in sorted(cat_rows):
        rs = cat_rows[cat]
        totals = [r[2] for r in rs]
        out.append(f"| {cat} | {len(rs)} | {sum(totals)/len(totals):.1f} | "
                   f"{min(totals):.1f} | {max(totals):.1f} |")
    all_totals = [r[2] for r in rows]
    out.append(f"| **ALL** | **{len(rows)}** | **{sum(all_totals)/len(all_totals):.1f}** | "
               f"**{min(all_totals):.1f}** | **{max(all_totals):.1f}** |")

    out.append("\n## Criterion means (population split)\n")
    for label, pred in (("Skills (Rubric A)", lambda p: p.startswith("skills/")),
                        ("Methodologies (Rubric B)", lambda p: p.startswith("methodologies/"))):
        sub = [r for r in rows if pred(r[0])]
        if not sub:
            continue
        means = [sum(r[1][i] for r in sub) / len(sub) for i in range(10)]
        cells = " | ".join(f"{m:.2f}" for m in means)
        out.append(f"**{label}** (n={len(sub)}): {cells}")

    out.append("\n## Per-file scores\n")
    out.append("| File | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | Total | Gaps |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for path, raw, total, gaps in sorted(rows, key=lambda r: r[2]):
        out.append(f"| {path} | " + " | ".join(map(str, raw)) +
                   f" | **{total:.1f}** | {gaps} |")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"wrote {out_path}: {len(rows)} files, overall mean "
          f"{sum(all_totals)/len(all_totals):.1f}")


if __name__ == "__main__":
    main()
