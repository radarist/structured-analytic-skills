#!/usr/bin/env python3
"""positioning.py — axis orthogonality, 2x2 map, crowding and whitespace for a
competitive landscape.

Implements the arithmetic behind ../SKILL.md (Position Competitor):

  * Step 1, axis choice — ORTHOGONALITY: Pearson r (and Spearman rank rho)
    between the two axis scores across the competitors. SKILL.md states the
    rule qualitatively ("if the axis pair is correlated ... pick a different
    pair"); this tool operationalises it as
        |r| >= 0.7        -> axes are not independent - choose another axis  (exit 2)
        0.4 <= |r| < 0.7  -> caution: document why they still capture different variance
        |r| <  0.4        -> OK
    With extra numeric columns it prints the full correlation matrix and names
    the least-correlated pair - a suggestion, not a decision (SKILL.md also
    demands that axes be material to the buyer and measurable from evidence).
  * Step 2, placement — MAP: min-max normalisation of each axis to 0-10 (the
    competitor at the axis minimum -> 0, at the maximum -> 10; the map is
    directional, not quantitative), quadrant assignment at the axis midpoint
    (low < 5 <= high), a 21x11 ASCII scatter, the crowding index (mean
    nearest-neighbour Euclidean distance; pairs closer than --crowd) and the
    centroid (plus the weighted centre of mass when a `weight` column exists).
  * Step 3, whitespace — WHITESPACE: a k x k grid over the map; empty cells
    ranked by the distance from the cell centre to the nearest competitor
    (largest empty region first), with the SKILL.md caveat that empty space is
    only opportunity if customers value that combination.
  * REPORT: all of the above in the SKILL.md "Output shape" order.

Definitions: Pearson product-moment correlation (K. Pearson, 1895, Proc. R.
Soc. London 58); Spearman rank correlation with mid-ranks for ties (C.
Spearman, 1904, Am. J. Psychol. 15); positioning maps after M. E. Porter,
Competitive Strategy (Free Press, 1980); whitespace after W. C. Kim and R.
Mauborgne, Blue Ocean Strategy (HBS Press, 2005).

Stdlib only. Python 3.9+. Deterministic (ties broken by name, ascending).

Usage:
    python3 positioning.py orthogonality --file competitors.csv
    python3 positioning.py map           --file competitors.json --crowd 1.0
    python3 positioning.py whitespace    --file competitors.csv --grid 4
    python3 positioning.py report        --demo [--json]
    python3 positioning.py --selftest

Input rows: name, x, y (raw scores on the two chosen axes, any scale), optional
weight (e.g. revenue or share), optional evidence (text), and any further
numeric columns (alternative axes for the correlation matrix). Axis names come
from --x-label/--y-label or the "x_label"/"y_label" keys of a JSON file;
--x-col/--y-col pick other columns as the axes. JSON may be a list of rows or
{"category": ..., "x_label": ..., "y_label": ..., "competitors": [...]}.

Exit codes: 0 success; 1 invalid input or usage; 2 the orthogonality verdict is
"axes are not independent" (orthogonality and report commands).
"""

import argparse
import csv
import json
import math
import sys

# --- constants ---------------------------------------------------------------

SCALE = 10.0               # normalised axis range 0..SCALE
R_NOT_INDEPENDENT = 0.7    # |r| at or above -> "axes are not independent"
R_CAUTION = 0.4            # |r| at or above -> "caution"
MAP_W, MAP_H = 21, 11      # ASCII scatter: columns x rows
DEFAULT_GRID = 4
DEFAULT_CROWD = 1.0
MARKER_POOL = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

NAME_KEYS = ("name", "entity", "competitor", "company", "vendor")
WEIGHT_KEYS = ("weight",)
EVIDENCE_KEYS = ("evidence", "justification", "source")

RULE_TEXT = (
    "|r| >= 0.7 -> axes are not independent - choose another axis; "
    "0.4 <= |r| < 0.7 -> caution (document why they still capture different variance); "
    "|r| < 0.4 -> OK"
)
RULE_NOTE = (
    "SKILL.md step 1 states the rule qualitatively ('if the axis pair is correlated ... "
    "pick a different pair'); the numeric cut-offs are this tool's operationalisation."
)
SUGGESTION_NOTE = (
    "a suggestion, not a decision: an axis must also be material to the buyer and "
    "measurable from evidence (SKILL.md step 1)."
)
CAVEAT = (
    "Caveat: empty space is only opportunity if customers value that combination - ask "
    "whether the region is empty because no one has tried or because it is unviable "
    "(SKILL.md step 3), and say which rather than calling it opportunity."
)

# Quadrants in SKILL.md output order, with the tags SKILL.md attaches to them.
QUADRANT_ORDER = ("upper-right", "upper-left", "lower-right", "lower-left")
QUADRANT_TAGS = {"upper-right": "leaders", "lower-left": "laggards / entrants"}

# Built-in synthetic landscape for --demo (fictional vendors). Same axes as the
# SKILL.md worked example. x = platform surface score 0-100 (integration
# depth), y = benchmark composite 0-100 (frontier quality); extra columns:
# size = headcount (correlated with x on purpose), price = $ per 1M tokens
# (correlated with neither); weight = share of category spend (%).
DEMO = {
    "category": "foundation-model API providers (synthetic demo)",
    "x_label": "integration depth",
    "y_label": "frontier quality",
    "competitors": [
        {"name": "Ardent", "x": 92, "y": 88, "size": 3000, "price": 8, "weight": 30,
         "evidence": "SDK + batch + files + agent tooling; leads the composite eval"},
        {"name": "Bramble", "x": 25, "y": 86, "size": 400, "price": 3, "weight": 12,
         "evidence": "second on the composite eval; chat + bare API only"},
        {"name": "Cobalt", "x": 50, "y": 62, "size": 900, "price": 12, "weight": 8,
         "evidence": "open weights, self-hostable; evals a generation behind"},
        {"name": "Dune", "x": 90, "y": 48, "size": 5000, "price": 6, "weight": 22,
         "evidence": "models embedded across an office suite; evals trail the frontier"},
        {"name": "Ember", "x": 12, "y": 45, "size": 60, "price": 9, "weight": 4,
         "evidence": "resells others' models; no own frontier work"},
        {"name": "Fjord", "x": 70, "y": 64, "size": 700, "price": 4, "weight": 6,
         "evidence": "orchestration tooling wrapped around licensed mid-tier models"},
        {"name": "Granite", "x": 35, "y": 70, "size": 300, "price": 11, "weight": 5,
         "evidence": "domain-tuned models with solid evals; thin platform"},
        {"name": "Halcyon", "x": 88, "y": 86, "size": 2500, "price": 5, "weight": 13,
         "evidence": "near-frontier evals; full platform surface via a cloud marketplace"},
    ],
}


# --- input parsing -----------------------------------------------------------


def _find_key(mapping, candidates):
    """Return the actual key in `mapping` matching one of `candidates` (case-insensitive)."""
    lowered = {str(k).strip().lower(): k for k in mapping}
    for cand in candidates:
        if cand.lower() in lowered:
            return lowered[cand.lower()]
    return None


def _to_float(value):
    """float(value) or None when the value is empty / not numeric / not finite."""
    if value is None or isinstance(value, bool):
        return None
    try:
        f = float(str(value).strip())
    except ValueError:
        return None
    return f if math.isfinite(f) else None


def parse_rows(dicts, x_col="x", y_col="y"):
    """Split raw row-dicts into (competitors, extras, ignored).

    competitors: list of {name, x, y, weight, evidence} sorted by name (asc);
                 x/y are the raw axis scores, weight is None when absent.
    extras:      {column: [float per competitor, same order]} — every other
                 column that is numeric for all rows (alternative axes).
    ignored:     sorted list of columns dropped (non-numeric or missing values).
    """
    if not dicts:
        raise ValueError("no rows")
    rows = []
    for i, row in enumerate(dicts, start=1):
        nkey = _find_key(row, NAME_KEYS)
        xkey = _find_key(row, (x_col,))
        ykey = _find_key(row, (y_col,))
        if nkey is None or xkey is None or ykey is None:
            raise ValueError(
                f"row {i}: need name {NAME_KEYS} and axis columns {x_col!r}, {y_col!r}; "
                f"got keys {list(row)}"
            )
        name = str(row[nkey]).strip()
        if not name:
            raise ValueError(f"row {i}: empty name")
        x, y = _to_float(row[xkey]), _to_float(row[ykey])
        if x is None or y is None:
            raise ValueError(f"row {i} ({name}): axis values must be finite numbers, got {row[xkey]!r}, {row[ykey]!r}")
        wkey = _find_key(row, WEIGHT_KEYS)
        weight = None
        if wkey is not None and str(row[wkey]).strip() != "":
            weight = _to_float(row[wkey])
            if weight is None or weight < 0:
                raise ValueError(f"row {i} ({name}): weight must be a number >= 0, got {row[wkey]!r}")
        ekey = _find_key(row, EVIDENCE_KEYS)
        evidence = str(row[ekey]).strip() if ekey is not None and row[ekey] is not None else ""
        reserved = {nkey, xkey, ykey}
        if wkey is not None:
            reserved.add(wkey)
        if ekey is not None:
            reserved.add(ekey)
        others = {str(k).strip(): row[k] for k in row if k not in reserved and str(k).strip()}
        rows.append({"name": name, "x": x, "y": y, "weight": weight, "evidence": evidence,
                     "_others": others})

    names = [r["name"] for r in rows]
    if len(set(names)) != len(names):
        dup = sorted(n for n in set(names) if names.count(n) > 1)
        raise ValueError(f"duplicate competitor name(s): {', '.join(dup)}")
    rows.sort(key=lambda r: r["name"])

    weights = [r["weight"] for r in rows]
    if any(w is not None for w in weights):
        if any(w is None for w in weights):
            raise ValueError("weight given for some rows but not all")
        if sum(weights) <= 0:
            raise ValueError("weights must sum to more than 0")

    columns = sorted({c for r in rows for c in r["_others"]})
    extras, ignored = {}, []
    for col in columns:
        vals = [_to_float(r["_others"].get(col)) for r in rows]
        if any(v is None for v in vals):
            ignored.append(col)
        else:
            extras[col] = vals
    competitors = [{k: v for k, v in r.items() if k != "_others"} for r in rows]
    return competitors, extras, ignored


def load_file(path, x_col="x", y_col="y"):
    """Load competitors from CSV or JSON (chosen by extension).

    CSV:  header row with name, x, y [, weight, evidence, <extra numeric columns>].
    JSON: a list of row objects, or an object with "competitors" (or "rows" /
          "entities") plus optional "category", "x_label", "y_label".
    Returns (competitors, extras, ignored, meta).
    """
    meta = {}
    with open(path, newline="", encoding="utf-8") as fh:
        if path.lower().endswith(".json"):
            data = json.load(fh)
            if isinstance(data, dict):
                for key in ("category", "x_label", "y_label"):
                    if data.get(key):
                        meta[key] = str(data[key])
                data = data.get("competitors", data.get("rows", data.get("entities", [])))
            if not isinstance(data, list):
                raise ValueError("JSON must be a list of rows or an object with a 'competitors' list")
            competitors, extras, ignored = parse_rows(data, x_col, y_col)
        else:
            competitors, extras, ignored = parse_rows(list(csv.DictReader(fh)), x_col, y_col)
    return competitors, extras, ignored, meta


# --- correlation (SKILL.md step 1) -------------------------------------------


def mean(values):
    return sum(values) / len(values)


def pearson(xs, ys):
    """Pearson product-moment r; None when either series has zero variance."""
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("pearson needs two equal-length series with n >= 2")
    mx, my = mean(xs), mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0.0 or syy == 0.0:
        return None
    return sxy / math.sqrt(sxx * syy)


def ranks(values):
    """Mid-ranks (1-based); tied values share the average of their positions."""
    order = sorted(range(len(values)), key=lambda i: (values[i], i))
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def spearman(xs, ys):
    """Spearman rank correlation = Pearson r of the mid-ranks; None if undefined."""
    return pearson(ranks(xs), ranks(ys))


def verdict(r):
    """Map |r| to the SKILL.md-derived verdict. Returns (label, explanation)."""
    if r is None:
        return "undefined", "an axis has zero variance - it does not discriminate; choose another axis"
    a = abs(r)
    if a >= R_NOT_INDEPENDENT:
        return "not independent", f"|r| >= {R_NOT_INDEPENDENT}: the axes measure the same thing - choose another axis"
    if a >= R_CAUTION:
        return "caution", f"{R_CAUTION} <= |r| < {R_NOT_INDEPENDENT}: partly redundant - document why both are kept"
    return "OK", f"|r| < {R_CAUTION}: the axes move independently"


def correlation_matrix(columns):
    """columns: {label: [values]} -> {a: {b: r}} (Pearson; None where undefined)."""
    labels = list(columns)
    return {a: {b: (1.0 if a == b else pearson(columns[a], columns[b])) for b in labels} for a in labels}


def least_correlated_pair(matrix):
    """(a, b, r) with the smallest |r| among distinct pairs; ties -> alphabetical.
    Pairs with undefined r are skipped. None when no defined pair exists."""
    best = None
    for a in sorted(matrix):
        for b in sorted(matrix[a]):
            if a >= b:
                continue
            r = matrix[a][b]
            if r is None:
                continue
            key = (abs(r), a, b)
            if best is None or key < best[0]:
                best = (key, (a, b, r))
    return best[1] if best else None


def same_axis_pairs(matrix):
    """Distinct pairs with |r| >= R_NOT_INDEPENDENT, sorted by |r| desc then names."""
    out = []
    for a in sorted(matrix):
        for b in sorted(matrix[a]):
            r = matrix[a][b]
            if a < b and r is not None and abs(r) >= R_NOT_INDEPENDENT:
                out.append((a, b, r))
    return sorted(out, key=lambda t: (-abs(t[2]), t[0], t[1]))


# --- placement (SKILL.md step 2) ---------------------------------------------


def normalise(values, scale=SCALE):
    """Min-max scale to 0..scale (min -> 0, max -> scale). A constant series maps
    to the midpoint (scale/2) - it carries no ordering information."""
    lo, hi = min(values), max(values)
    if hi == lo:
        return [scale / 2.0] * len(values)
    return [(v - lo) / (hi - lo) * scale for v in values]


def quadrant(x, y, x_split, y_split):
    """upper/lower by y (>= split is 'upper'), right/left by x (>= split is 'right')."""
    return ("upper" if y >= y_split else "lower") + "-" + ("right" if x >= x_split else "left")


def quadrant_description(q, x_label, y_label):
    """e.g. 'high integration depth / high frontier quality - leaders'."""
    upper, side = q.split("-")
    desc = f"{'high' if side == 'right' else 'low'} {x_label} / {'high' if upper == 'upper' else 'low'} {y_label}"
    tag = QUADRANT_TAGS.get(q)
    return f"{desc} - {tag}" if tag else desc


def assign_markers(names):
    """One-character map markers: the upper-cased initials when they are all
    distinct, else 1-9 then A-Z in name order (beyond 35 competitors: '#')."""
    initials = [n[0].upper() for n in names]
    if len(set(initials)) == len(initials) and all(c.isalnum() for c in initials):
        return initials
    return [MARKER_POOL[i] if i < len(MARKER_POOL) else "#" for i in range(len(names))]


def distance(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def crowding(points, names, threshold):
    """Mean nearest-neighbour distance and the pairs closer than `threshold`.
    Returns (mean_nn, nn_by_name, close_pairs); close_pairs = [(d, name_a, name_b)]
    sorted by distance then names."""
    n = len(points)
    nn = {}
    for i in range(n):
        best = None
        for j in range(n):
            if i != j:
                d = distance(points[i], points[j])
                if best is None or (d, names[j]) < best:
                    best = (d, names[j])
        nn[names[i]] = best
    mean_nn = mean([nn[k][0] for k in nn])
    close = []
    for i in range(n):
        for j in range(i + 1, n):
            d = distance(points[i], points[j])
            if d < threshold:
                a, b = sorted((names[i], names[j]))
                close.append((d, a, b))
    return mean_nn, nn, sorted(close)


def centroid(points, weights=None):
    if weights is None:
        return mean([p[0] for p in points]), mean([p[1] for p in points])
    total = sum(weights)
    return (sum(w * p[0] for w, p in zip(weights, points)) / total,
            sum(w * p[1] for w, p in zip(weights, points)) / total)


def _cell_index(v, lo, hi, n):
    """Position of v in [lo, hi] on an n-cell axis (nearest cell centre)."""
    if hi == lo:
        return n // 2
    return max(0, min(n - 1, int((v - lo) / (hi - lo) * (n - 1) + 0.5)))


def _num(v):
    """Compact number: '88', '9.5', '0.125'."""
    if float(v).is_integer():
        return str(int(v))
    return f"{v:.3f}".rstrip("0").rstrip(".")


def ascii_map(placements, frame, x_label, y_label, width=MAP_W, height=MAP_H):
    """Return the lines of a width x height character scatter of the placements.
    Column = x, row = y (top row is high). Middle row/column mark the quadrant
    split; markers overwrite them; '*' marks a cell holding several competitors.
    Returns (lines, collisions) with collisions = {(row, col): [markers]}."""
    x_lo, x_hi, y_lo, y_hi = frame
    grid = [[" "] * width for _ in range(height)]
    mid_c, mid_r = width // 2, height // 2
    for r in range(height):
        grid[r][mid_c] = ":"
    for c in range(width):
        grid[mid_r][c] = "."
    grid[mid_r][mid_c] = "+"
    cells = {}
    for p in placements:
        c = _cell_index(p["x"], x_lo, x_hi, width)
        r = height - 1 - _cell_index(p["y"], y_lo, y_hi, height)
        cells.setdefault((r, c), []).append(p["marker"])
    collisions = {}
    for (r, c) in sorted(cells):
        ms = cells[(r, c)]
        grid[r][c] = ms[0] if len(ms) == 1 else "*"
        if len(ms) > 1:
            collisions[(r, c)] = ms
    y_ticks = {0: _num(y_hi), mid_r: _num((y_lo + y_hi) / 2.0), height - 1: _num(y_lo)}
    gutter = max(len(t) for t in y_ticks.values()) + 1
    lines = [" " * gutter + f" ^ Y: {y_label} (high)"]
    for r in range(height):
        tick = y_ticks.get(r, "")
        lines.append(f"{tick:>{gutter}} |" + "".join(grid[r]) + "|")
    lines.append(" " * gutter + " +" + "-" * width + "+")
    lo_t, mid_t, hi_t = _num(x_lo), _num((x_lo + x_hi) / 2.0), _num(x_hi)
    axis = [" "] * (width + 2)
    for start, text in ((1, lo_t), (1 + mid_c - len(mid_t) // 2, mid_t), (1 + width - len(hi_t), hi_t)):
        for k, ch in enumerate(text):
            if 0 <= start + k < len(axis):
                axis[start + k] = ch
    lines.append(" " * gutter + " " + "".join(axis).rstrip())
    lines.append(" " * gutter + f" X: {x_label} (high) ->")
    for (r, c) in sorted(collisions):
        lines.append(" " * gutter + f" * = overlapping: {', '.join(collisions[(r, c)])}")
    return lines, collisions


# --- whitespace (SKILL.md step 3) --------------------------------------------


def _grid_index(v, lo, hi, k):
    """Cell 0..k-1 containing v; the top edge belongs to the last cell."""
    if hi == lo:
        return k // 2
    return max(0, min(k - 1, int((v - lo) / (hi - lo) * k)))


def whitespace_cells(placements, frame, k):
    """Overlay a k x k grid on `frame`. Returns (occupancy, empty_cells).

    occupancy: k x k list [iy][ix] of competitor counts (iy = 0 is the bottom row).
    empty_cells: dicts {ix, iy, x_range, y_range, centre, nearest, distance},
                 sorted by distance to the nearest competitor (desc), then ix, iy.
    """
    x_lo, x_hi, y_lo, y_hi = frame
    occupancy = [[0] * k for _ in range(k)]
    for p in placements:
        ix = _grid_index(p["x"], x_lo, x_hi, k)
        iy = _grid_index(p["y"], y_lo, y_hi, k)
        occupancy[iy][ix] += 1
    dx, dy = (x_hi - x_lo) / k, (y_hi - y_lo) / k
    empty = []
    for iy in range(k):
        for ix in range(k):
            if occupancy[iy][ix]:
                continue
            centre = (x_lo + (ix + 0.5) * dx, y_lo + (iy + 0.5) * dy)
            nearest = min(((distance(centre, (p["x"], p["y"])), p["name"]) for p in placements))
            empty.append({
                "ix": ix, "iy": iy,
                "x_range": (x_lo + ix * dx, x_lo + (ix + 1) * dx),
                "y_range": (y_lo + iy * dy, y_lo + (iy + 1) * dy),
                "centre": centre, "nearest": nearest[1], "distance": nearest[0],
            })
    empty.sort(key=lambda c: (-c["distance"], c["ix"], c["iy"]))
    return occupancy, empty


# --- analysis assembly -------------------------------------------------------


def analyse(competitors, extras, x_label, y_label, normalised=True, grid=DEFAULT_GRID,
            crowd=DEFAULT_CROWD):
    """Run every computation once; commands print slices of the result dict."""
    names = [c["name"] for c in competitors]
    xs_raw = [c["x"] for c in competitors]
    ys_raw = [c["y"] for c in competitors]
    weights = [c["weight"] for c in competitors] if competitors[0]["weight"] is not None else None

    r = pearson(xs_raw, ys_raw)
    rho = spearman(xs_raw, ys_raw)
    label, why = verdict(r)
    rho_label, _ = verdict(rho)
    bands = {"OK": 0, "caution": 1, "not independent": 2, "undefined": 2}
    spearman_note = None
    if rho is not None and r is not None and bands[rho_label] > bands[label]:
        spearman_note = (f"Spearman rho = {rho:+.3f} would read '{rho_label}': the relation is monotone "
                         f"but non-linear - treat the pair with at least that much suspicion.")
    columns = {f"{x_label} (x)": xs_raw, f"{y_label} (y)": ys_raw}
    for col in sorted(extras):
        columns[col] = extras[col]
    matrix = correlation_matrix(columns) if extras else None
    ortho = {
        "n": len(names), "pearson_r": r, "spearman_rho": rho, "verdict": label, "why": why,
        "rule": RULE_TEXT, "rule_note": RULE_NOTE, "spearman_note": spearman_note,
        "columns": list(columns), "matrix": matrix,
        "same_axis_pairs": same_axis_pairs(matrix) if matrix else [],
        "least_correlated_pair": least_correlated_pair(matrix) if matrix else None,
    }

    if normalised:
        xs, ys = normalise(xs_raw), normalise(ys_raw)
        frame = (0.0, SCALE, 0.0, SCALE)
    else:
        xs, ys = list(xs_raw), list(ys_raw)
        frame = (min(xs), max(xs), min(ys), max(ys))
    x_split, y_split = (frame[0] + frame[1]) / 2.0, (frame[2] + frame[3]) / 2.0
    markers = assign_markers(names)
    placements = []
    for i, c in enumerate(competitors):
        placements.append({
            "name": c["name"], "marker": markers[i], "x_raw": xs_raw[i], "y_raw": ys_raw[i],
            "x": xs[i], "y": ys[i], "quadrant": quadrant(xs[i], ys[i], x_split, y_split),
            "weight": c["weight"], "evidence": c["evidence"],
        })
    quadrants = {q: [p["name"] for p in placements if p["quadrant"] == q] for q in QUADRANT_ORDER}
    points = [(p["x"], p["y"]) for p in placements]
    mean_nn, nn, close = crowding(points, names, crowd)
    map_lines, collisions = ascii_map(placements, frame, x_label, y_label)
    occupancy, empty = whitespace_cells(placements, frame, grid)
    for cell in empty:
        cell["quadrant"] = quadrant(cell["centre"][0], cell["centre"][1], x_split, y_split)
    return {
        "x_label": x_label, "y_label": y_label, "normalised": normalised, "frame": frame,
        "x_split": x_split, "y_split": y_split, "orthogonality": ortho, "placements": placements,
        "quadrants": quadrants, "empty_quadrants": [q for q in QUADRANT_ORDER if not quadrants[q]],
        "map": map_lines, "collisions": collisions,
        "crowding": {"mean_nn_distance": mean_nn, "nearest": nn, "threshold": crowd, "close_pairs": close},
        "centroid": centroid(points), "weighted_centroid": centroid(points, weights) if weights else None,
        "whitespace": {"grid": grid, "occupancy": occupancy, "empty_cells": empty, "caveat": CAVEAT},
    }


# --- text output -------------------------------------------------------------


def _r(v):
    return "undefined" if v is None else f"{v:+.3f}"


def _suggestion(r):
    """Qualify the least-correlated pair: a suggestion, or a dead end when even it fails."""
    if abs(r) >= R_NOT_INDEPENDENT:
        return "even this pair is not independent (|r| >= 0.7): none of these columns yields orthogonal axes - measure something else."
    return SUGGESTION_NOTE


def lines_orthogonality(res):
    o = res["orthogonality"]
    out = [f"Orthogonality check - {res['x_label']} x {res['y_label']}, N = {o['n']} competitors",
           f"  Pearson r = {_r(o['pearson_r'])}   Spearman rho = {_r(o['spearman_rho'])}",
           f"  Verdict: {o['verdict'].upper()} - {o['why']}",
           f"  Rule: {o['rule']}",
           f"        {o['rule_note']}"]
    if o["spearman_note"]:
        out.append(f"  Note: {o['spearman_note']}")
    if o["matrix"]:
        cols = o["columns"]
        width = max(len(c) for c in cols)
        out.append("")
        out.append("  Correlation matrix (Pearson r) over all numeric columns:")
        for i, a in enumerate(cols):
            cells = "".join("   n/a" if o["matrix"][a][b] is None else f"{o['matrix'][a][b]:6.2f}" for b in cols)
            out.append(f"    [{i + 1}] {a:<{width}} {cells}")
        out.append("    " + " " * (width + 4) + " " + "".join(f"{'[' + str(i + 1) + ']':>6}" for i in range(len(cols))))
        if o["same_axis_pairs"]:
            out.append("  Same-axis pairs (|r| >= 0.7): " + "; ".join(f"{a} x {b} (r = {r:+.2f})" for a, b, r in o["same_axis_pairs"]))
        else:
            out.append("  Same-axis pairs (|r| >= 0.7): none")
        lc = o["least_correlated_pair"]
        if lc:
            out.append(f"  Least-correlated pair: {lc[0]} x {lc[1]} (r = {lc[2]:+.2f}) - {_suggestion(lc[2])}")
    return out


def _coord(p, axis, normalised):
    if normalised:
        return f"{p[axis]:.2f} (raw {_num(p[axis + '_raw'])})"
    return _num(p[axis])


def lines_placements(res):
    has_w = res["weighted_centroid"] is not None
    head = f"| Entity | X: {res['x_label']} | Y: {res['y_label']} | Quadrant |" + (" Weight |" if has_w else "") + " Evidence |"
    out = [head, "|---|---|---|---|" + ("---|" if has_w else "") + "---|"]
    for p in res["placements"]:
        ev = p["evidence"] or "{one sentence citing a source}"
        w = f" {_num(p['weight'])} |" if has_w else ""
        out.append(f"| {p['name']} [{p['marker']}] | {_coord(p, 'x', res['normalised'])} | "
                   f"{_coord(p, 'y', res['normalised'])} | {p['quadrant']} |{w} {ev} |")
    return out


def lines_quadrants(res):
    out = []
    for q in QUADRANT_ORDER:
        who = ", ".join(res["quadrants"][q]) or "(empty)"
        out.append(f"  {q:<11} ({quadrant_description(q, res['x_label'], res['y_label'])}): {who}")
    return out


def crowding_summary(res):
    """(index, pairs, centroid) phrases shared by the map and report views."""
    c = res["crowding"]
    unit = "0-10 scale" if res["normalised"] else "raw units"
    index = f"mean nearest-neighbour distance {c['mean_nn_distance']:.2f} ({unit}; lower = more crowded)"
    pairs = c["close_pairs"]
    pairs_text = f"pairs closer than {c['threshold']:.2f}: {len(pairs)}"
    if pairs:
        pairs_text += " - " + "; ".join(f"{a}-{b} ({d:.2f})" for d, a, b in pairs)
    cx, cy = res["centroid"]
    cent = f"({cx:.2f}, {cy:.2f})"
    if res["weighted_centroid"]:
        wx, wy = res["weighted_centroid"]
        cent += f"   weighted centroid (by weight): ({wx:.2f}, {wy:.2f})"
    return index, pairs_text, cent


def lines_crowding(res):
    index, pairs_text, cent = crowding_summary(res)
    return [f"Crowding index: {index}", f"  {pairs_text[0].upper() + pairs_text[1:]}", f"Centroid: {cent}"]


def lines_map(res):
    scale = ("min-max normalised to 0-10 (low < 5 <= high)" if res["normalised"]
             else f"raw values (split at the range midpoints {_num(res['x_split'])}, {_num(res['y_split'])})")
    out = [f"Map - {res['x_label']} (horizontal) x {res['y_label']} (vertical); N = {len(res['placements'])}; {scale}", ""]
    out += lines_placements(res)
    out.append("")
    out += res["map"]
    out.append("")
    out.append("Quadrant analysis:")
    out += lines_quadrants(res)
    out.append("")
    out += lines_crowding(res)
    return out


def lines_whitespace(res):
    w = res["whitespace"]
    k = w["grid"]
    x_lo, x_hi, y_lo, y_hi = res["frame"]
    dx, dy = (x_hi - x_lo) / k, (y_hi - y_lo) / k
    unit = "0-10 scale" if res["normalised"] else "raw units"
    out = [f"Whitespace - {k}x{k} grid over the map (cells of {_num(round(dx, 6))} x {_num(round(dy, 6))}, {unit})",
           "  Occupancy (rows: Y high -> low; columns: X low -> high):"]
    for iy in range(k - 1, -1, -1):
        hi_br = "]" if iy == k - 1 else ")"
        rng = f"y [{_num(round(y_lo + iy * dy, 6))},{_num(round(y_lo + (iy + 1) * dy, 6))}{hi_br}"
        out.append(f"    {rng:<16} | " + " ".join(f"{n:>2}" for n in w["occupancy"][iy]) + " |")
    if res["empty_quadrants"]:
        out.append("  Empty quadrants: " + "; ".join(
            f"{q} ({quadrant_description(q, res['x_label'], res['y_label'])})" for q in res["empty_quadrants"]))
    else:
        out.append("  Empty quadrants: none - all four quadrants are occupied (a valid answer, but argue it; SKILL.md anti-patterns)")
    if w["empty_cells"]:
        out.append(f"  Empty cells ({len(w['empty_cells'])} of {k * k}) ranked by distance from the nearest competitor (largest empty region first):")
        for i, c in enumerate(w["empty_cells"], start=1):
            xr, yr = c["x_range"], c["y_range"]
            xb = "]" if c["ix"] == k - 1 else ")"
            yb = "]" if c["iy"] == k - 1 else ")"
            out.append(f"   {i:>2}. x [{_num(round(xr[0], 6))},{_num(round(xr[1], 6))}{xb} x y [{_num(round(yr[0], 6))},{_num(round(yr[1], 6))}{yb}"
                       f"  centre ({c['centre'][0]:.2f}, {c['centre'][1]:.2f})  {c['quadrant']:<11}  nearest: {c['nearest']} at {c['distance']:.2f}")
    else:
        out.append(f"  Empty cells: none - every cell of the {k}x{k} grid is occupied")
    out.append("  " + w["caveat"])
    return out


def lines_report(res, category):
    o = res["orthogonality"]
    scale = ("min-max normalised to 0-10; low < 5 <= high; raw values in brackets" if res["normalised"]
             else f"raw values; split at the range midpoints ({_num(res['x_split'])}, {_num(res['y_split'])})")
    out = [f"## Competitive Positioning - {category}", "",
           f"**Axes chosen:** {res['x_label']} (horizontal) x {res['y_label']} (vertical)",
           "**Why these axes:** {one sentence on why these capture the variance best; why not {alternative}}",
           f"**Orthogonality check:** Pearson r = {_r(o['pearson_r'])} (Spearman rho = {_r(o['spearman_rho'])}) over N = {o['n']} - "
           f"{o['verdict'].upper()} ({o['why']}). Rule: {o['rule']}."]
    if o["spearman_note"]:
        out.append(f"  Note: {o['spearman_note']}")
    if o["least_correlated_pair"]:
        lc = o["least_correlated_pair"]
        out.append(f"  Least-correlated pair among all numeric columns: {lc[0]} x {lc[1]} (r = {lc[2]:+.2f}) - {_suggestion(lc[2])}")
    out += ["", f"**Placements:** ({scale})", ""]
    out += lines_placements(res)
    out += ["", "**Map:**", "", "```"] + res["map"] + ["```", "", "**Quadrant analysis:**", ""]
    out += ["- " + l.strip() for l in lines_quadrants(res)]
    out.append("")
    index, pairs_text, cent = crowding_summary(res)
    out.append(f"**Crowding:** {index}; {pairs_text}")
    out.append(f"**Centroid:** {cent}")
    out.append("")
    ws = lines_whitespace(res)
    out.append(f"**Whitespace ({res['whitespace']['grid']}x{res['whitespace']['grid']} grid):**")
    out += ws[1:]
    out += ["", "**Movement (optional, 3-year back-cast):** {who has moved? in which direction?} - not computed by the tool",
            "**Limitations:** {why this map is stale in X months; which dimensions it ignores} - not computed by the tool"]
    return out


# --- JSON output -------------------------------------------------------------


def _round(obj):
    """Round floats to 4 dp recursively; tuples -> lists."""
    if isinstance(obj, float):
        return round(obj, 4)
    if isinstance(obj, dict):
        return {str(k): _round(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_round(v) for v in obj]
    return obj


def to_json(payload):
    return json.dumps(_round(payload), indent=2, sort_keys=True)


def json_orthogonality(res):
    o = dict(res["orthogonality"])
    o["x_label"], o["y_label"] = res["x_label"], res["y_label"]
    return o


def json_map(res):
    return {k: res[k] for k in ("x_label", "y_label", "normalised", "frame", "x_split", "y_split",
                                "placements", "quadrants", "empty_quadrants", "map", "crowding",
                                "centroid", "weighted_centroid")}


def json_whitespace(res):
    return {"x_label": res["x_label"], "y_label": res["y_label"], "normalised": res["normalised"],
            "frame": res["frame"], "empty_quadrants": res["empty_quadrants"], **res["whitespace"]}


# --- selftest ----------------------------------------------------------------


def run_selftest():
    """Hand-verified assertions. Every expected value below was computed by
    hand, from the definitions in the module docstring, before being encoded."""
    n_checks = [0]

    def check(name, got, want, tol=1e-9):
        ok = (got is None and want is None) or (got is not None and want is not None and abs(got - want) <= tol)
        n_checks[0] += 1
        gs = "None" if got is None else f"{got:.6f}"
        ws = "None" if want is None else f"{want:.6f}"
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {gs}, expected {ws}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    def check_eq(name, got, want):
        ok = got == want
        n_checks[0] += 1
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got!r}, expected {want!r}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    # -- Pearson r (hand computation) --
    # x=[1,2,3,4], y=[2,4,6,8]: y = 2x exactly -> r = +1; y=[8,6,4,2] -> r = -1.
    check("pearson: y = 2x -> +1", pearson([1, 2, 3, 4], [2, 4, 6, 8]), 1.0)
    check("pearson: y = 10 - 2x -> -1", pearson([1, 2, 3, 4], [8, 6, 4, 2]), -1.0)
    # x=[1..5], y=[4,1,0,1,4] (symmetric parabola): dx=[-2,-1,0,1,2], dy=[2,-1,-2,-1,2]
    # -> sum dx*dy = -4+1+0-1+4 = 0 -> r = 0 exactly.
    check("pearson: symmetric parabola -> 0", pearson([1, 2, 3, 4, 5], [4, 1, 0, 1, 4]), 0.0)
    check_eq("pearson: zero variance -> undefined", pearson([1, 2, 3], [5, 5, 5]), None)

    # -- Spearman rho --
    # Monotone non-linear: x=[1,2,3,4], y=[1,4,9,16] -> ranks identical -> rho = 1.
    check("spearman: monotone squares -> +1", spearman([1, 2, 3, 4], [1, 4, 9, 16]), 1.0)
    # Ties: x=[1,2,2,3] -> mid-ranks [1,2.5,2.5,4]; y=[1,2,3,4] -> ranks [1,2,3,4].
    # dx=[-1.5,0,0,1.5], dy=[-1.5,-0.5,0.5,1.5]: sxy=4.5, sxx=4.5, syy=5 -> rho = 4.5/sqrt(22.5) = sqrt(0.9).
    check_eq("ranks: mid-ranks for ties", ranks([1, 2, 2, 3]), [1.0, 2.5, 2.5, 4.0])
    check("spearman: tied x -> sqrt(0.9)", spearman([1, 2, 2, 3], [1, 2, 3, 4]), math.sqrt(0.9))

    # -- verdict bands (|r| >= 0.7 not independent; 0.4 <= |r| < 0.7 caution; < 0.4 OK) --
    check_eq("verdict: r = 0.85", verdict(0.85)[0], "not independent")
    check_eq("verdict: r = -0.70 (boundary)", verdict(-0.70)[0], "not independent")
    check_eq("verdict: r = 0.50", verdict(0.50)[0], "caution")
    check_eq("verdict: r = 0.40 (boundary)", verdict(0.40)[0], "caution")
    check_eq("verdict: r = 0.20", verdict(0.20)[0], "OK")
    check_eq("verdict: r undefined", verdict(None)[0], "undefined")

    # -- correlation matrix + least-correlated pair --
    # a=[1,2,3,4], b=[2,4,6,8] (r=+1 with a), c=[4,1,0,1] (r vs a: dx=[-1.5,-.5,.5,1.5],
    # dc=[2.5,-.5,-1.5,-.5] -> sxy=-3.75-... = -3.75+0.25-0.75-0.75=-5, sxx=5, scc=9.0
    # -> r = -5/sqrt(45) = -0.745); least-correlated pair among {a,b,c} is (a,c)/(b,c) tie at
    # |r|=0.745 -> alphabetical (a, c).
    m = correlation_matrix({"a": [1, 2, 3, 4], "b": [2, 4, 6, 8], "c": [4, 1, 0, 1]})
    check("matrix: r(a,b) = +1", m["a"]["b"], 1.0)
    check("matrix: r(a,c) = -5/sqrt(45)", m["a"]["c"], -5 / math.sqrt(45))
    check_eq("matrix: least-correlated pair (tie -> alphabetical)", least_correlated_pair(m)[:2], ("a", "c"))
    check_eq("matrix: same-axis pairs", [(a, b) for a, b, _ in same_axis_pairs(m)], [("a", "b"), ("a", "c"), ("b", "c")])

    # -- normalisation --
    check_eq("normalise: [10,20,30] -> [0,5,10]", normalise([10, 20, 30]), [0.0, 5.0, 10.0])
    check_eq("normalise: constant -> midpoint 5", normalise([7, 7, 7]), [5.0, 5.0, 5.0])

    # -- quadrant assignment (split at 5; >= is high) --
    check_eq("quadrant: (7,8) upper-right", quadrant(7, 8, 5, 5), "upper-right")
    check_eq("quadrant: (2,8) upper-left", quadrant(2, 8, 5, 5), "upper-left")
    check_eq("quadrant: (7,2) lower-right", quadrant(7, 2, 5, 5), "lower-right")
    check_eq("quadrant: (2,2) lower-left", quadrant(2, 2, 5, 5), "lower-left")
    check_eq("quadrant: (5,5) boundary -> upper-right", quadrant(5, 5, 5, 5), "upper-right")
    check_eq("quadrant description", quadrant_description("upper-left", "cost", "quality"), "low cost / high quality")

    # -- nearest-neighbour crowding + centroid --
    # points (0,0), (3,4), (10,10): NN distances 5, 5, sqrt(85) -> mean (10 + sqrt(85))/3.
    pts, nms = [(0, 0), (3, 4), (10, 10)], ["p", "q", "r"]
    mean_nn, nn, close = crowding(pts, nms, 1.0)
    check("crowding: mean NN distance", mean_nn, (10 + math.sqrt(85)) / 3)
    check_eq("crowding: nearest of r is q", nn["r"][1], "q")
    check_eq("crowding: 0 pairs closer than 1.0", len(close), 0)
    check_eq("crowding: 1 pair closer than 6.0", [(a, b) for _, a, b in crowding(pts, nms, 6.0)[2]], [("p", "q")])
    check("centroid x", centroid(pts)[0], 13 / 3)
    check("weighted centroid: (0,0) w=1, (10,10) w=3 -> 7.5", centroid([(0, 0), (10, 10)], [1, 3])[0], 7.5)

    # -- ASCII map cell mapping: (10,10) top-right, (0,0) bottom-left, (5,5) centre --
    check_eq("map: x=10 -> column 20", _cell_index(10, 0, 10, MAP_W), 20)
    check_eq("map: y=10 -> row 0", MAP_H - 1 - _cell_index(10, 0, 10, MAP_H), 0)
    check_eq("map: x=0 -> column 0", _cell_index(0, 0, 10, MAP_W), 0)
    check_eq("map: y=5 -> middle row 5", MAP_H - 1 - _cell_index(5, 0, 10, MAP_H), 5)
    fixed = [{"name": "Hi", "marker": "H", "x": 10.0, "y": 10.0}, {"name": "Lo", "marker": "L", "x": 0.0, "y": 0.0}]
    lines, coll = ascii_map(fixed, (0, 10, 0, 10), "x", "y")
    check_eq("map: H drawn at top-right", lines[1][-2], "H")
    check_eq("map: L drawn at bottom-left", lines[MAP_H][-MAP_W - 1], "L")
    check_eq("map: no collisions", coll, {})
    _, coll2 = ascii_map(fixed + [{"name": "Hi2", "marker": "2", "x": 9.9, "y": 9.9}], (0, 10, 0, 10), "x", "y")
    check_eq("map: overlapping cell reported", coll2, {(0, 20): ["H", "2"]})
    check_eq("markers: unique initials", assign_markers(["Ardent", "Bramble"]), ["A", "B"])
    check_eq("markers: clashing initials -> sequence", assign_markers(["Ann", "Abe", "Cy"]), ["1", "2", "3"])

    # -- whitespace on a fixed layout: points (1,1), (9,9), (1,9) --
    # 2x2 grid: only the lower-right cell (x in [5,10], y in [0,5)) is empty; its centre
    # (7.5, 2.5) is sqrt(1.5^2 + 6.5^2) = sqrt(44.5) from both (9,9) and (1,1).
    layout = [{"name": "a", "x": 1.0, "y": 1.0}, {"name": "b", "x": 9.0, "y": 9.0}, {"name": "c", "x": 1.0, "y": 9.0}]
    occ, empty = whitespace_cells(layout, (0, 10, 0, 10), 2)
    check_eq("whitespace 2x2: occupancy", occ, [[1, 0], [1, 1]])
    check_eq("whitespace 2x2: one empty cell at (ix=1, iy=0)", [(c["ix"], c["iy"]) for c in empty], [(1, 0)])
    check("whitespace 2x2: distance to nearest = sqrt(44.5)", empty[0]["distance"], math.sqrt(44.5))
    check_eq("whitespace 2x2: nearest name (tie -> alphabetical)", empty[0]["nearest"], "a")
    # 4x4 grid: 13 empty cells; the farthest-from-anyone is (ix=3, iy=0), centre (8.75, 1.25),
    # distance sqrt(0.25^2 + 7.75^2) = sqrt(60.125) to (9,9).
    occ4, empty4 = whitespace_cells(layout, (0, 10, 0, 10), 4)
    check_eq("whitespace 4x4: 13 empty cells", len(empty4), 13)
    check_eq("whitespace 4x4: largest empty region first", (empty4[0]["ix"], empty4[0]["iy"]), (3, 0))
    check("whitespace 4x4: its distance = sqrt(60.125)", empty4[0]["distance"], math.sqrt(60.125))
    check_eq("grid index: top edge belongs to the last cell", _grid_index(10, 0, 10, 4), 3)

    # -- parsing: reserved columns, extras, ignored non-numeric, name sort --
    comps, extras, ignored = parse_rows([
        {"name": "Zed", "x": "3", "y": "1", "weight": "2", "size": "10", "note": "text", "evidence": "src"},
        {"name": "Amy", "x": "1", "y": "2", "weight": "1", "size": "5", "note": "7"},
    ])
    check_eq("parse: sorted by name", [c["name"] for c in comps], ["Amy", "Zed"])
    check_eq("parse: extras numeric only", extras, {"size": [5.0, 10.0]})
    check_eq("parse: non-numeric column ignored", ignored, ["note"])
    check_eq("parse: evidence kept", comps[1]["evidence"], "src")
    check("parse: weight kept", comps[0]["weight"], 1.0)

    # -- end-to-end on the demo: verdict OK, exit-code contract --
    d_comps, d_extras, _ = parse_rows(DEMO["competitors"])
    res = analyse(d_comps, d_extras, DEMO["x_label"], DEMO["y_label"])
    check_eq("demo: orthogonality verdict", res["orthogonality"]["verdict"], "OK")
    check_eq("demo: 8 placements, 4 quadrants occupied", (len(res["placements"]), res["empty_quadrants"]), (8, []))
    check_eq("demo: Ardent-Halcyon is the crowded pair", [(a, b) for _, a, b in res["crowding"]["close_pairs"]], [("Ardent", "Halcyon")])

    print(f"ALL {n_checks[0]} CHECKS PASSED")
    print("selftest OK")
    return 0


# --- CLI ---------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(
        description="Axis orthogonality (Pearson/Spearman), min-max 2x2 map with quadrants, "
        "crowding index and whitespace grid for a competitive landscape (SKILL.md steps 1-3)."
    )
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    sub = parser.add_subparsers(dest="command")
    for name, helptext in [
        ("orthogonality", "Pearson r / Spearman rho between the two axes, verdict, correlation matrix over extra columns"),
        ("map", "normalised placements, quadrants, ASCII scatter, crowding index, centroid"),
        ("whitespace", "k x k grid over the map: empty cells ranked by distance from the nearest competitor"),
        ("report", "everything above in the SKILL.md output order"),
    ]:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--file", help="CSV or JSON file of competitors (name, x, y [, weight, evidence, extra numeric columns])")
        p.add_argument("--demo", action="store_true", help="use the built-in synthetic 8-competitor landscape")
        p.add_argument("--x-col", default="x", help="column used as the X axis (default: x)")
        p.add_argument("--y-col", default="y", help="column used as the Y axis (default: y)")
        p.add_argument("--x-label", help="name of the X axis (default: JSON x_label, else the column name)")
        p.add_argument("--y-label", help="name of the Y axis (default: JSON y_label, else the column name)")
        p.add_argument("--json", action="store_true", help="emit JSON instead of text")
        if name in ("map", "whitespace", "report"):
            p.add_argument("--no-normalise", action="store_true", help="keep raw axis values (default: min-max to 0-10)")
            p.add_argument("--grid", type=int, default=DEFAULT_GRID, help=f"whitespace grid size k (default {DEFAULT_GRID})")
            p.add_argument("--crowd", type=float, default=DEFAULT_CROWD, help=f"pairs closer than this count as crowded (default {DEFAULT_CROWD})")
        if name == "report":
            p.add_argument("--category", help="category name for the report title (default: JSON category)")
    return parser


def get_data(args, parser):
    """Return (competitors, extras, ignored, meta) from --demo or --file."""
    if args.demo and args.file:
        parser.error("pass either --file PATH or --demo, not both")
    try:
        if args.demo:
            comps, extras, ignored = parse_rows(DEMO["competitors"], args.x_col, args.y_col)
            meta = {k: DEMO[k] for k in ("category", "x_label", "y_label")}
        elif args.file:
            comps, extras, ignored, meta = load_file(args.file, args.x_col, args.y_col)
        else:
            parser.error("pass --file PATH or --demo")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(f"could not load input: {exc}")
    if len(comps) < 3:
        parser.error(f"positioning needs >= 3 competitors for a meaningful map (SKILL.md); got {len(comps)}")
    return comps, extras, ignored, meta


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.command:
        parser.error("choose a command: orthogonality | map | whitespace | report  (or --selftest)")
    comps, extras, ignored, meta = get_data(args, parser)
    x_label = args.x_label or meta.get("x_label") or (args.x_col if args.x_col.lower() != "x" else "X")
    y_label = args.y_label or meta.get("y_label") or (args.y_col if args.y_col.lower() != "y" else "Y")
    normalised = not getattr(args, "no_normalise", False)
    grid = getattr(args, "grid", DEFAULT_GRID)
    crowd = getattr(args, "crowd", DEFAULT_CROWD)
    if grid < 2 or grid > 50:
        parser.error("--grid must be between 2 and 50")
    if crowd < 0:
        parser.error("--crowd must be >= 0")
    xs = [c["x"] for c in comps]
    ys = [c["y"] for c in comps]
    if args.command != "orthogonality" and (min(xs) == max(xs) or min(ys) == max(ys)):
        parser.error("an axis has zero range across the competitors - it does not discriminate; choose another axis")

    res = analyse(comps, extras, x_label, y_label, normalised=normalised, grid=grid, crowd=crowd)
    failing = res["orthogonality"]["verdict"] in ("not independent", "undefined")
    if args.command == "orthogonality":
        payload, text = json_orthogonality(res), lines_orthogonality(res)
    elif args.command == "map":
        payload, text = json_map(res), lines_map(res)
    elif args.command == "whitespace":
        payload, text = json_whitespace(res), lines_whitespace(res)
    else:
        category = args.category or meta.get("category") or "{category}"
        payload = {"category": category, "orthogonality": json_orthogonality(res), **json_map(res),
                   "whitespace": json_whitespace(res)}
        text = lines_report(res, category)
    if ignored:
        note = "note: non-numeric column(s) ignored as axes: " + ", ".join(ignored)
        payload["ignored_columns"] = ignored
        text = text + ["", note]
    if args.json:
        print(to_json(payload))
    else:
        print("\n".join(text))
    if failing and args.command in ("orthogonality", "report"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
