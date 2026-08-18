# Choosing axes for a positioning map

Reference material for `position-competitor`, step 1. An axis earns its place on a map only if it is
**material** (a buyer's decision changes along it), **measurable** (every entity can be scored from
evidence rather than impression) and **orthogonal** to the other axis (it does not measure the same
underlying variable twice).

## Candidate pairs

| Pair | What it separates | Typical evidence to score it |
|---|---|---|
| Cost ↔ quality | Commodity supply against premium supply | List prices, unit economics; benchmark or defect-rate results |
| Integrated ↔ modular | All-in-one platforms against best-of-breed components | Published surface area: SDKs, APIs, adjacent services, marketplace presence |
| Enterprise ↔ self-serve | Top-down sales motions against product-led ones | Contract sizes, sales-cycle length, presence of a free tier or public pricing |
| Proprietary ↔ open | Closed vendors against open-core or fully open suppliers | Licences, availability of source or weights, self-hosting support |
| Focused ↔ full-stack | One sharp capability against a suite | Product-line breadth, revenue concentration |
| Generalist ↔ specialist | Horizontal tooling against vertical-specific offerings | Named vertical SKUs, industry certifications, reference-customer distribution |
| Speed of change ↔ stability | Fast-moving challengers against slow, dependable incumbents | Release cadence, deprecation policy, long-term-support commitments |

Gartner's Magic Quadrant uses a domain-independent pair — completeness of vision against ability to
execute — which is why it travels across markets but says little about any particular buying decision.
A pair chosen for a specific decision usually beats it for that decision.

## The orthogonality test

Score every entity on both axes, then correlate the two score vectors across entities.

| Pearson \|r\| | Verdict | What to do |
|---|---|---|
| ≥ 0.7 | Not independent | Replace one axis; the map would be a diagonal line |
| 0.4 – 0.7 | Caution | Keep only with a documented reason why the axes still capture different variance |
| < 0.4 | OK | Proceed |

`python3 scripts/positioning.py orthogonality --file competitors.csv` reports Pearson r and Spearman
rho, plus a correlation matrix over any extra numeric columns and the least-correlated pair among
them. Treat that suggestion as a candidate, not a decision: a statistically independent pair that no
buyer cares about makes a useless map. The cut-offs are this skill's operationalisation of Porter's
qualitative rule that correlated axes should be replaced, not a published standard.

## Common traps

- **The same variable twice.** Company size against revenue; headcount against integration depth.
  The correlation matrix catches these — check every extra column against both axes.
- **An axis nobody buys on.** Technically independent, commercially irrelevant. Materiality first.
- **An axis that cannot be scored.** "Innovativeness" has no evidence source; release cadence does.
- **An ossified axis.** If a three-year back-cast shows nothing moved, the axis is measuring
  structure (size, age) rather than competitive dynamics.
