---
name: systematic-review
description: "Runs a reproducible literature review to PRISMA 2020 — a pre-registered protocol, an exhaustive documented search, dual title/abstract screening with an agreement statistic, full-text eligibility with logged exclusion reasons, per-study grading and a synthesis — and delivers the PRISMA flow counts plus an audit trail of every included and excluded record. Use when reproducibility matters: \"systematic review of the evidence on X\", \"what does the research say about Y?\", \"PRISMA review\", \"survey the literature with explicit inclusion criteria\". Not for pooling already-selected studies into an effect estimate (use `meta-analysis`) or answering one factual question (use `grounded-answer`)."
license: MIT
metadata:
  category: quantitative
  method: Systematic review reported to PRISMA 2020
  origin: M. J. Page, J. E. McKenzie, P. M. Bossuyt et al., PRISMA 2020 Statement, 2021 (after Moher et al., 2009)
  version: "2.0.0"
---
# Systematic Review (PRISMA 2020)

A systematic review answers a pre-specified question by searching for all the evidence bearing on it, screening it against criteria fixed in advance, and reporting the process in enough detail that another team could repeat it and get the same set. PRISMA 2020 (Page et al., *BMJ*, 2021) is the reporting standard: 27 checklist items and a flow diagram whose counts must reconcile stage by stage. Its principle is that the search and the criteria are decided *before* the results are seen and every exclusion is logged with a reason — which prevents the failure the method exists to stop: a "review" assembled from whichever sources confirmed the reviewer's expectation, the inconvenient ones quietly absent.

## When to invoke

Invoke when:

- A comprehensive, repeatable account of a literature is wanted: "systematic review of {topic}", "what does the research say about {X}?", "what's the evidence base for {claim}?".
- A report will be peer-reviewed or cited, so the search must be defensible and re-runnable.
- Conflicting studies must be assembled and characterised before anyone pools or summarises them.

Do NOT invoke when:

- The included studies are fixed and comparable and one pooled estimate is wanted — `meta-analysis`.
- One factual question needs one sourced answer — `grounded-answer`.
- A quick scan will do; a systematic review is expensive, so call an informal survey a scan.
- The task is judging one study's internal validity — `assess-study-bias`.
- The question is how much certainty the assembled body deserves — `evidence-appraisal`.

## Procedure

### 1 — Pre-register the protocol

Before searching, write down the question (PICO for clinical work; PECO or free-form otherwise), the inclusion criteria (date window, designs, languages, source types), the exclusion criteria, the exact search strings per database with the date each was run, the screening procedure and the quality threshold. Publish or timestamp it. Every later amendment is logged with its reason and date; an unlogged mid-review criterion change is what separates "systematic" from "ad hoc".

### 2 — Identify records and deduplicate

Run every pre-registered search and record the raw yield per source, plus registers, backward and forward citation snowballing, and any grey-literature source in the protocol. Report search strategies in full — PRISMA-S (Rethlefsen et al., 2021) is the extension for this step. Deduplicate on DOI, then URL, then normalised title, recording the number removed; that count is the flow diagram's first arrow and must reconcile.

### 3 — Screen titles and abstracts, in duplicate

Two screeners independently decide include / exclude on title and abstract alone, erring toward inclusion when uncertain. Measure agreement with Cohen's kappa on the dual-screened set — `scripts/prisma.py kappa` prints it with a Landis–Koch band and the disagreement indexes. Below about 0.6 (moderate) the criteria are ambiguous: refine and re-screen rather than adjudicating case by case. Route every disagreement to a third reviewer and log the resolution.

### 4 — Assess full texts for eligibility and log every exclusion

Retrieve and read the full text of every surviving record; record any that could not be retrieved. Apply the protocol's criteria strictly and log each exclusion against exactly one reason from the fixed vocabulary in [references/prisma-flow-and-screening.md](references/prisma-flow-and-screening.md) — wrong population or scope, outcome not measured, outside the date window, insufficient methodological detail, or a secondary report of an included primary. This exclusion list is a mandatory part of the review, not a droppable appendix.

### 5 — Grade the included studies

For each included study record the design, sample size, the key finding in one sentence, a source-reliability grade via `rate-source-admiralty`, and a risk-of-bias judgement via `assess-study-bias` for randomized trials (or a stated lighter heuristic otherwise). These grades weight the synthesis and must travel with every claim drawn from the study.

### 6 — Synthesise, and validate the flow arithmetic

Narrate what the included set collectively shows: convergent findings, divergent findings with the methodological reason for the divergence (different populations, measures or designs), and the gaps the literature does not answer. Cite each claim to specific studies. If — and only if — the outcomes share a scale, hand pooling to `meta-analysis`. Then validate the counts with `scripts/prisma.py flow`: every stage must equal the previous minus its exclusions.

## Output template

```
# Systematic review — {topic}

**Protocol (pre-registered {date}):**
- Question: {PICO / PECO / free-form}
- Inclusion: {criteria}   Exclusion: {criteria}
- Sources searched: {database → exact query string → date run}
- Quality threshold: {Admiralty grade, RoB judgement}
- Amendments: {change, reason, date | none}

**PRISMA 2020 flow:**
- Identification: {N1} records identified; {D} duplicates removed
- Screening: {N2} screened; {E1} excluded at title/abstract; dual-screened {n}, Cohen's kappa {k}
- Eligibility: {N3} full texts assessed; {E2} excluded, by reason: {reason: count, …}
- Included: {N4} studies in the synthesis ({N5} in quantitative synthesis)

**Included studies ({N4}):** {table: citation | year | design | n | Admiralty | RoB | key finding}
**Excluded at full text ({E2}):** {table: citation | exclusion reason}
**Synthesis:** {convergent findings | divergent findings and why | gaps}
**References:** {numbered list}
```

Mandatory: the pre-registration date, the exact queries with run dates, all four flow stages with counts that reconcile, the exclusion table with reasons, and the per-study grades. A review that omits the exclusion list is not systematic.

## Worked example (illustrative)

Question: *do four-day-workweek trials show a measurable productivity effect?* Protocol pre-registered 2025-03-04: controlled trials or matched pilots with a productivity metric, at least 20 participants, published 2015 or later; opinion pieces and surveys without a productivity measure excluded. Searches on OpenAlex, SSRN and two industry-report repositories yielded 1,240 records; 315 duplicates removed. Two screeners dual-screened a 93-record calibration sample (10 % of those screened); `scripts/prisma.py kappa --file examples/dual-screening.json --adjudicate` reports:

```
paired decisions: 93
observed agreement: 0.914
expected agreement (chance): 0.571
Cohen's kappa: 0.800 (substantial)
disagreements (0-based indexes, route to adjudication): 7, 12, 19, 28, 33, 46, 58, 77
```

Substantial agreement, so screening proceeded: 840 excluded at title/abstract, 85 full texts assessed, 61 excluded (no productivity metric 41, n < 20 twelve, opinion piece 8), **24 included** — 9 low risk of bias, 11 some concerns, 4 high. The flow arithmetic validates:

```
$ python3 scripts/prisma.py flow --identified 1240 --deduped 315 --screened 925 \
    --excluded-title 840 --fulltext 85 --excluded-fulltext 61 --included 24
  [OK] identified - duplicates = screened: 1240 - 315 = 925
  [OK] screened - title/abstract exclusions = full-text assessed: 925 - 840 = 85
  [OK] full-text assessed - full-text exclusions = included: 85 - 61 = 24
```

The nine low-risk studies show a consistent small positive effect; the four high-risk studies drive most of the spread. Pooling is handed to `meta-analysis` only for the subset reporting a common productivity scale.

## Verification

Before the review ships, confirm:

- [ ] The protocol carries a date earlier than the first search, and every amendment is logged with its reason.
- [ ] Every database query is reproduced verbatim with the date it was run.
- [ ] The flow counts reconcile — run `python3 scripts/prisma.py flow …`; a non-zero exit means a stage does not add up.
- [ ] Cohen's kappa is reported for the dual-screened sample and disagreements were adjudicated, not silently resolved.
- [ ] Every full-text exclusion has exactly one logged reason and appears in the exclusion table.
- [ ] Each included study carries its design, n, source grade and risk-of-bias judgement.
- [ ] Nothing is pooled unless the outcomes share a scale; otherwise the synthesis is narrative.

## Companion tool

`scripts/prisma.py` (stdlib only, Python 3.9+) does the review's bookkeeping. `flow` validates the PRISMA 2020 arithmetic chain stage by stage, prints the flow table, and exits non-zero if any stage fails to reconcile. `kappa` computes Cohen's kappa for two screeners from a JSON list of `{"a": 0/1, "b": 0/1}` decisions, reports observed and chance agreement with an interpretation band, and with `--adjudicate` lists the 0-based indexes of disagreements to route to a third reviewer.

```bash
python3 scripts/prisma.py flow --identified 1240 --deduped 315 --screened 925 \
    --excluded-title 840 --fulltext 85 --excluded-fulltext 61 --included 24
python3 scripts/prisma.py kappa --file examples/dual-screening.json --adjudicate
python3 scripts/prisma.py --selftest        # 7 hand-verified checks
```

`examples/dual-screening.json` is the 93-record calibration sample used in the worked example. Usable without the tool — both computations are elementary; the tool keeps the audit trail consistent and catches counts that do not reconcile.

## Pair with adjacent skills

- `meta-analysis` — the quantitative endpoint once the included studies share an outcome scale.
- `assess-study-bias` — the per-study RoB 2 grading in step 5.
- `evidence-appraisal` — GRADE the assembled body of evidence afterwards.
- `rate-source-admiralty` — the source-reliability grade in the included-studies table.
- `write-imrad-report` — renders the review; its Methods section is the pre-registered protocol.
- Methodology counterpart: [methodologies/research-methods/systematic-literature-review.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/research-methods/systematic-literature-review.md) — full protocol detail and PRISMA background.

## Anti-patterns

- Do **not** search first and write the criteria afterwards — that is a scan wearing a systematic-review label.
- Do **not** hide the excluded sources; the exclusion list with reasons is part of the evidence.
- Do **not** single-screen a large corpus; dual screening with a reported agreement statistic is the standard.
- Do **not** pool outcomes that are not the same outcome; two studies measuring "productivity" differently do not average.
- Do **not** publish flow counts that do not reconcile — arrows that fail to subtract are a visible error.

## Reference

- M. J. Page, J. E. McKenzie, P. M. Bossuyt, et al., "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews," *BMJ*, vol. 372, p. n71, 2021. doi:10.1136/bmj.n71 — the 27-item checklist and the flow diagram.
- M. L. Rethlefsen, S. Kirtley, S. Waffenschmidt, et al., "PRISMA-S: an extension to the PRISMA Statement for Reporting Literature Searches in Systematic Reviews," *Systematic Reviews*, vol. 10, no. 1, art. 39, 2021. doi:10.1186/s13643-020-01542-z
- J. P. T. Higgins, J. Thomas, J. Chandler, et al. (eds.), *Cochrane Handbook for Systematic Reviews of Interventions*, version 6.5. Cochrane, 2024. https://training.cochrane.org/handbook
- J. Cohen, "A Coefficient of Agreement for Nominal Scales," *Educational and Psychological Measurement*, vol. 20, no. 1, pp. 37–46, 1960. doi:10.1177/001316446002000104 — the screening agreement statistic.
- J. R. Landis and G. G. Koch, "The Measurement of Observer Agreement for Categorical Data," *Biometrics*, vol. 33, no. 1, pp. 159–174, 1977. doi:10.2307/2529310 — the kappa interpretation bands the tool prints.
