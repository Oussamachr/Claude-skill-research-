---
name: prisma-engineering-review
description: Run a full PRISMA 2020 systematic literature review (SLR) in any engineering field and write it up as a PhD-level manuscript ready for a journal or conference (IEEE, Elsevier, Springer, ASME, ASCE, ACM, MDPI). It covers the protocol (PICOC), Boolean search strings for Scopus, Web of Science, IEEE Xplore and Compendex, deduplication, two-stage screening with logged reasons, quality appraisal, data extraction, narrative, thematic or meta-analytic synthesis, the PRISMA flow diagram and checklist, and a LaTeX paper with checked references. Use it whenever someone asks for a literature review, state-of-the-art review, systematic review, scoping review, systematic mapping study, survey paper or review article on an engineering topic (mechanical, civil, electrical, chemical, materials, aerospace, energy, software, biomedical, industrial, environmental, robotics, AI for engineering), even when PRISMA isn't named, and when they want a review paper, thesis chapter 2, or "related work" built on a reproducible method.
---

# PRISMA Systematic Review → Engineering Manuscript

This skill turns a research topic into (1) an auditable PRISMA 2020 systematic review and (2) a manuscript a PhD-level engineering researcher would put their name on and submit. The core promise is **reproducibility and honesty**: every included study must be real and traceable, every count in the flow diagram must come from a log, and every claim in the paper must point to evidence.

## Non-negotiable integrity rules (read first)

These rules exist because a review paper with even one fabricated citation gets desk-rejected or retracted, and can end a career.

1. **Never invent a reference, DOI, author, number or result.** Cite only records you actually got from a search tool, a database export the user provided, or a DOI you checked. If you can't verify something, mark it `[VERIFY]` and say so to the user.
2. **Counts come from logs.** PRISMA numbers (identified, duplicates removed, screened, excluded with reasons, included) are computed by `scripts/screening.py` from the CSV logs, never estimated.
3. **Disclose AI assistance.** Screening or extraction done with an LLM must be described in the Methods and in an AI-use statement, and the user must be told that a human reviewer must check it (PRISMA item 8 asks how many reviewers screened each record). Most publishers (Elsevier, Springer Nature, IEEE, ACM) now require this disclosure.
4. **Be clear about scope.** If you couldn't reach full texts or a key database (Scopus and WoS need institutional access), say so. Search what you can reach, give the user the exact strings to run themselves, and take in their exports.

## Workflow overview

Work through the phases in order. Each one leaves a file in the review workspace (default `./slr-<short-topic>/`), so the review can be audited and picked up again. Tell the user which phase you're on. Check in at the gates marked ⛳: those are decisions the researcher has to own.

| Phase | Output file(s) | Reference to read |
|---|---|---|
| 0. Scoping and field adaptation ⛳ | `00_scope.md` | `references/engineering_fields.md` |
| 1. Protocol (PRISMA-P) ⛳ | `01_protocol.md` | `assets/protocol_template.md` |
| 2. Search | `02_search/` (strings, raw exports, search log) | `references/search_strategy.md` |
| 3. Deduplication | `03_records_dedup.csv` | `scripts/dedup.py` |
| 4. Screening (title/abstract, then full text) | `04_screening_ta.csv`, `05_screening_ft.csv` | `references/screening_quality.md` |
| 5. Quality / risk-of-bias appraisal | `06_quality.csv` | `references/screening_quality.md` |
| 6. Data extraction | `07_extraction.csv` | `assets/extraction_template.csv` |
| 7. Synthesis | `08_synthesis.md`, figures and tables | `references/synthesis.md` |
| 8. PRISMA diagram and checklist | `prisma_flow.svg/.tex`, `prisma_checklist.md` | `references/prisma2020_checklist.md` |
| 9. Manuscript ⛳ | `manuscript/main.tex`, `references.bib` | `references/manuscript_guide.md` |
| 10. Pre-submission audit | `10_audit.md` | checklist below |

If the user only wants part of this (say, just a search string or just the manuscript from their own extraction table), go straight to that phase, and say what upstream evidence you're assuming.

---

## Phase 0 — Scoping and field adaptation ⛳

Engineering reviews differ from medical ones. The evidence is experiments, simulations, prototypes, field deployments, benchmarks and case studies, not RCTs. Read `references/engineering_fields.md` and choose the section for the user's subfield. It tells you which databases, venues, evidence types, quality criteria and reporting conventions apply.

Pin down the following, asking only for what you can't infer:
- **Subfield and topic** (for example, "fatigue life prediction of additively manufactured Ti-6Al-4V with ML").
- **Review type.** A *systematic review* answers focused questions and appraises quality. A *scoping review* (PRISMA-ScR) maps a broad field. A *systematic mapping study* (Petersen et al., common in software engineering) classifies a field. When it's unclear, recommend one and explain why.
- **Target venue** (a journal or a conference). This sets the length (conference papers run 6–12 pages, journal reviews 8–20k words), the template and the citation style.
- **Time window, languages, publication types.** Usually the last 10–15 years, English, peer-reviewed journals plus top conferences. Grey literature (standards, patents, theses) only if it's justified.

Write the research questions with **PICOC** (Population, Intervention, Comparison, Outcome, Context; Kitchenham & Charters), which fits engineering better than PICO. Give 3–5 RQs that run from descriptive ("Which methods…?") to analytical ("How does X affect Y…?") to forward-looking ("What gaps remain…?"). A PhD-level review needs at least one RQ that **synthesises across** studies, not just one that lists them.

Before going further, check for **existing reviews** on the topic (search "review OR survey" + topic). A new review has to justify its novelty: it may be newer, cover a different scope, use a different method, or be the first systematic one. Write that justification in `00_scope.md`, because reviewers ask for it first.

## Phase 1 — Protocol ⛳

Fill in `assets/protocol_template.md`. Show the user the eligibility criteria (inclusion and exclusion, each with an ID such as `IC1`, `EC3`, because screening reasons refer to these IDs) and get their approval. Suggest registering the protocol on OSF Registries (it's free) or PROSPERO if the topic is health-related. Registration before screening is a real credibility signal.

## Phase 2 — Search

Read `references/search_strategy.md`. Then:
1. Build a **concept table**: 2–4 concept blocks, each with synonyms, acronyms, spelling variants and truncation. OR within a block, AND between blocks.
2. Translate it into each database's syntax (Scopus `TITLE-ABS-KEY`, WoS `TS=`, IEEE Xplore command search, Compendex `WN KY`, ACM, ScienceDirect's 8-operator limit). Save each string to `02_search/strings.md`.
3. **Run what you can reach:**
   - `python scripts/search.py --source openalex|crossref|arxiv|semanticscholar --query "..." --from-year 2014 --out 02_search/openalex.csv`. These sources are free with no API key, and the results are normalised to a common CSV schema.
   - If a Consensus or other scholarly-search MCP tool is available, use it as an extra source. Save its records to CSV with the same columns (`id,title,authors,year,venue,doi,abstract,source,url`).
   - For Scopus, WoS, IEEE Xplore and Compendex, give the user the exact strings and ask for exports (CSV/RIS/BibTeX). `scripts/search.py --import file.ris|file.bib|file.csv` converts them.
4. Log every search (database, date, exact string, filters, hit count) in `02_search/search_log.csv`. PRISMA item 7 requires the full strings for *all* databases, usually in a supplementary file.
5. Plan **snowballing** (backward and forward citation chasing, Wohlin 2014) on the included set. In PRISMA 2020 it's reported in the "other methods" branch of the flow diagram.

If network access is blocked, don't guess results. Say which source failed, hand over the strings, and continue once the user supplies exports.

## Phase 3 — Deduplication

`python scripts/dedup.py 02_search/*.csv --out 03_records_dedup.csv --report 03_dedup_report.json`

The script matches on normalised DOI first, then fuzzy title plus year. Look over the "possible duplicates" it flags before accepting them.

## Phase 4 — Screening

Read `references/screening_quality.md`. Two stages:
- **Title/abstract** against IC/EC. When in doubt, include: at this stage, when uncertain, move the record to full-text review.
- **Full text.** Every exclusion gets **one main reason code** (for example `EC2-not-experimental`). PRISMA reports exclusions *with reasons and counts*.

Use the CSV format in that reference (`record_id, decision, reason, reviewer, notes`). When you screen as an LLM, write `reviewer=AI` and give a one-line justification per record. Ask the user to screen at least a random 10–20% independently. Then run `python scripts/screening.py kappa 04_screening_ta.csv human_sample.csv` to get Cohen's κ (κ ≥ 0.6 is acceptable, ≥ 0.8 is strong), and report it. For large sets, screen in batches and save after each one.

If full texts aren't available, mark the record `ft_unavailable` (the "reports not retrieved" box in PRISMA) rather than screening it on the abstract alone.

## Phase 5 — Quality appraisal

Pick an instrument that suits the evidence type (`references/screening_quality.md` has engineering-specific checklists for experimental, simulation/numerical, ML/data-driven, case study and field studies, plus MMAT for mixed sets). Score every included study, report the distribution, and decide in advance whether low-quality studies are excluded or kept and analysed for sensitivity.

## Phase 6 — Data extraction

Start from `assets/extraction_template.csv` and add RQ-specific fields: materials or parameters, test conditions, models, datasets, performance metrics **with units and uncertainty**, validation method, and TRL. Extract quantitative values exactly as reported, with page or table locators, so a reviewer can trace them.

## Phase 7 — Synthesis

Read `references/synthesis.md`. Choose the approach that fits the data:
- **Quantitative meta-analysis** only when outcomes are comparable (same metric, comparable conditions, enough studies, usually ≥ 5). Use random effects, report heterogeneity (I², τ²), and add a forest plot.
- Otherwise, **structured narrative synthesis following SWiM** (Synthesis Without Meta-analysis). Group studies, tabulate them, and use vote counting by direction of effect only with its caveats stated.
- **Taxonomy or classification** of methods, the usual centrepiece of engineering reviews. Build it from the data, and show it as a figure.
- **Bibliometric descriptives**: publications per year, venues, countries, keyword co-occurrence (`python scripts/bibliometrics.py 07_extraction.csv --outdir figures/`).
- **Critical analysis**: contradictions across studies and their likely causes (test conditions, scale effects, dataset leakage, validation gaps), the reproducibility status (open data or code), and the TRL spread.

The synthesis is where a PhD-level review earns its contribution. Go **beyond summarising**: explain *why* results differ, propose a framework, and turn the gaps into a **research agenda** with specific, testable directions.

## Phase 8 — PRISMA diagram and checklist

1. `python scripts/screening.py counts --records 03_records_dedup.csv --dedup-report 03_dedup_report.json --ta 04_screening_ta.csv --ft 05_screening_ft.csv --out prisma_counts.json` (add `--search-log` for per-database counts and `--other-methods` for snowballing).
2. `python scripts/prisma_flow.py prisma_counts.json --out prisma_flow` writes the PRISMA 2020 flow diagram as `.svg` and as TikZ `.tex` for LaTeX.
3. Fill in `references/prisma2020_checklist.md` (27 items plus the 12-item abstract checklist) with the manuscript section or page where each item is reported. Journals often require it as a supplementary file.

## Phase 9 — Manuscript ⛳

Read `references/manuscript_guide.md`, which has section-by-section guidance, PhD-level quality markers, venue formats and the reasons reviews get rejected. Use `assets/latex/main.tex` (a generic article with an SLR structure) and swap in the venue class (`IEEEtran`, `elsarticle`, `sn-jnl`, `asme2ej`, `acmart`) as the guide explains.

Write in clear, precise academic English. Be quantitative where the evidence allows ("RMSE dropped by 12–38% across 9 studies"). Hedge in proportion to the strength of the evidence, use consistent terminology and SI units, and don't oversell. Every paragraph in Results and Discussion should rest on cited included studies.

Bibliography: build `references.bib` **only** from the records you processed (`python scripts/search.py --to-bibtex 07_extraction.csv --out manuscript/references.bib`). Then run `python scripts/verify_refs.py manuscript/references.bib`, which checks DOIs against Crossref and flags title mismatches. If it can't reach the network, say so and list the entries that remain unverified.

Hand the user a manuscript draft that is complete but clearly marked: `[AUTHOR INPUT]` for affiliations, funding and author contributions (CRediT), and `[VERIFY]` for anything uncertain.

## Phase 10 — Pre-submission audit

Write `10_audit.md` and confirm each of these:
- [ ] Every PRISMA 2020 item is reported or marked N/A with a reason.
- [ ] Flow-diagram numbers add up (identified − duplicates − automation removals = screened; screened − excluded = sought; and so on). `prisma_flow.py` checks this.
- [ ] Every citation key in `main.tex` exists in `references.bib`, and every included study is cited at least once (in the summary table if not in the text).
- [ ] Search strings for every database, the extraction sheet, and the quality scores are in the supplementary material or in an OSF/Zenodo repository (PRISMA item 27).
- [ ] The novelty statement compares this review against existing reviews explicitly.
- [ ] Limitations cover the databases searched, language, time window, single or AI-assisted screening, and publication bias.
- [ ] AI-use disclosure, data availability, competing interests and funding statements are present.
- [ ] Length, abstract word limit, keywords, highlights (Elsevier) and graphical abstract all match the venue's guide for authors.

Finally, give the user a short summary: the review type, databases, counts, the main findings, and what *they* still have to do (human screening check, institutional database exports, author details, journal-specific formatting).

## Scripts at a glance (Python 3 standard library only, no installs)

| Script | Purpose |
|---|---|
| `scripts/search.py` | Query OpenAlex, Crossref, arXiv or Semantic Scholar; import RIS/BibTeX/CSV exports; export BibTeX |
| `scripts/dedup.py` | DOI and fuzzy-title deduplication, with a report |
| `scripts/screening.py` | `counts` (PRISMA numbers from logs), `kappa` (inter-rater agreement), `sample` (random audit sample) |
| `scripts/prisma_flow.py` | PRISMA 2020 flow diagram → SVG and TikZ, with arithmetic checks |
| `scripts/bibliometrics.py` | Year, venue and keyword statistics → CSV and SVG bar charts |
| `scripts/verify_refs.py` | Check BibTeX DOIs against Crossref and flag mismatches |

Run any script with `-h` for options.
