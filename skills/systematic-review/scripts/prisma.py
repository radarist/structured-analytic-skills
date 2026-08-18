#!/usr/bin/env python3
"""prisma.py -- PRISMA 2020 flow bookkeeping + dual-screening agreement.

Companion tool for the `systematic-review` skill. Stdlib only, Python 3.9+.

Subcommands:
  flow   Validate the PRISMA 2020 arithmetic chain (identified -> screened ->
         full-text assessed -> included), print the flow table, and flag any
         stage that does not add up (exit 1).
  kappa  Cohen's kappa for two screeners' include(1)/exclude(0) decisions
         given as a JSON list of {"a": 0/1, "b": 0/1}; --adjudicate lists the
         0-based indexes of disagreements to route to a third reviewer.

--selftest runs hand-verified checks and exits non-zero on failure.
"""

import argparse
import json
import sys


# ---------------------------------------------------------------------------
# Cohen's kappa (dual screening)
# ---------------------------------------------------------------------------

def kappa_band(k):
    """Map a kappa value to the conventional interpretation band."""
    if k < 0.0:
        return "poor (less than chance agreement)"
    if k <= 0.20:
        return "slight"
    if k <= 0.40:
        return "fair"
    if k <= 0.60:
        return "moderate"
    if k <= 0.80:
        return "substantial"
    return "almost perfect"


def cohens_kappa(pairs):
    """Cohen's kappa for two raters with binary (0/1) decisions.

    pairs: list of (a, b) tuples, one per record. Returns
    (n, observed, expected, kappa); kappa is None when expected agreement
    is 1.0 (ratings have no variance, so kappa is undefined).
    """
    n = len(pairs)
    if n == 0:
        raise ValueError("no paired decisions")
    observed = sum(1 for a, b in pairs if a == b) / n
    p_a1 = sum(a for a, _ in pairs) / n  # screener A's include rate
    p_b1 = sum(b for _, b in pairs) / n  # screener B's include rate
    # Chance agreement: both include, or both exclude, by independent rates.
    expected = p_a1 * p_b1 + (1.0 - p_a1) * (1.0 - p_b1)
    if abs(1.0 - expected) < 1e-12:
        return n, observed, expected, None
    return n, observed, expected, (observed - expected) / (1.0 - expected)


def disagreement_indexes(pairs):
    """0-based indexes of records where the two screeners disagreed."""
    return [i for i, (a, b) in enumerate(pairs) if a != b]


def load_pairs(path):
    """Load and validate a screening file: JSON list of {"a": 0/1, "b": 0/1}."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list) or not data:
        raise ValueError('expected a non-empty JSON list of {"a": 0/1, "b": 0/1}')
    pairs = []
    for i, item in enumerate(data):
        if (not isinstance(item, dict)
                or item.get("a") not in (0, 1)
                or item.get("b") not in (0, 1)):
            raise ValueError(f'item {i} is not {{"a": 0/1, "b": 0/1}}: {item!r}')
        pairs.append((item["a"], item["b"]))
    return pairs


# ---------------------------------------------------------------------------
# PRISMA 2020 flow
# ---------------------------------------------------------------------------

def flow_checks(identified, deduped, screened, excluded_title,
                fulltext, excluded_fulltext, included,
                sought=None, not_retrieved=0):
    """Stage-by-stage equations of the PRISMA 2020 flow.

    PRISMA 2020 places two boxes between screening and eligibility that a
    three-arrow chain silently drops: "Reports sought for retrieval" and
    "Reports not retrieved" (Page et al., BMJ 2021;372:n71, Fig. 1). A review
    in which some reports could not be obtained is conforming, not broken, so
    the chain below models them explicitly:

        screened - excluded          = sought for retrieval
        sought   - not retrieved     = assessed for eligibility
        assessed - excluded w/reasons = reports of included studies

    `sought` defaults to `fulltext + not_retrieved`, so a review that retrieved
    everything (not_retrieved = 0) behaves exactly as before.

    Returns a list of (ok, message) tuples, one per arrow in the diagram.
    """
    if sought is None:
        sought = fulltext + not_retrieved
    stages = [
        ("identified - duplicates = screened",
         identified, deduped, screened),
        ("screened - title/abstract exclusions = reports sought for retrieval",
         screened, excluded_title, sought),
        ("sought - not retrieved = reports assessed for eligibility",
         sought, not_retrieved, fulltext),
        ("assessed - full-text exclusions = reports of included studies",
         fulltext, excluded_fulltext, included),
    ]
    checks = []
    for label, before, removed, reported in stages:
        computed = before - removed
        msg = f"{label}: {before} - {removed} = {computed}"
        if computed != reported:
            msg += f"  [MISMATCH: reported {reported}]"
        checks.append((computed == reported, msg))
    return checks


def print_flow(identified, deduped, screened, excluded_title,
               fulltext, excluded_fulltext, included,
               sought=None, not_retrieved=0, studies=None):
    """Print the PRISMA 2020 flow table plus the stage checks.

    Returns the number of flagged inconsistencies.
    """
    if sought is None:
        sought = fulltext + not_retrieved
    rows = [
        ("Identification", "Records identified", identified),
        ("", "Duplicates removed", -deduped),
        ("Screening", "Records screened (title/abstract)", screened),
        ("", "Records excluded", -excluded_title),
        ("", "Reports sought for retrieval", sought),
        ("", "Reports not retrieved", -not_retrieved),
        ("Eligibility", "Reports assessed for eligibility", fulltext),
        ("", "Reports excluded (with reasons)", -excluded_fulltext),
        ("Included", "Reports of included studies", included),
    ]
    if studies is not None:
        rows.append(("", "Studies included in synthesis", studies))
    print("PRISMA 2020 flow")
    print("-" * 60)
    for stage, label, count in rows:
        print(f"{stage:<15}{label:<40}{count:>5}")
    print("-" * 60)
    print("Checks")
    n_flagged = 0
    for ok, msg in flow_checks(identified, deduped, screened, excluded_title,
                               fulltext, excluded_fulltext, included,
                               sought, not_retrieved):
        print(f"  [{'OK' if ok else 'FLAG'}] {msg}")
        n_flagged += not ok
    if n_flagged:
        print(f"\n{n_flagged} inconsistency(ies) flagged -- "
              "fix the counts (or the exclusion log) before reporting.")
    return n_flagged


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def non_negative_int(text):
    """argparse type: a count, which cannot be negative."""
    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError("counts must be non-negative")
    return value


def cmd_flow(args):
    flagged = print_flow(args.identified, args.deduped, args.screened,
                         args.excluded_title, args.fulltext,
                         args.excluded_fulltext, args.included,
                         args.sought, args.not_retrieved, args.studies)
    return 1 if flagged else 0


def cmd_kappa(args):
    try:
        pairs = load_pairs(args.file)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    n, observed, expected, kappa = cohens_kappa(pairs)
    print(f"paired decisions: {n}")
    print(f"screener A include rate: {sum(a for a, _ in pairs) / n:.3f}")
    print(f"screener B include rate: {sum(b for _, b in pairs) / n:.3f}")
    print(f"observed agreement: {observed:.3f}")
    print(f"expected agreement (chance): {expected:.3f}")
    if kappa is None:
        print("Cohen's kappa: undefined "
              "(expected agreement = 1.0; no variance in ratings)")
    else:
        print(f"Cohen's kappa: {kappa:.3f} ({kappa_band(kappa)})")
    if args.adjudicate:
        idx = disagreement_indexes(pairs)
        if idx:
            print("disagreements (0-based indexes, route to adjudication): "
                  + ", ".join(map(str, idx)))
        else:
            print("disagreements: none")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="prisma.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selftest", action="store_true",
                        help="run hand-verified built-in checks and exit")
    sub = parser.add_subparsers(dest="command")

    f = sub.add_parser("flow", help="validate and print the PRISMA 2020 flow")
    f.add_argument("--identified", type=non_negative_int, required=True,
                   help="records identified before deduplication")
    f.add_argument("--deduped", type=non_negative_int, required=True,
                   help="duplicates removed")
    f.add_argument("--screened", type=non_negative_int, required=True,
                   help="records screened at title/abstract")
    f.add_argument("--excluded-title", type=non_negative_int, required=True,
                   help="records excluded at title/abstract")
    f.add_argument("--fulltext", type=non_negative_int, required=True,
                   help="full-text reports assessed for eligibility")
    f.add_argument("--excluded-fulltext", type=non_negative_int, required=True,
                   help="full-text reports excluded (with reasons)")
    f.add_argument("--sought", type=non_negative_int, default=None,
                   help="reports sought for retrieval (PRISMA 2020 box); "
                        "defaults to --fulltext plus --not-retrieved")
    f.add_argument("--not-retrieved", type=non_negative_int, default=0,
                   help="reports sought but not obtained (PRISMA 2020 box); "
                        "these are NOT full-text exclusions and carry no reason")
    f.add_argument("--studies", type=non_negative_int, default=None,
                   help="studies included in synthesis, when it differs from the "
                        "number of reports (one study may have several reports)")
    f.add_argument("--included", type=non_negative_int, required=True,
                   help="studies included in the synthesis")
    f.set_defaults(func=cmd_flow)

    k = sub.add_parser("kappa", help="Cohen's kappa for two screeners")
    k.add_argument("--file", required=True,
                   help='JSON list of {"a": 0/1, "b": 0/1} decisions')
    k.add_argument("--adjudicate", action="store_true",
                   help="list 0-based indexes of disagreements")
    k.set_defaults(func=cmd_kappa)
    return parser


# ---------------------------------------------------------------------------
# Selftest -- every expected value below was computed by hand, not by the tool
# ---------------------------------------------------------------------------

def selftest():
    checks = []

    def check(name, ok):
        checks.append((name, bool(ok)))

    # --- kappa on a 10-item micro-set, worked out by hand ---
    # By hand: 7 of 10 pairs agree            -> observed = 0.70
    #   A includes 6/10, B includes 5/10      -> rates 0.6 and 0.5
    #   expected = 0.6*0.5 + 0.4*0.5 = 0.50
    #   kappa = (0.70 - 0.50) / (1 - 0.50) = 0.40  -> band "fair"
    micro = [(1, 1), (1, 1), (1, 0), (0, 0), (1, 1),
             (0, 1), (0, 0), (1, 1), (0, 0), (1, 0)]
    n, po, pe, k = cohens_kappa(micro)
    check("kappa micro-set: n=10, observed=0.70, expected=0.50, kappa=0.40",
          n == 10 and abs(po - 0.70) < 1e-12
          and abs(pe - 0.50) < 1e-12 and abs(k - 0.40) < 1e-12)
    check("kappa 0.40 falls in the 'fair' band", kappa_band(k) == "fair")
    check("micro-set disagreement indexes are [2, 5, 9]",
          disagreement_indexes(micro) == [2, 5, 9])

    # Perfect agreement with variance -> kappa = 1.00 ("almost perfect").
    _, _, _, k_perfect = cohens_kappa([(1, 1), (0, 0), (1, 1), (0, 0)])
    check("perfect agreement gives kappa=1.00",
          k_perfect is not None and abs(k_perfect - 1.0) < 1e-12)

    # Constant ratings -> expected agreement 1.0 -> kappa undefined (None).
    _, _, _, k_flat = cohens_kappa([(1, 1), (1, 1)])
    check("constant ratings give undefined kappa", k_flat is None)

    # --- flow arithmetic ---
    # Consistent chain: 1240 - 315 = 925; 925 - 840 = 85; 85 - 61 = 24.
    good = flow_checks(1240, 315, 925, 840, 85, 61, 24)
    check("consistent flow passes all stage checks",
          all(ok for ok, _ in good) and len(good) == 4)

    # PRISMA 2020 Fig. 1 places "Reports sought for retrieval" and "Reports not
    # retrieved" between screening and eligibility. A review that could not
    # obtain 5 of the 85 reports it sought is conforming and must pass:
    #   925 - 840 = 85 sought; 85 - 5 = 80 assessed; 80 - 61 = 19 included.
    retrieval = flow_checks(1240, 315, 925, 840, 80, 61, 19,
                            sought=85, not_retrieved=5)
    check("conforming flow with unretrieved reports passes",
          all(ok for ok, _ in retrieval))

    # ... and a genuine break in the new arrow is still caught.
    bad_retrieval = flow_checks(1240, 315, 925, 840, 80, 61, 19,
                                sought=85, not_retrieved=2)
    check("mis-stated non-retrieval is flagged",
          sum(1 for ok, _ in bad_retrieval if not ok) == 1)

    # Deliberate inconsistency: 85 - 61 = 24, but included is given as 25
    # (exclusions + included = 86 != 85 full-text assessed). Only the last
    # stage must be flagged.
    bad = flow_checks(1240, 315, 925, 840, 85, 61, 25)
    flagged = [msg for ok, msg in bad if not ok]
    check("flow with exclusions + included != full-text assessed is flagged",
          len(flagged) == 1 and "included" in flagged[0])

    n_pass = 0
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'} {name}")
        n_pass += ok
    print(f"selftest: {n_pass}/{len(checks)} checks passed")
    return 0 if n_pass == len(checks) else 1


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not getattr(args, "func", None):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
