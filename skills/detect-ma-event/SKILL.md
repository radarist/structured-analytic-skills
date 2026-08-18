---
name: detect-ma-event
description: "Parses a news article, filing or press release about a change of control into a structured M&A event record — acquirer, target, deal type, consideration, deal value, premium, dates, regulatory jurisdictions, termination fee — and flags deal-structure risks. Use when text says \"agreed to acquire\", \"merger of equals\", \"takeover bid\", \"all-cash deal\", \"go-private\" or \"divests its division\". Not for primary capital raises — a seed or Series B round routes to `detect-funding-round`."
license: MIT
metadata:
  category: domain
  method: M&A event extraction (deal-structure taxonomy)
  origin: R. F. Bruner, Applied Mergers and Acquisitions, 2004; SEC disclosure forms
  version: "2.0.0"
---
# Detect M&A Event

A change-of-control announcement carries four facts that are easy to conflate: what was bought, how it was paid for, what it was worth, and whether it has actually happened. This skill turns unstructured M&A news into a structured event record, using the deal-structure taxonomy of Bruner (2004) and the vocabulary of the filings that carry these transactions (8-K Item 1.01, Schedule TO, Form S-4). It is the secondary-market counterpart to `detect-funding-round`. The failure it prevents is the confident wrong record — a rumour logged as a signed deal, an enterprise value reported as equity value, a premium pasted into the deal-value field.

## When to invoke

Invoke when the text contains:

- `acquir(e|es|ed|ing|ition)` next to a company name; `merg(er|es|ed)`, `takeover`, `buyout`, `LBO`, `MBO`
- `all-cash deal`, `stock swap`, `stock-for-stock`, `mixed consideration`
- `go-private`, `take private`, `tender offer`, `unsolicited bid`
- `divesting`, `carve-out`, `spin-off`, `sells its {division}`
- `letter of intent (LOI)`, `definitive agreement`, `merger agreement`

Do NOT invoke when:

- The money is new capital, not a change of ownership — a Series A/B/C or seed round is `detect-funding-round` territory.
- The announcement is a product or version release — use `analyze-release-notes`.
- The text describes a partnership (joint venture, licensing, OEM) or an internal reorganisation; neither transfers control.
- The text is too vague to name a target or a deal type — route to `abstain-or-escalate` rather than emitting a half-record.

## Procedure

### 1 — Classify the deal type

| Language                             | Deal type                                    |
| ------------------------------------ | -------------------------------------------- |
| "acquires all outstanding shares"    | `acquisition` (stock purchase)               |
| "acquires assets of"                 | `acquisition` (asset purchase) — `asset-deal`|
| "merger of equals", "combines with"  | `merger`                                     |
| "divests", "sells {division} to"     | `divestiture`                                |
| "spin-off", "spin-out", "separation" | `spinoff`                                    |
| "go-private", "take private", "LBO"  | `go_private`                                 |

Asset versus stock purchase is critical: asset deals usually do not transfer liabilities, stock deals do. A stated percentage refines the record — above 50 % is a change of control, at or below 50 % a minority stake.

### 2 — Extract the consideration structure

Consideration is not deal value. Parse each separately:

- **Type**: cash, stock or mixed.
- **Detail**: `$95.00/share in cash`, `0.28 shares of Acquirer per Target share`, `$45 cash + 0.15 shares`, `earnout up to $500M`.
- **Implied equity value**: price per share × shares outstanding. A bare "valued at $X" goes to `enterprise_value_usd`, ambiguity noted.
- **Premium**: `(offer price − unaffected trading price) / unaffected trading price × 100`, against the close before the rumour or announcement, whichever came first. Value an exchange ratio at the acquirer's share price.

### 3 — Dates and status

Record the announcement date, the expected close ("expected to close in H2 2026"), and the actual close only if the deal closed. Status vocabulary: `announced` / `pending` (regulatory review) / `closed` / `terminated` / `contested` (activist or counter-bid). A rumour is none of these — corroborate it before emitting anything.

### 4 — Regulatory jurisdictions

List the authorities with material review power: `US-DOJ` / `US-FTC` (HSR thresholds), `EU-EC` (EU Merger Regulation), `UK-CMA`, `CN-SAMR`, then `IN-CCI`, `BR-CADE`, `JP-JFTC`, `KR-KFTC`. Where deal size and geographic footprint exceed the thresholds, the jurisdiction belongs on the list even if the release never names it. Foreign-investment screening (CFIUS) is a mention, not an antitrust code.

### 5 — Risk flags

Emit only from this controlled vocabulary: `antitrust-concern` (concentration above thresholds, or regulators on record), `cross-border` (CFIUS or foreign-investment review), `hostile-bid` (offer launched without board approval), `reverse-merger` (target holders take the majority), `sponsor-backed` (private-equity go-private, hence post-close leverage), `activist-contested`, `regulatory-blocked-risk`.

### 6 — Grade the source

Run `rate-source-admiralty`. A1–B2: company 8-K or Schedule TO, EDGAR filing, primary Bloomberg / Reuters / FT reporting. C2–D3: trade-press aggregation without a primary citation. F6: anonymous blog or social speculation. High-value deals need two independent confirmations — `triangulate-sources`.

### 7 — Emit

Confidence is on a **0–100** scale, not 0–1. Score it from explicit rules — base 60; +15 an explicit deal value; +10 an explicit status cue; +10 both parties named; −15 rumour wording; −10 ambiguous currency — and print the trace. Emit the record when confidence ≥ 80 and the source grade is B3 or better; otherwise mark it for human review.

## Output template

```json
{
  "event_type": "ma_event",
  "deal_type": "acquisition | merger | divestiture | spinoff | go_private",
  "acquirer_name": "Helios Semiconductor Inc.",
  "target_name": "Meridian Photonics Corp.",
  "deal_value_usd": 5600000000,
  "consideration_type": "cash | stock | mixed",
  "consideration_detail": "all-cash at $42.00/share",
  "implied_equity_value_usd": 5600000000,
  "enterprise_value_usd": 6100000000,
  "premium_pct": 40,
  "announced_date": "2026-03-03",
  "expected_close_date": "2026-12-31",
  "actual_close_date": null,
  "status": "announced | pending | closed | terminated | contested",
  "regulatory_jurisdictions": ["US-DOJ", "US-FTC", "EU-EC"],
  "termination_fee_usd": 180000000,
  "risk_flags": ["antitrust-concern", "cross-border"],
  "source_url": "https://...",
  "source_grade": "A1",
  "confidence": 95
}
```

Mandatory fields: `event_type`, `deal_type`, `acquirer_name`, `target_name`, `source_url`, `confidence`. Every other field is optional and must be omitted when the source is silent — never invent a termination fee, a premium or a regulatory list.

## Worked example

An illustrative press release (fictional companies): *"SAN JOSE, Calif., March 3, 2026 — Helios Semiconductor Inc. today announced a definitive agreement to acquire Meridian Photonics Corp. for $42.00 per share in cash, a total equity value of about US$5.6 billion and an enterprise value of about US$6.1 billion including Meridian's net debt. The offer represents a premium of approximately 40 % to Meridian's unaffected closing price of $30.00 on February 27, 2026. The transaction is expected to close in the second half of 2026, subject to the HSR Act waiting period and clearance by the European Commission and SAMR. Meridian would pay a $180 million termination fee."*

`python3 scripts/maevent.py --demo` runs that release and prints (abridged):

```json
{ "deal_type": "acquisition", "deal_structure": "stock-purchase",
  "acquirer_name": "Helios Semiconductor Inc.", "target_name": "Meridian Photonics Corp.",
  "deal_value_usd": 5600000000, "deal_value_basis": "equity",
  "enterprise_value_usd": 6100000000, "implied_equity_value_usd": 5600000000,
  "consideration_detail": "all-cash at $42.00/share", "offer_price_per_share": 42,
  "premium_pct": 40.0, "unaffected_price": 30, "expected_close_date": "2026-12-31",
  "status": "announced", "stage": "definitive-agreement",
  "regulatory_jurisdictions": ["US-DOJ", "US-FTC", "EU-EC", "CN-SAMR"],
  "termination_fee_usd": 180000000, "confidence": 95 }
```

Note what the tool refuses to merge: the $5.6 B equity and $6.1 B enterprise values stay in separate fields, and the 40 % premium never enters a value field. The stated 40 % is checked against the 40.0 % computed from $42.00 versus $30.00.

## Verification

- [ ] Confirm acquirer and target are not swapped — "Y agreed to be acquired by X" reverses the order.
- [ ] Verify the status against the verb tense: "agreed", "expected to close" and "completed" are three different states, and only the last is `closed`.
- [ ] Recompute the premium from the offer and unaffected prices; check that it never appears in a value field.
- [ ] Check that enterprise and equity value sit in separate fields, and that a bare "$" carries a currency judgement, not a silent USD assumption.
- [ ] Confirm every optional field rests on a quotable sentence, and that the confidence trace matches the stated rules.

## Companion tool

`scripts/maevent.py` (Python 3.9+, stdlib only, offline) removes the normalisation and arithmetic slips. The skill is fully usable without it — the model reads and judges every field.

```bash
python3 scripts/maevent.py value "enterprise value of ~$5.6B"   # money grammar + basis
python3 scripts/maevent.py classify --text "an all-stock merger of equals"
python3 scripts/maevent.py premium --offer 55 --unaffected 40   # -> 37.5 %
python3 scripts/maevent.py extract --file article.txt --source-url URL
python3 scripts/maevent.py --demo       # the worked example above
python3 scripts/maevent.py --selftest   # 70 hand-verified checks
```

```
$ python3 scripts/maevent.py classify --text "Gamma agreed to acquire a 30% stake in Delta SA"
deal_type:      acquisition   (structure: minority-stake; tags: minority-stake)
status:         announced   (stage: definitive-agreement)
trace:                                                          (abridged)
  - structure: 30% stake (<=50) -> minority stake / strategic investment (no change of control)
```

`extract` prints the event JSON with a confidence trace; `--assume-usd` resolves a bare "$".

## Pair with adjacent skills

- `detect-funding-round` — the primary-market counterpart; check both so an acquisition is not double-counted as a raise.
- `rate-source-admiralty` — grades the source before step 7 decides to emit.
- `triangulate-sources` — corroborates a rumoured deal before it is emitted.
- `analyze-release-notes` — the same parsing discipline, different event type.
- `abstain-or-escalate` — when the text cannot fill the mandatory fields.

## Anti-patterns

- Do **not** combine deal value with premium. Deal value is absolute, premium a percentage over the unaffected price — different fields, different units.
- Do **not** mark a deal closed because the release says "agreed". Announced ≠ closed; use the status vocabulary and verb tense.
- Do **not** treat a letter of intent as a definitive agreement. LOIs are non-binding in most jurisdictions — status stays `announced`, confidence below 60.
- Do **not** skip the regulatory list on a cross-border deal, and do **not** silently read a bare "$" as USD — Canadian, Australian, Hong Kong and Singapore dollars share the symbol.

## Reference

- R. F. Bruner, *Applied Mergers and Acquisitions*. Hoboken, NJ: Wiley, 2004, ch. 18–21 — the deal-structure taxonomy (asset vs stock purchase, consideration design, earnouts). ISBN 978-0-471-39534-8
- A. Damodaran, "The Value of Control: Implications for Control Premia, Minority Discounts and Voting Share Differentials," *NYU Journal of Law and Business*, vol. 8, no. 2, pp. 487–503, 2012 — the control premium is measured against the unaffected price.
- U.S. Securities and Exchange Commission, *Form 8-K* (Item 1.01, material definitive agreement), *Schedule TO* (Rule 14d-100) and *Form S-4*, 2011. https://www.sec.gov/forms
- U.S. Federal Trade Commission and U.S. Department of Justice, *Hart-Scott-Rodino Premerger Notification Program*, 2024. https://www.ftc.gov/enforcement/premerger-notification-program
- European Union, Council Regulation (EC) No 139/2004 on concentrations between undertakings, *Official Journal of the European Union*, L 24, pp. 1–22, 2004. https://eur-lex.europa.eu/eli/reg/2004/139/oj
