---
name: smiles-sanity-check
description: "Checks a SMILES string token by token against the SMILES grammar — balanced brackets, atom symbols on the organic subset or a bracketed element, legal bond tokens, paired ring-closure digits, bond-order sums within normal valence — and returns a per-check VALID/INVALID verdict so copy-paste corruption and hallucinated structures are caught before a molecule is quoted. Use whenever a SMILES string appears in a paper, patent, dataset or prompt — \"is this SMILES valid?\", \"sanity-check these SMILES strings\", \"does this SMILES parse?\", \"validate the smiles column\". Not for prose molecular claims such as formulas or molecular weights (use `chemistry-claim-check`), and not a substitute for RDKit."
license: MIT
metadata:
  category: domain
  method: SMILES syntax sanity check (Weininger 1988; OpenSMILES 1.0)
  origin: David Weininger, Daylight Chemical Information Systems, 1988; OpenSMILES specification (Craig A. James et al.), 2016
  version: "2.0.0"
---
# SMILES Sanity Check

SMILES (Simplified Molecular Input Line Entry System) is the line notation for molecular structure introduced by David Weininger in 1988 and formalised as the OpenSMILES specification 1.0 (2016). This check reads a string against that grammar — brackets balanced, every atom symbol on the organic subset or a bracketed element, bond tokens legally placed, ring-closure digits paired, bond-order sums within the OpenSMILES normal valences — and returns a per-check verdict. The core principle is that this is a syntax tripwire, not a chemistry judgement: a string that passes may still describe a nonsense molecule, but a string that fails is certainly mis-copied or invented. It prevents the quiet failure in which a corrupted or hallucinated structure travels from a source into a report as if it were the compound named.

## When to invoke

Invoke when:

- A SMILES string appears anywhere in the material — a paper's methods or supplement, a patent claim, a CSV column named `smiles` or `canonical_smiles`, a model-generated answer, a user prompt.
- The user asks "is this SMILES valid?", "does this SMILES parse?", "sanity-check these SMILES strings", "validate the smiles column before I load it".
- A structure is about to be quoted in a report and the string was transcribed rather than copied from a database export.

Do NOT invoke when:

- The molecular claim is prose — a name paired with a formula, a molecular weight, a "drug-like" assertion — with no SMILES string; that is `chemistry-claim-check`.
- The question is chemical rather than syntactic — stereochemistry, tautomers, stability, valence beyond the simple limits; a syntactic pass does not answer it, so use RDKit or, if the structure is load-bearing and cannot be checked, `abstain-or-escalate`.
- The string is a SMARTS or SMIRKS pattern (wildcards, logical operators, reaction arrows) — a different grammar; report it as unchecked and route to `abstain-or-escalate` if it is load-bearing.

## Procedure

### 1 — Extract and normalise the string

Locate every SMILES candidate: backtick-fenced strings, fields labelled `SMILES:`, `smiles`, `canonical_smiles`, structures quoted in patent claims. Trim outer whitespace and strip surrounding quotes or sentence punctuation, but change nothing inside the string — case is significant (`C` aliphatic, `c` aromatic; `Cl` chlorine, `CL` two atoms and an error) and stray inner spaces are themselves a finding. Record where each string came from (document, page, field or line) so a failure can be traced to its source. With several strings, list them one per line for file mode.

### 2 — Run the five structural checks

Walk the string left to right, tokenising as the OpenSMILES grammar does, and record each check separately:

- **Brackets** — every `(` closes and follows an atom (`C((C)C)` is invalid); every `[` closes, and its content matches `[isotope? symbol chirality? H-count? charge? class?]`, e.g. `[13CH4]`, `[C@@H]`, `[NH4+:5]`.
- **Atoms** — unbracketed symbols must be the organic subset `B C N O P S F Cl Br I` (plus `*`) or aromatic `b c n o p s`; anything else — `H`, metals, `se`, `as`, an unknown token such as `Xz` — must appear inside brackets as a real element symbol.
- **Bonds** — only `-`, `=`, `#`, `$`, `:`, `/`, `\`; never two in a row (`CC==C`), never dangling at the end; `.` separates disconnected components (`[Na+].[Cl-]`).
- **Ring closures** — a digit or `%nn` opens a ring bond and the same number closes it; every number must be paired (`C1CCC` is invalid); a number may be reused once it has closed (`C1CCCCC1C1CCCCC1`).
- **Valence** — for each unbracketed atom, the sum of bond orders must not exceed the OpenSMILES normal valence (B 3; C 4; N 3 or 5; O 2; P 3 or 5; S 2, 4 or 6; halogens 1); aromatic bonds count as 1, so this is a tripwire, not electron bookkeeping (`C(F)(F)(F)(F)F` fails).

### 3 — Report per check and act on any failure

Emit the output template with one line per check; one INVALID line makes the string INVALID. Never autocorrect — a repaired string hides the fact that the source was unreliable. On failure, re-source the SMILES from the primary document or a database export; if it is load-bearing and cannot be re-sourced, drop it with a note or escalate. On success, keep the caveat visible: VALID means the syntax parses and the simple valence limits hold, not that the molecule is real or is the compound named.

## Output template

```
SMILES: {string}   (source: {document / field / line})
  {VALID|INVALID} brackets -- {detail: balanced, or the offending token and position}
  {VALID|INVALID} atoms -- {detail: symbols seen, or the unknown token and position}
  {VALID|INVALID} bonds -- {detail}
  {VALID|INVALID} ring-closures -- {detail: paired digits, or the unclosed number}
  {VALID|INVALID} valence -- {detail: atom, position, bond-order sum vs limit}
RESULT: {VALID|INVALID}
Action: {none — quote with syntax-only caveat | re-sourced from {primary source} | dropped from report | escalated}
```

Mandatory fields: the string as checked, all five check lines, `RESULT`, and — for any INVALID string — an `Action` line. Batch runs end with `FILE SUMMARY: {valid}/{total} VALID`.

## Worked example

`examples/molecules.smi` holds six strings — the checker's own hand-verified cases (Weininger's aspirin and the caffeine string are real molecules; the other four are deliberately broken). Running `python3 scripts/smiles.py check --file examples/molecules.smi` returns `FILE SUMMARY: 2/6 VALID` (exit code 1); the per-string verdicts:

| # | SMILES | Molecule / defect | Failing check | Tool detail |
|---|--------|-------------------|---------------|-------------|
| 1 | `CC(=O)Oc1ccccc1C(=O)O` | Aspirin (acetylsalicylic acid) | none — VALID | ring digits paired (1, 1); 13 atoms within limits |
| 2 | `Cn1cnc2c1c(=O)n(C)c(=O)n2C` | Caffeine | none — VALID | ring digits paired (1, 2, 1, 2); 14 atoms within limits |
| 3 | `C1CC` | ring bond never closed | ring-closures | ring digit 1 opened at char 1 but never closed |
| 4 | `C(F)(F)(F)(F)F` | pentavalent carbon | valence | carbon (C) at char 0: bond-order sum 5 exceeds max valence 4 |
| 5 | `CC(C` | unclosed branch | brackets | '(' at char 2 is never closed |
| 6 | `Ccc(=O)OC1=CC=CC=C1Xz` | invented atom symbol | atoms | atom 'Xz' at char 19 is not on the SMILES whitelist |

The full report for string 4, as printed by the tool:

```
SMILES: C(F)(F)(F)(F)F
  VALID   brackets -- parentheses balanced, no stray brackets
  VALID   atoms -- 2 unique atom symbol(s), all on whitelist: C, F
  VALID   bonds -- all bond/stereo tokens legally placed
  VALID   ring-closures -- no ring digits present
  INVALID valence -- carbon (C) at char 0: bond-order sum 5 exceeds max valence 4
RESULT: INVALID
```

Strings 3–6 get an `Action` line (re-source, or drop with a note); strings 1 and 2 are quoted with the syntax-only caveat. Had string 6 come from a model-generated answer, the right action is to treat that answer's chemistry as unverified, not to patch `Xz` into `Cl`.

## Verification

- [ ] Every string was re-run through `scripts/smiles.py check` (or hand-walked) on the exact text taken from the source — whitespace trimmed, nothing else changed.
- [ ] Recompute by hand for each string: opened `(` equals closed `)`, every `[` has its `]`, and every ring number occurs in pairs.
- [ ] Any string with one INVALID line carries `RESULT: INVALID` and an `Action` line; no string was silently repaired.
- [ ] Every failure line names the offending token and character position so the source can be checked.
- [ ] Every VALID verdict is reported with the syntax-only caveat, and chemistry questions (stereo, tautomer, stability) are routed to RDKit or escalated rather than answered by this check.

## Companion tool

`scripts/smiles.py` (stdlib only, Python 3.9+) implements the structural checks in this skill as real code: `python3 scripts/smiles.py check "CC(=O)Oc1ccccc1C(=O)O"` runs the tripwire on one string, or pass a file of SMILES (one per line). It reports each check's pass/fail and exits non-zero on any failure. `python3 scripts/smiles.py --selftest` runs built-in worked examples (valid and broken strings) to verify the checker itself.

The skill is fully usable without the tool — the checks are listed above in prose — but for more than a couple of strings, run the tool and spend your attention on the failures.

## Pair with adjacent skills

- `chemistry-claim-check` — the prose counterpart: name-vs-formula, molecular weight and drug-likeness claims around the structure.
- `abstain-or-escalate` — when a failed string is load-bearing and cannot be re-sourced, or when a chemistry question exceeds a syntax check.
- `analyze-patent-claims` — patent claims that recite structures by SMILES; check the strings before the claim scope is analysed.

## Anti-patterns

- Do **not** describe a VALID result as chemical validation. Syntax passes; the molecule may still be unstable, impossible or simply not the compound named.
- Do **not** silently fix a broken string. Surface it — a corrupt SMILES is evidence about the source's reliability.
- Do **not** run the check on SMARTS, SMIRKS or InChI strings; different grammars, false verdicts.
- Do **not** skip the source location — a failure that cannot be traced cannot be re-sourced.

## Reference

- D. Weininger, "SMILES, a chemical language and information system. 1. Introduction to methodology and encoding rules," *J. Chem. Inf. Comput. Sci.*, vol. 28, no. 1, pp. 31–36, Feb. 1988, doi: 10.1021/ci00057a005.
- C. A. James et al., "OpenSMILES specification," version 1.0, Blue Obelisk project, May 15, 2016. [Online]. Available: http://opensmiles.org/opensmiles.html
- Daylight Chemical Information Systems, "SMILES — A Simplified Chemical Language," *Daylight Theory Manual*, ch. 3. [Online]. Available: https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html
