# Methodology File Template & Writing Standards

Every methodology document in this library MUST follow this template. The library is
designed to be consumed by AI agents, so structure, cross-links, and the Agent
Adaptation section are mandatory and must be practical (copy-paste ready), not vague.

## File naming & location

- Path: `methodologies/<category>/<kebab-case-name>.md`
- Categories: `foresight/`, `research-methods/`, `scientific-methods/`
- One methodology per file.

## YAML frontmatter (required, first thing in the file)

```yaml
---
name: <Methodology Name>
category: foresight | research-method | scientific-method
origin: "Olaf Helmer & Norman Dalkey (RAND), 1950s"
agent_suitability: High | Medium | Low
tags: [<5-10 lowercase tags>]
related: [<relative paths to sibling files, e.g. ../foresight/delphi-method.md>]
---
```

Quote free-text scalar values such as `origin` with double quotes. This is required
when a value contains a colon followed by a space (`: `), which YAML otherwise
interprets as the start of another mapping.

## Section order (all sections required, in this order)

1. `# <Methodology Name>` followed by a `> **Essence:**` one-line blockquote.
2. `## Overview` — what it is, what problem it solves, 2-3 paragraphs.
3. `## Origin & History` — founders, key publications with years, how it evolved. Fact-check names and dates.
4. `## Core Concepts & Key Terms` — glossary table (Term | Definition).
5. `## When to Use / When Not to Use` — two bullet lists; be concrete about contexts, scale, time horizons, data needs.
6. `## Process & Steps` — numbered, detailed steps; include participants, timeframes, materials/inputs, and the artifact produced at each step.
7. `## Techniques, Tools & Deliverables` — supporting techniques, software/canvases, and the concrete deliverables.
8. `## Strengths & Limitations` — a table (Strengths | Limitations) plus short commentary.
9. `## Worked Examples & Case Studies` — 1-3 real, documented applications (name the organization/project and outcome).
10. `## Variants & Related Methodologies` — variants of the method; cross-link siblings via relative paths.
11. `## Agent Adaptation` — see below (mandatory, substantial).
12. `## References & Further Reading` — canonical books/papers (author, year, title) and links ONLY if verified or unquestionably canonical (official sites, DOIs, well-known orgs). Never invent a URL.

## Agent Adaptation section (mandatory subsections)

### Suitability for agent execution
Rating (High/Medium/Low) and a candid rationale: which steps agents do well, which need humans.

### Recommended multi-agent workflow
A table mapping the shared roles (below) to responsibilities in this methodology.

### Agent pipeline
Numbered pipeline mapping methodology steps -> assigned agent role -> input -> output artifact,
so outputs can be passed between agents and chained with other methodology files.

### Prompt templates
2-4 ready-to-use prompts in fenced code blocks (system and/or user prompts), with
`{{placeholders}}` for variables. They must be concrete and immediately usable.

### Tools & data requirements
What the agents need: web search, document retrieval/RAG, code execution, spreadsheets, etc.

### Quality checks, failure modes & mitigations
A table (Failure mode | Detection | Mitigation). Include hallucination, groupthink,
sycophancy, bias amplification, citation fabrication where relevant.

### Human-in-the-loop checkpoints
Where a human must review, decide, or supply judgment, and why.

### Inputs & outputs (chaining contract)
Bulleted `Inputs:` and `Outputs:` so this file can be wired into multi-methodology pipelines.

## Shared agent vocabulary (use these exact roles in every file)

| Role | Function |
|---|---|
| **Scout** | Wide gathering via web search/sources; returns raw material with source URLs. |
| **Analyst** | Structures, classifies, codes, and extracts patterns from gathered material. |
| **Domain Expert** | Persona-prompted specialist providing expert judgment (e.g., Delphi panelist). |
| **Critic / Red Team** | Challenges assumptions, hunts bias and weak signals, tries to falsify conclusions. |
| **Synthesizer** | Integrates material into coherent deliverables (scenarios, reports, taxonomies). |
| **Verifier** | Fact-checks claims against sources, validates citations and numbers. |
| **Facilitator** | Orchestrates rounds, gates, and convergence; human where accountability is needed. |

Standard pipeline stages: **Frame -> Gather -> Analyze -> Synthesize -> Stress-test -> Report**.

## Writing standards

- English, Markdown, tables for comparisons, fenced blocks for prompts/diagrams.
- Comprehensive but no filler: target ~2,000-3,000 words per methodology file (the
  library's files run ~1,900-2,600 words; line counts depend on wrapping and are not a
  useful target).
- Fact-check originator names, dates, and publication titles via web search before writing.
- No fabricated citations, page numbers, or URLs. If a link cannot be verified, cite the work by author/year/title only.
- Be candid in Limitations and failure modes; do not oversell agent automation.
- Cross-link related methodology files with relative paths.
