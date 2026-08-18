---
name: score-technology-readiness
description: "Scores how mature a specific technology is on the NASA Technology Readiness Level scale (TRL 1–9, read through a software/AI evidence checklist) and reports the highest level the evidence defends, the gap to any vendor claim, and the single piece of evidence needed to advance one level. Use when asked \"what TRL is X?\", \"is this production-ready or still a prototype?\", \"how mature is this model, library or platform?\", or \"score the technology readiness of X\". Not for market perception or hype (use `apply-hype-cycle`), open-source project vitality (use `oss-project-health`) or strategic build-vs-buy stage (use `evolution-stage`)."
license: "MIT (skill text); EU H2020 Annex G TRL definitions © European Union, CC BY 4.0"
metadata:
  category: technology-assessment
  method: Technology Readiness Level (TRL) assessment
  origin: NASA — S. Sadin, 1974 (seven levels); J. C. Mankins, 1995 (nine-level white paper)
  version: "2.0.0"
---
# Score Technology Readiness (TRL)

The Technology Readiness Level scale — conceived at NASA by Stan Sadin in 1974, fixed in nine levels by John C. Mankins' 1995 white paper and now normative in NPR 7123.1D (2023) — grades a technology by the environment in which it has actually been demonstrated, from basic principles observed (TRL 1) to a system proven in operations (TRL 9). A level is earned by evidence at that level *and every level below it* — cumulative and evidence-gated, never a marketing label — which prevents the commonest maturity failure: reading a demo, a benchmark or a vendor's "production-ready" as proof of deployment. This skill applies NASA's definitions through a software/AI evidence checklist; the verbatim NASA, EU and DoD tables (including the DoD software TRLs) are in `references/trl-scales.md`.

## When to invoke

Invoke when:

- Asked "what TRL is X?", "is X production-ready?", "can we deploy X?", "is this proven at scale?" or "how mature is this model / library / platform?".
- A vendor, paper or pitch claims a maturity level, or a roadmap or investment memo needs a readiness figure someone can act on.

Do NOT invoke when:

- The question is market perception ("is X overhyped?") — use `apply-hype-cycle`.
- The question is whether an open-source project is alive and maintained — use `oss-project-health`.
- The question is which strategic method fits (build, buy, rent, outsource) — use `evolution-stage`.
- The subject is a whole category ("AI for healthcare") — `decompose-research-question` splits it into scoreable components first.
- The claim under test is a benchmark number — use `benchmark-model-claims`; its score is the TRL 4 evidence here.

## The scale — software/AI reading

NASA wording abridged (verbatim in `references/trl-scales.md`); the right-hand column is this skill's evidence checklist.

| TRL | NASA definition (abridged) | Label — evidence that earns the level |
| --- | --- | --- |
| **1** | Basic principles observed and reported | **Basic principles** — arXiv preprint / peer-reviewed paper describing the mechanism |
| **2** | Technology concept / application formulated | **Concept** — written spec or working paper; no code required |
| **3** | Analytical and experimental proof-of-concept | **PoC** — public repo with a runnable example on toy input |
| **4** | Component validation in a laboratory environment | **Component validation** — benchmark on a controlled dataset; `benchmark-model-claims` score ≥ 3 |
| **5** | Component validated in a relevant environment | **Realistic environment** — third-party evaluation or replication on realistic, noisy data |
| **6** | Model/prototype demonstration in a relevant environment | **Pilot** — case study **or** named customer reference **or** closed beta with published results |
| **7** | System prototype demonstration in an operational environment | **Production** — production case study **and** visible incident reports **and** named reference customer |
| **8** | Actual system completed and qualified through test and demonstration | **Multi-customer** — published customer list **and** support SLA **and** public operational metrics |
| **9** | Actual system proven through successful mission operations | **Ecosystem** — industry-wide adoption **and** a downstream ecosystem that depends on it |

Software rarely reaches a pure TRL 9 — ecosystem dependence is the proxy (Kubernetes, CUDA); most enterprise SaaS is TRL 7–8. Hardware is scored on NASA's hardware descriptions; manufacturability is a separate MRL question (`references/trl-scales.md`, §6).

## Procedure

### 1 — Bound the technology

Name one technology with identifiable boundaries — a model, product, library, protocol or platform, scope stated ("the chat-completion API for general-purpose text", not "the company"). Vague categories cannot be scored; split them and score each component. Record who claims which level and where.

### 2 — Walk the levels from 1 upward, collecting evidence

At each level ask whether the table's requirement is met and cite the item (URL, DOI, named customer, status page). Type every item — demo, test report, deployment, peer-reviewed, vendor claim, press. **Vendor claims and press do not earn a level**; they only flag where independent confirmation is needed. Continue past the first gap so evidence stranded above it is reported, not credited.

### 3 — Fix the level and record the claim gap

The assessed TRL is the highest level such that every level from 1 to it is met — no skipping. If the claim is TRL 7 but level 6 rests on an unnamed pilot, the score is TRL 5 and the gap is two levels. State the delta (claimed minus evidenced); a delta of two or more is an over-claim and should be called one.

### 4 — Name the next-level gate and the deployment risk

Write the *single* evidence item that would move the technology up one level ("one named pilot with a published case study"; "independent incident reporting from a customer not on the vendor's marketing page") and the risk of using it above its evidenced level — typically unknown failure modes, because no incident record exists.

### 5 — Report and reproduce

Fill the output template. When the evidence list is long or contested, encode it in `evidence.json` and run `python3 scripts/trl.py assess --file evidence.json` so the cumulative rule and the vendor-claim gate are applied mechanically; quote its verdict line.

## Output template

```
## Technology Readiness Assessment — {technology}

**Subject:** {technology, with scope boundary}
**Claimed TRL:** {N | none} ({claimant}) · **Assessed TRL: {M}** · **Delta:** {N−M}

| TRL | Met? | Evidence (typed, cited) |
|---|---|---|
| 1 Basic principles | {met | partial | not met} | {item [type] — locator} |
| 2 Concept | … | … |
| 3 PoC | … | … |
| 4 Component validation | … | … |
| 5 Realistic environment | … | … |
| 6 Pilot | … | … |
| 7 Production | … | … |
| 8 Multi-customer | … | … |
| 9 Ecosystem | … | … |

**Verdict:** TRL {M} — {why the score stops here; "over-claim" if delta ≥ 2}
**To advance TRL {M} → {M+1}:** {the single evidence item still needed}
**Risks if deployed above TRL {M}:** {what is unknown because that evidence is missing}
```

Mandatory fields: subject with scope, the nine-row table with vendor-sourced items marked, verdict with delta, the next-level gate.

## Worked example

Subject: LLM-based code-review agents that comment on pull requests; the vendor claims TRL 8. The evidence set (illustrative, not a real vendor) is built into the companion tool, so `python3 scripts/trl.py --demo` reproduces the assessment exactly. Excerpt:

```
Claimed TRL: 8 (vendor)   Evidenced TRL: 7   Delta: +1 (claim exceeds evidence by 1 level)
TRL  Level                  Status        Evidence
5    Realistic environment  ✓ met         third-party-eval: third-party evaluations on live repos, incl. false-positive rates [test-report]
6    Pilot                  ✓ met         named-customer-reference: engineering blogs describing internal rollouts with metrics [deployment]
7    Production             ✓ met         production-case-study; incident-reports (public status pages); named-reference-customer [deployment]
8    Multi-customer         ⚠ partial     customer-list: vendor case studies and logo walls [vendor-claim, NOT counted]
                                          operational-metrics: ✗ missing (Operational metrics public)
9    Ecosystem              ✗ not met     industry-adoption: ✗ missing; ecosystem-dependence: ✗ missing
Verdict: TRL 7 -- claim of TRL 8 exceeds the evidence by one level; note the gap
```

Levels 1–7 are contiguous, so TRL 7 stands. Level 8 fails two of three criteria — the customer list is vendor-sourced (flagged, not counted) and no operational metrics are public — so the claimed TRL 8 sits one level above the evidence (delta +1: noted, not an over-claim). The gate is one item: independent incident or uptime reporting from a customer absent from the vendor's marketing page. Risk if adopted as TRL 8: production false-positive and silent-miss rates are undocumented, so merges should not be gated on the tool without an internal evaluation harness.

## Verification

- [ ] The subject is bounded (one technology, stated scope) and the claimant of any TRL is named.
- [ ] Every level 1…M is met by a cited, typed item — recompute the contiguous level by hand or with `scripts/trl.py assess`; nothing is credited on vendor claims or press alone.
- [ ] TRL 6 is a *relevant* environment and TRL 7 the *operational* environment, per NPR 7123.1D Appendix E.
- [ ] The delta (claimed − evidenced) is stated; a delta ≥ 2 is called an over-claim.
- [ ] The next-level gate is one checkable evidence item; hardware was scored on the hardware description and MRL / IRL / SRL questions were routed, not folded in.

## Companion tool

`scripts/trl.py` (stdlib-only) applies the cumulative gate above to an `evidence.json` listing the evidence present per level (free text or per-criterion items typed `demo|test-report|deployment|peer-reviewed|vendor-claim|press`). It scores the highest contiguous level with all criteria met, then reports claimed-vs-evidenced delta, gaps, next-level needs and a caution when a level rests only on vendor claims/press (not counted without `--accept-vendor-claims`).

```bash
python3 scripts/trl.py levels --scale nasa|eu|dod|all   # verbatim TRL 1–9 definitions
python3 scripts/trl.py assess --file evidence.json [--domain software|ai|hardware] [--json]
python3 scripts/trl.py --demo                            # reproduces the worked example
python3 scripts/trl.py --selftest
```

`--demo` output (excerpt):

```
8    Multi-customer         ⚠ partial     customer-list: vendor case studies and logo walls [vendor-claim, NOT counted]
To advance TRL 7 → 8 (Multi-customer), still needed:
  - operational-metrics: Operational metrics public
  - independent confirmation of: customer-list (currently vendor-claim/press only)
Verdict: TRL 7 -- claim of TRL 8 exceeds the evidence by one level; note the gap
```

Exit 2 = over-claim (claimed exceeds evidenced by ≥ 2). The skill is fully usable without the tool — walk the table by hand; the script only enforces no-skipping and the vendor gate.

## Pair with adjacent skills

- `evolution-stage` — Wardley stage is strategic method-fit; TRL is empirical readiness. Both belong on a technology profile.
- `apply-hype-cycle` — hype phase is perception; TRL is evidence. Divergence (TRL 8 in the Trough, TRL 3 at the Peak) is itself a finding.
- `benchmark-model-claims` — grades the benchmark claim that serves as TRL 4 evidence.
- `oss-project-health` — for open-source components, project vitality is part of the TRL 7–9 evidence.
- `abstain-or-escalate` — when a claimed level has no checkable evidence at all, say so rather than guess.

## Anti-patterns

- Do **not** accept a TRL from the vendor without independent evidence; check the cited pilot or customer directly.
- Do **not** score without a scope, and do **not** skip levels — no TRL 5 evidence means no TRL 7, however the product is sold.
- Do **not** use TRL for market readiness; technology and market are orthogonal.
- Do **not** invent a "hardware readiness level". Hardware takes NASA's hardware description plus MRL for manufacturability; integration and system maturity have their own scales (IRL, SRL).

## Reference

- J. C. Mankins, "Technology Readiness Levels: A White Paper," NASA Advanced Concepts Office, 6 April 1995.
- NASA, NPR 7123.1D, *NASA Systems Engineering Processes and Requirements*, effective 5 July 2023, §5.1.6 and Appendix E "Technology Readiness Levels", Table E-1. https://nodis3.gsfc.nasa.gov/displayDir.cfm?Internal_ID=N_PR_7123_001D_&page_name=AppendixE
- OUSD(R&E), *Technology Readiness Assessment Guidebook*, February 2025 — Table 2-1 (hardware TRLs), Table 2-2 "DoD Software TRL Definitions, Descriptions, and Supporting Information", ch. 6 (MRL, IRL, SRL). https://www.cto.mil/wp-content/uploads/2025/03/TRA-Guide-Feb2025-Cleared.pdf
- C. P. Graettinger, S. Garcia, J. Siviy, R. J. Schenk and P. J. Van Syckle, *Using the Technology Readiness Levels Scale to Support Technology Management in the DoD's ATD/STO Environments*, CMU/SEI-2002-SR-027, Software Engineering Institute, 2002.
- European Commission, *Horizon 2020 Work Programme 2014–2015, General Annexes*, Annex G "Technology readiness levels (TRL)", Commission Decision C(2014)4995.
- U.S. Department of Energy, DOE G 413.3-4A, *Technology Readiness Assessment Guide*, 2011.
- ISO 16290:2013, *Space systems — Definition of the Technology Readiness Levels (TRLs) and their criteria of assessment*.
- Sibling scales: OSD Manufacturing Technology Program, *MRL Deskbook*, 2022 (MRL 1–10); B. Sauser, R. Gove, E. Forbes and J. E. Ramirez-Marquez, "Integration maturity metrics: Development of an integration readiness level," *Information Knowledge Systems Management* 9(1):17–46, 2010, doi:10.3233/IKS-2010-0133; U.S. GAO, GAO-20-48G, *Technology Readiness Assessment Guide*, 2020.
