# Term-by-term tables — ICD 203, PHIA yardstick, IPCC AR5

Reference for `skills/estimative-language`. Read when converting a specific probability,
looking up a term's range, or auditing which standard a document uses. Ranges are
reproduced as the standards print them. `python3 ../scripts/wep.py table --standard
icd203|phia|ipcc` prints the same tables with their citations, and
`wep.py term --p 0.7 --standard X` / `wep.py prob --term "likely"` do the lookups.

## ODNI ICD 203 — likelihood terms (§D.6.e(2)(a))

Two synonym rows over seven contiguous bands. "Analysts are strongly encouraged not to mix
terms from different rows. Products that do mix terms must include a disclaimer clearly
noting the terms indicate the same assessment of probability."

| Term | Synonym row | Probability |
| --- | --- | --- |
| almost no chance | remote | 01–05 % |
| very unlikely | highly improbable | 05–20 % |
| unlikely | improbable (improbably) | 20–45 % |
| roughly even chance | roughly even odds | 45–55 % |
| likely | probable (probably) | 55–80 % |
| very likely | highly probable | 80–95 % |
| almost certain(ly) | nearly certain | 95–99 % |

Adjacent bands share a boundary (20 %, 45 %, 55 %, 80 %, 95 %): pick one term and attach the
number. The table runs 01–99 %, so 0 % and 100 % have no term — state certainty in words.

**Confidence.** ICD 203 §D.6.e(2)(b): a product using a confidence level "must not combine a
confidence level and a degree of likelihood, which refers to an event or development, in the
same sentence." Confidence "may be based on the logic and evidentiary base that underpin it,
including the quantity and quality of source material, and their understanding of the topic."
The NIE gloss ("What We Mean When We Say", 2007): **high** = judgments based on high-quality
information and/or an issue that permits a solid judgment (still not a fact or certainty);
**moderate** = credibly sourced and plausible, but not of sufficient quality or corroboration
for a higher level; **low** = credibility or plausibility questionable, information fragmented
or poorly corroborated, or concerns about the sources.

ICD 203 §D.6.e(3) also requires that products distinguish underlying information from
assumptions and judgments, state linchpin assumptions explicitly, explain the implications if
they prove incorrect, and identify indicators that would alter judgments. Source descriptors
and source summary statements come from ICD 206.

## UK PHIA Probability Yardstick

Seven ranges with deliberate gaps: "The scale is not continuous to avoid a false impression of
accuracy" (MoD Defence Intelligence, 2023). Terms are used "instead of numerical probabilities
(e.g. 55%) to avoid interpretation of judgements as being overly precise".

| Probability | Term |
| --- | --- |
| >0 % – ≈5 % | remote chance |
| ≈10 % – ≈20 % | highly unlikely |
| ≈25 % – ≈35 % | unlikely |
| ≈40 % – <50 % | realistic possibility |
| ≈55 % – ≈75 % | likely or probable |
| ≈80 % – ≈90 % | highly likely |
| ≈95 % – <100 % | almost certain |

Gaps: 5–10, 20–25, 35–40, 50–55, 75–80, 90–95 %. A judgment landing in a gap (50 % is the
common case) is stated as a number or moved into a band — never given an invented term. Note
there is no "roughly even chance" in this yardstick; "realistic possibility" tops out below
50 %.

**Confidence.** A separate Analytical Confidence Rating (AnCR): **High, Moderate or Low**,
chosen with the PHIA evaluation tool across three categories — Information Base (the
information and sources), Analytical Rigour (how the information was examined) and Complexity
& Volatility (how fast the situation is evolving). A supporting AnCR statement gives the
source and effect of the remaining uncertainty and how confidence could be increased.
Probability and confidence are "two frameworks to describe different but related aspects of
uncertainty".

## IPCC AR5 Guidance Note — Table 1 likelihood scale

Nested bands with "fuzzy" boundaries: several terms can be true of one probability; report the
narrowest. "When there is sufficient information, it is preferable to specify the full
probability distribution or a probability range (e.g., 90-95%) without using the terms."

| Term | Likelihood of the outcome |
| --- | --- |
| virtually certain | 99–100 % probability |
| very likely | 90–100 % probability |
| likely | 66–100 % probability |
| about as likely as not | 33–66 % probability |
| unlikely | 0–33 % probability |
| very unlikely | 0–10 % probability |
| exceptionally unlikely | 0–1 % probability |

AR4 terms usable "when appropriate": extremely likely 95–100 %, more likely than not
>50–100 %, extremely unlikely 0–5 %. "About as likely as not" must not be used to express a
lack of knowledge — that case takes evidence/agreement summary terms instead.

**Confidence.** Five qualifiers — very low, low, medium, high, very high — synthesising
evidence (limited / medium / robust) and agreement (low / medium / high). Confidence increases
with both. "Confidence should not be interpreted probabilistically, and it is distinct from
'statistical confidence'." A finding that already carries a probabilistic measure need not
state confidence when it is high or very high; findings at low or very low confidence should
be reserved for areas of major concern and explained.

## Sources

- Office of the Director of National Intelligence, *Intelligence Community Directive 203: Analytic Standards*, 2 January 2015; technical amendment 21 December 2022, §D.6.e(2)–(3). https://www.dni.gov/files/documents/ICD/ICD-203-TA-Analytic-Standards-21-Dec-2022.pdf
- National Intelligence Council, *Iran: Nuclear Intentions and Capabilities*, National Intelligence Estimate, November 2007, "What We Mean When We Say: An Explanation of Estimative Language". https://www.dni.gov/files/documents/Newsroom/Reports%20and%20Publications/20071203_release.pdf
- Professional Head of Intelligence Assessment (Cabinet Office), *Explaining Uncertainty in UK Intelligence Assessment*, GOV.UK guidance, 24 March 2025. https://www.gov.uk/government/publications/explaining-uncertainty-in-uk-intelligence-assessment/explaining-uncertainty-in-uk-intelligence-assessment
- Ministry of Defence, "Defence Intelligence: communicating probability", GOV.UK news story, 17 February 2023. https://www.gov.uk/government/news/defence-intelligence-communicating-probability
- M. D. Mastrandrea et al., *Guidance Note for Lead Authors of the IPCC Fifth Assessment Report on Consistent Treatment of Uncertainties*, IPCC, 2010, Table 1 and paragraphs 8–10. https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf
- Office of the Director of National Intelligence, *Intelligence Community Directive 206: Sourcing Requirements for Disseminated Analytic Products*, 22 January 2015. https://www.dni.gov/files/documents/ICD/ICD-206.pdf

## Attribution and licence of the reproduced tables

- **ODNI ICD 203** (US likelihood terms and confidence levels) — a work of the United States
  Government; public domain under 17 U.S.C. §105.
- **UK PHIA Probability Yardstick** — © Crown copyright. Contains public sector information
  licensed under the **Open Government Licence v3.0**
  (https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
- **IPCC AR5 likelihood and confidence scales** (Mastrandrea et al., 2010) — © IPCC. The IPCC
  permits copying for personal, non-commercial use; it grants no general reuse licence. The
  band boundaries themselves are facts and are reproduced here as such, in this repository's
  own layout, for identification and comparison. Anyone redistributing this file commercially
  should seek permission from copyright@ipcc.ch.

The MIT licence covering this repository's own text does **not** extend to the third-party
material above. See [THIRD-PARTY-NOTICES.md](../../../THIRD-PARTY-NOTICES.md).
