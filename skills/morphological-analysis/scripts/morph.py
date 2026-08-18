#!/usr/bin/env python3
"""morph.py — General Morphological Analysis: Zwicky box, cross-consistency assessment, solution space.

Implements the definitions in ../SKILL.md:

  * Morphological field ("Zwicky box"): parameters P_1..P_n, each with a discrete
    list of values (conditions). A configuration picks exactly one value per
    parameter. Raw configuration count  N = |P_1| x |P_2| x ... x |P_n|
    (Zwicky, Morphological Astronomy 1948 / Discovery, Invention, Research 1969;
    Álvarez & Ritchey, Acta Morphologica Generalis 4(1), 2015, §2).
  * Cross-Consistency Assessment (CCA): every pair of values drawn from two
    different parameters is judged for MUTUAL consistency — no direction, no
    causality (Ritchey, J. Oper. Res. Soc. 57(7):792–801, 2006). A pair is either
    consistent or excluded as a purely LOGICAL contradiction, an EMPIRICAL
    implausibility, or a NORMATIVE constraint that Ritchey says must be "clearly
    designated as such". Every exclusion needs a stated reason.
  * Solution space: the configurations that contain no excluded pair (internally
    consistent). Enumerated by backtracking in the parameter/value order of the
    input file — deterministic. Above --max-enumerate raw configurations the tool
    reports lower/upper bounds instead and says so.
  * Drivers: values fixed as input; the tool lists the consistent configurations
    that contain them (Ritchey's use of the reduced field as an inference model).

Stdlib only. Python 3.9+. Deterministic (no clock, no randomness, sorted output).

Usage:
    python3 morph.py box       --file box.json [--json]
    python3 morph.py space     --file box.json [--max-enumerate 200000] [--json]
    python3 morph.py solutions --file box.json [--must "Param:Value" ...] [--limit 50] [--json]
    python3 morph.py cca       --file box.json [--json]      # exit 2 while any value pair is un-assessed
    python3 morph.py --demo                                   # the SKILL.md worked example
    python3 morph.py --selftest

box.json:
    {"problem": "...",
     "parameters": [{"name": "Storage", "values": ["None", "Small battery", ...]}, ...],
     "exclusions": [{"a": "Storage:None", "b": "Revenue:Tariff arbitrage",
                     "type": "logical | empirical | normative", "reason": "..."}, ...],
     "consistent": [{"a": "Param:Value", "b": "Param:Value", "reason": "..."}, ...],  # optional
     "assessed_blocks": [["Storage", "Control"], ...]}                                 # optional
    `consistent` records value pairs judged compatible; `assessed_blocks` declares whole
    parameter-pair blocks as assessed (every non-excluded pair in them counts as consistent).
    Exit codes: 0 ok · 1 invalid input/usage · 2 `cca` found un-assessed value pairs.
"""

import argparse
import itertools
import json
import sys

EXCLUSION_TYPES = ("logical", "empirical", "normative")

# Built-in example for --demo: the SKILL.md worked example — architecture and
# business model of a residential home-energy product. 5 parameters, 3-4 values
# each: 3 x 4 x 3 x 3 x 4 = 432 raw configurations, 115 cross-parameter value pairs.
DEMO = {
    "problem": "Which architectures for a residential home-energy product are internally "
               "consistent, and which of them can sell grid flexibility?",
    "parameters": [
        {"name": "Storage", "values": ["None (controls only)", "Small battery (5 kWh)", "Large battery (15 kWh)"]},
        {"name": "Control", "values": ["Manual app", "Rule-based schedule", "Cloud optimiser", "Local edge optimiser"]},
        {"name": "Revenue", "values": ["Self-consumption savings", "Tariff arbitrage", "Grid flexibility (VPP)"]},
        {"name": "Ownership", "values": ["Customer-owned", "Leased", "Utility-owned"]},
        {"name": "Pricing", "values": ["One-off purchase", "Monthly subscription", "Revenue share", "Bundled in tariff"]},
    ],
    "exclusions": [
        {"a": "Storage:None (controls only)", "b": "Revenue:Tariff arbitrage", "type": "logical",
         "reason": "arbitrage means charging when cheap and discharging at peak; with no storage there is nothing to shift"},
        {"a": "Storage:None (controls only)", "b": "Revenue:Grid flexibility (VPP)", "type": "empirical",
         "reason": "aggregators contract dispatchable kW; a controls-only home cannot commit capacity reliably"},
        {"a": "Storage:None (controls only)", "b": "Ownership:Utility-owned", "type": "empirical",
         "reason": "no utility carries a 150-euro controller as an owned, serviced balance-sheet asset"},
        {"a": "Control:Manual app", "b": "Revenue:Tariff arbitrage", "type": "empirical",
         "reason": "households abandon manual daily scheduling within weeks; arbitrage income depends on daily action"},
        {"a": "Control:Manual app", "b": "Revenue:Grid flexibility (VPP)", "type": "logical",
         "reason": "VPP dispatch is a machine-to-machine signal with minutes to respond; manual control cannot answer it"},
        {"a": "Revenue:Self-consumption savings", "b": "Pricing:Revenue share", "type": "logical",
         "reason": "there is no grid income to share"},
        {"a": "Ownership:Utility-owned", "b": "Pricing:One-off purchase", "type": "logical",
         "reason": "a one-off purchase transfers title to the customer; the utility would no longer own the asset"},
        {"a": "Ownership:Leased", "b": "Pricing:One-off purchase", "type": "logical",
         "reason": "a lease is by definition a recurring payment"},
        {"a": "Ownership:Customer-owned", "b": "Pricing:Bundled in tariff", "type": "normative",
         "reason": "company policy: no tariff lock-in on hardware the customer already owns (consumer-protection exposure)"},
    ],
    "assessed_blocks": [
        ["Storage", "Control"], ["Storage", "Revenue"], ["Storage", "Ownership"], ["Storage", "Pricing"],
        ["Control", "Revenue"], ["Control", "Ownership"], ["Control", "Pricing"],
        ["Revenue", "Ownership"], ["Revenue", "Pricing"], ["Ownership", "Pricing"],
    ],
}
DEMO_DRIVER = "Revenue:Grid flexibility (VPP)"


class BoxError(ValueError):
    """Raised when the morphological box description is malformed."""


# --- parsing -----------------------------------------------------------------


class Box:
    """A validated morphological field plus its cross-consistency assessment."""

    def __init__(self, data):
        if not isinstance(data, dict):
            raise BoxError("top level must be a JSON object")
        self.problem = str(data.get("problem", "")).strip()
        self.names, self.values = self._parse_parameters(data.get("parameters"))
        self.index = {n: i for i, n in enumerate(self.names)}
        self.vindex = [{v: j for j, v in enumerate(vals)} for vals in self.values]
        self.exclusions = []          # dicts: a=(pi,vi) b=(pj,vj) type reason (pi < pj)
        self.excluded = set()         # {(pi, vi, pj, vj)} with pi < pj
        self.consistent = set()       # {(pi, vi, pj, vj)} with pi < pj
        self.assessed_blocks = set()  # {(pi, pj)} with pi < pj
        self._parse_exclusions(data.get("exclusions", []))
        self._parse_consistent(data.get("consistent", []))
        self._parse_blocks(data.get("assessed_blocks", []))

    @staticmethod
    def _parse_parameters(raw):
        if isinstance(raw, dict):
            raw = [{"name": k, "values": v} for k, v in raw.items()]
        if not isinstance(raw, list) or len(raw) < 2:
            raise BoxError("'parameters' must list at least 2 parameters")
        names, values = [], []
        for i, p in enumerate(raw, 1):
            if not isinstance(p, dict) or not isinstance(p.get("name"), str) or not p["name"].strip():
                raise BoxError(f"parameter #{i}: needs a non-empty string 'name'")
            name = p["name"].strip()
            if ":" in name:
                raise BoxError(f"parameter {name!r}: names must not contain ':' (it separates Param:Value)")
            if name in names:
                raise BoxError(f"duplicate parameter name {name!r}")
            vals = p.get("values")
            if not isinstance(vals, list) or len(vals) < 2:
                raise BoxError(f"parameter {name!r}: needs a list of at least 2 values "
                               "(a single-valued parameter is a constant — fold it into the problem statement)")
            clean = []
            for v in vals:
                if not isinstance(v, str) or not v.strip():
                    raise BoxError(f"parameter {name!r}: every value must be a non-empty string")
                v = v.strip()
                if v in clean:
                    raise BoxError(f"parameter {name!r}: duplicate value {v!r}")
                clean.append(v)
            names.append(name)
            values.append(clean)
        return names, values

    def ref(self, text, where):
        """Resolve 'Param:Value' to (parameter index, value index)."""
        if not isinstance(text, str) or ":" not in text:
            raise BoxError(f"{where}: reference {text!r} must be written 'Param:Value'")
        pname, vname = text.split(":", 1)
        pname, vname = pname.strip(), vname.strip()
        if pname not in self.index:
            raise BoxError(f"{where}: unknown parameter {pname!r} in {text!r} "
                           f"(parameters: {', '.join(self.names)})")
        pi = self.index[pname]
        if vname not in self.vindex[pi]:
            raise BoxError(f"{where}: unknown value {vname!r} for parameter {pname!r} "
                           f"(values: {', '.join(self.values[pi])})")
        return pi, self.vindex[pi][vname]

    def pair(self, entry, where):
        """Resolve an {a, b} entry to an ordered cross-parameter key (pi, vi, pj, vj)."""
        if not isinstance(entry, dict):
            raise BoxError(f"{where}: must be an object with 'a' and 'b'")
        a = self.ref(entry.get("a"), where + " 'a'")
        b = self.ref(entry.get("b"), where + " 'b'")
        if a[0] == b[0]:
            raise BoxError(f"{where}: both values belong to parameter {self.names[a[0]]!r} — values of one "
                           "parameter are mutually exclusive by construction; CCA only assesses pairs "
                           "across parameters")
        if a[0] > b[0]:
            a, b = b, a
        return a[0], a[1], b[0], b[1]

    def _parse_exclusions(self, raw):
        if not isinstance(raw, list):
            raise BoxError("'exclusions' must be a list")
        for i, e in enumerate(raw, 1):
            where = f"exclusion #{i}"
            key = self.pair(e, where)
            etype = str(e.get("type", "")).strip().lower()
            if etype not in EXCLUSION_TYPES:
                raise BoxError(f"{where}: 'type' must be one of {', '.join(EXCLUSION_TYPES)} (got {etype!r})")
            reason = str(e.get("reason", "")).strip()
            if not reason:
                raise BoxError(f"{where}: needs a non-empty 'reason' — CCA exclusions must be justified, "
                               "not asserted")
            if key in self.excluded:
                raise BoxError(f"{where}: pair {self.label(key)} is listed twice")
            self.excluded.add(key)
            self.exclusions.append({"key": key, "type": etype, "reason": reason})

    def _parse_consistent(self, raw):
        if not isinstance(raw, list):
            raise BoxError("'consistent' must be a list")
        for i, e in enumerate(raw, 1):
            key = self.pair(e, f"consistent #{i}")
            if key in self.excluded:
                raise BoxError(f"consistent #{i}: pair {self.label(key)} is also listed under 'exclusions'")
            self.consistent.add(key)

    def _parse_blocks(self, raw):
        if not isinstance(raw, list):
            raise BoxError("'assessed_blocks' must be a list of [ParamA, ParamB] pairs")
        for i, blk in enumerate(raw, 1):
            if not isinstance(blk, list) or len(blk) != 2 or not all(isinstance(x, str) for x in blk):
                raise BoxError(f"assessed_blocks #{i}: must be a pair of parameter names")
            try:
                a, b = self.index[blk[0].strip()], self.index[blk[1].strip()]
            except KeyError as exc:
                raise BoxError(f"assessed_blocks #{i}: unknown parameter {exc.args[0]!r}") from None
            if a == b:
                raise BoxError(f"assessed_blocks #{i}: a block needs two different parameters")
            self.assessed_blocks.add((min(a, b), max(a, b)))

    # --- helpers ---

    def label(self, key):
        pi, vi, pj, vj = key
        return f"{self.names[pi]}:{self.values[pi][vi]} × {self.names[pj]}:{self.values[pj][vj]}"

    def sizes(self):
        return [len(v) for v in self.values]

    def raw_count(self, domains=None):
        n = 1
        for d in (domains if domains is not None else self.values):
            n *= len(d)
        return n

    def blocks(self):
        """All parameter-pair blocks (pi, pj) with pi < pj, in parameter order."""
        return list(itertools.combinations(range(len(self.names)), 2))

    def is_assessed(self, key):
        return key in self.excluded or key in self.consistent or (key[0], key[2]) in self.assessed_blocks


def load_box(path):
    """Read a box description from a JSON file ('-' = stdin)."""
    try:
        if path == "-":
            data = json.load(sys.stdin)
        else:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
    except OSError as exc:
        raise BoxError(f"cannot read {path}: {exc}") from None
    except json.JSONDecodeError as exc:
        raise BoxError(f"{path}: not valid JSON ({exc})") from None
    return Box(data)


# --- the analysis --------------------------------------------------------------


def parse_must(box, musts):
    """Resolve --must 'Param:Value' drivers to a list of (pi, vi); one value per parameter."""
    fixed = {}
    for m in musts or []:
        pi, vi = box.ref(m, "--must")
        if pi in fixed and fixed[pi] != vi:
            raise BoxError(f"--must fixes parameter {box.names[pi]!r} to two different values")
        fixed[pi] = vi
    return sorted(fixed.items())


def domains_for(box, fixed):
    doms = [list(range(len(v))) for v in box.values]
    for pi, vi in fixed:
        doms[pi] = [vi]
    return doms


def enumerate_solutions(box, fixed=(), collect=True, limit=None):
    """Backtracking enumeration of internally consistent configurations.

    Order is lexicographic in the file's parameter and value order, so output is
    deterministic. Returns (count, solutions) — solutions as tuples of value
    indices (at most `limit` of them when collect is True).
    """
    doms = domains_for(box, fixed)
    excluded = box.excluded
    n = len(box.names)
    assignment = [None] * n
    sols = []
    count = 0

    def rec(k):
        nonlocal count
        if k == n:
            count += 1
            if collect and (limit is None or len(sols) < limit):
                sols.append(tuple(assignment))
            return
        for v in doms[k]:
            for i in range(k):
                if (i, assignment[i], k, v) in excluded:
                    break
            else:
                assignment[k] = v
                rec(k + 1)
        assignment[k] = None

    rec(0)
    return count, sols


def brute_force_count(box, fixed=()):
    """Independent cross-check: filter the full Cartesian product (selftest only)."""
    doms = domains_for(box, fixed)
    count = 0
    for cfg in itertools.product(*doms):
        if not any((i, cfg[i], j, cfg[j]) in box.excluded for i, j in box.blocks()):
            count += 1
    return count


def bounds(box, fixed=()):
    """Lower/upper bounds on the consistent count without enumeration.

    lower: raw − Σ over exclusions of the configurations each one hits
           (Bonferroni; exact when no configuration contains two excluded pairs).
    upper: pick disjoint parameter-pair blocks greedily (smallest allowed share
           first) and multiply their allowed pair counts with the sizes of the
           unmatched parameters — every consistent configuration passes those
           blocks, so the product bounds the count from above.
    """
    doms = domains_for(box, fixed)
    raw = box.raw_count(doms)
    sizes = [len(d) for d in doms]
    active = [(pi, vi, pj, vj) for (pi, vi, pj, vj) in box.excluded
              if vi in doms[pi] and vj in doms[pj]]
    hit = 0
    for pi, _, pj, _ in active:
        hit += raw // (sizes[pi] * sizes[pj])
    lower = max(0, raw - hit)
    per_block = {}
    for pi, _, pj, _ in active:
        per_block[(pi, pj)] = per_block.get((pi, pj), 0) + 1
    ranked = []
    for pi, pj in box.blocks():
        total = sizes[pi] * sizes[pj]
        allowed = total - per_block.get((pi, pj), 0)
        ranked.append((allowed / total, pi, pj, allowed))
    ranked.sort()
    used = set()
    upper = 1
    for _, pi, pj, allowed in ranked:
        if pi in used or pj in used:
            continue
        used.update((pi, pj))
        upper *= allowed
    for k, s in enumerate(sizes):
        if k not in used:
            upper *= s
    return lower, min(upper, raw)


def cca_coverage(box):
    """Per-block assessment coverage and the list of un-assessed value pairs."""
    rows, unassessed = [], []
    for pi, pj in box.blocks():
        total = len(box.values[pi]) * len(box.values[pj])
        exc = cons = 0
        for vi in range(len(box.values[pi])):
            for vj in range(len(box.values[pj])):
                key = (pi, vi, pj, vj)
                if key in box.excluded:
                    exc += 1
                elif box.is_assessed(key):
                    cons += 1
                else:
                    unassessed.append(key)
        rows.append({"block": f"{box.names[pi]} × {box.names[pj]}", "pairs": total, "excluded": exc,
                     "consistent": cons, "unassessed": total - exc - cons,
                     "declared": (pi, pj) in box.assessed_blocks})
    return rows, unassessed


# --- output ------------------------------------------------------------------


def fmt_int(n):
    return f"{n:,}"


def config_values(box, cfg):
    return [box.values[k][v] for k, v in enumerate(cfg)]


def print_table(header, rows):
    widths = [len(h) for h in header]
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(cell))
    line = "  ".join(h.ljust(w) for h, w in zip(header, widths)).rstrip()
    print(line)
    for r in rows:
        print("  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip())


def cmd_box(box, as_json):
    if as_json:
        print(json.dumps({"problem": box.problem,
                          "parameters": [{"name": n, "values": v} for n, v in zip(box.names, box.values)],
                          "sizes": box.sizes(), "raw_configurations": box.raw_count()},
                         indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    if box.problem:
        print(f"Problem: {box.problem}")
    depth = max(box.sizes())
    header = [f"{n} ({len(v)})" for n, v in zip(box.names, box.values)]
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join("---" for _ in header) + "|")
    for r in range(depth):
        cells = [vals[r] if r < len(vals) else "" for vals in box.values]
        print("| " + " | ".join(cells) + " |")
    print(f"Raw configurations: {' × '.join(str(s) for s in box.sizes())} = {fmt_int(box.raw_count())}")
    return 0


def space_report(box, max_enumerate):
    raw = box.raw_count()
    by_type = {t: sum(1 for e in box.exclusions if e["type"] == t) for t in EXCLUSION_TYPES}
    blocks_hit = len({(e["key"][0], e["key"][2]) for e in box.exclusions})
    rep = {"problem": box.problem, "parameters": len(box.names), "sizes": box.sizes(), "raw": raw,
           "exclusions": len(box.exclusions), "exclusions_by_type": by_type,
           "blocks_with_exclusions": blocks_hit, "blocks_total": len(box.blocks()),
           "value_pairs_total": sum(len(box.values[i]) * len(box.values[j]) for i, j in box.blocks()),
           "enumerated": raw <= max_enumerate}
    if rep["enumerated"]:
        count, _ = enumerate_solutions(box, collect=False)
        rep["consistent"] = count
        rep["removed"] = raw - count
        rep["reduction_pct"] = round(100.0 * (raw - count) / raw, 1) if raw else 0.0
    else:
        lo, hi = bounds(box)
        rep["consistent_lower_bound"], rep["consistent_upper_bound"] = lo, hi
    return rep


def cmd_space(box, max_enumerate, as_json):
    rep = space_report(box, max_enumerate)
    if as_json:
        print(json.dumps(rep, indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    if box.problem:
        print(f"Problem: {box.problem}")
    print("Parameters: " + " × ".join(f"{n}({len(v)})" for n, v in zip(box.names, box.values)))
    print(f"Raw configurations: {' × '.join(str(s) for s in box.sizes())} = {fmt_int(rep['raw'])}")
    bt = rep["exclusions_by_type"]
    print(f"Exclusions: {rep['exclusions']} value pairs (logical {bt['logical']}, empirical {bt['empirical']}, "
          f"normative {bt['normative']}) in {rep['blocks_with_exclusions']} of {rep['blocks_total']} "
          f"parameter-pair blocks ({fmt_int(rep['value_pairs_total'])} value pairs to assess in total)")
    if rep["enumerated"]:
        print(f"Consistent configurations: {fmt_int(rep['consistent'])} of {fmt_int(rep['raw'])} "
              f"({fmt_int(rep['removed'])} removed = {rep['reduction_pct']} % reduction)")
    else:
        print(f"Consistent configurations: NOT ENUMERATED — raw {fmt_int(rep['raw'])} exceeds "
              f"--max-enumerate {fmt_int(max_enumerate)}")
        print(f"  bounds: {fmt_int(rep['consistent_lower_bound'])} ≤ consistent ≤ "
              f"{fmt_int(rep['consistent_upper_bound'])} (lower = raw minus configurations hit by each "
              "exclusion; upper = product over disjoint parameter-pair blocks of allowed pairs). "
              "Raise --max-enumerate for the exact count.")
    return 0


def cmd_solutions(box, musts, limit, max_enumerate, as_json):
    fixed = parse_must(box, musts)
    doms = domains_for(box, fixed)
    eff_raw = box.raw_count(doms)
    driver_txt = ", ".join(f"{box.names[pi]}:{box.values[pi][vi]}" for pi, vi in fixed)
    if eff_raw > max_enumerate:
        lo, hi = bounds(box, fixed)
        msg = (f"NOT ENUMERATED — {fmt_int(eff_raw)} raw configurations"
               f"{' with driver(s) fixed' if fixed else ''} exceed --max-enumerate {fmt_int(max_enumerate)}; "
               f"bounds {fmt_int(lo)} ≤ consistent ≤ {fmt_int(hi)}. Add --must drivers or raise --max-enumerate.")
        if as_json:
            print(json.dumps({"drivers": driver_txt, "raw_with_drivers": eff_raw, "enumerated": False,
                              "consistent_lower_bound": lo, "consistent_upper_bound": hi},
                             indent=2, sort_keys=True, ensure_ascii=False))
        else:
            print(msg)
        return 0
    total_consistent, _ = enumerate_solutions(box, collect=False)
    count, sols = enumerate_solutions(box, fixed, collect=True, limit=limit)
    if as_json:
        print(json.dumps({"drivers": driver_txt, "parameters": box.names, "raw": box.raw_count(),
                          "consistent_total": total_consistent, "matching": count,
                          "shown": len(sols), "limit": limit,
                          "solutions": [config_values(box, s) for s in sols]},
                         indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    if fixed:
        print(f"Consistent configurations containing {driver_txt}: {fmt_int(count)} of "
              f"{fmt_int(total_consistent)} consistent (raw {fmt_int(box.raw_count())})")
    else:
        print(f"Consistent configurations: {fmt_int(count)} (raw {fmt_int(box.raw_count())})")
    if count == 0:
        print("  none — the driver value(s) survive no consistent configuration; revisit the exclusions "
              "that touch them or accept that the option is closed")
        return 0
    rows = [[str(i)] + config_values(box, s) for i, s in enumerate(sols, 1)]
    print_table(["#"] + box.names, rows)
    if count > len(sols):
        print(f"(showing {len(sols)} of {fmt_int(count)}; raise --limit to see more)")
    return 0


def cmd_cca(box, as_json):
    rows, unassessed = cca_coverage(box)
    total = sum(r["pairs"] for r in rows)
    n_un = len(unassessed)
    complete = n_un == 0
    if as_json:
        print(json.dumps({"blocks": rows, "value_pairs_total": total, "unassessed_total": n_un,
                          "complete": complete,
                          "exclusions": [{"pair": box.label(e["key"]), "type": e["type"], "reason": e["reason"]}
                                         for e in box.exclusions],
                          "unassessed": [box.label(k) for k in unassessed]},
                         indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if complete else 2
    print(f"Cross-consistency assessment — {len(rows)} parameter-pair blocks, {fmt_int(total)} value pairs")
    table = [[r["block"], str(r["pairs"]), str(r["excluded"]), str(r["consistent"]), str(r["unassessed"]),
              "declared assessed" if r["declared"] else ""] for r in rows]
    table.append(["Total", str(total), str(sum(r["excluded"] for r in rows)),
                  str(sum(r["consistent"] for r in rows)), str(n_un), ""])
    print_table(["Block", "pairs", "excluded", "consistent", "un-assessed", ""], table)
    if box.exclusions:
        print("Exclusions:")
        for i, e in enumerate(box.exclusions, 1):
            print(f"  X{i} {box.label(e['key'])} — {e['type']} — {e['reason']}")
    if complete:
        print("CCA COMPLETE — every cross-parameter value pair has been assessed.")
        return 0
    print(f"Un-assessed value pairs ({n_un}):")
    for k in unassessed[:40]:
        print(f"  ? {box.label(k)}")
    if n_un > 40:
        print(f"  … and {n_un - 40} more")
    print(f"CCA INCOMPLETE — {n_un} of {total} value pairs un-assessed "
          f"({100.0 * n_un / total:.0f} %); the solution space is not yet trustworthy.")
    return 1


def cmd_demo():
    box = Box(DEMO)
    print("Demo — SKILL.md worked example: residential home-energy product architecture")
    print()
    cmd_space(box, 200000, False)
    print()
    cmd_solutions(box, [DEMO_DRIVER], 2, 200000, False)
    return 0


# --- selftest ------------------------------------------------------------------


def run_selftest():
    """Hand-verified checks: a fixed 2 x 3 x 2 box whose consistent configurations
    were counted by hand, plus cross-checks of the demo box against an
    independent brute-force count."""
    results = []

    def check(name, got, want):
        ok = got == want
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got!r}, expected {want!r}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    def expect_error(name, data, fragment):
        try:
            Box(data)
        except BoxError as exc:
            ok = fragment in str(exc)
            results.append(ok)
            print(f"{'PASS' if ok else 'FAIL'}  {name}: rejected ({str(exc)[:70]})")
            if not ok:
                print(f"SELFTEST FAILED at: {name} — message lacked {fragment!r}", file=sys.stderr)
                sys.exit(1)
            return
        print(f"FAIL  {name}: accepted invalid input", file=sys.stderr)
        sys.exit(1)

    # Fixed box: A{a1,a2} B{b1,b2,b3} C{c1,c2}; raw = 2*3*2 = 12.
    # Exclusions: (a1,b1) kills 1*1*2 = 2; (b2,c2) kills 2*1*1 = 2; (a2,c1) kills 1*3*1 = 3.
    # No configuration contains two of these pairs, so consistent = 12 - 7 = 5 by hand:
    #   (a1,b2,c1) (a1,b3,c1) (a1,b3,c2) (a2,b1,c2) (a2,b3,c2)
    fixed = {
        "problem": "selftest",
        "parameters": [{"name": "A", "values": ["a1", "a2"]},
                       {"name": "B", "values": ["b1", "b2", "b3"]},
                       {"name": "C", "values": ["c1", "c2"]}],
        "exclusions": [
            {"a": "A:a1", "b": "B:b1", "type": "logical", "reason": "hand case 1"},
            {"a": "C:c2", "b": "B:b2", "type": "empirical", "reason": "hand case 2 (reversed order)"},
            {"a": "A:a2", "b": "C:c1", "type": "normative", "reason": "hand case 3"},
        ],
    }
    box = Box(fixed)
    check("raw count = 2*3*2", box.raw_count(), 12)
    count, sols = enumerate_solutions(box)
    check("consistent count by hand (12 - 2 - 2 - 3)", count, 5)
    check("solutions in deterministic lexicographic order",
          [tuple(config_values(box, s)) for s in sols],
          [("a1", "b2", "c1"), ("a1", "b3", "c1"), ("a1", "b3", "c2"), ("a2", "b1", "c2"), ("a2", "b3", "c2")])
    check("brute force agrees with backtracking", brute_force_count(box), 5)
    check("--limit truncates the listing but not the count", enumerate_solutions(box, limit=2), (5, [(0, 1, 0), (0, 2, 0)]))
    check("driver A:a1 -> 3 configurations", enumerate_solutions(box, parse_must(box, ["A:a1"]), collect=False)[0], 3)
    check("driver B:b3 -> 3 configurations", enumerate_solutions(box, parse_must(box, ["B:b3"]), collect=False)[0], 3)
    check("drivers A:a2 + B:b3 -> 1 configuration",
          [config_values(box, s) for s in enumerate_solutions(box, parse_must(box, ["A:a2", "B:b3"]))[1]],
          [["a2", "b3", "c2"]])
    check("driver B:b1 with A:a2 -> exactly (a2,b1,c2)",
          enumerate_solutions(box, parse_must(box, ["B:b1", "A:a2"]))[1], [(1, 0, 1)])
    # Bounds by hand: lower = 12 - (2+2+3) = 5 (no overlaps, so exact); upper: blocks A×B 5/6,
    # A×C 3/4, B×C 5/6 -> greedy takes A×C (3 allowed pairs) × |B| = 9.
    check("bounds when not enumerating (lower, upper)", bounds(box), (5, 9))
    check("space report enumerates at the limit", space_report(box, 12)["consistent"], 5)
    rep = space_report(box, 11)
    check("space report switches to bounds above the limit",
          (rep["enumerated"], rep["consistent_lower_bound"], rep["consistent_upper_bound"]), (False, 5, 9))
    check("reduction percentage 7/12", space_report(box, 12)["reduction_pct"], 58.3)

    # CCA coverage: value pairs = |A||B| + |A||C| + |B||C| = 6 + 4 + 6 = 16; 3 excluded -> 13 un-assessed.
    rows, un = cca_coverage(box)
    check("value pairs to assess = 16", sum(r["pairs"] for r in rows), 16)
    check("un-assessed pairs with only 3 exclusions", len(un), 13)
    fixed2 = dict(fixed, consistent=[{"a": "A:a1", "b": "B:b2", "reason": "checked"}])
    check("one 'consistent' entry -> 12 un-assessed", len(cca_coverage(Box(fixed2))[1]), 12)
    fixed3 = dict(fixed2, assessed_blocks=[["C", "A"]])
    check("declaring block A×C assessed -> 9 un-assessed", len(cca_coverage(Box(fixed3))[1]), 9)
    check("A×C block reports 1 excluded + 3 consistent", [(r["excluded"], r["consistent"]) for r in cca_coverage(Box(fixed3))[0]][1], (1, 3))
    fixed4 = dict(fixed3, assessed_blocks=[["A", "B"], ["A", "C"], ["B", "C"]])
    check("all blocks declared -> CCA complete", len(cca_coverage(Box(fixed4))[1]), 0)

    # Invalid input is rejected with a pointed message.
    expect_error("unknown parameter in a reference",
                 dict(fixed, exclusions=[{"a": "Z:a1", "b": "B:b1", "type": "logical", "reason": "x"}]), "unknown parameter 'Z'")
    expect_error("unknown value in a reference",
                 dict(fixed, exclusions=[{"a": "A:zz", "b": "B:b1", "type": "logical", "reason": "x"}]), "unknown value 'zz'")
    expect_error("same-parameter pair rejected",
                 dict(fixed, exclusions=[{"a": "A:a1", "b": "A:a2", "type": "logical", "reason": "x"}]), "mutually exclusive by construction")
    expect_error("unknown exclusion type rejected",
                 dict(fixed, exclusions=[{"a": "A:a1", "b": "B:b1", "type": "vibes", "reason": "x"}]), "'type' must be one of")
    expect_error("exclusion without a reason rejected",
                 dict(fixed, exclusions=[{"a": "A:a1", "b": "B:b1", "type": "logical"}]), "non-empty 'reason'")
    expect_error("duplicate pair rejected",
                 dict(fixed, exclusions=fixed["exclusions"] + [{"a": "B:b1", "b": "A:a1", "type": "logical", "reason": "again"}]), "listed twice")
    expect_error("pair both consistent and excluded rejected",
                 dict(fixed, consistent=[{"a": "B:b1", "b": "A:a1"}]), "also listed under 'exclusions'")
    expect_error("single-valued parameter rejected",
                 {"parameters": [{"name": "A", "values": ["only"]}, {"name": "B", "values": ["b1", "b2"]}]}, "at least 2 values")
    expect_error("fewer than two parameters rejected", {"parameters": [{"name": "A", "values": ["a1", "a2"]}]}, "at least 2 parameters")
    expect_error("colon in parameter name rejected",
                 {"parameters": [{"name": "A:x", "values": ["a1", "a2"]}, {"name": "B", "values": ["b1", "b2"]}]}, "must not contain ':'")
    expect_error("malformed reference rejected",
                 dict(fixed, exclusions=[{"a": "A a1", "b": "B:b1", "type": "logical", "reason": "x"}]), "must be written 'Param:Value'")
    try:
        parse_must(box, ["A:a1", "A:a2"])
        print("FAIL  conflicting --must values accepted", file=sys.stderr)
        sys.exit(1)
    except BoxError:
        results.append(True)
        print("PASS  conflicting --must values rejected")

    # Demo box (SKILL.md worked example): raw = 3*4*3*3*4 = 432. By hand: Storage=None forces
    # Revenue=Self-consumption and Ownership!=Utility -> 4 controls x 4 (Ownership,Pricing) pairs = 16;
    # each battery option: Manual control -> 6, each of 3 automated controls -> 6+9+9 = 24 -> 78;
    # total 16 + 78 + 78 = 172. VPP driver: 2 storages x 3 automated controls x 9 (O,P) pairs = 54.
    demo = Box(DEMO)
    check("demo raw count = 3*4*3*3*4", demo.raw_count(), 432)
    check("demo value pairs to assess (sum over 10 blocks)", sum(r["pairs"] for r in cca_coverage(demo)[0]), 115)
    demo_count, _ = enumerate_solutions(demo, collect=False)
    check("demo consistent count (backtracking = brute force)", demo_count, brute_force_count(demo))
    check("demo consistent count = 172 (by hand)", demo_count, 172)
    check("demo CCA complete", len(cca_coverage(demo)[1]), 0)
    vpp = parse_must(demo, [DEMO_DRIVER])
    check("demo driver VPP -> 54 configurations (by hand)", enumerate_solutions(demo, vpp, collect=False)[0], 54)
    check("demo driver VPP brute force agrees", brute_force_count(demo, vpp), 54)
    lo, hi = bounds(demo)
    check("demo bounds bracket the exact count", lo <= demo_count <= hi, True)

    print(f"ALL {len(results)} CHECKS PASSED")
    print("selftest OK")
    return 0


# --- CLI ---------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(
        description="General Morphological Analysis (Zwicky box + cross-consistency assessment): "
                    "raw and consistent configuration counts, solution listing, CCA coverage.")
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true", help="print the SKILL.md worked example (space + driver solutions)")
    sub = parser.add_subparsers(dest="command")
    specs = [
        ("box", "print the morphological box as a Markdown table with the raw configuration count"),
        ("space", "raw configuration count, exclusion summary, consistent count (or bounds above --max-enumerate)"),
        ("solutions", "list internally consistent configurations, optionally filtered by --must driver values"),
        ("cca", "cross-consistency assessment coverage: which value pairs are still un-assessed (exit 2 if any)"),
    ]
    for name, helptext in specs:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--file", required=True, help="box description JSON ('-' reads stdin)")
        p.add_argument("--json", action="store_true", help="JSON output")
        if name in ("space", "solutions"):
            p.add_argument("--max-enumerate", type=int, default=200000,
                           help="enumerate when the raw count is at most this; otherwise report bounds (default 200000)")
        if name == "solutions":
            p.add_argument("--must", action="append", default=[], metavar="PARAM:VALUE",
                           help="driver value every listed configuration must contain (repeatable)")
            p.add_argument("--limit", type=int, default=50, help="maximum configurations to list (default 50)")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo:
        return cmd_demo()
    if not args.command:
        parser.error("choose a command: box | space | solutions | cca  (or --demo / --selftest)")
    try:
        box = load_box(args.file)
        if args.command == "box":
            return cmd_box(box, args.json)
        if args.command == "space":
            if args.max_enumerate < 1:
                parser.error("--max-enumerate must be >= 1")
            return cmd_space(box, args.max_enumerate, args.json)
        if args.command == "solutions":
            if args.limit < 1:
                parser.error("--limit must be >= 1")
            return cmd_solutions(box, args.must, args.limit, args.max_enumerate, args.json)
        return cmd_cca(box, args.json)
    except BoxError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
