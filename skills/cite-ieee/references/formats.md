# IEEE reference formats by source type

Basic formats and examples from the *IEEE Reference Guide* (IEEE Publication Operations,
Piscataway, NJ, USA, V 3.28.2025), §II "Style". `scripts/ieee.py format` renders each of
these from structured fields; its `--selftest` checks the output against the guide's own
examples. Markdown reports italicise the periodical or book title (`*…*`); plain-text
output leaves it unstyled.

General rules (§II):
- Given names are reduced to initials before the surname; no commas around Jr., Sr., III.
- List all authors up to six; with seven or more, use the first author followed by "et al."
- Every reference ends with a period **except** one ending in a URL. A reference carrying
  both a DOI or accessed date and a URL puts the DOI/accessed date first, then the URL.
- Every reference carries at least a year. Months are abbreviated: Jan., Feb., Mar., Apr.,
  May, Jun., Jul., Aug., Sep., Oct., Nov., Dec. Page ranges use an en dash.
- "Do not combine references. There must be only one reference with each number."

## Periodical (journal article)

```
J. K. Author, "Name of paper," Abbrev. Title of Periodical, vol. x, no. x, pp. xxx–xxx, Abbrev. Month, year, doi: xxx.
```

Example (guide, "Periodical With DOI"):

```
M. M. Chiampi and L. L. Zilberti, "Induction of electric field in human bodies moving near MRI: An efficient BEM computational procedure," IEEE Trans. Biomed. Eng., vol. 58, no. 10, pp. 2787–2793, Oct. 2011, doi: 10.1109/TBME.2011.2158315.
```

Article-ID form, when the article has no page range:

```
J. Zhang and N. Tansu, "Optical gain and laser characteristics of InGaN quantum wells on ternary InGaN substrates," IEEE Photon. J., vol. 5, no. 2, Apr. 2013, Art no. 2600111.
```

## Conference proceedings

```
J. K. Author, "Title of paper," in Abbreviated Name of Conf., (location optional), year, pp. xxx–xxx, doi: xxx.
```

```
G. Veruggio, "The EURON roboethics roadmap," in Proc. Humanoids '06: 6th IEEE-RAS Int. Conf. Humanoid Robots, 2006, pp. 612–617, doi: 10.1109/ICHR.2006.321337.
```

## Book, and chapter in a book

```
J. K. Author, "Title of chapter in the book," in Title of Published Book, xth ed. City of Publisher, (only U.S. State), Country: Abbrev. of Publisher, year, ch. x, sect. x, pp. xxx–xxx.
```

```
B. Klaus and P. Horn, Robot Vision. Cambridge, MA, USA: MIT Press, 1986.
L. Stein, "Random patterns," in Computers and You, J. S. Brake, Ed., New York, NY, USA: Wiley, 1994, pp. 55–70.
```

## Preprint (arXiv)

```
J. K. Author, "Title of paper," year, arXiv number.
```

```
S. Urazhdin, N. O. Birge, W. P. Pratt Jr., and J. Bass, "Current-driven magnetic excitations in permalloy-based multilayer nanopillars," 2003, arXiv:0303149.
```

Note the order: the year precedes the identifier. The guide also warns that once an
article is available as advanced online access at the publisher, that version — journal
title, date of record and DOI — is cited instead of the arXiv version.

## News article

Print:

```
J. K. Author, "Title of the article," Title of the News Source, Month, Day, Year.
```

Online:

```
A. Clark, "A new AI tool creates hyperrealistic photos. Can you tell the difference?" CBS News, Aug. 30, 2024. [Online]. Available: https://www.cbsnews.com/news/can-you-tell-real-image-from-ai-flux/
```

## Website

```
First Name Initial(s) Last Name. "Page Title." Website Title. Accessed: Month Day, Year. [Online]. Available: Web Address
```

```
J. Smith. "Obama inaugurated as President." CNN.com. Accessed: Feb. 1, 2009. [Online.] Available: http://www.cnn.com/POLITICS/01/21/obama_inaugurated/index.html
```

## Patent

```
J. K. Author, "Title of patent," U.S. Patent x xxx xxx, Abbrev. Month, day, year.
```

```
J. P. Wilkinson, "Nonlinear resonant circuit devices," U.S. Patent 3 624 125, Jul. 16, 1990.
```

## Standard

```
Title of Standard, Standard number, Corporate author, location, date.
```

```
IEEE Criteria for Class IE Electric Systems, IEEE Standard 308, 1969.
```

## Technical report

```
J. K. Author, "Title of report," Abbrev. Name of Co., City of Co., Abbrev. State, Country, Rep. xxx, year.
```

```
E. E. Reber, R. L. Michell, and C. J. Carter, "Oxygen absorption in the Earth's atmosphere," Aerospace Corp., Los Angeles, CA, USA, Tech. Rep. TR-0200 (4230-46)-3, Nov. 1988.
```

## Thesis or dissertation

```
J. K. Author, "Title of dissertation," Ph.D. dissertation, Abbrev. Dept., Abbrev. Univ., City of Univ., Abbrev. State, year.
```

```
J. O. Williams, "Narrow-band analyzer," Ph.D. dissertation, Dept. Elect. Eng., Harvard Univ., Cambridge, MA, USA, 1993.
```

## Dataset

```
Author, Date, "Title of Dataset," Source, doi: xxx.
```

## Corporate or government filing

Cite the issuing entity as the author, quote the document type, and give the authority,
its location and the publication date — following the report format above, e.g.:

```
Nvidia Corporation, "Form 10-K for fiscal year ended Jan. 28, 2024," U.S. Securities and Exchange Commission, Washington, DC, USA, Feb. 21, 2024. [Online]. Available: https://www.sec.gov/
```

## Citing part of a reference

Locators go inside the bracket rather than into the entry: `[3, Th. 1]`, `[3, pp. 5–10]`,
`[3, eq. (2)]`, `[3, Fig. 1]`, `[3, Sect. 4.5]`, `[3, Ch. 2, pp. 5–10]`. Do not list the
same source twice to cite two of its pages.
