---
name: Reproducibility & Open Science
category: scientific-method
origin: replication norm since early science (Boyle's air-pump witnesses, 1660s); modern reform movement: replication crisis (2010s), Center for Open Science (2013), FAIR principles (2016)
agent_suitability: High
tags: [replication, reproducibility, preregistration, open-data, fair, p-hacking, registered-reports]
related: [../scientific-methods/scientific-method-cycle.md, ../scientific-methods/hypothetico-deductive-method.md, ../research-methods/experimental-design.md, ../research-methods/meta-analysis.md, ../agent-playbook.md]
---

# Reproducibility & Open Science

> **Essence:** The integrity layer of science — findings count when independent others can obtain them again — enforced by preregistration, open materials/data/code, replication, and reporting standards that make corner-cutting visible.

## Overview

Science's epistemic superpower has never been individual brilliance; it is **organized distrust**: claims survive because others tried to break them and couldn't. Three distinct reproducibility concepts (following the National Academies' 2019 usage): **reproducibility** — same data + same code → same results (computational); **replicability** — same methods, new data → same conclusion; **generalizability** — the finding holds across populations/contexts. A result that isn't computationally reproducible is a claim about a button no one else can press; a result that doesn't replicate is, provisionally, an artifact of one dataset.

The **replication crisis** made this visceral. The Open Science Collaboration's 2015 study (*Science*) replicated 100 psychology studies: 97% of originals reported significant results; only 36% of replications did, with effect sizes roughly halved. Similar signals followed across disciplines (economics replication projects, cancer biology's Reproducibility Project — about half of landmark preclinical studies failing). The diagnosis centered on **questionable research practices (QRPs)**: **p-hacking** (flexible analysis — trying specifications until p < .05), **HARKing** (Hypothesizing After Results are Known — retrofitting the hypothesis to the data), optional stopping (peeking), selective reporting of measures/conditions, and publication bias upstream (journals preferring positive novelty). John Ioannidis' "Why Most Published Research Findings Are False" (2005) supplied the formal argument that small samples + small effects + flexibility + bias mathematically guarantee a literature of false positives.

The reform toolkit is this file's core. **Preregistration**: timestamp hypotheses, design, sample size, and analysis plan *before* data collection — deviations become visible (OSF is the standard platform). **Registered Reports**: journals peer-review the *protocol* and commit to publish regardless of results — killing publication bias and HARKing at once. **Open materials/data/code**: share what others need to re-run (with FAIR data discipline: Findable, Accessible, Interoperable, Reusable — Wilkinson et al., 2016). **Replication types**: direct/exact replication (same procedure) vs conceptual replication (same hypothesis, different operationalization — tests robustness of the claim, not the procedure). Plus reporting standards (CONSORT for trials, PRISMA for reviews, TOP guidelines for journals) and post-publication peer review. For agent-conducted research, these norms are not optional decoration: an agent that can re-run analyses a thousand ways *will* find p < .05 — preregistration and immutable logs are the only thing standing between agent pipelines and industrial-scale p-hacking.

## Origin & History

- **1660s:** Robert Boyle insists experiments be witnessed and repeatable (air-pump demonstrations) — replication as science's founding norm (Shapin & Schaffer's *Leviathan and the Air-Pump*).
- **1950s–90s:** statistical reform rumblings (Meehl; Cohen's power critique, 1962) largely ignored.
- **2005:** Ioannidis, "Why Most Published Research Findings Are False" (*PLoS Medicine*).
- **2011:** Bem's "feeling the future" psi paper and the Stapel fraud scandal trigger public crisis; Simmons, Nelson & Simonsohn's "False-Positive Psychology" (2011) demonstrates p-hacking experimentally.
- **2013:** Center for Open Science founded (Brian Nosek); OSF platform; **2015:** Open Science Collaboration, "Estimating the Reproducibility of Psychological Science" (*Science*).
- **2014–present:** Registered Reports spread (200+ journals); TOP guidelines (2015); **2016:** FAIR principles (*Scientific Data*); Many Labs / Registered Replication Reports institutionalize large-scale replication; funders mandate open data.

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Reproducibility | Same data + same code → same results (computational audit). |
| Replicability | New data, same methods → same conclusion. |
| Direct vs conceptual replication | Same procedure retested vs same hypothesis tested differently. |
| p-hacking | Flexible analysis/specification search until significance appears. |
| HARKing | Hypothesizing After Results are Known, presented as a priori. |
| Preregistration | Timestamped pre-commitment of hypotheses/design/analysis (OSF). |
| Registered Reports | Protocol peer-reviewed and accepted before results exist. |
| Publication bias | Positive/novel results publish preferentially; the file-drawer problem. |
| QRPs | Questionable research practices (optional stopping, selective reporting, flexibility). |
| FAIR data | Findable, Accessible, Interoperable, Reusable (Wilkinson et al. 2016). |
| TOP guidelines | Transparency and Openness Promotion standards for journals. |

## When to Use / When Not to Use

**Use when:**
- Any empirical claim intended to be believed and built upon — which is to say: always, as the integrity layer.
- Designing studies (preregister), publishing (share materials), evaluating literature (check replication status).
- Running computational/agentic research (immutable analysis logs, rerun-ability).
- Meta-science: auditing a literature's evidential value before relying on it.

**Don't use when:**
- Exploratory work is mislabeled as confirmatory — preregistration doesn't forbid exploration; it forbids *disguising* it (label exploratory findings honestly).
- Openness would harm: privacy-protected data, dual-use risks — use controlled access and say so (FAIR ≠ always open to everyone).
- "Replicate everything" as a resource fantasy — replicate what decisions/theories depend on.
- Replication failure is treated as proof of fraud — it is evidence about robustness, including boundary conditions; interpret with care.

## Process & Steps

**As the integrity layer of a study:**

**Elapsed time:** pre-registration costs hours to days *before* data collection (and is worthless after); immutable logging is near-zero marginal cost if wired into the workflow; the replication step (5) is the long pole — months, and often run by other labs entirely. Auditing a literature (6) is days per literature for an experienced analyst.

1. **Pre-register** before data collection: hypotheses, design, n + power, measures, exclusion rules, analysis plan. *Artifact: timestamped registration.*
2. **Execute with immutable logging**: data provenance, every analysis run recorded. *Artifact: audit log.*
3. **Report with the diff**: preregistration-vs-executed deviations declared; exploratory analyses labeled. *Artifact: transparent report + registration diff.*
4. **Open the materials**: data (FAIR; access-controlled where needed), code, materials, in a durable repository with a DOI. *Artifact: open package.*
5. **Invite/perform replication**: direct replications for load-bearing claims; conceptual replications for robustness; pre-register those too. *Artifact: replication studies.*
6. **Audit a literature before relying on it**: replication status, p-curve evidential value, preregistration prevalence, effect-size inflation (see [meta-analysis.md](../research-methods/meta-analysis.md)). *Artifact: evidential audit.*

## Techniques, Tools & Deliverables

- OSF (osf.io) for preregistrations and open materials; AsPredicted for lightweight registration.
- Registered Reports (journal track); TOP-aligned reporting checklists (CONSORT/PRISMA per field).
- FAIR data repositories (Zenodo, Dryad, OSF) with DOIs; containerization (Docker) for computational reproducibility; rerun scripts.
- p-curve, z-curve for literature evidential value; multiverse/specification-curve analysis to expose flexibility.
- **Deliverables:** registration, audit logs, open package, deviation report, replication outcomes, literature evidential audits.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Makes science's error-correction machinery actually run | Compliance cost (time, infrastructure) is real, especially for small teams |
| Kills the silent QRPs (flexibility becomes visible) | Preregistration can be gamed (vague plans); quality varies |
| Registered Reports fix publication bias structurally | Openness vs privacy/dual-use tensions need case-by-case handling |
| FAIR + containers make verification cheap | Replication itself needs funding and career credit — still uneven |
| Auditable literature (p-curve etc.) guides trust | Reform metrics can become new targets to game (Goodhart) |

The movement's own evidence is sobering: preregistration works, but registered reports remain a minority practice; replication rates in the big reproducibility projects (psychology 2015, economics, cancer biology) were low enough to be the strongest argument *for* the method and a permanent caveat on trusting single studies. Goodhart's law is the live risk — badges, open-data mandates, and p-hacking detectors can all be gamed once they become targets, and some journals adopted the rituals without the substance. The tooling side is rosier: containers and FAIR data genuinely collapsed the cost of verification. The honest summary: the infrastructure works; the incentives are the unfinished half.

## Worked Examples & Case Studies

- **Open Science Collaboration (2015):** 100-study psychology replication — 36% significant replication rate vs 97% original; the crisis's landmark document (*Science*, 349).
- **Reproducibility Project: Cancer Biology:** ~half of selected high-impact preclinical studies failed replication attempts — reshaped funder expectations.
- **Many Labs projects:** dozens of labs replicating classic effects simultaneously; several textbook effects shrank or vanished, others proved robust — sorting psychology's heritage empirically.
- **Registered Reports growth:** from *Cortex* (2013) to hundreds of journals; evidence that RR articles show markedly lower positive-result rates than standard articles — i.e., less bias.

## Variants & Related Methodologies

- **Multiverse / specification-curve analysis** — run all defensible analyses, report the distribution.
- **Adversarial collaboration** — rivals co-design the decisive study.
- **Living systematic reviews** — continuously updated syntheses ([systematic-literature-review.md](../research-methods/systematic-literature-review.md)).
- **Open notebook science** — radical-transparency variant.
- Related: [scientific-method-cycle.md](scientific-method-cycle.md) (the loop this protects), [hypothetico-deductive-method.md](hypothetico-deductive-method.md) (severe testing), [experimental-design.md](../research-methods/experimental-design.md) (preregistration in practice), [meta-analysis.md](../research-methods/meta-analysis.md) (pooling with bias correction), [evidence-appraisal.md](evidence-appraisal.md) (grading with replication status).

## Agent Adaptation

### Suitability for agent execution

**High — and for agent research it is existentially important.** Agents make p-hacking scalable: an unmonitored agent can try thousands of specifications. The countermeasures are pipeline-structural: preregister before any analysis runs; make analysis logs immutable (append-only, hashed/timestamped); require Verifier re-runs from raw data; auto-generate the registration-vs-executed diff; and run specification-curve analyses so flexibility is shown, not hidden. On the positive side, agents are superb at the open-science chores humans skip: packaging data+code with documentation, generating reproduction scripts, auditing literatures for replication status, and checking FAIR compliance.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Synthesizer | Preregistration drafts; open-package assembly (README, codebook, rerun scripts); deviation reports. |
| Analyst | All analyses in logged code; specification-curve runs on demand. |
| Critic / Red Team | Flexibility audit (how many defensible analyses exist? did we try them?); HARKing detection via hypothesis-timestamp diff; QRP checklist per study. |
| Verifier | Reproduces reported numbers from raw data + scripts; checks open package completeness (can a stranger rerun this?). |
| Scout | Literature evidential audits: replication status, preregistration prevalence, p-curve inputs. |
| Facilitator (human) | Preregistration lock; ethics/privacy calls on openness; reliance decisions on literatures. |

### Agent pipeline

1. Preregister (Synthesizer + human lock) → timestamped plan.
2. Execute (Analyst, append-only logs) → data + `analysis_log.jsonl`.
3. Diff + audit (Synthesizer deviation report; Critic flexibility/HARKing audit) → `integrity_report.md`.
4. Verify (Verifier clean-room rerun from raw data) → `reproduction_attestation.md`.
5. Open (Synthesizer FAIR package; privacy review by human) → repository + DOI.
6. (For reliance) Audit (Scout + Critic) → literature evidential report before building on claims.

### Prompt templates

```text
SYSTEM: You are the flexibility Critic. Preregistration: {{prereg}}. Analysis log:
{{analysis_log}}. Report: {{report}}. (1) Count the researcher degrees of freedom the design
allowed (outcome measures, covariates, exclusion rules, subgroup cuts, model choices). (2) From
the log: how many specifications were actually run? Which produced the reported result? (3) Diff
the report's hypotheses against the preregistration — every mismatch is a HARKing candidate;
list them. (4) Run (or specify) a specification curve across the defensible choices and state
what fraction are significant. Verdict per claim: CONFIRMATORY / EXPLORATORY-MISLABELED /
UNAUDITABLE.
```

```text
SYSTEM: You are the reproduction Verifier. Open package: {{package_contents}}. Reported results:
{{results}}. Without looking at the original analysis narrative, rerun the pipeline from raw
data using the provided scripts (or your reconstruction if scripts are missing/broken). Report:
which numbers reproduce exactly, which differ (by how much), which cannot be attempted (what's
missing), and a completeness verdict: can a competent stranger reproduce this package unaided?
List the specific gaps (data dictionary, environment spec, seeds, versions).
```

```text
SYSTEM: You are the literature evidential auditor. Claim set the project wants to rely on:
{{claims}}. For each claim's supporting literature report: (1) replication status (direct/
conceptual replications and their outcomes, cited); (2) preregistration prevalence; (3) signs of
publication bias / effect-size inflation (funnel asymmetry, p-curve where computable);
(4) verdict: LOAD-BEARING / USE WITH CARE / DO NOT RELY, with reasons. Sources required for
every verdict.
```

### Tools & data requirements

Code execution with logged runs (mandatory), timestamped/append-only storage (registrations, logs), repository tooling (FAIR packages, DOIs), literature access for evidential audits.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Industrial p-hacking by re-running agents | Analysis-log review | Immutable logs; pre-committed primary analysis; specification curves |
| HARKing | Hypothesis-timestamp diff | Preregistration lock before data; deviation reporting |
| Fake reproducibility (numbers retyped, not rerun) | Verifier clean-room pass | Reproduction from raw data, not from the report |
| Open-washing (package exists but can't run) | Stranger-rerun test | Completeness verdict required before "open" is claimed |
| Reliance on unreplicated claims | Evidential audit absent | Load-bearing verdicts required per relied-upon claim |
| Privacy violations via openness | Human privacy review | Controlled access where needed; documented justification |

### Human-in-the-loop checkpoints

1. Preregistration lock (the commitment point).
2. Openness/privacy trade-off decisions.
3. Reliance decisions on literatures (what to build on).
4. Response to replication failures (interpretation is judgment).

### Inputs & outputs (chaining contract)

**Inputs:** study designs and analysis pipelines (from any empirical method here); literatures (from [systematic-literature-review.md](../research-methods/systematic-literature-review.md)).
**Outputs:** registrations, integrity reports, reproduction attestations, FAIR packages, evidential audits — feeding [evidence-appraisal.md](evidence-appraisal.md) (grading), [meta-analysis.md](../research-methods/meta-analysis.md) (cleaner pools), and any downstream reliance.

## References & Further Reading

- Open Science Collaboration (2015). "Estimating the Reproducibility of Psychological Science." *Science*, 349(6251).
- Ioannidis, J.P.A. (2005). "Why Most Published Research Findings Are False." *PLoS Medicine*, 2(8).
- Simmons, J.P., Nelson, L.D. & Simonsohn, U. (2011). "False-Positive Psychology: Undisclosed Flexibility in Data Collection and Analysis Allows Presenting Anything as Significant." *Psychological Science*, 22(11).
- Wilkinson, M.D. et al. (2016). "The FAIR Guiding Principles for Scientific Data Management and Stewardship." *Scientific Data*, 3:160018.
- National Academies of Sciences, Engineering, and Medicine (2019). *Reproducibility and Replicability in Science.* National Academies Press.
- Nosek, B.A. et al. (2015). "Promoting an Open Research Culture" (TOP Guidelines). *Science*, 348(6242).
- Chambers, C.D. (2013). "Registered Reports: A New Publishing Initiative at Cortex." *Cortex*, 49(3).
- Munafo, M.R. et al. (2017). "A Manifesto for Reproducible Science." *Nature Human Behaviour*, 1:0021.
- Shapin, S. & Schaffer, S. (1985). *Leviathan and the Air-Pump.* Princeton. (replication's origins)
- Center for Open Science — OSF platform and resources (cos.io).
