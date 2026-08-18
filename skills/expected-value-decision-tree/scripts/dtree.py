#!/usr/bin/env python3
"""dtree.py -- decision-tree roll-back, EVPI / EVSI, one-way sensitivity (tornado)
and seeded Monte Carlo for staged decisions under uncertainty.

Implements the definitions in ../SKILL.md (Raiffa 1968; Howard 1966, 1968;
Clemen & Reilly 2014, ch. 5 sensitivity analysis and ch. 12 value of information):

  * Roll-back: terminal = payoff; chance node EV = sum_i p_i * (EV_i - cost_i);
    decision node EV = max_i (EV_i - cost_i), ties broken by branch order.
  * EVPI for a named uncertainty U with prior P(o):
        EVPI = sum_o P(o) * [best EV when every U node is fixed at outcome o] - best EV
    (>= 0 whenever the tree's probabilities for U are Bayes-consistent).
  * EVSI for an imperfect signal S with likelihood P(s | o):
        P(s) = sum_o P(o) P(s|o);   P(o|s) = P(o) P(s|o) / P(s)
        EVSI = sum_s P(s) * [best EV with every U node at P(o|s)] - best EV
    with 0 <= EVSI <= EVPI; the signal is worth buying when EVSI exceeds its cost.
  * One-way sensitivity: each input moved -pct / +pct (default 20 %) with the
    others at base; swing = |EV(high) - EV(low)|, ranked into a tornado table;
    switching point = the input value at which the optimal root branch changes
    (found by bisection). Probabilities are clamped to [0, 1] and the sibling
    branches rescaled so every chance node still sums to 1.
  * Monte Carlo over inputs given as {"min", "mode", "max"} triangular ranges,
    seeded so runs are reproducible: distribution (mean, P10/P50/P90) of the
    base-policy EV and of the per-draw re-optimised EV, plus how often each
    root option is optimal.

Stdlib only. Python 3.9+. Deterministic: no wall clock, seeded randomness only.

Usage:
    python3 dtree.py solve       --file tree.json [--json]
    python3 dtree.py evpi        --file tree.json [--node NAME] [--all]
    python3 dtree.py evpi        --file tree.json --evsi --likelihood signal.json [--drop LABEL]
    python3 dtree.py sensitivity --file tree.json [--pct 20] [--param KEY --range a:b:steps]
    python3 dtree.py montecarlo  --file tree.json --draws 10000 --seed 42
    python3 dtree.py <command>   --demo              # the SKILL.md worked example (built in)
    python3 dtree.py --selftest

Tree file (JSON):
    {"title": "...", "units": "USD M (NPV)",                              # optional
     "variables": {"v_high": 60, "c_dev": {"min": 18, "mode": 20, "max": 25}},   # optional
     "root": <node>}                                                     # or the <node> itself
    <node> = {"type": "decision", "name": "...", "branches": [{"label": "...", "cost": 20, "node": <node>}, ...]}
           | {"type": "chance",   "name": "...", "branches": [{"label": "...", "p": 0.4, "node": <node>}, ...]}
           | {"type": "terminal", "value": 60}
    A branch may carry "value": x instead of "node" (a terminal leaf). One branch
    per chance node may omit "p" (the complement, 1 - the others). Any p / cost /
    value may be a number, a variable name (string) or a {"min","mode","max"}
    range (the mode is the point estimate; ranges feed montecarlo). Chance nodes
    with the same "name" are the same uncertainty (used by evpi / evsi).
    Sensitivity keys: var:NAME, p:PATH, cost:PATH, value:PATH where PATH is the
    branch labels from the root joined by "/", e.g. "p:Pilot first/Positive".
Signal file (for --evsi):
    {"uncertainty": "Demand", "signals": ["Positive", "Negative"], "cost": 2,
     "likelihood": {"High": {"Positive": 0.9, "Negative": 0.1},
                    "Low":  {"Positive": 0.4, "Negative": 0.6}}}       # rows = P(signal | outcome)
"""

import argparse
import json
import math
import random
import sys
from collections import Counter, OrderedDict

EPS = 1e-9
PROB_TOL = 1e-6
KINDS = ("decision", "chance", "terminal")


class TreeError(ValueError):
    """Malformed tree, signal or policy input."""


# --- data model --------------------------------------------------------------


class Node:
    __slots__ = ("kind", "name", "path", "branches", "value_key")

    def __init__(self, kind, name, path):
        self.kind, self.name, self.path = kind, name, path
        self.branches = []      # Branch objects (decision / chance nodes)
        self.value_key = None   # parameter key of the payoff (terminal nodes)


class Branch:
    __slots__ = ("label", "path", "p_key", "cost_key", "node")

    def __init__(self, label, path):
        self.label, self.path = label, path
        self.p_key = None       # chance branches: parameter key; None = complement
        self.cost_key = None    # parameter key of the branch cost; None = 0
        self.node = None        # child Node


class Tree:
    def __init__(self):
        self.title, self.units, self.root = "", "", None
        # key -> {"kind": p|cost|value|var, "base": float, "range": (lo, mode, hi) | None, "as_p": bool}
        self.params = OrderedDict()

    def base_values(self):
        return {k: v["base"] for k, v in self.params.items()}


class Result:
    def __init__(self):
        self.root_ev = 0.0
        self.node_ev = {}      # node path -> EV
        self.branch_ev = {}    # branch path -> child EV - branch cost
        self.choice = {}       # decision node path -> chosen label
        self.probs = {}        # chance node path -> effective probabilities


# --- parsing -----------------------------------------------------------------


def _number(x, what):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or math.isnan(x) or math.isinf(x):
        raise TreeError("%s must be a finite number, got %r" % (what, x))
    return float(x)


def _add_param(tree, key, kind, raw, what):
    if isinstance(raw, dict):
        for k in ("min", "mode", "max"):
            if k not in raw:
                raise TreeError("%s: a range needs min, mode and max" % what)
        lo, mode, hi = (_number(raw[k], "%s.%s" % (what, k)) for k in ("min", "mode", "max"))
        if not lo <= mode <= hi:
            raise TreeError("%s: need min <= mode <= max" % what)
        base, rng = mode, (lo, mode, hi)
    else:
        base, rng = _number(raw, what), None
    if kind == "p":
        vals = rng if rng else (base,)
        if min(vals) < -EPS or max(vals) > 1 + EPS:
            raise TreeError("%s: probabilities must lie in [0, 1]" % what)
    if key in tree.params:
        raise TreeError("duplicate parameter %s" % key)
    tree.params[key] = {"kind": kind, "base": base, "range": rng, "as_p": kind == "p"}
    return key


def _slot(tree, raw, kind, path, variables, what):
    """Register one numeric slot (literal, range or variable reference); return its key."""
    if isinstance(raw, str):
        if raw not in variables:
            raise TreeError("%s: unknown variable %r" % (what, raw))
        vk = "var:" + raw
        if kind == "p":
            prm = tree.params[vk]
            vals = prm["range"] or (prm["base"],)
            if min(vals) < -EPS or max(vals) > 1 + EPS:
                raise TreeError("%s: variable %r is used as a probability but lies outside [0, 1]" % (what, raw))
            prm["as_p"] = True
        return vk
    return _add_param(tree, "%s:%s" % (kind, path), kind, raw, what)


def _parse_node(tree, d, path, variables):
    where = "node %r" % (path or "root")
    if not isinstance(d, dict):
        raise TreeError("%s must be a JSON object" % where)
    kind = str(d.get("type", "")).lower()
    if kind not in KINDS:
        raise TreeError("%s: type must be decision, chance or terminal" % where)
    node = Node(kind, str(d.get("name", "")) or (path or "root"), path)
    if kind == "terminal":
        if "value" not in d:
            raise TreeError("%s: terminal needs a value" % where)
        node.value_key = _slot(tree, d["value"], "value", path, variables, "%s value" % where)
        return node
    branches = d.get("branches")
    if not isinstance(branches, list) or not branches:
        raise TreeError("%s: a %s node needs a non-empty branches list" % (where, kind))
    seen, n_comp = set(), 0
    for i, b in enumerate(branches):
        if not isinstance(b, dict):
            raise TreeError("%s: branch %d must be an object" % (where, i))
        label = str(b.get("label", "")).strip()
        if not label:
            raise TreeError("%s: branch %d needs a label" % (where, i))
        if label in seen:
            raise TreeError("%s: duplicate branch label %r" % (where, label))
        seen.add(label)
        bpath = label if not path else "%s/%s" % (path, label)
        br, bwhat = Branch(label, bpath), "branch %r" % bpath
        if "cost" in b:
            br.cost_key = _slot(tree, b["cost"], "cost", bpath, variables, "%s cost" % bwhat)
        if kind == "chance":
            if "p" in b:
                br.p_key = _slot(tree, b["p"], "p", bpath, variables, "%s p" % bwhat)
            else:
                n_comp += 1
                if n_comp > 1:
                    raise TreeError("%s: at most one branch may omit p (the complement)" % where)
        elif "p" in b:
            raise TreeError("%s: decision branches take no probability" % bwhat)
        if "node" in b:
            br.node = _parse_node(tree, b["node"], bpath, variables)
        elif "value" in b:
            br.node = Node("terminal", label, bpath)
            br.node.value_key = _slot(tree, b["value"], "value", bpath, variables, "%s value" % bwhat)
        else:
            raise TreeError("%s: needs a child node or a value" % bwhat)
        node.branches.append(br)
    return node


def parse_tree(data, drop=()):
    """Build a Tree from the JSON structure; `drop` removes root branches by label."""
    if not isinstance(data, dict):
        raise TreeError("tree file must be a JSON object")
    tree = Tree()
    if "root" in data:
        tree.title = str(data.get("title", ""))
        tree.units = str(data.get("units", ""))
        variables, root_data = data.get("variables") or {}, data["root"]
    else:
        variables, root_data = {}, data
    if not isinstance(variables, dict):
        raise TreeError("variables must be an object")
    if drop:
        if not isinstance(root_data, dict) or not isinstance(root_data.get("branches"), list):
            raise TreeError("--drop needs a root node with branches")
        labels = [str(b.get("label", "")) for b in root_data["branches"] if isinstance(b, dict)]
        for lab in drop:
            if lab not in labels:
                raise TreeError("--drop: no root branch labelled %r (have: %s)" % (lab, ", ".join(labels)))
        root_data = dict(root_data)
        root_data["branches"] = [b for b in root_data["branches"] if str(b.get("label", "")) not in drop]
        if not root_data["branches"]:
            raise TreeError("--drop removed every root branch")
    for vname in variables:
        _add_param(tree, "var:" + str(vname), "var", variables[vname], "variable %r" % vname)
    tree.root = _parse_node(tree, root_data, "", variables)
    validate_probabilities(tree)
    return tree


def load_tree(path, drop=()):
    with open(path, encoding="utf-8") as fh:
        return parse_tree(json.load(fh), drop)


def load_signal(data):
    """Validate a likelihood (signal) description; returns a normalised dict."""
    if not isinstance(data, dict) or not isinstance(data.get("likelihood"), dict):
        raise TreeError("signal file needs a 'likelihood' object {outcome: {signal: P(signal|outcome)}}")
    lik = data["likelihood"]
    signals = data.get("signals")
    if signals is None:
        signals = []
        for row in lik.values():
            for s in (row if isinstance(row, dict) else {}):
                if s not in signals:
                    signals.append(s)
    if not isinstance(signals, list) or not signals:
        raise TreeError("signal file: 'signals' must be a non-empty list")
    out_lik = {}
    for o, row in lik.items():
        if not isinstance(row, dict):
            raise TreeError("likelihood row for outcome %r must be an object" % o)
        vals = {}
        for s in signals:
            if s not in row:
                raise TreeError("likelihood row for %r lacks signal %r" % (o, s))
            v = _number(row[s], "P(%s | %s)" % (s, o))
            if v < -EPS or v > 1 + EPS:
                raise TreeError("P(%s | %s) = %.4f outside [0, 1]" % (s, o, v))
            vals[s] = v
        tot = sum(vals.values())
        if abs(tot - 1.0) > PROB_TOL:
            raise TreeError("likelihood row for %r sums to %.4f, not 1" % (o, tot))
        out_lik[str(o)] = vals
    cost = _number(data.get("cost", 0.0), "signal cost")
    prior = data.get("prior")
    if prior is not None:
        if not isinstance(prior, dict):
            raise TreeError("signal 'prior' must be an object {outcome: probability}")
        prior = {str(k): _number(v, "prior[%s]" % k) for k, v in prior.items()}
    return {"uncertainty": data.get("uncertainty"), "signals": [str(s) for s in signals],
            "likelihood": out_lik, "cost": cost, "prior": prior}


# --- probabilities -----------------------------------------------------------


def branch_probs(node, values, pinned=None, strict=False):
    """Effective probabilities of a chance node's branches (always sum to 1).

    strict: validate the stated numbers (used at load time; raises TreeError).
    pinned: parameter key held at its exact value while the siblings are
            rescaled to fill the remainder (one-way sensitivity)."""
    where = "chance node %r" % (node.path or "root")
    raw = [None if b.p_key is None else values[b.p_key] for b in node.branches]
    if strict:
        for b, x in zip(node.branches, raw):
            if x is not None and (x < -PROB_TOL or x > 1 + PROB_TOL):
                raise TreeError("branch %r: probability %.4f outside [0, 1]" % (b.path, x))
    if len(raw) == 1:
        if strict and raw[0] is not None and abs(raw[0] - 1.0) > PROB_TOL:
            raise TreeError("%s: single branch must have p = 1" % where)
        return [1.0]
    clamped = [None if x is None else min(1.0, max(0.0, x)) for x in raw]
    total = sum(x for x in clamped if x is not None)
    if None in clamped:                                   # complement branch present
        if strict and total > 1 + PROB_TOL:
            raise TreeError("%s: stated probabilities sum to %.4f > 1" % (where, total))
        scale = 1.0 / total if total > 1.0 else 1.0
        rest = max(0.0, 1.0 - total * scale)
        return [rest if x is None else x * scale for x in clamped]
    if strict and abs(total - 1.0) > PROB_TOL:
        raise TreeError("%s: probabilities sum to %.4f, not 1" % (where, total))
    if pinned is not None:
        idx = [i for i, b in enumerate(node.branches) if b.p_key == pinned]
        if idx:
            i, pv = idx[0], clamped[idx[0]]
            others = total - pv
            n_others = len(clamped) - 1
            return [pv if j == i else (x * (1.0 - pv) / others if others > EPS else (1.0 - pv) / n_others)
                    for j, x in enumerate(clamped)]
    if total <= EPS:
        raise TreeError("%s: probabilities sum to 0" % where)
    return [x / total for x in clamped]


def validate_probabilities(tree):
    values = tree.base_values()

    def walk(node):
        if node.kind == "chance":
            branch_probs(node, values, strict=True)
        for b in node.branches:
            walk(b.node)

    walk(tree.root)


# --- roll-back ---------------------------------------------------------------


def solve(tree, values=None, pinned=None, override=None, policy=None):
    """Roll the tree back. override = {uncertainty name: {label: prob}} replaces the
    probabilities of every chance node with that name; policy = {decision path:
    label} forces choices instead of maximising."""
    values = tree.base_values() if values is None else values
    override = override or {}
    res = Result()

    def cost(b):
        return values[b.cost_key] if b.cost_key else 0.0

    def ev(node):
        if node.kind == "terminal":
            v = values[node.value_key]
            res.node_ev[node.path] = v
            return v
        child = []
        for b in node.branches:
            bev = ev(b.node) - cost(b)
            res.branch_ev[b.path] = bev
            child.append(bev)
        if node.kind == "chance":
            if node.name in override:
                probs = [override[node.name][b.label] for b in node.branches]
            else:
                probs = branch_probs(node, values, pinned=pinned)
            res.probs[node.path] = probs
            total = sum(p * c for p, c in zip(probs, child))
        else:
            if policy and node.path in policy:
                labels = [b.label for b in node.branches]
                if policy[node.path] not in labels:
                    raise TreeError("policy names unknown branch %r at %r" % (policy[node.path], node.path or "root"))
                i = labels.index(policy[node.path])
            else:
                i = max(range(len(child)), key=lambda k: (child[k], -k))
            res.choice[node.path] = node.branches[i].label
            total = child[i]
        res.node_ev[node.path] = total
        return total

    res.root_ev = ev(tree.root)
    return res


def root_choice(res):
    return res.choice.get("")


def node_at(tree, path):
    node = tree.root
    if path:
        for label in path.split("/"):
            node = [b for b in node.branches if b.label == label][0].node
    return node


def policy_lines(tree, res):
    """[(where, chosen label)] for every decision node reachable under the optimal policy."""
    out = []

    def walk(node):
        if node.kind == "decision":
            lab = res.choice[node.path]
            out.append(("at root" if not node.path else "after %s" % node.path, lab))
            walk([b for b in node.branches if b.label == lab][0].node)
        elif node.kind == "chance":
            for b in node.branches:
                walk(b.node)

    walk(tree.root)
    return out


def risk_profile(tree, res, values=None):
    """Distribution of net outcomes (payoff minus costs on the path) under the solved policy."""
    values = tree.base_values() if values is None else values
    dist = {}

    def cost(b):
        return values[b.cost_key] if b.cost_key else 0.0

    def walk(node, prob, net):
        if node.kind == "terminal":
            v = round(net + values[node.value_key], 9)
            dist[v] = dist.get(v, 0.0) + prob
        elif node.kind == "decision":
            b = [x for x in node.branches if x.label == res.choice[node.path]][0]
            walk(b.node, prob, net - cost(b))
        else:
            for b, p in zip(node.branches, res.probs[node.path]):
                if p > 0:
                    walk(b.node, prob * p, net - cost(b))

    walk(tree.root, 1.0, 0.0)
    return sorted(dist.items())


# --- value of information ----------------------------------------------------


def uncertainties(tree):
    """OrderedDict name -> {"labels", "paths"} in breadth-first order (top-level first)."""
    out, queue = OrderedDict(), [tree.root]
    while queue:
        node = queue.pop(0)
        if node.kind == "chance":
            labels = [b.label for b in node.branches]
            if node.name in out:
                if out[node.name]["labels"] != labels:
                    raise TreeError("chance nodes named %r must list the same outcomes in the same order (%s vs %s)"
                                    % (node.name, "/".join(out[node.name]["labels"]), "/".join(labels)))
                out[node.name]["paths"].append(node.path)
            else:
                out[node.name] = {"labels": labels, "paths": [node.path]}
        queue.extend(b.node for b in node.branches)
    return out


def _prior_for(tree, unc, name, values, prior):
    labels = unc[name]["labels"]
    if prior is None:
        first = node_at(tree, unc[name]["paths"][0])
        return OrderedDict(zip(labels, branch_probs(first, values)))
    if set(prior) != set(labels):
        raise TreeError("prior outcomes %s do not match %r outcomes %s" % (sorted(prior), name, labels))
    tot = sum(prior.values())
    if abs(tot - 1.0) > PROB_TOL:
        raise TreeError("prior sums to %.4f, not 1" % tot)
    return OrderedDict((l, prior[l]) for l in labels)


def _pick_uncertainty(unc, name):
    if not unc:
        raise TreeError("the tree has no chance node")
    if name is None:
        return next(iter(unc))
    if name not in unc:
        raise TreeError("no chance node named %r (have: %s)" % (name, ", ".join(unc)))
    return name


def evpi(tree, name=None, values=None, prior=None):
    values = tree.base_values() if values is None else values
    unc = uncertainties(tree)
    name = _pick_uncertainty(unc, name)
    labels = unc[name]["labels"]
    prior = _prior_for(tree, unc, name, values, prior)
    base = solve(tree, values)
    ev_pi, rows = 0.0, []
    for lab in labels:
        res = solve(tree, values, override={name: {l: (1.0 if l == lab else 0.0) for l in labels}})
        ev_pi += prior[lab] * res.root_ev
        rows.append({"outcome": lab, "prior": prior[lab], "ev": res.root_ev, "choice": root_choice(res)})
    return {"uncertainty": name, "n_nodes": len(unc[name]["paths"]), "prior_from": unc[name]["paths"][0] or "root",
            "prior": prior, "ev_base": base.root_ev, "base_choice": root_choice(base),
            "ev_perfect": ev_pi, "evpi": ev_pi - base.root_ev, "outcomes": rows}


def evsi(tree, signal, values=None):
    values = tree.base_values() if values is None else values
    unc = uncertainties(tree)
    name = _pick_uncertainty(unc, signal.get("uncertainty"))
    labels = unc[name]["labels"]
    lik = signal["likelihood"]
    missing = [l for l in labels if l not in lik]
    if missing:
        raise TreeError("likelihood lacks rows for outcomes: %s" % ", ".join(missing))
    prior = _prior_for(tree, unc, name, values, signal.get("prior"))
    base = solve(tree, values)
    ev_si, rows = 0.0, []
    for s in signal["signals"]:
        ps = sum(prior[o] * lik[o][s] for o in labels)
        if ps <= EPS:
            rows.append({"signal": s, "p_signal": 0.0, "posterior": None, "ev": None, "choice": None})
            continue
        post = OrderedDict((o, prior[o] * lik[o][s] / ps) for o in labels)
        res = solve(tree, values, override={name: post})
        ev_si += ps * res.root_ev
        rows.append({"signal": s, "p_signal": ps, "posterior": post, "ev": res.root_ev, "choice": root_choice(res)})
    perfect = evpi(tree, name, values, prior)
    value = ev_si - base.root_ev
    return {"uncertainty": name, "signals": rows, "ev_base": base.root_ev, "base_choice": root_choice(base),
            "ev_sample": ev_si, "evsi": value, "cost": signal["cost"], "net": value - signal["cost"],
            "evpi": perfect["evpi"], "worth_running": value - signal["cost"] > EPS}


# --- sensitivity -------------------------------------------------------------


def _find_switch(tree, key, values, x_ok, x_bad, base_choice, iters=60):
    """Bisection between x_ok (root choice == base) and x_bad (root choice differs)."""
    for _ in range(iters):
        mid = 0.5 * (x_ok + x_bad)
        v = dict(values)
        v[key] = mid
        if root_choice(solve(tree, v, pinned=key)) == base_choice:
            x_ok = mid
        else:
            x_bad = mid
    return 0.5 * (x_ok + x_bad)


def _bounds(prm, lo, hi):
    if lo > hi:
        lo, hi = hi, lo
    if prm["as_p"]:
        lo, hi = max(0.0, lo), min(1.0, hi)
    return lo, hi


def tornado(tree, pct):
    """One-way +/- pct sensitivity on every input; rows sorted by swing (desc), then key."""
    values = tree.base_values()
    base = solve(tree, values)
    bc = root_choice(base)
    rows, skipped = [], []
    for key, prm in tree.params.items():
        b = prm["base"]
        if abs(b) <= EPS:
            skipped.append(key)
            continue
        lo, hi = _bounds(prm, b * (1 - pct / 100.0), b * (1 + pct / 100.0))
        ends = {}
        for tag, x in (("low", lo), ("high", hi)):
            v = dict(values)
            v[key] = x
            res = solve(tree, v, pinned=key)
            ends[tag] = (x, res.root_ev, root_choice(res))
        switches = []
        for tag in ("low", "high"):
            x, _, ch = ends[tag]
            if bc is not None and ch != bc:
                switches.append({"at": _find_switch(tree, key, values, b, x, bc), "to": ch})
        rows.append({"key": key, "base": b, "low": lo, "high": hi,
                     "ev_low": ends["low"][1], "ev_high": ends["high"][1],
                     "choice_low": ends["low"][2], "choice_high": ends["high"][2],
                     "swing": abs(ends["high"][1] - ends["low"][1]), "switch": switches})
    rows.sort(key=lambda r: (-round(r["swing"], 9), r["key"]))
    return {"pct": pct, "ev_base": base.root_ev, "base_choice": bc, "rows": rows, "skipped": skipped}


def sweep(tree, key, a, b, steps):
    """Root EV and root choice as one input runs from a to b in `steps` points."""
    if key not in tree.params:
        raise TreeError("unknown parameter %r (see the tornado table for keys)" % key)
    prm = tree.params[key]
    if prm["as_p"] and not (0.0 <= min(a, b) and max(a, b) <= 1.0):
        raise TreeError("probability range must lie in [0, 1]")
    values = tree.base_values()
    root_labels = [br.label for br in tree.root.branches] if tree.root.kind == "decision" else []
    rows = []
    for i in range(steps):
        x = a + (b - a) * i / (steps - 1) if steps > 1 else a
        v = dict(values)
        v[key] = x
        res = solve(tree, v, pinned=key)
        rows.append({"x": x, "ev": res.root_ev, "choice": root_choice(res),
                     "branch_ev": [res.branch_ev[lab] for lab in root_labels]})
    switches = []
    for r1, r2 in zip(rows, rows[1:]):
        if r1["choice"] != r2["choice"] and r1["choice"] is not None:
            switches.append({"at": _find_switch(tree, key, values, r1["x"], r2["x"], r1["choice"]),
                             "from": r1["choice"], "to": r2["choice"]})
    return {"key": key, "base": prm["base"], "rows": rows, "root_labels": root_labels, "switch": switches}


# --- Monte Carlo -------------------------------------------------------------


def _percentile(sorted_xs, q):
    n = len(sorted_xs)
    if n == 1:
        return sorted_xs[0]
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, n - 1)
    return sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (pos - lo)


def _stats(xs):
    s = sorted(xs)
    return {"mean": sum(s) / len(s), "p10": _percentile(s, 0.10), "p50": _percentile(s, 0.50),
            "p90": _percentile(s, 0.90), "min": s[0], "max": s[-1],
            "p_negative": sum(1 for x in s if x < 0) / len(s)}


def montecarlo(tree, draws, seed):
    if draws < 1:
        raise TreeError("--draws must be >= 1")
    values = tree.base_values()
    base = solve(tree, values)
    ranged = [k for k, p in tree.params.items() if p["range"]]
    rng = random.Random(seed)
    pol, opt, counts = [], [], Counter()
    for _ in range(draws):
        v = dict(values)
        for k in ranged:
            lo, mode, hi = tree.params[k]["range"]
            v[k] = rng.triangular(lo, hi, mode)
        r_opt = solve(tree, v)
        r_pol = solve(tree, v, policy=base.choice)
        opt.append(r_opt.root_ev)
        pol.append(r_pol.root_ev)
        counts[root_choice(r_opt)] += 1
    labels = [b.label for b in tree.root.branches] if tree.root.kind == "decision" else []
    return {"draws": draws, "seed": seed, "ranged": ranged, "base_ev": base.root_ev,
            "policy": policy_lines(tree, base), "base_policy": _stats(pol), "reoptimised": _stats(opt),
            "root_choice_freq": [(lab, counts.get(lab, 0) / draws) for lab in labels],
            "value_of_resolving_inputs": (sum(opt) - sum(pol)) / draws}


# --- rendering ---------------------------------------------------------------


def _f(x, dec):
    return "%.*f" % (dec, x)


def _c(choice):
    """Root choice for display; None when the root is a chance node."""
    return "n/a (root is a chance node)" if choice is None else choice


def _jsonable(obj):
    """Round floats (9 dp) and convert tuples/OrderedDicts so JSON output is clean and stable."""
    if isinstance(obj, float):
        return round(obj, 9)
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    return obj


def _dump(obj):
    print(json.dumps(_jsonable(obj), indent=2, sort_keys=True))


def render_tree(tree, res, values, dec):
    lines = []

    def walk(node, indent):
        pad = "  " * indent
        if node.kind == "decision":
            lines.append("%s[D] %s   EV = %s   choose: %s" % (pad, node.name, _f(res.node_ev[node.path], dec), res.choice[node.path]))
        else:
            lines.append("%s[C] %s   EV = %s" % (pad, node.name, _f(res.node_ev[node.path], dec)))
        for i, b in enumerate(node.branches):
            bits = []
            if node.kind == "chance":
                bits.append("p=%.3f" % res.probs[node.path][i])
            if b.cost_key:
                bits.append("cost %s" % _f(values[b.cost_key], dec))
            if b.node.kind == "terminal":
                bits.append("payoff %s" % _f(values[b.node.value_key], dec))
            mark = "*" if node.kind == "decision" and res.choice[node.path] == b.label else "-"
            lines.append("%s  %s %s  [%s]  EV = %s" % (pad, mark, b.label, ", ".join(bits), _f(res.branch_ev[b.path], dec)))
            if b.node.kind != "terminal":
                walk(b.node, indent + 2)

    if tree.root.kind == "terminal":
        lines.append("[T] payoff %s" % _f(res.root_ev, dec))
    else:
        walk(tree.root, 0)
    return lines


def _header(tree):
    bits = [tree.title or "decision tree"]
    if tree.units:
        bits.append("units: %s" % tree.units)
    return " -- ".join(bits)


def cmd_solve(tree, dec, as_json):
    values = tree.base_values()
    res = solve(tree, values)
    pol = policy_lines(tree, res)
    prof = risk_profile(tree, res, values)
    if as_json:
        out = {"title": tree.title, "units": tree.units, "root_ev": res.root_ev,
               "policy": [{"where": w, "choose": c} for w, c in pol],
               "choices": res.choice, "node_ev": res.node_ev, "branch_ev": res.branch_ev,
               "risk_profile": [{"outcome": v, "probability": p} for v, p in prof],
               "p_loss": sum(p for v, p in prof if v < 0)}
        _dump(out)
        return
    print(_header(tree))
    print("\n".join(render_tree(tree, res, values, dec)))
    print()
    print("Root EV = %s" % _f(res.root_ev, dec))
    if pol:
        print("Optimal policy:")
        for w, c in pol:
            print("  %s: %s" % (w, c))
    print("Risk profile of that policy (net outcome: probability):")
    for v, p in prof:
        print("  %s: %.3f" % (_f(v, dec), p))
    print("  P(net outcome < 0) = %.3f; mean = %s (equals root EV)" % (sum(p for v, p in prof if v < 0), _f(sum(v * p for v, p in prof), dec)))


def cmd_evpi(tree, args, dec, as_json):
    values = tree.base_values()
    unc = uncertainties(tree)
    if args.evsi:
        if args.likelihood:
            with open(args.likelihood, encoding="utf-8") as fh:
                signal = load_signal(json.load(fh))
        elif args.demo:
            signal = load_signal(DEMO_SIGNAL)
        else:
            raise TreeError("--evsi needs --likelihood FILE (or --demo)")
        if args.node:
            signal["uncertainty"] = args.node
        r = evsi(tree, signal, values)
        if as_json:
            _dump(r)
            return
        print(_header(tree))
        print("EVSI -- imperfect signal about %r (signals: %s)" % (r["uncertainty"], ", ".join(s["signal"] for s in r["signals"])))
        print("  Without the signal: best EV %s (%s)" % (_f(r["ev_base"], dec), _c(r["base_choice"])))
        print("  %-14s %-10s %-34s %-16s %s" % ("signal", "P(signal)", "posterior", "best option", "EV"))
        for s in r["signals"]:
            if s["posterior"] is None:
                print("  %-14s %-10s %s" % (s["signal"], "0.000", "(never occurs)"))
                continue
            post = ", ".join("%s %.3f" % (o, p) for o, p in s["posterior"].items())
            print("  %-14s %-10.3f %-34s %-16s %s" % (s["signal"], s["p_signal"], post, _c(s["choice"]), _f(s["ev"], dec)))
        print("  EV with sample information: %s" % _f(r["ev_sample"], dec))
        print("  EVSI = %s - %s = %s" % (_f(r["ev_sample"], dec), _f(r["ev_base"], dec), _f(r["evsi"], dec)))
        share = (100.0 * r["evsi"] / r["evpi"]) if r["evpi"] > EPS else float("nan")
        print("  EVPI = %s -> the signal captures %.0f %% of the value of perfect information" % (_f(r["evpi"], dec), share)
              if r["evpi"] > EPS else "  EVPI = %s (information cannot change the decision)" % _f(r["evpi"], dec))
        print("  Signal cost %s -> net %s -> %s" % (_f(r["cost"], dec), _f(r["net"], dec),
                                                    "WORTH RUNNING (EVSI > cost)" if r["worth_running"] else "not worth running (EVSI <= cost)"))
        if r["evsi"] < -1e-6:
            print("  WARNING: EVSI < 0 -- the tree's probabilities for this uncertainty are not consistent across branches")
        return
    if args.all:
        table = [evpi(tree, n, values) for n in unc]
        if as_json:
            _dump(table)
            return
        print(_header(tree))
        print("EVPI for every uncertainty (base EV %s, %s):" % (_f(table[0]["ev_base"], dec), _c(table[0]["base_choice"])))
        print("  %-24s %6s %12s %12s" % ("uncertainty", "nodes", "EV perfect", "EVPI"))
        for r in table:
            print("  %-24s %6d %12s %12s" % (r["uncertainty"], r["n_nodes"], _f(r["ev_perfect"], dec), _f(r["evpi"], dec)))
        print("  Note: EVPI is meaningful for state-of-the-world uncertainties; a test/signal node's EVPI ignores")
        print("  that its result would also change the probabilities elsewhere in the tree -- use --evsi for tests.")
        return
    r = evpi(tree, args.node, values)
    if as_json:
        _dump(r)
        return
    print(_header(tree))
    print("EVPI -- perfect information about %r (%d chance node%s; prior from %s)"
          % (r["uncertainty"], r["n_nodes"], "" if r["n_nodes"] == 1 else "s", r["prior_from"]))
    print("  Without information: best EV %s (%s)" % (_f(r["ev_base"], dec), _c(r["base_choice"])))
    print("  %-16s %-8s %-18s %s" % ("if known to be", "prior", "best option", "EV"))
    for o in r["outcomes"]:
        print("  %-16s %-8.3f %-18s %s" % (o["outcome"], o["prior"], _c(o["choice"]), _f(o["ev"], dec)))
    print("  EV with perfect information: %s" % _f(r["ev_perfect"], dec))
    print("  EVPI = %s - %s = %s   (ceiling on what any test about %r is worth)"
          % (_f(r["ev_perfect"], dec), _f(r["ev_base"], dec), _f(r["evpi"], dec), r["uncertainty"]))
    if r["evpi"] < -1e-6:
        print("  WARNING: EVPI < 0 -- probabilities for %r are not consistent across branches (check Bayes)" % r["uncertainty"])
    elif r["evpi"] <= 1e-9:
        print("  EVPI = 0: no outcome of %r would change the decision -- do not pay to learn it" % r["uncertainty"])


def cmd_sensitivity(tree, args, dec, as_json):
    if args.param:
        if not args.range:
            raise TreeError("--param needs --range a:b:steps")
        parts = args.range.split(":")
        if len(parts) != 3:
            raise TreeError("--range must be a:b:steps")
        try:
            a, b, steps = float(parts[0]), float(parts[1]), int(parts[2])
        except ValueError:
            raise TreeError("--range must be a:b:steps with numeric a, b and integer steps")
        if steps < 2:
            raise TreeError("--range needs at least 2 steps")
        r = sweep(tree, args.param, a, b, steps)
        if as_json:
            _dump(r)
            return
        prm_is_p = tree.params[r["key"]]["as_p"]
        print(_header(tree))
        print("Sweep %s from %s to %s (%d points; base %s)" % (r["key"], _f(a, 4), _f(b, 4), steps, _f(r["base"], 4)))
        head = "  %-12s %-12s %-18s" % ("value", "root EV", "root choice")
        if r["root_labels"]:
            head += " " + " ".join("%12s" % lab[:12] for lab in r["root_labels"])
        print(head)
        for row in r["rows"]:
            line = "  %-12s %-12s %-18s" % (_f(row["x"], 4), _f(row["ev"], dec), _c(row["choice"]))
            if r["root_labels"]:
                line += " " + " ".join("%12s" % _f(x, dec) for x in row["branch_ev"])
            print(line)
        pfmt = 4 if prm_is_p else dec
        for s in r["switch"]:
            print("  switching point: %s = %s (%s -> %s)" % (r["key"], _f(s["at"], pfmt), s["from"], s["to"]))
        if not r["switch"]:
            print("  no switch of the root choice inside this range")
        return
    r = tornado(tree, args.pct)
    if as_json:
        _dump(r)
        return
    print(_header(tree))
    print("One-way sensitivity: each input -%g %% / +%g %%, others at base. Base EV %s, root choice %s."
          % (r["pct"], r["pct"], _f(r["ev_base"], dec), _c(r["base_choice"])))
    top = max([row["swing"] for row in r["rows"]] or [0.0])
    print("  %-4s %-40s %10s %10s %10s %10s %9s  %-20s %s"
          % ("rank", "input (largest swing first)", "low", "high", "EV(low)", "EV(high)", "swing", "bar", "switching point"))
    for i, row in enumerate(r["rows"], 1):
        bar = "#" * int(round(20 * row["swing"] / top)) if top > EPS else ""
        pfmt = 4 if tree.params[row["key"]]["as_p"] else dec
        sw = "; ".join("%s -> %s" % (_f(s["at"], pfmt), s["to"]) for s in row["switch"]) or "-"
        print("  %-4d %-40s %10s %10s %10s %10s %9s  %-20s %s"
              % (i, row["key"][:40], _f(row["low"], pfmt), _f(row["high"], pfmt), _f(row["ev_low"], dec),
                 _f(row["ev_high"], dec), _f(row["swing"], dec), bar, sw))
    if r["skipped"]:
        print("  skipped (base 0 -> no relative range; use --param KEY --range a:b:steps): %s" % ", ".join(r["skipped"]))
    if r["rows"]:
        print("  Most sensitive input: %s (swing %s)" % (r["rows"][0]["key"], _f(r["rows"][0]["swing"], dec)))


def cmd_montecarlo(tree, args, dec, as_json):
    r = montecarlo(tree, args.draws, args.seed)
    if as_json:
        _dump(r)
        return
    print(_header(tree))
    print("Monte Carlo: %d draws, seed %d, %d ranged input%s%s"
          % (r["draws"], r["seed"], len(r["ranged"]), "" if len(r["ranged"]) == 1 else "s",
             (": " + ", ".join(r["ranged"])) if r["ranged"] else " (no {min,mode,max} ranges given -- degenerate)"))
    print("  Base policy: %s" % "; ".join("%s: %s" % (w, c) for w, c in r["policy"]))
    for label, st in (("EV of the base policy   ", r["base_policy"]), ("EV re-optimised per draw", r["reoptimised"])):
        print("  %s  mean %s  P10 %s  P50 %s  P90 %s  min %s  max %s  P(EV<0) %.3f"
              % (label, _f(st["mean"], dec), _f(st["p10"], dec), _f(st["p50"], dec), _f(st["p90"], dec),
                 _f(st["min"], dec), _f(st["max"], dec), st["p_negative"]))
    if r["root_choice_freq"]:
        print("  Root choice optimal in: " + ", ".join("%s %.1f %%" % (lab, 100 * f) for lab, f in r["root_choice_freq"]))
    print("  Value of resolving all ranged inputs before deciding: %s (mean re-optimised - mean base policy)"
          % _f(r["value_of_resolving_inputs"], dec))


# --- built-in trees ----------------------------------------------------------

# SKILL.md worked example: two-stage R&D bet -- commit USD 20M now, do nothing,
# or run a USD 2M pilot first. Demand prior P(High) = 0.4; the pilot has
# P(Positive | High) = 0.9, P(Positive | Low) = 0.4, so P(Positive) = 0.6,
# P(High | Positive) = 0.6, P(High | Negative) = 0.1 (Bayes). Payoffs in USD M NPV.
DEMO_TREE = {
    "title": "Two-stage R&D bet: pilot before the USD 20M commitment?",
    "units": "USD M, NPV",
    "variables": {
        "v_high": {"min": 45, "mode": 60, "max": 80},
        "v_low": {"min": 0, "mode": 5, "max": 12},
        "c_dev": {"min": 18, "mode": 20, "max": 25},
    },
    "root": {"type": "decision", "name": "Go / no-go", "branches": [
        {"label": "Commit now", "cost": "c_dev", "node": {"type": "chance", "name": "Demand", "branches": [
            {"label": "High", "p": 0.4, "value": "v_high"},
            {"label": "Low", "value": "v_low"}]}},
        {"label": "Do nothing", "value": 0},
        {"label": "Pilot first", "cost": 2, "node": {"type": "chance", "name": "Pilot result", "branches": [
            {"label": "Positive", "p": 0.6, "node": {"type": "decision", "name": "After positive pilot", "branches": [
                {"label": "Commit", "cost": "c_dev", "node": {"type": "chance", "name": "Demand", "branches": [
                    {"label": "High", "p": 0.6, "value": "v_high"},
                    {"label": "Low", "value": "v_low"}]}},
                {"label": "Stop", "value": 0}]}},
            {"label": "Negative", "node": {"type": "decision", "name": "After negative pilot", "branches": [
                {"label": "Commit", "cost": "c_dev", "node": {"type": "chance", "name": "Demand", "branches": [
                    {"label": "High", "p": 0.1, "value": "v_high"},
                    {"label": "Low", "value": "v_low"}]}},
                {"label": "Stop", "value": 0}]}}]}}]},
}

DEMO_SIGNAL = {
    "uncertainty": "Demand", "signals": ["Positive", "Negative"], "cost": 2,
    "likelihood": {"High": {"Positive": 0.9, "Negative": 0.1},
                   "Low": {"Positive": 0.4, "Negative": 0.6}},
}

# Textbook oil-wildcatter tree (Raiffa 1968 style): drill (cost 70) or not;
# P(oil) = 0.3, gross payoff 270 if oil, 0 if dry. Units: USD k.
OIL_TREE = {
    "title": "Oil wildcatter (textbook)", "units": "USD k",
    "root": {"type": "decision", "name": "Drill?", "branches": [
        {"label": "Drill", "cost": 70, "node": {"type": "chance", "name": "Oil", "branches": [
            {"label": "Oil", "p": 0.3, "value": 270},
            {"label": "Dry", "p": 0.7, "value": 0}]}},
        {"label": "Don't drill", "value": 0}]},
}

# Seismic survey: P(Favourable | Oil) = 0.9, P(Favourable | Dry) = 0.2, cost 10.
OIL_SEISMIC = {
    "uncertainty": "Oil", "signals": ["Favourable", "Unfavourable"], "cost": 10,
    "likelihood": {"Oil": {"Favourable": 0.9, "Unfavourable": 0.1},
                   "Dry": {"Favourable": 0.2, "Unfavourable": 0.8}},
}


# --- selftest ----------------------------------------------------------------


def run_selftest():
    """Hand-verified assertions (see the comments for the by-hand arithmetic)."""
    n = [0]

    def check(name, got, want, tol=1e-9):
        ok = (got == want) if isinstance(want, str) or want is None else abs(got - want) <= tol
        n[0] += 1
        shown = "%r" % (got,) if isinstance(want, str) or want is None else "%.6f (expected %.6f)" % (got, want)
        print("%s  %s: %s" % ("PASS" if ok else "FAIL", name, shown))
        if not ok:
            print("SELFTEST FAILED at: %s" % name, file=sys.stderr)
            sys.exit(1)

    def expect_error(name, fn):
        n[0] += 1
        try:
            fn()
        except TreeError as exc:
            print("PASS  %s: rejected (%s)" % (name, str(exc)[:70]))
            return
        print("FAIL  %s: no error raised" % name)
        sys.exit(1)

    # -- 1. Oil wildcatter: EV(Drill) = 0.3*270 - 70 = 81 - 70 = 11 > 0 = don't drill.
    oil = parse_tree(OIL_TREE)
    res = solve(oil)
    check("oil: chance node EV = 0.3*270", res.node_ev["Drill"], 81.0)
    check("oil: EV(Drill) = 81 - 70", res.branch_ev["Drill"], 11.0)
    check("oil: root EV", res.root_ev, 11.0)
    check("oil: root choice", root_choice(res), "Drill")
    prof = dict(risk_profile(oil, res))
    check("oil: risk profile P(net = 200)", prof[200.0], 0.3)
    check("oil: risk profile P(net = -70)", prof[-70.0], 0.7)

    # -- 2. EVPI: know Oil -> drill (200); know Dry -> don't (0): 0.3*200 = 60; EVPI = 60 - 11 = 49.
    e = evpi(oil)
    check("oil: top-level uncertainty auto-detected", e["uncertainty"], "Oil")
    check("oil: EV with perfect information", e["ev_perfect"], 60.0)
    check("oil: EVPI = 60 - 11", e["evpi"], 49.0)
    check("oil: EVPI >= 0", 1.0 if e["evpi"] >= 0 else 0.0, 1.0)

    # -- 3. EVSI with the seismic survey (by hand):
    #    P(F) = 0.3*0.9 + 0.7*0.2 = 0.41;  P(Oil|F) = 0.27/0.41;  drill after F: 0.27/0.41*270 - 70 = 107.805
    #    P(U) = 0.59;  P(Oil|U) = 0.03/0.59;  drill after U: 13.73 - 70 < 0 -> don't drill (0)
    #    EV_SI = 0.41 * 107.805 = 0.27*270 - 0.41*70 = 72.9 - 28.7 = 44.2;  EVSI = 44.2 - 11 = 33.2 <= 49.
    s = evsi(oil, load_signal(OIL_SEISMIC))
    check("oil: P(Favourable) = 0.41", s["signals"][0]["p_signal"], 0.41)
    check("oil: P(Oil | Favourable) = 0.27/0.41", s["signals"][0]["posterior"]["Oil"], 0.27 / 0.41)
    check("oil: choice after Unfavourable", s["signals"][1]["choice"], "Don't drill")
    check("oil: EV with sample information = 44.2", s["ev_sample"], 44.2)
    check("oil: EVSI = 33.2", s["evsi"], 33.2)
    check("oil: EVSI net of survey cost 10", s["net"], 23.2)
    check("oil: EVSI <= EVPI", 1.0 if s["evsi"] <= s["evpi"] + EPS else 0.0, 1.0)

    # -- 4. Rejections.
    bad = json.loads(json.dumps(OIL_TREE))
    bad["root"]["branches"][0]["node"]["branches"][1]["p"] = 0.6
    expect_error("probabilities 0.3 + 0.6 != 1 rejected", lambda: parse_tree(bad))
    bad2 = json.loads(json.dumps(OIL_TREE))
    bad2["root"]["branches"][1]["p"] = 0.5
    expect_error("probability on a decision branch rejected", lambda: parse_tree(bad2))
    bad3 = json.loads(json.dumps(OIL_TREE))
    bad3["root"]["branches"][0]["cost"] = "c_missing"
    expect_error("unknown variable rejected", lambda: parse_tree(bad3))
    bad_sig = json.loads(json.dumps(OIL_SEISMIC))
    bad_sig["likelihood"]["Oil"]["Favourable"] = 0.5
    expect_error("likelihood row not summing to 1 rejected", lambda: load_signal(bad_sig))

    # -- 5. Complement branch: omit p on Dry -> 0.7 inferred; same answer.
    comp = json.loads(json.dumps(OIL_TREE))
    del comp["root"]["branches"][0]["node"]["branches"][1]["p"]
    rc = solve(parse_tree(comp))
    check("complement branch p = 1 - 0.3", rc.probs["Drill"][1], 0.7)
    check("complement branch: same root EV", rc.root_ev, 11.0)

    # -- 6. Tornado (+/-20 %) and the switching probability: EV(Drill) = 270p - 70 = 0 at p = 70/270.
    #    p(oil) in [0.24, 0.36]: EV(low) = max(-5.2, 0) = 0, EV(high) = 27.2 -> swing 27.2 (switch inside range)
    #    payoff in [216, 324]: EV(low) = 0, EV(high) = 27.2 -> swing 27.2;  cost in [56, 84]: 25 / 0 -> swing 25.
    #    With Dry stated explicitly (0.7) it is an input of its own: p(dry) in [0.56, 0.84] pins p(dry) and
    #    rescales p(oil) to 0.44 / 0.16 -> EV 48.8 / 0 -> swing 48.8 (why the residual outcome should omit p).
    t = tornado(oil, 20.0)
    rows = {r["key"]: r for r in t["rows"]}
    check("tornado: p:Drill/Oil swing", rows["p:Drill/Oil"]["swing"], 27.2, 1e-9)
    check("tornado: p:Drill/Dry pinned, sibling rescaled (0.44*270-70)", rows["p:Drill/Dry"]["ev_low"], 48.8, 1e-9)
    check("tornado: value:Drill/Oil swing", rows["value:Drill/Oil"]["swing"], 27.2, 1e-9)
    check("tornado: cost:Drill swing", rows["cost:Drill"]["swing"], 25.0, 1e-9)
    check("tornado: switching probability p(oil) = 70/270", rows["p:Drill/Oil"]["switch"][0]["at"], 70.0 / 270.0, 1e-6)
    check("tornado: switches to", rows["p:Drill/Oil"]["switch"][0]["to"], "Don't drill")
    tc = tornado(parse_tree(comp), 20.0)          # Dry as the complement: p(oil) is the only probability input
    check("tornado (complement tree): ranking, tie broken by key", tc["rows"][0]["key"], "p:Drill/Oil")
    check("tornado (complement tree): second row", tc["rows"][1]["key"], "value:Drill/Oil")
    check("tornado (complement tree): third row", tc["rows"][2]["key"], "cost:Drill")
    check("tornado (complement tree): zero payoffs skipped", float(len(tc["skipped"])), 2.0)
    sw = sweep(oil, "p:Drill/Oil", 0.0, 1.0, 11)
    check("sweep: switching point p(oil) = 70/270", sw["switch"][0]["at"], 70.0 / 270.0, 1e-6)

    # -- 7. Seeded Monte Carlo is reproducible; triangular(200, 270, 400) has mean 290,
    #    so the base-policy EV averages about 0.3*290 - 70 = 17.
    mc_tree = json.loads(json.dumps(OIL_TREE))
    mc_tree["root"]["branches"][0]["node"]["branches"][0]["value"] = {"min": 200, "mode": 270, "max": 400}
    mct = parse_tree(mc_tree)
    m1, m2 = montecarlo(mct, 3000, 42), montecarlo(mct, 3000, 42)
    check("montecarlo: seeded runs identical (P50)", m1["base_policy"]["p50"], m2["base_policy"]["p50"], 0.0)
    check("montecarlo: seeded runs identical (mean)", m1["reoptimised"]["mean"], m2["reoptimised"]["mean"], 0.0)
    check("montecarlo: P10 <= P50", 1.0 if m1["base_policy"]["p10"] <= m1["base_policy"]["p50"] else 0.0, 1.0)
    check("montecarlo: P50 <= P90", 1.0 if m1["base_policy"]["p50"] <= m1["base_policy"]["p90"] else 0.0, 1.0)
    check("montecarlo: mean base-policy EV ~ 17", m1["base_policy"]["mean"], 17.0, 1.5)
    m3 = montecarlo(mct, 3000, 7)
    check("montecarlo: a different seed changes the draw", 1.0 if m3["base_policy"]["p50"] != m1["base_policy"]["p50"] else 0.0, 1.0)

    # -- 8. SKILL.md worked example (by hand): Commit now = 0.4*60 + 0.6*5 - 20 = 7;
    #    Pilot: after Positive commit = 0.6*60 + 0.4*5 - 20 = 18, after Negative commit = -9.5 -> stop 0;
    #    EV(Pilot) = 0.6*18 - 2 = 8.8.  EVPI(Demand) = 0.4*40 + 0.6*0 - 8.8 = 7.2.
    #    Base tree (pilot dropped): EV 7, EVPI 9; EVSI = 0.6*18 + 0.4*0 - 7 = 3.8, net of cost 2 = 1.8 = 8.8 - 7.
    demo = parse_tree(DEMO_TREE)
    d = solve(demo)
    check("demo: EV(Commit now) = 7", d.branch_ev["Commit now"], 7.0)
    check("demo: EV(Pilot first) = 8.8", d.branch_ev["Pilot first"], 8.8)
    check("demo: root EV", d.root_ev, 8.8)
    check("demo: root choice", root_choice(d), "Pilot first")
    check("demo: after positive pilot", d.choice["Pilot first/Positive"], "Commit")
    check("demo: after negative pilot", d.choice["Pilot first/Negative"], "Stop")
    dp = dict(risk_profile(demo, d))
    check("demo: risk profile P(net = 38)", dp[38.0], 0.36)
    check("demo: risk profile P(net = -17)", dp[-17.0], 0.24)
    check("demo: risk profile P(net = -2)", dp[-2.0], 0.4)
    de = evpi(demo)
    check("demo: EVPI(Demand) on the full tree = 16 - 8.8", de["evpi"], 7.2)
    base = parse_tree(DEMO_TREE, drop=("Pilot first",))
    be = evpi(base)
    check("demo: base tree EV = 7", be["ev_base"], 7.0)
    check("demo: base tree EVPI = 9", be["evpi"], 9.0)
    bs = evsi(base, load_signal(DEMO_SIGNAL))
    check("demo: P(Positive) = 0.6", bs["signals"][0]["p_signal"], 0.6)
    check("demo: P(High | Positive) = 0.6", bs["signals"][0]["posterior"]["High"], 0.6)
    check("demo: P(High | Negative) = 0.1", bs["signals"][1]["posterior"]["High"], 0.1)
    check("demo: EVSI = 3.8", bs["evsi"], 3.8)
    check("demo: EVSI net of pilot cost = 1.8", bs["net"], 1.8)
    check("demo: hand-built pilot branch agrees with Bayes (7 + 1.8 = 8.8)", be["ev_base"] + bs["net"], d.branch_ev["Pilot first"])
    dt = tornado(demo, 20.0)
    drows = {r["key"]: r for r in dt["rows"]}
    check("demo tornado: most sensitive input", dt["rows"][0]["key"], "var:v_high")
    check("demo tornado: v_high swing (13.12 - 4.48)", drows["var:v_high"]["swing"], 8.64, 1e-9)
    check("demo tornado: prior switch at (8.8 + 15)/55", drows["p:Commit now/High"]["switch"][0]["at"], 23.8 / 55.0, 1e-6)
    check("demo tornado: prior switch to", drows["p:Commit now/High"]["switch"][0]["to"], "Commit now")
    check("demo tornado: zero-base payoffs skipped", float(len(dt["skipped"])), 3.0)

    print("selftest OK (%d checks)" % n[0])
    return 0


# --- CLI ---------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(description="Decision-tree roll-back, EVPI/EVSI, tornado sensitivity and seeded Monte Carlo.")
    parser.add_argument("--selftest", action="store_true", help="run the built-in hand-verified checks and exit")
    sub = parser.add_subparsers(dest="command")
    specs = [
        ("solve", "roll back to expected values; optimal policy; risk profile"),
        ("evpi", "expected value of perfect information (or --evsi for an imperfect signal)"),
        ("sensitivity", "one-way +/- pct tornado with switching points, or --param/--range sweep"),
        ("montecarlo", "seeded Monte Carlo over {min,mode,max} input ranges"),
    ]
    for name, helptext in specs:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--file", help="tree JSON file")
        p.add_argument("--demo", action="store_true", help="use the built-in SKILL.md worked example")
        p.add_argument("--drop", action="append", default=[], metavar="LABEL", help="remove a root branch before solving (repeatable)")
        p.add_argument("--json", action="store_true", help="JSON output")
        p.add_argument("--decimals", type=int, default=2, help="decimals for money-like values (default 2)")
        if name == "evpi":
            p.add_argument("--node", help="uncertainty (chance-node name); default: the top-level one")
            p.add_argument("--all", action="store_true", help="EVPI table for every uncertainty")
            p.add_argument("--evsi", action="store_true", help="EVSI for an imperfect signal (needs --likelihood)")
            p.add_argument("--likelihood", help="signal JSON file: P(signal | outcome) rows + cost")
        if name == "sensitivity":
            p.add_argument("--pct", type=float, default=20.0, help="one-way +/- percentage (default 20)")
            p.add_argument("--param", help="single input key to sweep, e.g. 'p:Drill/Oil'")
            p.add_argument("--range", help="a:b:steps for --param")
        if name == "montecarlo":
            p.add_argument("--draws", type=int, default=10000)
            p.add_argument("--seed", type=int, default=42)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.command:
        parser.error("choose a command: solve | evpi | sensitivity | montecarlo  (or --selftest)")
    try:
        if args.demo:
            tree = parse_tree(DEMO_TREE, tuple(args.drop))
        elif args.file:
            tree = load_tree(args.file, tuple(args.drop))
        else:
            parser.error("pass --file tree.json or --demo")
        dec = max(0, args.decimals)
        if args.command == "solve":
            cmd_solve(tree, dec, args.json)
        elif args.command == "evpi":
            cmd_evpi(tree, args, dec, args.json)
        elif args.command == "sensitivity":
            cmd_sensitivity(tree, args, dec, args.json)
        else:
            cmd_montecarlo(tree, args, dec, args.json)
    except (OSError, ValueError) as exc:      # TreeError is a ValueError; json errors too
        print("error: %s" % exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
