---
name: Technology Roadmapping
category: foresight
origin: Motorola (late 1970s, Robert Galvin); codified by Robert Phaal, Clare Farrukh & David Probert (Cambridge IfM, 1990s–2000s)
agent_suitability: High
tags: [roadmap, technology-strategy, innovation, layers, s-curves, trl, planning]
related: [../foresight/backcasting.md, ../foresight/trend-analysis.md, ../foresight/horizon-scanning.md, ../agent-playbook.md]
---

# Technology Roadmapping

> **Essence:** A time-based, layered chart that aligns market/business drivers, products/services, and technologies on one page — answering "what must be true, by when, in the market, the product, and the technology, for our strategy to work?"

## Overview

A technology roadmap is a structured visual plan linking **why** (market and business drivers) to **what** (products and services) to **how** (technologies and R&D) across **when** (short / medium / long horizons). Each layer is a lane; time runs left to right; links between lanes show which technologies enable which products to capture which market opportunities — and, working backwards, which R&D must start now.

Roadmapping's value is as much *process* as artifact: building the chart forces marketing, product, and R&D into one conversation about timing and dependency, exposing gaps (a product promised before its enabling technology matures), orphans (technology with no market pull), and shared platforms across product lines. It is the firm-level workhorse that operationalizes normative futures work: where [backcasting.md](backcasting.md) yields societal milestones, roadmapping turns them into layered execution plans.

The canonical architecture (Phaal et al.) is a grid: **top layer** — market/business (drivers, trends, requirements); **middle layer** — product/service (features, generations, platforms); **bottom layer** — technology (components, R&D programmes, resources); all plotted over 2–3 time horizons, often annotated with milestones, gaps, and decision points.

## Origin & History

- **Late 1970s–80s — Motorola.** Robert Galvin championed roadmapping to coordinate technology and product planning; Motorola's published accounts (Willyard & McClees, 1987, "Motorola's Technology Roadmap Process", *Research Management*) seeded the practice.
- **1990s — industry consortia.** SEMATECH and the International Technology Roadmap for Semiconductors (ITRS, from 1992) made sector-level roadmapping famous, coordinating an entire industry's equipment and materials ecosystem around Moore's-law milestones.
- **1990s–2000s — codification at Cambridge.** Robert Phaal, Clare Farrukh and David Probert (Institute for Manufacturing) published the reference framework — "Technology Roadmapping: A Planning Framework for Evolution and Revolution" (*Technological Forecasting and Social Change*, 2004) — and the **T-Plan** "fast-start" workshop method that lets a firm build a first roadmap in ~4 facilitated workshops.
- **2000s–present:** integration with tech mining/bibliometrics (Porter & Cunningham, *Tech Mining*, 2005), TRLs (NASA/Mankins, 1995), portfolio methods, and digital tooling (Aha!, Roadmunk, SharpCloud, plain spreadsheets).

## Core Concepts & Key Terms

| Term | Definition |
|---|---|
| Layer / lane | One stratum of the chart: market, product, technology (plus variants: R&D, resources, standards). |
| Horizon | Time band: typically short (0–2y), medium (2–5y), long (5–15y); context-dependent. |
| Driver | A market/business force demanding response (customer need, regulation, competition). |
| Platform | A technology or product base shared across multiple offerings. |
| Milestone / node | A dated achievement on a lane (launch, demo, standard, TRL level). |
| Link / dependency | A connection across lanes: technology X enables product Y to serve driver Z. |
| Gap | A required node with no identified means to achieve it. |
| TRL (Technology Readiness Level) | NASA's 1–9 maturity scale, from basic principles to flight-proven. |
| S-curve | Technology performance vs effort: slow start, rapid improvement, maturity plateau; signals when to jump to a new curve. |
| T-Plan | Cambridge fast-start workshop process for building a first roadmap quickly. |
| Tech mining | Bibliometric analysis of patents/publications to chart technology emergence (feeds the technology lane). |

## When to Use / When Not to Use

**Use when:**
- Product and technology decisions must be synchronized across functions and years.
- You suspect misalignment (marketing promises vs R&D reality) and want it visible on one page.
- Sector coordination is needed (consortia, supply chains, standards).
- Translating a vision/backcast into an execution-level plan.

**Don't use when:**
- The environment shifts faster than the chart can be maintained and no one owns updates (roadmaps rot).
- The organization wants a *commitment schedule* disguised as strategy — roadmaps are planning hypotheses, not contracts.
- The question is which future will happen (use [scenario-planning.md](scenario-planning.md) upstream; roadmap per scenario or for robust strategies).
- A single small team with a 6-month horizon — overhead exceeds value.

## Process & Steps

T-Plan fast-start (Phaal et al.), adapted; four workshops plus pre/post work:

**Elapsed time and participants:** plan on 4–8 weeks end to end — four half-day workshops a week or two apart, plus 2–3 weeks of evidence gathering before and chart consolidation after. Participants are cross-functional by design (marketing, product, R&D, operations, strategy; 8–15 people); sector-level roadmaps stretch to months because the consensus rounds run across organizations.

0. **Pre-work:** scope (product-family / sector / firm), participants (cross-functional: marketing, product, R&D, operations, strategy), horizon, and evidence gathering (market trends, technology scouting — feed from [horizon-scanning.md](horizon-scanning.md), [trend-analysis.md](trend-analysis.md)).
1. **Workshop 1 — Market layer.** Drivers, trends, customer/business requirements, per horizon, prioritized. *Artifact: market lane.*
2. **Workshop 2 — Product layer.** Product/service concepts, feature generations, platforms mapped to drivers over time. *Artifact: product lane.*
3. **Workshop 3 — Technology layer.** Technologies, components, R&D programmes with maturity (TRL) estimates mapped to products over time. *Artifact: technology lane.*
4. **Workshop 4 — Linking & charting.** Draw cross-lane links, find gaps/orphans, place milestones and decision points, assign owners. *Artifact: integrated roadmap chart.*
5. **Ratify and maintain.** Management review; assign a roadmap owner; update on a fixed cadence (typically annually, or at trigger events). *Artifact: living roadmap + review calendar.*

For **sector-level** roadmaps (ITRS-style): add consensus-building rounds across organizations — essentially a [delphi-method.md](delphi-method.md) process per layer.

## Techniques, Tools & Deliverables

- **T-Plan facilitation packs** (Cambridge IfM publishes guidance).
- **S-curve analysis** (Foster, *Innovation: The Attacker's Advantage*, 1986) to time technology substitution.
- **TRL assessment** for the technology lane (Mankins, 1995).
- **Tech mining** (Porter & Cunningham, 2005): patent/publication trend analysis to populate and evidence the technology lane.
- **Gap/orphan analysis:** nodes lacking links in either direction.
- **Tools:** purpose-built (SharpCloud, ITONICS, Aha!) or slides/spreadsheets; the chart, not the tool, matters.
- **Deliverables:** the one-page layered chart (the icon of the method), gap register, decision-point list, linked R&D portfolio actions.

## Strengths & Limitations

| Strengths | Limitations |
|---|---|
| Single shared picture across silos | Rot: charts decay quickly without an owner and cadence |
| Exposes gaps, orphans, and timing impossibilities | False precision: neat bars hide deep uncertainty |
| Scales from product family to whole industry | Consensus versions can be conservative (lowest common denominator) |
| Directly actionable (R&D portfolio, dates, owners) | Process-heavy if scope is allowed to sprawl |
| Combines naturally with scenarios and backcasting | Layered-linear form underrepresents ecosystem/platform dynamics |

The documented misuse is precision theater: neat bars and dates make the roadmap read like a plan when every date is a judgment. The second trap is consensus drift — a workshop-built roadmap converges on the lowest common denominator and quietly deletes the bets that matter. And the form itself has a blind spot: layered linear maps underrepresent ecosystems and platforms, where value moves sideways between layers rather than forward through time. Keep the roadmap honest by marking every bar with its confidence and its kill condition, and re-baseline it on a fixed cadence; a roadmap that isn't re-baselined becomes a liability document.

## Worked Examples & Case Studies

- **ITRS (1992–2016):** the semiconductor industry's consensus roadmap coordinated equipment, materials, and design ecosystems worldwide around 2-year technology nodes — the most influential sector roadmap ever run; successor: IEEE IRDS.
- **Motorola (1980s):** Galvin's internal roadmaps aligned R&D with product generations, credited with improving technology-product synchronization; published by Willyard & McClees (1987).
- **National energy technology roadmaps:** the IEA publishes technology roadmaps (e.g., solar PV, hydrogen) that backcast deployment needs from climate scenarios — roadmapping at policy scale.

## Variants & Related Methodologies

- **Product roadmapping** (market+product lanes only) — common in software; lighter variant.
- **Science/sector roadmaps** (ITRS, IEA) — multi-organization consensus variant.
- **Agile/now-next-later roadmaps** — horizon bands replace dates in high-uncertainty software contexts.
- **Integrated s-curve/TRL roadmapping** — maturity-based variants.
- Related: [backcasting.md](backcasting.md) (upstream vision/milestones), [trend-analysis.md](trend-analysis.md) and [horizon-scanning.md](horizon-scanning.md) (lane evidence), [delphi-method.md](delphi-method.md) (consensus across organizations), [scenario-planning.md](scenario-planning.md) (roadmap per scenario).

## Agent Adaptation

### Suitability for agent execution

**High** for evidence assembly and chart drafting — populating lanes from market/technology research is a structured-gathering task agents do well, and tech mining (patent/publication trends) is scriptable. **Medium** for the linking and prioritization workshops, where cross-functional negotiation and commitment are human work. Best pattern: agents maintain a *living evidence base* per lane and regenerate draft charts; humans convene periodically to negotiate the actual plan.

### Recommended multi-agent workflow

| Role | Responsibility |
|---|---|
| Scout | Gather market drivers, competitor moves, regulations (market lane) and technology developments, TRL evidence, publications/patents (technology lane) — all sourced. |
| Analyst | Structure findings into lane tables per horizon; estimate maturities; draft cross-lane links; flag gaps/orphans. |
| Domain Expert (personas) | Challenge maturity estimates and timing (engineering, market, regulatory views). |
| Critic / Red Team | Attack false precision, missing dependencies, "hockey-stick" claims, single-source evidence. |
| Synthesizer | Render the layered chart (mermaid/table), gap register, decision-point list. |
| Verifier | Source-check all dated claims and TRL assertions. |
| Facilitator (human) | Owns priorities, commitments, and the cross-functional negotiation. |

### Agent pipeline

1. Frame (human) → scope, horizons, functions involved.
2. Gather (Scout ×2 tracks) → `market_evidence.json`, `tech_evidence.json` (sourced items with dates).
3. Analyze (Analyst) → lane tables + maturity estimates → `roadmap_draft.json` [layer, item, horizon, trl, links, source_ids].
4. Stress-test (Critic + Domain Experts) → flagged timing/maturity claims; Verifier source-check → graded roadmap.
5. Human workshop → negotiate priorities, dates, owners.
6. Report (Synthesizer) → chart + gap register + review calendar; Scout continues on a cadence for updates.

### Prompt templates

```text
SYSTEM: You are the Scout building the technology lane for a roadmap on "{{technology_domain}}".
Find technologies with credible development activity (publications, patents, funded programmes,
demonstrations). For each: name, what it enables, current maturity estimate (TRL 1-9 with
justification), key organizations, most recent milestone with date, source URLs. JSON array,
15+ items. Distinguish laboratory results from deployed systems rigorously.
```

```text
SYSTEM: You are the Analyst. Market lane items: {{market_items}}. Product lane: {{product_items}}.
Technology lane: {{tech_items}}. Draft the cross-lane links (technology -> product -> driver),
assign each node to a horizon ({{horizons}}), and list: (a) GAPS — nodes with no enabling
predecessor; (b) ORPHANS — technologies no product uses; (c) IMPOSSIBILITIES — nodes scheduled
before their dependencies mature. Output JSON with keys links, gaps, orphans, impossibilities.
```

```text
SYSTEM: You are the Critic reviewing this roadmap draft: {{roadmap}}. Attack the timing claims:
which milestones assume performance improvements faster than the technology's historical
s-curve? Which dates rest on a single vendor's announcement? Where is the chart over-precise
(a specific year for something at TRL 3)? Return a ranked list of the 10 least reliable nodes
with a recommended fix (widen the window, add evidence, or drop).
```

### Tools & data requirements

Web search + patent/publication sources (tech mining), retrieval over internal product/R&D plans, spreadsheet/JSON store as the single source of truth, diagramming (mermaid or roadmapping tools) for the chart.

### Quality checks, failure modes & mitigations

| Failure mode | Detection | Mitigation |
|---|---|---|
| Roadmap rot (stale evidence) | Items older than review cadence | Scout re-runs on schedule; stale items auto-flagged |
| False precision | Exact years on TRL≤3 items | Rule: uncertainty bands widen with immaturity; Critic enforces |
| Vendor-hype contamination | Single-source claims | Verifier requires ≥2 independent sources for dated milestones |
| Consensus flattening (human workshops) | No contested nodes | Critic presents the "dissenting roadmap" before ratification |
| Link spaghetti | Chart unreadable | Cap visible links; group by platform |

### Human-in-the-loop checkpoints

1. Scope and horizons (accountability).
2. Cross-functional workshop: priorities, commitments, owners.
3. Ratification and resource allocation (budget is human).

### Inputs & outputs (chaining contract)

**Inputs:** vision/milestones (from [backcasting.md](backcasting.md)); market and technology evidence (from [horizon-scanning.md](horizon-scanning.md), [trend-analysis.md](trend-analysis.md)); robust strategies (from [scenario-planning.md](scenario-planning.md)).
**Outputs:** layered roadmap chart, gap register, R&D portfolio actions, decision points, review calendar.

## References & Further Reading

- Phaal, R., Farrukh, C. & Probert, D. (2004). "Technology Roadmapping — A Planning Framework for Evolution and Revolution." *Technological Forecasting and Social Change*, 71(1–2).
- Phaal, R., Farrukh, C. & Probert, D. (2001). "T-Plan: The Fast-Start to Technology Roadmapping." Cambridge IfM.
- Willyard, C.H. & McClees, C.W. (1987). "Motorola's Technology Roadmap Process." *Research Management*, 30(5).
- Galvin, R. (1998). "Science Roadmaps." *Science*, 280(5365).
- Porter, A.L. & Cunningham, S.W. (2005). *Tech Mining: Exploiting New Technologies for Competitive Advantage.* Wiley.
- Mankins, J.C. (1995). *Technology Readiness Levels: A White Paper.* NASA.
- Foster, R. (1986). *Innovation: The Attacker's Advantage.* Summit Books. (S-curves)
