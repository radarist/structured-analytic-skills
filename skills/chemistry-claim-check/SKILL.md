---
name: chemistry-claim-check
description: "Checks molecular claims stated in prose — compound name against formula, degree of unsaturation, recomputed molecular weight, and the assessable part of the Lipinski rule of five — and returns a PASS/FAIL verdict per item with the arithmetic shown. Use when a paper, patent, or product page pairs a compound with a formula or a weight, on requests like \"does this molecular weight check out?\" or \"is C2H6O2 really ethanol?\". Not for validating a SMILES string — use `smiles-sanity-check` instead."
license: MIT
metadata:
  category: domain
  method: Formula arithmetic (DBE/RDBE, molecular weight) plus Lipinski's rule of five
  origin: Lipinski, Lombardo, Dominy & Feeney, 1997; DBE from classical mass-spectrometry practice
  version: "2.0.0"
---

# Chemistry Claim Check

A compound name, a molecular formula and a molecular weight are three statements about one molecule, and they must agree. When they do not — "ethanol (C2H6O2)", "caffeine … MW 312 g/mol" — the text has copied the wrong compound, mixed a free base with a salt, or invented the number. This skill recomputes the arithmetic each claim implies and reports where the claim contradicts itself. It is heuristic sanity-checking, not computational chemistry: it can prove a claim inconsistent, never prove a molecule real, stable or active.

## When to invoke

Invoke when:

- Prose pairs a compound with a formula or a weight: "aspirin (C9H8O4)", "the API, C21H23NO5", "MW 194.19", "molar mass of ~500 Da".
- A patent or press release asserts drug-likeness: "orally bioavailable small molecule", "Lipinski-compliant lead compound".
- A structured record carries `formula:` or `molecular_weight:` fields extracted from text rather than a chemical database.

Do NOT invoke when:

- The input is a SMILES string needing syntactic validation — use `smiles-sanity-check`: this skill checks the prose, that one the string.
- The question is whether the compound data is *true* rather than internally consistent — re-source it with `grounded-fact-check`, and grade the publisher with `rate-source-admiralty`.
- Real chemistry semantics are required (tautomers, computed logP, stereochemistry, synthesisability). Those need a cheminformatics toolkit; say so rather than approximating.

## Procedure

### 1 — Extract every molecular claim

Pull the compound name, the formula, the stated weight (with units, and whether it is average, monoisotopic or exact), and any drug-likeness language. Keep each claim attached to its sentence: a mismatch is diagnostic of *which* sentence was copied from elsewhere.

### 2 — Check name against formula

For well-known compounds the formula is a lookup, not a judgment: water H2O, ethanol C2H6O, glucose C6H12O6, aspirin C9H8O4, caffeine C8H10N4O2, ibuprofen C13H18O2, paracetamol C8H9NO2, penicillin G C16H18N2O4S, methane CH4, CO2, ammonia NH3. "Ethanol (C2H6O2)" fails: that is ethylene glycol, and a swapped formula usually means the rest of the claim came from the wrong compound too. For novel candidates, do not guess — mark it `unverified`.

### 3 — Test the formula for possibility

Compute the degree of unsaturation, `RDBE = C + Si + 1 + (N + P)/2 − (H + halogens)/2`. It must be a non-negative integer for a neutral molecule: benzene C6H6 gives 4, ethylamine C2H7N gives 0, and C2H8O gives −1, which nothing neutral can be. A negative or fractional value means the formula is corrupt — stop rather than checking anything downstream. Cross-check with the nitrogen rule: for a neutral C/H/N/O/S/halogen molecule, an odd nominal mass implies an odd nitrogen count.

### 4 — Recompute the molecular weight

Sum the IUPAC standard atomic weights (H 1.008, C 12.011, N 14.007, O 15.999, S 32.06, P 30.974, F 18.998, Cl 35.45, Br 79.904, I 126.904) and compare with the stated value. The tolerance is whichever is larger: 0.05 % or half the last written digit — so a weight quoted as "312" tolerates ±0.5. A few per cent off suggests a salt or hydrate mix-up; more than 10 % off means a different compound. Never reconcile a mismatch by adjusting the formula.

### 5 — Apply the assessable part of Lipinski's rule of five

Lipinski's rule of five (Lipinski et al., 1997) flags poor oral absorption when two or more of these fail: molecular weight ≤ 500, logP ≤ 5, hydrogen-bond donors ≤ 5, acceptors ≤ 10. From a formula alone only molecular weight and a crude acceptor ceiling (N + O) are computable; donors and logP need a structure, so mark them `not assessable`. Violations lower confidence in an oral-bioavailability claim, never disprove it: macrocycles and degraders legitimately live beyond the rule of five.

### 6 — Emit the verdict and route failures

Report each check with its arithmetic. On any FAIL, hand off to `abstain-or-escalate`: re-source from primary literature, drop the chemistry specifics and keep what survives, or escalate when the chemistry is load-bearing.

## Output template

Every check listed in the template is mandatory, and each must show the numbers it was decided on; a bare verdict without arithmetic is not a result.

```
Compound claim: {name} — {formula} — "{stated MW}" — "{drug-likeness language}"
{PASS|FAIL|UNVERIFIED}  name vs formula     {canonical formula, or why it cannot be verified}
{PASS|FAIL}             formula possibility  RDBE = {arithmetic} ({integer? ≥ 0?}); nitrogen rule {OK|violated}
{PASS|FAIL}             molecular weight     computed {x.xx} g/mol vs stated {y} ({Δ%}; {rounding|salt form|wrong compound})
{PASS|NOTE}             Lipinski subset      MW {x} vs 500; N+O = {n} vs 10; donors/logP not assessable
RESULT: {PASS|FAIL} — {what to do next}
```

## Worked example

A biotech press release states: *"our lead compound is caffeine, C8H10N4O2, MW 312 g/mol, a drug-like orally bioavailable small molecule."* Running `python3 scripts/chem.py check --name caffeine --formula C8H10N4O2 --mw 312` recomputes the weight from IUPAC standard atomic weights:

| Element | Count | Atomic weight | Contribution |
| --- | --- | --- | --- |
| C | 8 | 12.011 | 96.088 |
| H | 10 | 1.008 | 10.080 |
| N | 4 | 14.007 | 56.028 |
| O | 2 | 15.999 | 31.998 |
| **Total** | | | **194.19 g/mol** |

Name and formula agree — caffeine is C8H10N4O2. RDBE is 8 + 1 + 4/2 − 10/2 = 6, an integer and non-negative, so the formula is possible. The Lipinski subset passes easily: 194.19 ≤ 500 and N + O = 6 ≤ 10. But the stated 312 g/mol is 60.66 % above the computed 194.194, far outside tolerance, so the claim fails. The likely cause is a salt-form mix-up — caffeine citrate is heavier than the free base — but the skill flags rather than reconciles: the release pairs one form's formula with another's weight, and its author should say which was meant. RESULT: FAIL — re-source before use.

## Verification

Before the verdict ships:

- [ ] Every arithmetic check was recomputed from the stated formula, not copied from the text being checked.
- [ ] RDBE was evaluated and is a non-negative integer, or the formula was rejected as impossible.
- [ ] The molecular-weight comparison states both the computed value and the percentage difference, and names the likely cause when it fails.
- [ ] Unverifiable name-to-formula pairs are marked `unverified` rather than guessed.
- [ ] Lipinski criteria that need a structure are marked `not assessable` rather than estimated.
- [ ] `python3 scripts/chem.py check …` was run (or the arithmetic hand-checked twice) and its verdict matches the emitted one.

## Companion tool

`scripts/chem.py` (stdlib only, offline, deterministic) does the arithmetic of steps 2–5.

```bash
python3 scripts/chem.py formula "C8H10N4O2"                        # counts, MW, monoisotopic, RDBE, Lipinski subset
python3 scripts/chem.py check --name ethanol --formula C2H6O2      # per-item verdicts; exit 1 on any FAIL
python3 scripts/chem.py --demo                                     # the worked example above
python3 scripts/chem.py --selftest                                 # 106 checks against PubChem-verified values
```

Hydrates, brackets and charges parse (`CuSO4·5H2O`, `[Fe(CN)6]4-`); `--json` emits the verdict structure. Real output:

```
Claim: ethanol -- C2H6O2
Computed: C2H6O2  MW 62.068 g/mol  monoisotopic 62.036779 Da  RDBE 0
FAIL       name vs formula              ethanol is C2H6O; claimed C2H6O2 = ethylene glycol
PASS       formula plausibility         RDBE = 2 + 0 + 1 + (0 + 0)/2 - (6 + 0)/2 = 0 (integer, >= 0)
NOTE       Lipinski (assessable subset) MW 62.07 <= 500 OK; N+O = 2 <= 10 OK; donors/logP need a structure
RESULT: FAIL (1 of 2 checks failed) -- re-source before use
```

The skill works without the tool — every step is hand-computable — but beyond a single formula, run it and read the FAIL lines. Structure-level chemistry stays out of scope on purpose: a cheminformatics toolkit is a different dependency class from a stdlib script.

## Pair with adjacent skills

- `smiles-sanity-check` — the structural counterpart: this skill checks prose claims, that one checks SMILES strings.
- `grounded-fact-check` — re-source compound data from primary literature when a check fails.
- `abstain-or-escalate` — when the chemistry is load-bearing and cannot be verified.
- `rate-source-admiralty` — grade the publisher supplying the compound data before trusting it.
- `analyze-patent-claims` — patent chemistry arrives inside claim language that needs its own parsing.

## Anti-patterns

- Do **not** present a pass as chemical validation. A consistent name/formula/weight triple can still describe an inert or unsynthesisable molecule.
- Do **not** silently correct a formula or a weight. Surface the mismatch; autocorrection destroys the evidence that something was copied from the wrong source.
- Do **not** treat Lipinski violations as disqualifying. The rule is a heuristic for oral small molecules; biologics and macrocycles violate it legitimately. Report violations as confidence modifiers.
- Do **not** guess formulas for unfamiliar compound names. `unverified` is an honest answer; a guessed formula is a manufactured fact.
- Do **not** extend this skill into structure-level chemistry. That boundary is deliberate, not an oversight.

## Reference

- C. A. Lipinski, F. Lombardo, B. W. Dominy and P. J. Feeney, "Experimental and computational approaches to estimate solubility and permeability in drug discovery and development settings," *Advanced Drug Delivery Reviews*, vol. 23, no. 1–3, pp. 3–25, 1997. doi: 10.1016/S0169-409X(96)00423-1
- F. W. McLafferty and F. Tureček, *Interpretation of Mass Spectra*, 4th ed. University Science Books, 1993, ch. 2 — rings-plus-double-bonds and the nitrogen rule. ISBN 978-0-935702-25-5
- T. Prohaska et al., "Standard atomic weights of the elements 2021 (IUPAC Technical Report)," *Pure and Applied Chemistry*, vol. 94, no. 5, pp. 573–600, 2022. doi: 10.1515/pac-2019-0603
- CIAAW, *Standard Atomic Weights*, IUPAC, 2021 — the conventional values the companion tool uses. https://ciaaw.org/atomic-weights.htm
