---
name: Systematic Literature Review (SLR) & PRISMA
category: research-method
origin: evidence-based medicine tradition (Cochrane Collaboration, 1993); PRISMA statement (Moher et al., 2009; updated Page et al., 2021); Kitchener & Charters guidelines for software engineering (2007)
agent_suitability: High
tags: [systematic-review, prisma, evidence-synthesis, literature, screening, reproducibility]
related: [../research-methods/meta-analysis.md, ../scientific-methods/evidence-appraisal.md, ../scientific-methods/reproducibility-open-science.md, ../agent-playbook.md]
---

# Systematic Literature Review (SLR) & PRISMA

> **Essence:** A pre-specified, documented, reproducible protocol for finding, selecting, appraising, and synthesizing ALL relevant studies on a focused question — a review that is itself a scientific instrument, not an essay.

## Overview

A narrative review says "here is what I happen to know and think about this literature". A systematic review says "here is the question, here is exactly how I searched, here is what I found, here is exactly why each study was included or excluded, here is how I judged quality, and here is what the totality of evidence shows — and you can rerun every step and check me." The method exists because narrative reviews are demonstrably biased by the reviewer's reading habits, language, and prior beliefs; medicine learned this the hard way when treatments kept being recommended against the totality of evidence.

The core machinery: (1) a **focused question** (PICO — Population, Intervention, Comparison, Outcome — for intervention questions; SPIDER for qualitative); (2) a **protocol** written *before* searching (databases, search strings, dates, inclusion/exclusion criteria) — increasingly registered publicly (PROSPERO for health); (3) a **documented search** across multiple databases with boolean strings; (4) **dual screening** — two reviewers independently apply criteria to titles/abstracts, then full texts, with disagreements resolved by discussion or a third reviewer (inter-rater reliability reported, e.g., Cohen's kappa); (5) **quality appraisal** of included studies with validated tools; (6) **synthesis** — narrative/thematic, or statistical ([meta-analysis.md](meta-analysis.md)) when studies are commensurable; (7) **PRISMA reporting** — the 27-item checklist and the flow diagram (records identified → screened → excluded with reasons → included) that makes the whole process auditable.

An SLR is the most procedurally rigid — and therefore the most automatable — research method in this library. Large parts (search-string generation, deduplication, screening, data extraction, PRISMA flow bookkeeping) are precisely defined rule application, which is why SLR automation has become its own research field and why agent pipelines fit it so well (see Agent Adaptation).

## Origin & History

- **1970s–80s:** Archie Cochrane's critique of medicine's un-synthesized evidence (*Effectiveness and Efficiency*, 1972); Gene Glass coins "meta-analysis" (1976) ([meta-analysis.md](meta-analysis.md)).
- **1993 — Cochrane Collaboration** founded: systematic reviews of healthcare interventions as an institution, with the *Cochrane Handbook* as the methodological reference.
- **1996/1999 — QUOROM** statement (Quality of Reporting of Meta-analyses).
- **2007 — Kitchener & Charters**, *Guidelines for performing Systematic Literature Reviews in Software Engineering*: the standard adaptation for SE/CS research.
- **2009 — PRISMA** (Moher et al.): 27-item checklist + four-phase flow diagram, superseding QUOROM.
- **2020/2021 — PRISMA 2020** (Page et al., *BMJ* 2021): updated checklist and flow for modern search/reporting; PRISMA-S for search reporting; extensions for protocols (PRISMA-P), scoping reviews (PRISMA-ScR).
- **2010s–present:** automation tooling (EPPI-Reviewer, Rayyan, Covidence; ML-assisted screening — e.g., ASReview) and living reviews.

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Protocol | The pre-registered plan: question, sources, strings, criteria, analysis — deviations must be reported. |
| PICO | Population, Intervention, Comparison, Outcome — question frame for intervention reviews. |
| SPIDER | Sample, Phenomenon of Interest, Design, Evaluation, Research type — frame for qualitative reviews. |
| Search string | Boolean query per database (concept blocks OR'd within, AND'd across), iteratively tested against known seed papers. |
| Inclusion/exclusion criteria | Objective rules applied at screening; must be decidable without reading the whole paper. |
| Dual independent screening | Two reviewers screen separately; reliability (kappa) reported; conflicts adjudicated. |
| Quality / risk-of-bias appraisal | Structured assessment of each included study (e.g., Cochrane RoB 2, Newcastle–Ottawa, CASP). |
| PRISMA flow diagram | The auditable funnel: identified → duplicates removed → screened → full-text assessed → included, with exclusion reasons. |
| Thematic/narrative synthesis | Qualitative integration when meta-analysis is inappropriate (Thomas & Harden methods). |
| Scoping review | Cousin method: map the field's extent/nature rather than answer a focused question. |

## When to Use / When Not to Use

**Use when:**
- A decision or research program depends on what the *totality* of evidence says.
- The literature is large, scattered, or contested — narrative cherry-picking is likely.
- You need a defensible, auditable answer (guidelines, policy, dissertation rigor).
- Mapping a field systematically (use a scoping review variant if no focused question yet).

**Don't use when:**
- The literature is tiny or the question exploratory (do a narrative/integrative review or [grounded-theory.md](grounded-theory.md)-style reading).
- You cannot define decidable inclusion criteria (question too fuzzy — tighten it first).
- Time/resources don't allow dual screening (a single-screener "SLR" is a narrative review with extra steps — say what it is).
- Rapid answers are needed in days (consider rapid-review variants with declared shortcuts).

## Process & Steps

1. **Frame the question** (PICO/SPIDER); confirm an SLR is the right instrument; check for existing reviews. *Artifact: question statement.*
2. **Write and register the protocol**: databases, date ranges, languages, search strings, inclusion/exclusion criteria, appraisal tools, synthesis plan. Register (PROSPERO or equivalent) where applicable. *Artifact: protocol.*
3. **Search**: run strings across ≥2–3 databases (e.g., Scopus, Web of Science, PubMed/IEEE/ACM by field); snowball references of included papers; record everything. *Artifact: raw result set + search log.*
4. **Deduplicate and screen**: title/abstract screening by two independent reviewers against criteria; then full-text screening with exclusion reasons logged. Report kappa. *Artifact: screened set + exclusion log.*
5. **Appraise quality** of included studies with a validated tool. *Artifact: appraisal table.*
6. **Extract data** into a structured form (bibliographics, methods, findings, quality). *Artifact: extraction sheet.*
7. **Synthesize**: narrative/thematic synthesis, or meta-analysis if commensurable. *Artifact: synthesis.*
8. **Report per PRISMA 2020**: flow diagram, checklist, limitations (search bias, publication bias, your own deviations). *Artifact: the review.*

**Realistic effort:** months for human teams; hundreds to thousands of records screened. This is exactly where agent pipelines change the economics.

## Techniques, Tools & Deliverables

- Seed-paper-validated search strings (a string that misses a known key paper is broken).
- Rayyan / Covidence / ASReview for screening management; Zotero for references.
- Cochrane RoB 2 (RCTs), Newcastle–Ottawa (observational), CASP checklists, JBI tools — by study type.
- Thematic synthesis (line-by-line coding of findings → descriptive → analytical themes) for qualitative evidence.
- **Deliverables:** protocol, search log, PRISMA flow, extraction + appraisal tables, synthesis, the report.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Minimizes reviewer bias; auditable and reproducible | Slow and expensive in classic human form |
| Reveals what is NOT known (evidence gaps) | Garbage in, gospel out: quality of included studies caps the conclusion |
| Foundation for guidelines and cumulative science | Publication bias distorts the pool itself (see [meta-analysis.md](meta-analysis.md)) |
| Procedurally clear — hence automatable | Rigid; criteria set early can misfit an evolving literature |
| Inter-rater reliability makes subjectivity visible | Reporting compliance (PRISMA) ≠ actual methodological quality in practice |

The documented failure mode is compliance theater: a PRISMA flow diagram can be drawn for a review whose search was two databases and a hunch. The checklist measures *reporting*, not rigor — the protocol must be real (registered, dated, before screening) for the reproducibility claim to mean anything. Two more honest notes: criteria set early can misfit an evolving literature (a living-review cadence mitigates this), and the method inherits the biases of the published record — publication bias and English-language bias survive even perfect screening. The strength is real though: this is the most automatable rigorous method in the library, and its audit trail is what lets a reader trust the synthesis without trusting the authors.

## Worked Examples & Case Studies

- **Cochrane reviews:** thousands of healthcare reviews that changed practice (e.g., reviews establishing or overturning interventions); the institutional benchmark.
- **Software engineering SLRs:** the Kitchener guidelines spawned a large SE SLR culture (e.g., systematic reviews of agile practices, testing techniques) — the standard reference for CS researchers.
- **Automation research:** ASReview (van de Schoot et al., 2021, *Nature Machine Intelligence*) demonstrated active-learning screening cutting workload dramatically while finding the vast majority of relevant records — the empirical basis for agent-assisted screening.

## Variants & Related Methodologies

- **Scoping review** (map a field; PRISMA-ScR).
- **Rapid review** (accelerated, declared shortcuts).
- **Umbrella review** (review of reviews).
- **Realist review** (what works, for whom, in what circumstances — theory-driven).
- **Systematic mapping study** (SE variant focused on structuring a field).
- Related: [meta-analysis.md](meta-analysis.md) (statistical synthesis), [evidence-appraisal.md](../scientific-methods/evidence-appraisal.md) (grading the result), [reproducibility-open-science.md](../scientific-methods/reproducibility-open-science.md) (registration culture).
- Skill counterparts: [skills/systematic-review](../../skills/systematic-review/SKILL.md) (the executable PRISMA pipeline) and [skills/meta-analysis](../../skills/meta-analysis/SKILL.md) (the pooling endpoint).

## Agent Adaptation

### Suitability for agent execution

**High — the best-automatable method in this library.** Search execution, deduplication, screening against criteria, data extraction, flow bookkeeping, and PRISMA drafting are rule-bound tasks; ML-assisted screening already proved the concept (ASReview). The human-essential steps: question framing, protocol approval, criteria judgment calls at the boundary, quality-appraisal interpretation, and synthesis claims. Design pattern: agents do volume work; humans sample-audit (e.g., re-screen 5–10% to measure agent reliability, mirroring kappa); every exclusion carries a reason; every extraction traces to a quote. The cardinal risk is silent criterion drift and fabricated extractions — countered by structured outputs, quote-anchoring, and audit sampling.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Facilitator (human) | Owns question, protocol, and final synthesis sign-off. |
| Synthesizer (protocol) | Drafts PICO, criteria, and search strings for human approval. |
| Scout | Executes searches via database APIs/exports; manages deduplication and retrieval logs. |
| Analyst (×2 independent screeners) | Screen titles/abstracts, then full texts, against criteria — two agents with different prompts/models simulate dual review; disagreements go to adjudication. |
| Domain Expert (persona) | Adjudicates screener conflicts; interprets quality appraisals. |
| Critic / Red Team | Audits: criterion drift, boundary cases, missed seed papers, extraction-vs-quote fidelity. |
| Verifier | Confirms every extracted datum exists in the source text (quote anchoring); checks citation metadata. |
| Code executor | Flow counts, kappa computation, dedupe, export tables. |

### Agent pipeline

1. Frame (human) → question; Synthesizer drafts protocol → human approves (the gate).
2. Search (Scout) → `results.bib` + `search_log.md`; validate strings against seed papers.
3. Dedupe + screen (Analyst A & B independently) → `screening_r1.jsonl` [record_id, decision, criterion_cited, confidence]; conflicts → Domain Expert adjudication.
4. Audit (Critic) → 5–10% sample re-screened; compute agreement; investigate misses.
5. Full-text screen + extraction (Analysts; every field quote-anchored) → `extraction.csv`; Verifier checks quotes against PDFs/text.
6. Appraisal (Domain Expert) → `quality_table.csv`.
7. Synthesize (Synthesizer; optional handoff to [meta-analysis.md](meta-analysis.md)) → draft review + PRISMA flow → human revision.

### Prompt templates

```text
SYSTEM: You are the search-string engineer for a systematic review. Question (PICO): {{pico}}.
Databases: {{databases}}. Seed papers that MUST be retrieved: {{seed_papers}}. Build concept
blocks (one per PICO element) with synonyms/variants OR'd within blocks, AND'd across. Draft
strings per database respecting its syntax. Then self-test: for each seed paper, explain why the
string catches it; if any is missed, revise the string and report the change. Output: strings +
test table.
```

```text
SYSTEM: You are screener {{screener_id}} in a systematic review. Apply ONLY these criteria:
{{criteria}}. For each record (title + abstract below), decide INCLUDE / EXCLUDE / UNSURE.
Rules: exclude only when a criterion clearly fails; when uncertain, UNSURE (never guess-exclude);
cite the exact criterion for every EXCLUDE. Do not use outside knowledge of the authors/journal —
judge the text. Output JSONL: {"id": ..., "decision": ..., "criterion": ..., "rationale": one
sentence}. Records: {{batch}}
```

```text
SYSTEM: You are the extraction Verifier. Paper: {{paper_text}}. Extraction record:
{{extraction_row}}. For EACH extracted field, find the supporting passage in the paper and quote
it (<= 25 words). If a field is not supported by the text, mark it UNSUPPORTED and propose the
correct value or NOT-REPORTED. Output: field-by-field table with verdicts. This is an audit:
your job is to catch errors, not to be agreeable.
```

```text
SYSTEM: You are the adjudicator. Two screeners disagreed on these records:
{{conflicts_with_rationales}}. Inclusion criteria: {{criteria}}. For each, read both rationales
and the abstract, then rule INCLUDE/EXCLUDE with a one-paragraph justification that interprets
the criterion — your rulings also serve as precedent for similar boundary cases (list the
precedent rule you applied at the end).
```

### Tools & data requirements

Database access/exports (Scopus/WoS/PubMed/IEEE APIs or manual export), reference management, PDF text extraction, a structured store (CSV/JSONL), code execution for dedupe/kappa/flow counts, and ideally two different models for the dual screeners.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Fabricated extractions/quotes | Verifier quote-anchoring pass | No field ships without a source quote |
| Criterion drift over batches | Critic batch-consistency audit | Criteria versioned; precedent log from adjudicator |
| Sycophant screener (includes everything) | UNSURE/INCLUDE rate stats; sample audit | Decision distributions monitored; human re-screen sample |
| Missed relevant papers (false excludes) | Seed-paper check + snowballing + audit recall estimate | UNSURE bucket; dual independent screeners; recall audit |
| Kappa theater (two agents = same model, same bias) | Agent agreement ≈ 100% | Use different models/prompts; report this honestly as a limitation |
| Protocol quietly deviated from | Search log vs protocol diff | Versioned protocol; deviations section mandatory |

### Human-in-the-loop checkpoints

1. Question and protocol approval (before any searching).
2. Adjudication of genuinely contested records (agent-rulable volume aside).
3. Quality-appraisal judgment and synthesis claims.
4. Final interpretation: what the evidence does and does not support.

### Inputs & outputs (chaining contract)

**Inputs:** a focused question; access to bibliographic databases; seed papers.
**Outputs:** protocol, auditable flow + logs, extraction/appraisal tables, synthesis — feeding [meta-analysis.md](meta-analysis.md) (if commensurable), [evidence-appraisal.md](../scientific-methods/evidence-appraisal.md) (grading), guidelines/policy.

## References & Further Reading

- Page, M.J. et al. (2021). "The PRISMA 2020 Statement: An Updated Guideline for Reporting Systematic Reviews." *BMJ*, 372:n71. Official site: prisma-statement.org.
- Moher, D. et al. (2009). "Preferred Reporting Items for Systematic Reviews and Meta-Analyses: The PRISMA Statement." *PLoS Medicine*, 6(7).
- Higgins, J.P.T. et al. (eds.) (current). *Cochrane Handbook for Systematic Reviews of Interventions.* cochrane.org.
- Kitchener, B. & Charters, S. (2007). *Guidelines for Performing Systematic Literature Reviews in Software Engineering.* EBSE Technical Report EBSE-2007-01.
- Thomas, J. & Harden, A. (2008). "Methods for the Thematic Synthesis of Qualitative Research in Systematic Reviews." *BMC Medical Research Methodology*, 8:45.
- van de Schoot, R. et al. (2021). "An Open Source Machine Learning Framework for Efficient and Transparent Systematic Reviews" (ASReview). *Nature Machine Intelligence*, 3.
- Peters, M.D.J. et al. (2020). "Updated Methodological Guidance for the Conduct of Scoping Reviews." *JBI Evidence Synthesis*, 18(10).
