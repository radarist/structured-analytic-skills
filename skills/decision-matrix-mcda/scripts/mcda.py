#!/usr/bin/env python3
"""mcda.py — weighted decision matrix (additive MCDA) with AHP weights and sensitivity.

Implements the definitions in ../SKILL.md:

  * AHP weights (Saaty 1980; Saaty 1990, EJOR 48(1):9-26): the priority vector
    is the principal right eigenvector of the positive reciprocal pairwise
    comparison matrix A (a_ji = 1/a_ij, judgements on the 1-9 fundamental
    scale), computed here by power iteration and normalised to sum 1.
        lambda_max  = principal eigenvalue (= n iff A is consistent)
        CI          = (lambda_max - n) / (n - 1)          consistency index
        RI          = random index for order n (Saaty 1980, n = 1..10):
                      0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49
        CR          = CI / RI                              consistency ratio
        verdict     = consistent if CR <= 0.10 ("about 10% or less", Saaty 1990),
                      otherwise revisit the judgements.  n <= 2 is always
                      consistent (CR reported as 0).
  * Additive value model (Keeney & Raiffa 1976/1993): total score of option j
        S_j = sum_i w_i * v_ij,   sum_i w_i = 1,   v_ij in [0, 1]
    valid only when the criteria are mutually preferentially independent —
    the tool cannot check that; the SKILL.md verification list does.
  * Normalisation to a common 0-1 scale, direction-aware (Belton & Stewart 2002):
        minmax  benefit v = (x - lo) / (hi - lo)     cost v = (hi - x) / (hi - lo)
                lo/hi = the criterion's stated "range" (global scale) if given,
                else the observed min/max over the options (local scale)
        ratio   benefit v = x / max(x)               cost v = min(x) / x   (x > 0)
        none    v = x  (scores already on one "higher is better" scale)
  * Sensitivity (Belton & Stewart 2002, ch. 5-6): for each criterion k the
    break-even weight at which the leader changes when w_k is varied and the
    other weights are rescaled proportionally (S_j is linear in w_k, so the
    break-even is analytic); the one-at-a-time score change per cell that
    flips the leader; and a leave-one-out rank-reversal check (drop each
    non-leading option, re-normalise, compare the order of the survivors).

Input JSON (--file) for score / sensitivity / report:

    {
      "title": "R&D portfolio choice FY27",
      "criteria": [
        {"id": "C1", "name": "Strategic fit", "direction": "max", "weight": 0.30},
        {"id": "C2", "name": "Time to revenue (months)", "direction": "min",
         "weight": 0.10, "range": [6, 36]},          # optional global scale
        ...
      ],
      "pairwise": [[1, 3, ...], ["1/3", 1, ...], ...], # optional: n x n reciprocal
                                                        # matrix -> AHP weights
                                                        # (then omit "weight")
      "options": [
        {"id": "O1", "name": "Status quo", "scores": {"C1": 3, "C2": 6, ...}},
        ...
      ]
    }

Input JSON for weights: the same file, or {"criteria": [...names...],
"pairwise": [[...]]}, or a bare n x n list. Cells may be numbers or "1/3".

Usage:
    python3 mcda.py weights     --file pairwise.json [--json] [--tol 1e-12] [--max-iter 10000]
    python3 mcda.py score       --file matrix.json [--normalise minmax|ratio|none] [--json]
    python3 mcda.py sensitivity --file matrix.json [--normalise ...] [--step 1.0] [--json]
    python3 mcda.py report      --file matrix.json [--normalise ...] [--step 1.0] [--json]
    python3 mcda.py report      --demo              # SKILL.md worked example
    python3 mcda.py --selftest

Exit codes: 0 ok; 1 invalid input/usage; 2 the pairwise judgements are
inconsistent (CR > 0.10) — the weights are printed but must not be used as-is.

Stdlib only. Python 3.9+. Deterministic: no randomness, no clock, sorted keys.
"""

import argparse
import json
import math
import sys

# --- constants (Saaty) ------------------------------------------------------

# Random index by matrix order n (Saaty 1980; reproduced in Saaty 1987/1990).
RANDOM_INDEX = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32,
                8: 1.41, 9: 1.45, 10: 1.49}
CR_THRESHOLD = 0.10          # Saaty 1990: "about 10% or less"
SCALE_MIN, SCALE_MAX = 1.0 / 9.0, 9.0   # the fundamental 1-9 scale and its reciprocals

NORMALISERS = ("minmax", "ratio", "none")

# --- built-in worked example (SKILL.md) -------------------------------------

DEMO = {
    "title": "R&D portfolio choice FY27 — which programme gets the discretionary budget?",
    "criteria": [
        {"id": "C1", "name": "Strategic fit (1-5)", "direction": "max", "range": [1, 5]},
        {"id": "C2", "name": "Expected NPV (EUR m)", "direction": "max"},
        {"id": "C3", "name": "Time to first revenue (months)", "direction": "min"},
        {"id": "C4", "name": "Technical risk (1-5, 5 = riskiest)", "direction": "min", "range": [1, 5]},
        {"id": "C5", "name": "Capability fit (1-5)", "direction": "max", "range": [1, 5]},
    ],
    "pairwise": [
        [1, 1, 3, 3, 3],
        [1, 1, 3, 2, 4],
        ["1/3", "1/3", 1, "1/2", 1],
        ["1/3", "1/2", 2, 1, 2],
        ["1/3", "1/4", 1, "1/2", 1],
    ],
    "options": [
        {"id": "O1", "name": "Status quo (incremental roadmap)",
         "scores": {"C1": 3, "C2": 4, "C3": 6, "C4": 1, "C5": 5}},
        {"id": "O2", "name": "Solid-state cell pilot line",
         "scores": {"C1": 5, "C2": 12, "C3": 30, "C4": 4, "C5": 3}},
        {"id": "O3", "name": "AI materials-discovery platform",
         "scores": {"C1": 4, "C2": 9, "C3": 18, "C4": 3, "C5": 4}},
        {"id": "O4", "name": "Flow-battery demonstrator",
         "scores": {"C1": 3, "C2": 7, "C3": 24, "C4": 3, "C5": 2}},
    ],
}


# --- parsing helpers --------------------------------------------------------

def parse_cell(raw):
    """A pairwise cell: number, numeric string, or fraction string like '1/3'."""
    if isinstance(raw, bool):
        raise ValueError("boolean is not a valid pairwise judgement")
    if isinstance(raw, (int, float)):
        val = float(raw)
    else:
        s = str(raw).strip()
        if "/" in s:
            num, den = s.split("/", 1)
            val = float(num) / float(den)
        else:
            val = float(s)
    if not math.isfinite(val) or val <= 0:
        raise ValueError("pairwise judgement %r must be a positive number" % (raw,))
    return val


def parse_pairwise(payload):
    """Return (names, matrix) from a bare list, {'pairwise': ...} or a full case file."""
    if isinstance(payload, list):
        raw, names = payload, None
    elif isinstance(payload, dict):
        raw = payload.get("pairwise", payload.get("matrix"))
        names = payload.get("criteria")
    else:
        raise ValueError("pairwise input must be a JSON list or object")
    if not isinstance(raw, list) or not raw:
        raise ValueError('need an n x n "pairwise" matrix (list of rows)')
    n = len(raw)
    if n < 2:
        raise ValueError("pairwise matrix needs at least 2 criteria")
    if n > max(RANDOM_INDEX):
        raise ValueError("pairwise matrix of order %d: RI table covers n <= %d; cluster the criteria "
                         "(Saaty recommends at most 7 +/- 2 elements per comparison set)" % (n, max(RANDOM_INDEX)))
    matrix = []
    for i, row in enumerate(raw):
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("pairwise row %d must have %d cells" % (i + 1, n))
        matrix.append([parse_cell(c) for c in row])
    for i in range(n):
        if abs(matrix[i][i] - 1.0) > 1e-9:
            raise ValueError("pairwise diagonal cell (%d,%d) must be 1, got %g" % (i + 1, i + 1, matrix[i][i]))
        for j in range(i + 1, n):
            if abs(matrix[i][j] * matrix[j][i] - 1.0) > 1e-6:
                raise ValueError("pairwise cells (%d,%d)=%g and (%d,%d)=%g are not reciprocal"
                                 % (i + 1, j + 1, matrix[i][j], j + 1, i + 1, matrix[j][i]))
    if names is None:
        names = ["C%d" % (i + 1) for i in range(n)]
    else:
        names = [c["name"] if isinstance(c, dict) else str(c) for c in names]
        if len(names) != n:
            raise ValueError("criteria list has %d entries but the pairwise matrix is %d x %d" % (len(names), n, n))
    return names, matrix


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# --- AHP: principal eigenvector, lambda_max, CI, RI, CR ---------------------

def principal_eigenvector(matrix, tol=1e-12, max_iter=10000):
    """Power iteration on a positive matrix (Perron-Frobenius guarantees the
    dominant eigenvector is positive and unique). Start from the uniform
    vector, renormalise to sum 1 each step, stop when the largest component
    change is below `tol`. Returns (w, lambda_max, iterations, converged)."""
    n = len(matrix)
    w = [1.0 / n] * n
    converged = False
    it = 0
    for it in range(1, max_iter + 1):
        aw = [sum(matrix[i][j] * w[j] for j in range(n)) for i in range(n)]
        s = sum(aw)
        w_new = [x / s for x in aw]
        diff = max(abs(a - b) for a, b in zip(w_new, w))
        w = w_new
        if diff < tol:
            converged = True
            break
    aw = [sum(matrix[i][j] * w[j] for j in range(n)) for i in range(n)]
    lam = sum(aw) / sum(w)   # Rayleigh-type estimate: sum(Aw) = lambda * sum(w)
    return w, lam, it, converged


def consistency(matrix, tol=1e-12, max_iter=10000):
    """Full AHP consistency report for one reciprocal matrix."""
    n = len(matrix)
    w, lam, iters, converged = principal_eigenvector(matrix, tol, max_iter)
    ci = (lam - n) / (n - 1) if n > 1 else 0.0
    ri = RANDOM_INDEX[n]
    cr = ci / ri if ri > 0 else 0.0
    if n <= 2:
        cr = 0.0
    # Most inconsistent judgement: largest |ln a_ij - ln(w_i/w_j)|, upper triangle.
    worst = None
    for i in range(n):
        for j in range(i + 1, n):
            implied = w[i] / w[j]
            dev = abs(math.log(matrix[i][j]) - math.log(implied))
            if worst is None or dev > worst["deviation"]:
                worst = {"i": i, "j": j, "given": matrix[i][j], "implied": implied, "deviation": dev}
    off_scale = [(i, j, matrix[i][j]) for i in range(n) for j in range(n)
                 if i != j and not (SCALE_MIN - 1e-9 <= matrix[i][j] <= SCALE_MAX + 1e-9)]
    return {
        "n": n, "weights": w, "lambda_max": lam, "ci": ci, "ri": ri, "cr": cr,
        "consistent": cr <= CR_THRESHOLD, "iterations": iters, "converged": converged,
        "tolerance": tol, "worst": worst, "off_scale": off_scale,
    }


# --- decision matrix: validation, normalisation, scoring --------------------

def load_case(payload):
    """Validate a case file and return a normalised internal structure
    (criteria with ids/names/directions/weights, options with score vectors)."""
    if not isinstance(payload, dict):
        raise ValueError("case file must be a JSON object")
    crit_raw = payload.get("criteria")
    opt_raw = payload.get("options")
    if not isinstance(crit_raw, list) or len(crit_raw) < 2:
        raise ValueError('"criteria" must be a list of at least 2 criteria')
    if not isinstance(opt_raw, list) or len(opt_raw) < 2:
        raise ValueError('"options" must be a list of at least 2 options')
    notes = []
    if len(opt_raw) < 3:
        notes.append("only %d options: the procedure asks for >= 3 including the status quo" % len(opt_raw))

    criteria = []
    for k, c in enumerate(crit_raw):
        if isinstance(c, str):
            c = {"name": c}
        if not isinstance(c, dict) or not str(c.get("name", "")).strip():
            raise ValueError("criterion %d needs a name" % (k + 1))
        direction = str(c.get("direction", "max")).lower()
        if direction not in ("max", "min"):
            raise ValueError('criterion %r: direction must be "max" or "min"' % c["name"])
        rng = c.get("range")
        if rng is not None:
            if (not isinstance(rng, list) or len(rng) != 2 or
                    not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in rng) or
                    not float(rng[1]) > float(rng[0])):
                raise ValueError('criterion %r: "range" must be [lo, hi] with hi > lo' % c["name"])
            rng = [float(rng[0]), float(rng[1])]
        criteria.append({"id": str(c.get("id", "C%d" % (k + 1))), "name": str(c["name"]),
                         "direction": direction, "weight": c.get("weight"), "range": rng})
    ids = [c["id"] for c in criteria]
    if len(set(ids)) != len(ids):
        raise ValueError("criterion ids must be unique")

    # weights: from the pairwise matrix (AHP) or explicit
    ahp = None
    if payload.get("pairwise") is not None:
        if any(c["weight"] is not None for c in criteria):
            raise ValueError('give either per-criterion "weight" or a "pairwise" matrix, not both')
        _, matrix = parse_pairwise({"pairwise": payload["pairwise"], "criteria": [c["name"] for c in criteria]})
        ahp = consistency(matrix)
        for c, w in zip(criteria, ahp["weights"]):
            c["weight"] = w
        weight_source = "AHP principal eigenvector of the pairwise matrix"
    else:
        for c in criteria:
            if c["weight"] is None:
                raise ValueError('criterion %r has no "weight" (and no "pairwise" matrix was given)' % c["name"])
            try:
                c["weight"] = float(c["weight"])
            except (TypeError, ValueError):
                raise ValueError('criterion %r: weight must be a number' % c["name"])
            if not math.isfinite(c["weight"]) or c["weight"] < 0:
                raise ValueError('criterion %r: weight must be >= 0' % c["name"])
        total = sum(c["weight"] for c in criteria)
        if total <= 0:
            raise ValueError("weights must sum to more than 0")
        if abs(total - 1.0) > 1e-9:
            notes.append("weights summed to %.4f; renormalised to 1" % total)
        for c in criteria:
            c["weight"] /= total
        weight_source = "stated directly"

    options = []
    for j, o in enumerate(opt_raw):
        if not isinstance(o, dict) or not str(o.get("name", "")).strip():
            raise ValueError("option %d needs a name" % (j + 1))
        raw_scores = o.get("scores")
        vec = []
        if isinstance(raw_scores, list):
            if len(raw_scores) != len(criteria):
                raise ValueError("option %r: scores list must have %d values" % (o["name"], len(criteria)))
            vec = list(raw_scores)
        elif isinstance(raw_scores, dict):
            for c in criteria:
                key = c["id"] if c["id"] in raw_scores else c["name"]
                if key not in raw_scores:
                    raise ValueError("option %r: missing score for criterion %r" % (o["name"], c["id"]))
                vec.append(raw_scores[key])
        else:
            raise ValueError('option %r: "scores" must be a list or an object keyed by criterion id/name' % o["name"])
        clean = []
        for c, x in zip(criteria, vec):
            if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(float(x)):
                raise ValueError("option %r: score for %r must be a finite number" % (o["name"], c["id"]))
            x = float(x)
            if c["range"] is not None and not (c["range"][0] - 1e-9 <= x <= c["range"][1] + 1e-9):
                raise ValueError("option %r: score %g for %r lies outside its stated range %s"
                                 % (o["name"], x, c["id"], c["range"]))
            clean.append(x)
        options.append({"id": str(o.get("id", "O%d" % (j + 1))), "name": str(o["name"]), "raw": clean})
    oids = [o["id"] for o in options]
    if len(set(oids)) != len(oids):
        raise ValueError("option ids must be unique")
    return {"title": str(payload.get("title", "")), "criteria": criteria, "options": options,
            "ahp": ahp, "weight_source": weight_source, "notes": notes}


def normalise_column(values, direction, method, rng=None):
    """Map one criterion's raw values to [0, 1], higher = better. Returns (v, note)."""
    if method == "none":
        if direction != "max":
            raise ValueError('--normalise none needs every criterion to be direction "max" '
                             '(scores already point "higher is better")')
        return list(values), None
    if method == "minmax":
        lo, hi = (rng[0], rng[1]) if rng else (min(values), max(values))
        if hi - lo <= 0:
            return [1.0] * len(values), "all options tie on this criterion (it does not discriminate)"
        if direction == "max":
            return [(x - lo) / (hi - lo) for x in values], None
        return [(hi - x) / (hi - lo) for x in values], None
    if method == "ratio":
        if direction == "max":
            top = max(values)
            if top <= 0 or min(values) < 0:
                raise ValueError("ratio normalisation of a benefit criterion needs non-negative values with max > 0")
            return [x / top for x in values], None
        bottom = min(values)
        if bottom <= 0:
            raise ValueError("ratio normalisation of a cost criterion needs strictly positive values")
        return [bottom / x for x in values], None
    raise ValueError("unknown normalisation %r (choose %s)" % (method, "|".join(NORMALISERS)))


def score_case(case, method="minmax", option_mask=None):
    """Normalise, weight and rank. `option_mask` (list of bools) restricts the
    option set — used by the leave-one-out rank-reversal check. Returns dict."""
    criteria = case["criteria"]
    options = [o for o, keep in zip(case["options"], option_mask or [True] * len(case["options"])) if keep]
    cols = []
    col_notes = {}
    for k, c in enumerate(criteria):
        vals = [o["raw"][k] for o in options]
        v, note = normalise_column(vals, c["direction"], method, c["range"])
        cols.append(v)
        if note:
            col_notes[c["id"]] = note
    rows = []
    for j, o in enumerate(options):
        v = [cols[k][j] for k in range(len(criteria))]
        contrib = [criteria[k]["weight"] * v[k] for k in range(len(criteria))]
        rows.append({"id": o["id"], "name": o["name"], "raw": o["raw"], "normalised": v,
                     "contributions": contrib, "total": sum(contrib)})
    ranked = sorted(rows, key=lambda r: (-r["total"], r["id"]))
    for pos, r in enumerate(ranked, start=1):
        r["rank"] = pos
    margin = ranked[0]["total"] - ranked[1]["total"] if len(ranked) > 1 else 0.0
    return {"method": method, "rows": rows, "ranked": ranked, "margin": margin,
            "margin_pct": (100.0 * margin / ranked[0]["total"]) if ranked[0]["total"] > 0 else 0.0,
            "column_notes": col_notes}


# --- sensitivity ------------------------------------------------------------

def weight_breakevens(case, scored):
    """For each criterion k: the nearest weight w_k' (with the other weights
    rescaled proportionally) at which some option overtakes the current
    leader. S_j(t) = t*v_kj + (1-t)*R_j is linear in t = w_k, so the crossing
    with option j is t* = (R_L - R_j) / ((v_kj - v_kL) + (R_L - R_j))."""
    criteria = case["criteria"]
    rows = scored["ranked"]
    leader = rows[0]
    out = []
    for k, c in enumerate(criteria):
        wk = c["weight"]
        rest_w = 1.0 - wk

        def rest(r):
            if rest_w <= 1e-12:
                return 0.0
            return (r["total"] - wk * r["normalised"][k]) / rest_w

        r_l = rest(leader)
        v_l = leader["normalised"][k]
        candidates = []
        for r in rows[1:]:
            r_j = rest(r)
            v_j = r["normalised"][k]
            denom = (v_j - v_l) + (r_l - r_j)
            if abs(denom) < 1e-12:
                continue
            t = (r_l - r_j) / denom
            if -1e-9 <= t <= 1 + 1e-9:
                t = min(1.0, max(0.0, t))
                candidates.append((abs(t - wk), t, r["id"], r["name"]))
        entry = {"id": c["id"], "name": c["name"], "weight": wk, "breakeven": None,
                 "direction": None, "overtaken_by": None, "overtaken_by_name": None, "distance": None}
        if candidates:
            candidates.sort(key=lambda x: (x[0], x[1], x[2]))
            dist, t, oid, oname = candidates[0]
            entry.update({"breakeven": t, "direction": "below" if t < wk else "above",
                          "overtaken_by": oid, "overtaken_by_name": oname, "distance": dist})
        out.append(entry)
    return out


def _domain(case, k, method):
    """Plausible raw-score domain for criterion k when searching for a flip:
    the stated range if given, else the observed [min, max] widened by one
    span on each side (ratio scaling keeps values positive)."""
    c = case["criteria"][k]
    vals = [o["raw"][k] for o in case["options"]]
    if c["range"] is not None:
        lo, hi = c["range"]
    else:
        lo, hi = min(vals), max(vals)
        span = (hi - lo) if hi > lo else (abs(hi) if hi else 1.0)
        lo, hi = lo - span, hi + span
    if method == "ratio":
        lo = max(lo, min(vals) / 100.0 if c["direction"] == "min" else 0.0)
    return lo, hi


def _leader_after(case, method, j, k, x):
    """Leader id after setting option j's raw score on criterion k to x
    (the whole matrix is re-normalised, so moving bounds are handled)."""
    saved = case["options"][j]["raw"][k]
    case["options"][j]["raw"][k] = x
    try:
        return score_case(case, method)["ranked"][0]["id"]
    except ValueError:
        return None
    finally:
        case["options"][j]["raw"][k] = saved


def _flip_point(case, method, j, k, x0, x_end, leader_id, steps=100, refine=50):
    """Scan from x0 towards x_end for the first raw value at which the leader
    changes, then bisect between the last non-flipping and first flipping
    value. Returns (x_flip, new_leader) or None."""
    if x_end == x0:
        return None
    prev = x0
    for s in range(1, steps + 1):
        x = x0 + (x_end - x0) * s / steps
        lid = _leader_after(case, method, j, k, x)
        if lid is not None and lid != leader_id:
            a, b = prev, x
            for _ in range(refine):
                mid = (a + b) / 2.0
                lid_m = _leader_after(case, method, j, k, mid)
                if lid_m is not None and lid_m != leader_id:
                    b = mid
                else:
                    a = mid
            return b, _leader_after(case, method, j, k, b)
        prev = x
    return None


def score_sensitivity(case, scored, step=1.0):
    """One-at-a-time score changes that flip the leader, found by direct
    re-scoring (exact under the tool's own normalisation, including cases
    where the changed cell moves the observed min/max). For the leader each
    criterion is worsened; for every challenger it is improved. Cells are
    ranked by the change as a fraction of the criterion's domain; a cell whose
    raw change is within +/- `step` raw units is flagged fragile."""
    criteria = case["criteria"]
    leader_id = scored["ranked"][0]["id"]
    method = scored["method"]
    cells = []
    for j, o in enumerate(case["options"]):
        for k, c in enumerate(criteria):
            if c["weight"] <= 1e-12:
                continue
            lo, hi = _domain(case, k, method)
            x0 = o["raw"][k]
            is_leader = o["id"] == leader_id
            benefit = c["direction"] == "max" or method == "none"
            # leader: worsen; challenger: improve
            towards = (lo if benefit else hi) if is_leader else (hi if benefit else lo)
            hit = _flip_point(case, method, j, k, x0, towards, leader_id)
            if hit is None:
                continue
            x_flip, new_leader = hit
            span = hi - lo if hi > lo else 1.0
            cells.append({"option": o["id"], "option_name": o["name"], "criterion": c["id"],
                          "criterion_name": c["name"], "raw": x0, "new_raw": x_flip,
                          "d_raw": x_flip - x0, "rel_change": abs(x_flip - x0) / span,
                          "new_leader": new_leader, "within_step": abs(x_flip - x0) <= step + 1e-9})
    cells.sort(key=lambda x: (x["rel_change"], x["criterion"], x["option"]))
    return cells


def rank_reversal(case, scored):
    """Leave-one-out check: drop each non-leading option in turn, re-score the
    survivors, and report any pair whose relative order differs from the full
    ranking. Only local scales (minmax without a stated range, ratio) can
    reverse; stated ranges and --normalise none are set-independent."""
    n = len(case["options"])
    full_order = {r["id"]: r["rank"] for r in scored["ranked"]}
    reversals = []
    for drop in range(n):
        if case["options"][drop]["id"] == scored["ranked"][0]["id"]:
            continue
        mask = [i != drop for i in range(n)]
        sub = score_case(case, scored["method"], mask)
        sub_order = {r["id"]: r["rank"] for r in sub["ranked"]}
        ids = [r["id"] for r in sub["ranked"]]
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                x, y = ids[a], ids[b]
                if (full_order[x] < full_order[y]) != (sub_order[x] < sub_order[y]):
                    reversals.append({"dropped": case["options"][drop]["id"], "pair": [x, y],
                                      "full_order": "%s > %s" % ((x, y) if full_order[x] < full_order[y] else (y, x)),
                                      "reduced_order": "%s > %s" % ((x, y) if sub_order[x] < sub_order[y] else (y, x))})
    set_independent = scored["method"] == "none" or all(c["range"] is not None for c in case["criteria"])
    return {"reversals": reversals, "set_independent": set_independent}


# --- rendering ---------------------------------------------------------------

def _fmt(x, nd=3):
    return ("%%.%df" % nd) % x


def render_weights(names, res):
    n = res["n"]
    lines = ["AHP weights — principal eigenvector (power iteration, tol %g, %d iteration%s%s)"
             % (res["tolerance"], res["iterations"], "" if res["iterations"] == 1 else "s",
                "" if res["converged"] else ", NOT converged")]
    width = max(len(s) for s in names)
    for name, w in zip(names, res["weights"]):
        lines.append("  %-*s  %s" % (width, name, _fmt(w, 4)))
    lines.append("lambda_max = %s   n = %d   CI = (lambda_max - n)/(n - 1) = %s   RI(n=%d) = %.2f   CR = CI/RI = %s"
                 % (_fmt(res["lambda_max"], 4), n, _fmt(res["ci"], 4), n, res["ri"], _fmt(res["cr"], 4)))
    if res["consistent"]:
        lines.append("Verdict: consistent (CR %s <= %.2f) — weights usable." % (_fmt(res["cr"], 3), CR_THRESHOLD))
    else:
        lines.append("Verdict: INCONSISTENT (CR %s > %.2f) — revisit the judgements before using these weights."
                     % (_fmt(res["cr"], 3), CR_THRESHOLD))
    w = res["worst"]
    if w is not None and n > 2:
        lines.append("Most inconsistent judgement: %s vs %s given %s, implied by the weights %s"
                     % (names[w["i"]], names[w["j"]], _fmt(w["given"], 3), _fmt(w["implied"], 3)))
    for i, j, val in res["off_scale"]:
        lines.append("Note: cell (%d,%d) = %g lies outside the 1/9..9 fundamental scale" % (i + 1, j + 1, val))
    return "\n".join(lines)


def render_score(case, scored):
    criteria = case["criteria"]
    lines = []
    if case["title"]:
        lines.append("Decision: %s" % case["title"])
    lines.append("Weights (%s): " % case["weight_source"] +
                 ", ".join("%s %s" % (c["id"], _fmt(c["weight"], 3)) for c in criteria))
    lines.append("Normalisation: %s (direction-aware; cost criteria = %s)"
                 % (scored["method"], ", ".join(c["id"] for c in criteria if c["direction"] == "min") or "none"))
    for note in case["notes"]:
        lines.append("Note: %s" % note)
    for cid, note in sorted(scored["column_notes"].items()):
        lines.append("Note: %s — %s" % (cid, note))
    lines.append("")
    head = "%-4s %-34s" % ("Opt", "Option") + "".join("%9s" % c["id"] for c in criteria) + "%9s %5s" % ("Total", "Rank")
    lines.append(head)
    lines.append("     raw scores")
    for r in scored["rows"]:
        lines.append("%-4s %-34s" % (r["id"], r["name"][:34]) +
                     "".join("%9s" % ("%g" % x) for x in r["raw"]) + "%9s %5s" % ("", ""))
    lines.append("     normalised (0-1, higher = better)")
    for r in scored["rows"]:
        lines.append("%-4s %-34s" % (r["id"], r["name"][:34]) +
                     "".join("%9s" % _fmt(v) for v in r["normalised"]) + "%9s %5d" % (_fmt(r["total"]), r["rank"]))
    lines.append("")
    lines.append("Ranking (weighted total, higher is better):")
    for r in scored["ranked"]:
        lines.append("  %d. %-4s %-34s %s" % (r["rank"], r["id"], r["name"][:34], _fmt(r["total"])))
    top, second = scored["ranked"][0], scored["ranked"][1]
    lines.append("Margin between top two: %s - %s = %s (%.1f%% of the leader's score)"
                 % (top["id"], second["id"], _fmt(scored["margin"]), scored["margin_pct"]))
    return "\n".join(lines)


def render_sensitivity(case, scored, be, cells, rr, step):
    leader = scored["ranked"][0]
    lines = ["Sensitivity — leader %s (%s), margin %s" % (leader["id"], leader["name"], _fmt(scored["margin"]))]
    lines.append("Break-even weights (one criterion varied, the others rescaled proportionally):")
    for e in be:
        if e["breakeven"] is None:
            lines.append("  %-4s w = %s  no break-even in [0, 1] — leader holds for any weight of this criterion"
                         % (e["id"], _fmt(e["weight"])))
        else:
            lines.append("  %-4s w = %s  leader changes to %s if w %s %s (shift of %s)"
                         % (e["id"], _fmt(e["weight"]), e["overtaken_by"],
                            "falls below" if e["direction"] == "below" else "rises above",
                            _fmt(e["breakeven"]), _fmt(e["distance"])))
    lines.append("Most sensitive score cells (smallest one-at-a-time rescoring that flips the leader; "
                 "'!' = within +/- %g raw units):" % step)
    if not cells:
        lines.append("  none — no single-cell change inside the plausible range flips the leader")
    for cell in cells[:6]:
        lines.append("  %s %s x %s: raw %g -> %s (%+.3g, %.0f%% of the criterion's range) -> leader becomes %s"
                     % ("!" if cell["within_step"] else " ", cell["option"], cell["criterion"], cell["raw"],
                        _fmt(cell["new_raw"], 2), cell["d_raw"], 100 * cell["rel_change"], cell["new_leader"]))
    if rr["set_independent"]:
        lines.append("Rank reversal (leave-one-out): not possible — normalisation does not depend on the option set")
    elif not rr["reversals"]:
        lines.append("Rank reversal (leave-one-out): none — dropping any non-leading option keeps the survivors' order")
    else:
        lines.append("Rank reversal (leave-one-out): FOUND — local (observed-range) scaling changes the order:")
        for r in rr["reversals"]:
            lines.append("  drop %s: %s becomes %s" % (r["dropped"], r["full_order"], r["reduced_order"]))
        lines.append("  Fix: state a global \"range\" per criterion, or use --normalise none with a stated scale.")
    return "\n".join(lines)


def analyse(case, method, step):
    scored = score_case(case, method)
    be = weight_breakevens(case, scored)
    cells = score_sensitivity(case, scored, step)
    rr = rank_reversal(case, scored)
    return scored, be, cells, rr


def to_json(case, scored=None, be=None, cells=None, rr=None, step=None):
    out = {"title": case["title"], "weight_source": case["weight_source"], "notes": case["notes"],
           "criteria": [{"id": c["id"], "name": c["name"], "direction": c["direction"], "weight": c["weight"],
                         "range": c["range"]} for c in case["criteria"]]}
    if case["ahp"] is not None:
        a = case["ahp"]
        out["ahp"] = {"lambda_max": a["lambda_max"], "ci": a["ci"], "ri": a["ri"], "cr": a["cr"],
                      "consistent": a["consistent"], "iterations": a["iterations"], "tolerance": a["tolerance"]}
    if scored is not None:
        out["normalisation"] = scored["method"]
        out["options"] = [{"id": r["id"], "name": r["name"], "raw": r["raw"], "normalised": r["normalised"],
                           "total": r["total"], "rank": r["rank"]} for r in scored["ranked"]]
        out["margin"] = scored["margin"]
        out["margin_pct"] = scored["margin_pct"]
        out["column_notes"] = scored["column_notes"]
    if be is not None:
        out["weight_breakevens"] = be
    if cells is not None:
        out["score_cells"] = cells[:10]
        out["step"] = step
    if rr is not None:
        out["rank_reversal"] = rr
    return out


# --- CLI commands -------------------------------------------------------------

def get_case(args, parser):
    if getattr(args, "demo", False):
        payload = DEMO
    elif args.file:
        try:
            payload = load_json(args.file)
        except (OSError, ValueError) as exc:
            parser.error("could not load %s: %s" % (args.file, exc))
    else:
        parser.error("pass --file case.json or --demo")
    try:
        return load_case(payload)
    except ValueError as exc:
        parser.error(str(exc))


def cmd_weights(args, parser):
    if args.demo:
        payload = DEMO
    elif args.file:
        try:
            payload = load_json(args.file)
        except (OSError, ValueError) as exc:
            parser.error("could not load %s: %s" % (args.file, exc))
    else:
        parser.error("pass --file pairwise.json or --demo")
    try:
        names, matrix = parse_pairwise(payload)
    except ValueError as exc:
        parser.error(str(exc))
    if args.tol <= 0 or args.max_iter < 1:
        parser.error("--tol must be > 0 and --max-iter >= 1")
    res = consistency(matrix, args.tol, args.max_iter)
    if args.json:
        out = {"criteria": names, "weights": res["weights"], "lambda_max": res["lambda_max"], "n": res["n"],
               "ci": res["ci"], "ri": res["ri"], "cr": res["cr"], "consistent": res["consistent"],
               "iterations": res["iterations"], "tolerance": res["tolerance"], "converged": res["converged"],
               "most_inconsistent": None if res["worst"] is None else {
                   "pair": [names[res["worst"]["i"]], names[res["worst"]["j"]]],
                   "given": res["worst"]["given"], "implied": res["worst"]["implied"]}}
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(render_weights(names, res))
    return 0 if res["consistent"] else 2


def cmd_score(args, parser):
    case = get_case(args, parser)
    try:
        scored = score_case(case, args.normalise)
    except ValueError as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(to_json(case, scored), indent=2, sort_keys=True))
    else:
        if case["ahp"] is not None:
            print(render_weights([c["name"] for c in case["criteria"]], case["ahp"]))
            print()
        print(render_score(case, scored))
    return 0


def cmd_sensitivity(args, parser):
    case = get_case(args, parser)
    if args.step <= 0:
        parser.error("--step must be > 0")
    try:
        scored, be, cells, rr = analyse(case, args.normalise, args.step)
    except ValueError as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(to_json(case, scored, be, cells, rr, args.step), indent=2, sort_keys=True))
    else:
        print(render_sensitivity(case, scored, be, cells, rr, args.step))
    return 0


def cmd_report(args, parser):
    """Everything, in the SKILL.md output-template order: decision & weights
    (with CR), score table & ranking & margin, sensitivity, rank reversal."""
    case = get_case(args, parser)
    if args.step <= 0:
        parser.error("--step must be > 0")
    try:
        scored, be, cells, rr = analyse(case, args.normalise, args.step)
    except ValueError as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(to_json(case, scored, be, cells, rr, args.step), indent=2, sort_keys=True))
    else:
        parts = []
        if case["ahp"] is not None:
            parts.append(render_weights([c["name"] for c in case["criteria"]], case["ahp"]))
        parts.append(render_score(case, scored))
        parts.append(render_sensitivity(case, scored, be, cells, rr, args.step))
        print("\n\n".join(parts))
    if case["ahp"] is not None and not case["ahp"]["consistent"]:
        return 1
    return 0


# --- selftest -----------------------------------------------------------------

def run_selftest():
    """Hand-verified checks. Expected values come from Saaty (1990, EJOR 48:9-26,
    Tables 2-4) and from closed-form hand computation (for a 3x3 reciprocal
    matrix with a12 = a, a13 = b, a23 = c: lambda_max = 1 + k^(1/3) + k^(-1/3),
    k = a*c/b — so the eigenvalue can be checked without any linear algebra)."""
    checks = []

    def check(name, got, want, tol=1e-9):
        ok = abs(got - want) <= tol
        checks.append(ok)
        print("%s  %s: got %.6f, expected %.6f" % ("PASS" if ok else "FAIL", name, got, want))
        if not ok:
            print("SELFTEST FAILED at: %s" % name, file=sys.stderr)
            sys.exit(1)

    def check_true(name, cond):
        checks.append(bool(cond))
        print("%s  %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            print("SELFTEST FAILED at: %s" % name, file=sys.stderr)
            sys.exit(1)

    # 1. Random index table (Saaty 1980), n = 1..10.
    for n, ri in ((1, 0.0), (2, 0.0), (3, 0.58), (4, 0.90), (5, 1.12), (6, 1.24), (7, 1.32),
                  (8, 1.41), (9, 1.45), (10, 1.49)):
        check("RI(n=%d)" % n, RANDOM_INDEX[n], ri)

    # 2. Saaty 1990 Table 3, "General condition": consistent 3x3
    #    [[1,1/2,1/2],[2,1,1],[2,1,1]] -> priorities 0.200/0.400/0.400 (ratio 1:2:2),
    #    lambda_max = 3.000, CI = 0, CR = 0.
    _, m = parse_pairwise([[1, "1/2", "1/2"], [2, 1, 1], [2, 1, 1]])
    res = consistency(m)
    check("consistent 3x3: lambda_max = 3", res["lambda_max"], 3.0, 1e-9)
    check("consistent 3x3: CI = 0", res["ci"], 0.0, 1e-9)
    check("consistent 3x3: CR = 0", res["cr"], 0.0, 1e-9)
    check("consistent 3x3: w1 = 0.2", res["weights"][0], 0.2, 1e-9)
    check("consistent 3x3: w2 = 0.4", res["weights"][1], 0.4, 1e-9)
    check("consistent 3x3: w2/w1 = 2 (weights proportional to the judgements)",
          res["weights"][1] / res["weights"][0], 2.0, 1e-9)
    check_true("consistent 3x3: verdict consistent", res["consistent"])

    # 3. Saaty 1990 Table 3, "Transportation": inconsistent 3x3
    #    [[1,7,1/5],[1/7,1,1/8],[5,8,1]]; k = 7*(1/8)/(1/5) = 4.375,
    #    lambda_max = 1 + 4.375^(1/3) + 4.375^(-1/3) = 3.2469 (paper: 3.247),
    #    CI = 0.1235 (paper 0.124), CR = 0.2128 (paper 0.213) -> inconsistent.
    _, m = parse_pairwise([[1, 7, "1/5"], ["1/7", 1, "1/8"], [5, 8, 1]])
    res = consistency(m)
    k = 4.375
    lam_hand = 1 + k ** (1.0 / 3) + k ** (-1.0 / 3)
    check("inconsistent 3x3: lambda_max (closed form)", res["lambda_max"], lam_hand, 1e-9)
    check("inconsistent 3x3: lambda_max = 3.247 (Saaty 1990)", res["lambda_max"], 3.247, 5e-4)
    check("inconsistent 3x3: CR = 0.213 (Saaty 1990)", res["cr"], 0.213, 5e-4)
    check_true("inconsistent 3x3: CR > 0.10 -> verdict inconsistent", not res["consistent"])
    check("inconsistent 3x3: w3 = 0.713 (Saaty 1990)", res["weights"][2], 0.713, 1e-3)

    # 4. Saaty 1990 Table 3, "Financing": [[1,1/7,1/5],[7,1,3],[5,1/3,1]] ->
    #    0.072/0.650/0.278, lambda_max 3.065, CI 0.032, CR 0.056 (consistent).
    _, m = parse_pairwise([[1, "1/7", "1/5"], [7, 1, 3], [5, "1/3", 1]])
    res = consistency(m)
    check("Financing 3x3: lambda_max = 3.065", res["lambda_max"], 3.065, 5e-4)
    check("Financing 3x3: CR = 0.056", res["cr"], 0.056, 5e-4)
    check("Financing 3x3: w2 = 0.650", res["weights"][1], 0.650, 1e-3)
    check_true("Financing 3x3: verdict consistent", res["consistent"])

    # 5. Saaty 1990 Table 2: the 8x8 house-buying criteria matrix ->
    #    lambda_max = 9.669, CI = 0.238, CR = 0.169; priority vector
    #    0.173, 0.054, 0.188, 0.018, 0.031, 0.036, 0.167, 0.333.
    house = [
        [1, 5, 3, 7, 6, 6, "1/3", "1/4"],
        ["1/5", 1, "1/3", 5, 3, 3, "1/5", "1/7"],
        ["1/3", 3, 1, 6, 3, 4, 6, "1/5"],
        ["1/7", "1/5", "1/6", 1, "1/3", "1/4", "1/7", "1/8"],
        ["1/6", "1/3", "1/3", 3, 1, "1/2", "1/5", "1/6"],
        ["1/6", "1/3", "1/4", 4, 2, 1, "1/5", "1/6"],
        [3, 5, "1/6", 7, 5, 5, 1, "1/2"],
        [4, 7, 5, 8, 6, 6, 2, 1],
    ]
    _, m = parse_pairwise(house)
    res = consistency(m)
    check("house 8x8: lambda_max = 9.669", res["lambda_max"], 9.669, 2e-3)
    check("house 8x8: CI = 0.238", res["ci"], 0.238, 5e-4)
    check("house 8x8: CR = 0.169", res["cr"], 0.169, 5e-4)
    for i, want in enumerate((0.173, 0.054, 0.188, 0.018, 0.031, 0.036, 0.167, 0.333)):
        check("house 8x8: priority %d = %.3f" % (i + 1, want), res["weights"][i], want, 1.5e-3)
    check_true("house 8x8: power iteration converged", res["converged"])

    # 6. Weighted-sum ranking on a fixed matrix: Saaty 1990 Table 4 composes the
    #    criteria weights above with the houses' local priorities (already 0-1,
    #    so --normalise none) -> A 0.396, B 0.341, C 0.263.
    case = load_case({
        "criteria": [{"id": "K%d" % (i + 1), "name": "K%d" % (i + 1), "weight": w}
                     for i, w in enumerate((0.173, 0.054, 0.188, 0.018, 0.031, 0.036, 0.167, 0.333))],
        "options": [
            {"id": "A", "name": "House A", "scores": [0.754, 0.233, 0.754, 0.333, 0.674, 0.747, 0.200, 0.072]},
            {"id": "B", "name": "House B", "scores": [0.181, 0.055, 0.065, 0.333, 0.101, 0.060, 0.400, 0.650]},
            {"id": "C", "name": "House C", "scores": [0.065, 0.713, 0.181, 0.333, 0.226, 0.193, 0.400, 0.278]},
        ]})
    sc = score_case(case, "none")
    by_id = {r["id"]: r for r in sc["rows"]}
    check("Table 4: House A = 0.396", by_id["A"]["total"], 0.396, 1e-3)
    check("Table 4: House B = 0.341", by_id["B"]["total"], 0.341, 1e-3)
    check("Table 4: House C = 0.263", by_id["C"]["total"], 0.263, 1e-3)
    check_true("Table 4: ranking A > B > C", [r["id"] for r in sc["ranked"]] == ["A", "B", "C"])
    check("Table 4: margin A - B = 0.055", sc["margin"], 0.055, 1e-3)

    # 7. Break-even weight, two options / two criteria (hand): w = (0.7, 0.3),
    #    A = (0.9, 0.2), B = (0.5, 0.8) -> S_A 0.69, S_B 0.59; vary w1 = t:
    #    0.2 + 0.7t = 0.8 - 0.3t -> t* = 0.6 (B leads if w1 falls below 0.6);
    #    on criterion 2 the same crossing sits at w2 = 0.4 (rises above).
    case = load_case({
        "criteria": [{"id": "C1", "name": "C1", "weight": 0.7}, {"id": "C2", "name": "C2", "weight": 0.3}],
        "options": [{"id": "A", "name": "A", "scores": [0.9, 0.2]}, {"id": "B", "name": "B", "scores": [0.5, 0.8]}]})
    sc = score_case(case, "none")
    check("two-option: S_A = 0.69", sc["ranked"][0]["total"], 0.69)
    check("two-option: margin = 0.10", sc["margin"], 0.10)
    be = weight_breakevens(case, sc)
    check("two-option: break-even w1 = 0.6", be[0]["breakeven"], 0.6)
    check_true("two-option: leader changes if w1 falls below 0.6", be[0]["direction"] == "below" and be[0]["overtaken_by"] == "B")
    check("two-option: break-even w2 = 0.4", be[1]["breakeven"], 0.4)
    check_true("two-option: leader changes if w2 rises above 0.4", be[1]["direction"] == "above")
    # score-cell sensitivity: A loses on C1 when its score drops by (0.69-0.59)/0.7
    # = 0.142857 -> flip at 0.9 - 0.142857 = 0.757143 (found by direct re-scoring).
    cells = score_sensitivity(case, sc, step=1.0)
    first = cells[0]
    check_true("two-option: smallest flipping cell is A x C1", first["option"] == "A" and first["criterion"] == "C1")
    check("two-option: A x C1 flips at 0.757143", first["new_raw"], 0.9 - 0.1 / 0.7, 1e-6)
    check_true("two-option: new leader is B", first["new_leader"] == "B")

    # 8. Direction-aware normalisation of a cost criterion (hand):
    #    costs [2, 4, 8] (min): minmax -> 1, 2/3, 0 ; ratio -> 1, 0.5, 0.25.
    #    benefit [2, 4, 8] (max): minmax -> 0, 1/3, 1 ; ratio -> 0.25, 0.5, 1.
    v, _ = normalise_column([2, 4, 8], "min", "minmax")
    check("cost minmax [2,4,8][1] = 2/3", v[1], 2.0 / 3)
    check("cost minmax [2,4,8][2] = 0", v[2], 0.0)
    v, _ = normalise_column([2, 4, 8], "min", "ratio")
    check("cost ratio [2,4,8][1] = 0.5", v[1], 0.5)
    check("cost ratio [2,4,8][2] = 0.25", v[2], 0.25)
    v, _ = normalise_column([2, 4, 8], "max", "minmax")
    check("benefit minmax [2,4,8][1] = 1/3", v[1], 1.0 / 3)
    v, _ = normalise_column([2, 4, 8], "max", "ratio")
    check("benefit ratio [2,4,8][0] = 0.25", v[0], 0.25)
    # stated global range: cost 4 on range [0, 10] -> (10 - 4)/10 = 0.6
    v, _ = normalise_column([4, 8], "min", "minmax", [0, 10])
    check("cost minmax with stated range [0,10]: 4 -> 0.6", v[0], 0.6)

    # 9. Rank reversal under local (observed-range) min-max scaling (hand):
    #    w = (0.6, 0.4); A = (10, 0), B = (9, 1), C = (0, 0.5)
    #    full: A 0.60, B 0.94, C 0.20 -> B > A > C ; drop C: A 0.60, B 0.40 -> A > B.
    case = load_case({
        "criteria": [{"id": "X", "name": "X", "weight": 0.6}, {"id": "Y", "name": "Y", "weight": 0.4}],
        "options": [{"id": "A", "name": "A", "scores": [10, 0]}, {"id": "B", "name": "B", "scores": [9, 1]},
                    {"id": "C", "name": "C", "scores": [0, 0.5]}]})
    sc = score_case(case, "minmax")
    check("rank reversal case: B = 0.94", [r for r in sc["rows"] if r["id"] == "B"][0]["total"], 0.94)
    rr = rank_reversal(case, sc)
    check_true("rank reversal detected when C is dropped (B > A becomes A > B)",
               len(rr["reversals"]) == 1 and rr["reversals"][0]["dropped"] == "C" and
               rr["reversals"][0]["reduced_order"] == "A > B")
    # with stated global ranges the scaling is set-independent: no reversal possible
    case_g = load_case({
        "criteria": [{"id": "X", "name": "X", "weight": 0.6, "range": [0, 10]},
                     {"id": "Y", "name": "Y", "weight": 0.4, "range": [0, 1]}],
        "options": [{"id": "A", "name": "A", "scores": [10, 0]}, {"id": "B", "name": "B", "scores": [9, 1]},
                    {"id": "C", "name": "C", "scores": [0, 0.5]}]})
    rr_g = rank_reversal(case_g, score_case(case_g, "minmax"))
    check_true("stated ranges: rank reversal impossible and none found", rr_g["set_independent"] and not rr_g["reversals"])

    # 10. Input validation: non-reciprocal matrix, bad direction, mixed weight sources.
    for bad, why in (
        ([[1, 3], [2, 1]], "non-reciprocal"),
        ([[2, 3], ["1/3", 1]], "diagonal != 1"),
        ([[1, 0], [0, 1]], "non-positive cell"),
    ):
        try:
            parse_pairwise(bad)
            check_true("rejects %s pairwise matrix" % why, False)
        except ValueError:
            check_true("rejects %s pairwise matrix" % why, True)
    try:
        load_case({"criteria": [{"name": "a", "weight": 1, "direction": "up"}, {"name": "b", "weight": 1}],
                   "options": [{"name": "o1", "scores": [1, 1]}, {"name": "o2", "scores": [1, 2]}]})
        check_true("rejects unknown direction", False)
    except ValueError:
        check_true("rejects unknown direction", True)
    try:
        normalise_column([1, 2], "min", "none")
        check_true("--normalise none rejects a min-direction criterion", False)
    except ValueError:
        check_true("--normalise none rejects a min-direction criterion", True)

    # 11. The built-in worked example is internally consistent (CR <= 0.10) and
    #     the leave-one-out check runs on it.
    demo = load_case(DEMO)
    check_true("demo: AHP weights consistent (CR <= 0.10)", demo["ahp"]["consistent"])
    check("demo: weights sum to 1", sum(c["weight"] for c in demo["criteria"]), 1.0)
    sc = score_case(demo, "minmax")
    check_true("demo: a unique leader exists", sc["margin"] > 0)

    print("selftest OK (%d checks passed)" % len(checks))
    return 0


# --- argparse -------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(
        description="Weighted decision matrix / MCDA: AHP weights with consistency ratio, "
        "direction-aware normalisation, weighted totals, ranking, margin and sensitivity."
    )
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("weights", help="AHP: principal eigenvector, lambda_max, CI, RI, CR and verdict")
    p.add_argument("--file", help="JSON: bare n x n list, {\"criteria\", \"pairwise\"} or a full case file")
    p.add_argument("--demo", action="store_true", help="use the SKILL.md worked example's pairwise matrix")
    p.add_argument("--tol", type=float, default=1e-12, help="power-iteration stop tolerance (default 1e-12)")
    p.add_argument("--max-iter", type=int, default=10000, help="power-iteration cap (default 10000)")
    p.add_argument("--json", action="store_true", help="emit the result as JSON")

    for name, helptext in (("score", "normalised table, weighted totals, ranking, margin"),
                           ("sensitivity", "break-even weights, fragile score cells, rank-reversal check"),
                           ("report", "weights + scores + sensitivity in the SKILL.md output order")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--file", help="JSON case file (see module docstring)")
        p.add_argument("--demo", action="store_true", help="use the SKILL.md worked example (R&D portfolio)")
        p.add_argument("--normalise", choices=NORMALISERS, default="minmax",
                       help="minmax (default), ratio, or none (scores already on one higher-is-better scale)")
        if name != "score":
            p.add_argument("--step", type=float, default=1.0,
                           help="one-at-a-time perturbation in raw score units; cells that flip the leader "
                                "within +/- step are flagged (default 1.0)")
        p.add_argument("--json", action="store_true", help="emit the result as JSON")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.command:
        parser.error("choose a command: weights | score | sensitivity | report  (or --selftest)")
    if args.command == "weights":
        return cmd_weights(args, parser)
    if args.command == "score":
        return cmd_score(args, parser)
    if args.command == "sensitivity":
        return cmd_sensitivity(args, parser)
    return cmd_report(args, parser)


if __name__ == "__main__":
    sys.exit(main())
