---
name: sift-source-check
description: "Runs the SIFT moves (Caulfield, 2019) — Stop, Investigate the source, Find better coverage, Trace claims to the original context — by lateral reading, leaving the page to see what the wider web says about an unfamiliar site or a viral claim, and returns a verdict of trusted, usable with caveat, unconfirmed or refuted. Use before trusting, citing or sharing anything from a source not already known — \"is this website legit?\", \"can this article be trusted?\", \"run a SIFT check on this link\", \"is this viral post real?\". Not for grading a source already vetted (use `rate-source-admiralty`) or corroborating a claim across sources (use `triangulate-sources`)."
license: MIT
metadata:
  category: evidence-verification
  method: SIFT (Stop, Investigate the source, Find better coverage, Trace claims to the original context)
  origin: Mike Caulfield, 2019 (lateral reading — Wineburg and McGrew, 2017/2019)
  version: "2.0.0"
---
# SIFT Source Check

SIFT is Mike Caulfield's four-move routine for judging an unfamiliar web source or claim (2019, refined from his 2017 "four moves and a habit"), built on the lateral-reading finding of Wineburg and McGrew (2017; 2019): professional fact-checkers judge a site by *leaving* it and reading what the rest of the web says about it, whereas novices read the page itself harder. The core principle is that a source cannot be verified from its own words about itself. The failure it prevents is being taken in by a convincing page read on its own terms — polished design, an authoritative "About" page, an emotional hook — before anyone has looked sideways.

## When to invoke

Invoke when:

- An unfamiliar source or a striking claim is about to be trusted, cited or shared: "is this website legit?", "can this article be trusted?", "is this viral post real?", "should this be cited?".
- A report or answer is about to cite a site, account or outlet the author did not already know and trust.
- A quote, statistic, screenshot or clip is circulating without its original context.

Do NOT invoke when:

- The source is already known and vetted and what is needed is its trust grade — use `rate-source-admiralty`.
- The question is whether a claim is corroborated by several *independent* sources — use `triangulate-sources`; SIFT vets one source or one claim.
- The task is checking the identifiers of academic references (DOIs, arXiv IDs) — use `verify-citations`.
- SIFT has already returned unconfirmed or refuted and no better source exists — hand the claim to `abstain-or-escalate` rather than citing the bad one.

## Procedure

### 1 — Note the source and the load-bearing claim

Before searching, write down (a) the outlet, account or URL and (b) the specific claim the work depends on — the number, the quote, the event. Vague claims cannot be checked, and a check that starts by reading the suspicious page carefully has already lost. All four moves are then run laterally: in a fresh search, on sites other than the one being checked.

### 2 — Stop

Before reading further, sharing or reacting, ask two things: is this site, author or organisation already known? And what is the emotional reaction — outrage, vindication, fear, surprise? Strong emotion is the best single predictor of sharing something false; the feeling is the alarm, not the evidence. Stopping is the move that buys time for the other three, and it is never skipped as "obvious".

### 3 — Investigate the source

Leave the page and search for the *source itself* — who runs it, who funds it, what reputation it has, what established outlets and reference works say *about* it (not what it says about itself). The aim is a one-minute prior, not a full audit: is this a place that could plausibly carry this kind of claim, or a known misinformation vector? If the answer is the latter, the check may already be finished.

### 4 — Find better coverage

Search the *claim*, not the page. Look for established outlets, fact-checkers or primary bodies covering the same claim: do they agree, contradict, or say nothing? Silence from trusted coverage is itself information — a sensational claim no established outlet has touched is a flag, not a scoop. Better coverage counts only if it is independent; three articles copying one press release are one source.

### 5 — Trace claims, quotes and media to the original context

Take the load-bearing item back to where it originated: a quote to the full transcript or speech, a statistic to the study or dataset, an image or clip to its first upload and date. Then ask whether it means the same thing in its original setting. Many viral "gotchas" are real quotes in false context or real numbers stripped of their denominator; recontextualisation is how true things become false in transit.

### 6 — Converge on one verdict

| Verdict | Meaning |
| --- | --- |
| **Trusted** | Known reliable source carrying a claim corroborated by independent coverage. |
| **Usable with caveat** | Source or claim has a known slant or limitation; cite with the caveat attached. |
| **Unconfirmed** | No trusted coverage either way; treat as a lead, not evidence. |
| **Refuted / unreliable** | Source is a known bad actor, or the claim is contradicted by trusted coverage, or its context was stripped. Do not cite. |

Any single move can settle the question — a known bad actor at step 3 needs no step 5 — but the verdict must say which move settled it.

## Output template

Every field is mandatory; a move that was not needed is marked "not needed — settled at {move}".

```
## SIFT check — {claim} @ {source}

**Claim:** {the load-bearing specific claim}
**Source:** {outlet / account / URL}, {author if known}

**Stop:** {known source | unknown} — emotional hook: {outrage / surprise / none}
**Investigate the source:** {who runs it; reputation; known bias} → {prior}
**Find better coverage:** {trusted outlets covering the claim: agree / contradict / silent}
**Trace to original:** {original context found: same meaning / recontextualised / fabricated | not found}

**Verdict: {Trusted | Usable with caveat | Unconfirmed | Refuted}** — settled at {move}: {one-sentence why}
**Hand-off:** {grade with `rate-source-admiralty` | corroborate with `triangulate-sources` | refuse via `abstain-or-escalate`}
```

## Worked example

Illustrative data. A post seen 14 May 2026 from an anonymous account (2,400 reposts, created 3 weeks earlier) claims: "Acme's new inference chip is 100× faster than GPUs on transformers", with a screenshot of a benchmark table.

```
## SIFT check — "Acme chip 100× faster than GPUs" @ anonymous social post

**Claim:** Acme's chip delivers 100× GPU throughput on transformer inference
**Source:** anonymous account, screenshot of a benchmark table, no author

**Stop:** unknown source — emotional hook: surprise (100×); do not share or quote yet
**Investigate the source:** account has no affiliation, no history, no named author → prior low; the table formatting matches Acme's own marketing deck
**Find better coverage:** no established outlet covers the claim; one trade publication (12 May 2026) analysed the same vendor numbers and found a single-kernel microbenchmark at batch size 1 with no batched comparison
**Trace to original:** Acme's own controlled microbenchmark on one kernel against an unbatched GPU baseline → the 100× is real for that narrow setup but recontextualised as a general claim

**Verdict: Unconfirmed** — settled at Trace: the benchmark exists but does not support the general claim; the viral form is recontextualised marketing
**Hand-off:** refuse the general claim via `abstain-or-escalate`; if the narrow result matters, cite the trade publication and grade it with `rate-source-admiralty`
```

## Verification

Before the verdict ships, confirm:

- [ ] Every move was done laterally — the Investigate and Find lines each name at least one site or search other than the source being checked.
- [ ] The Trace line names the original artefact (transcript, dataset, study, first upload) or states explicitly that it could not be found.
- [ ] The verdict follows the table: absence of trusted coverage is Unconfirmed, never Trusted; Refuted names the contradicting coverage or the stripped context.
- [ ] Coverage counted as "better" is independent — sources re-reporting one origin were collapsed to one.
- [ ] The Hand-off line routes the result to a sibling skill instead of leaving the claim in limbo.

## Pair with adjacent skills

- `rate-source-admiralty` — SIFT is the entrance exam; the Admiralty grade is the durable record written after SIFT passes.
- `triangulate-sources` — SIFT often ends at "find better coverage"; triangulation is the stricter bar for treating a claim as established.
- `verify-citations` — for academic sources, trace the reference to the actual DOI/arXiv artefact, not the landing page.
- `abstain-or-escalate` — when SIFT returns Unconfirmed or Refuted and no better source exists, refuse the claim rather than cite the unreliable one.

## Anti-patterns

- Do **not** verify a source by reading its own "About" page. That is vertical reading; con artists write excellent About pages.
- Do **not** skip Stop. The emotional-hook check catches most of what would later be regretted.
- Do **not** treat "no debunking found" as "true". Absence of trusted coverage is Unconfirmed.
- Do **not** count several articles that trace to one origin as several sources.
- Do **not** take a single fact-checker's rating as final when it is contested; read the reasoning, not the label.
- Do **not** strip context when re-reporting — the Trace move exists because that is how true things become false.

## Reference

- M. Caulfield, "SIFT (The Four Moves)," *Hapgood* (blog), 19 June 2019. https://hapgood.us/2019/06/19/sift-the-four-moves/
- M. Caulfield, *Web Literacy for Student Fact-Checkers*, Pressbooks, 2017 — the earlier "four moves and a habit". https://pressbooks.pub/webliteracy/
- M. Caulfield and S. Wineburg, *Verified: How to Think Straight, Get Duped Less, and Make Better Decisions about What to Believe Online*. Chicago: University of Chicago Press, 2023. ISBN 978-0-226-82206-8.
- S. Wineburg and S. McGrew, "Lateral Reading: Reading Less and Learning More When Evaluating Digital Information," Stanford History Education Group Working Paper No. 2017-A1, 6 October 2017. SSRN 3048994, doi:10.2139/ssrn.3048994.
- S. Wineburg and S. McGrew, "Lateral Reading and the Nature of Expertise: Reading Less and Learning More When Evaluating Digital Information," *Teachers College Record*, vol. 121, no. 11, pp. 1–40, 2019. doi:10.1177/016146811912101102.
