---
name: analyze-patent-claims
description: "Dissects one patent's claim set the way an examiner reads it — independent versus dependent claims, the transitional phrase that fixes the scope (comprising = open, consisting of = closed), the elements of claim 1, the classification codes, and prior-art signals — and returns a structured record of what the filing actually covers. Use when a specific filing is on the table: \"what does US00000000B2 cover?\", \"read this patent application\", \"freedom-to-operate on this claim\", \"is this patent-pending claim broad?\". Not for a cluster of filings — use `read-patent-landscape` instead."
license: MIT
metadata:
  category: technology-assessment
  method: Patent claim construction and structural claim analysis
  origin: 35 U.S.C. §112; USPTO MPEP §§ 608.01(n), 2111.03, 2173.05(b), 2181
  version: "2.0.0"
---
# Analyze Patent Claims

A structural read of one patent's claims using the rules the USPTO applies in examination: 35 U.S.C. §112 and the *Manual of Patent Examining Procedure* (MPEP, Ninth Edition, Rev. 01.2024) — §2111.03 transitional phrases, §608.01(n) dependent claims, §2173.05(b) relative terms, §2181 means-plus-function. The claims, not the title or abstract, define the invention's legal boundary, and the transitional phrase decides how far it reaches. It prevents the standard failure: reporting a patent's marketing summary as its scope, and mistaking a narrow filing for a moat.

## When to invoke

Invoke when:

- A specific filing is named or pasted: a number of the form `US<NNNNNNNN>B2`, `EP<NNNNNNN>B1` or `WO<YYYY>/<NNNNNN>` (these are shapes, not real publications), or raw claim text.
- Someone asks what a patent covers, how broad claim 1 is, whether a product reads on the claims ("freedom-to-operate"), or what the prior art shows.

Do NOT invoke when:

- The question spans many filings — "who owns the IP around X?", "is this space crowded?" — use `read-patent-landscape`.
- The item is a trademark, design patent or trade secret: different rights, different claim structure.
- The announcement is a financing or transaction that merely mentions IP — use `detect-funding-round` or `detect-ma-event`.
- Only a press summary exists and the claim text is unavailable — use `abstain-or-escalate`, never inferring claims from prose.

## Procedure

### 1 — Identify jurisdiction and status from the number

Read the office prefix and kind code: `US` USPTO, `EP` EPO, `WO` PCT, `CN` CNIPA, `JP` JPO, `KR` KIPO. Under WIPO Standard ST.16 the letter marks the publication level — **A** first (application), **B** second (grant) — with each office's own digits (`US … B1` grant with no earlier publication, `B2` grant that had one; `EP … A1` application with search report, `B1` granted specification). Set status: granted, pending, expired, abandoned. A PCT (`WO`) publication is an application, never a grant: tag it pending, noting the national phases entered. Table: `references/kind-codes-and-classes.md`.

### 2 — Parse the claim set

Split the claim text into numbered claims and build the dependency tree. Independent claims stand alone and set the outer boundary; dependent claims incorporate a parent and add a limitation (35 U.S.C. §112(d)). Count multiple dependent claims separately — they reference parents in the alternative only and may not depend from another multiple dependent claim (§112(e); MPEP §608.01(n)). Note each claim's statutory category and flag defects: forward or dangling references, improper dependency, a dependent claim that narrows nothing.

### 3 — Fix the scope from the transitional phrase

Split preamble from body at the transitional phrase and read its scope per MPEP §2111.03: **"comprising"** (also "including", "containing") is open — a product with the recited elements *plus more* still reads on the claim; **"consisting of"** is closed, excluding any element not specified; **"consisting essentially of"** admits only additions that do not materially affect the basic and novel characteristics. "Having" is read against the specification; "group consisting of" is a Markush group.

### 4 — Summarise claim 1 by its elements

List the elements of the broadest independent claim (usually claim 1 — 37 CFR 1.75(g) expects the least restrictive first) as "A {method / system / medium} comprising: X; Y; Z". Every element must be present for infringement, so name the element a competitor could omit. Work from the claim text, never the abstract; the dependent claims are the fallbacks if claim 1 falls to prior art.

### 5 — Record classification codes and prior-art signals

Capture the complete IPC and CPC sets, not a subset — the full set describes the domain mix and makes the filing comparable with others (IPC is the WIPO-administered scheme, CPC the finer-grained joint EPO–USPTO scheme built on it; recurring symbols: `references/kind-codes-and-classes.md`). Then read the front-page citations (many mean crowded art), the prosecution history where public (USPTO Patent Center, EPO Register) and the fate of family members elsewhere: a claim granted in one office but refused in another signals surviving language narrower than the published application.

### 6 — Grade the source and note relevance

Grade the record with `rate-source-admiralty`: office publications and Google Patents (mirroring official data) are A1; patent-specialist press A2; generic tech news B2–C2; a blog citing no patent number D3 or worse. Note which companies or technologies the filing touches, and surface any apparent read on a competitor's product for human review, never as an infringement finding.

## Output template

```json
{
  "patent_number": "US00000000B2",
  "jurisdiction": "US",
  "status": "granted | pending | expired | abandoned",
  "assignee": "Example Corp",
  "cpc_codes": ["G06N 3/084", "G06F 18/2148"],
  "independent_claim_count": 3,
  "dependent_claim_count": 9,
  "multiple_dependent_claim_count": 1,
  "claim_transition_language": "comprising",
  "claim_1_elements": ["receiving ...", "generating ...", "transmitting ..."],
  "claim_1_gist": "A method comprising: receiving ...; generating ...; transmitting ...",
  "drafting_flags": ["claim 10: means-plus-function (§112(f))"],
  "prior_art_signals": ["office action cites a preprint"],
  "source_url": "https://patents.google.com/patent/...",
  "source_grade": "A1",
  "confidence": 78
}
```

Template values are illustrative placeholders — `US00000000B2`, `Example Corp` and the codes above are not a real record. Mandatory: `patent_number`, `jurisdiction`, `status`, both claim counts, `claim_transition_language`, `claim_1_elements`, `source_url`, `source_grade`. An unreadable field is `null`, never inferred; `scripts/claims.py parse --json` fills the claim-structure fields.

## Worked example

Illustrative claim set (synthetic, 12 claims) from `python3 scripts/claims.py parse --demo` — a Google Patents record (Admiralty A1), assignee Example Corp, pending at the USPTO:

```
Claims parsed: 12 (independent 3, dependent 9 of which 1 multiple dependent, canceled 0); max dependency depth 2
1   IND method [comprising, open] 3 elem, 39 w  | A method
10  IND apparatus [comprising, open] 4 elem, 49 w  | A retrieval system   112F REL
12  IND crm [comprising, open] 3 elem, 51 w  | A non-transitory computer-readable medium ...
```

Three independent claims cover one invention as a method, a system and a computer-readable medium — the standard trio. Claim 1 is broadest at 39 words and three elements: receive a natural-language query, generate a ranked passage set with a neural ranking model, transmit it with per-passage confidence scores. Its transition is "comprising", so a service doing all three *plus more* still reads on it (MPEP §2111.03); the shortest path around it is dropping the confidence scores. Claims 2–9 are the fallbacks — claim 2 limits the model to a cross-encoder, claim 5 the index to an approximate-nearest-neighbour structure; claim 7 is multiple dependent on claims 1 and 5, flagged because it costs an extra USPTO fee and cannot support another multiple dependent claim (MPEP §608.01(n)). Claim 10 carries two flags: "means for receiving" invokes 35 U.S.C. §112(f), construing it to the structure disclosed in the specification and equivalents, and "substantially calibrated" is a relative term on the §2173.05(b) watch-list. An office action citing a preprint against element (b) would narrow the grant toward claim 2 — confidence stays at 78 and the scope statement is written against claim 2.

## Verification

- [ ] Claim counts recomputed with `scripts/claims.py stats` and matching the record.
- [ ] The transitional phrase came from the claim text with its scope stated — not assumed to be "comprising".
- [ ] Claim 1's elements are quoted from the claim, not the abstract; the omittable one is named.
- [ ] Every dependent claim resolves to an earlier claim; forward, dangling and improper dependencies are flagged.
- [ ] The full IPC and CPC sets were captured; a PCT publication is pending, never granted.
- [ ] The source carries an Admiralty grade; infringement-shaped observations go to human review.

## Companion tool

`scripts/claims.py` (stdlib only) does step 2 deterministically: splits raw claim text into numbered claims, builds the dependency tree, labels each claim's category (method, apparatus, composition, CRM, use, product-by-process, kit), splits independent claims at the transitional phrase with its MPEP §2111.03 scope, counts elements and words, and flags "means for" (35 U.S.C. §112(f)), relative terms (MPEP §2173.05(b)), negative limitations, forward/dangling references and improper multiple dependency, each MPEP-cited. `--json` fills `independent_claim_count`, `dependent_claim_count`, `claim_transition_language` and `independent_claim_1_gist`.

```bash
python3 scripts/claims.py parse --file claims.txt    # tree, table, flags (--json)
python3 scripts/claims.py stats --file claims.txt    # counts only
python3 scripts/claims.py parse --demo               # worked example, system, CRM claim
python3 scripts/claims.py --selftest
```

`parse --demo` excerpt:

```
Claims parsed: 12 (independent 3, dependent 9 of which 1 multiple dependent, canceled 0); max dependency depth 2
1   IND method [comprising, open] 3 elem, 39 w  | A method
10  IND apparatus [comprising, open] 4 elem, 49 w  | A retrieval system   112F REL
```

The skill is fully usable without the tool; the script removes counting slips and exits 1 on a structural defect.

## Pair with adjacent skills

- `read-patent-landscape` — the cluster view that says which filings deserve this read.
- `rate-source-admiralty` — grade the record the claims came from.
- `triangulate-sources` — corroborate a claim finding with product or hiring signals.
- `detect-funding-round` — IP-heavy fundraises pair with filings; the round is its job.
- `abstain-or-escalate` — when only a press summary exists.

## Anti-patterns

- Do **not** read the title or abstract as the invention — the claims are the boundary.
- Do **not** treat "comprising" and "consisting of" as synonyms, or a PCT (`WO`) publication as a grant.
- Do **not** cherry-pick classification codes or merge family members — a continuation, a divisional and a national phase carry different claims.
- Do **not** assert infringement — this is not court claim construction, and not legal advice.

## Reference

- 35 U.S.C. §112 (1952, as amended by the America Invents Act, 2011) — (b) definiteness, (d) dependent claims ("a claim previously set forth"), (e) multiple dependent claims, (f) means-plus-function. https://www.law.cornell.edu/uscode/text/35/112
- U.S. Patent and Trademark Office, *Manual of Patent Examining Procedure*, Ninth Edition, Rev. 01.2024 (November 2024): §2111.03 Transitional Phrases; §608.01(n) Dependent Claims; §2173.05(b) Relative Terminology; §2181 (§112(f) limitations). https://www.uspto.gov/web/offices/pac/mpep/index.html
- WIPO, Standard ST.16, *Recommended Standard Code for the Identification of Different Kinds of Patent Documents*, revision adopted 30 May 1997. https://www.wipo.int/export/sites/www/standards/en/pdf/03-16-01.pdf
