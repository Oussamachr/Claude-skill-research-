# PRISMA 2020 Checklist (Page et al., BMJ 2021;372:n71), annotated for engineering

Copy this file into the workspace as `prisma_checklist.md` and fill in the **Location** column with the section, page or supplementary file where each item is reported. Mark an item N/A only when you can say why it doesn't apply (e.g., item 12 effect measures when there is no meta-analysis is *not* N/A: state the outcome metrics used instead).

## Main checklist

| Section | # | Item | Engineering note | Location |
|---|---|---|---|---|
| **TITLE** | 1 | Identify the report as a systematic review. | E.g., "… : A Systematic Review" / "… : A PRISMA-Guided Systematic Literature Review". | |
| **ABSTRACT** | 2 | See the PRISMA 2020 for Abstracts checklist (below). | Conference abstracts are short; prioritise items A1–A8. | |
| **INTRODUCTION** Rationale | 3 | Describe the rationale for the review in the context of existing knowledge. | Include an explicit comparison with existing reviews (a novelty table). | |
| Objectives | 4 | Provide an explicit statement of the objective(s) or question(s) the review addresses. | RQs in PICOC form. | |
| **METHODS** Eligibility criteria | 5 | Specify the inclusion and exclusion criteria and how studies were grouped for the syntheses. | IC/EC table with IDs. | |
| Information sources | 6 | Specify all databases, registers, websites, organisations, reference lists and other sources searched or consulted, with the date each was last searched. | Scopus, WoS, IEEE Xplore, Compendex…, with dates. | |
| Search strategy | 7 | Present the full search strategies for all databases, registers and websites, including any filters and limits used. | Full strings in a supplementary file; the main string in the text. | |
| Selection process | 8 | Methods used to decide inclusion: how many reviewers screened each record and each report, whether they worked independently, and any automation tools used. | **Disclose LLM assistance** and the human-verification sample with κ. | |
| Data collection process | 9 | Methods used to collect data from reports: how many reviewers, whether independent, processes for confirming data, automation tools. | Mention figure digitisation if used. | |
| Data items | 10a | List and define all outcomes for which data were sought, and whether all compatible results were sought. | Performance metrics with units. | |
| | 10b | List and define all other variables for which data were sought (e.g., participant and intervention characteristics, funding sources) and any assumptions about missing or unclear information. | Material, process, dataset, TRL, etc. | |
| Study risk of bias assessment | 11 | Methods used to assess risk of bias in the included studies: the tool(s), how many reviewers, whether independent. | QA-ENG checklist plus add-ons (`screening_quality.md`). | |
| Effect measures | 12 | For each outcome, specify the effect measure(s) (e.g., risk ratio, mean difference) used. | E.g., % improvement over baseline, RMSE, log response ratio. | |
| Synthesis methods | 13a | Processes used to decide which studies were eligible for each synthesis. | | |
| | 13b | Methods needed to prepare the data for presentation or synthesis (missing statistics, data conversions). | Unit conversions, normalisation. | |
| | 13c | Methods used to tabulate or visually display results of individual studies and syntheses. | | |
| | 13d | Methods used to synthesise results and the rationale; if meta-analysis, the model(s), method(s) to identify heterogeneity, and software. | SWiM or meta-analysis. | |
| | 13e | Methods used to explore possible causes of heterogeneity (subgroup analysis, meta-regression). | | |
| | 13f | Sensitivity analyses conducted to assess robustness of the synthesised results. | E.g., excluding low-quality or simulation-only studies. | |
| Reporting bias assessment | 14 | Methods used to assess the risk of bias due to missing results in a synthesis (reporting biases). | Funnel or Egger if k ≥ 10; otherwise a qualitative assessment. | |
| Certainty assessment | 15 | Methods used to assess certainty (or confidence) in the body of evidence for an outcome. | Adapted GRADE. | |
| **RESULTS** Study selection | 16a | Results of the search and selection, from the number of records identified to the number included, ideally with a flow diagram. | `prisma_flow.svg`. | |
| | 16b | Cite studies that might appear to meet the inclusion criteria but were excluded, and explain why. | A short table of "near-miss" exclusions. | |
| Study characteristics | 17 | Cite each included study and present its characteristics. | Summary table. | |
| Risk of bias in studies | 18 | Present assessments of risk of bias for each included study. | Quality chart plus a per-study table (supplementary). | |
| Results of individual studies | 19 | For all outcomes, present for each study: (a) summary statistics for each group (where appropriate) and (b) an effect estimate and its precision, ideally in structured tables or plots. | | |
| Results of syntheses | 20a | For each synthesis, briefly summarise the characteristics and risk of bias of the contributing studies. | | |
| | 20b | Present results of all statistical syntheses conducted (summary estimate, precision, heterogeneity). If comparing groups, describe the direction of the effect. | | |
| | 20c | Present results of all investigations of possible causes of heterogeneity. | | |
| | 20d | Present results of all sensitivity analyses. | | |
| Reporting biases | 21 | Present assessments of the risk of bias due to missing results for each synthesis. | | |
| Certainty of evidence | 22 | Present assessments of certainty (or confidence) in the body of evidence for each outcome. | Summary-of-findings table. | |
| **DISCUSSION** | 23a | Provide a general interpretation of the results in the context of other evidence. | | |
| | 23b | Discuss any limitations of the evidence included in the review. | | |
| | 23c | Discuss any limitations of the review processes used. | Databases, language, AI-assisted screening. | |
| | 23d | Discuss implications of the results for practice, policy and future research. | Industrial implications plus the research agenda. | |
| **OTHER INFORMATION** Registration and protocol | 24a | Provide registration information (register name and number) or state that the review was not registered. | OSF DOI. | |
| | 24b | Indicate where the protocol can be accessed, or state that no protocol was prepared. | | |
| | 24c | Describe and explain any amendments to information provided at registration or in the protocol. | | |
| Support | 25 | Describe sources of financial or non-financial support and the role of the funders or sponsors. | | |
| Competing interests | 26 | Declare any competing interests of the review authors. | | |
| Availability of data, code and other materials | 27 | Report which of the following are publicly available and where: template data collection forms; data extracted from included studies; data used for all analyses; analytic code; any other materials. | Zenodo/OSF/GitHub DOI for the workspace CSVs and scripts. | |

## PRISMA 2020 for Abstracts

| # | Section | Item |
|---|---|---|
| A1 | Title | Identify the report as a systematic review. |
| A2 | Objectives | An explicit statement of the main objective(s) or question(s). |
| A3 | Eligibility criteria | Inclusion and exclusion criteria. |
| A4 | Information sources | Information sources (databases, registers) and the date each was last searched. |
| A5 | Risk of bias | Methods used to assess risk of bias in the included studies. |
| A6 | Synthesis of results | Methods used to present and synthesise results. |
| A7 | Included studies | Total number of included studies and participants, and relevant characteristics. |
| A8 | Synthesis of results | Results for the main outcomes, preferably indicating the number of included studies for each; if meta-analysis, the summary estimate and CI. |
| A9 | Limitations of evidence | Brief summary of the limitations of the evidence (e.g., risk of bias, inconsistency, imprecision). |
| A10 | Interpretation | General interpretation of the results and important implications. |
| A11 | Funding | Primary source of funding. |
| A12 | Registration | Register name and registration number. |

Engineering journals often cap abstracts at 150–250 words. Fit A1–A10 into one structured paragraph, and put A11–A12 in the declarations if the venue disallows them in the abstract.

## Related extensions to cite when applicable
- PRISMA-S (search reporting): Rethlefsen et al., *Syst. Rev.* 2021;10:39.
- PRISMA-ScR (scoping reviews): Tricco et al., *Ann. Intern. Med.* 2018;169:467–473.
- PRISMA-P (protocols): Moher et al., *Syst. Rev.* 2015;4:1.
- SWiM (synthesis without meta-analysis): Campbell et al., *BMJ* 2020;368:l6890.
- Kitchenham & Charters, *Guidelines for performing Systematic Literature Reviews in Software Engineering*, EBSE Technical Report EBSE-2007-01, 2007.
- Petersen, Vakkalanka & Kuzniarz, "Guidelines for conducting systematic mapping studies in software engineering: An update", *Inf. Softw. Technol.* 2015;64:1–18.
- Wohlin, "Guidelines for snowballing in systematic literature studies…", *EASE* 2014.

Verify these citations' DOIs with `scripts/verify_refs.py` before using them, as with any other reference.
