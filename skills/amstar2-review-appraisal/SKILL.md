---
name: amstar2-review-appraisal
description: "Appraises a systematic review or meta-analysis with AMSTAR 2 (AMSTAR-2; Shea et al., BMJ 2017): answers the 16 checklist items from the review's report, flags flaws in the seven critical domains and derives the overall confidence rating — High, Moderate, Low or Critically low — never a summed score. Use when deciding whether a published review can be relied on, or ranking reviews for an umbrella review: \"appraise this systematic review with AMSTAR 2\", \"how trustworthy is this meta-analysis?\", \"which AMSTAR 2 items are critical?\". Not for one trial (use `assess-study-bias`), a body of evidence per outcome (use `evidence-appraisal`) or conducting a review (use `systematic-review`)."
license: "MIT (skill text); AMSTAR 2 items © Shea et al. 2017, CC BY 4.0, modified"
metadata:
  category: evidence-verification
  method: AMSTAR 2 (A MeaSurement Tool to Assess systematic Reviews, version 2)
  origin: Beverley J. Shea et al., BMJ 2017 (original AMSTAR — Shea et al., 2007)
  version: "1.0.0"
---
# AMSTAR 2 review appraisal

AMSTAR 2 (Shea et al., *BMJ* 2017) appraises systematic reviews of interventions that include randomised trials, non-randomised studies or both: 16 items answered from the review's report, seven of them **critical domains**, combined not into a score but into an overall confidence rating — High, Moderate, Low or Critically low. Its principle: one flaw in a critical domain — no protocol, thin search, unlisted exclusions, no risk-of-bias assessment, poor pooling, ignored bias, unexamined publication bias — can invalidate a review's conclusions however polished the rest looks.

## When to invoke

Invoke when:

- A decision is about to lean on a published review or meta-analysis: "appraise this systematic review with AMSTAR 2 before we rely on it", "how trustworthy is this meta-analysis?".
- Several reviews on one question disagree or must be ranked (umbrella review, overview).
- The question is which AMSTAR 2 items are critical, and what rating a set of answers yields. Non-clinical interventions (workplace, education, software) are appraised by adapting the items.

Do NOT invoke when:

- The object is a single trial or study — use `assess-study-bias` (RoB 2 / ROBINS-I).
- The question is the certainty a *body* of evidence deserves per outcome — use `evidence-appraisal` (GRADE); AMSTAR 2 rates methods, not certainty.
- The task is to *produce* a review or pool studies — use `systematic-review`, `meta-analysis`.
- The source is not a systematic review — use `rate-source-admiralty`.

## Procedure

### 1 — Identify the review and fix its question

Record the citation, the review type (RCTs only / NRSI only / both; meta-analysis or narrative synthesis) and its PICO — population, intervention, comparator, outcomes. Agree first, as the paper advises, how the items apply in the practice or policy context at hand.

### 2 — Pre-specify the critical domains and the Partial Yes convention

Default critical domains: items 2, 4, 7, 9, 11, 13, 15 (Box 1); the paper lets appraisers add or substitute — e.g. item 3 for a harms review that excluded non-randomised studies. Fix the list before answering. Fix the Partial Yes convention too: the paper adds it "to identify partial adherence" but never weights it, so the team pre-specifies (De Santis et al., 2023). Default here — a Partial Yes is a non-critical weakness; strict teams make it a flaw in a critical domain.

### 3 — Answer the 16 items from the report, quoting the evidence

Read the report, appendices and any registered protocol. Record Yes / Partial Yes / No per item — 11, 12, 15 take "No meta-analysis conducted" when nothing was pooled — plus *where* the evidence is. Partial Yes exists only for items 2, 4, 7, 8, 9; elsewhere anything short of the "For Yes" criteria is No. Never give the benefit of the doubt: "If no information is provided to rate an item … the item should be rated as a 'No'." Items 9 and 11 carry separate RCT and NRSI panels — rate both, take the weaker. Wording, options and criteria for all 16: [references/items.md](references/items.md), or `python3 scripts/amstar2.py items`.

### 4 — Classify flaws and weaknesses

A No in a critical domain is a **critical flaw**; a No elsewhere a **non-critical weakness**; a Partial Yes counts per step 2; "No meta-analysis conducted" is neither — the item does not apply. Add nothing up: the authors "strongly recommend that individual item ratings are not combined to create an overall score".

### 5 — Derive the overall rating mechanically (Box 2)

- **High** — at most one non-critical weakness, and no critical flaw.
- **Moderate** — two or more non-critical weaknesses, still no critical flaw.
- **Low** — exactly one critical flaw, whatever the number of non-critical weaknesses.
- **Critically low** — two or more critical flaws, whatever the number of non-critical weaknesses.

Box 2's footnote — accumulating non-critical weaknesses may erode confidence enough to warrant moving Moderate down to Low — is advisory; state it if applied. Run `python3 scripts/amstar2.py rate --file answers.json` for the rating and rule trace.

### 6 — Write the appraisal

Fill the template: rating, each critical flaw with its quoted evidence, the non-critical weaknesses, and the implications — what the conclusions can still be used for, and what needs an independent check.

## Output template

```
## AMSTAR 2 appraisal — {review citation}
**PICO:** P={…} | I={…} | C={…} | O={…}   **Type:** {RCTs / NRSI / both; meta-analysis?}
**Conventions:** critical domains {2,4,7,9,11,13,15 | override + reason}; Partial Yes = {weakness | flaw}

| Item | Response | Critical | Counts as | Evidence (section / quote) |
|---|---|---|---|---|
| {1 … 16} | {Y / PY / N / NMA} | {✔ / –} | {flaw / weakness / – / n/a} | {where} |

**Critical flaws ({n}):** {item + one line of evidence each}
**Non-critical weaknesses ({n}):** {items}
**Overall confidence: {High | Moderate | Low | Critically low}** — {Box 2 rule applied}
**Implications:** {what the conclusions support; what must be checked independently}
```

Mandatory: every item answered (no blanks, no "not applicable"), the conventions line, the rule applied, the implications. A rating without per-item evidence is not an appraisal.

## Worked example

Review (illustrative): "Digital cognitive behavioural therapy for insomnia in adults: systematic review and meta-analysis of 12 randomised trials" (2024). PICO: adults with chronic insomnia; app-delivered CBT-I; sleep-hygiene education; sleep-onset latency and Insomnia Severity Index. From the report: items 1, 3, 5, 8, 9, 11, 12, 13, 14, 16 = Yes; 2 = Partial Yes (protocol agreed, not registered); 4 = Partial Yes (MEDLINE, Embase, PsycINFO, CENTRAL, but no registry or grey-literature search and a search 30 months old); 6 = No (one extractor); 7 = No (PRISMA counts only); 10 = No; 15 = No (12 trials pooled, no funnel plot). `python3 scripts/amstar2.py rate --demo`:

```
Critical flaws (2): item 7, item 15
Non-critical weaknesses (4): item 2, item 4, item 6, item 10

Rule trace (Box 2, Shea et al. 2017):
  critical domains: 2, 4, 7, 9, 11, 13, 15 (AMSTAR 2 Box 1)
  Partial Yes convention: weakness
  critical flaws = 2 (items 7, 15)
  non-critical weaknesses = 4 (items 2, 4, 6, 10)
  critical flaws 2 > 1 -> Critically low

Overall confidence: CRITICALLY LOW — Two or more critical flaws, whatever the number of non-critical weaknesses
```

Implications: unlisted exclusions and unexamined small-study bias could each shift the pooled effect, so treat it as a lead and check the trials with `assess-study-bias`. The rating does not hinge on the convention — under `--partial-yes flaw` items 2 and 4 also become flaws and it stays Critically low; say so whenever it *would* change.

## Verification

- [ ] All 16 answered, each citing its evidence (unreported means No); Partial Yes only on 2, 4, 7, 8, 9; "No meta-analysis conducted" only on 11, 12, 15, consistently.
- [ ] Critical domains and the Partial Yes convention were fixed before answering, and appear in the output.
- [ ] Recompute with `scripts/amstar2.py rate` — flaws, weaknesses and the Box 2 rule must match the write-up; item 15 answered, not skipped, for any review with a meta-analysis; no numeric score anywhere.

## Companion tool

`scripts/amstar2.py` (stdlib only) applies Box 1 / Box 2 mechanically: a per-item table (response, critical?, counts as), counted critical flaws and non-critical weaknesses, the rating with its rule trace, and warnings (inconsistent no-meta-analysis answers, lenient conventions). Judgements stay yours; it removes counting slips.

```bash
python3 scripts/amstar2.py items                     # wording, options, criteria; --template → schema
python3 scripts/amstar2.py rate --file answers.json  # --json; --partial-yes weakness|flaw|met; --critical …
python3 scripts/amstar2.py rate --demo               # the worked example
python3 scripts/amstar2.py --selftest
```

`answers.json` holds `review`, `question`, `items` (`"2": {"response": "PY", "note": "…"}`) and optional `critical_override` / `partial_yes`; items 9 and 11 accept `{"RCT": "Y", "NRSI": "PY"}`.

## Pair with adjacent skills

- `systematic-review` — produces the document this skill appraises; its protocol and PRISMA flow are what items 2, 4, 5, 7 look for.
- `assess-study-bias` — appraises the primary studies; item 9 asks whether the review did so satisfactorily.
- `evidence-appraisal` — GRADE the findings' certainty once the review is trustworthy enough to use.
- `meta-analysis` — items 11, 12, 14, 15 concern the pooling it performs.
- `rate-source-admiralty` — grade the review as a source afterwards; a Critically-low review is no "A".
- Methodology counterpart: [methodologies/scientific-methods/evidence-appraisal.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/scientific-methods/evidence-appraisal.md) — the frame this instrument sits inside.

## Anti-patterns

- Do **not** rate a review by its journal, authors or "systematic" label — only by the 16 answers.
- Do **not** treat "Partial Yes" as "Yes" — it marks partial adherence, a weakness by default.
- Do **not** skip item 15 for a review with a meta-analysis — uninvestigated publication bias is a critical flaw.
- Do **not** answer "not applicable" or "cannot tell"; AMSTAR 2 removed both — unreported means No.
- Do **not** sum items into a score or percentage; the instrument's authors reject this explicitly.
- Do **not** appraise primary studies with AMSTAR 2, report this rating as GRADE certainty, or change the critical domains after seeing the answers.

## Reference

- B. J. Shea, B. C. Reeves, G. Wells, M. Thuku, C. Hamel, J. Moran, D. Moher, P. Tugwell, V. Welch, E. Kristjansson, D. A. Henry, "AMSTAR 2: a critical appraisal tool for systematic reviews that include randomised or non-randomised studies of healthcare interventions, or both," *BMJ*, vol. 358, j4008, 2017. doi:10.1136/bmj.j4008 — item wording, Box 1 (critical domains), Box 2 (ratings); licensed CC BY 4.0.
- AMSTAR 2 checklist and guidance document, 2017, https://amstar.ca/Amstar_Checklist.php — the authoritative response options and scoring criteria. Separately copyrighted and not reproduced here; consult it when an appraisal must be defended verbatim.
- K. De Santis, D. Pieper, R. Lorenz, U. Wegewitz, W. Siemens, K. Matthias, "User experience of applying AMSTAR 2 …: a commentary," *BMC Med Res Methodol*, vol. 23, 63, 2023. doi:10.1186/s12874-023-01879-8 — Partial Yes weighting is a team decision.

## Attribution and licence

The 16 item questions and the Box 1 critical-domain list used here and in [references/items.md](references/items.md) are reused from Shea et al., *BMJ* 2017;358:j4008 (doi:10.1136/bmj.j4008), **licensed CC BY 4.0** — <https://creativecommons.org/licenses/by/4.0/>. **Changes made:** the item text is condensed and reformatted, and the short labels, the Y/PY/N/NMA response codes, the per-item criteria, the overall-confidence descriptions and all surrounding guidance are this skill's own wording, not the original authors'. The criteria and rating descriptions in particular are restatements, not reproductions of the separately copyrighted AMSTAR 2 checklist. Neither the AMSTAR 2 authors nor *BMJ* endorse this skill; everything in it other than the CC BY material is MIT-licensed.
