#!/usr/bin/env python3
"""grade.py — GRADE certainty-of-evidence rating for one outcome across a body of evidence.

Implements the GRADE approach exactly as published (SKILL.md step 4):

  * Starting level by study design (Guyatt 2008; Handbook §5.1.1):
        randomized trials -> High (4);  observational studies -> Low (2).
    `--start` overrides the design default — documented use: bodies of
    non-randomized studies appraised with ROBINS-I start High and are then
    rated down for risk of bias (GRADE guidelines 18, Schünemann 2019).
  * Five reasons to rate DOWN, each 0 / -1 (serious) / -2 (very serious)
    (Handbook Table 5.2; Balshem 2011 Table 3): risk of bias, inconsistency,
    indirectness, imprecision, publication bias.
  * Three reasons to rate UP (Handbook Table 5.3, §5.3.1-5.3.3; Guyatt 2008),
    meant for observational bodies not already rated down for the same concern:
        large magnitude of effect  +1 (RR >2 or <0.5) / +2 (RR >5 or <0.2)  [Table 5.9]
        dose-response gradient     +1
        all plausible residual confounding would reduce the demonstrated
        effect, or would suggest a spurious effect when results show no
        effect                     +1
  * Final certainty = start + sum(down) + sum(up), clamped to 1..4:
        4 High ⊕⊕⊕⊕ | 3 Moderate ⊕⊕⊕◯ | 2 Low ⊕⊕◯◯ | 1 Very low ⊕◯◯◯
    reported with the one-line interpretation of Handbook Table 5.1
    (= Balshem 2011 Table 2).

The script does bookkeeping only. Which level each factor moves is a judgement
made from the per-study appraisal table; GRADE "is not a quantitative system"
(Handbook §5.1) and warns against a mechanistic application (§5.4). The tool
therefore warns — it does not refuse — when rating up is combined with rating
down (Handbook §5.3: rating down "must precede consideration of reasons for
rating it up"; §5.3.1: the large-effect upgrade is for bodies "not downgraded
for any of the 5 factors") and when randomized evidence is rated up (§5.3:
"we have yet to find a compelling example").

Sources:
  Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating
    quality of evidence and strength of recommendations. BMJ 2008;336:924-926.
  Balshem H, Helfand M, Schünemann HJ, et al. GRADE guidelines: 3. Rating the
    quality of evidence. J Clin Epidemiol 2011;64:401-406.
  Schünemann H, Brożek J, Guyatt G, Oxman A (eds). GRADE Handbook, 2013.
    gdt.gradepro.org/app/handbook/handbook.html — §5.1-5.4, Tables 5.1-5.3,
    5.9, 6.4.
  Schünemann HJ, Cuello C, Akl EA, et al. GRADE guidelines: 18. How ROBINS-I
    and other tools to assess risk of bias in nonrandomized studies should be
    used to rate the certainty of a body of evidence. J Clin Epidemiol
    2019;111:105-114.  (basis of the `--start high` override)

Stdlib only. Python 3.9+.

Usage:
    python3 grade.py rate    --file body.json [--start high|moderate|low|very-low] [--json]
    python3 grade.py rate    --demo
    python3 grade.py sof     --file bodies.json [--json]
    python3 grade.py factors [--json]
    python3 grade.py --selftest

body.json:
    {"outcome": "Sleep-onset latency (min)", "design": "rct",
     "n_studies": 5, "n_participants": 412, "effect": "MD -12 (95% CI -18 to -3)",
     "downgrade": {"risk_of_bias": 0, "inconsistency": -1, "indirectness": 0,
                   "imprecision": {"level": -1, "reason": "CI spans the MID"},
                   "publication_bias": 0},
     "upgrade": {"large_effect": 0, "dose_response": 0, "confounding": 0},
     "reasons": {"inconsistency": "I2 = 68%"}}
    A factor is an integer or {"level": int, "reason": str}; `reasons` maps
    factor -> text for factors given as bare integers. `upgrade`, `reasons`,
    `outcome`, `n_studies`, `n_participants`, `effect`, `start` are optional.
bodies.json: a list of such objects, or {"question": "...", "outcomes": [...]}.
"""

import argparse
import json
import sys

# --- the GRADE scale ---------------------------------------------------------

# level -> (label, symbol). Symbols follow Handbook Table 6.4 (⊕ = plus,
# ◯ = empty circle); ⊕⊕⊕◯ is also the form used in the SKILL.md tables.
LEVELS = {
    4: ("High", "⊕⊕⊕⊕"),
    3: ("Moderate", "⊕⊕⊕◯"),
    2: ("Low", "⊕⊕◯◯"),
    1: ("Very low", "⊕◯◯◯"),
}

# Handbook Table 5.1 "Quality of Evidence Grades" (= Balshem 2011, Table 2).
INTERPRETATION = {
    4: "We are very confident that the true effect lies close to that of the estimate of the effect.",
    3: "We are moderately confident in the effect estimate: the true effect is likely to be close to "
       "the estimate of the effect, but there is a possibility that it is substantially different.",
    2: "Our confidence in the effect estimate is limited: the true effect may be substantially "
       "different from the estimate of the effect.",
    1: "We have very little confidence in the effect estimate: the true effect is likely to be "
       "substantially different from the estimate of effect.",
}

LEVEL_BY_NAME = {"high": 4, "moderate": 3, "low": 2, "very-low": 1, "very_low": 1, "very low": 1}

# Handbook §5.1.1: "randomized trials without important limitations provide
# high quality evidence"; "observational studies without special strengths or
# important limitations provide low quality evidence".
DESIGN_START = {"rct": 4, "observational": 2}
DESIGN_ALIASES = {
    "rct": "rct", "randomized": "rct", "randomised": "rct",
    "observational": "observational", "nrs": "observational", "nrsi": "observational",
}
DESIGN_TEXT = {"rct": "randomized trials", "observational": "observational studies"}
DESIGN_SOF = {"rct": ("RCT", "RCTs"), "observational": ("observational study", "observational studies")}

# Rate-down factors: (key, label, allowed values, value -> descriptor).
# Descriptors follow Balshem 2011 Table 3 (serious / very serious;
# publication bias: likely / very likely).
SERIOUS = {0: "not serious", -1: "serious", -2: "very serious"}
PUBBIAS = {0: "undetected", -1: "likely", -2: "very likely"}
DOWN_FACTORS = [
    ("risk_of_bias", "Risk of bias", (0, -1, -2), SERIOUS),
    ("inconsistency", "Inconsistency", (0, -1, -2), SERIOUS),
    ("indirectness", "Indirectness", (0, -1, -2), SERIOUS),
    ("imprecision", "Imprecision", (0, -1, -2), SERIOUS),
    ("publication_bias", "Publication bias", (0, -1, -2), PUBBIAS),
]

# Rate-up factors (Handbook Table 5.3, Table 5.9).
UP_FACTORS = [
    ("large_effect", "Large magnitude of effect", (0, 1, 2),
     {0: "no", 1: "large (RR >2 or <0.5)", 2: "very large (RR >5 or <0.2)"}),
    ("dose_response", "Dose-response gradient", (0, 1),
     {0: "no", 1: "gradient present"}),
    ("confounding", "Plausible residual confounding", (0, 1),
     {0: "no", 1: "all plausible residual confounding would reduce the demonstrated effect "
                 "(or suggest a spurious effect when none was observed)"}),
]

DOWN_KEYS = [f[0] for f in DOWN_FACTORS]
UP_KEYS = [f[0] for f in UP_FACTORS]

# Wording of the `factors` command: quoted / closely paraphrased from the
# GRADE Handbook (2013) with section references; the summary rows are
# Handbook Tables 5.2 and 5.3.
FACTOR_DEFINITIONS = [
    ("risk_of_bias", "Risk of bias (limitations in study design or execution)", "rate down 1 or 2 levels",
     "Handbook §5.2.1: \"Limitations in the study design and execution may bias the estimates of the "
     "treatment effect ... The more serious the limitations are, the more likely it is that the quality "
     "of evidence will be downgraded.\" RCT limitations (Table 5.4): lack of allocation concealment; "
     "lack of blinding; incomplete accounting of patients and outcome events; selective outcome "
     "reporting; other (e.g. stopping early for benefit). Observational limitations (Table 5.5): "
     "inappropriate eligibility criteria; flawed measurement of exposure and outcome; failure to "
     "adequately control confounding; incomplete or inadequately short follow-up. Do not average "
     "across studies — weigh each study's contribution to the pooled estimate."),
    ("inconsistency", "Inconsistency of results", "rate down 1 or 2 levels",
     "Handbook §5.2.2: \"Inconsistency refers to an unexplained heterogeneity of results.\" If "
     "investigators \"cannot identify a plausible explanation, the quality of evidence should be "
     "downgraded. Whether it is downgraded by one or two levels will depend on the magnitude of the "
     "inconsistency.\" Criteria: wide variance of point estimates; minimal or no overlap of CIs; "
     "heterogeneity test p < 0.05; large I² (rule of thumb: <40% may be low, 30-60% moderate, "
     "50-90% substantial, 75-100% considerable). Judged on relative measures (RR/HR)."),
    ("indirectness", "Indirectness of evidence", "rate down 1 or 2 levels",
     "Handbook §5.2.3: \"Direct evidence consists of research that directly compares the interventions "
     "which we are interested in, delivered to the populations in which we are interested, and "
     "measures the outcomes important to patients.\" Four sources of indirectness: differences in "
     "population, in interventions, in outcome measures (surrogates), and indirect comparisons "
     "(A vs C and B vs C instead of A vs B). Animal studies: generally rate down two levels."),
    ("imprecision", "Imprecision", "rate down 1 or 2 levels",
     "Handbook §5.2.4: \"results are imprecise when studies include relatively few patients and few "
     "events and thus have a wide confidence interval (CI) around the estimate of the effect.\" The 95% "
     "CI is the primary criterion and the optimal information size (OIS) a second, necessary one. "
     "Systematic reviews (§5.2.4.2): rate down if OIS is not met (unless n is very large, ≥2000-4000); "
     "if OIS is met and the CI overlaps no effect, rate down if it fails to exclude important benefit "
     "or harm. Guideline panels judge against the decision threshold."),
    ("publication_bias", "Publication bias", "rate down 1 or 2 levels",
     "Handbook §5.2.5: \"Publication bias is a systematic under-estimation or an over-estimation of the "
     "underlying beneficial or harmful effect due to the selective publication of studies.\" Suspect it "
     "with small (industry-sponsored) studies, funnel-plot asymmetry, lag bias, or a non-comprehensive "
     "search; selective outcome reporting is a risk-of-bias issue, not publication bias. Balshem 2011: "
     "-1 likely, -2 very likely."),
    ("large_effect", "Large magnitude of effect", "rate up 1 or 2 levels",
     "Handbook §5.3.1 / Table 5.9: large = \"RR >2 or <0.5 (based on direct evidence, with no plausible "
     "confounders)\" may increase 1 level; very large = \"RR >5 or <0.2 (based on direct evidence with no "
     "serious problems with risk of bias or precision, i.e. with sufficiently narrow confidence "
     "intervals)\" may increase 2 levels. Applies to RR or HR — convert OR to RR before judging. Only for "
     "bodies \"not downgraded for any of the 5 factors\"; rate up rarely and cautiously if the CI "
     "overlaps substantially with effects smaller than the threshold."),
    ("dose_response", "Dose-response gradient", "rate up 1 level",
     "Handbook §5.3.2: \"The presence of a dose-response gradient may increase our confidence in the "
     "findings of observational studies and thereby increase the quality of evidence\" (e.g. higher INR "
     "-> more bleeding; each hour of antibiotic delay -> higher sepsis mortality)."),
    ("confounding", "Effect of plausible residual confounding", "rate up 1 level",
     "Handbook §5.3.3: \"all plausible residual confounding from observational studies may be working to "
     "reduce the demonstrated effect or increase the effect, if no effect was observed\" (Guyatt 2008: "
     "\"all plausible confounding would reduce a demonstrated effect or suggest a spurious effect when "
     "results show no effect\"). E.g. sicker patients get the intervention yet fare better; or over-"
     "reporting was expected but no association was found."),
]

# --- built-in example: the SKILL.md worked example ---------------------------

DEMO = {
    "outcome": "Sleep-onset latency (min)",
    "design": "rct",
    "n_studies": 5,
    "n_participants": 412,
    "effect": "MD −12 min (95% CI −18 to −3)",
    "downgrade": {
        "risk_of_bias": {"level": 0, "reason": "4 of 5 studies low RoB-2 risk; the 'some concerns' study is ~8% of pooled weight"},
        "inconsistency": {"level": -1, "reason": "point estimates range −4 to −22 min, I² = 68%"},
        "indirectness": {"level": 0, "reason": "study populations match the PICO"},
        "imprecision": {"level": -1, "reason": "95% CI −18 to −3 spans the pre-set 10-min MID"},
        "publication_bias": {"level": 0, "reason": "symmetric funnel plot; two small unpublished trials unlikely to move the pool"},
    },
    "upgrade": {"large_effect": 0, "dose_response": 0, "confounding": 0},
}


# --- input parsing -----------------------------------------------------------


def _factor_value(raw, key, allowed, fallback_reason):
    """Return (level, reason) for one factor entry.

    Accepts an integer or {"level": int, "reason": str}. Booleans, floats,
    strings and out-of-range integers are rejected — a sign slip such as
    "imprecision": 1 must fail loudly, not silently rate up.
    """
    reason = fallback_reason
    if isinstance(raw, dict):
        extra = sorted(set(raw) - {"level", "reason"})
        if extra:
            raise ValueError(f"{key}: unknown field(s) {extra}; use {{\"level\": int, \"reason\": str}}")
        if "level" not in raw:
            raise ValueError(f"{key}: object form needs a \"level\" field")
        if "reason" in raw:
            if not isinstance(raw["reason"], str):
                raise ValueError(f"{key}: reason must be a string")
            reason = raw["reason"]
        raw = raw["level"]
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise ValueError(f"{key}: expected an integer in {list(allowed)}, got {raw!r}")
    if raw not in allowed:
        raise ValueError(f"{key}: {raw} is not one of {list(allowed)}")
    return raw, reason


def _optional_int(body, key):
    if key not in body or body[key] is None:
        return None
    v = body[key]
    if isinstance(v, bool) or not isinstance(v, int) or v < 1:
        raise ValueError(f"{key}: expected a positive integer, got {v!r}")
    return v


def _optional_str(body, key):
    if key not in body or body[key] is None:
        return None
    if not isinstance(body[key], str):
        raise ValueError(f"{key}: expected a string, got {body[key]!r}")
    return body[key]


def parse_start(name):
    """Map a level name (high | moderate | low | very-low) to 4..1."""
    key = str(name).strip().lower()
    if key not in LEVEL_BY_NAME:
        raise ValueError(f"start: {name!r} is not one of high | moderate | low | very-low")
    return LEVEL_BY_NAME[key]


def parse_body(data, start_override=None):
    """Validate one body-of-evidence object; return a normalised dict.

    All five rate-down factors must be present (GRADE requires an explicit
    yes/no decision on each — Handbook §5.4); rate-up factors default to 0.
    """
    if not isinstance(data, dict):
        raise ValueError("body must be a JSON object")
    known = {"outcome", "design", "n_studies", "n_participants", "effect",
             "downgrade", "upgrade", "reasons", "start"}
    unknown = sorted(set(data) - known)
    if unknown:
        raise ValueError(f"unknown top-level field(s) {unknown}; allowed: {sorted(known)}")

    design_raw = str(data.get("design", "")).strip().lower()
    if design_raw not in DESIGN_ALIASES:
        raise ValueError(f"design: {data.get('design')!r} is not one of rct | observational")
    design = DESIGN_ALIASES[design_raw]

    reasons = data.get("reasons") or {}
    if not isinstance(reasons, dict):
        raise ValueError("reasons: expected an object mapping factor -> text")
    bad = sorted(set(reasons) - set(DOWN_KEYS) - set(UP_KEYS))
    if bad:
        raise ValueError(f"reasons: unknown factor(s) {bad}")
    for k, v in reasons.items():
        if not isinstance(v, str):
            raise ValueError(f"reasons.{k}: expected a string")

    down_raw = data.get("downgrade")
    if not isinstance(down_raw, dict):
        raise ValueError("downgrade: expected an object with the five factors "
                         f"{DOWN_KEYS} (use 0 for 'not serious')")
    missing = [k for k in DOWN_KEYS if k not in down_raw]
    if missing:
        raise ValueError(f"downgrade: missing {missing} — GRADE requires each of the five "
                         "rate-down factors to be considered explicitly (0 = not serious)")
    bad = sorted(set(down_raw) - set(DOWN_KEYS))
    if bad:
        raise ValueError(f"downgrade: unknown factor(s) {bad}; allowed: {DOWN_KEYS}")

    up_raw = data.get("upgrade") or {}
    if not isinstance(up_raw, dict):
        raise ValueError(f"upgrade: expected an object with any of {UP_KEYS}")
    bad = sorted(set(up_raw) - set(UP_KEYS))
    if bad:
        raise ValueError(f"upgrade: unknown factor(s) {bad}; allowed: {UP_KEYS}")

    down = []
    for key, label, allowed, desc in DOWN_FACTORS:
        level, reason = _factor_value(down_raw[key], "downgrade." + key, allowed, reasons.get(key, ""))
        down.append({"factor": key, "label": label, "level": level, "descriptor": desc[level], "reason": reason})
    up = []
    for key, label, allowed, desc in UP_FACTORS:
        level, reason = _factor_value(up_raw.get(key, 0), "upgrade." + key, allowed, reasons.get(key, ""))
        up.append({"factor": key, "label": label, "level": level, "descriptor": desc[level], "reason": reason})

    if start_override is not None:
        start, source = parse_start(start_override), "--start"
    elif data.get("start") is not None:
        start, source = parse_start(data["start"]), "start field"
    else:
        start, source = DESIGN_START[design], "design"

    return {
        "outcome": _optional_str(data, "outcome"),
        "design": design,
        "n_studies": _optional_int(data, "n_studies"),
        "n_participants": _optional_int(data, "n_participants"),
        "effect": _optional_str(data, "effect"),
        "start": start,
        "start_source": source,
        "down": down,
        "up": up,
    }


def load_bodies(path):
    """Load a list of bodies (and optional question) from a JSON file."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    question = None
    if isinstance(data, dict) and "outcomes" in data:
        question = data.get("question")
        data = data["outcomes"]
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not data:
        raise ValueError("expected a body object, a list of bodies, or {\"outcomes\": [...]}")
    return question, data


# --- the rating (SKILL.md step 4) --------------------------------------------


def rate(body):
    """Apply GRADE arithmetic to a parsed body; return the result dict.

    final = clamp(start + sum(down) + sum(up), 1, 4). Warnings (never
    refusals) mark combinations the Handbook says should be rare.
    """
    sum_down = sum(f["level"] for f in body["down"])
    sum_up = sum(f["level"] for f in body["up"])
    raw = body["start"] + sum_down + sum_up
    final = max(1, min(4, raw))

    warnings = []
    downgraded = [f["factor"] for f in body["down"] if f["level"] < 0]
    if sum_up > 0 and downgraded:
        warnings.append(
            "rated up (+%d) although the body was rated down for %s — GRADE Handbook §5.3: rating "
            "down must be considered first and \"the decision to rate up should only rarely be made if "
            "serious limitations are present\"; §5.3.1 restricts the large-effect upgrade to bodies "
            "\"not downgraded for any of the 5 factors\"." % (sum_up, ", ".join(downgraded))
        )
    if sum_up > 0 and body["design"] == "rct":
        warnings.append(
            "rating up randomized evidence — GRADE Handbook §5.3: \"Although it is theoretically "
            "possible to rate up results from randomized control trials, we have yet to find a "
            "compelling example of such an instance.\""
        )
    notes = []
    if body["start_source"] != "design":
        notes.append(
            "starting level %s set by %s (design default for %s: %s) — GRADE guidelines 18: bodies of "
            "non-randomized studies appraised with ROBINS-I start High and carry the ROBINS-I judgement "
            "in the risk-of-bias factor."
            % (LEVELS[body["start"]][0], body["start_source"], DESIGN_TEXT[body["design"]],
               LEVELS[DESIGN_START[body["design"]]][0])
        )

    return {
        "outcome": body["outcome"],
        "design": body["design"],
        "n_studies": body["n_studies"],
        "n_participants": body["n_participants"],
        "effect": body["effect"],
        "start": {"level": body["start"], "label": LEVELS[body["start"]][0], "source": body["start_source"]},
        "downgrade": body["down"],
        "upgrade": body["up"],
        "sum_down": sum_down,
        "sum_up": sum_up,
        "raw": raw,
        "clamped": raw != final,
        "final": {
            "level": final,
            "label": LEVELS[final][0],
            "symbol": LEVELS[final][1],
            "interpretation": INTERPRETATION[final],
        },
        "warnings": warnings,
        "notes": notes,
    }


def arithmetic_trace(result):
    """'4 (High) −1 inconsistency −1 imprecision = 2 → Low', with the clamp shown."""
    terms = [f"{result['start']['level']} ({result['start']['label']})"]
    for f in result["downgrade"]:
        if f["level"]:
            terms.append(f"−{-f['level']} {f['factor']}")
    for f in result["upgrade"]:
        if f["level"]:
            terms.append(f"+{f['level']} {f['factor']}")
    trace = " ".join(terms) + f" = {result['raw']}"
    if result["clamped"]:
        bound = "floored at 1" if result["raw"] < 1 else "capped at 4"
        trace += f" → {bound}"
    return trace + f" → {result['final']['label']}"


def factors_applied(result):
    """Compact factor list for tables: '−1 inconsistency (reason); +1 large_effect (reason)'."""
    parts = []
    for f in result["downgrade"] + result["upgrade"]:
        if f["level"]:
            sign = "−" if f["level"] < 0 else "+"
            txt = f"{sign}{abs(f['level'])} {f['factor']}"
            if f["reason"]:
                txt += f" ({f['reason']})"
            parts.append(txt)
    return "; ".join(parts) if parts else "No factors applied"


def participants_cell(result):
    """'412 (5 RCTs)' — the SoF '№ of participants (studies)' cell."""
    n = result["n_participants"]
    k = result["n_studies"]
    singular, plural = DESIGN_SOF[result["design"]]
    studies = plural if k is None else f"{k} {singular if k == 1 else plural}"
    return f"{n if n is not None else '—'} ({studies})"


def sof_row(result):
    """One Summary-of-Findings markdown row (pipes escaped)."""
    def cell(s):
        return str(s).replace("|", "\\|")
    comments = []
    if result["effect"]:
        comments.append(result["effect"])
    comments.append(factors_applied(result))
    comments.extend("WARNING: " + w for w in result["warnings"])
    comments.extend("NOTE: " + n for n in result["notes"])
    return "| %s | %s | %s | %s |" % (
        cell(result["outcome"] or "—"),
        cell(participants_cell(result)),
        cell(f"{result['final']['symbol']} {result['final']['label']}"),
        cell(". ".join(comments)),
    )


# --- CLI ---------------------------------------------------------------------


def print_rate(result):
    head = "GRADE certainty of evidence"
    if result["outcome"]:
        head += f" — {result['outcome']}"
    print(head)
    body_bits = [DESIGN_TEXT[result["design"]]]
    if result["n_studies"] is not None:
        k = result["n_studies"]
        body_bits[0] = f"{k} {DESIGN_SOF[result['design']][0 if k == 1 else 1]}"
    if result["n_participants"] is not None:
        body_bits.append(f"n = {result['n_participants']}")
    if result["effect"]:
        body_bits.append(f"effect {result['effect']}")
    print("Body: " + ", ".join(body_bits))
    src = "" if result["start"]["source"] == "design" else f" (set by {result['start']['source']})"
    print(f"Starting level: {result['start']['label']} ({result['start']['level']}) — "
          f"{DESIGN_TEXT[result['design']]}{src}  [Handbook §5.1.1]")
    print()
    print("Rate down (Handbook Table 5.2; 0 / −1 serious / −2 very serious):")
    for f in result["downgrade"]:
        lvl = f"−{-f['level']}" if f["level"] else "0"
        print(f"  {f['factor']:<17}{lvl:>3}  {f['descriptor']:<13} {f['reason']}".rstrip())
    print("Rate up (Handbook Table 5.3; observational bodies not rated down):")
    for f in result["upgrade"]:
        lvl = f"+{f['level']}" if f["level"] else "0"
        print(f"  {f['factor']:<17}{lvl:>3}  {f['descriptor']:<13} {f['reason']}".rstrip())
    print()
    print(f"Arithmetic: {arithmetic_trace(result)}")
    print(f"Certainty: {result['final']['symbol']} {result['final']['label']}")
    print(f"Interpretation (Handbook Table 5.1): {result['final']['interpretation']}")
    for w in result["warnings"]:
        print(f"WARNING: {w}")
    for n in result["notes"]:
        print(f"NOTE: {n}")


def cmd_rate(args, parser):
    if args.demo:
        raw = DEMO
    elif args.file:
        try:
            _, bodies = load_bodies(args.file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: could not load {args.file}: {exc}", file=sys.stderr)
            return 2
        if len(bodies) != 1:
            print(f"error: rate takes exactly one body; {args.file} holds {len(bodies)} — use `sof`",
                  file=sys.stderr)
            return 2
        raw = bodies[0]
    else:
        parser.error("pass --file body.json or --demo")
    try:
        result = rate(parse_body(raw, args.start))
    except ValueError as exc:
        print(f"error: invalid body: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print_rate(result)
    return 0


def cmd_sof(args, parser):
    if args.demo:
        question, bodies = "CBT-I versus sleep-hygiene education for chronic insomnia", [DEMO]
    elif args.file:
        try:
            question, bodies = load_bodies(args.file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: could not load {args.file}: {exc}", file=sys.stderr)
            return 2
    else:
        parser.error("pass --file bodies.json or --demo")
    results = []
    for i, raw in enumerate(bodies, start=1):
        try:
            results.append(rate(parse_body(raw)))
        except ValueError as exc:
            print(f"error: body {i}: {exc}", file=sys.stderr)
            return 2
    if args.json:
        print(json.dumps({"question": question, "rows": results}, indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    if question:
        print(f"Summary of findings — {question}")
        print()
    print("| Outcome | № of participants (studies) | Certainty | Comments |")
    print("|---|---|---|---|")
    for r in results:
        print(sof_row(r))
    print()
    print("Certainty (GRADE Handbook Table 5.1): "
          + "; ".join(f"{LEVELS[k][1]} {LEVELS[k][0]}" for k in (4, 3, 2, 1)))
    return 0


def cmd_factors(args):
    if args.json:
        out = [{"factor": k, "label": lab, "consequence": cons, "definition": text}
               for k, lab, cons, text in FACTOR_DEFINITIONS]
        print(json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    print("GRADE factors — Guyatt et al. BMJ 2008;336:924; Balshem et al. J Clin Epidemiol 2011;64:401; "
          "GRADE Handbook (2013) §5, Tables 5.1-5.3 and 5.9")
    print()
    print("Starting level (Handbook §5.1.1): \"randomized trials without important limitations provide high "
          "quality evidence\"; \"observational studies without special strengths or important limitations "
          "provide low quality evidence\".")
    print()
    print("Rate DOWN — five factors, each ↓ 1 or 2 levels (Table 5.2):")
    for i, (k, lab, cons, text) in enumerate(FACTOR_DEFINITIONS[:5], start=1):
        print(f" {i}. {lab} [{k}] — {cons}")
        print(f"    {text}")
    print()
    print("Rate UP — three factors (Table 5.3); consider only after rating down, chiefly for observational")
    print("bodies not rated down for any of the five factors (§5.3):")
    for i, (k, lab, cons, text) in enumerate(FACTOR_DEFINITIONS[5:], start=6):
        print(f" {i}. {lab} [{k}] — {cons}")
        print(f"    {text}")
    print()
    print("Levels (Table 5.1; symbols Table 6.4):")
    for lvl in (4, 3, 2, 1):
        print(f"  {LEVELS[lvl][1]} {LEVELS[lvl][0]} ({lvl}) — {INTERPRETATION[lvl]}")
    return 0


# --- selftest ----------------------------------------------------------------


def _body(design, down=None, up=None, **extra):
    """Shorthand for selftest bodies: all five rate-down factors default to 0."""
    d = {k: 0 for k in DOWN_KEYS}
    d.update(down or {})
    b = {"design": design, "downgrade": d, "upgrade": up or {}}
    b.update(extra)
    return b


def run_selftest():
    """Hand-verified cases from the GRADE rules (Handbook §5.1-5.3) and the
    SKILL.md worked example. Every expected level was worked out by hand:
    start (RCT 4 / observational 2) + downgrades + upgrades, clamped to 1..4."""
    checks = []

    def check(name, ok):
        checks.append(bool(ok))
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    def level(body, start=None):
        return rate(parse_body(body, start))

    # 1. RCT, nothing rated down: 4 -> High.
    r = level(_body("rct"))
    check("RCT, no downgrades -> High (4)", r["final"]["level"] == 4 and r["final"]["label"] == "High"
          and r["final"]["symbol"] == "⊕⊕⊕⊕" and not r["warnings"])

    # 2. RCT, -1 risk of bias, -1 imprecision: 4 - 2 = 2 -> Low.
    r = level(_body("rct", {"risk_of_bias": -1, "imprecision": -1}))
    check("RCT, -1 RoB -1 imprecision -> Low (2)", r["final"]["level"] == 2 and r["final"]["symbol"] == "⊕⊕◯◯"
          and r["sum_down"] == -2 and not r["clamped"])
    check("arithmetic trace names each factor",
          arithmetic_trace(r) == "4 (High) −1 risk_of_bias −1 imprecision = 2 → Low")

    # 3. RCT, very serious risk of bias: 4 - 2 = 2 -> Low.
    r = level(_body("rct", {"risk_of_bias": -2}))
    check("RCT, -2 RoB (very serious) -> Low (2)", r["final"]["level"] == 2
          and r["downgrade"][0]["descriptor"] == "very serious")

    # 4. Observational, no downgrades, +1 large effect: 2 + 1 = 3 -> Moderate, no warning.
    r = level(_body("observational", up={"large_effect": 1}))
    check("observational, +1 large effect -> Moderate (3), no warning",
          r["final"]["level"] == 3 and r["final"]["symbol"] == "⊕⊕⊕◯" and not r["warnings"])

    # 5. Observational, +2 very large effect: 2 + 2 = 4 -> High.
    r = level(_body("observational", up={"large_effect": 2}))
    check("observational, +2 very large effect -> High (4)", r["final"]["level"] == 4
          and r["upgrade"][0]["descriptor"] == "very large (RR >5 or <0.2)")

    # 6. Observational, -1 imprecision: 2 - 1 = 1 -> Very low.
    r = level(_body("observational", {"imprecision": -1}))
    check("observational, -1 imprecision -> Very low (1)", r["final"]["level"] == 1
          and r["final"]["label"] == "Very low" and r["final"]["symbol"] == "⊕◯◯◯")

    # 7. Floor: RCT -2 RoB, -2 imprecision, -1 inconsistency: 4 - 5 = -1 -> floored at Very low.
    r = level(_body("rct", {"risk_of_bias": -2, "imprecision": -2, "inconsistency": -1}))
    check("floor: raw -1 -> Very low (1), clamped", r["raw"] == -1 and r["final"]["level"] == 1 and r["clamped"]
          and arithmetic_trace(r).endswith("= -1 → floored at 1 → Very low"))

    # 8. Ceiling: observational +1 +1 +1: 2 + 3 = 5 -> capped at High.
    r = level(_body("observational", up={"large_effect": 1, "dose_response": 1, "confounding": 1}))
    check("ceiling: raw 5 -> High (4), clamped", r["raw"] == 5 and r["final"]["level"] == 4 and r["clamped"])

    # 9. Upgrade combined with downgrade: arithmetic applied (2 - 1 + 1 = 2) but warned.
    r = level(_body("observational", {"risk_of_bias": -1}, {"large_effect": 1}))
    check("observational, -1 RoB +1 large effect -> Low (2) with rate-up-despite-rate-down warning",
          r["final"]["level"] == 2 and len(r["warnings"]) == 1 and "rated down for risk_of_bias" in r["warnings"][0])

    # 10. Rating up randomized evidence is warned (Handbook §5.3).
    r = level(_body("rct", {"imprecision": -1}, {"dose_response": 1}))
    check("RCT with an upgrade -> warning about rating up randomized evidence",
          any("randomized evidence" in w for w in r["warnings"]) and r["final"]["level"] == 4)

    # 11. --start override: observational body appraised with ROBINS-I starts High; -1 RoB -> Moderate.
    r = level(_body("observational", {"risk_of_bias": -1}), start="high")
    check("--start high (ROBINS-I) observational, -1 RoB -> Moderate (3), override noted",
          r["start"]["level"] == 4 and r["final"]["level"] == 3 and not r["warnings"]
          and any("set by --start" in n for n in r["notes"]))

    # 12. Per-body "start" field works the same way; CLI flag wins over it.
    r = level(_body("observational", start="high"))
    check("start field: observational started High -> High (4)", r["final"]["level"] == 4)
    r = level(_body("observational", start="high"), start="low")
    check("--start beats the start field", r["start"]["level"] == 2)

    # 13. Interpretations are the Handbook Table 5.1 sentences.
    check("interpretation text (Table 5.1) attached to the final level",
          level(_body("rct"))["final"]["interpretation"].startswith("We are very confident")
          and INTERPRETATION[1].startswith("We have very little confidence"))

    # 14. Reasons: object form and top-level `reasons` map both reach the trace; object form wins.
    b = _body("rct", {"imprecision": {"level": -1, "reason": "CI spans the MID"}, "inconsistency": -1},
              reasons={"inconsistency": "I2 = 68%", "imprecision": "ignored"})
    r = level(b)
    check("reasons: object reason wins, reasons map fills bare integers",
          r["downgrade"][3]["reason"] == "CI spans the MID" and r["downgrade"][1]["reason"] == "I2 = 68%")
    check("factors_applied lists signed factors with reasons",
          factors_applied(r) == "−1 inconsistency (I2 = 68%); −1 imprecision (CI spans the MID)")

    # 15. Publication-bias descriptors follow Balshem 2011 (likely / very likely).
    r = level(_body("rct", {"publication_bias": -2}))
    check("publication bias -2 -> 'very likely', Low (2)", r["downgrade"][4]["descriptor"] == "very likely"
          and r["final"]["level"] == 2)

    # 16. Demo reproduces the SKILL.md worked example: 5 RCTs, -1 inconsistency, -1 imprecision -> Low.
    r = rate(parse_body(DEMO))
    check("demo (SKILL.md worked example): High -1 inconsistency -1 imprecision -> ⊕⊕◯◯ Low",
          r["final"]["symbol"] == "⊕⊕◯◯" and r["final"]["label"] == "Low" and not r["warnings"])
    check("demo SoF row: '412 (5 RCTs)' and the two factors",
          sof_row(r).startswith("| Sleep-onset latency (min) | 412 (5 RCTs) | ⊕⊕◯◯ Low | MD −12 min (95% CI −18 to −3). "
                                "−1 inconsistency (point estimates range −4 to −22 min, I² = 68%); −1 imprecision"))

    # 17. Invalid input is rejected (exit 1 at the CLI): bad design, out-of-range or wrong-type
    #     values, missing / unknown factors, sign slips.
    def rejects(label, body, start=None):
        try:
            level(body, start)
        except ValueError:
            return True
        print(f"  (no error for {label})")
        return False

    check("invalid: design 'cohort study'", rejects("design", _body("cohort study")))
    check("invalid: downgrade -3", rejects("-3", _body("rct", {"risk_of_bias": -3})))
    check("invalid: downgrade +1 (sign slip)", rejects("+1", _body("rct", {"imprecision": 1})))
    check("invalid: upgrade large_effect 3", rejects("3", _body("observational", up={"large_effect": 3})))
    check("invalid: upgrade dose_response 2", rejects("2", _body("observational", up={"dose_response": 2})))
    check("invalid: boolean level", rejects("bool", _body("rct", {"risk_of_bias": True})))
    check("invalid: string level", rejects("str", _body("rct", {"risk_of_bias": "-1"})))
    b = _body("rct")
    del b["downgrade"]["indirectness"]
    check("invalid: missing rate-down factor", rejects("missing", b))
    b = _body("rct")
    b["downgrade"]["imprecison"] = 0
    check("invalid: unknown rate-down factor (typo)", rejects("typo", b))
    check("invalid: unknown rate-up factor", rejects("unknown up", _body("observational", up={"large": 1})))
    check("invalid: --start value", rejects("start", _body("rct"), start="medium"))
    check("invalid: n_participants 0", rejects("n", _body("rct", n_participants=0)))

    print(f"selftest OK ({len(checks)} checks passed)")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="GRADE certainty of evidence: start level by design, five rate-down and three "
        "rate-up factors, final level with the Handbook interpretation."
    )
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("rate", help="rate one outcome's body of evidence (trace + certainty)")
    p.add_argument("--file", help="JSON body of evidence (see module docstring for the schema)")
    p.add_argument("--demo", action="store_true", help="use the SKILL.md worked example (CBT-I, 5 RCTs)")
    p.add_argument("--start", choices=["high", "moderate", "low", "very-low"],
                   help="override the design-based starting level (e.g. high for ROBINS-I-appraised bodies)")
    p.add_argument("--json", action="store_true", help="emit the result as JSON")

    p = sub.add_parser("sof", help="Summary-of-Findings markdown table, one row per outcome")
    p.add_argument("--file", help="JSON list of bodies, or {\"question\": ..., \"outcomes\": [...]}")
    p.add_argument("--demo", action="store_true", help="use the SKILL.md worked example")
    p.add_argument("--json", action="store_true", help="emit the rows as JSON")

    p = sub.add_parser("factors", help="print the 5 rate-down + 3 rate-up factor definitions with citations")
    p.add_argument("--json", action="store_true", help="emit the definitions as JSON")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.command:
        parser.error("choose a command: rate | sof | factors  (or --selftest)")
    if args.command == "rate":
        return cmd_rate(args, parser)
    if args.command == "sof":
        return cmd_sof(args, parser)
    return cmd_factors(args)


if __name__ == "__main__":
    sys.exit(main())
