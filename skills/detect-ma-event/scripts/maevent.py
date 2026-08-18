#!/usr/bin/env python3
"""maevent.py — deterministic helper for the detect-ma-event skill.

Implements the definitions in ../SKILL.md so the agent does not have to normalise
money strings, map phrasing onto the controlled vocabularies, or do premium
arithmetic in its head:

  * Deal-value grammar (SKILL.md step 2): `$1.2B`, `€850 million`, `£3.4bn`,
    `US$28 billion`, `~$10B` (approx flag), `enterprise value of $5.6B` vs
    `equity value of $4.9B` — kept as SEPARATE fields (`enterprise_value_usd`,
    `implied_equity_value_usd`). A bare `$` is reported as currency `USD?`
    (ambiguous) unless written `US$` or `--assume-usd` is given.
  * Deal type (SKILL.md step 1 table): acquisition | merger | divestiture |
    spinoff | go_private — plus `deal_structure` for the finer class the table
    distinguishes: stock-purchase, asset-deal (tag `asset-deal`),
    merger-of-equals, majority-stake, minority-stake, acqui-hire, tender-offer,
    take-private, carve-out, joint-venture (out of scope per "When to invoke").
  * Status (SKILL.md step 3): announced | pending | closed | terminated |
    contested — plus `stage` for the lifecycle detail (rumored, non-binding,
    definitive-agreement, pending-regulatory, closed, terminated, contested).
    "Rumored" is not a SKILL.md status: `status` is omitted, `stage` = rumored,
    `review_required` = true. An LOI keeps status=announced with confidence < 60
    (SKILL.md anti-pattern).
  * Premium (SKILL.md step 2): (offer − unaffected) / unaffected × 100;
    exchange ratio × acquirer share price (+ cash per share) = implied value.
  * Confidence (0–100) from explicit rules, printed in the trace:
        base 60
        +15 explicit deal value          +10 explicit status cue
        +10 both parties named           −15 rumour cues (sources say / in talks)
        −10 ambiguous currency (USD?)    clamp 0–100; non-binding LOI caps at 59
    review_required = confidence < 80 (SKILL.md step 7).

Missing fields are omitted, never fabricated. Stdlib only. Python 3.9+. Offline;
no wall-clock is read ("today" is left unresolved).

Usage:
    python3 maevent.py value "enterprise value of ~$5.6B" [--assume-usd] [--json]
    python3 maevent.py classify --text "Foo Corp to acquire Bar Inc ..." [--json]
    python3 maevent.py premium --offer 55 --unaffected 40
    python3 maevent.py premium --exchange-ratio "0.5 shares of X for each share of Y" \
                               --acquirer-price 100 --unaffected 40
    python3 maevent.py premium --text "$45 in cash and 0.15 shares of X for each share of Y" \
                               --acquirer-price 100 --unaffected 50
    python3 maevent.py extract --file article.txt | --text "..." [--assume-usd] [--source-url URL]
    python3 maevent.py --demo
    python3 maevent.py --selftest
"""

import argparse
import json
import re
import sys
from decimal import Decimal

# --- controlled vocabularies (SKILL.md) ---------------------------------------

DEAL_TYPES = ("acquisition", "merger", "divestiture", "spinoff", "go_private")
STATUSES = ("announced", "pending", "closed", "terminated", "contested")
CONSIDERATION_TYPES = ("cash", "stock", "mixed")
STAGES = ("rumored", "non-binding", "definitive-agreement", "pending-regulatory",
          "closed", "terminated", "contested")

CONFIDENCE_RULES = (
    "base 60",
    "+15 explicit deal value",
    "+10 explicit status cue",
    "+10 both parties named",
    "-15 rumour cues (sources say / in talks / people familiar)",
    "-10 ambiguous currency (bare '$' -> USD?)",
    "clamp 0-100; non-binding LOI/MOU caps at 59 (SKILL.md anti-pattern)",
    "review_required when confidence < 80 (SKILL.md step 7)",
)

# --- money grammar --------------------------------------------------------------

_CUR_PREFIX = (
    r"(?P<pre>US\s?\$|U\.S\.\s?\$|USD|C\$|CA\$|CAD|A\$|AU\$|AUD|HK\$|HKD|S\$|SGD|NZ\$|NZD|"
    r"R\$|BRL|CN¥|CNY|RMB|JPY|EUR|GBP|CHF|SEK|NOK|DKK|INR|KRW|\$|€|£|¥|₹|₩)"
)
_NUM = r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
_MAG = r"(?P<mag>trillion|billion|million|thousand|bn|mn|mm|tn|bil|mil|[BMKT])?"
_CUR_SUFFIX = (
    r"(?P<suf>USD|EUR|GBP|JPY|CNY|CHF|CAD|AUD|SGD|HKD|INR|KRW|SEK|NOK|DKK|BRL|NZD|"
    r"(?:U\.S\. |US |Canadian |Australian |Singapore |Hong Kong |New Zealand )?dollars?|"
    r"euros?|pounds?(?: sterling)?|yen|yuan|renminbi|(?:Swiss )?francs?|rupees?|won|kronor)"
)
MONEY_RE = re.compile(
    r"(?:%s\s?)?%s\s?%s(?![A-Za-z])(?:\s?%s\b)?" % (_CUR_PREFIX, _NUM, _MAG, _CUR_SUFFIX),
    re.I,
)

MAGNITUDE = {
    "trillion": 10 ** 12, "tn": 10 ** 12, "t": 10 ** 12,
    "billion": 10 ** 9, "bn": 10 ** 9, "bil": 10 ** 9, "b": 10 ** 9,
    "million": 10 ** 6, "mn": 10 ** 6, "mm": 10 ** 6, "mil": 10 ** 6, "m": 10 ** 6,
    "thousand": 10 ** 3, "k": 10 ** 3,
}

# prefix symbol/code -> (ISO code, ambiguous?)
PREFIX_CURRENCY = {
    "$": ("USD", True), "us$": ("USD", False), "u.s.$": ("USD", False), "usd": ("USD", False),
    "c$": ("CAD", False), "ca$": ("CAD", False), "cad": ("CAD", False),
    "a$": ("AUD", False), "au$": ("AUD", False), "aud": ("AUD", False),
    "hk$": ("HKD", False), "hkd": ("HKD", False), "s$": ("SGD", False), "sgd": ("SGD", False),
    "nz$": ("NZD", False), "nzd": ("NZD", False), "r$": ("BRL", False), "brl": ("BRL", False),
    "cn¥": ("CNY", False), "cny": ("CNY", False), "rmb": ("CNY", False), "jpy": ("JPY", False),
    "€": ("EUR", False), "eur": ("EUR", False), "£": ("GBP", False), "gbp": ("GBP", False),
    "¥": ("JPY", True), "chf": ("CHF", False), "sek": ("SEK", False), "nok": ("NOK", False),
    "dkk": ("DKK", False), "inr": ("INR", False), "₹": ("INR", False), "krw": ("KRW", False),
    "₩": ("KRW", False),
}
SUFFIX_CURRENCY = [
    (r"^(?:u\.s\. |us )dollars?$", ("USD", False)), (r"^canadian dollars?$", ("CAD", False)),
    (r"^australian dollars?$", ("AUD", False)), (r"^singapore dollars?$", ("SGD", False)),
    (r"^hong kong dollars?$", ("HKD", False)), (r"^new zealand dollars?$", ("NZD", False)),
    (r"^dollars?$", ("USD", True)), (r"^euros?$", ("EUR", False)),
    (r"^pounds?(?: sterling)?$", ("GBP", False)), (r"^yen$", ("JPY", False)),
    (r"^(?:yuan|renminbi)$", ("CNY", False)), (r"^(?:swiss )?francs?$", ("CHF", False)),
    (r"^rupees?$", ("INR", False)), (r"^won$", ("KRW", False)), (r"^kronor$", ("SEK", False)),
    (r"^usd$", ("USD", False)), (r"^eur$", ("EUR", False)), (r"^gbp$", ("GBP", False)),
    (r"^jpy$", ("JPY", False)), (r"^cny$", ("CNY", False)), (r"^chf$", ("CHF", False)),
    (r"^cad$", ("CAD", False)), (r"^aud$", ("AUD", False)), (r"^sgd$", ("SGD", False)),
    (r"^hkd$", ("HKD", False)), (r"^inr$", ("INR", False)), (r"^krw$", ("KRW", False)),
    (r"^sek$", ("SEK", False)), (r"^nok$", ("NOK", False)), (r"^dkk$", ("DKK", False)),
    (r"^brl$", ("BRL", False)), (r"^nzd$", ("NZD", False)),
]

APPROX_BEFORE_RE = re.compile(
    r"(?P<q>approximately|approx\.?|about|around|roughly|nearly|almost|circa|c\.|~|"
    r"an estimated|estimated|est\.|some|up to|more than|over|at least|in excess of|"
    r"as much as|as high as|close to|just under|just over|north of|south of)\s*$",
    re.I,
)
PER_SHARE_AFTER_RE = re.compile(
    r"^\s*(?:in cash\s+)?(?:per|a|/|for each|for every|for each outstanding)\s?"
    r"(?:common |ordinary |outstanding |issued )?(?:share|ads|adr|unit)\b|"
    r"\b(?:for each|for every|per)\s+(?:outstanding\s+|common\s+|ordinary\s+)?"
    r"(?:[A-Z][\w.&'’-]*\s+){0,3}(?:share|ADS|unit)\b|/share",
    re.I,
)
PER_SHARE_BEFORE_RE = re.compile(
    r"(?:per[- ]share (?:price|consideration|offer|cash (?:price|payment|consideration))|"
    r"price per share|offer price|purchase price per share) (?:of|at)\s*$",
    re.I,
)
_CONNECT = (r"(?:\s+(?:of|at|to|was|is|were|are|totaling|totalling|amounting to|equal to|worth|approximately|"
            r"approx\.|about|roughly|around|an estimated|estimated|nearly|almost|over|more than|some|circa|c\.|~)|:)*"
            r"\s*$")
SHARE_PRICE_BEFORE_RE = re.compile(
    r"(?:closing (?:share |stock )?price|unaffected (?:share |stock |closing |trading )?price|"
    r"last close|closed at|traded at|trading (?:at|price)|volume[- ]weighted average price|"
    r"vwap|average (?:closing |share |stock )?price|share price|stock price|"
    r"undisturbed (?:share |stock )?price)" + _CONNECT,
    re.I,
)
TERMINATION_FEE_BEFORE_RE = re.compile(
    r"(?:reverse )?(?:termination|break(?:-| )?up|break) fee" + _CONNECT,
    re.I,
)
TERMINATION_FEE_AFTER_RE = re.compile(
    r"^\s*(?:reverse )?(?:termination|break(?:-| )?up|break) fee", re.I)
OTHER_BEFORE_RE = re.compile(
    r"(?:revenues?|sales|ebitda|net income|net loss|profit|earnings|market cap(?:italization)?|"
    r"valuation|funding|cash|net cash|net debt|debt|synergies|savings|dividend|"
    r"assets under management|aum|backlog|bookings|arr|annual(?:ized)? recurring revenue|"
    r"gross margin|capex|capital expenditures?|raised|invested|investment|loan|credit facility|"
    r"financing|bridge loan|term loan|notes|bonds|fine|penalty|damages|settlement|budget|"
    r"contract|order|grant|subsidy|tax|charge|impairment|write-?down)" + _CONNECT,
    re.I,
)
ENTERPRISE_BEFORE_RE = re.compile(
    r"(?:enterprise value|total enterprise value|\bev\b|inclusive of (?:net )?debt|"
    r"including (?:the assumption of )?(?:net )?debt|debt-free|cash-free)"
    r"(?: of| at| basis of|:| is| was| totaling| totalling| approximately| about)*\s*$",
    re.I,
)
ENTERPRISE_AFTER_RE = re.compile(
    r"^\s*(?:,\s*)?(?:in enterprise value|enterprise value|on an enterprise value basis|"
    r"including (?:the assumption of )?(?:net )?debt|inclusive of (?:net )?debt|"
    r"including debt|plus (?:net )?debt|\(?ev\)?)",
    re.I,
)
EQUITY_BEFORE_RE = re.compile(
    r"(?:equity value|implied equity value|total equity value|market cap(?:italization)?|"
    r"fully[- ]diluted (?:equity value|basis|market value)|equity purchase price)"
    r"(?: of| at| basis of|:| is| was| totaling| totalling| approximately| about)*\s*$",
    re.I,
)
EQUITY_AFTER_RE = re.compile(
    r"^\s*(?:,\s*)?(?:in equity value|equity value|on a fully[- ]diluted basis|"
    r"on an equity value basis|in implied equity value|of equity value)",
    re.I,
)


def _num_from_decimal(d):
    """Return int when integral, else float — keeps JSON output exact and stable."""
    if d == d.to_integral_value():
        return int(d)
    return float(d)


def parse_money(text, assume_usd=False):
    """Find every money expression in `text`.

    Returns a list of dicts (in text order):
      raw, start, end, value, currency ('USD?' when a bare '$' is ambiguous),
      currency_ambiguous, approx, qualifier, per_share, basis
      (enterprise | equity | unspecified), kind (deal-value | per-share-offer |
      share-price | termination-fee | other | small-amount)
    Windows used for context never cross a neighbouring money expression, so
    "$5 billion, or $42 per share" does not tag the $5 billion as per-share.
    """
    matches = []
    for m in MONEY_RE.finditer(text):
        pre = (m.group("pre") or "").lower().replace(" ", "")
        suf = (m.group("suf") or "").lower()
        if not pre and not suf:
            continue  # a bare number ("30 million users", "0.15 shares") is not money
        cur, ambiguous = None, False
        if pre:
            cur, ambiguous = PREFIX_CURRENCY[pre]
        else:
            for pat, val in SUFFIX_CURRENCY:
                if re.match(pat, suf, re.I):
                    cur, ambiguous = val
                    break
        if cur is not None:
            matches.append((m, cur, ambiguous))
    out = []
    for i, (m, cur, ambiguous) in enumerate(matches):
        if ambiguous and cur == "USD" and assume_usd:
            ambiguous = False
        num = Decimal(m.group("num").replace(",", ""))
        mag = (m.group("mag") or "").lower()
        value = num * MAGNITUDE[mag] if mag else num
        prev_end = matches[i - 1][0].end() if i > 0 else 0
        next_start = matches[i + 1][0].start() if i + 1 < len(matches) else len(text)
        before = text[max(prev_end, m.start() - 90):m.start()]
        after = text[m.end():min(next_start, m.end() + 90)]
        qual = APPROX_BEFORE_RE.search(before)
        approx = bool(qual)
        qualifier = qual.group("q").lower() if qual else None
        per_share = bool(PER_SHARE_AFTER_RE.search(after) or PER_SHARE_BEFORE_RE.search(before))
        basis = "unspecified"
        if ENTERPRISE_BEFORE_RE.search(before) or ENTERPRISE_AFTER_RE.search(after):
            basis = "enterprise"
        elif EQUITY_BEFORE_RE.search(before) or EQUITY_AFTER_RE.search(after):
            basis = "equity"
        # kind
        if TERMINATION_FEE_BEFORE_RE.search(before) or TERMINATION_FEE_AFTER_RE.search(after):
            kind = "termination-fee"
        elif SHARE_PRICE_BEFORE_RE.search(before):
            kind = "share-price"
        elif per_share:
            kind = "per-share-offer"
        elif OTHER_BEFORE_RE.search(before) and basis == "unspecified":
            kind = "other"
        elif not mag and value < 100000:
            kind = "small-amount"
        else:
            kind = "deal-value"
        out.append({
            "raw": m.group(0).strip(),
            "start": m.start(),
            "end": m.end(),
            "value": _num_from_decimal(value),
            "currency": cur + ("?" if ambiguous else ""),
            "currency_ambiguous": ambiguous,
            "approx": approx,
            "qualifier": qualifier,
            "per_share": per_share,
            "basis": basis,
            "kind": kind,
        })
    return out


def value_summary(text, assume_usd=False):
    """Structured result for the `value` command."""
    amounts = parse_money(text, assume_usd=assume_usd)
    res = {"input": text, "amounts": amounts}
    notes = []
    ev = [a for a in amounts if a["basis"] == "enterprise" and not a["per_share"]]
    eq = [a for a in amounts if a["basis"] == "equity" and not a["per_share"]]
    if ev:
        res["enterprise_value"] = {"value": ev[0]["value"], "currency": ev[0]["currency"]}
    if eq:
        res["equity_value"] = {"value": eq[0]["value"], "currency": eq[0]["currency"]}
    if ev and eq:
        notes.append("enterprise value and equity value are different quantities (EV = equity + net debt); "
                     "kept as separate fields, never merged")
    if any(a["currency_ambiguous"] for a in amounts):
        notes.append("bare '$' is ambiguous (USD?, could be CAD/AUD/HKD/...); write US$ or pass --assume-usd")
    if any(a["approx"] for a in amounts):
        notes.append("approximate figure(s) flagged (approx=true) — quote as '~', not as an exact value")
    unspecified = [a for a in amounts if a["kind"] == "deal-value" and a["basis"] == "unspecified"]
    if unspecified and not ev and not eq:
        notes.append("basis unspecified: SKILL.md step 2 captures a bare 'valued at' figure as "
                     "enterprise_value_usd and notes the ambiguity")
    if notes:
        res["notes"] = notes
    return res


# --- deal-type classification (SKILL.md step 1) --------------------------------

JV_RE = re.compile(r"\bjoint venture\b|\bJV\b")
SPINOFF_RE = re.compile(
    r"\bspin[- ]?offs?\b|\bspin[- ]?outs?\b|\bspun[- ](?:off|out)\b|\bspinning (?:off|out)\b|"
    r"\bdemerger\b|\bdemerge[sd]?\b|"
    r"\bseparat(?:e|ion|ing)\b[^.]{0,40}\b(?:into two|independent|publicly[- ]traded|standalone|"
    r"stand-alone|two (?:companies|public companies|businesses))\b|"
    r"\bsplit(?:s|ting)? (?:itself |the company )?into (?:two|three|separate|independent)\b",
    re.I,
)
DIVEST_RE = re.compile(
    r"\bdivest\w*|\bcarve[- ]?outs?\b|"
    r"\bdispos(?:e|al|es|ing) of (?:its |the )?[\w\s-]{0,30}?(?:unit|division|business|subsidiary|arm|"
    r"stake|operations)\b|"
    r"\b(?:sells?|sold|selling|to sell)\b[^.]{0,50}?\b(?:unit|division|business|subsidiary|arm|"
    r"operations|assets|brand|portfolio|segment|stake)\b[^.]{0,20}?\bto\b|"
    r"\bsale of (?:its |the )?[\w\s-]{0,40}?(?:unit|division|business|subsidiary|arm|operations|"
    r"segment)\b|\boffload\w*",
    re.I,
)
CARVE_OUT_RE = re.compile(r"\bcarve[- ]?outs?\b", re.I)
GO_PRIVATE_RE = re.compile(
    r"\bgo(?:ing|es)?[- ]private\b|\btake[- ]private\b|\btaken private\b|"
    r"\btak(?:e|es|ing)\s+(?:[A-Z][\w.&'’-]*\s+){0,4}(?:the company\s+)?private\b|"
    r"\bleveraged buy-?out\b|\bmanagement buy-?out\b|\bLBO\b|\bMBO\b|\bdelist(?:ed|ing)?\b|"
    r"\bprivati[sz](?:e|ed|ation)\b|\bbuyout\b[^.]{0,30}\bprivate equity\b|"
    r"\bprivate equity\b[^.]{0,30}\bbuyout\b",
    re.I,
)
MERGER_EQUALS_RE = re.compile(r"\bmerger[- ]of[- ]equals\b|\bcombination of equals\b", re.I)
MERGER_RE = re.compile(
    r"\bmerger[- ]of[- ]equals\b|\bcombination of equals\b|\ball-stock merger\b|"
    r"\bmerg(?:e|es|ed|ing) with\b|\bto merge\b|\bwill merge\b|\bagreed to merge\b|"
    r"\bcombin(?:e|es|ed|ing) with\b|\bto combine\b|\bcombine in\b|\bcombination with\b|"
    r"\bmerger between\b|\bmerger with\b|\bbusiness combination\b|"
    r"\bannounced (?:a|an|their|the) (?:all-stock |proposed |definitive |strategic )?merger\b|"
    r"\bagreed (?:to|on) (?:a|an|the) merger\b|\bmerger (?:deal|transaction) (?:between|of|uniting|"
    r"combining)\b|\bmerger of\b",
    re.I,
)
ACQ_RE = re.compile(
    r"\bacqui(?:re|res|red|ring|sition|sitions)\b|\bbuy(?:s|ing)?\b|\bbought\b|"
    r"\bpurchas(?:e|es|ed|ing)\b|\btake-?overs?\b|\btak(?:e|es|en|ing) over\b|\btook over\b|"
    r"\bbuy-?outs?\b|\btender offer\b|\bstake in\b|\bacqui-?hir\w*|\bsnap(?:ped|s)? up\b|"
    r"\bbid for\b|\boffer for\b|\bsell(?:s|ing)? (?:the company|itself)\b|\bsold (?:the company|itself)\b|"
    r"\bsale of the company\b",
    re.I,
)
TENDER_RE = re.compile(
    r"\btender offer\b|\bexchange offer\b|\bschedule 14D\b|\bschedule TO\b|\btakeover (?:bid|offer)\b|"
    r"\bcash offer for\b|\bpublic offer\b|\bmakes? (?:an? )?(?:hostile |unsolicited |cash |takeover |"
    r"revised |sweetened |final )?(?:bid|offer) for\b|\bbid for\b|\boffer to (?:acquire|buy)\b|"
    r"\bunsolicited (?:bid|offer|proposal|approach)\b|\bhostile (?:bid|offer|takeover|approach)\b",
    re.I,
)
HOSTILE_RE = re.compile(
    r"\bhostile\b|\bunsolicited\b|\bwithout (?:the )?(?:approval|support|backing|consent) of "
    r"(?:the )?(?:target(?:'s)? |company(?:'s)? )?board\b|\bdirectly to (?:its |the )?(?:target(?:'s)? )?"
    r"shareholders\b|\bproxy fight\b|\bproxy contest\b|\bbypass(?:ing|ed)? the board\b",
    re.I,
)
ASSET_RE = re.compile(
    r"\bassets? (?:purchase|deal|sale|acquisition)\b|"
    r"\bacqui\w+ (?:certain |substantially all (?:of )?|all (?:of )?)?(?:the |its |their )?"
    r"(?:[\w-]+ ){0,3}assets\b|\bpurchase of (?:certain |substantially all (?:of )?)?(?:the |its )?"
    r"(?:[\w-]+ ){0,3}assets\b|\bassets of\b|"
    r"\bacqui\w+ (?:the |its |their )?(?:intellectual property|IP portfolio|patent portfolio|patents|"
    r"technology and assets|business and assets)\b",
    re.I,
)
ACQUIHIRE_RE = re.compile(
    r"\bacqui-?hir\w*|\btalent acquisition\b|"
    r"\bacqui\w+ (?:the |its |their )?(?:engineering |founding |core |entire |product |research )?team\b|"
    r"\bhir\w+ (?:the |its |their )?(?:entire |founding |core )?(?:team|staff|employees|engineers)\b|"
    r"\bteam (?:will|is|are|has|have) join(?:ed|ing)?\b|\bjoin(?:s|ed|ing)? [A-Z][\w.&'’-]* as part of\b",
    re.I,
)
STAKE_RE = re.compile(
    r"(?<![\d.])(?P<pct>\d{1,3}(?:\.\d+)?)\s?(?:%|percent|per cent|pct)\s+"
    r"(?:equity |economic |voting |ownership |shareholding |common |controlling |majority |minority )?"
    r"(?:stake|interest|shareholding|holding|ownership|share|of the (?:shares|equity|company))|"
    r"\b(?P<word>majority|minority|controlling|significant minority|non-controlling)\s+"
    r"(?:equity |economic |ownership |shareholding )?(?:stake|interest|shareholding|holding|position|"
    r"investment)\b|\bstrategic (?:minority )?investment\b|\bstrategic minority\b|"
    r"\b(?P<remaining>remaining)\s+(?:\d{1,3}(?:\.\d+)?\s?%\s+)?(?:stake|interest|shares|equity)\b",
    re.I,
)
SPONSOR_RE = re.compile(
    r"\bprivate[- ]equity\b|\bPE\b (?:firm|fund|sponsor|group|house)|\bbuyout (?:firm|fund|group|shop)\b|"
    r"\bfinancial sponsor\b|\bleveraged buy-?out\b|\bLBO\b|\bmanagement buy-?out\b|\bMBO\b|"
    r"\bconsortium\b|\binfrastructure fund\b|\bsovereign wealth fund\b",
    re.I,
)
REVERSE_MERGER_RE = re.compile(r"\breverse (?:merger|takeover)\b|\bRTO\b", re.I)
ACTIVIST_RE = re.compile(r"\bactivist\b", re.I)
CROSS_BORDER_RE = re.compile(
    r"\bCFIUS\b|\bCommittee on Foreign Investment\b|\bcross-border\b|\bforeign (?:direct )?investment "
    r"(?:review|approval|screening|clearance|regime|law|rules)\b|\bFDI\b|\bnational security review\b|"
    r"\bforeign (?:buyer|acquirer|bidder|takeover)\b",
    re.I,
)
ANTITRUST_CONCERN_RE = re.compile(
    r"\bantitrust (?:concerns?|scrutiny|objections?|challenge|lawsuit|suit|probe|hurdles?)\b|"
    r"\bregulatory (?:concerns?|scrutiny|hurdles?|pushback|challenge|risk)\b|"
    r"\b(?:FTC|DOJ|CMA|EC|European Commission|SAMR|regulators?) (?:has |have |had )?(?:sued|filed suit|"
    r"challenged|blocked|opposed|objected|raised concerns|voiced concerns|moved to block|is probing|"
    r"opened an? (?:in-depth |phase[- ](?:2|II|two) |formal )?(?:investigation|probe|review))\b|"
    r"\bsecond request\b|\bphase[- ](?:2|II|two)\b|\bin-depth (?:investigation|review|probe)\b|"
    r"\bstatement of objections\b|\bblocked (?:the|by)\b|\bprohibit(?:ed|ion)\b|\bremedies\b|"
    r"\bdivestitures? (?:required|to (?:win|secure|obtain))\b|\bconcentration\b[^.]{0,30}\bmarket\b|"
    r"\bmarket share\b[^.]{0,40}\bconcern",
    re.I,
)


def _first(regex, text):
    m = regex.search(text)
    return m.group(0) if m else None


def classify_deal(text):
    """Map phrasing to SKILL.md deal_type (+ finer deal_structure, tags, risk flags).

    Precedence when several cue families match (all matches are listed in the
    trace so the reader can override): joint venture (out of scope) > spinoff >
    divestiture > go_private > merger (merger-of-equals always; otherwise only
    when no acquisition cue is present) > acquisition (tender-offer > asset-deal
    > acqui-hire > stake > stock-purchase).
    """
    trace, tags, flags = [], [], []
    hits = {
        "joint-venture": _first(JV_RE, text),
        "spinoff": _first(SPINOFF_RE, text),
        "divestiture": _first(DIVEST_RE, text),
        "go_private": _first(GO_PRIVATE_RE, text),
        "merger": _first(MERGER_RE, text),
        "acquisition": _first(ACQ_RE, text),
    }
    for k in ("joint-venture", "spinoff", "divestiture", "go_private", "merger", "acquisition"):
        if hits[k]:
            trace.append("cue %s: %r" % (k, hits[k]))
    deal_type, structure, out_of_scope = None, None, False
    if hits["joint-venture"] and not hits["acquisition"]:
        structure, out_of_scope = "joint-venture", True
        tags.append("joint-venture")
        trace.append("deal_type: joint venture is an organic partnership -> out of scope per SKILL.md "
                     "'When to invoke' (deal_type omitted)")
    elif hits["spinoff"]:
        deal_type, structure = "spinoff", "spin-off"
        trace.append("deal_type: 'spin-off/spin-out/separation' -> spinoff (SKILL.md step 1)")
    elif hits["divestiture"]:
        deal_type, structure = "divestiture", "divestiture"
        trace.append("deal_type: 'divests / sells {division} to' -> divestiture (SKILL.md step 1)")
        if CARVE_OUT_RE.search(text):
            tags.append("carve-out")
            structure = "carve-out"
    elif hits["go_private"]:
        deal_type, structure = "go_private", "take-private"
        trace.append("deal_type: 'go-private / take private / LBO' -> go_private (SKILL.md step 1)")
    elif hits["merger"] and (MERGER_EQUALS_RE.search(text) or not hits["acquisition"]):
        deal_type = "merger"
        if MERGER_EQUALS_RE.search(text):
            structure = "merger-of-equals"
            tags.append("merger-of-equals")
            trace.append("deal_type: 'merger of equals' -> merger (SKILL.md step 1)")
        else:
            structure = "merger"
            trace.append("deal_type: 'merge/combine with' and no acquire cue -> merger (SKILL.md step 1)")
    elif hits["acquisition"] or hits["merger"]:
        deal_type = "acquisition"
        if hits["merger"] and not MERGER_EQUALS_RE.search(text):
            trace.append("deal_type: 'merger' wording with an acquire cue -> acquisition "
                         "(only 'merger of equals'/'combines with' maps to merger)")
        else:
            trace.append("deal_type: acquire/buy/purchase/takeover cue -> acquisition (SKILL.md step 1)")
    else:
        trace.append("deal_type: no deal-type cue matched (omitted, not guessed)")

    # finer structure for acquisitions / go-privates
    if deal_type in ("acquisition", "go_private"):
        stake = STAKE_RE.search(text)
        if TENDER_RE.search(text):
            tags.append("tender-offer")
            if deal_type == "acquisition":
                structure = "tender-offer"
            trace.append("structure: tender/exchange offer cue %r" % _first(TENDER_RE, text))
        if ASSET_RE.search(text):
            tags.append("asset-deal")
            if deal_type == "acquisition" and structure is None:
                structure = "asset-deal"
            trace.append("structure: 'acquires assets of' -> asset purchase, tag asset-deal (SKILL.md step 1: "
                         "asset deals usually do not transfer liabilities)")
        if ACQUIHIRE_RE.search(text):
            tags.append("acqui-hire")
            if deal_type == "acquisition" and structure is None:
                structure = "acqui-hire"
            trace.append("structure: acqui-hire cue %r" % _first(ACQUIHIRE_RE, text))
        if stake:
            pct = stake.group("pct")
            word = (stake.group("word") or "").lower()
            if stake.group("remaining"):
                tags.append("buy-in-remaining")
                trace.append("structure: 'remaining stake' -> buying out the rest (full ownership)")
            elif pct is not None:
                p = float(pct)
                if p >= 100:
                    trace.append("structure: 100%% -> full acquisition")
                elif p > 50:
                    tags.append("majority-stake")
                    if deal_type == "acquisition" and structure is None:
                        structure = "majority-stake"
                    trace.append("structure: %s%% stake (>50) -> majority stake (change of control)" % pct)
                else:
                    tags.append("minority-stake")
                    if deal_type == "acquisition" and structure is None:
                        structure = "minority-stake"
                    trace.append("structure: %s%% stake (<=50) -> minority stake / strategic investment "
                                 "(no change of control%s)" % (pct, "; 50/50 — control ambiguous" if p == 50 else ""))
            elif word in ("majority", "controlling"):
                tags.append("majority-stake")
                if deal_type == "acquisition" and structure is None:
                    structure = "majority-stake"
                trace.append("structure: '%s stake' -> majority stake" % word)
            else:
                tags.append("minority-stake")
                if deal_type == "acquisition" and structure is None:
                    structure = "minority-stake"
                trace.append("structure: %r -> minority stake / strategic investment (no change of control)"
                             % stake.group(0))
        if structure is None and deal_type == "acquisition":
            structure = "stock-purchase"
            trace.append("structure: default stock purchase (all outstanding shares)")

    # risk flags (SKILL.md step 5 controlled vocabulary)
    if HOSTILE_RE.search(text) and (deal_type in ("acquisition", "go_private") or TENDER_RE.search(text)):
        flags.append("hostile-bid")
        trace.append("risk_flag hostile-bid: %r" % _first(HOSTILE_RE, text))
    if deal_type == "go_private" and SPONSOR_RE.search(text):
        flags.append("sponsor-backed")
        trace.append("risk_flag sponsor-backed: %r" % _first(SPONSOR_RE, text))
    if CROSS_BORDER_RE.search(text):
        flags.append("cross-border")
        trace.append("risk_flag cross-border: %r" % _first(CROSS_BORDER_RE, text))
    if ANTITRUST_CONCERN_RE.search(text):
        flags.append("antitrust-concern")
        trace.append("risk_flag antitrust-concern: %r" % _first(ANTITRUST_CONCERN_RE, text))
    if ACTIVIST_RE.search(text):
        flags.append("activist-contested")
        trace.append("risk_flag activist-contested: 'activist'")
    if REVERSE_MERGER_RE.search(text):
        flags.append("reverse-merger")
        trace.append("risk_flag reverse-merger: %r" % _first(REVERSE_MERGER_RE, text))
    return {
        "deal_type": deal_type,
        "deal_structure": structure,
        "deal_tags": sorted(set(tags)),
        "risk_flags": sorted(set(flags)),
        "out_of_scope": out_of_scope,
        "trace": trace,
    }


# --- status classification (SKILL.md step 3) -----------------------------------

CONDITIONAL_BEFORE_RE = re.compile(
    r"\b(?:may|might|could|can|would|will|shall|should|unless|if|upon|in the event of|event of|"
    r"in connection with|following|prior to|before|right to|able to|entitled to|option to|either party|"
    r"case of|circumstances|payable (?:on|upon)|not|never|to)\b[^.]{0,25}$",
    re.I,
)
CONDITIONAL_AFTER_RE = re.compile(
    r"^\s*(?:under certain circumstances|in certain circumstances|if\b|in the event|should\b|"
    r"in specified circumstances)", re.I)
TERMINATED_RE = re.compile(
    r"\b(?:has|have|had|was|were|been|is|are|mutually|jointly|formally|officially)\s+(?:been\s+)?"
    r"terminated\b|"
    r"\bterminated (?:the|its|their|our|a|an) (?:[\w-]+ ){0,3}(?:agreement|deal|transaction|merger|"
    r"acquisition|offer|bid|talks|discussions)\b|\bagreed to terminate\b|\bdecided to terminate\b|"
    r"\btermination of (?:the|its|their) (?:[\w-]+ ){0,3}(?:agreement|deal|transaction)\b|"
    r"\bcalled off\b|\bcalls off\b|\babandon(?:ed|s|ing)? (?:its |the |their |plans? )?(?:[\w-]+ ){0,2}"
    r"(?:deal|bid|offer|merger|acquisition|takeover|plans?|proposal|transaction|pursuit)\b|"
    r"\bwalk(?:ed|s|ing)? away from\b|\bscrapped\b|\bscraps\b|\bcollapsed\b|"
    r"\bwithdr(?:ew|awn|aws) (?:its |the |their )?(?:[\w-]+ ){0,2}(?:offer|bid|proposal)\b|"
    r"\bfell through\b|\bfalls through\b|\bmutually agreed to end\b|\bagreed to end (?:the|their)\b",
    re.I,
)
_DEAL_NOUN = (r"(?:acquisition|merger|purchase|takeover|buyout|deal|transaction|combination|tender offer|"
              r"sale|divestiture|spin-?off|separation|offer)")
CLOSED_RES = [
    re.compile(r"\b(?:completed|completes|closed|closes|consummated|finali[sz]ed|finali[sz]es|concluded)\s+"
               r"(?:\S+\s+){0,4}?" + _DEAL_NOUN + r"\b", re.I),
    re.compile(_DEAL_NOUN + r"\s+(?:of\s+(?:\S+\s+){1,6}?)?(?:has|have|had|is|are|was|were)\s+"
               r"(?:now\s+|been\s+|successfully\s+|officially\s+|formally\s+)*"
               r"(?:completed|closed|consummated|finali[sz]ed|concluded)\b", re.I),
    re.compile(r"\bnow (?:a )?wholly[- ]owned subsidiary\b|\bbecame (?:a )?wholly[- ]owned subsidiary\b|"
               r"\bis now (?:a )?(?:part|subsidiary|division) of\b|"
               r"\bannounced (?:today )?(?:the )?(?:successful )?completion of\b|"
               r"\bsuccessfully (?:completed|closed)\b", re.I),
]
FUTURE_BEFORE_RE = re.compile(
    r"\b(?:expected|expects?|anticipated|anticipates?|will|would|should|to|slated|scheduled|targeted|"
    r"projected|on track|once|when|if|until|before|prior to|upon|not|yet|had not|hadn't|hasn't|haven't|"
    r"has not|have not|is to be|are to be|likely)\b[^.]{0,14}$",
    re.I,
)
CONTESTED_RE = re.compile(
    r"\bcounter-?bids?\b|\bcounter-?offers?\b|\brival (?:bid|offer|proposal|suitor|bidder)s?\b|"
    r"\bcompeting (?:bid|offer|proposal)s?\b|\bbidding war\b|\bactivist (?:investor|shareholder|"
    r"hedge fund|fund|campaign)\b|\bproxy (?:fight|battle|contest)\b|"
    r"\burg(?:ed|es|ing) (?:shareholders|investors|stockholders) to (?:vote against|reject)\b|"
    r"\bvote against the (?:deal|merger|transaction|acquisition)\b|"
    r"\boppos(?:e|es|ed|ing) the (?:deal|merger|transaction|takeover|acquisition|offer|bid)\b|"
    r"\bopposition to the (?:deal|merger|transaction|takeover|bid)\b|"
    r"\brejected (?:the|an?) (?:unsolicited |revised |latest |sweetened |hostile |takeover |initial |"
    r"non-binding )?(?:offer|bid|proposal|approach)\b|\bboard (?:has )?rejected\b|\brebuffed\b|"
    r"\btopping bid\b|\bhigher (?:offer|bid) from\b|\bhostile\b",
    re.I,
)
STRONG_ANNOUNCED_RE = re.compile(
    r"\bdefinitive (?:merger |purchase |acquisition |transaction )?agreement\b|\bmerger agreement\b|"
    r"\bbinding agreement\b|\bshare purchase agreement\b|\basset purchase agreement\b|"
    r"\bagreed to (?:acquire|buy|purchase|be acquired|merge|combine|sell|divest|take)\b|"
    r"\b(?:has|have) agreed to\b|\bentered into (?:a|an) (?:definitive |binding |merger |purchase |"
    r"share purchase |asset purchase |stock purchase )?agreement\b|"
    r"\bsigned (?:a|an) (?:definitive |binding |merger |purchase |share purchase )?agreement\b|"
    r"\breached (?:a|an) (?:definitive |binding )?agreement\b|\bagreement to (?:acquire|be acquired|merge|"
    r"combine|sell)\b|\bunanimously approved by (?:the )?boards?\b|"
    r"\bboards? of directors (?:of both companies )?(?:has|have) (?:unanimously )?approved\b|"
    r"\bannounces? (?:agreement|definitive agreement|acquisition of|the acquisition|merger agreement)\b|"
    r"\bannounced (?:today )?(?:that )?(?:it|they) (?:has|have|had) (?:agreed|entered|signed|reached)\b|"
    r"\bcompletes?\b|\bcompleted\b|\bagreed to a (?:merger|combination|deal)\b|"
    r"\b(?:launched|commenced|commences|launches) (?:a|an|its) (?:[\w-]+ )?(?:tender|exchange) offer\b",
    re.I,
)
WEAK_ANNOUNCED_RE = re.compile(
    r"\bto (?:acquire|buy|purchase|merge|combine|take over|take private|divest|sell|spin off|spin out)\b|"
    r"\b(?:will|would) (?:acquire|buy|purchase|merge|combine|take over|take private|divest|sell)\b|"
    r"\b(?:acquires|buys|purchases|takes over|is acquiring|are acquiring|is buying|snaps up|"
    r"agrees to|plans to acquire|plans to buy|announced (?:the|a|an|its) (?:acquisition|purchase|"
    r"takeover|merger|deal|transaction)|announces)\b|"
    r"\b(?:launched|launches|commenced|commences|made|makes) (?:a|an|its) (?:[\w-]+ ){0,2}(?:tender offer|"
    r"offer|bid|proposal)\b|\bin an? (?:all-cash |all-stock |cash |stock |cash-and-stock )?(?:deal|transaction)\b|"
    r"\bvalued at\b|\bacquired\b|\bbought\b",
    re.I,
)
PENDING_RE = re.compile(
    r"\bawaiting (?:regulatory |antitrust |shareholder |stockholder |HSR |CFIUS |CMA |EC |EU |SAMR |FTC |DOJ |"
    r"government |court |final |remaining )?(?:approval|clearance|review|sign-?off|consent)s?\b|"
    r"\bpending (?:regulatory |antitrust |shareholder |stockholder |HSR |CFIUS |CMA |EC |EU |SAMR |FTC |DOJ |"
    r"government |court |final |customary )?(?:approval|clearance|review|sign-?off|closing conditions)s?\b|"
    r"\bunder (?:regulatory |antitrust |competition |CMA |EC |EU |FTC |DOJ |SAMR |CFIUS |in-depth |"
    r"phase[- ](?:2|II|two) |formal )?(?:review|scrutiny|investigation|examination)\b|"
    r"\bsecond request\b|\bphase[- ](?:2|II|two|1|I|one) (?:review|investigation|probe)\b|"
    r"\bin-depth (?:investigation|review|probe)\b|"
    r"\bregulators? (?:is|are|were|has|have) (?:still )?(?:reviewing|examining|probing|scrutini[sz]ing|"
    r"investigating|assessing)\b|\bregulatory approvals? (?:is|are|remains?) (?:still )?(?:pending|outstanding)\b|"
    r"\bremains? subject to\b|\bstill (?:needs?|requires?|awaits?|subject to|pending)\b|"
    r"\b(?:has|have) (?:yet|not yet|still not) (?:to )?(?:receive|received|clear|cleared|obtain|obtained|"
    r"secure|secured|win|won)\b|\byet to (?:be )?(?:approved|cleared|receive|obtain|close|complete)\b|"
    r"\bextended the (?:review|deadline|waiting period)\b|"
    r"\bfiled (?:for|its|the) (?:HSR|antitrust|merger|regulatory) (?:approval|clearance|notification|filing)\b|"
    r"\bregulatory (?:review|process) (?:is )?(?:ongoing|continues|underway)\b|"
    r"\bopened (?:an|a) (?:in-depth |phase[- ](?:2|II|two) |formal )?(?:investigation|probe|review) into\b|"
    r"\b(?:cleared|approved|received (?:approval|clearance) from) [^.]{0,60}\b(?:but|however|while|although) "
    r"[^.]{0,60}\b(?:still|awaits?|pending|remain)",
    re.I,
)
RUMOR_RE = re.compile(
    r"\bsources? (?:say|said|says|tell|told|familiar)\b|\bpeople familiar\b|\bperson familiar\b|"
    r"\baccording to (?:people|sources|a person|two people|three people|several people|reports?|a report|"
    r"media reports)\b|\breportedly\b|\bis said to be\b|\bare said to be\b|"
    r"\bin (?:advanced |early |exclusive |preliminary |active |ongoing )?(?:talks|discussions|negotiations)\b|"
    r"\bexploring (?:a (?:sale|deal|bid|takeover|combination|merger)|options|strategic alternatives|"
    r"strategic options)\b|\bweighing (?:a |an )?(?:bid|offer|sale|deal|takeover|acquisition|options)\b|"
    r"\bconsidering (?:a |an )?(?:bid|offer|sale|deal|takeover|acquisition|acquiring|buying)\b|"
    r"\bmulling\b|\bnearing (?:a |an )?(?:deal|agreement)\b|"
    r"\bclose to (?:a deal|an agreement|agreeing|clinching|acquiring|buying)\b|\bclosing in on\b|"
    r"\bcould (?:be )?announce\w*\b|\bmay (?:be )?announce\w*\b|\brumou?rs?\b|\brumou?red\b|"
    r"\bspeculation\b|\bhas approached\b|\bapproached (?:[A-Z][\w.&'’-]* )?(?:about|over|regarding|with)\b|"
    r"\bmade an approach\b|\bpreliminary (?:talks|discussions|approach)\b|"
    r"\bpotential (?:takeover|sale|bid|offer|acquisition of)\b|\bpossible (?:takeover|sale|bid|offer)\b|"
    r"\bdeclined to comment\b|\bdid not (?:immediately )?respond to (?:a )?requests? for comment\b|"
    r"\bcould not be (?:reached|learned|determined)\b|\bno (?:final )?decision has been made\b|"
    r"\bmay not (?:lead|result)\b|\btalks could (?:still )?(?:fall apart|collapse|founder)\b|"
    r"\bhas held talks\b|\bheld (?:preliminary |early |informal )?talks\b|\bexploring a sale\b|"
    r"\bup for sale\b|\bon the block\b|\bsale process\b|\bworking with (?:advisers|advisors|bankers) on a\b",
    re.I,
)
LOI_RE = re.compile(
    r"\bletter of intent\b|\bLOI\b|\bmemorandum of understanding\b|\bMOU\b|\bheads of (?:terms|agreement)\b|"
    r"\bterm sheet\b|\bnon-binding (?:agreement|letter|offer|proposal|indication|indicative|bid|approach|"
    r"term sheet|memorandum)\b|\bindicative (?:offer|proposal|bid)\b|\bexclusivity agreement\b|"
    r"\bpreliminary agreement\b|\bagreement in principle\b",
    re.I,
)
DEFINITIVE_RE = re.compile(r"\bdefinitive (?:merger |purchase |acquisition |transaction )?agreement\b|"
                           r"\bbinding agreement\b|\bmerger agreement\b", re.I)


def _unconditional(regex_hits, text, before_re, after_re=None):
    """Return the first regex hit not preceded by modal/conditional wording."""
    for m in regex_hits:
        before = text[max(0, m.start() - 45):m.start()]
        after = text[m.end():m.end() + 40]
        if before_re.search(before):
            continue
        if after_re is not None and after_re.search(after):
            continue
        return m
    return None


def classify_status(text):
    """Map phrasing to SKILL.md status + lifecycle stage, with the matched cues.

    Precedence: terminated > closed > contested > rumored (unless a definitive
    cue is present) > pending > announced (definitive or LOI/non-binding) > none.
    """
    trace = []
    status, stage = None, None
    strong = STRONG_ANNOUNCED_RE.search(text)
    weak = WEAK_ANNOUNCED_RE.search(text)
    rumor = RUMOR_RE.search(text)
    loi = LOI_RE.search(text)
    term = _unconditional(TERMINATED_RE.finditer(text), text, CONDITIONAL_BEFORE_RE, CONDITIONAL_AFTER_RE)
    closed = None
    for rx in CLOSED_RES:
        closed = _unconditional(rx.finditer(text), text, FUTURE_BEFORE_RE)
        if closed:
            break
    contested = CONTESTED_RE.search(text)
    pending = PENDING_RE.search(text)
    if term:
        status, stage = "terminated", "terminated"
        trace.append("status: terminated — %r" % term.group(0))
    elif closed:
        status, stage = "closed", "closed"
        trace.append("status: closed — %r (completed/closed in the past tense; 'expected to close' "
                     "does not count)" % closed.group(0))
    elif contested:
        status, stage = "contested", "contested"
        trace.append("status: contested (activist or counter-bid, SKILL.md step 3) — %r" % contested.group(0))
    elif rumor and not strong:
        stage = "rumored"
        trace.append("status: rumour cue %r without a definitive-agreement cue -> stage=rumored; 'rumored' is "
                     "not a SKILL.md status, so status is omitted and review_required is set (corroborate first)"
                     % rumor.group(0))
    elif pending:
        status, stage = "pending", "pending-regulatory"
        trace.append("status: pending (regulatory review in progress) — %r" % pending.group(0))
    elif loi and not DEFINITIVE_RE.search(text):
        status, stage = "announced", "non-binding"
        trace.append("status: announced — %r is non-binding: SKILL.md anti-pattern keeps status=announced "
                     "with confidence < 60" % loi.group(0))
    elif strong:
        status, stage = "announced", "definitive-agreement"
        trace.append("status: announced (definitive agreement) — %r" % strong.group(0))
        if rumor:
            trace.append("note: rumour wording %r also present but a definitive cue wins (no penalty)"
                         % rumor.group(0))
    elif weak:
        status, stage = "announced", "definitive-agreement"
        trace.append("status: announced — %r (announcement wording; agreement type unstated)" % weak.group(0))
    else:
        trace.append("status: no status cue matched (omitted, not guessed)")
    return {"status": status, "stage": stage, "rumor_cue": rumor.group(0) if rumor else None,
            "loi_cue": loi.group(0) if loi else None, "trace": trace}


# --- consideration, exchange ratio, premium (SKILL.md step 2) -------------------

CASH_RE = re.compile(
    r"\ball[- ]cash\b|\bin cash\b|\bcash (?:deal|transaction|offer|consideration|purchase|price|payment|"
    r"tender offer|bid|merger|acquisition)\b|\bfor cash\b|\bcash-?only\b|\bpaid in cash\b|"
    r"\bfunded (?:with|through|by|from) (?:existing )?(?:cash|debt|cash on hand|balance sheet)\b",
    re.I,
)
STOCK_RE = re.compile(
    r"\ball[- ]stock\b|\ball[- ]share\b|\bstock[- ]for[- ]stock\b|\bshare[- ]for[- ]share\b|\bstock swap\b|"
    r"\bshare swap\b|\bshare exchange\b|\bin (?:common |ordinary )?(?:stock|shares)\b(?! of)|"
    r"\bexchange ratio\b|\bstock (?:deal|transaction|consideration|merger|component)\b|"
    r"\bnewly[- ]issued shares\b|\bpaid in (?:stock|shares)\b|\bequity consideration\b|"
    r"(?<![\d,.])(?:0?\.\d+|\d{1,2}(?:\.\d+)?)\s(?:new\s+|newly[- ]issued\s+)?(?:shares?|ADSs?|common shares?|"
    r"ordinary shares?) (?:of|in) [A-Z]",
    re.I,
)
MIXED_RE = re.compile(
    r"\bcash[- ]and[- ]stock\b|\bstock[- ]and[- ]cash\b|\bcash and shares\b|\bmixed consideration\b|"
    r"\bcombination of cash and (?:stock|shares)\b|\bcash plus (?:stock|shares)\b|\bpart cash\b|"
    r"\bcash-and-share\b|\bcash and share\b|\bcash and equity\b|\bcash and (?:[\w-]+ ){0,3}(?:shares|stock)\b",
    re.I,
)
EARNOUT_RE = re.compile(
    r"\b(?:earn-?outs?|contingent (?:value rights?|consideration|payments?|milestone payments?)|"
    r"milestone payments?|CVRs?|deferred consideration)\b(?: (?:of|worth|totaling|totalling))?"
    r"(?: up to)?(?: (?:approximately|about|~))?(?: (?:US\$|\$|€|£)?[\d.,]+\s?(?:billion|million|bn|mn|m|b)?)?",
    re.I,
)
RATIO_RES = [
    re.compile(r"(?<![\d,.])(?P<ratio>0?\.\d+|\d{1,2}(?:\.\d+)?)\s+(?:new\s+|newly[- ]issued\s+)?"
               r"(?:common\s+|ordinary\s+)?(?:shares?|ADSs?)\s+(?:of\s+|in\s+)?"
               r"(?P<issuer>(?:[A-Z][\w.&'’-]*\s+){0,4}?)(?:common\s+stock\s+|ordinary\s+shares?\s+|stock\s+|"
               r"class\s+[A-Z]\s+(?:common\s+)?(?:stock|shares?)\s+)?(?:for|per)\s+(?:each|every)?\s*"
               r"(?:outstanding\s+|common\s+|ordinary\s+|issued\s+)?(?:share|ADS)"),
    re.compile(r"\bexchange ratio of\s+(?:approximately\s+|about\s+)?(?P<ratio>0?\.\d+|\d{1,2}(?:\.\d+)?)", re.I),
    re.compile(r"(?<![\d,.])(?P<ratio>0?\.\d+|\d{1,2}(?:\.\d+)?)x?\s+(?:shares?|ADSs?)\s+(?:for|per)\s+"
               r"(?:each|every)?\s*(?:share|ADS)", re.I),
]
STATED_PREMIUM_RE = re.compile(
    r"premium of (?:approximately |about |roughly |around |~|nearly |some )?(?P<p1>\d+(?:\.\d+)?)\s?"
    r"(?:%|percent|per cent)|(?P<p2>\d+(?:\.\d+)?)\s?(?:%|percent|per cent)\s+premium",
    re.I,
)


def parse_exchange_ratio(text):
    """Return (ratio, issuer_name_or_None) or (None, None)."""
    for rx in RATIO_RES:
        m = rx.search(text)
        if m:
            issuer = m.groupdict().get("issuer")
            issuer = issuer.strip() if issuer else None
            return float(m.group("ratio")), (issuer or None)
    try:
        return float(text.strip()), None
    except ValueError:
        return None, None


def parse_consideration(text, amounts=None):
    """Consideration type/detail from phrasing (SKILL.md step 2)."""
    amounts = parse_money(text) if amounts is None else amounts
    trace, res = [], {}
    cash = CASH_RE.search(text)
    stock = STOCK_RE.search(text)
    mixed = MIXED_RE.search(text)
    ratio, issuer = parse_exchange_ratio(text)
    if ratio is not None and not RATIO_RES[0].search(text) and not RATIO_RES[1].search(text) \
            and not RATIO_RES[2].search(text):
        ratio, issuer = None, None  # bare-number fallback is for the premium command only
    per_share_offers = [a for a in amounts if a["kind"] == "per-share-offer"]
    cash_ps = per_share_offers[0] if per_share_offers else None
    if mixed or (cash and (stock or ratio is not None)) or (cash_ps and ratio is not None):
        ctype = "mixed"
        trace.append("consideration: mixed — cash cue %r + stock cue %r" % (
            cash.group(0) if cash else None, (mixed or stock).group(0) if (mixed or stock) else "exchange ratio"))
    elif stock or ratio is not None:
        ctype = "stock"
        trace.append("consideration: stock — %r" % (stock.group(0) if stock else "exchange ratio"))
    elif cash:
        ctype = "cash"
        trace.append("consideration: cash — %r" % cash.group(0))
    else:
        ctype = None
        trace.append("consideration: no cash/stock cue (omitted)")
    if ctype:
        res["consideration_type"] = ctype
    if cash_ps is not None:
        res["cash_per_share"] = cash_ps["value"]
        res["cash_per_share_currency"] = cash_ps["currency"]
    if ratio is not None:
        res["exchange_ratio"] = ratio
        if issuer:
            res["exchange_ratio_issuer"] = issuer
    detail = None
    if ctype == "cash":
        detail = "all-cash" + (" at %s/share" % _fmt_price(cash_ps) if cash_ps else "")
    elif ctype == "stock":
        detail = "all-stock" + (" at %s shares of %s per share" % (_fmt_num(ratio), issuer or "acquirer")
                                if ratio is not None else "")
    elif ctype == "mixed":
        parts = []
        if cash_ps:
            parts.append("%s cash" % _fmt_price(cash_ps))
        if ratio is not None:
            parts.append("%s shares of %s" % (_fmt_num(ratio), issuer or "acquirer"))
        detail = " + ".join(parts) + " per share" if parts else "cash and stock (split not stated)"
    earn = EARNOUT_RE.search(text)
    if earn:
        detail = (detail + "; " if detail else "") + earn.group(0).strip()
        res["earnout"] = earn.group(0).strip()
        trace.append("consideration: earnout/contingent component %r" % earn.group(0).strip())
    if detail:
        res["consideration_detail"] = detail
    res["trace"] = trace
    return res


def _fmt_num(x):
    if x is None:
        return "?"
    s = ("%.4f" % x).rstrip("0").rstrip(".")
    return s if s else "0"


def _fmt_price(amount):
    cur = amount["currency"]
    sym = {"USD": "$", "USD?": "$", "EUR": "€", "GBP": "£"}.get(cur, cur + " ")
    return "%s%.2f" % (sym, amount["value"])


def premium_pct(offer, unaffected):
    """SKILL.md step 2: (offer − unaffected) / unaffected × 100, rounded to 0.01."""
    if unaffected <= 0:
        raise ValueError("unaffected price must be > 0")
    return round((offer - unaffected) / unaffected * 100.0, 2)


def implied_value(ratio, acquirer_price, cash_per_share=0.0):
    """Implied per-share value of a stock (or mixed) offer."""
    return round(ratio * acquirer_price + (cash_per_share or 0.0), 4)


# --- parties -------------------------------------------------------------------

# Capitalised words that end (or cannot start) a company name: verbs and function
# words seen in title-case headlines, sentence starters, and reporting boilerplate.
STOP_TOKENS = (
    "To|Acquire|Acquires|Acquired|Acquiring|Acquisition|Acquisitions|Agrees|Agree|Agreed|Announces|Announce|"
    "Announced|Completes|Complete|Completed|Closes|Close|Closed|Buys|Buy|Bought|Purchase|Purchases|In|For|With|And|"
    "Merger|Mergers|Merge|Merges|Merging|Deal|Deals|Will|Has|Have|Is|Are|Was|Were|Signs|Sign|Enters|Enter|Definitive|"
    "Agreement|All-Cash|All-Stock|Stake|Take|Takes|Private|Bn|Billion|Million|The|This|That|It|On|At|As|But|Under|"
    "Terms|Shares|Stock|Stocks|Shareholders|Stockholders|Upon|After|Following|According|Sources|People|Reuters|"
    "Bloomberg|Today|Its|Their|Of|By|From|A|An|Plans|Plan|Set|Said|Says|Say|Combine|Combines|Combined|Sell|Sells|Sold|"
    "Divest|Divests|Launches|Launch|Launched|Makes|Make|Made|Offer|Offers|Bid|Bids|Tender|Talks|Nears|Weighs|Explores|"
    "Which|Who|Whose|Where|When|While|Subject|Pursuant|If|Then|Or|Nor|Not|Both|Each|Per|Approximately|About|Over|Into|"
    "Onto|Via|Toward|Towards|Through|Between|Among|Amid|Despite|Because|Since|Unless|Until|Whether|Also|Now|Then|"
    "Regulators|Regulator|Investors|Analysts|Executives|Officials|Bankers|Lawyers|Advisers|Advisors|Companies|Company|"
    "Meanwhile|However|Separately|Earlier|Later|Still|Yet|Some|Many|Several|Other|Others|No|Neither|News|Reports|"
    "Report|Antitrust|Rival|Rivals|Markets|Market|Two|Three|Four|Five|Last|Chief|Q[1-4]|H[12]|FY\\d*"
)
_TOKEN = r"(?!(?:%s)\b)[A-Z0-9][\w&.'’-]*" % STOP_TOKENS
_JOINER = r"(?:of|de|van|von|da|di|del|du|des|la|le|the|&)"
_LEGAL_TAIL = (r"(?:\s+(?:plc|inc\.?|ltd\.?|corp\.?|co\.?|gmbh|s\.a\.|n\.v\.|s\.p\.a\.|srl|llc|lp|l\.p\.|ag|"
               r"ab|asa|oyj?|nv|sa|se|bv|pty|limited|holdings|group)\b\.?)?"
               r"(?:,\s+(?:Inc\.?|Incorporated|LLC|L\.L\.C\.|Ltd\.?|Limited|L\.P\.|LP|Corp\.?|Co\.?|N\.V\.|S\.A\.|"
               r"plc|PLC|AG|SE)(?![\w&])\.?)?")
NAME = r"(?:The\s+)?%s(?:\s+(?:%s|%s\s+%s))*%s" % (_TOKEN, _TOKEN, _JOINER, _TOKEN, _LEGAL_TAIL)
NAME_A = r"(?P<A>%s)" % NAME
NAME_T = r"(?P<T>%s)" % NAME
NAME_S = r"(?P<S>%s)" % NAME
# optional "(NASDAQ: XXXX)" ticker and/or ", a leading maker of widgets," appositive after a name
_APPOS = r"(?:\s*\([^()]{0,60}\))?(?:,\s+(?:a|an|the|one of|which is|based in|maker of|owner of)\s[^,]{0,100},)?"

# words that may sit between the acquirer's name and the acquisition verb (case-insensitive)
_LEAD_WORD = (
    r"(?:has|have|had|is|are|was|were|will|would|to|today|also|formally|officially|now|again|"
    r"agreed|agrees|agreeing|plans?|planned|planning|intends?|intended|seeks?|sought|aims?|wants?|hopes?|expects?|"
    r"proposes?|proposed|offers?|offered|decided|opted|voted|moved|moves|set|poised|preparing|looking|seeking|"
    r"struck|reached|inked|unveiled|announced|announces|signed|signs|entered into|enters into|clinched|"
    r"said|says|confirmed|confirms|disclosed|revealed|that|it|they|the company|"
    r"terminated|abandoned|scrapped|called off|dropped|withdrew|ended|walked away from|halted|suspended|shelved|"
    r"cancelled|canceled|completed|closed|finali[sz]ed|failed in|lost|won|"
    r"(?:a|an|its|the|their)\s+(?:[\w$€£.,-]+\s+){0,3}?(?:deal|agreement|transaction|plans?|acquisition|purchase|"
    r"takeover|offer|proposal|bid|merger agreement|definitive agreement|tender offer|talks|intention|effort|attempt|"
    r"pursuit|move|approach|option|right)|"
    r"(?:on|in|earlier|late|last)\s+\w+|in a deal|in an agreement|under which|pursuant to which|whereby)"
)
_LEAD = r"(?:%s\s+){0,8}?" % _LEAD_WORD
_ACQ_VERB = (r"(?:acquire|acquires|acquired|acquiring|buy|buys|bought|buying|purchase|purchases|purchased|"
             r"purchasing|take over|takes over|took over|snap up|snaps up|snapped up|take private|"
             r"takes private|took private|be acquiring|acqui-?hire[sd]?|acquihire[sd]?)")
_OBJ_PREFIX = (
    r"(?:all\s+(?:of\s+)?(?:the\s+)?(?:outstanding\s+|issued\s+and\s+outstanding\s+)?(?:common\s+)?(?:shares|stock)\s+"
    r"of\s+|(?:the\s+|a\s+|an\s+)?(?:remaining\s+)?(?:approximately\s+|about\s+)?\d{1,3}(?:\.\d+)?\s?(?:%|percent|"
    r"per cent)\s+(?:equity\s+|economic\s+)?(?:stake|interest|shareholding|holding)\s+in\s+|(?:a\s+)?(?:majority|"
    r"minority|controlling|significant minority)\s+(?:stake|interest|shareholding)\s+in\s+|(?:substantially\s+all\s+"
    r"(?:of\s+)?(?:the\s+)?assets\s+of\s+)|(?:certain\s+assets\s+of\s+)|(?:the\s+assets\s+of\s+)|(?:the\s+)?team\s+"
    r"(?:behind|of|at|from)\s+|(?:the\s+)?(?:privately[- ]held|publicly[- ]traded|listed|nasdaq-listed|nyse-listed|"
    r"[\w.]+-based|its\s+(?:smaller\s+|larger\s+|bigger\s+)?(?:rival|competitor|peer)|rival|competitor|peer|startup|"
    r"start-up|chipmaker|drugmaker|software maker|retailer|lender|insurer|carrier|miner|toolmaker|automaker|biotech|"
    r"fintech)\s+)?"
)

PARTY_PATTERNS = [
    # (name, regex, parties confidence)
    ("completes", re.compile(
        NAME_A + _APPOS + r"(?i:\s+(?:has\s+|have\s+|today\s+|also\s+)*(?:announced (?:today )?(?:the |that it has )?"
        r"(?:completed|completes|completion of|closing of|closed)|completed|completes|closed|closes|finali[sz]ed|"
        r"finali[sz]es|consummated)\s+(?:its\s+|the\s+|their\s+)?(?:previously[- ]announced\s+|pending\s+|"
        r"proposed\s+|planned\s+)?(?:\S+\s+){0,2}?(?:acquisition|purchase|takeover|merger|buyout|deal|transaction|"
        r"tender offer)\s+(?:of|with|for)\s+)" + NAME_T), "high"),
    ("divests", re.compile(
        NAME_S + _APPOS + r"(?i:\s+(?:has\s+|have\s+)?(?:agreed|plans|intends|is|will|to|announced (?:that )?it "
        r"(?:will|would|has agreed to))?\s*(?:to\s+)?(?:sell|sells|sold|selling|divest|divests|divested|divesting|"
        r"dispose of|offload)\s+(?:its\s+|the\s+|a\s+|their\s+)?)(?P<T>[^.]{0,50}?\b(?:unit|division|business|"
        r"subsidiary|arm|operations|assets|brand|portfolio|segment|stake|interest|shares|plant|factory|mine|refinery|"
        r"pipeline|network|holdings|franchise|activities)\b[^.]{0,30}?)\s+to\s+" + NAME_A + r"(?=[\s,.;]|$)"), "medium"),
    ("acquired_by", re.compile(
        NAME_T + _APPOS + r"(?i:\s+(?:has\s+|have\s+|had\s+)?(?:agreed|is|are|was|were|will be|would be|to be|being|"
        r"been|has been|have been|is set|is to be|announced (?:today )?(?:that )?it (?:has|had|will be|would be))?"
        r"\s*(?:to\s+)?(?:be\s+)?(?:acquired|bought|purchased|taken over|taken private|snapped up)\s+by\s+)" + NAME_A),
     "high"),
    ("sold_to", re.compile(
        NAME_T + _APPOS + r"(?i:\s+" + _LEAD + r"(?:sell|sold|selling)\s+"
        r"(?:the company|itself|the business|all of its shares)\s+to\s+)" + NAME_A), "high"),
    ("acquisition_of_by", re.compile(
        r"(?i:(?:acquisition|takeover|purchase|buyout) of\s+)" + NAME_T + r"(?i:\s+by\s+)" + NAME_A), "high"),
    ("possessive", re.compile(
        NAME_A + r"(?:'s|’s)(?i:\s+(?:proposed\s+|planned\s+|pending\s+|(?:US\$|\$|€|£)[\d.,]+\s?(?:billion|million|"
        r"bn|mn|m|b)?\s+)*(?:acquisition|takeover|purchase|buyout|bid for|offer for|tender offer for)\s+(?:of\s+)?)"
        + NAME_T), "high"),
    ("acquires", re.compile(
        NAME_A + r"(?:'s|’s)?" + _APPOS + r"(?i:\s+" + _LEAD + _ACQ_VERB + r"\s+" + _OBJ_PREFIX + r")" + NAME_T), "high"),
    ("tender", re.compile(
        NAME_A + _APPOS + r"(?i:\s+(?:has\s+|have\s+|today\s+)?(?:launched|launches|commenced|commences|made|makes|"
        r"announced|submitted|submits|raised|raises|is making|is launching)\s+(?:a|an|its)?\s*(?:(?:hostile|"
        r"unsolicited|revised|sweetened|final|non-binding|preliminary|cash|all-cash|all-stock|takeover|formal|public|"
        r"friendly|improved|increased|higher|new)\s+|(?:US\$|\$|€|£)[\d.,]+\s?(?:billion|million|bn|mn|m|b)?"
        r"(?:-per-share|-a-share|/share| per share| a share)?\s+)*(?:tender offer|offer|bid|proposal|takeover bid|"
        r"takeover offer)\s+(?:for|to acquire|to buy)\s+(?:all\s+(?:of\s+)?(?:the\s+)?outstanding\s+shares\s+of\s+)?)"
        + NAME_T), "high"),
    ("consideration_flow", re.compile(
        NAME_T + r"(?i:\s+(?:stockholders|shareholders)\s+(?:will|would|shall|are entitled to)\s+receive\s+"
        r".{0,80}?\s+(?:shares?|stock|ADSs?)\s+of\s+)" + NAME_A), "medium"),
    ("merge_and", re.compile(
        NAME_A + r"\s+and\s+" + NAME_T + r"(?i:\s+(?:have\s+|has\s+|today\s+)*(?:agreed|announced|plan|plans|are set|"
        r"are|to|will|would|said they would)?\s*(?:to\s+)?(?:merge|combine|a merger|an all-stock merger|"
        r"a merger of equals|a definitive merger agreement))"), "low"),
    ("merge_with", re.compile(
        NAME_A + _APPOS + r"(?i:\s+(?:has\s+|have\s+)?(?:agreed|plans|is|will|would|to|is set)?\s*(?:to\s+)?"
        r"(?:merge|merges|merged|merging|combine|combines|combined|combining)\s+with\s+)" + NAME_T), "low"),
    ("merger_of", re.compile(
        r"(?i:merger (?:of|between)\s+)" + NAME_A + r"\s+and\s+" + NAME_T), "low"),
    ("talks", re.compile(
        NAME_A + _APPOS + r"(?i:\s+(?:is|are|was|were|has|have|reportedly|said to be)?\s*(?:reportedly\s+)?"
        r"(?:in\s+(?:advanced|early|exclusive|preliminary|active)?\s*(?:talks|discussions|negotiations)|exploring|"
        r"weighing|considering|nearing a deal|close to a deal|closing in on a deal|has approached|approached|"
        r"mulling|is nearing|nearing)\s+(?:a\s+(?:deal|bid|offer|takeover|possible deal|potential deal)\s+)?"
        r"(?:to\s+|for\s+|about\s+|on\s+|over\s+|with\s+)?(?:acquire|acquiring|buy|buying|purchase|take over|"
        r"a takeover of|a bid for|merge with|merging with|combining with|combine with)?\s*)" + NAME_T), "medium"),
]
TARGET_ONLY_PATTERNS = [
    ("exploring_sale", re.compile(
        NAME_T + _APPOS + r"(?i:\s+(?:is\s+|has\s+been\s+|was\s+)?(?:exploring|weighing|considering|has put itself up "
        r"for|put itself up for|is up for)\s+(?:a\s+)?(?:sale|options|strategic alternatives|a sale of itself|offers|"
        r"a takeover))"), "medium"),
]
ABBREV_TAIL = ("inc", "corp", "co", "ltd", "jr", "sr", "s.a", "n.v", "plc", "llc", "l.p", "lp", "s.p.a", "bros",
               "st", "mt")
SENTENCE_BREAK_RE = re.compile(r"\b(?:Inc|Corp|Co|Ltd|plc|LLC|Bros|N\.V|S\.A|L\.P|GmbH|AG|SE|SA|NV|Jr|Sr)\.(?=\s+[A-Z])")


def clean_name(s):
    if not s:
        return None
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^(?:its|their|the)\s+", "", s, flags=re.I) if re.match(r"(?:its|their)\s", s, re.I) else s
    m = SENTENCE_BREAK_RE.search(s)  # "Bar Inc. The deal ..." -> "Bar Inc."
    if m:
        s = s[:m.end()]
    s = s.strip(" ,;:")
    s = re.sub(r"(?:'s|’s)$", "", s)
    if s.endswith("."):
        last = s[:-1].split()[-1].lower() if s[:-1].split() else ""
        if last.rstrip(".") not in ABBREV_TAIL:
            s = s[:-1]
    # drop a trailing joiner left by a greedy match ("Bank of")
    s = re.sub(r"\s+(?:of|de|van|von|da|di|del|du|des|la|le|the|&)$", "", s, flags=re.I)
    return s or None


_BARE_SUFFIX_RE = re.compile(r"^(?:Inc|Corp|Co|Ltd|LLC|LP|plc|PLC|AG|SE|SA|NV|GmbH|Group|Holdings|Limited|Company)\.?$",
                             re.I)


def _looks_like_name(s):
    return bool(s) and 1 <= len(s.split()) <= 8 and not re.fullmatch(r"[\d.,%$]+", s) and not _BARE_SUFFIX_RE.match(s)


def _same_entity(a, b):
    """True when two name strings refer to the same company (shared first token)."""
    if not a or not b:
        return False
    ta, tb = a.split()[0].lower().strip(".,'’"), b.split()[0].lower().strip(".,'’")
    return ta == tb and len(ta) > 1


def extract_parties(text, deal_type=None):
    """Return {acquirer_name, target_name, seller_name?, parties_confidence, pattern, trace}.

    The seller-side "X sells its Y unit to Z" pattern is only tried when the deal
    was classified as a divestiture, so a buyer's unrelated asset sale in the same
    article cannot displace the main transaction.
    """
    trace = []
    patterns = [p for p in PARTY_PATTERNS if p[0] != "divests" or deal_type == "divestiture"]
    if deal_type == "divestiture":
        patterns.sort(key=lambda p: 0 if p[0] == "divests" else 1)
    for name, rx, conf in patterns:
        for m in rx.finditer(text):
            a = clean_name(m.group("A"))
            t = clean_name(m.group("T"))
            s = clean_name(m.group("S")) if "S" in m.groupdict() and m.group("S") else None
            if not (_looks_like_name(a) and _looks_like_name(t)) or a.lower() == t.lower():
                continue
            if name in ("merge_and", "merge_with", "merger_of"):
                trace.append("parties: pattern %s -> first-named %r treated as acquirer, %r as target "
                             "(merger: assignment by mention order; LOW confidence)" % (name, a, t))
            else:
                trace.append("parties: pattern %s -> acquirer %r, target %r (%s confidence)" % (name, a, t, conf))
            res = {"acquirer_name": a, "target_name": t, "parties_confidence": conf, "pattern": name}
            if s:
                res["seller_name"] = s
                trace[-1] += "; seller %r" % s
            res["trace"] = trace
            return res
    for name, rx, conf in TARGET_ONLY_PATTERNS:
        m = rx.search(text)
        if m:
            t = clean_name(m.group("T"))
            if _looks_like_name(t):
                trace.append("parties: pattern %s -> target %r only; acquirer unknown (%s confidence)"
                             % (name, t, conf))
                return {"target_name": t, "parties_confidence": conf, "pattern": name, "trace": trace}
    trace.append("parties: no acquirer/target pattern matched (names omitted, not guessed)")
    return {"parties_confidence": "none", "pattern": None, "trace": trace}


# --- dates ---------------------------------------------------------------------

_MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9,
           "sept": 9, "oct": 10, "nov": 11, "dec": 12}
_MONTH_RE = (r"(?:Jan(?:uary|\.)?|Feb(?:ruary|\.)?|Mar(?:ch|\.)?|Apr(?:il|\.)?|May|Jun(?:e|\.)?|Jul(?:y|\.)?|"
             r"Aug(?:ust|\.)?|Sep(?:t(?:ember|\.)?|\.)?|Oct(?:ober|\.)?|Nov(?:ember|\.)?|Dec(?:ember|\.)?)")
DATE_RE = re.compile(
    r"\b(?P<mon>%s)\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?,?\s+(?P<year>20\d\d)\b|"
    r"\b(?P<day2>\d{1,2})(?:st|nd|rd|th)?\s+(?P<mon2>%s)\s+(?P<year2>20\d\d)\b|"
    r"\b(?P<iso>20\d\d-\d\d-\d\d)\b" % (_MONTH_RE, _MONTH_RE))
MONTH_YEAR_RE = re.compile(r"\b(?P<mon>%s)\s+(?P<year>20\d\d)\b" % _MONTH_RE)
PERIOD_RE = re.compile(
    r"\bQ(?P<q>[1-4])\s*(?:of\s+)?(?:FY\s?|fiscal\s+)?(?P<qy>20\d\d)|"
    r"\b(?P<qword>first|second|third|fourth|1st|2nd|3rd|4th)\s+(?:calendar\s+|fiscal\s+)?quarter\s+(?:of\s+)?"
    r"(?:fiscal\s+(?:year\s+)?|calendar\s+(?:year\s+)?|FY\s?)?(?P<qwy>20\d\d)|"
    r"\b(?P<hword>first|second|1st|2nd)\s+(?:calendar\s+|fiscal\s+)?half\s+(?:of\s+)?"
    r"(?:fiscal\s+(?:year\s+)?|calendar\s+(?:year\s+)?|FY\s?)?(?P<hwy>20\d\d)|"
    r"\bH(?P<h>[12])\s*(?:of\s+)?(?:FY\s?)?(?P<hy>20\d\d)|"
    r"\b(?P<fy>fiscal(?: year)?|FY)\s?(?P<fyy>20\d\d)|"
    r"\b(?P<part>early|mid|mid-|late|the end of|end of|end-|year-end|year end|by year-end|calendar year|calendar|"
    r"by the end of|by)\s*(?P<py>20\d\d)|"
    r"\b(?P<y>20\d\d)\b",
    re.I,
)
EXPECTED_CLOSE_RES = [
    re.compile(r"(?:expected|anticipated|scheduled|slated|projected|targeted|likely|on track|aims?|hopes?|"
               r"plans?|intends?)\s+to\s+(?:close|be completed|complete|be consummated|be finali[sz]ed|occur|"
               r"be finalised|be closed|conclude)\s+(?:in|by|during|on|before|around|at|within|toward|towards|"
               r"no later than|prior to|early in|late in)?\s*(?:the\s+)?(?P<when>[^.;]{0,60})", re.I),
    re.compile(r"(?:closing|completion|close)\s+(?:of the (?:\S+\s+){0,3}(?:transaction|deal|acquisition|merger|"
               r"offer)\s+)?(?:is|are|was)\s+(?:currently\s+)?(?:expected|anticipated|targeted|projected)\s+"
               r"(?:to occur |to take place |to happen |for |in |by |during |on )?(?:the\s+)?(?P<when>[^.;]{0,60})",
               re.I),
    re.compile(r"expected (?:closing|completion|close)(?: date)?(?: of| in| by|:)\s*(?:the\s+)?(?P<when>[^.;]{0,40})",
               re.I),
    re.compile(r"(?:expects?|anticipates?)\s+(?:the (?:transaction|deal|acquisition|merger) )?to (?:close|complete)"
               r"\s+(?:in|by|during|on|before)?\s*(?:the\s+)?(?P<when>[^.;]{0,60})", re.I),
]
_QEND = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
_ORD = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3, "fourth": 4, "4th": 4}
_MEND = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def _month_num(s):
    return _MONTHS[s.lower().rstrip(".")[:4]] if s.lower().rstrip(".")[:4] == "sept" else _MONTHS[s.lower()[:3]]


def parse_date(s):
    """First explicit calendar date in `s` as YYYY-MM-DD, else None."""
    m = DATE_RE.search(s)
    if not m:
        return None
    if m.group("iso"):
        return m.group("iso")
    if m.group("mon"):
        return "%s-%02d-%02d" % (m.group("year"), _month_num(m.group("mon")), int(m.group("day")))
    return "%s-%02d-%02d" % (m.group("year2"), _month_num(m.group("mon2")), int(m.group("day2")))


def _month_end(y, mnum):
    d = _MEND[mnum]
    if mnum == 2 and (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)):
        d = 29
    return "%d-%02d-%02d" % (y, mnum, d)


def parse_period(s):
    """Return (end_of_period_date_or_None, matched_text, note) for a close-timing phrase.

    Normalisation: a stated period maps to its LAST calendar day (Q3 2026 ->
    2026-09-30; H2 2026 -> 2026-12-31; June 2026 -> 2026-06-30; 'early 2026' ->
    2026-03-31; 'mid-2026' -> 2026-06-30; 'late/end of/in 2026' -> 2026-12-31).
    A fiscal-year phrase has no computable end (fiscal year-ends differ), so the
    date is omitted and only the text is kept.
    """
    d = parse_date(s)
    if d:
        return d, DATE_RE.search(s).group(0), "explicit date"
    m = MONTH_YEAR_RE.search(s)
    if m:
        y, mnum = int(m.group("year")), _month_num(m.group("mon"))
        return _month_end(y, mnum), m.group(0), "end of stated month"
    m = PERIOD_RE.search(s)
    if not m:
        return None, None, None
    g = m.groupdict()
    if g["q"]:
        return "%s-%s" % (g["qy"], _QEND[int(g["q"])]), m.group(0), "end of stated quarter"
    if g["qword"]:
        return "%s-%s" % (g["qwy"], _QEND[_ORD[g["qword"].lower()]]), m.group(0), "end of stated quarter"
    if g["hword"]:
        return "%s-%s" % (g["hwy"], "06-30" if _ORD[g["hword"].lower()] == 1 else "12-31"), m.group(0), \
            "end of stated half"
    if g["h"]:
        return "%s-%s" % (g["hy"], "06-30" if g["h"] == "1" else "12-31"), m.group(0), "end of stated half"
    if g["fy"]:
        return None, m.group(0), "fiscal-year phrase: year-end differs by company; expected_close_date omitted"
    if g["part"]:
        part = g["part"].lower().rstrip("- ")
        end = "03-31" if part == "early" else "06-30" if part == "mid" else "12-31"
        return "%s-%s" % (g["py"], end), m.group(0), "end of stated part of year"
    return "%s-12-31" % g["y"], m.group(0), "end of stated year"


def extract_expected_close(text):
    for rx in EXPECTED_CLOSE_RES:
        for m in rx.finditer(text):
            when = m.group("when")
            date, matched, note = parse_period(when)
            if matched:
                return {"expected_close_date": date, "expected_close_text": matched.strip(), "note": note}
    return None


DATELINE_RE = re.compile(
    r"^\s*(?:[A-Z][A-Za-z.'’-]*(?:[ ,]+[A-Za-z.'’-]+){0,7}?),?\s*[—–-]{1,2}\s*(?P<d>[^—–\n]{6,40}?)\s*"
    r"(?:[—–-]{1,2}|/PRNewswire/|\(GLOBE NEWSWIRE\)|\(BUSINESS WIRE\)|--)|"
    r"^\s*(?:[A-Z][A-Za-z.'’-]*(?:[ ,]+[A-Za-z.'’-]+){0,7}?),\s+(?P<d2>%s\s+\d{1,2},?\s+20\d\d)\b|"
    r"^\s*(?P<d3>%s\s+\d{1,2},?\s+20\d\d)\b" % (_MONTH_RE, _MONTH_RE))
ANNOUNCED_ON_RE = re.compile(
    r"(?:announced|said|disclosed|reported|unveiled)\s+(?:on\s+|today,?\s+)?(?P<d>%s\s+\d{1,2}(?:st|nd|rd|th)?,?\s+"
    r"20\d\d|\d{1,2}\s+%s\s+20\d\d)" % (_MONTH_RE, _MONTH_RE), re.I)
CLOSED_ON_RE = re.compile(
    r"(?:completed|closed|consummated|finali[sz]ed|effective|took effect)\s+(?:the (?:\S+\s+){0,4}?)?(?:on|as of)\s+"
    r"(?P<d>%s\s+\d{1,2}(?:st|nd|rd|th)?,?\s+20\d\d|\d{1,2}\s+%s\s+20\d\d)" % (_MONTH_RE, _MONTH_RE), re.I)


def extract_dates(text, status):
    res, notes = {}, []
    dateline = None
    m = DATELINE_RE.search(text[:400])
    if m:
        dateline = parse_date(m.group("d") or m.group("d2") or m.group("d3") or "")
    ann = ANNOUNCED_ON_RE.search(text)
    if ann and parse_date(ann.group("d")):
        res["announced_date"] = parse_date(ann.group("d"))
        notes.append("announced_date from %r" % ann.group(0))
    elif dateline and status in ("announced", "pending", None):
        res["announced_date"] = dateline
        notes.append("announced_date taken from the dateline %s" % dateline)
    if status == "closed":
        c = CLOSED_ON_RE.search(text)
        if c and parse_date(c.group("d")):
            res["actual_close_date"] = parse_date(c.group("d"))
            notes.append("actual_close_date from %r" % c.group(0))
        elif dateline:
            res["actual_close_date"] = dateline
            notes.append("actual_close_date taken from the completion release dateline %s" % dateline)
    ec = extract_expected_close(text)
    if ec and status != "closed":
        if ec["expected_close_date"]:
            res["expected_close_date"] = ec["expected_close_date"]
        res["expected_close_text"] = ec["expected_close_text"]
        notes.append("expected close %r -> %s (%s)" % (ec["expected_close_text"], ec["expected_close_date"] or "date omitted",
                                                       ec["note"]))
    return res, notes


# --- regulatory jurisdictions (SKILL.md step 4) ----------------------------------

REGULATORY_CUES = [
    (re.compile(r"\bHSR\b|Hart-Scott-Rodino", re.I), ["US-DOJ", "US-FTC"], "HSR"),
    (re.compile(r"\bFTC\b|Federal Trade Commission"), ["US-FTC"], "FTC"),
    (re.compile(r"\bDOJ\b|Department of Justice|Justice Department|Antitrust Division"), ["US-DOJ"], "DOJ"),
    (re.compile(r"European Commission|\bEU\b (?:antitrust|competition|merger|regulators?|approval|clearance|review)|"
                r"\bEC\b (?:approval|clearance|review|merger|antitrust)|\bBrussels\b|EU Merger Regulation"),
     ["EU-EC"], "EC"),
    (re.compile(r"\bCMA\b|Competition and Markets Authority"), ["UK-CMA"], "CMA"),
    (re.compile(r"\bSAMR\b|State Administration for Market Regulation|Chinese (?:antitrust|competition) (?:regulators?|"
                r"authorit\w+)|China'?s (?:antitrust|competition|market) regulator"), ["CN-SAMR"], "SAMR"),
    (re.compile(r"\bCCI\b|Competition Commission of India"), ["IN-CCI"], "CCI"),
    (re.compile(r"\bCADE\b"), ["BR-CADE"], "CADE"),
    (re.compile(r"\bJFTC\b|Japan Fair Trade Commission"), ["JP-JFTC"], "JFTC"),
    (re.compile(r"\bKFTC\b|Korea Fair Trade Commission"), ["KR-KFTC"], "KFTC"),
    (re.compile(r"\bCFIUS\b|Committee on Foreign Investment"), [], "CFIUS"),
    (re.compile(r"\bFDI\b (?:review|approval|screening|clearance)|foreign (?:direct )?investment (?:review|approval|"
                r"screening|clearance|regime)|national security review", re.I), [], "FDI"),
    (re.compile(r"\bantitrust\b|\bcompetition (?:authorities|regulators|approval|clearance|review|law)\b|"
                r"\bmerger control\b", re.I), [], "antitrust (authority unspecified)"),
]


def extract_regulatory(text):
    codes, mentions, trace = [], [], []
    for rx, code_list, label in REGULATORY_CUES:
        m = rx.search(text)
        if m:
            mentions.append(label)
            for c in code_list:
                if c not in codes:
                    codes.append(c)
            trace.append("regulatory: %r -> %s" % (m.group(0), ", ".join(code_list) or "mention only"))
    return {"regulatory_jurisdictions": codes, "regulatory_mentions": mentions, "trace": trace}


# --- advisers -------------------------------------------------------------------

NAMELIST = r"%s(?:,\s*%s)*(?:,?\s+and\s+%s)?" % (NAME, NAME, NAME)
ADVISER_RES = [
    re.compile(r"(?P<adv>" + NAMELIST + r")\s+(?:is|are|was|were|has been|have been)?\s*(?:acting|acted|serving|served|"
               r"serves|acts)\s+as\s+(?:the\s+)?(?:exclusive\s+|lead\s+|sole\s+|joint\s+|co-\s*)?(?P<role>financial|legal|"
               r"strategic|transaction)?\s*(?:advis[eo]rs?|counsel)(?:\s+and\s+(?:legal\s+)?counsel)?[^.]{0,30}?\bto\s+"
               r"(?P<client>" + NAME + r")"),
    re.compile(r"(?P<client>" + NAME + r")\s+(?:is|was|were|are)\s+(?:being\s+)?advised\s+by\s+(?P<adv>" + NAMELIST + r")"),
    re.compile(r"(?P<role>[Ff]inancial|[Ll]egal)\s+advis[eo]rs?\s+to\s+(?P<client>" + NAME + r")\s*(?:is|are|were|was|"
               r"include|included|:)\s+(?P<adv>" + NAMELIST + r")"),
    re.compile(r"\badvised by\s+(?P<adv>" + NAMELIST + r")"),
]


def _split_names(s):
    parts = [p.strip() for p in re.split(r",\s*|\s+and\s+", s) if p.strip()]
    if len(parts) > 1 and (("&" in parts[-1]) or re.search(r"\b(?:LLP|LLC|L\.L\.P\.|PC|P\.C\.)\.?$", parts[-1])) \
            and all(len(p.split()) == 1 for p in parts[:-1]):
        return [s.strip()]  # "Skadden, Arps, Slate, Meagher & Flom LLP" is one firm
    return parts


def extract_advisers(text):
    out, seen = [], set()
    for rx in ADVISER_RES:
        for m in rx.finditer(text):
            g = m.groupdict()
            role = (g.get("role") or "").lower()
            if not role:
                span = m.group(0).lower()
                role = "legal" if "counsel" in span or "legal" in span else "financial" if "financial" in span else "unspecified"
            client = clean_name(g.get("client")) if g.get("client") else None
            for nm in _split_names(g["adv"]):
                nm = clean_name(nm)
                if not _looks_like_name(nm):
                    continue
                key = (nm.lower(), role, (client or "").lower())
                if key in seen:
                    continue
                seen.add(key)
                item = {"name": nm, "role": role}
                if client:
                    item["client"] = client
                out.append(item)
    return out


# --- confidence (SKILL.md step 7 scale) -------------------------------------------

def score_confidence(has_value, has_status, both_parties, rumored, ambiguous_currency, non_binding):
    trace = ["base 60"]
    c = 60
    if has_value:
        c += 15
        trace.append("+15 explicit deal value")
    if has_status:
        c += 10
        trace.append("+10 explicit status cue")
    if both_parties:
        c += 10
        trace.append("+10 both parties named")
    if rumored:
        c -= 15
        trace.append("-15 rumour cues (sources say / in talks)")
    if ambiguous_currency:
        c -= 10
        trace.append("-10 ambiguous currency (bare '$' -> USD?)")
    c = max(0, min(100, c))
    if non_binding and c > 59:
        c = 59
        trace.append("cap 59: non-binding LOI/MOU (SKILL.md anti-pattern: confidence < 60)")
    trace.append("= %d (clamped 0-100)" % c)
    return c, trace


# --- extract -----------------------------------------------------------------------

DOC_USD_RE = re.compile(r"US\s?\$|U\.S\.\s?\$|\bUSD\b|U\.S\. dollars|US dollars", re.I)
DOC_OTHER_DOLLAR_RE = re.compile(r"C\$|CA\$|A\$|AU\$|HK\$|S\$|NZ\$|R\$|\b(?:CAD|AUD|HKD|SGD|NZD|BRL)\b|"
                                 r"(?:Canadian|Australian|Singapore|Hong Kong|New Zealand) dollars", re.I)
UNDISCLOSED_RE = re.compile(r"\bundisclosed (?:sum|amount|terms|price|value|consideration)\b|"
                            r"\b(?:financial )?terms (?:of the (?:deal|transaction|agreement) )?were not disclosed\b|"
                            r"\bdid not disclose (?:the )?(?:financial )?(?:terms|price|value)\b|"
                            r"\bterms were not (?:disclosed|announced|revealed)\b", re.I)

def _money_field(out, base, amount, deal_currency, notes):
    """Write <base>_usd for USD/USD? amounts, else <base>_local + currency."""
    if amount["currency"] in ("USD", "USD?"):
        out[base + "_usd"] = amount["value"]
    else:
        out[base + "_local"] = amount["value"]
        notes.append("%s stated in %s — convert with the announcement-date FX rate before filling %s_usd"
                     % (base, amount["currency"], base))
    if amount["currency"] != deal_currency:
        out[base + "_currency"] = amount["currency"]
    if amount["approx"]:
        out[base + "_approx"] = True


def extract_event(text, assume_usd=False, source_url=None, source_grade=None, acquirer_price=None):
    """Rule-based extraction into the SKILL.md event JSON (+ trace and notes)."""
    text = text.replace("\r\n", "\n")
    flat = re.sub(r"\s+", " ", text)
    trace, notes = [], []
    if not assume_usd and DOC_USD_RE.search(flat) and not DOC_OTHER_DOLLAR_RE.search(flat):
        assume_usd = True
        trace.append("currency: the text writes 'US$'/'USD' and names no other dollar currency -> bare '$' read as USD")
    amounts = parse_money(flat, assume_usd=assume_usd)
    deal = classify_deal(flat)
    status = classify_status(flat)
    parties = extract_parties(flat, deal["deal_type"])
    cons = parse_consideration(flat, amounts)
    reg = extract_regulatory(flat)
    trace += parties["trace"] + deal["trace"] + status["trace"] + cons["trace"] + reg["trace"]

    out = {"event_type": "ma_event"}
    if deal["deal_type"]:
        out["deal_type"] = deal["deal_type"]
    if deal["deal_structure"]:
        out["deal_structure"] = deal["deal_structure"]
    if deal["deal_tags"]:
        out["deal_tags"] = deal["deal_tags"]
    if deal["out_of_scope"]:
        out["out_of_scope"] = True
        notes.append("joint venture: organic partnership, skip per SKILL.md 'When to invoke'")
    for k in ("acquirer_name", "target_name", "seller_name"):
        if parties.get(k):
            out[k] = parties[k]
    out["parties_confidence"] = parties["parties_confidence"]

    # deal value: headline (unspecified basis) > equity > enterprise; EV / equity kept separate
    deal_values = [a for a in amounts if a["kind"] == "deal-value"]
    unspecified = [a for a in deal_values if a["basis"] == "unspecified"]
    ev = [a for a in deal_values if a["basis"] == "enterprise"]
    eq = [a for a in deal_values if a["basis"] == "equity"]
    headline = (unspecified or eq or ev or [None])[0]
    deal_currency = headline["currency"] if headline else None
    if headline:
        _money_field(out, "deal_value", headline, None, notes)
        out["deal_value_currency"] = headline["currency"]
        out["deal_value_basis"] = headline["basis"]
        trace.append("deal_value: %r -> %s %s (basis %s%s)" % (headline["raw"], headline["value"], headline["currency"],
                                                             headline["basis"], ", approx" if headline["approx"] else ""))
        if headline["currency_ambiguous"]:
            notes.append("currency: bare '$' is ambiguous — reported as USD?; write US$ or pass --assume-usd")
    if eq:
        _money_field(out, "implied_equity_value", eq[0], deal_currency, notes)
        trace.append("implied_equity_value: %r" % eq[0]["raw"])
    if ev:
        _money_field(out, "enterprise_value", ev[0], deal_currency, notes)
        trace.append("enterprise_value: %r" % ev[0]["raw"])
    elif headline and headline["basis"] == "unspecified" and not eq:
        _money_field(out, "enterprise_value", headline, deal_currency, notes)
        notes.append("basis unspecified ('valued at' / 'for'): captured as enterprise_value per SKILL.md step 2 — "
                     "equity vs enterprise value ambiguous")
    if ev and eq:
        notes.append("enterprise value and equity value both stated — kept as separate fields")
    if headline is None and UNDISCLOSED_RE.search(flat):
        notes.append("deal value undisclosed (%r) — leave the value fields empty" % UNDISCLOSED_RE.search(flat).group(0))
        trace.append("deal_value: text says %r" % UNDISCLOSED_RE.search(flat).group(0))

    for k in ("consideration_type", "consideration_detail", "cash_per_share", "exchange_ratio", "exchange_ratio_issuer",
              "earnout"):
        if k in cons:
            out[k] = cons[k]
    issuer = cons.get("exchange_ratio_issuer")
    if issuer and out.get("acquirer_name") and out.get("target_name") and parties["parties_confidence"] == "low":
        if _same_entity(issuer, out["target_name"]) and not _same_entity(issuer, out["acquirer_name"]):
            out["acquirer_name"], out["target_name"] = out["target_name"], out["acquirer_name"]
            trace.append("parties: exchange-ratio issuer %r is the share issuer -> treated as acquirer (swapped)" % issuer)
        elif _same_entity(issuer, out["acquirer_name"]):
            trace.append("parties: exchange-ratio issuer %r confirms the acquirer" % issuer)
    offers = [a for a in amounts if a["kind"] == "per-share-offer"]
    if offers and cons.get("consideration_type") != "stock":
        out["offer_price_per_share"] = offers[0]["value"]
        out["offer_price_currency"] = offers[0]["currency"]
    implied = None
    if cons.get("exchange_ratio") is not None and acquirer_price:
        implied = implied_value(cons["exchange_ratio"], acquirer_price, cons.get("cash_per_share") or 0.0)
        out["implied_offer_per_share"] = implied
        trace.append("implied offer/share = %s x %s + %s = %s" % (cons["exchange_ratio"], acquirer_price,
                                                                cons.get("cash_per_share") or 0, implied))
    prices = [a for a in amounts if a["kind"] == "share-price"]
    stated = STATED_PREMIUM_RE.search(flat)
    if stated:
        out["premium_pct"] = float(stated.group("p1") or stated.group("p2"))
        trace.append("premium_pct stated: %r" % stated.group(0))
    offer_val = out.get("offer_price_per_share") if out.get("offer_price_per_share") is not None else implied
    if offer_val is not None and prices:
        out["unaffected_price"] = prices[0]["value"]
        comp = premium_pct(offer_val, prices[0]["value"])
        out["premium_pct_computed"] = comp
        trace.append("premium computed: (%s - %s) / %s x 100 = %s%%" % (offer_val, prices[0]["value"], prices[0]["value"], comp))
        if "premium_pct" in out and abs(out["premium_pct"] - comp) > 1.0:
            notes.append("stated premium %s%% differs from computed %s%% — check the unaffected price used"
                         % (out["premium_pct"], comp))
        if "premium_pct" not in out:
            out["premium_pct"] = comp
    dates, dnotes = extract_dates(flat, status["status"])
    out.update(dates)
    notes += dnotes
    if status["status"]:
        out["status"] = status["status"]
    if status["stage"]:
        out["stage"] = status["stage"]
    if reg["regulatory_jurisdictions"]:
        out["regulatory_jurisdictions"] = reg["regulatory_jurisdictions"]
    if reg["regulatory_mentions"]:
        out["regulatory_mentions"] = reg["regulatory_mentions"]
    fees = [a for a in amounts if a["kind"] == "termination-fee"]
    if fees:
        _money_field(out, "termination_fee", fees[0], deal_currency, notes)
        trace.append("termination_fee: %r" % fees[0]["raw"])
    advisers = extract_advisers(flat)
    if advisers:
        out["advisers"] = advisers
        trace.append("advisers: %s" % ", ".join(a["name"] for a in advisers))
    if deal["risk_flags"]:
        out["risk_flags"] = deal["risk_flags"]
    if source_url:
        out["source_url"] = source_url
    else:
        notes.append("source_url is required by SKILL.md — pass --source-url")
    if source_grade:
        out["source_grade"] = source_grade
    both = bool(out.get("acquirer_name") and out.get("target_name"))
    conf, ctrace = score_confidence(
        has_value=headline is not None,
        has_status=status["status"] is not None,
        both_parties=both,
        rumored=status["stage"] == "rumored",
        ambiguous_currency=bool(headline and headline["currency_ambiguous"]),
        non_binding=status["stage"] == "non-binding",
    )
    out["confidence"] = conf
    review_required = conf < 80
    if source_grade and re.match(r"^[A-F][1-6]$", source_grade.upper()):
        if source_grade[0].upper() > "B" or int(source_grade[1]) > 3:
            review_required = True
            notes.append("source grade %s is below B3 — human review per SKILL.md step 7" % source_grade)
    if review_required:
        out["review_required"] = True
    if parties["parties_confidence"] in ("low", "medium"):
        notes.append("party assignment is %s confidence (%s pattern) — verify acquirer vs target"
                     % (parties["parties_confidence"], parties["pattern"]))
    if notes:
        out["notes"] = notes
    out["confidence_rules"] = list(CONFIDENCE_RULES)
    out["confidence_trace"] = ctrace
    out["trace"] = trace
    return out


# --- demo ------------------------------------------------------------------------

DEMO_TEXT = (
    "SAN JOSE, Calif., March 3, 2026 -- Helios Semiconductor Inc. today announced that it has entered into a "
    "definitive agreement to acquire Meridian Photonics Corp. for $42.00 per share in cash, representing a total "
    "equity value of approximately US$5.6 billion and an enterprise value of approximately US$6.1 billion, "
    "including Meridian's net debt. The offer price represents a premium of approximately 40% to Meridian's "
    "unaffected closing price of $30.00 on February 27, 2026. The transaction, which has been unanimously approved "
    "by the boards of directors of both companies, is expected to close in the second half of 2026, subject to "
    "approval by Meridian shareholders, expiration of the waiting period under the HSR Act, clearance by the "
    "European Commission and SAMR, and other customary closing conditions. Meridian would be required to pay a "
    "termination fee of $180 million under certain circumstances. Bluepeak Partners is acting as exclusive "
    "financial advisor to Helios, and Harrow & Vance LLP is serving as legal counsel to Helios."
)


# --- CLI printing ------------------------------------------------------------------

def _dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)


def cmd_value(args):
    res = value_summary(args.string, assume_usd=args.assume_usd)
    if args.json:
        print(_dump(res))
        return 0
    print("input: %s" % res["input"])
    if not res["amounts"]:
        print("no money expression found (need a currency symbol/code: $, US$, €, £, EUR, GBP, ...)")
        return 1
    for a in res["amounts"]:
        bits = ["%s %s" % (a["value"], a["currency"])]
        if a["currency_ambiguous"]:
            bits.append("ambiguous currency")
        if a["approx"]:
            bits.append("approx (%s)" % a["qualifier"])
        if a["per_share"]:
            bits.append("per share")
        bits.append("basis: %s" % a["basis"])
        bits.append("kind: %s" % a["kind"])
        print("  %-28s -> %s" % (a["raw"], "; ".join(bits)))
    if "enterprise_value" in res:
        print("enterprise_value: %s %s" % (res["enterprise_value"]["value"], res["enterprise_value"]["currency"]))
    if "equity_value" in res:
        print("equity_value:     %s %s" % (res["equity_value"]["value"], res["equity_value"]["currency"]))
    for n in res.get("notes", []):
        print("note: %s" % n)
    return 0


def cmd_classify(args):
    text = re.sub(r"\s+", " ", args.text)
    deal = classify_deal(text)
    status = classify_status(text)
    cons = parse_consideration(text)
    res = {
        "deal_type": deal["deal_type"], "deal_structure": deal["deal_structure"], "deal_tags": deal["deal_tags"],
        "out_of_scope": deal["out_of_scope"], "status": status["status"], "stage": status["stage"],
        "consideration_type": cons.get("consideration_type"), "consideration_detail": cons.get("consideration_detail"),
        "risk_flags": deal["risk_flags"], "trace": deal["trace"] + status["trace"] + cons["trace"],
    }
    if args.json:
        print(_dump(res))
        return 0
    print("deal_type:      %s   (structure: %s; tags: %s)" % (res["deal_type"] or "-", res["deal_structure"] or "-",
                                                             ", ".join(res["deal_tags"]) or "-"))
    print("status:         %s   (stage: %s)" % (res["status"] or "-", res["stage"] or "-"))
    print("consideration:  %s   %s" % (res["consideration_type"] or "-", res["consideration_detail"] or ""))
    print("risk_flags:     %s" % (", ".join(res["risk_flags"]) or "-"))
    print("trace:")
    for t in res["trace"]:
        print("  - %s" % t)
    return 0


def cmd_premium(args, parser):
    res = {}
    lines = []
    ratio, issuer, cash_ps = None, None, None
    if args.text:
        cons = parse_consideration(re.sub(r"\s+", " ", args.text))
        ratio, issuer, cash_ps = cons.get("exchange_ratio"), cons.get("exchange_ratio_issuer"), cons.get("cash_per_share")
        for k in ("consideration_type", "consideration_detail", "cash_per_share", "exchange_ratio", "exchange_ratio_issuer"):
            if k in cons:
                res[k] = cons[k]
        lines.append("consideration: %s%s" % (cons.get("consideration_type") or "not stated",
                                             (" — " + cons["consideration_detail"]) if cons.get("consideration_detail") else ""))
    if args.exchange_ratio:
        r, iss = parse_exchange_ratio(args.exchange_ratio)
        if r is None:
            parser.error("could not parse --exchange-ratio %r" % args.exchange_ratio)
        ratio, issuer = r, iss or issuer
        res["exchange_ratio"] = ratio
        if issuer:
            res["exchange_ratio_issuer"] = issuer
    if args.cash_per_share is not None:
        cash_ps = args.cash_per_share
        res["cash_per_share"] = cash_ps
    offer = args.offer
    if ratio is not None:
        if args.acquirer_price is None:
            lines.append("exchange ratio %s%s (pass --acquirer-price to compute the implied per-share value)"
                         % (_fmt_num(ratio), " of %s" % issuer if issuer else ""))
        else:
            offer = implied_value(ratio, args.acquirer_price, cash_ps or 0.0)
            res["acquirer_price"] = args.acquirer_price
            res["implied_offer_per_share"] = offer
            lines.append("implied offer/share = %s x %s%s = %s" % (
                _fmt_num(ratio), _fmt_num(args.acquirer_price),
                (" + %s cash" % _fmt_num(cash_ps)) if cash_ps else "", _fmt_num(offer)))
    if offer is not None and args.unaffected is not None:
        p = premium_pct(offer, args.unaffected)
        res["offer"] = offer
        res["unaffected"] = args.unaffected
        res["premium_pct"] = p
        lines.append("premium: %s%%   ((%s - %s) / %s x 100)" % (_fmt_num(p), _fmt_num(offer), _fmt_num(args.unaffected),
                                                              _fmt_num(args.unaffected)))
    elif offer is not None:
        res["offer"] = offer
        lines.append("offer/share %s (pass --unaffected to compute the premium)" % _fmt_num(offer))
    if not res:
        parser.error("give --offer/--unaffected, --exchange-ratio [--acquirer-price], or --text")
    if args.json:
        print(_dump(res))
    else:
        for ln in lines:
            print(ln)
    return 0


def _read_text(args, parser):
    if args.text:
        return args.text
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                return fh.read()
        except OSError as exc:
            parser.error("could not read %s: %s" % (args.file, exc))
    data = sys.stdin.read()
    if not data.strip():
        parser.error("pass --text, --file PATH, or text on stdin")
    return data


def cmd_extract(args, parser):
    text = _read_text(args, parser)
    res = extract_event(text, assume_usd=args.assume_usd, source_url=args.source_url, source_grade=args.source_grade,
                        acquirer_price=args.acquirer_price)
    if args.no_trace:
        for k in ("trace", "confidence_rules", "confidence_trace"):
            res.pop(k, None)
    print(_dump(res))
    return 0


def cmd_demo():
    print("Demo article (fictional companies):\n")
    print(DEMO_TEXT + "\n")
    print("$ python3 maevent.py extract --text \"<article>\"\n")
    print(_dump(extract_event(DEMO_TEXT, source_url="https://example.com/helios-meridian-release")))
    return 0


# --- selftest --------------------------------------------------------------------

def run_selftest():
    checks = []

    def check(name, got, want):
        ok = got == want
        checks.append(ok)
        print("%s  %s: got %r, expected %r" % ("PASS" if ok else "FAIL", name, got, want))
        if not ok:
            print("SELFTEST FAILED at: %s" % name, file=sys.stderr)
            sys.exit(1)

    # 1. Plain acquisition announcement -> acquisition, all-cash, announced, parties, value, confidence 85
    e = extract_event("Foo Corp to acquire Bar Inc for $2.4 billion in cash")
    check("acquisition: deal_type", e["deal_type"], "acquisition")
    check("acquisition: consideration all-cash", e["consideration_type"], "cash")
    check("acquisition: status announced", e["status"], "announced")
    check("acquisition: acquirer", e["acquirer_name"], "Foo Corp")
    check("acquisition: target", e["target_name"], "Bar Inc")
    check("acquisition: deal value 2.4e9", e["deal_value_usd"], 2400000000)
    check("acquisition: bare $ -> USD?", e["deal_value_currency"], "USD?")
    check("acquisition: confidence 60+15+10+10-10", e["confidence"], 85)
    e2 = extract_event("Foo Corp to acquire Bar Inc for $2.4 billion in cash", assume_usd=True)
    check("acquisition: --assume-usd lifts the currency penalty", (e2["deal_value_currency"], e2["confidence"]), ("USD", 95))

    # 2. Merger of equals, all-stock
    c = classify_deal("Alpha Ltd and Beta plc agreed to combine in an all-stock merger of equals")
    check("merger of equals: deal_type", c["deal_type"], "merger")
    check("merger of equals: structure", c["deal_structure"], "merger-of-equals")
    check("merger of equals: all-stock", parse_consideration("in an all-stock merger of equals")["consideration_type"], "stock")

    # 3. Minority stake
    e = extract_event("Gamma Holdings agreed to acquire a 30% stake in Delta SA for €850 million")
    check("minority stake: deal_type", e["deal_type"], "acquisition")
    check("minority stake: structure", e["deal_structure"], "minority-stake")
    check("minority stake: EUR local value", (e["deal_value_local"], e["deal_value_currency"]), (850000000, "EUR"))
    check("minority stake: parties", (e["acquirer_name"], e["target_name"]), ("Gamma Holdings", "Delta SA"))

    # 4. Rumour -> stage rumored, status omitted, -15
    e = extract_event("Sources say Omega Corp is in talks to acquire Sigma Inc, people familiar with the matter said.")
    check("rumour: stage rumored", e["stage"], "rumored")
    check("rumour: status omitted (not a SKILL.md status)", "status" in e, False)
    check("rumour: penalty applied (60+10-15)", e["confidence"], 55)
    check("rumour: review_required", e.get("review_required"), True)
    check("rumour: parties", (e["acquirer_name"], e["target_name"]), ("Omega Corp", "Sigma Inc"))

    # 5. Premium arithmetic
    check("premium 55 vs 40 = 37.5%", premium_pct(55, 40), 37.5)

    # 6. Exchange ratio -> implied value and premium
    ratio, issuer = parse_exchange_ratio("0.5 shares of X for each share of Y")
    check("exchange ratio parsed", (ratio, issuer), (0.5, "X"))
    check("implied value 0.5 x 100 = 50", implied_value(ratio, 100), 50.0)
    check("premium on implied 50 vs 40 = 25%", premium_pct(implied_value(ratio, 100), 40), 25.0)

    # 7. Completed acquisition -> closed
    e = extract_event("Zeta Corp completed its acquisition of Eta Inc")
    check("completed: status closed", e["status"], "closed")
    check("completed: parties", (e["acquirer_name"], e["target_name"]), ("Zeta Corp", "Eta Inc"))
    check("expected to close is not closed", classify_status("The deal is expected to close in Q3 2026")["status"] != "closed", True)

    # 8. GBP
    v = value_summary("£3.4bn")
    check("£3.4bn -> GBP 3.4e9", (v["amounts"][0]["value"], v["amounts"][0]["currency"]), (3400000000, "GBP"))
    v = value_summary("US$28 billion")
    check("US$28 billion -> USD unambiguous", (v["amounts"][0]["value"], v["amounts"][0]["currency"]), (28000000000, "USD"))
    v = value_summary("€850 million")
    check("€850 million -> EUR", (v["amounts"][0]["value"], v["amounts"][0]["currency"]), (850000000, "EUR"))

    # 9. Enterprise vs equity value kept separate
    v = value_summary("an enterprise value of $5.6 billion and an equity value of $4.9 billion")
    check("EV kept separate", (v["enterprise_value"]["value"], v["enterprise_value"]["currency"]), (5600000000, "USD?"))
    check("equity value kept separate", v["equity_value"]["value"], 4900000000)
    e = extract_event("Kappa Inc agreed to acquire Lambda Corp at an enterprise value of US$5.6 billion and an equity value "
                      "of US$4.9 billion")
    check("extract: enterprise_value_usd", e["enterprise_value_usd"], 5600000000)
    check("extract: implied_equity_value_usd", e["implied_equity_value_usd"], 4900000000)
    check("extract: headline deal value = equity value when no bare figure", e["deal_value_usd"], 4900000000)

    # 10. Approx flag
    v = value_summary("all-stock deal valued at ~$10B")
    check("~$10B approx flag", (v["amounts"][0]["value"], v["amounts"][0]["approx"], v["amounts"][0]["currency"]),
          (10000000000, True, "USD?"))

    # 11. Divestiture with seller
    e = extract_event("Theta plc agreed to sell its packaging unit to Iota Group for $500 million")
    check("divestiture: deal_type", e["deal_type"], "divestiture")
    check("divestiture: seller/acquirer/target", (e["seller_name"], e["acquirer_name"], e["target_name"]),
          ("Theta plc", "Iota Group", "packaging unit"))

    # 12. Take-private / LBO
    c = classify_deal("Kappa Partners to take Lambda Inc private in a $3 billion leveraged buyout")
    check("take-private: go_private", (c["deal_type"], c["deal_structure"]), ("go_private", "take-private"))
    check("take-private: sponsor-backed flag", "sponsor-backed" in c["risk_flags"], True)

    # 13. Mixed consideration with cash + ratio, implied value and premium
    cons = parse_consideration("$45.00 in cash and 0.15 shares of Mu Corp for each share of Nu Inc")
    check("mixed: type", cons["consideration_type"], "mixed")
    check("mixed: cash per share + ratio", (cons["cash_per_share"], cons["exchange_ratio"]), (45, 0.15))
    check("mixed: implied 45 + 0.15 x 100 = 60", implied_value(0.15, 100, 45), 60.0)
    check("mixed: premium 60 vs 50 = 20%", premium_pct(60, 50), 20.0)

    # 14. Expected close normalisation
    ec = extract_expected_close("The transaction is expected to close in Q3 2026, subject to conditions.")
    check("expected close Q3 2026 -> 2026-09-30", (ec["expected_close_date"], ec["expected_close_text"]), ("2026-09-30", "Q3 2026"))
    ec = extract_expected_close("expected to close in the second half of 2026")
    check("expected close H2 2026 -> 2026-12-31", ec["expected_close_date"], "2026-12-31")
    ec = extract_expected_close("expected to close in fiscal year 2027")
    check("fiscal-year close: date omitted, text kept", (ec["expected_close_date"], ec["expected_close_text"]), (None, "fiscal year 2027"))

    # 15. LOI -> announced but capped below 60
    e = extract_event("Xi Corp signed a non-binding letter of intent to acquire Omicron Ltd for $1.2 billion")
    check("LOI: status announced (SKILL.md anti-pattern)", e["status"], "announced")
    check("LOI: stage non-binding", e["stage"], "non-binding")
    check("LOI: confidence capped at 59", e["confidence"], 59)

    # 16. Regulatory mentions -> jurisdiction codes; CFIUS -> cross-border flag
    r = extract_regulatory("subject to HSR clearance and approval by the CMA and SAMR, plus CFIUS review")
    check("regulatory codes", r["regulatory_jurisdictions"], ["US-DOJ", "US-FTC", "UK-CMA", "CN-SAMR"])
    check("CFIUS is a mention, not an antitrust code", "CFIUS" in r["regulatory_mentions"], True)
    check("CFIUS -> cross-border flag", "cross-border" in classify_deal("Pi Corp to acquire Rho Inc; CFIUS review")["risk_flags"], True)

    # 17. Pending regulatory approval
    s = classify_status("The deal is awaiting regulatory approval from the European Commission")
    check("pending: status", (s["status"], s["stage"]), ("pending", "pending-regulatory"))

    # 18. Terminated (but 'termination fee' alone is not termination)
    s = classify_status("Rho Inc and Tau Corp mutually agreed to terminate their merger agreement")
    check("terminated: status", s["status"], "terminated")
    e = extract_event("Upsilon Corp agreed to acquire Phi Inc for $9 billion; Phi would pay a termination fee of $300 million "
                      "upon termination of the merger agreement under certain circumstances.")
    check("termination fee does not mean terminated", e["status"], "announced")
    check("termination fee extracted", e["termination_fee_usd"], 300000000)

    # 19. Hostile tender offer
    e = extract_event("Chi Corp launched a hostile tender offer for Psi Inc at $30.00 per share in cash")
    check("tender offer: structure", (e["deal_type"], e["deal_structure"]), ("acquisition", "tender-offer"))
    check("tender offer: hostile-bid flag", "hostile-bid" in e["risk_flags"], True)
    check("tender offer: offer per share", e["offer_price_per_share"], 30)

    # 20. Nothing fabricated when nothing stated
    e = extract_event("Two companies discussed the weather.")
    check("no fabrication: no value/status/parties", [k for k in e if k.startswith(("deal_value", "status", "acquirer", "target"))], [])
    check("no fabrication: confidence = base 60", e["confidence"], 60)

    # 21. Demo: stated premium equals computed premium; both values separate; advisers
    d = extract_event(DEMO_TEXT)
    check("demo: premium 40% stated == computed", (d["premium_pct"], d["premium_pct_computed"]), (40.0, 40.0))
    check("demo: EV vs equity", (d["enterprise_value_usd"], d["implied_equity_value_usd"]), (6100000000, 5600000000))
    check("demo: expected close H2 2026", d["expected_close_date"], "2026-12-31")
    check("demo: announced date from dateline", d["announced_date"], "2026-03-03")
    check("demo: advisers", [a["name"] for a in d["advisers"]], ["Bluepeak Partners", "Harrow & Vance LLP"])
    check("demo: confidence 95", d["confidence"], 95)

    # 22. Determinism: two extractions are byte-identical
    check("deterministic output", _dump(extract_event(DEMO_TEXT)) == _dump(extract_event(DEMO_TEXT)), True)

    print("ALL %d CHECKS PASSED" % len(checks))
    print("selftest OK")
    return 0


# --- argparse -------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="detect-ma-event companion: deal-value grammar, deal-type/status classification, "
                    "premium arithmetic and rule-based extraction into the SKILL.md event JSON.")
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true", help="extract the built-in fictional press release")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("value", help="normalise a deal-value string ($1.2B, €850 million, £3.4bn, US$28 billion, ~$10B)")
    p.add_argument("string", help="the money string or sentence to parse")
    p.add_argument("--assume-usd", action="store_true", help="treat a bare '$' as USD instead of USD?")
    p.add_argument("--json", action="store_true", help="JSON output")

    p = sub.add_parser("classify", help="deal type, status, consideration and risk flags from phrasing")
    p.add_argument("--text", required=True, help="sentence or paragraph")
    p.add_argument("--json", action="store_true", help="JSON output")

    p = sub.add_parser("premium", help="premium %% and implied per-share value from an exchange ratio")
    p.add_argument("--offer", type=float, help="offer price per share")
    p.add_argument("--unaffected", type=float, help="unaffected (pre-rumour) share price")
    p.add_argument("--exchange-ratio", help="'0.5 shares of X for each share of Y' or a bare number")
    p.add_argument("--acquirer-price", type=float, help="acquirer share price used to value the exchange ratio")
    p.add_argument("--cash-per-share", type=float, help="cash component per share (mixed consideration)")
    p.add_argument("--text", help="consideration phrasing to parse (all-cash / all-stock / mixed, cash + ratio)")
    p.add_argument("--json", action="store_true", help="JSON output")

    p = sub.add_parser("extract", help="rule-based extraction into the SKILL.md event JSON (JSON output)")
    p.add_argument("--file", help="text file with the article / press release")
    p.add_argument("--text", help="article text inline (or pipe it on stdin)")
    p.add_argument("--assume-usd", action="store_true", help="treat a bare '$' as USD instead of USD?")
    p.add_argument("--source-url", help="fills source_url (required by SKILL.md; never inferred)")
    p.add_argument("--source-grade", help="Admiralty grade of the source, e.g. B2 (never inferred)")
    p.add_argument("--acquirer-price", type=float, help="acquirer share price to value an exchange ratio")
    p.add_argument("--no-trace", action="store_true", help="omit trace / confidence_trace from the JSON")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.demo:
        return cmd_demo()
    if not args.command:
        parser.error("choose a command: value | classify | premium | extract  (or --demo / --selftest)")
    if args.command == "value":
        return cmd_value(args)
    if args.command == "classify":
        return cmd_classify(args)
    if args.command == "premium":
        return cmd_premium(args, parser)
    return cmd_extract(args, parser)


if __name__ == "__main__":
    sys.exit(main())
