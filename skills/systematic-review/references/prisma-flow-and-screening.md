# PRISMA 2020 flow, exclusion reasons and screening agreement

Companion to `../SKILL.md`. Reporting follows Page et al., *BMJ* 372:n71 (2021); search reporting follows PRISMA-S (Rethlefsen et al., 2021).

## The PRISMA 2020 flow (new reviews, databases and registers)

| Phase | Box | Count |
|---|---|---|
| Identification | Records identified from databases and registers | N1 (per source) |
| Identification | Records removed before screening: duplicates, records marked ineligible by automation tools, records removed for other reasons | D |
| Screening | Records screened | N2 = N1 − D |
| Screening | Records excluded (title/abstract) | E1 |
| Screening | Reports sought for retrieval / reports not retrieved | — |
| Eligibility | Reports assessed for eligibility | N3 = N2 − E1 |
| Eligibility | Reports excluded, **with reasons** | E2 (by reason) |
| Included | Studies included in review; reports of included studies | N4 = N3 − E2 |

Every arrow must reconcile: `N1 − D = N2`, `N2 − E1 = N3`, `N3 − E2 = N4`. `../scripts/prisma.py flow` checks all three and exits non-zero on a mismatch. PRISMA 2020 also provides a variant diagram that adds records identified from other sources (websites, organisations, citation searching).

## Exclusion-reason vocabulary

Log each excluded full text against exactly one reason:

- wrong population or scope
- wrong study design (e.g. no comparator, single-arm)
- outcome of interest not measured
- outside the pre-registered date window
- language outside the protocol
- insufficient methodological detail to assess
- secondary report of a primary study already included
- full text not retrievable

## Screening agreement (Cohen's kappa)

```
kappa = (p_observed − p_chance) / (1 − p_chance)
p_chance = p_A1·p_B1 + (1 − p_A1)(1 − p_B1)
```

Landis and Koch (1977) bands, as printed by `../scripts/prisma.py kappa`:

| kappa | Band |
|---|---|
| < 0.00 | poor (less than chance agreement) |
| 0.00 – 0.20 | slight |
| 0.21 – 0.40 | fair |
| 0.41 – 0.60 | moderate |
| 0.61 – 0.80 | substantial |
| 0.81 – 1.00 | almost perfect |

Below moderate, the criteria — not the screeners — are the problem: refine and re-screen. Kappa is undefined when neither screener varies (both include everything, or exclude everything); the tool reports that rather than printing a number.

## Protocol elements to pre-register

Question (PICO/PECO or free-form) · inclusion criteria · exclusion criteria · databases and exact query strings with the date each was run · grey-literature and snowballing plan · screening procedure and number of screeners · data-extraction fields · quality threshold (Admiralty grade, risk-of-bias judgement) · planned synthesis method · amendment log.

## References

- M. J. Page et al., *BMJ* 372:n71, 2021. doi:10.1136/bmj.n71
- M. L. Rethlefsen et al., *Systematic Reviews* 10(1):39, 2021. doi:10.1186/s13643-020-01542-z
- J. Cohen, *Educational and Psychological Measurement* 20(1):37–46, 1960. doi:10.1177/001316446002000104
- J. R. Landis and G. G. Koch, *Biometrics* 33(1):159–174, 1977. doi:10.2307/2529310
