---
name: Agent Playbook — Running This Library with AI Agents
category: playbook
origin: synthesized for this library (2026)
agent_suitability: High
tags: [multi-agent, orchestration, roles, pipelines, verification, prompt-engineering, rigor]
related: [../methodologies/foresight/scenario-planning.md, ../methodologies/research-methods/systematic-literature-review.md, ../methodologies/scientific-methods/scientific-method-cycle.md]
---

# Agent Playbook

> **Essence:** The master guide for executing every methodology in this library with AI agents — the role catalog, orchestration patterns, end-to-end pipeline recipes, the rigor layer that keeps agent work honest, and the practical setup.

## Overview

Every methodology file in this library contains an **Agent Adaptation** section written against the shared vocabulary defined here. This playbook is the capstone: it specifies the agent roles and their system prompts, the orchestration patterns that recur across methodologies, three fully worked pipeline recipes that chain methodology files into end-to-end investigations, the verification layer that separates agent-*assisted* rigor from agent-*generated* confidence, and the practical setup guidance (tools, state, cost, and when not to automate).

The governing principle: **agents do volume, structure, and discipline; humans do framing, judgment, values, and accountability.** Agents never tire, never skip the boring transcript, never forget a control variable, and can hold 40 sources in view at once — but they hallucinate citations, converge on training-data consensus, flatter the asker, and cannot be accountable for anything. The patterns below are designed to harvest the first list and structurally suppress the second.

## 1. The Agent Role Catalog

Each role is a configuration: a model + a system prompt + tool access + input/output contract. Roles are *functions*, not agents — one orchestrator may play several, or a swarm may run one role a hundred times in parallel.

| Role | Function | Tool needs | Used heavily in |
|---|---|---|---|
| **Scout** | Wide gathering: web/feed/literature sweeps; returns raw material with source URLs and dates | Web search, fetch, RSS | horizon-scanning, SLR, trend-analysis, Delphi evidence packs |
| **Analyst** | Structure and compute: classify, cluster, code, rate, fit, extract — with quote/data anchoring | Code execution, stores | every methodology |
| **Domain Expert** | Persona-prompted specialist judgment; panels of diverse experts | None (reasoning) | Delphi, futures-triangle, IBE, cross-impact rating |
| **Critic / Red Team** | Adversarial audit: falsify, find bias, challenge consensus, enforce chain rules | Read access to all artifacts | every methodology (mandatory) |
| **Synthesizer** | Integrate into deliverables: narratives, tables, reports, maps | Document generation | every methodology |
| **Verifier** | Ground-truth checking: URLs resolve, quotes exist, numbers recompute, citations real | Web fetch, code execution | every methodology (mandatory) |
| **Facilitator** | Orchestrate rounds/gates; aggregate judgments; **human where accountability lives** | Orchestrator access | Delphi, scenario planning, all human gates |

### Example system prompts (copy-adapt)

```text
SYSTEM — SCOUT: You are a Scout in a research pipeline. Your job is gathering, not judging.
Return only sourced material: every item carries a URL (or document ID) and a retrieval date.
Prefer primary and official sources. If you find nothing worth reporting, report nothing —
silence is a valid and valued result. Never fill a quota with low-quality material.
Output format: JSONL, one item per line: {"item": ..., "why_relevant": ..., "url": ..., "date": ...}
```

```text
SYSTEM — DOMAIN EXPERT: You are {{persona_name}}, {{persona_description}}. Reason strictly from
this expertise: its typical methods, assumptions, and blind spots. When asked for estimates,
give numbers with confidence levels and state your key assumption. When the evidence pack lacks
facts you need, say so — do not invent them. You will disagree with other experts when your
discipline would; do not seek consensus. Stay in persona until told the round has ended.
```

```text
SYSTEM — CRITIC: You are the Critic. Your only loyalty is to the quality of the final output.
Attack: unsupported claims, motivated reasoning, consensus without argument, missing
alternatives, vague language dressed as analysis, and quality-check steps that were skipped or
performed carelessly. For every objection cite the specific artifact and passage. Rank your
objections by how much they would change the conclusion. You are never done early: if you find
nothing, say what you checked and why it survived.
```

```text
SYSTEM — VERIFIER: You are the Verifier. You trust nothing. For each claim assigned to you:
(1) if it cites a source, fetch the source and check the claim matches what it says;
(2) if it is a number, recompute it from the underlying data or locate it verbatim in a source;
(3) if it is a quote, find it verbatim. Verdicts: CONFIRMED / MISREPRESENTED / UNSOURCED /
UNRESOLVABLE, each with one line of evidence. You confirm nothing you could not check.
```

## 2. Orchestration Patterns

Five patterns recur across the library. Pick per methodology (each file's Agent Adaptation names its pattern).

### 2.1 Sequential pipeline
Linear stages with artifacts passed forward; gates between stages.

```
Frame ──► Gather ──► Analyze ──► Synthesize ──► Stress-test ──► Report
(human)   (Scout)    (Analyst)   (Synthesizer)  (Critic+Verifier)  (human sign-off)
```
Use for: SLR, trend analysis, STEEP, technology roadmapping.

### 2.2 Parallel scan → synthesize
N Scouts sweep in parallel (per domain/source/category); Analyst merges; Synthesizer integrates; Critic prunes.

```
        ┌─ Scout(STEEP-S) ─┐
        ├─ Scout(STEEP-T) ─┤
Frame ──┤─ Scout(STEEP-E) ─┼──► Analyst(merge/dedupe/cluster) ──► Synthesizer ──► Critic ──► Report
        ├─ Scout(STEEP-E2)─┤
        └─ Scout(STEEP-P) ─┘
```
Use for: horizon scanning, STEEP, futures-wheel ring generation, litany harvesting in CLA.

### 2.3 Adversarial red-team / debate
Two or more agents argue opposing positions before a judge; used wherever a single agent's answer would be unearned consensus.

```
Question ──► Advocate A (thesis) ──┐
                                   ├──► Critic (clash, cross-exam) ──► Human/Expert judge ──► verdict + reasons
Question ──► Advocate B (anti) ────┘
```
Use for: axis selection in scenarios, commensurability in meta-analysis, H2+/H2− classification, GRADE certainty.

### 2.4 Multi-round convergence (Delphi-style)
Independent parallel answers → aggregate → anonymized feedback → re-answer → until stability. Isolation within rounds is enforced by the orchestrator, not by politeness.

```
Round 1: Experts(isolated) ─► Facilitator(median/IQR, outlier rationales) ─► feedback
Round 2: Experts(feedback) ─► Facilitator ─► stability check ─► (loop or exit) ─► Critic(groupthink audit)
```
Use for: [delphi-method.md](foresight/delphi-method.md), cross-impact rating, prior estimation for [bayesian-evidence-updating.md](scientific-methods/bayesian-evidence-updating.md).

### 2.5 Human-in-the-loop gates
Non-negotiable human decision points embedded in every pipeline:

```
[Agent stage] ──► GATE: human reviews artifact, decides ──► [next agent stage]
```
Standard gates (from the methodology files): focal question / problem framing; vision and values choices; axis/variable-set selection; rating and classification ratification; synthesis and claim sign-off; anything committing resources or reputation.

## 3. End-to-End Pipeline Recipes

Three recipes chain methodology files into complete investigations. Each stage lists: methodology file → agents → artifact passed forward.

### Recipe A — Foresight: "Where is our industry going and what do we do about it?"

```
1. horizon-scanning.md     Scout fleet (per STEEP domain, weekly)         → signals DB, issue radar
        GATE: human picks 3-5 escalated issues
2. steep-pestle-analysis.md Analyst (cluster+rate) + Critic               → rated driver inventory
3. trend-analysis.md       Scout+Analyst+Verifier (validate & project)    → validated trends (predetermineds)
4. futures-wheel.md        Analyst fleet per driver + Critic (chain rule) → implication maps
        GATE: human selects the 2 axes (from top critical uncertainties)
5. scenario-planning.md    Synthesizer(4 narratives)+Critic+Verifier      → scenario set + signposts
        GATE: leadership wind-tunnels strategy options
6. backcasting.md          Analyst(milestones)+Scout(precedents)+Critic   → pathway roadmap + near-term actions
7. bayesian-evidence-updating.md  Analyst belief log on scenario odds     → living probability tracking
        LOOP: signposts from (5) feed the Scout fleet in (1) — the system learns
```
Elapsed: 4–8 weeks human-paced; agent stages run nightly. Human effort concentrates in gates.

### Recipe B — Evidence research: "What does the evidence actually say about X?"

```
1. Frame (human) + systematic-literature-review.md
     Synthesizer drafts PICO/protocol            → GATE: human approves protocol
     Scout executes searches + dedupe            → results.bib + search log
     Analyst A/B dual screen + Expert adjudicate → included set (kappa reported)
     Critic sample-audit + Verifier quote-check  → audited screening
2. meta-analysis.md (if commensurable)
     Analyst extraction (quote-anchored)         → effects dataset
     Code executor: pooling, heterogeneity, bias → forest/funnel + I², τ²
     Critic alternative specifications           → sensitivity report
3. evidence-appraisal.md
     Analyst CASP/RoB per study (quote-anchored) → appraisal table
     Expert+Critic GRADE debate                  → certainty per outcome
4. reproducibility-open-science.md
     Scout evidential audit (replication status) → reliance verdicts
        GATE: human signs the summary-of-findings
```
Elapsed: days-to-weeks instead of months; humans spend their time on protocol, adjudication, and interpretation.

### Recipe C — Scientific inquiry: "Why is Y happening — and can we trust our answer?"

```
1. induction-abduction-analogy.md
     Domain Experts(isolated, diversity slots)    → candidate explanations
     Critic diversity audit + IBE matrix          → ranked candidates + next tests
        GATE: human picks what to test
2. hypothetico-deductive-method.md
     Analyst prediction matrix                    → falsifiable predictions (timestamped!)
     Critic severity gate                         → most discriminating test chosen
3. experimental-design.md (or observational test)
     Analyst power analysis + preregistration     → GATE: human locks preregistration
     Execute (lab/code/platform)                  → data + immutable analysis log
     Analyst results / Verifier rerun             → effect estimates
4. bayesian-evidence-updating.md
     Analyst updates odds from pre-committed LRs  → posterior on each rival hypothesis
5. reproducibility-open-science.md
     Synthesizer FAIR package + deviation report  → auditable study package
        GATE: human owns the claim language ("corroborated, pending replication")
```

## 4. The Rigor & Verification Layer

This layer is not optional. Agent pipelines without it produce fluent, structured, confidently wrong output at scale.

### 4.1 Hallucination countermeasures

| Threat | Structural countermeasure |
|---|---|
| Fabricated citations | Verifier fetches every cited source; UNSOURCED claims are rewritten or deleted — no exceptions |
| Fabricated quotes | Quote-anchoring rule: every extraction/coding/appraisal judgment carries a ≤25-word source quote, spot-checked |
| Fabricated numbers | Code-or-source rule: every number is recomputed in code or located verbatim in a source |
| Confabulated "evidence" in reasoning | Evidence packs: Domain Experts may only reason from Scout-gathered, Verifier-passed material |
| Memory drift across stages | Artifacts are files (versioned), not chat memory; each stage reads files, writes files |

### 4.2 Groupthink & sycophancy countermeasures

| Threat | Structural countermeasure |
|---|---|
| Panel convergence (Delphi-style) | Persona engineering across schools/geographies/values; isolation within rounds; Critic groupthink audit on the final distribution |
| Training-data median thinking | Diversity slots in generation prompts (conventional / mundane / heterodox / cross-domain); diversity audited before ranking |
| Sycophancy toward the human's framing | Critic system prompts forbid agreement-as-default; red-team pattern (2.3) for consequential choices |
| Anchoring on first draft | Independent parallel generation, then merge (never sequential refinement of one draft) |
| Consensus theater | Report dissent explicitly: minority arguments are deliverables, not embarrassments (Delphi tradition) |

### 4.3 Evaluation criteria for pipeline outputs

- **Traceability:** every claim resolves to a source, a computation, or a named judgment with a named owner.
- **Dissent fidelity:** minority positions are represented at their strongest, not averaged away.
- **Certainty language:** calibrated wording (GRADE-style or probability ranges); banned-words lint ("proven", "obviously", "everyone knows").
- **Gate compliance:** every human gate in the recipe has a logged decision.
- **Failure reporting:** stages report what they could NOT do/find/verify — silence-as-valid-result is honored.

## 5. Practical Setup

**Tooling by role:**
- Scout/Verifier: web search + fetch; RSS/feed readers; database exports (Scopus/WoS/PubMed via API where licensed).
- Analyst: code execution (Python/R) for clustering, statistics, matrices, curve-fitting; structured stores (JSON/CSV/JSONL files or a DB) as the single source of truth between stages.
- Synthesizer: document generation (Markdown; mermaid for diagrams).
- Facilitator/orchestrator: the agent framework that enforces isolation, rounds, gates, and immutable logs.

**State & memory:** pass artifacts as **files with schemas** (each methodology file's Agent Adaptation specifies them: `forces.json`, `round1.jsonl`, `prediction_matrix.md`...). Version everything. Timestamp anything pre-committed (predictions, preregistrations, priors) — integrity depends on it.

**Cost/latency trade-offs:** Scout fleets are cheap-per-call but voluminous (batch and budget them); Critic/Verifier passes add 20–40% to token cost and are where the value lives — never cut them to save tokens; Domain Expert panels scale linearly with panel size (8–20 personas is the useful range; beyond that, marginal diversity is small).

**When NOT to automate:**
- Data collection from humans (interviews, ethnography, surveys of real people) — agents prepare, humans gather.
- Values decisions: visions, problem framings, certainty calls, anything with accountability.
- Adversarial/high-stakes verification of the final output (a second, independent review path — ideally different models or humans).
- Synthetic stand-ins for human respondents (see [survey-research.md](research-methods/survey-research.md): persona panels pilot instruments; they are never data).

## 6. Selection Matrix — What to Run for Your Goal

| Your goal | Start here | Then chain to |
|---|---|---|
| "Don't let the future surprise us" | [horizon-scanning.md](foresight/horizon-scanning.md) | → STEEP → scenarios (Recipe A) |
| "Choose a robust strategy" | [scenario-planning.md](foresight/scenario-planning.md) | → backcasting → roadmap |
| "Get there from here" | [backcasting.md](foresight/backcasting.md) | → technology-roadmapping |
| "Transform, don't just improve" | [three-horizons.md](foresight/three-horizons.md) | → CLA → backcasting |
| "What do experts think (and where do they disagree)?" | [delphi-method.md](foresight/delphi-method.md) | → cross-impact → bayesian updating |
| "Understand why this issue is stuck" | [futures-triangle.md](foresight/futures-triangle.md) | → causal-layered-analysis |
| "What does the literature say?" | [systematic-literature-review.md](research-methods/systematic-literature-review.md) | → meta-analysis → evidence-appraisal (Recipe B) |
| "How big is the effect?" | [meta-analysis.md](research-methods/meta-analysis.md) | → evidence-appraisal |
| "No theory exists — build one" | [grounded-theory.md](research-methods/grounded-theory.md) | → case-study → survey (test it) |
| "Understand this one case deeply" | [case-study-research.md](research-methods/case-study-research.md) | → mixed-methods |
| "Build something that works" | [design-science-research.md](research-methods/design-science-research.md) | → experimental evaluation |
| "Does X cause Y?" | [experimental-design.md](research-methods/experimental-design.md) | → meta-analysis (pool with others) |
| "Why is this happening?" | [induction-abduction-analogy.md](scientific-methods/induction-abduction-analogy.md) | → hypothetico-deductive (Recipe C) |
| "Kill my wrong ideas fast" | [hypothetico-deductive-method.md](scientific-methods/hypothetico-deductive-method.md) | → bayesian updating |
| "How confident should we be?" | [bayesian-evidence-updating.md](scientific-methods/bayesian-evidence-updating.md) | → evidence-appraisal |
| "Can we trust this literature/claim?" | [reproducibility-open-science.md](scientific-methods/reproducibility-open-science.md) | → evidence-appraisal |

## References & Further Reading

- Each methodology file's References section for its canonical sources.
- The library's `_TEMPLATE.md` for the shared vocabulary and file conventions.
- Foundational multi-agent reasoning patterns this playbook operationalizes: debate/red-teaming, ensemble/panel aggregation, retrieval-grounded generation, and tool-augmented verification — as instantiated per-methodology in the files above.
