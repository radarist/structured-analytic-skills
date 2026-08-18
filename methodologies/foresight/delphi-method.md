---
name: Delphi Method
category: foresight
origin: Project RAND, early 1950s; Olaf Helmer & Norman Dalkey (published 1963); Nicholas Rescher (1958)
agent_suitability: High
tags: [expert-judgment, consensus, iteration, anonymity, forecasting, panels, rounds]
related: [../foresight/cross-impact-analysis.md, ../foresight/scenario-planning.md, ../foresight/trend-analysis.md, ../scientific-methods/bayesian-evidence-updating.md, ../agent-playbook.md]
---

# Delphi Method

> **Essence:** A structured, multi-round survey of experts that converts individual judgments into a refined group position through anonymity, iteration, controlled feedback, and statistical aggregation — expert consensus without committee pathologies.

## Overview

Delphi is the classic method for systematically harvesting expert judgment about uncertain futures: when events will occur, how impactful developments will be, what policies would work, where consensus exists and — equally valuable — where it genuinely does not. A panel of experts answers a questionnaire; a facilitator aggregates responses statistically (median, interquartile range) and feeds the distribution — plus anonymized reasons for extreme positions — back to the panel; experts reconsider and re-answer; rounds repeat until positions stabilize (typically 2–4 rounds). The final output is the group distribution and the arguments behind outliers, not a forced unanimous statement.

The method's four design features each target a known failure of face-to-face expert groups: **anonymity** (kills dominance, bandwagon, and seniority effects), **iteration** (allows opinion change without loss of face), **controlled feedback** (informs reconsideration with the group's actual distribution and reasoning), and **statistical group response** (preserves the distribution and dissent instead of forcing a single "consensus" line).

Delphi is a research method as much as a foresight method — it appears in health research (clinical practice consensus), information systems (ranking frameworks), and policy. Its modern variants include the **Real-Time Delphi** (Gordon & Pease: continuous, computer-mediated, no discrete rounds) and the **Policy Delphi** (which seeks the strongest pro/con arguments on options rather than consensus). Delphi is also the most naturally *agent-native* foresight method: the panel, the facilitator, and the feedback loop map one-to-one onto multi-agent orchestration.

## Origin & History

- **Early 1950s, Project RAND:** developed for US defense forecasting ("Project Delphi") — estimating, from a Soviet perspective, optimal US industrial target selection and required atomic bomb stocks. Olaf Helmer and Norman Dalkey were the key developers; Nicholas Rescher's *Predicting the Future* (1958) gave an early philosophical treatment.
- **1963 — first open publication:** Dalkey & Helmer, "An Experimental Application of the Delphi Method to the Use of Experts" (*Management Science*, 1963). Helmer's *Social Technology* (1966) and *Analysis of the Future: The Delphi Method* (1967) codified it.
- **1970s — expansion and critique:** Harold Linstone & Murray Turoff's *The Delphi Method: Techniques and Applications* (1975) remains the reference volume; widespread corporate/government use; also Harold Sackman's critical RAND evaluation (1975) questioning validity assumptions.
- **2000s — Real-Time Delphi:** Theodore Gordon & Adam Pease ("RT Delphi: An Efficient, 'Round-less' Almost Real Time Delphi Method", *Technological Forecasting and Social Change*, 2006) — web-based, continuous rounds.
- **Today:** standard in health (clinical guidance consensus), futures studies, IS research (Okoli & Pawlowski's 2004 guide), and large foresight programmes (Millennium Project).

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Panel | The selected experts; quality and diversity of selection dominate result quality. |
| Round | One full question–answer–aggregate–feedback cycle. |
| Anonymity | Panelists never learn who said what (often not even who is on the panel). |
| Controlled feedback | The aggregated distribution + anonymized rationales returned between rounds. |
| Statistical group response | Median + IQR (or similar) as the result — dissent is preserved, not averaged away. |
| Stability | Convergence criterion: responses stop moving between rounds (not necessarily consensus). |
| Outlier rationales | Arguments from distribution tails — often the most informative content. |
| Monitor team / facilitator | Designs questionnaires, aggregates, sanitizes feedback, manages bias. |
| Real-Time Delphi | Continuous, platform-mediated variant without discrete rounds. |
| Policy Delphi | Variant seeking strongest arguments for/against options, not consensus (Turoff). |

## When to Use / When Not to Use

**Use when:**
- The question needs expert judgment, not available data (timing of technologies, policy effects, rare-event likelihoods).
- You need to know where genuine consensus exists vs where disagreement is real — and the best arguments on each side.
- Face-to-face expert meetings would be dominated by status, geography, or politics.
- Building rankings/priorities from distributed experts (research agendas, indicator sets).

**Don't use when:**
- Good data or models exist (use them; Delphi is for judgment gaps).
- The panel can't actually be assembled with real expertise — Delphi amplifies panel quality, good or bad.
- You need fast answers (classic Delphi runs weeks; RT-Delphi days).
- Questions are vague ("the future of AI") — Delphi needs concrete, estimable items ("year by which X reaches Y% adoption").
- Groupthink is unacceptable and panel independence can't be preserved (feedback creates its own convergence pressure — see Limitations).

## Process & Steps

1. **Define the problem and questions.** Concrete, estimable items: dates, quantities, rankings, impact ratings. Pilot the questionnaire with 2–3 experts for ambiguity. *Artifact: question set.*
2. **Select the panel.** 10–50 (commonly 15–35) experts chosen for *diversity of relevant expertise and perspective*, not prestige. Document selection criteria. *Artifact: panel roster + rationale.*
3. **Round 1.** Distribute questionnaire; collect quantitative estimates AND qualitative reasons (especially: what would change your mind? what are you assuming?). *Artifact: response dataset.*
4. **Aggregate and feed back.** Compute median, IQR/quartiles per item; summarize anonymized arguments, especially outlier rationales; return to panel. *Artifact: feedback report.*
5. **Rounds 2–3(+).** Panelists re-estimate, seeing the distribution; those outside the IQR are invited to defend or revise (their arguments are the gold). Repeat until stability. *Artifact: round-by-round movement data.*
6. **Analyze and report.** Final distributions, consensus/stability measures, dissent clusters, strongest arguments per position, and minority views. *Artifact: Delphi report.*
7. **(Optional) Cross-link results.** Feed timing estimates into [cross-impact-analysis.md](cross-impact-analysis.md) or scenario consistency work.

**Classical parameters:** rounds 1–2 weeks apart; high completion rates require short questionnaires and reminder management; attrition between rounds is the main operational enemy.

## Techniques, Tools & Deliverables

- Question types: date estimation, probability, Likert agreement, ranking/prioritization, argument elicitation.
- Statistics: median + IQR; stability via inter-round movement (e.g., % of responses changing); consensus measures (Kendall's W for rankings).
- Platforms: survey tools for classic Delphi; dedicated RT-Delphi platforms; spreadsheets suffice for small panels.
- **Deliverables:** item-by-item distributions, stability analysis, argument digest (pro/con/minority), panel-composition appendix.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Strips committee pathologies from expert judgment | Panel selection is destiny; bias in = bias out |
| Preserves dissent and surfaces best arguments | Feedback can manufacture convergence (bandwagon to the median) |
| Works across geography and disciplines | Slow (weeks) and labor-intensive in classic form |
| Quantifiable, auditable process | No guarantee experts are right — aggregates informed opinion, not truth |
| Repeatable for monitoring over time | Questionnaire framing strongly shapes answers; attrition skews later rounds |

The documented failure modes deserve emphasis. Convergence can be manufactured: when feedback shows each round's median, some panelists drift toward it to avoid defending an outlier — the process then measures social pressure, not expertise (this is why the method insists on echoing *rationales*, not just numbers). Panel selection is destiny — a panel sampled from one school of thought will converge confidently on that school's errors. And attrition is not random: the busiest and often most senior experts drop out between rounds, so later rounds systematically over-represent the less engaged. Delphi's own history is the caution: early RAND forecasts produced confident, convergent, wrong answers on technology timing. Use it to map and discipline expert judgment; never present the median as a measured fact.

## Worked Examples & Case Studies

- **RAND long-range forecasting studies (1960s):** Gordon & Helmer's "Report on a Long-Range Forecasting Study" (1964) applied Delphi to scientific/technological futures — the canonical early large application.
- **Health research:** Delphi is a standard method for clinical consensus (e.g., developing core outcome sets — COMET initiative uses Delphi routinely) and for criteria where trials are impractical.
- **Information systems:** Okoli & Pawlowski (2004) document Delphi use for rankings and framework development in IS; widely used for research-agenda setting.
- **Millennium Project Real-Time Delphi studies:** ongoing RT-Delphi applications to global futures questions (e.g., future pandemics, AI governance topics).

## Variants & Related Methodologies

- **Real-Time (round-less) Delphi** — continuous re-estimation on a platform (Gordon & Pease, 2006).
- **Policy Delphi** — argument-focused, decision-support variant (Turoff).
- **Disaggregation/Dissensus Delphi** — deliberately maps disagreement clusters instead of convergence.
- **Delphi + Cross-Impact** — estimates feed a cross-impact model ([cross-impact-analysis.md](cross-impact-analysis.md)).
- Related: [trend-analysis.md](trend-analysis.md) (TIA event judgments), [scenario-planning.md](scenario-planning.md) (expert input), [bayesian-evidence-updating.md](../scientific-methods/bayesian-evidence-updating.md) (formal belief aggregation alternative).
- Skill counterpart: [skills/delphi-method](../../skills/delphi-method/SKILL.md) — the one-page executable form, with a companion aggregation tool (median/IQR, stability check, Kendall's W).

## Agent Adaptation

### Suitability for agent execution

**High — Delphi is the most agent-native method in this library.** The architecture maps directly: Domain Expert agents as panelists (diverse personas = designed panel diversity), a Facilitator agent as monitor team (aggregation, feedback sanitization), iteration as a loop in the orchestrator. Agents don't fatigue, don't anchor on status, and can run 10 rounds overnight. Two honest caveats: (1) agents share training data and priors, so panel "diversity" is simulated — engineered persona variety mitigates but does not equal real expert diversity; (2) agents can hallucinate domain facts in their rationales — Verifier passes and grounding in retrieved sources are mandatory. Best use: agent-run Delphi for *draft* expert maps, pre-studies before convening real experts, and rapid option ranking — with human expert validation for high-stakes outputs.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Domain Expert (×8–20 personas) | Panelists: answer rounds with estimates + reasoning; personas engineered for discipline, geography, school-of-thought, and optimism/pessimism diversity. |
| Facilitator (agent) | Monitor team: distributes rounds, computes median/IQR, detects stability, sanitizes feedback (strips persona identity), elicits outlier rationales. |
| Scout | Grounds rounds: retrieves current evidence/facts panelists should reason from (reduces hallucinated premises). |
| Critic / Red Team | After final round: attacks consensus items (is this groupthink?) and validates that dissent is faithfully reported. |
| Synthesizer | Writes the Delphi report: distributions, argument digest, dissent map. |
| Verifier | Checks factual claims embedded in rationales. |
| Human | Designs/pilots questions, reviews the final report, decides what to trust. |

### Agent pipeline

1. Frame (human) → question set (piloted, concrete) + persona panel spec.
2. Ground (Scout) → `evidence_pack.md` shared to all panelists.
3. Round 1 (Domain Experts, parallel, isolated) → `round1.jsonl` [persona_id, item, estimate, rationale, confidence].
4. Aggregate (Facilitator) → medians/IQRs + outlier rationales (anonymized) → `feedback_r1.md`.
5. Rounds 2–3 (Experts with feedback) → movement tracked until stability (<15% of estimates change).
6. Stress-test (Critic) → groupthink audit; dissent fidelity check.
7. Report (Synthesizer + Verifier) → `delphi_report.md` → human review.

### Prompt templates

```text
SYSTEM: You are a panelist in a Delphi study. Your expert persona: {{persona_spec}} (stay in
character; reason from this expertise and its typical assumptions). You will estimate uncertain
future quantities. For each item give: numeric estimate, confidence (low|medium|high), your
reasoning (3-5 sentences), the key assumption, and what evidence would change your mind.
Base factual claims only on the provided evidence pack; if the pack lacks needed facts, say so
rather than inventing. Items: {{items}}
```

```text
SYSTEM: You are the Delphi facilitator. Round {{n}} results: {{round_jsonl}}. Compute per item:
median, Q1, Q3, IQR. Identify panelists outside the IQR (by persona_id). Draft the feedback
report: per item, the distribution summary and 2-4 anonymized rationales for extreme positions
(verbatim-edited, NO persona identifiers, no adjectives about the panelists). Then list items
that have stabilized (<15% movement vs previous round) vs still moving.
```

```text
SYSTEM: You are the Critic auditing this completed Delphi: {{all_rounds}}. (1) Groupthink audit:
which items converged fast on round-1 medians without argument exchange? (2) Faithfulness: does
the final report represent the strongest dissenting arguments, or were they averaged away?
(3) Panel audit: which persona clusters voted alike — is reported "consensus" actually one
school of thought? (4) Flag any rationale containing unsourced factual claims. Output a
structured audit with verdicts per item: TRUSTED / CONTESTED / SUSPECT.
```

### Tools & data requirements

No external tools strictly required (reasoning loop); web retrieval for the evidence pack strongly recommended; a structured store for rounds (JSONL); code execution or careful arithmetic for aggregation; an orchestrator that enforces panelist isolation within rounds.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Simulated diversity (personas vote alike) | Critic panel audit | Engineer personas across schools/geographies/values; measure cluster spread |
| Hallucinated facts in rationales | Verifier check | Evidence pack grounding; unsourced claims flagged or struck |
| Manufactured convergence (median gravity) | Movement analysis: convergence without argument change | Require revised estimates to state *why*; report argument movement, not just numbers |
| Persona leakage into feedback | Facilitator output review | Automated identity stripping; format-constrained feedback |
| False precision (dates to the year) | Output format | Report distributions (median + IQR), never point values |
| Anchor contamination from round 1 | Compare round-1 spread to final | Consider seeded question order variation; report anchoring analysis |

### Human-in-the-loop checkpoints

1. Question design and piloting (framing determines answers).
2. Persona panel composition (what "expertise" is simulated).
3. Final report interpretation — especially: which results are decision-grade vs hypothesis-grade.
4. For high-stakes use: validation of key findings by real human experts.

### Inputs & outputs (chaining contract)

**Inputs:** question set; evidence pack (from [horizon-scanning.md](horizon-scanning.md)/retrieval); persona spec.
**Outputs:** distributions per item, stability analysis, argument digest, dissent map — feeding [cross-impact-analysis.md](cross-impact-analysis.md) (event probabilities), [scenario-planning.md](scenario-planning.md) (timing estimates), [technology-roadmapping.md](technology-roadmapping.md) (milestone dates), [bayesian-evidence-updating.md](../scientific-methods/bayesian-evidence-updating.md) (priors).

## References & Further Reading

- Dalkey, N. & Helmer, O. (1963). "An Experimental Application of the Delphi Method to the Use of Experts." *Management Science*, 9(3).
- Linstone, H.A. & Turoff, M. (eds.) (1975). *The Delphi Method: Techniques and Applications.* Addison-Wesley.
- Gordon, T.J. & Helmer, O. (1964). *Report on a Long-Range Forecasting Study.* RAND P-2982.
- Sackman, H. (1975). *Delphi Critique: Expert Opinion, Forecasting, and Group Process.* Lexington Books.
- Gordon, T.J. & Pease, A. (2006). "RT Delphi: An Efficient, 'Round-less' Almost Real Time Delphi Method." *Technological Forecasting and Social Change*, 73(4).
- Okoli, C. & Pawlowski, S.D. (2004). "The Delphi Method as a Research Tool: An Example, Design Considerations and Applications." *Information & Management*, 42(1).
- Rowe, G. & Wright, G. (1999). "The Delphi Technique as a Forecasting Tool: Issues and Analysis." *International Journal of Forecasting*, 15(4).
- Glenn, J.C. & Gordon, T.J. (eds.) (2009). "The Delphi Method." In *Futures Research Methodology — Version 3.0.* The Millennium Project.
