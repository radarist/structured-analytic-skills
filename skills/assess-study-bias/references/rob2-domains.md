# RoB 2 domains, signalling-question IDs and judgement rules

Companion to `../SKILL.md`. Structure, question numbering, response options and judgement algorithms follow the *Revised Cochrane risk-of-bias tool for randomized trials (RoB 2)*, full guidance document version 22 August 2019, and Sterne et al., *BMJ* 366:l4898 (2019).

> **The signalling-question wording is not reproduced here.** RoB 2 is © its authors (Higgins, Savović, Page, Sterne and the RoB2 Development Group) and is published under CC BY-NC-ND 4.0 — Attribution, NonCommercial, NoDerivatives — which permits neither commercial redistribution nor adaptation of the instrument's text. This file therefore carries only the unprotectable method: question IDs, response options and the published decision logic. **Read the exact questions at https://www.riskofbias.info/welcome/rob-2-0-tool** (signalling-question boxes of the full guidance) and answer against that text. The one-line topics below and in `../scripts/rob2.py questions` are signposts written for this skill, not the instrument.

## Response options

`Y` Yes · `PY` Probably yes · `PN` Probably no · `N` No · `NI` No information. Conditional questions additionally accept `NA` (not applicable) and are answered only when their condition is met. NI is a legitimate answer — never upgrade it to PY to keep a domain Low.

## The two effects of interest

RoB 2 assesses one of two effects, and the answers to Domain 2 differ between them:

| Effect | Meaning |
|---|---|
| **Effect of assignment to intervention** | The intention-to-treat effect: the effect of being assigned at baseline, regardless of whether the intervention was received as intended. **This skill and `scripts/rob2.py` assess this effect.** |
| Effect of adhering to intervention | The per-protocol effect: the effect of adhering to the interventions as specified in the trial protocol. |

## The five domains

| # | Domain | Signalling questions |
|---|---|---|
| 1 | Bias arising from the randomization process | 1.1–1.3 |
| 2 | Bias due to deviations from intended interventions | 2.1–2.7 |
| 3 | Bias due to missing outcome data | 3.1–3.4 |
| 4 | Bias in measurement of the outcome | 4.1–4.5 |
| 5 | Bias in selection of the reported result | 5.1–5.3 |

## Signalling-question index

Topic labels below are this skill's own shorthand for locating each question in the source — **not** the question. Fetch the published wording before answering; the polarity of some questions (1.3, 4.1, 4.2, 5.2, 5.3) is inverted, so "Yes" is the unfavourable answer. Options are the published response sets; conditional questions also accept `NA` and are answered only when their condition is met.

| ID | Condition | Topic | Options |
|---|---|---|---|
| 1.1 | — | allocation sequence random? | Y/PY/PN/N/NI |
| 1.2 | — | allocation concealed until enrolment and assignment? | Y/PY/PN/N/NI |
| 1.3 | — | baseline differences suggesting a randomization problem? | Y/PY/PN/N/NI |
| 2.1 | — | participant awareness of their own trial arm? | Y/PY/PN/N/NI |
| 2.2 | — | carers and intervention deliverers aware of the assignment? | Y/PY/PN/N/NI |
| 2.3 | If Y/PY/NI to 2.1 or 2.2 | departures from the intended intervention arising from the trial context? | NA/Y/PY/PN/N/NI |
| 2.4 | If Y/PY to 2.3 | outcome plausibly affected by those departures? | NA/Y/PY/PN/N/NI |
| 2.5 | If Y/PY/NI to 2.4 | those departures balanced across arms? | NA/Y/PY/PN/N/NI |
| 2.6 | — | analysis appropriate for the effect of assignment (ITT)? | Y/PY/PN/N/NI |
| 2.7 | If N/PN/NI to 2.6 | potential for substantial impact of not analysing as randomized? | NA/Y/PY/PN/N/NI |
| 3.1 | — | data available for all or nearly all randomized participants? | Y/PY/PN/N/NI |
| 3.2 | If N/PN/NI to 3.1 | evidence against bias from the absent data? | NA/Y/PY/PN/N — **no `NI`** |
| 3.3 | If N/PN to 3.2 | possible dependence of missingness on the true outcome value? | NA/Y/PY/PN/N/NI |
| 3.4 | If Y/PY/NI to 3.3 | likely dependence of missingness on the true outcome value? | NA/Y/PY/PN/N/NI |
| 4.1 | — | measurement method inappropriate? | Y/PY/PN/N/NI |
| 4.2 | — | measurement or ascertainment differing between arms? | Y/PY/PN/N/NI |
| 4.3 | If N/PN/NI to 4.1 and 4.2 | assessor awareness of the arm a participant received? | NA/Y/PY/PN/N/NI |
| 4.4 | If Y/PY/NI to 4.3 | possible influence of that awareness on the assessment? | NA/Y/PY/PN/N/NI |
| 4.5 | If Y/PY/NI to 4.4 | likely influence of that awareness on the assessment? | NA/Y/PY/PN/N/NI |
| 5.1 | — | analysis followed a plan pre-specified before unblinded data? | Y/PY/PN/N/NI |
| 5.2 | — | result selected from multiple eligible outcome measurements? | Y/PY/PN/N/NI |
| 5.3 | — | result selected from multiple eligible analyses? | Y/PY/PN/N/NI |

5.2 and 5.3 share one printed stem in the source; read them there as a pair.

## Domain algorithms (as implemented in `../scripts/rob2.py`)

Branch labels collapse answers to `Y/PY`, `N/PN`, `NI`. These are the published decision trees (Figures 1, 2, 4, 5, 7 and mapping Tables 4, 6, 10, 12, 14).

- **D1** — 1.2 `N/PN` → High. 1.2 `NI` → 1.3 `Y/PY` → High, else Some concerns. 1.2 `Y/PY` → 1.1 `N/PN` → Some concerns; else 1.3 `Y/PY` → Some concerns, else Low.
- **D2** — judged in two parts, the domain taking the more severe. Part 1: 2.1 and 2.2 both `N/PN` → Low; else 2.3 `N/PN` → Low, `NI` → Some concerns, `Y/PY` → 2.4 `N/PN` → Some concerns, else 2.5 `Y/PY` → Some concerns, else High. Part 2: 2.6 `Y/PY` → Low; else 2.7 `N/PN` → Some concerns, else High.
- **D3** — 3.1 `Y/PY` → Low. Else 3.2 `Y/PY` → Low; else 3.3 `N/PN` → Low; else 3.4 `N/PN` → Some concerns, else High.
- **D4** — 4.1 `Y/PY` → High; 4.2 `Y/PY` → High. Otherwise the floor is Low when 4.2 is `N/PN` and Some concerns when 4.2 is `NI`: 4.3 `N/PN` → floor; else 4.4 `N/PN` → floor; else 4.5 `N/PN` → Some concerns, else High.
- **D5** — 5.2 or 5.3 `Y/PY` → High; either `NI` (neither `Y/PY`) → Some concerns; both `N/PN` → 5.1 `Y/PY` → Low, else Some concerns.

## Domain and overall judgements

Each domain resolves to **Low risk of bias**, **Some concerns**, or **High risk of bias**.

Overall judgement (RoB 2 Table 1; Cochrane Handbook v6, Table 8.2.b):

| Overall | Criterion |
|---|---|
| Low risk of bias | The trial is judged at low risk of bias for **all** domains for this result. |
| Some concerns | The trial raises some concerns in at least one domain, but is not at high risk of bias for any domain. |
| High risk of bias | The trial is at high risk of bias in **at least one** domain, **or** it has some concerns for **multiple** domains in a way that substantially lowers confidence in the result. |

The second clause of "High" is an explicit review-author judgement. RoB 2 supplies no threshold for it. `scripts/rob2.py` adds one — `--sc-high-threshold`, default 3 — as **this skill's own mechanical stand-in**, not part of the instrument, and says so in its output.

## Direction of bias (optional, per domain and overall)

`NA` · Favours experimental · Favours comparator · Towards null · Away from null · Unpredictable.

## Adjacent tools

- **ROBINS-I** (Sterne et al., *BMJ* 355:i4919, 2016) — non-randomized studies of interventions; seven domains including confounding and selection of participants.
- **Single-arm studies and case series** — neither tool applies; such studies are hypothesis-generating.
