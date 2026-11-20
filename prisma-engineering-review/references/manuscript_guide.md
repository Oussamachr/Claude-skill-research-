# Writing the Review Manuscript (PhD / Journal Standard)

## Contents
1. What makes a review publishable
2. Venue formats and templates
3. Section-by-section guidance
4. Style and language standards
5. Citations and bibliography
6. Common rejection reasons and how to pre-empt them
7. Cover letter and submission package

---

## 1. What makes a review publishable
Editors of engineering journals reject most submitted reviews. The ones that get through usually have:
1. **A clear gap in existing reviews**, shown with a comparison table (prior review | year | scope | method | databases | number of studies | what this review adds).
2. **A transparent, reproducible method** (PRISMA 2020, registered protocol, full strings, open data).
3. **A conceptual contribution**: a taxonomy, framework, design guideline or decision model, not just a catalogue.
4. **Critical depth**: explanations of contradictions and appraisal of validation and reproducibility (see `synthesis.md` §6).
5. **A concrete, evidence-anchored research agenda.**
6. **Currency**: the search was run less than 6–12 months before submission. Re-run it if the review took longer.

## 2. Venue formats and templates

| Publisher / venue | LaTeX class | Citation style | Typical review length | Notes |
|---|---|---|---|---|
| IEEE Transactions / Access | `IEEEtran` (`\documentclass[journal]{IEEEtran}`) | Numeric `[1]`, `IEEEtran.bst` | 10–20 pages two-column (Access: no limit, but concise) | Author biographies with photos in Trans. IEEE Access APC. |
| IEEE conferences | `IEEEtran` (`[conference]`) | Numeric | 6–8 pages (+refs at some venues) | Strongly compress Methods; full strings in an arXiv/OSF supplement |
| Elsevier journals | `elsarticle` (`[preprint,12pt]` for review) | Numeric (`elsarticle-num`) or author–year (`elsarticle-harv`) per journal | 8,000–15,000 words | Highlights (3–5 bullets, ≤85 chars each), graphical abstract, CRediT statement, AI declaration |
| Springer Nature | `sn-jnl` (`[sn-mathphys-num]`, etc.) | Per journal | 8,000–12,000 words | Declarations section mandatory |
| ASME journals | `asmejour` | Numeric (ASME style) | ~10–12 pages | Nomenclature list common |
| ASCE journals | `ascelike-new` | Author–year | ≤10,000 words, a "Data Availability Statement" required | Practical applications section |
| ACM (CSUR, TOSEM) | `acmart` (`[acmsmall]`) | Author–year or numeric | CSUR: ~35 pages | CCS concepts required |
| MDPI | MDPI LaTeX template (`Definitions/mdpi.cls`) | Numeric (ACS-like) | No strict limit | PRISMA checklist + flow diagram must be uploaded for systematic reviews |

`assets/latex/main.tex` uses `article` so it compiles anywhere. To switch: replace the `\documentclass` line, the author/affiliation block and the bibliography style as listed in the comments at the top of that file. Always check the journal's current Guide for Authors, because word limits and templates change.

## 3. Section-by-section guidance

### Title (PRISMA 1)
`<Topic>: A Systematic Review [of <scope>] [and Research Agenda]`, or `… : A PRISMA-Guided Systematic Literature Review`. Keep it ≤ 20 words. Name the core concepts (they're the search terms readers will use). Avoid "comprehensive" or "a survey on recent advances" unless the venue requires it.

### Abstract (PRISMA 2, A1–A12)
Usually one paragraph of 150–250 words, ordered **context → gap → objective → method (databases, dates, criteria, N screened, N included, appraisal) → key results (quantitative where possible) → implications → agenda**. No citations. Elsevier also asks for highlights.

### Keywords
5–7 keywords, none repeating the title verbatim. Include "systematic literature review" or "PRISMA".

### 1. Introduction (PRISMA 3–4) — ~10% of the length
1. Engineering context and why it matters, with quantified stakes (market size, energy share, failure costs) and citations.
2. Technical background, kept brief (or a separate Section 2 "Background and fundamentals" for a journal).
3. **Existing reviews and their limits**: the comparison table goes here.
4. Objectives and RQs (RQ1–RQn) with their motivation.
5. Contributions (bulleted, 3–5, specific).
6. Paper organisation (one sentence).

### 2. Background / Fundamentals (optional, journals)
Definitions and core concepts the reader needs to follow the synthesis, kept short. This is **not** the results section.

### 3. Methodology (PRISMA 5–15) — ~15% of the length
Subsections: 3.1 Protocol and registration; 3.2 Research questions (PICOC table); 3.3 Eligibility criteria (IC/EC table); 3.4 Information sources and search strategy (string plus database table with dates and hits); 3.5 Selection process (stages, reviewers, AI assistance, κ); 3.6 Data extraction (form fields, digitisation); 3.7 Quality assessment (instrument, scoring, thresholds); 3.8 Synthesis methods (SWiM or meta-analysis, grouping, heterogeneity, sensitivity, certainty).
Write it in the past tense, with enough detail that someone else could repeat the review.

### 4. Results (PRISMA 16–22) — ~40%
- 4.1 Study selection (flow diagram figure, near-miss exclusions).
- 4.2 Characteristics of the included studies (bibliometric figure, summary table).
- 4.3 Quality assessment results.
- 4.4–4.x **one subsection per RQ.** Organise them by your taxonomy, not paper by paper. Avoid "Smith et al. did X. Jones et al. did Y." Instead synthesise: "Three families of approach emerge… Physics-informed models (k = 14) consistently outperformed purely data-driven ones under extrapolation [refs], while…"
- Summary-of-findings table with certainty ratings.

### 5. Discussion (PRISMA 23) — ~25%
- 5.1 Principal findings, answering each RQ directly.
- 5.2 Interpretation against prior reviews and theory: agreements and disagreements.
- 5.3 Proposed framework or guideline (the conceptual contribution).
- 5.4 Implications for practice or industry (TRL, standards, design rules).
- 5.5 Research agenda (a table).
- 5.6 Limitations: of the evidence (23b) and of the review process (23c). Cover database coverage, language, time window, publication bias, AI-assisted screening, single-reviewer extraction, and the heterogeneity that prevented a meta-analysis.
- Threats to validity (SE convention): construct, internal, external, conclusion.

### 6. Conclusions — ~5%
A short paragraph per RQ answer, then the main contribution, the top 3 research priorities, and the next steps. No new information and no citations.

### Back matter (mandatory for most venues)
- CRediT author contributions `[AUTHOR INPUT]`
- Funding `[AUTHOR INPUT]`
- Declaration of competing interests
- **Declaration of generative AI use**. Elsevier's wording pattern: *"During the preparation of this work the author(s) used [tool] in order to [screening assistance / language editing / …]. After using this tool, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the publication."*
- Data availability (OSF/Zenodo link to the search strings, logs, extraction sheet, scripts)
- Supplementary material list (S1 PRISMA checklist, S2 search strings, S3 screening logs, S4 extraction table, S5 quality scores)

## 4. Style and language standards
- **Precise, quantitative claims**: "reduced RMSE by 12–38% (median 21%, k = 9)" rather than "significantly improved accuracy". Reserve "significant" for statistical significance.
- **Hedging proportional to the evidence**: "consistently shows" (high certainty), "suggests" (moderate), "limited evidence indicates" (low).
- **Attribute every factual claim** to included studies, or to background references for context.
- **Consistent terminology**: define each acronym at first use in the abstract and again in the body, keep a nomenclature table for long papers, and use one term per concept throughout.
- SI units, and a space between the number and the unit (`200 MPa`; use `siunitx` in LaTeX).
- Past tense for methods and results, present tense for established knowledge and for the paper's own claims.
- Paragraphs of 4–8 sentences, each opening with a topic sentence. Avoid bullet lists in the body text except for contributions.
- Avoid filler ("In recent years, … has attracted significant attention"), promotional adjectives ("novel", "groundbreaking"), and unsupported superlatives.
- Figures are vector (PDF/SVG), readable in greyscale and by colour-blind readers, and every one is referenced in the text. Tables use `booktabs`.
- Write the way a careful human expert writes: vary sentence length, take a clear position where the evidence supports one, and acknowledge nuance specifically rather than with generic caveats.

## 5. Citations and bibliography
- Every included study has to appear in the paper (at least in the summary table). Use `\cite{}` keys from `references.bib`.
- Generate the BibTeX entries from the processed records (`scripts/search.py --to-bibtex`) and add any background references only after verifying their DOIs.
- Run `scripts/verify_refs.py`. Fix or remove any entry it flags. **Never** fill in missing metadata from memory.
- Methodology citations to include: Page et al. 2021 (PRISMA 2020), plus Kitchenham & Charters 2007 / Petersen 2015 / Wohlin 2014 / Campbell 2020 (SWiM) as applicable.
- Avoid citation padding and self-citation clusters. Editors check for both.

## 6. Common rejection reasons and how to pre-empt them

| Rejection reason | Pre-emption |
|---|---|
| "Another review on X, no novelty" | Novelty comparison table plus a distinctive RQ or framework |
| "Descriptive, lacks critical analysis" | Explain contradictions, validation maturity, reproducibility; propose a framework |
| "Methodology not reproducible" | Full strings, dates, counts, logs, registered protocol, PRISMA checklist |
| "Search is outdated" | Re-run the search before submission and report the update date |
| "Database coverage too narrow" | At least Scopus + WoS + a subject database, or a justified limitation |
| "Quality of included studies not considered" | Appraisal plus a sensitivity analysis |
| "Pooled incomparable results" | Meta-analysis only on comparable data; otherwise SWiM |
| "Figures/tables just list papers" | Synthesis tables that group by taxonomy with metrics |
| "Out of scope for journal" | Check the aims and scope, cite the journal's own recent papers where relevant, tailor the framing |
| "Language/clarity" | Edit for concision and terminology consistency |

## 7. Cover letter and submission package
Cover letter (≤ 1 page): the title and article type (Review), why the topic matters to *this* journal's readers, the novelty versus existing reviews, the method in one sentence (PRISMA 2020, N studies, databases), the key contribution, a statement that the paper is not under consideration elsewhere, and optionally suggested reviewers `[AUTHOR INPUT]`.

Package checklist: main manuscript (PDF + source), PRISMA checklist (S1), flow diagram as a separate high-resolution file if requested, supplementary files, highlights, graphical abstract, cover letter, declarations, ORCID iDs, and the OSF/Zenodo DOI.
