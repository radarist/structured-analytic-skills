---
name: Fidelity report — a skill misrepresents its method
about: A SKILL.md states something the published method does not say, or changes its labels, scale or step order
title: "fidelity: <skill> — <what is wrong>"
labels: fidelity
---

<!-- Fidelity reports are triaged first. A report without the offending line and the
     contradicting source cannot be triaged, so both fields below are required. -->

## Skill

`skills/<name>/SKILL.md` (add the section heading and line number if you have them)

## The offending line — required

Quote it verbatim, one to three lines:

> 

## The primary source that contradicts it — required

Author, year, title, venue, and a DOI, ISBN or URL. Quote the passage that contradicts
the line above — a summary is not enough, because the fix has to be written against the
source's own wording.

> 

## What the skill should say instead

Your proposed wording, in the method's own vocabulary. Do not "improve" a published
scale (NATO Admiralty A–F / 1–6, NASA TRL 1–9, Cochrane RoB 2 domains); report it as
the source prints it.

## Blast radius

- [ ] The companion tool under `scripts/` implements the same wrong definition
- [ ] `references/` repeats it
- [ ] Sibling skills cite this skill for the same claim
- [ ] Don't know
