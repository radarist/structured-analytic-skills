---
name: write-imrad-report
description: "Structures an empirical report in the IMRAD convention — Introduction, Methods, Results, Discussion — with an optional executive summary above and a numbered reference list below, so a reader can audit the methods and results before meeting the interpretation. Use when findings will face reviewers or peer review: \"write this up as a scientific paper\", \"academic whitepaper on an experiment\", \"journal-style report\", \"IMRAD structure\". Not for a one-page decision brief (use `write-sbar-brief`) or for ordering an argument inside a memo (`pyramid-principle`)."
license: MIT
metadata:
  category: writing
  method: IMRAD (Introduction, Methods, Results, Discussion)
  origin: International Committee of Medical Journal Editors (Vancouver Group), Uniform Requirements 1978; adoption surveyed by Sollaci & Pereira, 2004
  version: "2.0.0"
---
# Write IMRAD Report

IMRAD splits a research report into four sections answering four questions — Introduction: what problem, and what question? Methods: what was done, in enough detail to repeat it? Results: what was observed? Discussion: what does it mean? The core principle, in the ICMJE Recommendations' words, is that the structure "is not an arbitrary publication format but a reflection of the process of scientific discovery": each section is sealed against the others, so a reader audits the evidence before meeting the interpretation. Codified for biomedical journals by the ICMJE (the Vancouver Group, first Uniform Requirements 1978) and documented as the dominant form by Sollaci and Pereira (2004), it prevents data and conclusions blending into a narrative no reader can check.

## When to invoke

Invoke when:

- A report presents empirical findings — measurements, counts, comparisons, benchmark runs — and someone will check them.
- The request names the form: "write this up as a scientific paper", "journal-style report", "IMRAD structure", "an academic whitepaper".
- The document will be cited or reviewed externally, so the method must be reproducible.

Do NOT invoke when:

- The reader needs one page and a decision, not a report — use `write-sbar-brief` (SBAR).
- The task is ordering a persuasive argument for executives — use `pyramid-principle`; IMRAD fixes section order, not argument logic.
- The literature search itself is the deliverable, with screening counts and inclusion criteria — use `systematic-review`, then report its output in IMRAD; pooling those studies' effect sizes is `meta-analysis`.
- The draft exists and needs a pre-publication audit rather than a structure — use `critique-report`.

## Procedure

### 1 — Fix the question before writing anything

Write the single question the report answers as one sentence, plus what a yes and a no would look like. Everything else is subordinate: a finding that does not bear on the question belongs in an appendix or nowhere. If the question needs more than a sentence, it is several questions — narrow the scope first.

### 2 — Introduction: context, gap, question

Provide the context or background — the nature of the problem and its significance — then name what is not yet known, then state the specific purpose, objective or hypothesis tested. Cite only directly pertinent references (two to four anchors suffices). Per the ICMJE, include no data or conclusions from the work being reported: the Introduction sets up the question and stops.

### 3 — Methods: enough detail to reproduce

State how and why the work was done this particular way: data sources with dates and versions, the retrieval or measurement procedure step by step, inclusion and exclusion criteria with a reason for each, instruments or models with their settings, and the analysis applied. Include only what was available when the plan was made; anything learned during the work belongs in Results. Name the limitations fixed in advance — sources unavailable, windows that truncate coverage. A Methods section that could be pasted into any other report is not one.

### 4 — Results: observations only

Present the findings in logical sequence, most important first, in text, tables and figures. Give numbers with units and uncertainty; report every outcome named in Methods, including null findings ("no evidence of X was found") and excluded cases with counts ("of 47 candidates, 12 met the criteria"). Do not repeat every table value in prose, and do not interpret — "the results show X matters" is a Discussion sentence. Every external number carries an inline citation.

### 5 — Discussion: interpret, bound, conclude

Begin by briefly summarising the main findings and exploring possible explanations. Emphasise what is new, and place the findings in the context of the totality of relevant evidence, including the Introduction's anchors. State limitations explicitly, distinguish statistical from practical significance, and avoid unqualified conclusions the data do not support. New hypotheses may be stated but must be labelled. Close with one sentence answering the Introduction's question, then the references.

## Output template

```
# {Title stating the finding, not the topic}

## Executive summary            {optional, 100–200 words}
{what was examined · the most important finding · confidence · the one recommended action}

## 1. Introduction
{context → what is not known → the one-sentence question → objective or hypothesis. 2–4 anchor citations. No results.}

## 2. Methods
{sources with dates/versions · procedure step by step · inclusion and exclusion criteria · instruments and settings · analysis · limitations known in advance}

## 3. Results
{most important finding first · tables · units and uncertainty · null findings and excluded counts · a citation per external number. No interpretation.}

## 4. Discussion
{main findings → explanations → what is new, against prior work → implications → limitations → labelled new hypotheses → one-sentence answer to the question}

## References
{numbered list, one entry per cited source}
```

Every section is mandatory except the executive summary: a report that omits Methods or merges Results into Discussion is not IMRAD, and Results must include the null and excluded cases, not only the positive findings.

## Worked example

The structure applied to a real study — Sollaci and Pereira's survey of IMRAD adoption in the *Journal of the Medical Library Association*, 2004 (an illustrative rendering of their published content into this template):

```
# IMRAD became the majority form of the medical research article only in the 1970s

## 1. Introduction
The scientific article evolved from the letter form of the seventeenth century to a
standardised structure. When IMRAD became the dominant pattern is not well established.
Question: during which period was IMRAD definitively and widely adopted?

## 2. Methods
Cross-sectional study; frequency of IMRAD articles measured at 5-year intervals over
1935–1985 in 4 leading internal-medicine journals — British Medical Journal, JAMA,
The Lancet, New England Journal of Medicine. Systematic sample of 1 in 10 issues;
1,297 original articles examined (341, 328, 401, 227). An article counted as IMRAD only
when the headings methods, results and discussion (or synonyms) appeared.

## 3. Results
No IMRAD article was found in 1935. The proportion passed 10% in all four journals by
1950 and rose from none to 20% over 1935–1955, then more than quadrupled over 1955–1975,
exceeding 80% in the 1970s. Full adoption: New England Journal of Medicine 1975,
British Medical Journal 1980, JAMA and The Lancet 1985.

## 4. Discussion
Although recommended since the early twentieth century, IMRAD became the majority form
only in the 1970s. Other disciplines — physics had adopted it extensively by the 1950s —
and editors' recommendations plausibly drove adherence. Limitation: four journals, one
specialty; heading order in early IMRAD articles did not match today's convention.
```

Note what the split enforces: "exceeding 80% in the 1970s" sits in Results with no explanation attached, while "editors' recommendations plausibly drove adherence" sits in Discussion, marked as conjecture. A blended draft would say "IMRAD spread in the 1970s because editors demanded it" — one sentence in which measurement and untested cause are indistinguishable.

## Verification

- [ ] The Introduction's question appears, answered, as the Discussion's last sentence — if it does not, the report answers a different question than it asked.
- [ ] No sentence in Results carries an interpretive verb (shows, proves, suggests, means, implies) — move offenders to Discussion.
- [ ] Every Results number carries a unit and either a citation or the Methods step that produced it.
- [ ] Methods names data sources with dates or versions and every selection criterion with its reason — confirm another analyst could repeat the work from that section alone.
- [ ] Null findings and excluded cases are reported with counts.
- [ ] Every inline citation resolves to a numbered entry in References and every entry is cited at least once (format with `cite-ieee`, validate with `verify-citations`).
- [ ] Discussion states the limitations, and any post-hoc hypothesis is labelled rather than presented as pre-registered.

## Pair with adjacent skills

- `cite-ieee` — formats the numbered reference list and inline markers this structure requires.
- `write-sbar-brief` — the one-page SBAR alternative when the reader needs a decision, not a report.
- `pyramid-principle` — orders the argument inside the Discussion; IMRAD orders sections.
- `critique-report` — the pre-publication audit of the finished draft.
- `grounded-answer` — verifies factual claims before they enter Results.

## Anti-patterns

- Do **not** blend interpretation into Results. Split it: Results — "the term appears in 34 of 47 documents"; Discussion — "this suggests wider mindshare, though the corpus is skewed".
- Do **not** ship a generic Methods section; if it reads as though written before the question, it cannot support reproduction.
- Do **not** present a hypothesis formed after seeing the data as though it preceded the analysis — label it post-hoc.
- Do **not** move References out of the final position, or leave inline claims unnumbered.
- Do **not** stretch IMRAD over a document with no empirical content — without Results, nothing needs the protection.

## Reference

- International Committee of Medical Journal Editors, *Recommendations for the Conduct, Reporting, Editing, and Publication of Scholarly Work in Medical Journals*, updated Jan. 2026, sect. IV.A "Preparing a Manuscript for Submission to a Medical Journal". [Online]. Available: https://www.icmje.org/recommendations/
- L. B. Sollaci and M. G. Pereira, "The introduction, methods, results, and discussion (IMRAD) structure: a fifty-year survey," *J. Med. Libr. Assoc.*, vol. 92, no. 3, pp. 364–367, Jul. 2004. PMID: 15243643. [Online]. Available: https://pmc.ncbi.nlm.nih.gov/articles/PMC442179/
- International Committee of Medical Journal Editors, *Uniform Requirements for Manuscripts Submitted to Biomedical Journals*, 1st ed., 1978 — the Vancouver Group standard that codified IMRAD, since superseded by the Recommendations above.
