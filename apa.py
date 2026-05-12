
# “””
APA Citation Builder (7th Edition)

Supports: journal article, book, book chapter, website, newspaper article,
report, podcast episode, YouTube/video, dissertation/thesis,
conference paper, magazine article.

Null-handling rules:

- Missing author       → use editor(s) with “(Ed.)” / “(Eds.)”, or “(Author unknown)”
- Missing year         → use “n.d.” (no date)
- Missing title        → use “[No title]”
- Missing source/journal → use “[Source unknown]”
- Missing URL/DOI      → omitted silently
- Missing volume/issue/pages → omitted silently
- Missing publisher    → use “[Publisher unknown]”
- Missing city/location → omitted silently (APA 7 no longer requires location)
- Partial author info  → use whatever is available; if only last name, use it alone
  “””

from **future** import annotations
from dataclasses import dataclass, field
from typing import Optional, List
import re

# —————————————————————————

# Helper utilities

# —————————————————————————

def _clean(value: Optional[str]) -> Optional[str]:
“”“Strip whitespace; return None for empty strings.”””
if value is None:
return None
s = value.strip()
return s if s else None

def _format_author_name(last: Optional[str], first: Optional[str]) -> Optional[str]:
“”“Return ‘Last, F.’ format, handling partial data.”””
last = _clean(last)
first = _clean(first)
if last and first:
initials = “. “.join(p[0].upper() for p in re.split(r”[\s-]+”, first) if p) + “.”
return f”{last}, {initials}”
if last:
return last
if first:
return first
return None

def _format_author_list(authors: List[dict]) -> str:
“””
Format a list of author dicts (keys: last, first, suffix).
APA rules:
1 author  → Last, F.
2-20      → Last, F., & Last2, F2.
21+       → first 19 … Last, F. (omit middle authors with ellipsis)
Returns “(Author unknown)” if list is empty or all entries are blank.
“””
formatted = [f for a in authors if (f := _format_author_name(a.get(“last”), a.get(“first”)))]
if not formatted:
return “(Author unknown)”
n = len(formatted)
if n == 1:
return formatted[0]
if n <= 20:
return “, “.join(formatted[:-1]) + “, & “ + formatted[-1]
# 21+ authors
return “, “.join(formatted[:19]) + “, … “ + formatted[-1]

def _format_editors(editors: List[dict]) -> str:
“”“Return ‘A. Last & B. Last (Ed.)’ style string.”””
formatted = [f for e in editors if (f := _format_author_name(e.get(“last”), e.get(“first”)))]
if not formatted:
return “(Author unknown)”
suffix = “(Ed.)” if len(formatted) == 1 else “(Eds.)”
if len(formatted) == 1:
return f”{formatted[0]} {suffix}”
joined = “, “.join(formatted[:-1]) + “, & “ + formatted[-1]
return f”{joined} {suffix}”

def _year_str(year: Optional[str]) -> str:
return f”({_clean(year) or ‘n.d.’}).”

def _doi_url(doi: Optional[str], url: Optional[str]) -> Optional[str]:
doi = _clean(doi)
url = _clean(url)
if doi:
doi = doi.lstrip(“https://doi.org/”).lstrip(“doi:”)
return f”https://doi.org/{doi}”
return url

def _italicize(text: Optional[str], fallback: str = “[No title]”) -> str:
“”“Wrap in markdown italics (used for titles of stand-alone works).”””
t = _clean(text) or fallback
return f”*{t}*”

def _sentence_case(text: Optional[str], fallback: str = “[No title]”) -> str:
“”“APA uses sentence case for article/chapter titles (no italics).”””
t = _clean(text) or fallback
if t and t[0].islower():
t = t[0].upper() + t[1:]
return t

# —————————————————————————

# Citation builders — one function per media type

# —————————————————————————

def cite_journal_article(
authors: List[dict],
year: Optional[str],
title: Optional[str],
journal: Optional[str],
volume: Optional[str],
issue: Optional[str],
pages: Optional[str],
doi: Optional[str] = None,
url: Optional[str] = None,
) -> str:
“””
Format:
Author(s). (Year). Article title. *Journal Name*, *Volume*(issue), pages. https://doi.org/…
“””
parts = []
parts.append(_format_author_list(authors))
parts.append(_year_str(year))
parts.append(_sentence_case(title) + “.”)

```
journal_clean = _clean(journal) or "[Source unknown]"
vol = _clean(volume)
iss = _clean(issue)
pg = _clean(pages)

source = f"*{journal_clean}*"
if vol:
    source += f", *{vol}*"
    if iss:
        source += f"({iss})"
if pg:
    source += f", {pg}"
source += "."
parts.append(source)

link = _doi_url(doi, url)
if link:
    parts.append(link)

return " ".join(parts)
```

def cite_book(
authors: List[dict],
year: Optional[str],
title: Optional[str],
edition: Optional[str],
publisher: Optional[str],
doi: Optional[str] = None,
url: Optional[str] = None,
editors: Optional[List[dict]] = None,
) -> str:
“””
Format:
Author(s). (Year). *Book title* (Xth ed.). Publisher.
“””
# Prefer authors; fall back to editors
if authors:
author_str = _format_author_list(authors)
elif editors:
author_str = _format_editors(editors)
else:
author_str = “(Author unknown)”

```
parts = [author_str, _year_str(year)]

title_str = _italicize(title)
ed = _clean(edition)
if ed:
    title_str += f" ({ed} ed.)"
title_str += "."
parts.append(title_str)

pub = _clean(publisher) or "[Publisher unknown]"
parts.append(pub + ".")

link = _doi_url(doi, url)
if link:
    parts.append(link)

return " ".join(parts)
```

def cite_book_chapter(
authors: List[dict],
year: Optional[str],
chapter_title: Optional[str],
editors: List[dict],
book_title: Optional[str],
pages: Optional[str],
publisher: Optional[str],
doi: Optional[str] = None,
url: Optional[str] = None,
) -> str:
“””
Format:
Author(s). (Year). Chapter title. In Editor(s) (Ed(s).), *Book title* (pp. X–X). Publisher.
“””
parts = [_format_author_list(authors), _year_str(year)]
parts.append(_sentence_case(chapter_title) + “.”)

```
editor_str = _format_editors(editors) if editors else "(Ed. unknown) (Ed.)"
book_str = _italicize(book_title)
pg = _clean(pages)
in_str = f"In {editor_str}, {book_str}"
if pg:
    in_str += f" (pp. {pg})"
in_str += "."
parts.append(in_str)

pub = _clean(publisher) or "[Publisher unknown]"
parts.append(pub + ".")

link = _doi_url(doi, url)
if link:
    parts.append(link)

return " ".join(parts)
```

def cite_website(
authors: List[dict],
year: Optional[str],
title: Optional[str],
site_name: Optional[str],
url: Optional[str],
retrieval_date: Optional[str] = None,
) -> str:
“””
Format:
Author(s). (Year). *Page title*. Site Name. URL
Note: retrieval date only needed for content that changes over time.
“””
parts = [_format_author_list(authors), _year_str(year)]
parts.append(_italicize(title) + “.”)

```
site = _clean(site_name)
if site:
    parts.append(site + ".")

link = _clean(url)
if link:
    if retrieval_date:
        parts.append(f"Retrieved {retrieval_date}, from {link}")
    else:
        parts.append(link)
else:
    parts.append("[URL unavailable]")

return " ".join(parts)
```

def cite_newspaper(
authors: List[dict],
year: Optional[str],
month_day: Optional[str],
title: Optional[str],
newspaper: Optional[str],
url: Optional[str] = None,
) -> str:
“””
Format:
Author(s). (Year, Month Day). Article title. *Newspaper Name*. URL
“””
parts = []
author_str = _format_author_list(authors)
parts.append(author_str)

```
yr = _clean(year) or "n.d."
md = _clean(month_day)
date_str = f"({yr}, {md})." if md else f"({yr})."
parts.append(date_str)

parts.append(_sentence_case(title) + ".")

paper = _clean(newspaper) or "[Source unknown]"
parts.append(f"*{paper}*.")

link = _clean(url)
if link:
    parts.append(link)

return " ".join(parts)
```

def cite_report(
authors: List[dict],
year: Optional[str],
title: Optional[str],
report_number: Optional[str],
institution: Optional[str],
doi: Optional[str] = None,
url: Optional[str] = None,
) -> str:
“””
Format:
Author(s). (Year). *Report title* (Report No. X). Institution. URL
“””
parts = [_format_author_list(authors), _year_str(year)]

```
title_str = _italicize(title)
rn = _clean(report_number)
if rn:
    title_str += f" (Report No. {rn})"
title_str += "."
parts.append(title_str)

inst = _clean(institution) or "[Publisher unknown]"
parts.append(inst + ".")

link = _doi_url(doi, url)
if link:
    parts.append(link)

return " ".join(parts)
```

def cite_podcast_episode(
host: List[dict],
year: Optional[str],
month_day: Optional[str],
episode_title: Optional[str],
series_title: Optional[str],
producer: Optional[str],
url: Optional[str] = None,
) -> str:
“””
Format:
Host(s). (Year, Month Day). Episode title [Audio podcast episode]. In *Series*. Producer. URL
“””
parts = [_format_author_list(host)]

```
yr = _clean(year) or "n.d."
md = _clean(month_day)
date_str = f"({yr}, {md})." if md else f"({yr})."
parts.append(date_str)

ep = _sentence_case(episode_title)
parts.append(ep + " [Audio podcast episode].")

series = _clean(series_title)
if series:
    parts.append(f"In *{series}*.")

prod = _clean(producer)
if prod:
    parts.append(prod + ".")

link = _clean(url)
if link:
    parts.append(link)

return " ".join(parts)
```

def cite_video(
authors: List[dict],
year: Optional[str],
month_day: Optional[str],
title: Optional[str],
site_name: Optional[str],
url: Optional[str] = None,
) -> str:
“””
Format:
Author(s). (Year, Month Day). *Video title* [Video]. Site. URL
“””
parts = [_format_author_list(authors)]

```
yr = _clean(year) or "n.d."
md = _clean(month_day)
date_str = f"({yr}, {md})." if md else f"({yr})."
parts.append(date_str)

title_str = _italicize(title) + " [Video]."
parts.append(title_str)

site = _clean(site_name)
if site:
    parts.append(site + ".")

link = _clean(url)
if link:
    parts.append(link)

return " ".join(parts)
```

def cite_dissertation(
authors: List[dict],
year: Optional[str],
title: Optional[str],
degree_type: Optional[str],
institution: Optional[str],
database: Optional[str] = None,
url: Optional[str] = None,
) -> str:
“””
Format:
Author(s). (Year). *Title* [Doctoral dissertation/Master’s thesis, Institution]. Database. URL
“””
parts = [_format_author_list(authors), _year_str(year)]

```
degree = _clean(degree_type) or "Doctoral dissertation"
inst = _clean(institution) or "[Institution unknown]"
title_str = _italicize(title) + f" [{degree}, {inst}]."
parts.append(title_str)

db = _clean(database)
if db:
    parts.append(db + ".")

link = _clean(url)
if link:
    parts.append(link)

return " ".join(parts)
```

def cite_conference_paper(
authors: List[dict],
year: Optional[str],
month_day: Optional[str],
title: Optional[str],
conference: Optional[str],
location: Optional[str],
doi: Optional[str] = None,
url: Optional[str] = None,
) -> str:
“””
Format:
Author(s). (Year, Month Day). Title [Conference paper]. Conference Name, Location. URL
“””
parts = [_format_author_list(authors)]

```
yr = _clean(year) or "n.d."
md = _clean(month_day)
date_str = f"({yr}, {md})." if md else f"({yr})."
parts.append(date_str)

parts.append(_sentence_case(title) + " [Conference paper].")

conf = _clean(conference) or "[Conference unknown]"
loc = _clean(location)
conf_str = f"{conf}, {loc}." if loc else f"{conf}."
parts.append(conf_str)

link = _doi_url(doi, url)
if link:
    parts.append(link)

return " ".join(parts)
```

def cite_magazine_article(
authors: List[dict],
year: Optional[str],
month_day: Optional[str],
title: Optional[str],
magazine: Optional[str],
volume: Optional[str],
issue: Optional[str],
pages: Optional[str],
url: Optional[str] = None,
) -> str:
“””
Format:
Author(s). (Year, Month Day). Article title. *Magazine*, *Volume*(issue), pages.
“””
parts = [_format_author_list(authors)]

```
yr = _clean(year) or "n.d."
md = _clean(month_day)
date_str = f"({yr}, {md})." if md else f"({yr})."
parts.append(date_str)

parts.append(_sentence_case(title) + ".")

mag = _clean(magazine) or "[Source unknown]"
vol = _clean(volume)
iss = _clean(issue)
pg = _clean(pages)

source = f"*{mag}*"
if vol:
    source += f", *{vol}*"
    if iss:
        source += f"({iss})"
if pg:
    source += f", {pg}"
source += "."
parts.append(source)

link = _clean(url)
if link:
    parts.append(link)

return " ".join(parts)
```

# —————————————————————————

# Public dispatcher

# —————————————————————————

MEDIA_TYPES = {
“journal_article”: cite_journal_article,
“book”: cite_book,
“book_chapter”: cite_book_chapter,
“website”: cite_website,
“newspaper”: cite_newspaper,
“report”: cite_report,
“podcast_episode”: cite_podcast_episode,
“video”: cite_video,
“dissertation”: cite_dissertation,
“conference_paper”: cite_conference_paper,
“magazine_article”: cite_magazine_article,
}

def build_citation(media_type: str, **kwargs) -> str:
“””
Main entry point.

```
Parameters
----------
media_type : str
    One of the keys in MEDIA_TYPES.
**kwargs
    Fields appropriate to that media type.

Returns
-------
str
    Formatted APA 7th-edition citation.

Raises
------
ValueError
    If media_type is not recognised.
"""
media_type = media_type.strip().lower()
if media_type not in MEDIA_TYPES:
    raise ValueError(
        f"Unknown media type '{media_type}'. "
        f"Supported types: {', '.join(MEDIA_TYPES)}"
    )
return MEDIA_TYPES[media_type](**kwargs)
```

# —————————————————————————

# Demo / smoke-test

# —————————————————————————

if **name** == “**main**”:
print(”=” * 72)
print(“APA Citation Builder — Demo”)
print(”=” * 72)

```
examples = [
    # 1. Complete journal article
    ("journal_article", dict(
        authors=[{"last": "Smith", "first": "Jane A."}, {"last": "Doe", "first": "John B."}],
        year="2022",
        title="The effects of mindfulness on productivity",
        journal="Journal of Applied Psychology",
        volume="107",
        issue="3",
        pages="45–67",
        doi="10.1037/apl0000123",
    )),
    # 2. Journal article — missing author & volume
    ("journal_article", dict(
        authors=[],
        year="2020",
        title=None,
        journal="Nature",
        volume=None,
        issue="7834",
        pages="100",
        url="https://nature.com/articles/example",
    )),
    # 3. Complete book
    ("book", dict(
        authors=[{"last": "Brown", "first": "Brené"}],
        year="2010",
        title="The gifts of imperfection",
        edition="1st",
        publisher="Hazelden Publishing",
    )),
    # 4. Book — missing publisher & year
    ("book", dict(
        authors=[{"last": "Unknown", "first": None}],
        year=None,
        title="A guide to nothing",
        edition=None,
        publisher=None,
    )),
    # 5. Book chapter
    ("book_chapter", dict(
        authors=[{"last": "Jones", "first": "A."}],
        year="2019",
        chapter_title="Memory and learning",
        editors=[{"last": "Williams", "first": "D."}, {"last": "Clark", "first": "S."}],
        book_title="Handbook of cognitive science",
        pages="112–134",
        publisher="Springer",
        doi="10.1007/978-3-319-example",
    )),
    # 6. Website — no author, no date
    ("website", dict(
        authors=[],
        year=None,
        title="Climate change overview",
        site_name="NASA",
        url="https://climate.nasa.gov/overview",
        retrieval_date=None,
    )),
    # 7. Newspaper
    ("newspaper", dict(
        authors=[{"last": "Garcia", "first": "Maria"}],
        year="2023",
        month_day="March 15",
        title="New regulations reshape tech industry",
        newspaper="The New York Times",
        url="https://nytimes.com/example",
    )),
    # 8. Report — missing report number
    ("report", dict(
        authors=[{"last": "World Health Organization"}],
        year="2021",
        title="Global health statistics 2021",
        report_number=None,
        institution="WHO",
        url="https://www.who.int/data/gho",
    )),
    # 9. Podcast episode
    ("podcast_episode", dict(
        host=[{"last": "Rao", "first": "Priya"}],
        year="2023",
        month_day="June 4",
        episode_title="The future of remote work",
        series_title="WorkLife with Adam Grant",
        producer="TED Audio Collective",
        url="https://www.ted.com/podcasts/worklife",
    )),
    # 10. Video — missing date
    ("video", dict(
        authors=[{"last": "Kurzgesagt"}],
        year=None,
        month_day=None,
        title="Why earth is a prison and how to escape it",
        site_name="YouTube",
        url="https://youtu.be/example",
    )),
    # 11. Dissertation
    ("dissertation", dict(
        authors=[{"last": "Patel", "first": "Rohan"}],
        year="2021",
        title="Machine learning approaches to early cancer detection",
        degree_type="Doctoral dissertation",
        institution="Stanford University",
        database="ProQuest Dissertations & Theses",
    )),
    # 12. Conference paper — missing location
    ("conference_paper", dict(
        authors=[{"last": "Li", "first": "Wei"}, {"last": "Zhang", "first": "Hui"}],
        year="2022",
        month_day="September 12–15",
        title="Transformers in low-resource NLP",
        conference="Proceedings of ACL 2022",
        location=None,
        doi="10.18653/v1/example",
    )),
    # 13. Magazine article
    ("magazine_article", dict(
        authors=[{"last": "Chang", "first": "Emily"}],
        year="2023",
        month_day="April",
        title="Silicon Valley's new obsession",
        magazine="Wired",
        volume="31",
        issue="4",
        pages="54–61",
        url="https://www.wired.com/story/example",
    )),
]

for i, (media_type, kwargs) in enumerate(examples, 1):
    label = media_type.replace("_", " ").title()
    print(f"\n[{i}] {label}")
    print("-" * 68)
    citation = build_citation(media_type, **kwargs)
    print(citation)

print("\n" + "=" * 72)
print("Done.")
```
