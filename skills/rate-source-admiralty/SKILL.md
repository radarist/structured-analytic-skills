---
name: rate-source-admiralty
description: "Grades one source on the NATO Admiralty Code — a letter for source reliability (A–F) and a digit for information credibility (1–6), such as B2 — and returns the code with a one-sentence rationale. Use when a source behind a claim, citation or record needs a defensible trust grade rather than a gut feeling — \"grade this source\", \"how reliable is this outlet?\", \"give it an Admiralty rating\", \"what is the A1–F6 for this?\". Not for corroborating a claim across several sources (use `triangulate-sources`) or vetting an unfamiliar site laterally first (use `sift-source-check`)."
license: MIT
metadata:
  category: evidence-verification
  method: Admiralty Code (NATO System, 6×6 source reliability × information credibility)
  origin: NATO STANAG 2511 / AJP-2.1, 2003; U.S. Army FM 2-22.3 Appendix B, 2006
  version: "2.0.0"
---
# Rate Source (Admiralty Code A1–F6)

The Admiralty Code — the NATO System codified in STANAG 2511 / AJP-2.1 (2003) and reproduced in U.S. Army FM 2-22.3 (2006), Appendix B — grades a source's **reliability** (A–F, from its track record) separately from the **credibility** of the item it reports (1–6, from corroboration and logic). The axes are independent: an established newspaper carrying an unconfirmed rumour is B2; an anonymous post carrying a corroborated fact is F1. Single-number "trust scores" conflate the two, letting a reputation launder an unchecked claim.

## When to invoke

Invoke when:

- A source is about to be relied on — cited, attached to a record, used as evidence — and its trustworthiness must be stated: "grade this source", "how reliable is this outlet?", "give it an Admiralty rating".
- Two sources conflict and a defensible statement of which carries more weight is needed.
- Pivotal evidence (e.g. what an `analysis-of-competing-hypotheses` ranking hinges on) needs a grade first.

Do NOT invoke when:

- The question is whether a *claim* is corroborated by independent sources, not how good one source is — use `triangulate-sources`.
- The source is unfamiliar and has not been checked laterally — run `sift-source-check` first; the grade records a judgement about a source already looked into.
- There is no source behind the claim — that is `abstain-or-escalate` territory, not a grade.

## Procedure

### 1 — Identify the actual originator

Name the publisher or author that originated the item — the wire service, the filing, the paper, the person — not the aggregator, feed or repost where it was found. A syndicated Reuters story on a portal is graded as Reuters. An unidentifiable originator is F by definition.

### 2 — Grade source reliability (A–F) from track record only

Use Axis 1 below. The letter reflects the source's history of accuracy, editorial process and competence on this kind of subject — never whether the present claim is agreeable. No reporting history means F ("cannot be judged"): ignorance, not distrust (FM 2-22.3, para B-1).

| Grade | Label                        | Meaning (standard wording)                                                                                                | Typical examples                                                                                          |
| ----- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **A** | Completely reliable          | No doubt of authenticity, trustworthiness, or competency; has a history of complete reliability                          | Govt filings, peer-reviewed papers, company 10-K, USPTO                                                   |
| **B** | Usually reliable             | Minor doubt about authenticity, trustworthiness, or competency; has a history of valid information most of the time      | Established news outlets with editorial standards (NYT, FT, Reuters, Nature News), Anthropic/OpenAI blogs |
| **C** | Fairly reliable              | Doubt of authenticity, trustworthiness, or competency but has provided valid information in the past                     | Industry publications, vendor marketing, Wikipedia, well-maintained community wikis                       |
| **D** | Not usually reliable         | Significant doubt about authenticity, trustworthiness, or competency but has provided valid information in the past      | Aggregators without editorial oversight, personal blogs, unclear provenance, LinkedIn posts               |
| **E** | Unreliable                   | Lacking in authenticity, trustworthiness, and competency; history of invalid information                                 | Known misinformation vectors, pure opinion                                                                |
| **F** | Reliability cannot be judged | No basis exists for evaluating the reliability of the source                                                              | Brand new source, anonymous post, blank profile                                                           |

### 3 — Grade information credibility (1–6) from the item itself

Use Axis 2 below, looking only at the information: confirmed by an *independent* source (1), merely consistent with what else is known (2–3), unsupported or illogical (4–5), or wholly new (6)? A 6, like F, means "no basis to judge", not "false" (FM 2-22.3, para B-2).

| Grade | Label                      | Meaning (standard wording)                                                                                    |
| ----- | -------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **1** | Confirmed by other sources | Confirmed by other independent sources; logical in itself; consistent with other information on the subject |
| **2** | Probably true              | Not confirmed; logical in itself; consistent with other information on the subject                          |
| **3** | Possibly true              | Not confirmed; reasonably logical in itself; agrees with some other information on the subject               |
| **4** | Doubtful                   | Not confirmed; possible but not logical; no other information on the subject                                 |
| **5** | Improbable                 | Not confirmed; not logical in itself; contradicted by other information on the subject                       |
| **6** | Truth cannot be judged     | No basis exists for evaluating the validity of the information                                                |

### 4 — Combine and write the rationale

Join letter and digit (B2, A1, F6) and write one sentence tying each half to an observable fact — "wire service with editorial standards (B); unconfirmed but consistent with the company's announcement (2)". Grades are current assessments: re-grade when corroboration arrives (2 → 1) or a correction is issued, and record the date.

## Output template

One JSON object per graded source. `combined` and `rationale` are mandatory; a grade without a rationale is not a grade.

```json
{
  "source": "{originator, title, date, URL or identifier}",
  "reliability": "{A–F}",
  "credibility": {1–6},
  "combined": "{letter+digit, e.g. B2}",
  "rationale": "{one sentence: why this letter (track record), why this digit (corroboration/logic)}",
  "graded_on": "{YYYY-MM-DD}"
}
```

## Worked example

Illustrative data. A draft states that a company closed a $3.5 billion Series E at a $61.5 billion valuation on 3 March 2025; the supporting item is a Reuters report of that day quoting the company's announcement; no filing has been located. Step 1: the originator is Reuters, not the portal that surfaced it. Step 2: established wire service with editorial standards → **B**. Step 3: unconfirmed by any independent source but consistent with the company's statement → **2**. Reproduced with the companion tool:

```text
$ python3 scripts/admiralty.py grade B2
B2
  Reliability  B — Usually reliable: Minor doubt about authenticity, trustworthiness, or competency; has a history of valid information most of the time
  Credibility  2 — Probably true: Not confirmed; logical in itself; consistent with other information on the subject
  Source: NATO AJP-2.1 / STANAG 2511; FM 2-22.3 (2006) App. B, Tables B-1/B-2
```

Emitted record: `{"source": "Reuters, 2025-03-03", "reliability": "B", "credibility": 2, "combined": "B2", "rationale": "Wire service with editorial standards (B); unconfirmed but consistent with the company announcement (2).", "graded_on": "2025-03-04"}`.

Two days later a Form D filing shows the same amount: the Reuters item is re-graded **B1**, the filing **A1**. A repost by an anonymous forum account with no history is **F6** (`python3 scripts/admiralty.py grade F6` prints both "cannot be judged" notes) and goes on the lateral-check list, not into the evidence.

## Verification

Before the grade ships, confirm:

- [ ] The letter rests on the originator's track record only — strike any reference in the rationale to whether the claim is welcome or plausible.
- [ ] The digit rests on the item: a 1 names the independent confirming source; 2–3 say what it is consistent with; 4–5 say why it is illogical or contradicted; 6 says nothing comparable exists.
- [ ] `python3 scripts/admiralty.py grade <code>` accepts the code (exit 0) and its definitions match the rationale.
- [ ] Unknown originator or wholly new information was graded F or 6 with the gap named — not defaulted to B2.
- [ ] The rationale names the originator, not the aggregator where the item was found.

## Companion tool

`scripts/admiralty.py` (Python 3, stdlib only) looks up the standard wording and summarises a set of grades; the skill is fully usable without it. Commands: `grade B2` (both labels + definitions + citation; invalid code exits 2), `matrix` (the 6×6 grid; `--json`), `aggregate --file sources.json` (rows `{source, grade, claim_polarity: supports|contradicts|neutral, note}` about one claim → counts per axis, best/worst judged grade, F/6 count and lateral-check list, plus a *heuristic* conflict flag when one source graded A or B with 1 or 2 supports the claim and another such source contradicts it — not part of the standard), `to-ordinal B2` (heuristic sort key = reliability rank + credibility rank; refuses to emit a percentage), `--demo`, `--selftest`.

```text
$ python3 scripts/admiralty.py grade B2
B2
  Reliability  B — Usually reliable: Minor doubt about authenticity, trustworthiness, or competency; has a history of valid information most of the time
  Credibility  2 — Probably true: Not confirmed; logical in itself; consistent with other information on the subject
  Source: NATO AJP-2.1 / STANAG 2511; FM 2-22.3 (2006) App. B, Tables B-1/B-2
```

## Pair with adjacent skills

- `sift-source-check` — lateral verification of an unfamiliar source before it earns a grade.
- `triangulate-sources` — when one graded source is not enough to establish the claim; grades each candidate with this skill.
- `analysis-of-competing-hypotheses` — grades the pivotal evidence its sensitivity check rests on.
- `abstain-or-escalate` — when there is no source to grade, refuse or escalate rather than invent one.

## Anti-patterns

- Do **not** default to B2. If the source is unknown, grade F6 and say so; vague grades corrupt every record carrying one.
- Do **not** grade reliability by whether the claim is agreeable. A reliable outlet reporting something later shown wrong is B5, not D3.
- Do **not** collapse the pair to one number or a percentage. Letter and digit stay together; the consumer decides which axis matters.
- Do **not** grade the aggregator. Grade the originator it relays.

## Reference

- NATO, STANAG 2511, *Intelligence Reports*, 2003 edition — the Admiralty Code / NATO System; the same A–F / 1–6 scheme is carried in AJP-2.1, *Allied Joint Doctrine for Intelligence Procedures* (Edition B, 2016).
- Headquarters, Department of the Army, FM 2-22.3 (FM 34-52), *Human Intelligence Collector Operations*, Washington, DC, 6 September 2006, Appendix B "Source and Information Reliability Matrix", Tables B-1 and B-2. https://irp.fas.org/doddir/army/fm2-22-3.pdf
