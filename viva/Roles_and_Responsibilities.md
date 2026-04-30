# Team Roles and Responsibilities

Suggested division for a 4-person team. Adjust to actual contributions.

---

## Deepanshu — Data Strategy & Product Lead

**Owned (the project's foundation)**:
- Defined the data strategy: how 10 different sources combine into one usable training set
- Reviewed 30+ Kaggle candidates and curated the 9 with the strongest signal-to-noise
- Aggregated ~912,000 raw rows across selected sources
- Personally observed and hand-tagged 120 competitor ads on Meta Ad Library + Google Ads Transparency over an 8-day window (20–28 April 2026)
- Designed the 20-brand coverage map: baby-care, parenting, edtech (Mamaearth, FirstCry, Pampers, BabyChakra, Healofy, Huggies, Himalaya, Johnson's, Sebamed, MamyPoko, BYJU's, Khan Academy + 8 more)
- Architected the canonical 12-column schema that lets 6 unrelated Kaggle vendors plug into the same training pipeline
- Caught the 382 misaligned rows in source-1 through manual inspection — a data forensics save that prevented downstream training corruption
- Built the ONLY Indian-competitor creative-metadata dataset in the public-research domain for this product segment — the project's signature contribution

**Viva specialty**:
- Where each dataset came from
- Why we chose Kaggle + manual tagging instead of pure synthetic
- Why 120 rows and not 1,000 (sample-size vs time trade-off)
- Brand selection rationale (Indian D2C parenting + edtech)

**Likely questions**:
- "Why didn't you scrape the ad libraries?" → ToS prohibits automated scraping
- "How is your manual data different from Kaggle?" → competitor metadata, Indian-market specific, no Kaggle source has it

---

## Akashdeep (Team Lead) — Model Development Lead

**Owned**:
- The full training pipeline in `hybrid_model_v5.py`
- Stacking-ensemble architecture (HGB + LightGBM + XGBoost + RandomForest under Ridge)
- Feature engineering (8 derived features: log-impressions, impression-decile, plat×source interaction, etc.)
- Leakage audit (caught CPM=1.0 trivial baseline, removed leaking features per-target)
- 5-fold cross-validation, bootstrap CIs, MAE / RMSE / MAPE / R² reporting
- Permutation feature importance

**Viva specialty**:
- Why 4 base learners and not just XGBoost
- How the leakage audit works (CPM example is the easiest to walk through)
- Why we report CV scores instead of just train/test
- How the Ridge meta-learner adds value
- Hyperparameter choices

**Likely questions**:
- "Why not deep learning?" → tabular size, explainability, gradient-boost beats DL on this scale
- "How did you tune hyperparameters?" → manual grid on max_iter, max_depth, learning_rate
- "Is this overfitting?" → CV5 stdev is 0.003–0.038 across all targets, so no
- "Why did some targets score low?" → ROI in source-06 has |r|<0.02 with every feature — data ceiling

---

## Medha — Feature Engineering & Data Pipeline Lead

**Owned (the model's input layer)**:
- Designed the harmonisation pipeline: 6 Kaggle vendors with different schemas → one canonical 12-column table
- Engineered 8 derived features that drive model accuracy: log_impressions, log_clicks, log_spend, impression_decile_within_source, platform×source interaction, ctr×log_impressions, spend_per_click, cost_per_impression
- Built the leakage-prevention guard: per-target feature exclusion list (caught CPM = 1.0 trivial baseline)
- Implemented label encoding for 8 categorical fields (platform, brand, format, theme, CTA, audience, language, source_dataset)
- Designed the missing-value strategy: fill with -1 so trees can split on absence
- Set up outlier clipping: 0.5%/99.5% quantile cuts per target
- Side responsibility: drafted the research-paper section on data + features

**Viva specialty**:
- Why log-transforms on impressions/clicks/spend
- How the impression_decile feature handles cross-vendor scale differences
- How the platform×source interaction captures vendor-specific pricing behaviour
- How the leakage-prevention guard works (CPM = 1.0 example)
- Why -1 fill instead of mean/median imputation

**Likely questions**:
- "Why these 8 features?" → each solves a specific modelling problem (long tails, scale heterogeneity, cross-vendor variance, leakage risk)
- "How did you catch the CPM leakage?" → per-target audit; spotted log_spend + log_impressions algebraically computing CPM
- "Why label encoding instead of one-hot?" → tree learners handle integer categories natively; one-hot wastes capacity
- "What if a brand has only 1 row?" → label encoder assigns it an integer; trees can still split on it; no NaN issue

---

## Harsh — Model Evaluation & Validation Lead

**Owned (model-side work)**:
- The full evaluation protocol: 80/20 train-test split + 5-fold CV + 200-resample bootstrap CIs
- Wrote the ablation study script (drop one base learner at a time, retrain, measure delta R²)
- Built the baseline comparison: predict-the-mean, linear regression, Ridge, single HGB, single XGB
- Hyperparameter exploration: max_iter {300, 500}, max_depth {6, 7, 8}, learning_rate = 0.05
- Computed per-platform R² breakdown (Meta vs Google vs Pinterest vs Twitter)
- Generated the 6 figures (R² with CI bars, feature importance, calibration, ablation, baselines, predicted-vs-actual)
- Discovered the LLM-data finding: dropping LLM rows IMPROVES D1 R² by 5.8 points
- Also: cross-checked numbers in paper vs JSON vs deck; coordinated rehearsals

**Viva specialty**:
- Why we use 5-fold CV instead of just train/test split
- How the bootstrap CI is computed and what it tells the reviewer
- What the ablation study revealed (and why we report unfavourable findings honestly)
- Per-platform performance breakdown
- The full validation framework (6 tools)

**Likely questions**:
- "Is the model overfitting?" → CV5 stdev is 0.003-0.038 across all targets; bootstrap CIs are tight; no.
- "How did you tune hyperparameters?" → manual grid on max_iter, max_depth, learning_rate; reported in the released code.
- "Did stacking actually help?" → ablation showed single HGB is competitive; we report this honestly in §5.1.
- "Why is ROI weak?" → source-06 ROI has |r|<0.02 with every numeric feature; that's the data ceiling.

---

## Joint responsibilities (everyone)

- Read the paper end-to-end at least once before viva
- Memorise the headline numbers (CTR 0.75, CPC 0.81, CPA 0.75, AUC 0.99, IQS 0.80)
- Practice answering the 13 questions in the QA booklet aloud
- Be ready to walk through `hybrid_model_v5.py` if asked to share screen

---

## Numbers everyone must know cold

- **15 prediction tasks** total (7 regression + 3 classifiers + 5 SDK retention/quality)
- **21,643 unified real-campaign rows** (after cleaning 6 Kaggle sources)
- **1,120 creative-metadata rows** (3 LLM files + 120 manual)
- **~912,000 raw rows** before cleaning
- **20 brands** in the manual tagging file
- **5-fold cross-validation** on every regression target
- **200-resample bootstrap 95% CIs** on every R²
- **4 base learners** in the stack: HGB, LightGBM, XGBoost, RandomForest
- **Ridge alpha = 0.5** for the meta-learner
