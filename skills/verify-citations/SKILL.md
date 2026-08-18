---
name: verify-citations
description: "Validates every scholarly identifier in a reference list — DOI, arXiv, ISBN, PMID, PMCID, ORCID, URL — against its canonical format and check digit, then reports PASS / REVIEW / FAIL per citation. Use when a draft's references need checking before it ships, or on requests like \"are these citations real?\", \"check these DOIs are valid\", or \"did the model invent this reference?\". Not for formatting a reference list — use `cite-ieee` instead."
license: MIT
metadata:
  category: evidence-verification
  method: Scholarly identifier format and checksum validation (ISO 26324, ISO 2108, ISO/IEC 7064)
  origin: ISO/IEC identifier standards; arXiv identifier scheme (Cornell University, 2007)
  version: "2.0.0"
---

# Verify Citations

Fabricated and decayed references are the most visible failure mode of machine-assisted writing, and the cheapest to catch: a DOI that does not match the ISO 26324 pattern, an ISBN whose check digit fails the ISO 2108 arithmetic, or an arXiv identifier whose month field reads `13` is provably wrong before anyone opens a browser. This skill runs that structural pass over every identifier in a reference list and assigns each one a verdict — PASS, REVIEW or FAIL — so nothing malformed reaches a reader.

## When to invoke

Invoke when:

- A draft carries a reference list and is about to be published, sent, or filed.
- A reader asks whether the references are genuine: "are these citations real?", "did the model make this up?".
- A reference list was assembled from several sources and may contain transcription damage (truncated DOI suffixes, `doi.org/` prefixes left in, hyphenated ISBNs pasted from a catalogue).

Do NOT invoke when:

- The reference list still needs to be written or reformatted — that is `cite-ieee` territory; run this skill afterwards on what it emits.
- The question is whether a *claim* is true rather than whether its citation is well-formed — use `grounded-fact-check`, or `grounded-answer` when the answer itself must be sourced.
- A single source's trustworthiness is at issue rather than the identifier's validity — use `rate-source-admiralty`, or `sift-source-check` for an unfamiliar publisher.

## Scope: what format validation can and cannot prove

A PASS means the identifier is *well-formed*, not that it points at the paper the text claims. Structural validation catches fabricated DOIs, malformed arXiv identifiers, failed ISBN and ORCID check digits, placeholder URLs, and out-of-range PMIDs. It cannot catch a correctly-formed DOI that resolves to a different paper, link rot behind a live URL, a retracted paper, or a preprint later published elsewhere. Resolution against the DOI handle system, the arXiv API and Open Library closes part of that gap and is available in the companion tool behind an explicit `--online` flag; the rest needs a human or a subject database.

## Procedure

### 1 — Parse the reference list

Locate the references section (a heading containing "References", or the first run of lines beginning `[N]`). Treat each numbered entry as one unit so verdicts can be reported against the citation a reader will see, not against a naked string. Wrapped entries, CRLF line endings and entries inside code fences all occur in real drafts — keep the entry number attached to every identifier extracted from it.

### 2 — Extract every identifier

From each entry pull: DOIs (`doi: 10.…`, `https://doi.org/10.…`, bare `10.…`), arXiv identifiers in both schemes, `PMID:` and `PMC` numbers, ISBNs (10 and 13, hyphenated or not), ORCIDs, and URLs following `Available:` or appearing inline. Strip trailing sentence punctuation and unbalanced brackets before matching, and unwrap `doi.org/` and `dx.doi.org/` prefixes so the identifier is normalised to its canonical form.

### 3 — Apply the format rules

Match each identifier against its standard: DOI `10.NNNN(.N)*/suffix` with no whitespace (a Crossref convention; ISO 26324 permits any Unicode graphic in the suffix, so SICI-style DOIs with angle brackets validate); arXiv new scheme `YYMM.NNNN(N)` with a month of 01–12, four digits before 1501 and five from 1501, optional `vN`; arXiv old scheme `archive[.SUBJ]/YYMMNNN` from 9107 to 0703; PMID 1–8 digits; URLs requiring scheme plus host. Never date-check against the wall clock — that makes the same reference list pass today and fail next year.

### 4 — Compute the check digits

ISBN-13: weight the first twelve digits alternately ×1 and ×3; the sum plus the check digit must be divisible by 10. ISBN-10: weight the nine digits ×10 down to ×2, where `X` is 10; the total mod 11 must be 0. ORCID: ISO/IEC 7064 MOD 11-2. A failed check digit is a FAIL, not a REVIEW — arithmetic does not have opinions.

### 5 — Assign a verdict and report

PASS for well-formed identifiers, REVIEW for anything suspicious but not provably wrong (reserved example domains per RFC 2606, `http` where `https` is expected, a truncated-looking DOI suffix), FAIL for anything that violates its standard. Emit the report below, then hand FAIL entries to `abstain-or-escalate` to decide between replacement, removal with a note, or holding the document.

## Output template

Every citation in the document must appear exactly once in the report — a silently skipped reference defeats the purpose. The verdict line and the summary counts are mandatory.

```
## Citation validation — {document title}

[{n}] {first 60 characters of the reference}
    {PASS|REVIEW|FAIL}  {type}  {normalised identifier}
            {note: | warn: | error:} {reason, naming the standard violated}

Summary: {k} identifiers in {m} entries -- PASS {p}, REVIEW {r}, FAIL {f}
Verdict: {PASS|REVIEW|FAIL}
Action:  {none | listed REVIEW items checked by hand | FAIL items replaced or removed with a note}
```

## Worked example

A four-entry reference list is validated with `python3 scripts/citecheck.py --demo`. Entry 1 carries the Chain-of-Verification preprint, entry 2 a news article behind a placeholder domain, entry 3 an invented DOI, and entry 4 Bishop's *Pattern Recognition and Machine Learning*:

```
citecheck validate: 4 entries, 4 identifiers

[1] S. Dhuliawala et al., "Chain-of-Verification...
    PASS    arxiv   2309.11495
            note:  new scheme, 5-digit era (2023-09)

[2] S. Reporter, "Article," Publication, 2024. [O...
    REVIEW  url     https://example.com/article
            warn:  reserved example domain (RFC 2606) - looks like a placeholder

[3] J. Smith, "Paper," Journal, vol. 5, no. 2, 20...
    FAIL    doi     10.invalid-fake
            error: does not match 10.NNNN/suffix (Crossref pattern; ISO 26324 itself sets no digit limit on the registrant code)

[4] C. M. Bishop, Pattern Recognition and Machine...
    PASS    isbn13  9780387310732
            note:  ISBN-10 equivalent 0387310738
```

Read the verdicts, not the count: entry 3 is the one that matters. `10.invalid-fake` has no digits after `10.`, which no registrant prefix can produce, so it is a fabrication rather than a typo and the entry must be replaced or removed. Entry 2 is well-formed but points at a reserved domain, so it needs a human to find the real article. Entry 4 shows the ISBN-13 check digit passing and its ISBN-10 equivalent derived — useful when a catalogue lists one and the draft cites the other. Overall verdict FAIL, exit code 1: this reference list does not ship as it stands.

## Verification

Before the report is accepted:

- [ ] Every reference in the document appears in the validation list — count the entries in the source and the entries in the report; the two numbers must match.
- [ ] Every identifier carries exactly one verdict from PASS / REVIEW / FAIL, and the summary counts sum to the identifier total.
- [ ] Each FAIL names the standard it violates (ISO 26324, ISO 2108, ISO/IEC 7064, the arXiv scheme), not just "invalid".
- [ ] No REVIEW or FAIL entry survives into the shipped text without an explicit note saying what was done about it.
- [ ] Re-run the check on the corrected document and confirm the verdict is PASS before release.

## Companion tool

`scripts/citecheck.py` (stdlib only) implements the rules above: it extracts every DOI, arXiv ID, ISBN, PMID, PMCID, ORCID and URL, checks syntax plus the ISBN and ORCID check digits, and reports PASS / REVIEW / FAIL per identifier and per `[N]` entry.

```bash
python3 scripts/citecheck.py validate --file refs.txt   # offline; --text/--json/stdin also accepted
python3 scripts/citecheck.py resolve --file refs.txt --online   # the only networked command
python3 scripts/citecheck.py --demo                     # the worked example above
python3 scripts/citecheck.py --selftest                 # 71 hand-verified checks
```

`validate` exits 1 when any identifier FAILs, so it drops straight into a publishing gate. `resolve` adds live checks (DOI handle API, arXiv Atom feed, Open Library) and never runs during `--selftest`. The skill is fully usable without the tool — the rules in the procedure are the whole method.

## Pair with adjacent skills

- `cite-ieee` — the formatting pass upstream; this skill validates what it emits.
- `grounded-fact-check` — verifies the load-bearing claims the citations support, once the citations themselves are sound.
- `rate-source-admiralty` — grades how much weight a validated source deserves.
- `abstain-or-escalate` — the hand-off when a citation fails and no replacement exists.
- `systematic-review` — screening pipelines generate long reference lists that need this pass in bulk.

## Anti-patterns

- Do **not** report a DOI as valid because it looks like one. Run the pattern; `10.invalid-fake` looks plausible and is not.
- Do **not** date-check identifiers against today's date. A rule that makes a document pass today and fail next year is not a rule.
- Do **not** treat a failed ISBN or ORCID check digit as a REVIEW. The arithmetic is decisive.
- Do **not** silently delete failing citations. Drop and notify, or the claim they supported quietly loses its evidence.
- Do **not** claim a PASS proves the reference exists. Format validation is necessary, never sufficient — say so in the report.

## Reference

- ISO 26324:2012, *Information and documentation — Digital object identifier system*. International Organization for Standardization, 2012. https://www.iso.org/standard/43506.html
- ISO 2108:2017, *Information and documentation — International standard book number (ISBN)*, 5th ed. International Organization for Standardization, 2017. https://www.iso.org/standard/65483.html
- ISO/IEC 7064:2003, *Information technology — Security techniques — Check character systems* — the MOD 11-2 scheme used by ORCID. https://www.iso.org/standard/31531.html
- arXiv, "Understanding the arXiv identifier," Cornell University, 2007 (old scheme 1991–2007; new scheme from April 2007). https://info.arxiv.org/help/arxiv_identifier.html
- T. Berners-Lee, R. Fielding and L. Masinter, "Uniform Resource Identifier (URI): Generic Syntax," RFC 3986, IETF, Jan. 2005. https://www.rfc-editor.org/rfc/rfc3986
- D. Eastlake and A. Panitz, "Reserved Top Level DNS Names," RFC 2606, IETF, Jun. 1999 — the `example.com` family flagged as placeholders. https://www.rfc-editor.org/rfc/rfc2606
