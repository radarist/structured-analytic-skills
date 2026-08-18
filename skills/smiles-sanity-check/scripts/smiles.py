#!/usr/bin/env python3
"""smiles.py -- SMILES sanity checker (companion tool for the smiles-sanity-check skill).

Zero-dependency structural tripwire for SMILES strings, implementing the checks
listed in ../SKILL.md as real code:

  1. brackets       -- balanced parentheses, no stray/unterminated square brackets
  2. atoms          -- every atom token on the SMILES whitelist (organic subset
                       unbracketed; any element plus isotope/charge/chirality/
                       H-count/class modifiers inside brackets)
  3. bonds          -- bond/stereo tokens (- = # $ : / \\) legally placed,
                       no back-to-back bond symbols, sane '.' usage
  4. ring-closures  -- every ring digit 0-9 (or %NN) opened exactly once and
                       closed exactly once
  5. valence        -- simple bond-order sanity limits for common unbracketed
                       atoms (C, N, O, S, P, halogens, B + aromatic b c n o p s)

This is a SANITY CHECKER, not a full chemistry toolkit: it catches copy-paste
corruption and hallucinated syntax. It does NOT validate chemistry semantics
(realistic tautomers, correct stereochemistry, exotic bonding) -- use RDKit
for that.

Usage:
    python3 smiles.py check 'CC(=O)Oc1ccccc1C(=O)O'
    python3 smiles.py check --file molecules.smi   # one SMILES per line
    python3 smiles.py --selftest

Exit code: 0 if every SMILES is VALID (or selftest passes), 1 otherwise.
"""

import argparse
import re
import sys

# --- Reference data ----------------------------------------------------------

# Full periodic table, used to validate bracket-atom symbols like [Fe+2].
ELEMENTS = frozenset((
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
    "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
))

ORGANIC_SUBSET = frozenset(("B", "C", "N", "O", "P", "S", "F", "Cl", "Br", "I"))
AROMATIC_SUBSET = frozenset(("b", "c", "n", "o", "p", "s"))
EXTENDED_AROMATIC = frozenset(("se", "as"))  # valid bracketed only, per SKILL.md

# Bond/stereo tokens and the bond order each contributes to the valence sum.
# `/` and `\` are directional single bonds (double-bond stereochemistry);
# `:` is an explicit aromatic bond, counted as 1 for this sanity model.
BOND_ORDERS = {"-": 1, "=": 2, "#": 3, "$": 4, ":": 1, "/": 1, "\\": 1}

# Allowed bond-order sums for UNBRACKETED atoms (bracket atoms carry explicit
# H/charge and are skipped). Aromatic bonds count as 1: this is a sigma-bond
# tripwire, not an electron-counting model. A sum above the largest allowed
# value, or between allowed values (N/P/S only), is flagged.
ALLOWED_VALENCES = {
    "B": (3,), "C": (4,), "N": (3, 5), "O": (2,), "P": (3, 5),
    "S": (2, 4, 6), "F": (1,), "Cl": (1,), "Br": (1,), "I": (1,),
    # Aromatic: fused-ring junction c reaches 3; c(=O) as in caffeine reaches 4.
    "b": (3,), "c": (4,), "n": (4,), "o": (3,), "p": (4,), "s": (4,),
}

ATOM_NAMES = {
    "B": "boron", "C": "carbon", "N": "nitrogen", "O": "oxygen",
    "P": "phosphorus", "S": "sulfur", "F": "fluorine", "Cl": "chlorine",
    "Br": "bromine", "I": "iodine",
    "b": "aromatic boron", "c": "aromatic carbon", "n": "aromatic nitrogen",
    "o": "aromatic oxygen", "p": "aromatic phosphorus", "s": "aromatic sulfur",
}

# Bracket-atom grammar: [isotope] symbol [chirality] [H-count] [charge] [:class]
# e.g. [13C], [C@H], [nH], [NH4+], [O-], [Fe+2], [C:1], [*].
BRACKET_RE = re.compile(
    r"^(\d{1,3})?"                         # optional isotope prefix
    r"(\*|[A-Z][a-z]?|se|as|[bcnops])"     # element / wildcard / aromatic symbol
    r"(@{1,2})?"                           # optional chirality @ or @@
    r"(H\d*)?"                             # optional attached-H count
    r"([+-](?:\d+|[+-])?)?"                # optional charge: + ++ +2 - -- -2
    r"(:\d+)?$"                            # optional atom-map class
)

CHECK_ORDER = ("brackets", "atoms", "bonds", "ring-closures", "valence")

SCOPE_NOTE = ("NOTE: this is a sanity checker, not a full chemistry toolkit -- "
              "VALID means the string passes structural syntax and simple valence "
              "tripwires, not that the molecule is chemically sensible "
              "(use RDKit/OpenBabel for real validation).")


class Token:
    """One lexical unit of a SMILES string."""

    __slots__ = ("kind", "text", "pos", "symbol", "aromatic", "bracketed")

    def __init__(self, kind, text, pos, symbol=None, aromatic=False, bracketed=False):
        self.kind = kind            # atom | bond | ring | lparen | rparen | dot
        self.text = text            # raw text of the token
        self.pos = pos              # 0-based char offset in the original string
        self.symbol = symbol        # atom symbol (atom tokens only)
        self.aromatic = aromatic    # lowercase aromatic atom
        self.bracketed = bracketed  # came from [...]


# --- Tokenizer -----------------------------------------------------------------

def parse_bracket(content):
    """Validate bracket-atom content. Return (symbol, aromatic, error_or_None)."""
    m = BRACKET_RE.match(content) if content else None
    if not m:
        return None, False, ("expected [isotope]<element>[@/@@][Hn][charge][:class], "
                             f"got '[{content}]'")
    symbol = m.group(2)
    if symbol == "*":
        return symbol, False, None
    if symbol in AROMATIC_SUBSET or symbol in EXTENDED_AROMATIC:
        return symbol, True, None
    if symbol not in ELEMENTS:
        return symbol, False, f"'{symbol}' is not an element symbol"
    return symbol, False, None


def tokenize(smiles):
    """Split a SMILES string into tokens.

    Returns (tokens, errors) where errors are (check_name, message) pairs.
    Tokenization continues past most errors so all bad atoms get reported.
    """
    tokens, errors = [], []
    i, n = 0, len(smiles)
    while i < n:
        ch = smiles[i]
        if ch == "[":
            j = smiles.find("]", i + 1)
            if j == -1:
                errors.append(("brackets", f"unterminated '[' at char {i}: no matching ']'"))
                break
            symbol, aromatic, err = parse_bracket(smiles[i + 1:j])
            if err:
                errors.append(("atoms", f"bad bracket atom at char {i}: {err}"))
            tokens.append(Token("atom", smiles[i:j + 1], i, symbol=symbol or "?",
                                aromatic=aromatic, bracketed=True))
            i = j + 1
        elif ch == "]":
            errors.append(("brackets", f"stray ']' at char {i} with no opening '['"))
            i += 1
        elif ch == "(":
            tokens.append(Token("lparen", ch, i)); i += 1
        elif ch == ")":
            tokens.append(Token("rparen", ch, i)); i += 1
        elif ch == ".":
            tokens.append(Token("dot", ch, i)); i += 1
        elif ch in BOND_ORDERS:
            tokens.append(Token("bond", ch, i)); i += 1
        elif ch.isdigit():
            tokens.append(Token("ring", ch, i)); i += 1
        elif ch == "%":
            if smiles[i + 1:i + 3].isdigit() and len(smiles[i + 1:i + 3]) == 2:
                tokens.append(Token("ring", smiles[i:i + 3], i)); i += 3
            else:
                errors.append(("ring-closures",
                               f"bad ring token at char {i}: '%' must be followed by two digits"))
                i += 1
        elif smiles[i:i + 2] in ("Cl", "Br"):      # two-letter organic subset
            tokens.append(Token("atom", smiles[i:i + 2], i, symbol=smiles[i:i + 2])); i += 2
        elif ch in ORGANIC_SUBSET:                 # single-letter organic subset
            tokens.append(Token("atom", ch, i, symbol=ch)); i += 1
        elif ch in AROMATIC_SUBSET:
            tokens.append(Token("atom", ch, i, symbol=ch, aromatic=True)); i += 1
        elif ch.isalpha():                         # unknown letter run, e.g. 'Xz'
            j = i
            while j < n and smiles[j].isalpha():
                j += 1
            errors.append(("atoms",
                           f"atom '{smiles[i:j]}' at char {i} is not on the SMILES whitelist "
                           "(unbracketed: B C N O P S F Cl Br I b c n o p s; others need [brackets])"))
            i = j
        else:
            errors.append(("atoms",
                           f"unexpected character {ch!r} at char {i} is not SMILES syntax"))
            i += 1
    return tokens, errors


# --- Individual checks -----------------------------------------------------------

def check_brackets(tokens):
    """Paren balance + sane branch placement (square brackets are tokenizer-level)."""
    depth, first_open = 0, None
    for k, t in enumerate(tokens):
        if t.kind == "lparen":
            if k == 0 or tokens[k - 1].kind in ("dot", "lparen"):
                return False, f"'(' at char {t.pos} has no preceding atom to branch from"
            if k + 1 < len(tokens) and tokens[k + 1].kind == "rparen":
                return False, f"empty branch '()' at char {t.pos}"
            if depth == 0:
                first_open = t.pos
            depth += 1
        elif t.kind == "rparen":
            depth -= 1
            if depth < 0:
                return False, f"unbalanced parentheses: ')' at char {t.pos} has no matching '('"
    if depth > 0:
        return False, f"unbalanced parentheses: '(' at char {first_open} is never closed"
    return True, "parentheses balanced, no stray brackets"


def check_bonds(tokens):
    """Bond/stereo token placement: no back-to-back bonds, atoms on both sides."""
    n = len(tokens)
    for k, t in enumerate(tokens):
        prev = tokens[k - 1].kind if k else None
        nxt = tokens[k + 1].kind if k + 1 < n else None
        if t.kind == "bond":
            if prev is None:
                return False, f"bond token '{t.text}' at char {t.pos} has no atom before it"
            if prev == "bond":
                return False, (f"back-to-back bond tokens at char {t.pos}: "
                               f"'{tokens[k - 1].text}{t.text}'")
            if prev == "dot":
                return False, f"bond token '{t.text}' at char {t.pos} follows '.' (nothing to bond)"
            if nxt in (None, "bond", "rparen", "dot"):
                return False, f"bond token '{t.text}' at char {t.pos} has no atom after it"
        elif t.kind == "dot":
            if prev in (None, "dot") or nxt in (None, "dot", "rparen"):
                return False, f"'.' at char {t.pos} does not separate two fragments"
    return True, "all bond/stereo tokens legally placed"


def structural_pass(tokens):
    """One pass over the token stream computing per-atom bond-order sums and
    ring-closure pairing errors. Returns (atoms, sums, ring_errors)."""
    atoms, sums = [], {}
    prev = None            # index of the atom a new atom/ring closure attaches to
    stack = []             # branch stack of atom indices
    pending = None         # bond order waiting for its right-hand atom
    open_rings = {}        # digit -> (atom_index, pending_order_or_None, pos)
    ring_errors = []
    for t in tokens:
        if t.kind == "atom":
            atoms.append(t)
            sums[len(atoms) - 1] = 0
            if prev is not None:
                order = pending if pending is not None else 1
                sums[prev] += order
                sums[len(atoms) - 1] += order
            pending = None
            prev = len(atoms) - 1
        elif t.kind == "lparen":
            stack.append(prev)
            pending = None
        elif t.kind == "rparen":
            prev = stack.pop() if stack else None
            pending = None
        elif t.kind == "dot":
            prev = None
            pending = None
        elif t.kind == "bond":
            pending = BOND_ORDERS[t.text]
        elif t.kind == "ring":
            digit = t.text if len(t.text) == 1 else t.text[1:]
            if prev is None:
                ring_errors.append(f"ring digit {t.text} at char {t.pos} has no atom to open on")
            elif digit in open_rings:
                other, open_order, _ = open_rings.pop(digit)
                order = pending if pending is not None else (open_order or 1)
                sums[other] += order
                sums[prev] += order
                pending = None
            else:
                open_rings[digit] = (prev, pending, t.pos)
                pending = None
    for digit, (_, _, pos) in sorted(open_rings.items()):
        ring_errors.append(f"ring digit {digit} opened at char {pos} but never closed")
    return atoms, sums, ring_errors


def check_valence(atoms, sums):
    """Bond-order sanity limits for unbracketed organic-subset atoms.

    Only an explicit bond-order sum ABOVE the element's highest normal valence
    is an error. A sum that falls between two normal valences is legal: per
    OpenSMILES 3.1.5, "if that sum is equal to a known valence for the element
    or is greater than any known valence then the implicit hydrogen count is 0.
    Otherwise the implicit hydrogen count is the difference between that sum and
    the next highest known valence" -- i.e. the atom simply takes implicit
    hydrogens up to the next valence. Flagging those as invalid rejects
    perfectly good SMILES: CS(C)C (sulfur sum 3, takes 1 H to reach 4) and
    CP(C)(C)C (phosphorus sum 4, takes 1 H to reach 5) are both valid and are
    parsed by RDKit. SKILL.md states the correct rule -- "must not exceed" --
    and this function now implements it.
    """
    for idx, t in enumerate(atoms):
        if t.bracketed or t.symbol not in ALLOWED_VALENCES:
            continue
        allowed = ALLOWED_VALENCES[t.symbol]
        total = sums[idx]
        name = ATOM_NAMES.get(t.symbol, t.symbol)
        if total > allowed[-1]:
            return False, (f"{name} ({t.symbol}) at char {t.pos}: bond-order sum "
                           f"{total} exceeds max valence {allowed[-1]}")
    return True, f"{len(atoms)} atom(s) within bond-order limits"


# --- Driver ----------------------------------------------------------------------

def check_smiles(smiles):
    """Run all checks. Returns a list of (check_name, ok, detail) in CHECK_ORDER;
    ok is True/False, or None when a check could not run (tokenization failed)."""
    tokens, tok_errors = tokenize(smiles)
    if tok_errors:
        by_check = {}
        for name, msg in tok_errors:
            by_check.setdefault(name, []).append(msg)
        return [(name,
                 False if name in by_check else None,
                 "; ".join(by_check[name]) if name in by_check
                 else "skipped: tokenization failed")
                for name in CHECK_ORDER]
    if not any(t.kind == "atom" for t in tokens):
        return [(name, False if name == "atoms" else None,
                 "no atoms found (empty SMILES)" if name == "atoms"
                 else "skipped: nothing to check")
                for name in CHECK_ORDER]

    results = {}
    results["brackets"] = check_brackets(tokens)
    symbols = list(dict.fromkeys(t.symbol for t in tokens if t.kind == "atom"))
    results["atoms"] = (True, f"{len(symbols)} unique atom symbol(s), all on whitelist: "
                              + ", ".join(symbols))
    results["bonds"] = check_bonds(tokens)
    atoms, sums, ring_errors = structural_pass(tokens)
    if ring_errors:
        results["ring-closures"] = (False, "; ".join(ring_errors))
    else:
        digits = [t.text for t in tokens if t.kind == "ring"]
        results["ring-closures"] = (True, "no ring digits present" if not digits
                                    else f"all ring digits paired ({', '.join(digits)})")
    results["valence"] = check_valence(atoms, sums)
    return [(name, *results[name]) for name in CHECK_ORDER]


def report(smiles):
    """Print the per-check verdict block for one SMILES. Returns True if VALID."""
    print(f"SMILES: {smiles}")
    results = check_smiles(smiles)
    for name, ok, detail in results:
        verdict = "VALID  " if ok else ("INVALID" if ok is False else "SKIP   ")
        print(f"  {verdict} {name} -- {detail}")
    valid = all(ok for _, ok, _ in results)
    print(f"RESULT: {'VALID' if valid else 'INVALID'}")
    return valid


# --- Selftest ----------------------------------------------------------------------

# Hand-verified cases: good molecules must pass all five checks; bad strings must
# fail with the named check. Valences verified by hand, e.g. C(F)(F)(F)(F)F has a
# central carbon with 5 single bonds (bond-order sum 5 > carbon's max 4).
SELFTEST_CASES = [
    # (label, SMILES, expect_valid, expected_failing_check_or_None)
    ("aspirin", "CC(=O)Oc1ccccc1C(=O)O", True, None),
    ("caffeine", "Cn1cnc2c1c(=O)n(C)c(=O)n2C", True, None),
    ("ethanol", "CCO", True, None),
    ("benzene (aromatic)", "c1ccccc1", True, None),
    ("benzene (Kekule)", "C1=CC=CC=C1", True, None),
    ("unbalanced ring digit", "C1CC", False, "ring-closures"),
    ("pentavalent carbon", "C(F)(F)(F)(F)F", False, "valence"),
    ("unbalanced parens", "CC(C", False, "brackets"),
    # Regression: an explicit bond-order sum BETWEEN two normal valences is
    # legal -- OpenSMILES 3.1.5 fills the gap with implicit hydrogens. A checker
    # that tests set membership instead of "exceeds the maximum" rejects these
    # two, and RDKit parses both. See check_valence().
    ("sulfur sum 3 (takes 1 implicit H to 4)", "CS(C)C", True, None),
    ("phosphorus sum 4 (takes 1 implicit H to 5)", "CP(C)(C)C", True, None),
    ("sulfone, sulfur sum 6", "CS(=O)(=O)C", True, None),
    # ... while a genuine over-valence is still caught.
    ("trivalent oxygen", "CO(C)C", False, "valence"),
    ("hexavalent carbon", "C(C)(C)(C)(C)C", False, "valence"),
]


def selftest():
    passed = 0
    for label, smiles, expect_valid, expect_check in SELFTEST_CASES:
        results = check_smiles(smiles)
        valid = all(ok for _, ok, _ in results)
        failed = {name for name, ok, _ in results if ok is False}
        ok_case = (valid == expect_valid
                   and (expect_valid or expect_check in failed))
        if ok_case:
            passed += 1
            extra = "" if expect_valid else f" (failed check: {expect_check})"
            print(f"PASS {label}: {'VALID' if valid else 'INVALID'} as expected{extra} [{smiles}]")
        else:
            got = ", ".join(f"{n}={'INVALID' if o is False else 'VALID'}" for n, o, _ in results)
            print(f"FAIL {label}: expected {'VALID' if expect_valid else 'INVALID ' + expect_check}"
                  f", got {got} [{smiles}]")
    total = len(SELFTEST_CASES)
    print(f"SELFTEST: {passed}/{total} checks passed")
    return 0 if passed == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="SMILES sanity checker -- structural tripwire, not a chemistry toolkit.")
    ap.add_argument("--selftest", action="store_true",
                    help="run built-in worked examples and exit")
    sub = ap.add_subparsers(dest="cmd")
    cp = sub.add_parser("check", help="check one SMILES string or a file of SMILES")
    cp.add_argument("smiles", nargs="?", help="SMILES string to check")
    cp.add_argument("--file", help="path to a file with one SMILES per line")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.cmd == "check":
        targets = []
        if args.file:
            with open(args.file, "r", encoding="utf-8") as fh:
                targets = [ln.strip() for ln in fh
                           if ln.strip() and not ln.startswith("#")]
        elif args.smiles:
            targets = [args.smiles]
        else:
            cp.error("provide a SMILES string or --file PATH")
        n_valid = 0
        for i, smi in enumerate(targets):
            if i:
                print()
            n_valid += report(smi)
        if len(targets) > 1:
            print(f"\nFILE SUMMARY: {n_valid}/{len(targets)} VALID")
        print(SCOPE_NOTE)
        return 0 if n_valid == len(targets) else 1

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
