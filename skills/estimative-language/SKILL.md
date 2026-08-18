---
name: estimative-language
description: "Rewrites and lints the likelihood and confidence wording of an assessment against one declared standard — the ODNI ICD 203 estimative-probability terms, the UK PHIA Probability Yardstick, or the IPCC AR5 likelihood scale — converting numbers to calibrated terms, keeping confidence in its own sentence, and flagging vague words. Use when asked to \"rewrite this assessment using ICD 203 probability language\", \"what does 'realistic possibility' mean in the UK yardstick\", or \"lint my brief for vague likelihood words and mixed confidence statements\". Not for scoring how accurate past forecasts were, or for revising a probability after new information."
license: "MIT (skill text); PHIA yardstick © Crown copyright, OGL v3.0; IPCC AR5 table © IPCC"
metadata:
  category: writing
  method: Estimative language — words of estimative probability and analytic confidence
  origin: Sherman Kent, CIA Office of National Estimates, 1964; codified in ODNI ICD 203, 2015
  version: "1.0.0"
---
# Estimative language

In 1964 Sherman Kent found that officers who had signed a National Intelligence Estimate read its phrase "serious possibility" as anything from 20 % to 80 %. Estimative language is the fix: a short published vocabulary in which every likelihood word has a number range, and **likelihood** (will it happen?) stays apart from **confidence** (how sound is the basis?). It stops "possible" being read as 50 % and "high confidence" as "very likely".

## When to invoke

Invoke when:

- Writing or reviewing an assessment, forecast, risk statement or brief that contains probability judgments — "how likely is this?", "rewrite this using ICD 203 language", "what does 'realistic possibility' mean?", "lint my brief for vague likelihood words".
- A number from `bayesian-update` or `reference-class-forecasting` must become prose, or a `write-sbar-brief` recommendation is about to ship.

Do NOT invoke when:

- Scoring forecasts against known outcomes — use `brier-score-calibration`.
- Changing the probability in light of new evidence — use `bayesian-update`; this skill only words the result.
- Sorting facts from assumptions sentence by sentence — use `claim-provenance`.
- No verifiable basis exists for any likelihood — use `abstain-or-escalate` rather than writing "possible".

## Procedure — six steps

### 1 — Declare one standard for the document

Pick one — ODNI **ICD 203** (seven contiguous bands, 01–99 %, two synonym rows), the UK **PHIA Probability Yardstick** (seven ranges with deliberate gaps, because "the scale is not continuous to avoid a false impression of accuracy") or the **IPCC AR5** scale (nested bands — report the narrowest). Name it in the header ("Likelihood terms follow ICD 203") and never mix standards inside a product; under ICD 203, mixing synonym rows needs a disclaimer.

Full term-by-term tables for all three standards: [references/scales.md](references/scales.md) — read when converting a specific probability or auditing which standard a document uses. `python3 scripts/wep.py table --standard icd203|phia|ipcc` prints the same tables with their citations, so nothing is lost by keeping them out of this file.

Confidence is a separate scale in every standard: ICD 203 **high / moderate / low**, grounded in the quality and quantity of sourcing, corroboration and logic; PHIA's Analytical Confidence Rating (High / Moderate / Low) from Information Base, Analytical Rigour and Complexity & Volatility; IPCC's very low … very high from evidence × agreement, "not to be interpreted probabilistically".

### 2 — Convert every probability to the standard's term (or attach the number)

Run `python3 scripts/wep.py term --p 0.7 --standard phia` for each numeric judgment and use the term returned. On a shared boundary (ICD 203 at 20 %) pick one term and attach the number; in a PHIA gap (50 %) give the number or move the judgment into a band — never invent a term; under IPCC report the narrowest band. Use the standard's own words: "even chance" is not "roughly even chance".

### 3 — Express confidence separately

ICD 203 D.6.e(2)(b): a product "must not combine a confidence level and a degree of likelihood ... in the same sentence". Write the likelihood sentence, then a confidence sentence naming its basis — number and quality of sources, corroboration, logic, load-bearing assumptions. Confidence answers "how sound is the basis?", never "how likely?"; "80 % confident" is a likelihood in disguise.

### 4 — Ban vague words unless mapped

*possible, may, might, could, potentially, perhaps, significant / real / good chance* carry no number: replace each with a term or delete it. In NIE usage *may* and *might* mean "unable to assess the likelihood" — if that is meant, say so. *We cannot rule out / cannot dismiss / cannot discount* is not in this class: the 2007 NIE explainer defines it as the correct way to flag "an unlikely, improbable, or remote event whose consequences are such that it warrants mentioning", so the linter reports it as a note, not an error — keep it only in that sense and still give the event its own term. Run `python3 scripts/wep.py lint --file draft.md --standard icd203` and clear every finding.

### 5 — Keep the number when the audience needs it

Readers who compare options, aggregate judgments or act on thresholds get the number in parentheses — "likely (70 %)"; words plus numbers are read more consistently than words alone (Budescu et al., 2009). PHIA products default to words, but never leave a *bare* number ("a 70 % chance") without its term.

### 6 — State what would change the judgment

ICD 203 (2)–(3): note the causes of uncertainty, name indicators that would alter it, and distinguish underlying information from assumptions and judgments — state a linchpin assumption and what follows if it is wrong. Give every key judgment one "would change if …" line.

## Output template

```
## Likelihood & confidence — {product / question}
Standard: {ICD 203 | PHIA Probability Yardstick | IPCC AR5}   (one per document)

| # | Judgment | Term (number) | Confidence | Basis: sourcing · corroboration · logic | Would change if … |
| 1 | {judgment} | {term} ({p} %) | {high | moderate | low} | {sources, corroboration, key assumption} | {indicator} |

Lint (python3 scripts/wep.py lint --file {draft} --standard {std}): {n error(s), m advisory}
- L{line}: {rule} — "{snippet}" → {fix}
```

Every field is mandatory: the standard line, a term for every judgment, confidence in its own cell or sentence with its basis, and the lint list (or "lint clean, exit 0").

## Worked example

A semiconductor brief, ICD 203 declared; `python3 scripts/wep.py --demo` reproduces it.

Before: *"We assess with high confidence that Vendor A will likely ship its 2 nm process node in 2027. There is a significant chance the second fab slips, and it is possible that yields stay below 60 %. We think there is roughly a 70 % chance that Vendor B loses its lead customer. A price war is a realistic possibility."*

`python3 scripts/wep.py lint --text "…" --standard icd203` (exit 1; messages abridged):

```
before.md:1:16:  [error] mixed-confidence-likelihood — 'high confidence' and 'likely' in one sentence
before.md:1:105: [error] vague-likelihood — 'significant chance' — map to a term of the declared standard, or delete
before.md:1:156: [error] vague-likelihood — 'possible' — map to a term of the declared standard, or delete
before.md:1:222: [error] bare-number — '70 % chance' has no estimative term
before.md:1:290: [error] foreign-term — 'realistic possibility' is a PHIA yardstick term, not ICD 203
lint: 5 error(s), 0 advisory; declared standard: icd203; distinctive terms seen: PHIA yardstick
```

"60 %" is a yield, not a probability, and is left alone. After (lint: 0 errors, exit 0):

*"Vendor A will likely (about 70 %) ship its 2 nm process node in 2027. There is a roughly even chance (45–55 %) that the second fab slips by a quarter or more, and it is unlikely (20–45 %) that yields stay below 60 %. Vendor B will likely (70 %) lose its lead customer. A price war is unlikely (about 30 %). We have moderate confidence in these judgments: two corroborating supplier reports and one dated public filing; the fab-slip judgment rests on the assumption that tool deliveries stay on schedule. A slip in the lithography tool delivery date would move the fab-slip judgment to likely."*

Under PHIA, `term --p 0.7 --standard phia` gives *likely (≈55–≈75 %)*, but `term --p 0.5` gives no term — 50 % sits in the gap between *realistic possibility* (≈40–<50 %) and *likely*.

## Verification

Before the product ships, confirm:

- [ ] One standard is declared and `wep.py lint --standard {std}` reports no `foreign-term` or `mixed-standards` finding.
- [ ] Every probability maps to a term of that standard; boundary and gap cases were resolved with `wep.py term --p`, not by inventing a term.
- [ ] No sentence carries both a confidence level and a likelihood term or number; no numeric confidence.
- [ ] No unmapped vague words, hedged terms or bare numbers remain.
- [ ] Every key judgment states its basis and what would change it; assumptions are labelled as assumptions.
- [ ] Re-run `python3 scripts/wep.py lint --file final.md --standard {std}` — exit code 0.

## Companion tool

`scripts/wep.py` holds the three tables verbatim and does the mapping and linting; stdlib only, deterministic. The lint is a heuristic reviewer's aid — clear its findings, then read the text once more yourself.

```bash
python3 scripts/wep.py term --p 0.7 --standard icd203        # term(s); reports boundaries, PHIA gaps, IPCC nesting
python3 scripts/wep.py prob --term "likely" --standard phia   # range for a term (all standards if none given)
python3 scripts/wep.py lint --file doc.md --standard icd203   # findings with line:col; exit 1 on any error
python3 scripts/wep.py lint --text "..." --json --numbers allow
python3 scripts/wep.py table --standard ipcc                  # the table with its citation
python3 scripts/wep.py --demo | --selftest
```

## Pair with adjacent skills

- `brier-score-calibration` — once outcomes are known, checks whether "likely (70 %)" calls came true about 70 % of the time.
- `bayesian-update` — produces the posterior number; this skill words it without losing it.
- `claim-provenance` — inline `[validated]` / `[assumption]` brackets are the sentence-level form of step 6.
- `write-sbar-brief` — its mandatory confidence tag on the recommendation is written with steps 3 and 6.
- `pyramid-principle` — the governing thought is a judgment; give it a term and a separate confidence line.
- `abstain-or-escalate` — when no basis exists for any likelihood, say so instead of writing "possible".

## Anti-patterns

- Do **not** hide "50 %" as "possible" or "20 %" as "could" — Kent's "serious possibility" problem.
- Do **not** use "high confidence" to mean "very likely": confidence grades the basis, likelihood grades the event.
- Do **not** mix scales in one document — "realistic possibility" (PHIA) beside "roughly even chance" (ICD 203).
- Do **not** put a confidence level and a likelihood term in one sentence, and never write "80 % confident".
- Do **not** hedge a term ("quite likely", "not unlikely") or "improve" a table (no "extremely likely" under ICD 203).
- Do **not** drop the number when the reader will compute with it, and never leave a bare number without its term.

## Reference

- S. Kent, "Words of Estimative Probability", *Studies in Intelligence*, vol. 8, no. 4, 1964, pp. 49–65 (declassified 1993). https://www.cia.gov/resources/csi/static/Words-of-Estimative-Probability.pdf
- Office of the Director of National Intelligence, *Intelligence Community Directive 203: Analytic Standards*, 2 January 2015; technical amendment 21 December 2022, §D.6.e(2)–(3). https://www.dni.gov/files/documents/ICD/ICD-203-TA-Analytic-Standards-21-Dec-2022.pdf
- National Intelligence Council, *Iran: Nuclear Intentions and Capabilities*, National Intelligence Estimate, November 2007, "What We Mean When We Say: An Explanation of Estimative Language". https://www.dni.gov/files/documents/Newsroom/Reports%20and%20Publications/20071203_release.pdf
- Professional Head of Intelligence Assessment (Cabinet Office), *Explaining Uncertainty in UK Intelligence Assessment*, GOV.UK guidance, 24 March 2025. https://www.gov.uk/government/publications/explaining-uncertainty-in-uk-intelligence-assessment/explaining-uncertainty-in-uk-intelligence-assessment — gap rationale: Ministry of Defence, "Defence Intelligence: communicating probability", 17 February 2023. https://www.gov.uk/government/news/defence-intelligence-communicating-probability
- M. D. Mastrandrea, C. B. Field, T. F. Stocker, O. Edenhofer, K. L. Ebi, D. J. Frame, H. Held, E. Kriegler, K. J. Mach, P. R. Matschoss, G.-K. Plattner, G. W. Yohe and F. W. Zwiers, *Guidance Note for Lead Authors of the IPCC Fifth Assessment Report on Consistent Treatment of Uncertainties*, IPCC, 2010. https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf
- Office of the Director of National Intelligence, *Intelligence Community Directive 206: Sourcing Requirements for Disseminated Analytic Products*, 22 January 2015. https://www.dni.gov/files/documents/ICD/ICD-206.pdf
- D. V. Budescu, S. Broomell and H.-H. Por, "Improving Communication of Uncertainty in the Reports of the Intergovernmental Panel on Climate Change", *Psychological Science*, vol. 20, no. 3, 2009, pp. 299–308. https://doi.org/10.1111/j.1467-9280.2009.02284.x
- J. A. Friedman and R. Zeckhauser, "Assessing Uncertainty in Intelligence", *Intelligence and National Security*, vol. 27, no. 6, 2012, pp. 824–847. https://doi.org/10.1080/02684527.2012.708275
