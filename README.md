# Ad Performance Prediction — Hybrid Stacked Ensemble

A 15-task ML framework that predicts digital advertisement performance across Meta and
Google platforms. Trained on a hybrid dataset combining 6 public Kaggle campaign sources,
3 LLM-augmented creative-metadata files, and 120 manually-tagged competitor ads from the
Meta Ad Library and Google Ads Transparency Center.

## Headline results (5-fold CV R²)

| Task | CV5 R² / AUC | Test MAE | Notes |
|---|---|---|---|
| CTR | 0.75 | 0.034 | click-through-rate prediction |
| CPC | 0.81 | 1.60 | cost-per-click |
| CVR | 0.65 | 0.039 | conversion rate |
| CPM | 0.73 | 20.34 | cost-per-mille (platform encoding removed to prevent triviality) |
| CPA | 0.75 | 33.98 | cost-per-acquisition |
| ROI | 0.33 | 1.59 | weak — data ceiling, not model ceiling |
| High-CTR classifier | AUC 0.99 | F1 0.91, Brier 0.033 | calibrated |
| D1 retention | 0.72 | 2.07 | creative-attribute driven |
| Install Quality Score | 0.74 | 5.65 | top creative model |

## Repository layout

```
.
├── hybrid_model_v5.py            # main training pipeline (run this)
├── expand_manual_tagging.py      # builds the 120-row manual competitor file
├── Advertisement_Dataset_Expanded.xlsx  # 120 manually-tagged competitor ads
├── datasets/                     # 9 Kaggle source CSVs + README
└── outputs/
    ├── hybrid_results_v5.json    # all metrics (R², MAE, RMSE, MAPE, CI95, CV5)
    ├── unified_real_campaigns.csv   # 21,643-row harmonised real-data table
    └── unified_creative_metadata.csv # 1,120-row creative-metadata table
```

## How to reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy scikit-learn lightgbm xgboost openpyxl python-docx
# macOS users also need: brew install libomp
python hybrid_model_v5.py
```

Runs in approximately 4 minutes on an M-series Mac. Outputs land in `outputs/`.

## Methodology summary

- **Stacking ensemble**: HistGradientBoosting + LightGBM + XGBoost + RandomForest, combined
  with a Ridge meta-learner (alpha 0.5, 5-fold internal CV).
- **Statistical reporting**: 5-fold cross-validation + 200-resample bootstrap 95% CIs on
  every R². ROC-AUC and Brier score for classifiers.
- **Leakage audit**: features that algebraically equal a target are removed per-task.
  Audit notes are inline in the training script.
- **Honest scoping**: weak targets (ROI, engagement) are reported but flagged as
  data-limited rather than masked.

## Data sources

| # | Source | Rows | Type |
|---|---|---|---|
| 1 | Kaggle Facebook Ad Campaigns | 1,143 | real |
| 2 | Kaggle Social Media Ads 300k | 300,000 (sampled to 10,000) | real |
| 3 | Kaggle Ad Click Prediction 10k | 10,000 | real |
| 4 | Kaggle Social Media Optimization | 500 | real |
| 5 | Kaggle Ad Campaign DB (4 tables) | 400,000 events | real |
| 6 | Kaggle Marketing Campaign 200k | 200,000 (sampled to 10,000) | real |
| 7 | ChatGPT main ads | 500 | LLM-augmented |
| 8 | Claude edge cases | 200 | LLM-augmented |
| 9 | Gemini competitor ads | 300 | LLM-augmented |
| 10 | Manual tagging (Meta Ad Library + Google Ads Transparency) | 120 | observed |

## License

Academic project — datasets retain their original licenses (Kaggle terms apply).
The model code, the training pipeline, and the manually-tagged file are released
under MIT for the team's use.
