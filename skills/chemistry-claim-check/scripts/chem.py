#!/usr/bin/env python3
"""chem.py — molecular-formula arithmetic for the chemistry-claim-check skill.

Implements, as deterministic code, the arithmetic that ../SKILL.md asks the
agent to do in steps 2-5 (name-vs-formula lookup, degree of unsaturation,
molecular weight, Lipinski's assessable subset), plus the mass-spectrometry
quantities usually quoted next to a formula (exact mass, nominal mass).

Definitions implemented
  * Formula parsing: case-sensitive element symbols; counts; nested ( ) [ ] { }
    with multipliers (Ca(OH)2, K4[Fe(CN)6]); hydrate/adduct dots with a leading
    multiplier (CuSO4·5H2O, CuSO4.5H2O, MgSO4*7H2O, CaSO4·0.5H2O); charges
    (NH4+, SO4^2-, [Fe(CN)6]4-, "SO4 2-", Fe^3+, Fe+3, superscript ²⁻);
    Unicode sub/superscripts (C₈H₁₀N₄O₂, Fe³⁺). Output uses Hill order
    (C, then H, then alphabetical; all-alphabetical when there is no carbon).
  * Average molecular weight (g/mol) = sum n_i * Ar(i), with IUPAC standard
    atomic weights (Prohaska et al. 2022, "Standard atomic weights of the
    elements 2021", Pure Appl. Chem. 94(5) 573-600, incl. the CIAAW 2023
    revisions of Gd, Lu, Zr) rounded to three decimals; the IUPAC
    *conventional* value is used for the 14 interval elements
    (H 1.008, Li 6.94, B 10.81, C 12.011, N 14.007, O 15.999, Mg 24.305,
    Si 28.085, S 32.06, Cl 35.45, Ar 39.95, Br 79.904, Tl 204.38, Pb 207.2).
    Radioactive elements without a standard atomic weight carry the mass of
    the isotope named in the IUPAC Periodic Table (4 May 2022), e.g. Tc-97.
    Table source: ciaaw.org/atomic-weights.htm (accessed 2026-08-16).
  * Monoisotopic (exact) mass (Da) = sum n_i * m(most abundant isotope of i):
    12C 12 (exact), 1H 1.007825, 14N 14.003074, 16O 15.994915, 32S 31.972071,
    31P 30.973762, 19F 18.998403, 35Cl 34.968853, 79Br 78.918338,
    127I 126.904472, 23Na 22.989769, 39K 38.963706, 28Si 27.976927 ...
    Source: NIST Atomic Weights and Isotopic Compositions (Coursey et al.,
    physics.nist.gov/Comp, AME2016 masses; differs from AME2020 by < 1e-6 u).
    Ion m/z and adduct masses use CODATA 2022 m_e = 5.48579909e-4 u and
    m_p = 1.00727646658 u. Electron mass is NOT subtracted from the
    monoisotopic mass of ions (PubChem convention); it is subtracted in m/z.
  * Nominal mass = sum n_i * A(most abundant isotope of i)  (Cl 35, Br 79).
  * Mass-percent composition = 100 * n_i * Ar(i) / MW.
  * RDBE (rings + double-bond equivalents = degree of unsaturation), the
    McLafferty & Tureček (1993) convention: valences C,Si = 4; N,P,B,As = 3;
    O,S,Se = 2; H,D,T,halogens = 1  ->
        RDBE = C + Si + 1 + (N + P)/2 - (H + halogens)/2   (+ B/2 + As/2)
    S(VI)/P(V) centres are still counted at 2/3 (standard MS convention).
    A neutral closed-shell molecule must have an integer RDBE >= 0; a
    half-integer means radical/ion/corrupt formula, negative means too many
    H for the heavy atoms.  For ions the even-electron adjustment
    RDBE + z/2 (z = signed charge) is reported as well.  Not applicable when
    the formula contains elements outside that valence set (metals ...).
  * Nitrogen rule (neutral C/H/N/O/S/P/Si/B/Se/As/halogen formulas): an odd
    nominal mass implies an odd number of N atoms and vice versa.
  * Lipinski rule of five (Lipinski et al. 1997), assessable-from-formula
    subset only: MW <= 500 and (N + O) <= 10 as a ceiling on H-bond
    acceptors; donors and logP need a structure and are reported as
    "not assessable".  Violations are confidence modifiers, never a FAIL.
  * `check` tolerances: MW passes within max(--mw-tol % of computed
    [default 0.05 %], half a unit in the claim's last written digit) — so
    "194" and "194.2" both pass for caffeine (194.194); exact mass within
    --mono-tol ppm (default 10) or the same last-digit rule; composition
    within --comp-tol percentage points (default 0.4, the elemental-analysis
    convention).  Verdicts: PASS / FAIL / NOTE / UNVERIFIED; exit 2 if any FAIL.

Reference values used by --selftest were checked against PubChem (PUG REST,
2026-08-16): water 18.015; glucose 180.16; caffeine 194.19 (RDBE 6, exact
194.08037557); aspirin 180.16 (RDBE 6); ibuprofen 206.28 (RDBE 5); benzene
RDBE 4; ethanol RDBE 0; NaCl 58.44; CuSO4·5H2O 249.69; sulfate O4S(2-) 96.07;
ferrocyanide C6FeN6(4-) 211.95; bortezomib C19H25BN4O4 384.2.  PubChem
computes MW from interval *midpoints* (S 32.0675) whereas this tool uses the
IUPAC conventional S 32.06, so sulfur compounds differ by ~0.0075 g/mol per S
(CuSO4·5H2O 249.677 vs 249.69; sulfate 96.056 vs 96.07) — well inside 0.05 %.

Stdlib only.  Python 3.9+.  Offline.  Deterministic.

Usage:
    python3 chem.py formula "C8H10N4O2"
    python3 chem.py formula "CuSO4·5H2O" --json
    python3 chem.py formula --file formulas.txt          # one formula per line
    python3 chem.py check --name caffeine --formula C8H10N4O2 --mw 312 --druglike
    python3 chem.py check --file claim.json               # {"name":..,"formula":..,"mw":..,
                                                          #  "exact_mass":..,"rdbe":..,
                                                          #  "composition":{"C":49.5,..},
                                                          #  "druglike":true}  or a list
    python3 chem.py --demo                                # SKILL.md worked example
    python3 chem.py --selftest
Exit codes: 0 ok; 1 invalid input (unknown element, unbalanced brackets ...);
2 at least one claim FAILs.
"""

import argparse
import json
import re
import sys

# ---------------------------------------------------------------------------
# Data tables
# ---------------------------------------------------------------------------

# sym: (Z, name, average atomic weight g/mol, A of the most abundant (or, for
# "radio", longest-lived) isotope, its atomic mass in Da, note)
#   note "conv"  = IUPAC conventional value of an interval element
#   note "radio" = no standard atomic weight; longest-lived isotope used
# Average weights: CIAAW standard atomic weights (IUPAC 2021 + 2023 revisions),
# rounded half-up to 3 decimals.  Isotope masses: NIST Atomic Weights and
# Isotopic Compositions (AME2016).  Fl-290 has no tabulated mass (mass number).
ELEMENTS = {
    "H": (1, "hydrogen", 1.008, 1, 1.00782503223, "conv"),
    "He": (2, "helium", 4.003, 4, 4.00260325413, ""),
    "Li": (3, "lithium", 6.94, 7, 7.0160034366, "conv"),
    "Be": (4, "beryllium", 9.012, 9, 9.012183065, ""),
    "B": (5, "boron", 10.81, 11, 11.00930536, "conv"),
    "C": (6, "carbon", 12.011, 12, 12.0, "conv"),
    "N": (7, "nitrogen", 14.007, 14, 14.00307400443, "conv"),
    "O": (8, "oxygen", 15.999, 16, 15.99491461957, "conv"),
    "F": (9, "fluorine", 18.998, 19, 18.99840316273, ""),
    "Ne": (10, "neon", 20.18, 20, 19.9924401762, ""),
    "Na": (11, "sodium", 22.99, 23, 22.989769282, ""),
    "Mg": (12, "magnesium", 24.305, 24, 23.985041697, "conv"),
    "Al": (13, "aluminium", 26.982, 27, 26.98153853, ""),
    "Si": (14, "silicon", 28.085, 28, 27.97692653465, "conv"),
    "P": (15, "phosphorus", 30.974, 31, 30.97376199842, ""),
    "S": (16, "sulfur", 32.06, 32, 31.9720711744, "conv"),
    "Cl": (17, "chlorine", 35.45, 35, 34.968852682, "conv"),
    "Ar": (18, "argon", 39.95, 40, 39.9623831237, "conv"),
    "K": (19, "potassium", 39.098, 39, 38.9637064864, ""),
    "Ca": (20, "calcium", 40.078, 40, 39.962590863, ""),
    "Sc": (21, "scandium", 44.956, 45, 44.95590828, ""),
    "Ti": (22, "titanium", 47.867, 48, 47.94794198, ""),
    "V": (23, "vanadium", 50.942, 51, 50.94395704, ""),
    "Cr": (24, "chromium", 51.996, 52, 51.94050623, ""),
    "Mn": (25, "manganese", 54.938, 55, 54.93804391, ""),
    "Fe": (26, "iron", 55.845, 56, 55.93493633, ""),
    "Co": (27, "cobalt", 58.933, 59, 58.93319429, ""),
    "Ni": (28, "nickel", 58.693, 58, 57.93534241, ""),
    "Cu": (29, "copper", 63.546, 63, 62.92959772, ""),
    "Zn": (30, "zinc", 65.38, 64, 63.92914201, ""),
    "Ga": (31, "gallium", 69.723, 69, 68.9255735, ""),
    "Ge": (32, "germanium", 72.63, 74, 73.921177761, ""),
    "As": (33, "arsenic", 74.922, 75, 74.92159457, ""),
    "Se": (34, "selenium", 78.971, 80, 79.9165218, ""),
    "Br": (35, "bromine", 79.904, 79, 78.9183376, "conv"),
    "Kr": (36, "krypton", 83.798, 84, 83.9114977282, ""),
    "Rb": (37, "rubidium", 85.468, 85, 84.9117897379, ""),
    "Sr": (38, "strontium", 87.62, 88, 87.9056125, ""),
    "Y": (39, "yttrium", 88.906, 89, 88.9058403, ""),
    "Zr": (40, "zirconium", 91.222, 90, 89.9046977, ""),
    "Nb": (41, "niobium", 92.906, 93, 92.906373, ""),
    "Mo": (42, "molybdenum", 95.95, 98, 97.90540482, ""),
    "Tc": (43, "technetium", 96.906, 97, 96.9063667, "radio"),
    "Ru": (44, "ruthenium", 101.07, 102, 101.9043441, ""),
    "Rh": (45, "rhodium", 102.905, 103, 102.905498, ""),
    "Pd": (46, "palladium", 106.42, 106, 105.9034804, ""),
    "Ag": (47, "silver", 107.868, 107, 106.9050916, ""),
    "Cd": (48, "cadmium", 112.414, 114, 113.90336509, ""),
    "In": (49, "indium", 114.818, 115, 114.903878776, ""),
    "Sn": (50, "tin", 118.71, 120, 119.90220163, ""),
    "Sb": (51, "antimony", 121.76, 121, 120.903812, ""),
    "Te": (52, "tellurium", 127.6, 130, 129.906222748, ""),
    "I": (53, "iodine", 126.904, 127, 126.9044719, ""),
    "Xe": (54, "xenon", 131.293, 132, 131.9041550856, ""),
    "Cs": (55, "caesium", 132.905, 133, 132.905451961, ""),
    "Ba": (56, "barium", 137.327, 138, 137.905247, ""),
    "La": (57, "lanthanum", 138.905, 139, 138.9063563, ""),
    "Ce": (58, "cerium", 140.116, 140, 139.9054431, ""),
    "Pr": (59, "praseodymium", 140.908, 141, 140.9076576, ""),
    "Nd": (60, "neodymium", 144.242, 142, 141.907729, ""),
    "Pm": (61, "promethium", 144.913, 145, 144.9127559, "radio"),
    "Sm": (62, "samarium", 150.36, 152, 151.9197397, ""),
    "Eu": (63, "europium", 151.964, 153, 152.921238, ""),
    "Gd": (64, "gadolinium", 157.249, 158, 157.9241123, ""),
    "Tb": (65, "terbium", 158.925, 159, 158.9253547, ""),
    "Dy": (66, "dysprosium", 162.5, 164, 163.9291819, ""),
    "Ho": (67, "holmium", 164.93, 165, 164.9303288, ""),
    "Er": (68, "erbium", 167.259, 166, 165.9302995, ""),
    "Tm": (69, "thulium", 168.934, 169, 168.9342179, ""),
    "Yb": (70, "ytterbium", 173.045, 174, 173.9388664, ""),
    "Lu": (71, "lutetium", 174.967, 175, 174.9407752, ""),
    "Hf": (72, "hafnium", 178.486, 180, 179.946557, ""),
    "Ta": (73, "tantalum", 180.948, 181, 180.9479958, ""),
    "W": (74, "tungsten", 183.84, 184, 183.95093092, ""),
    "Re": (75, "rhenium", 186.207, 187, 186.9557501, ""),
    "Os": (76, "osmium", 190.23, 192, 191.961477, ""),
    "Ir": (77, "iridium", 192.217, 193, 192.9629216, ""),
    "Pt": (78, "platinum", 195.084, 195, 194.9647917, ""),
    "Au": (79, "gold", 196.967, 197, 196.96656879, ""),
    "Hg": (80, "mercury", 200.592, 202, 201.9706434, ""),
    "Tl": (81, "thallium", 204.38, 205, 204.9744278, "conv"),
    "Pb": (82, "lead", 207.2, 208, 207.9766525, "conv"),
    "Bi": (83, "bismuth", 208.98, 209, 208.9803991, ""),
    "Po": (84, "polonium", 208.982, 209, 208.9824308, "radio"),
    "At": (85, "astatine", 209.987, 210, 209.9871479, "radio"),
    "Rn": (86, "radon", 222.018, 222, 222.0175782, "radio"),
    "Fr": (87, "francium", 223.02, 223, 223.019736, "radio"),
    "Ra": (88, "radium", 226.025, 226, 226.0254103, "radio"),
    "Ac": (89, "actinium", 227.028, 227, 227.0277523, "radio"),
    "Th": (90, "thorium", 232.038, 232, 232.0380558, ""),
    "Pa": (91, "protactinium", 231.036, 231, 231.0358842, ""),
    "U": (92, "uranium", 238.029, 238, 238.0507884, ""),
    "Np": (93, "neptunium", 237.048, 237, 237.0481736, "radio"),
    "Pu": (94, "plutonium", 244.064, 244, 244.0642053, "radio"),
    "Am": (95, "americium", 243.061, 243, 243.0613813, "radio"),
    "Cm": (96, "curium", 247.07, 247, 247.0703541, "radio"),
    "Bk": (97, "berkelium", 247.07, 247, 247.0703073, "radio"),
    "Cf": (98, "californium", 251.08, 251, 251.0795886, "radio"),
    "Es": (99, "einsteinium", 252.083, 252, 252.08298, "radio"),
    "Fm": (100, "fermium", 257.095, 257, 257.0951061, "radio"),
    "Md": (101, "mendelevium", 258.098, 258, 258.0984315, "radio"),
    "No": (102, "nobelium", 259.101, 259, 259.10103, "radio"),
    "Lr": (103, "lawrencium", 262.11, 262, 262.10961, "radio"),
    "Rf": (104, "rutherfordium", 267.122, 267, 267.12179, "radio"),
    "Db": (105, "dubnium", 268.126, 268, 268.12567, "radio"),
    "Sg": (106, "seaborgium", 269.129, 269, 269.12863, "radio"),
    "Bh": (107, "bohrium", 270.133, 270, 270.13336, "radio"),
    "Hs": (108, "hassium", 269.134, 269, 269.13375, "radio"),
    "Mt": (109, "meitnerium", 277.153, 277, 277.15327, "radio"),
    "Ds": (110, "darmstadtium", 281.165, 281, 281.16451, "radio"),
    "Rg": (111, "roentgenium", 282.169, 282, 282.16912, "radio"),
    "Cn": (112, "copernicium", 285.177, 285, 285.17712, "radio"),
    "Nh": (113, "nihonium", 286.182, 286, 286.18221, "radio"),
    "Fl": (114, "flerovium", 290.0, 290, 290.0, "radio"),
    "Mc": (115, "moscovium", 290.196, 290, 290.19598, "radio"),
    "Lv": (116, "livermorium", 293.204, 293, 293.20449, "radio"),
    "Ts": (117, "tennessine", 294.21, 294, 294.21046, "radio"),
    "Og": (118, "oganesson", 294.214, 294, 294.21392, "radio"),
}
# Isotopic hydrogen written as D / T (NIST masses); counted as H for RDBE.
ELEMENTS["D"] = (1, "deuterium", 2.014, 2, 2.01410177812, "isotope")
ELEMENTS["T"] = (1, "tritium", 3.016, 3, 3.0160492779, "isotope")

ELECTRON_MASS = 5.48579909e-4    # u, CODATA 2022
PROTON_MASS = 1.00727646658      # u, CODATA 2022

# Typical lowest valences for the RDBE convention (see docstring).
RDBE_VALENCE = {
    "C": 4, "Si": 4,
    "N": 3, "P": 3, "B": 3, "As": 3,
    "O": 2, "S": 2, "Se": 2,
    "H": 1, "D": 1, "T": 1, "F": 1, "Cl": 1, "Br": 1, "I": 1,
}
HALOGENS = ("F", "Cl", "Br", "I")
# Nitrogen rule holds when every element has parity(A) == parity(valence),
# except N itself (A 14 even, valence 3 odd) — that exception *is* the rule.
NITROGEN_RULE_ELEMENTS = frozenset(RDBE_VALENCE) - {"D", "T"}

# Well-known compounds for the SKILL.md step-2 name-vs-formula lookup.  Every
# formula verified against PubChem (PUG REST) on 2026-08-16.  Names are
# matched case-insensitively after collapsing spaces/hyphens.  Anything not
# in this table is reported UNVERIFIED — never guessed.
KNOWN_COMPOUNDS = {
    "water": "H2O", "hydrogen peroxide": "H2O2", "ammonia": "NH3",
    "methane": "CH4", "ethylene": "C2H4", "acetylene": "C2H2", "propane": "C3H8",
    "butane": "C4H10", "octane": "C8H18", "hexane": "C6H14", "cyclohexane": "C6H12",
    "benzene": "C6H6", "toluene": "C7H8", "styrene": "C8H8", "naphthalene": "C10H8",
    "phenol": "C6H6O", "aniline": "C6H7N", "pyridine": "C5H5N",
    "methanol": "CH4O", "ethanol": "C2H6O", "ethyl alcohol": "C2H6O",
    "ethylene glycol": "C2H6O2", "glycerol": "C3H8O3", "ethylamine": "C2H7N",
    "acetone": "C3H6O", "formaldehyde": "CH2O", "formic acid": "CH2O2",
    "acetic acid": "C2H4O2", "oxalic acid": "C2H2O4", "lactic acid": "C3H6O3",
    "citric acid": "C6H8O7", "ethyl acetate": "C4H8O2", "diethyl ether": "C4H10O",
    "tetrahydrofuran": "C4H8O", "dichloromethane": "CH2Cl2", "chloroform": "CHCl3",
    "dimethyl sulfoxide": "C2H6OS", "dmso": "C2H6OS", "urea": "CH4N2O",
    "carbon dioxide": "CO2", "carbon monoxide": "CO", "nitrous oxide": "N2O",
    "ozone": "O3", "hydrogen": "H2", "oxygen": "O2", "nitrogen": "N2",
    "glucose": "C6H12O6", "dextrose": "C6H12O6", "fructose": "C6H12O6",
    "sucrose": "C12H22O11", "lactose": "C12H22O11",
    "glycine": "C2H5NO2", "alanine": "C3H7NO2", "glutamic acid": "C5H9NO4",
    "tryptophan": "C11H12N2O2", "adenine": "C5H5N5", "guanine": "C5H5N5O",
    "cytosine": "C4H5N3O", "thymine": "C5H6N2O2", "uracil": "C4H4N2O2",
    "adenosine": "C10H13N5O4", "atp": "C10H16N5O13P3",
    "adenosine triphosphate": "C10H16N5O13P3", "nadh": "C21H29N7O14P2",
    "palmitic acid": "C16H32O2", "stearic acid": "C18H36O2", "oleic acid": "C18H34O2",
    "cholesterol": "C27H46O", "testosterone": "C19H28O2", "estradiol": "C18H24O2",
    "progesterone": "C21H30O2", "cortisol": "C21H30O5",
    "dopamine": "C8H11NO2", "serotonin": "C10H12N2O", "adrenaline": "C9H13NO3",
    "epinephrine": "C9H13NO3", "histamine": "C5H9N3", "melatonin": "C13H16N2O2",
    "ascorbic acid": "C6H8O6", "vitamin c": "C6H8O6", "retinol": "C20H30O",
    "cholecalciferol": "C27H44O", "niacin": "C6H5NO2", "riboflavin": "C17H20N4O6",
    "folic acid": "C19H19N7O6", "biotin": "C10H16N2O3S", "heme": "C34H32FeN4O4",
    "aspirin": "C9H8O4", "acetylsalicylic acid": "C9H8O4", "caffeine": "C8H10N4O2",
    "ibuprofen": "C13H18O2", "paracetamol": "C8H9NO2", "acetaminophen": "C8H9NO2",
    "penicillin g": "C16H18N2O4S", "benzylpenicillin": "C16H18N2O4S",
    "penicillin v": "C16H18N2O5S", "amoxicillin": "C16H19N3O5S",
    "ciprofloxacin": "C17H18FN3O3", "tetracycline": "C22H24N2O8",
    "erythromycin": "C37H67NO13", "vancomycin": "C66H75Cl2N9O24",
    "metformin": "C4H11N5", "atorvastatin": "C33H35FN2O5", "sildenafil": "C22H30N6O4S",
    "imatinib": "C29H31N7O", "paclitaxel": "C47H51NO14", "taxol": "C47H51NO14",
    "doxorubicin": "C27H29NO11", "cisplatin": "Cl2H6N2Pt", "warfarin": "C19H16O4",
    "diazepam": "C16H13ClN2O", "fluoxetine": "C17H18F3NO", "omeprazole": "C17H19N3O3S",
    "lisinopril": "C21H31N3O5", "salbutamol": "C13H21NO3", "albuterol": "C13H21NO3",
    "nitroglycerin": "C3H5N3O9", "lidocaine": "C14H22N2O", "ketamine": "C13H16ClNO",
    "propofol": "C12H18O", "fentanyl": "C22H28N2O", "morphine": "C17H19NO3",
    "cocaine": "C17H21NO4", "nicotine": "C10H14N2", "amphetamine": "C9H13N",
    "methamphetamine": "C10H15N", "mdma": "C11H15NO2", "lsd": "C20H25N3O",
    "psilocybin": "C12H17N2O4P", "dronabinol": "C21H30O2", "thc": "C21H30O2",
    "chloroquine": "C18H26ClN3", "hydroxychloroquine": "C18H26ClN3O",
    "dexamethasone": "C22H29FO5", "remdesivir": "C27H35N6O8P",
    "molnupiravir": "C13H19N3O7", "nirmatrelvir": "C23H32F3N5O4",
    "rapamycin": "C51H79NO13", "sirolimus": "C51H79NO13", "cyclosporine": "C62H111N11O12",
    "bortezomib": "C19H25BN4O4", "quinine": "C20H24N2O2", "capsaicin": "C18H27NO3",
    "menthol": "C10H20O", "vanillin": "C8H8O3", "aspartame": "C14H18N2O5",
    "bisphenol a": "C15H16O2", "caffeine citrate": "C14H18N4O9",
    "metformin hydrochloride": "C4H12ClN5", "sildenafil citrate": "C28H38N6O11S",
    "penicillin g potassium": "C16H17KN2O4S",
    "sodium chloride": "NaCl", "table salt": "NaCl", "potassium chloride": "KCl",
    "sodium hydroxide": "NaOH", "sodium bicarbonate": "NaHCO3",
    "sodium carbonate": "Na2CO3", "sodium sulfate": "Na2SO4",
    "sodium sulfate decahydrate": "Na2SO4·10H2O", "lithium carbonate": "Li2CO3",
    "calcium carbonate": "CaCO3", "calcium chloride": "CaCl2",
    "calcium hydroxide": "Ca(OH)2", "magnesium sulfate": "MgSO4",
    "magnesium sulfate heptahydrate": "MgSO4·7H2O", "potassium nitrate": "KNO3",
    "potassium permanganate": "KMnO4", "ammonium nitrate": "NH4NO3",
    "ammonium sulfate": "(NH4)2SO4", "silver nitrate": "AgNO3",
    "copper(ii) sulfate": "CuSO4", "copper sulfate": "CuSO4",
    "copper(ii) sulfate pentahydrate": "CuSO4·5H2O",
    "copper sulfate pentahydrate": "CuSO4·5H2O", "sulfuric acid": "H2SO4",
    "hydrochloric acid": "HCl", "hydrogen chloride": "HCl", "silicon dioxide": "SiO2",
    "titanium dioxide": "TiO2", "zinc oxide": "ZnO", "aluminium oxide": "Al2O3",
    "aluminum oxide": "Al2O3", "ammonium": "NH4+", "hydronium": "H3O+",
    "azide": "N3^-", "sulfate": "SO4^2-", "ferrocyanide": "[Fe(CN)6]4-",
}

# ---------------------------------------------------------------------------
# Formula parsing
# ---------------------------------------------------------------------------


class FormulaError(ValueError):
    """Raised for any unparsable formula (exit code 1 at the CLI)."""


_SUBSCRIPTS = "₀₁₂₃₄₅₆₇₈₉"
_SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_SEPARATORS = ".·•∙⋅*"           # hydrate / adduct separators
_OPEN = {"(": ")", "[": "]", "{": "}"}
_CLOSE = {v: k for k, v in _OPEN.items()}
_ELEMENT_RE = re.compile(r"[A-Z][a-z]?")
_INT_RE = re.compile(r"\d+")
_MULT_RE = re.compile(r"\d+(?:\.\d+)?")
_CHARGE_RE = re.compile(r"\s*(?:(\d+)\s*([+-])|([+-])\s*(\d*))")   # 2- | -2 | -


def normalize_formula(text):
    """Map Unicode sub/superscripts, minus signs and vulgar fractions to ASCII.
    Superscript runs become a caret charge token: 'SO₄²⁻' -> 'SO4^2-'."""
    out = []
    in_sup = False
    for ch in text.strip():
        if ch in _SUBSCRIPTS:
            out.append(str(_SUBSCRIPTS.index(ch)))
            in_sup = False
        elif ch in _SUPERSCRIPTS or ch in "⁺⁻":
            if not in_sup:
                out.append("^")
                in_sup = True
            out.append(str(_SUPERSCRIPTS.index(ch)) if ch in _SUPERSCRIPTS else ("+" if ch == "⁺" else "-"))
        else:
            in_sup = False
            if ch in "−–—":
                out.append("-")
            elif ch == "½":
                out.append("0.5")
            elif ch == "¼":
                out.append("0.25")
            elif ch == "¾":
                out.append("0.75")
            else:
                out.append(ch)
    return "".join(out)


class _Parser:
    def __init__(self, text):
        self.s = normalize_formula(text)
        self.i = 0
        self.notes = []
        self.raw = text

    # -- helpers ------------------------------------------------------------
    def _err(self, msg):
        raise FormulaError(f"{msg} in formula {self.raw!r} (position {self.i + 1})")

    def _peek(self, k=0):
        j = self.i + k
        return self.s[j] if j < len(self.s) else ""

    def _skip_ws(self):
        while self._peek().isspace():
            self.i += 1

    def _next_nonspace(self):
        j = self.i
        while j < len(self.s) and self.s[j].isspace():
            j += 1
        return self.s[j] if j < len(self.s) else ""

    def _read_charge(self):
        """Read a charge token starting at self.i (sign or digits+sign)."""
        m = _CHARGE_RE.match(self.s, self.i)
        if not m or m.end() == self.i:
            self._err("expected a charge such as 2-, +, ^3+ after '^'")
        if m.group(1) is not None:
            mag, sign = int(m.group(1)), m.group(2)
            self.i = m.end()
        else:
            sign, digits = m.group(3), m.group(4)
            if digits:
                mag = int(digits)
                self.i = m.end()
            else:
                # bare sign, possibly repeated: ++ / --
                self.i = m.end()
                mag = 1
                while self._peek() == sign:
                    mag += 1
                    self.i += 1
        if mag == 0:
            self._err("charge magnitude 0 is not a charge")
        return mag if sign == "+" else -mag

    # -- grammar ------------------------------------------------------------
    def parse(self):
        components = []
        total = {}
        charge = 0.0
        ascii_dot = False
        while True:
            self._skip_ws()
            if self.i >= len(self.s):
                break
            mult = 1.0
            m = _MULT_RE.match(self.s, self.i)
            if m:                                   # leading multiplier or a bare charge
                j = m.end()
                while j < len(self.s) and self.s[j].isspace():
                    j += 1
                if j < len(self.s) and self.s[j] in "+-" and "." not in m.group(0):
                    charge += self._read_charge()   # e.g. "SO4 2-"
                    continue
                mult = float(m.group(0))
                self.i = m.end()
                if mult <= 0:
                    self._err("a component multiplier must be positive")
                if not (self._peek().isalpha() or self._peek() in _OPEN):
                    self._err("a leading number must be followed by an element or bracket")
                if self._peek() and self._peek().islower():
                    self._err(f"unexpected character {self._peek()!r}")
            counts, q = self._sequence(depth=0)
            if not counts:
                if q:
                    charge += q
                    continue
                self._err("empty component")
            components.append({"formula": hill_formula(counts), "multiplier": _num(mult),
                               "counts": {k: _num(v) for k, v in _hill_sorted(counts)},
                               "charge": _num(q)})
            for el, n in counts.items():
                total[el] = total.get(el, 0.0) + mult * n
            charge += mult * q
            # after a component: separator, charge, or end
            self._skip_ws()
            if self.i < len(self.s) and self.s[self.i] in _SEPARATORS:
                sep = self.s[self.i]
                before = self.s[self.i - 1] if self.i > 0 else ""
                after = self.s[self.i + 1] if self.i + 1 < len(self.s) else ""
                if sep == "." and before.isdigit() and after.isdigit():
                    ascii_dot = True
                self.i += 1
                self._skip_ws()
                if self.i >= len(self.s):
                    self._err("dangling separator")
        if not total:
            self._err("no atoms")
        if ascii_dot:
            parts = " · ".join((f"{c['multiplier']} " if c["multiplier"] != 1 else "") + c["formula"] for c in components)
            self.notes.append(f"ASCII '.' between digits read as a hydrate/adduct dot: {parts} "
                              "(decimal element counts are not supported)")
        return total, charge, components

    def _sequence(self, depth):
        """Parse a run of element/group/charge tokens; return (counts, charge)."""
        counts = {}
        charge = 0.0
        while self.i < len(self.s):
            ch = self.s[self.i]
            if ch.isspace():
                nxt = self._next_nonspace()
                # whitespace before a digit: charge ("SO4 2-") or new component ("CuSO4 5H2O")
                if nxt.isdigit():
                    if depth:
                        self._err("unexpected number inside brackets")
                    return counts, charge
                self._skip_ws()
                continue
            if ch in _SEPARATORS:
                if depth:
                    self._err("hydrate/adduct separator inside brackets")
                return counts, charge
            if ch in _CLOSE:
                if depth == 0:
                    self._err(f"unbalanced brackets: unexpected {ch!r}")
                return counts, charge
            if ch in _OPEN:
                self._group(counts, depth)
                # charge inside a group is folded into counts via _group; keep going
                charge += counts.pop("__charge__", 0.0)
                continue
            if ch == "^":
                self.i += 1
                charge += self._read_charge()
                continue
            if ch == "+":
                charge += self._read_charge()
                continue
            if ch == "-":
                nxt = self._peek(1)
                if nxt.isupper() or nxt in _OPEN:
                    # structural dash: CH3-CH2-OH
                    if "hyphen(s) read as bond dashes (CH3-CH2-OH style), not charges" not in self.notes:
                        self.notes.append("hyphen(s) read as bond dashes (CH3-CH2-OH style), not charges")
                    self.i += 1
                    continue
                charge += self._read_charge()
                continue
            if ch.isupper():
                m = _ELEMENT_RE.match(self.s, self.i)
                if m is None:
                    # `ch.isupper()` is true for every uppercase code point in
                    # Unicode, but _ELEMENT_RE is ASCII-only. Formulas pasted
                    # from PDFs and web pages routinely carry homoglyphs -- a
                    # Cyrillic 'С' (U+0421) looks identical to Latin 'C'. Name
                    # the character rather than crashing, so the user can see
                    # what is actually in their string.
                    self._err(
                        "non-ASCII character %r (U+%04X) where an element symbol was "
                        "expected -- this looks like a Latin letter but is not one. "
                        "Retype the formula in plain ASCII." % (ch, ord(ch)))
                sym = m.group(0)
                if sym not in ELEMENTS:
                    if len(sym) == 2 and sym[0] in ELEMENTS:
                        self._err(f"unknown element symbol {sym!r} (did you mean {sym[0]!r} followed by {sym[1]!r}? symbols are case-sensitive)")
                    self._err(f"unknown element symbol {sym!r}")
                self.i = m.end()
                n = 1
                m2 = _INT_RE.match(self.s, self.i)
                if m2:
                    n = int(m2.group(0))
                    if n == 0:
                        self._err(f"element count 0 after {sym!r} (decimal / non-stoichiometric counts are not supported)")
                    self.i = m2.end()
                    # Digits glued to an element and followed by a bare terminal sign:
                    # "Fe3+" (single element) or "SO42-" (two+ digits) are ambiguous
                    # between count and charge magnitude; "NH4+" / "NO3-" (polyatomic,
                    # one digit) are read as count + charge 1.
                    sign, after = self._peek(), self._peek(1)
                    terminal = sign in ("+", "-") and (after == "" or after.isspace() or after in _SEPARATORS
                                                       or after in _CLOSE or after == sign)
                    if terminal and ((not counts and depth == 0) or len(m2.group(0)) > 1):
                        d = m2.group(0)
                        split = (f", {sym}{d[:-1]}^{d[-1]}{sign} for {d[:-1]} atoms with a {d[-1]}{sign} charge"
                                 if len(d) > 1 else "")
                        self._err(f"ambiguous {sym}{d}{sign}: write {sym}^{d}{sign} for a {d}{sign} charge{split}, "
                                  f"or ({sym}{d}){sign} for {d} atoms with charge {sign}1")
                counts[sym] = counts.get(sym, 0.0) + n
                continue
            if ch.isdigit():
                self._err(f"unexpected number {ch!r} (a count must follow an element or a closing bracket"
                          "; isotope labels such as [13C] are not supported)")
            if ch.islower():
                self._err(f"unexpected character {ch!r} (element symbols start with a capital letter)")
            self._err(f"unexpected character {ch!r}")
        return counts, charge

    def _group(self, counts, depth):
        open_ch = self.s[self.i]
        close_ch = _OPEN[open_ch]
        # a parenthesised charge: (2-) (+) (3+)
        m = re.compile(re.escape(open_ch) + r"\s*(?:(\d+)\s*([+-])|([+-])\s*(\d*))\s*" + re.escape(close_ch)).match(self.s, self.i)
        if m:
            self.i += 1
            q = self._read_charge()
            self._skip_ws()
            self.i += 1
            counts["__charge__"] = counts.get("__charge__", 0.0) + q
            return
        self.i += 1
        if self._peek().isdigit():
            self._err(f"leading number inside {open_ch}...{close_ch} (isotope labels such as [13C] are not supported)")
        inner, q = self._sequence(depth + 1)
        if self.i >= len(self.s) or self.s[self.i] != close_ch:
            got = self.s[self.i] if self.i < len(self.s) else "end of formula"
            self._err(f"unbalanced brackets: {open_ch!r} is not closed by {close_ch!r} (found {got!r})")
        self.i += 1
        mult = 1
        q_after = 0
        m2 = _INT_RE.match(self.s, self.i)
        sign = self.s[m2.end():m2.end() + 1] if m2 else ""
        if m2 and sign in ("+", "-") and not self.s[m2.end() + 1:m2.end() + 2].isdigit():
            # "]4-" / ")2-": a single digit + sign is a charge; more digits are ambiguous
            if len(m2.group(0)) == 1:
                q_after = self._read_charge()
            else:
                self._err(f"ambiguous {close_ch}{m2.group(0)}{sign}: write {close_ch}^{m2.group(0)}{sign} "
                          f"for a charge, or put a space between the group multiplier and the charge")
        elif m2:
            mult = int(m2.group(0))
            if mult == 0:
                self._err("group multiplier 0")
            self.i = m2.end()
        if not inner and not q:
            self._err(f"empty brackets {open_ch}{close_ch}")
        for el, n in inner.items():
            counts[el] = counts.get(el, 0.0) + mult * n
        if q or q_after:
            counts["__charge__"] = counts.get("__charge__", 0.0) + mult * q + q_after


def _num(x):
    """Return int for integral floats, else float rounded to 6 decimals."""
    if isinstance(x, float) and abs(x - round(x)) < 1e-9:
        return int(round(x))
    if isinstance(x, float):
        return round(x, 6)
    return x


def _hill_sorted(counts):
    """Hill order: C, H first when carbon is present; else alphabetical."""
    items = [(el, n) for el, n in counts.items() if el != "__charge__"]
    if "C" in counts:
        head = [(el, n) for el, n in items if el in ("C", "H")]
        head.sort(key=lambda t: 0 if t[0] == "C" else 1)
        tail = sorted((el, n) for el, n in items if el not in ("C", "H"))
        return head + tail
    return sorted(items)


def hill_formula(counts):
    parts = []
    for el, n in _hill_sorted(counts):
        n = _num(n)
        parts.append(el if n == 1 else f"{el}{n}")
    return "".join(parts)


def charge_string(z):
    z = _num(z)
    if z == 0:
        return "0"
    mag = abs(z)
    return ("" if mag == 1 else str(mag)) + ("+" if z > 0 else "-")


def parse_formula(text):
    """Parse a formula string.  Returns dict with keys
    input, formula (Hill), counts (Hill-ordered dict), charge, atoms,
    components (list), notes (list).  Raises FormulaError."""
    p = _Parser(text)
    total, charge, components = p.parse()
    counts = {el: _num(n) for el, n in _hill_sorted(total)}
    return {
        "input": text,
        "formula": hill_formula(total),
        "counts": counts,
        "charge": _num(charge),
        "atoms": _num(sum(total.values())),
        "components": components,
        "notes": list(p.notes),
    }


# ---------------------------------------------------------------------------
# The arithmetic (SKILL.md steps 3-5)
# ---------------------------------------------------------------------------


def _is_int(x, eps=1e-9):
    return abs(x - round(x)) < eps


def compute(parsed):
    """Attach masses, composition, RDBE, nitrogen rule and Lipinski subset."""
    counts = parsed["counts"]
    z = parsed["charge"]
    mw = sum(n * ELEMENTS[el][2] for el, n in counts.items())
    mono = sum(n * ELEMENTS[el][4] for el, n in counts.items())
    nominal = sum(n * ELEMENTS[el][3] for el, n in counts.items())
    rows = []
    for el, n in counts.items():
        Z, name, ar, A, m, note = ELEMENTS[el]
        rows.append({
            "element": el, "count": n, "atomic_weight": ar, "mass": round(n * ar, 6),
            "percent": round(100.0 * n * ar / mw, 4) if mw else 0.0,
            "isotope": f"{A}{el if el not in ('D', 'T') else 'H'}", "isotope_mass": m,
            "note": note,
        })
    conv = sorted(el for el in counts if ELEMENTS[el][5] == "conv")
    radio = sorted(el for el in counts if ELEMENTS[el][5] == "radio")
    weight_notes = []
    if conv:
        weight_notes.append("IUPAC conventional atomic weight used for interval element(s) " + ", ".join(conv))
    if radio:
        weight_notes.append("no standard atomic weight for " + ", ".join(radio) +
                            ": mass of the longest-lived isotope used")

    # RDBE ------------------------------------------------------------------
    outside = sorted(el for el in counts if el not in RDBE_VALENCE)
    rdbe = {"applicable": not outside}
    if outside:
        rdbe.update({"value": None, "status": "not_applicable",
                     "note": "not applicable: contains " + ", ".join(outside) +
                             " (outside the C/H/N/O/S/P/Si/B/Se/As/halogen valence convention)"})
    else:
        def get(*els):
            return sum(counts.get(e, 0) for e in els)
        c, si, n_, p, b, as_ = get("C"), get("Si"), get("N"), get("P"), get("B"), get("As")
        h = get("H", "D", "T")
        x = get(*HALOGENS)
        value = 1.0 + 0.5 * sum(n * (RDBE_VALENCE[el] - 2) for el, n in counts.items())
        expr = f"{_num(c)} + {_num(si)} + 1 + ({_num(n_)} + {_num(p)})/2 - ({_num(h)} + {_num(x)})/2"
        extra = []
        if b:
            extra.append(f"+ {_num(b)}/2 (B)")
        if as_:
            extra.append(f"+ {_num(as_)}/2 (As)")
        if extra:
            expr += " " + " ".join(extra)
        rdbe["value"] = _num(value)
        rdbe["expression"] = f"C + Si + 1 + (N + P)/2 - (H + X)/2 = {expr} = {_num(value)}"
        if z == 0:
            if value < 0:
                rdbe["status"] = "negative"
                rdbe["note"] = "negative: impossible formula (more H/halogen than the heavy atoms can bond)"
            elif not _is_int(value):
                rdbe["status"] = "half_integer"
                rdbe["note"] = ("half-integer: not a neutral closed-shell molecule "
                                "(radical, ion with omitted charge, or corrupt formula)")
            else:
                rdbe["status"] = "ok"
                rdbe["note"] = "integer >= 0: consistent with a neutral closed-shell molecule"
        else:
            adj = value + z / 2.0
            rdbe["adjusted_for_charge"] = _num(adj)
            if adj < 0:
                rdbe["status"] = "negative"
                rdbe["note"] = f"adjusted for charge ({charge_string(z)}, even-electron ion): {_num(adj)} < 0 -> impossible formula"
            elif not _is_int(adj):
                rdbe["status"] = "half_integer"
                rdbe["note"] = (f"adjusted for charge ({charge_string(z)}, even-electron ion): {_num(adj)} is not an integer "
                                "-> odd-electron (radical) ion or corrupt formula")
            else:
                rdbe["status"] = "ok"
                rdbe["note"] = f"adjusted for charge ({charge_string(z)}, even-electron ion): {_num(adj)} -> consistent"

    # Nitrogen rule -----------------------------------------------------------
    nrule = {}
    if z != 0:
        nrule = {"applicable": False, "note": "not applied to ions (the rule flips for even-electron ions)"}
    elif not set(counts) <= NITROGEN_RULE_ELEMENTS:
        nrule = {"applicable": False, "note": "not applied: formula contains elements outside C/H/N/O/S/P/Si/B/Se/As/halogens"}
    elif not _is_int(nominal):
        nrule = {"applicable": False, "note": "not applied: fractional composition"}
    else:
        n_count = int(round(counts.get("N", 0)))
        nom = int(round(nominal))
        ok = (nom % 2) == (n_count % 2)
        nrule = {"applicable": True, "consistent": ok,
                 "note": (f"nominal mass {nom} is {'odd' if nom % 2 else 'even'} and N count {n_count} is "
                          f"{'odd' if n_count % 2 else 'even'} -> " + ("consistent" if ok else "VIOLATED (corrupt formula)"))}

    # Lipinski assessable subset -----------------------------------------------
    n_o = _num(counts.get("N", 0) + counts.get("O", 0))
    lip = {"applicable": "C" in counts, "mw_ok": mw <= 500.0, "n_plus_o": n_o, "n_plus_o_ok": n_o <= 10,
           "assessable_violations": int(mw > 500.0) + int(n_o > 10),
           "not_assessable": ["H-bond donors (OH + NH)", "logP"]}

    # MS quantities: m/z for ions; common ESI adducts for single-component
    # neutral organic formulas (meaningless for salts/hydrates, so omitted)
    ms = {}
    if z != 0:
        ms = {"m/z": round((mono - z * ELECTRON_MASS) / abs(z), 6)}
    elif "C" in counts and len(parsed["components"]) == 1:
        ms = {"[M+H]+": round(mono + PROTON_MASS, 6),
              "[M+Na]+": round(mono + ELEMENTS["Na"][4] - ELECTRON_MASS, 6),
              "[M-H]-": round(mono - PROTON_MASS, 6)}

    return {
        "input": parsed["input"], "formula": parsed["formula"], "charge": z,
        "charge_string": charge_string(z), "atoms": parsed["atoms"],
        "counts": counts, "components": parsed["components"], "parse_notes": parsed["notes"],
        "average_mw": round(mw, 4), "monoisotopic_mass": round(mono, 6), "nominal_mass": _num(nominal),
        "elements": rows, "atomic_weight_notes": weight_notes,
        "rdbe": rdbe, "nitrogen_rule": nrule, "lipinski": lip, "ms": ms,
    }


def analyze(text):
    """parse + compute; raises FormulaError."""
    return compute(parse_formula(text))


# ---------------------------------------------------------------------------
# Name lookup (SKILL.md step 2)
# ---------------------------------------------------------------------------


def normalize_name(name):
    """Case-, space-, hyphen- and punctuation-insensitive key: 'Acetyl-Salicylic Acid'
    and 'acetylsalicylic acid' both map to 'acetylsalicylicacid'."""
    return re.sub(r"[^a-z0-9]+", "", str(name).lower())


_NAME_INDEX = None
_FORMULA_INDEX = None


def lookup_name(name):
    """Return the canonical formula string for a well-known compound, or None."""
    global _NAME_INDEX
    if _NAME_INDEX is None:
        _NAME_INDEX = {normalize_name(k): v for k, v in sorted(KNOWN_COMPOUNDS.items())}
    return _NAME_INDEX.get(normalize_name(name))


def names_for_formula(hill, charge):
    """Reverse lookup: which table compounds have this composition + charge."""
    global _FORMULA_INDEX
    if _FORMULA_INDEX is None:
        _FORMULA_INDEX = {}
        for nm in sorted(KNOWN_COMPOUNDS):
            p = parse_formula(KNOWN_COMPOUNDS[nm])
            _FORMULA_INDEX.setdefault((p["formula"], p["charge"]), []).append(nm)
    return _FORMULA_INDEX.get((hill, charge), [])


# ---------------------------------------------------------------------------
# check: verdicts against claimed values
# ---------------------------------------------------------------------------

_NUM_RE = re.compile(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def parse_claimed_number(raw, what):
    """Accept 194, '194', '194.19 g/mol', '~500 Da', '≈ 762'.
    Returns (value, half_unit_of_last_digit, number_as_written)."""
    if raw is None:
        return None, None, None
    if isinstance(raw, bool):
        raise ValueError(f"{what}: expected a number, got a boolean")
    if isinstance(raw, (int, float)):
        s = repr(raw)
    else:
        s = str(raw)
    m = _NUM_RE.search(s.replace(",", ""))
    if not m:
        raise ValueError(f"{what}: no number found in {raw!r}")
    tok = m.group(0)
    value = float(tok)
    mant = tok.lower().split("e")[0]
    decimals = len(mant.split(".")[1]) if "." in mant else 0
    return value, 0.5 * 10.0 ** (-decimals), tok


def _tol_text(tol):
    return f"{tol:.4g}"


def run_check(claim, mw_tol_pct=0.05, mono_tol_ppm=10.0, comp_tol=0.4):
    """Evaluate one claim dict.  Returns a result dict (never raises for
    verdicts; raises FormulaError/ValueError for unusable input)."""
    name = claim.get("name")
    formula_txt = claim.get("formula")
    checks = []

    canonical = lookup_name(name) if name else None
    if not formula_txt:
        if canonical:
            formula_txt = canonical
            checks.append({"item": "formula source", "verdict": "NOTE",
                           "detail": f"no formula claimed; using the built-in canonical formula for {name}: {canonical}"})
        else:
            raise ValueError("a formula is required (or a name from the built-in table)")
    res = analyze(formula_txt)
    hill, z = res["formula"], res["charge"]

    # 1. name vs formula ------------------------------------------------------
    if name and claim.get("formula"):
        if canonical is None:
            checks.append({"item": "name vs formula", "verdict": "UNVERIFIED",
                           "detail": f"{name!r} is not in the built-in table of {len(KNOWN_COMPOUNDS)} well-known "
                                     "compounds; do not guess — re-source from primary literature"})
        else:
            can = parse_formula(canonical)
            if can["formula"] == hill and can["charge"] == z:
                checks.append({"item": "name vs formula", "verdict": "PASS",
                               "detail": f"{res['input']} matches {name} ({can['formula']}"
                                         + (f", charge {charge_string(can['charge'])}" if can["charge"] else "")
                                         + ", built-in table)"})
            else:
                others = [n for n in names_for_formula(hill, z) if normalize_name(n) != normalize_name(name)]
                hint = f" = {', '.join(others)}" if others else ""
                claimed = res["input"] + (f" ({hill})" if res["input"].strip() != hill else "")
                checks.append({"item": "name vs formula", "verdict": "FAIL",
                               "detail": f"{name} is {can['formula']}"
                                         + (f" ({charge_string(can['charge'])})" if can["charge"] else "")
                                         + f"; claimed {claimed}{hint}"})

    # 2. formula plausibility (RDBE / nitrogen rule) ----------------------------
    rd = res["rdbe"]
    if not rd["applicable"]:
        checks.append({"item": "formula plausibility", "verdict": "NOTE", "detail": "RDBE " + rd["note"]})
    else:
        nr = res["nitrogen_rule"]
        nr_txt = ""
        if nr.get("applicable"):
            nom = res["nominal_mass"]
            n_count = res["counts"].get("N", 0)
            nr_txt = (f"; nitrogen rule {'OK' if nr['consistent'] else 'VIOLATED'} "
                      f"(nominal {nom} {'odd' if nom % 2 else 'even'}, N {n_count} {'odd' if n_count % 2 else 'even'})")
        verdict = "PASS" if rd["status"] == "ok" else "FAIL"
        short = {"ok": "integer, >= 0", "negative": "NEGATIVE: impossible, too many H/halogen for the heavy atoms",
                 "half_integer": "HALF-INTEGER: radical, ion with omitted charge, or corrupt formula"}[rd["status"]]
        if z != 0:
            short = f"{rd['adjusted_for_charge']} after the {charge_string(z)} even-electron adjustment: {short}"
        checks.append({"item": "formula plausibility", "verdict": verdict,
                       "detail": f"RDBE = {rd['expression'].split(' = ', 1)[1]} ({short}){nr_txt}"})

    # 3. molecular weight ---------------------------------------------------------
    mw_raw = claim.get("mw")
    if mw_raw is not None:
        val, half, tok = parse_claimed_number(mw_raw, "mw")
        comp = res["average_mw"]
        tol = max(comp * mw_tol_pct / 100.0, half)
        diff = val - comp
        pct = 100.0 * diff / comp if comp else float("inf")
        ok = abs(diff) <= tol + 1e-12
        if ok:
            hint = ""
        elif abs(pct) > 10:
            hint = " -- >10 % off: wrong compound, or a salt/hydrate weight with the free-base formula"
        elif abs(pct) > 1:
            hint = " -- 1-10 % off: salt / hydrate / free-base mix-up?"
        else:
            hint = " -- <1 % off: rounding or atomic-weight convention, but outside tolerance"
        checks.append({"item": "molecular weight", "verdict": "PASS" if ok else "FAIL",
                       "detail": f"computed {comp:.3f} vs stated {tok} g/mol "
                                 f"({diff:+.3f}, {pct:+.2f} %; tol {_tol_text(tol)}){hint}"})

    # 4. exact / monoisotopic mass -------------------------------------------------
    em_raw = claim.get("exact_mass")
    if em_raw is not None:
        val, half, tok = parse_claimed_number(em_raw, "exact_mass")
        comp = res["monoisotopic_mass"]
        tol = max(comp * mono_tol_ppm * 1e-6, half)
        diff = val - comp
        ppm = 1e6 * diff / comp if comp else float("inf")
        ok = abs(diff) <= tol + 1e-12
        hint = ""
        if not ok and abs(val - res["average_mw"]) <= max(res["average_mw"] * mw_tol_pct / 100.0, half):
            hint = " -- the stated value matches the AVERAGE molecular weight, not the monoisotopic mass"
        checks.append({"item": "exact mass", "verdict": "PASS" if ok else "FAIL",
                       "detail": f"computed monoisotopic {comp:.6f} vs stated {tok} Da "
                                 f"({diff:+.6f}, {ppm:+.1f} ppm; tol {_tol_text(tol)}){hint}"})

    # 5. RDBE claim -----------------------------------------------------------------
    rdbe_raw = claim.get("rdbe")
    if rdbe_raw is not None:
        val, _, tok = parse_claimed_number(rdbe_raw, "rdbe")
        if not rd["applicable"]:
            checks.append({"item": "RDBE claim", "verdict": "UNVERIFIED", "detail": "RDBE " + rd["note"]})
        else:
            comp = rd["value"]
            ok = abs(val - comp) < 1e-9
            checks.append({"item": "RDBE claim", "verdict": "PASS" if ok else "FAIL",
                           "detail": f"computed RDBE {comp} vs stated {tok}"})

    # 6. composition ------------------------------------------------------------------
    comp_claim = claim.get("composition")
    if comp_claim:
        if isinstance(comp_claim, str):
            comp_claim = parse_composition_string(comp_claim)
        pct = {r["element"]: r["percent"] for r in res["elements"]}
        for el in sorted(comp_claim):
            val, half, tok = parse_claimed_number(comp_claim[el], f"composition[{el}]")
            if el not in pct:
                checks.append({"item": f"composition {el}", "verdict": "FAIL",
                               "detail": f"{el} is not in the formula {hill} (stated {tok} %)"})
                continue
            tol = max(comp_tol, half)
            diff = val - pct[el]
            ok = abs(diff) <= tol + 1e-12
            checks.append({"item": f"composition {el}", "verdict": "PASS" if ok else "FAIL",
                           "detail": f"computed {pct[el]:.2f} vs stated {tok} % ({diff:+.2f}; tol {_tol_text(tol)})"})

    # 7. Lipinski assessable subset -----------------------------------------------------
    lip = res["lipinski"]
    druglike = bool(claim.get("druglike"))
    if not lip["applicable"]:
        checks.append({"item": "Lipinski (assessable subset)", "verdict": "NOTE",
                       "detail": "not applicable (no carbon: not a small-molecule drug candidate)"
                                 + ("; the 'drug-like' assertion cannot be assessed" if druglike else "")})
        n_fail = sum(1 for c in checks if c["verdict"] == "FAIL")
        n_scored = sum(1 for c in checks if c["verdict"] in ("PASS", "FAIL"))
        return {"claim": claim, "computed": res, "checks": checks,
                "result": "FAIL" if n_fail else "PASS", "n_fail": n_fail, "n_scored": n_scored}
    parts = [f"MW {res['average_mw']:.2f} {'<=' if lip['mw_ok'] else '>'} 500 {'OK' if lip['mw_ok'] else 'VIOLATION'}",
             f"N+O = {lip['n_plus_o']} {'<=' if lip['n_plus_o_ok'] else '>'} 10 {'OK' if lip['n_plus_o_ok'] else 'VIOLATION'}",
             "donors/logP need a structure"]
    v = lip["assessable_violations"]
    if druglike:
        tail = (" -> drug-like claim consistent with the assessable subset" if v == 0 else
                f" -> {v} violation(s): 'drug-like/orally bioavailable' carries an elevated burden of proof "
                "(confidence modifier, not a verdict)")
    else:
        tail = f" -> {v} assessable violation(s)"
    checks.append({"item": "Lipinski (assessable subset)", "verdict": "NOTE", "detail": "; ".join(parts) + tail})

    n_fail = sum(1 for c in checks if c["verdict"] == "FAIL")
    n_scored = sum(1 for c in checks if c["verdict"] in ("PASS", "FAIL"))
    return {"claim": claim, "computed": res, "checks": checks,
            "result": "FAIL" if n_fail else "PASS", "n_fail": n_fail, "n_scored": n_scored}


def parse_composition_string(text):
    """'C:49.48,H:5.19' or 'C 49.48 H 5.19' -> {'C': 49.48, 'H': 5.19}."""
    out = {}
    for m in re.finditer(r"([A-Z][a-z]?)\s*[:=]?\s*([-+]?\d+(?:\.\d+)?)\s*%?", text):
        out[m.group(1)] = float(m.group(2))
    if not out:
        raise ValueError(f"could not read a composition from {text!r} (use 'C:49.48,H:5.19')")
    return out


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_formula(res):
    lines = []
    lines.append(f"Formula: {res['formula']}" + (f"  charge {res['charge_string']}" if res["charge"] else "")
                 + (f"   (input: {res['input']})" if res["input"].strip() != res["formula"] else ""))
    if len(res["components"]) > 1:
        comps = " + ".join((f"{c['multiplier']} " if c["multiplier"] != 1 else "") + c["formula"]
                           + (f"({charge_string(c['charge'])})" if c["charge"] else "") for c in res["components"])
        lines.append(f"Components: {comps}")
    for n in res["parse_notes"]:
        lines.append(f"Note: {n}")
    els = ", ".join(f"{el} {n}" for el, n in res["counts"].items())
    lines.append(f"Elements (Hill order): {els}   [{res['atoms']} atoms]")
    lines.append(f"Average molecular weight: {res['average_mw']:.3f} g/mol")
    for n in res["atomic_weight_notes"]:
        lines.append(f"  ({n})")
    lines.append(f"Monoisotopic mass:        {res['monoisotopic_mass']:.6f} Da")
    lines.append(f"Nominal mass:             {res['nominal_mass']}")
    lines.append(f"  {'El':<4}{'count':>7}{'at. wt':>10}{'mass':>12}{'mass %':>9}   most abundant isotope")
    for r in res["elements"]:
        lines.append(f"  {r['element']:<4}{r['count']:>7}{r['atomic_weight']:>10}{r['mass']:>12.3f}{r['percent']:>9.2f}"
                     f"   {r['isotope']:<6}{r['isotope_mass']:.6f}")
    rd = res["rdbe"]
    if rd["applicable"]:
        lines.append(f"RDBE = {rd['expression']} -> {rd['note']}")
    else:
        lines.append(f"RDBE: {rd['note']}")
    lines.append(f"Nitrogen rule: {res['nitrogen_rule']['note']}")
    lip = res["lipinski"]
    if lip["applicable"]:
        lines.append(f"Lipinski (assessable subset): MW {res['average_mw']:.2f} {'<=' if lip['mw_ok'] else '>'} 500 "
                     f"{'OK' if lip['mw_ok'] else 'VIOLATION'}; N+O = {lip['n_plus_o']} {'<=' if lip['n_plus_o_ok'] else '>'} 10 "
                     f"{'OK' if lip['n_plus_o_ok'] else 'VIOLATION'}; donors/logP need a structure")
    else:
        lines.append("Lipinski (assessable subset): not applicable (no carbon: not a small-molecule drug candidate)")
    if res["charge"]:
        lines.append(f"m/z (electron-mass corrected): {res['ms']['m/z']:.6f}")
    elif res["ms"]:
        lines.append("MS adducts (monoisotopic): " + "   ".join(f"{k} {v:.6f}" for k, v in res["ms"].items()))
    return "\n".join(lines)


def render_check(result):
    claim = result["claim"]
    res = result["computed"]
    head = []
    if claim.get("name"):
        head.append(str(claim["name"]))
    head.append(str(claim.get("formula") or res["formula"]))
    if claim.get("mw") is not None:
        head.append(f"MW {claim['mw']}")
    if claim.get("exact_mass") is not None:
        head.append(f"exact mass {claim['exact_mass']}")
    if claim.get("rdbe") is not None:
        head.append(f"RDBE {claim['rdbe']}")
    if claim.get("composition"):
        head.append("composition")
    if claim.get("druglike"):
        head.append('"drug-like"')
    lines = ["Claim: " + " -- ".join(head)]
    lines.append(f"Computed: {res['formula']}" + (f" ({res['charge_string']})" if res["charge"] else "")
                 + f"  MW {res['average_mw']:.3f} g/mol  monoisotopic {res['monoisotopic_mass']:.6f} Da"
                 + (f"  RDBE {res['rdbe']['value']}" if res["rdbe"]["applicable"] else ""))
    for n in res["parse_notes"]:
        lines.append(f"Note: {n}")
    for c in result["checks"]:
        lines.append(f"{c['verdict']:<10} {c['item']:<28} {c['detail']}")
    if result["n_fail"]:
        lines.append(f"RESULT: FAIL ({result['n_fail']} of {result['n_scored']} checks failed) -- re-source before use")
    else:
        lines.append(f"RESULT: PASS ({result['n_scored']} checks; NOTE/UNVERIFIED items are not verdicts)")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

DEMO_CLAIMS = [
    {"name": "caffeine", "formula": "C8H10N4O2", "mw": "312 g/mol", "druglike": True},
    {"formula": "C39H47N5O9S", "mw": "≈ 762", "druglike": True},
    {"name": "ethanol", "formula": "C2H6O2"},
]

CLAIM_KEYS = {
    "name": ("name", "compound"),
    "formula": ("formula", "molecular_formula", "molecularformula"),
    "mw": ("mw", "molecular_weight", "molecularweight", "molar_mass", "molarmass"),
    "exact_mass": ("exact_mass", "exactmass", "monoisotopic_mass", "monoisotopicmass", "mono"),
    "rdbe": ("rdbe", "dbe", "degree_of_unsaturation", "unsaturation"),
    "composition": ("composition", "mass_percent", "masspercent", "elemental_analysis"),
    "druglike": ("druglike", "drug_like", "lipinski", "orally_bioavailable"),
}


def normalize_claim(raw):
    """Map synonyms / camelCase keys to the canonical claim keys."""
    if not isinstance(raw, dict):
        raise ValueError("each claim must be a JSON object")
    low = {re.sub(r"[\s\-]", "_", str(k)).lower(): v for k, v in raw.items()}
    claim = {}
    for canon, alts in CLAIM_KEYS.items():
        for a in alts:
            if a in low and low[a] is not None and low[a] != "":
                claim[canon] = low[a]
                break
    return claim


def load_claims(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "claims" in data:
        data = data["claims"]
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not data:
        raise ValueError("claim file must hold a JSON object or a non-empty list of objects")
    return [normalize_claim(d) for d in data]


def cmd_formula(args, parser):
    inputs = []
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            inputs = [ln.strip() for ln in fh if ln.strip() and not ln.lstrip().startswith("#")]
        if not inputs:
            parser.error(f"{args.file}: no formulas found")
    if args.formula is not None:
        inputs.append(args.formula)
    if not inputs:
        parser.error("give a FORMULA or --file")
    results = []
    for f in inputs:
        try:
            results.append(analyze(f))
        except FormulaError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    if args.json:
        print(json.dumps(results[0] if len(results) == 1 else results, indent=2, ensure_ascii=False))
    else:
        print("\n\n".join(render_formula(r) for r in results))
    return 0


def cmd_check(args, parser):
    claims = []
    if args.file:
        try:
            claims = load_claims(args.file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.error(f"could not load {args.file}: {exc}")
    flag_claim = {}
    for key in ("name", "formula", "mw", "exact_mass", "rdbe", "composition"):
        v = getattr(args, key)
        if v is not None:
            flag_claim[key] = v
    if args.druglike:
        flag_claim["druglike"] = True
    if flag_claim:
        if len(claims) == 1:
            claims[0].update(flag_claim)      # flags override the file
        elif not claims:
            claims = [flag_claim]
        else:
            parser.error("flags cannot be combined with a multi-claim file")
    if not claims:
        parser.error("pass --file claim.json or --formula/--name with the claimed values")
    results = []
    for c in claims:
        try:
            results.append(run_check(c, args.mw_tol, args.mono_tol, args.comp_tol))
        except (FormulaError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    if args.json:
        print(json.dumps(results[0] if len(results) == 1 else results, indent=2, ensure_ascii=False))
    else:
        print("\n\n".join(render_check(r) for r in results))
    return 1 if any(r["n_fail"] for r in results) else 0


def run_demo():
    print("Worked example from SKILL.md (steps 4-6): claims as they appear in a signal or patent.\n")
    for i, claim in enumerate(DEMO_CLAIMS):
        if i:
            print()
        print(render_check(run_check(claim)))
    print("\nFormula breakdown (SKILL.md step 4):\n")
    print(render_formula(analyze("C8H10N4O2")))
    print("\n(As a real `check`, the first and third claims would exit with code 2.)")
    return 0


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------


def run_selftest():
    """Hand-verified reference values (see docstring for sources)."""
    n_ok = 0
    n_all = 0

    def check(name, got, want, tol=0.0):
        nonlocal n_ok, n_all
        n_all += 1
        if isinstance(want, (int, float)) and not isinstance(want, bool) and isinstance(got, (int, float)):
            ok = abs(got - want) <= tol
        else:
            ok = got == want
        n_ok += ok
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got!r}, expected {want!r}" + (f" (tol {tol})" if tol else ""))
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    def expect_error(name, text, fragment):
        nonlocal n_ok, n_all
        n_all += 1
        try:
            parse_formula(text)
        except FormulaError as exc:
            ok = fragment in str(exc)
            n_ok += ok
            print(f"{'PASS' if ok else 'FAIL'}  {name}: {text!r} -> {exc}")
            if not ok:
                sys.exit(1)
            return
        print(f"FAIL  {name}: {text!r} parsed without error", file=sys.stderr)
        sys.exit(1)

    # -- molecular weights: PubChem MW to two decimals; tolerance 0.02 covers
    #    PubChem's interval-midpoint sulfur (see docstring)
    for f, want, tol in [("H2O", 18.015, 0.02), ("C6H12O6", 180.156, 0.02), ("C8H10N4O2", 194.19, 0.02),
                         ("C9H8O4", 180.16, 0.02), ("C13H18O2", 206.28, 0.02), ("NaCl", 58.44, 0.02),
                         ("CuSO4·5H2O", 249.69, 0.02), ("SO4 2-", 96.06, 0.02), ("[Fe(CN)6]4-", 211.95, 0.02),
                         ("C19H25BN4O4", 384.2, 0.05), ("Ca(OH)2", 74.09, 0.02), ("C6H6", 78.11, 0.02)]:
        check(f"MW {f}", analyze(f)["average_mw"], want, tol)
    # exact hand sums with the tabulated weights
    check("MW caffeine = 8*12.011 + 10*1.008 + 4*14.007 + 2*15.999", analyze("C8H10N4O2")["average_mw"], 194.194, 1e-9)
    check("MW C39H47N5O9S (SKILL Lipinski example ~762)", analyze("C39H47N5O9S")["average_mw"], 761.891, 1e-9)

    # -- monoisotopic masses (PubChem MonoisotopicMass)
    for f, want in [("H2O", 18.010565), ("C8H10N4O2", 194.080376), ("C9H8O4", 180.042259),
                    ("C13H18O2", 206.130680), ("NaCl", 57.958622), ("CuSO4·5H2O", 248.934150),
                    ("SO4^2-", 95.951730), ("[Fe(CN)6]4-", 211.953380), ("C19H25BN4O4", 384.196886)]:
        check(f"monoisotopic {f}", analyze(f)["monoisotopic_mass"], want, 2e-6)
    check("nominal mass caffeine", analyze("C8H10N4O2")["nominal_mass"], 194)
    check("nominal mass CHCl3 uses 35Cl", analyze("CHCl3")["nominal_mass"], 118)
    check("[M+H]+ caffeine", analyze("C8H10N4O2")["ms"]["[M+H]+"], 195.087652, 2e-6)
    check("m/z of SO4 2- (electron corrected)", analyze("SO4^2-")["ms"]["m/z"], 47.976413, 2e-6)

    # -- RDBE / degree of unsaturation
    for f, want in [("C8H10N4O2", 6), ("C9H8O4", 6), ("C13H18O2", 5), ("C6H6", 4), ("C2H6O", 0),
                    ("C2H7N", 0), ("C2H8O", -1), ("CH3", 0.5), ("C19H25BN4O4", 10), ("CHCl3", 0),
                    ("C39H47N5O9S", 19)]:
        check(f"RDBE {f}", analyze(f)["rdbe"]["value"], want, 1e-9)
    check("RDBE status C2H8O", analyze("C2H8O")["rdbe"]["status"], "negative")
    check("RDBE status CH3 (radical)", analyze("CH3")["rdbe"]["status"], "half_integer")
    check("RDBE status caffeine", analyze("C8H10N4O2")["rdbe"]["status"], "ok")
    check("RDBE NH4+ adjusted for charge", analyze("NH4+")["rdbe"]["adjusted_for_charge"], 0)
    check("RDBE NH4+ status", analyze("NH4+")["rdbe"]["status"], "ok")
    check("RDBE not applicable with metals", analyze("CuSO4·5H2O")["rdbe"]["status"], "not_applicable")

    # -- nitrogen rule
    check("nitrogen rule caffeine (194 even, N4)", analyze("C8H10N4O2")["nitrogen_rule"]["consistent"], True)
    check("nitrogen rule pyridine (79 odd, N1)", analyze("C5H5N")["nitrogen_rule"]["consistent"], True)
    check("nitrogen rule CH3 (15 odd, N0) violated", analyze("CH3")["nitrogen_rule"]["consistent"], False)

    # -- composition (caffeine: C 49.48, H 5.19, N 28.85, O 16.48)
    pct = {r["element"]: r["percent"] for r in analyze("C8H10N4O2")["elements"]}
    for el, want in [("C", 49.48), ("H", 5.19), ("N", 28.85), ("O", 16.48)]:
        check(f"mass % {el} in caffeine", pct[el], want, 0.005)
    check("mass % sums to 100", sum(pct.values()), 100.0, 1e-6)

    # -- parsing
    check("Hill order NaCl -> ClNa", parse_formula("NaCl")["formula"], "ClNa")
    check("Hill order CuSO4·5H2O -> CuH10O9S", parse_formula("CuSO4·5H2O")["formula"], "CuH10O9S")
    check("dot / star / space hydrate spellings agree",
          [parse_formula(f)["counts"] for f in ("CuSO4.5H2O", "CuSO4*5H2O", "CuSO4 5H2O")],
          [parse_formula("CuSO4·5H2O")["counts"]] * 3)
    check("nested brackets K4[Fe(CN)6]", parse_formula("K4[Fe(CN)6]")["counts"], {"C": 6, "Fe": 1, "K": 4, "N": 6})
    check("charge [Fe(CN)6]4-", parse_formula("[Fe(CN)6]4-")["charge"], -4)
    check("charge SO4 2- / SO4^2- / (SO4)2- / SO4(2-) / SO₄²⁻",
          [parse_formula(f)["charge"] for f in ("SO4 2-", "SO4^2-", "(SO4)2-", "SO4(2-)", "SO₄²⁻")], [-2] * 5)
    check("charge Fe^3+ / Fe+3 / Fe³⁺", [parse_formula(f)["charge"] for f in ("Fe^3+", "Fe+3", "Fe³⁺")], [3] * 3)
    check("charge Ca++", parse_formula("Ca++")["charge"], 2)
    check("ion pair NH4+Cl- is neutral", parse_formula("NH4+Cl-")["charge"], 0)
    check("unicode subscripts C₈H₁₀N₄O₂", parse_formula("C₈H₁₀N₄O₂")["formula"], "C8H10N4O2")
    check("bond dashes CH3-CH2-OH", parse_formula("CH3-CH2-OH")["formula"], "C2H6O")
    check("hemihydrate CaSO4·0.5H2O", parse_formula("CaSO4·0.5H2O")["counts"], {"Ca": 1, "H": 1, "O": 4.5, "S": 1})
    check("case-sensitive: CO is carbon monoxide", parse_formula("CO")["counts"], {"C": 1, "O": 1})
    check("case-sensitive: Co is cobalt", parse_formula("Co")["counts"], {"Co": 1})
    check("deuterium D2O", parse_formula("D2O")["counts"], {"D": 2, "O": 1})
    check("MW D2O", analyze("D2O")["average_mw"], 20.027, 0.001)
    expect_error("unknown element", "C6H5Xx", "unknown element symbol 'Xx'")
    expect_error("unbalanced (", "Ca(OH", "unbalanced")
    expect_error("unbalanced )", "Ca(OH))2", "unbalanced")
    expect_error("mismatched [ )", "K4[Fe(CN)6)", "unbalanced")
    expect_error("ambiguous Fe3+", "Fe3+", "ambiguous")
    expect_error("ambiguous SO42-", "SO42-", "ambiguous")
    expect_error("empty", "   ", "no atoms")
    expect_error("zero count", "Fe0.95O", "count 0")
    expect_error("lowercase start", "cH4", "capital letter")
    expect_error("isotope label", "[13C]6H12O6", "isotope labels")

    # -- name lookup
    check("lookup caffeine", lookup_name("Caffeine"), "C8H10N4O2")
    check("lookup acetyl-salicylic acid (hyphen/case)", lookup_name("Acetyl-Salicylic Acid"), "C9H8O4")
    check("lookup unknown -> None", lookup_name("zorbomycin"), None)
    check("reverse lookup C2H6O2", names_for_formula("C2H6O2", 0), ["ethylene glycol"])
    n_all += 1
    for nm in sorted(KNOWN_COMPOUNDS):
        parse_formula(KNOWN_COMPOUNDS[nm])
    n_ok += 1
    print(f"PASS  all {len(KNOWN_COMPOUNDS)} built-in canonical formulas parse")

    # -- check verdicts (SKILL.md step 6 worked example)
    r = run_check({"name": "caffeine", "formula": "C8H10N4O2", "mw": 312, "druglike": True})
    v = {c["item"]: c["verdict"] for c in r["checks"]}
    check("worked example: name vs formula", v["name vs formula"], "PASS")
    check("worked example: formula plausibility", v["formula plausibility"], "PASS")
    check("worked example: MW 312 fails", v["molecular weight"], "FAIL")
    check("worked example: Lipinski is a NOTE, never a verdict", v["Lipinski (assessable subset)"], "NOTE")
    check("worked example: RESULT FAIL", r["result"], "FAIL")
    check("MW 194 (integer rounding) passes", run_check({"formula": "C8H10N4O2", "mw": "194 g/mol"})["result"], "PASS")
    check("MW 194.19 passes", run_check({"formula": "C8H10N4O2", "mw": 194.19})["result"], "PASS")
    check("MW 194.3 fails (0.05 % = 0.097; half-unit 0.05)", run_check({"formula": "C8H10N4O2", "mw": 194.3})["result"], "FAIL")
    check("MW ~762 for C39H47N5O9S passes", run_check({"formula": "C39H47N5O9S", "mw": "≈ 762"})["result"], "PASS")
    check("Lipinski example: 2 assessable violations", analyze("C39H47N5O9S")["lipinski"]["assessable_violations"], 2)
    r = run_check({"name": "ethanol", "formula": "C2H6O2"})
    check("ethanol vs C2H6O2 fails name check", r["checks"][0]["verdict"], "FAIL")
    check("...and names ethylene glycol", "ethylene glycol" in r["checks"][0]["detail"], True)
    r = run_check({"name": "zorbomycin", "formula": "C10H10"})
    check("unknown name -> UNVERIFIED", r["checks"][0]["verdict"], "UNVERIFIED")
    check("C2H8O -> formula plausibility FAIL", run_check({"formula": "C2H8O"})["result"], "FAIL")
    check("exact mass 194.0804 passes", run_check({"formula": "C8H10N4O2", "exact_mass": 194.0804})["result"], "PASS")
    r = run_check({"formula": "C8H10N4O2", "exact_mass": 194.19})
    check("exact mass given as average MW fails", r["result"], "FAIL")
    check("...with the average-vs-mono hint", "AVERAGE" in r["checks"][-2]["detail"], True)
    check("RDBE claim 6 passes", run_check({"formula": "C8H10N4O2", "rdbe": 6})["result"], "PASS")
    check("RDBE claim 5 fails", run_check({"formula": "C8H10N4O2", "rdbe": 5})["result"], "FAIL")
    check("composition within 0.4 passes",
          run_check({"formula": "C8H10N4O2", "composition": "C:49.6,H:5.0,N:28.9"})["result"], "PASS")
    check("composition off by 1 fails",
          run_check({"formula": "C8H10N4O2", "composition": {"C": 50.5}})["result"], "FAIL")
    check("name-only claim uses canonical formula",
          run_check({"name": "aspirin", "mw": 180.16})["result"], "PASS")
    check("claim key synonyms", normalize_claim({"Molecular Weight": 1, "molecularFormula": "H2O", "DBE": 0}),
          {"formula": "H2O", "mw": 1, "rdbe": 0})

    print(f"selftest OK ({n_ok}/{n_all} checks passed)")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="chem.py",
        description="Molecular-formula arithmetic for chemistry claims: element counts, molecular "
                    "weight, exact/nominal mass, composition, RDBE, nitrogen rule, Lipinski subset, "
                    "and PASS/FAIL checks of claimed values.",
        epilog="Charges: NH4+, SO4^2-, 'SO4 2-', (SO4)2-, [Fe(CN)6]4-, Fe^3+, Fe+3, superscripts. "
               "'Fe3+' is rejected as ambiguous (write Fe^3+). Hydrates: CuSO4·5H2O, CuSO4.5H2O, MgSO4*7H2O. "
               "Exit codes: 0 ok, 1 bad input, 2 a claim FAILs.")
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true", help="print the SKILL.md worked example and exit")
    sub = parser.add_subparsers(dest="command")

    pf = sub.add_parser("formula", help="parse a formula: counts, MW, exact/nominal mass, composition, RDBE")
    pf.add_argument("formula", nargs="?", help="molecular formula, e.g. C8H10N4O2, CuSO4·5H2O, [Fe(CN)6]4-")
    pf.add_argument("--file", help="text file with one formula per line")
    pf.add_argument("--json", action="store_true", help="JSON output")

    pc = sub.add_parser("check", help="compare claimed name/MW/exact mass/RDBE/composition with computed values")
    pc.add_argument("--file", help="JSON claim (object or list): name, formula, mw, exact_mass, rdbe, composition, druglike")
    pc.add_argument("--name", help="compound name (checked against the built-in table of well-known compounds)")
    pc.add_argument("--formula", help="claimed molecular formula")
    pc.add_argument("--mw", help="claimed molecular weight, e.g. 194.19 or '194 g/mol'")
    pc.add_argument("--exact-mass", dest="exact_mass", help="claimed exact / monoisotopic mass")
    pc.add_argument("--rdbe", help="claimed degree of unsaturation (RDBE / DBE)")
    pc.add_argument("--composition", help="claimed mass percent, e.g. 'C:49.48,H:5.19,N:28.85,O:16.48'")
    pc.add_argument("--druglike", action="store_true", help="the source asserts drug-likeness / oral bioavailability")
    pc.add_argument("--mw-tol", dest="mw_tol", type=float, default=0.05, help="MW tolerance in percent (default 0.05)")
    pc.add_argument("--mono-tol", dest="mono_tol", type=float, default=10.0, help="exact-mass tolerance in ppm (default 10)")
    pc.add_argument("--comp-tol", dest="comp_tol", type=float, default=0.4,
                    help="composition tolerance in percentage points (default 0.4)")
    pc.add_argument("--json", action="store_true", help="JSON output")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo:
        return run_demo()
    if args.command == "formula":
        return cmd_formula(args, parser)
    if args.command == "check":
        return cmd_check(args, parser)
    parser.error("choose a command: formula | check  (or --demo / --selftest)")


if __name__ == "__main__":
    sys.exit(main())
