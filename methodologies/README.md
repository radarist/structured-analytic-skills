# Methodologies Library

A curated knowledge base of the top methodologies for **foresight**, **research**, and **scientific inquiry** — each documented in depth and adapted for execution by **AI agents** (multi-agent pipelines with roles, prompt templates, verification, and human-in-the-loop gates).

## Structure

```
methodologies/
├── _TEMPLATE.md                  # File conventions + shared agent vocabulary (read first)
├── README.md                     # This index
├── agent-playbook.md             # CAPSTONE: roles, orchestration patterns, pipeline recipes, rigor layer
├── foresight/                    # 12 methodologies for exploring & shaping futures
├── research-methods/             # 10 methodologies for generating knowledge
└── scientific-methods/           # 6 frameworks for reasoning & rigor
```

## How to use this library

1. **Start at [agent-playbook.md](agent-playbook.md)** — the role catalog (Scout, Analyst, Domain Expert, Critic/Red Team, Synthesizer, Verifier, Facilitator), orchestration patterns, three end-to-end pipeline recipes, the anti-hallucination rigor layer, and a goal→methodology selection matrix.
2. **Each methodology file** follows the same template ([_TEMPLATE.md](_TEMPLATE.md)): overview, origins, core concepts, when (not) to use, step-by-step process, strengths/limits, real cases — plus a full **Agent Adaptation** section (suitability rating, multi-agent workflow, pipeline, ready-to-use prompt templates, failure modes, human gates, input/output chaining contract).
3. **Files chain together**: each file declares its inputs and outputs so pipelines can be composed (see the three recipes in the playbook).

## Foresight (`foresight/`)

| File | Method | One-liner |
|---|---|---|
| [horizon-scanning.md](foresight/horizon-scanning.md) | Horizon Scanning | Continuous scanning for weak signals & emerging issues |
| [steep-pestle-analysis.md](foresight/steep-pestle-analysis.md) | STEEP/PESTLE | Coverage checklist for macro-environment drivers |
| [trend-analysis.md](foresight/trend-analysis.md) | Trend Analysis | Validate, quantify & project trends (TIA, S-curves) |
| [scenario-planning.md](foresight/scenario-planning.md) | Scenario Planning | Shell/GBN scenarios: plausible futures to stress-test strategy |
| [futures-wheel.md](foresight/futures-wheel.md) | Futures Wheel | First/second/third-order implication mapping |
| [delphi-method.md](foresight/delphi-method.md) | Delphi | Iterated anonymous expert panels → convergence (agent-native) |
| [cross-impact-analysis.md](foresight/cross-impact-analysis.md) | Cross-Impact / MICMAC | Interaction matrices, consistency, influence maps |
| [backcasting.md](foresight/backcasting.md) | Backcasting | From a desired future, backwards to today's actions |
| [three-horizons.md](foresight/three-horizons.md) | Three Horizons | H1/H2/H3 transition mapping for systemic change |
| [causal-layered-analysis.md](foresight/causal-layered-analysis.md) | CLA | Litany → system → worldview → myth/metaphor depth analysis |
| [futures-triangle.md](foresight/futures-triangle.md) | Futures Triangle | Push / pull / weight force-field diagnostic |
| [technology-roadmapping.md](foresight/technology-roadmapping.md) | Technology Roadmapping | Market–product–technology layers over time |

## Research Methods (`research-methods/`)

| File | Method | One-liner |
|---|---|---|
| [systematic-literature-review.md](research-methods/systematic-literature-review.md) | SLR & PRISMA | Reproducible evidence search/screen/synthesis (highly automatable) |
| [meta-analysis.md](research-methods/meta-analysis.md) | Meta-Analysis | Statistical pooling of effect sizes + bias assessment |
| [grounded-theory.md](research-methods/grounded-theory.md) | Grounded Theory | Build theory from data via coding & constant comparison |
| [case-study-research.md](research-methods/case-study-research.md) | Case Study (Yin/Eisenhardt) | In-depth bounded inquiry with chain of evidence |
| [ethnography.md](research-methods/ethnography.md) | Ethnography/Netnography | Thick description of cultures, incl. online communities |
| [action-research.md](research-methods/action-research.md) | Action Research | Plan-act-observe-reflect cycles with participants |
| [design-science-research.md](research-methods/design-science-research.md) | Design Science (DSR) | Build & evaluate artifacts as research (Hevner/Peffers) |
| [survey-research.md](research-methods/survey-research.md) | Survey Research | Valid measurement instruments + honest sampling |
| [mixed-methods.md](research-methods/mixed-methods.md) | Mixed Methods | Designed QUAL+QUAN integration (joint displays) |
| [experimental-design.md](research-methods/experimental-design.md) | Experiments & Quasi-Experiments | Randomization, controls, validity threats, A/B tests |

## Scientific Methods (`scientific-methods/`)

| File | Method | One-liner |
|---|---|---|
| [scientific-method-cycle.md](scientific-methods/scientific-method-cycle.md) | Scientific Method | The observe→hypothesize→test→revise loop |
| [hypothetico-deductive-method.md](scientific-methods/hypothetico-deductive-method.md) | Hypothetico-Deductive | Popper falsification, strong inference, crucial tests |
| [induction-abduction-analogy.md](scientific-methods/induction-abduction-analogy.md) | Induction/Abduction/Analogy | The generative logics of discovery |
| [bayesian-evidence-updating.md](scientific-methods/bayesian-evidence-updating.md) | Bayesian Updating | Priors × likelihood ratios → posteriors; calibration |
| [reproducibility-open-science.md](scientific-methods/reproducibility-open-science.md) | Reproducibility & Open Science | Preregistration, FAIR, replication — the integrity layer |
| [evidence-appraisal.md](scientific-methods/evidence-appraisal.md) | Evidence Appraisal | Hierarchies, CASP, Bradford Hill, GRADE certainty |

## Agent-readiness at a glance

- **Most agent-native:** Delphi (agents as expert panels), horizon scanning (Scout fleets), SLR (dual-screening automation), Bayesian updating (pure arithmetic + logs), futures wheel (implication generation).
- **Agent-strong with human gates:** scenario planning, backcasting, trend analysis, meta-analysis, evidence appraisal, cross-impact, roadmapping, DSR, H-D/strong inference.
- **Human-led, agent-supported:** grounded theory (agents code, humans theorize), case study, mixed methods, ethnography/netnography, CLA.
- **Least automatable:** action research (its substance is human relationships in a setting) — agents support documentation and analysis only.

## Provenance note

Files were written from established methodological literature (originators, key publications, and canonical references cited per file by author/year/title). URLs are included only where canonical and stable (e.g., prisma-statement.org, cos.io). Verify field-specific details against the cited primary sources before high-stakes use.
