# CareLoop Clinics: No-Show Guard
> **From raw bookings to a risk model and an AI-assisted follow-up review**  
> *IIT Roorkee & Masai School — Data Science & AI Capstone Project*

**Public Repository URL:** `https://github.com/<your-username>/careloop-noshow-guard` *(Update with actual repo URL)*

---

## 1. Project Overview & Business Context

CareLoop Clinics operates eight outpatient healthcare centres across six Indian cities:
* **Pune:** Hadapsar Care Centre, Kothrud Family Clinic
* **Jaipur:** Malviya Nagar Clinic, Vaishali Nagar Clinic
* **Indore:** Vijay Nagar Clinic
* **Kochi:** Edappally Medical Centre Kochi
* **Lucknow:** Gomti Nagar Care Point
* **Nagpur:** Sitabuldi Health Point

### The Business Challenge
In outpatient healthcare, every missed appointment represents an empty doctor slot that another patient could have used. Currently, clinic front desks only identify no-shows after the working day has ended. Furthermore, while the call-centre team records brief qualitative follow-up notes after speaking with patients who missed visits, these notes are never aggregated or analyzed systematically at scale.

### The Core Business Question
> **"Which appointments are most likely to be missed, why do patients miss them, and what should CareLoop do first?"**

### The Operational Prediction Point
Risk scores are generated on the **evening before the appointment** (after that day’s automated reminders have been sent or skipped). At this exact moment, all features—including reminder status and historical no-show counts—are known, allowing clinic front desk teams to prioritize personal telephone calls to the riskiest patients.

---

## 2. End-to-End System Architecture

```
Raw Data Pack (appointments.csv, clinics.csv, followup_notes.csv)
   │
   ├── Part 1: Python & Data Foundations (01_ingest_clean.ipynb)
   │     ├── Low-level CSV type parsing & exception routing (rejected_rows.json)
   │     ├── Multi-pass pandas cleaning, deduplication & gap imputation
   │     ├── Tukey outlier fencing & vectorized NumPy audits
   │     ├── Open-Meteo REST API live weather enrichment (clinics_enriched.csv)
   │     └── Clean export (appointments_clean.csv) & DB script (load_data.sql)
   │
   ├── Part 2: SQL Analytics & Relational Integrity (02_queries.sql)
   │     ├── Relational schema creation (PK/FK integrity checks)
   │     ├── Clinic no-show clustering & sample size filtering (HAVING >= 95)
   │     ├── Lead-time banding via CASE WHEN (1-7d, 8-14d, 15-30d, 31+d)
   │     ├── Monthly trend tracking via LAG() window functions
   │     └── Intra-city clinic ranking via RANK() OVER (PARTITION BY city)
   │
   ├── Part 3: Machine Learning & Predictive Risk Scoring (03_model.ipynb)
   │     ├── Leak-free train/test partition (80/20, seed 42)
   │     ├── Scaled Logistic Regression & odds ratio interpretability
   │     ├── Decision Tree overfitting diagnostics & Random Forest ensembles
   │     ├── 5-Fold cross-validation & hyperparameter tuning
   │     ├── Threshold optimization (0.50 vs 0.35) prioritizing clinical recall
   │     └── Final hold-out evaluation (test_risk_scores.csv)
   │
   ├── Part 4: Generative AI Follow-Up Review (04_genai.ipynb)
   │     ├── Gemini Flash integration via Google GenAI SDK
   │     ├── CRAFT structured prompting with strict JSON schema
   │     ├── Pydantic v2 data model validation (FollowupInsight)
   │     ├── Rate-limit throttling (time.sleep(13)) & blank-note bypass
   │     └── Adversarial fault-injection & Hinglish evaluation (notes_analysed.csv)
   │
   └── Strategic Synthesis & Executive Recommendation
         └── Crosstab: root_cause vs reminder_sent → Actionable Clinic Strategy
```

---

## 3. Four-Line Finding Summary

* **Part 1 (Data Foundations):** Ingested 1,020 raw bookings and isolated 32 invalid rows; cleaning, deduplication, and outlier capping yielded 990 verified appointments with an overall baseline no-show rate of 22.0% (218 no-shows).
* **Part 2 (SQL Analytics):** SQL aggregations revealed that no-show risk escalates dramatically with lead time, jumping from 16.2% for 1–7 day bookings to 60.5% for appointments booked 31+ days in advance.
* **Part 3 (Machine Learning):** Logistic Regression achieved the highest cross-validated ROC-AUC (0.77); tuning the decision threshold to 0.35 maximized recall (0.57) and identified that sending reminders is associated with an approximate 69% reduction in no-show odds (Odds Ratio = 0.31).
* **Part 4 (Generative AI):** Automated analysis of follow-up notes via Gemini Flash and Pydantic revealed that 100% of patients who cited forgetting their appointment had not received an automated reminder (`reminder_sent = No`).

---

## 4. Executive Business Recommendation

CareLoop Clinics should immediately execute a targeted, two-pronged operational intervention focused on advance bookings and systematic communication. First, because patients booking more than 30 days ahead exhibit a prohibitive **60.5% no-show rate** (compared to **16.2%** for 1–7 day bookings), CareLoop must institute automated SMS/WhatsApp reminder sequences at 7 days and 24 hours prior to the appointment; empirical modeling shows that sending reminders is associated with a **69% reduction in no-show odds** ($\text{Odds Ratio} = 0.31$, holding other features constant), and all follow-up notes citing forgetfulness belonged to unreminded patients. Second, clinic managers should deploy the Logistic Regression risk scoring model each evening using the optimized **0.35 probability threshold** (ROC-AUC $\approx 0.79$, Recall $\approx 0.57$). This flags approximately **25%** of daily scheduled patients (around 49 patients in our test cohort) for personalized 1-minute front-desk phone calls, directly addressing the operational cost asymmetry where an empty doctor slot far outweighs the nominal expense of an evening telephone check-in. High-risk clinics such as Hadapsar (**27.3%** no-shows) and Malviya Nagar (**26.8%** no-shows) should be prioritized for immediate workflow deployment.

---

## 5. Model Selection & Threshold Justification

* **Chosen Model:** **Logistic Regression** (with `StandardScaler` inside a cross-validation pipeline).
* **Cross-Validated ROC-AUC:** **0.77** on 5-fold training cross-validation (matching the tuned Random Forest while offering full interpretability and superior calibration). Held-out test set ROC-AUC: **0.789**.
* **Chosen Threshold:** **0.35** (over the standard default of 0.50).
* **Justification:** At threshold 0.50, out-of-fold recall was severely restricted to $\approx 25\%$ (missing 3 out of 4 no-shows). At threshold 0.35, training F1 increased from 0.35 to 0.49 and recall nearly doubled to $47\%$ ($57\%$ on test set). In a healthcare outpatient clinic, a missed warning results in an unutilized 15–30 minute consultation slot and lost fee revenue, whereas an extra check-in call costs only 1 minute of front desk staff time.

---

## 6. Analytical & Methodological Limitations

1. **Small Qualitative Sample Size:** The 10 analyzed follow-up notes serve as an architectural illustration of the GenAI extraction pipeline and cannot be assumed to represent the statistical distribution of no-show causes clinic-wide.
2. **Observational Association vs. Causality:** The data are strictly observational; the significant negative coefficient for reminders proves statistical association, not randomized clinical causality (e.g., more organized patients may be more likely to opt into or verify reminder phone numbers).
3. **Pre-Split Data Cleaning Influence:** Missing value imputations and Tukey outlier fences in Task 1.3 were calculated across all 990 rows before partitioning, allowing test set distributions a slight indirect influence on data cleaning (in a full production system, imputers and fences must be fit strictly on training data).

---

## 7. Deliverables & Repository Structure

```
.
├── data/
│   ├── appointments.csv         # Raw booking export (1,020 rows) - Unaltered
│   ├── clinics.csv              # Clinic master table (8 rows) - Unaltered
│   └── followup_notes.csv       # Call-centre follow-up notes (30 rows) - Unaltered
├── 01_ingest_clean.ipynb        # Part 1: Python data foundations, cleaning & Open-Meteo API
├── rejected_rows.json           # Part 1.1: 32 rejected rows from low-level CSV parser
├── appointments_clean.csv       # Part 1.6: 990 cleaned rows with exactly 16 columns
├── clinics_enriched.csv         # Part 1.5: 8 clinics enriched with live temperature data
├── load_data.sql                # Part 1.6: 998 INSERT statements for DB ingestion
├── 02_queries.sql               # Part 2: SQL analytics queries & duplicate key comments
├── 03_model.ipynb               # Part 3: Scikit-learn predictive modeling & threshold tuning
├── test_risk_scores.csv         # Part 3.5: 198 test row risk predictions and flags
├── 04_genai.ipynb               # Part 4: Gemini Flash + Pydantic v2 extraction pipeline
├── notes_analysed.csv           # Part 4.2: Structured extraction results for 10 notes
├── README.md                    # Project report, findings summary & limitations
└── requirements.txt             # Environment dependencies and versions
```

---

## 8. Setup & Execution Instructions

### Local Environment Setup
```bash
# Clone the repository
git clone https://github.com/<your-username>/careloop-noshow-guard.git
cd careloop-noshow-guard

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### Running the Components
1. **Data Cleaning:** Run `01_ingest_clean.ipynb` to generate `appointments_clean.csv`, `clinics_enriched.csv`, and `load_data.sql`.
2. **SQL Analytics:** Execute `load_data.sql` followed by `02_queries.sql` inside MySQL Workbench or SQLiteOnline.
3. **Machine Learning:** Execute `03_model.ipynb` to evaluate models, tune thresholds, and export `test_risk_scores.csv`.
4. **GenAI Review:** Open `04_genai.ipynb`, enter your Google AI Studio API key at the interactive prompt, and run the pipeline to generate `notes_analysed.csv`.
