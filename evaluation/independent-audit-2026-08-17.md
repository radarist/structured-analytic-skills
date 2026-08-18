# Independent audit — 2026-08-17 (pre-remediation)

> **Status:** historical pre-remediation findings. The blockers and Fix-first/Hold findings
> below were subsequently remediated and re-verified. Read
> [`second-pass-2026-08-18.md`](second-pass-2026-08-18.md) for closure evidence and
> [`../CHANGELOG.md`](../CHANGELOG.md) for the release summary.

## Objective checks run by the orchestrator (not by the blind reviewers)

## External validator — agentskills / skills-ref v0.1.1 (agentskills.io reference implementation)
Independent of this repository's own tooling.
- `agentskills validate` over all 69 skills: **69 passed, 0 failed**.

## Client listing-budget exposure
- `agentskills to-prompt skills/*/` → **57,810 characters** of `<available_skills>` XML (~16,000 tokens).
- Codex documents an initial skill-listing cap of 8,000 characters (or 2% of context).
  Installing the full library is **7.2× that budget**, so a capped client will shorten
  descriptions or omit skills. The README mentions this in prose but gives no number and no
  per-category install command. → **should-fix**.

## Template-following / uniformity analysis
The library was produced rapidly against a structural standard, so uniformity masquerading
as quality is the expected failure mode. Measured:
- **58 distinct top-level heading sequences across 69 skills**; the largest identical-structure
  cluster is 7 skills. Not a single enforced template.
- **Verbatim sentence reuse: 59 of 4,569 sentences (1.3%)**, across 24 distinct sentences —
  and every one of the top repeats is a *shared citation line* (Heuer & Pherson 3rd ed.,
  Tetlock & Gardner, the CIA Tradecraft Primer, Futures Research Methodology V3.0). Shared
  sources across related methods are correct, not boilerplate.
- **Mean pairwise TF-IDF cosine similarity across full bodies: 0.059**; **0 of 2,346 pairs
  above 0.50**. The most similar pairs are genuinely adjacent methods
  (evolution-stage ↔ wardley-map-drafting 0.301; experimental-design ↔ test-significance 0.260;
  chemistry-claim-check ↔ smiles-sanity-check 0.241).

Conclusion: the bodies are substantively differentiated. The structural convergence is at the
section-heading level (a house style), not at the content level.

## Verified release blockers (orchestrator re-verification of the readiness review)

| Claim | Verified | Evidence |
|---|---|---|
| Working tree ahead of git | YES | `git ls-tree -d HEAD skills/` = **68**; disk = **69**. `value-intellectual-property`, all 69 `agents/openai.yaml`, `eval_schema.py`, `build_openai_metadata.py` untracked. |
| CI fails on fresh clone | YES | `.github/workflows/ci.yml` invokes `evaluation/eval_schema.py` and `evaluation/build_openai_metadata.py`; **neither is tracked in git**. |
| Spec-validation CI job is inert | YES | ci.yml calls `skills-ref validate`; the PyPI package `skills-ref` installs a console script named **`agentskills`**, so every call is command-not-found — and the job carries `continue-on-error: true`, so it can never fail the build. |
| Copy-out install breaks links | YES | **25 links of the form `](../../methodologies/…)` across 25 skills.** These escape the skill directory and resolve only inside this repo, contradicting the "self-contained" claim for the documented `cp -R skills/* .agents/skills/` path. |
| No remote, no tags | YES | `git remote` = 0, `git tag -l` = 0. At audit time, CHANGELOG documented an internal v2.1.0 that existed in no commit. |

## Baseline reproducibility (correction to the project's own headline)

Re-scoring commit `6882e92` with the scorer as it stands today:

| Figure | Committed baseline | Recomputed today | |
|---|---|---|---|
| mean skill score | 78.4 | 78.4 | reproduces |
| median skill score | 77.3 | 77.3 | reproduces |
| minimum skill score | 61.3 | 61.3 | reproduces |
| checks passed | 2902 / 3708 | 2902 / 3708 | reproduces |
| repo-hygiene score | 45.0 | **30.0** | differs |
| **library score** | **73.4** | **71.1** | **differs** |

Cause: the library score is `0.85 × mean skill score + 0.15 × repo hygiene`, and the hygiene
component (a) inspects the working tree, so a stray `.DS_Store` moves it, and (b) gained
checks after the committed baseline was generated. The **per-skill** scoring is fully
deterministic and reproducible; the **library** score is not stable across scorer versions
or working-tree state. The defensible headline is the per-skill figure, not "73.4 → 100.0".

## Orchestrator re-verification of Group 1 findings

| Finding | Verified | Evidence |
|---|---|---|
| `cross-impact-analysis` labels a non-MICMAC computation "MICMAC" | YES | `crossimpact.py` has **no** matrix multiplication (`grep matmul\|power\|indirect\|multiply` = 0 hits). Computation is `influence[i] = sum_j abs(m[i][j])`, `dependence[j] = sum_i abs(m[i][j])` — the *direct* classification only. MICMAC is defined by raising the matrix to successive powers for *indirect* influence. "MICMAC" nonetheless appears in the frontmatter `method:`, the retrieval `description:`, the body, the output template, the tool's printed heading and an eval prompt. |
| `agents/openai.yaml` fields machine-truncated | YES | **25 of 69** files carry a mid-phrase truncated `short_description` or `default_prompt`, e.g. `"Apply AMSTAR 2 (A MeaSurement Tool to Assess systematic Reviews"`, `"Apply Bayesian belief updating in odds form (prior odds × Bayes"`. Generated by a character-budget truncation and never read by a human. |

## Orchestrator re-verification of Group 2 findings — TWO RELEASE BLOCKERS

### BLOCKER A — RoB 2 relicensed from CC BY-NC-ND to MIT
Verified directly at https://www.riskofbias.info/ :
> "Creative Commons Attribution-**NonCommercial-NoDerivatives** 4.0 International License" — "© 2025 by the authors."

`skills/assess-study-bias/SKILL.md` declares `license: MIT`, and **no Creative Commons notice
appears anywhere in that skill directory** (grep confirms zero matches). The repository LICENSE
grants the right to "sublicense, and/or sell". The skill reproduces the signalling questions
verbatim, re-encodes the published decision trees in `scripts/rob2.py`, and adds a mechanism
the instrument does not contain (`--sc-high-threshold`).

Both licence terms are breached: **NonCommercial** (MIT permits sale) and **NoDerivatives**
(the material is adapted). Aggravating: the same repository handles Ecosyste.ms's CC BY-SA
obligations meticulously in `oss-project-health` — enforced in the output template, the
verification checklist, the anti-patterns *and* the script. So this is inconsistent
application, not ignorance.

### BLOCKER B — a citation naming an author who did not write the paper
`skills/amstar2-review-appraisal/SKILL.md` line 141 cites:
> K. K. De Santis, R. C. Lorenz, **M. Lakeberg**, K. Matthias … doi:10.1186/s12874-023-01879-8

Crossref for that DOI returns: **De Santis K, Pieper D, Lorenz R, Wegewitz U, Siemens W,
Matthias K**. M. Lakeberg is not an author of it (she is an author of a *different* De Santis
paper, doi:10.1002/jrsm.1532); three real co-authors are dropped without an "et al.". Two
papers have been merged into one reference — inside the skill whose purpose is auditing
whether other people's evidence syntheses were done properly, and it is the sole citation
supporting an authorial deviation from the published instrument.

### Quota-gaming fingerprint, quantified by the reviewer across 12 unrelated methods
| Metric | Range |
|---|---|
| SKILL.md word count | 1,701 – 1,860 (9 % spread) |
| description length | 567 – 694 chars |
| exclusion clause present | 12 / 12 |
| verification checklist items | 3 – 7 (all ≥ 3) |
| sibling cross-references | 4 – 6 (all ≥ 4) |
| section order | identical in all 12 |

## Orchestrator re-verification of Group 4 findings

| Finding | Verified | Evidence |
|---|---|---|
| Real patent numbers used as invented examples | YES | `US11234567B2` is a **real granted patent**: "Vacuum cleaner tool having a rotatable duct…", SharkNinja Operating LLC (patents.google.com). The skill attaches to it `"assignee": "Example Corp"`, CPC `G06N 3/084` (neural networks) and a neural-retrieval claim set; the frontmatter uses `"what does US11234567 cover?"` as a **retrieval trigger phrase**; and eval case `patent-pos-1` reads *"Read US11234567B2 and tell me what independent claim 1 actually covers."* An agent that follows the instruction gets a vacuum cleaner. `EP3456789B1` is likewise real (3D Systems). |
| GRADE Handbook reproduced under MIT | YES | `grade.py` contains 160 long quoted strings totalling ~2,200 words derived from the GRADE Handbook, whose own terms require permission from the editors to reproduce. Declared `license: MIT`. |
| IEEE Reference Guide reproduced under MIT | YES | `cite-ieee/references/formats.md` = 849 words of formats and examples taken from the © 2025 IEEE Reference Guide. Declared `license: MIT`. |
| No third-party notice anywhere | YES | No `NOTICE`, `THIRD-PARTY*` or equivalent file exists at the repository root. |

### Additional Group 4 fidelity findings (reviewer-verified against primary sources)
- **`cite-ieee` teaches the wrong in-text convention.** It mandates `[1, 4]` / `[3, 7, 9]`; the IEEE
  Reference Guide writes `[2], [4], [5]` and reserves the comma-inside-brackets form for *locators*
  (`[3, pp. 5–10]`, `[3, Fig. 1]`), so `[1, 4]` reads to an IEEE copy editor as "reference 1, part 4".
  The guide also states ranges "will not include an en dash", yet the description advertises `[2]–[5]`.
- **`premortem-analysis`** attributes to Mitchell, Russo & Pennington (1989) a finding that imagining
  an event raises "the ability to identify reasons … by roughly 30 %". The paper reports *more reasons
  generated* under outcome certainty and states temporal perspective "showed little influence"; the
  30 %-ability formulation is Klein's gloss in HBR 2007.
- **`bayesian-update`** labels Jeffreys' pooled scale (1–3.2 / 3.2–10 / 10–100 / >100) as
  "Kass and Raftery (1995)". K&R's *own* recommended scale is 1–3 / 3–20 / 20–150 / >150
  ("bare mention / positive / strong / very strong", JASA 90(430):777).
- **Fabricated provenance inside evidence-discipline skills**: `jtbd-framing` labels an invented quote
  `— sourced (Helios talent-acquisition lead, March 2026 interview)`; `steelman-argument` records
  `Endorsement test: passes — a CTO … reviewed the reconstruction and endorsed it`; `red-team-claim`
  asserts an invented base rate and a shipment claim about the real company **Cerebras**.
- **`triangulate-sources`'s worked example fails its own four-test independence rule** yet concludes
  "corroborated, 3 independent sources".

## Orchestrator re-verification of Group 3 findings

| Finding | Verified | Evidence |
|---|---|---|
| SBAR skill named `write-srl-brief` | YES | H1 reads `# Write SBAR Brief`; "SBAR" appears 13× in the body; the string "SRL" appears **only in the slug**. Propagated to `index.json` (4 refs), `README.md`, and 6 sibling SKILL.md files. No user searching "SBAR" matches the slug. |
| `smiles-sanity-check` rejects spec-valid SMILES | YES | `check "CS(C)C"` → `INVALID valence -- sulfur (S) … bond-order sum 3 is not an allowed valence (2, 4, 6)`; `check "CP(C)(C)C"` → `INVALID … 4 is not an allowed valence (3, 5)`. OpenSMILES §3.1.5 adds implicit hydrogens to reach the **next highest** known valence, so both are valid and RDKit parses them. The code tests set membership; the SKILL.md prose states the correct rule ("must not exceed"), so doc and code disagree and the code is the wrong one. The 8-check self-test never exercises this branch. |

### Additional Group 3 findings (reviewer-verified against primary sources)
- **`estimative-language`**: the ICD 203 rule is at **D.6.e(2)(b)**, not "D.2.e(2)(b)" — wrong in SKILL.md, in `references/scales.md` (twice) and in `wep.py`, which **prints the wrong locator to the user**. Separately, its linter raises *error*-level findings on "cannot rule out / cannot dismiss / cannot discount" — the exact three phrases the 2007 NIE explainer (cited by this same skill) names as correct usage for an unlikely-but-consequential event. All three probability tables (ICD 203, PHIA, IPCC AR5) were verified band-for-band as **exact**.
- **`analysis-of-competing-hypotheses`**: step 8 is not Heuer's step 8. Heuer's is "identify milestones for future observation"; the skill substitutes "look for loose ends" under a heading reading "Heuer's eight steps", and the output template has no field for milestones.
- **`trend-analysis`**: applies Rogers' 16 % *cumulative-adoption* boundary to an *annual new-sales share* series — a stock/flow confusion a diffusion practitioner would flag.
- **`indicators-validation`**: "Pherson's five qualities of an indicator" is cited to a paper about five analytic *habits*.
- **`decision-matrix-mcda`** (scored 4.8, arithmetic independently reproduced against all three of Saaty's published matrices with numpy): the Saaty-1980 random-index table is used without disclosing that later re-simulations (Alonso & Lamata 2006) give lower values that push CR *up* and can flip a borderline CR ≤ 0.10 gate.

## Inter-rater reliability (two blind reviewers, same skills, no contact)

| Skill | Group reviewer | Inter-rater | |Δ| |
|---|---|---|---|
| decision-matrix-mcda | 4.80 | 4.75 | 0.05 |
| rate-source-admiralty | 4.40 | 4.50 | 0.10 |
| estimative-language | 4.40 | 4.50 | 0.10 |
| evidence-appraisal | 4.90 | 4.75 | 0.15 |
| value-intellectual-property | 3.30 | 3.13 | 0.17 |
| cite-ieee | 3.90 | 4.75 | **0.85** |

**Mean absolute difference 0.24; five of six agree within 0.17.** That is high agreement for
independent qualitative scoring, and it means the per-skill numbers are reproducible rather
than one reviewer's taste.

**The single disagreement, adjudicated by the orchestrator:** Group 4 is right.
`skills/cite-ieee/SKILL.md` line 38 mandates *"Combine several sources in one bracket —
`[1, 4]`, `[3, 7, 9]`"* and, **in the same paragraph**, teaches *"Cite part of a source with a
locator inside the bracket: `[3, pp. 5–10]`, `[3, Fig. 1]`"*. The IEEE Reference Guide writes
combined citations as `[1], [4]` and reserves the comma-inside-brackets form for locators, so
`[1, 4]` reads to an IEEE copy editor as "reference 1, part 4". The inter-rater verified the
*ranges* rule — which the skill does handle honestly, explicitly noting the guide writes ranges
out — and did not examine the *combining* rule. cite-ieee's score should be ~3.9, not 4.75.

Independently reproduced by both reviewers without contact: the `value-intellectual-property`
fabricated-patent finding, the `agents/openai.yaml` truncation, and the
`decision-matrix-mcda` worked-example-versus-tool contradiction.

## Orchestrator re-verification of the value-intellectual-property blocker

**EP 4 321 765 A1 is real**: *"Carriage for a linear guidance system and linear guidance system
comprising such a carriage"*, applicant **Accuride International GmbH**, inventors Neuhaus /
Neidhöfer / Quirein — a sliding-drawer bearing patent (patents.google.com). The skill's worked
example values it, plus "Aurelia Bio's cell-culture know-how", at EUR 2.4m–7.1m for **the
University of Valencia** (a real institution), on a specific date, with "documented" comparables —
and carries **no illustrative/hypothetical label**, while every sibling skill labels its example.

## Orchestrator re-verification of Group 6's headline finding — CONFIRMED CODE BUG

**`skills/brier-score-calibration/scripts/brier.py` mislabels calibration direction.**

Reproduction — a forecaster who says 0.50 six times and is right exactly half the time:
```
Reliability (calibration error):  0.0000   (lower is better; 0 = perfectly calibrated)
bin              n  midpoint   mean f  observed   direction
[0.50,0.60)      6      0.55    0.500     0.500   overconfident
```
The tool reports **perfect calibration (reliability 0.0000)** and simultaneously labels the
forecaster **overconfident**.

Cause (line 176): the direction test compares the observed frequency to the bin **midpoint**
(`mid`), not to the mean forecast actually made (`mean_f`):
```python
mean_f = sum(f for f, _ in g) / nk          # line 167 - computed correctly
rel += nk * (mean_f - obs) ** 2             # line 169 - reliability uses it correctly
...
if obs > mid:      direction = "underconfident"     # line 176 - uses the MIDPOINT
elif obs < mid:    direction = "overconfident"
else:              direction = "calibrated"
```
`mean_f` is even printed in the same table (line 241). Any forecaster whose probabilities sit
below their bin's midpoint is systematically mislabelled. The `calibrated` branch is
effectively unreachable. **Fix is one line**: compare `obs` against `mean_f`.

**The self-test enshrines the bug** — it asserts `by_k[8]["direction"] == "overconfident"` and
prints the rationale *"(observed 0.50 < midpoint 0.85)"*, so the wrong comparison is locked in
as expected behaviour. This is the rubric's "self-test passes while the tool is broken" case,
in the skill whose entire subject is calibration.

**Second defect, same command:** the printed Murphy identity is not an identity —
`Check: REL - RES + UNC = 0.2346 = mean Brier 0.2311`. Two different numbers joined by `=`
(gap 0.0035). The Murphy (1973) decomposition is exact when computed with bin means.

## IP & licensing review — VERDICT: not safe to publish under MIT today (4 blockers, ~half a day to fix)

| # | Blocker | Verified |
|---|---|---|
| B1 | **Cochrane RoB 2 — CC BY-NC-ND 4.0, declared MIT.** All 22 signalling questions reproduced verbatim; `rob2.py` line 113 says so itself: `# Signalling questions, verbatim from Boxes 4, 6, 8, 10 and 11 of the guidance`. NC bars commercial use (MIT grants "sell"); ND bars derivatives (the questions are restructured into a Python dict). No CC notice in the directory. **Remedy:** delete the question *text*, keep IDs + algorithms (logic is unprotectable method) + a pointer to riskofbias.info. ~1 h |
| B2 | **Wardley evolution cheat sheet — CC BY-SA 4.0 vs MIT.** A 21-row table transcribed from Figure 17 of *Wardley Maps* ch. 2. BY-SA §3(b) requires adaptations to be BY-SA; CC's compatible list is only FAL 1.3 and GPLv3 — MIT is not on it. **Counter-intuitive remedy:** copying *more faithfully* is safer — verbatim reproduction is a collection member (§2(a)(1)(A)), while the current *condensed* version is Adapted Material and triggers share-alike. Or simply delete it: the skill's own four-question diagnostic already does the job. ~30 min |
| B3 | **AMSTAR 2 — right instrument, wrong source.** The BMJ paper is **CC BY 4.0** (reusable commercially with attribution) and covers the 16 item stems and Box 1. But the "For Yes"/"For Partial Yes" criteria and Box 2 wording are **not in the paper** — they come from amstar.ca, whose footer reads "Copyright © 2026 AMSTAR All Rights Reserved" with no reuse grant. **Remedy:** keep stems + Box 1 with CC BY attribution; reword the criteria grid. ~1 h |
| B4 | **Repo-wide MIT is an affirmative misstatement.** **69 of 69** skills declare `license: MIT`, and there is no `NOTICE` / `THIRD-PARTY-NOTICES.md` anywhere. CC BY (PRISMA, AMSTAR paper, EU Annex G), OGL v3 (PHIA) and CC BY-SA (Ecosyste.ms) do not become MIT by being placed in an MIT repo. **Remedy:** ship the notices file the reviewer drafted; add "Except as noted in THIRD-PARTY-NOTICES.md" to LICENSE. ~1 h |

### Corrections to my own earlier figures (the reviewer measured; I had over-counted)
- **GRADE in `grade.py`: ~430 words of reproduced text, not ~2,200.** My grep counted every quoted
  string in a 4,779-word Python file. Actual verbatim Handbook quotation is **341 words across 23
  spans**, each inside quote marks with a § locator, plus a ~90-word interpretation block — marked,
  attributed, section-located quotation for instruction. **Should-fix, not a blocker.** One real
  defect: the four Table 5.1 sentences appear *without* quotation marks, as if the tool's own words.
- **IEEE in `formats.md`: ~250 words of IEEE material, not 849.** Of the 849 total, 349 are the
  repo's own prose and 182 are placeholder templates (the citation *system*, unprotectable). The
  protectable slice is **12 concrete examples lifted from the guide**. **Remedy (~20 min):** swap
  those 12 for examples the repo authors itself.

### Additional should-fix items verified
- **arXiv rate limit violated**: `citecheck.py` line 1102 sets `--delay` default **1.0 s**; arXiv's
  terms require *"no more than one request every three seconds"*. Change to 3.0.
- **Admiralty label provenance is wrong.** The labels used ("Completely reliable", "Doubtful",
  "Reliability cannot be judged") are attributed to AJP-2.1/STANAG 2511, but FM 2-22.3's actual
  tables read "Reliable", "Doubtfully True", "Cannot Be Judged". The repo's exact set matches
  **UK JDP 2-00 Table 3.1**, which is **Crown copyright, "for UK government and MOD use only"** —
  not covered by OGL. Thin, likely-unprotectable matter, so not a blocker; switch to FM 2-22.3's
  verified public-domain wording (~10 min).
- Trademarks (Gartner "HYPE CYCLE" US Reg. 4,640,207/4,640,209; Cynefin® US Reg. 5,853,538) are used
  nominatively and defensibly — add a trademark + non-affiliation line.

### Explicitly cleared
PRISMA 2020 (CC BY 4.0) · all TRL scales (US federal, public domain; EU Annex G reusable) ·
Admiralty *explanatory sentences* (FM 2-22.3, public domain) · ICD 203/206, Tradecraft Primer
(ODNI, public domain) · ISO usage in `verify-citations` (identifiers and algorithms only, no ISO
text — "exactly the right posture") · CHAOSS (MIT) · OpenSSF Scorecard (Apache-2.0) ·
`osshealth.py` GitHub client (ToS-compliant: descriptive UA, serial requests, honours 429) ·
SemVer/Conventional Commits (CC BY 3.0, paraphrased) · **no secrets or personal data in 362 files** ·
no defamation risk · `methodologies/` (28 docs, original prose).

## Orchestrator re-verification of Group 6's two self-undermining findings — BOTH CONFIRMED

**1. `verify-citations` FAILs real, resolvable DOIs — including its own sibling's foundational citations.**
```
[1] Brier 1950  doi: 10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2   -> FAIL
[2] Murphy 1973 doi: 10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2   -> FAIL
    error: does not match 10.NNNN/suffix (ISO 26324)
Verdict: FAIL -> exit 2
```
Both DOIs resolve at Crossref. They are the two founding citations of `brier-score-calibration`.
Cause: the extraction and validation regexes exclude `<` and `>`, killing the entire legacy
AMS/AGU/GSA SICI-style DOI family. The rule is also attributed to the wrong standard — the DOI
Handbook (normative for ISO 26324) permits any Unicode Graphic in the suffix, **including
angle brackets and spaces**, and sets no registrant-code digit limit. The `\d{4,9}` and
"no whitespace" rules are Crossref heuristics, not ISO requirements.

**2. `systematic-review`'s tool rejects a conforming PRISMA 2020 flow.**
A valid flow — 925 screened − 840 excluded = 85 **sought**, 5 **not retrieved**, 80 assessed
− 61 excluded = 19 included — is flagged:
```
[FLAG] screened - title/abstract exclusions = full-text assessed: 925 - 840 = 85  [MISMATCH: reported 80]
```
`prisma.py flow --help` contains **zero** `--sought` / `--not-retrieved` arguments, so the two
PRISMA 2020 boxes "Reports sought for retrieval" and "Reports not retrieved" cannot be
expressed at all. The skill's own step 4 tells the user to "record any that could not be
retrieved" and gives the number nowhere to go.

## FINAL AGGREGATE — 69 skills, independently scored, 8 criteria each

- **Mean 4.42 / 5 · median 4.60 · range 3.20–4.90**
- **24 SHIP · 38 SHIP WITH FIXES · 7 HOLD**
- Distribution: **36 at ≥4.5**, 24 at 4.0–4.49, 5 at 3.5–3.99, 4 below 3.5
- Inter-rater agreement on the overlap sample: mean |Δ| **0.24**, five of six within 0.17
