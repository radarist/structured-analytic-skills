# AMSTAR 2 — the 16 items, response options and rating criteria

Reference sheet for [SKILL.md](../SKILL.md) step 3. The 16 item questions and the Box 1 critical-domain list come from the AMSTAR 2 paper (attribution below). The "For Yes" / "For Partial Yes" criteria under each item, and the overall-confidence descriptions, are **restated in this sheet's own words** — they set out the same operational requirements as the authoritative checklist at <https://amstar.ca/Amstar_Checklist.php> (PDF: <https://amstar.ca/docs/AMSTAR-2.pdf>) without reproducing its wording; consult the checklist itself when an appraisal has to be defended verbatim. `python3 ../scripts/amstar2.py items` prints the same content.

**Responses:** Yes / No for every item; **Partial Yes** only for items 2, 4, 7, 8, 9; **No meta-analysis conducted** only for items 11, 12, 15. AMSTAR 2 removed "not applicable" and "cannot answer": if the report gives no information, the item is rated **No**.

**Critical domains (Box 1):** items 2, 4, 7, 9, 11, 13, 15 — appraisers may add or substitute others for their context, but must fix the list before answering.

## Item summary

| # | Item (short) | Options | Critical |
|---|---|---|---|
| 1 | Research question and inclusion criteria include PICO | Y/N |  |
| 2 | Protocol established before conduct; deviations justified | Y/PY/N | ✔ |
| 3 | Selection of study designs explained | Y/N |  |
| 4 | Comprehensive literature search strategy | Y/PY/N | ✔ |
| 5 | Study selection in duplicate | Y/N |  |
| 6 | Data extraction in duplicate | Y/N |  |
| 7 | Excluded studies listed and exclusions justified | Y/PY/N | ✔ |
| 8 | Included studies described in adequate detail | Y/PY/N |  |
| 9 | Satisfactory technique for assessing risk of bias (RoB) in included studies | Y/PY/N | ✔ |
| 10 | Sources of funding of included studies reported | Y/N |  |
| 11 | Appropriate methods for statistical combination (if meta-analysis) | Y/N/NMA | ✔ |
| 12 | Impact of RoB on the synthesis assessed (if meta-analysis) | Y/N/NMA |  |
| 13 | RoB accounted for when interpreting/discussing results | Y/N | ✔ |
| 14 | Heterogeneity satisfactorily explained and discussed | Y/N |  |
| 15 | Publication bias investigated and its impact discussed (if quantitative synthesis) | Y/N/NMA | ✔ |
| 16 | Conflicts of interest and review funding reported | Y/N |  |

## Full wording and criteria

Each item shows the question as published (quoted), the responses available, and — in this sheet's own words — what the review must have done to earn each response.

### 1. Research question and inclusion criteria include PICO

> Did the research questions and inclusion criteria for the review include the components of PICO?

**Options:** Yes / No

Yes requires all four PICO elements to be stated: who was studied, what was done to them, what that was compared against, and which outcomes were measured. Naming the follow-up window as well is encouraged but is not required for a Yes.

### 2. Protocol established before conduct; deviations justified — CRITICAL DOMAIN

> Did the report of the review contain an explicit statement that the review methods were established prior to the conduct of the review and did the report justify any significant deviations from the protocol?

**Options:** Yes / Partial Yes / No

Partial Yes requires the report to say a written protocol or plan existed beforehand and to show it covered every one of: the review question(s); how the literature would be searched; what would be included and excluded; how risk of bias would be judged. Yes requires all of that, plus the protocol to have been registered and to have additionally specified how results would be pooled or synthesised where that applies, how the causes of heterogeneity would be explored, and any departure from the plan to be explained.

### 3. Selection of study designs explained

> Did the review authors explain their selection of the study designs for inclusion in the review?

**Options:** Yes / No

Yes requires a stated reason for whichever design choice was made — admitting randomised trials only, admitting non-randomised studies only, or admitting both.

### 4. Comprehensive literature search strategy — CRITICAL DOMAIN

> Did the review authors use a comprehensive literature search strategy?

**Options:** Yes / Partial Yes / No

Partial Yes requires all three of: two or more databases suited to the question were searched; the search terms or the full strategy are reported; and any restriction on what could be retrieved (language, date, publication status) is defended. Yes requires those three and all of the following as well: the bibliographies of the included papers were checked; trial or study registers were queried; subject-matter experts were consulted; grey literature was sought wherever it is pertinent; and no more than 24 months separate the search from the finished review.

### 5. Study selection in duplicate

> Did the review authors perform study selection in duplicate?

**Options:** Yes / No

Yes by either route: two or more reviewers screened eligibility independently and then settled on a common include list; or two reviewers screened a subset, concurred on at least 80 percent of it, and a single reviewer handled the remainder.

### 6. Data extraction in duplicate

> Did the review authors perform data extraction in duplicate?

**Options:** Yes / No

Yes by either route: two or more reviewers reached agreement on the data pulled from the included studies; or two reviewers extracted from a subset with at least 80 percent concordance and one reviewer extracted the remainder.

### 7. Excluded studies listed and exclusions justified — CRITICAL DOMAIN

> Did the review authors provide a list of excluded studies and justify the exclusions?

**Options:** Yes / Partial Yes / No

Partial Yes requires the report to name every candidate study that was read at full text and then rejected. Yes additionally requires a stated reason for rejecting each of those studies; counts alone in a flow diagram do not reach either level.

### 8. Included studies described in adequate detail

> Did the review authors describe the included studies in adequate detail?

**Options:** Yes / Partial Yes / No

Partial Yes requires every included study to be characterised on all of: population, intervention, comparator, outcomes and research design. Yes requires that characterisation to go further on all counts — population, intervention and comparator described in depth (dose or intensity wherever that matters), plus the setting in which the study ran and how long participants were followed.

### 9. Satisfactory technique for assessing risk of bias (RoB) in included studies — CRITICAL DOMAIN

> Did the review authors use a satisfactory technique for assessing the risk of bias (RoB) in individual studies that were included in the review?

**Options:** Yes / Partial Yes / No

Randomised trials — Partial Yes requires the review to have appraised at least whether allocation was concealed and whether patients and outcome assessors were blinded (blinding may be waived for outcomes that knowledge of the arm cannot sway, such as death from any cause). Yes requires two further sources of bias to have been appraised as well: whether the allocation sequence was genuinely random, and whether the reported result was picked out of several measurements or analyses of one specified outcome. Non-randomised studies — Partial Yes requires appraisal of confounding and of how participants came to be in the study. Yes requires two more: how exposures and outcomes were ascertained, and whether the reported result was picked out of several measurements or analyses of one specified outcome. A panel covering a design the review did not include is left unrated rather than counted.

### 10. Sources of funding of included studies reported

> Did the review authors report on the sources of funding for the studies included in the review?

**Options:** Yes / No

Yes requires the funding behind each individual included study to be reported. Stating that the reviewers went looking and the original authors had not disclosed it also earns Yes.

### 11. Appropriate methods for statistical combination (if meta-analysis) — CRITICAL DOMAIN

> If meta-analysis was performed did the review authors use appropriate methods for statistical combination of results?

**Options:** Yes / No / No meta-analysis conducted

Randomised trials — Yes requires all of: a stated rationale for pooling at all; a suitable weighted estimator, accommodating heterogeneity where it exists; and an inquiry into what drove any heterogeneity. Non-randomised studies — Yes requires all of: a stated rationale for pooling; a suitable weighted estimator accommodating heterogeneity where it exists; pooling of confounding-adjusted effect estimates rather than of unadjusted raw data (or an argument for using raw data where adjusted estimates did not exist); and, when both designs were included, pooled estimates reported separately for randomised and non-randomised evidence.

### 12. Impact of RoB on the synthesis assessed (if meta-analysis)

> If meta-analysis was performed, did the review authors assess the potential impact of RoB in individual studies on the results of the meta-analysis or other evidence synthesis?

**Options:** Yes / No / No meta-analysis conducted

Yes by either route: the synthesis drew only on randomised trials judged at low risk of bias; or, where the pooled randomised and/or non-randomised studies varied in risk of bias, the reviewers ran analyses testing how far that variation moved the summary effect.

### 13. RoB accounted for when interpreting/discussing results — CRITICAL DOMAIN

> Did the review authors account for RoB in individual studies when interpreting/discussing the results of the review?

**Options:** Yes / No

Yes by either route: only low-risk-of-bias randomised trials were included; or, where randomised trials at moderate or high risk of bias or non-randomised studies were included, the review works through what that risk of bias probably does to the findings.

### 14. Heterogeneity satisfactorily explained and discussed

> Did the review authors provide a satisfactory explanation for, and discussion of, any heterogeneity observed in the results of the review?

**Options:** Yes / No

Yes by either route: the results showed no material heterogeneity; or heterogeneity was present and the reviewers both traced where it came from and spelled out what it means for the review's results.

### 15. Publication bias investigated and its impact discussed (if quantitative synthesis) — CRITICAL DOMAIN

> If they performed quantitative synthesis did the review authors carry out an adequate investigation of publication bias (small study bias) and discuss its likely impact on the results of the review?

**Options:** Yes / No / No meta-analysis conducted

Yes requires both halves: a graphical or statistical examination for publication bias, and a discussion of how likely such bias is and how large a distortion it could have produced in the review's results.

### 16. Conflicts of interest and review funding reported

> Did the review authors report any potential sources of conflict of interest, including any funding they received for conducting the review?

**Options:** Yes / No

Yes by either route: the review authors declare that they hold no competing interests; or they name who funded the review and explain how any resulting conflicts were handled.

Items 9 and 11 carry separate randomised-trial and non-randomised-study panels; a review including both designs is rated on both and takes the weaker applicable answer, while the panel for a design the review did not include is left unrated.

## Overall confidence (Box 2)

- **High** — at most one non-critical weakness, and no critical flaw.
- **Moderate** — two or more non-critical weaknesses, still no critical flaw.
- **Low** — exactly one critical flaw, whatever the number of non-critical weaknesses.
- **Critically low** — two or more critical flaws, whatever the number of non-critical weaknesses.

Where non-critical weaknesses accumulate, confidence may erode enough to justify moving a Moderate rating down to Low (the Box 2 footnote; advisory — state it when applied). Item ratings are never summed into a score.

## Attribution and licence

The 16 item questions quoted above and the Box 1 list of critical domains are taken from:

> Shea BJ, Reeves BC, Wells G, Thuku M, Hamel C, Moran J, Moher D, Tugwell P, Welch V, Kristjansson E, Henry DA. "AMSTAR 2: a critical appraisal tool for systematic reviews that include randomised or non-randomised studies of healthcare interventions, or both." *BMJ* 2017;358:j4008. doi:10.1136/bmj.j4008 — **licensed CC BY 4.0** (<https://creativecommons.org/licenses/by/4.0/>).

**Changes made:** the item text has been condensed and reformatted; short item labels, the summary table, the response-code abbreviations (Y / PY / N / NMA) and all of the surrounding guidance are additions by this skill and are not the original authors'. The criteria and overall-confidence descriptions in this sheet are restatements written for this skill, not reproductions of the AMSTAR 2 checklist published at <https://amstar.ca/Amstar_Checklist.php>, which is separately copyrighted. Neither the AMSTAR 2 authors nor *BMJ* endorse this skill.
