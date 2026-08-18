# Critique Report — full point criteria

Companion reference for `../SKILL.md`. Each point carries three verdicts: **pass ✅**,
**fix ⚠️** (revise before shipping), **block 🔴** (do not ship until rewritten).

## The ten base points

### 1. Does it answer the question that was asked?

- **Pass** — the original question is restated in the introduction or summary, and the document delivers a specific answer to *that* question.
- **Fix** — the question is implicit, or the answer is hedged into vagueness.
- **Block** — the document answers an adjacent question (the one that was easier to research).

### 2. Is the evidence sourced?

- **Pass** — every non-trivial factual claim carries a citation, and every citation resolves to an entry in the reference list.
- **Fix** — a few uncited claims, all trivially verifiable.
- **Block** — load-bearing claims are uncited, or citations do not resolve. Run `verify-citations` for identifier-level checking and `grounded-fact-check` for the specifics.

### 3. Are the format's anti-patterns avoided?

Check against the anti-patterns of the document type actually being written:

| Format | Characteristic anti-pattern |
| --- | --- |
| IMRAD | Interpretation in Results (it belongs in Discussion) |
| SBAR brief | Editorialising in Situation (it belongs in Assessment) |
| Systematic review | A hidden exclusion list — studies dropped without a recorded reason |
| Market or technology brief | Verdicts without a stated axis ("clear leader" on no named measure) |
| Forecast | A point estimate with no interval and no resolution date |

- **Pass** — none detected. **Fix** — one localised instance. **Block** — the anti-pattern is systematic.

### 4. Is the method reproducible?

The methods section (or its equivalent) must name which sources were queried, which queries ran, and which inclusion or exclusion rules applied.

- **Pass** — another analyst could re-derive the result from the same sources.
- **Fix** — methods mentioned but too vague to repeat.
- **Block** — no method disclosed; results appear as assertions.

### 5. Is confidence honest?

Every recommendation and headline claim carries a stated confidence, and the level matches the evidence behind it: corroborated high-grade sources support a high level; a single mid-grade source supports a moderate one; an uncorroborated claim cannot support more than a low one. Grades come from `rate-source-admiralty`; for bodies of studies, from `evidence-appraisal`.

- **Pass** — stated confidence matches the evidence grade for every headline claim.
- **Fix** — over- or under-stated on some claims.
- **Block** — no confidence stated, or confidence is inflated relative to the evidence.

### 6. Are limitations stated?

- **Pass** — an explicit limitations section naming at least three: what was not covered, which assumptions are load-bearing, what would change the conclusion.
- **Fix** — limitations implicit, or only one or two named.
- **Block** — none; the document reads as complete.

### 7. Is the audience calibrated?

Jargon level, length, and the authority level the recommendations assume must match the reader.

- **Pass** — voice, density, and length fit the audience. **Fix** — some sections mis-pitched. **Block** — wrong format for the reader entirely.

### 8. Have counter-evidence and dissent been addressed?

- **Pass** — the strongest disconfirming evidence is named and engaged, and the runner-up interpretation is stated.
- **Fix** — counter-evidence mentioned but not engaged.
- **Block** — one-sided. Where the document rests on `analysis-of-competing-hypotheses`, check that the runner-up hypothesis is named; otherwise run `red-team-claim` to surface what is missing.

### 9. Are the numbers defensible?

Every quantitative claim needs units, a measurement date, a baseline for any comparison, and a stated method for any computed figure.

- **Pass** — all four present, and computed figures reproduce. **Fix** — some numbers missing one element. **Block** — headline numbers unsourced or unrecomputable. Use `quantitative-sanity-check` and `test-significance` where numbers carry the argument.

### 10. Is the next action actionable?

- **Pass** — concrete next steps with an owner and a date. **Fix** — vague "should look into X". **Block** — no call to action at all.

## The conditional points

These apply only when the document's structure invokes them. When the condition is not met,
record `N/A — <reason>` and move on; forcing them onto a document that does not need them is
its own failure mode.

### 11. Job-to-be-done framing per technology

**Applies when** the document names three or more distinct technologies, vendors, or products **and** is a comparison, landscape, ecosystem, or buy-versus-build analysis (not a single-technology profile or a narrative forecast).

- **Pass** — each named technology has a verb-led job statement (minimise / maximise / reduce / accelerate the metric, plus object and context), two to four competing solutions including non-consumption, and a struggling moment in the customer's words.
- **Fix** — some technologies framed, others not; or the job statement is written as a solution rather than an outcome.
- **Block** — three or more technologies with no job framing at all: peer comparison without the underlying job is tautological. Run `jtbd-framing` on each before re-reviewing.

### 12. Evolution-stage placement per technology

**Applies when** the document names three or more technologies **and** makes any maturity or method claim (adopt/pilot/build/buy, "this category is mature", a readiness level).

- **Pass** — each technology carries an evolution-stage tag (genesis / custom-built / product / commodity) with a one-line rationale anchored in observable evidence: number of customer references, integration time, breaking-change history — not vendor self-positioning.
- **Fix** — partial placement, or rationales resting on vendor claims.
- **Block** — maturity claims with no placement at all. Run `evolution-stage` on each before re-reviewing.

### 13. Horizon tag per bet

**Applies when** the document proposes three or more distinct bets, recommendations, or investments spanning more than one time horizon.

- **Pass** — every bet carries a horizon tag (H1 0–12 months, H2 1–3 years, H3 3–5 years), a time-to-impact estimate, and the evidence bar that follows from it: hard return for H1, innovation accounting for H2, weak-signal monitoring for H3.
- **Fix** — partial tagging, or the wrong bar applied (an H1 return threshold used to kill an H3 option).
- **Block** — three or more untagged bets: portfolio balance cannot be assessed. Run `three-horizons` before re-reviewing.
