# Adapting the Review to an Engineering Subfield

## Contents
1. Why engineering is different from medicine
2. Universal engineering databases
3. Subfield profiles (databases · evidence types · quality concerns · venues · conventions)
   - 3.1 Mechanical & manufacturing
   - 3.2 Civil, structural & geotechnical
   - 3.3 Electrical, electronic & power/energy systems
   - 3.4 Computer, software & AI/ML engineering
   - 3.5 Chemical & process engineering
   - 3.6 Materials science & engineering
   - 3.7 Aerospace & automotive
   - 3.8 Biomedical engineering
   - 3.9 Environmental, water & sustainability engineering
   - 3.10 Industrial engineering, operations & systems engineering
   - 3.11 Robotics, control & mechatronics
   - 3.12 Telecommunications & networking
4. Review-type guidance per field
5. Field-specific reporting conventions

---

## 1. Why engineering is different from medicine

PRISMA was built for health research, where the RCT is the strongest evidence. Engineering evidence is more varied, so the review has to adapt:

| Medical concept | Engineering adaptation |
|---|---|
| PICO | **PICOC**: Population (system, material, structure, dataset), Intervention (method, design, technique), Comparison (baseline, state of the art, standard), Outcome (performance metrics), Context (scale, environment, application domain) |
| RCT / cohort | Controlled lab experiment, numerical simulation, prototype, field deployment, benchmark study, industrial case study |
| Risk-of-bias tools (RoB 2, ROBINS-I) | Engineering quality checklists (see `screening_quality.md`): validation, uncertainty quantification, reproducibility, baseline fairness, data leakage |
| Effect size (OR, RR) | Domain metrics: % improvement, RMSE/MAE, efficiency, fatigue life cycles, strength (MPa), cost (USD/kWh), accuracy/F1, latency |
| GRADE certainty | Adapted certainty: consistency, number of independent groups, TRL, experimental vs simulated evidence, scale |
| Clinical relevance | Practical relevance: TRL, scalability, cost, standards compliance, industrial uptake |

**Conferences matter.** In computer science, EE and robotics, top conference papers (NeurIPS, ICRA, DAC, ISSCC, CVPR) are primary, peer-reviewed literature. Include them where the field treats them that way.

**Standards and patents** (ISO, IEC, ASTM, IEEE Std, Eurocodes, ASME BPVC; Espacenet, Google Patents) are often essential grey literature for applied topics. Include them only if the protocol says so, and report them in the "other methods" branch.

## 2. Universal engineering databases

| Database | Coverage | Access | Notes |
|---|---|---|---|
| **Scopus** | Broadest STEM abstract and citation index | Institutional | `TITLE-ABS-KEY()`; usually the core database |
| **Web of Science Core Collection** | Curated high-impact journals and proceedings | Institutional | `TS=`; reviewers expect it with Scopus |
| **Engineering Village (Compendex/Inspec)** | Engineering-specific, controlled vocabulary | Institutional | Ei Thesaurus terms improve recall |
| **IEEE Xplore** | EE, CS, electronics, power, comms | Institutional (abstracts free) | Essential for any electrical or computing topic |
| **ScienceDirect** | Elsevier full text | Institutional | Max 8 Boolean connectors per field |
| **SpringerLink** | Springer journals and LNCS proceedings | Partial | Weak search engine; use as a supplement |
| **ACM Digital Library** | Computing | Partial | Essential for software, HCI, systems |
| **OpenAlex** | 250M+ works, open | Free API (`scripts/search.py`) | Good open proxy for Scopus-like coverage |
| **Crossref** | DOI metadata | Free API | Metadata verification |
| **arXiv** | Preprints (CS, EE, physics) | Free API | Preprints are grey literature; flag them |
| **Semantic Scholar** | CS, biomedical, broad | Free API (rate-limited) | Citation graph, useful for snowballing |
| **Google Scholar** | Everything | Free UI only | Not reproducible (Gusenbauer & Haddaway 2020). Use only for snowballing or as a supplement, first 200–300 results |

**Minimum defensible set:** Scopus + WoS + one subject database (IEEE Xplore, Compendex, ACM, ASCE, etc.). If the user has no institutional access: OpenAlex + Crossref + arXiv + the free IEEE Xplore abstract search. State this limitation explicitly in the paper.

---

## 3. Subfield profiles

### 3.1 Mechanical & manufacturing engineering
- **Subject databases:** ASME Digital Collection, Compendex, SAE Mobilus (automotive), ScienceDirect.
- **Evidence types:** mechanical tests (tensile, fatigue, fracture to ASTM E8/E466/E399), FEA/CFD simulation, process experiments (DoE), digital-twin case studies.
- **Quality concerns:** specimen count and statistical treatment, standard test methods followed, mesh-convergence study (FEA), validation of simulation against experiment, process-parameter reporting completeness.
- **Typical extraction fields:** material, process parameters, test standard, specimen geometry, loading conditions, metric ± scatter, model type, validation.
- **Venues:** *Int. J. Machine Tools and Manufacture*, *J. Manufacturing Systems*, *Additive Manufacturing*, *CIRP Annals*, *J. Mech. Design (ASME)*, *Mech. Systems and Signal Processing*, *Int. J. Fatigue*; conferences: CIRP CMS, ASME IDETC/MSEC, NAMRC.

### 3.2 Civil, structural & geotechnical engineering
- **Subject databases:** ASCE Library, ICE Virtual Library, TRID (transport), Compendex.
- **Evidence types:** full- or reduced-scale structural tests, shake-table tests, field monitoring (SHM), FE models, code-comparison studies, life-cycle assessment.
- **Quality concerns:** scale effects, boundary conditions, code basis (Eurocode/ACI/AISC), material characterisation, model calibration vs. blind prediction, monitoring duration.
- **Venues:** *J. Structural Engineering (ASCE)*, *Engineering Structures*, *Automation in Construction*, *Structural Health Monitoring*, *Construction and Building Materials*, *Computer-Aided Civil and Infrastructure Engineering*, *Tunnelling and Underground Space Technology*.

### 3.3 Electrical, electronic & power/energy systems
- **Subject databases:** IEEE Xplore (mandatory), IET Digital Library, Inspec.
- **Evidence types:** hardware prototypes, circuit or system simulation (SPICE, MATLAB/Simulink, PSCAD), hardware-in-the-loop, field pilots, benchmark test systems (IEEE 14/33/118-bus).
- **Quality concerns:** benchmark system named and standard, operating conditions, simulation vs. hardware validation, efficiency measurement method, comparison against recent baselines, scalability.
- **Venues:** *IEEE Trans. Power Electronics / Power Systems / Smart Grid / Industrial Electronics / Sustainable Energy*, *Applied Energy*, *Renewable and Sustainable Energy Reviews* (review-focused), *Energy Conversion and Management*; conferences: IEEE ECCE, APEC, PES GM, ISGT.

### 3.4 Computer, software & AI/ML engineering
- **Subject databases:** ACM DL, IEEE Xplore, DBLP (metadata), arXiv (high preprint share), Semantic Scholar.
- **Review conventions:** Kitchenham & Charters (2007) SLR guidelines and Petersen et al. (2015) systematic mapping guidelines are expected *in addition to* PRISMA. Snowballing (Wohlin 2014) is standard.
- **Evidence types:** controlled experiments, benchmark evaluations, case studies, surveys of practitioners, mining software repositories.
- **Quality concerns (ML):** train/test leakage, dataset named and public, baselines tuned fairly, statistical significance or multiple seeds, ablations, code availability, compute reporting.
- **Venues:** *IEEE TSE*, *ACM TOSEM*, *Empirical Software Engineering*, *Information and Software Technology*, *ACM Computing Surveys* (review-focused), *IEEE TPAMI*, *IEEE TNNLS*, *Artificial Intelligence Review* (review-focused); conferences: ICSE, FSE, ASE, NeurIPS, ICML, CVPR, AAAI.

### 3.5 Chemical & process engineering
- **Subject databases:** SciFinder/CAS (institutional), Reaxys, Compendex, ACS Publications, Wiley.
- **Evidence types:** lab-scale experiments, pilot plant, process simulation (Aspen Plus/HYSYS), techno-economic analysis (TEA), LCA, kinetic modelling.
- **Quality concerns:** mass and energy balance closure, reproducibility (replicates), scale (bench → pilot → industrial), TEA assumptions transparent (base year, discount rate), LCA per ISO 14040/14044 with a defined functional unit.
- **Venues:** *Chemical Engineering Journal*, *AIChE Journal*, *Industrial & Engineering Chemistry Research*, *Computers & Chemical Engineering*, *Chemical Engineering Science*, *Green Chemistry*.

### 3.6 Materials science & engineering
- **Subject databases:** Compendex, Inspec, ScienceDirect, ACS, RSC, Wiley; materials databases (Materials Project, NIST) for context.
- **Evidence types:** synthesis + characterisation (XRD, SEM, TEM, DSC), property testing, DFT/MD simulation, ML property prediction.
- **Quality concerns:** characterisation completeness, sample count, processing history reported, computational parameters (functional, cut-off), ML dataset provenance and splits.
- **Venues:** *Acta Materialia*, *Materials & Design*, *Progress in Materials Science* (reviews), *Materials Science and Engineering A/R*, *npj Computational Materials*, *Advanced Materials*.

### 3.7 Aerospace & automotive engineering
- **Subject databases:** AIAA ARC, SAE Mobilus, NASA NTRS (grey literature), Compendex.
- **Evidence types:** wind-tunnel or flight tests, CFD, structural tests, vehicle tests, drive cycles (WLTP), HIL/SIL.
- **Quality concerns:** test-facility characterisation, Reynolds/Mach similarity, CFD turbulence model and grid independence, certification-standard relevance (DO-178C, ISO 26262).
- **Venues:** *AIAA Journal*, *Progress in Aerospace Sciences* (reviews), *Aerospace Science and Technology*, *IEEE Trans. Vehicular Technology*, *IEEE Trans. Intelligent Transportation Systems*, *SAE Int. J.*.

### 3.8 Biomedical engineering
- **Subject databases:** PubMed/MEDLINE (mandatory), Embase, IEEE Xplore, Scopus, WoS.
- **Note:** this is the subfield closest to medical PRISMA. Use clinical risk-of-bias tools (QUADAS-2 for diagnostic accuracy, RoB 2, ROBINS-I) for clinical studies, and engineering checklists for device or bench studies. Register in PROSPERO if there are human-health outcomes.
- **Venues:** *IEEE TBME*, *IEEE JBHI*, *Medical Image Analysis*, *Annals of Biomedical Engineering*, *J. Biomechanics*, *Biomaterials*.

### 3.9 Environmental, water & sustainability engineering
- **Subject databases:** GreenFILE, Compendex, Scopus, WoS, AGRIS; grey literature from EPA, EEA, IPCC, World Bank.
- **Evidence types:** field monitoring, lab treatability, hydrological or environmental modelling, LCA, TEA, policy or case studies.
- **Quality concerns:** monitoring duration and seasonality, model calibration and validation split (NSE, KGE), LCA system boundaries and functional unit, regional transferability.
- **Venues:** *Water Research*, *Environmental Science & Technology*, *J. Cleaner Production*, *Resources, Conservation & Recycling*, *Science of the Total Environment*, *Renewable and Sustainable Energy Reviews*.

### 3.10 Industrial engineering, operations & systems engineering
- **Subject databases:** Business Source Complete, ABI/INFORM, INFORMS PubsOnline, Compendex, IEEE Xplore.
- **Evidence types:** optimisation models (MILP, metaheuristics) on benchmark instances, simulation (DES, agent-based), case studies, surveys, action research.
- **Quality concerns:** benchmark instances public, comparison against best-known solutions, computational settings reported, real-data validation, managerial insights.
- **Venues:** *European J. Operational Research*, *Int. J. Production Research*, *Int. J. Production Economics*, *Computers & Industrial Engineering*, *IISE Transactions*, *J. Manufacturing Systems*, *Systems Engineering (INCOSE)*.

### 3.11 Robotics, control & mechatronics
- **Subject databases:** IEEE Xplore (mandatory), ACM DL, arXiv (cs.RO), Scopus.
- **Evidence types:** simulation (Gazebo, MuJoCo, Isaac), real-robot experiments, sim-to-real transfer, stability proofs, benchmarks.
- **Quality concerns:** number of trials, success-rate definitions, real hardware vs. simulation only, sim-to-real gap, stability or robustness proof assumptions, code or dataset release.
- **Venues:** *IEEE Trans. Robotics*, *IJRR*, *IEEE RA-L*, *Automatica*, *IEEE TAC*, *IEEE/ASME Trans. Mechatronics*, *Annual Reviews in Control* (reviews); conferences: ICRA, IROS, RSS, CDC, ACC.

### 3.12 Telecommunications & networking
- **Subject databases:** IEEE Xplore (mandatory), ACM DL, arXiv (cs.NI, eess.SP), 3GPP/ITU documents (grey literature).
- **Evidence types:** analytical models, link- or system-level simulation (ns-3, MATLAB), testbeds, field measurements.
- **Quality concerns:** channel model stated (3GPP TR 38.901, etc.), simulation parameters tabulated, comparison with standard baselines, testbed vs. simulation.
- **Venues:** *IEEE Communications Surveys & Tutorials* (top review venue), *IEEE JSAC*, *IEEE TWC*, *IEEE TCOM*, *IEEE IoT Journal*, *Computer Networks*; conferences: INFOCOM, ICC, GLOBECOM, SIGCOMM.

---

## 4. Review-type guidance per field

| Situation | Recommend | Guideline |
|---|---|---|
| Focused question, comparable quantitative outcomes | Systematic review ± meta-analysis | PRISMA 2020 |
| Broad or emerging field, mapping concepts | Scoping review | PRISMA-ScR (Tricco 2018), JBI methodology |
| Software engineering / CS classification of a field | Systematic mapping study | Petersen 2015 + PRISMA 2020 flow |
| Very large literature, tertiary | Umbrella review / tertiary study | PRISMA 2020 + overlap analysis (CCA) |
| Rapidly evolving topic needing ongoing updates | Living systematic review | PRISMA 2020 + update log |
| Technology-oriented with patents/standards | Systematic review + technology landscape | PRISMA 2020 with grey-literature branch |

Review-focused engineering venues (higher acceptance of review papers): *Renewable and Sustainable Energy Reviews*, *Progress in Materials Science*, *Progress in Aerospace Sciences*, *ACM Computing Surveys*, *IEEE Communications Surveys & Tutorials*, *Artificial Intelligence Review*, *Archives of Computational Methods in Engineering*, *Annual Reviews in Control*, *Materials Science and Engineering R*, *Applied Energy* (reviews section), *Engineering* (CAE), *Sensors* / *Applied Sciences* / *Energies* (MDPI, faster but check fit). Always verify the current scope, APCs and indexing on the venue website, because these change.

## 5. Field-specific reporting conventions
- SI units throughout. Convert imperial units where studies used them, and note the conversion.
- Report quantitative results with their uncertainty (± SD, CI, or the range across studies) and the number of studies (k) and specimens or samples (n) behind each claim.
- Use TRL (1–9, EU/NASA definition) to map maturity. Engineering reviewers value it.
- Name the standards studies followed (ASTM, ISO, IEC, IEEE Std), and use "standard compliance" as an extraction field.
- Separate **simulated-only** from **experimentally validated** evidence everywhere (tables, figures, conclusions). It is the most common critique of engineering reviews.
