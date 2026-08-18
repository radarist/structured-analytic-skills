# Placement signals — eight observable questions for the evolution axis

The axis has four stages, in this order: **Genesis**, **Custom-built**, **Product (including rental)**
and **Commodity (including utility)**. Components travel one way along it — left to right — as more
people use them and as what they do becomes better defined. A component that seems to have moved
back to the left was almost certainly placed wrongly the first time.

This page is the repository's own placement instrument. Every question below asks about something
countable, timeable or lookup-able; none of them asks how new or clever the component feels, because
that is the judgement teams get wrong about their own work. Answer as many questions as the evidence
supports, then read the column where most answers land.

## The eight questions

| # | Ask | Genesis | Custom-built | Product (+rental) | Commodity (+utility) |
|---|---|---|---|---|---|
| 1 | How many independent suppliers will sell it to you today? | none — nobody sells this yet | none; every instance so far was built to order | several, competing for the same buyers | many, and buyers hardly tell them apart |
| 2 | What does replacing the supplier or implementation cost? | nothing exists to replace it with | a rewrite: months of work, little carries over | a migration with documented steps and a quotable price | a change of billing account, measured in hours |
| 3 | How is it paid for? | out of a research or experiment budget | a statement of work priced per engagement | a licence or subscription with a published rate card | metered consumption on a per-unit tariff |
| 4 | How long until it runs in a new environment? | unknown; nobody has completed it twice | months, and the estimate is redone per environment | weeks, following the supplier's documented path | hours; there is nothing to integrate |
| 5 | What public artefacts exist about it? | talks, preprints, one or two write-ups | write-ups of individual builds, no shared package | product documentation, reference architectures, a change log | published standards, conformance tests, interchangeable specs |
| 6 | Who is able to operate it? | only the people who built it | a small bench who have done a comparable build | a hiring market with courses and certifications | ordinary operations staff; no specialist hire |
| 7 | Do two informed people describe the same scope for it? | no; the definition shifts between conversations | roughly, but each build draws its own boundary | yes — arguments are about features, not scope | yes; the scope is written down somewhere neutral |
| 8 | What does a failure in it mean? | a result — the experiment ran | a setback the plan already allows for | a support ticket against a service commitment | a contractual breach, occasionally newsworthy |

## Reading the answers

- **Count, do not average.** Pick the column holding most of the answers you could evidence. A
  placement resting on one answer is an estimate; say so.
- **Questions 1 and 2 carry the most weight.** Supply and switching cost are hard to fake. When they
  disagree with the softer questions, follow them: a "platform" with one supplier and a rewrite-sized
  exit is Custom-built however it is sold.
- **Vendor positioning answers none of these questions.** A rate card, a documented migration path and
  a named third party who has done the migration do.
- **Split answers mean transition.** If answers divide evenly between two adjacent columns, label the
  component transitional ("Custom-to-Product") and plan with the left-hand stage's way of working;
  that is the one that governs the cost.
- **Judge the market, not the room.** Question 1 asks who will sell it to you, not whether your team
  has built it before.

## What each stage implies for the way of working

Matching the method to the stage is the point of placing the component at all: the same delivery
process cannot serve a component nobody has finished building and one that arrives as a metered
utility.

| Stage | Way of working | Budget and schedule consequence |
|---|---|---|
| Genesis | Time-boxed experiments with an explicit kill criterion | High failure rate; assume the first build is thrown away |
| Custom-built | Lean delivery borrowing the closest comparable build | Multi-month integration, re-tuned per environment |
| Product (+rental) | Adoption along the supplier's documented path and roadmap | Short integration while you stay on the reference architecture |
| Commodity (+utility) | Buy on price and reliability; leave it alone | No integration budget; switching cost is the risk to watch |

The failure this table exists to prevent is one delivery method applied across a whole value chain —
running a discovery experiment against a metered utility, or budgeting two weeks for a bespoke build
that will take twenty.

## Attribution and licence

The evolution axis and its four stage names are Simon Wardley's. Primary source: Simon Wardley,
"Finding a Path", chapter 2 of *Wardley Maps*, Medium, 2016 —
https://medium.com/wardleymaps/finding-a-path-cdb1249078c0 — which the author publishes under the
Creative Commons Attribution-ShareAlike 4.0 International licence (CC BY-SA 4.0),
https://creativecommons.org/licenses/by-sa/4.0/. Read the chapter for Wardley's own account of the
axis and his own table of stage characteristics.

The eight questions, the tables and all wording on this page were written for this repository from
observable market evidence. They are not a copy, condensation or adaptation of Wardley's text, and
they carry the repository's MIT licence; the stage names and their order are plain facts about the
model, not protected expression.
