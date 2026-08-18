# Security

This repository contains Markdown skills and standard-library-only Python scripts. The
scripts read local files and print results; none of them writes outside the current
directory, and none contacts the network unless you explicitly opt in. There are
exactly two network entry points in the library:

- `skills/verify-citations/scripts/citecheck.py --online` — resolves DOIs, arXiv IDs
  and ISBNs against doi.org, export.arxiv.org and openlibrary.org. Without the flag
  the tool validates identifier syntax and checksums offline.
- `skills/oss-project-health/scripts/osshealth.py fetch --github OWNER/REPO` — reads
  the GitHub REST API. Every other subcommand scores a metrics JSON file you supply.

`--selftest` never uses the network, in any script.

Please report a vulnerability (for example a script that executes input, or a skill that
instructs an agent to run untrusted code) through a
[private security advisory](https://github.com/radarist/structured-analytic-skills/security/advisories/new).
Never put vulnerability details, credentials, exploit code or private data in a public issue.
If private advisories are unavailable, open a non-sensitive issue asking the maintainer to
enable a private reporting channel, without including the vulnerability details. We aim to
respond within seven days.

Supported version: the `main` branch and the latest tagged release.
