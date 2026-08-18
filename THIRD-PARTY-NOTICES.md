# Third-Party Notices

This repository is licensed MIT (see [LICENSE](./LICENSE)). **The MIT grant covers this
repository's own text, code and data structures. It does not, and cannot, relicense the
third-party material that some skills reproduce.** Material published under CC BY, CC BY-SA,
the Open Government Licence or Apache-2.0 keeps its own licence and its own conditions when
it travels inside this repository, and those conditions bind anyone who redistributes it.

This file records, per file, what is third-party, who owns it, under what licence it is used,
and what the licence requires. It also records what is deliberately *not* reproduced, and
which names are trademarks.

If you copy a single skill directory out of this repository, the notices for that skill's
files travel with it. Copy the relevant rows below alongside it.

- [1. Separately licensed files](#1-separately-licensed-files)
- [2. Used under an open licence (attribution required)](#2-used-under-an-open-licence-attribution-required)
- [3. Public-domain works of the United States Government (17 U.S.C. §105)](#3-public-domain-works-of-the-united-states-government-17-usc-105)
- [4. Not reproduced — consult the source](#4-not-reproduced--consult-the-source)
- [5. Methods described, not reproduced](#5-methods-described-not-reproduced)
- [6. Trademarks](#6-trademarks)
- [7. Corrections](#7-corrections)

---

## 1. Separately licensed files

Every file below contains third-party expression. The licence named in the "Licence" column
governs that expression; the rest of each file is this repository's own work under MIT.

| File | Source material | Rights holder | Licence | Basis |
|---|---|---|---|---|
| `skills/amstar2-review-appraisal/references/items.md` | The 16 AMSTAR 2 item questions and the Box 1 list of critical domains, condensed and reformatted | Shea, Reeves, Wells et al.; published by BMJ Publishing Group Ltd | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | CC BY 4.0 §3(a): attribution, licence identifier and URI, and a notice of modification — all carried in the file's "Attribution and licence" section |
| `skills/amstar2-review-appraisal/scripts/amstar2.py` | The same item questions and Box 1 list, embedded in the `items` command | as above | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | as above; the notice is in the module docstring and printed by `amstar2.py items` |
| `skills/systematic-review/references/prisma-flow-and-screening.md` | PRISMA 2020 flow-diagram box labels ("Records identified from databases and registers", "Records removed before screening", "Reports assessed for eligibility", "Reports excluded, with reasons", …) | Page, McKenzie, Bossuyt et al.; published by BMJ Publishing Group Ltd | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | CC BY 4.0 §3(a): attribution to the PRISMA 2020 statement with the licence identifier and URI |
| `skills/systematic-review/scripts/prisma.py` | The same flow-stage labels, embedded in the `flow` command's table | as above | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | as above |
| `skills/score-technology-readiness/references/trl-scales.md` §2 | The nine EU TRL definitions, verbatim | © European Union | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), per Commission Decision 2011/833/EU on the reuse of Commission documents | CC BY 4.0 §3(a): source, rights holder, licence identifier and URI |
| `skills/score-technology-readiness/scripts/trl.py` (`levels --scale eu`) | The same nine EU TRL definitions | © European Union | as above | as above |
| `skills/estimative-language/references/scales.md` — "UK PHIA Probability Yardstick" | The seven yardstick bands and their terms, and two short quoted sentences of PHIA guidance | © Crown copyright | [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) | OGL v3 attribution statement, reproduced verbatim in §2 below |
| `skills/estimative-language/scripts/wep.py` (`--standard phia`) | The same yardstick bands and terms | © Crown copyright | [OGL v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) | as above |
| `skills/estimative-language/references/scales.md` — "IPCC AR5 Guidance Note" | The Table 1 likelihood scale and short quoted sentences of the guidance note | © Intergovernmental Panel on Climate Change | **No open licence.** Used under the IPCC terms of use for short excerpts, with full acknowledgement — see the caveat in §2 | Source, authors and document acknowledged in the file's Sources list |
| `skills/estimative-language/scripts/wep.py` (`--standard ipcc`) | The same Table 1 likelihood bands | © IPCC | as above | as above |
| `skills/oss-project-health/references/indicator-thresholds.md` | CHAOSS metric names and their definitions ("Contributor Absence Factor", "Elephant Factor", "Time to First Response", "Release Frequency", …) | CHAOSS, a Linux Foundation Project | [MIT](https://opensource.org/license/mit) | MIT permission notice reproduced in full in §2 below |
| `skills/oss-project-health/scripts/osshealth.py` | The same CHAOSS metric names; OpenSSF Scorecard check names ("Maintained", "Vulnerabilities", "License", "Security-Policy", "CI-Tests") | CHAOSS / the OpenSSF, both Linux Foundation projects | [MIT](https://opensource.org/license/mit) and [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) | MIT permission notice (§2) and Apache-2.0 attribution (§2) |
| `skills/oss-project-health/SKILL.md`, `scripts/osshealth.py` | Not source text but a downstream condition: reports that quote Ecosyste.ms figures must carry its attribution | Ecosyste.ms | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | The skill mandates the `Data: Ecosyste.ms (CC-BY-SA 4.0)` line and the companion tool self-tests for it |
| `skills/analyze-release-notes/SKILL.md`, `references/cue-vocabulary.md`, `scripts/relnotes.py` | Rules of Semantic Versioning 2.0.0 and Conventional Commits 1.0.0, paraphrased with section references; the marker tokens `BREAKING CHANGE:` and `!` are the specifications' own | Tom Preston-Werner (SemVer); the Conventional Commits contributors | [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) | CC BY 3.0 attribution, in each skill's Reference list |

The remaining third-party material in the tree is in the public domain in the United States
and is listed in [§3](#3-public-domain-works-of-the-united-states-government-17-usc-105).

---

## 2. Used under an open licence (attribution required)

### AMSTAR 2 — item questions and Box 1

> Shea BJ, Reeves BC, Wells G, Thuku M, Hamel C, Moran J, Moher D, Tugwell P, Welch V,
> Kristjansson E, Henry DA. "AMSTAR 2: a critical appraisal tool for systematic reviews that
> include randomised or non-randomised studies of healthcare interventions, or both."
> *BMJ* 2017;358:j4008. doi:[10.1136/bmj.j4008](https://doi.org/10.1136/bmj.j4008).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

**Changes made.** The item questions have been condensed and reformatted. Short item labels,
the summary table, the response codes (Y / PY / N / NMA), the ordering and all surrounding
guidance are additions by this repository and are not the original authors'.

The "For Yes" / "For Partial Yes" operational criteria and the overall-confidence
descriptions are **not** reproduced from the AMSTAR 2 checklist at
<https://amstar.ca/Amstar_Checklist.php>, which is separately copyrighted; the versions in
this repository are restatements written for these skills. Consult the checklist itself when
an appraisal must be defended verbatim.

Neither the AMSTAR 2 authors nor *BMJ* endorse this repository.

### PRISMA 2020 — flow-diagram labels

> Page MJ, McKenzie JE, Bossuyt PM, Boutron I, Hoffmann TC, Mulrow CD, et al. "The PRISMA
> 2020 statement: an updated guideline for reporting systematic reviews."
> *BMJ* 2021;372:n71. doi:[10.1136/bmj.n71](https://doi.org/10.1136/bmj.n71).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

**Changes made.** Flow-stage labels are reproduced; the surrounding arithmetic checks, the
exclusion-reason vocabulary and the screening-agreement material are this repository's own.
The PRISMA Statement authors do not endorse this repository.

### EU Technology Readiness Levels — Horizon 2020 General Annex G

> Technology readiness levels (TRL), Horizon 2020 Work Programme 2014–2015, General Annex G,
> Commission Decision C(2014)4995. © European Union, 2014.
> Reused under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) in accordance with
> the Commission's reuse policy, implemented by the
> [Commission Decision of 12 December 2011 on the reuse of Commission documents (2011/833/EU)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32011D0833):
> unless otherwise indicated, content owned by the EU is licensed CC BY 4.0.

The Annex G extract carries the footer "Extract from Part 19 — Commission Decision
C(2014)4995" and no document-level licence notice, so it takes the Commission's general reuse
policy. That policy excludes "software or documents covered by industrial property rights,
such as patents, trade marks, registered designs, logos and names"; the TRL definitions are
none of these.

**Changes made.** The nine definitions are reproduced verbatim; the line wrapping and the
comparison against the NASA and DoD scales are this repository's own. The European
Commission does not endorse this repository, and reuse of this material does not imply that
the Commission approves of how it is used here.

### UK PHIA Probability Yardstick — Open Government Licence v3.0

The Probability Yardstick and the accompanying guidance are © Crown copyright and are
published under the Open Government Licence v3.0. The source page carries the standard
notice: "© Crown copyright 2025. This publication is licensed under the terms of the Open
Government Licence v3.0 except where otherwise stated."

The OGL requires an attribution statement, and where the Information Provider specifies none,
the licence prescribes the following wording, reproduced here verbatim as it directs:

> Contains public sector information licensed under the Open Government Licence v3.0.

Licence text: <https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/>

Sources:

- Professional Head of Intelligence Assessment (Cabinet Office), *Explaining Uncertainty in
  UK Intelligence Assessment*, GOV.UK guidance.
  <https://www.gov.uk/government/publications/explaining-uncertainty-in-uk-intelligence-assessment/explaining-uncertainty-in-uk-intelligence-assessment>
- Ministry of Defence, "Defence Intelligence: communicating probability", GOV.UK, 17 February 2023.
  <https://www.gov.uk/government/news/defence-intelligence-communicating-probability>

**Changes made.** The bands and terms are reproduced as published; the gap analysis, the
lint rules and the conversion tool are this repository's own. Use of this material does not
imply that the Cabinet Office, PHIA or the Ministry of Defence endorses this repository.

### IPCC AR5 uncertainty guidance — Table 1 likelihood scale

> Mastrandrea MD, Field CB, Stocker TF, et al. *Guidance Note for Lead Authors of the IPCC
> Fifth Assessment Report on Consistent Treatment of Uncertainties*. Intergovernmental Panel
> on Climate Change, 2010, Table 1 and paragraphs 8–10.
> <https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf>
> © Intergovernmental Panel on Climate Change.

**This is not open-licensed material, and the MIT licence on this repository does not reach
it.** The guidance note itself carries no copyright or licence statement; the IPCC's terms of
use (<https://www.ipcc.ch/copyright/>) govern. They state that IPCC material "is the property
of the IPCC and is protected by intellectual property laws", and that for "personal,
non-commercial usages, reproduction of limited number of figures or short excerpts of IPCC
material is authorized free of charge and without formal written permission provided that the
original source is properly acknowledged, with mention of the complete name of the report, the
publisher and the numbering of the page(s) or the figure(s)"; that "permission can only be
granted to use the material exactly as it is in the report"; and that "for any other use,
permission is required" (copyright@ipcc.ch).

**Practical effect.** The Table 1 terms and bands are reproduced unaltered and fully credited,
which the terms above cover for personal, non-commercial use. Anyone redistributing this
repository commercially, or altering the table, should seek permission from the IPCC first —
the MIT licence cannot grant it.

**Changes made.** The likelihood terms and their probability bands are reproduced as
published, with short quoted sentences of the guidance, presented in a Markdown table rather
than the original layout; the surrounding lint rules are this repository's own. The IPCC does
not endorse this repository.

### Ecosyste.ms — repository data

Ecosyste.ms splits its licensing — the site footer reads "Code: AGPL-3 — Data: CC BY-SA 4.0".
The **data** retrieved from its APIs (<https://repos.ecosyste.ms>) is published under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), and its attribution
condition survives into anything that quotes its numbers. No Ecosyste.ms code is used here.

This repository ships no Ecosyste.ms data. What it ships is the obligation: any report
produced by `skills/oss-project-health` that quotes Ecosyste.ms figures must carry the line

> **Data:** Ecosyste.ms (CC-BY-SA 4.0)

The requirement is stated in the skill's output template, its verification checklist and its
"Do not" list, and `scripts/osshealth.py --selftest` fails if the demo report drops it. Note
that CC BY-SA is a copyleft licence: a work that *adapts* Ecosyste.ms data must be shared
under CC BY-SA 4.0 or a compatible licence. Quoting figures with attribution, which is what
this skill does, is not adaptation.

### CHAOSS — metric names and definitions

CHAOSS metric definitions are published by CHAOSS, a Linux Foundation Project, under the MIT
licence — both the metrics repository (<https://github.com/chaoss/metrics>) and the knowledge
base site (<https://chaoss.community/kb-metrics-and-metrics-models/>, from
<https://github.com/chaoss/website>) carry an MIT `LICENSE`. Metric names and definitions are
used in `skills/oss-project-health`.

The MIT licence requires its copyright notice and permission notice to be reproduced in full.
The upstream copyright lines are `Copyright (c) 2017 CHAOSS Project` (metrics) and
`Copyright (c) 2018-2022 CHAOSS` (website); CHAOSS is a Linux Foundation Project:

```
MIT License

Copyright (c) 2017 CHAOSS Project
Copyright (c) 2018-2022 CHAOSS
(CHAOSS, a Linux Foundation Project)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Changes made.** The red / amber / green thresholds attached to each metric are this
repository's own: CHAOSS publishes metric *definitions*, not thresholds, and
`references/indicator-thresholds.md` says so. CHAOSS does not endorse this repository.

### OpenSSF Scorecard — check names

Check names and their definitions ("Maintained", "Vulnerabilities", "License",
"Security-Policy", "CI-Tests") are from the OpenSSF Scorecard project, licensed
[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).

> Copyright 2020 OpenSSF Scorecard Authors. Licensed under the Apache License, Version 2.0.
> <https://github.com/ossf/scorecard/blob/main/docs/checks.md>

`docs/checks.md` carries no licence header of its own and `docs/` has no separate `LICENSE`,
so it is covered by the repository-root Apache-2.0.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use these files
except in compliance with the License. Unless required by applicable law or agreed to in
writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

**Changes made.** Check names are used as vocabulary; the 90-day "normal fix window" band
and the verdict rules are this repository's own. The OpenSSF does not endorse this repository.

### Semantic Versioning 2.0.0 and Conventional Commits 1.0.0

Both specifications are published under
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/):

- T. Preston-Werner, *Semantic Versioning 2.0.0*, 2013. <https://semver.org/spec/v2.0.0.html>
- *Conventional Commits 1.0.0*, 2019. <https://www.conventionalcommits.org/en/v1.0.0/>

**Changes made.** `skills/analyze-release-notes` paraphrases the rules and cites them by
section number rather than reproducing the specification text; the `BREAKING CHANGE:` footer
and the `!` marker are the specifications' own tokens and appear as such. Neither project
endorses this repository.

---

## 3. Public-domain works of the United States Government (17 U.S.C. §105)

[17 U.S.C. §105(a)](https://www.law.cornell.edu/uscode/text/17/105): "Copyright protection
under this title is not available for any work of the United States Government, but the United
States Government is not precluded from receiving and holding copyrights transferred to it by
assignment, bequest, or otherwise." A "work of the United States Government" is defined at
§101 as one prepared by an officer or employee of the US Government **as part of that person's
official duties**. Material drawn from the following is therefore used without a copyright
licence. Three limits are worth stating: §105 does not place these works in the public domain
outside the United States; it does not cover material a US agency commissioned from a
contractor or incorporated from a third party (GAO, for example, warns that its products may
contain third-party copyrighted images needing separate permission); and §105(b)–(d), added in
2020, carve out certain works by covered authors at Department of Defense educational
institutions. Each is cited in its skill regardless, because attribution is a research-integrity
obligation independent of copyright.

| Source | Used in | What is used |
|---|---|---|
| NASA, *NASA Systems Engineering Processes and Requirements*, NPR 7123.1D (and 7123.1C), Appendix E, Table E-1 | `skills/score-technology-readiness/references/trl-scales.md` §1; `scripts/trl.py` (`--scale nasa`) | The nine NASA TRL definitions, software descriptions and success criteria, verbatim |
| J. C. Mankins, *Technology Readiness Levels: A White Paper*, NASA Office of Space Access and Technology, 1995 | as above | The 1995 wording of the levels, where it differs from the current NPR |
| Assistant Secretary of Defense (Research and Engineering), *Technology Readiness Assessment (TRA) Guidance*, April 2011, §2.5 | `skills/score-technology-readiness/references/trl-scales.md` §3; `scripts/trl.py` (`--scale dod`) | The nine DoD hardware TRL definitions and their supporting-information notes, verbatim |
| Office of the Under Secretary of Defense for Research and Engineering, *Technology Readiness Assessment Guidebook*, February 2025, Tables 2-1, 2-2, 2-3 | `skills/score-technology-readiness/references/trl-scales.md` §4 | The DoD software TRL definitions, abridged |
| US Government Accountability Office, *Technology Readiness Assessment Guide*, GAO-20-48G, 2020 | `skills/score-technology-readiness` | The restated Integration Readiness Level and System Readiness Level scales |
| US Army, *Human Intelligence Collector Operations*, FM 2-22.3, 2006, Appendix B, Tables B-1 / B-2 | `skills/rate-source-admiralty/SKILL.md`; `scripts/admiralty.py` | The Admiralty Code reliability (A–F) and credibility (1–6) labels and their explanatory sentences as printed in FM 2-22.3. The underlying codification is NATO STANAG 2511 / AJP-2.1, which is not a US Government work; the wording used here is the FM's |
| Office of the Director of National Intelligence, *Intelligence Community Directive 203: Analytic Standards*, 2 January 2015 (technical amendment 21 December 2022) | `skills/estimative-language/references/scales.md`; `scripts/wep.py` (`--standard icd203`); `skills/abstain-or-escalate` | The seven likelihood bands and their two synonym rows, and quoted requirements on expressing likelihood and confidence |
| ODNI, *Intelligence Community Directive 206: Sourcing Requirements for Disseminated Analytic Products*, 22 January 2015 | `skills/quality-of-information-check/references/icd-206-descriptors.md` | The source-descriptor factors and the source-summary-statement requirements of §D.3.d |
| National Intelligence Council, "What We Mean When We Say: An Explanation of Estimative Language", in *Iran: Nuclear Intentions and Capabilities* (NIE), November 2007 | `skills/estimative-language/references/scales.md` | The high / moderate / low confidence gloss |
| US Government, *A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis*, March 2009 | `skills/analysis-of-competing-hypotheses`, `skills/key-assumptions-check`, `skills/high-impact-low-probability`, `skills/indicators-validation`, `skills/critique-report`, `skills/quality-of-information-check` | Method steps and technique descriptions, paraphrased with page locators |

None of these agencies endorses this repository, and nothing here is an official
publication of any of them.

---

## 4. Not reproduced — consult the source

The following instruments are implemented but their authoritative text is deliberately
**absent** from this repository. In each case the skill routes the user to the source.

### Cochrane Risk of Bias 2 (RoB 2)

riskofbias.info states: "© 2025 by the authors. RoB 2, ROBINS-I, ROBINS-E and ROB ME are
licensed under Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International
License." [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) permits
neither commercial redistribution nor adaptation of the instrument's text — so it is
incompatible with redistributing the instrument inside an MIT-licensed repository.

**The signalling-question wording is therefore not included anywhere in this repository.**
`skills/assess-study-bias` carries only the unprotectable method: question IDs, response
options and the published decision algorithms. The one-line topics in
`references/rob2-domains.md` and in `scripts/rob2.py questions` are signposts written for
this repository, not the instrument. Read the exact questions at
<https://www.riskofbias.info/welcome/rob-2-0-tool> and answer against that text.

Source: Higgins JPT, Savović J, Page MJ, Sterne JAC (eds), on behalf of the RoB2 Development
Group, *Revised Cochrane risk-of-bias tool for randomized trials (RoB 2)*, full guidance
document, 22 August 2019; and Sterne JAC et al., *BMJ* 2019;366:l4898,
doi:[10.1136/bmj.l4898](https://doi.org/10.1136/bmj.l4898).

### The GRADE Handbook

The Handbook states, under "Reproduction and translation": "Permission to reproduce or
translate the GRADE handbook for grading the quality of evidence and the strength of
recommendation should be sought from the editors." No such permission has been sought, so
`skills/evidence-appraisal` implements the GRADE *method* — the starting certainty by design,
the five rating-down domains, the three rating-up domains and the four certainty levels — and
quotes only short, marked passages. The Handbook's tables are not reproduced.

Source: H. Schünemann, J. Brożek, G. Guyatt, A. Oxman (eds.), *GRADE Handbook*, GRADE Working
Group, 2013. <https://gdt.gradepro.org/app/handbook/handbook.html>. The GRADE Working Group
does not endorse this repository.

### The IEEE Reference Guide

The *IEEE Reference Guide* and the *IEEE Editorial Style Manual for Authors* are © 2025 IEEE.
`skills/cite-ieee` implements the citation and reference **formats** the guide specifies —
formats are unprotectable — and does not reproduce IEEE's own worked examples, its reference
list or its prose. The examples in the skill and in `scripts/ieee.py` were written for this
repository.

Source: IEEE Publication Operations, *IEEE Reference Guide*, V 3.28.2025, Piscataway, NJ:
IEEE, 2025. <https://ieeeauthorcenter.ieee.org/wp-content/uploads/IEEE-Reference-Guide.pdf>.
IEEE does not endorse this repository.

---

## 5. Methods described, not reproduced

A method — a sequence of analytic steps — is not protected by copyright; a particular
*expression* of it is. Every skill below describes a published method in this repository's
own words and cites the originating publication in its `## Reference` section, with a
locator. No substantial passage of any of these works is reproduced.

| Originator | Method | Skill |
|---|---|---|
| Richards J. Heuer Jr. (and Randolph H. Pherson) | Analysis of Competing Hypotheses; Key Assumptions Check; the diagnostic and contrarian technique family | `analysis-of-competing-hypotheses`, `key-assumptions-check`, `high-impact-low-probability`, `indicators-validation`, `red-team-claim`, `quality-of-information-check` |
| Michael E. Porter | Five Forces; strategic-group maps | `five-forces-analysis`, `position-competitor` |
| Barbara Minto | The Pyramid Principle; SCQ framing | `pyramid-principle` |
| Clayton M. Christensen; Anthony W. Ulwick | Jobs to be Done; Outcome-Driven Innovation job and outcome grammar | `jtbd-framing` |
| Mehrdad Baghai, Stephen Coley, David White | Three Horizons of Growth | `three-horizons` |
| Gary Klein | The premortem (prospective hindsight) | `premortem-analysis` |
| David J. Snowden (with Mary E. Boone; C. F. Kurtz) | The Cynefin framework | `cynefin-classification` |
| Thomas L. Saaty | The Analytic Hierarchy Process and its consistency ratio | `decision-matrix-mcda` |
| Fritz Zwicky; Tom Ritchey | General Morphological Analysis; Cross-Consistency Assessment | `morphological-analysis` |
| Michael Leonard, Suzanne Graham, Doug Bonacum | SBAR | `write-sbar-brief` |
| Jackie Fenn; Jackie Fenn and Mark Raskino | The Hype Cycle and its five phases | `apply-hype-cycle` |
| Bent Flyvbjerg; Daniel Kahneman and Dan Lovallo | Reference class forecasting; the outside view | `reference-class-forecasting` |
| Simon Wardley | The evolution axis and its four stage names — Genesis, Custom-built, Product (+rental), Commodity (+utility) | `evolution-stage`, `wardley-map-drafting` |

**On Wardley in particular.** *Wardley Maps* is published by its author under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), and CC BY-SA's ShareAlike
condition would attach to an adaptation of its text. No adaptation is shipped: the
characteristics cheat sheet that was previously condensed from chapter 2 has been replaced by
`skills/evolution-stage/references/placement-signals.md`, an original instrument written for
this repository. What remains is the axis, the four stage names — plain facts about a
published framework — and, in `skills/wardley-map-drafting/SKILL.md`, one short quoted
sentence used as a quotation with attribution. Source: S. Wardley, "Finding a Path", chapter 2
of *Wardley Maps*, Medium, 2016.
<https://medium.com/wardleymaps/finding-a-path-cdb1249078c0>

---

## 6. Trademarks

The following are used **nominatively** — that is, to identify the method being implemented,
because there is no other way to say which method it is. No claim to any of these marks is
made or implied.

- **HYPE CYCLE** is a registered trademark of **Gartner, Inc.** — US Reg. Nos. **4,640,207**
  (Serial 86224033) and **4,640,209** (Serial 86224040), both registered 18 November 2014,
  renewed in 2024 and currently live. **MAGIC QUADRANT** is likewise a Gartner, Inc. trademark; no
  registration number is asserted here because none was independently verified.
- **CYNEFIN** is a registered trademark of **Cognitive Edge Pte Ltd**, trading as
  **The Cynefin Company** — US Reg. No. **5,853,538** (Serial 87576158, registered 3 September
  2019, **Supplemental Register**), WIPO International Registration **1403925**, and the UK
  designation recorded as UK00801403925. (The USPTO record spells the owner "Cognitive Edge
  Ptd Ltd"; the company's own materials use "Pte Ltd", which is the spelling used here.)
- **Outcome-Driven Innovation® (ODI)** is asserted by **Strategyn LLC** as a registered
  trademark; the registration record was not independently verified.

Other product and organisation names appearing in this repository may be trademarks of their
respective owners.

**Non-affiliation and non-endorsement.** This repository is not affiliated with, sponsored by,
endorsed by, or in any way officially connected with Gartner, Inc., The Cynefin Company
(Cognitive Edge Pte Ltd), Strategyn LLC, or with any other rights holder, standards body,
agency or publisher named anywhere in this file. Nothing here is an official implementation
of any named method, and no named party has reviewed, approved or endorsed this work.

---

## 7. Corrections

If you believe material in this repository is misattributed, used outside its licence, or
missing a required notice, open an issue quoting the file, the line and the source. Licensing
and attribution issues are treated as defects and take priority over feature work.
