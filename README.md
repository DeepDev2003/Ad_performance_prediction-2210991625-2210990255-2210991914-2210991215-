# Ad Performance Prediction

Final-year project. We trained a model that predicts how a digital ad will perform
before it goes live, using public Kaggle datasets plus 120 competitor ads we tagged
ourselves from the Meta Ad Library and Google Ads Transparency Center.

The model predicts 15 different ad metrics (CTR, CPC, CVR, ROI, CPM, CPA, retention
windows etc.) using a stacked ensemble of HGB, LightGBM, XGBoost, and Random Forest
with a Ridge regressor on top.

## Headline numbers

| Task | CV R² / AUC |
|---|---|
| CTR | 0.75 |
| CPC | 0.81 |
| CVR | 0.65 |
| CPM | 0.73 |
| CPA | 0.75 |
| High-CTR classifier | AUC 0.99 |
| D1 retention | 0.73 |
| Install Quality Score | 0.80 |

ROI is weak (R² 0.33) because the source data has near-zero correlation between
ROI and any feature - we report this in §6 of the paper.

## How to run

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy scikit-learn lightgbm xgboost openpyxl python-docx matplotlib
# macOS only: brew install libomp
python hybrid_model.py
python evaluation.py
```

`hybrid_model.py` does the training. `evaluation.py` runs the ablation and makes the
charts. Outputs land in `outputs/` and `figures/`.

## Folder layout

- `hybrid_model.py` - main training pipeline
- `evaluation.py` - ablation, baselines, figures
- `expand_manual_tagging.py` - builds the 120-row competitor file
- `datasets/` - 9 Kaggle source files
- `figures/` - charts used in the paper
- `outputs/` - results JSON + unified CSVs
- `viva/` - presentation deck

## Data sources

| # | Source | Rows |
|---|---|---|
| 1 | Kaggle Facebook Ad Campaigns | 1,143 |
| 2 | Kaggle Social Media Ads 300k | 10,000 (sampled) |
| 3 | Kaggle Ad Click Prediction 10k | 10,000 |
| 4 | Kaggle Social Media Optimization | 500 |
| 5 | Kaggle Ad Campaign DB | 400,000 events |
| 6 | Kaggle Marketing Campaign 200k | 10,000 (sampled) |
| 7-9 | Synthetic creative metadata | 1,000 |
| 10 | Manual: Meta Ad Library + Google Ads Transparency | 120 |

## Team

Deepanshu (data), Akashdeep (model, team lead), Medha (feature engineering),
Harsh (evaluation, validation).
