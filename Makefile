# Convenience targets for the structured-analytic-skills library.
# Everything is stdlib Python 3.9+; no installation required.

PY ?= python3

.PHONY: check score compare trigger index metadata eval-schema exit-codes validate all clean

all: check score trigger index metadata eval-schema exit-codes ## run the full evaluation suite

check:                                  ## structural gate: frontmatter, links, self-containment, script self-tests
	$(PY) evaluation/check_repo.py

score:                                  ## deterministic 12-dimension scorecard -> evaluation/scores/latest.{json,md}
	$(PY) evaluation/score_skills.py --min-score 95 --min-library 99

compare:                                ## like-for-like current vs baseline report -> /tmp
	$(PY) evaluation/score_skills.py --baseline evaluation/scores/baseline-2026-08-16.json --json /tmp/skill-library-comparison.json --md /tmp/skill-library-comparison.md

trigger:                                ## discoverability (BM25 trigger) eval over skills/*/evals/evals.json
	$(PY) evaluation/trigger_eval.py --min-rank1 0.98 --min-negative 0.98 --min-cases 3 --min-routed 0.90

index:                                  ## regenerate index.json from frontmatter
	$(PY) evaluation/build_index.py

metadata:                               ## verify Codex / ChatGPT agents/openai.yaml metadata
	$(PY) evaluation/build_openai_metadata.py --check

eval-schema:                            ## verify canonical skill-creator eval files
	$(PY) evaluation/eval_schema.py --check

exit-codes:                             ## enforce 0 pass / 1 failing verdict / 2 usage across every tool
	$(PY) evaluation/exit_codes.py

validate:                               ## official Claude Code validator (needs the claude CLI)
	claude plugin validate skills --strict && claude plugin validate .claude-plugin/marketplace.json --strict

clean:                                  ## remove caches and OS junk
	find . -name '__pycache__' -type d -prune -exec rm -rf {} + ; find . -name '.DS_Store' -delete
