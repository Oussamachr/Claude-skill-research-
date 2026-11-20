# Screening and Quality Appraisal

## Contents
1. Screening workflow and CSV formats
2. Writing good eligibility criteria
3. AI-assisted screening protocol (honest and auditable)
4. Inter-rater agreement
5. Quality appraisal instruments for engineering evidence
6. Certainty of evidence (adapted GRADE)

---

## 1. Screening workflow and CSV formats

### Title/abstract log (`04_screening_ta.csv`)
```
record_id,decision,reason,reviewer,notes
R0001,include,,AI,"Proposes CNN for SLM fatigue life; experimental data"
R0002,exclude,EC1-off-topic,AI,"About polymer FDM tensile strength, not fatigue"
R0003,maybe,,AI,"Abstract unclear whether ML used"
```
- `decision ∈ {include, exclude, maybe}`. `maybe` goes forward to full text, and `screening.py` counts it as passing.
- `reason` is required for `exclude`, and must be an EC code from the protocol.
- `record_id` must match `id` in `03_records_dedup.csv`.

### Full-text log (`05_screening_ft.csv`)
```
record_id,decision,reason,reviewer,notes
R0001,include,,AI+HUMAN,"Meets IC1-IC4"
R0007,exclude,EC3-simulation-only,AI,"No experimental validation"
R0011,not_retrieved,,AI,"Paywalled; requested via ILL"
```
- `decision ∈ {include, exclude, not_retrieved}`
- Exclusion reasons are summarised automatically, with counts, for the PRISMA diagram ("Reports excluded: EC3 simulation only (n = 14) …").

### Procedure
1. Pilot: screen the same 20–50 records with the user. Calibrate the criteria wording until the decisions agree, and record the calibration in the protocol.
2. Title/abstract stage: be inclusive. Exclude only when a criterion is clearly violated.
3. Full-text stage: apply every criterion. Record **one primary reason** per exclusion, ordered by the EC list (the first one that applies), so the counts stay unambiguous.
4. Resolve disagreements by discussion or a third reviewer, and record how.

## 2. Writing good eligibility criteria
Criteria must be **operational** (two people would apply them the same way) and must map to PICOC plus study design and publication filters.

Example set (AM fatigue + ML):
- IC1: Studies metallic parts produced by an additive-manufacturing process.
- IC2: Applies a data-driven or ML model to predict fatigue life, fatigue strength or crack growth.
- IC3: Reports quantitative predictive performance (e.g., R², RMSE, scatter band).
- IC4: Peer-reviewed journal article or full conference paper, in English, 2014–2025.
- EC1: Off-topic (not AM metals, or not fatigue).
- EC2: No ML or data-driven model (purely physics-based or empirical curve fits).
- EC3: No quantitative evaluation of predictive performance.
- EC4: Review, editorial, abstract-only, thesis, book chapter (reviews are mined for snowballing).
- EC5: Duplicate publication of the same dataset/model (keep the most complete version, link companions).
- EC6: Full text not in English.

## 3. AI-assisted screening protocol (honest and auditable)
When you (the LLM) screen:
- Read the title and abstract (and keywords). Decide against each IC/EC explicitly, and write a 1-line justification in `notes`.
- Be **conservative toward inclusion** at the title/abstract stage. A false exclusion is unrecoverable, while a false inclusion only costs a full-text read.
- Work in batches of 25–50 and save the CSV after each batch, so progress survives interruptions.
- Never mark a full-text decision without having the full text. If you only have the abstract, use `not_retrieved` or ask the user for the PDF.
- Generate an audit sample: `python scripts/screening.py sample 04_screening_ta.csv --frac 0.2 --seed 42 --out human_check.csv`. Ask the user to fill in their own `decision` column blind, then compute κ.
- In the Methods, report something like: *"Title/abstract screening was performed by one reviewer assisted by a large language model (model, version, date), with the prompt provided in Supplementary S2. A second reviewer independently screened a random 20% sample (n = …); agreement was κ = …. All full-text decisions were verified by a human reviewer."* Fill in the values from the run. Never report a κ that was not computed.

## 4. Inter-rater agreement
`python scripts/screening.py kappa rater1.csv rater2.csv` joins on `record_id`, treats `maybe` as `include`, and reports the percentage agreement, Cohen's κ and the 2×2 table.

Interpretation (Landis & Koch 1977): < 0.20 slight; 0.21–0.40 fair; 0.41–0.60 moderate; 0.61–0.80 substantial; 0.81–1.00 almost perfect. If κ < 0.6, refine the criteria and re-screen the pilot set.

## 5. Quality appraisal instruments for engineering evidence

Score each item **Yes = 1 / Partly = 0.5 / No = 0**. Report the per-item distribution (stacked bar chart) and the total. Pre-define the thresholds in the protocol (e.g., high ≥ 75%, medium 50–75%, low < 50%). Store the scores in `06_quality.csv` with one column per item, plus a short justification for each "Partly" or "No".

### 5.1 Generic engineering study checklist (QA-ENG, adapted from Kitchenham & Charters 2007, Dybå & Dingsøyr 2008)
| # | Item |
|---|---|
| Q1 | Are the aims and research question clearly stated? |
| Q2 | Is the method/system described in enough detail to be reproduced? |
| Q3 | Is the experimental/simulation setup (conditions, parameters, equipment, software versions) fully reported? |
| Q4 | Is the method validated against independent data, experiments or an accepted benchmark? |
| Q5 | Is it compared against appropriate, recent baselines or the state of the art? |
| Q6 | Are uncertainty, variability or statistical significance reported (replicates, CI, multiple runs)? |
| Q7 | Are the limitations and threats to validity discussed? |
| Q8 | Are data, code or models available (or the reason they aren't stated)? |
| Q9 | Are the conclusions supported by the results presented? |

### 5.2 Add-on items by evidence type
**Experimental (lab/field):** sample size justified; standard test method (ASTM/ISO) followed; measurement uncertainty and instrument calibration reported; specimens' manufacturing history reported.

**Numerical simulation (FEA/CFD/system models):** mesh/grid-convergence or time-step independence shown; boundary conditions and material models justified; verification (code) and validation (physics, against experiment) separated (ASME V&V 10/20); solver and version stated.

**ML / data-driven:** dataset source, size and split described; no train/test leakage (e.g., same specimen or batch in both); hyper-parameter tuning on validation data only; multiple seeds or CV with variance; ablation or feature importance; external test set or out-of-distribution evaluation; compute reported.

**Optimisation / OR:** benchmark instances public; compared against best-known solutions; parameter tuning procedure stated; runtime and hardware reported; statistical tests over multiple runs (metaheuristics).

**Case study / industrial deployment:** context described (company, scale); data collection method; triangulation of sources; duration; generalisability discussed (Runeson & Höst 2009 for SE).

**Mixed sets:** use **MMAT 2018** (Hong et al.) when qualitative, quantitative and mixed-methods studies are combined.

**Clinical/biomedical with human subjects:** RoB 2 (randomised), ROBINS-I (non-randomised), QUADAS-2 (diagnostic accuracy).

### 5.3 Using quality in synthesis
- Report the quality distribution in a figure or table.
- Run a sensitivity analysis: do the conclusions change if low-quality studies are removed?
- Give each finding a weight in the narrative ("supported by 7 high-quality experimental studies" vs. "suggested by 3 simulation-only studies").

## 6. Certainty of evidence (adapted GRADE, for PRISMA item 15 and item 22)
For each key finding, rate certainty as **High / Moderate / Low / Very low**. Start at High for consistent, experimentally validated evidence from several independent groups, and downgrade for:
- **Risk of bias**: most of the contributing studies are low quality.
- **Inconsistency**: the results conflict without explanation.
- **Indirectness**: simulation only, lab scale only, or conditions far from the application (low TRL).
- **Imprecision**: few studies or small samples.
- **Publication bias**: only positive results, or most of the evidence from one group.

Present a "Summary of findings" table: finding | k studies | evidence type | certainty | rationale.
