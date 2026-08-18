---
name: steelman-argument
description: "Reconstructs an opposing argument at its strongest, in its proponents' own terms and to the standard they would endorse, then names where even that version is exposed — so any rebuttal lands on the real position rather than a caricature. Use before refuting or dismissing a view: \"steelman this argument\", \"what is the strongest case for the other side?\", \"is this a strawman?\", \"ideological Turing test\". Not for attacking one's own conclusion (use `red-team-claim`) or for verifying a single factual claim (use `grounded-fact-check`)."
license: MIT
metadata:
  category: evidence-verification
  method: Steelmanning (Rapoport's rules; ideological Turing test)
  origin: A. Rapoport's rules as stated by D. C. Dennett, 2013; B. Caplan, 2011 (ideological Turing test)
  version: "2.0.0"
---
# Steelman an Argument

A steelman is the opposite of a strawman: instead of the weakest version of an opposing view, it builds the version hardest to knock down — and engages *that*. Dennett (2013) sets out the rules of respectful criticism he credits to Anatol Rapoport: re-express the target's position so clearly and fairly that the target says "Thanks, I wish I'd thought of putting it that way"; list the points of agreement; say what has been learned from it; and only then offer a word of rebuttal. Caplan's ideological Turing test (2011) supplies the pass mark — a reconstruction genuine proponents could not tell came from an opponent. It prevents the satisfying refutation of a position nobody holds, which leaves the real disagreement untouched.

## When to invoke

Invoke when:

- A rebuttal or "here's why they're wrong" section is about to be written: "steelman this argument", "strongest case for the other side".
- A position is described in language its holders would reject: "is this a strawman?", "the charitable reading of {view}".
- A recommendation depends on the opposing school being wrong, and its best case is unstated.
- Two camps are talking past each other and each needs the other's argument reconstructed faithfully.

Do NOT invoke when:

- The task is attacking one's own conclusion — use `red-team-claim`; steelman first.
- A single factual claim needs checking — use `grounded-fact-check`; this is for positions, not facts.
- Rival explanations of the same evidence need ranking — use `analysis-of-competing-hypotheses`.
- The question has one correct answer and no genuine opposing school: nothing to steelman.

## Procedure

### 1 — Name the position in its proponents' own words

State the opposing view in one sentence using the terms its advocates use, not a relabelled version. If it can only be described dismissively ("they just think…"), it is not yet understood — read what its actual proponents write. A hostile summary yields a parody; use `sift-source-check` to reach the source material first.

### 2 — Build the strongest case inside their frame

Assemble the argument as its best advocates would: the core claim; the values it rests on; its strongest evidence, cited at its best rather than its weakest instance; its best answer to the obvious objection; and the genuine insight at the centre — the true observation even a rejected view usually contains. Import no outside premise; a steelman stands on the opponent's own terms.

### 3 — Apply Rapoport's rules

Re-express the position so clearly and fairly that a proponent would say "Thanks, I wish I'd thought of putting it that way". Then list the points of agreement, especially those outside general consensus, and state what the reconstruction has learned from the position. Only after all three is rebuttal permitted; jumping to the fourth move is the strawman habit renamed.

### 4 — Locate where the strong version is still exposed

A steelman is not admiration: it marks the load-bearing assumption whose failure would weaken this best version most, and the evidence whose overturning would collapse it. Naming these separates a steelman from advocacy.

### 5 — Run the endorsement test

Ask whether a genuine advocate would recognise this as their position, fairly stated, checking against a real proponent or text where one exists. "Yes, exactly" is a pass; "still missing the point" is the signal to iterate — that feedback is the product. Record which verdict the reconstruction actually earned.

### 6 — Only now engage

With the steelman passing, state where the strong version still fails: which assumption is contested, which evidence is thought not to hold, what would change the verdict. A rebuttal aimed at the steelman is the only kind worth making, and it is now specific enough to test.

## Output template

```
## Steelman — {opposing position}

**Position (their terms):** {one sentence in the proponents' own language}

**Strongest case, in their frame:**
- Core claim: {…}
- Values and premises it rests on: {…}
- Strongest evidence: {…, cited at its best}
- Best answer to the obvious objection: {…}
- Genuine insight at the centre: {…}

**Rapoport check:** re-expressed {yes/no} · agreements: {…} · learned: {…}

**Where the strong version is exposed:**
- Load-bearing assumption: {…} — if false, {consequence}
- Pivotal evidence: {…} — if overturned, {consequence}

**Endorsement test:** {passes — a proponent signed it | not run — what it needs | fails — still caricaturing {point}}

**Engagement:** {which assumption or evidence is contested, and why}
```

Mandatory fields: the position in their terms, all five elements of the case, the exposure pair, and the endorsement verdict. A steelman naming no genuine insight and no exposure has not been done.

## Worked example

Position to steelman (illustrative): *"We should train and host our own model in-house rather than rent API access."* The reviewer's own view is the opposite — which is why the reconstruction runs first.

```
## Steelman — "train and host our own model in-house"

**Position (their terms):** Owning the model is the only way to own the product; API dependency
is strategic tenancy, not ownership.

**Strongest case, in their frame:**
- Core claim: an owned model compounds — every one of the 40M internal support tickets improves
  an asset on the balance sheet, while the $2.4M annual API spend rents someone else's.
- Values and premises: differentiation lives in the model layer; unit-cost control matters at
  scale; vendor roadmaps can turn (3 price changes and 2 deprecations in the last 18 months).
- Strongest evidence: fine-tuning on domain data beat prompting by 11 points on the internal
  ticket-routing eval; at 400M tokens/day, owned inference undercuts list API pricing.
- Best answer to the obvious objection ("frontier training is unaffordable"): frontier is not
  required — a 7-30B open-weight model on domain data beats a generalist API on this workflow at
  roughly 1/100th the entry cost.
- Genuine insight at the centre: if the model is the product surface, outsourcing it outsources
  the rate at which the product differentiates.

**Rapoport check:** re-expressed yes · agreements: vendor roadmap risk is real, unit economics do
invert at high volume · learned: the 11-point eval gap was not in the original analysis.

**Where the strong version is exposed:**
- Load-bearing assumption: differentiation lives in the model layer rather than in workflow and
  data distribution — if false, ownership is pure cost.
- Pivotal evidence: the 11-point eval gap — if a blind rerun on 2026 API models closes it, the
  case collapses.

**Endorsement test:** not yet run — no proponent has reviewed this reconstruction. Running it
means showing the block to a CTO who has made this bet and recording whether they would sign it
unchanged; the engagement below is provisional until it is.

**Engagement:** the load-bearing assumption is contested: differentiation here is workflow
integration, not model quality. The blind rerun, not the strategy deck, should decide.
```

## Verification

- [ ] Every element of the case is in the proponents' vocabulary; no outside premise was imported to make it work.
- [ ] The reconstruction names a genuine insight — finding nothing true in the position means it was not understood.
- [ ] Rapoport's first three moves (re-expression, agreements, what was learned) all appear *before* any rebuttal.
- [ ] The endorsement test records a real verdict against a proponent or representative text, not an assumed pass.
- [ ] The exposure pair is specific: a named assumption and a named piece of evidence, each with the consequence of its failure.
- [ ] The engagement attacks the steelman, not the original weak version.

## Pair with adjacent skills

- `red-team-claim` — steelman the opposing case, then red-team one's own; doing only the second is where shallow rebuttals come from.
- `sift-source-check` — find the genuine proponents; never steelman a hostile summary.
- `analysis-of-competing-hypotheses` — the same charity applied to all rival explanations at once.
- `key-assumptions-check` — step 4's exposure pair is a targeted assumptions audit of the reconstructed case.
- `critique-report` — a self-review whose alternative position was never steelmanned has not earned its confidence.

## Anti-patterns

- Do **not** build a version the opponent would disown; that is a strawman in better clothing.
- Do **not** smuggle in outside premises. A steelman must be strong on the opponent's terms.
- Do **not** skip the genuine insight; finding nothing true in a widely held view indicates a bad reconstruction.
- Do **not** confuse steelmanning with conceding. The strong version permits sharper disagreement, not agreement.
- Do **not** stop at "one could see how someone might think that"; that is empathy, not a reconstruction.
- Do **not** rebut before Rapoport's first three moves are complete.

## Reference

- D. C. Dennett, *Intuition Pumps and Other Tools for Thinking*. W. W. Norton, 2013 — "Rapoport's Rules", the four-move discipline of respectful criticism, credited to Anatol Rapoport. ISBN 9780393082067
- B. Caplan, "The Ideological Turing Test," EconLog, Library of Economics and Liberty, 20 June 2011 — the operational pass mark: stating opposing views as clearly and persuasively as their proponents. https://www.econlib.org/archives/2011/06/the_ideological.html
- D. Davidson, "Radical Interpretation," *Dialectica*, vol. 27, no. 3–4, pp. 313–328, 1973. doi:10.1111/j.1746-8361.1973.tb00623.x — the principle of charity in interpretation, the philosophical root of the practice.
- D. Walton, *Fundamentals of Critical Argumentation*. Cambridge University Press, 2006 — the strawman fallacy and the argumentation-scheme tradition distinguishing fair reconstruction from caricature.
- J. Galef, *The Scout Mindset: Why Some People See Things Clearly and Others Don't*. Portfolio, 2021. ISBN 9780735217553 — the scout-versus-soldier framing that makes charitable reconstruction a truth-seeking habit rather than a courtesy.
