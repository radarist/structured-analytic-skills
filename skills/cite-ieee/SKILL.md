---
name: cite-ieee
description: "Converts a report's sources into IEEE numbered-bracket citations — inline `[1]`, `[1], [4]`, `[2]–[5]` markers numbered by first appearance, plus an end-of-document References list formatted per source type — and checks that the numbering and the list agree. Use when a document carries three or more sources and must look publishable: \"format these references in IEEE style\", \"add citations to this report\", \"IEEE reference list\", \"renumber my citations\". Not for checking whether a DOI or arXiv ID resolves (use `verify-citations`) and not for author-year styles such as APA."
license: MIT
metadata:
  category: writing
  method: IEEE numbered-bracket citation style
  origin: IEEE Publication Operations, IEEE Reference Guide (V 3.28.2025) and IEEE Editorial Style Manual for Authors (2024)
  version: "2.0.0"
---
# Cite IEEE

IEEE style cites sources by number, not by author and year: a bracketed numeral on the line and inside the punctuation marks each claim, and a numbered list at the end gives each source once, in the order the numbers were first used. The rules come from the *IEEE Reference Guide* (IEEE Publication Operations, V 3.28.2025) and the "References" section of the *IEEE Editorial Style Manual for Authors* (2024), whose governing constraint is one source per number — "Do not combine references. There must be only one reference with each number." The core principle is that the numbering is a bijection between claims and sources: every marker resolves to exactly one entry and every entry is cited at least once. It prevents the failure in which a report looks sourced but its brackets point at gaps, at duplicate entries, or at entries no reader can match back to the sentence that needed them.

## When to invoke

Invoke when:

- A report, paper or long-form answer carries three or more sources and will be read as a publishable document.
- The request names the style: "format these references in IEEE style", "add citations to this report", "IEEE reference list", "renumber my citations after the edit".
- Sources were added or removed during editing, so the numbering may no longer follow first appearance.

Do NOT invoke when:

- The question is whether an identifier is real and resolvable — DOI, arXiv ID, PubMed ID, URL — use `verify-citations`; formatting comes first, validation second.
- The house style is author-year (APA, Chicago, Harvard) or the venue publishes its own style sheet — follow that style; these rules are IEEE-specific.
- A conversational answer leans on one or two links; inline attribution is enough without the numbering machinery.
- The claims themselves are unverified — use `grounded-answer` before dressing them in brackets.

## Procedure

### 1 — Collect the sources in order of first citation

Walk the document top to bottom and list every source at the point where it is first used, including sources named only in a figure caption or a table note. Record for each what type it is — periodical, conference paper, book or chapter, preprint, news article, website, patent, standard, report, thesis, dataset — because the type decides the entry's shape. Merge duplicates now: the same source cited three times is one entry.

### 2 — Number by first appearance and mark the text

Assign `[1]` to the first source used, `[2]` to the next, and so on; later citations of the same source reuse the number. Put the bracket on the line and inside the punctuation, as close to the claim it supports as possible: "… a 409% increase [1], [2]." Cite several sources as separate brackets — the guide's own examples are `[4], [5]` and `[2], [4]–[7], [9]` — never as `[1][2]` and never as `[1, 4]`, which the guide reads as "reference 1, part 4". Cite part of a source with a locator inside the bracket: `[3, pp. 5–10]`, `[3, Fig. 1]`, `[3, eq. (2)]`. Note that the 2025 guide writes ranges out in text as `[1], [2], [3], [4]`; a compressed `[2–5]` is a common house variant that `scripts/ieee.py check` also accepts.

### 3 — Format each entry by source type

Build the `## References` list, one numbered entry per source, using the basic format for its type — see `references/formats.md` for the per-type catalogue with the guide's own examples. Across all types: initials precede the surname; list up to six authors and use "et al." from seven; every entry carries at least a year; every entry ends with a period except one ending in a URL; include the DOI when one exists, and put a DOI or accessed date before any trailing URL.

### 4 — Check the numbering against the list

Verify that the numbers run 1, 2, 3 … in order of first citation with no gaps, that every cited number has an entry, that every entry is cited at least once, and that no source appears twice under different numbers. Run `python3 scripts/ieee.py check --file report.md`; it reports these as errors and entry-style problems (missing period, missing year, unquoted title, missing venue, URL without an access date) as warnings.

### 5 — Renumber after every edit, then hand off for validation

Editing moves citations, so re-run the numbering rather than patching it by hand: `python3 scripts/ieee.py renumber --file report.md` renumbers by first appearance and reorders the list, flagging entries that are uncited or missing. Only when the numbering is clean does validation make sense — hand the reference list to `verify-citations` to check that each DOI, arXiv ID and URL is well formed and resolves.

## Output template

Inline, in the body:

```
{claim} [{n}].            e.g. Data-center revenue reached $47.5B in Q4 FY2024 [1].
{claim} [{n}], [{m}].     e.g. … a 409% year-over-year increase [1], [2].
{claim} [{n}, {locator}]. e.g. … as the guide requires [5, pp. 12–14].
```

At the end of the document:

```
## References

[1] {author initials and surname(s)}, "{title in sentence case}," {venue with vol., no., pp.}, {Abbrev. Month} {year}, doi: {doi}.
[2] {author}, "{title}," {year}, arXiv:{id}.
[3] {issuing entity}, "{document type}," {authority}, {city, state, country}, {Abbrev. Month} {day}, {year}. [Online]. Available: {url}
```

Mandatory in every entry: an author or issuing organisation, a title, a venue or publisher, and a date of at least a year; entries must be numbered consecutively from 1 with no gaps, and each number must be used at least once in the text.

## Worked example

`examples/draft.md` is a four-sentence draft with the classic faults — the first citation in the text is `[3]`, `[5]` is missing from the list, `[6]` is listed but never cited, `[7]` is cited with no entry, and one entry carries a URL with no access date. Running the checker:

```
$ python3 scripts/ieee.py check --file examples/draft.md
examples/draft.md: 5 in-text citation groups (5 distinct sources); reference list: 5 entries (lines 7–11, heading at line 5)

 line  level    code            ref    problem
    3  ERROR    no-entry        [7]    [7] is cited but has no entry in the reference list
    3  ERROR    order           [3]    [3] is first cited before [1], [2] first appear
    3  ERROR    sequence        [3]    cited in the order [3], [1], [2], [4], [7]; IEEE numbers sources 1, 2, 3, ... by first citation (renumber: [3]->[1], [1]->[2], [2]->[3], [7]->[5])
   10  WARNING  no-accessed     [4]    URL without an access date; add "Accessed: Mon. D, YYYY." before "[Online]. Available:"
   11  ERROR    list-gap        [5]    gap in the reference list: no entry for [5]
   11  ERROR    uncited         [6]    [6] is listed but never cited in the text

5 errors, 1 warning — FAIL
```

`python3 scripts/ieee.py renumber --file examples/draft.md` then rewrites the document, reporting the mapping `[3]→[1]`, `[1]→[2]`, `[2]→[3]`, `[7]→[5]` (placeholder inserted for the missing entry) and moving the uncited `[6]` to the end. Formatting the same three sources from structured fields in `examples/refs.json`:

```
$ python3 scripts/ieee.py format --file examples/refs.json
[1] S. Dhuliawala et al., "Chain-of-Verification reduces hallucination in large language models," 2023, arXiv:2309.11495.
[2] A. Vaswani et al., "Attention is all you need," in Proc. Adv. Neural Inf. Process. Syst. (NeurIPS), 2017, pp. 5998–6008.
[3] M. J. Page et al., "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews," BMJ, vol. 372, 2021, Art. no. n71, doi: 10.1136/bmj.n71.
```

Three details to notice: the preprint entry puts the year before the identifier — `2023, arXiv:2309.11495.` — which is the guide's "Preprint arXiv" basic format `J. K. Author, "Title of paper," year, arXiv number.`; each source has seven or more authors, so all three collapse to "et al."; and the PRISMA entry has an article ID rather than a page range, so it renders as `Art. no. n71` with the DOI last.

## Verification

- [ ] Recount the numbering: the first bracket in the text is `[1]`, and each new source takes the next unused integer — re-run `scripts/ieee.py check` after every edit rather than trusting the earlier pass.
- [ ] Confirm every cited number has exactly one entry and every entry is cited at least once; no gaps, no duplicates, no source listed twice under different numbers.
- [ ] Confirm each entry carries an author or issuing organisation, a title, a venue and at least a year, and ends with a period unless it ends with a URL.
- [ ] Confirm every DOI that exists is present, and that a DOI or accessed date precedes any trailing URL.
- [ ] Confirm brackets sit inside the sentence punctuation and next to the claim they support, not parked at the end of a paragraph.
- [ ] Hand the finished list to `verify-citations` and confirm every identifier resolves before the document ships.

## Companion tool

`scripts/ieee.py` (Python 3.9+, stdlib only) mechanises the numbering rules. `check --file report.md` finds `[n]`, `[1], [4]`, `[2]–[5]`, `[2–5]`, `[7, pp. 12–14]` (the house `[1, 4]` form is accepted too, and `renumber` rewrites it to the guide's separate brackets) and reports errors (first-citation order, gaps, duplicates, uncited/missing entries) and warnings (period, year, quoted title, venue, `Accessed:` for URLs); `--json`; exit 1 on errors. `renumber --file report.md [--write out.md]` renumbers by first appearance and reorders the list (uncited/missing entries flagged). `format --file refs.json [--md]` renders journal, conference, book, chapter, website/news, arXiv, patent, standard, thesis and report entries per the IEEE Reference Guide (V 3.28.2025). `--demo` reproduces the worked example; `--selftest` checks the guide's own examples.

```
$ python3 scripts/ieee.py check --file draft.md
draft.md: 2 in-text citation groups (2 distinct sources); reference list: 2 entries (lines 5–6, heading at line 3)

 line  level    code            ref    problem
    1  ERROR    order           [2]    [2] is first cited before [1] first appears
    1  ERROR    sequence        [2]    cited in the order [2], [1]; IEEE numbers sources 1, 2, 3, ... by first citation (renumber: [2]->[1], [1]->[2])

2 errors, 0 warnings — FAIL
```

The skill is fully usable without the tool.

## Pair with adjacent skills

- `verify-citations` — the validation pass after formatting: cite first, then check that each identifier resolves.
- `write-imrad-report` — the research-report structure whose References section this fills.
- `grounded-answer` — produces the verified claims that earn a citation in the first place.
- `systematic-review` — supplies large, screened source sets that need consistent numbering.

## Anti-patterns

- Do **not** use author-year form such as `(Smith, 2024)`. IEEE is numbered; mixing the two makes the list unusable.
- Do **not** give a source a second number when it is cited again. One source, one number, for the whole document.
- Do **not** write `[1][2]` or `[1, 2]`; separate the brackets as `[1], [2]` — a comma inside a bracket marks a locator, not a second source.
- Do **not** drop the DOI when one exists — it is the durable pointer, and URLs rot.
- Do **not** cite a specific page by adding a duplicate entry; put the locator in the bracket as `[3, pp. 5–10]`.
- Do **not** leave a paraphrased source uncited. Either attribute it or cut the sentence.
- Do **not** treat formatting as verification: a perfectly styled entry can still point at a paper that does not exist.

## Reference

- IEEE Publication Operations, *IEEE Reference Guide*, V 3.28.2025. Piscataway, NJ, USA: IEEE, 2025, §I "Citing References", §II "Style", §III "Notes About Online References". [Online]. Available: https://ieeeauthorcenter.ieee.org/wp-content/uploads/IEEE-Reference-Guide.pdf — source of the per-type basic formats, e.g. the preprint entry "S. Urazhdin et al., ... 2003, arXiv:0303149."
- IEEE Publishing Operations, *IEEE Editorial Style Manual for Authors*, updated Jul. 29, 2024, "References", pp. 13–14. [Online]. Available: https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE-Editorial-Style-Manual-for-Authors.pdf
- Per-type basic formats and the guide's own examples: [references/formats.md](references/formats.md).
