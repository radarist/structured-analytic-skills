---
name: Bug — a script or check misbehaves
about: A companion tool, an evaluation script or a CI gate does the wrong thing
title: "bug: <script or check> — <symptom>"
labels: bug
---

## Command — required

The exact command, copy-pasteable from a clone of this repository:

```bash

```

## Expected — required

What you expected it to print, or which exit code you expected.

## Observed — required

What it actually printed. Paste the output, including the traceback if there is one:

```

```

## Environment

- Python version (`python3 --version`): 
- OS: 
- Commit (`git rev-parse --short HEAD`): 

## Determinism

Companion tools must produce byte-identical output on two runs. Did they?

- [ ] Ran it twice; output identical
- [ ] Ran it twice; output differed (paste the diff above)
- [ ] Not applicable
