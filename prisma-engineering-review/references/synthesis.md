# Evidence Synthesis for Engineering Reviews

## Contents
1. Choosing the synthesis approach
2. Structured narrative synthesis (SWiM)
3. Building a taxonomy / classification framework
4. Quantitative meta-analysis in engineering
5. Bibliometric and descriptive analysis
6. Critical analysis: turning summaries into contributions
7. Research agenda
8. Figures and tables that reviewers expect

---

## 1. Choosing the synthesis approach

| Data situation | Approach |
|---|---|
| ≥ 5 studies report the **same metric** under **comparable conditions** with variance | Random-effects meta-analysis, plus narrative |
| Same metric but no variance, or conditions differ a lot | Tabulate the ranges; vote counting by direction of effect; narrative (SWiM) |
| Heterogeneous methods and outcomes (the most common case in engineering) | Taxonomy plus structured narrative plus comparative tables |
| Broad field mapping | Classification scheme plus frequency maps (bubble plots), as in a systematic mapping study |
| Qualitative studies (practitioner interviews, case studies) | Thematic synthesis (Thomas & Harden 2008) |

State the choice and justify it in Methods (PRISMA item 13).

## 2. Structured narrative synthesis (SWiM; Campbell et al. 2020, BMJ)
Report these SWiM items:
1. How the studies were **grouped** (by method family, application, material class, evidence type), and why.
2. The **standardised metric** used to compare them (e.g., % improvement over the baseline, normalised error), and how it was transformed.
3. The **synthesis method** (for example, vote counting by direction of effect, or a summary of the range and median of effects).
4. The criteria for **prioritising** results (e.g., experimental over simulated, high-quality first).
5. How **heterogeneity** was investigated (subgroups such as scale, material, dataset).
6. How **certainty** was assessed (see GRADE in `screening_quality.md`).
7. How the data are **presented** (tables and plots).
8. A clear **summary** of the findings for each RQ.
9. **Limitations** of the synthesis.

Writing pattern for each finding:
> *Claim*, supported by k studies [refs] (evidence type and quality). *Magnitude* (range, median). *Boundary conditions* (where it holds and where it fails). *Explanation* (likely mechanism or methodological cause). *Certainty*.

## 3. Building a taxonomy / classification framework
Engineering reviewers value a well-founded taxonomy highly. It is often the paper's main conceptual contribution.
1. Start from the extracted attributes (method, input data, physics integration, output, validation level).
2. Group them inductively (open coding → axial coding), and check the result against existing taxonomies in prior reviews. Explain how yours differs or extends them.
3. Make the categories **mutually exclusive and collectively exhaustive** for at least one dimension.
4. Map every included study to the taxonomy in a table, so the taxonomy rests on evidence.
5. Present it as a tree or matrix figure (TikZ `forest` or a Mermaid sketch, then redrawn), and cross-tabulate the dimensions (method × application) as a bubble plot to show the **white spaces**, which are the research gaps.

## 4. Quantitative meta-analysis in engineering
Use it only when it is justified. Many engineering reviews are rejected for pooling incomparable numbers.
- **Effect measures:** standardised mean difference (Hedges' g) for comparisons; log response ratio `ln(X_treatment / X_control)` for ratio-scale outcomes (strength, efficiency). This is common and interpretable in materials and energy work; pooled correlation (Fisher z) for correlations; and for model accuracy, pooled error metrics only on the **same benchmark/dataset**.
- **Model:** random effects (DerSimonian–Laird or, better, REML with the Hartung–Knapp adjustment), because between-study heterogeneity is expected.
- **Heterogeneity:** report Q, I², τ², and the prediction interval. Explore it with subgroup analysis or meta-regression (on material, process, scale, test standard).
- **Dependence:** several results from one paper → use a multilevel model, or choose one per study using a pre-specified rule.
- **Publication bias (item 14/21):** funnel plot and Egger's test if k ≥ 10. Otherwise discuss it qualitatively (for example, a positive-results bias in method papers that compare against weak baselines).
- **Software:** R `metafor` is the reference implementation. Python: `statsmodels.stats.meta_analysis`. If you run the analysis, save the script and data for item 27.
- **Never** pool values extracted from graphs without saying so. If you digitised figures (WebPlotDigitizer), state it and report the digitisation uncertainty.

## 5. Bibliometric and descriptive analysis
Useful as context, but it is not the contribution. Keep it to 1–2 figures plus a table:
- Publications per year (growth trend), split by evidence type.
- Top venues and the countries or institutions involved (shows community structure).
- Keyword co-occurrence or a method-by-application matrix (`scripts/bibliometrics.py`; VOSviewer or bibliometrix for network maps).
- Keep it short. Reviewers penalise bibliometrics that replace critical synthesis.

## 6. Critical analysis: turning summaries into contributions
A PhD-level review does at least four of the following:
- **Explains disagreements.** For example, Study A reports 20% gains and Study B none. Is it a scale effect, a different test standard, a weaker baseline, or data leakage?
- **Assesses validation maturity.** What share of studies is simulation-only, lab-validated or field-validated, and how is that changing over time?
- **Examines reproducibility.** Data, code and parameter availability, and whether the claims can be checked.
- **Checks the fairness of comparisons.** Are baselines up to date? Are improvements measured on identical setups?
- **Identifies methodological anti-patterns.** For example, the same specimens used for both training and test, missing mesh-convergence studies, cherry-picked operating points.
- **Maps findings to TRL and industrial readiness**, along with standardisation gaps.
- **Proposes a framework**: a conceptual model, decision guide or design guideline that practitioners can use, derived from the evidence.
- **Quantifies trends**: method shares over time, and how performance has evolved on common benchmarks.

## 7. Research agenda
End the Discussion with a structured agenda. Each gap should be:
- **Evidence-anchored**: "Only 3 of 64 studies [refs] validated in operational conditions…"
- **Specific and actionable**: name the experiment, dataset, benchmark or method that is missing.
- **Prioritised**: short- vs. long-term, or by impact.
A table works well: Gap | Evidence | Why it matters | Suggested research direction | Related RQ.

## 8. Figures and tables that reviewers expect
1. PRISMA 2020 flow diagram (required).
2. Publications per year, by category.
3. Taxonomy figure.
4. Summary table of the included studies: Ref | Year | Method | Application or system | Data or setup | Key metric (value ± uncertainty) | Validation level | Quality score. Long tables go in the supplementary material, with a condensed version in the paper.
5. Comparative performance table or plot (only for comparable conditions).
6. Quality appraisal chart (stacked bars per item).
7. Bubble plot or heat map of method × application, showing the gaps.
8. Summary-of-findings table with certainty ratings.
9. Research agenda table.
