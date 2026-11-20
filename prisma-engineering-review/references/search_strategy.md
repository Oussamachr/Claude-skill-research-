# Search Strategy Construction

## Contents
1. Building the concept table
2. Database syntax cheat-sheet
3. Worked example (engineering)
4. Testing and refining the string
5. Search log format
6. Snowballing and other methods
7. PRISMA-S reporting items

---

## 1. Building the concept table

1. Split the RQ into 2–4 **concepts**. Use PICOC elements, but not all of them. Leave out Outcome and Comparison terms from the search string, because they cut recall badly.
2. For each concept, list:
   - synonyms and near-synonyms ("digital twin", "virtual replica", "cyber-physical model")
   - acronyms ("DT", but only inside a phrase or AND-ed with context, since short acronyms are noisy)
   - spelling variants (US/UK: "optimization/optimisation", "modeling/modelling")
   - truncation (`optimi*`, `manufactur*`) and hyphenation ("data-driven" OR "data driven")
   - controlled vocabulary (Ei Thesaurus for Compendex, INSPEC terms, IEEE Terms, MeSH for biomedical)
3. OR within a concept, AND between concepts.
4. **Seed set validation.** Before running the full search, ask the user for (or find) 5–10 known relevant papers. The final string must retrieve all of them in Scopus or OpenAlex. Report this recall check in Methods. It is a strong signal of rigour.

| Concept | Terms |
|---|---|
| C1 Population | ... |
| C2 Intervention | ... |
| C3 Context | ... |

## 2. Database syntax cheat-sheet

| Database | Field code (title/abstract/keywords) | Truncation | Phrase | Proximity | Notes |
|---|---|---|---|---|---|
| Scopus | `TITLE-ABS-KEY(...)` | `*` | `"..."` (loose) or `{...}` (exact) | `W/n`, `PRE/n` | Add `AND PUBYEAR > 2013 AND (LIMIT-TO(DOCTYPE,"ar") OR LIMIT-TO(DOCTYPE,"cp")) AND (LIMIT-TO(LANGUAGE,"English"))` |
| Web of Science | `TS=(...)` | `*` | `"..."` | `NEAR/n` | Timespan and document type set in the UI or with `PY=(2014-2025)`, `DT=(Article OR Proceedings Paper)` |
| IEEE Xplore | Command search `("All Metadata":...)` or `("Abstract":...)` | `*` (min 3 chars) | `"..."` | `NEAR/n`, `ONEAR/n` | Max ~25 wildcards and 40 search terms per query; split long strings and merge the results |
| Engineering Village | `((...) WN KY)` (subject/title/abstract) | `*` | `{...}` or `"..."` | `NEAR/n`, `ONEAR/n` | Select Compendex + Inspec; use the "Autostemming off" option for precision |
| ACM DL | `Title:(...) OR Abstract:(...) OR Keyword:(...)` | `*` | `"..."` | — | Search "The ACM Guide to Computing Literature" for broader coverage |
| ScienceDirect | Title/abstract/keywords field | No wildcards | `"..."` | — | **Max 8 Boolean operators per field.** Split into several searches |
| SpringerLink | Advanced search | `*` | `"..."` | `NEAR` | Weak precision; filter by discipline |
| PubMed | `[tiab]`, `[MeSH]` | `*` | `"..."` | `"..."[tiab:~n]` | For biomedical engineering |
| OpenAlex API | `search=` (title+abstract+fulltext) or `filter=title_and_abstract.search:` | No | `"..."` inside the search | — | Boolean `AND`/`OR`/`NOT` uppercase are supported in `search`; `scripts/search.py` uses `title_and_abstract.search` |
| arXiv API | `ti:`, `abs:`, `all:` | No (stemmed) | `"..."` (URL-encoded) | — | `AND`, `OR`, `ANDNOT` |
| Crossref API | `query.bibliographic=` | No | — | — | Relevance-ranked, not Boolean. Use only as a supplement or for verification |

## 3. Worked example (engineering)

RQ: *"Which machine-learning methods are used to predict the fatigue life of additively manufactured metals, and how accurate are they?"*

Concept table:
- C1 (Population, process): additive manufactur*, "3D print*", "selective laser melting", SLM, "laser powder bed fusion", "L-PBF", "LPBF", "electron beam melting", "directed energy deposition", "wire arc additive"
- C2 (Intervention): "machine learning", "deep learning", "neural network*", "random forest", "gaussian process", "support vector", "data-driven", "physics-informed"
- C3 (Outcome-context kept because it defines the topic): fatigue

Scopus:
```
TITLE-ABS-KEY( ( "additive manufactur*" OR "3D print*" OR "selective laser melting" OR "laser powder bed fusion" OR "L-PBF" OR "LPBF" OR "electron beam melting" OR "directed energy deposition" OR "wire arc additive" )
AND ( "machine learning" OR "deep learning" OR "neural network*" OR "random forest" OR "gaussian process*" OR "support vector" OR "data-driven" OR "physics-informed" )
AND ( fatigue ) )
AND PUBYEAR > 2013 AND ( LIMIT-TO ( DOCTYPE , "ar" ) OR LIMIT-TO ( DOCTYPE , "cp" ) OR LIMIT-TO ( DOCTYPE , "re" ) ) AND ( LIMIT-TO ( LANGUAGE , "English" ) )
```

Web of Science:
```
TS=( ("additive manufactur*" OR "3D print*" OR "selective laser melting" OR "laser powder bed fusion" OR "L-PBF" OR LPBF OR "electron beam melting" OR "directed energy deposition" OR "wire arc additive")
AND ("machine learning" OR "deep learning" OR "neural network*" OR "random forest" OR "gaussian process*" OR "support vector" OR "data-driven" OR "physics-informed")
AND fatigue )
```
Refine: Publication Years 2014–2025; Document Types: Article, Proceedings Paper, Review Article; Language: English.

IEEE Xplore (command search, All Metadata):
```
(("All Metadata":"additive manufacturing" OR "All Metadata":"3D printing" OR "All Metadata":"laser powder bed fusion" OR "All Metadata":"selective laser melting") AND ("All Metadata":"machine learning" OR "All Metadata":"deep learning" OR "All Metadata":"neural network") AND ("All Metadata":fatigue))
```

OpenAlex via the script:
```
python scripts/search.py --source openalex --from-year 2014 --out 02_search/openalex.csv \
  --query '("additive manufacturing" OR "laser powder bed fusion" OR "selective laser melting" OR "3D printing") AND ("machine learning" OR "deep learning" OR "neural network" OR "data-driven") AND fatigue'
```

## 4. Testing and refining the string
- Run it, then look at the **first 50 results**. If fewer than ~30% are relevant, the string is too broad. Add a context concept or use proximity operators.
- Check seed-set recall. For each missed seed paper, find the term that would have caught it and add it.
- Target a total of a few hundred to ~3,000 records after deduplication for a feasible review. Beyond that, narrow the scope or time window, or use a scoping or mapping design.
- Record every iteration (string version, hits, reason for change) in `02_search/strings.md`. Reviewers sometimes ask how the string was developed.
- Peer review of the string (PRESS checklist, McGowan 2016). Recommend a librarian check if the user has access.

## 5. Search log format (`02_search/search_log.csv`)

```
source,date_searched,interface,query_string,filters,records_found,export_file
Scopus,2026-03-14,scopus.com advanced,"TITLE-ABS-KEY(...)","2014-2025; ar,cp,re; English",742,scopus.csv
```

`scripts/screening.py counts --search-log` reads `source` and `records_found` and lists the databases separately in the PRISMA diagram.

## 6. Snowballing and other methods
- **Backward**: screen the reference lists of the included studies.
- **Forward**: screen the papers citing the included studies (Scopus/WoS "cited by", or OpenAlex `filter=cites:W...`. Use `scripts/search.py --source openalex --cites W123456`).
- Iterate until no new includes are found (Wohlin 2014). Usually 1–2 rounds are enough.
- Other sources: expert recommendations, key-author pages, conference proceedings hand-searched, standards, patents.
- In PRISMA 2020, these go in the **right-hand "other methods" column** of the flow diagram, with their own sought, not retrieved, assessed, excluded and included counts. Give the counts to `prisma_flow.py` through `--other-methods` (see `screening.py counts -h`).

## 7. PRISMA-S reporting items (literature search extension)
Report the following: every database and platform by name, the multi-database search approach, study registries, online resources browsed, citation searching, contact with authors, other methods, the full strings for all databases, limits and restrictions, search filters used (and whether validated), prior work the strings were adapted from, updates (re-run dates), dates of search, peer review of the strings, the total records, and the deduplication method.
