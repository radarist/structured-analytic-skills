#!/usr/bin/env python3
"""trl.py -- Technology Readiness Level (TRL) evidence-gate assessment.

Implements the scoring rule in ../SKILL.md ("Score Technology Readiness"):

  * The scale is NASA's nine TRLs, read through the SKILL.md software/AI
    adaptation table.  Each level has an *evidence requirement*; the table's
    checklist keys are the criteria below (levels 1-5 one criterion each,
    level 6 any ONE of three, levels 7-9 ALL listed criteria).
  * TRL is cumulative (SKILL.md step 2 "you cannot skip levels"): the
    evidenced TRL is the highest level L such that every level 1..L is met.
    Evidence at higher levels above a gap is reported, not credited.
  * Evidence items carry an ``evidence_type``.  ``vendor-claim`` and
    ``press`` are marketing-sourced and are NOT counted unless
    ``--accept-vendor-claims`` is given (SKILL.md anti-pattern: "do not
    accept a TRL claim from the vendor without independent evidence"); a
    level whose evidence is vendor-sourced only raises a caution.
  * Verdict = claimed TRL minus evidenced TRL.  Delta >= 2 is an
    "over-claim" and exits 2; delta 1 is noted (exit 0).

Level definitions printed by ``levels`` are quoted from the canonical
sources (wording differs slightly between them -- see ``levels --scale all``):

  * NASA -- J. C. Mankins, "Technology Readiness Levels: A White Paper",
    NASA Advanced Concepts Office, Office of Space Access and Technology,
    6 April 1995 (TRL 1-9 summary); NASA NPR 7123.1C, "NASA Systems
    Engineering Processes and Requirements", Appendix E "Technology
    Readiness Levels" (2020; w/Change 2, 2022) -- definition, hardware and
    software descriptions and success criteria per level (the same table
    appears in NASA/SP-2016-6105 Rev 2, Systems Engineering Handbook,
    Appendix G).  NPR 7123.1 states it takes precedence over other NASA
    directives on TRL definitions.
  * EU -- European Commission, Horizon 2020 Work Programme 2014-2015,
    General Annexes, Annex G "Technology readiness levels (TRL)" (extract of
    Part 19, Commission Decision C(2014)4995).
  * DoD -- Assistant Secretary of Defense for Research and Engineering,
    "Technology Readiness Assessment (TRA) Guidance", April 2011 (revision
    posted 13 May 2011), section 2.5 "TRL Definitions, Descriptions, and
    Supporting Information".

Stdlib only.  Python 3.9+.  Deterministic: no randomness, no clock.

Usage:
    python3 trl.py levels [--scale nasa|eu|dod|all] [--json]
    python3 trl.py criteria                      # SKILL.md checklist keys per level
    python3 trl.py template > evidence.json      # skeleton to fill in
    python3 trl.py assess --file evidence.json [--domain software|ai|hardware]
                          [--accept-vendor-claims] [--json]
    python3 trl.py assess --demo                 # SKILL.md worked example
    python3 trl.py --demo
    python3 trl.py --selftest

Exit codes: 0 = claim supported (or exceeds evidence by one level, noted);
            1 = invalid input / usage;
            2 = over-claim (claimed TRL exceeds evidenced TRL by >= 2 levels).

Input file (JSON):
    {"technology": "...", "claimed_trl": 6, "claimed_by": "vendor",
     "evidence": {
        "1": ["arXiv preprint ..."],                    # free-text items
        "6": {"case-study": true, "closed-beta-results": "..."},  # per-criterion
        "7": [{"criterion": "incident-reports", "item": "public status page",
               "evidence_type": "deployment", "source": "https://..."}, ...],
        "8": false }}                                   # bare boolean per level
Free-text items without a "criterion" are matched to a level's criteria by
keyword (shown in the report); at levels 7-9 an unmatched item satisfies no
criterion -- tag it.  evidence_type: demo | test-report | deployment |
peer-reviewed | vendor-claim | press (default "unspecified": counted, flagged).
"""

import argparse
import json
import re
import sys
import textwrap

EVIDENCE_TYPES = ("demo", "test-report", "deployment", "peer-reviewed", "vendor-claim", "press", "unspecified")
INSUFFICIENT_TYPES = ("vendor-claim", "press")  # marketing-sourced; not counted unless --accept-vendor-claims

# --- SKILL.md "The 9-level scale (software/AI adaptation)" ---------------------
# One entry per level: short label (SKILL.md output template), the software/AI
# adaptation, the combination rule, and the evidence criteria (key, description,
# keywords used to place untagged free-text items).  "any" = one satisfied
# criterion earns the level; "all" = every criterion is required.
LEVELS = [
    {"trl": 1, "short": "Basic principles", "adaptation": "Research paper describing mechanism", "rule": "any",
     "criteria": [("paper", "arXiv preprint / peer-reviewed paper",
                   ("arxiv", "peer-review", "peer review", "peer reviewed", "paper", "preprint", "journal",
                    "publication", "published", "thesis"))]},
    {"trl": 2, "short": "Concept", "adaptation": "Algorithm + problem statement", "rule": "any",
     "criteria": [("spec", "Written spec or working paper; no code required",
                   ("spec", "working paper", "working-paper", "problem statement", "design doc", "rfc",
                    "white paper", "whitepaper", "architecture", "algorithm"))]},
    {"trl": 3, "short": "PoC", "adaptation": "Working code on toy input", "rule": "any",
     "criteria": [("runnable-example", "Public repo with a runnable example",
                   ("repo", "github", "gitlab", "runnable", "example", "demo", "prototype", "notebook",
                    "proof of concept", "proof-of-concept", "poc", "code"))]},
    {"trl": 4, "short": "Component validation", "adaptation": "Component validated on controlled dataset", "rule": "any",
     "criteria": [("benchmark", "Benchmark results on a controlled dataset; benchmark-model-claims score >= 3",
                   ("benchmark", "dataset", "leaderboard", "controlled", "eval", "accuracy", "f1", "score"))]},
    {"trl": 5, "short": "Realistic environment", "adaptation": "Tested on realistic noisy data", "rule": "any",
     "criteria": [("third-party-eval", "Third-party evaluation or replication in an adjacent domain",
                   ("third-party", "third party", "independent", "replicat", "reproduc", "external",
                    "adjacent domain", "noisy", "realistic", "live repo", "real-world", "real world"))]},
    {"trl": 6, "short": "Pilot", "adaptation": "Pilot deployment with real users", "rule": "any",
     "criteria": [("case-study", "Case study",
                   ("case study", "case-study")),
                  ("named-customer-reference", "Named customer reference",
                   ("reference customer", "customer reference", "named customer", "named pilot",
                    "named company", "named-company", "logo")),
                  ("closed-beta-results", "Closed beta with published results",
                   ("closed beta", "beta", "early access", "design partner", "pilot users",
                    "pilot results", "rollout"))]},
    {"trl": 7, "short": "Production", "adaptation": "Production-grade deployment at one customer", "rule": "all",
     "criteria": [("production-case-study", "Production case study",
                   ("case study", "case-study", "in production", "production deployment",
                    "production rollout", "customer story", "ga product", "general availability")),
                  ("incident-reports", "Incident reports visible",
                   ("incident", "post-mortem", "postmortem", "status page", "outage", "uptime",
                    "on-call", "sre")),
                  ("named-reference-customer", "Named reference customer",
                   ("reference customer", "named customer", "customer reference", "named reference",
                    "logo", "testimonial"))]},
    {"trl": 8, "short": "Multi-customer", "adaptation": "Productized offering, multiple customers", "rule": "all",
     "criteria": [("customer-list", "Published customer list",
                   ("customer list", "customers page", "logos", "customer count", "customers",
                    "clients", "case studies")),
                  ("support-sla", "Support SLA",
                   ("sla", "support tier", "support plan", "enterprise support", "uptime guarantee",
                    "service level", "service-level")),
                  ("operational-metrics", "Operational metrics public",
                   ("operational metric", "metrics", "uptime", "throughput", "latency", "usage stat",
                    "dashboard", "status page", "incident report", "post-mortem", "postmortem"))]},
    {"trl": 9, "short": "Ecosystem", "adaptation": "De facto standard in the category", "rule": "all",
     "criteria": [("industry-adoption", "Industry-wide adoption",
                   ("industry-wide", "industry wide", "adoption", "de facto", "de-facto", "market share",
                    "standard", "ubiquit", "default")),
                  ("ecosystem-dependence", "Downstream ecosystem depends on it",
                   ("ecosystem", "downstream", "depends on", "dependency", "dependencies",
                    "integrations", "plugins", "built on", "built-on"))]},
]
LEVEL_BY_TRL = {lv["trl"]: lv for lv in LEVELS}

# --- Canonical level definitions (verbatim; see module docstring for sources) --
NASA_NPR = {  # NPR 7123.1C Appendix E, "Definition" column
    1: "Basic principles observed and reported.",
    2: "Technology concept and/or application formulated.",
    3: "Analytical and experimental proof-of-concept of critical function and/or characteristics.",
    4: "Component and/or breadboard validation in a laboratory environment.",
    5: "Component and/or brassboard validated in a relevant environment.",
    6: "System/sub-system model or prototype demonstration in a relevant environment.",
    7: "System prototype demonstration in an operational environment.",
    8: 'Actual system completed and "flight qualified" through test and demonstration.',
    9: "Actual system flight proven through successful mission operations.",
}
MANKINS_1995 = {  # Mankins (1995) "Technology Readiness Levels Summary", where it differs from NPR 7123.1C
    3: "Analytical and experimental critical function and/or characteristic proof-of-concept",
    5: "Component and/or breadboard validation in relevant environment",
    6: "System/subsystem model or prototype demonstration in a relevant environment (ground or space)",
    7: "System prototype demonstration in a space environment",
    8: 'Actual system completed and "flight qualified" through test and demonstration (ground or space)',
    9: 'Actual system "flight proven" through successful mission operations',
}
NASA_SOFTWARE = {  # NPR 7123.1C Appendix E, "Software Description" column
    1: "Scientific knowledge generated underpinning basic properties of software architecture and "
       "mathematical formulation.",
    2: "Practical application is identified but is speculative; no experimental proof or detailed analysis "
       "is available to support the conjecture. Basic properties of algorithms, representations, and "
       "concepts defined. Basic principles coded. Experiments performed with synthetic data.",
    3: "Development of limited functionality to validate critical properties and predictions using "
       "non-integrated software components.",
    4: "Key, functionality critical software components are integrated and functionally validated to "
       "establish interoperability and begin architecture development. Relevant environments defined and "
       "performance in the environment predicted.",
    5: "End-to-end software elements implemented and interfaced with existing systems/simulations "
       "conforming to target environment. End-to-end software system tested in relevant environment, "
       "meeting predicted performance. Operational environment performance predicted. Prototype "
       "implementations developed.",  # 7123.1C prints a truncated "Implementations."; last sentence as in NPR 7123.1A/B
    6: "Prototype implementations of the software demonstrated on full-scale, realistic problems. "
       "Partially integrated with existing hardware/software systems. Limited documentation available. "
       "Engineering feasibility fully demonstrated.",
    7: "Prototype software exists having all key functionality available for demonstration and test. "
       "Well integrated with operational hardware/software systems demonstrating operational feasibility. "
       "Most software bugs removed. Limited documentation available.",
    8: "All software has been thoroughly debugged and fully integrated with all operational hardware and "
       "software systems. All user documentation, training documentation, and maintenance documentation "
       "completed. All functionality successfully demonstrated in simulated operational scenarios. "
       "Verification and Validation completed.",
    9: "All software has been thoroughly debugged and fully integrated with all operational hardware and "
       "software systems. All documentation has been completed. Sustaining software support is in place. "
       "System has been successfully operated in the operational environment.",
}
NASA_SUCCESS = {  # NPR 7123.1C Appendix E, "Success criteria" column
    1: "Peer reviewed documentation of research underlying the proposed concept/application.",
    2: "Documented description of the application/concept that addresses feasibility and benefit.",
    3: "Documented analytical/experimental results validating predictions of key parameters.",
    4: "Documented test performance demonstrating agreement with analytical predictions. Documented "
       "definition of potentially relevant environment.",
    5: "Documented test performance demonstrating agreement with analytical predictions. Documented "
       "definition of scaling requirements. Performance predictions are made for subsequent development "
       "phases.",
    6: "Documented test performance demonstrating agreement with analytical predictions.",
    7: "Documented test performance demonstrating agreement with analytical predictions.",
    8: "Documented test performance verifying analytical predictions.",
    9: "Documented mission operational results.",
}
EU_H2020 = {  # Horizon 2020 General Annex G (Commission Decision C(2014)4995)
    1: "basic principles observed",
    2: "technology concept formulated",
    3: "experimental proof of concept",
    4: "technology validated in lab",
    5: "technology validated in relevant environment (industrially relevant environment in the case of "
       "key enabling technologies)",
    6: "technology demonstrated in relevant environment (industrially relevant environment in the case "
       "of key enabling technologies)",
    7: "system prototype demonstration in operational environment",
    8: "system complete and qualified",
    9: "actual system proven in operational environment (competitive manufacturing in the case of key "
       "enabling technologies; or in space)",
}
DOD_2011 = {  # DoD TRA Guidance (April 2011), section 2.5, "Definition" column
    1: "Basic principles observed and reported.",
    2: "Technology concept and/or application formulated.",
    3: "Analytical and experimental critical function and/or characteristic proof of concept.",
    4: "Component and/or breadboard validation in a laboratory environment.",
    5: "Component and/or breadboard validation in a relevant environment.",
    6: "System/subsystem model or prototype demonstration in a relevant environment.",
    7: "System prototype demonstration in an operational environment.",
    8: "Actual system completed and qualified through test and demonstration.",
    9: "Actual system proven through successful mission operations.",
}
DOD_SUPPORT = {  # DoD TRA Guidance (2011), "Supporting Information" column (the evidence a TRA asks for)
    1: "Published research that identifies the principles that underlie this technology. References to "
       "who, where, when.",
    2: "Publications or other references that outline the application being considered and that provide "
       "analysis to support the concept.",
    3: "Results of laboratory tests performed to measure parameters of interest and comparison to "
       "analytical predictions for critical subsystems. References to who, where, and when these tests "
       "and comparisons were performed.",
    4: "System concepts that have been considered and results from testing laboratory-scale "
       "breadboard(s). References to who did this work and when. Provide an estimate of how breadboard "
       "hardware and test results differ from the expected system goals.",
    5: "Results from testing laboratory breadboard system are integrated with other supporting elements "
       'in a simulated operational environment. How does the "relevant environment" differ from the '
       "expected operational environment? How do the test results compare with expectations? What "
       "problems, if any, were encountered?",
    6: "Results from laboratory testing of a prototype system that is near the desired configuration in "
       "terms of performance, weight, and volume. How did the test environment differ from the "
       "operational environment? Who performed the tests? How did the test compare with expectations?",
    7: "Results from testing a prototype system in an operational environment. Who performed the tests? "
       "How did the test compare with expectations? What problems, if any, were encountered?",
    8: "Results of testing the system in its final configuration under the expected range of "
       "environmental conditions in which it will be expected to operate. Assessment of whether it will "
       "meet its operational requirements.",
    9: "OT&E reports.",
}
SCALE_NOTES = [
    "TRL 6 is a RELEVANT environment in NASA (Mankins 1995 adds 'ground or space'), DoD and EU; the "
    "OPERATIONAL environment starts at TRL 7 (Mankins 1995 wrote 'space environment' for TRL 7; NPR "
    "7123.1, DoD and EU write 'operational environment').",
    "EU TRL 5-6 add 'industrially relevant environment' for key enabling technologies and EU TRL 9 adds "
    "'competitive manufacturing ... or in space'.",
    "NASA TRL 8-9 say 'flight qualified' / 'flight proven'; DoD says 'qualified' / 'proven'; EU says "
    "'system complete and qualified' / 'actual system proven in operational environment'.",
    "NPR 7123.1C TRL 3 reorders Mankins' wording and TRL 5 says 'brassboard validated' where Mankins and "
    "DoD say 'breadboard validation'.",
]

# --- Domain notes (SKILL.md software/AI adaptation; NASA software column) ------
DOMAIN_NOTES = {
    "software": [
        "Relevant environment (TRL 5) = realistic, noisy, representative data and interfaces outside "
        "production; operational environment (TRL 6-7) = real users and real traffic: a pilot earns TRL 6, "
        "a production-grade deployment at one customer TRL 7 (SKILL.md software/AI adaptation).",
        "A benchmark, however large, is a laboratory environment and evidences TRL 4, not 5. NPR 7123.1C "
        "software column: TRL 4 = key components integrated and validated in the lab; TRL 5 = end-to-end "
        "software tested in a relevant environment; TRL 6 = prototype on full-scale realistic problems, "
        "partially integrated; TRL 7 = well integrated with operational systems, most bugs removed.",
        "Software rarely reaches a pure TRL 9 -- 'ecosystem dependence' (downstream projects depend on it) "
        "is the best proxy (SKILL.md).",
    ],
    "ai": [
        "For AI/ML systems a held-out test set is still the laboratory (TRL 4); TRL 5 needs a third-party "
        "evaluation on data with realistic noise or distribution shift; TRL 6 needs real users with the "
        "live failure modes (false positives, silent misses) monitored and reported.",
        "A retrained or upgraded model is a new technology element: Mankins (1995) excludes planned "
        "product improvements from inheriting TRL 9 -- re-enter the scale at the level the new evidence "
        "supports.",
    ],
    "hardware": [
        "SKILL.md scopes this checklist to software/AI and defers chips, sensors and other hardware to "
        "HRL/MRL. Use the NASA/DoD hardware definitions (`levels --scale nasa|dod`) and pair the TRL with "
        "a Manufacturing Readiness Level; the software criteria used here (repo, benchmark, SLA) are "
        "proxies only.",
    ],
}
DOMAIN_NOTES["ai"] = DOMAIN_NOTES["software"] + DOMAIN_NOTES["ai"]

# --- SKILL.md worked example: AI code-review agents, vendor claims TRL 8 -------
DEMO = {
    "technology": "AI code-review agents (LLM-based review of pull requests)",
    "claimed_trl": 8,
    "claimed_by": "vendor",
    "evidence": {
        "1": [{"item": "peer-reviewed work on LLM code understanding (multiple papers)",
               "evidence_type": "peer-reviewed"}],
        "2": [{"item": "published architectures for diff-aware review", "evidence_type": "peer-reviewed"}],
        "3": [{"item": "open-source prototypes with reproducible demos", "evidence_type": "demo"}],
        "4": [{"item": "published benchmarks on defect-detection datasets (public PR corpora)",
               "evidence_type": "test-report"}],
        "5": [{"item": "third-party evaluations on live repos, incl. false-positive rates",
               "evidence_type": "test-report"}],
        "6": [{"criterion": "named-customer-reference",
               "item": "named-company engineering blogs describing internal rollouts with metrics",
               "evidence_type": "deployment"}],
        "7": [{"criterion": ["production-case-study", "named-reference-customer"],
               "item": "multiple vendors selling GA products to named customers", "evidence_type": "deployment"},
              {"criterion": "incident-reports", "item": "public status pages with incident history",
               "evidence_type": "deployment"}],
        "8": [{"criterion": "customer-list", "item": "vendor case studies and logo walls",
               "evidence_type": "vendor-claim"},
              {"criterion": "support-sla", "item": "SLAs and support tiers in published enterprise contracts",
               "evidence_type": "deployment"}],
        "9": [],
    },
}


class InputError(ValueError):
    """Raised when the evidence file is malformed."""


# --- input parsing -----------------------------------------------------------


def _criteria_keys(trl):
    return [key for key, _, _ in LEVEL_BY_TRL[trl]["criteria"]]


def _keyword_match(trl, text):
    """Place an untagged item: the sole criterion at single-criterion levels
    (1-5); otherwise every criterion whose keywords occur (word-initial) in the
    text. Returns (keys, how) with how in {"sole", "keyword", "generic"}."""
    keys = _criteria_keys(trl)
    if len(keys) == 1:
        return keys, "sole"
    low = text.lower()
    hits = [key for key, _, keywords in LEVEL_BY_TRL[trl]["criteria"]
            if any(re.search(r"\b" + re.escape(kw), low) for kw in keywords)]
    return hits, ("keyword" if hits else "generic")


def _make_item(trl, text, criteria, matched, evidence_type, source, asserted=False):
    text = str(text).strip()
    if not text and not asserted:
        raise InputError(f"TRL {trl}: evidence item text must not be empty")
    et = str(evidence_type or "unspecified").strip().lower()
    if et not in EVIDENCE_TYPES:
        raise InputError(f"TRL {trl}: evidence_type {evidence_type!r} not in {'|'.join(EVIDENCE_TYPES)}")
    for c in criteria:
        if c not in _criteria_keys(trl):
            raise InputError(f"TRL {trl}: unknown criterion {c!r}; valid keys: {', '.join(_criteria_keys(trl))}")
    return {"text": text, "criteria": sorted(set(criteria)), "matched": matched,
            "evidence_type": et, "source": source, "asserted": asserted}


def _parse_item(trl, raw, forced_criteria=None, default_type="unspecified"):
    """One evidence item: str | dict -> normalised item dict."""
    if isinstance(raw, str):
        crit, how = (list(forced_criteria), "explicit") if forced_criteria else _keyword_match(trl, raw)
        return _make_item(trl, raw, crit, how, default_type, None)
    if isinstance(raw, dict):
        text = raw.get("item", raw.get("text", raw.get("description", "")))
        crit = raw.get("criterion", raw.get("criteria"))
        if crit is None:
            crit, how = (list(forced_criteria), "explicit") if forced_criteria else _keyword_match(trl, str(text))
        else:
            crit, how = ([crit] if isinstance(crit, str) else list(crit)), "explicit"
        et = raw.get("evidence_type", raw.get("type", default_type))
        return _make_item(trl, text, crit, how, et, raw.get("source"))
    raise InputError(f"TRL {trl}: evidence item must be a string or object, got {type(raw).__name__}")


def _parse_level(trl, raw):
    """Level value: bool | str | list | dict -> list of items."""
    if isinstance(raw, bool):
        if not raw:
            return []
        # bare `true`: every criterion asserted, no artefact recorded
        return [_make_item(trl, "(asserted, no evidence item recorded)", _criteria_keys(trl), "explicit",
                           "unspecified", None, asserted=True)]
    if raw is None:
        return []
    if isinstance(raw, str):
        return [_parse_item(trl, raw)]
    if isinstance(raw, list):
        return [_parse_item(trl, r) for r in raw]
    if isinstance(raw, dict):
        if "items" in raw:  # {"items": [...], "evidence_type": "..."}: level-wide default type
            if not isinstance(raw["items"], list):
                raise InputError(f"TRL {trl}: 'items' must be a list")
            default_type = raw.get("evidence_type", "unspecified")
            return [_parse_item(trl, r, default_type=default_type) for r in raw["items"]]
        items = []
        for key in sorted(raw):
            val = raw[key]
            if key not in _criteria_keys(trl):
                raise InputError(f"TRL {trl}: unknown criterion {key!r}; valid keys: {', '.join(_criteria_keys(trl))}")
            if isinstance(val, bool):
                if val:
                    items.append(_make_item(trl, "(asserted, no evidence item recorded)", [key], "explicit",
                                            "unspecified", None, asserted=True))
                continue
            if val is None:
                continue
            for r in (val if isinstance(val, list) else [val]):
                items.append(_parse_item(trl, r, forced_criteria=[key]))
        return items
    raise InputError(f"TRL {trl}: level value must be bool, string, list or object")


def parse_case(data):
    """Validate a JSON case and normalise it to
    {"technology", "claimed_trl", "claimed_by", "items": {trl: [item, ...]}}."""
    if not isinstance(data, dict):
        raise InputError("top level must be a JSON object")
    tech = str(data.get("technology") or data.get("subject") or "(unnamed technology)")
    claimed = data.get("claimed_trl")
    if claimed is not None:
        if isinstance(claimed, bool) or not isinstance(claimed, int) or not 1 <= claimed <= 9:
            raise InputError(f"claimed_trl must be an integer 1..9, got {claimed!r}")
    claimed_by = data.get("claimed_by")
    evidence = data.get("evidence", {})
    if not isinstance(evidence, dict):
        raise InputError("'evidence' must be an object keyed by level '1'..'9'")
    items = {trl: [] for trl in range(1, 10)}
    for key in sorted(evidence, key=str):
        try:
            trl = int(str(key).strip().lower().replace("trl", "").strip())
        except ValueError:
            raise InputError(f"evidence key {key!r} is not a TRL 1..9")
        if not 1 <= trl <= 9:
            raise InputError(f"evidence key {key!r} is not a TRL 1..9")
        items[trl] = _parse_level(trl, evidence[key])
    return {"technology": tech, "claimed_trl": claimed,
            "claimed_by": str(claimed_by) if claimed_by is not None else None, "items": items}


def load_file(path):
    if path == "-":
        data = json.load(sys.stdin)
    else:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    return parse_case(data)


# --- the assessment (SKILL.md steps 2-4) --------------------------------------


def assess(case, accept_vendor=False):
    """Apply the cumulative evidence-gate rule. Returns a plain dict (JSON-able)."""
    levels = []
    for lv in LEVELS:
        trl = lv["trl"]
        items = [dict(it, counted=accept_vendor or it["evidence_type"] not in INSUFFICIENT_TYPES)
                 for it in case["items"].get(trl, [])]
        criteria = []
        satisfied = []
        vendor_reliant = []  # criteria whose only evidence is vendor-claim/press
        for key, desc, _ in lv["criteria"]:
            assigned = [it for it in items if key in it["criteria"]]
            counted = [it for it in assigned if it["counted"]]
            ok = bool(counted)
            if ok:
                satisfied.append(key)
            if assigned and all(it["evidence_type"] in INSUFFICIENT_TYPES for it in assigned):
                vendor_reliant.append(key)
            criteria.append({"key": key, "description": desc, "satisfied": ok,
                             "items": [_item_view(it) for it in assigned]})
        needs_independent = [] if accept_vendor else list(vendor_reliant)
        generic = [it for it in items if not it["criteria"]]
        generic_counted = [it for it in generic if it["counted"]]
        if lv["rule"] == "any":
            met = bool(satisfied) or bool(generic_counted)
        else:
            met = len(satisfied) == len(lv["criteria"])
        any_counted = any(it["counted"] for it in items)
        vendor_only = bool(items) and all(it["evidence_type"] in INSUFFICIENT_TYPES for it in items)
        if met:
            status = "met"
        elif any_counted:
            status = "partial"
        elif items:
            status = "unverified"
        else:
            status = "not met"
        levels.append({
            "trl": trl, "short": lv["short"], "adaptation": lv["adaptation"], "rule": lv["rule"],
            "status": status, "met": met, "criteria": criteria,
            "generic_items": [_item_view(it) for it in generic],
            "vendor_only": vendor_only, "vendor_reliant": vendor_reliant,
            "needs_independent": needs_independent,
            "asserted_only": bool(items) and all(it["asserted"] for it in items),
            "untyped": sum(1 for it in items if it["evidence_type"] == "unspecified" and not it["asserted"]),
            "unassigned": [it["text"] for it in generic] if lv["rule"] == "all" else [],
        })

    evidenced = 0
    for lv in levels:  # highest contiguous run of met levels starting at TRL 1
        if lv["met"]:
            evidenced = lv["trl"]
        else:
            break
    met_above = [lv["trl"] for lv in levels if lv["met"] and lv["trl"] > evidenced]
    gaps = [lv["trl"] for lv in levels
            if not lv["met"] and met_above and evidenced < lv["trl"] < max(met_above)]

    claimed = case["claimed_trl"]
    delta = None if claimed is None else claimed - evidenced
    if delta is None:
        verdict, exit_code = "no-claim", 0
    elif delta >= 2:
        verdict, exit_code = "over-claim", 1
    elif delta == 1:
        verdict, exit_code = "one-level-gap", 0
    elif delta == 0:
        verdict, exit_code = "supported", 0
    else:
        verdict, exit_code = "under-claim", 0

    next_level = None
    if evidenced < 9:
        nxt = levels[evidenced]  # index evidenced == TRL evidenced+1
        missing = [c for c in nxt["criteria"] if not c["satisfied"]]
        next_level = {
            "trl": nxt["trl"], "short": nxt["short"], "rule": nxt["rule"], "status": nxt["status"],
            "missing": [{"key": c["key"], "description": c["description"]} for c in missing],
            "needs_independent_confirmation": list(nxt["needs_independent"]),
        }

    cautions = []
    for lv in levels:
        if lv["vendor_only"]:
            if accept_vendor:
                cautions.append(f"TRL {lv['trl']}: evidence is vendor-sourced only (vendor-claim/press) and was "
                                "counted because --accept-vendor-claims was given; verify the cited pilot/customer.")
            else:
                cautions.append(f"TRL {lv['trl']}: evidence is vendor-sourced only (vendor-claim/press); not "
                                "counted (pass --accept-vendor-claims to count it).")
        elif lv["vendor_reliant"]:
            if accept_vendor:
                cautions.append(f"TRL {lv['trl']}: {', '.join(lv['vendor_reliant'])} counted from vendor-claim/press "
                                "items only because --accept-vendor-claims was given; verify independently.")
            else:
                cautions.append(f"TRL {lv['trl']}: {', '.join(lv['vendor_reliant'])} evidenced only by "
                                "vendor-claim/press items; independent confirmation needed.")
        if lv["asserted_only"]:
            cautions.append(f"TRL {lv['trl']}: asserted true without an evidence item; record the artefact "
                            "(URL, DOI, customer name) before shipping the score.")
        if lv["unassigned"]:
            cautions.append(f"TRL {lv['trl']}: {len(lv['unassigned'])} item(s) matched no criterion and satisfy "
                            f"nothing at an all-criteria level; tag with \"criterion\": one of "
                            f"{', '.join(_criteria_keys(lv['trl']))}.")
    if gaps:
        cautions.append(f"TRL {', '.join(str(g) for g in gaps)} unevidenced although TRL "
                        f"{', '.join(str(m) for m in met_above)} {'has' if len(met_above) == 1 else 'have'} "
                        f"evidence; TRL is cumulative, so the evidenced TRL stops at {evidenced}.")
    untyped = sum(lv["untyped"] for lv in levels)
    if untyped:
        cautions.append(f"{untyped} item(s) carry no evidence_type; counted, but type them "
                        "(demo|test-report|deployment|peer-reviewed|vendor-claim|press) so the vendor gate can act.")
    if claimed is not None and delta is not None and delta > 0 and (case["claimed_by"] or "").lower() == "vendor":
        cautions.append("Self-reported (vendor) TRL exceeds the evidence; check the cited pilot/customer "
                        "directly (SKILL.md anti-pattern 1).")

    return {
        "technology": case["technology"], "scale": "NASA TRL 1-9, SKILL.md software/AI adaptation",
        "claimed_trl": claimed, "claimed_by": case["claimed_by"], "evidenced_trl": evidenced,
        "delta": delta, "verdict": verdict, "exit_code": exit_code,
        "accept_vendor_claims": bool(accept_vendor),
        "levels": levels, "gaps": gaps, "evidence_above_gap": met_above,
        "next_level": next_level, "cautions": cautions,
    }


def _item_view(it):
    return {"item": it["text"], "evidence_type": it["evidence_type"], "counted": it["counted"],
            "source": it["source"], "matched": it["matched"], "criteria": it["criteria"]}


# --- text rendering ----------------------------------------------------------


def _symbols():
    enc = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        "✓✗⚠→".encode(enc)
        return {"met": "✓", "not met": "✗", "partial": "⚠", "unverified": "?", "arrow": "→"}
    except (UnicodeEncodeError, LookupError):
        return {"met": "OK", "not met": "--", "partial": "~", "unverified": "?", "arrow": "->"}


def _item_line(view):
    tag = view["evidence_type"]
    if not view["counted"]:
        tag += ", NOT counted"
    if view["matched"] == "keyword":
        tag += ", keyword-matched"
    return f"{view['item']} [{tag}]"


def render_text(result, domain=None):
    sym = _symbols()
    out = []
    out.append(f"Technology Readiness Assessment -- {result['technology']}")
    out.append(f"Scale: {result['scale']}")
    claimed = result["claimed_trl"]
    by = f" ({result['claimed_by']})" if result["claimed_by"] else ""
    if claimed is None:
        out.append(f"Claimed TRL: none stated   Evidenced TRL: {result['evidenced_trl']}")
    else:
        d = result["delta"]
        out.append(f"Claimed TRL: {claimed}{by}   Evidenced TRL: {result['evidenced_trl']}   "
                   f"Delta: {d:+d} (claim {'exceeds' if d > 0 else 'is below' if d < 0 else 'matches'} evidence"
                   f"{'' if d == 0 else f' by {abs(d)} level' + ('s' if abs(d) != 1 else '')})")
    out.append("")
    out.append(f"{'TRL':<4} {'Level':<22} {'Status':<13} Evidence")
    for lv in result["levels"]:
        status = f"{sym[lv['status']]} {lv['status']}"
        multi_option = lv["rule"] == "any" and len(lv["criteria"]) > 1
        lines = []
        if multi_option and not lv["met"]:
            lines.append(f"needs one of: {' | '.join(c['key'] for c in lv['criteria'])}")
        for c in lv["criteria"]:
            for v in c["items"]:
                lines.append(f"{c['key']}: {_item_line(v)}")
            if not c["items"] and not multi_option and (lv["rule"] == "all" or not lv["met"]):
                lines.append(f"{c['key']}: {sym['not met']} missing ({c['description']})")
        for v in lv["generic_items"]:
            lines.append(f"(criterion unspecified): {_item_line(v)}")
        if not lines:
            lines.append("--")
        out.append(f"{lv['trl']:<4} {lv['short']:<22} {status:<13} {lines[0]}")
        for extra in lines[1:]:
            out.append(f"{'':<4} {'':<22} {'':<13} {extra}")
    out.append("")
    if result["gaps"]:
        out.append(f"Gaps: TRL {', '.join(str(g) for g in result['gaps'])} unevidenced below evidence at TRL "
                   f"{', '.join(str(m) for m in result['evidence_above_gap'])} -- not credited (TRL is cumulative).")
    else:
        out.append(f"Gaps: none (evidence contiguous through TRL {result['evidenced_trl']}).")
    nxt = result["next_level"]
    if nxt:
        out.append(f"To advance TRL {result['evidenced_trl']} {sym['arrow']} {nxt['trl']} ({nxt['short']}), still needed:")
        if nxt["rule"] == "any" and len(nxt["missing"]) == len(LEVEL_BY_TRL[nxt["trl"]]["criteria"]) > 1:
            out.append("  - one of: " + "; ".join(f"{m['key']} ({m['description']})" for m in nxt["missing"]))
        else:
            for m in nxt["missing"]:
                if m["key"] in nxt["needs_independent_confirmation"]:
                    continue
                out.append(f"  - {m['key']}: {m['description']}")
        if nxt["needs_independent_confirmation"]:
            out.append("  - independent confirmation of: " + ", ".join(nxt["needs_independent_confirmation"])
                       + " (currently vendor-claim/press only)")
        if not nxt["missing"] and not nxt["needs_independent_confirmation"]:
            out.append("  - (criteria satisfied; level blocked only by the gap below it)")
    else:
        out.append("TRL 9 evidenced -- no higher level on the scale.")
    if result["cautions"]:
        out.append("Cautions:")
        for c in result["cautions"]:
            out.append("  - " + c)
    if domain:
        out.append(f"Domain notes ({domain}):")
        for note in DOMAIN_NOTES[domain]:
            out.extend(textwrap.wrap(note, width=96, initial_indent="  - ", subsequent_indent="    "))
    verdicts = {
        "no-claim": "no TRL claim to test; evidenced TRL {e}",
        "supported": "claim of TRL {c} is supported by evidence (evidenced TRL {e})",
        "under-claim": "claim of TRL {c} is below the evidenced TRL {e} (conservative claim)",
        "one-level-gap": "TRL {e} -- claim of TRL {c} exceeds the evidence by one level; note the gap",
        "over-claim": "TRL {e} -- OVER-CLAIM: claim of TRL {c} exceeds the evidence by {d} levels (exit 2)",
    }
    out.append("Verdict: " + verdicts[result["verdict"]].format(
        c=claimed, e=result["evidenced_trl"], d=result["delta"]))
    return "\n".join(out)


def render_levels(scale):
    out = []
    lines = {"nasa": [], "eu": [], "dod": []}
    for trl in range(1, 10):
        lines["nasa"].append((trl, NASA_NPR[trl], MANKINS_1995.get(trl), NASA_SOFTWARE[trl], NASA_SUCCESS[trl]))
        lines["eu"].append((trl, EU_H2020[trl]))
        lines["dod"].append((trl, DOD_2011[trl], DOD_SUPPORT[trl]))

    def wrap(label, text, indent=7):
        return textwrap.wrap(text, width=96, initial_indent=" " * indent + label, subsequent_indent=" " * (indent + len(label)))

    if scale in ("nasa", "all"):
        out.append("NASA TRL definitions -- NPR 7123.1C Appendix E (2020; w/Change 2, 2022); Mankins (1995) wording where it differs")
        for trl, d, mk, sw, sc in lines["nasa"]:
            out.append(f"TRL {trl}  {d}")
            if mk:
                out.extend(wrap("Mankins 1995: ", mk))
            out.extend(wrap("software:     ", sw))
            out.extend(wrap("success:      ", sc))
        out.append("")
    if scale in ("eu", "all"):
        out.append("EU TRL definitions -- Horizon 2020 General Annex G (Commission Decision C(2014)4995)")
        for trl, d in lines["eu"]:
            out.extend(textwrap.wrap(f"TRL {trl}  {d}", width=96, subsequent_indent="       "))
        out.append("")
    if scale in ("dod", "all"):
        out.append("DoD TRL definitions -- Technology Readiness Assessment (TRA) Guidance, ASD(R&E), April 2011, section 2.5")
        for trl, d, sup in lines["dod"]:
            out.append(f"TRL {trl}  {d}")
            out.extend(wrap("supporting information: ", sup))
        out.append("")
    if scale == "all":
        out.append("Wording differences:")
        for note in SCALE_NOTES:
            out.extend(textwrap.wrap(note, width=96, initial_indent="  - ", subsequent_indent="    "))
    return "\n".join(out).rstrip("\n")


def levels_json(scale):
    data = {}
    for trl in range(1, 10):
        row = {}
        if scale in ("nasa", "all"):
            row["nasa"] = {"definition": NASA_NPR[trl], "mankins_1995": MANKINS_1995.get(trl, NASA_NPR[trl]),
                           "software_description": NASA_SOFTWARE[trl], "success_criteria": NASA_SUCCESS[trl]}
        if scale in ("eu", "all"):
            row["eu"] = EU_H2020[trl]
        if scale in ("dod", "all"):
            row["dod"] = {"definition": DOD_2011[trl], "supporting_information": DOD_SUPPORT[trl]}
        data[str(trl)] = row
    return {"scale": scale, "levels": data, "wording_notes": SCALE_NOTES if scale == "all" else []}


def render_criteria():
    out = ["SKILL.md evidence checklist (keys accepted in evidence.json):"]
    for lv in LEVELS:
        if lv["rule"] == "all":
            rule = "all of: "
        elif len(lv["criteria"]) > 1:
            rule = "any one of: "
        else:
            rule = ""
        out.append(f"TRL {lv['trl']}  {lv['short']:<22} {lv['adaptation']}")
        for i, (key, desc, _) in enumerate(lv["criteria"]):
            out.append(f"       {rule if i == 0 else '':<13}{key}: {desc}")
    out.append("evidence_type: " + " | ".join(EVIDENCE_TYPES[:-1])
               + "   (vendor-claim/press not counted without --accept-vendor-claims)")
    return "\n".join(out)


def template():
    types = "<" + "|".join(EVIDENCE_TYPES[:-1]) + ">"
    ev = {str(lv["trl"]): [{"criterion": key, "item": f"<{desc}>", "evidence_type": types,
                            "source": "<url or DOI>"} for key, desc, _ in lv["criteria"]]
          for lv in LEVELS}
    return {"technology": "<specific technology, with scope boundary>", "claimed_trl": 6,
            "claimed_by": "<vendor|analyst|internal>", "evidence": ev}


# --- selftest ----------------------------------------------------------------


def _case(claimed, evidence, **kw):
    d = {"technology": "selftest", "claimed_trl": claimed, "evidence": evidence}
    d.update(kw)
    return parse_case(d)


def run_selftest():
    checks = []

    def check(name, ok):
        checks.append(bool(ok))
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    # 1. Contiguous evidence 1-5, claimed 5 -> evidenced 5, delta 0, supported, exit 0.
    r = assess(_case(5, {"1": ["arXiv preprint"], "2": ["design spec"], "3": ["github repo with example"],
                         "4": ["benchmark on a controlled dataset"],
                         "5": [{"item": "independent replication", "evidence_type": "peer-reviewed"}]}))
    check("contiguous 1-5, claimed 5 -> evidenced 5", r["evidenced_trl"] == 5)
    check("contiguous 1-5, claimed 5 -> delta 0, verdict supported, exit 0",
          r["delta"] == 0 and r["verdict"] == "supported" and r["exit_code"] == 0)
    check("next level after 5 is 6 with three 'any' options",
          r["next_level"]["trl"] == 6 and len(r["next_level"]["missing"]) == 3)

    # 2. Evidence at 1-3 and 5-6, nothing at 4 -> evidenced 3, gap at 4 reported.
    r = assess(_case(6, {"1": ["paper"], "2": ["spec"], "3": ["repo"],
                         "5": [{"item": "third-party eval", "evidence_type": "test-report"}],
                         "6": [{"criterion": "case-study", "item": "Acme pilot case study", "evidence_type": "deployment"}]}))
    check("gap at 4 -> evidenced 3 (no skipping)", r["evidenced_trl"] == 3)
    check("gap at 4 reported, evidence above gap = [5, 6]", r["gaps"] == [4] and r["evidence_above_gap"] == [5, 6])
    check("gap case: claimed 6 vs evidenced 3 -> over-claim, exit 1", r["verdict"] == "over-claim" and r["exit_code"] == 1)
    check("gap case: next level is 4 (benchmark missing)",
          r["next_level"]["trl"] == 4 and r["next_level"]["missing"][0]["key"] == "benchmark")

    # 3. Vendor-claim-only evidence at 6 -> not counted unless --accept-vendor-claims.
    base = {"1": ["paper"], "2": ["spec"], "3": ["repo"], "4": ["benchmark"],
            "5": [{"item": "independent eval", "evidence_type": "test-report"}],
            "6": [{"criterion": "case-study", "item": "vendor case study", "evidence_type": "vendor-claim"},
                  {"criterion": "named-customer-reference", "item": "press release naming Acme", "evidence_type": "press"}]}
    r = assess(_case(6, base))
    check("vendor-claim/press only at 6 -> not counted, evidenced 5", r["evidenced_trl"] == 5)
    check("vendor-only level 6 flagged 'unverified' with caution",
          r["levels"][5]["status"] == "unverified" and r["levels"][5]["vendor_only"]
          and any(c.startswith("TRL 6: evidence is vendor-sourced only") for c in r["cautions"]))
    check("claimed 6 vs evidenced 5 -> one-level-gap, exit 0", r["verdict"] == "one-level-gap" and r["exit_code"] == 0)
    r2 = assess(_case(6, base), accept_vendor=True)
    check("--accept-vendor-claims -> level 6 counted, evidenced 6, still cautioned",
          r2["evidenced_trl"] == 6 and r2["verdict"] == "supported"
          and any("counted because --accept-vendor-claims" in c for c in r2["cautions"]))

    # 4. Claimed 8 vs evidenced 5 -> over-claim verdict, exit 2.
    r = assess(_case(8, {"1": ["paper"], "2": ["spec"], "3": ["repo"], "4": ["benchmark"],
                         "5": [{"item": "third-party eval", "evidence_type": "test-report"}]}, claimed_by="vendor"))
    check("claimed 8 vs evidenced 5 -> delta 3, over-claim, exit 2",
          r["delta"] == 3 and r["verdict"] == "over-claim" and r["exit_code"] == 1)
    check("vendor self-report caution raised", any("Self-reported (vendor)" in c for c in r["cautions"]))

    # 5. Level 7 needs ALL three criteria: two of three -> partial, evidenced 6.
    r = assess(_case(7, {"1": True, "2": True, "3": True, "4": True, "5": True, "6": True,
                         "7": {"production-case-study": "Acme case study", "incident-reports": True,
                               "named-reference-customer": False}}))
    check("level 7 with 2/3 criteria -> partial, evidenced 6",
          r["evidenced_trl"] == 6 and r["levels"][6]["status"] == "partial")
    check("missing item for 7 is named-reference-customer",
          [m["key"] for m in r["next_level"]["missing"]] == ["named-reference-customer"])
    check("bare `true` levels flagged as asserted without artefact",
          any(c.startswith("TRL 1: asserted true") for c in r["cautions"]))

    # 6. Keyword matching of untagged free text at an all-criteria level.
    r = assess(_case(None, {"8": ["public customer list on the website", "enterprise SLA in the contract",
                                  "status page with uptime metrics"]}))
    l8 = r["levels"][7]
    check("free-text items keyword-matched to customer-list / support-sla / operational-metrics",
          all(c["satisfied"] for c in l8["criteria"]) and l8["met"])
    check("no claim -> verdict no-claim; evidenced 0 because TRL 1-7 are unevidenced",
          r["verdict"] == "no-claim" and r["evidenced_trl"] == 0 and r["gaps"] == [1, 2, 3, 4, 5, 6, 7])
    r = assess(_case(None, {"7": ["something vague"]}))
    check("unmatched free text at level 7 satisfies no criterion and is cautioned",
          r["levels"][6]["status"] == "partial" and any("matched no criterion" in c for c in r["cautions"]))

    # 7. Demo reproduces the SKILL.md worked example: verdict TRL 7, vendor claim 8, delta 1.
    r = assess(parse_case(DEMO))
    check("demo: evidenced TRL 7, claimed 8, delta 1, exit 0",
          r["evidenced_trl"] == 7 and r["claimed_trl"] == 8 and r["delta"] == 1 and r["exit_code"] == 0)
    check("demo: levels 1-7 met, 8 partial, 9 not met",
          [lv["status"] for lv in r["levels"]] == ["met"] * 7 + ["partial", "not met"])
    check("demo: to reach 8 -> operational-metrics missing + independent confirmation of customer-list",
          [m["key"] for m in r["next_level"]["missing"]] == ["customer-list", "operational-metrics"]
          and r["next_level"]["needs_independent_confirmation"] == ["customer-list"])

    # 8. Invalid input is rejected.
    for bad, why in [({"claimed_trl": 10, "evidence": {}}, "claimed_trl 10"),
                     ({"evidence": {"10": ["x"]}}, "level key 10"),
                     ({"evidence": {"7": {"nope": True}}}, "unknown criterion"),
                     ({"evidence": {"3": [{"item": "x", "evidence_type": "rumour"}]}}, "bad evidence_type"),
                     ({"evidence": {"3": [{"criterion": "paper", "item": "x"}]}}, "criterion of another level"),
                     ([], "non-object top level")]:
        try:
            parse_case(bad)
            check(f"invalid input rejected ({why})", False)
        except InputError:
            check(f"invalid input rejected ({why})", True)

    # 9. Determinism: identical input -> identical text and JSON.
    a = render_text(assess(parse_case(DEMO)), "ai")
    b = render_text(assess(parse_case(DEMO)), "ai")
    check("render is deterministic (byte-identical on repeat)", a == b)
    check("JSON render is deterministic",
          json.dumps(assess(parse_case(DEMO)), sort_keys=True) == json.dumps(assess(parse_case(DEMO)), sort_keys=True))
    check("levels tables cover TRL 1-9 for nasa/eu/dod",
          all(set(d) == set(range(1, 10))
              for d in (NASA_NPR, NASA_SOFTWARE, NASA_SUCCESS, EU_H2020, DOD_2011, DOD_SUPPORT))
          and set(MANKINS_1995) <= set(range(1, 10)))

    print(f"ALL {len(checks)} CHECKS PASSED")
    print("selftest OK")
    return 0


# --- CLI ---------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(description="TRL evidence-gate assessment: cumulative NASA TRL 1-9 with the SKILL.md "
                                "software/AI evidence checklist; vendor claims are not counted by default.")
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true", help="assess the SKILL.md worked example (same as `assess --demo`)")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("levels", help="print TRL 1-9 definitions from NASA / EU / DoD sources")
    p.add_argument("--scale", choices=["nasa", "eu", "dod", "all"], default="nasa")
    p.add_argument("--json", action="store_true", help="emit JSON")
    sub.add_parser("criteria", help="print the SKILL.md evidence checklist keys used by `assess`")
    sub.add_parser("template", help="print an evidence.json skeleton to fill in")
    p = sub.add_parser("assess", help="score evidence.json: evidenced vs claimed TRL, gaps, next-level needs")
    p.add_argument("--file", help="JSON evidence file (- for stdin); see module docstring for the format")
    p.add_argument("--demo", action="store_true", help="use the SKILL.md worked example")
    p.add_argument("--domain", choices=["software", "ai", "hardware"], help="append domain adaptation notes")
    p.add_argument("--accept-vendor-claims", action="store_true",
                   help="count vendor-claim/press evidence (still flagged)")
    p.add_argument("--json", action="store_true", help="emit JSON")
    return parser


def cmd_assess(args, parser):
    if args.demo:
        case = parse_case(DEMO)
    elif args.file:
        try:
            case = load_file(args.file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:  # InputError is a ValueError
            print(f"error: could not load {args.file}: {exc}", file=sys.stderr)
            return 2
    else:
        parser.error("assess needs --file PATH (or --demo)")
    result = assess(case, accept_vendor=args.accept_vendor_claims)
    if args.json:
        result["domain"] = args.domain
        result["domain_notes"] = DOMAIN_NOTES[args.domain] if args.domain else []
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text(result, args.domain))
    return result["exit_code"]


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.command == "levels":
        if args.json:
            print(json.dumps(levels_json(args.scale), indent=2, sort_keys=True))
        else:
            print(render_levels(args.scale))
        return 0
    if args.command == "criteria":
        print(render_criteria())
        return 0
    if args.command == "template":
        print(json.dumps(template(), indent=2))
        return 0
    if args.command == "assess":
        return cmd_assess(args, parser)
    if args.demo:
        result = assess(parse_case(DEMO))
        print(render_text(result))
        return result["exit_code"]
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
