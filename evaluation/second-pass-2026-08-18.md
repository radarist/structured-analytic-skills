# Second audit pass — 2026-08-18

A verification pass over the remediation claimed for the 2026-08-17 independent audit
(`independent-audit-2026-08-17.md`). Method: every principal finding behind a "Fix first" or
"Hold" verdict was re-checked against the current tree — the file opened, the tool run, the
cited source fetched where it was decisive. This pass is **verification, not a re-score against
the repo's own rubric**: no per-skill 1–5 rescoring was done, because scoring one's own
remediation is what the first audit existed to avoid. Where a finding reproduced, it was fixed
in this pass and re-verified (below, "re-opened → fixed").

## Result

- 8/8 release blockers verified closed (one needed a doc-level finish — see R2).
- 45 skills carried Fix-first/Hold findings; 35 verified closed as remediated.
- **10 findings re-opened by this pass and fixed the same day** (table below).
- 24 SHIP-verdict skills: spot-checked (companion tools, flagship claims, 5 citations) — held.
- All gates green at close: `make all` exit 0 (**4356/4356 checks**, library 100.0, trigger
  rank-1 100% / negatives held 100%, 365 cases), `build_index.py --check` exit 0,
  `claude plugin validate skills --strict` pass, `claude plugin validate
  .claude-plugin/marketplace.json --strict` pass, `agentskills validate` 69/69,
  36/36 tool self-tests byte-for-byte deterministic over two runs.

## Blockers, re-verified

| # | Blocker | Verdict | Evidence |
|---|---|---|---|
| B1 | RoB 2 (CC BY-NC-ND) relicensed MIT | CLOSED | `assess-study-bias/SKILL.md:15` carries a licence notice and deliberately omits the question wording; `rob2.py` keeps IDs/algorithms only and points to riskofbias.info |
| B2 | Wardley cheat sheet (CC BY-SA) | CLOSED | condensed table gone; `evolution-stage/SKILL.md:15,120` attribute the axis and stage names under CC BY-SA in place |
| B3 | AMSTAR 2 criteria from amstar.ca | CLOSED | stems kept with CC BY 4.0 attribution (`amstar2-review-appraisal/SKILL.md:145`); criteria grid restated (`references/items.md:3` "restated in this sheet's own words") |
| B4 | No notices file | CLOSED | `THIRD-PARTY-NOTICES.md` (7 sections); `LICENSE:23` carve-out |
| C1 | brier.py direction vs midpoint | CLOSED | `brier.py:188-193` compares observed to `mean_f`; 6×0.50/3-true reads `calibrated`; regression test (ten 0.70, seven true) at `:352-358`; selftest 15/15. The false Murphy identity print is also gone: `=` is printed only when `abs(residual) < 5e-5`, else the gap is shown |
| C2 | PRISMA flow missing two boxes | CLOSED | `--sought`/`--not-retrieved` at `prisma.py:236-241`; fourth identity at `:113-114`; the audit's failing case now passes all four checks; selftest 9/9 |
| C3 | citecheck FAILs SICI DOIs | CLOSED (docs finished in this pass, R2) | angle brackets accepted (`citecheck.py:86`); both Brier 1950 / Murphy 1973 DOIs PASS; error text attributes `\d{4,9}` to Crossref; `--delay` default 3.0 s; selftest 73/73 |
| R0 | Release mechanics (tree, CI, links) | CLOSED | tree fully tracked; ci.yml calls `agentskills validate` with no `continue-on-error`; zero `](../` escaping links; `write-srl-brief` renamed `write-sbar-brief`; all 69 `openai.yaml` free of mid-phrase truncation; v1.0.0 is identified as the first public tag and older work as pre-publication milestones |

## Re-opened by this pass → fixed (10)

| Finding at re-check | Fix |
|---|---|
| R1 `decision-matrix-mcda`: Saaty RI table provenance still undisclosed | SKILL.md step 3 now names Saaty 1980 and that re-simulations (Alonso & Lamata 2006) give lower RI values that can flip a borderline CR ≤ 0.10; reference entry added (doi:10.1142/S0218488506004114) |
| R2 `verify-citations`: tool fixed but docs taught the old rule | SKILL.md:46 now says the `10.NNNN/suffix` form is a Crossref convention and that ISO 26324 permits any Unicode graphic; worked-example error string matches `--demo` output; citecheck.py docstring de-scrambled and the stale `[^\s"<>]+` matcher text corrected |
| R3 `claim-provenance`: `[validated]` tag still pointed at an impossible filing (Workday FY2024 Q2 for a March 2024 acquisition) | tag corrected to Form 10-Q FY2025 Q1 (the quarter ended 2024-04-30 that contains it) |
| R4 `position-competitor`: still no small-n caveat on the orthogonality verdict | step 2 now treats the verdict as indicative under ~10 entities |
| R5 `assess-research-momentum`: S-curve example still spanned years with no literature (protein-diffusion from 2014) | worked example moved to CRISPR-based genetic screens, whose literature spans the plotted 2014–2024 window (counts remain illustrative) |
| R6 `estimate-market-size`: example still ran a 48 % cut labelled SOM against its own 1–10 % ceiling, then relabelled the tool output as TAM | the cascade now uses $120B global TAM → 48% geography-and-segment SAM ($57.6B) → 5% vendor SOM ($2.88B); the independent bottom-up estimate triangulates the SAM, not a relabelled output |
| R7 `pyramid-principle`: "written while Minto was at McKinsey" still unsupported (book 1987; she left in 1973) | reference entry now reads "the method comes from Minto's McKinsey years (she left in 1973)" |
| R8 `analyze-release-notes`: Keep a Changelog date wrong and version stale | verified against upstream CHANGELOG: 1.1.0 is **2019-02-15** (not "11 November 2019") and **2.0.0 shipped 2026-06-07**; skill now cites 2.0.0 and notes the six section types are unchanged |
| R9 `cynefin-classification`: rename still cited to a post that does not introduce it | fetched both posts: part 1 introduces both Obvious→Clear and Disorder→A/C; part 2 elaborates the A/C terminology. The reference now assigns those roles precisely |
| R10 `cross-impact-analysis`: still claimed MICMAC with no matrix powering | relabelled "direct-stage MICMAC" in frontmatter, body, output template and tool output; docstring and reference state that indirect influence (matrix powers) is not computed |
| — `scenario-planning` (strengthened) | Millett 2009 entry now discloses it argues *for* qualified use of probabilities and is cited for its documentation of Wack's stance |

## Fix-first / Hold findings verified closed as remediated (35)

wardley-map-drafting (critique-in-references intact, licence fixed under B2) · evidence-appraisal
(GRADE structure intact; Table 5.1 sentences now quoted and attributed, `grade.py:86-95`) ·
amstar2-review-appraisal (B3) · analyze-patent-claims (no US11234567B2/EP3456789B1 anywhere;
trigger and eval case gone) · premortem-analysis (30 % now Klein's HBR 2007 gloss;
Mitchell/Russo/Pennington 1989 described correctly) · estimative-language (D.6.e in all four
places; linter now emits an *info* advisory for "cannot rule out", 0 errors) ·
rate-source-admiralty (label provenance declared: AJP-2.1 labels, FM 2-22.3 wording) ·
bayesian-update (Jeffreys/Kass & Raftery scales distinguished, hybrid labelled) ·
chemistry-claim-check (example now flags rather than diagnoses: "the skill flags rather than
reconciles") · jtbd-framing (invented quote labelled; 12,000 consistent) · meta-analysis
(I² adjectives to Higgins, Thompson, Deeks & Altman 2003) · steep-pestle-analysis (example
declares its condensed scale; checklist enforces disclosure) · trend-analysis (Rogers' 16 %
boundary now restricted to cumulative series; flow series read as Fisher–Pry) ·
write-sbar-brief (renamed; index, README, siblings updated) · cheapest-experiment (cost
reconciles $95–130k vs $4.2M = 3.1 %; Superforecasting cited for a defensible claim) ·
futures-wheel (70 % valence and ring budget labelled the skill's own) · indicators-validation
(five qualities to Pherson & Pherson 2017; the Habits paper annotated as habits) ·
key-assumptions-check (Primer attributions scoped; house additions labelled) ·
smiles-sanity-check (`CS(C)C` and `CP(C)(C)C` now VALID; selftest covers the branch) ·
abstain-or-escalate (invented figures carry an unmissable illustrative label) ·
analysis-of-competing-hypotheses (Heuer's step 8 milestones restored; loose-ends pass labelled
as the skill's addition; template has a milestones field) · detect-funding-round (currency
kept as stated, `USD?` ambiguity marker, no silent conversion; ReDoS fixed per CHANGELOG) ·
steelman-argument (Dennett paraphrase faithful; endorsement test records "not yet run") ·
triangulate-sources (worked example now satisfies the four tests via a documented exception
written into `rationale`; counterfactual shows single-source) · cite-ieee (teaches `[1], [4]`;
`[1, 4]` flagged as locator-form; tool rewrites it) · red-team-claim (seven-vector instrument
declared the skill's own construction) · critique-report (origin honestly scoped: ~3 of 13
overlap, 11–13 route to siblings) · assess-study-bias (B1) · brier-score-calibration (C1) ·
systematic-review (C2) · detect-ma-event (terminated in status vocabulary with extraction
precedence; example is fictional with clean per-share/total separation) · apply-hype-cycle
(26 indicators declared the library's own; Gartner trademark notice in THIRD-PARTY-NOTICES §6) ·
value-intellectual-property (fabricated Accuride/Valencia valuation replaced by an explicitly
hypothetical example with an invented patent number) · evolution-stage (B2) ·
decision-matrix-mcda (R1 in this pass)

## SHIP-verdict spot checks (held)

- 36/36 companion tools: `--selftest` exit 0, two runs byte-identical.
- oss-project-health: CHAOSS metric names verbatim · reference-class-forecasting: Flyvbjerg
  uplifts (+40 %/+57 % rail), DfT P80 · sift-source-check: the two Wineburg & McGrew works
  correctly separated (SSRN 3048994) · delphi-method: 15 % approximation disclosed ·
  three-horizons: 70/20/10 defended in three places · foresight / decompose-research-question:
  "composite, not canonical" declarations intact · grounded-answer: CoVe metrics intact.
- 5 citations re-verified against primary sources in this pass: Keep a Changelog upstream
  CHANGELOG (drove R8), Cynefin St David's 2020 parts 1–2 (drove R9), Millett 2009 (annotation
  strengthened), Alonso & Lamata 2006 (added, R1), AMSTAR 2 BMJ/CC BY status (B3).

## Gates re-run at close of pass

```
make all                         exit 0   (check, score, trigger, index, metadata, eval-schema, exit-codes)
score_skills --min-score 95 --min-library 99
  Library 100.0 | mean 100.0 | median 100.0 | min 100.0 | hygiene 100.0 | checks 4356/4356
trigger_eval                     rank-1 100.0% | MRR 1.000 | negatives 100.0% | 365 cases
build_index.py --check           exit 0
build_openai_metadata.py --check OK: 69 current
eval_schema.py --check           OK: 69 canonical
exit_codes.py                    OK: 194 cases, 36 tools
claude plugin validate skills --strict                    pass
claude plugin validate .claude-plugin/marketplace.json    pass (strict)
agentskills validate (skills-ref, per skill)              69/69 pass
selftest determinism loop        36/36 byte-identical
```

One incident during the pass is worth recording: a frontmatter edit introduced a YAML parse
error that this repo's own line-based parser tolerated but `claude plugin validate --strict`
rejected (`analyze-release-notes` origin line, an unquoted colon). Fixed; both validators pass.
It is evidence the two-parser setup earns its keep.

## What this pass did not do

- No per-skill 1–5 rescoring against the external rubric — that needs a third, independent party.
- No new external link crawl; networked checks were limited to the decisive primary sources above.
- The 24 SHIP skills were sampled, not re-audited end to end.

## Publication-readiness review

A final review after the Kimi 3 and Fable 5 edits re-opened the wording of R6 and R9 once
more. The market example now preserves the tool's TAM→SAM→SOM semantics instead of relabelling
an output, and the Cynefin reference distinguishes the post that introduces both 2020 renames
from the follow-up that elaborates A/C. The release documentation now also distinguishes this
mechanical score from the much thinner behavioral evidence, marks the pre-publication report and original
audit as historical, preserves `methodologies/` as published research/provenance material, and
states the repository's issue-only maintenance policy consistently.

GitHub's repository-level pull-request feature is disabled while issues remain enabled. That
host setting makes a pull-request template and auto-close workflow unnecessary, so neither is
included in the publication tree. CI action dependencies are immutable commit pins to current
Node 24-based releases, and the irrelevant `setup-uv` dependency cache is disabled.

This review supports publication of the audited tree. It does **not** turn the deterministic
100.0 score into evidence that every model will produce high-quality analysis: the model-based
tests remain small, non-gated probes, and the 24 original SHIP skills remain spot-checked rather
than independently re-audited end to end.

The final publication candidate was re-verified after these edits: `make all` passed at
4356/4356; both Claude manifests passed strict validation; the Agent Skills reference validator
passed 69/69 skills; Python compilation, JSON/YAML parsing and `git diff --check` passed; Gitleaks
found no secret in the 5.14 MB working tree; and a best-effort crawl found no hard failure among
158 non-placeholder external URLs (the one crawler-hostile McKinsey page was opened and verified
separately). Repository-self links were excluded from that crawl because the destination was
still private and empty at verification time; internal relative links are covered by
`evaluation/check_repo.py`.
