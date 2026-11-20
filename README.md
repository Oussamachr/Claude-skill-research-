# Claude skill: PRISMA systematic review → engineering manuscript

`prisma-engineering-review/` is a Claude skill. It carries out a **PRISMA 2020 systematic literature review** in any engineering field and writes it up as a **manuscript ready to submit to a journal or conference**.

## What it does
1. **Scoping**: PICOC research questions, a check for existing reviews, the choice of review type (systematic, scoping or mapping), adapted to the subfield (12 engineering profiles).
2. **Protocol** (PRISMA-P) with eligibility criteria that have IDs, ready to register on OSF.
3. **Search**: database-specific Boolean strings (Scopus, WoS, IEEE Xplore, Compendex, ACM, ScienceDirect), live searches of OpenAlex, Crossref, arXiv and Semantic Scholar, and import of Scopus, WoS and IEEE exports.
4. **Deduplication**, **two-stage screening** with logged reason codes, and an inter-rater **Cohen's κ**.
5. **Quality appraisal** with engineering checklists (experimental, simulation, ML, optimisation, case study) and adapted GRADE.
6. **Data extraction** template and **synthesis**: taxonomy, SWiM narrative, or meta-analysis when it's justified.
7. **PRISMA 2020 flow diagram** (SVG + TikZ) generated from the logs, with arithmetic checks, and the 27-item checklist.
8. **LaTeX manuscript** (IEEE, Elsevier, Springer, ASME, ACM or MDPI), BibTeX built only from records actually retrieved, and **reference verification** against Crossref.
9. **Pre-submission audit.**

It keeps the work honest: it never fabricates references, takes every number in the flow diagram from the logs, and discloses AI-assisted screening.

## Install
- **Claude Code**: copy `prisma-engineering-review/` to `~/.claude/skills/` (personal) or `.claude/skills/` (project).
- **Claude.ai**: upload `prisma-engineering-review.skill` under Settings → Capabilities → Skills.

## Scripts (Python 3 standard library only)
| Script | Purpose |
|---|---|
| `search.py` | API search, import of database exports, BibTeX export |
| `dedup.py` | DOI and fuzzy-title deduplication |
| `screening.py` | PRISMA counts, Cohen's κ, audit samples |
| `prisma_flow.py` | PRISMA 2020 flow diagram (SVG + TikZ) |
| `bibliometrics.py` | Charts of publications per year, venues and keywords |
| `verify_refs.py` | Crossref DOI and title check, cite-key consistency |

Example prompt: *"Do a PRISMA systematic review on machine-learning fatigue-life prediction for additively manufactured metals and write it as a review paper for the International Journal of Fatigue."*
