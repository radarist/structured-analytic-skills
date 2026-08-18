#!/usr/bin/env python3
"""osshealth.py — CHAOSS-style vitality scorecard for one open-source repository.

Turns a metrics snapshot (JSON) into the indicator reads of ../SKILL.md
steps 2-7 and prints the step-8 report template. Every indicator is rated
green / amber / red with its threshold printed alongside; thresholds the
SKILL.md leaves vague are documented defaults (see the DEFAULTS block) and
are named as such in the output.

Definitions implemented (metric names verified against the CHAOSS knowledge
base, https://chaoss.community/kb-metrics-and-metrics-models/):

  * Bus factor      = CHAOSS "Contributor Absence Factor" (formerly "Bus
                      Factor"; also called pony/truck factor): the smallest
                      number of authors whose commits, taken in descending
                      order, reach >= 50 % of all commits in the window.
                      Bot accounts ("*[bot]") are excluded and listed.
  * Elephant factor = CHAOSS "Elephant Factor": the same computation over
                      organisations (commits_by_org), 50 % share.
  * Concentration   = share of commits by the top author (the read the
                      SKILL.md worked example uses: "top maintainer authored
                      71 % of commits").
  * Activity        = days since last commit, commits per month (CHAOSS
                      "Activity Dates and Times", "Code Changes Commits";
                      the 90-day band follows the OpenSSF Scorecard
                      "Maintained" check).
  * Release cadence = days since last release, releases in the window
                      (CHAOSS "Release Frequency").
  * Responsiveness  = median time to first response on issues (CHAOSS "Time
                      to First Response", "Issue Response Time") and median
                      PR merge time (CHAOSS "Change Requests Duration").
  * Backlog ratio   = open issues / issues closed in the window (CHAOSS
                      "Issues New", "Issues Closed"; a closure ratio in the
                      style of "Change Request Closure Ratio").
  * Community growth= new contributors in the window (CHAOSS "New
                      Contributors", "Contributors").
  * Hygiene         = OSI-approved licence (CHAOSS "OSI Approved Licenses",
                      "Licenses Declared"), security policy, CI, code of
                      conduct (CHAOSS "Code of Conduct for a Project";
                      OpenSSF Scorecard "License", "Security-Policy",
                      "CI-Tests" checks).
  * Adoption        = stars, forks, downloads, dependents — context, never
                      health (CHAOSS "Project Popularity", "Technical Fork",
                      "Number of Downloads"; SKILL.md anti-pattern 1).
  * Advisories      = open, unpatched security advisories (SKILL.md step 6);
                      "unpatched beyond a normal fix window" = 90 days.
  * Verdict         = SKILL.md step-7 labels healthy / at-risk / abandoned,
                      operationalised as: abandoned = commits stalled > 365 d
                      AND no release for > 365 d (or none in the window) AND
                      issue first response > 14 d, all three known; at-risk =
                      any red indicator or >= 3 amber; healthy = no red and
                      <= 2 amber. The rule is printed with every verdict.

Stdlib only. Python 3.9+. Deterministic: sorted iteration, no wall clock in
`assess` output. Offline by default — only the `fetch` subcommand touches the
network (GitHub REST, explicit `--github owner/repo`), and `--selftest`
never calls it.

Usage:
    python3 osshealth.py assess --file metrics.json [--json]
    python3 osshealth.py assess --demo                # SKILL.md worked example
    python3 osshealth.py fetch --github owner/repo [--token TOKEN] [--out metrics.json]
    python3 osshealth.py --selftest
Exit codes: 0 healthy / success; 1 invalid input or usage; 2 verdict at-risk or abandoned.
"""

import argparse
import contextlib
import io
import json
import os
import re
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# --- documented defaults -----------------------------------------------------
# Bands are (green_max, amber_max): value <= green_max -> green,
# <= amber_max -> amber, otherwise red ("lower is better").

SHARE = 0.50                          # CHAOSS cumulative-share threshold (bus/elephant)
WINDOW_MONTHS_DEFAULT = 12
BAND_COMMIT_DAYS = (90, 180)          # SKILL.md/task: 90-180 d amber, > 180 d red
BAND_RELEASE_DAYS = (180, 365)        # default: CHAOSS Release Frequency
BAND_FIRST_RESPONSE_HOURS = (48, 336)  # 2 d green, <= 14 d amber, > 14 d red
BAND_PR_MERGE_DAYS = (7, 30)          # default: CHAOSS Change Requests Duration
BAND_BACKLOG_RATIO = (1.0, 3.0)       # default; green is strict (< 1.0)
ADVISORY_FIX_WINDOW_DAYS = 90         # default "normal fix window" (SKILL.md step 6)
LONG_WINDOW_DAYS = 365                # default "sustained over a long window" (abandoned)
HEALTHY_MAX_AMBER = 2                 # healthy tolerates <= 2 amber, 0 red
AT_RISK_MIN_AMBER = 3                 # >= 3 amber -> at-risk even with 0 red

VERDICT_RULE = (
    "abandoned = no commits for > {lw} d AND no release for > {lw} d (or none in the "
    "window) AND median issue first response > 14 d, all three known; "
    "at-risk = any red indicator, or >= {ar} amber; healthy = no red and <= {hm} amber. "
    "Adoption and governance/funding rows are context and never counted."
).format(lw=LONG_WINDOW_DAYS, ar=AT_RISK_MIN_AMBER, hm=HEALTHY_MAX_AMBER)

# Order in which a red (then amber) indicator is named as "biggest risk".
# Bus factor first: the SKILL.md worked example calls it decisive on its own.
RISK_PRIORITY = ["bus_factor", "advisories", "activity", "release", "first_response",
                 "pr_merge", "backlog", "hygiene", "elephant", "new_contributors"]

# Fields whose absence lowers the stated confidence (SKILL.md step 1 & template).
CORE_FIELDS = [
    ("bus factor", ("commits_by_author",)),
    ("last commit", ("days_since_last_commit",)),
    ("releases", ("days_since_last_release", "releases_12mo")),
    ("issue response", ("issue_first_response_median_hours",)),
    ("advisories", ("open_advisories",)),
]

BOT_NAMES = {"dependabot", "dependabot-preview", "renovate", "renovate-bot",
             "github-actions", "greenkeeper", "pre-commit-ci"}

# --- licences ----------------------------------------------------------------
# Common OSI-approved licences by (normalised) SPDX identifier. Not exhaustive:
# an identifier missing here is reported "not recognised", never "not approved".
OSI_APPROVED = {
    "0BSD", "AFL-3.0", "AGPL-3.0", "APACHE-1.1", "APACHE-2.0", "ARTISTIC-2.0",
    "BLUEOAK-1.0.0", "BSD-1-CLAUSE", "BSD-2-CLAUSE", "BSD-2-CLAUSE-PATENT", "BSD-3-CLAUSE",
    "BSL-1.0", "CAL-1.0", "CDDL-1.0", "CECILL-2.1", "CPL-1.0", "ECL-2.0", "EPL-1.0",
    "EPL-2.0", "EUPL-1.1", "EUPL-1.2", "GPL-2.0", "GPL-3.0", "ICU", "ISC", "LGPL-2.1",
    "LGPL-3.0", "LPPL-1.3C", "MIT", "MIT-0", "MPL-1.1", "MPL-2.0", "MS-PL", "MS-RL",
    "MULANPSL-2.0", "NCSA", "OFL-1.1", "OSL-3.0", "POSTGRESQL", "PYTHON-2.0",
    "UNLICENSE", "UPL-1.0", "W3C", "ZLIB", "ZOPE-2.0",
}
# Common licences that are NOT OSI-approved (source-available, CC, public-domain
# dedications the OSI declined). CC0-1.0 was submitted and withdrawn.
NOT_OSI = {
    "BUSL-1.1", "CC-BY-4.0", "CC-BY-NC-4.0", "CC-BY-SA-4.0", "CC0-1.0", "COMMONS-CLAUSE",
    "ELASTIC-2.0", "JSON", "PROPRIETARY", "SSPL-1.0", "WTFPL", "BEERWARE",
    "FSL-1.1-MIT", "FSL-1.1-APACHE-2.0", "PROSPERITY-3.0.0", "PARITY-7.0.0",
}
LICENSE_ALIASES = {
    "APACHE": "APACHE-2.0", "APACHE-2": "APACHE-2.0", "APACHE2": "APACHE-2.0",
    "APACHE-2.0.0": "APACHE-2.0", "GPL2": "GPL-2.0", "GPLV2": "GPL-2.0", "GPL-2": "GPL-2.0",
    "GPL3": "GPL-3.0", "GPLV3": "GPL-3.0", "GPL-3": "GPL-3.0", "LGPL2.1": "LGPL-2.1",
    "LGPLV2.1": "LGPL-2.1", "LGPL3": "LGPL-3.0", "LGPLV3": "LGPL-3.0", "LGPL-3": "LGPL-3.0",
    "AGPL3": "AGPL-3.0", "AGPLV3": "AGPL-3.0", "AGPL-3": "AGPL-3.0", "MPL2": "MPL-2.0",
    "MPL-2": "MPL-2.0", "BSD-2": "BSD-2-CLAUSE", "BSD-3": "BSD-3-CLAUSE",
    "BSD-3-CLAUSE-NEW": "BSD-3-CLAUSE", "NEW-BSD": "BSD-3-CLAUSE", "SIMPLIFIED-BSD": "BSD-2-CLAUSE",
    "BOOST-1.0": "BSL-1.0", "PSF-2.0": "PYTHON-2.0", "PUBLIC-DOMAIN": "UNLICENSE",
}
UNRECOGNISED_TOKENS = {"NOASSERTION", "OTHER", "UNKNOWN", "CUSTOM", "SEE-LICENSE", "SEE-LICENSE-IN-LICENSE"}


def normalise_license(value):
    """Map a licence string to an upper-case SPDX-like identifier."""
    s = str(value).strip().upper()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[_ ]", "-", s)
    s = re.sub(r"^THE-", "", s)
    s = re.sub(r"-?LICEN[SC]E$", "", s)
    s = re.sub(r"-(ONLY|OR-LATER)$", "", s)
    s = re.sub(r"\+$", "", s)  # "GPL-3.0+"
    return LICENSE_ALIASES.get(s, s)


def license_status(value):
    """Return (status, canonical) with status in {"not-found", "missing", "osi",
    "non-osi", "unrecognised"} (CHAOSS "OSI Approved Licenses"). A null/absent
    value is data not found; an explicit "" / "none" means no licence declared."""
    if value is None:
        return "not-found", None
    if str(value).strip() == "" or str(value).strip().lower() in ("none", "null", "no license", "no licence"):
        return "missing", None
    canon = normalise_license(value)
    if canon in OSI_APPROVED:
        return "osi", canon
    if canon in NOT_OSI:
        return "non-osi", canon
    return "unrecognised", canon


# --- input -------------------------------------------------------------------

NUMERIC_FIELDS = {
    # name: (allow_negative, must_be_int)
    "contributors_12mo": (False, True), "contributors_all_time": (False, True),
    "new_contributors_12mo": (False, True), "days_since_last_commit": (False, False),
    "releases_12mo": (False, True), "days_since_last_release": (False, False),
    "issue_first_response_median_hours": (False, False), "pr_merge_median_days": (False, False),
    "open_issues": (False, True), "closed_issues_12mo": (False, True),
    "stars": (False, True), "forks": (False, True), "dependents": (False, True),
    "downloads_12mo": (False, True), "stars_growth_12mo_pct": (True, False),
    "downloads_growth_yoy_pct": (True, False), "open_advisories": (False, True),
    "advisory_max_age_days": (False, False), "window_months": (False, False),
}
BOOL_FIELDS = ("has_security_policy", "has_ci", "has_code_of_conduct", "has_governance_doc",
               "funding", "archived")
STRING_FIELDS = ("repo", "license", "stars_trend", "last_commit_date", "last_release_date",
                 "snapshot_date", "advisories_note")
LIST_FIELDS = ("sources", "notes")
MAPPING_FIELDS = ("commits_by_author", "commits_by_org")
KNOWN_FIELDS = set(NUMERIC_FIELDS) | set(BOOL_FIELDS) | set(STRING_FIELDS) | set(LIST_FIELDS) | set(MAPPING_FIELDS)

# SKILL.md worked example (acme-utils/htmltidy, values illustrative). The
# commit split gives the top maintainer exactly 71 % of 200 commits.
DEMO = {
    "repo": "acme-utils/htmltidy",
    "window_months": 12,
    "commits_by_author": {
        "m.reyes": 142, "a.okafor": 21, "j.lindqvist": 12, "p.nair": 8, "s.dubois": 6,
        "k.tanaka": 4, "l.moreau": 3, "d.chen": 2, "r.silva": 1, "t.novak": 1,
    },
    "commits_by_org": {"Acme Utils": 163, "Lindqvist Consulting": 12, "unaffiliated": 25},
    "contributors_all_time": 340,
    "new_contributors_12mo": 3,
    "days_since_last_commit": 243,
    "releases_12mo": 0,
    "days_since_last_release": 426,
    "issue_first_response_median_hours": 1104,
    "pr_merge_median_days": 41,
    "open_issues": 212,
    "closed_issues_12mo": 96,
    "stars": 28400,
    "stars_growth_12mo_pct": 1,
    "downloads_growth_yoy_pct": -30,
    "license": "MIT",
    "has_security_policy": False,
    "has_ci": True,
    "has_code_of_conduct": True,
    "has_governance_doc": False,
    "funding": False,
    "open_advisories": 2,
    "advisory_max_age_days": 190,
    "advisories_note": "1 moderate severity",
    "sources": ["Ecosyste.ms (CC-BY-SA 4.0)"],
}


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_metrics(data):
    """Type-check a metrics snapshot. Returns (metrics, notes); raises ValueError."""
    if not isinstance(data, dict):
        raise ValueError("metrics file must contain a JSON object")
    notes = []
    for name, (allow_negative, must_be_int) in NUMERIC_FIELDS.items():
        v = data.get(name)
        if v is None:
            continue
        if not _is_number(v):
            raise ValueError(f"field {name!r} must be a number or null, got {v!r}")
        if not allow_negative and v < 0:
            raise ValueError(f"field {name!r} must be >= 0, got {v!r}")
        if must_be_int and float(v) != int(v):
            raise ValueError(f"field {name!r} must be an integer, got {v!r}")
    for name in BOOL_FIELDS:
        v = data.get(name)
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"field {name!r} must be true/false/null, got {v!r}")
    for name in STRING_FIELDS:
        v = data.get(name)
        if v is not None and not isinstance(v, str):
            raise ValueError(f"field {name!r} must be a string or null, got {v!r}")
    for name in LIST_FIELDS:
        v = data.get(name)
        if v is not None and not (isinstance(v, list) and all(isinstance(x, str) for x in v)):
            raise ValueError(f"field {name!r} must be a list of strings, got {v!r}")
    for name in MAPPING_FIELDS:
        v = data.get(name)
        if v is None:
            continue
        if not isinstance(v, dict) or not v:
            raise ValueError(f"field {name!r} must be a non-empty object of name -> commits")
        for k, n in v.items():
            if not _is_number(n) or n < 0:
                raise ValueError(f"field {name!r}: commits for {k!r} must be a number >= 0, got {n!r}")
    wm = data.get("window_months")
    if wm is not None and wm <= 0:
        raise ValueError("field 'window_months' must be > 0")
    unknown = sorted(k for k in data if k not in KNOWN_FIELDS)
    if unknown:
        notes.append("ignored unknown fields: " + ", ".join(unknown))
    return data, notes


def load_metrics(path):
    """Load the metrics JSON from a file path or '-' (stdin)."""
    if path == "-":
        return json.load(sys.stdin)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# --- the arithmetic (SKILL.md steps 2-6) --------------------------------------


def absence_factor(counts, share=SHARE):
    """CHAOSS Contributor Absence Factor / Elephant Factor.

    Smallest number of contributors (or organisations) whose contributions,
    taken in descending order, reach >= `share` of the total. Ties are broken
    by name so the result is deterministic. Returns (factor, ordered, total);
    factor is None when there are no contributions."""
    ordered = sorted(((str(k), v) for k, v in counts.items() if v > 0),
                     key=lambda kv: (-kv[1], kv[0]))
    total = sum(v for _, v in ordered)
    if total <= 0:
        return None, ordered, 0
    cum = 0
    for i, (_, v) in enumerate(ordered, start=1):
        cum += v
        if cum >= share * total - 1e-9:
            return i, ordered, total
    return len(ordered), ordered, total


def is_bot(name):
    n = str(name).strip().lower()
    return n.endswith("[bot]") or n in BOT_NAMES


def split_bots(counts):
    """Split an author -> commits mapping into (humans, bots)."""
    humans, bots = {}, {}
    for k, v in counts.items():
        (bots if is_bot(k) else humans)[k] = v
    return humans, bots


def band(value, green_max, amber_max, green_strict=False):
    """Lower-is-better rating: green / amber / red."""
    if (value < green_max) if green_strict else (value <= green_max):
        return "green"
    if value <= amber_max:
        return "amber"
    return "red"


def num(v, digits=1):
    """Compact number: integers without decimals, floats with `digits`."""
    if v is None:
        return "n/a"
    if float(v).is_integer():
        return f"{int(v):,}"
    return f"{v:,.{digits}f}"


def fmt_count(v):
    """28400 -> '28.4k', 2500000 -> '2.5M', 1234 -> '1,234'."""
    if v is None:
        return "n/a"
    v = float(v)
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if v >= 10_000:
        return f"{v / 1_000:.1f}k"
    return f"{int(v):,}"


def yesno(v):
    return "n/a" if v is None else ("yes" if v else "no")


def indicator(iid, label, rating, display, threshold, metric, value=None, risk=None, note=None):
    return {"id": iid, "label": label, "rating": rating, "value": value, "display": display,
            "threshold": threshold, "metric": metric, "risk": risk, "note": note}


def ind_bus_factor(m, window):
    thr = "1 red | 2 amber | >= 3 green (SKILL.md step 3; cumulative-share threshold 50 %)"
    metric = "CHAOSS Contributor Absence Factor (formerly Bus Factor)"
    cba = m.get("commits_by_author")
    if not cba:
        return indicator("bus_factor", "Bus factor", None, "data not found (commits_by_author missing)", thr, metric)
    humans, bots = split_bots(cba)
    bf, ordered, total = absence_factor(humans)
    if bf is None:
        return indicator("bus_factor", "Bus factor", None, "no human commits in window", thr, metric)
    top_name, top_n = ordered[0]
    share = top_n / total
    rating = "red" if bf == 1 else ("amber" if bf == 2 else "green")
    bots_txt = ""
    if bots:
        bots_txt = "; bots excluded: " + ", ".join(f"{k} ({num(v)})" for k, v in sorted(bots.items()))
    display = (f"{bf} — top author {top_name} {share:.1%} of {num(total)} commits over "
               f"{num(window)} months ({len(ordered)} authors{bots_txt})")
    if bf == 1:
        risk = (f"single-maintainer dependence — {top_name} authored {share:.0%} of commits in the "
                f"last {num(window)} months; the project is one resignation from unmaintained")
    elif bf == 2:
        risk = f"two-person maintainer core (top two authors hold >= 50 % of commits; top author {share:.0%})"
    else:
        risk = f"contributor base spread across {len(ordered)} authors (bus factor {bf})"
    value = {"bus_factor": bf, "top_author": top_name, "top_share": round(share, 4),
             "authors": len(ordered), "commits": total, "bots_excluded": dict(sorted(bots.items()))}
    return indicator("bus_factor", "Bus factor", rating, display, thr, metric, value, risk)


def ind_elephant(m):
    thr = "1 amber (single-organisation dependence) | >= 2 green (default; cumulative share 50 %)"
    metric = "CHAOSS Elephant Factor"
    cbo = m.get("commits_by_org")
    if not cbo:
        return indicator("elephant", "Elephant factor", None, "data not found (commits_by_org not provided)", thr, metric)
    ef, ordered, total = absence_factor(cbo)
    if ef is None:
        return indicator("elephant", "Elephant factor", None, "no commits attributed to organisations", thr, metric)
    top_name, top_n = ordered[0]
    share = top_n / total
    rating = "amber" if ef == 1 else "green"
    display = f"{ef} — top organisation {top_name} {share:.1%} of {num(total)} commits ({len(ordered)} organisations)"
    risk = (f"single-organisation dependence — {top_name} holds {share:.0%} of commits" if ef == 1
            else f"work spread across {len(ordered)} organisations (elephant factor {ef})")
    value = {"elephant_factor": ef, "top_org": top_name, "top_share": round(share, 4),
             "organisations": len(ordered), "commits": total}
    return indicator("elephant", "Elephant factor", rating, display, thr, metric, value, risk)


def ind_activity(m, window):
    g, a = BAND_COMMIT_DAYS
    thr = f"<= {g} d green | {g + 1}-{a} d amber | > {a} d red (SKILL.md step 4 / task default); archived repo -> red"
    metric = "CHAOSS Activity Dates and Times, Code Changes Commits; OpenSSF Scorecard 'Maintained' (90-d window)"
    d = m.get("days_since_last_commit")
    archived = m.get("archived")
    cba = m.get("commits_by_author") or {}
    humans, _ = split_bots(cba)
    total = sum(v for v in humans.values())
    cpm = total / window if cba else None
    cpm_txt = f"; {num(cpm)} commits/month over {num(window)} months" if cpm is not None else ""
    date_txt = f" ({m['last_commit_date']})" if m.get("last_commit_date") else ""
    if d is None and not archived:
        return indicator("activity", "Last commit", None, "data not found (days_since_last_commit missing)" + cpm_txt, thr, metric)
    if archived:
        display = "repository archived" + (f"; last commit {num(d)} d ago{date_txt}" if d is not None else "") + cpm_txt
        return indicator("activity", "Last commit", "red", display, thr, metric,
                         {"days_since_last_commit": d, "commits_per_month": cpm, "archived": True},
                         "repository is archived — explicitly unmaintained")
    rating = band(d, g, a)
    display = f"{num(d)} d ago{date_txt}" + cpm_txt
    risk = (f"no commits for {num(d)} days — cadence stalled" if rating == "red"
            else f"commit cadence slowing ({num(d)} d since last commit)" if rating == "amber"
            else f"active cadence ({num(d)} d since last commit)")
    return indicator("activity", "Last commit", rating, display, thr, metric,
                     {"days_since_last_commit": d, "commits_per_month": cpm, "archived": False}, risk)


def ind_release(m, window):
    g, a = BAND_RELEASE_DAYS
    thr = f"<= {g} d green | {g + 1}-{a} d amber | > {a} d red (default); count only: 0 in window amber, >= 1 green"
    metric = "CHAOSS Release Frequency"
    d = m.get("days_since_last_release")
    n = m.get("releases_12mo")
    date_txt = f" ({m['last_release_date']})" if m.get("last_release_date") else ""
    n_txt = f"{num(n)} releases in {num(window)} months" if n is not None else "release count data not found"
    if d is None and n is None:
        return indicator("release", "Last release", None, "data not found", thr, metric)
    if d is None:
        rating = "amber" if n == 0 else "green"
        display = f"date data not found; {n_txt}"
        risk = ("no releases in the window (tag-only or unreleased — check)" if n == 0
                else f"{num(n)} releases in the window")
        return indicator("release", "Last release", rating, display, thr, metric,
                         {"days_since_last_release": None, "releases_in_window": n}, risk)
    rating = band(d, g, a)
    display = f"{num(d)} d ago{date_txt}; {n_txt}"
    risk = (f"no release for {num(d)} days" if rating == "red"
            else f"release rhythm slowing ({num(d)} d since last release)" if rating == "amber"
            else f"recent release ({num(d)} d ago)")
    return indicator("release", "Last release", rating, display, thr, metric,
                     {"days_since_last_release": d, "releases_in_window": n}, risk)


def ind_first_response(m):
    g, a = BAND_FIRST_RESPONSE_HOURS
    thr = f"median <= {g // 24} d green | <= {a // 24} d amber | > {a // 24} d red (task default)"
    metric = "CHAOSS Time to First Response, Issue Response Time"
    h = m.get("issue_first_response_median_hours")
    if h is None:
        return indicator("first_response", "Issue first response", None, "data not found", thr, metric)
    rating = band(h, g, a)
    display = f"median {num(h / 24)} d ({num(h)} h)"
    risk = (f"median first response {num(h / 24)} days — maintainers are not responding" if rating == "red"
            else f"slow first response (median {num(h / 24)} d)" if rating == "amber"
            else f"responsive (median first response {num(h)} h)")
    return indicator("first_response", "Issue first response", rating, display, thr, metric,
                     {"median_hours": h}, risk)


def ind_pr_merge(m):
    g, a = BAND_PR_MERGE_DAYS
    thr = f"median <= {g} d green | <= {a} d amber | > {a} d red (default)"
    metric = "CHAOSS Change Requests Duration (cf. Change Request Closure Ratio)"
    d = m.get("pr_merge_median_days")
    if d is None:
        return indicator("pr_merge", "PR merge time", None, "data not found", thr, metric)
    rating = band(d, g, a)
    display = f"median {num(d)} d"
    risk = (f"median PR merge time {num(d)} days — change requests are not being absorbed" if rating == "red"
            else f"slow PR merges (median {num(d)} d)" if rating == "amber"
            else f"PRs merged promptly (median {num(d)} d)")
    return indicator("pr_merge", "PR merge time", rating, display, thr, metric, {"median_days": d}, risk)


def ind_backlog(m, window):
    g, a = BAND_BACKLOG_RATIO
    thr = f"open/closed-in-window < {num(g)} green | {num(g)}-{num(a)} amber | > {num(a)} red (default)"
    metric = "CHAOSS Issues New, Issues Closed (closure-ratio style)"
    o, c = m.get("open_issues"), m.get("closed_issues_12mo")
    if o is None or c is None:
        return indicator("backlog", "Issue backlog", None, "data not found", thr, metric)
    if c == 0:
        if o == 0:
            return indicator("backlog", "Issue backlog", None, "no issue traffic (0 open, 0 closed)", thr, metric)
        return indicator("backlog", "Issue backlog", "red",
                         f"{num(o)} open, none closed in {num(window)} months (ratio undefined)", thr, metric,
                         {"open": o, "closed_in_window": c, "ratio": None},
                         f"{num(o)} open issues and none closed in {num(window)} months")
    ratio = o / c
    rating = band(ratio, g, a, green_strict=True)
    display = f"{ratio:.2f} ({num(o)} open / {num(c)} closed in {num(window)} months)"
    risk = (f"issue backlog {ratio:.1f}x annual closures" if rating == "red"
            else f"issue backlog building ({ratio:.1f}x annual closures)" if rating == "amber"
            else f"backlog under control ({ratio:.2f}x annual closures)")
    return indicator("backlog", "Issue backlog", rating, display, thr, metric,
                     {"open": o, "closed_in_window": c, "ratio": round(ratio, 4)}, risk)


def ind_new_contributors(m, window):
    thr = ">= 1 green | 0 amber (default: a stable, feature-complete library may legitimately attract none)"
    metric = "CHAOSS New Contributors, Contributors"
    n = m.get("new_contributors_12mo")
    active = m.get("contributors_12mo")
    derived = ""
    if active is None and m.get("commits_by_author"):
        humans, _ = split_bots(m["commits_by_author"])
        active = len([k for k, v in humans.items() if v > 0])
        derived = " (derived from commits_by_author)"
    active_txt = f"; {num(active)} active authors{derived}" if active is not None else ""
    all_time = f"; {num(m['contributors_all_time'])} all-time" if m.get("contributors_all_time") is not None else ""
    if n is None:
        return indicator("new_contributors", "New contributors", None, "data not found" + active_txt + all_time, thr, metric)
    rating = "amber" if n == 0 else "green"
    display = f"{num(n)} new in {num(window)} months" + active_txt + all_time
    risk = (f"no new contributors in the last {num(window)} months" if rating == "amber"
            else f"{num(n)} new contributors in the window")
    return indicator("new_contributors", "New contributors", rating, display, thr, metric,
                     {"new_in_window": n, "active_in_window": active}, risk)


def ind_advisories(m):
    fw = ADVISORY_FIX_WINDOW_DAYS
    thr = f"0 green | open, within the {fw}-d fix window amber | open > {fw} d red (SKILL.md step 6; fix window default)"
    metric = "SKILL.md step 6 (open, unpatched advisories); OpenSSF Scorecard 'Vulnerabilities'"
    n = m.get("open_advisories")
    if n is None:
        return indicator("advisories", "Advisories", None, "data not found", thr, metric)
    if n == 0:
        return indicator("advisories", "Advisories", "green", "none found", thr, metric,
                         {"open": 0}, "no open advisories")
    age = m.get("advisory_max_age_days")
    note = f" — {m['advisories_note']}" if m.get("advisories_note") else ""
    rating = "red" if (age is not None and age > fw) else "amber"
    age_txt = f"oldest {num(age)} d" if age is not None else "age unknown"
    display = f"{num(n)} open ({age_txt}){note}"
    risk = (f"{num(n)} open security advisor{'y' if n == 1 else 'ies'} unaddressed beyond the {fw}-day fix window"
            if rating == "red" else f"{num(n)} open advisor{'y' if n == 1 else 'ies'} inside the {fw}-day fix window")
    return indicator("advisories", "Advisories", rating, display, thr, metric,
                     {"open": n, "max_age_days": age}, risk)


def ind_hygiene(m):
    thr = ("no licence red | licence not OSI-recognised, or >= 2 of {SECURITY.md, CI, CoC} missing amber | "
           "else green (default)")
    metric = ("CHAOSS OSI Approved Licenses, Licenses Declared, Code of Conduct for a Project; "
              "OpenSSF Scorecard 'License', 'Security-Policy', 'CI-Tests'")
    status, canon = license_status(m.get("license"))
    lic_txt = {"not-found": "licence: data not found",
               "missing": "licence: none declared",
               "osi": f"licence {canon} (OSI-approved)",
               "non-osi": f"licence {canon} (NOT OSI-approved)",
               "unrecognised": f"licence {m.get('license')!r} not recognised — check manually"}[status]
    sec, ci, coc = m.get("has_security_policy"), m.get("has_ci"), m.get("has_code_of_conduct")
    missing = [name for name, v in (("SECURITY.md", sec), ("CI", ci), ("CoC", coc)) if v is False]
    unknown = [name for name, v in (("SECURITY.md", sec), ("CI", ci), ("CoC", coc)) if v is None]
    if status == "not-found" and len(unknown) == 3:
        return indicator("hygiene", "Hygiene", None, "data not found (license, has_security_policy, has_ci, "
                         "has_code_of_conduct all missing)", thr, metric)
    if status == "missing":
        rating = "red"
    elif status in ("non-osi", "unrecognised") or len(missing) >= 2:
        rating = "amber"
    else:
        rating = "green"
    display = f"{lic_txt}; SECURITY.md {yesno(sec)}; CI {yesno(ci)}; CoC {yesno(coc)}"
    if unknown:
        display += f" (data not found: {', '.join(unknown)})"
    if status == "not-found":
        unknown = ["licence"] + unknown
    if rating == "red":
        risk = "no licence declared — not safely reusable"
    elif status == "non-osi":
        risk = f"licence {canon} is not OSI-approved — check reuse terms"
    elif status == "unrecognised":
        risk = "licence not recognised — verify terms manually"
    elif len(missing) >= 2:
        risk = "hygiene gaps: missing " + ", ".join(missing)
    else:
        risk = "hygiene in order" + (f" (missing {', '.join(missing)})" if missing else "")
    return indicator("hygiene", "Hygiene", rating, display, thr, metric,
                     {"license": canon, "license_status": status, "missing": missing, "unknown": unknown}, risk)


def adoption_text(m):
    """'{stars, trajectory}' and 'downloads/dependents' phrases for the template."""
    stars = m.get("stars")
    pct = m.get("stars_growth_12mo_pct")
    if stars is None:
        stars_txt = "stars data not found"
    else:
        stars_txt = f"{fmt_count(stars)} stars"
        if pct is not None:
            if pct <= -5:
                stars_txt += f", declining {num(abs(pct))} % over 12 months"
            elif pct < 5:
                stars_txt += f", flat over 12 months ({pct:+g} %)"
            elif pct < 25:
                stars_txt += f", growing {num(pct)} % over 12 months"
            else:
                stars_txt += f", growing fast (+{num(pct)} % over 12 months)"
        elif m.get("stars_trend"):
            stars_txt += f", {m['stars_trend']}"
        else:
            stars_txt += ", trajectory data not found"
    parts = []
    dl, dl_pct = m.get("downloads_12mo"), m.get("downloads_growth_yoy_pct")
    if dl is not None:
        parts.append(f"{fmt_count(dl)} downloads/12 mo" + (f" ({dl_pct:+g} % YoY)" if dl_pct is not None else ""))
    elif dl_pct is not None:
        parts.append(f"downloads {'declining' if dl_pct < 0 else 'growing'} {num(abs(dl_pct))} % YoY")
    if m.get("dependents") is not None:
        parts.append(f"{fmt_count(m['dependents'])} dependents")
    dd_txt = "; ".join(parts) if parts else "data not found"
    return stars_txt, dd_txt


def ind_adoption(m):
    thr = "not rated — context only (SKILL.md anti-pattern: stars are past attention, not health)"
    metric = "CHAOSS Project Popularity, Technical Fork, Number of Downloads"
    stars_txt, dd_txt = adoption_text(m)
    forks_txt = f"; forks {fmt_count(m['forks'])}" if m.get("forks") is not None else ""
    return indicator("adoption", "Adoption (context)", None, f"{stars_txt}{forks_txt}; downloads/dependents: {dd_txt}",
                     thr, metric, {"stars": m.get("stars"), "forks": m.get("forks"),
                                   "dependents": m.get("dependents"), "downloads_12mo": m.get("downloads_12mo")})


def ind_governance(m):
    thr = "not rated — context only"
    metric = "CHAOSS Sponsorship (funding); governance document presence"
    return indicator("governance", "Governance & funding (context)", None,
                     f"governance doc {yesno(m.get('has_governance_doc'))}; funding {yesno(m.get('funding'))}",
                     thr, metric, {"has_governance_doc": m.get("has_governance_doc"), "funding": m.get("funding")})


# --- verdict (SKILL.md step 7) -----------------------------------------------


def stall_pattern(m):
    """Return (is_abandoned, unknown_parts) for the 'abandoned' rule."""
    d_commit = m.get("days_since_last_commit")
    d_rel, n_rel = m.get("days_since_last_release"), m.get("releases_12mo")
    h = m.get("issue_first_response_median_hours")
    commit_stall = None if d_commit is None else d_commit > LONG_WINDOW_DAYS
    if d_rel is not None:
        release_stall = d_rel > LONG_WINDOW_DAYS
    elif n_rel is not None:
        release_stall = n_rel == 0
    else:
        release_stall = None
    response_stall = None if h is None else h > BAND_FIRST_RESPONSE_HOURS[1]
    parts = {"last commit": commit_stall, "releases": release_stall, "issue response": response_stall}
    if all(v is True for v in parts.values()):
        return True, []
    unknown = [k for k, v in parts.items() if v is None]
    if all(v is not False for v in parts.values()) and unknown:
        return False, unknown  # every known part stalled; some unknown
    return False, []


def confidence(m):
    missing = [label for label, fields in CORE_FIELDS if all(m.get(f) is None for f in fields)]
    if not missing:
        return "high", "all core fields present (" + ", ".join(l for l, _ in CORE_FIELDS) + ")"
    level = "medium" if len(missing) <= 2 else "low"
    return level, "data not found: " + ", ".join(missing)


def assess(metrics):
    """Compute every indicator, the verdict and the report. Pure function of `metrics`."""
    m, notes = validate_metrics(metrics)
    window = m.get("window_months")
    if window is None:
        window = WINDOW_MONTHS_DEFAULT
        notes.append(f"window_months not given; {WINDOW_MONTHS_DEFAULT} assumed")
    notes = list(m.get("notes") or []) + notes
    inds = [
        ind_bus_factor(m, window), ind_elephant(m), ind_activity(m, window), ind_release(m, window),
        ind_first_response(m), ind_pr_merge(m), ind_backlog(m, window), ind_new_contributors(m, window),
        ind_advisories(m), ind_hygiene(m), ind_adoption(m), ind_governance(m),
    ]
    by_id = {i["id"]: i for i in inds}
    counts = {"red": 0, "amber": 0, "green": 0, "unrated": 0}
    for i in inds:
        counts[i["rating"] or "unrated"] += 1
    abandoned, unknown_stall = stall_pattern(m)
    if abandoned:
        verdict = "abandoned"
    elif counts["red"] >= 1 or counts["amber"] >= AT_RISK_MIN_AMBER:
        verdict = "at-risk"
    else:
        verdict = "healthy"
    if unknown_stall:
        notes.append("possibly abandoned: every known stall signal is present but data not found for "
                     + ", ".join(unknown_stall) + " — verdict capped at at-risk (SKILL.md: never guess a null metric)")
    if abandoned:
        d = m.get("days_since_last_commit")
        rel = m.get("days_since_last_release")
        rel_txt = f"no release for {num(rel)} d" if rel is not None else "no release in the window"
        biggest = (f"full stall — no commits for {num(d)} d, {rel_txt}, median issue first response "
                   f"{num(m['issue_first_response_median_hours'] / 24)} d")
        driver = "stall pattern"
    else:
        driver, biggest = None, None
        for level in ("red", "amber"):
            for iid in RISK_PRIORITY:
                if by_id[iid]["rating"] == level:
                    driver, biggest = iid, by_id[iid]["risk"]
                    break
            if driver:
                break
        if driver is None:
            driver, biggest = None, "none material — all rated indicators green"
    level, reason = confidence(m)
    result = {
        "repo": m.get("repo") or "unknown/unknown",
        "window_months": window,
        "indicators": inds,
        "counts": counts,
        "verdict": verdict,
        "verdict_rule": VERDICT_RULE,
        "biggest_risk": biggest,
        "biggest_risk_driver": driver,
        "confidence": level,
        "confidence_reason": reason,
        "notes": notes,
        "sources": list(m.get("sources") or []),
        "defaults": {
            "share_threshold": SHARE, "commit_days_band": BAND_COMMIT_DAYS,
            "release_days_band": BAND_RELEASE_DAYS, "first_response_hours_band": BAND_FIRST_RESPONSE_HOURS,
            "pr_merge_days_band": BAND_PR_MERGE_DAYS, "backlog_ratio_band": BAND_BACKLOG_RATIO,
            "advisory_fix_window_days": ADVISORY_FIX_WINDOW_DAYS, "long_window_days": LONG_WINDOW_DAYS,
            "healthy_max_amber": HEALTHY_MAX_AMBER, "at_risk_min_amber": AT_RISK_MIN_AMBER,
        },
    }
    result["report"] = render_report(m, result)
    return result


# --- rendering (SKILL.md step 8) ---------------------------------------------


def data_line(sources):
    if not sources:
        return 'not stated in the metrics file — add "sources": [...] (Ecosyste.ms numbers require "Ecosyste.ms (CC-BY-SA 4.0)")'
    out = []
    for s in sources:
        if "ecosyste" in s.lower() and "cc-by-sa" not in s.lower():
            s = s + " (CC-BY-SA 4.0)"
        out.append(s)
    return "; ".join(out)


def render_report(m, r):
    """The SKILL.md step-8 template, filled from the computed indicators."""
    by_id = {i["id"]: i for i in r["indicators"]}
    window = r["window_months"]
    stars_txt, dd_txt = adoption_text(m)
    bf = by_id["bus_factor"]
    if bf["rating"] is None:
        bus_txt = "data not found"
    else:
        v = bf["value"]
        all_time = f"; {num(m['contributors_all_time'])} all-time contributors" if m.get("contributors_all_time") is not None else ""
        bus_txt = (f"bus factor {v['bus_factor']} — top author {v['top_author']} authored {v['top_share']:.0%} of "
                   f"commits in the last {num(window)} months ({v['authors']} active authors{all_time}) — "
                   + ("spread" if bf["rating"] == "green" else "fragile"))
    act = by_id["activity"]
    if m.get("days_since_last_commit") is not None:
        commit_txt = f"{num(m['days_since_last_commit'])} days ago"
        if m.get("last_commit_date"):
            commit_txt += f" ({m['last_commit_date']})"
        if act["value"] and act["value"].get("archived"):
            commit_txt += "; repository archived"
    elif m.get("archived"):
        commit_txt = "repository archived"
    else:
        commit_txt = "data not found"
    rel = by_id["release"]
    if rel["rating"] is None:
        rel_txt = "data not found"
    else:
        bits = []
        if m.get("releases_12mo") is not None:
            bits.append(f"{num(m['releases_12mo'])} releases in {num(window)} months")
        if m.get("days_since_last_release") is not None:
            bits.append(f"last release {num(m['days_since_last_release'])} days ago"
                        + (f" ({m['last_release_date']})" if m.get("last_release_date") else ""))
        rel_txt = ", ".join(bits)
    adv = by_id["advisories"]
    adv_txt = "data not found" if adv["rating"] is None else adv["display"]
    lines = [
        f"## OSS Project Health — {r['repo']}",
        "",
        f"**Project:** {r['repo']}",
        "",
        f"**Adoption:** {stars_txt}; downloads/dependents: {dd_txt}",
        "",
        f"**Bus factor:** {bus_txt}",
        "",
        f"**Cadence:** last commit {commit_txt}; release rhythm: {rel_txt}",
        "",
        f"**Advisories:** {adv_txt}",
        "",
        f"**Verdict: {r['verdict']}** — biggest risk: {r['biggest_risk']}",
        "",
        f"**Confidence:** {r['confidence']} — {r['confidence_reason']}",
        "",
        f"**Data:** {data_line(r['sources'])}",
    ]
    return "\n".join(lines)


def render_text(r):
    out = []
    out.append(f"OSS Project Health scorecard — {r['repo']}  (window {num(r['window_months'])} months)")
    out.append("")
    out.append("Indicators (rating  indicator  value; threshold and CHAOSS metric on the next line):")
    for i in r["indicators"]:
        tag = (i["rating"] or "n/a").upper()
        out.append(f"  {tag:<6} {i['label']:<30} {i['display']}")
        out.append(f"         threshold: {i['threshold']}")
        out.append(f"         metric:    {i['metric']}")
    c = r["counts"]
    out.append("")
    out.append(f"Counts: {c['red']} red, {c['amber']} amber, {c['green']} green, {c['unrated']} unrated/context")
    out.append(f"Verdict rule (SKILL.md step 7, operationalised): {r['verdict_rule']}")
    out.append(f"Verdict: {r['verdict'].upper()} — biggest risk: {r['biggest_risk']}")
    out.append(f"Confidence: {r['confidence']} — {r['confidence_reason']}")
    if r["notes"]:
        out.append("Notes:")
        out.extend(f"  - {n}" for n in r["notes"])
    out.append("")
    out.append("Report (SKILL.md step 8 template):")
    out.append("")
    out.append(r["report"])
    return "\n".join(out)


# --- fetch (network; explicit opt-in) ----------------------------------------

GITHUB_API = "https://api.github.com"
PERSONAL_DOMAINS = {
    "gmail.com", "googlemail.com", "hotmail.com", "hotmail.co.uk", "outlook.com", "live.com",
    "yahoo.com", "yahoo.co.uk", "ymail.com", "icloud.com", "me.com", "mac.com", "protonmail.com",
    "proton.me", "pm.me", "gmx.de", "gmx.net", "gmx.com", "web.de", "qq.com", "163.com", "126.com",
    "foxmail.com", "yandex.ru", "yandex.com", "mail.ru", "fastmail.com", "fastmail.fm", "hey.com",
    "aol.com", "msn.com", "localhost", "example.com", "users.noreply.github.com",
}
CI_MARKERS_ROOT = {".travis.yml", ".circleci", "azure-pipelines.yml", "jenkinsfile", ".gitlab-ci.yml",
                   "appveyor.yml", ".appveyor.yml", ".buildkite", ".drone.yml", "cloudbuild.yaml",
                   ".woodpecker.yml", ".woodpecker", "bitbucket-pipelines.yml", ".cirrus.yml", "wercker.yml"}


class FetchError(Exception):
    pass


class GitHub:
    """Minimal GitHub REST client (urllib, timeout, rate-limit aware)."""

    def __init__(self, token=None, timeout=20, quiet=False):
        self.token = token
        self.timeout = timeout
        self.quiet = quiet
        self.calls = 0
        self.remaining = None

    def log(self, msg):
        if not self.quiet:
            print(msg, file=sys.stderr)

    def get(self, path, params=None):
        """Return (status, json_or_None). 404 -> (404, None); rate limit -> FetchError."""
        url = GITHUB_API + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "osshealth.py (skill-library)",
                   "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        req = urllib.request.Request(url, headers=headers)
        self.calls += 1
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                self.remaining = resp.headers.get("X-RateLimit-Remaining")
                return resp.status, json.loads(resp.read().decode("utf-8") or "null")
        except urllib.error.HTTPError as exc:
            self.remaining = exc.headers.get("X-RateLimit-Remaining") if exc.headers else None
            if exc.code == 404:
                return 404, None
            if exc.code == 409:  # empty repository (commits endpoint)
                return 409, None
            body = ""
            try:
                body = exc.read().decode("utf-8", "replace")
            except Exception:  # noqa: BLE001 - best effort
                pass
            if exc.code in (403, 429) and (self.remaining == "0" or "rate limit" in body.lower()):
                reset = exc.headers.get("X-RateLimit-Reset") if exc.headers else None
                when = ""
                if reset and reset.isdigit():
                    when = " (resets at %s UTC)" % datetime.fromtimestamp(int(reset), timezone.utc).strftime("%H:%M:%S")
                raise FetchError(
                    "GitHub API rate limit exhausted%s. Unauthenticated calls are capped at 60/hour "
                    "(search: 10/minute); pass --token or set GITHUB_TOKEN for 5,000/hour." % when)
            raise FetchError(f"GitHub API HTTP {exc.code} for {path}: {body[:200].strip() or exc.reason}")
        except urllib.error.URLError as exc:
            raise FetchError(f"network error fetching {path}: {exc.reason}")
        except (TimeoutError, OSError) as exc:
            raise FetchError(f"network error fetching {path}: {exc}")


def parse_gh_time(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def author_key(commit):
    user = commit.get("author") or {}
    login = user.get("login")
    if login:
        return login + ("[bot]" if user.get("type") == "Bot" and not login.endswith("[bot]") else "")
    return (commit.get("commit", {}).get("author") or {}).get("name") or "unknown"


def org_key(commit, akey):
    email = ((commit.get("commit", {}).get("author") or {}).get("email") or "").lower()
    domain = email.rsplit("@", 1)[-1] if "@" in email else ""
    if not domain or domain in PERSONAL_DOMAINS or domain.endswith(".noreply.github.com") or "." not in domain:
        return "individual:" + akey
    return domain


def fetch_github(slug, token=None, window_months=12, issue_sample=15, max_commits=1000, timeout=20, quiet=False):
    """Assemble the metrics snapshot for `assess` from the GitHub REST API."""
    if not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", slug):
        raise FetchError(f"--github expects owner/repo, got {slug!r}")
    gh = GitHub(token, timeout, quiet)
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=round(30.4375 * window_months))
    since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    since_date = since.strftime("%Y-%m-%d")
    notes = []
    m = {"repo": slug, "snapshot_date": now.strftime("%Y-%m-%d"), "window_months": window_months,
         "sources": ["GitHub REST API (api.github.com), snapshot " + now.strftime("%Y-%m-%d")]}

    gh.log(f"fetch: repository {slug}")
    status, repo = gh.get(f"/repos/{slug}")
    if status == 404 or repo is None:
        raise FetchError(f"repository {slug} not found on GitHub (private or misspelt?)")
    m["repo"] = repo.get("full_name") or slug
    m["stars"] = repo.get("stargazers_count")
    m["forks"] = repo.get("forks_count")
    m["archived"] = bool(repo.get("archived"))
    lic = repo.get("license") or {}
    m["license"] = lic.get("spdx_id") if lic else None
    if m["license"] == "NOASSERTION":
        notes.append("licence file present but GitHub could not identify it (NOASSERTION) — check manually")

    # Commits in the window -> commits_by_author / commits_by_org / recency.
    gh.log("fetch: commits in window")
    authors, orgs, window_counts = {}, {}, {}
    newest, page, n_commits, capped = None, 1, 0, False
    while True:
        status, data = gh.get(f"/repos/{slug}/commits", {"since": since_iso, "per_page": 100, "page": page})
        if status in (404, 409) or not data:
            break
        for c in data:
            akey = author_key(c)
            authors[akey] = authors.get(akey, 0) + 1
            okey = org_key(c, akey)
            orgs[okey] = orgs.get(okey, 0) + 1
            n_commits += 1
            date = (c.get("commit", {}).get("committer") or {}).get("date")
            if date and newest is None:
                newest = parse_gh_time(date)
        if len(data) < 100:
            break
        if n_commits >= max_commits:
            capped = True
            break
        page += 1
    if capped:
        notes.append(f"commit sample capped at {n_commits} commits (--max-commits); shares are from the sample")
    if authors:
        m["commits_by_author"] = dict(sorted(authors.items()))
        m["commits_by_org"] = dict(sorted(orgs.items()))
        notes.append("commits_by_org derived from author e-mail domains; personal/noreply addresses count as "
                     "one 'individual:<author>' organisation each")
        window_counts = dict(authors)
    if newest is None:
        status, data = gh.get(f"/repos/{slug}/commits", {"per_page": 1})
        if data:
            date = (data[0].get("commit", {}).get("committer") or {}).get("date")
            newest = parse_gh_time(date) if date else None
        notes.append(f"no commits in the last {window_months} months")
    if newest is not None:
        m["days_since_last_commit"] = (now - newest).days
        m["last_commit_date"] = newest.strftime("%Y-%m-%d")

    # Contributors -> active / new (all-time total == commits in window).
    gh.log("fetch: contributors")
    totals, page = {}, 1
    while page <= 3:
        status, data = gh.get(f"/repos/{slug}/contributors", {"per_page": 100, "page": page, "anon": "false"})
        if not data:
            break
        for u in data:
            if u.get("login"):
                totals[u["login"]] = u.get("contributions", 0)
        if len(data) < 100:
            break
        page += 1
    humans = {k: v for k, v in window_counts.items() if not is_bot(k)}
    m["contributors_12mo"] = len(humans)
    if totals:
        m["contributors_all_time"] = len(totals)
        m["new_contributors_12mo"] = sum(1 for k, v in humans.items() if k in totals and totals[k] == v)
        notes.append("new_contributors_12mo = window authors whose all-time contribution total equals their "
                     "commits in the window (first 300 contributors checked; heuristic)")

    # Releases (fallback: newest tag).
    gh.log("fetch: releases")
    status, rels = gh.get(f"/repos/{slug}/releases", {"per_page": 100})
    published = [parse_gh_time(r["published_at"]) for r in (rels or []) if r.get("published_at") and not r.get("draft")]
    if published:
        latest = max(published)
        m["releases_12mo"] = sum(1 for d in published if d >= since)
        m["days_since_last_release"] = (now - latest).days
        m["last_release_date"] = latest.strftime("%Y-%m-%d")
        if len(rels or []) == 100:
            notes.append("releases_12mo counted from the 100 most recent releases")
    else:
        status, tags = gh.get(f"/repos/{slug}/tags", {"per_page": 1})
        if tags:
            sha = tags[0].get("commit", {}).get("sha")
            status, tc = gh.get(f"/repos/{slug}/commits/{sha}") if sha else (404, None)
            date = ((tc or {}).get("commit", {}).get("committer") or {}).get("date")
            if date:
                latest = parse_gh_time(date)
                m["days_since_last_release"] = (now - latest).days
                m["last_release_date"] = latest.strftime("%Y-%m-%d")
                notes.append(f"no GitHub releases; last tag {tags[0].get('name')} used as last release; release count not available")
        else:
            m["releases_12mo"] = 0
            notes.append("no GitHub releases or tags found")

    # Issues: open count, closed in window (search API), first-response sample.
    if repo.get("has_issues", True):
        gh.log("fetch: issue counts")
        status, s_open = gh.get("/search/issues", {"q": f"repo:{slug} is:issue is:open", "per_page": 1, "advanced_search": "true"})
        status, s_closed = gh.get("/search/issues", {"q": f"repo:{slug} is:issue is:closed closed:>={since_date}",
                                                    "per_page": 1, "advanced_search": "true"})
        if s_open is not None:
            m["open_issues"] = s_open.get("total_count")
        if s_closed is not None:
            m["closed_issues_12mo"] = s_closed.get("total_count")
        if issue_sample > 0:
            gh.log(f"fetch: first-response sample (up to {issue_sample} issues)")
            status, issues = gh.get(f"/repos/{slug}/issues", {"state": "all", "since": since_iso, "sort": "created",
                                                              "direction": "desc", "per_page": min(100, 2 * issue_sample)})
            issues = [i for i in (issues or []) if "pull_request" not in i][:issue_sample]
            hours, unanswered = [], 0
            for i in issues:
                created = parse_gh_time(i["created_at"])
                opener = (i.get("user") or {}).get("login")
                responded = None
                if i.get("comments", 0) > 0:
                    status, comments = gh.get(f"/repos/{slug}/issues/{i['number']}/comments", {"per_page": 30})
                    for c in comments or []:
                        u = c.get("user") or {}
                        if u.get("login") != opener and u.get("type") != "Bot":
                            responded = parse_gh_time(c["created_at"])
                            break
                if responded is None and i.get("closed_at"):
                    responded = parse_gh_time(i["closed_at"])
                if responded is None:
                    unanswered += 1
                    responded = now  # right-censored: current age is a lower bound
                hours.append((responded - created).total_seconds() / 3600.0)
            if hours:
                m["issue_first_response_median_hours"] = round(statistics.median(hours), 1)
                note = (f"issue_first_response_median_hours from a sample of {len(hours)} recent issues "
                        f"(first non-author, non-bot comment or close)")
                if unanswered:
                    note += f"; lower bound — {unanswered} unanswered issues counted at their current age"
                notes.append(note)
    else:
        notes.append("issues disabled on GitHub")

    # PR merge time: last 30 closed PRs.
    gh.log("fetch: pull requests")
    status, pulls = gh.get(f"/repos/{slug}/pulls", {"state": "closed", "sort": "updated", "direction": "desc", "per_page": 30})
    merged = [(parse_gh_time(p["merged_at"]) - parse_gh_time(p["created_at"])).total_seconds() / 86400.0
              for p in (pulls or []) if p.get("merged_at")]
    if merged:
        m["pr_merge_median_days"] = round(statistics.median(merged), 2)
        notes.append(f"pr_merge_median_days from the {len(merged)} merged PRs among the last {len(pulls)} closed PRs")

    # Hygiene files: root and .github listings.
    gh.log("fetch: repository files")
    status, root = gh.get(f"/repos/{slug}/contents/")
    status, dot_github = gh.get(f"/repos/{slug}/contents/.github")
    root_names = {e.get("name", "").lower(): e.get("type") for e in (root or []) if isinstance(e, dict)}
    gh_names = {e.get("name", "").lower(): e.get("type") for e in (dot_github or []) if isinstance(e, dict)}
    names = set(root_names) | set(gh_names)
    m["has_security_policy"] = any(n.startswith("security.") or n == "security" for n in names)
    m["has_ci"] = gh_names.get("workflows") == "dir" or bool(CI_MARKERS_ROOT & set(root_names))
    m["has_code_of_conduct"] = any(n.startswith("code_of_conduct") or n.startswith("code-of-conduct") for n in names)
    m["has_governance_doc"] = any(n.startswith("governance") for n in names)
    m["funding"] = "funding.yml" in names or "funding.yaml" in names
    notes.append("hygiene flags from the repository root and .github/ listings only (docs/ not checked)")
    notes.append("open_advisories, dependents and downloads are not available from the GitHub REST API without a "
                 "package identifier — consult OSV / GitHub Advisory Database / Ecosyste.ms and add them by hand "
                 "(keep the Ecosyste.ms CC-BY-SA 4.0 attribution in \"sources\")")
    m["notes"] = notes
    gh.log(f"fetch: done in {gh.calls} API calls; rate-limit remaining: {gh.remaining}")
    return dict(sorted(m.items()))


# --- selftest ----------------------------------------------------------------


def run_selftest():
    """Hand-verified checks: bus/elephant factor examples, every threshold band,
    licence classification, the verdict rule, and the SKILL.md worked example."""
    checks = []

    def check(name, got, want):
        ok = got == want
        checks.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got!r}, expected {want!r}")
        if not ok:
            print(f"SELFTEST FAILED at: {name}", file=sys.stderr)
            sys.exit(1)

    # Bus factor (CHAOSS Contributor Absence Factor): cumulative share >= 50 %.
    check("bus factor 60/20/20 -> 1", absence_factor({"a": 60, "b": 20, "c": 20})[0], 1)
    check("bus factor 30/30/20/20 -> 2", absence_factor({"a": 30, "b": 30, "c": 20, "d": 20})[0], 2)
    check("bus factor five equal -> 3", absence_factor({"a": 20, "b": 20, "c": 20, "d": 20, "e": 20})[0], 3)
    # CHAOSS worked example: total 2,475, threshold 1,237.5; 1,000 < 1,237.5 < 1,433 -> 2.
    check("bus factor CHAOSS example -> 2",
          absence_factor({"o1": 1000, "o2": 433, "o3": 343, "o4": 332, "o5": 202, "o6": 90, "o7": 42, "o8": 33})[0], 2)
    check("bus factor exactly 50 % counts (50/25/25) -> 1", absence_factor({"a": 50, "b": 25, "c": 25})[0], 1)
    check("bus factor single author -> 1", absence_factor({"solo": 7})[0], 1)
    check("bus factor no commits -> None", absence_factor({"a": 0})[0], None)
    check("bus factor tie order deterministic", absence_factor({"b": 10, "a": 10, "c": 5})[1][0][0], "a")
    humans, bots = split_bots({"dependabot[bot]": 500, "a": 60, "b": 20, "c": 20})
    check("bots excluded from bus factor", (sorted(bots), absence_factor(humans)[0]), (["dependabot[bot]"], 1))

    # Elephant factor (CHAOSS): same computation over organisations.
    check("elephant 55/45 -> 1", absence_factor({"Acme": 55, "Beta": 45})[0], 1)
    check("elephant 40/35/25 -> 2", absence_factor({"A": 40, "B": 35, "C": 25})[0], 2)
    check("elephant 34/33/33 -> 2", absence_factor({"A": 34, "B": 33, "C": 33})[0], 2)
    check("elephant rating 1 -> amber", ind_elephant({"commits_by_org": {"A": 9, "B": 1}})["rating"], "amber")
    check("elephant exactly 50 % (5/5) -> 1", absence_factor({"A": 5, "B": 5})[0], 1)
    check("elephant rating 2 -> green", ind_elephant({"commits_by_org": {"A": 4, "B": 3, "C": 3}})["rating"], "green")

    # Threshold bands (each edge).
    for d, want in ((0, "green"), (90, "green"), (91, "amber"), (180, "amber"), (181, "red")):
        check(f"last commit {d} d -> {want}", ind_activity({"days_since_last_commit": d}, 12)["rating"], want)
    check("archived repo -> red", ind_activity({"days_since_last_commit": 3, "archived": True}, 12)["rating"], "red")
    for d, want in ((180, "green"), (181, "amber"), (365, "amber"), (366, "red")):
        check(f"last release {d} d -> {want}", ind_release({"days_since_last_release": d, "releases_12mo": 1}, 12)["rating"], want)
    check("release count only, 0 -> amber", ind_release({"releases_12mo": 0}, 12)["rating"], "amber")
    check("release count only, 2 -> green", ind_release({"releases_12mo": 2}, 12)["rating"], "green")
    for h, want in ((48, "green"), (49, "amber"), (336, "amber"), (337, "red")):
        check(f"first response {h} h -> {want}", ind_first_response({"issue_first_response_median_hours": h})["rating"], want)
    for d, want in ((7, "green"), (7.5, "amber"), (30, "amber"), (31, "red")):
        check(f"PR merge {d} d -> {want}", ind_pr_merge({"pr_merge_median_days": d})["rating"], want)
    for o, c, want in ((99, 100, "green"), (100, 100, "amber"), (300, 100, "amber"), (301, 100, "red"), (5, 0, "red")):
        check(f"backlog {o}/{c} -> {want}", ind_backlog({"open_issues": o, "closed_issues_12mo": c}, 12)["rating"], want)
    check("backlog 0/0 -> unrated", ind_backlog({"open_issues": 0, "closed_issues_12mo": 0}, 12)["rating"], None)
    check("new contributors 0 -> amber", ind_new_contributors({"new_contributors_12mo": 0}, 12)["rating"], "amber")
    check("new contributors 1 -> green", ind_new_contributors({"new_contributors_12mo": 1}, 12)["rating"], "green")
    check("advisories 0 -> green", ind_advisories({"open_advisories": 0})["rating"], "green")
    check("advisories 1, age unknown -> amber", ind_advisories({"open_advisories": 1})["rating"], "amber")
    check("advisories 1, 90 d -> amber", ind_advisories({"open_advisories": 1, "advisory_max_age_days": 90})["rating"], "amber")
    check("advisories 1, 91 d -> red", ind_advisories({"open_advisories": 1, "advisory_max_age_days": 91})["rating"], "red")
    check("advisories missing -> unrated", ind_advisories({})["rating"], None)

    # Licence classification (CHAOSS OSI Approved Licenses) and hygiene rating.
    check("licence MIT -> osi", license_status("MIT")[0], "osi")
    check("licence apache-2.0 -> osi", license_status("apache-2.0")[0], "osi")
    check("licence GPL-3.0-or-later -> osi", license_status("GPL-3.0-or-later")[0], "osi")
    check("licence 'BSD 3-Clause' -> osi", license_status("BSD 3-Clause")[0], "osi")
    check("licence SSPL-1.0 -> non-osi", license_status("SSPL-1.0")[0], "non-osi")
    check("licence CC0-1.0 -> non-osi", license_status("CC0-1.0")[0], "non-osi")
    check("licence NOASSERTION -> unrecognised", license_status("NOASSERTION")[0], "unrecognised")
    check("licence null -> not-found (data not found, never 'no licence')", license_status(None)[0], "not-found")
    check("licence 'none' -> missing", license_status("none")[0], "missing")
    all_ok = {"license": "MIT", "has_security_policy": True, "has_ci": True, "has_code_of_conduct": True}
    check("hygiene all present -> green", ind_hygiene(all_ok)["rating"], "green")
    check("hygiene one gap -> green", ind_hygiene(dict(all_ok, has_security_policy=False))["rating"], "green")
    check("hygiene two gaps -> amber", ind_hygiene(dict(all_ok, has_security_policy=False, has_code_of_conduct=False))["rating"], "amber")
    check("hygiene non-OSI licence -> amber", ind_hygiene(dict(all_ok, license="BUSL-1.1"))["rating"], "amber")
    check("hygiene no licence -> red", ind_hygiene(dict(all_ok, license="none"))["rating"], "red")
    check("hygiene licence data not found, files fine -> green", ind_hygiene(dict(all_ok, license=None))["rating"], "green")
    check("hygiene nothing known -> unrated", ind_hygiene({})["rating"], None)

    # Verdict rule.
    good = {"repo": "x/y", "commits_by_author": {"a": 24, "b": 22, "c": 20, "d": 18, "e": 16}, "days_since_last_commit": 10,
            "releases_12mo": 4, "days_since_last_release": 60, "issue_first_response_median_hours": 24,
            "pr_merge_median_days": 3, "open_issues": 50, "closed_issues_12mo": 200, "new_contributors_12mo": 5,
            "open_advisories": 0, "license": "Apache-2.0", "has_security_policy": True, "has_ci": True,
            "has_code_of_conduct": True}
    r = assess(good)
    check("all green -> healthy", (r["verdict"], r["counts"]["red"], r["counts"]["amber"]), ("healthy", 0, 0))
    check("healthy confidence high", r["confidence"], "high")
    r = assess(dict(good, new_contributors_12mo=0, pr_merge_median_days=10))
    check("2 amber, 0 red -> healthy", (r["verdict"], r["counts"]["amber"]), ("healthy", 2))
    r = assess(dict(good, new_contributors_12mo=0, pr_merge_median_days=10, days_since_last_commit=100))
    check("3 amber, 0 red -> at-risk", (r["verdict"], r["counts"]["amber"]), ("at-risk", 3))
    r = assess(dict(good, commits_by_author={"solo": 100}))
    check("1 red (bus factor) -> at-risk", (r["verdict"], r["biggest_risk_driver"]), ("at-risk", "bus_factor"))
    stalled = dict(good, days_since_last_commit=400, days_since_last_release=500, releases_12mo=0,
                   issue_first_response_median_hours=24 * 30)
    r = assess(stalled)
    check("full stall -> abandoned", r["verdict"], "abandoned")
    r = assess(dict(stalled, issue_first_response_median_hours=None))
    check("stall with response unknown -> at-risk (never guess a null)", r["verdict"], "at-risk")
    check("stall note explains the cap", any(n.startswith("possibly abandoned") for n in r["notes"]), True)
    r = assess(dict(good, open_advisories=None, days_since_last_release=None, releases_12mo=None))
    check("2 core fields missing -> medium confidence", r["confidence"], "medium")
    r = assess({"repo": "x/y", "stars": 10})
    check("3+ core fields missing -> low confidence", r["confidence"], "low")
    check("nothing rated -> 0 red, 0 amber -> healthy (low confidence)", (r["verdict"], r["counts"]["unrated"]), ("healthy", 12))

    # SKILL.md worked example reproduced by --demo.
    r = assess(DEMO)
    bf = r["indicators"][0]["value"]
    check("demo bus factor", (bf["bus_factor"], round(bf["top_share"], 2)), (1, 0.71))
    check("demo verdict at-risk", r["verdict"], "at-risk")
    check("demo biggest risk = single-maintainer dependence", r["biggest_risk"].startswith("single-maintainer dependence"), True)
    check("demo report has verdict line", "**Verdict: at-risk**" in r["report"], True)
    check("demo report keeps Ecosyste.ms attribution", "**Data:** Ecosyste.ms (CC-BY-SA 4.0)" in r["report"], True)

    # CLI: exit codes and JSON determinism.
    with contextlib.redirect_stdout(io.StringIO()):
        code = main(["assess", "--demo"])
    check("assess --demo exits 1 (at-risk verdict)", code, 1)
    buf1, buf2 = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf1):
        main(["assess", "--demo", "--json"])
    with contextlib.redirect_stdout(buf2):
        main(["assess", "--demo", "--json"])
    check("json output byte-identical across runs", buf1.getvalue() == buf2.getvalue(), True)
    check("json output parses with verdict", json.loads(buf1.getvalue())["verdict"], "at-risk")
    try:
        validate_metrics({"days_since_last_commit": "soon"})
        bad = False
    except ValueError:
        bad = True
    check("invalid input raises ValueError", bad, True)
    try:
        validate_metrics({"commits_by_author": {"a": -1}})
        bad = False
    except ValueError:
        bad = True
    check("negative commits rejected", bad, True)

    print(f"ALL {len(checks)} CHECKS PASSED")
    print("selftest OK")
    return 0


# --- CLI ---------------------------------------------------------------------


def build_parser():
    parser = argparse.ArgumentParser(
        description="CHAOSS-style OSS project health scorecard: bus/elephant factor, cadence, "
                    "responsiveness, backlog, growth, hygiene, verdict (healthy / at-risk / abandoned).")
    parser.add_argument("--selftest", action="store_true", help="run built-in hand-verified checks and exit")
    parser.add_argument("--demo", action="store_true", help="shortcut for: assess --demo")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("assess", help="rate a metrics snapshot and print the SKILL.md report")
    p.add_argument("--file", help="metrics JSON (see module docstring); '-' reads stdin")
    p.add_argument("--demo", action="store_true", help="use the SKILL.md worked example (acme-utils/htmltidy)")
    p.add_argument("--json", action="store_true", help="emit the full result as JSON")
    f = sub.add_parser("fetch", help="[network] assemble metrics JSON from the GitHub REST API")
    f.add_argument("--github", required=True, metavar="OWNER/REPO", help="repository slug")
    f.add_argument("--token", help="GitHub token (else $GITHUB_TOKEN / $GH_TOKEN); optional")
    f.add_argument("--window-months", type=int, default=12, help="activity window (default 12)")
    f.add_argument("--issue-sample", type=int, default=15, help="issues sampled for first-response median (default 15; 0 skips)")
    f.add_argument("--max-commits", type=int, default=1000, help="cap on commits paged (default 1000)")
    f.add_argument("--timeout", type=int, default=20, help="per-request timeout in seconds (default 20)")
    f.add_argument("--out", help="write the metrics JSON here instead of stdout")
    f.add_argument("--quiet", action="store_true", help="suppress progress messages on stderr")
    return parser


def cmd_assess(args, parser):
    if args.demo:
        data = DEMO
    elif args.file:
        try:
            data = load_metrics(args.file)
        except (OSError, ValueError) as exc:
            print(f"error: could not load {args.file}: {exc}", file=sys.stderr)
            return 2
    else:
        parser.error("assess needs --file PATH or --demo")
    try:
        result = assess(data)
    except ValueError as exc:
        print(f"error: invalid metrics: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_text(result))
    return 1 if result["verdict"] in ("at-risk", "abandoned") else 0


def cmd_fetch(args):
    token = args.token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    try:
        metrics = fetch_github(args.github, token=token, window_months=args.window_months,
                               issue_sample=args.issue_sample, max_commits=args.max_commits,
                               timeout=args.timeout, quiet=args.quiet)
    except FetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(metrics, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"wrote {args.out}; next: python3 {os.path.basename(sys.argv[0])} assess --file {args.out}", file=sys.stderr)
    else:
        print(text)
    return 0


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if args.command is None and args.demo:
        args = parser.parse_args(["assess", "--demo"])
    if not args.command:
        parser.error("choose a command: assess | fetch  (or --demo / --selftest)")
    if args.command == "assess":
        return cmd_assess(args, parser)
    if args.window_months <= 0:
        parser.error("--window-months must be >= 1")
    return cmd_fetch(args)


if __name__ == "__main__":
    sys.exit(main())
