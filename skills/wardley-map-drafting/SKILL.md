---
name: wardley-map-drafting
description: "Draws a Wardley map — anchor on the user need, chain the components that deliver it by visibility, plot each on the evolution axis from genesis to commodity, then read the map for build, buy and consume-as-utility calls. Use when a strategy argument needs a picture of the whole dependency chain — \"map the value chain for this product\", \"draw a Wardley map\", \"where should the team build versus buy?\", \"why does this architecture keep reinventing infrastructure?\". Not for scoring one component's maturity in isolation (use `evolution-stage`) or for plotting rival firms (use `position-competitor`)."
license: MIT
metadata:
  category: decision-strategy
  method: Wardley mapping
  origin: Simon Wardley, 2005–2016 (Wardley Maps, CC BY-SA 4.0)
  version: "2.0.0"
---
# Wardley Map Drafting

A Wardley map plots the chain of components meeting a user need against how evolved each is, so strategy is argued over a picture rather than in the abstract. Simon Wardley developed the technique from 2005 and published it as *Wardley Maps* (Medium, 2016): components sit on a value chain anchored at the user need — "the higher up the map a component is then the more visible it becomes to the user" (Wardley, "Finding a Path", ch. 2) — and on an evolution axis running genesis → custom-built → product (including rental) → commodity (including utility). The quotation, the axis and the stage names are Wardley's, published under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/); the rest of this skill is the repository's own wording, MIT-licensed. Its core principle: components evolve rightwards, so method and the build/buy/consume choice depend on where a component sits *now*. It prevents building what the market already sells as a utility, or industrialising something still being invented.

## When to invoke

Invoke when:

- A build-versus-buy or outsourcing decision spans several dependent components and the argument circles.
- An architecture or roadmap review needs the whole dependency chain visible.
- The discussion is about capabilities with no reference to their maturity or the user.

Do NOT invoke when:

- One component's maturity is all that is needed — `evolution-stage` for a single stage judgement, `score-technology-readiness` for empirical readiness.
- The subject is rival firms on a competitive landscape — use `position-competitor`; industry-level profitability — `five-forces-analysis`.
- The question is portfolio timing across horizons — use `three-horizons`.
- The user need itself is unclear — establish it with `jtbd-framing` before mapping.

## Procedure — anchor, chain, evolve, read, decide

### 1 — Anchor on the user need

Write one sentence naming the user and what they need; that anchor sits at the top. "An on-call engineer needs to be alerted within 60 seconds of a production incident" is an anchor; "observability platform" is an inventory. Doctrine begins with *focus on user needs* — everything below exists only to serve it.

### 2 — Build the value chain by visibility

From the need, ask repeatedly "what does that require?", placing each component below the one it serves. The y-axis is visibility: the need at the top, components the user never thinks about at the bottom. Continue until reaching things consumed raw. Paging chains alerting rules → metrics pipeline → time-series storage → compute → power; the user perceives being paged and nothing below.

### 3 — Plot each component on the evolution axis

Place every component left to right by what the market will sell you: **genesis** — no supplier offers it and informed people disagree about its scope; **custom-built** — a few made-to-order instances, and leaving one means a rewrite; **product including rental** — competing suppliers with published prices, documentation and roadmaps; **commodity including utility** — interchangeable supply billed by consumption, differing only on price and reliability. Judge by the market's state, not by how novel it feels in-house — teams systematically place their own work too far left. Cross-check contested placements with `evolution-stage`, and `oss-project-health` for third-party components.

### 4 — Read the map

A component far left while its neighbours are product or commodity is either the real differentiator or the biggest risk — decide which. Commodities at the bottom should be consumed, not built. Everything drifts rightwards: ask how fast each genesis or custom component is moving and what happens when it becomes a product. Clustering in one column means the components were not distinguished — split and re-plot.

### 5 — Apply doctrine and decide

Turn position into a decision: **build** genesis and custom-built components where differentiation lives and no market serves it; **buy or rent** products where vendors compete; **consume as a utility** commodities. Apply *use appropriate methods* — exploratory approaches on the left, volume operations and procurement on the right; one method across the whole map is the classic error. Apply *remove duplication and bias* — the same capability custom-built several times is the commonest finding. Name at least one thing to stop doing.

## Output template

```
## Wardley map — {user need}

**Anchor (user need):** {who + what, one sentence}

| # | Component | Visibility | Evolution | Decision | Note |
|---|---|---|---|---|---|
| 1 | {component} | High/Med/Low | Genesis/Custom/Product/Commodity | Build/Buy/Consume | {why} |

**Dependencies:** {1 → 2 → 3; 1 → 4 → 5}
**Reads:** inversion — {component far left of its neighbours: differentiator or risk}; drift — {component, how fast it moves right}; duplication — {capability built twice}
**Doctrine calls:** build {…} · buy {…} · consume as utility {…}
**Methods:** {which components get exploratory methods, which get volume operations}
**Stop doing:** {the commodity currently being built in-house}
```

Mandatory: the anchor, every component with a visibility and an evolution position, a build/buy/consume decision per component, at least one read, and the stop-doing line. A map with no decisions is a diagram, not a strategy.

## Worked example

Illustrative case (details invented): Halcyon Photos, a photo-sharing service with 3.2 M monthly users, decides where its 24-engineer platform budget goes in 2027.

**Anchor:** a casual user needs to share photos with friends in under 10 seconds from a phone, configuring nothing.

| # | Component | Visibility | Evolution | Decision | Note |
|---|---|---|---|---|---|
| 1 | Mobile app UI | High | Custom-built | Build | Where the 10-second promise is kept |
| 2 | Feed ranking | Medium | Genesis | Build | The differentiator; 3 of 24 engineers, unproven |
| 3 | Auto-tagging | Medium | Custom → Product | Buy | Four vendors compete; in-house model 6 months behind |
| 4 | Image transcoding | Low | Commodity | Consume | A self-hosted farm of 40 machines today |
| 5 | Object storage | Low | Commodity | Consume | Already a utility, 1.4 PB |
| 6 | CDN delivery | Low | Commodity | Consume | Already a utility |

**Dependencies:** 1 → 2 → 3; 1 → 4 → 5 → 6.
**Reads:** inversion — feed ranking sits at genesis while everything beneath is commodity, so it is both differentiator and concentrated risk; drift — auto-tagging moved custom → product in about 24 months and the in-house version now trails vendors; duplication — transcoding and thumbnailing are maintained by two teams.
**Doctrine calls:** build the app UI and feed ranking · buy auto-tagging · consume storage, CDN and transcoding as utilities.
**Methods:** feed ranking gets fast exploratory iterations with an explicit hypothesis; storage and CDN get procurement, SLAs and volume operations — one process for both is the error the map exposes.
**Stop doing:** the 40-machine self-hosted transcoding farm — about 5 engineer-months a year on a commodity, redeployable to feed ranking.

## Verification

- [ ] A user need sits at the top and every component traces up to it; components serving no need are removed.
- [ ] Each component has both coordinates, and none sits between two stages without a stated reason.
- [ ] Re-examine every own-built component against the market: if a vendor sells it, it is not genesis; cross-check with `evolution-stage`.
- [ ] Components are spread across the evolution axis; a single-column map means split and re-plot.
- [ ] Every component carries a build/buy/consume decision, and no commodity carries "build".
- [ ] Placements are stated as claims open to challenge, not as measured fact.

## Pair with adjacent skills

- `evolution-stage` — scores one component on the same genesis → commodity axis; the cross-check for contested placements.
- `position-competitor` — plots rival firms; this maps one organisation's own chain.
- `five-forces-analysis` — industry structure; the map shows where those forces bite on the chain.
- `oss-project-health` — check a third-party component before acting on a "consume" call.
- `scenario-planning` — rightward drift is a key uncertainty over multi-year horizons.
- `jtbd-framing` — establishes the user need that anchors the map.

## Anti-patterns

- Do **not** draw a map without a user need at the top; an unanchored chain is an inventory, not a map.
- Do **not** cluster every component in one evolution column; without spread the map cannot separate build from consume.
- Do **not** place in-house work further left than the market warrants — that is how a team rebuilds a commodity for the fourth time.
- Do **not** treat the map as static; a map drawn once embeds a snapshot as permanent truth.
- Do **not** apply one method across the whole map; exploratory methods on the left, volume operations on the right.
- Do **not** stop before the doctrine calls, or use the canvas to launder an assumption into agreed fact — placements are claims, not measurements.

## Reference

- S. Wardley, "Finding a Path," ch. 2 of *Wardley Maps*, Medium, 2016 — the value-chain and evolution axes, the stage names and the quoted sentence on visibility; published under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). https://medium.com/wardleymaps/finding-a-path-cdb1249078c0
- S. Wardley, "On being lost," ch. 1 of *Wardley Maps*, Medium, August 2016 — anchor, position and movement; carries the series licence statement. https://medium.com/wardleymaps/on-being-lost-2ef5f05eb1ec
- S. Wardley, "Doctrine," ch. 4 of *Wardley Maps*, Medium, 2016 — the three principles named in step 5; same licence.
- S. Wardley, "An Introduction to Wardley (Value Chain) Mapping," *Bits or pieces?*, 2 Feb. 2015. https://blog.gardeviance.org/2015/02/an-introduction-to-wardley-value-chain.html
- M. Edgar, "What do Wardley maps really map? A settler writes," 13 Aug. 2017 — the critique that maps are socially constructed and can launder assumptions into fact. https://blog.mattedgar.com/2017/08/13/what-do-wardley-maps-really-map-a-settler-writes/
