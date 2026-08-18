# Analytic canon: coverage map and fidelity audit

Research date: 2026-08-16. Scope: the 59 v1 skills and 28 methodology files, checked
against primary sources on the web. Ten SKILL.md files were read in full for the fidelity
check; the rest were mapped by name and README one-liner.

## 1. Coverage against Heuer & Pherson, *Structured Analytic Techniques* (3rd ed., 2019; 66 techniques, six families)

| Family | Covered in v1 | High-value gaps |
|---|---|---|
| Getting organised (sorting, ranking/scoring, matrices, process maps) | — | weighted ranking/scoring |
| Exploration (structured brainstorming, nominal group, starbursting, mind maps) | partial (`futures-wheel`, `cross-impact-analysis`) | structured brainstorming, nominal group, starbursting |
| Diagnostic (KAC, chronologies, cross-impact matrix, multiple hypothesis generation, ACH, inconsistencies finder, deception detection, argument mapping) | `key-assumptions-check`, `analysis-of-competing-hypotheses`, `cross-impact-analysis`, `bayesian-update` | chronologies & timelines, argument mapping, deception detection, **quality of information check** |
| Reframing (outside-in, structured analogies, red hat, quadrant crunching, Delphi, what if?, HILP, premortem, structured self-critique, adversarial collaboration) | `delphi-method`, `premortem-analysis`, `steelman-argument`, `red-team-claim`, `critique-report`, `steep-pestle-analysis` (≈ outside-in) | **what if? / high-impact–low-probability**, red hat, structured analogies, quadrant crunching |
| Foresight (key drivers, reversing assumptions, simple scenarios, cone of plausibility, alternative futures, multiple scenarios generation, morphological analysis, counterfactual reasoning, indicators generation/validation/evaluation) | `scenario-planning`, `horizon-scanning`, `foresight`, `backcasting`, `causal-layered-analysis`, `trend-analysis` | **indicators + indicator validation**, **morphological analysis**, cone of plausibility, counterfactual reasoning |
| Decision support (opportunities incubator, bowtie, impact matrix, SWOT, critical path, decision trees, **decision matrix**, force field, pros-cons-faults-fixes) | none | **decision matrix / MCDA**, **decision trees / EV**, force field, SWOT, bowtie |

## 2. Standards for uncertainty and sourcing

ICD 203 (2015, amended 2022): sourcing quality ✔ (`rate-source-admiralty`,
`triangulate-sources`, `verify-citations`); information-vs-assumption-vs-judgment ✔
(`claim-provenance`, KAC); alternatives ✔ (ACH); argumentation ✔ (`pyramid-principle`);
**uncertainty expression ✗; confidence levels ✗** — v1 skills used inconsistent numeric
confidences (0–1 in KAC, 0–100 in `assess-study-bias`) with no shared lexicon. Standards to
encode: ICD 203's seven-term likelihood table and its rule that a confidence level and a
likelihood must not share a sentence; the UK PHIA Probability Yardstick (deliberate gaps
between bands); the IPCC AR5 guidance (Mastrandrea et al. 2010: likelihood terms;
confidence = evidence × agreement); ICD 206 source descriptors / source summary statements.

## 3. Forecasting and evidence-based practice

Brier + Murphy decomposition ✔; Bayes ✔; decomposition ✔; base rates partial;
**outside view / reference-class forecasting ✗** (Kahneman & Lovallo 1993; Flyvbjerg 2006);
log score ✗. GRADE ✔, RoB 2 ✔, PRISMA 2020 ✔ (with `prisma.py`), meta-analysis ✔;
ROBINS-I routed but not implemented; **AMSTAR 2 ✗** (Shea et al., BMJ 2017;358:j4008 — 16
items, 7 critical, deterministic overall rating); **QUADAS-2 ✗** (Whiting et al., Ann Intern
Med 2011;155:529–536 — 4 domains; relevant to diagnostic/AI-model claims).

## 4. Strategy and innovation

Wardley ✔, Porter ✔, JTBD ✔, Three Horizons ✔, hype cycle ✔, TRL ✔ (with fidelity issues,
below); S-curve/Rogers partial (`trend-analysis`, no Bass fit); Fermi partial; DoE partial.
Gaps: MRL/IRL/SRL, Blue Ocean canvas, Ansoff, real options, decision trees/EV, MCDA/AHP,
Kepner–Tregoe, Monte Carlo sensitivity, causal loop diagrams, morphological analysis, TRIZ.

## 5. Recommended additions (top ten, with script feasibility)

| # | Addition | Canonical source | Script? | Status after the expansion pass |
|---|---|---|---|---|
| 1 | Estimative language & confidence | ODNI ICD 203 (2015/2022); UK PHIA yardstick; Mastrandrea et al. IPCC AR5 guidance (2010); Kent (1964); ICD 206 | yes — p→term (3 standards), lint mixed sentences | **added** `estimative-language` |
| 2 | Reference-class forecasting / outside view | Kahneman & Lovallo, *Management Science* 39(1) 1993; Flyvbjerg, *PMJ* 37(3) 2006; Tetlock & Gardner 2015 | yes — percentile of inside estimate, uplift | **added** `reference-class-forecasting` |
| 3 | Indicators & indicator validation | Heuer & Pherson 3rd ed. (2019); *Tradecraft Primer* (2009) | yes — indicator × scenario diagnosticity | **added** `indicators-validation` |
| 4 | Decision matrix / MCDA with AHP consistency | Heuer & Pherson; Saaty (1980; *EJOR* 48(1) 1990); Keeney & Raiffa (1976) | yes — weighted sum, eigenvector, CR, sensitivity | **added** `decision-matrix-mcda` |
| 5 | Decision tree / expected value + EVPI + Monte Carlo sensitivity | Raiffa (1968); Howard (1966/1968); Clemen & Reilly (2014); Hubbard (2014) | yes | **added** `expected-value-decision-tree` |
| 6 | Real options for staged R&D | Luehrman, *HBR* (1998); Dixit & Pindyck (1994); Trigeorgis (1996) | yes — binomial lattice | deferred |
| 7 | Diffusion & S-curve fitting (Bass, Fisher–Pry) | Bass, *Mgmt Sci* 15(5) 1969; Fisher & Pry, *TFSC* 3 (1971); Rogers (2003) | yes | partly — logistic (Fisher–Pry) fit in `trend.py`; Bass deferred |
| 8 | MRL / IRL / SRL + software TRL | DoD MRL Deskbook (2020/22); Sauser et al. IRL/SRL; DoD TRA Guidebook (2025) | yes | deferred (software-TRL sources added to `score-technology-readiness`) |
| 9 | Morphological analysis / TRIZ | Zwicky (1969); Ritchey (2006/2011); Altshuller (1984) | yes — cross-consistency enumeration | **added** `morphological-analysis`; TRIZ deferred |
| 10 | Chronologies & timelines; argument mapping; quality-of-information check | Heuer & Pherson §7.2/§7.9; *Tradecraft Primer* (2009); Toulmin (1958) | partial | QIC **added** (`quality-of-information-check`); others deferred |

Runners-up: what-if? / high-impact–low-probability (**added** `high-impact-low-probability`),
AMSTAR-2 (**added** `amstar2-review-appraisal`), QUADAS-2, technology roadmapping skill,
causal loop diagrams, log-score option in `brier.py`.

## 6. Fidelity spot-check (ten skills read in full)

| Skill | Finding | Correction | Source |
|---|---|---|---|
| rate-source-admiralty | Credibility 3 misdefined ("possible but not logical" is grade 4's wording); other cells paraphrased | Standard wording restored in both tables | FM 2-22.3 App. B Tables B-1/B-2; STANAG 2511 (2003) |
| score-technology-readiness | TRL 6/7 wording shifted (operational vs relevant environment); NPR 7123.1C §6.5 cited (TRLs are App. E; 7123.1D is current); unverifiable "IEEE SysCon 2021" citation; "HRL" is not a NASA/DoD/EU scale | Wording fixed; NPR 7123.1D App. E; SEI CMU/SEI-2002-SR-027 and DoD TRA Guidebook (2025) Table 2-2; MRL/IRL/SRL | NASA NPR 7123.1D; H2020 Annex G; DoD TRA Guidebook (Feb 2025) |
| assess-study-bias | Overall rule incomplete ("High = at least one high domain"); description used RoB 1 vocabulary; Domain 2's two effects unmentioned | Table 1 rule incl. "several some-concerns" clause; RoB 2 domain names; assignment (ITT) effect stated | Sterne et al., BMJ 2019;366:l4898; Cochrane Handbook ch. 8 |
| evidence-appraisal | "Move at most one level per factor" (GRADE allows two); "never a randomised one" overstates | One or two levels; large effect +1/+2; rate-up "mostly" observational | GRADE Handbook Table 5.2/5.9; Guyatt et al. 2011 (guidelines 9) |
| brier-score-calibration | "Resolution (sharpness/discrimination)" conflates terms | Resolution (Murphy 1973) ≠ sharpness (property of forecasts alone) | Gneiting, Balabdaoui & Raftery, *JRSS-B* 69(2) 2007 |
| sift-source-check | Citation mixed SHEG working paper (2017) with the *TCR* article (2019) | Both cited correctly | SSRN 3048994; *TCR* 121(11) 2019, doi:10.1177/016146811912101102 |
| key-assumptions-check | Grid adaptation without mapping to canonical categories | Mapping to solid / correct-with-caveats / unsupported named | *Tradecraft Primer* (2009); Heuer & Pherson §7.1 |
| scenario-planning | Anti-pattern instructed weighting scenarios 40/30/20/10 — contradicts Shell/GBN doctrine; "Shell method" for the GBN 2×2 | Equally plausible, no probabilities; Shell/GBN tradition | Ogilvy & Schwartz, *Plotting Your Scenarios*; Millett, *JFS* 13(4) 2009 |
| three-horizons | 70/20/10 attributed to Baghai, Coley & White; time bands attributed to the book | Nagji & Tuff, *HBR* 2012; bands indicative | *The Alchemy of Growth* (1999); Nagji & Tuff (2012); Curry & Hodgson *JFS* 13(1) 2008 |
| cynefin-classification | Four domains only | Fifth domain (Disorder → Confused/Aporetic, 2020) added | Snowden & Boone, *HBR* 85(11) 2007; thecynefin.co (2020) |
| red-team-claim (aside) | "M. Tetlock" | P. E. Tetlock | Tetlock & Gardner (2015) |

## URLs consulted (selection)

en.wikipedia.org/wiki/Admiralty_code; redanalysis.org (FM 2-22.3 App. B copy);
nodis3.gsfc.nasa.gov (NPR 7123.1D App. E); ec.europa.eu H2020 Annex G;
cto.mil TRA Guide Feb 2025; sei.cmu.edu 2002 special report; cochrane.org handbook ch. 8;
riskofbias.info RoB 2; gdt.gradepro.org handbook; journals.ametsoc.org (Murphy 1973);
academic.oup.com JRSS-B (Gneiting et al. 2007); hapgood.us SIFT; journals.sagepub.com TCR
2019; papers.ssrn.com 3048994; sagepub.com SAT 3rd ed. sample chapter; cia.gov Tradecraft
Primer 2009; irp.fas.org ICD 206; gov.uk explaining-uncertainty-in-uk-intelligence-
assessment; pubsonline.informs.org (Kahneman & Lovallo 1993); journals.sagepub.com PMJ
(Flyvbjerg 2006); pubmed 28935701 (AMSTAR 2); acpjournals QUADAS-2; adaptknowledge.com GBN
Plotting Your Scenarios; jfsdigital.org (Millett 2009); hbr.org 2012 innovation portfolio;
pubmed 18159787 (Snowden & Boone); thecynefin.co 2020; dodmrl.com deskbook.
