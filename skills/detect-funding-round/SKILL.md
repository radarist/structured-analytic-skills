---
name: detect-funding-round
description: "Parses a capital-raise announcement into a structured FundingEvent record — company, round stage, amount and currency, dates, lead and participating investors, valuation, use of proceeds, confidence. Use when a news item, press release or search result reports financing: \"raised $47 million\", \"closed its Series B\", \"seed round\", \"post-money valuation of $400M\", \"led by Northgate Ventures\". Not for change-of-control news — an acquisition or merger routes to `detect-ma-event`, a product launch to `analyze-release-notes`."
license: MIT
metadata:
  category: domain
  method: Funding-round event extraction (Form D / venture round taxonomy)
  origin: U.S. SEC Regulation D Form D, 1982; staged-financing taxonomy, Gompers & Lerner
  version: "2.0.0"
---
# Detect Funding Round

A funding announcement is prose; the record it should become is short and easy to corrupt — a range averaged the wrong way, a valuation filed as the amount raised, a bare `$` from a Toronto newsroom read as USD. This skill turns capital-raise news into a **FundingEvent** built on the facts the U.S. Securities and Exchange Commission's Form D (Regulation D, in force since 1982) requires of the primary filing: who raised, how much, in what currency, from whom, when. It never fills a field the source did not state: the failure mode is a tidy record that misstates the number.

## When to invoke

Invoke when the text contains:

- `Series [A-Z]` or `Series [A-Z]-\d` ("Series B-2"), `seed round`, `pre-seed`, `bridge round`, `crossover round`
- `raised $[\d.]+ ?[MmBbKk]`, `raised [\d.]+ (million|billion)`, `closed (a|its) … (round|financing)`
- `post-money valuation (of|at) $`, or `led by <investor>` beside an amount

Do NOT invoke when:

- The story is a change of control — acquisition, merger, take-private. Route to `detect-ma-event`: a buyout counted as a round wrecks comparables.
- It is a product, model or version announcement. Route to `analyze-release-notes`.
- The mention is incidental ("the Y Combinator-backed startup") with no round announced — no event to record.
- The amount or investors cannot be corroborated from a second source — use `triangulate-sources` first.

## Procedure

### 1 — Normalise the amount

`$47M` → `47000000`; `£500k` → `500000`; `INR 400 crore` → `4000000000` (1 crore = 10^7). A range — `$47M-$50M`, `$47M to $50M` — becomes its midpoint `48500000` and costs confidence; "up to $50M" is a ceiling, not the amount raised. Never convert currency: keep the figure as stated and name the currency beside it. A bare `$` is ambiguous — USD, CAD, AUD, SGD and HKD all write it — so commit to USD only on `US$`/`USD`.

### 2 — Identify the stage

Map to the canonical vocabulary and nothing else: "Series A round" → `Series A`, "Series B-2 financing" → `Series B-2`, "seed financing" → `Seed`, "pre-seed" → `Pre-seed`, "bridge"/"extension" → `Bridge`, "tender offer" → `Secondary`, "growth equity"/"late-stage"/"crossover" → `Growth`, and an IPO, direct listing or SPAC merger → `Public (IPO)`, `Public (Direct)`, `Public (SPAC)`. If the text says only "its latest round", leave `stage` blank. Venture debt and grants are not equity stages.

### 3 — Keep the valuation out of the amount

"$3.5B at a $61.5B post-money valuation" is two numbers in two fields. Read the qualifier: "post-money" → `post_money_valuation_usd`, "pre-money" → `pre_money_valuation_usd`. A bare "valued at $X" defaults to post-money by convention, but note the ambiguity: the two differ by exactly the size of the round.

### 4 — Identify the investors

The **lead** is the investor the text says led, co-led or priced the round. Everyone else named — after "with participation from", "joined by", "alongside" — is a **participant**. Split lists on commas and "and", stripping qualifiers such as "existing investors". No lead named means `lead_investors` stays empty: being named first is not evidence of leading.

### 5 — Date the round

The announcement date is normally the article's publication date. The close date is a different fact, often stated in the body ("which closed on 18 February 2025"); record both in ISO `YYYY-MM-DD` form when both appear. A single unmarked date is the announcement date.

### 6 — Grade the source

Grade the source with `rate-source-admiralty`. An SEC Form D filing, a press release on the company's own domain, or Reuters/FT/Bloomberg copy sits at A1–B2; an aggregator with no primary citation is C2–D3; a rumour blog is F6. A confident parse of a bad source is still a bad record, so the grade travels beside it.

### 7 — Score the confidence and emit the record

Confidence is 0–100: base 60; **+15** an explicit stage; **+10** an explicit lead; **+10** an exact single amount; **−15** a range or "up to" cap; **−10** an ambiguous currency; clamp to 0–100. A record scoring ≥ 75 from a source graded B3 or better ships as it stands. Below either bar, attach the failing reason and hand it to a human reviewer — `abstain-or-escalate` covers that decision.

## Output template

```json
{
  "event_type": "funding_round",
  "company_name": "Helion Diagnostics",
  "stage": "Series B",
  "amount_usd": 47000000,
  "amount_currency": "USD?",
  "announced_date": "2025-03-03",
  "close_date": "2025-02-18",
  "post_money_valuation_usd": 400000000,
  "lead_investors": ["Northgate Ventures"],
  "participating_investors": ["Baseline Capital", "Kestrel Partners"],
  "use_of_proceeds": "expand its clinical trial programme",
  "source_url": "https://example.com/pr/helion-series-b",
  "source_grade": "B2",
  "confidence": 85
}
```

`event_type`, `company_name` and `source_url` are mandatory; a pre-money figure goes in `pre_money_valuation_usd`. Every other field is optional and **must** be omitted — not nulled, not guessed — when unstated. `amount_currency` keeps a trailing `?` (`USD?`) while the currency is unresolved; `amount_usd` holds the figure in the currency named beside it, with no exchange rate applied.

## Worked example

Illustrative article text (company and funds invented):

> Helion Diagnostics, a Cambridge-based cancer-screening company, raised $47 million in Series B funding, the company announced on 2025-03-03. The round was led by Northgate Ventures, with participation from Baseline Capital, Kestrel Partners and Orion Growth Fund. The financing, which closed on 2025-02-18, values Helion at $400 million post-money. Helion will use the funds to expand its clinical trial programme and open a manufacturing site in Basel.

`python3 scripts/funding.py extract --demo --source-grade B2` prints the record (wrapped) and trace:

```json
{
  "event_type": "funding_round", "company_name": "Helion Diagnostics",
  "stage": "Series B", "amount_usd": 47000000, "amount_currency": "USD?",
  "announced_date": "2025-03-03", "close_date": "2025-02-18",
  "post_money_valuation_usd": 400000000,
  "lead_investors": ["Northgate Ventures"],
  "participating_investors": ["Baseline Capital", "Kestrel Partners", "Orion Growth Fund"],
  "use_of_proceeds": "expand its clinical trial programme and open a manufacturing site in Basel",
  "source_grade": "B2", "confidence": 85
}
```

```
confidence trace (SKILL.md scoring rules):
  base                           +60   starting point for a single-source parse
  + explicit stage               +15   Series B
  + explicit lead investor       +10   Northgate Ventures
  + exact single amount          +10   47,000,000 USD?
  - ambiguous currency           -10   USD?
  = confidence                    85   the SKILL.md review threshold is 75
```

Three readings carry the example. The $400 million is a valuation, so it never touches `amount_usd`. The `$` is unmarked, so the currency stays `USD?` and the score loses 10 rather than deciding the question. `source_url` is absent, so the field is omitted and the notes flag it must be supplied. At 85 with a B2 source, the record clears both bars.

## Verification

- [ ] Amount and valuation are different numbers in different fields; no valuation reached `amount_usd`.
- [ ] Each currency is the one the source used, no exchange rate applied, and any bare `$` is either resolved by explicit context or still carries `?`.
- [ ] `lead_investors` holds only investors the text says led, co-led or priced the round — empty rather than guessed.
- [ ] A range was recorded as its midpoint and an "up to" figure as a cap, penalty applied — recompute with `python3 scripts/funding.py amount "<string>"`.
- [ ] The stage is a canonical label or blank; none was inferred from the round size.
- [ ] Every populated field traces to a sentence in the source, every unstated field is absent, and the confidence arithmetic reproduces.

## Companion tool

`scripts/funding.py` (Python 3.9+, stdlib only, offline) applies steps 1–3 and 7:

```bash
python3 scripts/funding.py amount "$47M to $50M"
python3 scripts/funding.py stage "its Series B-2 financing"
python3 scripts/funding.py extract --file article.txt --source-grade B2
python3 scripts/funding.py --demo | --selftest   # worked example | 83 checks
```

```
$ python3 scripts/funding.py amount "$47M to $50M"
value:              48,500,000
currency:           USD?
confidence_penalty: -25
note:               '$' is ambiguous (USD/CAD/AUD/SGD/HKD/NZD); no US$/USD marker in the text
note:               range 47,000,000 to 50,000,000 -> midpoint (SKILL.md step 1)
```

`extract` prints the record on stdout, the confidence trace on stderr. The skill works without it — reading the article is the analyst's job either way; the tool only removes arithmetic and normalisation slips (midpoints, crore, caps, ambiguous `$`), and never invents a field.

## Pair with adjacent skills

- `detect-ma-event` — the change-of-control sibling; run one or the other, never both, or the money is counted twice.
- `analyze-release-notes` — sibling parser for product announcements.
- `rate-source-admiralty` — supplies the `source_grade` step 6 requires.
- `triangulate-sources` — corroborates amount and investors before a consequential record ships.
- `abstain-or-escalate` — the decision procedure for records below the confidence or source bar.
- Methodology counterpart: [methodologies/foresight/horizon-scanning.md](https://github.com/radarist/structured-analytic-skills/blob/main/methodologies/foresight/horizon-scanning.md) — funding events are one signal type a scan collects.


## Anti-patterns

- Do **not** merge amount and valuation. "$3.5B raised" and "$61.5B post-money" are two facts; conflating them inflates a round by an order of magnitude.
- Do **not** guess the stage. Seed and Series A are different rounds; a wrong one propagates into every comparable built on the record.
- Do **not** convert currency silently. `$47M` in a Canadian report may be CAD, and an unmarked conversion is unrecoverable.
- Do **not** promote the first-named investor to lead, or present a midpoint as exact; the penalty exists so the reader knows the number was reconstructed.

## Reference

- U.S. Securities and Exchange Commission, *Form D — Notice of Exempt Offering of Securities*, Regulation D (17 CFR §§230.501–508), adopted 1982. https://www.sec.gov/forms — primary record for US private rounds.
- P. A. Gompers and J. Lerner, *The Venture Capital Cycle*, 2nd ed. Cambridge, MA: MIT Press, 2004. ISBN 978-0-262-07255-7 — staged financing as an economic mechanism; why the stage label carries weight.
- W. A. Sahlman, "The structure and governance of venture-capital organizations," *Journal of Financial Economics*, vol. 27, no. 2, pp. 473–521, 1990 — why the lead investor and post-money valuation are worth extracting.
- Crunchbase and PitchBook round taxonomies, accessed 2025 — cross-checks on stage and amount, never primary.
